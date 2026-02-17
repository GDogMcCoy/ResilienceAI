"""
ResilienceAI - Vector Space Tests

Comprehensive test suite for the hyperdimensional vector space module.
Tests encoding, indexing, similarity search, and cross-domain analysis.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil

# Test subjects
from src.vector_space import (
    CountyVectorEncoder, CountyVectorIndex, CrossDomainAnalyzer,
    VectorSpaceManager, VectorSearchResult, CrossDomainInsight,
    DOMAIN_FEATURES, create_vector_space
)


class TestCountyVectorEncoder(unittest.TestCase):
    """Test the CountyVectorEncoder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.encoder = CountyVectorEncoder()
        
        # Create sample county data
        self.sample_df = pd.DataFrame({
            'fips': ['01001', '01003', '01005'],
            'county_name': ['Autauga County, Alabama', 'Baldwin County, Alabama', 'Barbour County, Alabama'],
            'total_population': [58761, 233420, 24877],
            'median_income': [68315, 71039, 39712],
            'poverty_pct': [11.28, 10.04, 21.22],
            'elderly_pct': [15.62, 21.21, 19.8],
            'disability_pct': [16.04, 13.66, 15.96],
            'uninsured_pct': [7.36, 9.33, 10.73],
            'disaster_count': [24, 38, 28],
            'disaster_flood': [2, 2, 1],
            'disaster_hurricane': [11, 23, 11],
            'dist_nearest_hospitals_km': [22.89, 16.79, 27.73],
            'density_hospitals_per10k': [1.36, 0.47, 0.80],
            'vulnerability_index': [0.218, 0.233, 0.294],
            'risk_score': [0.23, 0.311, 0.330],
            'redundancy_score': [0.997, 0.998, 0.996]
        })
    
    def test_initialization(self):
        """Test encoder initialization."""
        self.assertEqual(self.encoder.model_name, "all-MiniLM-L6-v2")
        self.assertEqual(self.encoder.embedding_dim, 384)
    
    def test_create_text_description(self):
        """Test text description generation."""
        row = self.sample_df.iloc[0]
        text = self.encoder._create_text_description(row)
        
        self.assertIn("Autauga County", text)
        self.assertIn("disasters", text.lower())
        self.assertIn("hospital", text.lower())
        self.assertIn("population", text.lower())
    
    def test_create_domain_specific_description(self):
        """Test domain-specific description generation."""
        row = self.sample_df.iloc[0]
        
        climate_text = self.encoder._create_text_description(row, domain="climate")
        self.assertIn("disasters", climate_text.lower())
        self.assertNotIn("hospital", climate_text.lower())
        
        health_text = self.encoder._create_text_description(row, domain="health")
        self.assertIn("hospital", health_text.lower())
        self.assertNotIn("disasters", health_text.lower())
    
    def test_encode_county(self):
        """Test single county encoding."""
        row = self.sample_df.iloc[0]
        embedding = self.encoder.encode_county(row)
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (384,))
        self.assertEqual(embedding.dtype, np.float32)
    
    def test_encode_counties(self):
        """Test batch county encoding."""
        embeddings = self.encoder.encode_counties(self.sample_df)
        
        self.assertIsInstance(embeddings, np.ndarray)
        self.assertEqual(embeddings.shape, (3, 384))
        self.assertEqual(embeddings.dtype, np.float32)
    
    def test_encode_domain_specific(self):
        """Test domain-specific encoding."""
        domain_embeddings = self.encoder.encode_domain_specific(self.sample_df)
        
        self.assertIn("climate", domain_embeddings)
        self.assertIn("health", domain_embeddings)
        self.assertIn("infrastructure", domain_embeddings)
        self.assertIn("socioeconomic", domain_embeddings)
        
        for domain, embeddings in domain_embeddings.items():
            self.assertEqual(embeddings.shape, (3, 384))


