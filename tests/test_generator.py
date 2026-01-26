import pytest
from unittest.mock import MagicMock, patch
from src.drafter.generator import OrderGenerator
from src.database import Case

@patch('src.drafter.generator.ChatOpenAI')
def test_generate_order(mock_chat_openai):
    # Setup Mock LLM
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value.content = "ORDER\n\nThis is a generated order specific to the submissions."
    mock_chat_openai.return_value = mock_llm_instance
    
    generator = OrderGenerator()
    
    # Inputs
    submissions = "The establishment pleads financial difficulty due to Covid-19."
    precedents = [
        Case(case_id="1", text_content="Precedent 1: Financial difficulty rejected regarding employee shares.", judge_name="Krishan Kumar", section_cited="7A"),
        Case(case_id="2", text_content="Precedent 2: Allowed installment payment.", judge_name="Krishan Kumar", section_cited="7A")
    ]
    judge_name = "Krishan Kumar"
    section = "7A"
    
    # Action
    draft = generator.generate_draft(submissions, precedents, judge_name, section)
    
    # Assert
    assert "ORDER" in draft
    assert "This is a generated order" in draft
    
    # Verify Prompt Construction
    # We check if invokes was called with a prompt containing our inputs
    args, _ = mock_llm_instance.invoke.call_args
    prompt_sent = args[0]
    # prompt_sent is a String or Message list depending on implementation. 
    # If using invoke on ChatOpenAI, it gets messages usually, or string.
    # We'll inspect string representation
    prompt_str = str(prompt_sent)
    
    assert "Krishan Kumar" in prompt_str
    assert "Covid-19" in prompt_str
    assert "Precedent 1" in prompt_str
