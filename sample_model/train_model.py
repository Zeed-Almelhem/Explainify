from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import pickle
import pandas as pd
import os

# Create the directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# Load and prepare the iris dataset
iris = load_iris()
X = iris.data
y = iris.target
feature_names = iris.feature_names

# Create a DataFrame with feature names
df = pd.DataFrame(X, columns=feature_names)
df['target'] = y

# Save the dataset
df.to_csv('models/iris_data.csv', index=False)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train RandomForest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Calculate accuracy
train_accuracy = model.score(X_train, y_train)
test_accuracy = model.score(X_test, y_test)

print("Random Forest Model:")
print(f"Train accuracy: {train_accuracy:.3f}")
print(f"Test accuracy: {test_accuracy:.3f}")

# Save the model in .pkl format
model_path = 'models/iris_classifier.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"\nModel saved to: {model_path}")

# Save feature names and target names for reference
model_info = {
    'feature_names': feature_names,
    'target_names': iris.target_names.tolist(),
    'model_type': 'RandomForestClassifier'
}
with open('models/model_info.pkl', 'wb') as f:
    pickle.dump(model_info, f)
print("Model info saved to: models/model_info.pkl")

# Create a sample input for testing
sample_input = X_test[0].reshape(1, -1)
sample_prediction = model.predict(sample_input)
print(f"\nSample prediction for input {sample_input[0]}:")
print(f"Predicted class: {iris.target_names[sample_prediction[0]]}")
