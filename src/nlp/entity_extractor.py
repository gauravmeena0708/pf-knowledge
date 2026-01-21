from gliner import GLiNER
from typing import List, Dict, Any
import re

class GLiNEREntityExtractor:
    def __init__(self, model_name: str = "urchade/gliner_multi-v2.1", threshold: float = 0.3):
        """
        Initialize GLiNER model.
        
        Args:
            model_name (str): GLiNER model name.
            threshold (float): Confidence threshold.
        """
        self.model_name = model_name
        self.threshold = threshold
        # Lazy loading could be implemented, but for now we load on init or on demand
        self._model = None

    @property
    def model(self):
        if self._model is None:
            # Using CPU map_location for safety
            self._model = GLiNER.from_pretrained(self.model_name, map_location="cpu")
        return self._model

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities using GLiNER.
        
        Labels: Judge, Establishment, Representative, Act, Section, Amount, Date
        
        Returns:
            Dict[str, List[str]]: {'Judge': ['Name'], 'Amount': [10000.0]}
        """
        if not text or not text.strip():
            return {}

        labels = ["Judge", "Establishment", "Representative", "Act", "Section", "Amount", "Date"]
        
        try:
            predictions = self.model.predict_entities(text, labels, threshold=self.threshold)
        except Exception as e:
            print(f"GLiNER prediction failed: {e}")
            return {}

        # Post-process predictions
        extracted = {label: [] for label in labels}
        
        for pred in predictions:
            label = pred['label']
            text_val = pred['text'].strip()
            
            if not text_val:
                continue
                
            # Clean specific types
            if label == "Amount":
                clean_val = self._clean_amount(text_val)
                if clean_val:
                   extracted[label].append(clean_val)
            elif label == "Date":
                # Basic cleaning or keeping as string
                extracted[label].append(text_val)
            else:
                if text_val not in extracted[label]:
                     extracted[label].append(text_val)
        
        return extracted

    def _clean_amount(self, amount_str: str) -> float:
        """
        Clean amount string e.g. "Rs. 40,704/-" -> 40704.0
        """
        # Remove "Rs.", "/-", commas, spaces
        # Handle "Rs." specifically to remove its dot
        text = amount_str.lower().replace("rs.", "").replace("rs", "")
        # Remove commas
        text = text.replace(",", "")
        
        clean = re.sub(r'[^\d.]', '', text)
        print(f"DEBUG: Input='{amount_str}', Cleaned='{clean}'")
        try:
            val = float(clean)
            return val
        except ValueError:
            return None
