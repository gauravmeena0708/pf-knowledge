import pytest
from unittest.mock import MagicMock, patch

def test_key_phrase_extraction():
    """Test extraction of top key phrases."""
    from src.nlp.summarizer import Summarizer
    
    text = """
    The employer M/s City Auto Mobiles failed to remit provident fund contributions 
    for the period April 2018 to March 2019. The APFC conducted multiple hearings 
    and directed submission of Form 5A and salary registers. Due to non-submission,
    default assessment was applied under Section 7A of the EPF Act.
    """
    
    summarizer = Summarizer()
    phrases = summarizer.extract_key_phrases(text, top_n=5)
    
    assert len(phrases) >= 3
    # Check that relevant terms are in key phrases
    phrase_text = ' '.join([p[0].lower() for p in phrases])
    assert any(term in phrase_text for term in ['provident', 'fund', 'employer', 'section', 'assessment'])

def test_extractive_summary():
    """Test extractive summary generation."""
    from src.nlp.summarizer import Summarizer
    
    text = """
    First sentence about the case. Second sentence with details about employer.
    Third sentence about officer directions. Fourth sentence about outcome.
    Fifth sentence with financial details. Sixth sentence about penalty.
    """
    
    summarizer = Summarizer()
    summary = summarizer.summarize_extractive(text, num_sentences=3)
    
    # Should return 3 sentences
    sentences = [s for s in summary.split('.') if s.strip()]
    assert len(sentences) <= 3

def test_empty_text():
    """Handle empty text."""
    from src.nlp.summarizer import Summarizer
    
    summarizer = Summarizer()
    
    phrases = summarizer.extract_key_phrases("")
    assert phrases == []
    
    summary = summarizer.summarize_extractive("")
    assert summary == ""
