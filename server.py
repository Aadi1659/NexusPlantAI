import os
import sys
import time
import json
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Append workspace root directly
sys.path.append("/Users/aadityadevsharma/Documents/hackathon")

from src.agents.copilot import query_copilot
from src.agents.rca_agent import run_rca_analysis
from src.agents.compliance_agent import run_compliance_audit
from src.knowledge_graph.graph_builder import build_knowledge_graph, HTML_PATH
from src.retrieval.vectorstore import get_collection, add_chunks

app = Flask(__name__, static_folder=".", static_url_path="")

# Fast in-memory cache for file listing
_FILE_CACHE = {
    "tech_docs": [
        "1737029789_fa33f264822ba23a495f.pdf",
        "1776342005_56c5fa47e1d373e0a79d.pdf",
        "52-Near-Miss-Report-Form-1903.pdf",
        "811_iom.pdf",
        "811cc-series-iom.pdf",
        "IOM_manual_CTP.pdf",
        "Safety_occurrence_reporting_and_investigation.pdf",
        "b878b8d9f3d9abc62fbe0a6c92f606e3.pdf",
        "centrifugal-pump-acp-se-manual-v2-2-en-data.pdf",
        "factory_acta1948-63.pdf",
        "hsg245.pdf",
        "riddor-background-quality-report.pdf",
        "user_manual_2023_NHVf_EN.pdf",
        "workplace-accident-and-incident-investigation-template-2018.pdf"
    ],
    "maint_docs": [
        "maintenance_log_synthetic.csv",
        "near_miss_incident_log_synthetic.csv"
    ]
}

def get_fast_ingested_files():
    # Scan raw data directory quickly for any new files
    raw_dir = "/Users/aadityadevsharma/Documents/hackathon/data/raw"
    if os.path.exists(raw_dir):
        raw_files = os.listdir(raw_dir)
        tech_set = set(_FILE_CACHE["tech_docs"])
        maint_set = set(_FILE_CACHE["maint_docs"])
        for f in raw_files:
            if f.endswith(".pdf"):
                tech_set.add(f)
            elif f.endswith(".csv") or f.endswith(".xlsx"):
                maint_set.add(f)
        _FILE_CACHE["tech_docs"] = sorted(list(tech_set))
        _FILE_CACHE["maint_docs"] = sorted(list(maint_set))
        
    return _FILE_CACHE["tech_docs"], _FILE_CACHE["maint_docs"]

# --- Serve Frontend Landing Page ---
@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

# --- Serve Workspaces Selection Hub ---
@app.route("/workspaces.html")
def serve_workspaces():
    return send_from_directory(".", "workspaces.html")

# --- Serve Dedicated Dashboard Webpage ---
@app.route("/dashboard.html")
def serve_dashboard():
    return send_from_directory(".", "dashboard.html")

# --- Serve Knowledge Graph HTML ---
@app.route("/data/processed/knowledge_graph.html")
def serve_graph():
    if not os.path.exists(HTML_PATH):
        build_knowledge_graph()
    return send_from_directory("data/processed", "knowledge_graph.html")

# --- API Endpoint: Get Ingested Files List (INSTANT 1ms Response) ---
@app.route("/api/files", methods=["GET"])
def api_files():
    tech_docs, maint_docs = get_fast_ingested_files()
    return jsonify({
        "technical_docs": tech_docs,
        "maintenance_records": maint_docs
    })

# --- API Endpoint: Upload & Live Ingest New File ---
@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Selected file is empty"}), 400
        
    filename = secure_filename(file.filename)
    raw_dir = "/Users/aadityadevsharma/Documents/hackathon/data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    save_path = os.path.join(raw_dir, filename)
    file.save(save_path)
    
    ext = filename.split(".")[-1].lower()
    try:
        if ext == "pdf":
            from src.ingestion.pdf_loader import load_pdf, chunk_documents
            docs = load_pdf(save_path)
            chunks = chunk_documents(docs)
            add_chunks("technical_docs", chunks)
            cnt = len(chunks)
            if filename not in _FILE_CACHE["tech_docs"]:
                _FILE_CACHE["tech_docs"].append(filename)
        else:
            from src.ingestion.excel_loader import load_csv_or_excel
            records = load_csv_or_excel(save_path)
            add_chunks("maintenance_records", records)
            cnt = len(records)
            if filename not in _FILE_CACHE["maint_docs"]:
                _FILE_CACHE["maint_docs"].append(filename)
            
        build_knowledge_graph()
        return jsonify({"message": f"Indexed {cnt} chunks from {filename}!"})
    except Exception as e:
        return jsonify({"error": f"Ingestion error: {str(e)}"}), 500

# --- API Endpoint: Delete File & Re-index Corpus ---
@app.route("/api/delete_file", methods=["POST"])
def api_delete_file():
    data = request.get_json() or {}
    filename = data.get("filename", "")
    collection_name = data.get("collection_name", "technical_docs")
    
    if not filename:
        return jsonify({"error": "Filename required"}), 400
        
    try:
        col = get_collection(collection_name)
        col.delete(where={"source_file": filename})
        
        raw_path = os.path.join("/Users/aadityadevsharma/Documents/hackathon/data/raw", filename)
        if os.path.exists(raw_path):
            os.remove(raw_path)
            
        if filename in _FILE_CACHE["tech_docs"]:
            _FILE_CACHE["tech_docs"].remove(filename)
        if filename in _FILE_CACHE["maint_docs"]:
            _FILE_CACHE["maint_docs"].remove(filename)
            
        build_knowledge_graph()
        return jsonify({"message": f"Deleted {filename} and updated vector store!"})
    except Exception as e:
        return jsonify({"error": f"Delete error: {str(e)}"}), 500

# --- API Endpoint: Copilot RAG Search ---
@app.route("/api/copilot", methods=["POST"])
def api_copilot():
    data = request.get_json() or {}
    query = data.get("query", "")
    equipment_tag = data.get("equipment_tag", None)
    
    if not query.strip():
        return jsonify({"error": "Query cannot be empty"}), 400
        
    result = query_copilot(query, equipment_tag=equipment_tag)
    return jsonify(result)

# --- API Endpoint: RCA Intelligence Agent ---
@app.route("/api/rca", methods=["POST"])
def api_rca():
    data = request.get_json() or {}
    failure_desc = data.get("failure_desc", "")
    
    if not failure_desc.strip():
        return jsonify({"error": "Failure description cannot be empty"}), 400
        
    result = run_rca_analysis(failure_desc)
    return jsonify(result)

# --- API Endpoint: Compliance Auditor ---
@app.route("/api/compliance", methods=["GET"])
def api_compliance():
    result = run_compliance_audit()
    return jsonify(result)

# --- API Endpoint: System Benchmark Results ---
@app.route("/api/benchmark", methods=["GET"])
def api_benchmark():
    json_path = "/Users/aadityadevsharma/Documents/hackathon/data/processed/benchmark_results.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "Benchmark data not found"}), 404

if __name__ == "__main__":
    print("🚀 Starting NexusPlant AI Backend Server on http://localhost:8080...")
    app.run(host="0.0.0.0", port=8080, debug=False)
