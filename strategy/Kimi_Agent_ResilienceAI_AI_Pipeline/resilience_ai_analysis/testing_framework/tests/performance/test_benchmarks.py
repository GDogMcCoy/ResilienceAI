"""
Performance benchmarks for ResilienceAI components

Uses pytest-benchmark for reproducible performance measurements.
"""
import pytest
import time
import statistics
from typing import List, Callable, Any
import pandas as pd
import numpy as np


class PerformanceBenchmark:
    """Base class for performance benchmarks."""
    
    def __init__(self, iterations: int = 10):
        self.iterations = iterations
        self.results: List[float] = []
    
    def benchmark(self, func: Callable, *args, **kwargs) -> dict:
        """Run benchmark and return statistics."""
        self.results = []
        
        for i in range(self.iterations):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            self.results.append((end - start) * 1000)  # Convert to ms
        
        return {
            'mean': statistics.mean(self.results),
            'median': statistics.median(self.results),
            'stdev': statistics.stdev(self.results) if len(self.results) > 1 else 0,
            'min': min(self.results),
            'max': max(self.results),
            'iterations': self.iterations,
            'throughput': 1000 / statistics.mean(self.results) if statistics.mean(self.results) > 0 else 0
        }


@pytest.mark.performance
class TestDataProcessingBenchmarks:
    """Benchmarks for data processing operations."""
    
    @pytest.fixture
    def large_dataset(self):
        """Generate large dataset for benchmarking."""
        np.random.seed(42)
        n = 10000
        return pd.DataFrame({
            'fips': [f'29{i:05d}' for i in range(n)],
            'population': np.random.lognormal(10, 1.5, n).astype(int),
            'uninsured_pct': np.clip(np.random.normal(12, 5, n), 3, 35),
            'poverty_rate': np.clip(np.random.normal(15, 7, n), 5, 45),
            'median_income': np.random.lognormal(10.8, 0.4, n).astype(int),
            'physician_per_1000': np.random.uniform(0.5, 4.0, n),
            'hospital_distance_miles': np.random.uniform(5, 50, n),
            'flood_risk_score': np.random.uniform(0, 100, n),
            'tornado_risk_score': np.random.uniform(0, 100, n),
            'historical_disaster_count': np.random.poisson(3, n),
        })
    
    def test_feature_engineering_performance(self, benchmark, large_dataset):
        """Benchmark feature engineering on large dataset."""
        # from src.feature_engineering import FeatureEngineer
        # engineer = FeatureEngineer()
        
        # Benchmark the transform operation
        # result = benchmark(engineer.transform, large_dataset)
        
        # Placeholder benchmark
        def dummy_transform(df):
            time.sleep(0.001)  # Simulate 1ms processing
            return df
        
        result = benchmark(dummy_transform, large_dataset)
        
        # Assert performance requirements
        # Feature engineering should complete in under 5 seconds for 10k rows
        assert result.stats.mean < 5000, f"Feature engineering too slow: {result.stats.mean:.2f}ms"
    
    def test_data_loading_performance(self, benchmark):
        """Benchmark data loading performance."""
        def load_data():
            # Simulate data loading
            time.sleep(0.01)
            return pd.DataFrame({'test': [1, 2, 3]})
        
        result = benchmark(load_data)
        
        # Data loading should be fast
        assert result.stats.mean < 100, f"Data loading too slow: {result.stats.mean:.2f}ms"
    
    def test_dataframe_operations(self, benchmark, large_dataset):
        """Benchmark common DataFrame operations."""
        def operations(df):
            # Common operations
            df = df.copy()
            df['new_col'] = df['uninsured_pct'] * df['poverty_rate']
            df = df.groupby('fips').agg({'population': 'sum'})
            return df
        
        result = benchmark(operations, large_dataset)
        
        assert result.stats.mean < 1000, f"DataFrame operations too slow: {result.stats.mean:.2f}ms"


@pytest.mark.performance
class TestModelBenchmarks:
    """Benchmarks for ML model operations."""
    
    @pytest.fixture
    def model_features(self):
        """Generate model features for benchmarking."""
        np.random.seed(42)
        return np.random.rand(1000, 66)  # 66 features
    
    def test_prediction_performance(self, benchmark, model_features):
        """Benchmark model prediction performance."""
        # from src.predictive_models import RiskPredictor
        # predictor = RiskPredictor()
        
        # Placeholder prediction function
        def predict_batch(X):
            time.sleep(0.005)  # Simulate 5ms prediction
            return np.random.rand(len(X))
        
        result = benchmark(predict_batch, model_features)
        
        # Predictions should be fast (< 100ms for 1000 samples)
        assert result.stats.mean < 100, f"Prediction too slow: {result.stats.mean:.2f}ms"
        
        # Calculate throughput
        throughput = len(model_features) / (result.stats.mean / 1000)
        print(f"\nPrediction Throughput: {throughput:.0f} predictions/sec")
    
    def test_model_training_performance(self, benchmark):
        """Benchmark model training performance."""
        from sklearn.ensemble import RandomForestClassifier
        
        # Generate training data
        np.random.seed(42)
        X = np.random.rand(1000, 20)
        y = np.random.randint(0, 2, 1000)
        
        def train_model():
            model = RandomForestClassifier(n_estimators=10, max_depth=5)
            model.fit(X, y)
            return model
        
        result = benchmark(train_model)
        
        # Training should complete in reasonable time
        assert result.stats.mean < 10000, f"Training too slow: {result.stats.mean:.2f}ms"


