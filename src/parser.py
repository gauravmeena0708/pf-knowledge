import re
from typing import Dict, Optional

def extract_metadata(text: str) -> Dict[str, Optional[str]]:
    """
    Extracts metadata like 'Order Date' and 'Case ID' from the text.
    
    Args:
        text (str): The raw text extracted from OCR.
        
    Returns:
        dict: A dictionary containing 'date' and 'id'. 
    """
    metadata = {
        'date': None,
        'id': None
    }
    
    # Regex patterns
    # Date pattern: attempts to find DD-MM-YYYY or DD/MM/YYYY
    # This is a basic implementation, can be improved for robustness
    date_pattern = re.compile(r"Order Date\s*[:]\s*(\d{2}[-/]\d{2}[-/]\d{4})", re.IGNORECASE)
    
    # Case ID pattern: matches 7A/numbers or 14B/numbers
    # Adjust regex based on expected format
    id_pattern = re.compile(r"Case ID\s*[:]\s*([0-9A-Za-z/]+)", re.IGNORECASE)
    
    date_match = date_pattern.search(text)
    if date_match:
        date_str = date_match.group(1).replace('/', '-')
        parts = date_str.split('-')
        # Simple reformat to YYYY-MM-DD
        if len(parts) == 3:
            metadata['date'] = f"{parts[2]}-{parts[1]}-{parts[0]}"
    
    id_match = id_pattern.search(text)
    if id_match:
        metadata['id'] = id_match.group(1).strip()
        
    return metadata
