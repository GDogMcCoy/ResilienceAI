# ResilienceAI Explainable AI (XAI) Framework

## Executive Summary

This document provides a comprehensive design for the Explainable AI (XAI) framework within ResilienceAI, ensuring model transparency, regulatory compliance, and user trust. The framework implements multiple explanation techniques including SHAP, LIME, counterfactual explanations, and model-agnostic approaches to provide interpretable insights for all AI-driven decisions.

---

## 1. XAI Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESILIENCEAI XAI FRAMEWORK                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EXPLANATION ORCHESTRATOR LAYER                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │   │
│  │  │  Explanation │  │   Request    │  │    Explanation Cache     │  │   │
│  │  │   Router     │  │   Handler    │  │      & Registry          │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│  ┌───────────────────────────┼──────────────────────────────────────────┐  │
│  │              EXPLANATION ENGINE LAYER                                 │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────────┐  │  │
│  │  │    SHAP     │ │    LIME     │ │  Feature    │ │ Counterfactual │  │  │
│  │  │   Engine    │ │   Engine    │ │ Importance  │ │   Generator    │  │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│  ┌───────────────────────────┼──────────────────────────────────────────┐  │
│  │                    MODEL ADAPTER LAYER                                │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │  │
│  │  │  Random  │ │ Gradient │ │  Neural  │ │ Ensemble │ │  Custom  │    │  │
│  │  │  Forest  │ │ Boosting │ │  Network │ │  Models  │ │  Models  │    │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│  ┌───────────────────────────┼──────────────────────────────────────────┐  │
│  │                  VISUALIZATION & OUTPUT LAYER                         │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐  │  │
│  │  │   Force      │ │   Decision   │ │   Feature    │ │ Waterfall   │  │  │
│  │  │   Plots      │ │    Plots     │ │ Importance   │ │   Charts    │  │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│  ┌───────────────────────────┼──────────────────────────────────────────┐  │
│  │                    API & INTEGRATION LAYER                            │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐  │  │
│  │  │  REST API    │ │  GraphQL     │ │  WebSocket   │ │  gRPC       │  │  │
│  │  │  Endpoints   │ │  Interface   │ │  Streaming   │ │  Services   │  │  │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Core Components

| Component | Purpose | Technology Stack |
|-----------|---------|------------------|
| Explanation Orchestrator | Route requests to appropriate explainers | Python, FastAPI |
| SHAP Engine | Calculate SHAP values for feature attribution | shap, tree-shap, kernel-shap |
| LIME Engine | Generate local interpretable explanations | lime, anchor-exp |
| Feature Importance | Global and local feature importance | sklearn, eli5 |
| Counterfactual Generator | Generate "what-if" scenarios | dice-ml, alibi |
| Visualization Layer | Render explanation graphics | plotly, matplotlib, d3.js |
| Model Adapters | Interface with different model types | Custom adapters |
| Explanation Cache | Store and retrieve explanations | Redis, PostgreSQL |

---

## 2. SHAP Value Implementation

### 2.1 SHAP Architecture

