from sqlalchemy.orm import Session
from src.loader import load_pdf
from src.ocr_engine import extract_text
from src.parser import extract_metadata
from src.database import add_case, Case
from src.nlp.cleaner import clean_text
from src.nlp.ner_engine import LegalEntityExtractor
from src.table_extractor import extract_tables

# Global instance for lazy loading
_ner_engine = None

def get_ner_engine():
    global _ner_engine
    if _ner_engine is None:
        _ner_engine = LegalEntityExtractor()
    return _ner_engine

def process_case_file(pdf_path: str, session: Session) -> Case:
    """
    Processes a legal case PDF file:
    1. Loads PDF as images.
    2. Performs OCR on each page.
    3. Cleans the extracted text.
    4. Extracts metadata (Date, Case ID).
    5. Extracts Entities (Person, Org) using BERT.
    6. Extracts Tables.
    7. Saves the case to the database.
    
    Args:
        pdf_path (str): Path to the PDF file.
        session (Session): Database session.
        
    Returns:
        Case: The created Case object.
    """
    # 1. Load PDF
    images = load_pdf(pdf_path)
    
    # 2. OCR
    full_text_list = []
    for image in images:
        page_text = extract_text(image)
        full_text_list.append(page_text)
    
    raw_text = "\n".join(full_text_list)
    
    # 3. Clean Text
    cleaned_text = clean_text(raw_text)
    
    # 4. Extract Metadata (from clean text)
    metadata = extract_metadata(cleaned_text)
    
    # 5. Extract Entities (BERT)
    ner = get_ner_engine()
    entities = ner.extract_entities(cleaned_text)
    
    # 6. Extract Tables
    # Note: tabula.read_pdf might take time.
    try:
        raw_tables = extract_tables(pdf_path)
        # Convert DataFrames to JSON-serializable dicts
        tables = [df.to_dict(orient='records') for df in raw_tables]
    except Exception as e:
        print(f"Table extraction failed for {pdf_path}: {e}")
        tables = []

    # Use defaults if metadata not found
    case_id = metadata.get('id')
    order_date = metadata.get('date')
    
    if not case_id:
        case_id = "UNKNOWN" 

    # 7. Save to DB
    new_case = add_case(
        session=session,
        case_id=case_id,
        pdf_path=pdf_path,
        order_date=order_date,
        text_content=cleaned_text,
        entities=entities,
        tables=tables
    )
    
    return new_case
