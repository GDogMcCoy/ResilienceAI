"""
Feature Selection for ResilienceAI
Algorithms for selecting optimal feature subsets.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Set
from sklearn.feature_selection import (
    SelectKBest, f_regression, mutual_info_regression,
    RFE, SelectFromModel
)
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr
import warnings

class FeatureSelector:
    """
    Comprehensive feature selection for disaster vulnerability modeling.
    
    Methods:
    - Correlation-based selection
    - Mutual information selection
    - Recursive feature elimination
    - L1 regularization (Lasso)
    - Tree-based importance selection
    - Variance inflation factor (VIF)
    """
    
    def __init__(
        self,
        n_features: Optional[int] = None,
        correlation_threshold: float = 0.95,
        importance_threshold: float = 0.01,
        random_state: int = 42
    ):
        self.n_features = n_features
        self.correlation_threshold = correlation_threshold
        self.importance_threshold = importance_threshold
        self.random_state = random_state
        
        self.selected_features: List[str] = []
        self.selection_history: List[Dict] = []
    
    def select_features(
        self,
        df: pd.DataFrame,
        target_col: str = 'risk_score',
        method: str = 'hybrid',
        exclude_cols: Optional[List[str]] = None
    ) -> List[str]:
        """
        Select features using specified method.
        
        Args:
            df: DataFrame with features and target
            target_col: Target variable column
            method: Selection method ('correlation', 'mutual_info', 'rfe', 'lasso', 'tree', 'hybrid')
            exclude_cols: Columns to exclude from selection
            
        Returns:
            List of selected feature names
        """
        exclude_cols = exclude_cols or ['fips', 'county_name', 'state', 'risk_level']
        if target_col not in exclude_cols:
            exclude_cols.append(target_col)
        
        # Prepare feature matrix
        feature_cols = [c for c in df.columns if c not in exclude_cols]
        X = df[feature_cols].select_dtypes(include=[np.number]).fillna(0)
        y = df[target_col]
        
        # Remove highly correlated features first
        X = self._remove_correlated_features(X)
        
        # Apply selection method
        if method == 'correlation':
            selected = self._select_by_correlation(X, y)
        elif method == 'mutual_info':
            selected = self._select_by_mutual_info(X, y)
        elif method == 'rfe':
            selected = self._select_by_rfe(X, y)
        elif method == 'lasso':
            selected = self._select_by_lasso(X, y)
        elif method == 'tree':
            selected = self._select_by_tree_importance(X, y)
        elif method == 'hybrid':
            selected = self._select_hybrid(X, y)
        else:
            raise ValueError(f"Unknown selection method: {method}")
        
        self.selected_features = selected
        
        print(f"Selected {len(selected)} features using {method} method")
        
        return selected
    
    def _remove_correlated_features(
        self,
        X: pd.DataFrame
    ) -> pd.DataFrame:
        """Remove highly correlated features to reduce multicollinearity."""
        
        # Compute correlation matrix
        corr_matrix = X.corr().abs()
        
        # Find highly correlated pairs
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # Features to drop
        to_drop = set()
        
        for col in upper.columns:
            highly_correlated = upper[col][upper[col] > self.correlation_threshold].index.tolist()
            
            for correlated_col in highly_correlated:
                # Keep the feature with higher variance
                if X[col].std() >= X[correlated_col].std():
                    to_drop.add(correlated_col)
                else:
                    to_drop.add(col)
        
        if to_drop:
            print(f"  Removed {len(to_drop)} highly correlated features")
            X = X.drop(columns=list(to_drop))
        
        return X
    
    def _select_by_correlation(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> List[str]:
        """Select features by correlation with target."""
        
        correlations = []
        
        for col in X.columns:
            corr, _ = pearsonr(X[col], y)
            correlations.append((col, abs(corr)))
        
        # Sort by absolute correlation
        correlations.sort(key=lambda x: x[1], reverse=True)
        
        # Select top features
        if self.n_features:
            selected = [c for c, _ in correlations[:self.n_features]]
        else:
            selected = [c for c, corr in correlations if corr >= self.importance_threshold]
        
        self.selection_history.append({
            'method': 'correlation',
            'n_selected': len(selected),
            'top_features': selected[:10]
        })
        
        return selected
    
    def _select_by_mutual_info(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> List[str]:
        """Select features by mutual information."""
        
        # Compute mutual information scores
        mi_scores = mutual_info_regression(X, y, random_state=self.random_state)
        
        # Create feature importance dataframe
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'mutual_info': mi_scores
        }).sort_values('mutual_info', ascending=False)
        
        # Select features
        if self.n_features:
            selected = feature_importance.head(self.n_features)['feature'].tolist()
        else:
            threshold = feature_importance['mutual_info'].max() * self.importance_threshold
            selected = feature_importance[feature_importance['mutual_info'] >= threshold]['feature'].tolist()
        
        self.selection_history.append({
            'method': 'mutual_info',
            'n_selected': len(selected),
            'top_features': selected[:10]
        })
        
        return selected
    
    def _select_by_rfe(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> List[str]:
        """Select features using Recursive Feature Elimination."""
        
        # Determine number of features
        n_features = self.n_features or max(10, len(X.columns) // 2)
        
        # Use Random Forest as base estimator
        estimator = RandomForestRegressor(
            n_estimators=50,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        # RFE
        selector = RFE(
            estimator=estimator,
            n_features_to_select=n_features,
            step=0.1
        )
        
        selector = selector.fit(X, y)
        
        selected = X.columns[selector.support_].tolist()
        
        self.selection_history.append({
            'method': 'rfe',
            'n_selected': len(selected),
            'top_features': selected[:10]
        })
        
        return selected
    
    def _select_by_lasso(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> List[str]:
        """Select features using L1 regularization (Lasso)."""
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Lasso with cross-validation
        lasso = LassoCV(
            cv=5,
            random_state=self.random_state,
            max_iter=2000
        )
        
        lasso.fit(X_scaled, y)
        
        # Select features with non-zero coefficients
        selected = X.columns[lasso.coef_ != 0].tolist()
        
        self.selection_history.append({
            'method': 'lasso',
            'n_selected': len(selected),
            'alpha': lasso.alpha_,
            'top_features': selected[:10]
        })
        
        return selected
    
    def _select_by_tree_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> List[str]:
        """Select features using tree-based importance."""
        
        # Train Random Forest
        rf = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        rf.fit(X, y)
        
        # Get feature importances
        importances = pd.DataFrame({
            'feature': X.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Select features
        if self.n_features:
            selected = importances.head(self.n_features)['feature'].tolist()
        else:
            threshold = importances['importance'].max() * self.importance_threshold
            selected = importances[importances['importance'] >= threshold]['feature'].tolist()
        
        self.selection_history.append({
            'method': 'tree',
            'n_selected': len(selected),
            'top_features': selected[:10]
        })
        
        return selected
    
    def _select_hybrid(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> List[str]:
        """
        Hybrid feature selection combining multiple methods.
        
        Strategy:
        1. Start with correlation-based selection (fast)
        2. Refine with mutual information
        3. Final selection with tree importance
        """
        
        # Step 1: Correlation-based pre-selection
        corr_selected = self._select_by_correlation(X, y)
        X_corr = X[corr_selected]
        
        # Step 2: Mutual information refinement
        mi_selected = self._select_by_mutual_info(X_corr, y)
        X_mi = X_corr[mi_selected]
        
        # Step 3: Tree-based final selection
        tree_selected = self._select_by_tree_importance(X_mi, y)
        
        self.selection_history.append({
            'method': 'hybrid',
            'n_selected': len(tree_selected),
            'correlation_step': len(corr_selected),
            'mutual_info_step': len(mi_selected),
            'top_features': tree_selected[:10]
        })
        
        return tree_selected
    
    def get_selection_summary(self) -> pd.DataFrame:
        """Get summary of feature selection history."""
        return pd.DataFrame(self.selection_history)


class VarianceInflationFactorSelector:
    """
    Feature selection based on Variance Inflation Factor (VIF).
    Removes features with high multicollinearity.
    """
    
    def __init__(self, vif_threshold: float = 5.0):
        self.vif_threshold = vif_threshold
        self.removed_features: List[str] = []
    
    def select_features(
        self,
        X: pd.DataFrame,
        verbose: bool = True
    ) -> List[str]:
        """
        Select features by removing high VIF features.
        
        Args:
            X: Feature matrix
            verbose: Print progress
            
        Returns:
            List of selected feature names
        """
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        
        X = X.select_dtypes(include=[np.number]).fillna(0)
        
        features = X.columns.tolist()
        vif_data = pd.DataFrame()
        vif_data['feature'] = features
        
        # Iteratively remove high VIF features
        while True:
            # Compute VIF for all features
            vif_values = []
            for i in range(len(features)):
                try:
                    vif = variance_inflation_factor(X[features].values, i)
                    vif_values.append(vif)
                except:
                    vif_values.append(np.inf)
            
            vif_data = pd.DataFrame({
                'feature': features,
                'vif': vif_values
            })
            
            # Find feature with highest VIF
            max_vif_idx = vif_data['vif'].idxmax()
            max_vif = vif_data.loc[max_vif_idx, 'vif']
            max_vif_feature = vif_data.loc[max_vif_idx, 'feature']
            
            if max_vif <= self.vif_threshold:
                break
            
            # Remove feature with highest VIF
            features.remove(max_vif_feature)
            self.removed_features.append(max_vif_feature)
            
            if verbose:
                print(f"  Removed {max_vif_feature} (VIF: {max_vif:.2f})")
        
        if verbose:
            print(f"  Final features: {len(features)} (removed {len(self.removed_features)})")
        
        return features


def select_optimal_features(
    df: pd.DataFrame,
    target_col: str = 'risk_score',
    n_features: int = 50,
    method: str = 'hybrid'
) -> List[str]:
    """
    Convenience function for feature selection.
    
    Args:
        df: DataFrame with features and target
        target_col: Target variable column
        n_features: Number of features to select
        method: Selection method
        
    Returns:
        List of selected feature names
    """
    selector = FeatureSelector(n_features=n_features)
    return selector.select_features(df, target_col, method)
