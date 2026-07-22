import os
import json
import time
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.retrieval.vectorstore import query_vectorstore

# Load environment variables
load_dotenv()

DEFAULT_MODEL = "llama-3.1-8b-instant"

# Paths to raw files
MAINTENANCE_LOG_PATH = "/Users/aadityadevsharma/Documents/hackathon/data/raw/maintenance_log_synthetic.csv"
INCIDENT_LOG_PATH = "/Users/aadityadevsharma/Documents/hackathon/data/raw/near_miss_incident_log_synthetic.csv"

def get_chat_model(model=DEFAULT_MODEL):
    """
    Initializes and returns the ChatGroq model.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not found. Please set it in your .env file.")
    return ChatGroq(model=model, temperature=0.1, api_key=api_key)

def scan_for_compliance_anomalies():
    """
    Scans maintenance and incident logs for compliance anomalies.
    Returns a list of dictionary anomalies.
    """
    anomalies = []
    
    # 1. Load Maintenance logs
    if os.path.exists(MAINTENANCE_LOG_PATH):
        df_maint = pd.read_csv(MAINTENANCE_LOG_PATH)
        # Filter for Emergency maintenance with significant downtime (> 2 hours)
        emergency_issues = df_maint[
            (df_maint["Maintenance_Type"].str.lower() == "emergency") & 
            (df_maint["Downtime_Hours"] > 2.0)
        ]
        for _, row in emergency_issues.head(2).iterrows():
            anomalies.append({
                "source": "Maintenance Log",
                "id": str(row["Log_ID"]),
                "date": str(row["Date"]),
                "asset": str(row["Equipment_ID_Name"]),
                "type": "Emergency Downtime Event",
                "details": f"Technician {row['Technician']} executed Emergency repairs. downtime: {row['Downtime_Hours']} hours. Observation: {row['Observation_Remarks']}. Parts replaced: {row['Parts_Replaced']}.",
                "raw_data": dict(row)
            })
            
    # 2. Load Incident logs
    if os.path.exists(INCIDENT_LOG_PATH):
        df_inc = pd.read_csv(INCIDENT_LOG_PATH)
        # Filter for Open minor injuries or high-potential near-misses
        incident_issues = df_inc[
            (df_inc["Severity"].isin(["Minor Injury", "Property Damage", "Near Miss - High Potential"])) & 
            (df_inc["Status"].str.lower().isin(["open", "under review"]))
        ]
        for _, row in incident_issues.head(2).iterrows():
            anomalies.append({
                "source": "Incident Log",
                "id": str(row["Report_ID"]),
                "date": str(row["Date"]),
                "asset": str(row["Location"]),
                "type": f"Safety Incident ({row['Severity']})",
                "details": f"Reported by {row['Reported_By']}. Severity: {row['Severity']}. Cause: {row['Probable_Cause']}. Description: {row['Description']}. Status: {row['Status']}. Corrective Action: {row['Corrective_Action']}.",
                "raw_data": dict(row)
            })
            
    return anomalies

def audit_anomaly(anomaly, model=DEFAULT_MODEL):
    """
    Evaluates a single anomaly against safety regulations retrieved from ChromaDB.
    """
    llm = get_chat_model(model)
    
    # Query vector store for regulatory information (Factories Act, HSG245, etc.)
    query_text = f"safety requirements accident reporting factories act riddor incident {anomaly['type']} {anomaly['asset']}"
    tech_docs = query_vectorstore(
        "technical_docs",
        query_text=query_text,
        n_results=3
    )
    
    # Format regulatory context
    formatted_docs = []
    for idx, r in enumerate(tech_docs):
        meta = r["metadata"]
        src = meta.get("source_file", "Safety Guide")
        page = meta.get("page_number", "Unknown Page")
        formatted_docs.append(f"Source [{idx+1}]: {src} (Page {page})\nText: {r['text']}")
        
    context_text = "\n\n".join(formatted_docs) if formatted_docs else "No specific regulatory matching sections found in vector store."
    
    # Prompt the LLM to run the compliance audit
    audit_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert industrial safety auditor.\n"
                   "Analyze the operational event (anomaly) and cross-reference it against the provided safety regulations.\n"
                   "Evaluate if there is any safety gap, violation, or non-compliance.\n"
                   "Generate a structured JSON compliance audit report.\n"
                   "You must respond ONLY with a JSON object. Schema:\n"
                   "{{\n"
                   "  \"violation_flag\": true/false,\n"
                   "  \"regulations_cited\": \"Specific section/clause from safety regulations, or 'None' (string)\",\n"
                   "  \"severity\": \"Critical\", \"Major\", \"Minor\", or \"Compliant\" (string),\n"
                   "  \"audit_assessment\": \"Detailed evaluation of why this is a violation or why it is compliant (string)\",\n"
                   "  \"remediation\": \"Specific action required by the plant operators to resolve this compliance gap (string)\",\n"
                   "  \"reporting_template\": \"A pre-filled official incident notification template for regulatory reporting (e.g. RIDDOR Form or Factories Act Form F-18 format) containing date, location, equipment, description of event, injury type if any, and corrective actions (string)\"\n"
                   "}}"),
        ("user", "OPERATIONAL ANOMALY DETAILS:\n"
                 "- Source: {source}\n"
                 "- ID: {id}\n"
                 "- Date: {date}\n"
                 "- Asset/Location: {asset}\n"
                 "- Type: {type}\n"
                 "- Details: {details}\n\n"
                 "RETRIEVED SAFETY REGULATIONS CONTEXT:\n"
                 "{context}")
    ])
    
    audit_chain = audit_prompt | llm.bind(response_format={"type": "json_object"})
    
    try:
        response = audit_chain.invoke({
            "source": anomaly["source"],
            "id": anomaly["id"],
            "date": anomaly["date"],
            "asset": anomaly["asset"],
            "type": anomaly["type"],
            "details": anomaly["details"],
            "context": context_text
        })
        audit_report = json.loads(response.content)
    except Exception as e:
        print(f"Error auditing anomaly {anomaly['id']}: {e}")
        audit_report = {
            "violation_flag": True,
            "regulations_cited": "Factories Act 1948 / Safety Guidelines",
            "severity": "Major",
            "audit_assessment": f"Failed to execute audit due to LLM error. Event details: {anomaly['details']}",
            "remediation": "Review incident log manually.",
            "reporting_template": "Draft reporting form unavailable."
        }
        
    return {
        "anomaly": anomaly,
        "audit": audit_report,
        "sources": [{
            "source_file": r["metadata"].get("source_file", "OEM Manual"),
            "location": f"Page {r['metadata'].get('page_number', 'Unknown')}",
            "text": r["text"]
        } for r in tech_docs]
    }

def run_compliance_audit(model=DEFAULT_MODEL):
    """
    Scans the logs, audits each detected anomaly, and returns a summary report list.
    """
    start_time = time.time()
    anomalies = scan_for_compliance_anomalies()
    
    audit_results = []
    for anomaly in anomalies:
        result = audit_anomaly(anomaly, model=model)
        audit_results.append(result)
        
    latency = time.time() - start_time
    
    # Calculate summary KPIs
    total_scanned = len(audit_results)
    total_gaps = sum(1 for r in audit_results if r["audit"].get("violation_flag", False))
    critical_gaps = sum(1 for r in audit_results if r["audit"].get("severity", "").lower() == "critical")
    safety_score = 100.0 if total_scanned == 0 else ((total_scanned - total_gaps) / total_scanned) * 100.0
    
    return {
        "summary": {
            "total_scanned": total_scanned,
            "total_gaps": total_gaps,
            "critical_gaps": critical_gaps,
            "safety_score_percentage": safety_score
        },
        "results": audit_results,
        "latency": latency
    }