```python
# File: /app/xai/shap_engine.py

import shap
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class SHAPExplainerType(Enum):
    """Types of SHAP explainers for different model architectures."""
    TREE = "tree"           # For tree-based models
    KERNEL = "kernel"       # Model-agnostic
    DEEP = "deep"           # For neural networks
    LINEAR = "linear"       # For linear models
    GRADIENT = "gradient"   # For gradient-based models


@dataclass
class SHAPExplanation:
    """Structured SHAP explanation result."""
    feature_names: List[str]
    shap_values: np.ndarray
    base_value: float
    prediction: float
    instance: np.ndarray
    explanation_type: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_names": self.feature_names,
            "shap_values": self.shap_values.tolist(),
            "base_value": self.base_value,
            "prediction": self.prediction,
            "instance": self.instance.tolist(),
            "explanation_type": self.explanation_type,
            "metadata": self.metadata
        }


class SHAPEngine:
    """Comprehensive SHAP explanation engine for ResilienceAI."""
    
    def __init__(
        self,
        model: Any,
        feature_names: List[str],
        explainer_type: SHAPExplainerType = SHAPExplainerType.TREE,
        background_data: Optional[np.ndarray] = None,
        cache_enabled: bool = True,
        cache_size: int = 1000
    ):
        self.model = model
        self.feature_names = feature_names
        self.explainer_type = explainer_type
        self.background_data = background_data
        self.cache_enabled = cache_enabled
        self.cache_size = cache_size
        self.explainer = None
        self._explanation_cache = {}
        self._initialize_explainer()
        
    def _initialize_explainer(self):
        """Initialize the appropriate SHAP explainer."""
        try:
            if self.explainer_type == SHAPExplainerType.TREE:
                self.explainer = shap.TreeExplainer(self.model)
            elif self.explainer_type == SHAPExplainerType.KERNEL:
                if self.background_data is None:
                    raise ValueError("Background data required")
                self.explainer = shap.KernelExplainer(
                    self.model.predict, self.background_data
                )
            elif self.explainer_type == SHAPExplainerType.DEEP:
                self.explainer = shap.DeepExplainer(self.model, self.background_data)
            elif self.explainer_type == SHAPExplainerType.LINEAR:
                self.explainer = shap.LinearExplainer(self.model, self.background_data)
            elif self.explainer_type == SHAPExplainerType.GRADIENT:
                self.explainer = shap.GradientExplainer(self.model, self.background_data)
            logger.info(f"Initialized {self.explainer_type.value} explainer")
        except Exception as e:
            logger.error(f"Failed to initialize explainer: {e}")
            raise
    
    def explain_local(self, instance: Union[np.ndarray, pd.DataFrame], return_viz: bool = False) -> SHAPExplanation:
        """Generate local SHAP explanation for a single instance."""
        cache_key = self._get_cache_key(instance)
        if self.cache_enabled and cache_key in self._explanation_cache:
            return self._explanation_cache[cache_key]
        
        if isinstance(instance, pd.DataFrame):
            instance_array = instance.values
        else:
            instance_array = np.array(instance)
        if instance_array.ndim == 1:
            instance_array = instance_array.reshape(1, -1)
        
        shap_values = self.explainer.shap_values(instance_array)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        base_value = self.explainer.expected_value[0] if isinstance(
            self.explainer.expected_value, (list, np.ndarray)
        ) else self.explainer.expected_value
        
        prediction = self._get_prediction(instance_array)
        
        explanation = SHAPExplanation(
            feature_names=self.feature_names,
            shap_values=shap_values[0] if shap_values.ndim > 1 else shap_values,
            base_value=float(base_value),
            prediction=float(prediction),
            instance=instance_array[0],
            explanation_type="local",
            metadata={"explainer_type": self.explainer_type.value}
        )
        
        if self.cache_enabled:
            self._cache_explanation(cache_key, explanation)
        return explanation
    
    def explain_global(self, X: Union[np.ndarray, pd.DataFrame], sample_size: int = 1000) -> Dict[str, Any]:
        """Generate global SHAP explanations across dataset."""
        if len(X) > sample_size:
            if isinstance(X, pd.DataFrame):
                X_sample = X.sample(n=sample_size, random_state=42)
            else:
                indices = np.random.choice(len(X), sample_size, replace=False)
                X_sample = X[indices]
        else:
            X_sample = X
        
        X_array = X_sample.values if isinstance(X_sample, pd.DataFrame) else np.array(X_sample)
        shap_values = self.explainer.shap_values(X_array)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        feature_importance = list(zip(self.feature_names, mean_abs_shap))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "feature_importance": [{"feature": name, "importance": float(imp)} 
                                   for name, imp in feature_importance],
            "shap_values": shap_values.tolist(),
            "base_value": float(self.explainer.expected_value) if hasattr(
                self.explainer, 'expected_value') else 0.0,
            "summary_statistics": {
                "mean_shap": shap_values.mean(axis=0).tolist(),
                "std_shap": shap_values.std(axis=0).tolist(),
                "max_shap": shap_values.max(axis=0).tolist(),
                "min_shap": shap_values.min(axis=0).tolist()
            },
            "sample_size": len(X_sample)
        }
    
    def explain_batch(self, instances: Union[np.ndarray, pd.DataFrame], n_workers: int = 4) -> List[SHAPExplanation]:
        """Generate SHAP explanations for multiple instances in parallel."""
        if isinstance(instances, pd.DataFrame):
            instances = instances.values
        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            explanations = list(executor.map(lambda x: self.explain_local(x), instances))
        return explanations
    
    def _get_prediction(self, instance: np.ndarray) -> float:
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(instance)[0, 1]
        return self.model.predict(instance)[0]
    
    def _get_cache_key(self, instance) -> str:
        if isinstance(instance, pd.DataFrame):
            instance = instance.values
        return hash(instance.tobytes())
    
    def _cache_explanation(self, key: str, explanation: SHAPExplanation):
        if len(self._explanation_cache) >= self.cache_size:
            oldest_key = next(iter(self._explanation_cache))
            del self._explanation_cache[oldest_key]
        self._explanation_cache[key] = explanation
```

---

## 3. LIME Explanations

### 3.1 LIME Engine Implementation

```python
# File: /app/xai/lime_engine.py

import lime
import lime.lime_tabular
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LIMEDataType(Enum):
    """Data types supported by LIME."""
    TABULAR = "tabular"
    TEXT = "text"
    IMAGE = "image"


@dataclass
class LIMEExplanation:
    """Structured LIME explanation result."""
    feature_weights: List[tuple]
    intercept: float
    prediction: float
    score: float
    local_pred: float
    instance: np.ndarray
    explanation_type: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_weights": self.feature_weights,
            "intercept": self.intercept,
            "prediction": self.prediction,
            "score": self.score,
            "local_pred": self.local_pred,
            "instance": self.instance.tolist(),
            "explanation_type": self.explanation_type,
            "metadata": self.metadata
        }


class LIMEEngine:
    """LIME explanation engine for local interpretable explanations."""
    
    def __init__(
        self,
        model: Any,
        feature_names: List[str],
        data_type: LIMEDataType = LIMEDataType.TABULAR,
        training_data: Optional[np.ndarray] = None,
        categorical_features: Optional[List[int]] = None,
        class_names: Optional[List[str]] = None
    ):
        self.model = model
        self.feature_names = feature_names
        self.data_type = data_type
        self.training_data = training_data
        self.categorical_features = categorical_features or []
        self.class_names = class_names or []
        self.explainer = None
        self._initialize_explainer()
        
    def _initialize_explainer(self):
        """Initialize the appropriate LIME explainer."""
        try:
            if self.data_type == LIMEDataType.TABULAR:
                if self.training_data is None:
                    raise ValueError("Training data required")
                self.explainer = lime.lime_tabular.LimeTabularExplainer(
                    self.training_data,
                    feature_names=self.feature_names,
                    categorical_features=self.categorical_features,
                    class_names=self.class_names,
                    mode='classification' if self.class_names else 'regression'
                )
            logger.info(f"Initialized {self.data_type.value} LIME explainer")
        except Exception as e:
            logger.error(f"Failed to initialize LIME: {e}")
            raise
    
    def explain(
        self,
        instance: Union[np.ndarray, pd.DataFrame],
        num_features: int = 10,
        num_samples: int = 5000
    ) -> LIMEExplanation:
        """Generate LIME explanation for an instance."""
        if hasattr(self.model, 'predict_proba'):
            predict_fn = self.model.predict_proba
        else:
            predict_fn = self.model.predict
        
        if isinstance(instance, pd.DataFrame):
            instance_array = instance.values[0]
        else:
            instance_array = np.array(instance)
            if instance_array.ndim > 1:
                instance_array = instance_array[0]
        
        explanation = self.explainer.explain_instance(
            instance_array, predict_fn,
            num_features=num_features, num_samples=num_samples
        )
        
        prediction = predict_fn(instance_array.reshape(1, -1))[0]
        if len(prediction.shape) > 0:
            prediction = prediction[1] if len(prediction) > 1 else prediction[0]
        
        return LIMEExplanation(
            feature_weights=explanation.as_list(),
            intercept=explanation.intercept[1] if isinstance(explanation.intercept, dict) else explanation.intercept,
            prediction=float(prediction),
            score=explanation.score,
            local_pred=explanation.local_pred[1] if isinstance(explanation.local_pred, (list, np.ndarray)) else explanation.local_pred,
            instance=instance_array,
            explanation_type="local",
            metadata={"num_features": num_features, "num_samples": num_samples}
        )
```

