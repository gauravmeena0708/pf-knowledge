import pytesseract
from PIL import Image

def extract_text(image: Image.Image) -> str:
    """
    Extracts text from a PIL Image using Tesseract OCR.
    
    Args:
        image (PIL.Image.Image): The image to process.
        
    Returns:
        str: The extracted text.
        
    Raises:
        pytesseract.TesseractNotFoundError: If Tesseract is not installed or not found.
    """
    try:
        # We can specify language or config here if needed, default is English
        text = pytesseract.image_to_string(image)
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        raise
    except Exception as e:
        # Fallback or re-raise generic errors
        raise e
