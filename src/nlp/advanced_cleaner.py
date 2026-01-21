"""
Advanced Text Cleaning for Processed Content
Removes OCR artifacts and produces human-readable text
"""

import re

def remove_ocr_artifacts(text: str) -> str:
    """
    Remove common OCR artifacts and garbage characters.
    
    Args:
        text: Raw OCR text
        
    Returns:
        Cleaned text without artifacts
    """
    if not text:
        return ""
    
    # Step 1: Remove excessive special characters and symbols
    # Keep only letters, numbers, spaces, and common punctuation
    text = re.sub(r'[^\w\s.,;:!?()\[\]{}\-/&@\'\"₹\n]', ' ', text)
    
    # Step 2: Remove standalone ## symbols (common OCR error)
    text = re.sub(r'\s*##\s*', ' ', text)
    
    # Step 3: Fix spacing around punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)
    text = re.sub(r'([.,;:!?])([^\s])', r'\1 \2', text)
    
    # Step 4: Remove single characters surrounded by spaces (likely OCR errors)
    # But keep common single letters like 'A', 'I'
    text = re.sub(r'\s+([^AIa\s])\s+', ' ', text)
    
    # Step 5: Remove excessive repetition (like "- - - -")
    text = re.sub(r'([-_=*])\s*\1{2,}', '', text)
    
    # Step 5b: Remove underscores (common in forms)
    text = re.sub(r'_{2,}', ' ', text)
    
    # Step 6: Fix common OCR character substitutions
    substitutions = {
        r'\s+l\s+': ' I ',  # lowercase L often mistaken for I
        r'\btbe\b': 'the',
        r'\bTbe\b': 'The',
        r'\baod\b': 'and',
        r'\bOrgaoisation\b': 'Organisation',
        r'\bOrgaoization\b': 'Organization',
        r'\bProvideot\b': 'Provident',
    }
    
    for pattern, replacement in substitutions.items():
        text = re.sub(pattern, replacement, text)
    
    # Step 7: Remove multiple consecutive spaces
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Step 8: Remove multiple consecutive newlines (keep max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Step 9: Fix sentence spacing
    text = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1\n\n\2', text)
    
    return text.strip()

def extract_key_sections(text: str) -> str:
    """
    Extract and format key sections from legal documents.
    
    Args:
        text: Cleaned text
        
    Returns:
        Formatted text with clear section headers
    """
    if not text:
        return ""
    
    # Identify section headers (all caps lines)
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # If line is mostly uppercase and short, treat as header
        if len(line) > 5 and len(line) < 100 and line.isupper():
            processed_lines.append(f"\n### {line.title()}\n")
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def create_processed_content(raw_text: str) -> str:
    """
    Main function to create processed, human-readable content.
    
    Args:
        raw_text: Raw OCR text
        
    Returns:
        Cleaned and formatted text
    """
    # First pass: Remove OCR artifacts
    cleaned = remove_ocr_artifacts(raw_text)
    
    # Second pass: Format sections
    formatted = extract_key_sections(cleaned)
    
    # Final cleanup
    formatted = re.sub(r'\n{3,}', '\n\n', formatted)
    
    return formatted.strip()
