# NexusPlant AI — Industrial Knowledge Intelligence Platform (Problem Statement #8)

**NexusPlant AI** is an autonomous, RAG-driven Industrial Knowledge Intelligence Platform designed for plant operations, reliability engineering, and safety compliance. Built with **Streamlit, ChromaDB, ChatGroq (Llama-3-8B), LangChain, NetworkX, and Pyvis**.

---

## 🌟 Key Features & Agent Architecture

The platform processes heterogeneous document silos (OEM PDF manuals, CSV maintenance work orders, near-miss safety logs, and regulatory acts) into a persistent vector database with **1,161 indexed knowledge chunks** across 2 collections.

1. 💬 **Maintenance Copilot**: Conversational RAG assistant with hybrid BM25 + dense vector search, asset tag filtering, confidence scoring, and page-level source citations.
2. 🔍 **RCA Intelligence Agent**: Multi-step diagnostic reasoner that performs triple lookups (Logs + OEM Manuals + Incident History) to generate structured Root Cause Analysis JSON reports.
3. 📋 **Quality & Regulatory Compliance Auditor**: Automated safety scanner that evaluates plant logs against the Factories Act, HSG245, and RIDDOR guidelines, flagging compliance gaps and generating pre-filled regulatory filing forms.
4. 🕸️ **Knowledge Graph Network**: Interactive Pyvis network visualization mapping Equipment tags, Technical Manuals, and Failure Modes.
5. 📊 **System Benchmark Dashboard**: Live evaluation suite tracking LLM accuracy scores (9.1/10 avg), citation rates (100%), and latency across 20 real-world engineering queries.

---

## 📁 Repository Structure

```text
├── index.html                 # Vercel Production Web Application (HTML5/Tailwind/WebGL)
├── vercel.json                # Vercel routing configuration
├── app.py                     # Streamlit multi-tab web application
├── requirements.txt           # Python dependencies
├── .env.example               # Template environment configuration file
├── src/
│   ├── ingestion/
│   │   ├── pdf_loader.py      # Extract and chunk text-native PDF manuals
│   │   ├── ocr_loader.py      # Preprocess and OCR scanned manuals
│   │   └── excel_loader.py    # Row-by-row natural serialization for CSV logs
│   ├── retrieval/
│   │   ├── vectorstore.py     # ChromaDB manager using sentence-transformers
│   │   └── retriever.py       # Hybrid retrieval, tag filtering & local BM25 re-ranking
│   ├── knowledge_graph/
│   │   └── graph_builder.py   # NetworkX graph construction & Pyvis HTML export
│   └── agents/
│       ├── copilot.py         # Conversational RAG copilot chain (LCEL)
│       ├── rca_agent.py       # Multi-source Root Cause Analysis diagnostic flow
│       └── compliance_agent.py# Regulatory safety audit scanning engine
├── data/
│   ├── raw/                   # Raw manuals (PDFs) and incident/maintenance logs (CSVs)
│   └── processed/
│       ├── chromadb/          # Persistent vector database
│       └── benchmark_results.json # Pre-computed 20-question evaluation dataset
├── docs/
│   ├── architecture diagram.png       # High-resolution system architecture blueprint
│   ├── architecture.md               # Detailed pipeline specification
│   ├── presentation_deck_outline.md  # 10-slide submission deck outline
│   ├── demo_video_script.md          # Scene-by-scene video script & narration guide
│   └── walkthrough.md                # Execution walk-through report
└── tests/
    ├── test_retrieval.py      # Vector search verification script
    ├── test_compliance.py     # Automated compliance auditor test
    └── run_benchmark.py       # 20-query benchmark evaluation harness
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Environment Setup
Clone the repository and set up a virtual environment:
```bash
git clone <your-repo-url>
cd hackathon
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 3. Launch Vercel Web App (Local Preview)
```bash
python3 -m http.server 8000
```
Open your browser at `http://localhost:8000`.

---

## 🧪 Running Automated Tests & Benchmarks

To run the compliance agent audit scan in terminal:
```bash
python -m unittest tests/test_compliance.py
```

To run the full 20-question benchmark suite:
```bash
python tests/run_benchmark.py
```