---

## 4. Feature Importance Framework

```python
# File: /app/xai/feature_importance.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, mean_squared_error
import logging

logger = logging.getLogger(__name__)


@dataclass
class FeatureImportanceResult:
    """Feature importance result structure."""
    feature_names: List[str]
    importance_values: np.ndarray
    importance_type: str
    std_values: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "feature_names": self.feature_names,
            "importance": self.importance_values.tolist(),
            "importance_type": self.importance_type,
            "metadata": self.metadata or {}
        }
        if self.std_values is not None:
            result["std"] = self.std_values.tolist()
        return result


class FeatureImportanceCalculator:
    """Comprehensive feature importance calculator."""
    
    def __init__(self, model: Any, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
    
    def get_builtin_importance(self) -> FeatureImportanceResult:
        """Get built-in feature importance from model."""
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            importance = np.abs(self.model.coef_)
            if importance.ndim > 1:
                importance = importance[0]
        else:
            raise ValueError("Model does not have built-in feature importance")
        
        return FeatureImportanceResult(
            feature_names=self.feature_names,
            importance_values=importance,
            importance_type="built-in",
            metadata={"method": "model_builtin"}
        )
    
    def get_permutation_importance(
        self, X, y, n_repeats: int = 10, random_state: int = 42, scoring: Optional[str] = None
    ) -> FeatureImportanceResult:
        """Calculate permutation feature importance."""
        if scoring is None:
            scoring = 'accuracy' if hasattr(self.model, 'predict_proba') else 'neg_mean_squared_error'
        
        perm_importance = permutation_importance(
            self.model, X, y, n_repeats=n_repeats,
            random_state=random_state, scoring=scoring
        )
        
        return FeatureImportanceResult(
            feature_names=self.feature_names,
            importance_values=perm_importance.importances_mean,
            importance_type="permutation",
            std_values=perm_importance.importances_std,
            metadata={"method": "permutation", "n_repeats": n_repeats, "scoring": scoring}
        )
    
    def get_all_importance_methods(self, X, y=None) -> Dict[str, FeatureImportanceResult]:
        """Get feature importance using all available methods."""
        results = {}
        try:
            results["built_in"] = self.get_builtin_importance()
        except Exception as e:
            logger.warning(f"Could not get built-in importance: {e}")
        if y is not None:
            try:
                results["permutation"] = self.get_permutation_importance(X, y)
            except Exception as e:
                logger.warning(f"Could not get permutation importance: {e}")
        return results
```

---

## 5. Counterfactual Explanations

