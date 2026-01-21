import re
from typing import List, Dict, Optional
from datetime import datetime

class TimelineExtractor:
    """
    Extracts chronological hearing events from EPF case documents.
    """
    
    def __init__(self):
        # Patterns to find hearing blocks
        self.date_patterns = [
            # DD.MM.YYYY, DD-MM-YYYY, DD/MM/YYYY
            r'(?:On|Dated?|Hearing\s+(?:on|held\s+on)?)\s*[:\s]*(\d{1,2}[./-]\d{1,2}[./-]\d{4})',
            # Standalone dates at start of sentence
            r'(?:^|\.\s+)(\d{1,2}[./-]\d{1,2}[./-]\d{4})',
        ]
        
        # Outcome keywords
        self.outcome_keywords = {
            'adjourned': ['adjourned', 'postponed', 'next date', 'put up'],
            'concluded': ['concluded', 'closed', 'disposed'],
            'order_issued': ['order issued', 'order passed', 'order was issued'],
        }
        
        # Appearance patterns
        self.appearance_patterns = [
            r'(Shri\.|Smt\.|Mr\.|Ms\.)\s*([A-Z][a-zA-Z\s.]+?)(?:\s*\(([^)]+)\))?(?:\s*appeared|\s*present)',
            r'([A-Z][a-zA-Z\s.]+?)\s*\(([^)]+)\)\s*(?:appeared|present)',
            r'No\s*one\s*appeared',
        ]

    def extract(self, text: str) -> List[Dict]:
        """
        Extract timeline events from document text.
        
        Args:
            text: Raw text content
            
        Returns:
            List of timeline events, chronologically sorted
        """
        if not text or not text.strip():
            return []
        
        events = []
        
        # Split into potential hearing blocks
        # Look for date markers
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                date_str = match.group(1)
                normalized_date = self._normalize_date(date_str)
                
                if normalized_date is None:
                    continue
                
                # Get context around the date (next ~300 chars or until next date)
                start_pos = match.end()
                end_pos = min(start_pos + 500, len(text))
                
                # Try to find next date marker to bound the context
                next_date_match = re.search(r'\d{1,2}[./-]\d{1,2}[./-]\d{4}', text[start_pos:end_pos])
                if next_date_match:
                    end_pos = start_pos + next_date_match.start()
                
                context = text[start_pos:end_pos]
                
                event = {
                    'date': normalized_date,
                    'appeared': self._extract_appearances(context),
                    'discussion': self._extract_discussion(context),
                    'outcome': self._classify_outcome(context),
                    'next_date': self._extract_next_date(context),
                }
                
                # Avoid duplicates
                if not any(e['date'] == normalized_date for e in events):
                    events.append(event)
        
        # Sort chronologically
        events.sort(key=lambda x: x['date'])
        
        return events

    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        Normalize date to YYYY-MM-DD format.
        """
        # Replace separators
        clean = date_str.replace('/', '-').replace('.', '-')
        parts = clean.split('-')
        
        if len(parts) != 3:
            return None
        
        try:
            day, month, year = parts
            day = int(day)
            month = int(month)
            year = int(year)
            
            # Validate
            if day < 1 or day > 31 or month < 1 or month > 12:
                return None
            
            # Create datetime to validate
            dt = datetime(year, month, day)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    def _extract_appearances(self, context: str) -> List[str]:
        """Extract who appeared at the hearing."""
        appearances = []
        
        # Check for "No one appeared"
        if re.search(r'no\s*one\s*appeared', context, re.IGNORECASE):
            return ['No one']
        
        # Look for named appearances
        for pattern in self.appearance_patterns[:2]:
            matches = re.findall(pattern, context, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    name_parts = [p.strip() for p in match if p and p.strip()]
                    appearances.append(' '.join(name_parts))
                else:
                    appearances.append(match.strip())
        
        return list(set(appearances))

    def _extract_discussion(self, context: str) -> str:
        """Extract what was discussed (simplified)."""
        # Look for common action phrases
        action_patterns = [
            r'directed\s+([^.]+)',
            r'requested\s+([^.]+)',
            r'submitted\s+([^.]+)',
            r'produced\s+([^.]+)',
        ]
        
        for pattern in action_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(0).strip()[:200]
        
        # Return first sentence as fallback
        first_sentence = context.split('.')[0].strip()
        return first_sentence[:200] if first_sentence else ''

    def _classify_outcome(self, context: str) -> str:
        """Classify the hearing outcome."""
        context_lower = context.lower()
        
        for outcome, keywords in self.outcome_keywords.items():
            for kw in keywords:
                if kw in context_lower:
                    return outcome.replace('_', ' ').title()
        
        return 'Unknown'

    def _extract_next_date(self, context: str) -> Optional[str]:
        """Extract the next hearing date if adjourned."""
        patterns = [
            r'adjourned\s+to\s+(\d{1,2}[./-]\d{1,2}[./-]\d{4})',
            r'next\s+date[:\s]+(\d{1,2}[./-]\d{1,2}[./-]\d{4})',
            r'put\s+up\s+(?:on|to)\s+(\d{1,2}[./-]\d{1,2}[./-]\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return self._normalize_date(match.group(1))
        
        return None
