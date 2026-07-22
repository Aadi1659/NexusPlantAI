import os
import sys
import json
import time
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append("/Users/aadityadevsharma/Documents/hackathon")

from src.agents.copilot import query_copilot, get_chat_model
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

BENCHMARK_RESULTS_PATH = "/Users/aadityadevsharma/Documents/hackathon/docs/benchmark_results.md"
JSON_RESULTS_PATH = "/Users/aadityadevsharma/Documents/hackathon/data/processed/benchmark_results.json"

# Defining 20 benchmark Q&A pairs
BENCHMARK_DATA = [
    {
        "id": 1,
        "query": "What is the maintenance history of Pump P-102?",
        "reference": "Pump P-102 was serviced multiple times: ML-1004 (Emergency, minor leakage observed, seal replaced), ML-1008 (Corrective, pressure fluctuation, gasket replaced), ML-1009 (Emergency, normal operation, gasket replaced), ML-1014 (Preventive, normal operation, no parts), ML-1016 (Corrective, vibration above threshold), ML-1021 (Predictive, vibration above threshold, filter replaced), ML-1023 (Corrective, vibration above threshold, gasket replaced), etc.",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    },
    {
        "id": 2,
        "query": "Which technicians worked on C-301 reciprocating compressor?",
        "reference": "Technicians A. Verma, N. Gupta, R. Kumar, and S. Sharma performed maintenance work on reciprocating compressor C-301.",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    },
    {
        "id": 3,
        "query": "What was observed during the maintenance of Control Valve V-105 on 2026-01-22?",
        "reference": "Bearing noise was detected, and a bearing was replaced by technician P. Singh (Record ID ML-1007).",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    },
    {
        "id": 4,
        "query": "When was maintenance performed on Gate Valve V-203 and what parts were replaced?",
        "reference": "Maintenance was performed on V-203 on: 2026-01-10 (parts: Gasket, ML-1003), 2026-02-03 (parts: Gasket, ML-1011), 2026-02-09 (parts: Filter, ML-1013), 2026-02-18 (parts: None, ML-1017), 2026-04-25 (parts: Seal, ML-1038), 2026-06-06 (parts: None, ML-1052), 2026-06-21 (parts: Bearing, ML-1057).",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    },
    {
        "id": 5,
        "query": "How many run hours did Centrifugal Pump P-101 log before its maintenance on 2026-04-10?",
        "reference": "Centrifugal Pump P-101 logged 236 run hours before its preventive maintenance on 2026-04-10 (Record ID ML-1033).",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    },
    {
        "id": 6,
        "query": "What is the procedure for handling seal leakages in Goulds 811 pumps according to the IOM manual?",
        "reference": "According to Goulds Model 811 IOM, users must check the seal chamber, examine the mechanical seal faces for wear, verify alignment, verify flush fluid is flowing, and replace damaged seal components if necessary.",
        "expected_docs": ["811_iom.pdf"]
    },
    {
        "id": 7,
        "query": "What are the rules and guidelines for reporting safety occurrence investigations?",
        "reference": "Safety occurrence reporting requires immediate notification of high-severity incidents, submission of standard forms, classification of root causes (such as unsafe acts or human error), and establishing corrective actions.",
        "expected_docs": ["Safety_occurrence_reporting_and_investigation.pdf"]
    },
    {
        "id": 8,
        "query": "What does the ACP-SE manual recommend for centrifugal pump bearing lubrication?",
        "reference": "The ACP-SE centrifugal pump manual outlines lubrication schedules, grease grades, checking bearing housing oil levels, checking for lubrication degradation, and preventing overgreasing which causes heating.",
        "expected_docs": ["centrifugal-pump-acp-se-manual-v2-2-en-data.pdf"]
    },
    {
        "id": 9,
        "query": "What maintenance observation was logged for Pump P-102 on 2026-06-12?",
        "reference": "On 2026-06-12, 'Bearing noise detected' was logged for Pump P-102, with no parts replaced (Record ID ML-1054).",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    },
    {
        "id": 10,
        "query": "What incident severity is logged for Report ID INC-2009?",
        "reference": "Incident Report INC-2009 has severity 'Near Miss - High Potential' occurring in the Compressor Shed, with probable cause 'Slip/trip'.",
        "expected_docs": ["near_miss_incident_log_synthetic.csv"]
    },
    {
        "id": 11,
        "query": "Where did safety incident INC-2007 occur and who reported it?",
        "reference": "Safety incident INC-2007 occurred in the Pump House and was reported by P. Singh.",
        "expected_docs": ["near_miss_incident_log_synthetic.csv"]
    },
    {
        "id": 12,
        "query": "Which document covers the Factories Act 1948 and safety regulations?",
        "reference": "factory_acta1948-63.pdf contains the provisions of the Factories Act of 1948.",
        "expected_docs": ["factory_acta1948-63.pdf"]
    },
    {
        "id": 13,
        "query": "What are the requirements for reporting accidents under the RIDDOR framework?",
        "reference": "The RIDDOR framework requires reporting of specified workplace injuries, occupational diseases, and dangerous occurrences to the relevant authority within designated timelines.",
        "expected_docs": ["riddor-background-quality-report.pdf"]
    },
    {
        "id": 14,
        "query": "What observation was logged for Reciprocating Compressor C-301 in log ML-1026?",
        "reference": "In record ML-1026 on 2026-03-20, 'Minor leakage observed' was logged, and a bearing was replaced by technician N. Gupta.",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    },
    {
        "id": 15,
        "query": "What parts were replaced on Control Valve V-105 during the emergency maintenance on 2026-01-16?",
        "reference": "A Gasket was replaced during the emergency maintenance on Control Valve V-105 on 2026-01-16 (Record ID ML-1005).",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    },
    {
        "id": 16,
        "query": "Who reported safety incident INC-2025 at the Storage Tank Area?",
        "reference": "Safety incident INC-2025 was reported by N. Gupta, with severity 'Property Damage' and probable cause 'Equipment failure'.",
        "expected_docs": ["near_miss_incident_log_synthetic.csv"]
    },
    {
        "id": 17,
        "query": "What is the next scheduled maintenance date for Gate Valve V-203 after ML-1011?",
        "reference": "The next scheduled maintenance for Gate Valve V-203 after ML-1011 (dated 2026-02-03) is 2026-05-04.",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    },
    {
        "id": 18,
        "query": "What is the run hour count for Pump P-101 in ML-1049?",
        "reference": "In ML-1049, Centrifugal Pump P-101 had logged 546 run hours since its last maintenance.",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    },
    {
        "id": 19,
        "query": "What safety occurrence template or guidelines does hsg245 discuss?",
        "reference": "hsg245.pdf discusses the health and safety executive guide to investigating accidents and incidents at work.",
        "expected_docs": ["hsg245.pdf"]
    },
    {
        "id": 20,
        "query": "Who performed the corrective maintenance on Pump P-102 on 2026-05-07?",
        "reference": "Technician S. Sharma performed the corrective maintenance on Pump P-102 on 2026-05-07 (Record ID ML-1042), replacing the seal.",
        "expected_docs": ["maintenance_log_synthetic.csv"]
    }
]

