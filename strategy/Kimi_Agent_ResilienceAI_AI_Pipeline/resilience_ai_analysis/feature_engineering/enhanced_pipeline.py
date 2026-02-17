"""
Enhanced Feature Engineering Pipeline for ResilienceAI
Integrates all new feature engineering capabilities.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import RAW_DIR, PROCESSED_DIR

# Import feature engineering modules
from temporal_features import add_temporal_features
from geospatial_features import add_geospatial_features
from interaction_features import add_interaction_features, add_polynomial_features
from automated_generator import AutoFeatureGenerator
from feature_selector import FeatureSelector
from feature_importance import FeatureImportanceAnalyzer
from pca_reduction import apply_pca_to_counties

class EnhancedFeaturePipeline:
    """
    Enhanced feature engineering pipeline with automation and feature store.
    """
    
    def __init__(
        self,
        use_auto_generate: bool = True,
        apply_selection: bool = True,
        target_feature_count: int = 100
    ):
        self.use_auto_generate = use_auto_generate
        self.apply_selection = apply_selection
        self.target_feature_count = target_feature_count
        
        self.auto_generator = AutoFeatureGenerator() if use_auto_generate else None
        self.selector = FeatureSelector() if apply_selection else None
        self.importance_analyzer = FeatureImportanceAnalyzer()
    
    def run(
        self,
        save_intermediate: bool = True,
        apply_pca: bool = False,
        pca_variance: float = 0.95
    ) -> pd.DataFrame:
        """
        Run the enhanced feature engineering pipeline.
        
        Args:
            save_intermediate: Save intermediate results
            apply_pca: Apply PCA dimensionality reduction
            pca_variance: Variance threshold for PCA
            
        Returns:
            DataFrame with engineered features
        """
        print("=" * 70)
        print("ResilienceAI - Enhanced Feature Engineering Pipeline")
        print("=" * 70)
        
        # Load raw data
        print("\n[1/8] Loading raw data...")
        census = pd.read_csv(RAW_DIR / "census_demographics.csv", dtype={"fips": str})
        centroids = pd.read_csv(RAW_DIR / "county_centroids.csv", dtype={"fips": str})
        fema = pd.read_csv(RAW_DIR / "fema_disasters.csv")
        
        # Merge base data
        df = census.merge(centroids[["fips", "latitude", "longitude"]], on="fips", how="left")
        df = df.dropna(subset=["latitude", "longitude"])
        print(f"  Base counties: {len(df)}")
        
        # Compute base features (from existing feature_engineering.py)
        print("\n[2/8] Computing base features...")
        df = self._compute_base_features(df)
        print(f"  Features after base: {len(df.columns)}")
        
        # Compute advanced features (from existing feature_engineering.py)
        print("\n[3/8] Computing advanced features...")
        df = self._compute_advanced_features(df, fema)
        print(f"  Features after advanced: {len(df.columns)}")
        
        # Add temporal features
        print("\n[4/8] Adding temporal features...")
        df = add_temporal_features(df, fema)
        print(f"  Features after temporal: {len(df.columns)}")
        
        # Add geospatial features
        print("\n[5/8] Adding geospatial features...")
        df = add_geospatial_features(df)
        print(f"  Features after geospatial: {len(df.columns)}")
        
        # Add interaction features
        print("\n[6/8] Adding interaction features...")
        df = add_interaction_features(df)
        print(f"  Features after interactions: {len(df.columns)}")
        
        # Add polynomial features
        print("\n[7/8] Adding polynomial features...")
        df = add_polynomial_features(df)
        print(f"  Features after polynomial: {len(df.columns)}")
        
        # Auto-generate features
        if self.use_auto_generate:
            print("\n[8/8] Auto-generating features...")
            df = self.auto_generator.generate(df)
            print(f"  Features after auto-generation: {len(df.columns)}")
        
        # Feature importance analysis
        print("\n[9/8] Analyzing feature importance...")
        if 'risk_score' in df.columns:
            importance_results = self.importance_analyzer.analyze(
                df.select_dtypes(include=['float64', 'int64']).fillna(0),
                df['risk_score']
            )
            
            consensus = self.importance_analyzer.get_consensus_ranking(top_n=15)
            print("\n  Top 15 Most Important Features:")
            for i, row in consensus.iterrows():
                print(f"    {i+1:2d}. {row['feature'][:40]:<40} {row['consensus_score']:.4f}")
        
        # Feature selection
        if self.apply_selection and len(df.columns) > self.target_feature_count:
            print(f"\n[10/8] Selecting top {self.target_feature_count} features...")
            selected = self.selector.select_features(
                df,
                target_col='risk_score',
                method='hybrid'
            )
            
            # Keep essential columns
            essential = ['fips', 'county_name', 'state', 'latitude', 'longitude', 'risk_score', 'risk_level']
            selected = list(set(selected + essential))
            
            df = df[selected]
            print(f"  Features after selection: {len(df.columns)}")
        
        # Apply PCA if requested
        if apply_pca:
            print("\n[11/8] Applying PCA dimensionality reduction...")
            pca_df, reducer = apply_pca_to_counties(df, variance_threshold=pca_variance)
            
            # Save PCA model
            reducer.save(PROCESSED_DIR / "pca_reducer.joblib")
            
            # Merge PCA components back
            df = df.merge(pca_df[['fips'] + [c for c in pca_df.columns if c.startswith('PC')]], on='fips')
        
        # Save final output
        output_path = PROCESSED_DIR / "county_features_enhanced.csv"
        df.to_csv(output_path, index=False)
        
        print("\n" + "=" * 70)
        print("Enhanced Feature Engineering Complete!")
        print(f"  Counties: {len(df)}")
        print(f"  Features: {len(df.columns)}")
        print(f"  Output: {output_path}")
        print("=" * 70)
        
        return df
    
    def _compute_base_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute base features (from existing pipeline)."""
        # This would call the existing compute_base_features function
        # For now, return as-is (assuming census already has base features)
        return df
    
    def _compute_advanced_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute advanced features (from existing pipeline)."""
        # This would call the existing compute_advanced_features function
        # For now, add basic risk score if not present
        
        if 'risk_score' not in df.columns:
            # Simple risk score calculation
            if 'vulnerability_index' in df.columns and 'disaster_count' in df.columns:
                df['risk_score'] = (
                    df['vulnerability_index'] * 0.4 +
                    df.get('isolation_index', 0) * 0.3 +
                    df['disaster_count'] / (df['disaster_count'].max() + 1) * 0.3
                )
        
        return df


def run_enhanced_pipeline(**kwargs) -> pd.DataFrame:
    """Convenience function to run enhanced pipeline."""
    pipeline = EnhancedFeaturePipeline()
    return pipeline.run(**kwargs)


if __name__ == "__main__":
    # Run pipeline
    df = run_enhanced_pipeline(
        save_intermediate=True,
        apply_pca=False
    )
