import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from src.pipeline import process_case_file
    from src.database import Base, get_case
except ImportError:
    pass

@pytest.fixture
def mock_session():
    """Creates an in-memory SQLite database session."""
    engine = create_engine('sqlite:///:memory:')
    try:
        from src.database import Base
        Base.metadata.create_all(engine)
    except ImportError:
        pass
        
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@patch('src.pipeline.load_pdf')
@patch('src.pipeline.extract_text')
@patch('src.pipeline.extract_tables')
@patch('src.pipeline.get_ner_engine')
def test_process_case_file(mock_get_ner, mock_tables, mock_extract_text, mock_load_pdf, mock_session):
    """
    Test the full pipeline with mocked IO components.
    """
    try:
        from src.pipeline import process_case_file
        from src.database import get_case
    except ImportError:
        pytest.fail("src.pipeline module or process_case_file function not found")

    # Setup mocks
    # mock_load_pdf returns a list of dummy images
    mock_load_pdf.return_value = ["dummy_image_obj"]
    
    # mock_extract_text returns a string with valid metadata
    mock_extract_text.return_value = "Content here. Order Date: 20-10-2023. Case ID: 7A/555. End."
    
    # Mock NER
    mock_ner_instance = MagicMock()
    mock_ner_instance.extract_entities.return_value = {"PER": ["Test Person"]}
    mock_get_ner.return_value = mock_ner_instance
    
    # Mock Tables - return DataFrame-like objects
    mock_df = MagicMock()
    mock_df.to_dict.return_value = [{"A": 1, "B": 2}]
    mock_tables.return_value = [mock_df]

    pdf_path = "/tmp/test_case.pdf"
    
    # Run pipeline
    result_case = process_case_file(pdf_path, mock_session)
    
    # Verify DB insertion
    saved_case = get_case(mock_session, "7A/555")
    
    assert saved_case is not None
    assert saved_case.order_date == "2023-10-20"
    assert saved_case.pdf_path == pdf_path
    assert saved_case.id is not None
    # Verify new fields
    assert saved_case.entities == {"PER": ["Test Person"]}
    assert saved_case.tables == [[{"A": 1, "B": 2}]]
    
    # Verify interactions
    mock_load_pdf.assert_called_once_with(pdf_path)
    mock_extract_text.assert_called()
    mock_tables.assert_called_once_with(pdf_path)
    mock_ner_instance.extract_entities.assert_called()
