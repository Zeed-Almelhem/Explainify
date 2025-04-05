from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import joblib
import os

# Create a sample directory if it doesn't exist
sample_dir = 'sample_upload'
if not os.path.exists(sample_dir):
    os.makedirs(sample_dir)

# Load iris dataset
iris = load_iris()
X = iris.data
y = iris.target

# Create a pandas DataFrame
df = pd.DataFrame(X, columns=iris.feature_names)
df['target'] = y

# Save the dataset
df.to_csv(os.path.join(sample_dir, 'iris_data.csv'), index=False)

# Train a random forest model
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X, y)

# Save the model
joblib.dump(model, os.path.join(sample_dir, 'iris_model.pkl'))

print("Created sample model and dataset in the 'sample_upload' directory.")
print("You can upload:")
print("1. iris_data.csv - Dataset")
print("2. iris_model.pkl - Model file")
