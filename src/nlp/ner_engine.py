from transformers import pipeline
from typing import Dict, List, Any

class LegalEntityExtractor:
    def __init__(self, model_name: str = "dslim/bert-base-NER", threshold: float = 0.7):
        """
        Initialize the Legal Entity Extractor.
        
        Args:
            model_name (str): HuggingFace model name.
            threshold (float): Confidence threshold to accept an entity.
        """
        self.model_name = model_name
        self.threshold = threshold
        self._pipeline = None

    @property
    def pipeline(self):
        """Lazy loader for the NER pipeline."""
        if self._pipeline is None:
            # aggregation_strategy="simple" groups subwords like "Go" "##vin" "##da" -> "Govinda"
            self._pipeline = pipeline("ner", model=self.model_name, aggregation_strategy="simple")
        return self._pipeline

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text.
        
        Args:
            text (str): Input text.
            
        Returns:
            Dict[str, List[str]]: Dictionary of entities by type (e.g., {'PER': [], 'ORG': []})
        """
        if not text or not text.strip():
            return {}

        try:
            results = self.pipeline(text)
        except Exception as e:
            # Fallback or log error
            print(f"BERT Inference Error: {e}")
            return {}

        entities = {
            'PER': [],
            'ORG': [],
            'LOC': [],
            'MISC': []
        }

        for result in results:
            score = result.get('score', 0.0)
            if score < self.threshold:
                continue
                
            entity_group = result.get('entity_group')
            word = result.get('word', '').strip()
            
            if entity_group in entities and word:
                if word not in entities[entity_group]:
                    entities[entity_group].append(word)

        return entities

    def extract_with_fallback(self, text: str) -> Dict[str, List[str]]:
        """
        Hybrid approach: BERT + Regex.
        For now, just calls extract_entities.
        """
        return self.extract_entities(text)
