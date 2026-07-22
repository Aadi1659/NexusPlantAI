import os
import re
import sys
from PIL import Image
from src.ingestion.pdf_loader import extract_equipment_tags, extract_section_heading, chunk_documents

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

def is_tesseract_available():
    """
    Checks if the tesseract command-line binary is available on the system path.
    """
    if pytesseract is None:
        return False
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False

def preprocess_image(image):
    """
    Applies image preprocessing: grayscale -> threshold -> deskew.
    """
    # 1. Grayscale conversion
    gray = image.convert('L')
    
    # 2. Thresholding (Binarization)
    threshold_value = 127
    binary = gray.point(lambda p: 255 if p > threshold_value else 0)
    
    # 3. Deskewing using pytesseract OSD
    if is_tesseract_available():
        try:
            osd = pytesseract.image_to_osd(binary)
            rotation = re.search(r'Rotate: (\d+)', osd)
            if rotation:
                angle = int(rotation.group(1))
                if angle != 0:
                    binary = binary.rotate(-angle, expand=True)
        except Exception as e:
            # If OSD fails, proceed with the binary image
            pass
            
    return binary

def load_scanned_pdf_or_image(file_path):
    """
    Ingests scanned files using pytesseract OCR. Falls back to text extraction
    using pdfplumber/standard PDF reading if tesseract or pdf2image is not available.
    """
    filename = os.path.basename(file_path)
    documents = []
    
    # Check if the file is an image or PDF
    is_pdf = file_path.lower().endswith('.pdf')
    
    # Fallback condition check
    tesseract_available = is_tesseract_available()
    pdf2image_available = convert_from_path is not None
    
    if is_pdf and (not tesseract_available or not pdf2image_available):
        print(f"Warning: Tesseract OCR or pdf2image is missing. Falling back to pdfplumber text extraction for {filename}.")
        from src.ingestion.pdf_loader import load_pdf
        return load_pdf(file_path)
        
    print(f"Processing scanned document with OCR: {filename}...")
    
    try:
        images = []
        if is_pdf:
            # Convert PDF pages to PIL images
            images = convert_from_path(file_path)
        else:
            # Read single image file
            images = [Image.open(file_path)]
            
        for page_idx, img in enumerate(images):
            page_num = page_idx + 1
            
            # Preprocess the image
            processed_img = preprocess_image(img)
            
            # Perform OCR
            if tesseract_available:
                text = pytesseract.image_to_string(processed_img)
            else:
                text = ""
                print(f"Skipping OCR for page {page_num} of {filename} (Tesseract not available)")
                
            if not text.strip():
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
                    "equipment_tags": ",".join(all_tags) if all_tags else "",
                    "ingestion_method": "OCR"
                }
            })
    except Exception as e:
        print(f"Error OCR loading {file_path}: {e}")
        # Try one last fallback to pdfplumber
        if is_pdf:
            print("Attempting emergency fallback to pdfplumber...")
            from src.ingestion.pdf_loader import load_pdf
            return load_pdf(file_path)
            
    return documents
