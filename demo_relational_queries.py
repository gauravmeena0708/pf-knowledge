"""
Demo: Powerful Queries with Relational Schema
Shows what's now possible that wasn't before
"""

from src.database_v2 import (
    init_db, get_session, Case, Entity, TimelineEvent, Relation, FinancialRecord,
    get_cases_by_entity, get_cases_by_financial_threshold
)
from sqlalchemy import func

def demo_queries():
    print("="*70)
    print("ELIS Relational Schema - Query Demonstrations")
    print("="*70)
    
    engine = init_db('sqlite:///elis.db')
    session = get_session(engine)
    
    # Query 1: Find all cases with more than 10 timeline events
    print("\n📅 Query 1: Cases with more than 10 hearings")
    print("-"*70)
    cases_many_hearings = session.query(Case).join(TimelineEvent).group_by(Case.id).having(
        func.count(TimelineEvent.id) > 10
    ).all()
    
    for case in cases_many_hearings:
        hearing_count = session.query(func.count(TimelineEvent.id)).filter(
            TimelineEvent.case_id == case.id
        ).scalar()
        print(f"  • {case.case_id}: {hearing_count} hearings")
    
    if not cases_many_hearings:
        print("  (No cases with >10 hearings)")
    
    # Query 2: All entities of type ORG
    print("\n🏢 Query 2: All Organizations mentioned")
    print("-"*70)
    orgs = session.query(Entity.entity_text).filter(
        Entity.entity_type == 'ORG'
    ).distinct().limit(10).all()
    
    for org in orgs:
        print(f"  • {org[0]}")
    
    # Query 3: Cases by case type
    print("\n⚖️  Query 3: Cases by Type")
    print("-"*70)
    case_type_stats = session.query(
        Case.case_type, func.count(Case.id)
    ).group_by(Case.case_type).all()
    
    for case_type, count in case_type_stats:
        print(f"  • {case_type}: {count} cases")
    
    # Query 4: Cases with non-compliant outcome
    print("\n🔴 Query 4: Non-Compliant Cases")
    print("-"*70)
    non_compliant = session.query(Case).filter(
        Case.outcome == 'non_compliant'
    ).all()
    
    for case in non_compliant:
        print(f"  • {case.case_id} (Date: {case.order_date or 'N/A'})")
    
    if not non_compliant:
        print("  (No non-compliant cases)")
    
    # Query 5: All relation types
    print("\n🔗 Query 5: Relation Types Found")
    print("-"*70)
    relation_types = session.query(
        Relation.relation_type, func.count(Relation.id)
    ).group_by(Relation.relation_type).all()
    
    for rel_type, count in relation_types:
        print(f"  • {rel_type}: {count} instances")
    
    # Query 6: Timeline events in chronological order for one case
    print("\n📆 Query 6: Timeline for Longest Case")
    print("-"*70)
    longest_case = session.query(Case).join(TimelineEvent).group_by(Case.id).order_by(
        func.count(TimelineEvent.id).desc()
    ).first()
    
    if longest_case:
        print(f"Case: {longest_case.case_id}")
        timeline = session.query(TimelineEvent).filter(
            TimelineEvent.case_id == longest_case.id
        ).order_by(TimelineEvent.event_date).limit(5).all()
        
        for i, event in enumerate(timeline, 1):
            print(f"  {i}. {event.event_date}: {event.discussion[:60]}...")
    
    # Query 7: Financial records
    print("\n💰 Query 7: Cases with Financial Records")
    print("-"*70)
    financial_cases = session.query(Case).join(FinancialRecord).distinct().all()
    
    for case in financial_cases:
        records = session.query(FinancialRecord).filter(
            FinancialRecord.case_id == case.id
        ).all()
        
        print(f"  • {case.case_id}:")
        for record in records:
            print(f"      {record.account_type}: ₹{record.amount:,.2f}")
    
    if not financial_cases:
        print("  (No cases with financial records)")
    
    # Query 8: Entity co-occurrence
    print("\n👥 Query 8: Cases Involving Multiple Entity Types")
    print("-"*70)
    cases_with_entities = session.query(Case).join(Entity).group_by(Case.id).having(
        func.count(func.distinct(Entity.entity_type)) > 3
    ).all()
    
    for case in cases_with_entities:
        entity_types = session.query(func.distinct(Entity.entity_type)).filter(
            Entity.case_id == case.id
        ).all()
        print(f"  • {case.case_id}: {len(entity_types)} entity types")
    
    # Summary
    print("\n" + "="*70)
    print("Overall Statistics")
    print("="*70)
    print(f"Total Cases: {session.query(func.count(Case.id)).scalar()}")
    print(f"Total Entities: {session.query(func.count(Entity.id)).scalar()}")
    print(f"Total Timeline Events: {session.query(func.count(TimelineEvent.id)).scalar()}")
    print(f"Total Relations: {session.query(func.count(Relation.id)).scalar()}")
    print(f"Total Financial Records: {session.query(func.count(FinancialRecord.id)).scalar()}")
    
    # Complex query: Average hearings per case
    avg_hearings = session.query(
        func.avg(func.count(TimelineEvent.id))
    ).select_from(Case).outerjoin(TimelineEvent).group_by(Case.id).scalar()
    
    print(f"\nAverage Hearings per Case: {avg_hearings:.1f}" if avg_hearings else "\nNo timeline data")
    
    print("="*70)
    
    session.close()

if __name__ == "__main__":
    demo_queries()
