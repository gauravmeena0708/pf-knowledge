import os
import tabula
import pandas as pd
from typing import List

def extract_tables(pdf_path: str) -> List[pd.DataFrame]:
    """
    Extracts tables from a PDF using Tabula.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        List[pd.DataFrame]: A list of DataFrames representing extracted tables.
        
    Raises:
        FileNotFoundError: If the PDF file does not exist.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        
    try:
        # pages='all' extracts tables from all pages
        # multiple_tables=True handles multiple tables on one page
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        return tables
    except Exception as e:
        # Re-raise or handle specific tabula errors
        raise e
