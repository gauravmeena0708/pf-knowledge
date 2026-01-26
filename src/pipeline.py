from sqlalchemy.orm import Session
from src.loader import load_pdf
from src.ocr_engine import extract_text
from src.parser import extract_metadata
from src.database import add_case, Case
from src.nlp.cleaner import clean_text
from src.nlp.ner_engine import LegalEntityExtractor
from src.nlp.entity_extractor import GLiNEREntityExtractor
from src.nlp.case_classifier import CaseClassifier
from src.nlp.timeline_extractor import TimelineExtractor
from src.nlp.relation_extractor import RelationExtractor
from src.nlp.financial_parser import FinancialParser
from src.nlp.advanced_cleaner import create_processed_content
from src.table_extractor import extract_tables
import pandas as pd

# Global instances for lazy loading
_ner_engine = None
_gliner_extractor = None
_case_classifier = None
_timeline_extractor = None
_relation_extractor = None
_financial_parser = None

def get_ner_engine():
    global _ner_engine
    if _ner_engine is None:
        _ner_engine = LegalEntityExtractor()
    return _ner_engine

def get_gliner_extractor():
    global _gliner_extractor
    if _gliner_extractor is None:
        _gliner_extractor = GLiNEREntityExtractor()
    return _gliner_extractor

def get_case_classifier():
    global _case_classifier
    if _case_classifier is None:
        _case_classifier = CaseClassifier()
    return _case_classifier

def get_timeline_extractor():
    global _timeline_extractor
    if _timeline_extractor is None:
        _timeline_extractor = TimelineExtractor()
    return _timeline_extractor

def get_relation_extractor():
    global _relation_extractor
    if _relation_extractor is None:
        _relation_extractor = RelationExtractor()
    return _relation_extractor

def get_financial_parser():
    global _financial_parser
    if _financial_parser is None:
        _financial_parser = FinancialParser()
    return _financial_parser

def merge_entities(bert_entities: dict, gliner_entities: dict) -> dict:
    """Merge BERT and GLiNER entity extractions."""
    merged = {}
    
    # Start with BERT entities
    for entity_type, entities in bert_entities.items():
        merged[entity_type] = entities
    
    # Add GLiNER entities (domain-specific)
    for entity_type, entities in gliner_entities.items():
        if entity_type in merged:
            # Merge and deduplicate
            merged[entity_type] = list(set(merged[entity_type] + entities))
        else:
            merged[entity_type] = entities
    
    return merged

