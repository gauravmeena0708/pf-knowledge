import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

try:
    from src.database import Base, Case, init_db, add_case, get_case
except ImportError:
    pass

@pytest.fixture
def session():
    """Creates an in-memory SQLite database session."""
    engine = create_engine('sqlite:///:memory:')
    try:
        from src.database import Base
        Base.metadata.create_all(engine)
    except ImportError:
        pytest.fail("src.database module or Base class not found")
        
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_db_schema_creation(session):
    """Test that the Case table is created."""
    engine = session.get_bind()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert 'cases' in tables

def test_add_and_get_case(session):
    """Test adding and retrieving a case."""
    try:
        from src.database import add_case, get_case
    except ImportError:
        pytest.fail("src.database module or functions not found")

    case_data = {
        'case_id': '7A/123',
        'order_date': '2023-05-12',
        'pdf_path': '/tmp/test.pdf',
        'text_content': 'Sample text'
    }
    
    case = add_case(session, **case_data)
    assert case.id is not None
    
    retrieved_case = get_case(session, '7A/123')
    assert retrieved_case is not None
    assert retrieved_case.case_id == '7A/123'
    assert retrieved_case.order_date == '2023-05-12'

def test_get_nonexistent_case(session):
    """Test retrieving a case that doesn't exist."""
    try:
        from src.database import get_case
    except ImportError:
        pytest.fail("src.database module or functions not found")
        
    retrieved_case = get_case(session, '99Z/999')
    assert retrieved_case is None
