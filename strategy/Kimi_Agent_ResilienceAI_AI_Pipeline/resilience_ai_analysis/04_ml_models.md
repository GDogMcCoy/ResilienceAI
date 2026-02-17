 met
            
        return result
    
    def _send_notification(self, message: str, level: str = "info"):
        """Send notification (placeholder for integration)."""
        # This would integrate with notification systems
        print(f"[{level.upper()}] {message}")


class RetrainingTriggerMonitor:
    """
    Monitor for retraining triggers.
    """
    
    def __init__(self, config: RetrainingConfig):
        self.config = config
        self.performance_history = []
        self.drift_history = []
        
    def check_performance_trigger(self, current_metrics: Dict[str, float],
                                   baseline_metrics: Dict[str, float]) -> bool:
        """Check if performance degradation triggers retraining."""
        primary_metric = self.config.promotion_metric
        
        if primary_metric not in current_metrics or primary_metric not in baseline_metrics:
            return False
        
        current = current_metrics[primary_metric]
        baseline = baseline_metrics[primary_metric]
        
        degradation = (baseline - current) / baseline if baseline > 0 else 0
        
        return degradation > self.config.performance_threshold
    
    def check_drift_trigger(self, drift_score: float) -> bool:
        """Check if data drift triggers retraining."""
        return drift_score > self.config.data_drift_threshold
    
    def check_data_volume_trigger(self, n_new_samples: int) -> bool:
        """Check if enough new data has accumulated."""
        return n_new_samples >= self.config.min_samples_since_last_train


# Integration with existing train_models.py
class EnhancedTrainingPipeline:
    """
    Enhanced training pipeline that integrates with existing train_models.py.
    """
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
    def train_with_enhancements(self, df: pd.DataFrame,
                                 use_ensemble: bool = True,
                                 use_tuning: bool = True,
                                 use_mlflow: bool = True) -> Dict[str, Any]:
        """
        Train models with all enhancements.
        
        Args:
            df: Training data
            use_ensemble: Use stacking ensemble
            use_tuning: Use hyperparameter tuning
            use_mlflow: Log to MLflow
            
        Returns:
            Training results
        """
        from .train_models import prepare_data
        from .ensemble_models import StackingEnsemble, EnsembleConfig
        from .hyperparameter_tuning import HyperparameterTuner, TuningConfig
        from .mlflow_tracker import MLflowTracker, ExperimentConfig
        
        results = {}
        
        # Initialize MLflow
        mlflow_tracker = None
        if use_mlflow:
            mlflow_config = ExperimentConfig(
                experiment_name="resilienceai_enhanced",
                tags={"version": "2.0", "type": "enhanced_training"}
            )
            mlflow_tracker = MLflowTracker(mlflow_config)
            mlflow_tracker.start_run(run_name="enhanced_training")
        
        try:
            # Prepare data
            X, y, le, feature_names = prepare_data(df)
            
            if mlflow_tracker:
                mlflow_tracker.log_params({
                    "n_samples": len(X),
                    "n_features": len(feature_names),
                    "classes": list(le.classes_)
                })
            
            # Hyperparameter tuning
            tuned_models = {}
            if use_tuning:
                print("\n" + "="*60)
                print("HYPERPARAMETER TUNING")
                print("="*60)
                
                tuning_config = TuningConfig(
                    n_trials=50,
                    cv_folds=5,
                    scoring="f1_macro"
                )
                
                for model_name in ["random_forest", "gradient_boosting", "xgboost"]:
                    tuner = HyperparameterTuner(tuning_config)
                    tune_results = tuner.tune(model_name, X, y)
                    tuned_models[model_name] = tuner._create_model(
                        model_name, tune_results["best_params"]
                    )
                    
                    if mlflow_tracker:
                        mlflow_tracker.log_params({f"{model_name}_best_params": tune_results["best_params"]})
                        mlflow_tracker.log_metrics({f"{model_name}_best_score": tune_results["best_score"]})
            
            # Train ensemble
            if use_ensemble:
                print("\n" + "="*60)
                print("TRAINING STACKING ENSEMBLE")
                print("="*60)
                
                from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
                from sklearn.linear_model import LogisticRegression
                
                base_models = {
                    "random_forest": tuned_models.get("random_forest", RandomForestClassifier(n_estimators=200, random_state=42)),
                    "gradient_boosting": tuned_models.get("gradient_boosting", GradientBoostingClassifier(n_estimators=200, random_state=42)),
                    "logistic_regression": LogisticRegression(max_iter=1000, random_state=42)
                }
                
                ensemble_config = EnsembleConfig(
                    base_models=base_models,
                    meta_learner=LogisticRegression(max_iter=1000, random_state=42),
                    n_folds=5
                )
                
                ensemble = StackingEnsemble(ensemble_config)
                ensemble.fit(X, y)
                
                # Save ensemble
                ensemble_path = self.models_dir / "ensemble_stacking.pkl"
                joblib.dump(ensemble, ensemble_path)
                
                if mlflow_tracker:
                    mlflow_tracker.log_model(
                        ensemble, "stacking_ensemble",
                        registered_model_name="resilienceai_stacking_ensemble"
                    )
                
                results["ensemble"] = ensemble
            
            # Log final artifacts
            if mlflow_tracker:
                mlflow_tracker.log_artifacts(str(self.models_dir))
            
            results["status"] = "success"
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            if mlflow_tracker:
                mlflow_tracker.log_params({"error": str(e)})
        
        finally:
            if mlflow_tracker:
                mlflow_tracker.end_run()
        
        return results
