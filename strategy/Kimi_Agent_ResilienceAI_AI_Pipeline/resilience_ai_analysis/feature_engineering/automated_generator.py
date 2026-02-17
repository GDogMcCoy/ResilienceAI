"""
Automated Feature Generator for ResilienceAI
Automatically discovers and generates predictive features.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Callable
from sklearn.feature_selection import mutual_info_regression
from sklearn.preprocessing import PowerTransformer
from scipy import stats
import warnings

class AutoFeatureGenerator:
    """
    Automatically generate features based on data characteristics.
    
    Capabilities:
    - Automatic transformation detection
    - Feature interaction discovery
    - Statistical feature generation
    - Domain-specific feature templates
    """
    
    def __init__(
        self,
        max_features: int = 50,
        min_importance: float = 0.01,
        random_state: int = 42
    ):
        self.max_features = max_features
        self.min_importance = min_importance
        self.random_state = random_state
        self.generated_features: List[str] = []
    
    def generate(
        self,
        df: pd.DataFrame,
        target_col: Optional[str] = 'risk_score',
        numeric_cols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Automatically generate features for the dataset.
        
        Args:
            df: Input DataFrame
            target_col: Target variable for importance scoring
            numeric_cols: Numeric columns to use (default: all numeric)
            
        Returns:
            DataFrame with generated features added
        """
        df = df.copy()
        
        print("Running automated feature generation...")
        
        # Identify numeric columns
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            exclude = ['fips', target_col] if target_col else ['fips']
            numeric_cols = [c for c in numeric_cols if c not in exclude]
        
        # Generate transformation features
        df = self._generate_transformations(df, numeric_cols)
        
        # Generate aggregation features
        df = self._generate_aggregations(df, numeric_cols)
        
        # Generate statistical features
        df = self._generate_statistical_features(df, numeric_cols)
        
        # Generate domain-specific features
        df = self._generate_domain_features(df)
        
        # Select best features if target available
        if target_col and target_col in df.columns:
            df = self._select_best_features(df, target_col)
        
        print(f"  Total generated features: {len(self.generated_features)}")
        
        return df
    
    def _generate_transformations(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str]
    ) -> pd.DataFrame:
        """Generate transformation-based features."""
        
        for col in numeric_cols:
            if col not in df.columns:
                continue
            
            values = df[col].replace([np.inf, -np.inf], np.nan).fillna(0)
            
            # Box-Cox transformation (for positive values)
            if values.min() > 0:
                try:
                    transformed, _ = stats.boxcox(values + 0.01)
                    new_col = f"auto_boxcox_{col}"
                    df[new_col] = transformed
                    self.generated_features.append(new_col)
                except:
                    pass
            
            # Yeo-Johnson transformation
            try:
                pt = PowerTransformer(method='yeo-johnson')
                transformed = pt.fit_transform(values.values.reshape(-1, 1)).flatten()
                new_col = f"auto_yeojohnson_{col}"
                df[new_col] = transformed
                self.generated_features.append(new_col)
            except:
                pass
            
            # Rank transformation (robust to outliers)
            new_col = f"auto_rank_{col}"
            df[new_col] = values.rank(pct=True)
            self.generated_features.append(new_col)
            
            # Z-score normalization
            if values.std() > 0:
                new_col = f"auto_zscore_{col}"
                df[new_col] = (values - values.mean()) / values.std()
                self.generated_features.append(new_col)
            
            # Winsorization (cap outliers)
            new_col = f"auto_winsor_{col}"
            lower = values.quantile(0.01)
            upper = values.quantile(0.99)
            df[new_col] = values.clip(lower, upper)
            self.generated_features.append(new_col)
        
        return df
    
    def _generate_aggregations(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str]
    ) -> pd.DataFrame:
        """Generate aggregation-based features."""
        
        # Group-based aggregations (by state if available)
        if 'state_fips' in df.columns or 'fips' in df.columns:
            group_col = 'state_fips' if 'state_fips' in df.columns else df['fips'].str[:2]
            
            for col in numeric_cols[:5]:  # Limit to top 5 features
                if col not in df.columns:
                    continue
                
                # Group mean
                new_col = f"auto_grpmean_{col}"
                df[new_col] = df.groupby(group_col)[col].transform('mean')
                self.generated_features.append(new_col)
                
                # Group std
                new_col = f"auto_grpstd_{col}"
                df[new_col] = df.groupby(group_col)[col].transform('std')
                self.generated_features.append(new_col)
                
                # Deviation from group mean
                new_col = f"auto_grpdev_{col}"
                df[new_col] = df[col] - df.groupby(group_col)[col].transform('mean')
                self.generated_features.append(new_col)
                
                # Group percentile
                new_col = f"auto_grppct_{col}"
                df[new_col] = df.groupby(group_col)[col].rank(pct=True)
                self.generated_features.append(new_col)
        
        # Bin-based aggregations
        for col in numeric_cols[:3]:
            if col not in df.columns:
                continue
            
            # Quantile bins
            try:
                bins = pd.qcut(df[col].replace([np.inf, -np.inf], np.nan).fillna(0), q=5, labels=False, duplicates='drop')
                new_col = f"auto_qbin_{col}"
                df[new_col] = bins
                self.generated_features.append(new_col)
            except:
                pass
        
        return df
    
    def _generate_statistical_features(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str]
    ) -> pd.DataFrame:
        """Generate statistical features."""
        
        # Feature clusters (correlation-based)
        vulnerability_cols = [c for c in numeric_cols if any(x in c for x in ['vuln', 'poverty', 'elderly', 'disability'])]
        infrastructure_cols = [c for c in numeric_cols if any(x in c for x in ['dist', 'count', 'isolation', 'redundancy'])]
        disaster_cols = [c for c in numeric_cols if any(x in c for x in ['disaster', 'flood', 'storm', 'fire'])]
        
        # Cluster means
        if vulnerability_cols:
            new_col = "auto_vuln_cluster_mean"
            df[new_col] = df[vulnerability_cols].mean(axis=1)
            self.generated_features.append(new_col)
        
        if infrastructure_cols:
            new_col = "auto_infra_cluster_mean"
            df[new_col] = df[infrastructure_cols].mean(axis=1)
            self.generated_features.append(new_col)
        
        if disaster_cols:
            new_col = "auto_disaster_cluster_mean"
            df[new_col] = df[disaster_cols].mean(axis=1)
            self.generated_features.append(new_col)
        
        # Cluster stds (variability within cluster)
        if vulnerability_cols:
            new_col = "auto_vuln_cluster_std"
            df[new_col] = df[vulnerability_cols].std(axis=1)
            self.generated_features.append(new_col)
        
        # Outlier scores (distance from median)
        for col in numeric_cols[:3]:
            if col not in df.columns:
                continue
            
            median = df[col].median()
            mad = np.median(np.abs(df[col] - median))  # Median absolute deviation
            
            if mad > 0:
                new_col = f"auto_outlier_{col}"
                df[new_col] = np.abs(df[col] - median) / mad
                self.generated_features.append(new_col)
        
        # Entropy-based features (for diversity)
        facility_cols = [c for c in numeric_cols if c.startswith('count_') and c.endswith('_50km')]
        if len(facility_cols) >= 2:
            # Shannon entropy of facility distribution
            facility_counts = df[facility_cols].values + 1  # Add 1 to avoid log(0)
            facility_probs = facility_counts / facility_counts.sum(axis=1, keepdims=True)
            entropy = -np.sum(facility_probs * np.log(facility_probs), axis=1)
            
            new_col = "auto_facility_entropy"
            df[new_col] = entropy
            self.generated_features.append(new_col)
        
        return df
    
    def _generate_domain_features(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Generate domain-specific features for disaster vulnerability."""
        
        # Healthcare system pressure
        if all(c in df.columns for c in ['total_population', 'count_hospitals_50km', 'elderly_pct']):
            new_col = "auto_healthcare_pressure"
            vulnerable_pop = df['total_population'] * df['elderly_pct'] / 100
            df[new_col] = vulnerable_pop / (df['count_hospitals_50km'] + 1)
            self.generated_features.append(new_col)
        
        # Emergency response capacity
        if all(c in df.columns for c in ['count_ems_stations_50km', 'count_fire_stations_50km', 'total_population']):
            new_col = "auto_response_capacity"
            df[new_col] = (df['count_ems_stations_50km'] + df['count_fire_stations_50km']) / (df['total_population'] / 10000 + 1)
            self.generated_features.append(new_col)
        
        # Disaster resilience index
        if all(c in df.columns for c in ['disaster_count', 'redundancy_score', 'vulnerability_index']):
            new_col = "auto_resilience_index"
            exposure = df['disaster_count'] / (df['disaster_count'].max() + 1)
            capacity = df['redundancy_score']
            vulnerability = df['vulnerability_index']
            df[new_col] = (1 - exposure) * capacity * (1 - vulnerability)
            self.generated_features.append(new_col)
        
        # Risk exposure intensity
        if all(c in df.columns for c in ['disaster_count', 'disaster_acceleration', 'disaster_seasonality_cv']):
            new_col = "auto_risk_intensity"
            df[new_col] = df['disaster_count'] * (1 + df['disaster_acceleration']) * (1 + df['disaster_seasonality_cv'])
            self.generated_features.append(new_col)
        
        # Social capital proxy (inverse of vulnerability)
        if 'vulnerability_index' in df.columns:
            new_col = "auto_social_capital"
            df[new_col] = 1 - df['vulnerability_index']
            self.generated_features.append(new_col)
        
        # Infrastructure maturity (combination of density and redundancy)
        if all(c in df.columns for c in ['density_hospitals_per10k', 'redundancy_score']):
            new_col = "auto_infra_maturity"
            df[new_col] = df['density_hospitals_per10k'] * df['redundancy_score']
            self.generated_features.append(new_col)
        
        # Geographic risk concentration
        if 'spatial_moran_risk' in df.columns:
            new_col = "auto_risk_concentration"
            df[new_col] = np.abs(df['spatial_moran_risk'])
            self.generated_features.append(new_col)
        
        # Temporal risk trajectory
        if all(c in df.columns for c in ['disaster_acceleration', 'trend_slope']):
            new_col = "auto_risk_trajectory"
            df[new_col] = np.sign(df['trend_slope']) * np.log1p(np.abs(df['trend_slope'])) * df['disaster_acceleration']
            self.generated_features.append(new_col)
        
        return df
    
    def _select_best_features(
        self,
        df: pd.DataFrame,
        target_col: str
    ) -> pd.DataFrame:
        """Select best generated features based on mutual information."""
        
        if not self.generated_features:
            return df
        
        # Compute mutual information for generated features
        X = df[self.generated_features].fillna(0)
        y = df[target_col]
        
        try:
            mi_scores = mutual_info_regression(X, y, random_state=self.random_state)
            
            # Create feature importance dataframe
            feature_importance = pd.DataFrame({
                'feature': self.generated_features,
                'mutual_info': mi_scores
            }).sort_values('mutual_info', ascending=False)
            
            # Select top features
            top_features = feature_importance[
                feature_importance['mutual_info'] >= self.min_importance
            ]['feature'].tolist()[:self.max_features]
            
            # Keep only selected generated features
            features_to_drop = [f for f in self.generated_features if f not in top_features]
            df = df.drop(columns=features_to_drop)
            
            self.generated_features = top_features
            
            print(f"  Selected {len(top_features)} features by importance")
            
        except Exception as e:
            warnings.warn(f"Feature selection failed: {e}")
        
        return df


def auto_generate_features(
    df: pd.DataFrame,
    target_col: Optional[str] = 'risk_score',
    max_features: int = 50
) -> pd.DataFrame:
    """
    Convenience function for automatic feature generation.
    
    Args:
        df: Input DataFrame
        target_col: Target variable for importance scoring
        max_features: Maximum number of features to generate
        
    Returns:
        DataFrame with generated features
    """
    generator = AutoFeatureGenerator(max_features=max_features)
    return generator.generate(df, target_col)
