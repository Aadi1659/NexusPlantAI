# Project Milestones & Progress Checklist

## Week 1 Milestone: Ingestion Pipeline & Terminal RAG
- [x] Create loaders: PDF (`pdf_loader.py`), OCR (`ocr_loader.py`), and CSV Logs (`excel_loader.py`)
- [x] Initialize ChromaDB collections (`technical_docs` and `maintenance_records`)
- [x] Build hybrid retriever with BM25 re-ranking
- [x] Create terminal copilot CLI
- [x] Verify basic RAG querying and attribute citations

## Week 2 Milestone: Copilot UI & RCA Agent
- [x] Refactor Copilot chain using LangChain LCEL (Query Analysis, Context Assembly, Citation formatting)
- [x] Implement Root Cause Analysis (RCA) Intelligence Agent (`rca_agent.py`)
- [x] Implement NetworkX/Pyvis interactive knowledge graph builder (`graph_builder.py`)
- [x] Assemble Command OS UI (`server.py` + `index.html` + `workspaces.html` + `dashboard.html`)
- [x] Establish evaluation suite with 20 Q&A pairs (`run_benchmark.py`)

## Week 3 Milestone: Quality & Regulatory Compliance Auditor
- [x] Design log scanning and anomaly pre-filtering engine
- [x] Build regulatory document lookup matching incident scopes
- [x] Develop LLM compliance synthesis and notification form drafting (`compliance_agent.py`)
- [x] Integrate `Compliance Auditor` tab into Command OS dashboard (`dashboard.html`)
- [x] Create automated scanner tests (`test_compliance.py`)
