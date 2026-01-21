import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

def test_financial_table_parsing():
    """Test parsing of Schedule table with account breakdowns."""
    from src.nlp.financial_parser import FinancialParser
    
    # Simulate tabula output (list of DataFrames)
    mock_table = pd.DataFrame({
        'Account': ['EE Share (A/c 1)', 'ER Share (A/c 1)', 'Admin Charges (A/c 2)', 
                    'Pension Fund (A/c 10)', 'Insurance (A/c 21)', 'Insurance Admin (A/c 22)'],
        'Amount': ['1,00,000', '1,50,000', '25,000', '50,000', '10,000', '5,000']
    })
    
    parser = FinancialParser()
    result = parser.parse_schedule(mock_table)
    
    assert result['ee_share_ac1'] == 100000.0
    assert result['er_share_ac1'] == 150000.0
    assert result['admin_charges_ac2'] == 25000.0
    assert result['pension_fund_ac10'] == 50000.0
    assert result['insurance_ac21'] == 10000.0
    assert result['insurance_admin_ac22'] == 5000.0

def test_total_calculation():
    """Verify total_dues equals sum of breakdown."""
    from src.nlp.financial_parser import FinancialParser
    
    mock_table = pd.DataFrame({
        'Account': ['EE Share', 'ER Share', 'Admin'],
        'Amount': ['100', '200', '50']
    })
    
    parser = FinancialParser()
    result = parser.parse_schedule(mock_table)
    
    total = result.get('total_dues', 0)
    breakdown_sum = sum(v for k, v in result.items() if k != 'total_dues' and isinstance(v, (int, float)))
    
    assert total == breakdown_sum, f"Total {total} != Sum {breakdown_sum}"

def test_amount_cleaning():
    """Test various amount formats are cleaned correctly."""
    from src.nlp.financial_parser import FinancialParser
    
    parser = FinancialParser()
    
    assert parser._clean_amount("Rs. 1,00,000/-") == 100000.0
    assert parser._clean_amount("50,000") == 50000.0
    assert parser._clean_amount("739196") == 739196.0
    assert parser._clean_amount("invalid") is None

def test_empty_table():
    """Handle empty or malformed tables."""
    from src.nlp.financial_parser import FinancialParser
    
    parser = FinancialParser()
    result = parser.parse_schedule(pd.DataFrame())
    
    assert result == {}, "Empty table should return empty dict"
