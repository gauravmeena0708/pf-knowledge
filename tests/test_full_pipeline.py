import pytest
from unittest.mock import MagicMock, patch
from src.pipeline import process_case_file
from src.database import Case
from sqlalchemy.orm import Session

@pytest.fixture
def mock_session():
    session = MagicMock(spec=Session)
    return session

@patch('src.pipeline.load_pdf')
@patch('src.pipeline.extract_text')
@patch('src.pipeline.get_case_classifier')
@patch('src.pipeline.get_timeline_extractor')
@patch('src.pipeline.get_gliner_extractor')
def test_process_case_file_integration(
    mock_gliner,
    mock_timeline,
    mock_classifier,
    mock_extract_text,
    mock_load_pdf,
    mock_session
):
    # Setup mocks
    mock_load_pdf.return_value = ["page1"] # 1 page
    mock_extract_text.return_value = "This is a Section 7A order. The establishment failed to pay dues. Hearing on 12-10-2023."
    
    # Mock NLP modules
    mock_classifier_instance = MagicMock()
    mock_classifier_instance.classify.return_value = {
        'case_type': '7A',
        'outcome': 'non_compliant',
        'confidence': 0.9
    }
    mock_classifier.return_value = mock_classifier_instance

    mock_timeline_instance = MagicMock()
    mock_timeline_instance.extract.return_value = [
        {'date': '2023-10-12', 'event': 'Hearing'}
    ]
    mock_timeline.return_value = mock_timeline_instance
    
    mock_gliner_instance = MagicMock()
    mock_gliner_instance.extract.return_value = {
        'Judge': ['Krishan Kumar'],
        'Section': ['7A']
    }
    mock_gliner.return_value = mock_gliner_instance
    
    # Call pipeline
    result_case = process_case_file("dummy.pdf", mock_session)
    
    # Assertions
    assert result_case is not None
    
    # Check if attributes are populated (as per Step 1 requirement)
    # The requirement asks for 'classification', 'timeline', 'gliner_entities'
    # Since these are not yet columns in database.Case, we might expect them attached dynamically
    # or inside the 'entities' JSON.
    
    # Check classification (Case Type) - now directly mapped
    mock_classifier_instance.classify.assert_called_once()
    mock_timeline_instance.extract.assert_called_once()
    mock_gliner_instance.extract.assert_called_once()
    
    # Verify new columns are populated
    assert result_case.section_cited == '7A'
    assert result_case.judge_name == 'Krishan Kumar'
    assert result_case.timeline is not None
    assert len(result_case.timeline) > 0
    assert result_case.timeline[0]['date'] == '2023-10-12'
    
    # Verify entity was merged
    assert 'Judge' in result_case.entities
