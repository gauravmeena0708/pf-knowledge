from typing import List, Optional
from sqlalchemy.orm import Session
from src.database import Case
from src.knowledge_base import LegalKnowledgeBase

class PrecedentRetriever:
    def __init__(self, db_session: Session, vectors_db: LegalKnowledgeBase = None):
        self.session = db_session
        self.vectors = vectors_db or LegalKnowledgeBase()
        
    def get_precedents(self, query: str, section: Optional[str] = None, judge: Optional[str] = None, k: int = 3) -> List[Case]:
        """
        Retrieve precedent cases based on semantic query and metadata filters.
        
        Strategy:
        1. Fetch candidates from Vector DB (fetch more than k).
        2. Filter candidates using SQL DB for strict metadata matching.
        3. Return top k complying cases.
        """
        # 1. Broad semantic search (fetch 5x requested to allow for filtering)
        # Note: 'sources' in kb.query returns unique case_ids
        search_results = self.vectors.query(query, n_results=k * 5)
        
        candidates = search_results.get('chunks', [])
        if not candidates:
            return []
            
        candidate_case_ids = list(set([c['metadata']['case_id'] for c in candidates]))
        
        # 2. Filter via SQL
        # We want to keep the order of relevance, so we fetch valid IDs and then filter the list
        
        sql_query = self.session.query(Case).filter(Case.case_id.in_(candidate_case_ids))
        
        if section:
            sql_query = sql_query.filter(Case.section_cited == section)
            
        if judge:
            sql_query = sql_query.filter(Case.judge_name == judge)
            
        valid_cases_map = {c.case_id: c for c in sql_query.all()}
        
        # 3. Reconstruct result list preserving semantic order
        final_results = []
        seen_ids = set()
        
        for chunk in candidates:
            c_id = chunk['metadata']['case_id']
            if c_id in valid_cases_map and c_id not in seen_ids:
                case_obj = valid_cases_map[c_id]
                # Attach the snippet used for matching (optional, for debugging/display)
                # attributes can be set dynamically
                case_obj.relevance_snippet = chunk['text']
                final_results.append(case_obj)
                seen_ids.add(c_id)
                
            if len(final_results) >= k:
                break
                
        return final_results