class TestCountyVectorIndex(unittest.TestCase):
    """Test the CountyVectorIndex class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.index = CountyVectorIndex(embedding_dim=384, metric="cosine")
        
        # Create sample vectors
        np.random.seed(42)
        self.vectors = np.random.randn(10, 384).astype(np.float32)
        self.fips = [f"{i:05d}" for i in range(10)]
        self.names = [f"County {i}" for i in range(10)]
    
    def test_initialization(self):
        """Test index initialization."""
        self.assertEqual(self.index.embedding_dim, 384)
        self.assertEqual(self.index.metric, "cosine")
        self.assertFalse(self.index.is_built)
    
    def test_build_index(self):
        """Test index building."""
        self.index.build_index(self.vectors, self.fips, self.names)
        
        self.assertTrue(self.index.is_built)
        self.assertEqual(len(self.index.county_fips), 10)
        np.testing.assert_array_equal(self.index.vectors, self.vectors)
    
    def test_search(self):
        """Test similarity search."""
        self.index.build_index(self.vectors, self.fips, self.names)
        
        # Search with first vector
        query = self.vectors[0]
        results = self.index.search(query, k=5)
        
        self.assertEqual(len(results), 5)
        self.assertIsInstance(results[0], VectorSearchResult)
        
        # First result should be the query itself
        self.assertEqual(results[0].county_fips, self.fips[0])
        self.assertAlmostEqual(results[0].similarity_score, 1.0, places=5)
    
    def test_search_by_fips(self):
        """Test search by FIPS code."""
        self.index.build_index(self.vectors, self.fips, self.names)
        
        results = self.index.search_by_fips(self.fips[0], k=5)
        
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0].county_fips, self.fips[0])
    
    def test_search_invalid_fips(self):
        """Test search with invalid FIPS."""
        self.index.build_index(self.vectors, self.fips, self.names)
        
        with self.assertRaises(ValueError):
            self.index.search_by_fips("99999")
    
    def test_save_load(self):
        """Test index save and load."""
        self.index.build_index(self.vectors, self.fips, self.names)
        
        # Save to temp directory
        temp_dir = tempfile.mkdtemp()
        try:
            self.index.save(temp_dir)
            
            # Load
            loaded_index = CountyVectorIndex.load(temp_dir)
            
            self.assertTrue(loaded_index.is_built)
            self.assertEqual(loaded_index.embedding_dim, 384)
            np.testing.assert_array_equal(loaded_index.vectors, self.vectors)
            self.assertEqual(loaded_index.county_fips, self.fips)
        finally:
            shutil.rmtree(temp_dir)


class TestCrossDomainAnalyzer(unittest.TestCase):
    """Test the CrossDomainAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.encoder = CountyVectorEncoder()
        
        # Create sample county data with all required features
        self.sample_df = pd.DataFrame({
            'fips': [f"{i:05d}" for i in range(20)],
            'county_name': [f"County {i}" for i in range(20)],
            'total_population': np.random.randint(10000, 500000, 20),
            'median_income': np.random.randint(30000, 100000, 20),
            'poverty_pct': np.random.uniform(5, 30, 20),
            'elderly_pct': np.random.uniform(10, 25, 20),
            'disability_pct': np.random.uniform(10, 20, 20),
            'uninsured_pct': np.random.uniform(5, 15, 20),
            'disaster_count': np.random.randint(0, 50, 20),
            'disaster_flood': np.random.randint(0, 10, 20),
            'disaster_severe_storms': np.random.randint(0, 10, 20),
            'disaster_hurricane': np.random.randint(0, 20, 20),
            'disaster_fire': np.random.randint(0, 5, 20),
            'disaster_tornado': np.random.randint(0, 5, 20),
            'disaster_count_recent': np.random.randint(0, 20, 20),
            'disasters_2015_2025': np.random.randint(0, 20, 20),
            'disasters_2005_2014': np.random.randint(0, 20, 20),
            'disaster_acceleration': np.random.uniform(0, 2, 20),
            'dist_nearest_hospitals_km': np.random.uniform(5, 50, 20),
            'dist_2nd_nearest_hospitals_km': np.random.uniform(10, 80, 20),
            'count_hospitals_50km': np.random.randint(0, 20, 20),
            'density_hospitals_per10k': np.random.uniform(0, 5, 20),
            'dist_nearest_nursing_homes_km': np.random.uniform(5, 50, 20),
            'density_nursing_homes_per10k': np.random.uniform(0, 3, 20),
            'dist_nearest_fire_stations_km': np.random.uniform(1, 20, 20),
            'dist_2nd_nearest_fire_stations_km': np.random.uniform(2, 30, 20),
            'count_fire_stations_50km': np.random.randint(10, 100, 20),
            'density_fire_stations_per10k': np.random.uniform(1, 20, 20),
            'dist_nearest_ems_stations_km': np.random.uniform(10, 60, 20),
            'dist_2nd_nearest_ems_stations_km': np.random.uniform(20, 100, 20),
            'count_ems_stations_50km': np.random.randint(0, 10, 20),
            'density_ems_stations_per10k': np.random.uniform(0, 2, 20),
            'redundancy_score': np.random.uniform(0.9, 1.0, 20),
            'zero_redundancy_flag': np.random.randint(0, 2, 20),
            'vulnerability_index': np.random.uniform(0.1, 0.4, 20),
            'isolation_index': np.random.uniform(0, 0.01, 20),
            'risk_score': np.random.uniform(0.1, 0.5, 20),
            'pop_weighted_vulnerability': np.random.uniform(1000, 50000, 20),
            'pop_weighted_risk': np.random.uniform(1000, 50000, 20)
        })
        
        self.analyzer = CrossDomainAnalyzer(self.encoder)
    
    def test_fit(self):
        """Test fitting the analyzer."""
        self.analyzer.fit(self.sample_df)
        
        self.assertIsNotNone(self.analyzer.df)
        self.assertEqual(len(self.analyzer.domain_embeddings), 4)
        
        for domain in DOMAIN_FEATURES.keys():
            self.assertIn(domain, self.analyzer.domain_embeddings)
            self.assertIn(domain, self.analyzer.domain_indices)
    
    def test_compute_cross_domain_similarity(self):
        """Test cross-domain similarity computation."""
        self.analyzer.fit(self.sample_df)
        
        fips = self.sample_df.iloc[0]['fips']
        similarities = self.analyzer.compute_cross_domain_similarity(fips)
        
        self.assertIn("climate", similarities)
        self.assertIn("health", similarities)
        
        # Diagonal should be 1.0
        for domain in similarities:
            self.assertAlmostEqual(similarities[domain][domain], 1.0, places=5)
    
    def test_compute_similarity_matrix(self):
        """Test similarity matrix computation."""
        self.analyzer.fit(self.sample_df)
        
        sim_matrix = self.analyzer.compute_similarity_matrix()
        
        self.assertEqual(len(sim_matrix), 20)
        self.assertIn('avg_cross_domain_similarity', sim_matrix.columns)
        self.assertIn('cross_domain_coherence', sim_matrix.columns)
    
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        self.analyzer.fit(self.sample_df)
        
        anomalies = self.analyzer.detect_anomalies(contamination=0.1)
        
        self.assertEqual(len(anomalies), 20)
        self.assertIn('anomaly_score', anomalies.columns)
        self.assertIn('is_anomaly', anomalies.columns)
        
        # Should have some anomalies
        self.assertTrue(anomalies['is_anomaly'].sum() > 0)
    
    def test_find_similar_multi_domain(self):
        """Test multi-domain similarity search."""
        self.analyzer.fit(self.sample_df)
        
        fips = self.sample_df.iloc[0]['fips']
        similar = self.analyzer.find_similar_multi_domain(fips, k=5)
        
        self.assertEqual(len(similar), 5)
        self.assertIn('similarity_score', similar.columns)
        
        # Should not include self
        self.assertNotIn(fips, similar['fips'].values)
    
    def test_discover_correlations(self):
        """Test correlation discovery."""
        self.analyzer.fit(self.sample_df)
        
        insights = self.analyzer.discover_correlations(top_n=5)
        
        self.assertGreater(len(insights), 0)
        self.assertIsInstance(insights[0], CrossDomainInsight)


