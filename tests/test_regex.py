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

def test_extract_metadata_real_world():
    """Test formats found in actual PDFs."""
    try:
        from src.parser import extract_metadata
    except ImportError:
        pytest.fail("src.parser module or extract_metadata function not found")

    # Example 1: Chennai format
    text1 = "No.TN/RO-AMB/CC-II/A-7(2)/16565 16/2019 Date: 25.11.2019"
    meta1 = extract_metadata(text1)
    # Flexible ID matching (strip "No." and whitespace)
    assert "TN/RO-AMB" in meta1['id'] 
    assert meta1['date'] == '2019-11-25'

    # Example 2: Amritsar format (approximate based on OCR)
    text2 = "No. RO/ASR/43012. Dated: 31 DEC 2025"
    meta2 = extract_metadata(text2)
    assert "RO/ASR/43012" in meta2['id']
    # Note: parser needs to handle DD MMM YYYY
    assert meta2['date'] == '2025-12-31'

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

def test_invalid_dates():
    """Test that invalid dates are not extracted."""
    from src.parser import extract_metadata
    
    # User reported case
    text = "Order Date: 68-07-2025."
    metadata = extract_metadata(text)
    # Should ideally return None or fail parsing and fallback to something valid?
    # Current implementation falls back to raw string. We want it to be None or validated.
    # If validation fails, it might return raw string currently.
    # We want to change behavior so if it's invalid, it doesn't return garbage.
    
    # If we implement strict validation, this should be None.
    # If logic is "try parse, else return raw", it returns "68-07-2025".
    # User wants to PREVENT this from DB. So we assert it is NOT "68-07-2025".
    assert metadata['date'] is None, f"Expected None for invalid date, got {metadata['date']}"
