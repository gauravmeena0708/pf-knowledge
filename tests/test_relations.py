import pytest

def test_relation_extraction_basic():
    """Test extraction of cause-effect relations."""
    from src.nlp.relation_extractor import RelationExtractor
    
    text = """
    The employer failed to submit Form 5A as directed by the officer.
    The officer requested salary register and attendance records.
    Due to non-submission of records, default assessment was applied.
    """
    
    extractor = RelationExtractor()
    relations = extractor.extract(text)
    
    assert len(relations) >= 2
    
    # Check for expected relation types
    relation_types = [r['type'] for r in relations]
    assert 'failure_to_submit' in relation_types or 'non_compliance' in relation_types

def test_officer_request_extraction():
    """Test extraction of officer requests."""
    from src.nlp.relation_extractor import RelationExtractor
    
    text = "The APFC directed the employer to produce Form 12A and salary statements."
    
    extractor = RelationExtractor()
    relations = extractor.extract(text)
    
    # Should find officer request relation
    requests = [r for r in relations if 'request' in r['type'] or 'direct' in r['type']]
    assert len(requests) >= 1

def test_consequence_extraction():
    """Test extraction of consequence relations."""
    from src.nlp.relation_extractor import RelationExtractor
    
    text = "As a result of non-compliance, penalty was imposed under Section 14B."
    
    extractor = RelationExtractor()
    relations = extractor.extract(text)
    
    consequences = [r for r in relations if 'consequence' in r['type'] or 'result' in r['type']]
    assert len(consequences) >= 1

def test_empty_text():
    """Handle empty text gracefully."""
    from src.nlp.relation_extractor import RelationExtractor
    
    extractor = RelationExtractor()
    relations = extractor.extract("")
    
    assert relations == []