```python
# File: /app/xai/counterfactual_engine.py

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CounterfactualExplanation:
    """Counterfactual explanation result."""
    original_instance: np.ndarray
    counterfactual_instance: np.ndarray
    original_prediction: float
    counterfactual_prediction: float
    feature_changes: Dict[str, Dict[str, Any]]
    distance: float
    sparsity: int
    feasibility_score: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_instance": self.original_instance.tolist(),
            "counterfactual_instance": self.counterfactual_instance.tolist(),
            "original_prediction": self.original_prediction,
            "counterfactual_prediction": self.counterfactual_prediction,
            "feature_changes": self.feature_changes,
            "distance": self.distance,
            "sparsity": self.sparsity,
            "feasibility_score": self.feasibility_score,
            "metadata": self.metadata
        }


class CounterfactualGenerator:
    """Counterfactual explanation generator."""
    
    def __init__(
        self, model: Any, feature_names: List[str],
        feature_ranges: Optional[Dict] = None,
        immutable_features: Optional[List[str]] = None,
        proximity_weight: float = 0.5,
        sparsity_weight: float = 0.2
    ):
        self.model = model
        self.feature_names = feature_names
        self.feature_ranges = feature_ranges or {}
        self.immutable_features = immutable_features or []
        self.proximity_weight = proximity_weight
        self.sparsity_weight = sparsity_weight
        self.feature_index = {name: i for i, name in enumerate(feature_names)}
    
    def generate_counterfactual(
        self, instance, target_class=None, target_probability=None,
        max_iterations: int = 1000, num_counterfactuals: int = 1
    ) -> List[CounterfactualExplanation]:
        """Generate counterfactual explanations."""
        if isinstance(instance, pd.DataFrame):
            instance_array = instance.values[0]
        else:
            instance_array = np.array(instance)
            if instance_array.ndim > 1:
                instance_array = instance_array[0]
        
        original_pred = self._get_prediction(instance_array)
        if target_class is None and target_probability is None:
            target_probability = 1.0 - original_pred
        
        counterfactuals = []
        for i in range(num_counterfactuals):
            cf = self._optimize_counterfactual(
                instance_array, original_pred, target_class,
                target_probability, max_iterations
            )
            if cf is not None:
                counterfactuals.append(cf)
        return counterfactuals
    
    def _optimize_counterfactual(
        self, original, original_pred, target_class, target_probability, max_iterations
    ):
        """Optimize counterfactual using gradient-based approach."""
        cf = original.copy() + np.random.randn(len(original)) * 0.01
        cf = self._apply_constraints(cf, original)
        best_cf = None
        best_loss = float('inf')
        learning_rate = 0.1
        
        for iteration in range(max_iterations):
            loss, gradient = self._calculate_loss_and_gradient(
                cf, original, original_pred, target_class, target_probability
            )
            cf = cf - learning_rate * gradient
            cf = self._apply_constraints(cf, original)
            if loss < best_loss:
                best_loss = loss
                best_cf = cf.copy()
            current_pred = self._get_prediction(cf)
            if self._target_achieved(current_pred, target_class, target_probability):
                break
            if iteration % 100 == 0:
                learning_rate *= 0.95
        
        if best_cf is None:
            return None
        cf_pred = self._get_prediction(best_cf)
        return self._create_explanation(original, best_cf, original_pred, cf_pred)
    
    def _calculate_loss_and_gradient(self, cf, original, original_pred, target_class, target_probability):
        """Calculate loss and gradient."""
        cf_pred = self._get_prediction(cf)
        if target_probability is not None:
            pred_loss = (cf_pred - target_probability) ** 2
            pred_grad = 2 * (cf_pred - target_probability)
        else:
            pred_loss = -np.log(cf_pred + 1e-10) if target_class == 1 else -np.log(1 - cf_pred + 1e-10)
            pred_grad = -1 / (cf_pred + 1e-10) if target_class == 1 else 1 / (1 - cf_pred + 1e-10)
        
        proximity_loss = np.sum((cf - original) ** 2)
        proximity_grad = 2 * (cf - original)
        sparsity_loss = np.sum(np.abs(cf - original))
        sparsity_grad = np.sign(cf - original)
        
        total_loss = pred_loss + self.proximity_weight * proximity_loss + self.sparsity_weight * sparsity_loss
        total_grad = pred_grad + self.proximity_weight * proximity_grad + self.sparsity_weight * sparsity_grad
        return total_loss, total_grad
    
    def _apply_constraints(self, cf, original):
        """Apply feature constraints."""
        cf = cf.copy()
        for feature in self.immutable_features:
            if feature in self.feature_index:
                cf[self.feature_index[feature]] = original[self.feature_index[feature]]
        for feature, (min_val, max_val) in self.feature_ranges.items():
            if feature in self.feature_index:
                cf[self.feature_index[feature]] = np.clip(cf[self.feature_index[feature]], min_val, max_val)
        return cf
    
    def _get_prediction(self, instance):
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(instance.reshape(1, -1))[0, 1]
        return self.model.predict(instance.reshape(1, -1))[0]
    
    def _target_achieved(self, prediction, target_class, target_probability):
        if target_probability is not None:
            return abs(prediction - target_probability) < 0.05
        return (target_class == 1 and prediction > 0.5) or (target_class == 0 and prediction < 0.5)
    
    def _create_explanation(self, original, counterfactual, original_pred, cf_pred):
        """Create counterfactual explanation."""
        feature_changes = {}
        changed_features = 0
        for i, name in enumerate(self.feature_names):
            if abs(original[i] - counterfactual[i]) > 1e-6:
                changed_features += 1
                feature_changes[name] = {
                    "original": float(original[i]),
                    "counterfactual": float(counterfactual[i]),
                    "change": float(counterfactual[i] - original[i]),
                    "percent_change": float((counterfactual[i] - original[i]) / (abs(original[i]) + 1e-10) * 100)
                }
        distance = np.sqrt(np.sum((original - counterfactual) ** 2))
        feasibility = self._calculate_feasibility(original, counterfactual)
        return CounterfactualExplanation(
            original_instance=original, counterfactual_instance=counterfactual,
            original_prediction=original_pred, counterfactual_prediction=cf_pred,
            feature_changes=feature_changes, distance=distance,
            sparsity=changed_features, feasibility_score=feasibility,
            metadata={"proximity_weight": self.proximity_weight}
        )
    
    def _calculate_feasibility(self, original, counterfactual):
        changes = np.abs(counterfactual - original)
        if self.feature_ranges:
            normalized_changes = []
            for i, name in enumerate(self.feature_names):
                if name in self.feature_ranges:
                    min_val, max_val = self.feature_ranges[name]
                    range_val = max_val - min_val
                    normalized_changes.append(changes[i] / range_val if range_val > 0 else 0)
                else:
                    normalized_changes.append(changes[i])
            avg_change = np.mean(normalized_changes)
        else:
            avg_change = np.mean(changes)
        return max(0, 1 - avg_change)
```

---

## 6. Explanation Orchestrator

