"""
Build Knowledge Base from Existing Database
Run this after processing PDFs to create the vector index.
"""

from src.database import get_session, init_db
from src.knowledge_base import build_knowledge_base_from_db

def main():
    # Initialize database connection
    db_path = 'sqlite:///elis.db'
    engine = init_db(db_path)
    session = get_session(engine)
    
    print("=" * 50)
    print("Building Knowledge Base from Database")
    print("=" * 50)
    
    # Build knowledge base
    kb = build_knowledge_base_from_db(session)
    
    # Display stats
    stats = kb.get_stats()
    print("\n" + "=" * 50)
    print("Knowledge Base Statistics")
    print("=" * 50)
    print(f"Total Chunks: {stats['total_chunks']}")
    print(f"Indexed Cases: {stats['indexed_cases']}")
    print(f"Storage: ./chroma_db/")
    
    # Test query
    print("\n" + "=" * 50)
    print("Test Query: 'provident fund'")
    print("=" * 50)
    
    result = kb.query("provident fund", n_results=3)
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources: {', '.join(result['sources'])}")
    
    session.close()
    print("\n✅ Knowledge base built successfully!")
    print("You can now use it in the Streamlit app or API.")

if __name__ == "__main__":
    main()