class TestVectorSpaceManager(unittest.TestCase):
    """Test the VectorSpaceManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample county data
        self.sample_df = pd.DataFrame({
            'fips': [f"{i:05d}" for i in range(50)],
            'county_name': [f"County {i}" for i in range(50)],
            'total_population': np.random.randint(10000, 500000, 50),
            'median_income': np.random.randint(30000, 100000, 50),
            'poverty_pct': np.random.uniform(5, 30, 50),
            'elderly_pct': np.random.uniform(10, 25, 50),
            'disability_pct': np.random.uniform(10, 20, 50),
            'uninsured_pct': np.random.uniform(5, 15, 50),
            'disaster_count': np.random.randint(0, 50, 50),
            'disaster_flood': np.random.randint(0, 10, 50),
            'disaster_severe_storms': np.random.randint(0, 10, 50),
            'disaster_hurricane': np.random.randint(0, 20, 50),
            'disaster_fire': np.random.randint(0, 5, 50),
            'disaster_tornado': np.random.randint(0, 5, 50),
            'disaster_count_recent': np.random.randint(0, 20, 50),
            'disasters_2015_2025': np.random.randint(0, 20, 50),
            'disasters_2005_2014': np.random.randint(0, 20, 50),
            'disaster_acceleration': np.random.uniform(0, 2, 50),
            'dist_nearest_hospitals_km': np.random.uniform(5, 50, 50),
            'dist_2nd_nearest_hospitals_km': np.random.uniform(10, 80, 50),
            'count_hospitals_50km': np.random.randint(0, 20, 50),
            'density_hospitals_per10k': np.random.uniform(0, 5, 50),
            'dist_nearest_nursing_homes_km': np.random.uniform(5, 50, 50),
            'density_nursing_homes_per10k': np.random.uniform(0, 3, 50),
            'dist_nearest_fire_stations_km': np.random.uniform(1, 20, 50),
            'dist_2nd_nearest_fire_stations_km': np.random.uniform(2, 30, 50),
            'count_fire_stations_50km': np.random.randint(10, 100, 50),
            'density_fire_stations_per10k': np.random.uniform(1, 20, 50),
            'dist_nearest_ems_stations_km': np.random.uniform(10, 60, 50),
            'dist_2nd_nearest_ems_stations_km': np.random.uniform(20, 100, 50),
            'count_ems_stations_50km': np.random.randint(0, 10, 50),
            'density_ems_stations_per10k': np.random.uniform(0, 2, 50),
            'redundancy_score': np.random.uniform(0.9, 1.0, 50),
            'zero_redundancy_flag': np.random.randint(0, 2, 50),
            'vulnerability_index': np.random.uniform(0.1, 0.4, 50),
            'isolation_index': np.random.uniform(0, 0.01, 50),
            'risk_score': np.random.uniform(0.1, 0.5, 50),
            'pop_weighted_vulnerability': np.random.uniform(1000, 50000, 50),
            'pop_weighted_risk': np.random.uniform(1000, 50000, 50)
        })
        
        self.manager = VectorSpaceManager()
    
    def test_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager.encoder)
        self.assertIsNone(self.manager.index)
        self.assertIsNone(self.manager.analyzer)
    
    def test_build(self):
        """Test building the vector space."""
        self.manager.build(self.sample_df, build_domains=True)
        
        self.assertIsNotNone(self.manager.index)
        self.assertIsNotNone(self.manager.analyzer)
        self.assertIsNotNone(self.manager.embeddings)
        self.assertEqual(self.manager.embeddings.shape, (50, 384))
    
    def test_search_similar_by_fips(self):
        """Test similarity search by FIPS."""
        self.manager.build(self.sample_df, build_domains=True)
        
        fips = self.sample_df.iloc[0]['fips']
        results = self.manager.search_similar(fips, k=10)
        
        self.assertEqual(len(results), 10)
        self.assertIn('similarity_score', results.columns)
        self.assertIn('county_name', results.columns)
    
    def test_get_anomalies(self):
        """Test getting anomalies."""
        self.manager.build(self.sample_df, build_domains=True)
        
        anomalies = self.manager.get_anomalies(contamination=0.05)
        
        self.assertEqual(len(anomalies), 50)
        self.assertIn('anomaly_score', anomalies.columns)
    
    def test_get_insights(self):
        """Test getting insights."""
        self.manager.build(self.sample_df, build_domains=True)
        
        insights = self.manager.get_insights(top_n=5)
        
        self.assertGreater(len(insights), 0)
        self.assertIsInstance(insights[0], CrossDomainInsight)
    
    def test_save_load(self):
        """Test save and load."""
        self.manager.build(self.sample_df, build_domains=False)
        
        temp_dir = tempfile.mkdtemp()
        try:
            self.manager.save(temp_dir)
            
            loaded = VectorSpaceManager.load(temp_dir)
            
            self.assertIsNotNone(loaded.index)
            self.assertIsNotNone(loaded.df)
            np.testing.assert_array_equal(loaded.embeddings, self.manager.embeddings)
        finally:
            shutil.rmtree(temp_dir)


class TestDomainFeatures(unittest.TestCase):
    """Test domain feature definitions."""
    
    def test_domain_features_structure(self):
        """Test that domain features are properly defined."""
        self.assertIn("climate", DOMAIN_FEATURES)
        self.assertIn("health", DOMAIN_FEATURES)
        self.assertIn("infrastructure", DOMAIN_FEATURES)
        self.assertIn("socioeconomic", DOMAIN_FEATURES)
    
    def test_domain_features_non_empty(self):
        """Test that each domain has features."""
        for domain, features in DOMAIN_FEATURES.items():
            self.assertGreater(len(features), 0, f"{domain} has no features")


class TestIntegration(unittest.TestCase):
    """Integration tests with real data."""
    
    @unittest.skipUnless(
        (PROCESSED_DIR / "county_features.csv").exists(),
        "County features data not available"
    )
    def test_with_real_data(self):
        """Test with actual county data."""
        df = pd.read_csv(PROCESSED_DIR / "county_features.csv")
        
        # Use subset for faster testing
        df = df.head(100)
        
        manager = VectorSpaceManager()
        manager.build(df, build_domains=True)
        
        # Test search
        fips = df.iloc[0]['fips']
        results = manager.search_similar(fips, k=10)
        self.assertEqual(len(results), 10)
        
        # Test anomalies
        anomalies = manager.get_anomalies(contamination=0.05)
        self.assertEqual(len(anomalies), len(df))
        
        # Test insights
        insights = manager.get_insights(top_n=5)
        self.assertGreater(len(insights), 0)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCountyVectorEncoder))
    suite.addTests(loader.loadTestsFromTestCase(TestCountyVectorIndex))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossDomainAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorSpaceManager))
    suite.addTests(loader.loadTestsFromTestCase(TestDomainFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
