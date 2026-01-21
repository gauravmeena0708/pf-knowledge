import pytest
from unittest.mock import MagicMock, patch

def test_timeline_extraction_basic():
    """Test basic timeline extraction from sample text."""
    from src.nlp.timeline_extractor import TimelineExtractor
    
    sample_text = """
    On 02.07.2018, the case was called. Shri. R. Kumar (AR) appeared on behalf of the employer.
    The officer directed submission of Form 5A. Case adjourned to 15.08.2018.
    
    On 15.08.2018, the case was called again. No one appeared. Case adjourned to 10.09.2018.
    
    On 10.09.2018, Shri. R. Kumar appeared. Documents were submitted. Order was issued.
    """
    
    extractor = TimelineExtractor()
    timeline = extractor.extract(sample_text)
    
    assert len(timeline) >= 3, f"Expected 3 hearings, got {len(timeline)}"
    
    # Check first hearing
    assert timeline[0]['date'] == '2018-07-02'
    assert 'adjourned' in timeline[0]['outcome'].lower()

def test_timeline_chronological_order():
    """Verify timeline is sorted chronologically."""
    from src.nlp.timeline_extractor import TimelineExtractor
    
    # Dates in reverse order in text
    sample_text = """
    On 15.08.2018, second hearing.
    On 02.07.2018, first hearing.
    On 10.09.2018, third hearing.
    """
    
    extractor = TimelineExtractor()
    timeline = extractor.extract(sample_text)
    
    dates = [e['date'] for e in timeline]
    assert dates == sorted(dates), "Timeline should be chronologically sorted"

def test_timeline_empty_text():
    """Handle empty or no-hearing text gracefully."""
    from src.nlp.timeline_extractor import TimelineExtractor
    
    extractor = TimelineExtractor()
    timeline = extractor.extract("No hearings mentioned here.")
    
    assert timeline == [], "Empty timeline expected for text without hearings"

def test_date_normalization():
    """Test various date formats are normalized."""
    from src.nlp.timeline_extractor import TimelineExtractor
    
    sample_text = """
    Hearing on 2.7.2018. Next on 15-08-2018. Final on 10/09/2018.
    """
    
    extractor = TimelineExtractor()
    timeline = extractor.extract(sample_text)
    
    # All dates should be in YYYY-MM-DD format
    for event in timeline:
        assert len(event['date'].split('-')) == 3
        year, month, day = event['date'].split('-')
        assert len(year) == 4
