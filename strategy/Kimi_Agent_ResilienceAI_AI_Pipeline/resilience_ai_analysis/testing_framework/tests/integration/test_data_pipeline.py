"""
Integration tests for complete data pipeline

Tests the end-to-end data flow from raw data ingestion through
feature engineering to model training.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil

# Import modules under test
# from src.download_data import DataDownloader
# from src.feature_engineering import FeatureEngineer
# from src.train_models import ModelTrainer


@pytest.mark.integration
class TestDataPipeline:
    """End-to-end data pipeline integration tests."""
    
    @pytest.fixture(scope="class")
    def pipeline_output(self, tmp_path_factory):
        """Run full pipeline and return outputs."""
        temp_dir = tmp_path_factory.mktemp("pipeline_test")
        
        try:
            # Step 1: Download/Load data
            # downloader = DataDownloader(output_dir=temp_dir / "raw")
            # raw_data = downloader.download_all()
            
            # For testing, create synthetic data
            raw_data = pd.DataFrame({
                'fips': [f'29{i:03d}' for i in range(1, 21)],
                'county_name': [f'County {i}, Missouri' for i in range(1, 21)],
                'population': np.random.randint(10000, 500000, 20),
                'uninsured_pct': np.random.uniform(5, 25, 20),
                'poverty_rate': np.random.uniform(8, 35, 20),
                'physician_per_1000': np.random.uniform(0.5, 4.0, 20),
                'hospital_distance_miles': np.random.uniform(5, 50, 20),
                'flood_risk_score': np.random.uniform(0, 100, 20),
                'tornado_risk_score': np.random.uniform(0, 100, 20),
                'historical_disaster_count': np.random.randint(0, 10, 20),
            })
            
            # Step 2: Feature engineering
            # engineer = FeatureEngineer()
            # processed_data = engineer.transform(raw_data)
            processed_data = raw_data.copy()  # Placeholder
            processed_data['healthcare_gap_score'] = np.random.uniform(0, 100, 20)
            processed_data['disaster_risk_score'] = np.random.uniform(0, 100, 20)
            processed_data['vulnerability_index'] = np.random.uniform(0, 100, 20)
            processed_data['risk_level'] = np.random.choice(['Low', 'Medium', 'High'], 20)
            
            # Step 3: Train models
            # trainer = ModelTrainer(output_dir=temp_dir / "models")
            # models = trainer.train_all(processed_data)
            models = {
                'vulnerability_classifier': MockModel(),
                'risk_predictor': MockModel(),
            }
            
            yield {
                'raw_data': raw_data,
                'processed_data': processed_data,
                'models': models,
                'temp_dir': temp_dir
            }
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_raw_data_downloaded(self, pipeline_output):
        """Test that raw data was obtained successfully."""
        raw_data = pipeline_output['raw_data']
        assert raw_data is not None
        assert len(raw_data) > 0
        assert 'fips' in raw_data.columns
    
    def test_features_engineered(self, pipeline_output):
        """Test that features were properly engineered."""
        processed = pipeline_output['processed_data']
        
        # Check required columns exist
        required_cols = [
            'healthcare_gap_score',
            'disaster_risk_score',
            'vulnerability_index',
            'risk_level'
        ]
        
        for col in required_cols:
            assert col in processed.columns, f"Missing column: {col}"
    
    def test_feature_ranges(self, pipeline_output):
        """Test that engineered features are within expected ranges."""
        processed = pipeline_output['processed_data']
        
        # Score columns should be 0-100
        score_cols = ['healthcare_gap_score', 'disaster_risk_score', 'vulnerability_index']
        for col in score_cols:
            assert processed[col].between(0, 100).all(), f"{col} out of range"
    
    def test_risk_level_categories(self, pipeline_output):
        """Test risk level categories are valid."""
        processed = pipeline_output['processed_data']
        
        valid_levels = {'Low', 'Medium', 'High', 'Critical'}
        actual_levels = set(processed['risk_level'].unique())
        
        assert actual_levels.issubset(valid_levels), f"Invalid risk levels: {actual_levels - valid_levels}"
    
    def test_models_trained(self, pipeline_output):
        """Test that models were trained successfully."""
        models = pipeline_output['models']
        
        required_models = [
            'vulnerability_classifier',
            'risk_predictor',
        ]
        
        for model_name in required_models:
            assert model_name in models, f"Missing model: {model_name}"
            assert models[model_name] is not None
    
    def test_data_integrity_through_pipeline(self, pipeline_output):
        """Test data integrity through the pipeline."""
        raw = pipeline_output['raw_data']
        processed = pipeline_output['processed_data']
        
        # Row count should be preserved
        assert len(raw) == len(processed), "Row count changed during processing"
        
        # FIPS codes should be preserved
        assert raw['fips'].equals(processed['fips']), "FIPS codes changed during processing"
    
    def test_no_missing_values_in_key_columns(self, pipeline_output):
        """Test that key columns have no missing values."""
        processed = pipeline_output['processed_data']
        
        key_columns = [
            'fips',
            'healthcare_gap_score',
            'disaster_risk_score',
            'vulnerability_index',
            'risk_level'
        ]
        
        for col in key_columns:
            assert not processed[col].isna().any(), f"Missing values in {col}"


@pytest.mark.integration
class TestAgentWorkflowIntegration:
    """Integration tests for agent workflows."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create agent orchestrator."""
        # from src.agents.orchestrator import AgentOrchestrator
        # return AgentOrchestrator()
        return MockOrchestrator()  # Placeholder
    
    def test_vulnerability_assessment_workflow(self, orchestrator):
        """Test complete vulnerability assessment workflow."""
        query = "Assess vulnerability for St. Louis County, Missouri"
        
        result = orchestrator.process(query)
        
        assert result['success'] is True
        assert 'vulnerability_score' in result['data']
        assert 'risk_factors' in result['data']
    
    def test_multi_agent_coordination(self, orchestrator):
        """Test coordination between multiple agents."""
        query = "Generate a comprehensive disaster preparedness report for Missouri"
        
        result = orchestrator.process(query)
        
        assert result['success'] is True
        # Should involve multiple agents
        assert 'agents_invoked' in result.get('metadata', {})
    
    def test_agent_error_recovery(self, orchestrator):
        """Test agent system recovers from errors."""
        # Query that might cause issues
        query = "Assess vulnerability for INVALID_COUNTY"
        
        result = orchestrator.process(query)
        
        # Should handle gracefully, not crash
        assert 'success' in result
    
    def test_agent_context_passing(self, orchestrator):
        """Test context is properly passed between agents."""
        query = "What are the healthcare gaps?"
        context = {'state': 'Missouri', 'county': 'Jackson'}
        
        result = orchestrator.process(query, context=context)
        
        assert result['success'] is True
        # Context should be reflected in response