```python
# File: /app/xai/explanation_orchestrator.py

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
import numpy as np

logger = logging.getLogger(__name__)


class ExplanationMethod(Enum):
    """Available explanation methods."""
    SHAP = "shap"
    LIME = "lime"
    FEATURE_IMPORTANCE = "feature_importance"
    COUNTERFACTUAL = "counterfactual"


@dataclass
class UnifiedExplanation:
    """Unified explanation result."""
    method: str
    explanation_type: str
    instance_id: Optional[str]
    prediction: float
    explanation_data: Dict[str, Any]
    visualization_data: Dict[str, Any]
    confidence: float
    computation_time_ms: float
    metadata: Dict[str, Any]


class ExplanationOrchestrator:
    """Central orchestrator for all explanation methods."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.explainers = {}
        self.model_registry = {}
    
    def register_model(self, model_id: str, model: Any, feature_names: List[str],
                       model_type: str = "auto", training_data=None, metadata=None):
        """Register a model for explanation."""
        self.model_registry[model_id] = {
            "model": model, "feature_names": feature_names,
            "model_type": model_type, "training_data": training_data,
            "metadata": metadata or {}
        }
        self._initialize_explainers(model_id)
        logger.info(f"Registered model {model_id}")
    
    def _initialize_explainers(self, model_id: str):
        """Initialize explainers for registered model."""
        from app.xai.shap_engine import SHAPEngine, SHAPModelFactory
        from app.xai.lime_engine import LIMEEngine, LIMEDataType
        from app.xai.feature_importance import FeatureImportanceCalculator
        from app.xai.counterfactual_engine import CounterfactualGenerator
        
        model_info = self.model_registry[model_id]
        model = model_info["model"]
        feature_names = model_info["feature_names"]
        training_data = model_info["training_data"]
        
        self.explainers[model_id] = {}
        try:
            self.explainers[model_id]["shap"] = SHAPModelFactory.create_explainer(
                model, feature_names, training_data
            )
        except Exception as e:
            logger.warning(f"Could not initialize SHAP: {e}")
        try:
            if training_data is not None:
                self.explainers[model_id]["lime"] = LIMEEngine(
                    model, feature_names, data_type=LIMEDataType.TABULAR,
                    training_data=training_data
                )
        except Exception as e:
            logger.warning(f"Could not initialize LIME: {e}")
        try:
            self.explainers[model_id]["feature_importance"] = FeatureImportanceCalculator(model, feature_names)
        except Exception as e:
            logger.warning(f"Could not initialize Feature Importance: {e}")
        try:
            self.explainers[model_id]["counterfactual"] = CounterfactualGenerator(model, feature_names)
        except Exception as e:
            logger.warning(f"Could not initialize Counterfactual: {e}")
    
    def explain(self, model_id: str, instance: Any, method: ExplanationMethod = ExplanationMethod.SHAP,
                explanation_type: str = "local", num_features: int = 10,
                return_visualization: bool = True, **kwargs) -> UnifiedExplanation:
        """Generate explanation using specified method."""
        import time
        start_time = time.time()
        
        if model_id not in self.model_registry:
            raise ValueError(f"Model {model_id} not registered")
        
        model = self.model_registry[model_id]["model"]
        if hasattr(model, 'predict_proba'):
            prediction = model.predict_proba(instance.reshape(1, -1))[0, 1]
        else:
            prediction = model.predict(instance.reshape(1, -1))[0]
        
        explainer = self.explainers[model_id].get(method.value)
        if explainer is None:
            raise ValueError(f"Explainer {method.value} not available")
        
        explanation_data = {}
        visualization_data = {}
        
        if method == ExplanationMethod.SHAP:
            if explanation_type == "local":
                result = explainer.explain_local(instance, return_visualization)
                explanation_data = result.to_dict()
                if return_visualization:
                    visualization_data = {
                        "force_plot": explainer.get_force_plot_data(result),
                        "waterfall_plot": explainer.get_waterfall_plot_data(result)
                    }
            else:
                explanation_data = explainer.explain_global(instance)
        elif method == ExplanationMethod.LIME:
            result = explainer.explain(instance, num_features=num_features)
            explanation_data = result.to_dict()
        elif method == ExplanationMethod.FEATURE_IMPORTANCE:
            y = kwargs.get('y')
            results = explainer.get_all_importance_methods(instance, y)
            explanation_data = {m: r.to_dict() for m, r in results.items()}
        elif method == ExplanationMethod.COUNTERFACTUAL:
            target_class = kwargs.get('target_class')
            num_cf = kwargs.get('num_counterfactuals', 1)
            results = explainer.generate_counterfactual(instance, target_class=target_class, num_counterfactuals=num_cf)
            explanation_data = {f"counterfactual_{i}": cf.to_dict() for i, cf in enumerate(results)}
        
        computation_time = (time.time() - start_time) * 1000
        return UnifiedExplanation(
            method=method.value, explanation_type=explanation_type,
            instance_id=kwargs.get('instance_id'), prediction=float(prediction),
            explanation_data=explanation_data, visualization_data=visualization_data,
            confidence=1.0, computation_time_ms=computation_time,
            metadata={"model_id": model_id, "num_features": num_features}
        )
    
    def explain_multi_method(self, model_id: str, instance: Any, methods: List[ExplanationMethod], **kwargs):
        """Generate explanations using multiple methods."""
        explanations = {}
        for method in methods:
            try:
                explanations[method.value] = self.explain(model_id, instance, method, **kwargs)
            except Exception as e:
                logger.error(f"Failed {method.value}: {e}")
                explanations[method.value] = None
        return explanations
```

---

## 7. Visualization Components

