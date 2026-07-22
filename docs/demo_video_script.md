# Demo Video Script
## Industrial Knowledge Intelligence Platform (Problem Statement #8)
### Target Duration: 3.5 – 4 minutes

---

## PRE-RECORDING SETUP CHECKLIST
- [ ] Run `./venv/bin/python -m streamlit run app.py` and confirm app loads at localhost:8501
- [ ] Pre-type the RCA failure description in Notepad so you can paste it quickly
- [ ] Open the Compliance Auditor tab and confirm the audit has already run (so results show instantly)
- [ ] Set browser zoom to 90% so all tabs are visible without scrolling
- [ ] Use a screen recorder at 1920x1080. Record system audio off, narrate separately.
- [ ] Recommended tool: Loom, OBS, or QuickTime

---

## [SCENE 1] — Title Card
**Duration: 0:00 – 0:10**
**On Screen**: Fade in with title card:
> *"Industrial Knowledge Intelligence Platform"*
> *"AI-Powered Industrial Knowledge Management (Problem Statement #8)"*

**Voiceover**:
> "Industrial plants run on knowledge — maintenance manuals, safety logs, equipment records, and regulatory acts. But in most facilities, that knowledge is fragmented across dozens of disconnected systems. We built an AI platform to change that."

---

## [SCENE 2] — App Overview
**Duration: 0:10 – 0:30**
**On Screen**: Show the full Streamlit app. Slowly pan across the 5 tab names at the top. Point to the sidebar showing the indexed document library.

**Voiceover**:
> "This is the Industrial Knowledge Intelligence Platform — a unified platform built on a hybrid RAG pipeline with three autonomous AI agents. Every document you see in this sidebar — OEM manuals, safety acts, maintenance logs — has been indexed into a persistent vector database with over 1,100 knowledge chunks. All running locally. No cloud. No API cost per query."

**Action**: Hover cursor slowly over each tab name as you say it:
> "The Maintenance Copilot. The RCA Intelligence Agent. The Knowledge Graph. The Compliance Auditor. And the Benchmark Dashboard."

---

## [SCENE 3] — Expert Copilot Tab
**Duration: 0:30 – 1:10**
**On Screen**: Click on **💬 Maintenance Copilot** tab.

**Voiceover**:
> "Let's start with the Expert Copilot. A field engineer can type any question in plain English — about a specific piece of equipment, a procedure, or a safety rule."

**Action**: Click the **P-102 chip** in the left sidebar to activate asset filter. Then type in the chat input:
> *"What are the common causes of high vibration in Pump P-102 and how do I fix it?"*

Hit Enter and wait for the response.

**Voiceover** (while response loads):
> "The system performs a hybrid search — combining semantic vector similarity with BM25 keyword matching — and retrieves the most relevant chunks from both the OEM centrifugal pump manual and the maintenance logs for this specific asset."

**Action**: Once the response appears, click **🔍 Cited Sources & Snippets** expander to show citation cards.

**Voiceover**:
> "Every answer is grounded in your actual documents. The engineer sees the exact source file, the page number, and a confidence score. No hallucinations. No guessing."

---

## [SCENE 4] — RCA Intelligence Agent Tab
**Duration: 1:10 – 2:00**
**On Screen**: Click on **🔍 RCA Intelligence Agent** tab.

**Voiceover**:
> "Now imagine a pump has just failed on the plant floor. The maintenance manager needs a root cause analysis — fast. They describe the failure here."

**Action**: Paste into the text area:
> *"Pump P-102 is vibrating excessively and has developed a minor oil leak from the bearing housing. We have had two similar incidents in the past 6 months."*

Click **Generate Root Cause Analysis Report**.

**Voiceover** (while it processes):
> "The agent runs a four-step reasoning loop. First it extracts the asset tag and failure mode. Then it simultaneously queries the maintenance log history for this pump, the OEM troubleshooting manual, and any past safety incidents involving similar failure signatures."

