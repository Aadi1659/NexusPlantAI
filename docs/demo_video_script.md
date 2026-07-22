# Demo Video Script
## NexusPlant AI — Industrial Command OS (Problem Statement #8)
### Target Duration: 3.5 – 4 minutes

---

## PRE-RECORDING SETUP CHECKLIST
- [ ] Run `./venv/bin/python server.py` and confirm app loads at `http://localhost:8080`
- [ ] Open `http://localhost:8080` (Landing Page with Typewriter Simulation)
- [ ] Pre-type the RCA failure description in Notepad so you can paste it quickly
- [ ] Set browser zoom to 90% so all UI cards are visible without scrolling
- [ ] Use a screen recorder at 1920x1080 (Loom, OBS, or QuickTime)

---

## [SCENE 1] — Title Card & Landing Page
**Duration: 0:00 – 0:30**
**On Screen**: Show the `index.html` main landing page. Point to the **Holographic Command Console** auto-typing simulation loop and hover over the 3D feature module cards.

**Voiceover**:
> "Industrial plants run on knowledge — OEM manuals, safety logs, maintenance records, and regulatory acts. But in most facilities, that knowledge is trapped across disconnected silos. We built NexusPlant AI — an autonomous RAG-driven Industrial Command OS to unify all plant knowledge into a single sub-second operational brain."

---

## [SCENE 2] — Workspace Selection Hub
**Duration: 0:30 – 1:00**
**On Screen**: Click **Login to OS** -> Show `workspaces.html` (Plant Workspaces Selection Hub). Show live vector store document listings (14 PDFs, 2 CSVs).

**Voiceover**:
> "Here in the Plant Workspaces Hub, operators select active plant unit workspaces. Every document — OEM pump manuals, compressor guides, safety acts, and work orders — is vectorized into ChromaDB. Let's launch the Command OS Workspace."

**Action**: Click **Launch Command OS Dashboard →**.

---

## [SCENE 3] — RAG Engineering Copilot Tab
**Duration: 1:00 – 1:45**
**On Screen**: Open **`dashboard.html`** -> **Copilot** tab.

**Voiceover**:
> "In the Maintenance Copilot tab, a field engineer can ask any technical question in plain English. Let's filter by Pump P-101."

**Action**: Click **P-101** asset filter chip. Type:
> *"What are the common causes of high vibration in Pump P-101 and how do I fix it?"*

Hit Enter.

**Voiceover**:
> "The system performs a hybrid BM25 + dense vector search across the technical manuals. The answer is synthesized using Groq LPU Llama-3.1-8B hardware inference with exact page citations and confidence scores."

---

## [SCENE 4] — Triple-Lookup RCA Agent Tab
**Duration: 1:45 – 2:30**
**On Screen**: Click **RCA Agent** tab.

**Voiceover**:
> "When equipment fails on the plant floor, the RCA Intelligence Agent performs a multi-source diagnostic lookup."

**Action**: Click sample scenario chip **Pump P-102 Vibration & Seal Leak** and click **Generate Root Cause Analysis Report**.

**Voiceover**:
> "The agent cross-references work order logs, OEM manuals, and prior incident signatures. Notice how the Immediate Recommended Remediation Action Plan is placed prominently at the top, followed by extracted multi-source evidence micro-cards below."

---

## [SCENE 5] — Compliance Auditor Tab
**Duration: 2:30 – 3:15**
**On Screen**: Click **Compliance Auditor** tab. Click **Run Compliance & Safety Audit**.

**Voiceover**:
> "The Compliance Auditor acts as the plant's automated safety officer. It scans maintenance incident logs against the Factories Act 1948 and RIDDOR guidelines."

**Action**: Scroll down through the 4 anomaly cards showing cited regulations, audit assessments, and pretty-printed Form F-18 statutory report templates.

**Voiceover**:
> "It calculates a safety scorecard, flags regulatory gaps, and auto-generates official statutory reporting forms ready for regulatory filing."

---

## [SCENE 6] — Knowledge Graph & Benchmarks
**Duration: 3:15 – 3:45**
**On Screen**: Show **Knowledge Graph** tab (Pyvis Dark Cyber network canvas) and **Benchmarks** tab.

**Voiceover**:
> "The Dark Cyber Knowledge Graph visually maps relationships between equipment tags, OEM manuals, failure modes, and safety acts. Finally, our 20-question Benchmark Suite proves 100% citation accuracy and sub-second response times."

---

## [SCENE 7] — Closing
**Duration: 3:45 – 4:00**
**On Screen**: Return to landing page or GitHub repo.

**Voiceover**:
> "NexusPlant AI — One platform, three agents, instant access to the collective knowledge of an entire plant. Thank you."

---

## RECORDING TIPS

| Tip | Detail |
|---|---|
| **Pace** | Speak slowly and deliberately (~130 words per minute) |
| **Mouse** | Move the cursor smoothly without rapid jitter |
| **Length** | Keep final video between 3.5 and 4 minutes |
