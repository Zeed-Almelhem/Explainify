# Explainify
Explainify is an XAI tool that reveals how machine learning models make decisions. Upload your data and model to get interactive visual explanations, feature importance, and the top training examples that influenced each prediction.

## Features
- Support for multiple ML frameworks (scikit-learn, XGBoost, TensorFlow)
- Multiple XAI techniques (SHAP, LIME, ELI5, Alibi, InterpretML)
- Asynchronous explanation generation for large models
- RESTful API for easy integration
- Visual explanations and feature importance analysis

## Setup

### Prerequisites
- Python 3.8+
- Redis server
- Virtual environment (recommended)

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/explainify.git
cd explainify
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (create a .env file):
```bash
DATABASE_URL=sqlite:///./explainify.db
REDIS_URL=redis://localhost:6379/0
MODEL_STORAGE_PATH=./storage/models
DATASET_STORAGE_PATH=./storage/datasets
```

### Running the Application
1. Start Redis server
2. Start Celery worker:
```bash
celery -A app.core.celery_app worker --loglevel=info
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000
API documentation: http://localhost:8000/docs

## API Usage

### Upload a Model
```bash
curl -X POST "http://localhost:8000/api/v1/models/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "model_file=@model.joblib" \
  -F "model_type=sklearn"
```

### Generate Explanations
```bash
curl -X POST "http://localhost:8000/api/v1/explanations/explain" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "model.joblib",
    "data_id": "test_data",
    "instance_index": 0,
    "methods": ["shap", "lime"]
  }'
```

## License
MIT License
