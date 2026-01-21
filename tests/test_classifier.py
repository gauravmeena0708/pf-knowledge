import pytest

def test_case_type_classification():
    """Test classification of 7A vs 14B case types."""
    from src.nlp.case_classifier import CaseClassifier
    
    classifier = CaseClassifier()
    
    # 7A case text
    text_7a = "Under Section 7A of EPF Act, determination of dues is made. Total arrears of Rs. 50,000."
    result_7a = classifier.classify(text_7a)
    assert result_7a['case_type'] == '7A'
    
    # 14B case text  
    text_14b = "Penalty under Section 14B is imposed for delayed remittance of contributions."
    result_14b = classifier.classify(text_14b)
    assert result_14b['case_type'] == '14B'

def test_compliance_outcome():
    """Test compliance outcome classification."""
    from src.nlp.case_classifier import CaseClassifier
    
    classifier = CaseClassifier()
    
    # Non-compliant case
    text_nc = "Employer failed to comply with the Act. Dues confirmed. Default assessment applied."
    result_nc = classifier.classify(text_nc)
    assert result_nc['outcome'] == 'non_compliant'
    
    # Compliant case
    text_c = "Records verified. No discrepancy found. Case disposed."
    result_c = classifier.classify(text_c)
    assert result_c['outcome'] == 'compliant'

def test_mixed_case():
    """Test case with both 7A and 14B references."""
    from src.nlp.case_classifier import CaseClassifier
    
    classifier = CaseClassifier()
    
    text = "Section 7A determination with 14B penalty proceedings."
    result = classifier.classify(text)
    
    # Should classify as primary type
    assert result['case_type'] in ['7A', '14B', 'mixed']

def test_empty_text():
    """Handle empty text."""
    from src.nlp.case_classifier import CaseClassifier
    
    classifier = CaseClassifier()
    result = classifier.classify("")
    
    assert result['case_type'] == 'unknown'
