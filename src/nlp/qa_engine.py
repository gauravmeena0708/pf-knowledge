import re
from typing import Optional

class QAEngine:
    """
    Question-Answering engine for EPF case documents.
    Uses pattern matching and extractive QA for domain-specific questions.
    """
    
    def __init__(self):
        # Question-to-pattern mapping for common queries
        self.question_patterns = {
            'total_dues': [
                (r'total\s+dues?', r'(?:total\s+dues?|amount\s+to)[:\s]*(?:rs\.?\s*)?([\d,]+)'),
                (r'how\s+much', r'(?:total|amount|dues?)[:\s]*(?:rs\.?\s*)?([\d,]+)'),
            ],
            'hearing_count': [
                (r'how\s+many\s+hearings?', r'(?:heard\s+on|conducted)\s+(\d+)\s+(?:occasions?|times?)'),
                (r'number\s+of\s+hearings?', r'(\d+)\s+hearings?'),
            ],
            'officer': [
                (r'who\s+is\s+the\s+officer', r'(?:order\s+(?:passed|issued)\s+by|signed\s+by)\s+([A-Z][a-zA-Z\s.]+?)(?:,|\n)'),
                (r'officer\s+name', r'(?:Shri\.|Smt\.|Mr\.|Ms\.)\s*([A-Z][A-Z\s.]+)'),
            ],
            'establishment': [
                (r'establishment|employer', r'(?:M/s|Messrs)\s+([A-Za-z\s]+?)(?:\.|,|\n)'),
            ],
            'case_number': [
                (r'case\s+number', r'(?:Case\s+No\.|No\.)\s*([A-Z0-9/()-]+)'),
            ],
            'period': [
                (r'period|duration', r'(?:period|from)\s+([A-Za-z]+\s+\d{4})\s+to\s+([A-Za-z]+\s+\d{4})'),
            ],
        }

    def answer(self, question: str, context: str) -> str:
        """
        Answer a question based on the context.
        
        Args:
            question: Natural language question
            context: Document text to search
            
        Returns:
            Answer string or empty if not found
        """
        if not context or not context.strip():
            return ""
        
        if not question or not question.strip():
            return ""
        
        question_lower = question.lower()
        
        # Identify question type
        for q_type, patterns in self.question_patterns.items():
            for q_pattern, a_pattern in patterns:
                if re.search(q_pattern, question_lower):
                    # Try to extract answer
                    match = re.search(a_pattern, context, re.IGNORECASE)
                    if match:
                        # Return first captured group
                        groups = match.groups()
                        if groups:
                            return groups[0].strip()
                        return match.group(0).strip()
        
        # Fallback: try to find relevant sentence
        return self._fallback_answer(question, context)

    def _fallback_answer(self, question: str, context: str) -> str:
        """Fallback: find most relevant sentence."""
        # Extract key terms from question
        stopwords = {'what', 'who', 'how', 'many', 'much', 'the', 'was', 'is', 'are', 'were'}
        question_terms = set(re.findall(r'\b[a-z]{3,}\b', question.lower())) - stopwords
        
        if not question_terms:
            return ""
        
        # Score each sentence
        sentences = re.split(r'(?<=[.!?])\s+', context)
        
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sent_lower = sentence.lower()
            score = sum(1 for term in question_terms if term in sent_lower)
            if score > best_score:
                best_score = score
                best_sentence = sentence
        
        # Extract answer from best sentence
        if best_score > 0:
            # Return numbers or named entities
            numbers = re.findall(r'[\d,]+', best_sentence)
            if numbers and any(term in ['total', 'dues', 'amount', 'many', 'count'] for term in question_terms):
                return numbers[0]
            return best_sentence[:200].strip()
        
        return "Not found"

    def batch_qa(self, questions: list, context: str) -> dict:
        """Answer multiple questions at once."""
        return {q: self.answer(q, context) for q in questions}
