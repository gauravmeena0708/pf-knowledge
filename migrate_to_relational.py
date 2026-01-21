"""
Migration Script: Convert from JSON schema to Relational schema
Reads existing elis.db and creates elis_relational.db with new schema
"""

import sqlite3
import json
from src.database_v2 import (
    init_db as init_db_v2, get_session as get_session_v2,
    add_case, add_entity, add_timeline_event, add_relation, add_financial_record
)
import os

def parse_amount(amount_str):
    """Parse amount string to float."""
    if isinstance(amount_str, (int, float)):
        return float(amount_str)
    if isinstance(amount_str, str):
        try:
            cleaned = amount_str.replace(',', '').replace('/-', '').strip()
            return float(cleaned)
        except ValueError:
            return None
    return None

def migrate_database():
    """Main migration function."""
    print("="*60)
    print("ELIS Database Migration: JSON -> Relational")
    print("="*60)
    
    if not os.path.exists('elis.db'):
        print("❌ elis.db not found. Run pipeline first.")
        return
    
    #  Read from old schema using raw SQL
    conn_old = sqlite3.connect('elis.db')
    conn_old.row_factory = sqlite3.Row
    cursor = conn_old.cursor()
    
    # Get all cases
    cursor.execute("SELECT * FROM cases")
    cases_old = cursor.fetchall()
    
    print(f"\n📊 Found {len(cases_old)} cases to migrate\n")
    
    # Create new database
    if os.path.exists('elis_relational.db'):
        os.remove('elis_relational.db')
    
    engine_v2 = init_db_v2('sqlite:///elis_relational.db')
    session_v2 = get_session_v2(engine_v2)
    
    stats = {
        'cases': 0,
        'entities': 0,
        'timeline_events': 0,
        'relations': 0,
        'financial_records': 0
    }
    
    for case_old in cases_old:
        case_id = case_old['case_id']
        print(f"Migrating: {case_id}")
        
        # Parse JSON fields
        entities_json = json.loads(case_old['entities']) if case_old['entities'] else {}
        enriched_data = entities_json.get('_enriched', {})
        
        # Create case in v2
        case_v2 = add_case(
            session=session_v2,
            case_id=case_id,
            pdf_path=case_old['pdf_path'],
            case_type=enriched_data.get('case_type', 'unknown'),
            outcome=enriched_data.get('outcome', 'unknown'),
            confidence=enriched_data.get('confidence', 0.0),
            order_date=case_old['order_date'],
            text_content=case_old['text_content'],
            tables=json.loads(case_old['tables']) if case_old['tables'] else None
        )
        stats['cases'] += 1
        
        # Migrate entities
        entity_count = 0
        for entity_type, entities in entities_json.items():
            if entity_type == '_enriched':
                continue
            if isinstance(entities, list):
                for entity_text in entities:
                    if entity_text:
                        add_entity(session_v2, case_v2.id, entity_type, entity_text)
                        entity_count += 1
        
        stats['entities'] += entity_count
        print(f"  ✓ Entities: {entity_count}")
        
        # Migrate timeline
        timeline_count = 0
        if 'timeline' in enriched_data and isinstance(enriched_data['timeline'], list):
            for event in enriched_data['timeline']:
                if isinstance(event, dict):
                    add_timeline_event(session_v2, case_v2.id, event)
                    timeline_count += 1
        
        stats['timeline_events'] += timeline_count
        print(f"  ✓ Timeline: {timeline_count} events")
        
        # Migrate relations
        relation_count = 0
        if 'relations' in enriched_data and isinstance(enriched_data['relations'], list):
            for relation in enriched_data['relations']:
                if isinstance(relation, dict):
                    add_relation(session_v2, case_v2.id, relation)
                    relation_count += 1
        
        if 'compliance_gaps' in enriched_data and isinstance(enriched_data['compliance_gaps'], list):
            for gap in enriched_data['compliance_gaps']:
                gap_relation = {
                    'type': 'compliance_gap',
                    'subject': gap.get('entity'),
                    'relation': 'non_compliance',
                    'object': gap.get('requirement'),
                    'context': gap.get('context', '')
                }
                add_relation(session_v2, case_v2.id, gap_relation)
                relation_count += 1
        
        stats['relations'] += relation_count
        print(f"  ✓ Relations: {relation_count}")
        
        # Migrate financial
        financial_count = 0
        if 'financial_data' in enriched_data and isinstance(enriched_data['financial_data'], dict):
            for account_type, amount in enriched_data['financial_data'].items():
                parsed_amount = parse_amount(amount)
                if parsed_amount is not None:
                    add_financial_record(session_v2, case_v2.id, account_type, parsed_amount)
                    financial_count += 1
        
        stats['financial_records'] += financial_count
        print(f"  ✓ Financial: {financial_count} records")
        print()
        
        session_v2.commit()
    
    # Close connections
    conn_old.close()
    session_v2.close()
    
    # Print summary
    print("="*60)
    print("Migration Complete!")
    print("="*60)
    print(f"Cases migrated: {stats['cases']}")
    print(f"Total entities: {stats['entities']}")
    print(f"Total timeline events: {stats['timeline_events']}")
    print(f"Total relations: {stats['relations']}")
    print(f"Total financial records: {stats['financial_records']}")
    print(f"\n✅ New database: elis_relational.db")
    print(f"✅ Old database: elis.db (unchanged)")
    print("\nTo switch to new schema:")
    print("  1. Test: inspect_db.py with elis_relational.db")
    print("  2. Rename: mv elis.db elis_old.db && mv elis_relational.db elis.db")
    print("  3. Update imports: database.py -> database_v2.py")
    print("="*60)

if __name__ == "__main__":
    migrate_database()
