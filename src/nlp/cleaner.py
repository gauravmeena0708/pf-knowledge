import re

def clean_text(text: str) -> str:
    """
    Cleans OCR extracted text to remove common noise and artifacts.
    
    Strategies:
    1. Fix hyphenation (word- break).
    2. Filter out "garbage lines" (high frequency of symbols).
    3. Remove specific OCR artifacts (e.g., "bE |", "Jag=").
    4. Normalize whitespace.
    
    Args:
        text (str): Raw input text.
        
    Returns:
        str: Cleaned text.
    """
    if not text:
        return ""

    # 1. Start by splitting into lines to process line-by-line
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            # Preserve paragraph breaks (empty lines) but max 1
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue
            
        # 2. Garbage Line Detection
        # Calculate ratio of non-alphanumeric chars (excluding spaces)
        alnum_count = sum(c.isalnum() for c in stripped_line)
        total_count = len(stripped_line.replace(" ", ""))
        
        if total_count > 0:
            ratio = alnum_count / total_count
            # If less than 50% alphanumeric, treat as garbage (e.g., "||..//")
            # But be careful with short headers like "No." or dates "20-10-2023"
            if ratio < 0.5 and total_count > 5:
                continue

        # 3. Artifact Removal
        # Specific patterns observed in this dataset
        line_clean = stripped_line.replace("Jag=", "") \
                                  .replace("bE |", "") \
                                  .replace("3a DES", "") \
                                  .replace("|", "")
        
        line_clean = line_clean.strip()
        if line_clean:
            cleaned_lines.append(line_clean)
            
    # Reassemble
    text_step1 = "\n".join(cleaned_lines)
    
    # 4. Fix Hyphenation
    # "demonst-\nration" -> "demonstration"
    # Regex: word char + hyphen + whitespace + word char
    text_step2 = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text_step1)
    
    return text_step2
