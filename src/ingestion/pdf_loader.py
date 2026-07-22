import os
import re
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Regular expression to extract equipment tags (e.g., P-101, V-203, C-301, ACP-SE, CTP)
# Specifically target common plant tags: one to three letters followed by a hyphen and three or four digits.
EQUIP_TAG_PATTERN = re.compile(r'\b([A-Z]{1,4}-\d{3,4})\b', re.IGNORECASE)

def extract_equipment_tags(text):
    """
    Extracts unique equipment tags from a given text.
    """
    if not text:
        return []
    matches = EQUIP_TAG_PATTERN.findall(text)
    # Normalize tags to uppercase
    return list(set(match.upper() for match in matches))

def extract_section_heading(text):
    """
    Tries to infer a section heading from the first few lines of page text.
    """
    if not text:
        return "Unknown Section"
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:3]:
        # Filter out short page numbers or header templates
        if len(line) > 3 and not line.isdigit() and len(line) < 100:
            return line
    return "Introduction"

def load_pdf(file_path):
    """
    Loads a text-native PDF using pdfplumber, extracts text, extracts equipment tags,
    and returns a list of dictionaries with text and metadata.
    """
    documents = []
    filename = os.path.basename(file_path)
    
    print(f"Loading PDF: {filename}...")
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                page_num = page_idx + 1
                text = page.extract_text()
                if not text:
                    continue
                
                heading = extract_section_heading(text)
                all_tags = extract_equipment_tags(text)
                
                documents.append({
                    "text": text,
                    "metadata": {
                        "source_file": filename,
                        "page_number": page_num,
                        "doc_type": "technical_docs",
                        "section_heading": heading,
                        "equipment_tags": ",".join(all_tags) if all_tags else ""
                    }
                })
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        
    return documents

def chunk_documents(documents, chunk_size=2000, chunk_overlap=250):
    """
    Splits documents into smaller chunks using RecursiveCharacterTextSplitter
    and computes specific equipment tags for each chunk.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = []
    for doc in documents:
        split_texts = splitter.split_text(doc["text"])
        for chunk_idx, text in enumerate(split_texts):
            # Recalculate equipment tags present in this specific chunk text
            chunk_tags = extract_equipment_tags(text)
            
            # Inherit and override metadata
            metadata = doc["metadata"].copy()
            metadata["chunk_index"] = chunk_idx
            metadata["equipment_tags"] = ",".join(chunk_tags) if chunk_tags else ""
            
            chunks.append({
                "text": text,
                "metadata": metadata
            })
            
    return chunks
