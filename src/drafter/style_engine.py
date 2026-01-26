import re
from typing import Dict, Any

class StyleAnalyzer:
    """
    Analyzes legal orders to extract structural templates and stylistic elements.
    """
    
    def __init__(self):
        self.sections = {
            'header': r'(.*?)(?:IN THE MATTER OF|PRESENT:|ORDER)',
            'appearance': r'PRESENT:(.*?)(?:ORDER|The proceedings)',
            'body': r'(?:ORDER|The proceedings)(.*)(?:\([A-Z][a-z]+ [A-Z][a-z]+\))', # Rough capture up to signature
            'signature': r'(\([A-Z][a-z]+ [A-Z][a-z]+\)\s*(?:APFC|RPFC|Assistant|Regional).*)'
        }
        
    def analyze(self, text: str) -> Dict[str, str]:
        if not text:
            return {}
            
        style = {}
        
        # Header (Top element)
        # Regex is bit fragile, so we use heuristics
        lines = text.split('\n')
        
        # Header: usually first few lines until "IN THE MATTER OF" or "ORDER"
        header_lines = []
        for line in lines:
            if "IN THE MATTER OF" in line or "PRESENT" in line or line.strip() == "ORDER":
                break
            header_lines.append(line)
        style['header'] = "\n".join(header_lines).strip()
        
        # Appearance
        match = re.search(r'PRESENT:(.*?)(?:ORDER|The proceedings)', text, re.DOTALL | re.IGNORECASE)
        if match:
             style['appearance'] = match.group(1).strip()
        else:
             style['appearance'] = ""
             
        # Signature (last few lines looking for Name in parens)
        # Look for (Name) at end
        sig_match = re.search(r'(\([A-Za-z\s.]+\)\s*\n\s*(?:APFC|RPFC|Assistant|Regional|[A-Z]+))', text, re.DOTALL | re.IGNORECASE)
        if sig_match:
            style['signature'] = sig_match.group(1).strip()
        else:
            style['signature'] = ""
            
        # Body (Between Appearance/Header and Signature)
        # Simplified logic
        start = len(style['header'])
        if style['appearance']:
             # find end of appearance in text
             # This is hard because we extracted it via Regex which normalizes whitespace
             pass
        
        # Let's just key off "ORDER" keyword if present
        order_idx = text.find("\nORDER\n")
        if order_idx == -1:
             order_idx = text.find("\nOrder\n")
             
        if order_idx != -1:
             body_text = text[order_idx+7:] # skip ORDER
             # remove signature
             if style['signature']:
                 body_text = body_text.replace(style['signature'], '')
             style['body'] = body_text.strip()
        else:
             style['body'] = text
        
        return style
