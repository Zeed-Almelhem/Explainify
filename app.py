from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from src.model_handler import ModelHandler
from src.explainer import XAIExplainer
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.datasets import load_iris, fetch_california_housing

app = Flask(__name__)
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
EXAMPLE_MODELS_FOLDER = os.path.join('static', 'example_models')
ALLOWED_EXTENSIONS = {'csv', 'pkl', 'h5', 'pt', 'pth'}

for folder in [UPLOAD_FOLDER, EXAMPLE_MODELS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_example_models():
    """Create and save example models if they don't exist"""
    # Always recreate clustering model due to previous version mismatch
    # Classification example (Iris dataset)
    if not os.path.exists(os.path.join(EXAMPLE_MODELS_FOLDER, 'classification_model.pkl')):
        iris = load_iris()
        X, y = iris.data, iris.target
        model = LogisticRegression(random_state=42)
        model.fit(X, y)
        joblib.dump(model, os.path.join(EXAMPLE_MODELS_FOLDER, 'classification_model.pkl'))
        pd.DataFrame(X, columns=iris.feature_names).assign(target=y).to_csv(
            os.path.join(EXAMPLE_MODELS_FOLDER, 'classification_data.csv'), index=False
        )

    # Regression example (California Housing dataset)
    if not os.path.exists(os.path.join(EXAMPLE_MODELS_FOLDER, 'regression_model.pkl')):
        housing = fetch_california_housing()
        X, y = housing.data, housing.target
        model = LinearRegression()
        model.fit(X, y)
        joblib.dump(model, os.path.join(EXAMPLE_MODELS_FOLDER, 'regression_model.pkl'))
        pd.DataFrame(X, columns=housing.feature_names).assign(target=y).to_csv(
            os.path.join(EXAMPLE_MODELS_FOLDER, 'regression_data.csv'), index=False
        )

    # Clustering example (synthetic data) - Always recreate
    np.random.seed(42)
    n_samples = 300
    X = np.concatenate([
        np.random.normal(0, 1, (n_samples, 2)),
        np.random.normal(4, 1.5, (n_samples, 2)),
        np.random.normal(-4, 1.2, (n_samples, 2))
    ])
    model = KMeans(n_clusters=3, random_state=42)
    model.fit(X)
    joblib.dump(model, os.path.join(EXAMPLE_MODELS_FOLDER, 'clustering_model.pkl'))
    pd.DataFrame(X, columns=['feature1', 'feature2']).to_csv(
        os.path.join(EXAMPLE_MODELS_FOLDER, 'clustering_data.csv'), index=False
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/example/<model_type>', methods=['POST'])
def example_model(model_type):
    try:
        if model_type not in ['classification', 'regression', 'clustering']:
            return jsonify({'error': 'Invalid model type'}), 400
        
        model_path = os.path.join(EXAMPLE_MODELS_FOLDER, f'{model_type}_model.pkl')
        data_path = os.path.join(EXAMPLE_MODELS_FOLDER, f'{model_type}_data.csv')
        
        # Always recreate clustering model
        if model_type == 'clustering':
            create_example_models()
        elif not os.path.exists(model_path) or not os.path.exists(data_path):
            create_example_models()
        
        model_handler = ModelHandler(model_path)
        explainer = XAIExplainer(model_handler, data_path)
        
        results = {
            'feature_importance': explainer.get_feature_importance(),
            'global_explanations': explainer.get_global_explanations(),
            'local_explanations': explainer.get_local_explanations(),
            'influential_samples': explainer.get_influential_samples()
        }
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_files():
    try:
        if 'dataset' not in request.files or 'model' not in request.files:
            return jsonify({'error': 'Missing required files'}), 400
        
        dataset = request.files['dataset']
        model_file = request.files['model']
        
        if dataset.filename == '' or model_file.filename == '':
            return jsonify({'error': 'No selected files'}), 400
        
        if not allowed_file(dataset.filename) or not allowed_file(model_file.filename):
            return jsonify({'error': 'Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400

        # Create upload folder if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # Save files with secure filenames
        dataset_filename = secure_filename(dataset.filename)
        model_filename = secure_filename(model_file.filename)
        
        dataset_path = os.path.join(app.config['UPLOAD_FOLDER'], dataset_filename)
        model_path = os.path.join(app.config['UPLOAD_FOLDER'], model_filename)
        
        try:
            dataset.save(dataset_path)
            model_file.save(model_path)
            
            # Validate dataset format
            try:
                data = pd.read_csv(dataset_path)
                if len(data.columns) < 2:
                    raise ValueError("Dataset must have at least 2 columns (features and target)")
            except Exception as e:
                raise ValueError(f"Error reading dataset: {str(e)}")
            
            # Load and validate model
            model_handler = ModelHandler(model_path)
            explainer = XAIExplainer(model_handler, dataset_path)
            
            results = {
                'feature_importance': explainer.get_feature_importance(),
                'global_explanations': explainer.get_global_explanations(),
                'local_explanations': explainer.get_local_explanations(),
                'influential_samples': explainer.get_influential_samples()
            }
            
            return jsonify(results), 200
            
        except Exception as e:
            # Clean up files if there was an error
            if os.path.exists(dataset_path):
                os.remove(dataset_path)
            if os.path.exists(model_path):
                os.remove(model_path)
            raise e
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Create example models on startup
    create_example_models()
    app.run(debug=True, port=5000)
