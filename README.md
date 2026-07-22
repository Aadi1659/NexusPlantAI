# NexusPlant AI — Industrial Knowledge Intelligence Command OS (Problem Statement #8)

**NexusPlant AI** is an autonomous, RAG-driven Industrial Knowledge Intelligence Command OS designed for plant operations, reliability engineering, and safety compliance. Powered by **Groq LPU Hardware Inference (Llama-3.1-8B-Instant), ChromaDB, Pyvis Dark Cyber Knowledge Graph, and Python Flask**.

---

## 🌟 Key Features & Agent Architecture

The platform processes heterogeneous document silos (OEM PDF manuals, CSV maintenance work orders, near-miss safety logs, and regulatory acts) into a persistent vector database with **indexed technical and maintenance knowledge chunks**.

1. 💬 **RAG Engineering Copilot**: Conversational RAG assistant with hybrid BM25 + dense vector search, asset tag filtering (`P-101`, `P-102`, `V-105`, `C-301`), confidence scoring, formatted markdown output, and page-level source citations.
2. 🕵️ **Triple-Lookup RCA Intelligence Agent**: Multi-source diagnostic reasoner that correlates failure symptoms with maintenance history to output prominent, high-priority remediation action plans.
3. 🛡️ **Quality & Regulatory Compliance Auditor**: Automated safety scanner evaluating plant logs against the Factories Act 1948, HSG245, and RIDDOR guidelines, outputting safety scores and pre-formatted statutory filing report templates.
4. 🕸️ **Dark Cyber Relational Knowledge Graph**: Interactive Pyvis 3D network visualization mapping Equipment tags, OEM Manuals, Failure Modes, and Statutory Regulations.
5. 📊 **System Benchmark Suite**: Live evaluation dataset tracking model precision (9.1/10 avg), 100% citation accuracy, and sub-second latency across 20 real-world engineering queries.
6. 🏭 **Plant Workspaces Selection Hub**: Dedicated workspace manager (`workspaces.html`) showing live vector store counts & indexed document listings.

---

## 📁 Repository Structure

```text
├── server.py                  # Python Flask Command OS Server & REST API (Port 8080)
├── index.html                 # Main Product Landing Page with Holographic Typewriter Simulation
├── workspaces.html            # Plant Workspaces Selection Hub
├── dashboard.html             # Full-Screen Industrial Command OS Workspace
├── requirements.txt           # Python dependencies
├── .env.example               # Template environment configuration file
├── src/
│   ├── ingestion/
│   │   ├── pdf_loader.py      # Extract and chunk text-native PDF manuals
│   │   ├── ocr_loader.py      # Preprocess and OCR scanned manuals
│   │   └── excel_loader.py    # Row-by-row natural serialization for CSV logs
│   ├── retrieval/
│   │   ├── vectorstore.py     # ChromaDB manager using sentence-transformers (all-MiniLM-L6-v2)
│   │   └── retriever.py       # Hybrid retrieval, tag filtering & local BM25 re-ranking
│   ├── knowledge_graph/
│   │   └── graph_builder.py   # NetworkX graph construction & Pyvis Dark Cyber HTML export
│   └── agents/
│       ├── copilot.py         # Conversational RAG copilot chain (Groq Llama-3.1-8B)
│       ├── rca_agent.py       # Multi-source Root Cause Analysis diagnostic engine
│       └── compliance_agent.py# Regulatory safety audit scanning engine
├── data/
│   ├── raw/                   # Raw manuals (PDFs) and incident/maintenance logs (CSVs)
│   └── processed/
│       ├── chromadb/          # Persistent vector database
│       └── benchmark_results.json # Pre-computed 20-question evaluation dataset
├── docs/
│   ├── architecture diagram.png       # High-resolution system architecture blueprint
│   ├── architecture.md               # Detailed 5-tier pipeline specification
│   ├── presentation_deck_outline.md  # 10-slide submission deck outline
│   ├── demo_video_script.md          # Scene-by-scene video script & narration guide
│   ├── detailed_design_document.md   # Comprehensive technical design document
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
git clone https://github.com/Aadi1659/NexusPlantAI.git
cd NexusPlantAI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Launch the Industrial Command OS Server
```bash
python server.py
```
Open your browser at **`http://localhost:8080`**.

* **Main Landing Page**: `http://localhost:8080/`
* **Workspaces Selection Hub**: `http://localhost:8080/workspaces.html`
* **Command OS Workspace**: `http://localhost:8080/dashboard.html`

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
