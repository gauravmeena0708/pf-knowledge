from typing import List, Dict, Any, Optional
import numpy as np

class SemanticSearch:
    """
    Semantic search engine using sentence-transformers and FAISS.
    Enables similarity search across case documents.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self._model = None
        self._index = None
        self._documents = []
        self._dimension = None
    
    @property
    def model(self):
        """Lazy load sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError("sentence-transformers required. Install with: pip install sentence-transformers")
        return self._model

    def _get_faiss(self):
        """Get FAISS module."""
        try:
            import faiss
            return faiss
        except ImportError:
            raise ImportError("faiss-cpu required. Install with: pip install faiss-cpu")

    def index(self, documents: List[Dict[str, Any]]) -> None:
        """
        Index documents for semantic search.
        
        Args:
            documents: List of dicts with 'id' and 'text' keys
        """
        if not documents:
            return
        
        self._documents = documents
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        self._dimension = embeddings.shape[1]
        
        # Create FAISS index
        faiss = self._get_faiss()
        self._index = faiss.IndexFlatIP(self._dimension)  # Inner product for cosine similarity
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        self._index.add(embeddings)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of dicts with 'id', 'text', 'score'
        """
        if self._index is None or len(self._documents) == 0:
            return []
        
        faiss = self._get_faiss()
        
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search
        k = min(top_k, len(self._documents))
        scores, indices = self._index.search(query_embedding, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0:
                doc = self._documents[idx]
                results.append({
                    'id': doc['id'],
                    'text': doc['text'][:200],
                    'score': float(scores[0][i]),
                })
        
        return results

    def save(self, path: str) -> None:
        """Save index to disk."""
        if self._index is None:
            raise ValueError("No index to save")
        faiss = self._get_faiss()
        faiss.write_index(self._index, f"{path}/index.faiss")
        # Save documents separately (pickle or JSON)
        import json
        with open(f"{path}/documents.json", 'w') as f:
            json.dump(self._documents, f)

    def load(self, path: str) -> None:
        """Load index from disk."""
        faiss = self._get_faiss()
        self._index = faiss.read_index(f"{path}/index.faiss")
        import json
        with open(f"{path}/documents.json", 'r') as f:
            self._documents = json.load(f)
