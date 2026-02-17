"""
Main Locust load test file for ResilienceAI
"""

from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import json
import random
import time
from typing import Dict, Any

# Test data generators
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
        }
    return {}


def generate_batch_request(batch_size: int = 10) -> Dict[str, Any]:
    """Generate a batch prediction request"""
    return {
        "model_id": f"model_{random.randint(1, 10)}",
        "batch_id": f"batch_{random.randint(1000, 9999)}",
        "requests": [
            generate_prediction_request()
            for _ in range(batch_size)
        ],
        "priority": random.choice(["low", "normal", "high"]),
    }


class APIConsumer(HttpUser):
    """
    Simulates a typical API consumer making prediction requests
    """
    wait_time = between(1, 5)
    weight = 50
    
    def on_start(self):
        """Initialize user session"""
        self.model_ids = [f"model_{i}" for i in range(1, 11)]
        self.request_count = 0
    
    @task(60)
    def predict(self):
        """Make a prediction request"""
        payload = generate_prediction_request()
        
        with self.client.post(
            "/api/v1/predict",
            json=payload,
            catch_response=True,
            timeout=30
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Predict failed: {response.status_code}")
        
        self.request_count += 1
    
    @task(20)
    def explain_prediction(self):
        """Request prediction explanation"""
        payload = {
            "model_id": random.choice(self.model_ids),
            "prediction_id": f"pred_{random.randint(100000, 999999)}",
            "method": random.choice(["shap", "lime"]),
            "features": generate_prediction_request()["features"],
        }
        
        with self.client.post(
            "/api/v1/explain",
            json=payload,
            catch_response=True,
            timeout=30
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.success()  # Explanation is optional
    
    @task(20)
    def health_check(self):
        """Perform health check"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


class BatchProcessor(HttpUser):
    """
    Simulates batch processing users
    """
    wait_time = between(10, 30)
    weight = 25
    
    def on_start(self):
        self.model_ids = [f"model_{i}" for i in range(1, 11)]
    
    @task(80)
    def batch_predict(self):
        """Submit batch prediction job"""
        payload = generate_batch_request(batch_size=random.randint(5, 50))
        
        with self.client.post(
            "/api/v1/batch-predict",
            json=payload,
            catch_response=True,
            timeout=120
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Batch predict failed: {response.status_code}")
    
    @task(20)
    def list_models(self):
        """List available models"""
        with self.client.get("/api/v1/models", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"List models failed: {response.status_code}")


class ModelManager(HttpUser):
    """
    Simulates model management operations
    """
    wait_time = between(5, 15)
    weight = 15
    
    def on_start(self):
        self.model_ids = [f"model_{i}" for i in range(1, 11)]
    
    @task(40)
    def get_model_info(self):
        """Get model information"""
        model_id = random.choice(self.model_ids)
        
        with self.client.get(
            f"/api/v1/models/{model_id}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Get model failed: {response.status_code}")
    
    @task(30)
    def list_models(self):
        """List all models"""
        with self.client.get("/api/v1/models", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"List models failed: {response.status_code}")
    
    @task(20)
    def deploy_model(self):
        """Deploy a model"""
        model_id = random.choice(self.model_ids)
        payload = {
            "model_id": model_id,
            "version": f"1.{random.randint(0, 9)}.{random.randint(0, 9)}",
        }
        
        with self.client.post(
            f"/api/v1/models/{model_id}/deploy",
            json=payload,
            catch_response=True,
            timeout=60
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.success()  # Deploy is infrequent
    
    @task(10)
    def get_metrics(self):
        """Get system metrics"""
        with self.client.get("/api/v1/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.success()  # Metrics are optional


class FeedbackUser(HttpUser):
    """
    Simulates users submitting feedback
    """
    wait_time = between(3, 10)
    weight = 10
    
    @task(100)
    def submit_feedback(self):
        """Submit prediction feedback"""
        payload = {
            "prediction_id": f"pred_{random.randint(100000, 999999)}",
            "actual_value": random.uniform(0, 100),
            "feedback_type": random.choice(["correction", "validation"]),
            "metadata": {
                "user_id": f"user_{random.randint(1, 1000)}",
                "confidence": random.uniform(0, 1),
            },
        }
        
        with self.client.post(
            "/api/v1/feedback",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.success()  # Feedback is best-effort


# Event handlers
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print(f"Load test starting at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target host: {environment.host}")
    
    if isinstance(environment.runner, MasterRunner):
        print("Running as master node")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print(f"Load test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if isinstance(environment.runner, MasterRunner):
        print("Master node test completed")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, 
               response, context, exception, **kwargs):
    """Called on each request"""
    # Log slow requests
    if response_time > 5000:
        print(f"SLOW REQUEST: {name} took {response_time}ms")