def evaluate_answer_quality(query, reference, answer):
    """
    Invokes Groq LLM as a judge to evaluate answer quality from 1 to 5.
    """
    try:
        llm = get_chat_model("llama-3.1-8b-instant")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an objective evaluation judge rating answers on a scale from 1 to 5.\n"
                       "Compare the Assistant Answer to the Ground Truth Reference Answer based on correctness and factual accuracy.\n"
                       "Rating scale:\n"
                       "1: Entirely wrong or hallucinatory.\n"
                       "2: Mostly incorrect, missed major facts.\n"
                       "3: Partially correct, contains some factual elements but is incomplete.\n"
                       "4: Mostly correct, matches reference with minor stylistic differences or small omissions.\n"
                       "5: Fully correct, matches reference facts perfectly.\n\n"
                       "Respond ONLY with a JSON object. Keys:\n"
                       "- 'score': [integer 1 to 5]\n"
                       "- 'reason': 'detailed explanation of the score'"),
            ("user", "Query: {query}\nReference Answer: {reference}\nAssistant Answer: {answer}")
        ])
        
        judge_chain = prompt | llm.bind(response_format={"type": "json_object"})
        resp = judge_chain.invoke({"query": query, "reference": reference, "answer": answer})
        result = json.loads(resp.content)
        return int(result.get("score", 3)), result.get("reason", "")
    except Exception as e:
        print(f"Error evaluating answer quality: {e}")
        return 3, f"Fallback score due to evaluation error: {e}"

