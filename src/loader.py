import os
from pdf2image import convert_from_path
from typing import List
from PIL import Image

def load_pdf(path: str) -> List[Image.Image]:
    """
    Loads a PDF file and converts it to a list of PIL Images.
    
    Args:
        path (str): The absolute or relative path to the PDF file.
        
    Returns:
        List[Image.Image]: A list of PIL Image objects, one for each page.
        
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF file not found at: {path}")
        
    # convert_from_path handles the conversion
    # We might need poppler installed on the system, but let's assume it is 
    # or pdf2image will raise an error which is also fine for now.
    # The user requirement said "Environment: WSL".
    try:
        images = convert_from_path(path)
        return images
    except Exception as e:
        # Wrap or re-raise exceptions as needed
        raise e
