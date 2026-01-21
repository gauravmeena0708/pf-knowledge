import pytest
from gliner import GLiNER

def test_gliner_model_load():
    """
    Test that the GLiNER model loads successfully.
    Uses 'urchade/gliner_multi_v2.1' as preferred by user.
    """
    try:
        model_name = "urchade/gliner_multi-v2.1"
        # Checking if we can load it. 
        # map_location="cpu" is safer for CI/CD or envs without GPU, 
        # though GLiNER automatically handles device if not specified usually.
        # But let's be explicit to avoid CUDA errors if torch detects cuda but fails.
        model = GLiNER.from_pretrained(model_name, map_location="cpu")
        
        assert model is not None
        
        # Simple inference test
        text = "Order passed by APFC Krishan Kumar against M/s City Auto Mobiles."
        labels = ["Judge", "Establishment"]
        entities = model.predict_entities(text, labels)
        
        assert len(entities) > 0
        
        # Check if we got reasonable expected prediction (Judge or Establishment)
        # Note: Zero-shot is powerful but we just assert we got *some* output for now.
        found_judge = any(e['label'] == 'Judge' for e in entities)
        found_est = any(e['label'] == 'Establishment' for e in entities)
        
        # We expect at least one of them to be found in this clear sentence
        assert found_judge or found_est
        
    except Exception as e:
        pytest.fail(f"Failed to load GLiNER output: {e}")
