from sqlalchemy import create_engine, Column, Integer, String, Date, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.engine import Engine
from typing import Optional

Base = declarative_base()

class Case(Base):
    """
    SQLAlchemy model for legal cases.
    """
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, nullable=False, index=True) # e.g., "7A/123"
    order_date = Column(String, nullable=True) # Storing as ISO YYYY-MM-DD string for simplicity
    pdf_path = Column(String, nullable=False)
    text_content = Column(Text, nullable=True)

def init_db(db_url: str = 'sqlite:///elis.db') -> Engine:
    """
    Initializes the database engine and creates tables.
    """
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine: Engine) -> Session:
    """
    Creates a new session.
    """
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def add_case(session: Session, case_id: str, pdf_path: str, order_date: Optional[str] = None, text_content: Optional[str] = None) -> Case:
    """
    Adds a new case to the database.
    """
    new_case = Case(
        case_id=case_id,
        pdf_path=pdf_path,
        order_date=order_date,
        text_content=text_content
    )
    session.add(new_case)
    session.commit()
    session.refresh(new_case)
    return new_case

def get_case(session: Session, case_id: str) -> Optional[Case]:
    """
    Retrieves a case by its Case ID.
    """
    return session.query(Case).filter(Case.case_id == case_id).first()