```python
# File: /app/xai/visualization.py

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, List, Any


class ExplanationVisualizer:
    """Visualization components for XAI explanations."""
    
    @staticmethod
    def create_force_plot(shap_values, feature_values, feature_names, base_value, prediction, title="SHAP Force Plot"):
        """Create SHAP force plot."""
        sorted_indices = np.argsort(np.abs(shap_values))[::-1]
        features = [feature_names[i] for i in sorted_indices]
        values = shap_values[sorted_indices]
        colors = ['#ff4444' if v < 0 else '#44ff44' for v in values]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[base_value], y=['Base Value'], orientation='h', marker_color='#888888'))
        for i, (feature, value) in enumerate(zip(features, values)):
            fig.add_trace(go.Bar(x=[value], y=[feature], orientation='h', marker_color=colors[i]))
        fig.add_vline(x=prediction, line_dash="dash", line_color="black", annotation_text=f"Prediction: {prediction:.3f}")
        fig.update_layout(title=title, xaxis_title="SHAP Value", barmode='relative', height=max(400, len(features) * 30), showlegend=False)
        return fig.to_dict()
    
    @staticmethod
    def create_waterfall_plot(shap_values, feature_values, feature_names, base_value, prediction, max_features=10, title="SHAP Waterfall"):
        """Create SHAP waterfall plot."""
        sorted_indices = np.argsort(np.abs(shap_values))[::-1][:max_features]
        features = ['Base Value'] + [feature_names[i] for i in sorted_indices] + ['Prediction']
        values = [base_value] + shap_values[sorted_indices].tolist() + [0]
        measure = ['absolute'] + ['relative'] * len(sorted_indices) + ['total']
        
        fig = go.Figure(go.Waterfall(
            name="SHAP", orientation="v", measure=measure, x=features,
            textposition="outside", text=[f"{v:.3f}" for v in values],
            y=[base_value] + shap_values[sorted_indices].tolist() + [prediction],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#ff4444"}},
            increasing={"marker": {"color": "#44ff44"}},
            totals={"marker": {"color": "#4444ff"}}
        ))
        fig.update_layout(title=title, yaxis_title="Prediction Value", showlegend=False, height=500)
        return fig.to_dict()
    
    @staticmethod
    def create_feature_importance_plot(importance_data, title="Feature Importance"):
        """Create feature importance bar chart."""
        features = [d['feature'] for d in importance_data]
        importance = [d['importance'] for d in importance_data]
        fig = go.Figure(go.Bar(x=importance, y=features, orientation='h', marker_color='#3366cc'))
        fig.update_layout(title=title, xaxis_title="Importance", yaxis_title="Feature", height=max(400, len(features) * 25))
        return fig.to_dict()
    
    @staticmethod
    def create_lime_plot(feature_weights, prediction, title="LIME Explanation"):
        """Create LIME explanation bar chart."""
        features = [f for f, _ in feature_weights]
        weights = [w for _, w in feature_weights]
        colors = ['#ff4444' if w < 0 else '#44ff44' for w in weights]
        fig = go.Figure(go.Bar(x=weights, y=features, orientation='h', marker_color=colors))
        fig.update_layout(title=f"{title}<br>Prediction: {prediction:.3f}", xaxis_title="Weight", height=max(400, len(features) * 30))
        return fig.to_dict()
```

---

## 8. REST API Implementation

```python
# File: /app/api/explanation_api.py

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
import numpy as np
import json

from app.xai.explanation_orchestrator import ExplanationOrchestrator, ExplanationMethod
from app.xai.visualization import ExplanationVisualizer
from app.core.auth import get_current_user
from app.core.cache import cache_response

router = APIRouter(prefix="/xai", tags=["Explainable AI"])
orchestrator = ExplanationOrchestrator()


class ExplainRequest(BaseModel):
    model_id: str = Field(..., description="Registered model identifier")
    instance: List[float] = Field(..., description="Instance to explain")
    method: Literal["shap", "lime", "feature_importance", "counterfactual", "all"] = "shap"
    explanation_type: Literal["local", "global"] = "local"
    num_features: int = Field(10, ge=1, le=50)
    return_visualization: bool = True


class ExplanationResponse(BaseModel):
    success: bool
    explanation: Optional[Dict[str, Any]]
    visualization: Optional[Dict[str, Any]]
    computation_time_ms: float
    model_id: str
    method: str
    error: Optional[str] = None


@router.post("/explain", response_model=ExplanationResponse)
@cache_response(expire=3600)
async def generate_explanation(request: ExplainRequest, current_user: dict = Depends(get_current_user)):
    """Generate explanation for a model prediction."""
    try:
        import time
        start_time = time.time()
        
        method_map = {
            "shap": ExplanationMethod.SHAP,
            "lime": ExplanationMethod.LIME,
            "feature_importance": ExplanationMethod.FEATURE_IMPORTANCE,
            "counterfactual": ExplanationMethod.COUNTERFACTUAL
        }
        
        if request.method == "all":
            methods = [ExplanationMethod.SHAP, ExplanationMethod.LIME, ExplanationMethod.FEATURE_IMPORTANCE]
            explanations = orchestrator.explain_multi_method(
                model_id=request.model_id, instance=np.array(request.instance),
                methods=methods, explanation_type=request.explanation_type,
                num_features=request.num_features, return_visualization=request.return_visualization
            )
            explanation_data = {m: e.explanation_data if e else None for m, e in explanations.items()}
            visualization_data = {m: e.visualization_data if e else None for m, e in explanations.items()}
        else:
            explanation = orchestrator.explain(
                model_id=request.model_id, instance=np.array(request.instance),
                method=method_map[request.method], explanation_type=request.explanation_type,
                num_features=request.num_features, return_visualization=request.return_visualization
            )
            explanation_data = explanation.explanation_data
            visualization_data = explanation.visualization_data
        
        computation_time = (time.time() - start_time) * 1000
        return ExplanationResponse(
            success=True, explanation=explanation_data,
            visualization=visualization_data if request.return_visualization else None,
            computation_time_ms=computation_time, model_id=request.model_id, method=request.method
        )
    except Exception as e:
        return ExplanationResponse(
            success=False, explanation=None, visualization=None,
            computation_time_ms=0, model_id=request.model_id, method=request.method, error=str(e)
        )


@router.get("/methods")
async def list_available_methods(model_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """List available explanation methods."""
    all_methods = {
        "shap": {"name": "SHAP", "description": "SHapley Additive exPlanations",
                 "supports_local": True, "supports_global": True, "computation_time": "medium"},
        "lime": {"name": "LIME", "description": "Local Interpretable Model-agnostic Explanations",
                 "supports_local": True, "supports_global": False, "computation_time": "medium"},
        "feature_importance": {"name": "Feature Importance", "description": "Built-in and permutation importance",
                               "supports_local": False, "supports_global": True, "computation_time": "fast"},
        "counterfactual": {"name": "Counterfactual", "description": "What-if scenario explanations",
                          "supports_local": True, "supports_global": False, "computation_time": "slow"}
    }
    if model_id and model_id in orchestrator.explainers:
        available = orchestrator.explainers[model_id].keys()
        return {"model_id": model_id, "available_methods": list(available),
                "methods": {k: v for k, v in all_methods.items() if k in available}}
    return {"methods": all_methods}


@router.get("/health")
async def health_check():
    """Check XAI service health."""
    return {"status": "healthy", "registered_models": len(orchestrator.model_registry),
            "available_methods": ["shap", "lime", "feature_importance", "counterfactual"]}
```

