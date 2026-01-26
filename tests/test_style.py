import pytest
from src.drafter.style_engine import StyleAnalyzer

def test_analyze_style_structure():
    text = """
    EMPLOYEES PROVIDENT FUND ORGANISATION
    Proceedings of the Assistant Provident Fund Commissioner...
    
    IN THE MATTER OF:
    M/s ABC Corp
    
    PRESENT:
    Sh. X for Dept
    Sh. Y for Estt
    
    ORDER
    
    This is an inquiry under Section 7A.
    The establishment failed to remit dues.
    
    ORDER
    I hereby assess the dues.
    
    (Krishan Kumar)
    APFC
    """
    
    analyzer = StyleAnalyzer()
    style = analyzer.analyze(text)
    
    assert 'header' in style
    assert 'appearance' in style
    assert 'body' in style
    assert 'signature' in style
    
    # Check specific extractions
    assert "Proceedings of the Assistant Provident Fund Commissioner" in style['header']
    assert "Sh. X for Dept" in style['appearance']
    assert "Krishan Kumar" in style['signature']
