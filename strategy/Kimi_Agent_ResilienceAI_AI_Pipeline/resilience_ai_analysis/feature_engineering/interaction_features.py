"""
Interaction Feature Engineering for ResilienceAI
Feature interactions and polynomial expansions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Set
from itertools import combinations

class InteractionFeatureEngineer:
    """
    Generate interaction features for disaster vulnerability analysis.
    """
    
    def __init__(self, max_interaction_degree: int = 2):
        self.max_interaction_degree = max_interaction_degree
    
    def compute_all_interaction_features(
        self,
        county_df: pd.DataFrame,
        feature_pairs: Optional[List[Tuple[str, str]]] = None
    ) -> pd.DataFrame:
        """
        Compute all interaction features for counties.
        
        Args:
            county_df: County features DataFrame
            feature_pairs: Optional list of feature pairs to interact
            
        Returns:
            County DataFrame with interaction features added
        """
        df = county_df.copy()
        
        print("Computing interaction features...")
        
        # Define default feature pairs if not provided
        if feature_pairs is None:
            feature_pairs = self._get_default_interaction_pairs(df)
        
        # Compute pairwise interactions
        df = self._compute_pairwise_interactions(df, feature_pairs)
        
        # Compute ratio features
        df = self._compute_ratio_features(df)
        
        # Compute compound interactions
        df = self._compute_compound_interactions(df)
        
        print(f"  Added {len([c for c in df.columns if 'x_' in c or 'ratio_' in c or 'compound_' in c])} interaction features")
        
        return df
    
    def _get_default_interaction_pairs(
        self,
        df: pd.DataFrame
    ) -> List[Tuple[str, str]]:
        """Get default feature pairs for interaction."""
        pairs = []
        
        # Vulnerability × Infrastructure interactions
        vulnerability_cols = ['vulnerability_index', 'poverty_pct', 'elderly_pct', 'disability_pct']
        infrastructure_cols = [
            'dist_nearest_hospitals_km', 'dist_nearest_ems_stations_km',
            'count_hospitals_50km', 'count_ems_stations_50km',
            'isolation_index', 'redundancy_score'
        ]
        
        for vuln_col in vulnerability_cols:
            if vuln_col in df.columns:
                for inf_col in infrastructure_cols:
                    if inf_col in df.columns:
                        pairs.append((vuln_col, inf_col))
        
        # Disaster × Demographic interactions
        disaster_cols = ['disaster_count', 'disaster_flood', 'disaster_severe_storm', 'disaster_fire']
        demographic_cols = ['poverty_pct', 'elderly_pct', 'uninsured_pct', 'total_population']
        
        for dis_col in disaster_cols:
            if dis_col in df.columns:
                for demo_col in demographic_cols:
                    if demo_col in df.columns:
                        pairs.append((dis_col, demo_col))
        
        # Risk × Context interactions
        if 'risk_score' in df.columns:
            context_cols = ['isolation_index', 'vulnerability_index', 'disaster_count']
            for ctx_col in context_cols:
                if ctx_col in df.columns and ctx_col != 'risk_score':
                    pairs.append(('risk_score', ctx_col))
        
        return pairs
    
    def _compute_pairwise_interactions(
        self,
        df: pd.DataFrame,
        feature_pairs: List[Tuple[str, str]]
    ) -> pd.DataFrame:
        """Compute pairwise interaction features."""
        
        for col1, col2 in feature_pairs:
            if col1 in df.columns and col2 in df.columns:
                # Multiplicative interaction
                interaction_name = f"x_{col1}_{col2}"
                df[interaction_name] = df[col1] * df[col2]
                
                # Additive interaction (for interpretability)
                additive_name = f"plus_{col1}_{col2}"
                df[additive_name] = df[col1] + df[col2]
        
        return df
    
    def _compute_ratio_features(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute ratio-based interaction features."""
        
        # Vulnerability to infrastructure ratio
        if 'vulnerability_index' in df.columns and 'isolation_index' in df.columns:
            df['ratio_vuln_to_isolation'] = df['vulnerability_index'] / (df['isolation_index'] + 0.01)
        
        # Disaster to infrastructure ratio
        if 'disaster_count' in df.columns and 'count_hospitals_50km' in df.columns:
            df['ratio_disaster_to_hospitals'] = df['disaster_count'] / (df['count_hospitals_50km'] + 1)
        
        # Population to facility ratio
        if 'total_population' in df.columns and 'count_hospitals_50km' in df.columns:
            df['ratio_pop_to_hospitals'] = df['total_population'] / (df['count_hospitals_50km'] + 1)
        
        # Poverty to healthcare access ratio
        if 'poverty_pct' in df.columns and 'dist_nearest_hospitals_km' in df.columns:
            df['ratio_poverty_to_hospital_dist'] = df['poverty_pct'] / (df['dist_nearest_hospitals_km'] + 1)
        
        # Elderly to facility ratio
        if 'elderly_pct' in df.columns and 'count_nursing_homes_50km' in df.columns:
            df['ratio_elderly_to_nursing'] = df['elderly_pct'] / (df['count_nursing_homes_50km'] + 1)
        
        # Disaster acceleration to preparedness gap
        if 'disaster_acceleration' in df.columns and 'redundancy_score' in df.columns:
            df['ratio_accel_to_redundancy'] = df['disaster_acceleration'] / (df['redundancy_score'] + 0.01)
        
        return df
    
    def _compute_compound_interactions(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute compound multi-way interaction features."""
        
        # Triple interaction: vulnerability × isolation × disaster
        if all(col in df.columns for col in ['vulnerability_index', 'isolation_index', 'disaster_count']):
            df['compound_vuln_iso_dis'] = (
                df['vulnerability_index'] * 
                df['isolation_index'] * 
                df['disaster_count']
            )
        
        # Infrastructure deficit interaction
        facility_count_cols = [c for c in df.columns if c.startswith('count_') and c.endswith('_50km')]
        if facility_count_cols:
            df['compound_infra_deficit'] = 1 / (df[facility_count_cols].sum(axis=1) + 1)
        
        # Social vulnerability amplification
        vuln_components = []
        for col in ['elderly_pct', 'poverty_pct', 'disability_pct', 'uninsured_pct']:
            if col in df.columns:
                # Normalize to 0-1
                vmin, vmax = df[col].min(), df[col].max()
                if vmax > vmin:
                    vuln_components.append((df[col] - vmin) / (vmax - vmin))
        
        if vuln_components:
            # Multiplicative amplification
            df['compound_sv_amplification'] = np.prod([1 + v for v in vuln_components], axis=0)
        
        # Risk contagion interaction
        if 'risk_score' in df.columns and 'neighbor_avg_risk' in df.columns:
            df['compound_risk_contagion'] = df['risk_score'] * df['neighbor_avg_risk']
        
        # Temporal × Spatial interaction
        if 'disaster_acceleration' in df.columns and 'spatial_moran_disaster' in df.columns:
            df['compound_temporal_spatial'] = df['disaster_acceleration'] * df['spatial_moran_disaster']
        
        # Population-weighted compound risk
        if all(col in df.columns for col in ['vulnerability_index', 'isolation_index', 'disaster_count', 'total_population']):
            df['compound_pop_weighted_risk'] = (
                df['vulnerability_index'] * 
                df['isolation_index'] * 
                df['disaster_count'] * 
                np.log1p(df['total_population'])
            )
        
        return df


class PolynomialFeatureEngineer:
    """
    Generate polynomial feature expansions.
    """
    
    def __init__(self, degree: int = 2):
        self.degree = degree
    
    def compute_polynomial_features(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Compute polynomial feature expansions.
        
        Args:
            df: DataFrame with features
            columns: Columns to expand (default: key numeric features)
            
        Returns:
            DataFrame with polynomial features added
        """
        df = df.copy()
        
        print("Computing polynomial features...")
        
        if columns is None:
            columns = self._get_default_polynomial_columns(df)
        
        for col in columns:
            if col in df.columns:
                # Quadratic term
                df[f"{col}_squared"] = df[col] ** 2
                
                # Cubic term
                if self.degree >= 3:
                    df[f"{col}_cubed"] = df[col] ** 3
                
                # Square root (for diminishing returns)
                if df[col].min() >= 0:
                    df[f"{col}_sqrt"] = np.sqrt(df[col])
                
                # Log transform (for skewed distributions)
                if df[col].min() >= 0:
                    df[f"{col}_log1p"] = np.log1p(df[col])
        
        print(f"  Added {len([c for c in df.columns if '_squared' in c or '_cubed' in c or '_sqrt' in c or '_log1p' in c])} polynomial features")
        
        return df
    
    def _get_default_polynomial_columns(
        self,
        df: pd.DataFrame
    ) -> List[str]:
        """Get default columns for polynomial expansion."""
        candidates = [
            'vulnerability_index',
            'isolation_index',
            'disaster_count',
            'poverty_pct',
            'elderly_pct',
            'risk_score'
        ]
        return [c for c in candidates if c in df.columns]


def add_interaction_features(
    county_df: pd.DataFrame,
    feature_pairs: Optional[List[Tuple[str, str]]] = None
) -> pd.DataFrame:
    """
    Convenience function to add all interaction features.
    
    Args:
        county_df: County features DataFrame
        feature_pairs: Optional list of feature pairs to interact
        
    Returns:
        DataFrame with interaction features added
    """
    engineer = InteractionFeatureEngineer()
    return engineer.compute_all_interaction_features(county_df, feature_pairs)


def add_polynomial_features(
    county_df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    degree: int = 2
) -> pd.DataFrame:
    """
    Convenience function to add polynomial features.
    
    Args:
        county_df: County features DataFrame
        columns: Columns to expand
        degree: Maximum polynomial degree
        
    Returns:
        DataFrame with polynomial features added
    """
    engineer = PolynomialFeatureEngineer(degree=degree)
    return engineer.compute_polynomial_features(county_df, columns)