---

## 9. Natural Language Explanations

```python
# File: /app/xai/natural_language.py

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class NaturalLanguageExplanation:
    summary: str
    key_factors: List[str]
    detailed_explanation: str
    recommendations: List[str]
    confidence_level: str
    target_audience: str


class NaturalLanguageGenerator:
    """Generate user-friendly natural language explanations."""
    
    AUDIENCE_LEVELS = {
        "executive": {"detail": "low", "technical_terms": False, "focus": "business_impact"},
        "analyst": {"detail": "medium", "technical_terms": True, "focus": "insights"},
        "technical": {"detail": "high", "technical_terms": True, "focus": "mechanics"},
        "regulatory": {"detail": "high", "technical_terms": True, "focus": "compliance"}
    }
    
    def __init__(self, audience: str = "analyst"):
        self.audience = audience
        self.config = self.AUDIENCE_LEVELS.get(audience, self.AUDIENCE_LEVELS["analyst"])
    
    def generate_explanation(self, prediction: float, shap_values=None, feature_names=None,
                             feature_values=None, lime_weights=None, counterfactual=None):
        """Generate natural language explanation."""
        summary = self._generate_summary(prediction)
        key_factors = self._generate_key_factors(shap_values, feature_names, feature_values, lime_weights)
        detailed = self._generate_detailed(prediction, shap_values, feature_names, feature_values, lime_weights, counterfactual)
        recommendations = self._generate_recommendations(prediction, key_factors, counterfactual)
        confidence = self._determine_confidence(prediction, key_factors)
        return NaturalLanguageExplanation(summary, key_factors, detailed, recommendations, confidence, self.audience)
    
    def _generate_summary(self, prediction: float) -> str:
        if self.audience == "executive":
            if prediction > 0.7:
                return f"High likelihood outcome ({prediction:.1%}). Consider proactive measures."
            elif prediction > 0.3:
                return f"Moderate risk ({prediction:.1%}). Monitoring recommended."
            return f"Low likelihood outcome ({prediction:.1%}). Current approach effective."
        elif self.audience == "regulatory":
            return f"Model prediction: {prediction:.4f}. Auditable explanation available."
        return f"Model predicts probability of {prediction:.3f} for positive class."
    
    def _generate_key_factors(self, shap_values, feature_names, feature_values, lime_weights):
        factors = []
        if shap_values is not None and feature_names is not None:
            indices = np.argsort(np.abs(shap_values))[::-1][:5]
            for idx in indices:
                feature = feature_names[idx]
                value = shap_values[idx]
                direction = "increases" if value > 0 else "decreases"
                magnitude = "significantly" if abs(value) > 0.3 else "moderately" if abs(value) > 0.1 else "slightly"
                if self.config["technical_terms"]:
                    factors.append(f"{feature} {direction} prediction by {abs(value):.3f}")
                else:
                    factors.append(f"{feature} {direction} the prediction {magnitude}")
        elif lime_weights is not None:
            for feature, weight in lime_weights[:5]:
                direction = "increases" if weight > 0 else "decreases"
                factors.append(f"{feature} {direction} prediction")
        return factors
    
    def _generate_detailed(self, prediction, shap_values, feature_names, feature_values, lime_weights, counterfactual):
        if self.config["detail"] == "low":
            return "See key factors for main drivers."
        parts = []
        if prediction > 0.7:
            parts.append(f"Strong positive prediction with {prediction:.1%} confidence.")
        elif prediction > 0.5:
            parts.append(f"Positive prediction with {prediction:.1%} confidence.")
        elif prediction > 0.3:
            parts.append(f"Leans negative with {(1-prediction):.1%} confidence.")
        else:
            parts.append(f"Strong negative prediction with {(1-prediction):.1%} confidence.")
        return "\n".join(parts)
    
    def _generate_recommendations(self, prediction, key_factors, counterfactual):
        recommendations = []
        if prediction > 0.7:
            recommendations.extend(["Consider immediate intervention", "Investigate top risk factors"])
        elif prediction > 0.5:
            recommendations.extend(["Monitor closely", "Review contributing factors"])
        else:
            recommendations.extend(["Continue current approach", "Maintain monitoring"])
        if counterfactual:
            recommendations.append("Review counterfactual scenarios")
        return recommendations
    
    def _determine_confidence(self, prediction, key_factors):
        if prediction < 0.2 or prediction > 0.8:
            return "High" if len(key_factors) >= 3 else "Medium"
        return "Low to Medium"
```

---

## 10. Regulatory Compliance

