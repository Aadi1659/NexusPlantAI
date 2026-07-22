import os
import re
import json
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.retrieval.vectorstore import query_vectorstore
from src.retrieval.retriever import hybrid_retrieve, extract_equipment_tags

# Load environment variables
load_dotenv()

DEFAULT_MODEL = "llama-3.1-8b-instant"

def get_chat_model(model=DEFAULT_MODEL):
    """
    Initializes and returns the ChatGroq model.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not found. Please set it in your .env file.")
    return ChatGroq(model=model, temperature=0.1, api_key=api_key)

def run_rca_analysis(failure_description, model=DEFAULT_MODEL):
    """
    Executes the multi-step Root Cause Analysis (RCA) agent flow.
    """
    start_time = time.time()
    llm = get_chat_model(model)
    
    # --- Step 1: Parse failure description ---
    parse_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert maintenance assistant.\n"
                   "Analyze the failure description and extract key search attributes.\n"
                   "Respond ONLY with a JSON object. Keys:\n"
                   "- 'equipment_tag': e.g., 'P-101', 'C-301' (string, or null if none)\n"
                   "- 'equipment_type': e.g., 'Pump', 'Compressor', 'Valve' (string, or null if none)\n"
                   "- 'failure_mode': e.g., 'Mechanical seal failure', 'Bearing failure' (string)\n"
                   "- 'keywords': List of 3-5 keywords for document search (list of strings)"),
        ("user", "Description: {description}")
    ])
    
    parse_chain = parse_prompt | llm.bind(response_format={"type": "json_object"})
    try:
        parse_response = parse_chain.invoke({"description": failure_description})
        parsed_attributes = json.loads(parse_response.content)
    except Exception as e:
        print(f"Error parsing failure description: {e}")
        # Regex fallback
        tags = extract_equipment_tags(failure_description)
        parsed_attributes = {
            "equipment_tag": tags[0] if tags else None,
            "equipment_type": "Equipment",
            "failure_mode": "Unknown Failure Mode",
            "keywords": [failure_description]
        }
        
    eq_tag = parsed_attributes.get("equipment_tag")
    eq_type = parsed_attributes.get("equipment_type") or "Equipment"
    failure_mode = parsed_attributes.get("failure_mode")
    keywords = parsed_attributes.get("keywords", [])
    
    # --- Step 2: Query maintenance records for last N work orders ---
    maint_records = []
    if eq_tag:
        # Search specifically for this equipment's maintenance history
        maint_records = query_vectorstore(
            "maintenance_records",
            query_text=f"Equipment {eq_tag} {failure_mode}",
            n_results=5,
            where_filter={"equipment_tags": eq_tag}
        )
    if not maint_records:
        # Generic query if tag is missing or database filter returned nothing
        maint_records = query_vectorstore(
            "maintenance_records",
            query_text=f"{eq_type} {failure_mode}",
            n_results=5
        )
        
    # --- Step 3: Query technical manuals for OEM troubleshooting section ---
    oem_query = f"{eq_type} {failure_mode} troubleshooting manual"
    if keywords:
        oem_query = f"{eq_type} {' '.join(keywords)} troubleshooting"
        
    tech_docs = query_vectorstore(
        "technical_docs",
        query_text=oem_query,
        n_results=4
    )
    
    # --- Step 4: Query incident corpus for similar past failures ---
    incident_query = f"incident near miss accident {failure_mode} {' '.join(keywords)}"
    incident_records = query_vectorstore(
        "maintenance_records", # CSV incident logs are also indexed in maintenance_records
        query_text=incident_query,
        n_results=4
    )
    # Filter incident records to exclude the current active work orders if possible,
    # or prioritize those with incident markers (e.g. INC- prefix in metadata['record_id'])
    incident_cases = []
    for r in incident_records:
        rec_id = r["metadata"].get("record_id", "")
        if "INC-" in rec_id or "Incident" in r["text"]:
            incident_cases.append(r)
    # Fallback to general matches if no strict incident records found
    if not incident_cases:
        incident_cases = incident_records[:3]
        
    # --- Format retrieved contexts for LLM Synthesis ---
    formatted_work_orders = []
    for idx, r in enumerate(maint_records):
        formatted_work_orders.append(f"Work Order [{idx+1}]: {r['text']}")
        
    formatted_oem = []
    for idx, r in enumerate(tech_docs):
        meta = r["metadata"]
        src = meta.get("source_file", "OEM Manual")
        page = meta.get("page_number", "Unknown Page")
        formatted_oem.append(f"OEM Ref [{idx+1}]: Source: {src}, Page {page}\nContent: {r['text']}")
        
    formatted_incidents = []
    for idx, r in enumerate(incident_cases):
        formatted_incidents.append(f"Past Incident [{idx+1}]: {r['text']}")
        
    # --- Step 5: LLM Synthesis ---
    synthesis_system_prompt = (
        "You are an industrial safety and reliability expert performing Root Cause Analysis (RCA).\n"
        "Synthesize the provided maintenance history, OEM troubleshooting guidelines, and historical incidents "
        "to formulate a comprehensive RCA report.\n"
        "You MUST respond ONLY with a JSON object. Do not include markdown wraps (like ```json). Keys:\n"
        "- 'equipment': String identifying the asset (e.g., 'Pump P-101')\n"
        "- 'failure_mode': String describing the failure mode\n"
        "- 'root_cause_hypothesis': String outlining the most likely root cause\n"
        "- 'supporting_evidence': List of objects detailing evidence from logs or manuals. Each object must have keys 'source' and 'finding'.\n"
        "- 'recommended_action': String describing remediation and preventative maintenance steps\n"
        "- 'recurrence_risk': 'High' | 'Medium' | 'Low'\n"
        "- 'confidence': 'High' | 'Medium' | 'Low'"
    )
    
    synthesis_user_prompt = (
        f"Failure Description: {failure_description}\n\n"
        f"--- RELEVANT PAST WORK ORDERS FOR THIS ASSET ---\n"
        f"{chr(10).join(formatted_work_orders) if formatted_work_orders else 'No records found.'}\n\n"
        f"--- OEM TROUBLESHOOTING SECTIONS ---\n"
        f"{chr(10).join(formatted_oem) if formatted_oem else 'No sections found.'}\n\n"
        f"--- SIMILAR PAST INCIDENTS & NEAR MISSES ---\n"
        f"{chr(10).join(formatted_incidents) if formatted_incidents else 'No similar incidents found.'}\n\n"
        f"Perform RCA and output JSON:"
    )
    
    synthesis_prompt = ChatPromptTemplate.from_messages([
        ("system", synthesis_system_prompt),
        ("user", synthesis_user_prompt)
    ])
    
    synthesis_chain = synthesis_prompt | llm.bind(response_format={"type": "json_object"})
    
    try:
        synthesis_response = synthesis_chain.invoke({})
        rca_report = json.loads(synthesis_response.content)
    except Exception as e:
        rca_report = {
            "equipment": eq_tag if eq_tag else "Unknown Equipment",
            "failure_mode": failure_mode if failure_mode else "Unknown",
            "root_cause_hypothesis": f"Error synthesizing RCA: {e}",
            "supporting_evidence": [],
            "recommended_action": "Manually inspect asset.",
            "recurrence_risk": "Medium",
            "confidence": "Low"
        }
        
    latency = time.time() - start_time
    
    return {
        "report": rca_report,
        "maint_records": maint_records,
        "oem_docs": tech_docs,
        "incident_cases": incident_cases,
        "latency": latency
    }