```

---

## 11. Feature Importance Tracking

### 11.1 Comprehensive Feature Importance Module

**New File:** `src/ml/feature_importance_tracker.py`

```python
"""
ResilienceAI - Feature Importance Tracking Module
Tracks feature importance over time and across models.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import joblib
import json
from collections import defaultdict


@dataclass
class FeatureImportanceConfig:
    """Configuration for feature importance tracking."""
    track_methods: List[str] = None
    top_k_features: int = 20
    stability_threshold: float = 0.1
    
    def __post_init__(self):
        if self.track_methods is None:
            self.track_methods = ["model", "permutation", "shap"]


class FeatureImportanceTracker:
    """
    Track feature importance across time and models.
    
    Features:
    - Multiple importance calculation methods
    - Temporal stability analysis
    - Feature ranking evolution
    - Importance drift detection
    """
    
    def __init__(self, feature_names: List[str], config: FeatureImportanceConfig):
        self.config = config
        self.feature_names = feature_names
        self.importance_history = []
        self.current_importance = {}
        
    def calculate_importance(self, model, X: np.ndarray, y: np.ndarray,
                             method: str = "model") -> pd.DataFrame:
        """
        Calculate feature importance using specified method.
        
        Args:
            model: Trained model
            X: Feature data
            y: Target labels
            method: "model", "permutation", or "shap"
            
        Returns:
            DataFrame with feature importances
        """
        if method == "model":
            return self._model_importance(model)
        elif method == "permutation":
            return self._permutation_importance(model, X, y)
        elif method == "shap":
            return self._shap_importance(model, X)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _model_importance(self, model) -> pd.DataFrame:
        """Get importance from model's built-in feature importance."""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_).mean(axis=0) if model.coef_.ndim > 1 else np.abs(model.coef_)
        else:
            importances = np.zeros(len(self.feature_names))
        
        return pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances,
            'method': 'model'
        }).sort_values('importance', ascending=False)
    
    def _permutation_importance(self, model, X: np.ndarray, 
                                 y: np.ndarray, n_repeats: int = 10) -> pd.DataFrame:
        """Calculate permutation importance."""
        from sklearn.inspection import permutation_importance
        
        result = permutation_importance(
            model, X, y, 
            n_repeats=n_repeats,
            random_state=42,
            scoring='f1_macro'
        )
        
        return pd.DataFrame({
            'feature': self.feature_names,
            'importance': result.importances_mean,
            'std': result.importances_std,
            'method': 'permutation'
        }).sort_values('importance', ascending=False)
    
    def _shap_importance(self, model, X: np.ndarray) -> pd.DataFrame:
        """Calculate SHAP importance."""
        try:
            import shap
            
            explainer = shap.TreeExplainer(model) if hasattr(model, 'tree_') else shap.KernelExplainer(model.predict, X[:100])
            shap_values = explainer.shap_values(X)
            
            if isinstance(shap_values, list):
                shap_values = np.abs(shap_values).mean(axis=0).mean(axis=0)
            else:
                shap_values = np.abs(shap_values).mean(axis=0)
            
            return pd.DataFrame({
                'feature': self.feature_names,
                'importance': shap_values,
                'method': 'shap'
            }).sort_values('importance', ascending=False)
        except ImportError:
            return pd.DataFrame({'feature': self.feature_names, 'importance': 0, 'method': 'shap'})
    
    def track_importance(self, model, X: np.ndarray, y: np.ndarray,
                         timestamp: Optional[datetime] = None):
        """Track importance for all methods."""
        timestamp = timestamp or datetime.now()
        
        importance_record = {
            'timestamp': timestamp,
            'methods': {}
        }
        
        for method in self.config.track_methods:
            try:
                importance_df = self.calculate_importance(model, X, y, method)
                importance_record['methods'][method] = importance_df.to_dict()
            except Exception as e:
                print(f"Failed to calculate {method} importance: {e}")
        
        self.importance_history.append(importance_record)
        
    def analyze_stability(self, feature: str, window: int = 5) -> Dict[str, float]:
        """Analyze importance stability for a feature."""
        if len(self.importance_history) < window:
            return {'stability': None, 'trend': 'insufficient_data'}
        
        # Get importance values over time
        values = []
        for record in self.importance_history[-window:]:
            for method, data in record['methods'].items():
                df = pd.DataFrame(data)
                feat_importance = df[df['feature'] == feature]['importance'].values
                if len(feat_importance) > 0:
                    values.append(feat_importance[0])
        
        if len(values) < 2:
            return {'stability': None, 'trend': 'insufficient_data'}
        
        # Calculate coefficient of variation
        mean_val = np.mean(values)
        std_val = np.std(values)
        cv = std_val / mean_val if mean_val > 0 else float('inf')
        
        # Determine trend
        if len(values) >= 3:
            trend = 'increasing' if values[-1] > values[0] else 'decreasing' if values[-1] < values[0] else 'stable'
        else:
            trend = 'unknown'
        
        return {
            'stability': 1 - min(cv, 1),  # Higher is more stable
            'coefficient_of_variation': cv,
            'mean_importance': mean_val,
            'std_importance': std_val,
            'trend': trend
        }
    
    def get_feature_ranking_evolution(self, top_k: int = 10) -> pd.DataFrame:
        """Get evolution of feature rankings over time."""
        rankings = []
        
        for record in self.importance_history:
            # Use first available method
            method = list(record['methods'].keys())[0] if record['methods'] else None
            if not method:
                continue
            
            df = pd.DataFrame(record['methods'][method])
            df = df.sort_values('importance', ascending=False).head(top_k)
            df['rank'] = range(1, len(df) + 1)
            df['timestamp'] = record['timestamp']
            
            rankings.append(df[['timestamp', 'feature', 'rank', 'importance']])
        
        if not rankings:
            return pd.DataFrame()
        
        return pd.concat(rankings, ignore_index=True)
    
    def detect_importance_drift(self, threshold: Optional[float] = None) -> List[Dict]:
        """Detect features with significant importance drift."""
        threshold = threshold or self.config.stability_threshold
        drifted_features = []
        
        for feature in self.feature_names:
            stability = self.analyze_stability(feature)
            if stability['stability'] is not None and stability['stability'] < threshold:
                drifted_features.append({
                    'feature': feature,
                    'stability': stability['stability'],
                    'trend': stability['trend'],
                    'recommendation': 'review' if stability['stability'] < threshold / 2 else 'monitor'
                })
        
        return sorted(drifted_features, key=lambda x: x['stability'])
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generate feature importance report."""
        report = f"""
{'='*70}
FEATURE IMPORTANCE TRACKING REPORT
{'='*70}

