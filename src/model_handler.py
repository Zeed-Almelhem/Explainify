import joblib
from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.cluster import KMeans
import os

class ModelHandler:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = self._load_model()
        self.model_type = self._detect_model_type()

    def _load_model(self):
        """Load model from pickle file"""
        try:
            if not os.path.exists(self.model_path):
                raise ValueError(f"Model file not found: {self.model_path}")
                
            model = joblib.load(self.model_path)
            
            if not isinstance(model, BaseEstimator):
                raise ValueError("Uploaded model must be a scikit-learn model")
                
            return model
        except Exception as e:
            raise ValueError(f"Error loading model: {str(e)}")

    def _detect_model_type(self):
        """Detect if model is for classification, regression, or clustering"""
        try:
            if isinstance(self.model, LogisticRegression):
                return "classification"
            elif isinstance(self.model, LinearRegression):
                return "regression"
            elif isinstance(self.model, KMeans):
                return "clustering"
            elif hasattr(self.model, 'predict_proba'):
                return "classification"
            elif hasattr(self.model, 'predict'):
                return "regression"
            elif hasattr(self.model, 'fit_predict'):
                return "clustering"
            else:
                raise ValueError("Unable to determine model type")
        except Exception as e:
            raise ValueError(f"Error detecting model type: {str(e)}")
