import sys
import os

# Append project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval.retriever import hybrid_retrieve

def test_query(query):
    print(f"\nQUERY: '{query}'")
    results = hybrid_retrieve(query, top_k=3)
    
    print(f"Retrieved {len(results)} chunks:")
    for idx, cand in enumerate(results):
        meta = cand["metadata"]
        print(f"[{idx+1}] File: {meta.get('source_file')} | Distance: {cand.get('distance'):.4f} | Blended Score: {cand.get('blended_score'):.4f}")
        if "page_number" in meta:
            print(f"    Page: {meta.get('page_number')} | Section: {meta.get('section_heading')}")
        elif "row_index" in meta:
            print(f"    Record ID: {meta.get('record_id')} | Row Index: {meta.get('row_index')}")
        print(f"    Snippet: {cand['text'][:150]}...")
        print(f"    Tags: {meta.get('equipment_tags')}")

if __name__ == "__main__":
    # Test 1: Query with explicit equipment tag
    test_query("What is the maintenance history of Pump P-102?")
    
    # Test 2: General technical query
    test_query("How to handle emergency reporting under the Factories Act?")
    
    # Test 3: Maintenance log query
    test_query("Which technician worked on C-301 reciprocating compressor?")
