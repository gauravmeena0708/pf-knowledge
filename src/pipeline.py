from sqlalchemy.orm import Session
from src.loader import load_pdf
from src.ocr_engine import extract_text
from src.parser import extract_metadata
from src.database import add_case, Case

def process_case_file(pdf_path: str, session: Session) -> Case:
    """
    Processes a legal case PDF file:
    1. Loads PDF as images.
    2. Performs OCR on each page.
    3. Extracts metadata (Date, Case ID).
    4. Saves the case to the database.
    
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
    
    full_text = "\n".join(full_text_list)
    
    # 3. Extract Metadata
    metadata = extract_metadata(full_text)
    
    # Use defaults if metadata not found, or handle error
    # For now, we proceed even if partial metadata
    case_id = metadata.get('id')
    order_date = metadata.get('date')
    
    if not case_id:
        # Generate a fallback ID or raise error?
        # Requirement said "Robust ETL", let's assume valid files for now 
        # or use filename as fallback if needed.
        # But to satisfy DB constraint (nullable=False), we need something.
        case_id = "UNKNOWN" 

    # 4. Save to DB
    new_case = add_case(
        session=session,
        case_id=case_id,
        pdf_path=pdf_path,
        order_date=order_date,
        text_content=full_text
    )
    
    return new_case
