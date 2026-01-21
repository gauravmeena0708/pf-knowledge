import re
from typing import List, Tuple
from collections import Counter

class Summarizer:
    """
    Extractive summarization and key phrase extraction for EPF case documents.
    Uses TF-IDF based approach for lightweight operation.
    KeyBERT can be used if available.
    """
    
    def __init__(self):
        self._keybert = None
        
    @property
    def keybert(self):
        """Lazy load KeyBERT if available."""
        if self._keybert is None:
            try:
                from keybert import KeyBERT
                self._keybert = KeyBERT()
            except ImportError:
                self._keybert = False
        return self._keybert

    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Extract top key phrases from text.
        
        Args:
            text: Document text
            top_n: Number of key phrases to return
            
        Returns:
            List of (phrase, score) tuples
        """
        if not text or not text.strip():
            return []
        
        # Try KeyBERT if available
        if self.keybert and self.keybert is not False:
            try:
                keywords = self.keybert.extract_keywords(
                    text, 
                    keyphrase_ngram_range=(1, 3),
                    stop_words='english',
                    top_n=top_n
                )
                return keywords
            except Exception:
                pass
        
        # Fallback to TF-IDF based extraction
        return self._tfidf_keywords(text, top_n)

    def _tfidf_keywords(self, text: str, top_n: int) -> List[Tuple[str, float]]:
        """Simple TF-IDF based keyword extraction."""
        # Tokenize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stopwords
        stopwords = {'the', 'and', 'for', 'was', 'were', 'that', 'this', 'with', 'from', 
                     'have', 'has', 'had', 'not', 'are', 'but', 'been', 'being', 'which',
                     'their', 'they', 'you', 'your', 'will', 'would', 'could', 'should'}
        words = [w for w in words if w not in stopwords]
        
        # Count frequencies
        word_counts = Counter(words)
        
        # Domain-specific boost
        domain_terms = {'employer', 'employee', 'contribution', 'provident', 'fund', 
                       'section', 'act', 'penalty', 'dues', 'assessment', 'hearing',
                       'officer', 'commissioner', 'arrears', 'remittance'}
        
        # Score: frequency * domain_boost
        scores = {}
        for word, count in word_counts.items():
            boost = 2.0 if word in domain_terms else 1.0
            scores[word] = count * boost
        
        # Sort and return top_n
        sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:top_n]

    def summarize_extractive(self, text: str, num_sentences: int = 5) -> str:
        """
        Generate extractive summary by selecting top sentences.
        
        Args:
            text: Document text
            num_sentences: Number of sentences in summary
            
        Returns:
            Summary string
        """
        if not text or not text.strip():
            return ""
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= num_sentences:
            return ' '.join(sentences)
        
        # Score sentences by key phrase presence
        key_phrases = [kp[0] for kp in self.extract_key_phrases(text, top_n=20)]
        
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            sent_lower = sentence.lower()
            score = sum(1 for kp in key_phrases if kp in sent_lower)
            # Position bonus: first and last sentences
            if i == 0:
                score += 2
            elif i == len(sentences) - 1:
                score += 1
            sentence_scores.append((i, sentence, score))
        
        # Sort by score, take top N, then re-sort by position
        top_sentences = sorted(sentence_scores, key=lambda x: x[2], reverse=True)[:num_sentences]
        top_sentences = sorted(top_sentences, key=lambda x: x[0])
        
        return ' '.join([s[1] for s in top_sentences])