```python
# File: /app/xai/compliance.py

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json


@dataclass
class ComplianceRecord:
    record_id: str
    timestamp: datetime
    model_id: str
    model_version: str
    explanation_method: str
    explanation_data: Dict[str, Any]
    input_hash: str
    output_hash: str
    user_id: str
    regulatory_framework: str
    retention_period_days: int


class RegulatoryComplianceManager:
    """Manage regulatory compliance for XAI explanations."""
    
    REGULATORY_FRAMEWORKS = {
        "gdpr": {
            "right_to_explanation": True, "data_minimization": True,
            "retention_period": 2555, "audit_trail": True, "human_oversight": True
        },
        "ai_act_high_risk": {
            "right_to_explanation": True, "transparency": True, "human_oversight": True,
            "accuracy_monitoring": True, "retention_period": 3650, "audit_trail": True
        },
        "ai_act_limited_risk": {
            "right_to_explanation": True, "transparency": True,
            "retention_period": 1825, "audit_trail": True
        },
        "financial_services": {
            "model_documentation": True, "fairness_testing": True,
            "retention_period": 2555, "audit_trail": True, "model_validation": True
        },
        "healthcare": {
            "clinical_validation": True, "human_oversight": True,
            "retention_period": 3650, "audit_trail": True, "explainability": True
        }
    }
    
    def __init__(self, framework: str = "gdpr"):
        self.framework = framework
        self.config = self.REGULATORY_FRAMEWORKS.get(framework, self.REGULATORY_FRAMEWORKS["gdpr"])
        self.audit_log = []
    
    def validate_explanation(self, explanation: Dict, model_id: str, model_version: str) -> Dict:
        """Validate explanation for regulatory compliance."""
        result = {"compliant": True, "framework": self.framework, "checks": {}, "recommendations": []}
        if self.config.get("right_to_explanation"):
            has_exp = "explanation_data" in explanation and explanation["explanation_data"]
            result["checks"]["right_to_explanation"] = has_exp
            if not has_exp:
                result["compliant"] = False
                result["recommendations"].append("Provide meaningful explanation")
        if self.config.get("transparency"):
            result["checks"]["transparency"] = "method" in explanation
        return result
    
    def create_audit_record(self, model_id: str, model_version: str, explanation_method: str,
                           explanation_data: Dict, input_data: Any, user_id: str) -> ComplianceRecord:
        """Create compliance audit record."""
        input_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
        output_hash = hashlib.sha256(json.dumps(explanation_data, sort_keys=True).encode()).hexdigest()
        record = ComplianceRecord(
            record_id=self._generate_record_id(), timestamp=datetime.utcnow(),
            model_id=model_id, model_version=model_version, explanation_method=explanation_method,
            explanation_data=explanation_data, input_hash=input_hash, output_hash=output_hash,
            user_id=user_id, regulatory_framework=self.framework,
            retention_period_days=self.config.get("retention_period", 2555)
        )
        self.audit_log.append(record)
        return record
    
    def generate_compliance_report(self, model_id=None, start_date=None, end_date=None):
        """Generate compliance report."""
        records = self.audit_log
        if model_id:
            records = [r for r in records if r.model_id == model_id]
        if start_date:
            records = [r for r in records if r.timestamp >= start_date]
        if end_date:
            records = [r for r in records if r.timestamp <= end_date]
        return {
            "framework": self.framework,
            "summary": {"total_explanations": len(records), "unique_models": len(set(r.model_id for r in records))},
            "details": [{"record_id": r.record_id, "timestamp": r.timestamp.isoformat(),
                        "model_id": r.model_id, "method": r.explanation_method} for r in records]
        }
    
    def _generate_record_id(self) -> str:
        timestamp = datetime.utcnow().isoformat()
        return f"REC-{hashlib.sha256(timestamp.encode()).hexdigest()[:16]}"
```

---

## 11. Implementation Priority

| Phase | Component | Priority | Timeline |
|-------|-----------|----------|----------|
| Phase 1 | Core SHAP Engine | Critical | Week 1-2 |
| Phase 1 | Basic API Endpoints | Critical | Week 2-3 |
| Phase 1 | Feature Importance | High | Week 3-4 |
| Phase 2 | LIME Engine | High | Week 4-5 |
| Phase 2 | Visualization Layer | High | Week 5-6 |
| Phase 2 | Explanation Orchestrator | High | Week 6-7 |
| Phase 3 | Counterfactual Generator | Medium | Week 7-8 |
| Phase 3 | Natural Language | Medium | Week 8-9 |
| Phase 3 | Compliance Framework | Medium | Week 9-10 |
| Phase 4 | Performance Optimization | Low | Week 11-12 |

---

## 12. File Structure

```
/app/xai/
├── __init__.py
├── shap_engine.py              # SHAP implementation
├── lime_engine.py              # LIME implementation
├── feature_importance.py       # Feature importance
├── counterfactual_engine.py    # Counterfactual explanations
├── explanation_orchestrator.py # Unified interface
├── visualization.py            # Visualization components
├── natural_language.py         # NL explanations
├── compliance.py               # Regulatory compliance
└── utils.py                    # Utility functions

/app/api/
├── __init__.py
├── explanation_api.py          # REST API endpoints
└── shap_routes.py              # SHAP-specific routes

/app/core/
├── cache.py                    # Explanation caching
├── rate_limit.py               # Rate limiting
└── auth.py                     # Authentication
```

---

## 13. Summary

This comprehensive XAI framework for ResilienceAI provides:

1. **Multiple Explanation Methods**: SHAP, LIME, Feature Importance, Counterfactuals
2. **Model-Agnostic Design**: Works with any model type
3. **Unified API**: Consistent interface across all methods
4. **Rich Visualizations**: Interactive plots and dashboards
5. **Natural Language**: User-friendly explanations
6. **Regulatory Compliance**: GDPR, AI Act support
7. **Audit Trail**: Complete explanation history
8. **Performance**: Caching and optimization

The framework ensures transparency, builds user trust, and maintains regulatory compliance for all AI-driven decisions in ResilienceAI.
