import pytest
import pandas as pd
import os
from unittest.mock import patch

try:
    from src.table_extractor import extract_tables
except ImportError:
    pass

@pytest.fixture
def dummy_pdf_path(tmp_path):
    return str(tmp_path / "table_test.pdf")

def test_extract_tables_import():
    try:
        from src.table_extractor import extract_tables
    except ImportError:
        pytest.fail("src.table_extractor module or extract_tables function not found")

@patch('src.table_extractor.tabula.read_pdf')
def test_extract_tables_success(mock_read_pdf, dummy_pdf_path):
    """
    Test extraction using mocked tabula.
    We mock tabula because we don't have a real PDF with tables handy 
    and tabula might require Java which might be missing.
    """
    try:
        from src.table_extractor import extract_tables
    except ImportError:
        pytest.fail("src.table_extractor module or extract_tables function not found")

    # Mock return value as a list of DataFrames
    mock_df = pd.DataFrame({'Col1': [1, 2], 'Col2': [3, 4]})
    mock_read_pdf.return_value = [mock_df]

    # Create dummy file so os.path.exists passes
    with open(dummy_pdf_path, 'w') as f:
        f.write("dummy")

    tables = extract_tables(dummy_pdf_path)
    
    assert len(tables) == 1
    assert isinstance(tables[0], pd.DataFrame)
    assert tables[0].equals(mock_df)

def test_extract_tables_no_file():
    """Test handling of missing file."""
    try:
        from src.table_extractor import extract_tables
    except ImportError:
        pytest.fail("src.table_extractor module or extract_tables function not found")
        
    with pytest.raises(FileNotFoundError):
        extract_tables("non_existent.pdf")
