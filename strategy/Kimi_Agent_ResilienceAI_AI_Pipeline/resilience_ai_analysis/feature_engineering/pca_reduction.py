"""
PCA Dimensionality Reduction for ResilienceAI
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import joblib

class PCAReducer:
    """
    PCA-based dimensionality reduction with feature store integration.
    """
    
    def __init__(self, n_components: Optional[int] = None, variance_threshold: float = 0.95):
        """
        Initialize PCA reducer.
        
        Args:
            n_components: Number of components (None for auto-selection)
            variance_threshold: Minimum cumulative variance to retain
        """
        self.n_components = n_components
        self.variance_threshold = variance_threshold
        self.pca: Optional[PCA] = None
        self.scaler = StandardScaler()
        self.feature_names: Optional[List[str]] = None
    
    def fit(self, X: pd.DataFrame) -> 'PCAReducer':
        """
        Fit PCA on training data.
        
        Args:
            X: Feature matrix (numeric only)
            
        Returns:
            Self for method chaining
        """
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Standardize
        X_scaled = self.scaler.fit_transform(X)
        
        # Determine number of components
        if self.n_components is None:
            # Fit full PCA first to determine components
            pca_full = PCA()
            pca_full.fit(X_scaled)
            
            # Find number of components for variance threshold
            cumsum = np.cumsum(pca_full.explained_variance_ratio_)
            self.n_components = np.argmax(cumsum >= self.variance_threshold) + 1
            print(f"Auto-selected {self.n_components} components for {self.variance_threshold:.0%} variance")
        
        # Fit final PCA
        self.pca = PCA(n_components=self.n_components)
        self.pca.fit(X_scaled)
        
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data using fitted PCA.
        
        Args:
            X: Feature matrix
            
        Returns:
            Transformed data with principal components
        """
        if self.pca is None:
            raise ValueError("PCA not fitted. Call fit() first.")
        
        # Ensure same columns
        if self.feature_names:
            X = X[self.feature_names]
        
        # Standardize and transform
        X_scaled = self.scaler.transform(X)
        X_pca = self.pca.transform(X_scaled)
        
        # Create DataFrame
        columns = [f'PC{i+1}' for i in range(self.n_components)]
        return pd.DataFrame(X_pca, columns=columns, index=X.index)
    
    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform in one step."""
        return self.fit(X).transform(X)
    
    def get_explained_variance(self) -> pd.DataFrame:
        """Get explained variance by component."""
        if self.pca is None:
            raise ValueError("PCA not fitted.")
        
        return pd.DataFrame({
            'component': [f'PC{i+1}' for i in range(self.n_components)],
            'explained_variance_ratio': self.pca.explained_variance_ratio_,
            'cumulative_variance_ratio': np.cumsum(self.pca.explained_variance_ratio_)
        })
    
    def get_feature_loadings(self, n_components: Optional[int] = None) -> pd.DataFrame:
        """
        Get feature loadings (contributions) for each component.
        
        Args:
            n_components: Number of components to include
            
        Returns:
            DataFrame with feature loadings
        """
        if self.pca is None:
            raise ValueError("PCA not fitted.")
        
        n = n_components or self.n_components
        
        loadings = pd.DataFrame(
            self.pca.components_[:n].T,
            columns=[f'PC{i+1}' for i in range(n)],
            index=self.feature_names
        )
        
        return loadings
    
    def get_top_features_per_component(
        self,
        component: int = 0,
        n_features: int = 10
    ) -> pd.DataFrame:
        """
        Get top contributing features for a component.
        
        Args:
            component: Component index (0-based)
            n_features: Number of top features to return
            
        Returns:
            DataFrame with top features and their loadings
        """
        loadings = self.get_feature_loadings(n_components=component + 1)
        pc_col = f'PC{component + 1}'
        
        top = loadings[pc_col].abs().sort_values(ascending=False).head(n_features)
        
        return pd.DataFrame({
            'feature': top.index,
            'loading': loadings.loc[top.index, pc_col],
            'abs_loading': top.values
        })
    
    def inverse_transform(self, X_pca: pd.DataFrame) -> pd.DataFrame:
        """Transform PCA components back to original feature space."""
        if self.pca is None:
            raise ValueError("PCA not fitted.")
        
        X_recovered = self.pca.inverse_transform(X_pca)
        X_unscaled = self.scaler.inverse_transform(X_recovered)
        
        return pd.DataFrame(X_unscaled, columns=self.feature_names, index=X_pca.index)
    
    def save(self, path: str):
        """Save fitted PCA to disk."""
        joblib.dump({
            'pca': self.pca,
            'scaler': self.scaler,
            'n_components': self.n_components,
            'variance_threshold': self.variance_threshold,
            'feature_names': self.feature_names
        }, path)
    
    def load(self, path: str) -> 'PCAReducer':
        """Load fitted PCA from disk."""
        data = joblib.load(path)
        self.pca = data['pca']
        self.scaler = data['scaler']
        self.n_components = data['n_components']
        self.variance_threshold = data['variance_threshold']
        self.feature_names = data['feature_names']
        return self


def apply_pca_to_counties(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
    n_components: Optional[int] = None,
    variance_threshold: float = 0.95
) -> Tuple[pd.DataFrame, PCAReducer]:
    """
    Apply PCA to county features.
    
    Args:
        df: County features DataFrame
        feature_cols: Columns to use (default: all numeric)
        n_components: Number of components
        variance_threshold: Minimum variance to retain
        
    Returns:
        Tuple of (transformed DataFrame, fitted reducer)
    """
    # Select features
    if feature_cols is None:
        exclude = ['fips', 'county_name', 'state', 'risk_level', 'latitude', 'longitude']
        feature_cols = [c for c in df.columns 
                       if c not in exclude and df[c].dtype in ['float64', 'int64']]
    
    X = df[feature_cols].fillna(0)
    
    # Fit PCA
    reducer = PCAReducer(n_components=n_components, variance_threshold=variance_threshold)
    X_pca = reducer.fit_transform(X)
    
    # Add FIPS back
    X_pca['fips'] = df['fips'].values
    
    # Print summary
    print("\nPCA Summary:")
    print(f"  Original dimensions: {len(feature_cols)}")
    print(f"  Reduced dimensions: {reducer.n_components}")
    print(f"  Variance retained: {reducer.get_explained_variance()['cumulative_variance_ratio'].iloc[-1]:.2%}")
    
    print("\nTop Features by Component:")
    for i in range(min(3, reducer.n_components)):
        top = reducer.get_top_features_per_component(i, n_features=5)
        print(f"\n  PC{i+1} (explains {reducer.pca.explained_variance_ratio_[i]:.1%} variance):")
        for _, row in top.iterrows():
            print(f"    - {row['feature']}: {row['loading']:.3f}")
    
    return X_pca, reducer
