"""
Base class for XAI explainers.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Union

import numpy as np
from sklearn.base import BaseEstimator
import tensorflow as tf

from ...schemas.explanation import ExplanationRequest


class BaseExplainer(ABC):
    """Abstract base class for XAI explainers."""

    def __init__(self, name: str):
        """
        Initialize base explainer.

        Args:
            name: Name of the explainer
        """
        self.name = name

    @abstractmethod
    def explain(
        self,
        model: Union[BaseEstimator, tf.keras.Model],
        data: np.ndarray,
        request: ExplanationRequest,
    ) -> Dict[str, Any]:
        """
        Generate explanations for model predictions.

        Args:
            model: The trained model to explain
            data: Input data to explain
            request: ExplanationRequest containing parameters

        Returns:
            Dict containing explanation data
        """
        pass
