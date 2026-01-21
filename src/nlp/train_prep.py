import json
from typing import List, Dict

def convert_to_bio_format(text: str, entities: List[Dict]) -> List[tuple]:
    """
    Convert text and extracted entities into BIO (Beginning, Inside, Outside) format
    suitable for training custom NER models (CoNLL format).
    
    Args:
        text (str): One sentence or segment of text.
        entities (List[Dict]): List of dicts like {'start': 10, 'end': 15, 'label': 'PER'}
        
    Returns:
        List[tuple]: List of (token, label) tuples.
    """
    tokens = text.split()
    # Simple tokenization by whitespace for demonstration. 
    # Real implementation needs a proper tokenizer to align with character indices.
    
    bio_tags = ['O'] * len(tokens)
    
    # This is a basic implementation placeholder. 
    # Aligning character offsets to tokens is non-trivial without a tokenizer library (like spaCy or Transformers).
    # Since we have 'transformers' installed, we could use a tokenizer, but for this "Preparation" task,
    # we will output a JSON structure that is easier to inspect and load later.
    return []

def export_training_data(cases_data: List[Dict], output_file: str = "ner_training_data.json"):
    """
    Exports case data into a JSON format for annotation/fine-tuning.
    
    Args:
        cases_data: List of dicts containing 'text' and 'metadata' (labels).
        output_file: Path to save JSON.
    """
    data_for_annotation = []
    
    for case in cases_data:
        # We can pre-label based on our Regex extractors
        # e.g., if we found "Order Date: 2023-01-01", we label "2023-01-01" as DATE
        item = {
            "text": case['text'],
            "predictions": [] # Placeholders for annotators
        }
        data_for_annotation.append(item)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_for_annotation, f, indent=2)
    
    print(f"Exported {len(data_for_annotation)} items to {output_file}")

if __name__ == "__main__":
    # Example usage
    dummy_data = [
        {"text": "Order Date: 20-10-2023. Case ID: 7A/555.", "metadata": {}}
    ]
    export_training_data(dummy_data)