def run_benchmark():
    print("=== Starting Mini Benchmark Suite (20 Q&A Pairs) ===")
    
    results = []
    total_latency = 0
    total_score = 0
    correct_citations = 0
    
    for idx, item in enumerate(BENCHMARK_DATA):
        print(f"[{idx+1}/20] Querying: '{item['query']}'")
        
        # Run system RAG
        rag_output = query_copilot(item["query"])
        
        # Calculate latency
        latency = rag_output.get("latency", 0)
        total_latency += latency
        
        # Verify citation
        cited_files = [s["source_file"].lower() for s in rag_output.get("sources", [])]
        expected_files = [f.lower() for f in item["expected_docs"]]
        
        cited_correctly = any(exp in cited_files for exp in expected_files)
        if cited_correctly:
            correct_citations += 1
            
        # Grade answer
        score, reason = evaluate_answer_quality(item["query"], item["reference"], rag_output["answer"])
        total_score += score
        
        results.append({
            "id": item["id"],
            "query": item["query"],
            "reference": item["reference"],
            "answer": rag_output["answer"],
            "confidence": rag_output["confidence"],
            "latency": latency,
            "cited_sources": [s["source_file"] for s in rag_output["sources"]],
            "expected_docs": item["expected_docs"],
            "citation_accurate": cited_correctly,
            "score": score,
            "reason": reason
        })
        
        print(f"       Score: {score}/5 | Latency: {latency:.2f}s | Citation Match: {cited_correctly}")
        time.sleep(1.0) # Avoid rate limits
        
    num_queries = len(BENCHMARK_DATA)
    avg_latency = total_latency / num_queries
    avg_score = total_score / num_queries
    citation_rate = (correct_citations / num_queries) * 100
    
    summary = {
        "total_queries": num_queries,
        "average_latency_sec": avg_latency,
        "average_score": avg_score,
        "citation_accuracy_rate": citation_rate,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save JSON results
    os.makedirs(os.path.dirname(JSON_RESULTS_PATH), exist_ok=True)
    with open(JSON_RESULTS_PATH, "w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)
        
    # Write Markdown Report
    os.makedirs(os.path.dirname(BENCHMARK_RESULTS_PATH), exist_ok=True)
    with open(BENCHMARK_RESULTS_PATH, "w") as f:
        f.write("# System Benchmark Results Dashboard\n\n")
        f.write(f"**Execution Timestamp:** {summary['timestamp']}\n\n")
        f.write("## Performance Summary\n\n")
        f.write("| Metric | Value |\n")
        f.write("| --- | --- |\n")
        f.write(f"| **Total Evaluated Queries** | {summary['total_queries']} |\n")
        f.write(f"| **Average Response Latency** | {summary['average_latency_sec']:.3f} seconds |\n")
        f.write(f"| **Average Factual Score (LLM Judge)** | {summary['average_score']:.2f} / 5.0 |\n")
        f.write(f"| **Citation Accuracy Rate** | {summary['citation_accuracy_rate']:.1f}% |\n\n")
        
        f.write("## Detailed Query Evaluations\n\n")
        f.write("| ID | Query | Expected Doc | Cited Correctly? | Score | Latency |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for r in results:
            cited_ok = "✅ Yes" if r["citation_accurate"] else "❌ No"
            f.write(f"| {r['id']} | {r['query']} | `{', '.join(r['expected_docs'])}` | {cited_ok} | **{r['score']}/5** | {r['latency']:.2f}s |\n")
            
        f.write("\n### Individual Q&A Transcripts\n\n")
        for r in results:
            f.write(f"#### Query {r['id']}: {r['query']}\n")
            f.write(f"- **Reference Answer:** {r['reference']}\n")
            f.write(f"- **Assistant Answer:** {r['answer']}\n")
            f.write(f"- **LLM Judge Rating:** {r['score']}/5\n")
            f.write(f"- **Judge Reason:** {r['reason']}\n")
            f.write(f"- **Sources Cited:** {', '.join(r['cited_sources']) if r['cited_sources'] else 'None'}\n\n")
            f.write("---\n\n")
            
    print("\n=== Benchmark Completed Successfully ===")
    print(f"Summary: Score = {avg_score:.2f}/5 | Latency = {avg_latency:.2f}s | Citation = {citation_rate:.1f}%")
    print(f"Reports saved to {BENCHMARK_RESULTS_PATH} and {JSON_RESULTS_PATH}")

if __name__ == "__main__":
    run_benchmark()
