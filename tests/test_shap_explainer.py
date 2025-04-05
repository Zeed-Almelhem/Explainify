"""
Tests for SHAP explainer.
"""
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
import tensorflow as tf

from app.core.xai.shap_explainer import SHAPExplainer
from app.schemas.explanation import ExplanationRequest, ExplanationFormat


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    X, y = make_classification(
        n_samples=100,
        n_features=5,
        n_informative=3,
        n_redundant=2,
        random_state=42
    )
    feature_names = [f"feature_{i}" for i in range(X.shape[1])]
    target_names = ["class_0", "class_1"]
    return X, y, feature_names, target_names


@pytest.fixture
def sklearn_model(sample_data):
    """Create and fit a sample sklearn model."""
    X, y, _, _ = sample_data
    model = LogisticRegression(random_state=42)
    model.fit(X, y)
    return model


@pytest.fixture
def tf_model(sample_data):
    """Create and fit a sample TensorFlow model."""
    X, y, _, _ = sample_data
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(10, activation='relu', input_shape=(X.shape[1],)),
        tf.keras.layers.Dense(2, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
    model.fit(X, y, epochs=1, verbose=0)
    return model


def test_feature_importance_sklearn(sample_data, sklearn_model):
    """Test feature importance for sklearn models."""
    X, _, feature_names, target_names = sample_data
    explainer = SHAPExplainer()
    request = ExplanationRequest(
        format=ExplanationFormat.FEATURE_IMPORTANCE,
        feature_names=feature_names,
        target_names=target_names
    )
    
    explanation = explainer.explain(sklearn_model, X, request)
    
    assert explanation["method"] == "shap"
    assert explanation["type"] == "feature_importance"
    assert set(explanation["feature_names"]) == set(feature_names)
    assert set(explanation["target_names"]) == set(target_names)
    assert isinstance(explanation["explanation"]["feature_importances"], dict)
    assert set(explanation["explanation"]["feature_importances"].keys()) == set(feature_names)


def test_instance_explanation_sklearn(sample_data, sklearn_model):
    """Test instance-level explanations for sklearn models."""
    X, _, feature_names, target_names = sample_data
    explainer = SHAPExplainer()
    request = ExplanationRequest(
        format=ExplanationFormat.INSTANCE,
        feature_names=feature_names,
        target_names=target_names
    )
    
    explanation = explainer.explain(sklearn_model, X[:1], request)  # Test with single instance
    
    assert explanation["method"] == "shap"
    assert explanation["type"] == "instance"
    assert set(explanation["feature_names"]) == set(feature_names)
    assert set(explanation["target_names"]) == set(target_names)
    assert "shap_values" in explanation["explanation"]
    assert "expected_value" in explanation["explanation"]
    assert len(explanation["explanation"]["shap_values"]) == len(feature_names)


def test_feature_importance_tensorflow(sample_data, tf_model):
    """Test feature importance for TensorFlow models."""
    X, _, feature_names, target_names = sample_data
    explainer = SHAPExplainer()
    request = ExplanationRequest(
        format=ExplanationFormat.FEATURE_IMPORTANCE,
        feature_names=feature_names,
        target_names=target_names
    )
    
    explanation = explainer.explain(tf_model, X, request)
    
    assert explanation["method"] == "shap"
    assert explanation["type"] == "feature_importance"
    assert set(explanation["feature_names"]) == set(feature_names)
    assert set(explanation["target_names"]) == set(target_names)
    assert isinstance(explanation["explanation"]["feature_importances"], dict)
    assert set(explanation["explanation"]["feature_importances"].keys()) == set(feature_names)


def test_instance_explanation_tensorflow(sample_data, tf_model):
    """Test instance-level explanations for TensorFlow models."""
    X, _, feature_names, target_names = sample_data
    explainer = SHAPExplainer()
    request = ExplanationRequest(
        format=ExplanationFormat.INSTANCE,
        feature_names=feature_names,
        target_names=target_names
    )
    
    explanation = explainer.explain(tf_model, X[:1], request)  # Test with single instance
    
    assert explanation["method"] == "shap"
    assert explanation["type"] == "instance"
    assert set(explanation["feature_names"]) == set(feature_names)
    assert set(explanation["target_names"]) == set(target_names)
    assert "shap_values" in explanation["explanation"]
    assert "expected_value" in explanation["explanation"]
    assert len(explanation["explanation"]["shap_values"]) == len(feature_names)


def test_invalid_model_type():
    """Test error handling for invalid model types."""
    explainer = SHAPExplainer()
    request = ExplanationRequest(
        format=ExplanationFormat.FEATURE_IMPORTANCE,
        feature_names=["f1"],
        target_names=["class_0"]
    )
    
    with pytest.raises(ValueError):
        explainer.explain("not_a_model", np.array([[1]]), request)