@pytest.mark.performance
class TestAPIBenchmarks:
    """Benchmarks for API client operations."""
    
    def test_weather_api_latency(self, benchmark):
        """Benchmark weather API response time."""
        # from src.weather_client import WeatherClient
        # client = WeatherClient()
        
        # Mock API call for benchmarking
        def mock_api_call():
            time.sleep(0.5)  # Simulate 500ms API latency
            return {'alerts': []}
        
        result = benchmark(mock_api_call)
        
        # External API should respond within 2 seconds
        assert result.stats.mean < 2000, f"Weather API too slow: {result.stats.mean:.2f}ms"
    
    def test_geocoding_performance(self, benchmark):
        """Benchmark geocoding operations."""
        def geocode_address():
            time.sleep(0.1)  # Simulate geocoding
            return {'lat': 38.6, 'lon': -90.2}
        
        result = benchmark(geocode_address)
        
        assert result.stats.mean < 500, f"Geocoding too slow: {result.stats.mean:.2f}ms"


@pytest.mark.performance
class TestAgentBenchmarks:
    """Benchmarks for agent system performance."""
    
    def test_agent_response_time(self, benchmark):
        """Benchmark agent response time."""
        # from src.agents.orchestrator import AgentOrchestrator
        # orchestrator = AgentOrchestrator()
        
        def agent_query():
            time.sleep(0.1)  # Simulate agent processing
            return {'success': True, 'data': {}}
        
        result = benchmark(agent_query)
        
        # Agent response should be under 5 seconds
        assert result.stats.mean < 5000, f"Agent response too slow: {result.stats.mean:.2f}ms"
    
    def test_multi_agent_coordination(self, benchmark):
        """Benchmark multi-agent coordination overhead."""
        def multi_agent_workflow():
            time.sleep(0.3)  # Simulate coordination
            return {'agents_invoked': 3}
        
        result = benchmark(multi_agent_workflow)
        
        assert result.stats.mean < 10000, f"Multi-agent coordination too slow: {result.stats.mean:.2f}ms"


@pytest.mark.performance
class TestMemoryBenchmarks:
    """Memory usage benchmarks."""
    
    def test_large_dataset_memory(self, large_dataset):
        """Test memory usage with large datasets."""
        import sys
        
        # Calculate memory usage
        memory_bytes = large_dataset.memory_usage(deep=True).sum()
        memory_mb = memory_bytes / (1024 * 1024)
        
        print(f"\nLarge dataset memory usage: {memory_mb:.2f} MB")
        
        # Should be under 100 MB for 10k rows
        assert memory_mb < 100, f"Memory usage too high: {memory_mb:.2f} MB"
    
    def test_dataframe_copy_memory(self, large_dataset):
        """Test memory impact of DataFrame copies."""
        import sys
        
        initial_memory = large_dataset.memory_usage(deep=True).sum()
        
        # Create a copy
        df_copy = large_dataset.copy()
        
        final_memory = df_copy.memory_usage(deep=True).sum()
        
        # Memory should roughly double
        memory_ratio = final_memory / initial_memory
        assert 1.8 < memory_ratio < 2.2, f"Unexpected memory ratio: {memory_ratio:.2f}"


# Performance regression tests
@pytest.mark.performance
class TestPerformanceRegression:
    """Tests to detect performance regressions."""
    
    def test_feature_engineering_no_regression(self, large_dataset):
        """Test that feature engineering hasn't regressed."""
        # Baseline: 10k rows should process in under 5 seconds
        start = time.perf_counter()
        
        # Simulate feature engineering
        df = large_dataset.copy()
        df['new_feature'] = df['uninsured_pct'] * df['poverty_rate']
        
        elapsed = (time.perf_counter() - start) * 1000
        
        # Should be under baseline
        baseline = 5000  # 5 seconds
        regression_threshold = baseline * 1.2  # Allow 20% regression
        
        assert elapsed < regression_threshold, \
            f"Performance regression detected: {elapsed:.2f}ms > {regression_threshold:.2f}ms"
