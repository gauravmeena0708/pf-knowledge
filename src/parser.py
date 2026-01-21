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
    # Date pattern: matches "Order Date: DD-MM-YYYY", "Date: DD.MM.YYYY", "Dated: 31 DEC 2025"
    date_pattern = re.compile(r"(?:Order\s*)?Dat[ed]+(?:\s*[:])?\s*(\d{1,2}[-./]\d{1,2}[-./]\d{4}|\d{1,2}\s+[a-zA-Z]{3,}\s+\d{4})", re.IGNORECASE)
    
    # Case ID pattern: "Case ID: ...", "No. ...", "No ..."
    # Capture until a period+space, newline, end of string, or start of Date field.
    id_pattern = re.compile(r"(?:Case\s*ID|No[.])\s*[:]?\s*([0-9A-Za-z/(). -]+?)(?=\s+Dated?|\.\s|\n|$)", re.IGNORECASE)
    
    date_match = date_pattern.search(text)
    if date_match:
        raw_date = date_match.group(1).replace('/', '-').replace('.', '-')
        # Handle "31 DEC 2025" format
        try:
            from datetime import datetime
            # Try specific formats
            if '-' in raw_date:
                 # Assume DD-MM-YYYY
                 d = datetime.strptime(raw_date, "%d-%m-%Y")
                 metadata['date'] = d.strftime("%Y-%m-%d")
            else:
                 # Assume DD MON YYYY
                 d = datetime.strptime(raw_date, "%d %b %Y")
                 metadata['date'] = d.strftime("%Y-%m-%d")
        except ValueError:
            # Fallback or keep raw if parsing fails
            metadata['date'] = raw_date
    
    id_match = id_pattern.search(text)
    if id_match:
        # Cleanup ID
        metadata['id'] = id_match.group(1).strip()
        
    return metadata
