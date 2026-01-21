"""
ELIS Knowledge Base Module
Provides intelligent Q&A over legal case documents using RAG.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

class LegalKnowledgeBase:
    """
    High-level knowledge base for EPF legal cases.
    Uses ChromaDB for vector storage and retrieval.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize knowledge base with persistent storage."""
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="legal_cases",
            metadata={"description": "EPF legal case documents"}
        )
        
        # Track indexed cases
        self.indexed_cases = set()
    
    def add_case(self, case) -> None:
        """
        Add a case to the knowledge base.
        
        Args:
            case: Case object from database with text_content, entities, etc.
        """
        case_id = case.case_id or f"case_{case.id}"
        
        # Skip if already indexed
        if case_id in self.indexed_cases:
            return
        
        # Create document chunks
        chunks = self._create_chunks(case)
        
        if not chunks:
            print(f"Warning: No chunks created for {case_id}")
            return
        
        # Prepare data for ChromaDB
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        ids = [chunk['id'] for chunk in chunks]
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        self.indexed_cases.add(case_id)
        print(f"Indexed case: {case_id} ({len(chunks)} chunks)")
    
    def _create_chunks(self, case) -> List[Dict]:
        """
        Create semantic chunks from a case.
        
        Strategy:
        - Chunk 1: Metadata + summary (first 500 chars)
        - Chunk 2-N: Text in 1000-char chunks with overlap
        """
        chunks = []
        case_id = case.case_id or f"case_{case.id}"
        text = case.text_content or ""
        
        if not text.strip():
            return chunks
        
        # Chunk 1: Metadata
        metadata_chunk = {
            'id': f"{case_id}_metadata",
            'text': self._create_metadata_text(case),
            'metadata': {
                'case_id': case_id,
                'chunk_type': 'metadata',
                'order_date': str(case.order_date) if case.order_date else 'unknown',
                'chunk_index': 0
            }
        }
        chunks.append(metadata_chunk)
        
        # Chunk 2-N: Text content in overlapping windows
        chunk_size = 1000
        overlap = 200
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk_text = text[i:i + chunk_size]
            
            if len(chunk_text.strip()) < 100:
                continue
            
            chunk_id = len(chunks)
            chunks.append({
                'id': f"{case_id}_chunk_{chunk_id}",
                'text': chunk_text,
                'metadata': {
                    'case_id': case_id,
                    'chunk_type': 'content',
                    'order_date': str(case.order_date) if case.order_date else 'unknown',
                    'chunk_index': chunk_id,
                    'has_entities': 'PER' in (case.entities or {}),
                }
            })
        
        return chunks
    
    def _create_metadata_text(self, case) -> str:
        """Create a searchable metadata summary."""
        parts = [f"Case ID: {case.case_id or 'Unknown'}"]
        
        if case.order_date:
            parts.append(f"Order Date: {case.order_date}")
        
        # Add entities
        if case.entities:
            for entity_type, entities in case.entities.items():
                if entities:
                    parts.append(f"{entity_type}: {', '.join(entities[:5])}")
        
        # Add summary (first 500 chars)
        if case.text_content:
            summary = case.text_content[:500].strip()
            parts.append(f"Summary: {summary}")
        
        return "\n".join(parts)
    
    def query(self, question: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Query the knowledge base with natural language.
        
        Args:
            question: Natural language question
            n_results: Number of relevant chunks to retrieve
            
        Returns:
            Dict with results and metadata
        """
        if self.collection.count() == 0:
            return {
                'answer': 'Knowledge base is empty. Please index some cases first.',
                'sources': [],
                'chunks': []
            }
        
        # Retrieve relevant chunks
        results = self.collection.query(
            query_texts=[question],
            n_results=min(n_results, self.collection.count())
        )
        
        # Format results
        chunks = []
        for i in range(len(results['documents'][0])):
            chunks.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        # Generate simple answer from top chunk
        answer = self._generate_answer(question, chunks)
        
        return {
            'answer': answer,
            'sources': list(set([c['metadata']['case_id'] for c in chunks])),
            'chunks': chunks
        }
    
    def _generate_answer(self, question: str, chunks: List[Dict]) -> str:
        """
        Generate answer from retrieved chunks.
        
        For MVP: Simple extraction from most relevant chunk.
        Future: Integrate LLM (GPT-4, Claude, etc.)
        """
        if not chunks:
            return "No relevant information found."
        
        # Use most relevant chunk
        top_chunk = chunks[0]
        case_id = top_chunk['metadata']['case_id']
        
        return f"""Based on case {case_id}:

{top_chunk['text'][:500]}...

(Showing most relevant excerpt. For detailed analysis, consider integrating an LLM.)
"""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        return {
            'total_chunks': self.collection.count(),
            'indexed_cases': len(self.indexed_cases),
            'collection_name': self.collection.name
        }
    
    def find_similar_cases(self, case_id: str, n_results: int = 5) -> List[Dict]:
        """
        Find cases similar to a given case.
        
        Args:
            case_id: Case ID to find similar cases for
            n_results: Number of similar cases to return
        """
        # Get chunks for this case
        case_chunks = self.collection.get(
            where={"case_id": case_id}
        )
        
        if not case_chunks['documents']:
            return []
        
        # Use first chunk as query
        query_text = case_chunks['documents'][0]
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results + 1  # +1 because it includes itself
        )
        
        similar = []
        seen_cases = set()
        for i in range(len(results['documents'][0])):
            c_id = results['metadatas'][0][i]['case_id']
            # Skip the query case itself
            if c_id != case_id and c_id not in seen_cases:
                similar.append({
                    'case_id': c_id,
                    'relevance': 1 - (results['distances'][0][i] / 2),  # Convert distance to similarity
                    'snippet': results['documents'][0][i][:200]
                })
                seen_cases.add(c_id)
        
        return similar[:n_results]


def build_knowledge_base_from_db(db_session) -> LegalKnowledgeBase:
    """
    Build knowledge base from existing database.
    
    Args:
        db_session: SQLAlchemy session
        
    Returns:
        Initialized knowledge base
    """
    from src.database import Case
    
    kb = LegalKnowledgeBase()
    
    cases = db_session.query(Case).all()
    print(f"Building knowledge base from {len(cases)} cases...")
    
    for case in cases:
        kb.add_case(case)
    
    stats = kb.get_stats()
    print(f"Knowledge base built: {stats['total_chunks']} chunks from {stats['indexed_cases']} cases")
    
    return kb
