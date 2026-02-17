"""
Ranking Algorithms for ResilienceAI
Implements various learning-to-rank approaches
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics.pairwise import cosine_similarity


class ListwiseRanker(nn.Module):
    """Neural listwise ranking model"""
    
    def __init__(
        self,
        n_features: int,
        hidden_dims: List[int] = [128, 64, 32],
        dropout: float = 0.2
    ):
        super().__init__()
        
        layers = []
        prev_dim = n_features
        
        for dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, dim),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.BatchNorm1d(dim)
            ])
            prev_dim = dim
        
        layers.append(nn.Linear(prev_dim, 1))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        return self.network(x)


class LearningToRank:
    """Learning-to-rank implementation"""
    
    def __init__(
        self,
        method: str = 'listnet',
        learning_rate: float = 0.001,
        epochs: int = 100
    ):
        self.method = method
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.model = None
        self.feature_columns = []
    
    def fit(
        self,
        training_data: pd.DataFrame,
        query_col: str = 'county_id',
        label_col: str = 'relevance',
        feature_cols: Optional[List[str]] = None
    ) -> None:
        """Train ranking model"""
        
        if feature_cols is None:
            feature_cols = [c for c in training_data.columns 
                          if c not in [query_col, label_col, 'item_id']]
        
        self.feature_columns = feature_cols
        
        if self.method == 'listnet':
            self._fit_listnet(training_data, query_col, label_col)
        elif self.method == 'ranknet':
            self._fit_ranknet(training_data, query_col, label_col)
        elif self.method == 'lambdarank':
            self._fit_lambdarank(training_data, query_col, label_col)
        elif self.method == 'xgboost':
            self._fit_xgboost(training_data, query_col, label_col)
    
    def _fit_listnet(
        self,
        data: pd.DataFrame,
        query_col: str,
        label_col: str
    ) -> None:
        """Fit ListNet ranking model"""
        
        n_features = len(self.feature_columns)
        self.model = ListwiseRanker(n_features)
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        # Group by query
        queries = data[query_col].unique()
        
        for epoch in range(self.epochs):
            total_loss = 0
            
            for query in queries:
                query_data = data[data[query_col] == query]
                
                if len(query_data) < 2:
                    continue
                
                # Prepare data
                X = torch.FloatTensor(query_data[self.feature_columns].values)
                y = torch.FloatTensor(query_data[label_col].values)
                
                # Forward pass
                scores = self.model(X).squeeze()
                
                # ListNet loss (cross-entropy between score distribution and label distribution)
                score_probs = F.softmax(scores, dim=0)
                label_probs = F.softmax(y, dim=0)
                
                loss = -torch.sum(label_probs * torch.log(score_probs + 1e-10))
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}, Loss: {total_loss:.4f}")
    
    def _fit_ranknet(
        self,
        data: pd.DataFrame,
        query_col: str,
        label_col: str
    ) -> None:
        """Fit RankNet ranking model"""
        
        n_features = len(self.feature_columns)
        self.model = ListwiseRanker(n_features)
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        queries = data[query_col].unique()
        
        for epoch in range(self.epochs):
            total_loss = 0
            
            for query in queries:
                query_data = data[data[query_col] == query]
                
                if len(query_data) < 2:
                    continue
                
                X = torch.FloatTensor(query_data[self.feature_columns].values)
                y = torch.FloatTensor(query_data[label_col].values)
                
                # Compute pairwise preferences
                scores = self.model(X).squeeze()
                
                # Create pairwise differences
                n = len(scores)
                score_diffs = scores.unsqueeze(1) - scores.unsqueeze(0)
                label_diffs = y.unsqueeze(1) - y.unsqueeze(0)
                
                # Target probabilities (sigmoid of label differences)
                S = torch.sign(label_diffs)
                S = (S + 1) / 2  # Convert to 0, 1
                
                # RankNet loss
                probs = torch.sigmoid(score_diffs)
                loss = -torch.sum(S * torch.log(probs + 1e-10) + 
                                 (1 - S) * torch.log(1 - probs + 1e-10))
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}, Loss: {total_loss:.4f}")
    
    def _fit_xgboost(
        self,
        data: pd.DataFrame,
        query_col: str,
        label_col: str
    ) -> None:
        """Fit XGBoost ranking model"""
        
        try:
            import xgboost as xgb
            
            # Prepare data
            X = data[self.feature_columns]
            y = data[label_col]
            groups = data.groupby(query_col).size().values
            
            # Create DMatrix
            dtrain = xgb.DMatrix(X, label=y)
            dtrain.set_group(groups)
            
            # Parameters
            params = {
                'objective': 'rank:pairwise',
                'eval_metric': 'ndcg',
                'max_depth': 6,
                'eta': 0.1,
                'subsample': 0.8
            }
            
            # Train
            self.model = xgb.train(
                params,
                dtrain,
                num_boost_round=100
            )
            
        except ImportError:
            print("XGBoost not available, using GradientBoostingRegressor")
            self.model = GradientBoostingRegressor(n_estimators=100)
            self.model.fit(data[self.feature_columns], data[label_col])
    
    def rank(
        self,
        items: pd.DataFrame,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Rank items"""
        
        X = items[self.feature_columns].values
        
        if isinstance(self.model, nn.Module):
            self.model.eval()
            with torch.no_grad():
                scores = self.model(torch.FloatTensor(X)).squeeze().numpy()
        else:
            scores = self.model.predict(X)
        
        # Sort by score
        ranked_indices = np.argsort(scores)[::-1][:n_results]
        
        results = []
        for idx in ranked_indices:
            item = items.iloc[idx].to_dict()
            item['rank_score'] = float(scores[idx])
            results.append(item)
        
        return results
    
    def evaluate(
        self,
        test_data: pd.DataFrame,
        query_col: str = 'county_id',
        label_col: str = 'relevance',
        k: int = 10
    ) -> Dict[str, float]:
        """Evaluate ranking performance"""
        
        queries = test_data[query_col].unique()
        
        ndcg_scores = []
        mrr_scores = []
        
        for query in queries:
            query_data = test_data[test_data[query_col] == query]
            
            if len(query_data) < 2:
                continue
            
            # Get predictions
            X = query_data[self.feature_columns].values
            
            if isinstance(self.model, nn.Module):
                self.model.eval()
                with torch.no_grad():
                    scores = self.model(torch.FloatTensor(X)).squeeze().numpy()
            else:
                scores = self.model.predict(X)
            
            # Get true labels
            labels = query_data[label_col].values
            
            # Calculate NDCG
            ndcg = self._calculate_ndcg(labels, scores, k)
            ndcg_scores.append(ndcg)
            
            # Calculate MRR
            mrr = self._calculate_mrr(labels, scores)
            mrr_scores.append(mrr)
        
        return {
            f'ndcg@{k}': np.mean(ndcg_scores),
            'mrr': np.mean(mrr_scores)
        }
    
    def _calculate_ndcg(
        self,
        labels: np.ndarray,
        scores: np.ndarray,
        k: int
    ) -> float:
        """Calculate NDCG@k"""
        
        # Sort by scores
        sorted_indices = np.argsort(scores)[::-1][:k]
        sorted_labels = labels[sorted_indices]
        
        # Calculate DCG
        dcg = np.sum((2 ** sorted_labels - 1) / np.log2(np.arange(2, k + 2)))
        
        # Calculate ideal DCG
        ideal_labels = np.sort(labels)[::-1][:k]
        idcg = np.sum((2 ** ideal_labels - 1) / np.log2(np.arange(2, k + 2)))
        
        return dcg / idcg if idcg > 0 else 0
    
    def _calculate_mrr(
        self,
        labels: np.ndarray,
        scores: np.ndarray
    ) -> float:
        """Calculate Mean Reciprocal Rank"""
        
        sorted_indices = np.argsort(scores)[::-1]
        sorted_labels = labels[sorted_indices]
        
        # Find first relevant item
        for i, label in enumerate(sorted_labels):
            if label > 0:
                return 1.0 / (i + 1)
        
        return 0.0


