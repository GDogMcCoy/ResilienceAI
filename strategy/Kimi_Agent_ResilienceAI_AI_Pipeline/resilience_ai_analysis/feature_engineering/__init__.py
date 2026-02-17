"""
ResilienceAI Feature Engineering Package

This package provides comprehensive feature engineering capabilities for
disaster vulnerability assessment and risk prediction.

Modules:
    - temporal_features: Time-based feature generation
    - geospatial_features: Spatial analysis features
    - interaction_features: Feature interactions and polynomials
    - automated_generator: Automatic feature discovery
    - feature_selector: Feature selection algorithms
    - feature_importance: Feature importance analysis
    - pca_reduction: Dimensionality reduction
    - feature_store: Centralized feature storage
    - enhanced_pipeline: Integrated feature engineering pipeline

Example Usage:
    >>> from feature_engineering import EnhancedFeaturePipeline
    >>> pipeline = EnhancedFeaturePipeline()
    >>> df = pipeline.run()
    
    >>> from feature_engineering import add_temporal_features
    >>> df = add_temporal_features(county_df, fema_df)
"""

# Core feature engineering functions
from .temporal_features import (
    TemporalFeatureEngineer,
    add_temporal_features
)

from .geospatial_features import (
    GeospatialFeatureEngineer,
    add_geospatial_features
)

from .interaction_features import (
    InteractionFeatureEngineer,
    PolynomialFeatureEngineer,
    add_interaction_features,
    add_polynomial_features
)

# Advanced feature generation
from .automated_generator import (
    AutoFeatureGenerator,
    auto_generate_features
)

# Feature selection and importance
from .feature_selector import (
    FeatureSelector,
    VarianceInflationFactorSelector,
    select_optimal_features
)

from .feature_importance import (
    FeatureImportanceAnalyzer,
    analyze_feature_importance
)

# Dimensionality reduction
from .pca_reduction import (
    PCAReducer,
    apply_pca_to_counties
)

# Feature store
from .feature_store import (
    FeatureStore,
    FeatureMetadata,
    FeatureLineage,
    FeatureType,
    FeatureStoreType,
    get_feature_store
)

# Enhanced pipeline
from .enhanced_pipeline import (
    EnhancedFeaturePipeline,
    run_enhanced_pipeline
)

__version__ = "2.0.0"

__all__ = [
    # Classes
    'TemporalFeatureEngineer',
    'GeospatialFeatureEngineer',
    'InteractionFeatureEngineer',
    'PolynomialFeatureEngineer',
    'AutoFeatureGenerator',
    'FeatureSelector',
    'VarianceInflationFactorSelector',
    'FeatureImportanceAnalyzer',
    'PCAReducer',
    'FeatureStore',
    'FeatureMetadata',
    'FeatureLineage',
    'EnhancedFeaturePipeline',
    
    # Functions
    'add_temporal_features',
    'add_geospatial_features',
    'add_interaction_features',
    'add_polynomial_features',
    'auto_generate_features',
    'select_optimal_features',
    'analyze_feature_importance',
    'apply_pca_to_counties',
    'get_feature_store',
    'run_enhanced_pipeline',
    
    # Enums
    'FeatureType',
    'FeatureStoreType',
    
    # Version
    '__version__'
]
