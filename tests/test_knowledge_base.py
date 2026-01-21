import pytest
from unittest.mock import MagicMock
import tempfile
import shutil

def test_knowledge_base_creation():
    """Test creating knowledge base."""
    from src.knowledge_base import LegalKnowledgeBase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = LegalKnowledgeBase(persist_directory=tmpdir)
        stats = kb.get_stats()
        
        assert stats['total_chunks'] == 0
        assert stats['indexed_cases'] == 0

def test_add_case_to_kb():
    """Test adding a case to knowledge base."""
    from src.knowledge_base import LegalKnowledgeBase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = LegalKnowledgeBase(persist_directory=tmpdir)
        
        # Mock case
        mock_case = MagicMock()
        mock_case.id = 1
        mock_case.case_id = "TEST/001"
        mock_case.order_date = "2024-01-01"
        mock_case.text_content = "This is a test case about EPF compliance. " * 50
        mock_case.entities = {"PER": ["Test Person"], "ORG": ["Test Org"]}
        
        kb.add_case(mock_case)
        
        stats = kb.get_stats()
        assert stats['indexed_cases'] == 1
        assert stats['total_chunks'] > 0

def test_query_knowledge_base():
    """Test querying knowledge base."""
    from src.knowledge_base import LegalKnowledgeBase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = LegalKnowledgeBase(persist_directory=tmpdir)
        
        # Add mock case
        mock_case = MagicMock()
        mock_case.id = 1
        mock_case.case_id = "TEST/001"
        mock_case.order_date = "2024-01-01"
        mock_case.text_content = "Employer failed to remit provident fund contributions."
        mock_case.entities = {}
        
        kb.add_case(mock_case)
        
        # Query
        result = kb.query("provident fund")
        
        assert 'answer' in result
        assert 'sources' in result
        assert len(result['sources']) > 0

def test_find_similar_cases():
    """Test finding similar cases."""
    from src.knowledge_base import LegalKnowledgeBase
    
    with tempfile.TemporaryDirectory() as tmpdir:
        kb = LegalKnowledgeBase(persist_directory=tmpdir)
        
        # Add two cases
        case1 = MagicMock()
        case1.id = 1
        case1.case_id = "TEST/001"
        case1.text_content = "Employer failed to submit Form 5A."
        case1.entities = {}
        case1.order_date = None
        
        case2 = MagicMock()
        case2.id = 2
        case2.case_id = "TEST/002"
        case2.text_content = "Employer did not submit required forms."
        case2.entities = {}
        case2.order_date = None
        
        kb.add_case(case1)
        kb.add_case(case2)
        
        # Find similar to case1
        similar = kb.find_similar_cases("TEST/001", n_results=1)
        
        assert len(similar) > 0
        assert similar[0]['case_id'] == "TEST/002"
