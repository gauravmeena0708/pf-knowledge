import pytest
from PIL import Image, ImageDraw, ImageFont
import pytesseract
try:
    from src.ocr_engine import extract_text
except ImportError:
    pass

@pytest.fixture
def dummy_image(tmp_path):
    """Creates a dummy image with known text."""
    img = Image.new('RGB', (200, 100), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    # Using default font, might want to check if it works or use a specific one
    d.text((10,10), "EPFO ORDER", fill=(0,0,0))
    return img

def test_ocr_extract(dummy_image, monkeypatch):
    """Test that extract_text retrieves the correct string."""
    try:
        from src.ocr_engine import extract_text
    except ImportError:
        pytest.fail("src.ocr_engine module not found")

    # Mock pytesseract.image_to_string to return expected text
    def mock_image_to_string(*args, **kwargs):
        return "EPFO ORDER"
    
    monkeypatch.setattr(pytesseract, "image_to_string", mock_image_to_string)

    text = extract_text(dummy_image)
    assert "EPFO ORDER" in text

def test_ocr_missing_tesseract(monkeypatch):
    """Test handling of TesseractNotFoundError (simulated)."""
    try:
        from src.ocr_engine import extract_text
    except ImportError:
        pytest.fail("src.ocr_engine module not found")
        
    def mock_image_to_string(*args, **kwargs):
        raise pytesseract.TesseractNotFoundError()
        
    monkeypatch.setattr(pytesseract, "image_to_string", mock_image_to_string)
    
    with pytest.raises(pytesseract.TesseractNotFoundError):
         extract_text(Image.new('RGB', (10, 10)))
