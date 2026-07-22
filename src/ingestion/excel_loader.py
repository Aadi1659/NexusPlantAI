import os
import pandas as pd
from src.ingestion.pdf_loader import extract_equipment_tags

def load_csv_or_excel(file_path):
    """
    Ingests tabular CSV or Excel files. Performs row-by-row natural language text serialization.
    """
    filename = os.path.basename(file_path)
    documents = []
    
    print(f"Loading tabular log: {filename}...")
    try:
        # Load file based on extension
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        # Clean column names
        columns = [col.strip() for col in df.columns]
        df.columns = columns
        
        is_maintenance = 'Log_ID' in columns and 'Equipment_ID_Name' in columns
        is_incident = 'Report_ID' in columns and 'Severity' in columns
        
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            # Clean values (replace NaN with 'None')
            cleaned_row = {k: str(v).strip() if pd.notna(v) else "None" for k, v in row_dict.items()}
            
            if is_maintenance:
                # Custom maintenance record layout
                text = (
                    f"Maintenance Log {cleaned_row.get('Log_ID')}: "
                    f"Equipment: {cleaned_row.get('Equipment_ID_Name')} | "
                    f"Date: {cleaned_row.get('Date')} | "
                    f"Type: {cleaned_row.get('Maintenance_Type')} | "
                    f"Technician: {cleaned_row.get('Technician')} | "
                    f"Run Hours: {cleaned_row.get('Hours_Run_Since_Last_Maint')} | "
                    f"Observation: {cleaned_row.get('Observation_Remarks')} | "
                    f"Parts Replaced: {cleaned_row.get('Parts_Replaced')} | "
                    f"Downtime: {cleaned_row.get('Downtime_Hours')} hours | "
                    f"Next Scheduled: {cleaned_row.get('Next_Scheduled_Maint')}"
                )
                eq_tag = cleaned_row.get('Equipment_ID_Name')
                record_id = cleaned_row.get('Log_ID')
                doc_type = "maintenance_records"
            elif is_incident:
                # Custom incident record layout
                text = (
                    f"Incident Report {cleaned_row.get('Report_ID')}: "
                    f"Date: {cleaned_row.get('Date')} | "
                    f"Location: {cleaned_row.get('Location')} | "
                    f"Severity: {cleaned_row.get('Severity')} | "
                    f"Probable Cause: {cleaned_row.get('Probable_Cause')} | "
                    f"Description: {cleaned_row.get('Description')} | "
                    f"Reported By: {cleaned_row.get('Reported_By')} | "
                    f"Corrective Action: {cleaned_row.get('Corrective_Action')} | "
                    f"Status: {cleaned_row.get('Status')}"
                )
                eq_tag = ""
                record_id = cleaned_row.get('Report_ID')
                doc_type = "maintenance_records"
            else:
                # Fallback generic key-value serialization
                kv_pairs = [f"{k}: {v}" for k, v in cleaned_row.items()]
                text = f"Record from {filename} row {idx}: " + " | ".join(kv_pairs)
                eq_tag = ""
                record_id = f"ROW-{idx}"
                doc_type = "maintenance_records"
                
            # Extract equipment tags from text
            all_tags = extract_equipment_tags(text)
            if not all_tags and eq_tag:
                all_tags = extract_equipment_tags(eq_tag)
                
            documents.append({
                "text": text,
                "metadata": {
                    "source_file": filename,
                    "row_index": idx,
                    "record_id": record_id,
                    "doc_type": doc_type,
                    "equipment_tags": ",".join(all_tags) if all_tags else ""
                }
            })
            
    except Exception as e:
        print(f"Error loading CSV/Excel {file_path}: {e}")
        
    return documents
