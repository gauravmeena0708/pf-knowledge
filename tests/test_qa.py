import pytest

def test_total_dues_question():
    """Test answering 'What was the total dues?'"""
    from src.nlp.qa_engine import QAEngine
    
    context = """
    The total dues assessed under Section 7A amount to Rs. 7,39,196/-. 
    This includes employee share, employer share, and admin charges.
    """
    
    qa = QAEngine()
    answer = qa.answer("What was the total dues?", context)
    
    assert '739196' in answer.replace(',', '').replace(' ', '') or '7,39,196' in answer

def test_hearing_count_question():
    """Test answering 'How many hearings were held?'"""
    from src.nlp.qa_engine import QAEngine
    
    context = """
    The case was heard on 15 occasions. First hearing on 02.07.2018,
    followed by hearings on 15.08.2018, 10.09.2018, and 12 more dates.
    Final hearing concluded on 25.11.2019.
    """
    
    qa = QAEngine()
    answer = qa.answer("How many hearings were held?", context)
    
    assert '15' in answer

def test_officer_name_question():
    """Test answering 'Who is the officer?'"""
    from src.nlp.qa_engine import QAEngine
    
    context = """
    Order passed by Shri. D. GOVINDARAJAN, Assistant Provident Fund Commissioner,
    Regional Office, Ambattur.
    """
    
    qa = QAEngine()
    answer = qa.answer("Who is the officer?", context)
    
    assert 'govindarajan' in answer.lower() or 'commissioner' in answer.lower()

def test_empty_context():
    """Handle empty context."""
    from src.nlp.qa_engine import QAEngine
    
    qa = QAEngine()
    answer = qa.answer("What is the case number?", "")
    
    assert answer == "" or answer.lower() == "not found"
