import os
import joblib
import pickle


# Global model variables
encoder = None
classifier = None

def load_models():
    global encoder, classifier
    try:
        # Use absolute paths or relative to the project root
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        encoder_path = os.path.join(base_path, "backend", "ml_assets", "vector_brain.pkl")
        model_path = os.path.join(base_path, "backend", "ml_assets", "scam_model.pkl")
        
        if os.path.exists(encoder_path) and os.path.exists(model_path):
            encoder = joblib.load(encoder_path)
            classifier = joblib.load(model_path)
            print("Security: Models loaded successfully.")
        else:
            print("Security: Model files not found. Using fallback.")
    except Exception as e:
        print(f"Security: Failed to load models: {e}")

# Load on module import (effectively startup)
load_models()

def predict_scam(text: str):
    """
    Predicts if the text is a scam.
    Returns: (is_scam: bool, confidence: float)
    """
    global encoder, classifier
    
    # Fallback keywords
    keywords = ["urgent", "verify", "block", "lottery", "bank", "credit card", "password", "otp"]
    
    try:
        if encoder and classifier:
            # Vectorize
            vector = encoder.encode([text])
            # Predict
            prob = classifier.predict_proba(vector)[0][1] # Probability of class 1 (Scam)
            is_scam = prob > 0.5
            return is_scam, float(prob)
    except Exception as e:
        print(f"Security: Prediction error: {e}")
        pass
        
    # Fallback Logic
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            return True, 1.0
            
    return False, 0.0
