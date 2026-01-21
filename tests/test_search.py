import pytest
from unittest.mock import MagicMock, patch

def test_index_and_search():
    """Test indexing documents and searching."""
    from src.nlp.semantic_search import SemanticSearch
    
    documents = [
        {"id": "1", "text": "Employer failed to remit provident fund contributions."},
        {"id": "2", "text": "Penalty imposed for delayed payment under Section 14B."},
        {"id": "3", "text": "Case dismissed as records were verified and found correct."},
    ]
    
    search = SemanticSearch()
    search.index(documents)
    
    # Search for similar cases
    results = search.search("provident fund default", top_k=2)
    
    assert len(results) >= 1
    # First result should be most relevant
    assert results[0]['id'] in ['1', '2']

def test_similarity_score():
    """Test that similarity scores are returned."""
    from src.nlp.semantic_search import SemanticSearch
    
    documents = [
        {"id": "1", "text": "Payment was made on time."},
        {"id": "2", "text": "Payment was delayed by 6 months."},
    ]
    
    search = SemanticSearch()
    search.index(documents)
    
    results = search.search("delayed payment", top_k=2)
    
    # Should have similarity scores
    assert all('score' in r for r in results)
    # Second doc should be more relevant
    assert results[0]['id'] == '2'

def test_empty_index():
    """Handle search on empty index."""
    from src.nlp.semantic_search import SemanticSearch
    
    search = SemanticSearch()
    results = search.search("any query")
    
    assert results == []