def process_case_file(pdf_path: str, session: Session) -> Case:
    """
    Processes a legal case PDF file with ENHANCED PIPELINE:
    
    1. Loads PDF as images
    2. Performs OCR with preprocessing
    3. Cleans the extracted text
    4. Extracts metadata (Date, Case ID)
    5. Classifies case type (7A/14B) and outcome
    6. Extracts timeline (hearing events)
    7. Extracts relations (officer directives, failures, consequences)
    8. Extracts entities (BERT + GLiNER)
    9. Extracts financial details from tables/text
    10. Saves enriched case to database
    
    Args:
        pdf_path (str): Path to the PDF file.
        session (Session): Database session.
        
    Returns:
        Case: The created Case object.
    """
    print(f"[Pipeline] Processing: {pdf_path}")
    
    # 1. Load PDF
    images = load_pdf(pdf_path)
    print(f"[Pipeline] Loaded {len(images)} pages")
    
    # 2. OCR with preprocessing
    full_text_list = []
    for i, image in enumerate(images):
        page_text = extract_text(image, preprocess=True)
        full_text_list.append(page_text)
        print(f"[Pipeline] OCR page {i+1}/{len(images)}")
    
    raw_text = "\n".join(full_text_list)
    
    # 3. Clean Text
    cleaned_text = clean_text(raw_text)
    print(f"[Pipeline] Text cleaned ({len(cleaned_text)} chars)")
    
    # 4. Extract Metadata
    metadata = extract_metadata(cleaned_text)
    print(f"[Pipeline] Metadata: Case ID={metadata.get('id')}, Date={metadata.get('date')}")
    
    # 5. Classify Case Type (7A/14B) and Outcome
    classification = get_case_classifier().classify(cleaned_text)
    print(f"[Pipeline] Classification: Type={classification['case_type']}, Outcome={classification['outcome']}")
    
    # 6. Extract Timeline
    timeline = get_timeline_extractor().extract(cleaned_text)
    print(f"[Pipeline] Timeline: {len(timeline)} hearings extracted")
    
    # 7. Extract Relations
    relations = get_relation_extractor().extract(cleaned_text)
    compliance_gaps = get_relation_extractor().extract_compliance_gaps(cleaned_text)
    print(f"[Pipeline] Relations: {len(relations)} extracted")
    
    # 8. Extract Entities (BERT + GLiNER)
    bert_entities = get_ner_engine().extract_entities(cleaned_text)
    try:
        gliner_entities = get_gliner_extractor().extract(cleaned_text)
    except Exception as e:
        print(f"[Pipeline] GLiNER extraction failed: {e}, using BERT only")
        gliner_entities = {}
    
    entities = merge_entities(bert_entities, gliner_entities)
    print(f"[Pipeline] Entities: {sum(len(v) for v in entities.values())} total")
    
    # 9. Extract Financial Details
    financial_data = {}
    
    # From tables (if present)
    try:
        raw_tables = extract_tables(pdf_path)
        tables = []
        for df in raw_tables:
            if isinstance(df, pd.DataFrame):
                # Try to parse as financial schedule
                parsed = get_financial_parser().parse_schedule(df)
                if parsed:
                    financial_data.update(parsed)
                tables.append(df.to_dict(orient='records'))
        print(f"[Pipeline] Tables: {len(tables)} extracted, Financial: {bool(financial_data)}")
    except Exception as e:
        print(f"[Pipeline] Table extraction failed: {e}")
        tables = []
    
    # From text (fallback)
    if not financial_data:
        financial_data = get_financial_parser().extract_from_text(cleaned_text)
        print(f"[Pipeline] Financial (from text): {bool(financial_data)}")
    
    # Use defaults if metadata not found
    case_id = metadata.get('id') or 'UNKNOWN'
    order_date = metadata.get('date')
    
    # 10. Create processed content (human-readable)
    processed_text = create_processed_content(cleaned_text)
    print(f"[Pipeline] Processed content: {len(processed_text)} chars (vs {len(cleaned_text)} raw)")

    enriched_data = {
        'case_type': classification['case_type'],
        'outcome': classification['outcome'],
        'confidence': classification['confidence'],
        'timeline': timeline,
        'relations': relations,
        'compliance_gaps': compliance_gaps,
        'financial_data': financial_data
    }

    # 11. Save to DB with enriched data
    # Create merged entities dictionary which includes enriched data
    entities['_enriched'] = enriched_data
    
    # Extract specific fields for the new columns
    judge_name = None
    if 'Judge' in entities and entities['Judge']:
        judge_name = entities['Judge'][0]
        
    establishment_name = None
    if 'Establishment' in entities and entities['Establishment']:
        establishment_name = entities['Establishment'][0]
        
    section_cited = classification.get('case_type')
    if (not section_cited or section_cited == 'unknown') and 'Section' in entities and entities['Section']:
        section_cited = entities['Section'][0]
        
    total_dues = None
    # Try to get from financial data first
    if financial_data and 'total_dues' in financial_data:
        try:
            total_dues = float(financial_data['total_dues'])
        except:
             pass
    # Fallback to GLiNER extracted Amount if available (heuristic: max amount?)
    if total_dues is None and 'Amount' in entities and entities['Amount']:
        try:
             # Heuristic: take the largest amount extracted
             amounts = entities['Amount']
             # entities['Amount'] might be strings or floats (GLiNER returns numbers now based on my read of EntityExtractor)
             # EntityExtractor._clean_amount returns floats.
             # But merge_entities might have mixed types if BERT returns strings.
             # Let's handle safely.
             valid_amounts = []
             for a in amounts:
                 if isinstance(a, (int, float)):
                     valid_amounts.append(a)
                 else:
                     # try parsing
                     try:
                         valid_amounts.append(float(a))
                     except:
                         pass
             if valid_amounts:
                 total_dues = max(valid_amounts)
        except:
            pass

    # Save using the refactored database module
    new_case = add_case(
        session=session,
        case_id=case_id,
        pdf_path=pdf_path,
        order_date=order_date,
        text_content=cleaned_text,
        entities=entities,
        tables=tables,
        judge_name=judge_name,
        establishment_name=establishment_name,
        section_cited=section_cited,
        total_dues=total_dues,
        timeline=timeline
    )
    
    print(f"[Pipeline] ✅ Saved case: {case_id} (Judge: {judge_name}, Section: {section_cited})\n")
    return new_case
