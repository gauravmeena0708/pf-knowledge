import os
import pytest
from pypdf import PdfWriter
from src.loader import load_pdf

@pytest.fixture
def dummy_pdf(tmp_path):
    """Creates a dummy PDF file for testing."""
    pdf_path = tmp_path / "test.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)

def test_pdf_load_exists(dummy_pdf):
    """Test that load_pdf can load a valid PDF file."""
    assert os.path.exists(dummy_pdf)
    
    # This should fail if load_pdf is not implemented or imports fail
    if load_pdf is None:
        pytest.fail("src.loader module or load_pdf function not found")
        
    images = load_pdf(dummy_pdf)
    assert images is not None
    assert len(images) > 0
    # pdf2image returns a list of PIL images
    from PIL import Image
    assert isinstance(images[0], Image.Image)

def test_pdf_load_missing():
    """Test that load_pdf raises FileNotFoundError for missing file."""
    if load_pdf is None:
        pytest.fail("src.loader module or load_pdf function not found")
        
    with pytest.raises(FileNotFoundError):
        load_pdf("non_existent_file.pdf")
