import os
import sys
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Add local Shapash to Python path
shapash_path = os.path.join(os.path.dirname(__file__), 'shapash')
if shapash_path not in sys.path:
    sys.path.append(shapash_path)

from shapash.explainer.smart_explainer import SmartExplainer

def test_shapash():
    # Load and prepare data
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name='target')
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    
    # Train model
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_scaled, y)
    
    # Make predictions
    y_pred = pd.Series(model.predict(X_scaled), name='prediction')
    
    # Initialize and compile explainer
    features_dict = {name: name for name in X.columns}
    explainer = SmartExplainer(model=model, features_dict=features_dict)
    explainer.compile(x=X_scaled, y_pred=y_pred)
    
    print("Shapash explainer compiled successfully!")
    print("Starting web app on http://localhost:8050")
    
    # Launch web app
    app = explainer.run_app(port=8050)
    app.run_server(debug=False, host='0.0.0.0', port=8050)

if __name__ == '__main__':
    test_shapash()
