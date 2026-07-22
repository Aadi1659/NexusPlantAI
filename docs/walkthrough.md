# Walkthrough Report: NexusPlant AI Industrial Command OS

This walkthrough summarizes the implementation, verification steps, and dashboard integration of **NexusPlant AI (Industrial Command OS)**. The platform is fully feature-complete, integrating conversational copilot Q&A, RCA failure diagnostics, relational asset network graphs, automated safety compliance audits, and system benchmarks under a unified full-screen Command OS workspace.

---

## What Was Accomplished

1. **Compliance Scanning Engine (`compliance_agent.py`)**:
    * **Anomaly Pre-filtering**: Reads `maintenance_log_synthetic.csv` and `near_miss_incident_log_synthetic.csv` using Pandas to extract high-risk compliance events (e.g., Emergency repairs with significant downtime, safety incidents with injuries, or unresolved hazards).
    * **Regulatory Semantic Search**: Queries the ChromaDB `technical_docs` collection (retrieving sections from `factory_acta1948-63.pdf`, `hsg245.pdf`, and safety occurrence guides) to locate safety directives governing the incident.
    * **Auditor Reasoning Loop**: Prompts Groq LPU (Llama-3.1-8B-Instant) to assess the anomaly against the retrieved safety acts, identify violations, assign risk severity (Critical, Major, Minor), and cite the specific section of the Act.
    * **Notification Draft Generator**: Auto-generates a pre-filled compliance notification form formatted according to official standards (e.g. RIDDOR incident report or Factories Act Form F-18 format) for easy copy-pasting.

2. **Command OS Interface (`server.py` + `dashboard.html` + `workspaces.html` + `index.html`)**:
    * **Landing Page (`index.html`)**: Product showcase featuring continuous holographic console simulation loop and 3D interactive module cards.
    * **Workspace Selection Hub (`workspaces.html`)**: Dedicated plant workspace selector showing live vector store counts & indexed document listings.
    * **Command OS Workspace (`dashboard.html`)**: Full-screen workspace featuring:
        * **RAG Engineering Copilot Tab**: Formatted markdown Q&A with equipment tag filtering (`P-101`, `P-102`, `V-105`, `C-301`) and page-exact citations.
        * **RCA Agent Tab**: Prominent high-priority remediation action plan cards followed by extracted multi-source evidence micro-cards.
        * **Knowledge Graph Tab**: Pyvis Dark Cyber relational network canvas.
        * **Compliance Auditor Tab**: Fully dynamic scorecard metrics and pre-filled statutory report templates.
        * **Benchmarks Tab**: 20-question verification ledger.

3. **Automated Test Suite (`test_compliance.py`)**:
    * Created `tests/test_compliance.py` which runs the compliance scanner and audits end-to-end, validating the returned JSON payloads.

---

## Verification: How to Run & Audit

Follow these steps to run the platform locally and verify its functionality:

### 1. Run the Compliance Agent Test (Terminal)
Execute the automated test script to run the auditor locally and output a full command-line audit summary:
```bash
./venv/bin/python -m unittest tests/test_compliance.py
```

### 2. Launch the Industrial Command OS Server
Launch the server on port 8080:
```bash
./venv/bin/python server.py
```
This opens the application at `http://localhost:8080`.

### 3. Run the Safety Audit in the UI
* Navigate to **`http://localhost:8080/workspaces.html`** and click **`Launch Command OS Dashboard`**.
* Navigate to the **`Compliance Auditor`** tab.
* Click **`Run Compliance & Safety Audit`**.
* The system will scan the CSV logs, query ChromaDB, and display a scorecard showing a **Safety Score**, total gaps flagged, and the active audit records.
* Expand any flagged anomaly card (e.g., *ML-1035 - Emergency Downtime Event (Control Valve V-105)*) to read the **Audit Assessment**, the **Remediation Action**, the **Regulations Cited**, and copy the pre-filled **RIDDOR / Factories Act reporting form**.
