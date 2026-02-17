"""
Test data generation for load testing
"""

import json
import random
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class TestDataGenerator:
    """Generate realistic test data for ML API testing"""
    
    @staticmethod
    def generate_prediction_request(model_type: str = "tabular") -> Dict[str, Any]:
        """Generate a prediction request payload"""
        
        if model_type == "tabular":
            return {
                "model_id": f"model_{random.randint(1, 10)}",
                "features": {
                    f"feature_{i}": random.uniform(0, 100)
                    for i in range(1, 11)
                },
                "request_id": f"req_{random.randint(100000, 999999)}",
                "timestamp": random.randint(1609459200, 1704067200),
            }
        
        elif model_type == "image":
            return {
                "model_id": f"vision_model_{random.randint(1, 5)}",
                "image": "base64_encoded_image_data_placeholder",
                "preprocessing": {
                    "resize": [224, 224],
                    "normalize": True,
                },
                "request_id": f"req_{random.randint(100000, 999999)}",
            }
        
        elif model_type == "text":
            return {
                "model_id": f"nlp_model_{random.randint(1, 5)}",
                "text": random.choice([
                    "This is a sample text for classification",
                    "Another example of text input for NLP models",
                    "Machine learning provides powerful predictions",
                    "Load testing ensures system reliability",
                    "API performance is critical for user experience",
                ]),
                "task": random.choice(["classification", "sentiment", "ner"]),
                "request_id": f"req_{random.randint(100000, 999999)}",
            }
        
        elif model_type == "time_series":
            return {
                "model_id": f"ts_model_{random.randint(1, 5)}",
                "sequence": np.random.randn(100).tolist(),
                "window_size": 100,
                "forecast_horizon": random.randint(1, 30),
                "request_id": f"req_{random.randint(100000, 999999)}",
            }
        
        else:
            return TestDataGenerator.generate_prediction_request("tabular")
    
    @staticmethod
    def generate_batch_request(batch_size: int = 100) -> Dict[str, Any]:
        """Generate a batch prediction request"""
        return {
            "model_id": f"model_{random.randint(1, 10)}",
            "batch_id": f"batch_{random.randint(1000, 9999)}",
            "requests": [
                TestDataGenerator.generate_prediction_request()
                for _ in range(batch_size)
            ],
            "priority": random.choice(["low", "normal", "high"]),
            "callback_url": f"https://callback.example.com/batch/{random.randint(1000, 9999)}",
        }
    
    @staticmethod
    def generate_explanation_request() -> Dict[str, Any]:
        """Generate an explanation request"""
        return {
            "model_id": f"model_{random.randint(1, 10)}",
            "prediction_id": f"pred_{random.randint(100000, 999999)}",
            "method": random.choice(["shap", "lime", "integrated_gradients"]),
            "features": TestDataGenerator.generate_prediction_request()["features"],
            "top_k": random.randint(3, 10),
        }
    
    @staticmethod
    def generate_feedback_request() -> Dict[str, Any]:
        """Generate a feedback request"""
        return {
            "prediction_id": f"pred_{random.randint(100000, 999999)}",
            "actual_value": random.uniform(0, 100),
            "feedback_type": random.choice(["correction", "validation", "rejection"]),
            "metadata": {
                "user_id": f"user_{random.randint(1, 1000)}",
                "timestamp": random.randint(1609459200, 1704067200),
                "confidence": random.uniform(0, 1),
            },
        }
    
    @staticmethod
    def generate_model_deployment_request() -> Dict[str, Any]:
        """Generate a model deployment request"""
        return {
            "model_id": f"model_{random.randint(1, 10)}",
            "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "config": {
                "batch_size": random.choice([1, 8, 16, 32]),
                "device": random.choice(["cpu", "cuda:0"]),
                "precision": random.choice(["fp32", "fp16"]),
            },
            "preload": random.choice([True, False]),
        }
    
    @staticmethod
    def generate_health_check_request() -> Dict[str, Any]:
        """Generate a health check request"""
        return {
            "check_type": random.choice(["basic", "deep", "readiness", "liveness"]),
        }


# Pre-generated test data sets for reuse
TEST_DATA_SETS = {
    "small_tabular": [TestDataGenerator.generate_prediction_request("tabular") for _ in range(100)],
    "medium_tabular": [TestDataGenerator.generate_prediction_request("tabular") for _ in range(1000)],
    "large_tabular": [TestDataGenerator.generate_prediction_request("tabular") for _ in range(10000)],
    "text_samples": [TestDataGenerator.generate_prediction_request("text") for _ in range(100)],
    "batch_samples": [TestDataGenerator.generate_batch_request(random.randint(10, 100)) for _ in range(50)],
}
