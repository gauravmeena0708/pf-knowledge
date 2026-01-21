import os
import glob
from sqlalchemy.orm import Session
from src.database import init_db, get_session, Case
from src.pipeline import process_case_file
import pandas as pd

def main():
    # Initialize DB
    db_path = 'sqlite:///elis.db'
    if os.path.exists('elis.db'):
        os.remove('elis.db') # Start fresh for this run
    
    engine = init_db(db_path)
    session = get_session(engine)
    
    # Find all PDFs
    root_dir = "/mnt/c/Users/gaura/Documents/GitHub/pf-knowledge/case_pdfs"
    pdf_files = glob.glob(os.path.join(root_dir, "**/*.pdf"), recursive=True)
    
    print(f"Found {len(pdf_files)} PDF files.")
    
    results = []
    
    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path}")
        try:
            case = process_case_file(pdf_path, session)
            print(f"  -> Success! Case ID: {case.case_id}, Date: {case.order_date}")
            results.append({
                "PDF": os.path.basename(pdf_path),
                "Case ID": case.case_id,
                "Order Date": case.order_date,
                "Status": "Success"
            })
        except Exception as e:
            print(f"  -> Failed: {str(e)}")
            results.append({
                "PDF": os.path.basename(pdf_path),
                "Case ID": "N/A",
                "Order Date": "N/A",
                "Status": f"Failed: {str(e)}"
            })
            
    # Display Summary
    print("\n" + "="*30)
    print("       EXECUTION SUMMARY       ")
    print("="*30)
    df = pd.DataFrame(results)
    if not df.empty:
        print(df.to_string(index=False))
    else:
        print("No results to display.")

if __name__ == "__main__":
    main()
