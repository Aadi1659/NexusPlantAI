import re
import math
from collections import Counter
from src.ingestion.pdf_loader import extract_equipment_tags
from src.retrieval.vectorstore import query_vectorstore

def tokenize(text):
    """
    Simple tokenizer that lowercases and extracts alphanumeric words.
    """
    if not text:
        return []
    return re.findall(r'\b\w+\b', text.lower())

class SimpleBM25:
    """
    A lightweight, pure-Python implementation of BM25.
    """
    def __init__(self, documents_text, b=0.75, k1=1.5):
        self.b = b
        self.k1 = k1
        self.corpus_size = len(documents_text)
        self.avg_doc_len = 0
        self.doc_freqs = []
        self.idf = {}
        
        if self.corpus_size == 0:
            return
            
        tokenized_docs = [tokenize(doc) for doc in documents_text]
        self.avg_doc_len = sum(len(doc) for doc in tokenized_docs) / self.corpus_size
        
        df = Counter()
        for doc in tokenized_docs:
            self.doc_freqs.append(Counter(doc))
            for token in set(doc):
                df[token] += 1
                
        for token, freq in df.items():
            # Standard BM25 IDF formula with smoothing
            self.idf[token] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)

    def get_score(self, doc_idx, query_tokens):
        if self.corpus_size == 0:
            return 0.0
            
        score = 0.0
        doc_len = sum(self.doc_freqs[doc_idx].values())
        freqs = self.doc_freqs[doc_idx]
        
        for token in query_tokens:
            if token not in self.idf:
                continue
            tf = freqs[token]
            numerator = self.idf[token] * tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
            score += numerator / denominator
            
        return score

def hybrid_retrieve(query_text, top_k=5, semantic_weight=0.7, query_tags=None):
    """
    Performs hybrid retrieval:
    1. Extracts equipment tags from the query.
    2. Queries 'technical_docs' and 'maintenance_records' collections.
    3. Performs metadata filtering in Python for equipment tags.
    4. Computes BM25 scores and blends them with the semantic scores.
    """
    if query_tags is None:
        query_tags = extract_equipment_tags(query_text)
    
    # 1. Retrieve candidates from both vector collections semantically
    tech_limit = max(top_k * 3, 15)
    tech_candidates = query_vectorstore("technical_docs", query_text, n_results=tech_limit)
    
    # Retrieve a larger count for maintenance logs since the dataset is small (~100 records total)
    maint_candidates = query_vectorstore("maintenance_records", query_text, n_results=80)
    
    # 2. Equipment Tag Metadata Filter (Only applied to maintenance records)
    if query_tags:
        filtered_maint = []
        for cand in maint_candidates:
            cand_tags_str = cand["metadata"].get("equipment_tags", "")
            cand_tags = [t.strip().upper() for t in cand_tags_str.split(",") if t.strip()]
            
            # Check if any tag from query matches the candidate tags
            if any(q_tag in cand_tags for q_tag in query_tags):
                filtered_maint.append(cand)
                
        if filtered_maint:
            maint_candidates = filtered_maint
            print(f"Filter Match: Retained {len(maint_candidates)} maintenance records matching tags: {query_tags}")
            
    candidates = tech_candidates + maint_candidates
            
    # 3. BM25 Re-ranking
    # Prepare documents for BM25
    doc_texts = [cand["text"] for cand in candidates]
    bm25 = SimpleBM25(doc_texts)
    query_tokens = tokenize(query_text)
    
    # Compute BM25 scores
    bm25_scores = [bm25.get_score(idx, query_tokens) for idx in range(len(candidates))]
    max_bm25 = max(bm25_scores) if bm25_scores else 0
    
    # Normalize BM25 scores and blend with Semantic scores
    for idx, cand in enumerate(candidates):
        raw_bm25 = bm25_scores[idx]
        norm_bm25 = raw_bm25 / max_bm25 if max_bm25 > 0 else 0.0
        
        # Weighted blend (Semantic + BM25)
        # ChromaDB cosine similarity score proxy is used as cand['score']
        semantic_score = cand["score"]
        blended_score = (semantic_weight * semantic_score) + ((1.0 - semantic_weight) * norm_bm25)
        
        cand["bm25_score"] = raw_bm25
        cand["blended_score"] = blended_score
        
    # Sort candidates by blended score descending
    candidates.sort(key=lambda x: x["blended_score"], reverse=True)
    
    return candidates[:top_k]
