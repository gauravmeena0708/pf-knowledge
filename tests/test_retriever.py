import pytest
from unittest.mock import MagicMock
from src.drafter.retriever import PrecedentRetriever
from src.database import Case

@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.database import Base, add_case
    
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Pre-populate DB
    add_case(session, "14B/1", "p1", section_cited="14B", judge_name="J1")
    add_case(session, "7A/2", "p2", section_cited="7A", judge_name="J1")
    add_case(session, "14B/3", "p3", section_cited="14B", judge_name="J2")
    
    yield session
    session.close()

@pytest.fixture
def mock_kb():
    return MagicMock()

def test_retriever_hybrid_search(db_session, mock_kb):
    # Setup
    retriever = PrecedentRetriever(db_session=db_session, vectors_db=mock_kb)
    
    # Mock Vector DB results
    # KB returns chunks. Retriever extracts case_ids from metadata.
    mock_kb.query.return_value = {
        'chunks': [
            {'metadata': {'case_id': '14B/1'}, 'text': 'financial crisis details...'},
            {'metadata': {'case_id': '7A/2'}, 'text': 'evasion of dues...'},
            {'metadata': {'case_id': '14B/3'}, 'text': 'more financial trouble...'}
        ]
    }
    
    # Action
    results = retriever.get_precedents(
        query="Delay due to financial crisis",
        section="14B",
        k=2
    )
    
    # Assert
    # Should only return the 14B cases
    assert len(results) == 2
    
    # Verify we got the correct cases (order might vary depending on list processing, 
    # but retriever implementation preserves semantic order)
    # The Semantic order was 14B/1, 7A/2, 14B/3.
    # 7A/2 is filtered out.
    # So result should be 14B/1, then 14B/3.
    assert results[0].case_id == '14B/1'
    assert results[1].case_id == '14B/3'
    
    # Ensure 7A case was filtered out
    case_ids = [r.case_id for r in results]
    assert '7A/2' not in case_ids
