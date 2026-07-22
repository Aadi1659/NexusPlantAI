import os
import sys
import time
import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Append workspace root directly
sys.path.append("/Users/aadityadevsharma/Documents/hackathon")

from src.agents.copilot import query_copilot
from src.agents.rca_agent import run_rca_analysis
from src.agents.compliance_agent import run_compliance_audit
from src.knowledge_graph.graph_builder import build_knowledge_graph, HTML_PATH
from src.retrieval.vectorstore import get_collection

# --- Page Setup ---
st.set_page_config(
    page_title="NexusPlant AI | Industrial Knowledge Intelligence Command OS",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling for Modern Cyber Industrial Command OS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Background Canvas */
.stApp {
    background: radial-gradient(circle at 50% -20%, #0D1424 0%, #060911 70%, #030509 100%) !important;
    color: #F8FAFC;
}

/* Top Navigation Header */
.top-nav {
    background: rgba(13, 19, 34, 0.85);
    border: 1px solid rgba(255, 153, 0, 0.3);
    border-radius: 16px;
    padding: 16px 24px;
    margin-bottom: 20px;
    backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.top-brand {
    font-size: 1.8rem;
    font-weight: 900;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #FFFFFF 0%, #FFB800 50%, #FF9900 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Telemetry Pills */
.telemetry-pill {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 153, 0, 0.25);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    color: #FFB800;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.telemetry-pill-success {
    border-color: rgba(0, 255, 157, 0.3);
    color: #00FF9D;
}

/* Badge styling */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    margin-right: 8px;
}
.badge-high { background-color: #10B981; color: white; }
.badge-medium { background-color: #F59E0B; color: black; }
.badge-low { background-color: #EF4444; color: white; }

.badge-risk-high { background-color: #EF4444; color: white; }
.badge-risk-medium { background-color: #F59E0B; color: black; }
.badge-risk-low { background-color: #10B981; color: white; }

/* Citation Box */
.citation-box {
    background-color: #0B0F19;
    border: 1px solid rgba(255, 153, 0, 0.25);
    border-radius: 10px;
    padding: 12px;
    margin-top: 8px;
    margin-bottom: 8px;
}

.citation-header {
    font-weight: 700;
    color: #FFB800;
    font-size: 0.85rem;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 4px;
}

.citation-text {
    font-size: 0.82rem;
    color: #CBD5E0;
    background-color: #05070B;
    padding: 10px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    overflow-x: auto;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

/* Streamlit Native Tab Styling */
div[data-baseweb="tab-list"] {
    background-color: rgba(13, 19, 34, 0.8) !important;
    border-radius: 12px !important;
    padding: 6px !important;
    border: 1px solid rgba(255, 153, 0, 0.25) !important;
    gap: 8px !important;
}

button[data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #94A3B8 !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 10px 20px !important;
}

button[aria-selected="true"] {
    background: linear-gradient(135deg, #FF9900 0%, #D97706 100%) !important;
    color: #060911 !important;
    box-shadow: 0 4px 14px rgba(255, 153, 0, 0.3) !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #060911 !important;
    border-right: 1px solid rgba(255, 153, 0, 0.2) !important;
}

/* Auth Login Container */
.login-box {
    max-width: 440px;
    margin: 60px auto;
    background: rgba(13, 19, 34, 0.9);
    border: 1px solid rgba(255, 153, 0, 0.4);
    border-radius: 24px;
    padding: 36px;
    box-shadow: 0 0 40px rgba(255, 153, 0, 0.15);
    backdrop-filter: blur(20px);
}
</style>
""", unsafe_allow_html=True)

# --- Session State Initializations ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_tag" not in st.session_state:
    st.session_state.active_tag = None
if "last_citations" not in st.session_state:
    st.session_state.last_citations = []
if "rca_result" not in st.session_state:
    st.session_state.rca_result = None
if "compliance_results" not in st.session_state:
    st.session_state.compliance_results = None

# --- Helper Functions ---
@st.cache_data(show_spinner=False)
def get_ingested_files():
    tech_files = set()
    maint_files = set()
    try:
        tech_col = get_collection("technical_docs")
        tech_data = tech_col.get(include=["metadatas"])
        if tech_data and "metadatas" in tech_data:
            for meta in tech_data["metadatas"]:
                if meta.get("source_file"):
                    tech_files.add(meta["source_file"])
    except Exception:
        pass
        
    try:
        maint_col = get_collection("maintenance_records")
        maint_data = maint_col.get(include=["metadatas"])
        if maint_data and "metadatas" in maint_data:
            for meta in maint_data["metadatas"]:
                if meta.get("source_file"):
                    maint_files.add(meta["source_file"])
    except Exception:
        pass
        
    return sorted(list(tech_files)), sorted(list(maint_files))

# ==============================================================================
# VIEW 1: AUTHENTICATION LOGIN SCREEN
# ==============================================================================
if not st.session_state.authenticated:
    st.markdown("""
    <div class="login-box">
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #FF9900, #8B5CF6); border-radius: 14px; display: inline-flex; align-items: center; justify-content: center; color: white; font-size: 22px; margin-bottom: 12px; box-shadow: 0 8px 24px rgba(255,153,0,0.3);">
                ⚙️
            </div>
            <h2 style="font-size: 1.6rem; font-weight: 800; margin: 0; color: #FFFFFF;">NexusPlant AI</h2>
            <p style="font-size: 0.82rem; font-family: monospace; color: #94A3B8; margin-top: 4px;">Industrial Command OS v3.0 Authentication</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Click button to auto-fill demo credentials:**")
    if st.button("⚡ Auto-Fill Demo Credentials (operator@refinery4.nexusplant.ai)", use_container_width=True):
        st.session_state.demo_email = "operator@refinery4.nexusplant.ai"
        st.session_state.demo_pass = "nexus2026password"
        
    email = st.text_input("User Email", value=st.session_state.get("demo_email", ""))
    password = st.text_input("Password", type="password", value=st.session_state.get("demo_pass", ""))
    
    if st.button("Authenticate & Access Command OS →", type="primary", use_container_width=True):
        if email.strip():
            with st.spinner("Authenticating credentials & initializing neural brain..."):
                time.sleep(0.5)
                st.session_state.authenticated = True
                st.rerun()
        else:
            st.error("Please enter user email.")
            
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# VIEW 2: FULL-SCREEN INDUSTRIAL COMMAND OS WORKSPACE
# ==============================================================================
else:
    # --- SIDEBAR PANEL ---
    st.sidebar.markdown("### 🧠 NexusPlant Library")

    with st.sidebar.expander("📤 Ingest New File", expanded=False):
        uploaded_file = st.file_uploader("Upload PDF or CSV", type=["pdf", "csv", "xlsx", "xls"], label_visibility="collapsed")
        if uploaded_file is not None:
            raw_dir = "/Users/aadityadevsharma/Documents/hackathon/data/raw"
            os.makedirs(raw_dir, exist_ok=True)
            save_path = os.path.join(raw_dir, uploaded_file.name)
            
            if not os.path.exists(save_path):
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
                with st.status("Indexing document live...", expanded=True) as status:
                    try:
                        ext = uploaded_file.name.split('.')[-1].lower()
                        if ext == 'pdf':
                            from src.ingestion.pdf_loader import load_pdf, chunk_documents
                            docs = load_pdf(save_path)
                            chunks = chunk_documents(docs)
                            from src.retrieval.vectorstore import add_chunks
                            add_chunks("technical_docs", chunks)
                            status.update(label=f"Ingested {len(chunks)} PDF chunks!", state="complete", icon="✅")
                        else:
                            from src.ingestion.excel_loader import load_csv_or_excel
                            records = load_csv_or_excel(save_path)
                            from src.retrieval.vectorstore import add_chunks
                            add_chunks("maintenance_records", records)
                            status.update(label=f"Ingested {len(records)} log records!", state="complete", icon="✅")
                        
                        st.toast(f"Indexed {uploaded_file.name} successfully!", icon="🎉")
                        st.cache_data.clear()
                    except Exception as e:
                        status.update(label=f"Ingestion failed: {e}", state="error", icon="❌")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Indexed Corpus")
    tech_docs, maint_docs = get_ingested_files()

    with st.sidebar.expander("Technical Manuals (PDFs)", expanded=True):
        if tech_docs:
            for doc in tech_docs:
                st.markdown(f"📄 `<span style='color:#FFB800;'>{doc}</span>`", unsafe_allow_html=True)

    with st.sidebar.expander("Maintenance Logs (CSV)", expanded=True):
        if maint_docs:
            for doc in maint_docs:
                st.markdown(f"📊 `<span style='color:#00FF9D;'>{doc}</span>`", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Asset Filter Chips")
    equip_tags = ["P-101", "P-102", "V-105", "V-203", "C-301"]
    cols = st.sidebar.columns(3)
    for idx, tag in enumerate(equip_tags):
        col = cols[idx % 3]
        is_active = st.session_state.active_tag == tag
        label = f"🟢 {tag}" if is_active else tag
        if col.button(label, key=f"chip_{tag}", use_container_width=True):
            st.session_state.active_tag = None if is_active else tag
            st.rerun()

    if st.session_state.active_tag:
        st.sidebar.info(f"Retrieval constrained to: **{st.session_state.active_tag}**")
        if st.sidebar.button("Clear Tag Filter", type="primary", use_container_width=True):
            st.session_state.active_tag = None
            st.rerun()

    # --- TOP WORKSPACE NAVBAR HEADER ---
    head_col1, head_col2 = st.columns([4, 1.2])
    with head_col1:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:16px; margin-bottom:10px;">
            <span class="top-brand">NexusPlant AI</span>
            <span class="telemetry-pill telemetry-pill-success">🟢 REAL GROQ & CHROMADB ONLINE</span>
            <span class="telemetry-pill">👤 Operator: Senior Reliability Engineer (Unit 4)</span>
        </div>
        """, unsafe_allow_html=True)
    with head_col2:
        st.write("") # spacer
        if st.button("🔴 Logout of OS", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # --- 5 WORKSPACE TABS ---
    tab_chat, tab_rca, tab_graph, tab_compliance, tab_benchmark = st.tabs([
        "💬 Maintenance Copilot", 
        "🔍 RCA Intelligence Agent", 
        "🕸️ Knowledge Graph Network",
        "📋 Compliance Auditor",
        "📊 System Benchmark Dashboard"
    ])

    # ==========================================================================
    # TAB 1: MAINTENANCE COPILOT
    # ==========================================================================
    with tab_chat:
        col_h, col_b = st.columns([5, 1.2])
        with col_h:
            st.subheader("💬 Industrial Engineering Copilot")
            st.caption("Ask real-time questions about asset manuals, maintenance logs, and safety procedures.")
        with col_b:
            st.write("")
            if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
                st.session_state.messages = []
                st.session_state.last_citations = []
                st.rerun()

        # Display Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and "confidence" in msg:
                    c_class = "badge-high" if msg["confidence"] == "High" else ("badge-medium" if msg["confidence"] == "Medium" else "badge-low")
                    st.markdown(f"<span class='badge {c_class}'>Confidence: {msg['confidence']}</span> <span style='font-size:0.8rem; color:#888; font-family:monospace;'>⏱️ {msg['latency']:.2f}s</span>", unsafe_allow_html=True)
                    
                    if msg.get("sources"):
                        with st.expander("🔍 Cited Sources & Snippets", expanded=False):
                            for s in msg["sources"]:
                                st.markdown(f"""
                                <div class="citation-box">
                                    <div class="citation-header">📄 {s['source_file']} [{s['location']}]</div>
                                    <div class="citation-text">{s['text']}</div>
                                </div>
                                """, unsafe_allow_html=True)

        # Real Chat Input
        if prompt := st.chat_input("Enter your engineering or troubleshooting question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.chat_message("assistant"):
                with st.spinner("Searching ChromaDB and synthesizing response via ChatGroq Llama-3.1-8B..."):
                    result = query_copilot(prompt, equipment_tag=st.session_state.active_tag)
                    
                st.markdown(result["answer"])
                c_class = "badge-high" if result["confidence"] == "High" else ("badge-medium" if result["confidence"] == "Medium" else "badge-low")
                st.markdown(f"<span class='badge {c_class}'>Confidence: {result['confidence']}</span> <span style='font-size:0.8rem; color:#888; font-family:monospace;'>⏱️ {result['latency']:.2f}s</span>", unsafe_allow_html=True)
                
                if result.get("sources"):
                    with st.expander("🔍 Cited Sources & Snippets", expanded=False):
                        for s in result["sources"]:
                            st.markdown(f"""
                            <div class="citation-box">
                                <div class="citation-header">📄 {s['source_file']} [{s['location']}]</div>
                                <div class="citation-text">{s['text']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "confidence": result["confidence"],
                    "sources": result["sources"],
                    "latency": result["latency"]
                })

    # ==========================================================================
    # TAB 2: RCA INTELLIGENCE AGENT
    # ==========================================================================
    with tab_rca:
        st.subheader("🔍 Root Cause Analysis (RCA) Intelligence Agent")
        st.caption("Provide an equipment failure description. The agent executes triple lookups across manuals, maintenance logs, and incidents.")
        
        st.markdown("**Click an example to auto-fill failure description:**")
        ex1 = "Pump P-102 is vibrating excessively and has a minor oil leak from the bearing housing."
        ex2 = "Gate Valve V-203 is leaking steam from the packing gland during pressure peaks."
        
        col_ex1, col_ex2 = st.columns(2)
        if col_ex1.button(f"Example 1: {ex1[:45]}...", use_container_width=True):
            st.session_state.rca_input = ex1
        if col_ex2.button(f"Example 2: {ex2[:45]}...", use_container_width=True):
            st.session_state.rca_input = ex2
            
        failure_desc = st.text_area("Describe the equipment failure:", value=st.session_state.get("rca_input", ""), height=100)
        
        if st.button("Generate Root Cause Analysis Report", type="primary"):
            if not failure_desc.strip():
                st.warning("Please provide a failure description.")
            else:
                with st.spinner("Executing multi-step RCA Agent reasoning loop..."):
                    rca_result = run_rca_analysis(failure_desc)
                    st.session_state.rca_result = rca_result
                    
        if st.session_state.rca_result:
            res = st.session_state.rca_result
            report = res["report"]
            
            st.success("Root Cause Analysis Generated!")
            st.markdown(f"**Agent Latency:** `{res['latency']:.2f} seconds`")
            
            rca_subtabs = st.tabs(["Summary Report", "Supporting Evidence", "Recommended Actions", "Similar Past Cases"])
            
            with rca_subtabs[0]:
                st.markdown(f"### RCA Report Summary: {report.get('equipment', 'Equipment')}")
                c_class = "badge-high" if report.get("confidence") == "High" else ("badge-medium" if report.get("confidence") == "Medium" else "badge-low")
                r_class = "badge-risk-high" if report.get("recurrence_risk") == "High" else ("badge-risk-medium" if report.get("recurrence_risk") == "Medium" else "badge-risk-low")
                
                st.markdown(f"""
                <div style='margin-bottom:15px;'>
                    <span class='badge {c_class}'>Confidence: {report.get('confidence')}</span>
                    <span class='badge {r_class}'>Recurrence Risk: {report.get('recurrence_risk')}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**Failure Mode Identified:** `{report.get('failure_mode')}`")
                st.markdown("#### Root Cause Hypothesis")
                st.info(report.get("root_cause_hypothesis", "No hypothesis synthesized."))
                
            with rca_subtabs[1]:
                st.markdown("### Supporting Evidence & Findings")
                evidence = report.get("supporting_evidence", [])
                if evidence:
                    for idx, ev in enumerate(evidence):
                        st.markdown(f"**{idx+1}. {ev.get('source')}**")
                        st.markdown(f"> {ev.get('finding')}")
                else:
                    st.caption("No supporting evidence extracted.")
                    
            with rca_subtabs[2]:
                st.markdown("### Recommended Remediation & Action Items")
                st.write(report.get("recommended_action", "No recommendations synthesized."))
                
            with rca_subtabs[3]:
                st.markdown("### Similar Past Cases & Incidents")
                cases = res.get("incident_cases", [])
                if cases:
                    for idx, case in enumerate(cases):
                        meta = case["metadata"]
                        st.markdown(f"**Case [{idx+1}]: {meta.get('source_file')} - ID: {meta.get('record_id')}**")
                        st.markdown(f"```text\n{case['text']}\n```")
                else:
                    st.caption("No past incidents or maintenance records retrieved.")

    # ==========================================================================
    # TAB 3: KNOWLEDGE GRAPH NETWORK
    # ==========================================================================
    with tab_graph:
        st.subheader("🕸️ Interactive Plant Assets Knowledge Graph")
        st.caption("Draggable, zoomable network graph mapping Equipment tags, Technical Manuals, and Failure Modes.")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Rebuild Knowledge Graph", use_container_width=True):
                with st.spinner("Regenerating network relationships..."):
                    build_knowledge_graph()
                st.toast("Knowledge Graph updated successfully!", icon="🕸️")
                
            st.markdown("""
            **Color Legend:**
            - 🟣 **Purple**: Equipment Node (e.g. P-101)
            - 🔵 **Blue**: Document Manual Node (e.g. 811_iom.pdf)
            - 🔴 **Red**: Failure Mode Node (e.g. Seal Leak)
            
            **Edges:**
            - **HASMANUAL**: Link to Manual
            - **HASFAILURE**: Link to Failure Mode
            """)
            
        with col2:
            if not os.path.exists(HTML_PATH):
                build_knowledge_graph()
                
            if os.path.exists(HTML_PATH):
                with open(HTML_PATH, 'r') as f:
                    html_data = f.read()
                components.html(html_data, height=600, scrolling=True)
            else:
                st.error("Knowledge Graph HTML file not found.")

    # ==========================================================================
    # TAB 4: COMPLIANCE AUDITOR
    # ==========================================================================
    with tab_compliance:
        st.subheader("📋 Quality & Regulatory Compliance Auditor")
        st.caption("Scan maintenance logs and incident reports to audit compliance against safety standards (Factories Act, HSG245, RIDDOR).")
        
        if st.button("Run Compliance & Safety Audit", type="primary", use_container_width=True):
            with st.spinner("Scanning logs and auditing against safety guidelines..."):
                st.session_state.compliance_results = run_compliance_audit()
                st.toast("Compliance Audit Completed!", icon="📋")
                
        if st.session_state.compliance_results:
            res = st.session_state.compliance_results
            summary = res["summary"]
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Scanned Logs", f"{summary['total_scanned']}")
            score = summary['safety_score_percentage']
            m2.metric("Safety Score", f"{score:.1f}%")
            m3.metric("Gaps Flagged", f"{summary['total_gaps']}")
            m4.metric("Auditor Latency", f"{res['latency']:.2f}s")
            
            st.markdown("### ⚠️ Identified Compliance Gaps & Violations")
            
            for idx, item in enumerate(res["results"]):
                anomaly = item["anomaly"]
                audit = item["audit"]
                
                sev = audit.get("severity", "Minor")
                if sev.lower() == "critical":
                    badge_style = "background-color: #EF4444; color: white;"
                elif sev.lower() == "major":
                    badge_style = "background-color: #F59E0B; color: black;"
                else:
                    badge_style = "background-color: #10B981; color: white;"
                    
                with st.expander(f"Anomaly [{idx+1}]: {anomaly['id']} - {anomaly['type']} ({anomaly['asset']})", expanded=(idx==0)):
                    st.markdown(f"""
                    <div style='margin-bottom: 12px;'>
                        <span style='display: inline-block; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; {badge_style}'>
                            {sev}
                        </span>
                        <span style='margin-left: 10px; font-weight: 700; color: #FFB800; font-family: monospace;'>
                            Cited: {audit.get('regulations_cited')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**Anomaly Event details:**")
                    st.write(anomaly["details"])
                    
                    st.markdown("**Audit Assessment:**")
                    st.info(audit.get("audit_assessment", "No assessment provided."))
                    
                    st.markdown("**Remediation / Corrective Action:**")
                    st.success(audit.get("remediation", "No remediation actions specified."))
                    
                    st.markdown("**Generated Regulatory Notification Form:**")
                    st.code(audit.get("reporting_template", ""), language="text")

    # ==========================================================================
    # TAB 5: SYSTEM BENCHMARK DASHBOARD
    # ==========================================================================
    with tab_benchmark:
        st.subheader("📊 System Benchmark Dashboard")
        st.caption("Evaluation metrics showing average RAG accuracy, latency, and citation match rates based on a 20 Q&A corpus.")
        
        json_path = "/Users/aadityadevsharma/Documents/hackathon/data/processed/benchmark_results.json"
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                bench_data = json.load(f)
                
            summary = bench_data["summary"]
            results = bench_data["results"]
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Evaluated Queries", f"{summary['total_queries']}")
            m2.metric("Avg Quality Score", f"{summary['average_score']:.2f} / 5.0")
            m3.metric("Citation Accuracy", f"{summary['citation_accuracy_rate']:.1f}%")
            m4.metric("Avg Latency", f"{summary['average_latency_sec']:.2f}s")
            
            st.markdown("### Metrics Distributions")
            chart_data = pd.DataFrame([
                {"Query ID": f"Q{r['id']}", "Score (1-5)": r["score"], "Latency (s)": r["latency"]}
                for r in results
            ])
            st.bar_chart(chart_data, x="Query ID", y="Score (1-5)", color="#EF4444")
            st.bar_chart(chart_data, x="Query ID", y="Latency (s)", color="#FF9900")
            
            st.markdown("### Detailed Benchmark Results")
            table_rows = []
            for r in results:
                table_rows.append({
                    "ID": r["id"],
                    "Query": r["query"],
                    "Score": f"{r['score']}/5",
                    "Latency": f"{r['latency']:.2f}s",
                    "Cited correctly?": "✅ Yes" if r["citation_accurate"] else "❌ No",
                    "Documents Cited": ", ".join(r["cited_sources"]) if r["cited_sources"] else "None"
                })
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True)
        else:
            st.warning("Benchmark results JSON file not found.")
