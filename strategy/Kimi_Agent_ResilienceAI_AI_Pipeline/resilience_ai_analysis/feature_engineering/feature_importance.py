"""
Feature Importance Analysis for ResilienceAI
Multiple methods for identifying key predictive features.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
import warnings

class FeatureImportanceAnalyzer:
    """
    Comprehensive feature importance analysis using multiple methods.
    
    Methods:
    - Tree-based importance (Gini/MDI)
    - Permutation importance
    - SHAP values (if available)
    - Correlation-based importance
    - Mutual information
    """
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.importance_results: Dict[str, pd.DataFrame] = {}
    
    def analyze(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        methods: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Run comprehensive feature importance analysis.
        
        Args:
            X: Feature matrix
            y: Target variable
            methods: List of methods to use (default: all)
            
        Returns:
            Dictionary of importance results by method
        """
        if methods is None:
            methods = ['tree', 'permutation', 'correlation', 'mutual_info']
        
        results = {}
        
        if 'tree' in methods:
            results['tree_importance'] = self._tree_importance(X, y)
        
        if 'permutation' in methods:
            results['permutation_importance'] = self._permutation_importance(X, y)
        
        if 'correlation' in methods:
            results['correlation_importance'] = self._correlation_importance(X, y)
        
        if 'mutual_info' in methods:
            results['mutual_information'] = self._mutual_information(X, y)
        
        self.importance_results = results
        return results
    
    def _tree_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> pd.DataFrame:
        """Compute tree-based feature importance using Random Forest."""
        # Train Random Forest
        rf = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=self.random_state,
            n_jobs=-1
        )
        rf.fit(X, y)
        
        # Get importance
        importance = rf.feature_importances_
        
        # Also train Gradient Boosting for comparison
        gb = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=self.random_state
        )
        gb.fit(X, y)
        
        # Combine results
        results = pd.DataFrame({
            'feature': X.columns,
            'rf_importance': importance,
            'gb_importance': gb.feature_importances_,
            'mean_importance': (importance + gb.feature_importances_) / 2
        })
        
        return results.sort_values('mean_importance', ascending=False)
    
    def _permutation_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_repeats: int = 10
    ) -> pd.DataFrame:
        """Compute permutation importance."""
        # Train a model
        rf = RandomForestRegressor(
            n_estimators=50,
            random_state=self.random_state,
            n_jobs=-1
        )
        rf.fit(X, y)
        
        # Compute permutation importance
        perm_importance = permutation_importance(
            rf, X, y,
            n_repeats=n_repeats,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        results = pd.DataFrame({
            'feature': X.columns,
            'importance_mean': perm_importance.importances_mean,
            'importance_std': perm_importance.importances_std
        })
        
        return results.sort_values('importance_mean', ascending=False)
    
    def _correlation_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> pd.DataFrame:
        """Compute correlation-based importance."""
        correlations = []
        
        for col in X.columns:
            corr = np.abs(X[col].corr(y))
            correlations.append(corr)
        
        results = pd.DataFrame({
            'feature': X.columns,
            'abs_correlation': correlations
        })
        
        return results.sort_values('abs_correlation', ascending=False)
    
    def _mutual_information(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> pd.DataFrame:
        """Compute mutual information scores."""
        from sklearn.feature_selection import mutual_info_regression
        
        # Handle missing values
        X_clean = X.fillna(X.median())
        
        # Compute mutual information
        mi_scores = mutual_info_regression(
            X_clean, y,
            random_state=self.random_state
        )
        
        results = pd.DataFrame({
            'feature': X.columns,
            'mutual_info': mi_scores
        })
        
        return results.sort_values('mutual_info', ascending=False)
    
    def get_consensus_ranking(
        self,
        top_n: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get consensus ranking across all methods.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            DataFrame with consensus rankings
        """
        if not self.importance_results:
            raise ValueError("No importance results available. Run analyze() first.")
        
        # Normalize each method's scores to 0-1
        normalized_scores = {}
        
        for method, df in self.importance_results.items():
            score_col = [c for c in df.columns if 'importance' in c or 'correlation' in c or 'info' in c][0]
            scores = df[score_col].values
            
            if scores.max() > scores.min():
                normalized = (scores - scores.min()) / (scores.max() - scores.min())
            else:
                normalized = np.ones_like(scores)
            
            for i, feature in enumerate(df['feature']):
                if feature not in normalized_scores:
                    normalized_scores[feature] = []
                normalized_scores[feature].append(normalized[i])
        
        # Compute consensus score (mean of normalized scores)
        consensus = []
        for feature, scores in normalized_scores.items():
            consensus.append({
                'feature': feature,
                'consensus_score': np.mean(scores),
                'score_std': np.std(scores),
                'methods_count': len(scores)
            })
        
        results = pd.DataFrame(consensus).sort_values(
            'consensus_score', ascending=False
        )
        
        if top_n:
            results = results.head(top_n)
        
        return results
    
    def select_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        method: str = 'consensus',
        threshold: float = 0.01,
        top_n: Optional[int] = None
    ) -> List[str]:
        """
        Select important features based on analysis.
        
        Args:
            X: Feature matrix
            y: Target variable
            method: Selection method ('consensus', 'tree', 'permutation')
            threshold: Minimum importance threshold
            top_n: Maximum number of features to select
            
        Returns:
            List of selected feature names
        """
        # Run analysis if not already done
        if not self.importance_results:
            self.analyze(X, y)
        
        # Get importance scores
        if method == 'consensus':
            ranking = self.get_consensus_ranking()
            scores = ranking.set_index('feature')['consensus_score']
        elif method in self.importance_results:
            df = self.importance_results[method]
            score_col = [c for c in df.columns if 'importance' in c or 'correlation' in c][0]
            scores = df.set_index('feature')[score_col]
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Apply threshold
        selected = scores[scores >= threshold].index.tolist()
        
        # Apply top_n limit
        if top_n and len(selected) > top_n:
            selected = selected[:top_n]
        
        return selected


def analyze_feature_importance(
    df: pd.DataFrame,
    target_col: str = 'risk_score',
    exclude_cols: Optional[List[str]] = None
) -> Dict[str, pd.DataFrame]:
    """
    Convenience function for quick feature importance analysis.
    
    Args:
        df: DataFrame with features and target
        target_col: Name of target column
        exclude_cols: Columns to exclude from analysis
        
    Returns:
        Dictionary of importance results
    """
    exclude_cols = exclude_cols or ['fips', 'county_name', 'state', 'risk_level']
    exclude_cols.append(target_col)
    
    # Prepare features
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    X = df[feature_cols].select_dtypes(include=[np.number]).fillna(0)
    y = df[target_col]
    
    # Run analysis
    analyzer = FeatureImportanceAnalyzer()
    results = analyzer.analyze(X, y)
    
    # Print summary
    print("=" * 60)
    print("Feature Importance Analysis Summary")
    print("=" * 60)
    
    consensus = analyzer.get_consensus_ranking(top_n=10)
    print("\nTop 10 Features (Consensus Ranking):")
    print(consensus.to_string(index=False))
    
    return results