**Action**: Once results appear, click through the tabs — **Summary**, **Supporting Evidence**, **Recommended Actions**.

**Voiceover**:
> "The output is a fully structured diagnostic report — the probable root cause, supporting evidence from three data sources, and step-by-step corrective actions. What previously took a senior engineer two days of log reading now takes under a minute."

---

## [SCENE 5] — Compliance Auditor Tab
**Duration: 2:00 – 2:50**
**On Screen**: Click on **📋 Compliance Auditor** tab. Results should already be loaded from your pre-run.

**Voiceover**:
> "The third agent is the Compliance Auditor — the plant's automated safety officer. It scans the maintenance and incident logs, cross-references every anomaly against the Factories Act, RIDDOR, and HSE guidelines stored in the vector database, and flags violations."

**Action**: Point to the **4 metrics** at the top — Total Scanned, Safety Score, Gaps Flagged, Latency.

**Voiceover**:
> "In this scan, the agent identified 4 high-risk operational events — including emergency downtime events and open safety incident reports — and flagged all four as compliance gaps."

**Action**: Click to expand **Anomaly [1]: ML-1032 — Emergency Downtime Event (Pump P-102)**.

**Voiceover**:
> "For each gap, the agent cites the exact regulatory clause it violated..."

**Action**: Scroll down slowly to show the **Audit Assessment**, then the **Remediation**, then the **Generated Regulatory Notification Form**.

**Voiceover**:
> "...and auto-generates a pre-filled notification form — ready to submit to the regulator. Safety managers go from days of manual paperwork to a copy-paste."

---

## [SCENE 6] — Knowledge Graph Tab
**Duration: 2:50 – 3:20**
**On Screen**: Click on **🕸️ Knowledge Graph Network** tab.

**Voiceover**:
> "Finally, the Knowledge Graph gives plant managers a visual map of everything the platform knows. Equipment assets, their linked manuals, the failure modes each machine has experienced, and the regulatory documents governing them."

**Action**: Drag a few nodes around to show the interactive physics simulation. Zoom in on the Pump P-102 cluster.

**Voiceover**:
> "Every relationship here was extracted automatically from the indexed corpus. This is institutional knowledge — the kind that used to live only in the heads of retiring senior engineers — now preserved, queryable, and visual."

---

## [SCENE 7] — Benchmark Dashboard (Quick Flash)
**Duration: 3:20 – 3:35**
**On Screen**: Click on **📊 System Benchmark Dashboard** tab. Show the 4 metric cards at the top, then the bar chart.

**Voiceover**:
> "We validated the system against a curated set of 20 real engineering queries. Average LLM grader score: 9.1 out of 10. Pass rate: 100%. Average latency: under 2 seconds. Citation accuracy: 100%."

---

## [SCENE 8] — Closing
**Duration: 3:35 – 3:50**
**On Screen**: Fade back to a clean title card showing:
> *"Industrial Knowledge Intelligence Platform"*
> *"Built on: Python · Streamlit · ChromaDB · Llama-3-8B · LangChain"*
> *"1,161 chunks · 12 documents · 3 agents · 1 unified platform"*

**Voiceover**:
> "One platform. Three agents. Instant access to the collective knowledge of an entire plant. Every engineer deserves an assistant who never sleeps, never forgets, and always cites their sources. Thank you."

**Action**: Fade to black.

---

## RECORDING TIPS

| Tip | Detail |
|---|---|
| **Pace** | Speak slowly and deliberately — aim for 130 words per minute |
| **Pauses** | Add 1-second pauses after every section heading before narrating |
| **Mouse** | Move the cursor slowly and deliberately. Avoid rapid jitter. |
| **Edits** | Record each scene separately and cut together — easier than one take |
| **Music** | Add a subtle ambient background track at 10–15% volume in post |
| **Captions** | Add auto-captions in Loom or CapCut for accessibility |
| **Length** | Keep final cut under 4 minutes — judges typically watch first 3 minutes |
