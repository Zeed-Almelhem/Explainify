"""
Test script to verify XAI libraries are working correctly.
Tests LIME explanations on both scikit-learn and TensorFlow models.
"""

import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import lime
from lime import lime_tabular
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

def test_sklearn_explanations():
    """Test LIME with a scikit-learn model."""
    print("\nTesting scikit-learn model explanations...")
    
    # Load and prepare data
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )

    # Train a random forest model
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    # Test LIME
    print("\nTesting LIME...")
    lime_explainer = lime_tabular.LimeTabularExplainer(
        X_train,
        feature_names=iris.feature_names,
        class_names=iris.target_names,
        mode='classification'
    )
    lime_exp = lime_explainer.explain_instance(X_test[0], rf.predict_proba)
    print("LIME explanation features:", len(lime_exp.as_list()))
    print("LIME top features:", lime_exp.as_list()[:2])
    
    # Test edge case with single feature
    print("\nTesting LIME with single feature...")
    single_feature = X_test[0].reshape(1, -1)[:, :1]
    lime_exp_single = lime_explainer.explain_instance(X_test[0], rf.predict_proba, num_features=1)
    print("LIME single feature:", lime_exp_single.as_list()[:1])
    
    # Test failure case with invalid input
    print("\nTesting LIME with invalid input...")
    try:
        invalid_input = np.array([1, 2])  # Wrong shape
        lime_explainer.explain_instance(invalid_input, rf.predict_proba)
        print("Should have raised an error!")
    except:
        print("Successfully caught error for invalid input")

def test_tensorflow_explanations():
    """Test LIME with a TensorFlow model."""
    print("\nTesting TensorFlow model explanations...")
    
    # Load and prepare data
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    
    # Convert to one-hot encoding for tensorflow
    y_train_one_hot = tf.keras.utils.to_categorical(y_train)
    y_test_one_hot = tf.keras.utils.to_categorical(y_test)
    
    # Create and train a simple neural network
    model = Sequential([
        Dense(10, activation='relu', input_shape=(4,)),
        Dense(3, activation='softmax')
    ])
    
    model.compile(optimizer='adam',
                 loss='categorical_crossentropy',
                 metrics=['accuracy'])
    
    model.fit(X_train, y_train_one_hot, epochs=50, batch_size=32, verbose=0)
    
    # Test LIME with TensorFlow model
    print("\nTesting LIME with TensorFlow...")
    lime_explainer = lime_tabular.LimeTabularExplainer(
        X_train,
        feature_names=iris.feature_names,
        class_names=iris.target_names,
        mode='classification'
    )
    lime_exp = lime_explainer.explain_instance(
        X_test[0], 
        lambda x: model.predict(x.reshape(-1, 4))
    )
    print("LIME explanation features for TensorFlow:", len(lime_exp.as_list()))
    print("LIME top features for TensorFlow:", lime_exp.as_list()[:2])
    
    # Test edge case with all features
    print("\nTesting LIME with all features...")
    lime_exp_all = lime_explainer.explain_instance(
        X_test[0],
        lambda x: model.predict(x.reshape(-1, 4)),
        num_features=len(iris.feature_names)
    )
    print("LIME all features:", len(lime_exp_all.as_list()))
    
    # Test failure case with wrong input shape
    print("\nTesting LIME with wrong input shape...")
    try:
        wrong_shape = X_test[0].reshape(2, 2)  # Wrong shape
        lime_explainer.explain_instance(
            wrong_shape,
            lambda x: model.predict(x.reshape(-1, 4))
        )
        print("Should have raised an error!")
    except:
        print("Successfully caught error for wrong input shape")

if __name__ == "__main__":
    print("Testing XAI libraries integration...")
    test_sklearn_explanations()
    test_tensorflow_explanations()
    print("\nAll tests completed!")
