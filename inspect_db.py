from src.database import init_db, get_session, Case

def inspect_db():
    engine = init_db()
    session = get_session(engine)
    cases = session.query(Case).all()
    
    print(f"Total Cases in DB: {len(cases)}")
    for case in cases:
        print("-" * 40)
        print(f"ID: {case.id}")
        print(f"Case ID: {case.case_id}")
        print(f"Order Date: {case.order_date}")
        print(f"PDF: {case.pdf_path}")
        print("Text Content Preview (first 500 chars):")
        print(case.text_content[:500] if case.text_content else "NO TEXT CONTENT")
        print(f"Entities: {case.entities}")
        print(f"Tables (Count): {len(case.tables) if case.tables else 0}")
        print("-" * 40)

if __name__ == "__main__":
    inspect_db()
