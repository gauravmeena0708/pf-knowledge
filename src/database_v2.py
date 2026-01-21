from sqlalchemy import create_engine, Column, Integer, String, Date, Text, JSON, Float, ForeignKey, Index
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.engine import Engine
from typing import Optional, List
from datetime import date as date_type

Base = declarative_base()

class Case(Base):
    """Main case table."""
    __tablename__ = 'cases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, nullable=False, unique=True, index=True)
    case_type = Column(String, index=True)  # '7A', '14B', or 'unknown'
    outcome = Column(String, index=True)  # 'compliant', 'non_compliant', 'unknown'
    confidence = Column(Float)  # Classification confidence
    order_date = Column(String, nullable=True, index=True)  # ISO YYYY-MM-DD
    pdf_path = Column(String, nullable=False)
    text_content = Column(Text, nullable=True)
    
    # Relationships
    entities = relationship("Entity", back_populates="case", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="case", cascade="all, delete-orphan")
    relations = relationship("Relation", back_populates="case", cascade="all, delete-orphan")
    financial_records = relationship("FinancialRecord", back_populates="case", cascade="all, delete-orphan")
    
    # Legacy: Keep tables column for backward compatibility (can be removed later)
    tables = Column(JSON, nullable=True)

class Entity(Base):
    """Extracted entities (Person, Organization, Judge, Amount, etc.)"""
    __tablename__ = 'entities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('cases.id', ondelete='CASCADE'), nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)  # PER, ORG, LOC, JUDGE, AMOUNT, etc.
    entity_text = Column(String, nullable=False, index=True)
    confidence = Column(Float)  # Optional confidence score
    
    case = relationship("Case", back_populates="entities")
    
    __table_args__ = (
        Index('idx_entity_type_text', 'entity_type', 'entity_text'),
    )

class TimelineEvent(Base):
    """Hearing timeline events."""
    __tablename__ = 'timeline_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('cases.id', ondelete='CASCADE'), nullable=False, index=True)
    event_date = Column(String, index=True)  # ISO date
    appeared = Column(JSON)  # List of who appeared
    discussion = Column(Text)
    outcome = Column(Text)
    next_date = Column(String)  # ISO date for next hearing
    
    case = relationship("Case", back_populates="timeline_events")
    
    __table_args__ = (
        Index('idx_timeline_date', 'event_date'),
    )

class Relation(Base):
    """Extracted cause-effect relations and officer directives."""
    __tablename__ = 'relations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('cases.id', ondelete='CASCADE'), nullable=False, index=True)
    relation_type = Column(String, nullable=False, index=True)  # officer_directive, failure_to_submit, etc.
    subject = Column(String)  # Who/what is the subject
    relation_verb = Column(String)  # The action/relation
    object = Column(String)  # Target of the relation
    context = Column(Text)  # Full sentence/context
    
    case = relationship("Case", back_populates="relations")
    
    __table_args__ = (
        Index('idx_relation_type', 'relation_type'),
    )

class FinancialRecord(Base):
    """Financial details and dues."""
    __tablename__ = 'financial_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('cases.id', ondelete='CASCADE'), nullable=False, index=True)
    account_type = Column(String, index=True)  # ee_share_ac1, er_share_ac1, total_dues, etc.
    amount = Column(Float, index=True)
    period_from = Column(String)  # Optional period information
    period_to = Column(String)
    
    case = relationship("Case", back_populates="financial_records")
    
    __table_args__ = (
        Index('idx_financial_amount', 'amount'),
        Index('idx_account_type_amount', 'account_type', 'amount'),
    )

def init_db(db_url: str = 'sqlite:///elis.db') -> Engine:
    """Initialize the database engine and create tables."""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine: Engine) -> Session:
    """Create a new session."""
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def add_case(
    session: Session,
    case_id: str,
    pdf_path: str,
    case_type: str = 'unknown',
    outcome: str = 'unknown',
    confidence: float = 0.0,
    order_date: Optional[str] = None,
    text_content: Optional[str] = None,
    tables: Optional[list] = None
) -> Case:
    """Add a new case to the database."""
    new_case = Case(
        case_id=case_id,
        case_type=case_type,
        outcome=outcome,
        confidence=confidence,
        pdf_path=pdf_path,
        order_date=order_date,
        text_content=text_content,
        tables=tables
    )
    session.add(new_case)
    session.commit()
    session.refresh(new_case)
    return new_case

def add_entity(session: Session, case_id: int, entity_type: str, entity_text: str, confidence: float = None):
    """Add an entity to a case."""
    entity = Entity(
        case_id=case_id,
        entity_type=entity_type,
        entity_text=entity_text,
        confidence=confidence
    )
    session.add(entity)

def add_timeline_event(session: Session, case_id: int, event_data: dict):
    """Add a timeline event to a case."""
    event = TimelineEvent(
        case_id=case_id,
        event_date=event_data.get('date'),
        appeared=event_data.get('appeared'),
        discussion=event_data.get('discussion'),
        outcome=event_data.get('outcome'),
        next_date=event_data.get('next_date')
    )
    session.add(event)

def add_relation(session: Session, case_id: int, relation_data: dict):
    """Add a relation to a case."""
    relation = Relation(
        case_id=case_id,
        relation_type=relation_data.get('type', 'unknown'),
        subject=relation_data.get('subject'),
        relation_verb=relation_data.get('relation'),
        object=relation_data.get('object'),
        context=relation_data.get('context')
    )
    session.add(relation)

def add_financial_record(session: Session, case_id: int, account_type: str, amount: float):
    """Add a financial record to a case."""
    record = FinancialRecord(
        case_id=case_id,
        account_type=account_type,
        amount=amount
    )
    session.add(record)

def get_case(session: Session, case_id: str) -> Optional[Case]:
    """Retrieve a case by its Case ID."""
    return session.query(Case).filter(Case.case_id == case_id).first()

def get_cases_by_entity(session: Session, entity_type: str, entity_text: str) -> List[Case]:
    """Find all cases involving a specific entity."""
    return session.query(Case).join(Entity).filter(
        Entity.entity_type == entity_type,
        Entity.entity_text.contains(entity_text)
    ).all()

def get_cases_by_financial_threshold(session: Session, min_amount: float) -> List[Case]:
    """Find cases with financial amounts above a threshold."""
    return session.query(Case).join(FinancialRecord).filter(
        FinancialRecord.amount >= min_amount
    ).distinct().all()

def get_cases_by_date_range(session: Session, start_date: str, end_date: str) -> List[Case]:
    """Find cases within a date range."""
    return session.query(Case).filter(
        Case.order_date >= start_date,
        Case.order_date <= end_date
    ).all()