class DiversityReranker:
    """Rerank recommendations for diversity"""
    
    def __init__(
        self,
        diversity_weight: float = 0.3,
        similarity_threshold: float = 0.8
    ):
        self.diversity_weight = diversity_weight
        self.similarity_threshold = similarity_threshold
    
    def rerank(
        self,
        items: List[Dict[str, Any]],
        item_embeddings: np.ndarray,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Rerank items for diversity using MMR (Maximal Marginal Relevance)"""
        
        if len(items) <= n_results:
            return items
        
        selected = []
        remaining = list(range(len(items)))
        
        # Select first item (highest relevance)
        selected.append(remaining.pop(0))
        
        while len(selected) < n_results and remaining:
            mmr_scores = []
            
            for idx in remaining:
                # Relevance score
                relevance = items[idx].get('rank_score', 0)
                
                # Max similarity to selected items
                max_sim = 0
                for sel_idx in selected:
                    sim = cosine_similarity(
                        item_embeddings[idx:idx+1],
                        item_embeddings[sel_idx:sel_idx+1]
                    )[0, 0]
                    max_sim = max(max_sim, sim)
                
                # MMR score
                mmr_score = (1 - self.diversity_weight) * relevance - \
                           self.diversity_weight * max_sim
                mmr_scores.append((idx, mmr_score))
            
            # Select item with highest MMR score
            best_idx, _ = max(mmr_scores, key=lambda x: x[1])
            selected.append(best_idx)
            remaining.remove(best_idx)
        
        return [items[i] for i in selected]


class FairnessReranker:
    """Rerank recommendations for fairness across groups"""
    
    def __init__(
        self,
        fairness_weight: float = 0.3,
        group_attribute: str = 'category'
    ):
        self.fairness_weight = fairness_weight
        self.group_attribute = group_attribute
    
    def rerank(
        self,
        items: List[Dict[str, Any]],
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Rerank items for fairness across groups"""
        
        if len(items) <= n_results:
            return items
        
        # Group items by attribute
        groups = {}
        for i, item in enumerate(items):
            group = item.get(self.group_attribute, 'unknown')
            if group not in groups:
                groups[group] = []
            groups[group].append((i, item))
        
        # Sort each group by score
        for group in groups:
            groups[group].sort(key=lambda x: x[1].get('rank_score', 0), reverse=True)
        
        # Interleave from different groups
        result = []
        group_pointers = {g: 0 for g in groups}
        
        while len(result) < n_results and any(
            group_pointers[g] < len(groups[g]) for g in groups
        ):
            for group in groups:
                if group_pointers[group] < len(groups[group]):
                    idx, item = groups[group][group_pointers[group]]
                    result.append(item)
                    group_pointers[group] += 1
                    
                    if len(result) >= n_results:
                        break
        
        return result


# Example usage
if __name__ == "__main__":
    # Create sample training data
    training_data = pd.DataFrame({
        'county_id': ['c1', 'c1', 'c1', 'c2', 'c2', 'c2'],
        'item_id': ['i1', 'i2', 'i3', 'i1', 'i2', 'i3'],
        'relevance': [3, 2, 1, 3, 1, 2],
        'feature1': [0.8, 0.6, 0.4, 0.9, 0.3, 0.7],
        'feature2': [0.7, 0.5, 0.3, 0.8, 0.2, 0.6]
    })
    
    # Train ranking model
    ranker = LearningToRank(method='listnet', epochs=50)
    ranker.fit(training_data, query_col='county_id', label_col='relevance')
    
    # Rank items
    test_items = pd.DataFrame({
        'item_id': ['i1', 'i2', 'i3'],
        'feature1': [0.85, 0.55, 0.35],
        'feature2': [0.75, 0.45, 0.25]
    })
    
    ranked = ranker.rank(test_items, n_results=3)
    
    print("Ranked Items:")
    for item in ranked:
        print(f"  {item['item_id']}: {item['rank_score']:.3f}")
    
    # Evaluate
    metrics = ranker.evaluate(training_data, k=3)
    print(f"\nEvaluation Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.3f}")
