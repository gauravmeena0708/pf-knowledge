import re
from typing import Dict, Any

class CaseClassifier:
    """
    Classifies EPF case documents by type (7A/14B) and compliance outcome.
    """
    
    def __init__(self):
        # Case type indicators
        self.type_indicators = {
            '7A': [
                r'section\s*7[- ]?a',
                r'7a\s*(?:order|determination)',
                r'determination\s+of\s+dues',
                r'arrears?\s+(?:of|assessment)',
            ],
            '14B': [
                r'section\s*14[- ]?b',
                r'14b\s*(?:order|penalty)',
                r'penalty\s+(?:for|under)',
                r'delayed\s+remittance',
                r'penal\s+damages?',
            ],
        }
        
        # Compliance outcome indicators
        self.outcome_indicators = {
            'non_compliant': [
                r'failed\s+to\s+comply',
                r'non-?compliance',
                r'dues?\s+(?:confirmed|assessed)',
                r'default\s+assessment',
                r'penalty\s+(?:imposed|levied)',
                r'liable\s+to\s+pay',
            ],
            'compliant': [
                r'no\s+discrepancy',
                r'records?\s+verified',
                r'(?:case|matter)\s+disposed',
                r'compliant',
                r'in\s+order',
            ],
        }

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify case document.
        
        Args:
            text: Document text
            
        Returns:
            Dict with case_type, outcome, confidence
        """
        if not text or not text.strip():
            return {
                'case_type': 'unknown',
                'outcome': 'unknown',
                'confidence': 0.0,
            }
        
        text_lower = text.lower()
        
        # Classify case type
        type_scores = {}
        for case_type, patterns in self.type_indicators.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            type_scores[case_type] = score
        
        # Determine primary type
        if type_scores.get('7A', 0) > 0 and type_scores.get('14B', 0) > 0:
            # Both present
            if type_scores['7A'] > type_scores['14B']:
                case_type = '7A'
            elif type_scores['14B'] > type_scores['7A']:
                case_type = '14B'
            else:
                case_type = 'mixed'
        elif type_scores.get('7A', 0) > 0:
            case_type = '7A'
        elif type_scores.get('14B', 0) > 0:
            case_type = '14B'
        else:
            case_type = 'unknown'
        
        # Classify outcome
        outcome_scores = {}
        for outcome, patterns in self.outcome_indicators.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            outcome_scores[outcome] = score
        
        if outcome_scores.get('non_compliant', 0) > outcome_scores.get('compliant', 0):
            outcome = 'non_compliant'
        elif outcome_scores.get('compliant', 0) > 0:
            outcome = 'compliant'
        else:
            outcome = 'unknown'
        
        # Confidence based on match count
        total_matches = sum(type_scores.values()) + sum(outcome_scores.values())
        confidence = min(1.0, total_matches / 10.0)
        
        return {
            'case_type': case_type,
            'outcome': outcome,
            'confidence': confidence,
            'type_scores': type_scores,
            'outcome_scores': outcome_scores,
        }
