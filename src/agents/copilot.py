import os
import re
import time
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from src.retrieval.retriever import hybrid_retrieve, extract_equipment_tags

# Load environment variables from .env file
load_dotenv()

DEFAULT_MODEL = "llama-3.1-8b-instant"

def get_chat_model(model=DEFAULT_MODEL):
    """
    Initializes and returns the LangChain ChatGroq model.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not found. Please set it in your .env file.")
    return ChatGroq(model=model, temperature=0.1, api_key=api_key)

def parse_query_analysis(llm_output):
    """
    Parses LLM output content into structured query analysis details.
    """
    try:
        data = json.loads(llm_output.content)
        # Ensure correct structure
        if "equipment_tags" not in data or not isinstance(data["equipment_tags"], list):
            data["equipment_tags"] = []
        if "search_keywords" not in data:
            data["search_keywords"] = ""
        # Normalize tags to uppercase
        data["equipment_tags"] = [str(t).strip().upper() for t in data["equipment_tags"]]
        return data
    except Exception:
        # Fallback in case of parsing failures
        return {"equipment_tags": [], "search_keywords": "", "query_type": "general"}

def perform_retrieval(inputs):
    """
    Runs the hybrid retrieval using the parsed query keywords and tags.
    """
    user_query = inputs["user_query"]
    analysis = inputs["analysis"]
    
    # Check if a forced equipment tag was passed from query_copilot arguments
    forced_tag = inputs.get("forced_tag")
    if forced_tag:
        tags = [forced_tag]
    else:
        tags = analysis.get("equipment_tags", [])
        
    keywords = analysis.get("search_keywords", "")
    
    # Fallback to regex extraction on original query if LLM query analysis returned empty tags
    if not tags and not forced_tag:
        tags = extract_equipment_tags(user_query)
        
    search_query = keywords if keywords.strip() else user_query
    
    # Retrieve top candidates
    retrieved_chunks = hybrid_retrieve(search_query, top_k=6, query_tags=tags)
    
    return {
        "user_query": user_query,
        "analysis": analysis,
        "retrieved_chunks": retrieved_chunks,
        "forced_tag": forced_tag
    }

# Mapping local asset tags to manufacturer/OEM manuals
ASSET_MODEL_MAPPING = {
    "P-101": "ACP-SE Centrifugal Pump",
    "P-102": "Goulds Model 811 Pump (Griswold Model 811)",
    "C-301": "811CC Series Reciprocating Compressor",
    "V-105": "Control Valve V-105",
    "V-203": "Gate Valve V-203"
}

def assemble_context(inputs):
    """
    Formats the retrieved chunks into a standard structured context block.
    """
    chunks = inputs["retrieved_chunks"]
    formatted_parts = []
    
    # Resolve active asset tags for mapping hints
    forced_tag = inputs.get("forced_tag")
    tags = [forced_tag] if forced_tag else inputs["analysis"].get("equipment_tags", [])
    if not tags:
        tags = extract_equipment_tags(inputs["user_query"])
        
    asset_hints = []
    for tag in tags:
        tag_upper = tag.upper()
        if tag_upper in ASSET_MODEL_MAPPING:
            asset_hints.append(f"Note: Local plant asset tag '{tag_upper}' corresponds to the manufacturer model series '{ASSET_MODEL_MAPPING[tag_upper]}'.")
            
    if asset_hints:
        formatted_parts.append("=== ASSET TO MODEL MAPPING DIRECTIVE ===\n" + "\n".join(asset_hints) + "\n========================================")
        
    for idx, cand in enumerate(chunks):
        meta = cand["metadata"]
        source_name = meta.get("source_file", "Unknown File")
        
        location_info = ""
        if "page_number" in meta:
            location_info = f"Page {meta['page_number']}"
        elif "row_index" in meta:
            location_info = f"Row {meta['row_index']}"
            
        cand_tags = meta.get("equipment_tags", "None")
        
        formatted_parts.append(
            f"--- Source [{idx + 1}]: {source_name} ({location_info}) | Equipment Tags: {cand_tags} ---\n"
            f"{cand['text']}"
        )
        
    return {
        "user_query": inputs["user_query"],
        "analysis": inputs["analysis"],
        "retrieved_chunks": chunks,
        "context": "\n\n".join(formatted_parts)
    }

def extract_citations_and_confidence(answer_text, chunks):
    """
    Extracts confidence rating and maps inline citations to matching retrieved source chunks.
    Supports both file-based citations [Manual.pdf, Page X] and index citations Source [X], [Source X], [X].
    """
    # 1. Parse confidence level (High / Medium / Low)
    confidence = "Medium"
    confidence_match = re.search(r'(?i)confidence\s*(?:level|score)?\s*:\s*(high|medium|low)', answer_text)
    if confidence_match:
        confidence = confidence_match.group(1).capitalize()
    else:
        # Check for standalone mentions
        for level in ["High", "Medium", "Low"]:
            if level in answer_text[:100] or level in answer_text[-100:]:
                confidence = level
                break
                
    cited_sources = []
    seen_citations = set()
    
    # 2. Extract citations like [Document_Name.pdf, Page X] or [Document_Name.csv, Row Y]
    citation_pattern = re.compile(r'\[([^,\]]+),\s*(Page\s*\d+|Row\s*\d+)\]', re.IGNORECASE)
    citations_found = citation_pattern.findall(answer_text)
    
    for doc_name, loc in citations_found:
        doc_name = doc_name.strip()
        loc = loc.strip()
        citation_key = f"{doc_name}:{loc}".lower()
        
        if citation_key in seen_citations:
            continue
        seen_citations.add(citation_key)
        
        # Find matching chunk to pull the raw text snippet
        matching_chunk = None
        for chunk in chunks:
            meta = chunk["metadata"]
            source = meta.get("source_file", "")
            
            chunk_loc = ""
            if "page_number" in meta:
                chunk_loc = f"Page {meta['page_number']}"
            elif "row_index" in meta:
                chunk_loc = f"Row {meta['row_index']}"
                
            if source.lower() == doc_name.lower() and chunk_loc.lower() == loc.lower():
                matching_chunk = chunk
                break
                
        if matching_chunk:
            cited_sources.append({
                "source_file": doc_name,
                "location": loc,
                "text": matching_chunk["text"],
                "metadata": matching_chunk["metadata"]
            })
        else:
            cited_sources.append({
                "source_file": doc_name,
                "location": loc,
                "text": "Snippet context referenced by model.",
                "metadata": {}
            })
            
    # 3. Extract index-based citations like Source [X], [Source X], or [X]
    index_patterns = [
        re.compile(r'(?i)source\s*\[(\d+)\]'),
        re.compile(r'(?i)\[source\s*(\d+)\]'),
        re.compile(r'\[(\d+)\]')
    ]
    
    for pattern in index_patterns:
        for match in pattern.finditer(answer_text):
            val_str = match.group(1)
            if val_str.isdigit():
                val = int(val_str)
                chunk_idx = val - 1
                if 0 <= chunk_idx < len(chunks):
                    chunk = chunks[chunk_idx]
                    meta = chunk["metadata"]
                    doc_name = meta.get("source_file", "Unknown File")
                    
                    loc = ""
                    if "page_number" in meta:
                        loc = f"Page {meta['page_number']}"
                    elif "row_index" in meta:
                        loc = f"Row {meta['row_index']}"
                        
                    citation_key = f"{doc_name}:{loc}".lower()
                    if citation_key not in seen_citations:
                        seen_citations.add(citation_key)
                        cited_sources.append({
                            "source_file": doc_name,
                            "location": loc,
                            "text": chunk["text"],
                            "metadata": meta
                        })
            
    # Clean up the output text by removing the confidence statement if it is at the very beginning or end
    clean_answer = answer_text
    clean_answer = re.sub(r'(?i)^\s*confidence\s*(?:level|score)?\s*:\s*(?:high|medium|low)\s*\.?', '', clean_answer).strip()
    clean_answer = re.sub(r'(?i)confidence\s*(?:level|score)?\s*:\s*(?:high|medium|low)\s*\.?$', '', clean_answer).strip()
    
    return clean_answer, confidence, cited_sources

def query_copilot(query_text, model=DEFAULT_MODEL, top_k=5, equipment_tag=None):
    """
    Executes the full LangChain LCEL pipeline for querying the Copilot.
    """
    start_time = time.time()
    
    try:
        llm = get_chat_model(model)
        
        # 1. Query Analysis Setup
        query_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a maintenance query analyzer for heavy engineering assets.\n"
                       "Extract equipment tags (like P-101, C-301, V-105) and key search terms for retrieval.\n"
                       "Respond ONLY with a JSON object. Keys:\n"
                       "- 'equipment_tags': [list of tags or empty list]\n"
                       "- 'search_keywords': 'optimized search keywords for DB lookup'\n"
                       "- 'query_type': 'technical_manual' | 'maintenance_history' | 'safety_incident' | 'general'"),
            ("user", "Query: {user_query}")
        ])
        
        query_analyzer = query_analysis_prompt | llm.bind(response_format={"type": "json_object"}) | RunnableLambda(parse_query_analysis)
        
        # 2. Context Prompt Setup
        system_prompt = (
            "You are an industrial knowledge expert assisting maintenance engineers.\n"
            "Answer the question based ONLY on the provided context. If the answer is not in the context, say so.\n"
            "Always cite your sources in the text as [Document Name, Page X] (for PDFs) or [Document Name, Row X] (for tabular logs).\n"
            "At the beginning or end of your answer, write: 'Confidence level: [High / Medium / Low]' and explain why."
        )
        user_prompt = (
            "Context:\n{context}\n\n"
            "Question: {user_query}\n\n"
            "Answer:"
        )
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        
        qa_chain = qa_prompt | llm
        
        # 3. Build and execute LCEL Chain
        chain = (
            {"user_query": RunnablePassthrough(), "forced_tag": lambda x: equipment_tag}
            | RunnablePassthrough.assign(analysis=query_analyzer)
            | RunnableLambda(perform_retrieval)
            | RunnableLambda(assemble_context)
            | RunnablePassthrough.assign(response=qa_chain)
        )
        
        result = chain.invoke(query_text)
        
        raw_answer = result["response"].content
        chunks = result["retrieved_chunks"]
        
        # Parse final output structure
        clean_answer, confidence, cited_sources = extract_citations_and_confidence(raw_answer, chunks)
        
        # If no citations were extracted by regex, but we retrieved chunks, list retrieved chunks as fallback sources
        if not cited_sources and chunks:
            for chunk in chunks[:2]:
                meta = chunk["metadata"]
                loc = f"Page {meta.get('page_number')}" if "page_number" in meta else f"Row {meta.get('row_index')}"
                cited_sources.append({
                    "source_file": meta.get("source_file", "Unknown"),
                    "location": loc,
                    "text": chunk["text"],
                    "metadata": meta
                })
        
        latency = time.time() - start_time
        
        return {
            "answer": clean_answer,
            "confidence": confidence,
            "sources": cited_sources,
            "latency": latency,
            "all_retrieved": chunks
        }
        
    except Exception as e:
        latency = time.time() - start_time
        return {
            "answer": f"Error running LangChain Copilot: {e}",
            "confidence": "Low",
            "sources": [],
            "latency": latency,
            "all_retrieved": []
        }
