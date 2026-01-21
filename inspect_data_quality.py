"""
Data Quality Inspection Script
Analyzes elis.db for quality issues, normalization needs, and extraction gaps.
"""

from src.database_v2 import init_db, get_session, Case, Entity, TimelineEvent, Relation, FinancialRecord
from sqlalchemy import func, text
import pandas as pd
from collections import Counter

def analyze_data_quality():
    print("="*60)
    print("🔍 ELIS Database Quality Inspection")
    print("="*60)
    
    engine = init_db('sqlite:///elis.db')
    session = get_session(engine)
    
    # 1. Overview
    case_count = session.query(func.count(Case.id)).scalar()
    entity_count = session.query(func.count(Entity.id)).scalar()
    event_count = session.query(func.count(TimelineEvent.id)).scalar()
    
    print(f"\n📊 Overview:")
    print(f"  Cases: {case_count}")
    print(f"  Entities: {entity_count} ({entity_count/case_count:.1f} per case)")
    print(f"  Timeline Events: {event_count} ({event_count/case_count:.1f} per case)")
    
    # 2. Entity Quality
    print(f"\n👥 Entity Analysis:")
    
    # Check for "garbage" entities (too short, special chars)
    short_entities = session.query(Entity.entity_text).filter(func.length(Entity.entity_text) < 3).all()
    print(f"  • Very short entities (<3 chars): {len(short_entities)}")
    if short_entities:
        print(f"    Examples: {[e[0] for e in short_entities[:5]]}")

    # Check for duplicate entities (case-insensitive) within same case
    duplicates = session.query(
        Entity.case_id, Entity.entity_type, func.lower(Entity.entity_text), func.count(Entity.id)
    ).group_by(
        Entity.case_id, Entity.entity_type, func.lower(Entity.entity_text)
    ).having(func.count(Entity.id) > 1).all()
    
    print(f"  • Duplicate entities within cases: {len(duplicates)}")
    
    # Entity Type distribution
    type_dist = session.query(Entity.entity_type, func.count(Entity.id)).group_by(Entity.entity_type).all()
    print(f"  • Distribution: {dict(type_dist)}")

    # 3. Timeline Quality
    print(f"\n📅 Timeline Analysis:")
    # Check for invalid dates
    invalid_dates = session.query(TimelineEvent).filter(
        TimelineEvent.event_date.notlike('20%') # Simple check for 20xx
    ).all()
    print(f"  • Potentially invalid dates (not starting with '20'): {len(invalid_dates)}")
    for evt in invalid_dates[:3]:
        print(f"    - {evt.event_date}: {evt.discussion[:50]}...")

    # 4. Text Content Quality
    print(f"\n📝 Text Content Analysis:")
    cases_with_text = session.query(Case).all()
    for case in cases_with_text:
        raw_len = len(case.text_content) if case.text_content else 0
        clean_len = len(case.processed_content) if case.processed_content else 0
        ratio = clean_len / raw_len if raw_len > 0 else 0
        print(f"  Case {case.case_id[:20]}... : Raw {raw_len} -> Clean {clean_len} ({ratio:.2%} retained)")
        
        # Check for remaining garbage in processed content
        if case.processed_content:
            garbage_markers = ['##', '..', '__', '  ']
            found_markers = [m for m in garbage_markers if m in case.processed_content]
            if found_markers:
                print(f"    ⚠️  Contains artifacts: {found_markers}")

    session.close()

if __name__ == "__main__":
    analyze_data_quality()
