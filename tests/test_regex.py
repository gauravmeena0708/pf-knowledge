import pytest
try:
    from src.parser import extract_metadata
except ImportError:
    pass

def test_extract_metadata_success():
    """Test successful extraction of date and case ID."""
    try:
        from src.parser import extract_metadata
    except ImportError:
        pytest.fail("src.parser module or extract_metadata function not found")

    text = "Some random text. Order Date: 12-05-2023. More text. Case ID: 7A/123. End of text."
    metadata = extract_metadata(text)
    
    assert metadata['date'] == '2023-05-12'
    assert metadata['id'] == '7A/123'

def test_extract_metadata_formats():
    """Test different formats if applicable, or robustness."""
    try:
        from src.parser import extract_metadata
    except ImportError:
        pytest.fail("src.parser module or extract_metadata function not found")

    # Example with different spacing or context
    text = "Case ID :  14B/999  \n Order Date : 01-01-2024"
    metadata = extract_metadata(text)
    
    assert metadata['date'] == '2024-01-01'
    assert metadata['id'] == '14B/999'

def test_extract_metadata_none():
    """Test robustness when metadata is missing."""
    try:
        from src.parser import extract_metadata
    except ImportError:
        pytest.fail("src.parser module or extract_metadata function not found")

    text = "No metadata here."
    metadata = extract_metadata(text)
    
    assert metadata['date'] is None
    assert metadata['id'] is None
