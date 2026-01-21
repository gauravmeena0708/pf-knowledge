import re
from typing import List, Dict, Any

class RelationExtractor:
    """
    Extracts cause-effect relations from EPF case documents.
    Focus on: officer requests, employer failures, consequences.
    """
    
    def __init__(self):
        # Relation patterns
        self.patterns = {
            'officer_directive': [
                r'(?:officer|apfc|pfc|commissioner)\s+(?:directed|instructed|ordered)\s+(?:the\s+)?(?:employer\s+)?to\s+([^.]+)',
                r'(?:directed|instructed)\s+to\s+(?:produce|submit|provide)\s+([^.]+)',
            ],
            'failure_to_submit': [
                r'(?:employer\s+)?failed\s+to\s+(?:submit|produce|provide)\s+([^.]+)',
                r'(?:non-?submission|non-?production)\s+of\s+([^.]+)',
                r'did\s+not\s+(?:submit|produce|provide)\s+([^.]+)',
            ],
            'consequence': [
                r'(?:as\s+a\s+)?result\s+of\s+([^,]+),\s*([^.]+)',
                r'due\s+to\s+([^,]+),\s*([^.]+)',
                r'(?:therefore|hence|consequently),?\s*([^.]+)',
            ],
            'penalty': [
                r'penalty\s+(?:was\s+)?(?:imposed|levied)\s+(?:under\s+)?(?:section\s+)?(\d+[AB]?)',
                r'liable\s+(?:to\s+pay|for)\s+([^.]+)',
            ],
            'default_assessment': [
                r'default\s+(?:assessment|rate)\s+(?:was\s+)?applied',
                r'(?:assumed|presumed)\s+(?:at\s+)?(?:minimum|maximum)\s+wages?',
            ],
        }

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract relations from document text.
        
        Args:
            text: Raw text content
            
        Returns:
            List of relation dicts with type, subject, object, context
        """
        if not text or not text.strip():
            return []
        
        relations = []
        
        for relation_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    groups = match.groups()
                    
                    relation = {
                        'type': relation_type,
                        'text': match.group(0).strip(),
                        'start': match.start(),
                        'end': match.end(),
                    }
                    
                    # Extract subject/object from groups
                    if len(groups) >= 1:
                        relation['object'] = groups[0].strip() if groups[0] else ''
                    if len(groups) >= 2:
                        relation['consequence'] = groups[1].strip() if groups[1] else ''
                    
                    # Get surrounding context
                    context_start = max(0, match.start() - 50)
                    context_end = min(len(text), match.end() + 50)
                    relation['context'] = text[context_start:context_end].strip()
                    
                    relations.append(relation)
        
        # Sort by position in text
        relations.sort(key=lambda x: x['start'])
        
        return relations

    def extract_compliance_gaps(self, text: str) -> Dict[str, List[str]]:
        """
        Extract compliance gaps: requested vs submitted documents.
        
        Returns:
            Dict with 'requested', 'submitted', 'missing' lists
        """
        result = {
            'requested': [],
            'submitted': [],
            'missing': [],
        }
        
        # Requested documents
        requested_patterns = [
            r'(?:directed|instructed|requested)\s+to\s+(?:submit|produce|provide)\s+([^.]+)',
            r'(?:submit|produce|provide)\s+(?:the\s+)?following[:\s]+([^.]+)',
        ]
        
        for pattern in requested_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            result['requested'].extend([m.strip() for m in matches])
        
        # Submitted documents
        submitted_patterns = [
            r'(?:employer\s+)?(?:produced|submitted|provided)\s+([^.]+)',
        ]
        
        for pattern in submitted_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            result['submitted'].extend([m.strip() for m in matches])
        
        # Missing/not submitted
        missing_patterns = [
            r'(?:not\s+)?(?:submitted|produced|provided)\s+(?:the\s+)?([^.]+)',
            r'(?:failed|failure)\s+to\s+(?:submit|produce|provide)\s+([^.]+)',
        ]
        
        for pattern in missing_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            result['missing'].extend([m.strip() for m in matches])
        
        return result
