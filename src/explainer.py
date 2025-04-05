import os
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Add local Shapash to Python path
shapash_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shapash')
if shapash_path not in sys.path:
    sys.path.append(shapash_path)

from shapash.explainer.smart_explainer import SmartExplainer
import dash

class XAIExplainer:
    def __init__(self, model_handler, data_path):
        """Initialize the XAI explainer with a model and data"""
        self.model_handler = model_handler
        self.data = pd.read_csv(data_path)
        self.target_column = 'target' if 'target' in self.data.columns else self.data.columns[-1]
        self.features = self.data.drop(columns=[self.target_column])
        self.target = pd.Series(self.data[self.target_column], name=self.target_column)
        
        # Handle categorical features
        self.label_encoders = {}
        self.encode_categorical_features()
        
    def encode_categorical_features(self):
        """Encode categorical features in the dataset"""
        
        for column in self.features.columns:
            if self.features[column].dtype == 'object':
                le = LabelEncoder()
                self.features[column] = le.fit_transform(self.features[column])
                self.label_encoders[column] = le
                
    def compile_explainer(self):
        """Compile the explainer with the current model and data"""
        try:
            # Drop any rows with NaN values
            data = self.data.dropna()
            
            # Create a features dictionary
            features_dict = {col: col for col in data.columns if col != 'target'}
            
            # Initialize SmartExplainer with proper feature names
            self.explainer = SmartExplainer(
                model=self.model_handler.model,
                features_dict=features_dict,
                preprocessing=None  # We've already preprocessed the data
            )
            
            # Split features and target
            X = data.drop('target', axis=1)
            y = data['target']
            
            # Get predictions
            y_pred = pd.Series(self.model_handler.predict(X), name='prediction')
            
            # Compile the explainer
            self.explainer.compile(
                x=X,
                y_pred=y_pred,
                y_target=y  # Pass the target variable
            )
            
            print("Shapash explainer compiled successfully!")
            return True
            
        except Exception as e:
            print(f"Error compiling explainer: {str(e)}")
            return False
        
    def launch_webapp(self, port=8050):
        """Launch the Shapash web app"""
        try:
            self.compile_explainer()
            print(f"Starting Shapash web app on http://localhost:{port}")
            # Let SmartExplainer handle the threading and app startup
            app = self.explainer.run_app(host='0.0.0.0', port=port)
            return app
        except Exception as e:
            raise ValueError(f"Error launching webapp: {str(e)}")