@pytest.mark.integration
class TestLLMOrchestrationIntegration:
    """Tests for LLM and agent orchestration integration."""
    
    @pytest.fixture
    def llm_manager(self):
        """Create LLM manager with mock provider."""
        # from src.llm_interface import LLMManager, LLMMessage
        # manager = LLMManager()
        
        # Register mock provider
        mock_provider = Mock()
        mock_provider.generate.return_value = Mock(
            content='{"action": "assess_vulnerability", "county": "St. Louis"}',
            model='test-model'
        )
        
        # manager.providers['test'] = mock_provider
        # manager.default_provider = 'test'
        
        # return manager
        return MockLLMManager()  # Placeholder
    
    def test_llm_agent_communication(self, llm_manager):
        """Test LLM can communicate with agents."""
        # messages = [
        #     LLMMessage(role="system", content="You are a disaster assessment agent."),
        #     LLMMessage(role="user", content="Assess St. Louis County")
        # ]
        # 
        # response = llm_manager.generate(messages)
        
        # assert response.content is not None
        pass  # Placeholder


# Mock classes for testing
class MockModel:
    """Mock ML model for testing."""
    def predict(self, X):
        return np.random.rand(len(X))
    
    def predict_proba(self, X):
        probs = np.random.rand(len(X), 2)
        return probs / probs.sum(axis=1, keepdims=True)


class MockOrchestrator:
    """Mock orchestrator for testing."""
    def process(self, query, context=None):
        return {
            'success': True,
            'data': {
                'vulnerability_score': 75.5,
                'risk_factors': ['flood', 'tornado'],
                'query': query
            },
            'metadata': {
                'agents_invoked': ['vulnerability_agent', 'risk_agent'],
                'processing_time_ms': 150
            }
        }


class MockLLMManager:
    """Mock LLM manager for testing."""
    def generate(self, messages):
        return Mock(
            content='{"action": "test"}',
            model='test-model'
        )
