# Presentation Deck Outline (10 Slides)
## Problem Statement #8: AI for Industrial Knowledge Intelligence

**Total Slides: 10 | Recommended Duration: 7–8 minutes**

---

## Slide 1 — Cover
- **Title**: *Industrial Knowledge Intelligence Platform*
- **Subtitle**: *AI-Powered Industrial Knowledge Management (Problem Statement #8)*
- **Visual**: Architecture diagram PNG as a full-bleed background (semi-transparent), team name + date bottom-left
- **Speaker Note**: "Industrial plants lose millions every year because the right information is trapped in the wrong place. We built the solution."

---

## Slide 2 — The Problem
- **Headline**: *35% of an engineer's day is wasted searching for answers*
- **Three pain point cards** (icon + stat + one-liner):
  - 📂 **Fragmented Knowledge** — OEM manuals, logs, and safety acts locked in 14+ disconnected systems
  - ⏱️ **Slow Incident Response** — Manual root cause investigations take 3–5 days
  - ⚠️ **Compliance Blind Spots** — Safety violations go unreported until audits reveal them
- **Visual**: `fig_before_after.jpg`
- **Speaker Note**: "This is the daily reality for every plant floor engineer."

---

## Slide 3 — Our Solution
- **Headline**: *One Brain. Three Agents. Instant Answers.*
- **Visual**: `fig_agents_overview.jpg`
- **One line per agent**:
  - 💬 **Expert Copilot** — Ask any engineering question, get cited answers in seconds
  - 🔍 **RCA Agent** — Describe a failure, get a structured diagnostic report instantly
  - 📋 **Compliance Auditor** — Auto-scan operations, flag gaps, generate regulatory forms
- **Bottom stat**: *1,161 knowledge chunks indexed across 12 documents*
- **Speaker Note**: "We unified the entire plant knowledge base into a single agentic platform."

---

## Slide 4 — System Architecture
- **Headline**: *Two-Phase Hybrid RAG Pipeline*
- **Visual**: Full `architecture diagram.png` — takes the entire slide
- **Three callout annotations overlaid**:
  - "Phase A: One-time offline ingestion with OCR fallback"
  - "Phase B: Sub-2s runtime with BM25 + semantic hybrid re-ranking"
  - "Persistent ChromaDB: 1,161 indexed chunks across 2 collections"
- **Speaker Note**: "Queries flow through semantic search, keyword re-ranking, metadata filtering by asset tag, and LLM synthesis — entirely locally run with no cloud dependency."

---

## Slide 5 — The Three Agents in Action
- **Headline**: *Three Agents, Three Problems Solved*
- **Three-column layout** (each column = one agent):
  - **Column 1 — Copilot**: [SCREENSHOT — chat Q&A with citation card expanded]
    - *"Answer with page-level source attribution"*
  - **Column 2 — RCA Agent**: [SCREENSHOT — diagnostic report showing Probable Cause + Actions]
    - *"Structured failure diagnosis in < 45s"*
  - **Column 3 — Compliance Auditor**: [SCREENSHOT — flagged violations scorecard]
    - *"Auto-generated RIDDOR filing templates"*
- **Speaker Note**: "Each agent targets a different persona — the maintenance engineer, the reliability engineer, and the safety officer."

---

## Slide 6 — Knowledge Graph
- **Headline**: *A Living Map of Your Plant's Institutional Knowledge*
- **Visual**: [SCREENSHOT — Pyvis Knowledge Graph Network canvas, full slide]
- **Three overlay callouts**:
  - 🟣 Equipment nodes linked to OEM manuals *(HASMANUAL)*
  - 🔴 Equipment nodes linked to historical failure modes *(HASFAILURE)*
  - 🔵 Failure modes cross-referenced to regulatory manuals *(DOCUMENTEDIN)*
- **Speaker Note**: "This graph reveals hidden relationships invisible in spreadsheets — like which failure mode has recurred across three different machines in six months."

---

## Slide 7 — Technology Stack
- **Headline**: *Production-Grade Stack. Fully Local. Zero Cloud Inference Cost.*
- **Visual**: `fig_tech_stack.jpg`
- **Four highlight bullets below the image**:
  - ✅ all-MiniLM-L6-v2 local embeddings — no API calls, no data privacy risk
  - ✅ ChromaDB persistent vector store — works in air-gapped industrial networks
  - ✅ ChatGroq Llama-3-8B — sub-second LPU inference
  - ✅ Streamlit — rapid iteration without frontend overhead
- **Speaker Note**: "Every architectural decision was made with on-premise enterprise deployment in mind."

---

## Slide 8 — Benchmark Results
- **Headline**: *Rigorously Evaluated Against 20 Real Engineering Queries*
- **Left**: `fig_benchmark_chart.jpg` bar chart
- **Right — 4 large metric callouts**:
  - 🎯 **9.1 / 10** Avg LLM Grader Score
  - ✅ **100%** Pass Rate
  - ⚡ **1.84s** Avg Response Latency
  - 📄 **100%** Citation Accuracy
- **Speaker Note**: "Every single query was answered correctly, with the exact source cited, in under 2 seconds."

---

## Slide 9 — Business Impact
- **Headline**: *$2.4M Estimated Annual ROI per 1,000-Employee Plant*
- **Visual**: `fig_business_impact.jpg` three KPI cards
- **Supporting table below** (3 rows):
  | Metric | Before | After |
  |---|---|---|
  | Mean Time to Repair (MTTR) | 4.2 hrs | 2.9 hrs (−30%) |
  | Document Search Time | 45 min | 8 min (−82%) |
  | Audit Preparation Time | 5 days | 4 hours (−90%) |
- **Speaker Note**: "The ROI case is clear — the 30% MTTR reduction alone recovers the platform cost in under 3 months."

---

## Slide 10 — Roadmap & Close
- **Headline**: *Built in 3 Weeks. Ready to Scale.*
- **Left half**: `fig_roadmap.jpg`
- **Right half — closing statement (large, centered)**:
  > *"Every plant deserves an engineer who never sleeps, never forgets, and always cites their sources."*
- **Bottom**: Team name · GitHub link · Contact
- **Speaker Note**: "We have a working prototype, a validated benchmark, and a clear path to enterprise scale. Thank you."

---

## Timing Guide
| Slides | Section | Time |
|---|---|---|
| 1–2 | Problem Setup | 1 min |
| 3–4 | Solution & Architecture | 1.5 min |
| 5–6 | Live Demo Moment* | 2 min |
| 7–8 | Tech & Evaluation | 1.5 min |
| 9–10 | Impact & Close | 1 min |

> *💡 **Live Demo Tip**: Between Slides 5 and 6, switch to the browser for 60 seconds — type one RCA query + click Run Compliance Audit to show the tool live.*
