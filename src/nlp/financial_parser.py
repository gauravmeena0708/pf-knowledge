import re
from typing import Dict, Optional, Any
import pandas as pd

class FinancialParser:
    """
    Parses Schedule tables from EPF case documents to extract
    account-wise dues breakdown.
    """
    
    def __init__(self):
        # Account mapping patterns - use word boundaries and more specific patterns
        self.account_patterns = {
            'ee_share_ac1': [r'\bee\b.*share', r'employee.*share'],
            'er_share_ac1': [r'\ber\b.*share', r'employer.*share', r'employer.*contribution'],
            'admin_charges_ac2': [r'admin.*charge', r'a/c\s*2\)', r'account\s*2(?!\d)'],
            'pension_fund_ac10': [r'pension', r'a/c\s*10', r'account\s*10'],
            'insurance_ac21': [r'insurance(?!\s*admin)', r'a/c\s*21', r'account\s*21', r'edli'],
            'insurance_admin_ac22': [r'insurance.*admin', r'a/c\s*22', r'account\s*22'],
        }

    def parse_schedule(self, table: pd.DataFrame) -> Dict[str, Any]:
        """
        Parse a Schedule table DataFrame and extract dues breakdown.
        
        Args:
            table: DataFrame from tabula-py extraction
            
        Returns:
            Dict with account-wise breakdown and total
        """
        if table is None or table.empty:
            return {}
        
        result = {}
        
        # Find columns that look like account names and amounts
        account_col = self._find_column(table, ['account', 'particular', 'head', 'type'])
        amount_col = self._find_column(table, ['amount', 'dues', 'rs', 'total', 'sum'])
        
        if account_col is None or amount_col is None:
            # Try first two columns as fallback
            if len(table.columns) >= 2:
                account_col = table.columns[0]
                amount_col = table.columns[1]
            else:
                return {}
        
        # Extract values
        for _, row in table.iterrows():
            account_text = str(row.get(account_col, '')).lower()
            amount_text = str(row.get(amount_col, ''))
            
            amount = self._clean_amount(amount_text)
            if amount is None:
                continue
            
            # Match to known account types - stop at first match
            matched = False
            for account_key, patterns in self.account_patterns.items():
                if matched:
                    break
                for pattern in patterns:
                    if re.search(pattern, account_text, re.IGNORECASE):
                        # Only set if not already set (first match wins per row)
                        if account_key not in result:
                            result[account_key] = amount
                        matched = True
                        break
        
        # Calculate total
        if result:
            result['total_dues'] = sum(v for v in result.values() if isinstance(v, (int, float)))
        
        return result

    def _find_column(self, table: pd.DataFrame, keywords: list) -> Optional[str]:
        """Find column name matching any of the keywords."""
        for col in table.columns:
            col_lower = str(col).lower()
            for kw in keywords:
                if kw in col_lower:
                    return col
        return None

    def _clean_amount(self, amount_str: str) -> Optional[float]:
        """
        Clean amount string to float.
        Handles: "Rs. 1,00,000/-", "50,000", etc.
        """
        if not amount_str:
            return None
        
        # Remove Rs., ₹, -, /, and commas
        text = str(amount_str).lower()
        text = text.replace('rs.', '').replace('rs', '').replace('₹', '')
        text = text.replace(',', '').replace('/-', '').replace('-', '')
        
        # Extract digits and decimal
        clean = re.sub(r'[^\d.]', '', text)
        
        if not clean:
            return None
        
        try:
            return float(clean)
        except ValueError:
            return None

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract financial details from raw text using regex patterns.
        Fallback when table extraction fails.
        
        Args:
            text: Raw document text
            
        Returns:
            Dict with extracted amounts
        """
        result = {}
        
        # Pattern for amounts with labels
        patterns = [
            (r'ee\s*share[:\s]*(?:rs\.?\s*)?([\d,]+)', 'ee_share_ac1'),
            (r'er\s*share[:\s]*(?:rs\.?\s*)?([\d,]+)', 'er_share_ac1'),
            (r'admin(?:istration)?\s*charges?[:\s]*(?:rs\.?\s*)?([\d,]+)', 'admin_charges_ac2'),
            (r'pension\s*fund?[:\s]*(?:rs\.?\s*)?([\d,]+)', 'pension_fund_ac10'),
            (r'total\s*dues?[:\s]*(?:rs\.?\s*)?([\d,]+)', 'total_dues'),
        ]
        
        for pattern, key in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = self._clean_amount(match.group(1))
                if amount:
                    result[key] = amount
        
        return result