SUMMARY
-------
Total Tracking Periods: {len(self.importance_history)}
Features Tracked: {len(self.feature_names)}
Methods Used: {', '.join(self.config.track_methods)}

TOP FEATURES (Current)
----------------------
"""
        
        if self.importance_history:
            last_record = self.importance_history[-1]
            method = list(last_record['methods'].keys())[0]
            df = pd.DataFrame(last_record['methods'][method]).head(10)
            
            for _, row in df.iterrows():
                report += f"  {row['feature']:30s}: {row['importance']:.4f}\n"
        
        # Feature stability
        report += """
FEATURE STABILITY ANALYSIS
--------------------------
"""
        
        for feature in self.feature_names[:10]:
            stability = self.analyze_stability(feature)
            if stability['stability'] is not None:
                report += f"  {feature:30s}: stability={stability['stability']:.2f}, trend={stability['trend']}\n"
        
        # Drift detection
        drifted = self.detect_importance_drift()
        if drifted:
            report += """
IMPORTANCE DRIFT DETECTED
-------------------------
"""
            for feat in drifted[:5]:
                report += f"  {feat['feature']:30s}: stability={feat['stability']:.2f} ({feat['recommendation']})\n"
        
        report += f"""
{'='*70}
"""
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
        
        return report
    
    def save(self, path: str):
        """Save tracker state."""
        joblib.dump({
            'config': self.config,
            'feature_names': self.feature_names,
            'importance_history': self.importance_history
        }, path)
    
    @classmethod
    def load(cls, path: str) -> 'FeatureImportanceTracker':
        """Load tracker state."""
        data = joblib.load(path)
        tracker = cls(data['feature_names'], data['config'])
        tracker.importance_history = data['importance_history']
        return tracker
```

---

## 12. MLOps Pipeline Design

### 12.1 Complete MLOps Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESILIENCEAI MLOps PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  DATA INGESTION LAYER                                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ FEMA API    │  │ Census API  │  │ NOAA API    │  │ HIFLD API   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         └─────────────────┴─────────────────┴─────────────────┘              │
│                                   │                                          │
│                         ┌─────────▼─────────┐                               │
│                         │  Data Pipeline    │                               │
│                         │  src/pipeline/    │                               │
│                         └─────────┬─────────┘                               │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│  FEATURE ENGINEERING LAYER                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  src/feature_engineering.py                                         │   │
│  │  - Demographic features                                             │   │
│  │  - Infrastructure features                                          │   │
│  │  - Disaster history features                                        │   │
│  │  - Composite indices                                                │   │
│  └────────────────────────┬────────────────────────────────────────────┘   │
│                           │                                                │
│  ┌────────────────────────▼────────────────────────────────────────────┐   │
│  │  Feature Store (Future)                                             │   │
│  │  - Online features (real-time)                                      │   │
│  │  - Offline features (batch)                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│  MODEL TRAINING LAYER                                                        │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  src/ml/train_models.py (Enhanced)                                  │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │   Random    │  │  Gradient   │  │   XGBoost   │  │  LightGBM  │ │   │
│  │  │   Forest    │  │   Boosting  │  │             │  │            │ │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │   │
│  │         └─────────────────┴─────────────────┴───────────────┘       │   │
│  │                           │                                         │   │
│  │              ┌────────────▼────────────┐                            │   │
│  │              │  Stacking Ensemble      │                            │   │
│  │              │  src/ml/ensemble_models │                            │   │
│  │              └────────────┬────────────┘                            │   │
│  └───────────────────────────┼─────────────────────────────────────────┘   │
│                              │                                              │
│  ┌───────────────────────────▼─────────────────────────────────────────┐   │
│  │  Hyperparameter Tuning                                               │   │
│  │  src/ml/hyperparameter_tuning.py                                     │   │
│  │  - Optuna Bayesian Optimization                                      │   │
│  │  - Multi-model parallel tuning                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  AutoML (Optional)                                                   │   │
│  │  src/ml/automl.py                                                    │   │
│  │  - TPOT / Auto-sklearn integration                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│  MODEL VALIDATION LAYER                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Cross-Validation                                                    │   │
│  │  - Stratified K-Fold                                                 │   │
│  │  - Time-series CV (for temporal data)                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Model Explainability                                                │   │
│  │  src/ml/explainability.py                                            │   │
│  │  - SHAP global/local explanations                                    │   │
│  │  - LIME local explanations                                           │   │
│  │  - Feature interaction analysis                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│  MODEL REGISTRY (MLflow)                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  src/ml/mlflow_tracker.py                                            │   │
│  │                                                                     │   │
│  │  Experiment Tracking                                                 │   │
│  │  ├── Parameters                                                      │   │
│  │  ├── Metrics                                                         │   │
│  │  ├── Artifacts (plots, reports)                                      │   │
│  │  └── Models                                                          │   │
│  │                                                                     │   │
│  │  Model Registry                                                      │   │
│  │  ├── Versioning                                                      │   │
│  │  ├── Staging → Production                                            │   │
│  │  └── Tags & Annotations                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│  DEPLOYMENT LAYER                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Model Serving                                                       │   │
│  │  ├── Batch Prediction                                                │   │
│  │  └── Real-time API (FastAPI/Flask)                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  A/B Testing                                                         │   │
│  │  src/ml/ab_testing.py                                                │   │
│  │  ├── Traffic Splitting                                               │   │
│  │  ├── Statistical Testing                                             │   │
│  │  └── Winner Selection                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│  MONITORING LAYER                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Drift Detection                                                     │   │
│  │  src/ml/drift_detection.py                                           │   │
│  │  ├── Data Drift (feature distributions)                              │   │
│  │  ├── Concept Drift (target distribution)                             │   │
│  │  ├── Prediction Drift (model outputs)                                │   │
│  │  └── Performance Drift (accuracy degradation)                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Performance Monitoring                                              │   │
│  │  ├── Accuracy tracking                                               │   │
│  │  ├── Latency monitoring                                              │   │
│  │  └── Error analysis                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Feature Importance Tracking                                         │   │
│  │  src/ml/feature_importance_tracker.py                                │   │
│  │  ├── Importance evolution                                            │   │
│  │  ├── Stability analysis                                              │   │
│  │  └── Drift detection                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│  RETRAINING LAYER                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Automated Retraining                                                │   │
│  │  src/ml/auto_retrain.py                                              │   │
│  │  ├── Scheduled (cron-based)                                          │   │
│  │  ├── Trigger-based (drift/performance)                               │   │
│  │  └── Online Learning (incremental updates)                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 12.2 Integration Points with Existing Code

| New Component | Integrates With | Integration Method |
|--------------|-----------------|-------------------|
| `ensemble_models.py` | `train_models.py` | Replace model dictionary with StackingEnsemble |
| `hyperparameter_tuning.py` | `train_models.py` | Add tuning step before model training |
| `explainability.py` | `train_models.py`, Dashboard | Generate explanations after training |
| `mlflow_tracker.py` | All training modules | Wrap training calls with MLflow logging |
| `drift_detection.py` | `realtime_pipeline.py` | Monitor incoming data for drift |
| `ab_testing.py` | Prediction API | Route traffic between model versions |
| `auto_retrain.py` | Scheduler/Cron | Trigger retraining jobs |
| `feature_importance_tracker.py` | `train_models.py` | Track importance after each training |

---

## 13. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)
1. **Enhanced Ensemble** - Implement stacking ensemble (`ensemble_models.py`)
2. **Hyperparameter Tuning** - Add Optuna integration (`hyperparameter_tuning.py`)
3. **Model Explainability** - Full SHAP/LIME support (`explainability.py`)

### Phase 2: MLOps Core (Weeks 3-4)
4. **MLflow Integration** - Experiment tracking and model registry (`mlflow_tracker.py`)
5. **Feature Importance Tracking** - Temporal importance analysis (`feature_importance_tracker.py`)
6. **A/B Testing Framework** - Model comparison infrastructure (`ab_testing.py`)

### Phase 3: Production Monitoring (Weeks 5-6)
7. **Drift Detection** - Data and concept drift monitoring (`drift_detection.py`)
8. **Performance Monitoring** - Continuous performance tracking
9. **Automated Retraining** - Trigger-based retraining pipeline (`auto_retrain.py`)

### Phase 4: Advanced Features (Weeks 7-8)
10. **AutoML Integration** - TPOT/Auto-sklearn support (`automl.py`)
11. **Online Learning** - Incremental model updates (`online_learning.py`)
12. **Advanced Ensembles** - Blending, weighted voting

---

## 14. File Structure Summary

```
resilienceai/
├── src/
│   ├── ml/                          # NEW: ML modules
│   │   ├── __init__.py
│   │   ├── ensemble_models.py       # Stacking, blending ensembles
│   │   ├── automl.py                # AutoML integration
│   │   ├── explainability.py        # SHAP, LIME explanations
│   │   ├── hyperparameter_tuning.py # Optuna optimization
│   │   ├── drift_detection.py       # Data/concept drift
│   │   ├── ab_testing.py            # A/B testing framework
│   │   ├── mlflow_tracker.py        # MLflow integration
│   │   ├── online_learning.py       # Incremental learning
│   │   ├── auto_retrain.py          # Automated retraining
│   │   ├── feature_importance_tracker.py  # Importance tracking
│   │   └── model_configs.py         # Model configurations
│   │
│   ├── train_models.py              # EXISTING (to be enhanced)
│   ├── predictive_models.py         # EXISTING (Prophet/ARIMA)
│   ├── feature_engineering.py       # EXISTING
│   └── ...
│
├── models/
│   ├── versions/                    # NEW: Versioned models
│   │   ├── model_v20240217_120000/
│   │   ├── model_v20240218_080000/
│   │   └── manifest.json
│   │
│   ├── ensemble_stacking.pkl        # NEW: Stacking ensemble
│   ├── best_model.pkl               # EXISTING
│   └── ...
│
├── outputs/
│   ├── explainability/              # NEW: SHAP/LIME outputs
│   ├── drift_reports/               # NEW: Drift detection reports
│   └── figures/                     # EXISTING
│
├── mlruns/                          # NEW: MLflow tracking
│
└── config.py                        # EXISTING (add ML config)
```

---

## 15. Dependencies

### Required New Dependencies

```txt
# requirements-ml-enhanced.txt

# Ensemble & Advanced Models
xgboost>=1.7.0
lightgbm>=4.0.0
catboost>=1.2.0

# Hyperparameter Tuning
optuna>=3.3.0

# Explainability
shap>=0.42.0
lime>=0.2.0

# MLflow
mlflow>=2.8.0

# Drift Detection
alibi-detect>=0.11.0

# Online Learning
river>=0.19.0

# AutoML (optional)
tpot>=0.12.0
auto-sklearn>=0.15.0  # Linux only

# Statistical Tests
scipy>=1.11.0

# Utilities
schedule>=1.2.0
joblib>=1.3.0
```

---

## 16. Summary

This comprehensive ML enhancement plan for ResilienceAI provides:

1. **Advanced Ensemble Methods** - Stacking, blending, and weighted voting for improved prediction accuracy
2. **AutoML Integration** - Automated model selection and hyperparameter optimization
3. **Model Explainability** - SHAP and LIME for transparent, interpretable predictions
4. **MLOps Infrastructure** - MLflow for experiment tracking and model versioning
5. **Production Monitoring** - Drift detection, performance tracking, and A/B testing
6. **Automated Retraining** - Scheduled and trigger-based model updates
7. **Online Learning** - Incremental model adaptation for streaming data

The implementation follows a phased approach, starting with foundational enhancements and progressing to advanced production features. All components are designed to integrate seamlessly with the existing ResilienceAI codebase.

---

*Document Version: 1.0*
*Last Updated: 2026-02-17*
*Author: ML Engineering Team*
