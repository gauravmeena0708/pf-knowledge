import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for better OCR accuracy.
    
    Steps:
    1. Convert to grayscale
    2. Denoise
    3. Contrast enhancement (CLAHE)
    4. Binarization (Otsu's thresholding)
    
    Args:
        image: PIL Image to preprocess
        
    Returns:
        Preprocessed PIL Image
    """
    try:
        # Convert PIL to OpenCV format
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 1. Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 2. Denoise using Non-local Means Denoising
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # 3. Contrast enhancement using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 4. Binarization using Otsu's method
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL Image
        return Image.fromarray(binary)
    
    except Exception as e:
        # If preprocessing fails, return original image
        print(f"Warning: Image preprocessing failed: {e}. Using original image.")
        return image

def extract_text(image: Image.Image, preprocess: bool = True) -> str:
    """
    Extracts text from a PIL Image using Tesseract OCR.
    
    Args:
        image (PIL.Image.Image): The image to process.
        preprocess (bool): Whether to apply preprocessing (default: True)
        
    Returns:
        str: The extracted text.
        
    Raises:
        pytesseract.TesseractNotFoundError: If Tesseract is not installed or not found.
    """
    try:
        # Preprocess image if enabled
        if preprocess:
            image = preprocess_image(image)
        
        # Tesseract config for better accuracy
        # --oem 3: Use LSTM OCR Engine
        # --psm 6: Assume uniform block of text
        custom_config = r'--oem 3 --psm 6'
        
        text = pytesseract.image_to_string(image, config=custom_config)
        return text.strip()
    
    except pytesseract.TesseractNotFoundError:
        raise
    except Exception as e:
        # Fallback: try without preprocessing
        if preprocess:
            print(f"OCR with preprocessing failed: {e}. Retrying without preprocessing...")
            return extract_text(image, preprocess=False)
        raise e
