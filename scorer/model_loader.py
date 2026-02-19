"""Model loading utilities."""
import joblib
import os

class ModelLoader:
    """Lazy model loader with caching."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, model_path="models/fraud_model.joblib"):
        if self._model is None:
            if not os.path.exists(model_path):
                raise FileNotFoundError("Model not found: {}".format(model_path))
            self._model = joblib.load(model_path)
        return self._model
    
    def predict_proba(self, features):
        model = self.load()
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        proba = model.predict_proba(features)
        return float(proba[0][1])
    
    def reload(self, model_path="models/fraud_model.joblib"):
        self._model = None
        return self.load(model_path)

def get_model_loader():
    return ModelLoader()
