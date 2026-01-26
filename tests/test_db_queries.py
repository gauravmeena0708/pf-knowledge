import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, Case, add_case

@pytest.fixture
def db_session():
    # Use in-memory SQLite
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_query_by_judge_name(db_session):
    # Add a case
    add_case(
        session=db_session,
        case_id="7A/2023/1",
        pdf_path="dummy.pdf",
        judge_name="Krishan Kumar",
        section_cited="7A",
        total_dues=50000.0,
        timeline=[{'date': '2023-01-01', 'event': 'Hearing'}]
    )
    
    # Add another case
    add_case(
        session=db_session,
        case_id="14B/2023/2",
        pdf_path="dummy2.pdf",
        judge_name="Other Judge",
        section_cited="14B"
    )
    
    # Query
    results = db_session.query(Case).filter(Case.judge_name == "Krishan Kumar").all()
    
    assert len(results) == 1
    assert results[0].case_id == "7A/2023/1"
    assert results[0].section_cited == "7A"
    assert results[0].timeline[0]['date'] == "2023-01-01"

def test_query_by_section(db_session):
    # Add cases
    add_case(db_session, "1", "p1", section_cited="7A", judge_name="J1")
    add_case(db_session, "2", "p2", section_cited="7A", judge_name="J2")
    add_case(db_session, "3", "p3", section_cited="14B", judge_name="J1")
    
    results = db_session.query(Case).filter(Case.section_cited == "7A").all()
    assert len(results) == 2
