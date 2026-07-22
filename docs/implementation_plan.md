# Week 1 Checklist Implementation: Ingestion Pipeline & Basic RAG

This plan details the implementation of the Week 1 milestone: creating the document ingestion pipeline and enabling basic RAG via a terminal client using Groq's Llama 3 8B model.

## User Review Required

> [!IMPORTANT]
> **Tesseract OCR Binary:** Tesseract is not currently installed on this system. Our `ocr_loader.py` will contain a graceful fallback that uses `pdfplumber` / `pypdfium2` text extraction if the tesseract binary is missing. We highly recommend installing tesseract via Homebrew: `brew install tesseract` if there are pure scanned images in the document list.
>
> **Groq API Key:** The system will require `GROQ_API_KEY` to be set in a `.env` file or exported in the environment to connect to the LLM. We will write to a `.env` file for local development.

---

## Proposed Changes

### 1. Project Dependencies

#### [MODIFY] [requirements.txt](file:///Users/aadityadevsharma/Documents/hackathon/requirements.txt)
We will add required dependencies:
*   `groq`: For accessing Llama 3 8B.
*   `pdfplumber`: For text extraction from PDFs.
*   `pytesseract`: OCR interface.
*   `pandas`: For row-by-row serialization of CSV datasets.
*   `chromadb`: The vector database.
*   `sentence-transformers`: For local embedding generation (`all-MiniLM-L6-v2`).
*   `python-dotenv`: To load the Groq API key from `.env`.

---

### 2. Ingestion Engine

#### [NEW] [ocr_loader.py](file:///Users/aadityadevsharma/Documents/hackathon/src/ingestion/ocr_loader.py)
*   Implements a pipeline using `pytesseract` to OCR scanned pages.
*   Performs image preprocessing (grayscale conversion, thresholding, and deskewing).
*   Contains a fallback mechanism to standard text-extraction if Tesseract is not installed.

#### [NEW] [pdf_loader.py](file:///Users/aadityadevsharma/Documents/hackathon/src/ingestion/pdf_loader.py)
*   Loads text-native PDFs using `pdfplumber`.
*   Extracts text, page numbers, and parses section headings/metadata.
*   Uses a regex-based equipment tag extractor (finding references matching patterns like `P-101`, `V-203`, `C-301`, etc.).
*   Uses LangChain's `RecursiveCharacterTextSplitter` configured for a chunk size of 512 tokens (~2000 characters) and 64 tokens overlap (~250 characters).

#### [NEW] [excel_loader.py](file:///Users/aadityadevsharma/Documents/hackathon/src/ingestion/excel_loader.py)
*   Loads tabular data (maintenance log and near-miss logs in CSV/Excel formats) using `pandas`.
*   Serializes each row into structured natural language text (e.g. *"Equipment: P-101 | Date: 2024-03-15 | Failure: Seal leak | Resolution: Mechanical seal replaced"*).
*   Assigns metadata mapping row indices, source files, and extracting equipment tags.

---

### 3. Retrieval & Storage Layer

#### [NEW] [vectorstore.py](file:///Users/aadityadevsharma/Documents/hackathon/src/retrieval/vectorstore.py)
*   Initializes a persistent ChromaDB client inside `data/processed/chromadb`.
*   Creates two collections:
    1.  `technical_docs`: Stores chunks from manuals and regulatory PDF files.
    2.  `maintenance_records`: Stores serialized rows/chunks from CSV logs.
*   Implements local embedding generation using `sentence-transformers/all-MiniLM-L6-v2`.
*   Exposes functions to index document chunks and check collection stats.

#### [NEW] [retriever.py](file:///Users/aadityadevsharma/Documents/hackathon/src/retrieval/retriever.py)
*   Implements hybrid retrieval:
    1.  **Metadata filtering & Pre-search:** Uses regex to check if the user query contains equipment tags (like `P-101`). If found, prioritizes matching tag metadata.
    2.  **Semantic Search:** Queries both ChromaDB collections.
    3.  **Re-ranking:** Custom lightweight BM25/TF-IDF similarity script implemented in pure Python to re-rank the retrieved chunks and compute a weighted similarity blend.

---

### 4. RAG Interface

#### [NEW] [copilot.py](file:///Users/aadityadevsharma/Documents/hackathon/src/agents/copilot.py)
*   Integrates the Groq API client with model `llama3-8b-8192` (or `llama-3.1-8b-instant`).
*   Formulates a prompt templates that enforces:
    *   Synthesizing answers using *only* the retrieved context.
    *   Providing explicit source citations (document name, page number, or log row ID).
    *   Indicating a confidence score (Low, Medium, High).
*   Provides a clean command-line script interface to prompt the system.

---

## Verification Plan

### Automated Tests
*   We will run a script `/Users/aadityadevsharma/Documents/hackathon/tests/test_ingestion.py` that processes a subset of PDFs and CSVs and prints ingestion counts.
*   We will run a retrieval test `/Users/aadityadevsharma/Documents/hackathon/tests/test_retrieval.py` verifying hybrid search returns correct equipment references.

### Manual Verification
*   We will run a terminal session: `python app.py --query "How do I troubleshoot leakage in Pump P-102?"` and verify the output contains source manual citations and past maintenance logs with a confidence score.
