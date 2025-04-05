from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from src.model_handler import ModelHandler
from src.explainer import XAIExplainer
import os
import sys
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.datasets import load_iris, fetch_california_housing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import threading

# Add local Shapash to Python path
shapash_path = os.path.join(os.path.dirname(__file__), 'shapash')
if shapash_path not in sys.path:
    sys.path.append(shapash_path)

app = Flask(__name__)
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
EXAMPLE_MODELS_FOLDER = os.path.join(os.path.dirname(__file__), 'example_models')
ALLOWED_EXTENSIONS = {'csv', 'pkl', 'h5', 'pt', 'pth'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXAMPLE_MODELS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variable to store the Shapash app instance
shapash_app = None
shapash_thread = None

def train_iris_model():
    """Train a model on the Iris dataset"""
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name='target')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
    
    # Train model with feature names
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)
    
    return model, X_test_scaled, y_test, scaler

def train_california_model():
    """Train a model on the California Housing dataset"""
    housing = fetch_california_housing()
    X = pd.DataFrame(housing.data, columns=housing.feature_names)
    y = pd.Series(housing.target, name='target')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
    
    # Train model with feature names
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    
    return model, X_test_scaled, y_test, scaler

def create_example_models():
    """Create and save example models if they don't exist"""
    # Classification example (Iris dataset)
    model, X_test_scaled, y_test, scaler = train_iris_model()
    
    # Save model and data
    joblib.dump(model, os.path.join(EXAMPLE_MODELS_FOLDER, 'classification_model.pkl'))
    pd.concat([X_test_scaled, y_test], axis=1).to_csv(
        os.path.join(EXAMPLE_MODELS_FOLDER, 'classification_data.csv'), index=False
    )

    # Regression example (California Housing dataset)
    model, X_test_scaled, y_test, scaler = train_california_model()
    
    # Save model and data
    joblib.dump(model, os.path.join(EXAMPLE_MODELS_FOLDER, 'regression_model.pkl'))
    pd.concat([X_test_scaled, y_test], axis=1).to_csv(
        os.path.join(EXAMPLE_MODELS_FOLDER, 'regression_data.csv'), index=False
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

def run_shapash_app(explainer, port):
    """Run Shapash app in a separate thread"""
    global shapash_app
    try:
        shapash_app = explainer.launch_webapp(port=port)
        # The app is already running in a thread via SmartExplainer.run_app()
        # We don't need to do anything else
    except Exception as e:
        print(f"Error launching Shapash app: {str(e)}")
        raise

@app.route('/api/example/<model_type>', methods=['POST'])
def example_model(model_type):
    try:
        if model_type not in ['classification', 'regression']:
            return jsonify({'error': 'Invalid model type'}), 400
        
        model_path = os.path.join(EXAMPLE_MODELS_FOLDER, f'{model_type}_model.pkl')
        data_path = os.path.join(EXAMPLE_MODELS_FOLDER, f'{model_type}_data.csv')
        
        if not os.path.exists(model_path) or not os.path.exists(data_path):
            create_example_models()
        
        model_handler = ModelHandler(model_path)
        explainer = XAIExplainer(model_handler, data_path)
        
        # Start Shapash app in a separate thread
        global shapash_thread
        if shapash_thread is not None:
            # Stop previous instance if exists
            if shapash_app is not None:
                shapash_app.server.shutdown()
            shapash_thread.join()
        
        shapash_thread = threading.Thread(target=run_shapash_app, args=(explainer, 8050))
        shapash_thread.daemon = True
        shapash_thread.start()
        
        return jsonify({
            'message': 'Shapash visualization started',
            'url': 'http://localhost:8050'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_files():
    try:
        if 'model' not in request.files or 'dataset' not in request.files:
            return jsonify({'error': 'Missing files'}), 400
        
        model_file = request.files['model']
        dataset_file = request.files['dataset']
        
        if model_file.filename == '' or dataset_file.filename == '':
            return jsonify({'error': 'No selected files'}), 400
        
        if not (allowed_file(model_file.filename) and dataset_file.filename.endswith('.csv')):
            return jsonify({'error': 'Invalid file types'}), 400
        
        # Save files
        model_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(model_file.filename))
        dataset_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(dataset_file.filename))
        
        model_file.save(model_path)
        dataset_file.save(dataset_path)
        
        try:
            # Load and validate model
            model_handler = ModelHandler(model_path)
            explainer = XAIExplainer(model_handler, dataset_path)
            
            # Start Shapash app in a separate thread
            global shapash_thread
            if shapash_thread is not None:
                # Stop previous instance if exists
                if shapash_app is not None:
                    shapash_app.server.shutdown()
                shapash_thread.join()
            
            shapash_thread = threading.Thread(target=run_shapash_app, args=(explainer, 8050))
            shapash_thread.daemon = True
            shapash_thread.start()
            
            return jsonify({
                'message': 'Shapash visualization started',
                'url': 'http://localhost:8050'
            }), 200
            
        except Exception as e:
            # Clean up uploaded files if processing fails
            os.remove(model_path)
            os.remove(dataset_path)
            raise
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Create example models on startup
    create_example_models()
    app.run(debug=True, port=5000)
