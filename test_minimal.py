import os
import sys
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import webbrowser
import threading
import time

# Add local Shapash to Python path
shapash_path = os.path.join(os.path.dirname(__file__), 'shapash')
if shapash_path not in sys.path:
    sys.path.append(shapash_path)

from shapash.explainer.smart_explainer import SmartExplainer

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)  # Give the server a moment to start
    webbrowser.open('http://localhost:8050/')

def main():
    # Load data
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name='target')
    
    # Split and scale data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
    
    # Train model
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)
    
    # Initialize explainer
    xpl = SmartExplainer(
        model=model,
        features_dict={name: name for name in X.columns}
    )
    
    # Compile explainer
    xpl.compile(
        x=X_test_scaled,
        y_pred=pd.Series(model.predict(X_test_scaled), name='prediction')
    )
    
    print("Starting Shapash web app...")
    
    # Open browser in a new thread
    threading.Thread(target=open_browser).start()
    
    # Run the app
    app = xpl.run_app(host='0.0.0.0', port=8050)
    app.run(debug=False, host='0.0.0.0', port=8050)

if __name__ == "__main__":
    main()
