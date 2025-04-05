# XAI Explainify

An interactive web application for explaining machine learning models using various XAI (Explainable AI) techniques.

## Features

- Support for multiple ML frameworks (Scikit-learn, TensorFlow, PyTorch)
- Upload datasets (CSV) and trained models
- Generate visual explanations:
  - Feature importance analysis
  - Global model explanations
  - Local prediction explanations
  - Influential training samples identification
- Interactive visualizations using Plotly
- Modern UI with Tailwind CSS

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000/static/index.html`

## Supported File Formats

- Dataset: CSV files
- Models: 
  - Scikit-learn models (.pkl)
  - TensorFlow models (.h5)
  - PyTorch models (.pt, .pth)

## How to Use

1. Upload your dataset (CSV file)
2. Upload your trained model file
3. Click "Generate Explanations"
4. View the interactive visualizations for:
   - Feature importance
   - Global model behavior
   - Local prediction explanations
   - Influential training samples

**Note:** This code is kind of functional go back to in case of any new bugs.