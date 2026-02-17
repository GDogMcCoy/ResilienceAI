"""
ResilienceAI Bias Mitigation Techniques
========================================
Comprehensive bias mitigation strategies.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.optimize import minimize


def sigmoid(z):
    """Sigmoid function."""
    return 1 / (1 + np.exp(-np.clip(z, -500, 500)))


def softmax(z):
    """Softmax function."""
    exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
    return exp_z / exp_z.sum(axis=1, keepdims=True)


class PreprocessingMitigation:
    """Bias mitigation techniques applied before model training."""
    
    @staticmethod
    def reweighting(X: pd.DataFrame, y: np.ndarray, protected_attr: np.ndarray) -> np.ndarray:
        """Reweight samples to ensure fairness."""
        groups = np.unique(protected_attr)
        classes = np.unique(y)
        n = len(y)
        weights = np.ones(n)
        
        for group in groups:
            for cls in classes:
                mask = (protected_attr == group) & (y == cls)
                count = mask.sum()
                if count > 0:
                    weights[mask] = n / (len(groups) * len(classes) * count)
        return weights
    
    @staticmethod
    def disparate_impact_remover(X: pd.DataFrame, protected_attr: np.ndarray, repair_level: float = 1.0) -> pd.DataFrame:
        """Remove disparate impact by modifying features."""
        X_repaired = X.copy()
        for col in X.select_dtypes(include=[np.number]).columns:
            medians = {group: X.loc[protected_attr == group, col].median() for group in np.unique(protected_attr)}
            overall_median = X[col].median()
            for group in np.unique(protected_attr):
                mask = protected_attr == group
                X_repaired.loc[mask, col] = X.loc[mask, col] + repair_level * (overall_median - medians[group])
        return X_repaired
    
    @staticmethod
    def learning_fair_representations(X: np.ndarray, protected_attr: np.ndarray, n_components: int = 10) -> np.ndarray:
        """Learn fair representations using LFR approach."""
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X_scaled)
        groups = np.unique(protected_attr)
        X_fair = X_pca.copy()
        for i in range(X_pca.shape[1]):
            for group in groups:
                mask = protected_attr == group
                X_fair[mask, i] = X_pca[mask, i] - X_pca[mask, i].mean()
        return X_fair


class InProcessingMitigation:
    """Bias mitigation during model training."""
    
    @staticmethod
    def adversarial_debiasing(X: np.ndarray, y: np.ndarray, protected_attr: np.ndarray,
                               n_epochs: int = 100, lambda_adv: float = 1.0) -> Dict:
        """Adversarial debiasing implementation."""
        np.random.seed(42)
        n_samples, n_features = X.shape
        n_classes = len(np.unique(y))
        n_protected = len(np.unique(protected_attr))
        
        W_pred = np.random.randn(n_features, n_classes) * 0.01
        b_pred = np.zeros(n_classes)
        W_adv = np.random.randn(n_classes, n_protected) * 0.01
        b_adv = np.zeros(n_protected)
        learning_rate = 0.01
        
        for epoch in range(n_epochs):
            logits_pred = X @ W_pred + b_pred
            y_pred_prob = softmax(logits_pred)
            logits_adv = y_pred_prob @ W_adv + b_adv
            attr_pred_prob = softmax(logits_adv)
            
            y_onehot = np.eye(n_classes)[y]
            attr_onehot = np.eye(n_protected)[protected_attr]
            
            grad_adv = (attr_pred_prob - attr_onehot) / n_samples
            dW_adv = y_pred_prob.T @ grad_adv
            W_adv -= learning_rate * dW_adv
            
            dy_pred = (y_pred_prob - y_onehot) / n_samples - lambda_adv * (grad_adv @ W_adv.T)
            dW_pred = X.T @ dy_pred
            W_pred -= learning_rate * dW_pred
        
        return {'W_pred': W_pred, 'b_pred': b_pred, 'W_adv': W_adv, 'b_adv': b_adv}
    
    @staticmethod
    def fairness_constraints(X: np.ndarray, y: np.ndarray, protected_attr: np.ndarray,
                             epsilon: float = 0.05) -> Dict:
        """Train with fairness constraints."""
        n_samples, n_features = X.shape
        
        def objective(params):
            w = params[:-1]
            b = params[-1]
            z = X @ w + b
            y_pred = sigmoid(z)
            return -np.mean(y * np.log(y_pred + 1e-8) + (1-y) * np.log(1-y_pred + 1e-8))
        
        def constraint(params):
            w = params[:-1]
            b = params[-1]
            z = X @ w + b
            y_pred = sigmoid(z)
            groups = np.unique(protected_attr)
            rates = [y_pred[protected_attr == g].mean() for g in groups]
            return epsilon - max(rates) + min(rates)
        
        x0 = np.zeros(n_features + 1)
        cons = {'type': 'ineq', 'fun': constraint}
        result = minimize(objective, x0, method='SLSQP', constraints=cons)
        return {'w': result.x[:-1], 'b': result.x[-1], 'success': result.success}


class PostProcessingMitigation:
    """Bias mitigation applied after model training."""
    
    @staticmethod
    def calibrated_equalized_odds(y_true: np.ndarray, y_prob: np.ndarray, protected_attr: np.ndarray) -> Dict:
        """Calibrated equalized odds post-processing."""
        from sklearn.metrics import confusion_matrix
        groups = np.unique(protected_attr)
        thresholds = {}
        
        for group in groups:
            mask = protected_attr == group
            y_t, y_p = y_true[mask], y_prob[mask]
            best_threshold, best_score = 0.5, float('inf')
            
            for threshold in np.linspace(0.1, 0.9, 50):
                y_pred = (y_p >= threshold).astype(int)
                cm = confusion_matrix(y_t, y_pred)
                if cm.shape == (2, 2):
                    tn, fp, fn, tp = cm.ravel()
                    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
                    score = abs(tpr - 0.8) + abs(fpr - 0.2)
                    if score < best_score:
                        best_score, best_threshold = score, threshold
            thresholds[group] = best_threshold
        return thresholds


if __name__ == "__main__":
    np.random.seed(42)
    n, n_features = 1000, 10
    X = np.random.randn(n, n_features)
    y = np.random.randint(0, 2, n)
    protected = np.random.choice(['A', 'B'], n)
    protected_encoded = np.array([0 if p == 'A' else 1 for p in protected])
    
    weights = PreprocessingMitigation.reweighting(pd.DataFrame(X), y, protected_encoded)
    print(f"Sample weights range: [{weights.min():.2f}, {weights.max():.2f}]")
    
    model_params = InProcessingMitigation.adversarial_debiasing(X, y, protected_encoded, n_epochs=50)
    print(f"Adversarial model trained with {len(model_params)} parameters")
