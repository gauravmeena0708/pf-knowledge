import pytest
from unittest.mock import MagicMock, patch

def test_legal_ner_logic():
    """
    Test extraction logic and post-processing independently of the model.
    """
    try:
        from src.nlp.entity_extractor import GLiNEREntityExtractor
    except ImportError:
        pytest.fail("src.nlp.entity_extractor not found")

    # Mock the internal model to avoid heavy loading
    with patch('gliner.GLiNER.from_pretrained') as mock_load:
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        
        extractor = GLiNEREntityExtractor()
        
        # Setup mock predictions
        # "Order passed by APFC Krishan Kumar against M/s City Auto Mobiles. Due: Rs. 40,704/-"
        mock_model.predict_entities.return_value = [
            {'label': 'Judge', 'text': 'Krishan Kumar', 'score': 0.9},
            {'label': 'Establishment', 'text': 'City Auto Mobiles', 'score': 0.8},
            {'label': 'Amount', 'text': 'Rs. 40,704/-', 'score': 0.85}
        ]
        
        results = extractor.extract("Dummy text")
        
        # Assertions
        assert "Krishan Kumar" in results['Judge']
        assert "City Auto Mobiles" in results['Establishment']
        assert 40704.0 in results['Amount']
        assert isinstance(results['Amount'][0], float)

def test_amount_cleaning():
    from src.nlp.entity_extractor import GLiNEREntityExtractor
    extractor = GLiNEREntityExtractor()
    
    assert extractor._clean_amount("Rs. 1,00,000/-") == 100000.0
    assert extractor._clean_amount("5000") == 5000.0
    assert extractor._clean_amount("invalid") is None
