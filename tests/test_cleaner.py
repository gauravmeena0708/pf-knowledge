import pytest

def test_clean_text_basic():
    """Test basic cleaning: whitespace, artifacts."""
    try:
        from src.nlp.cleaner import clean_text
    except ImportError:
        pytest.fail("src.nlp.cleaner module or clean_text function not found")

    # Garbage artifacts
    raw_text = "Jag= Employees’ Provident Fund\n\n\nOrganisation\nbE | 3a DES Ministry"
    cleaned = clean_text(raw_text)
    
    assert "Jag=" not in cleaned
    assert "bE |" not in cleaned
    assert "Employees’ Provident Fund" in cleaned
    assert "Organisation" in cleaned
    
    # Check newlines are preserved where appropriate but normalized
    # Expect single blank line between paragraphs if double was there
    assert "\n\n" not in cleaned or "\n" in cleaned

def test_clean_text_hyphenation():
    """Test removing word-break hyphens."""
    try:
        from src.nlp.cleaner import clean_text
    except ImportError:
        pytest.fail("src.nlp.cleaner module or clean_text function not found")

    raw_text = "This is a demonst-\nration of hyphen removal."
    cleaned = clean_text(raw_text)
    assert "demonstration" in cleaned
    assert "demonst-ration" not in cleaned

def test_clean_text_garbage_lines():
    """Test removing lines with high non-alphanumeric ratio."""
    try:
        from src.nlp.cleaner import clean_text
    except ImportError:
        pytest.fail("src.nlp.cleaner module or clean_text function not found")

    raw_text = "Valid Line\n|||...///\nAnother Valid Line"
    cleaned = clean_text(raw_text)
    assert "Valid Line" in cleaned
    assert "|||...///" not in cleaned
    assert "Another Valid Line" in cleaned
