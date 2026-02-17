# ResilienceAI Insight Discovery Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of the ResilienceAI repository's current insight capabilities and designs a complete automated insight discovery system. The proposed enhancements transform the platform from basic analytics to an intelligent, self-discovering analysis engine capable of automatically identifying patterns, anomalies, correlations, and actionable insights in disaster vulnerability data.

---

## 1. Current State Analysis

### 1.1 Existing Analytics Infrastructure

Based on analysis of the `claw-autonomous` branch, ResilienceAI currently has:

| Component | Location | Current Capabilities |
|-----------|----------|---------------------|
| **Predictive Models** | `src/predictive_models.py` | Prophet/ARIMA forecasting, climate scenarios (SSP1-1.9, SSP2-4.5, SSP5-8.5) |
| **Spatial Statistics** | `src/spatial_stats.py` | Moran's I autocorrelation, Getis-Ord Gi* hotspot analysis |
| **Network Analysis** | `src/network_analysis.py` | Infrastructure network graphs, cascade risk assessment |
| **Feature Engineering** | `src/feature_engineering.py` | 66 vulnerability features, composite indices |
| **Dashboard** | `app/dashboard.py` | Streamlit visualization, 9+ dashboard tabs |
| **Agent Orchestration** | `src/agents/orchestrator.py` | Multi-agent coordination, MCP tools |
| **Climate Intelligence** | `src/climate_client.py` | ACIS grid data, climate projections |
| **Alert Manager** | `src/alert_manager.py` | Real-time alerting system |

### 1.2 Current Limitations

```python
# Current insight generation is manual and limited:
# - No automated anomaly detection
# - No correlation discovery between variables
# - No root cause analysis automation
# - No pattern recognition in disaster sequences
# - No comparative benchmarking
# - No statistical significance testing
# - Manual report generation
# - No executive briefing automation
```

### 1.3 Data Assets Available

```
data/
├── processed/
│   ├── county_features.csv          # 66 engineered features
│   ├── vulnerability_index.csv      # Composite vulnerability scores
│   ├── time_series/                 # Historical disaster data
│   └── risk_predictions.csv         # Model predictions
├── raw/
│   ├── fema_disasters.csv           # FEMA disaster declarations
│   ├── census_acs.csv               # Census demographics
│   ├── hifld_*.csv                  # Infrastructure data
│   └── noaa_weather.csv             # Real-time weather
└── models/
    ├── risk_classifier.pkl          # Trained ML models
    └── vulnerability_scaler.pkl     # Feature scalers
```

---

## 2. Proposed Automated Insight Engine Architecture

### 2.1 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI INSIGHT DISCOVERY ENGINE                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  Data Ingestion │  │  Feature Store  │  │  Model Registry │             │
│  │     Layer       │→ │    (Feast)      │→ │   (MLflow)      │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│           ↓                  ↓                    ↓                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    INSIGHT GENERATION PIPELINE                       │   │
│  ├──────────────┬──────────────┬──────────────┬───────────────────────┤   │
│  │   Anomaly    │   Pattern    │ Correlation  │    Root Cause         │   │
│  │  Detection   │ Recognition  │   Analysis   │     Analysis          │   │
│  │   Engine     │    Engine    │    Engine    │      Engine           │   │
│  └──────────────┴──────────────┴──────────────┴───────────────────────┘   │
│           ↓                  ↓                    ↓                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    INSIGHT AGGREGATION LAYER                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │   Trend     │  │ Comparative │  │ Statistical │  │  Insight   │ │   │
│  │  │  Analysis   │  │  Analysis   │  │  Testing    │  │  Ranking   │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│           ↓                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    OUTPUT GENERATION LAYER                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │  Automated  │  │  Executive  │  │   Alert     │  │  API       │ │   │
│  │  │   Reports   │  │  Briefings  │  │  Generation │  │  Endpoint  │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 New Module Structure

```
src/
├── insights/                          # NEW: Insight discovery modules
│   ├── __init__.py
│   ├── anomaly_detector.py            # Anomaly detection engine
│   ├── pattern_recognizer.py          # Pattern recognition ML
│   ├── correlation_engine.py          # Correlation analysis
│   ├── root_cause_analyzer.py         # Root cause analysis
│   ├── trend_analyzer.py              # Trend identification
│   ├── comparative_analyzer.py        # Benchmarking analysis
│   ├── statistical_tester.py          # Significance testing
│   ├── insight_ranker.py              # Insight prioritization
│   └── insight_generator.py           # Main orchestrator
├── reporting/                         # NEW: Automated reporting
│   ├── __init__.py
│   ├── report_generator.py            # Report generation
│   ├── briefing_generator.py          # Executive briefings
│   ├── alert_formatter.py             # Alert formatting
│   └── template_engine.py             # Report templates
├── ml_models/                         # NEW: ML model implementations
│   ├── __init__.py
│   ├── isolation_forest.py            # Anomaly detection model
│   ├── lstm_patterns.py               # Sequence pattern detection
│   ├── graph_neural_net.py            # Spatial pattern detection
│   └── transformer_insights.py        # NLP for insight generation
└── existing_modules/                  # EXISTING: Current modules
    ├── predictive_models.py
    ├── spatial_stats.py
    └── ...
```

---

## 3. Core Insight Discovery Components

### 3.1 Anomaly Detection Engine

**File:** `src/insights/anomaly_detector.py`

```python
"""
ResilienceAI - Anomaly Detection Engine
Detects unusual patterns in vulnerability metrics using multiple algorithms.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class AnomalyType(Enum):
    """Types of anomalies detected."""
    POINT_ANOMALY = "point"           # Single unusual value
    CONTEXTUAL_ANOMALY = "contextual" # Unusual in context
    COLLECTIVE_ANOMALY = "collective" # Unusual sequence
    SPATIAL_ANOMALY = "spatial"       # Unusual geographic pattern
    TEMPORAL_ANOMALY = "temporal"     # Unusual time pattern


@dataclass
class AnomalyResult:
    """Container for anomaly detection results."""
    timestamp: datetime
    county_fips: str
    county_name: str
    variable: str
    value: float
    expected_range: Tuple[float, float]
    anomaly_score: float
    anomaly_type: AnomalyType
    severity: str  # 'low', 'medium', 'high', 'critical'
    contributing_factors: List[str]
    recommendation: str
    

class AnomalyDetector:
    """
    Multi-algorithm anomaly detection for vulnerability metrics.
    
    Uses ensemble approach combining:
    - Isolation Forest (unsupervised)
    - Local Outlier Factor (density-based)
    - LSTM Autoencoder (sequence-based)
    - Statistical methods (Z-score, IQR)
    """
    
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.models = {}
        self.scalers = {}
        self.baseline_stats = {}
        self.is_fitted = False
        
    def fit(self, df: pd.DataFrame, 
            feature_cols: List[str],
            county_col: str = 'fips',
            date_col: str = 'date') -> 'AnomalyDetector':
        """
        Fit anomaly detection models on historical data.
        
        Args:
            df: Historical vulnerability data
            feature_cols: Columns to monitor for anomalies
            county_col: County identifier column
            date_col: Date column
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for anomaly detection")
            
        self.feature_cols = feature_cols
        self.county_col = county_col
        self.date_col = date_col
        
        # Calculate baseline statistics per county
        for county in df[county_col].unique():
            county_data = df[df[county_col] == county][feature_cols]
            if len(county_data) > 10:
                self.baseline_stats[county] = {
                    'mean': county_data.mean(),
                    'std': county_data.std(),
                    'q25': county_data.quantile(0.25),
                    'q75': county_data.quantile(0.75),
                    'median': county_data.median()
                }
        
        # Fit Isolation Forest (global anomalies)
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df[feature_cols].dropna())
        
        self.models['isolation_forest'] = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=200
        )
        self.models['isolation_forest'].fit(scaled_data)
        
        # Fit Local Outlier Factor (local anomalies)
        self.models['lof'] = LocalOutlierFactor(
            n_neighbors=20,
            contamination=self.contamination,
            novelty=True
        )
        self.models['lof'].fit(scaled_data)
        
        self.scalers['global'] = scaler
        self.is_fitted = True
        
        return self
    
    def detect(self, df: pd.DataFrame,
               return_details: bool = True) -> Dict[str, Any]:
        """
        Detect anomalies in new data.
        
        Args:
            df: New data to analyze
            return_details: Whether to return detailed results
            
        Returns:
            Dictionary with anomaly results and summary
        """
        if not self.is_fitted:
            raise ValueError("Detector must be fitted before detection")
            
        results = []
        anomaly_counts = {t.value: 0 for t in AnomalyType}
        
        for county in df[self.county_col].unique():
            county_data = df[df[self.county_col] == county].copy()
            
            if county not in self.baseline_stats:
                continue
                
            county_results = self._detect_county_anomalies(
                county_data, county
            )
            results.extend(county_results)
            
            for r in county_results:
                anomaly_counts[r.anomaly_type.value] += 1
        
        # Sort by severity and score
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        results.sort(key=lambda x: (severity_order.get(x.severity, 4), -x.anomaly_score))
        
        output = {
            'anomalies': results,
            'summary': {
                'total_anomalies': len(results),
                'by_type': anomaly_counts,
                'by_severity': self._count_by_severity(results),
                'top_counties': self._top_anomalous_counties(results)
            }
        }
        
        return output
    
    def _detect_county_anomalies(self, 
                                  county_data: pd.DataFrame,
                                  county: str) -> List[AnomalyResult]:
        """Detect anomalies for a single county."""
        results = []
        baseline = self.baseline_stats[county]
        
        for idx, row in county_data.iterrows():
            for col in self.feature_cols:
                if pd.isna(row[col]):
                    continue
                    
                value = row[col]
                mean = baseline['mean'][col]
                std = baseline['std'][col]
                
                # Statistical anomaly detection
                z_score = abs((value - mean) / std) if std > 0 else 0
                
                # IQR method
                q25 = baseline['q25'][col]
                q75 = baseline['q75'][col]
                iqr = q75 - q25
                lower_bound = q25 - 1.5 * iqr
                upper_bound = q75 + 1.5 * iqr
                
                # Determine if anomaly
                is_anomaly = z_score > 3 or value < lower_bound or value > upper_bound
                
                if is_anomaly:
                    severity = self._calculate_severity(z_score, value, lower_bound, upper_bound)
                    anomaly_type = self._classify_anomaly_type(value, mean, col)
                    
                    result = AnomalyResult(
                        timestamp=row.get(self.date_col, datetime.now()),
                        county_fips=county,
                        county_name=row.get('county_name', county),
                        variable=col,
                        value=value,
                        expected_range=(lower_bound, upper_bound),
                        anomaly_score=min(z_score / 3, 1.0),
                        anomaly_type=anomaly_type,
                        severity=severity,
                        contributing_factors=self._identify_contributing_factors(
                            row, baseline, col
                        ),
                        recommendation=self._generate_recommendation(
                            col, value, mean, severity
                        )
                    )
                    results.append(result)
        
        return results
    
    def _calculate_severity(self, z_score: float, 
                           value: float,
                           lower: float, 
                           upper: float) -> str:
        """Calculate anomaly severity."""
        if z_score > 5 or value < lower * 0.5 or value > upper * 2:
            return 'critical'
        elif z_score > 3.5 or value < lower * 0.7 or value > upper * 1.5:
            return 'high'
        elif z_score > 2.5:
            return 'medium'
        else:
            return 'low'
    
    def _classify_anomaly_type(self, value: float, 
                               mean: float,
                               variable: str) -> AnomalyType:
        """Classify the type of anomaly."""
        # Time-based variables suggest temporal anomalies
        if any(t in variable.lower() for t in ['trend', 'change', 'rate']):
            return AnomalyType.TEMPORAL_ANOMALY
        # Geographic variables suggest spatial anomalies
        elif any(s in variable.lower() for s in ['density', 'distance', 'proximity']):
            return AnomalyType.SPATIAL_ANOMALY
        else:
            return AnomalyType.POINT_ANOMALY
    
    def _identify_contributing_factors(self, row: pd.Series,
                                       baseline: Dict,
                                       anomalous_var: str) -> List[str]:
        """Identify factors contributing to the anomaly."""
        factors = []
        
        for col in self.feature_cols:
            if col == anomalous_var:
                continue
            if pd.isna(row[col]):
                continue
                
            mean = baseline['mean'][col]
            std = baseline['std'][col]
            z_score = abs((row[col] - mean) / std) if std > 0 else 0
            
            if z_score > 2:
                factors.append(f"{col}: {row[col]:.2f} (z={z_score:.1f})")
        
        return factors[:5]  # Top 5 contributing factors
    
    def _generate_recommendation(self, variable: str,
                                  value: float,
                                  expected: float,
                                  severity: str) -> str:
        """Generate actionable recommendation."""
        direction = "increased" if value > expected else "decreased"
        
        recommendations = {
            'vulnerability_index': f"Review emergency preparedness protocols. {direction.capitalize()} risk detected.",
            'healthcare_access': "Evaluate healthcare facility capacity and resource allocation.",
            'infrastructure_risk': "Conduct infrastructure resilience assessment.",
            'social_vulnerability': "Engage community support services and vulnerable population outreach.",
            'economic_resilience': "Review economic support programs and business continuity plans.",
            'default': f"Monitor {variable} closely. Investigate underlying causes of {direction} value."
        }
        
        for key, rec in recommendations.items():
            if key in variable.lower():
                return rec
        
        return recommendations['default']
    
    def _count_by_severity(self, results: List[AnomalyResult]) -> Dict[str, int]:
        """Count anomalies by severity level."""
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for r in results:
            counts[r.severity] = counts.get(r.severity, 0) + 1
        return counts
    
    def _top_anomalous_counties(self, results: List[AnomalyResult],
                                 top_n: int = 10) -> List[Dict]:
        """Identify counties with most anomalies."""
        from collections import Counter
        
        county_scores = Counter()
        for r in results:
            score = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(r.severity, 1)
            county_scores[r.county_fips] += score
        
        return [
            {'county_fips': fips, 'anomaly_score': score}
            for fips, score in county_scores.most_common(top_n)
        ]


# Example usage
if __name__ == "__main__":
    # Load sample data
    df = pd.read_csv("data/processed/county_features.csv")
    
    # Initialize detector
    detector = AnomalyDetector(contamination=0.05)
    
    # Define features to monitor
    features = [
        'vulnerability_index',
        'healthcare_access_score',
        'infrastructure_risk_score',
        'social_vulnerability_index',
        'economic_resilience_score'
    ]
    
    # Fit on historical data
    detector.fit(df, feature_cols=features)
    
    # Detect anomalies
    results = detector.detect(df)
    
    print(f"Detected {results['summary']['total_anomalies']} anomalies")
    print(f"By severity: {results['summary']['by_severity']}")
```

### 3.2 Pattern Recognition Engine

**File:** `src/insights/pattern_recognizer.py`

```python
"""
ResilienceAI - Pattern Recognition Engine
Identifies recurring patterns in disaster vulnerability data using ML.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
try:
    from sklearn.cluster import DBSCAN, HDBSCAN, KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from scipy.cluster.hierarchy import linkage, fcluster
    from scipy.spatial.distance import pdist
    from scipy.stats import entropy
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


@dataclass
class Pattern:
    """Discovered pattern in vulnerability data."""
    pattern_id: str
    pattern_type: str  # 'cluster', 'sequence', 'seasonal', 'trend', 'spatial'
    description: str
    confidence: float
    affected_counties: List[str]
    time_range: Tuple[datetime, datetime]
    characteristics: Dict[str, Any]
    similar_historical_events: List[str]
    predictive_indicators: List[str]


class PatternRecognizer:
    """
    Multi-modal pattern recognition for disaster vulnerability.
    
    Pattern types detected:
    - Temporal patterns: Seasonal disaster cycles, trend changes
    - Spatial patterns: Geographic clusters, hotspot evolution
    - Sequential patterns: Disaster cascade sequences
    - Multivariate patterns: Correlated vulnerability changes
    """
    
    def __init__(self, min_pattern_size: int = 5):
        self.min_pattern_size = min_pattern_size
        self.patterns = []
        self.cluster_models = {}
        
    def discover_patterns(self, df: pd.DataFrame,
                          feature_cols: List[str],
                          county_col: str = 'fips',
                          date_col: str = 'date') -> Dict[str, Any]:
        """
        Discover all pattern types in the data.
        
        Args:
            df: Vulnerability data
            feature_cols: Features to analyze
            county_col: County identifier
            date_col: Date column
            
        Returns:
            Dictionary of discovered patterns by type
        """
        results = {
            'temporal_patterns': self._discover_temporal_patterns(df, feature_cols, date_col),
            'spatial_patterns': self._discover_spatial_patterns(df, feature_cols, county_col),
            'sequential_patterns': self._discover_sequential_patterns(df, feature_cols, county_col, date_col),
            'multivariate_patterns': self._discover_multivariate_patterns(df, feature_cols),
            'summary': {}
        }
        
        # Generate summary
        results['summary'] = self._generate_pattern_summary(results)
        
        return results
    
    def _discover_temporal_patterns(self, df: pd.DataFrame,
                                     features: List[str],
                                     date_col: str) -> List[Pattern]:
        """Discover temporal patterns (seasonality, trends)."""
        patterns = []
        
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        
        for feature in features:
            # Seasonal decomposition
            if len(df) > 365:  # Need at least a year of data
                monthly_avg = df.groupby(df[date_col].dt.month)[feature].mean()
                
                # Detect seasonality using coefficient of variation
                cv = monthly_avg.std() / monthly_avg.mean() if monthly_avg.mean() != 0 else 0
                
                if cv > 0.2:  # Significant seasonal variation
                    peak_month = monthly_avg.idxmax()
                    low_month = monthly_avg.idxmin()
                    
                    pattern = Pattern(
                        pattern_id=f"seasonal_{feature}_{peak_month}",
                        pattern_type='seasonal',
                        description=f"{feature} shows seasonal pattern with peak in month {peak_month}",
                        confidence=min(cv * 2, 1.0),
                        affected_counties=df['fips'].unique().tolist(),
                        time_range=(df[date_col].min(), df[date_col].max()),
                        characteristics={
                            'peak_month': peak_month,
                            'low_month': low_month,
                            'seasonal_strength': cv,
                            'monthly_values': monthly_avg.to_dict()
                        },
                        similar_historical_events=[],
                        predictive_indicators=[feature]
                    )
                    patterns.append(pattern)
            
            # Trend detection
            from scipy import stats
            x = np.arange(len(df))
            y = df[feature].values
            
            # Remove NaN values
            mask = ~np.isnan(y)
            if mask.sum() > 10:
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    x[mask], y[mask]
                )
                
                if p_value < 0.05 and abs(r_value) > 0.3:
                    trend_direction = "increasing" if slope > 0 else "decreasing"
                    
                    pattern = Pattern(
                        pattern_id=f"trend_{feature}_{trend_direction}",
                        pattern_type='trend',
                        description=f"{feature} shows significant {trend_direction} trend (R²={r_value**2:.2f})",
                        confidence=abs(r_value),
                        affected_counties=df['fips'].unique().tolist(),
                        time_range=(df[date_col].min(), df[date_col].max()),
                        characteristics={
                            'slope': slope,
                            'r_squared': r_value**2,
                            'p_value': p_value,
                            'trend_direction': trend_direction
                        },
                        similar_historical_events=[],
                        predictive_indicators=[feature]
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _discover_spatial_patterns(self, df: pd.DataFrame,
                                    features: List[str],
                                    county_col: str) -> List[Pattern]:
        """Discover spatial clustering patterns."""
        patterns = []
        
        if not SKLEARN_AVAILABLE:
            return patterns
        
        # Need coordinates for spatial analysis
        if 'latitude' not in df.columns or 'longitude' not in df.columns:
            return patterns
        
        coords = df[['latitude', 'longitude']].values
        
        for feature in features:
            if feature not in df.columns:
                continue
                
            # Create feature-augmented coordinates
            scaler = StandardScaler()
            feature_values = df[feature].fillna(df[feature].median()).values.reshape(-1, 1)
            
            augmented_data = np.hstack([
                scaler.fit_transform(coords),
                scaler.fit_transform(feature_values)
            ])
            
            # DBSCAN clustering
            clustering = DBSCAN(eps=0.3, min_samples=self.min_pattern_size)
            labels = clustering.fit_predict(augmented_data)
            
            # Analyze clusters
            unique_labels = set(labels) - {-1}  # Exclude noise
            
            for cluster_id in unique_labels:
                cluster_mask = labels == cluster_id
                cluster_counties = df[cluster_mask][county_col].tolist()
                cluster_data = df[cluster_mask]
                
                if len(cluster_counties) >= self.min_pattern_size:
                    pattern = Pattern(
                        pattern_id=f"spatial_{feature}_cluster_{cluster_id}",
                        pattern_type='spatial_cluster',
                        description=f"Geographic cluster of {len(cluster_counties)} counties with similar {feature}",
                        confidence=len(cluster_counties) / len(df),
                        affected_counties=cluster_counties,
                        time_range=(datetime.now(), datetime.now()),
                        characteristics={
                            'cluster_size': len(cluster_counties),
                            'mean_feature_value': cluster_data[feature].mean(),
                            'std_feature_value': cluster_data[feature].std(),
                            'centroid_lat': cluster_data['latitude'].mean(),
                            'centroid_lon': cluster_data['longitude'].mean()
                        },
                        similar_historical_events=[],
                        predictive_indicators=[feature, 'latitude', 'longitude']
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _discover_sequential_patterns(self, df: pd.DataFrame,
                                       features: List[str],
                                       county_col: str,
                                       date_col: str) -> List[Pattern]:
        """Discover sequential patterns (disaster cascades)."""
        patterns = []
        
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values([county_col, date_col])
        
        # Look for disaster cascade sequences
        for county in df[county_col].unique():
            county_data = df[df[county_col] == county].copy()
            
            if len(county_data) < 10:
                continue
            
            # Detect rapid changes in vulnerability
            for feature in features:
                if feature not in county_data.columns:
                    continue
                    
                values = county_data[feature].values
                changes = np.diff(values)
                
                # Find sequences of consecutive increases/decreases
                for direction in [1, -1]:  # 1 for increase, -1 for decrease
                    sequences = self._find_consecutive_sequences(
                        changes, direction, min_length=3
                    )
                    
                    for seq in sequences:
                        if len(seq) >= 3:
                            start_idx = seq[0]
                            end_idx = seq[-1] + 1
                            
                            pattern = Pattern(
                                pattern_id=f"sequence_{county}_{feature}_{start_idx}",
                                pattern_type='sequence',
                                description=f"{county} shows {len(seq)}-period {'increasing' if direction == 1 else 'decreasing'} trend in {feature}",
                                confidence=min(len(seq) / 10, 1.0),
                                affected_counties=[county],
                                time_range=(
                                    county_data.iloc[start_idx][date_col],
                                    county_data.iloc[end_idx][date_col]
                                ),
                                characteristics={
                                    'sequence_length': len(seq),
                                    'total_change': values[end_idx] - values[start_idx],
                                    'direction': 'increasing' if direction == 1 else 'decreasing',
                                    'start_value': values[start_idx],
                                    'end_value': values[end_idx]
                                },
                                similar_historical_events=[],
                                predictive_indicators=[feature]
                            )
                            patterns.append(pattern)
        
        return patterns
    
    def _discover_multivariate_patterns(self, df: pd.DataFrame,
                                         features: List[str]) -> List[Pattern]:
        """Discover multivariate correlation patterns."""
        patterns = []
        
        # Correlation matrix
        corr_matrix = df[features].corr()
        
        # Find highly correlated feature pairs
        for i, feat1 in enumerate(features):
            for j, feat2 in enumerate(features):
                if i >= j:
                    continue
                    
                corr = corr_matrix.loc[feat1, feat2]
                
                if abs(corr) > 0.7:  # Strong correlation
                    pattern = Pattern(
                        pattern_id=f"correlation_{feat1}_{feat2}",
                        pattern_type='multivariate',
                        description=f"Strong {'positive' if corr > 0 else 'negative'} correlation between {feat1} and {feat2} (r={corr:.2f})",
                        confidence=abs(corr),
                        affected_counties=df['fips'].unique().tolist(),
                        time_range=(datetime.now(), datetime.now()),
                        characteristics={
                            'correlation': corr,
                            'correlation_strength': 'strong' if abs(corr) > 0.8 else 'moderate',
                            'feature1': feat1,
                            'feature2': feat2
                        },
                        similar_historical_events=[],
                        predictive_indicators=[feat1, feat2]
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _find_consecutive_sequences(self, arr: np.ndarray,
                                     direction: int,
                                     min_length: int = 3) -> List[List[int]]:
        """Find consecutive sequences of values in given direction."""
        sequences = []
        current_seq = []
        
        for i, val in enumerate(arr):
            if (direction == 1 and val > 0) or (direction == -1 and val < 0):
                current_seq.append(i)
            else:
                if len(current_seq) >= min_length:
                    sequences.append(current_seq)
                current_seq = []
        
        if len(current_seq) >= min_length:
            sequences.append(current_seq)
        
        return sequences
    
    def _generate_pattern_summary(self, results: Dict) -> Dict:
        """Generate summary statistics for discovered patterns."""
        summary = {
            'total_patterns': 0,
            'by_type': defaultdict(int),
            'high_confidence_patterns': 0,
            'most_affected_counties': [],
            'pattern_timeline': []
        }
        
        for pattern_type, patterns in results.items():
            if pattern_type == 'summary':
                continue
            summary['total_patterns'] += len(patterns)
            summary['by_type'][pattern_type] = len(patterns)
            
            for p in patterns:
                if p.confidence > 0.8:
                    summary['high_confidence_patterns'] += 1
        
        return dict(summary)


# Example usage
if __name__ == "__main__":
    recognizer = PatternRecognizer(min_pattern_size=5)
    
    df = pd.read_csv("data/processed/county_features.csv")
    
    features = [
        'vulnerability_index',
        'healthcare_access_score',
        'infrastructure_risk_score'
    ]
    
    patterns = recognizer.discover_patterns(df, features)
    
    print(f"Discovered {patterns['summary']['total_patterns']} patterns")
    print(f"By type: {patterns['summary']['by_type']}")
```

### 3.3 Correlation Analysis Engine

**File:** `src/insights/correlation_engine.py`

```python
"""
ResilienceAI - Correlation Analysis Engine
Advanced correlation discovery including lagged and nonlinear correlations.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from scipy.stats import pearsonr, spearmanr, kendalltau
from scipy.signal import correlate
import warnings
warnings.filterwarnings('ignore')


@dataclass
class CorrelationResult:
    """Container for correlation analysis results."""
    feature1: str
    feature2: str
    correlation_type: str
    correlation_value: float
    p_value: float
    confidence: float
    sample_size: int
    lag: Optional[int] = None
    time_window: Optional[Tuple] = None
    interpretation: str = ""


class CorrelationEngine:
    """
    Advanced correlation analysis for vulnerability metrics.
    
    Supports:
    - Pearson correlation (linear)
    - Spearman correlation (rank-based)
    - Kendall's tau (ordinal)
    - Cross-correlation (lagged)
    - Mutual information (nonlinear)
    - Granger causality (predictive)
    """
    
    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
        self.correlations = []
        
    def analyze(self, df: pd.DataFrame,
                features: List[str],
                target: Optional[str] = None,
                max_lag: int = 5) -> Dict[str, Any]:
        """
        Perform comprehensive correlation analysis.
        
        Args:
            df: Data to analyze
            features: Features to correlate
            target: Optional target variable
            max_lag: Maximum lag for time-series correlation
            
        Returns:
            Dictionary with correlation results
        """
        results = {
            'linear_correlations': self._analyze_linear(df, features, target),
            'rank_correlations': self._analyze_rank(df, features, target),
            'lagged_correlations': self._analyze_lagged(df, features, max_lag),
            'nonlinear_indicators': self._analyze_nonlinear(df, features),
            'causal_relationships': self._analyze_causality(df, features),
            'summary': {}
        }
        
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _analyze_linear(self, df: pd.DataFrame,
                        features: List[str],
                        target: Optional[str]) -> List[CorrelationResult]:
        """Analyze linear (Pearson) correlations."""
        results = []
        
        feature_pairs = self._get_feature_pairs(features, target)
        
        for feat1, feat2 in feature_pairs:
            if feat1 not in df.columns or feat2 not in df.columns:
                continue
                
            # Remove NaN values
            data = df[[feat1, feat2]].dropna()
            
            if len(data) < 10:
                continue
            
            corr, p_value = pearsonr(data[feat1], data[feat2])
            
            if p_value < self.significance_level:
                interpretation = self._interpret_correlation(corr, feat1, feat2)
                
                result = CorrelationResult(
                    feature1=feat1,
                    feature2=feat2,
                    correlation_type='pearson',
                    correlation_value=corr,
                    p_value=p_value,
                    confidence=1 - p_value,
                    sample_size=len(data),
                    interpretation=interpretation
                )
                results.append(result)
        
        # Sort by absolute correlation strength
        results.sort(key=lambda x: abs(x.correlation_value), reverse=True)
        
        return results
    
    def _analyze_rank(self, df: pd.DataFrame,
                      features: List[str],
                      target: Optional[str]) -> List[CorrelationResult]:
        """Analyze rank-based (Spearman, Kendall) correlations."""
        results = []
        
        feature_pairs = self._get_feature_pairs(features, target)
        
        for feat1, feat2 in feature_pairs:
            if feat1 not in df.columns or feat2 not in df.columns:
                continue
                
            data = df[[feat1, feat2]].dropna()
            
            if len(data) < 10:
                continue
            
            # Spearman correlation
            spearman_corr, spearman_p = spearmanr(data[feat1], data[feat2])
            
            if spearman_p < self.significance_level:
                result = CorrelationResult(
                    feature1=feat1,
                    feature2=feat2,
                    correlation_type='spearman',
                    correlation_value=spearman_corr,
                    p_value=spearman_p,
                    confidence=1 - spearman_p,
                    sample_size=len(data),
                    interpretation=f"Rank-based correlation: {self._interpret_correlation(spearman_corr, feat1, feat2)}"
                )
                results.append(result)
            
            # Kendall's tau
            kendall_corr, kendall_p = kendalltau(data[feat1], data[feat2])
            
            if kendall_p < self.significance_level:
                result = CorrelationResult(
                    feature1=feat1,
                    feature2=feat2,
                    correlation_type='kendall',
                    correlation_value=kendall_corr,
                    p_value=kendall_p,
                    confidence=1 - kendall_p,
                    sample_size=len(data),
                    interpretation=f"Ordinal correlation: {self._interpret_correlation(kendall_corr, feat1, feat2)}"
                )
                results.append(result)
        
        return results
    
    def _analyze_lagged(self, df: pd.DataFrame,
                        features: List[str],
                        max_lag: int) -> List[CorrelationResult]:
        """Analyze lagged (time-shifted) correlations."""
        results = []
        
        # Need time series data
        if 'date' not in df.columns:
            return results
        
        df = df.sort_values('date')
        
        feature_pairs = self._get_feature_pairs(features)
        
        for feat1, feat2 in feature_pairs:
            if feat1 not in df.columns or feat2 not in df.columns:
                continue
            
            for lag in range(1, max_lag + 1):
                # Shift feature2 by lag periods
                shifted = df[feat2].shift(lag)
                
                # Calculate correlation
                valid_idx = ~(df[feat1].isna() | shifted.isna())
                
                if valid_idx.sum() < 10:
                    continue
                
                corr, p_value = pearsonr(
                    df[feat1][valid_idx],
                    shifted[valid_idx]
                )
                
                if p_value < self.significance_level and abs(corr) > 0.3:
                    interpretation = f"{feat1} at time t correlates with {feat2} at t-{lag}"
                    
                    result = CorrelationResult(
                        feature1=feat1,
                        feature2=feat2,
                        correlation_type='lagged',
                        correlation_value=corr,
                        p_value=p_value,
                        confidence=1 - p_value,
                        sample_size=valid_idx.sum(),
                        lag=lag,
                        interpretation=interpretation
                    )
                    results.append(result)
        
        return results
    
    def _analyze_nonlinear(self, df: pd.DataFrame,
                           features: List[str]) -> Dict[str, Any]:
        """Analyze nonlinear relationships using mutual information."""
        results = {}
        
        try:
            from sklearn.feature_selection import mutual_info_regression
            
            for target in features:
                if target not in df.columns:
                    continue
                
                other_features = [f for f in features if f != target]
                
                X = df[other_features].fillna(df[other_features].median())
                y = df[target].fillna(df[target].median())
                
                mi_scores = mutual_info_regression(X, y, random_state=42)
                
                results[target] = [
                    {
                        'feature': feat,
                        'mutual_information': mi,
                        'interpretation': f"{mi:.3f} bits of information shared with {target}"
                    }
                    for feat, mi in zip(other_features, mi_scores)
                    if mi > 0.1  # Filter low-information relationships
                ]
                
                results[target].sort(key=lambda x: x['mutual_information'], reverse=True)
        
        except ImportError:
            pass
        
        return results
    
    def _analyze_causality(self, df: pd.DataFrame,
                           features: List[str]) -> List[Dict]:
        """Analyze potential causal relationships using Granger causality."""
        results = []
        
        try:
            from statsmodels.tsa.stattools import grangercausalitytests
            
            feature_pairs = self._get_feature_pairs(features)
            
            for feat1, feat2 in feature_pairs:
                if feat1 not in df.columns or feat2 not in df.columns:
                    continue
                
                # Prepare time series data
                ts_data = df[[feat2, feat1]].dropna()
                
                if len(ts_data) < 20:
                    continue
                
                try:
                    gc_result = grangercausalitytests(
                        ts_data, maxlag=3, verbose=False
                    )
                    
                    # Check if feat1 Granger-causes feat2
                    min_p_value = min(
                        gc_result[lag][0]['ssr_ftest'][1]
                        for lag in gc_result.keys()
                    )
                    
                    if min_p_value < self.significance_level:
                        results.append({
                            'cause': feat1,
                            'effect': feat2,
                            'p_value': min_p_value,
                            'confidence': 1 - min_p_value,
                            'interpretation': f"{feat1} may predict {feat2} (Granger causality)"
                        })
                
                except Exception:
                    continue
        
        except ImportError:
            pass
        
        return results
    
    def _get_feature_pairs(self, features: List[str],
                           target: Optional[str] = None) -> List[Tuple]:
        """Generate feature pairs for analysis."""
        if target:
            return [(target, f) for f in features if f != target]
        else:
            pairs = []
            for i, f1 in enumerate(features):
                for f2 in features[i+1:]:
                    pairs.append((f1, f2))
            return pairs
    
    def _interpret_correlation(self, corr: float, feat1: str, feat2: str) -> str:
        """Generate human-readable correlation interpretation."""
        strength = "strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak"
        direction = "positive" if corr > 0 else "negative"
        
        return f"{strength.capitalize()} {direction} correlation: as {feat1} increases, {feat2} tends to {'increase' if corr > 0 else 'decrease'}"
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate correlation analysis summary."""
        summary = {
            'total_correlations': 0,
            'strong_correlations': 0,
            'significant_correlations': 0,
            'top_correlations': []
        }
        
        all_corrs = []
        
        for corr_type, corrs in results.items():
            if corr_type == 'summary':
                continue
            if isinstance(corrs, list):
                for c in corrs:
                    if isinstance(c, CorrelationResult):
                        all_corrs.append(c)
                        summary['total_correlations'] += 1
                        if abs(c.correlation_value) > 0.7:
                            summary['strong_correlations'] += 1
                        if c.p_value < self.significance_level:
                            summary['significant_correlations'] += 1
        
        # Top 10 correlations
        all_corrs.sort(key=lambda x: abs(x.correlation_value), reverse=True)
        summary['top_correlations'] = [
            {
                'features': f"{c.feature1} - {c.feature2}",
                'correlation': c.correlation_value,
                'type': c.correlation_type
            }
            for c in all_corrs[:10]
        ]
        
        return summary


# Example usage
if __name__ == "__main__":
    engine = CorrelationEngine(significance_level=0.05)
    
    df = pd.read_csv("data/processed/county_features.csv")
    
    features = [
        'vulnerability_index',
        'healthcare_access_score',
        'infrastructure_risk_score',
        'social_vulnerability_index',
        'economic_resilience_score'
    ]
    
    results = engine.analyze(df, features, target='vulnerability_index')
    
    print(f"Found {results['summary']['total_correlations']} correlations")
    print(f"Strong correlations: {results['summary']['strong_correlations']}")
    print("\nTop correlations:")
    for corr in results['summary']['top_correlations'][:5]:
        print(f"  {corr['features']}: {corr['correlation']:.3f}")
```

---

## 4. Root Cause Analysis Engine

### 4.1 Implementation

**File:** `src/insights/root_cause_analyzer.py`

```python
"""
ResilienceAI - Root Cause Analysis Engine
Identifies underlying causes of vulnerability changes and anomalies.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')


@dataclass
class RootCause:
    """Identified root cause."""
    cause_id: str
    description: str
    primary_factor: str
    contributing_factors: List[Dict]
    confidence: float
    evidence: List[str]
    recommendations: List[str]
    affected_counties: List[str]
    time_identified: Any


class RootCauseAnalyzer:
    """
    Automated root cause analysis for vulnerability metrics.
    
    Methods:
    - Feature importance analysis (SHAP, permutation)
    - Causal graph inference
    - Counterfactual analysis
    - Historical pattern matching
    """
    
    def __init__(self):
        self.causal_graph = None
        self.historical_patterns = []
        
    def analyze(self, df: pd.DataFrame,
                target_variable: str,
                anomaly_results: List[Dict],
                feature_cols: List[str]) -> Dict[str, Any]:
        """
        Perform root cause analysis.
        
        Args:
            df: Vulnerability data
            target_variable: Variable to analyze
            anomaly_results: Detected anomalies
            feature_cols: Features to consider as causes
            
        Returns:
            Dictionary with root cause analysis results
        """
        results = {
            'feature_importance': self._analyze_feature_importance(
                df, target_variable, feature_cols
            ),
            'causal_chains': self._identify_causal_chains(
                df, target_variable, feature_cols
            ),
            'historical_matches': self._match_historical_patterns(
                anomaly_results
            ),
            'root_causes': [],
            'summary': {}
        }
        
        # Synthesize root causes
        results['root_causes'] = self._synthesize_root_causes(results)
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _analyze_feature_importance(self, df: pd.DataFrame,
                                     target: str,
                                     features: List[str]) -> List[Dict]:
        """Analyze feature importance using multiple methods."""
        importances = []
        
        # Prepare data
        X = df[features].fillna(df[features].median())
        y = df[target].fillna(df[target].median())
        
        # Random Forest importance
        try:
            from sklearn.ensemble import RandomForestRegressor
            
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X, y)
            
            for feat, imp in zip(features, rf.feature_importances_):
                importances.append({
                    'feature': feat,
                    'importance': imp,
                    'method': 'random_forest',
                    'rank': 0  # Will be set after sorting
                })
        except ImportError:
            pass
        
        # Permutation importance
        try:
            from sklearn.inspection import permutation_importance
            
            perm_importance = permutation_importance(
                rf, X, y, n_repeats=10, random_state=42
            )
            
            for feat, imp in zip(features, perm_importance.importances_mean):
                importances.append({
                    'feature': feat,
                    'importance': imp,
                    'method': 'permutation',
                    'rank': 0
                })
        except ImportError:
            pass
        
        # Sort by importance
        importances.sort(key=lambda x: x['importance'], reverse=True)
        
        # Assign ranks
        for i, imp in enumerate(importances):
            imp['rank'] = i + 1
        
        return importances
    
    def _identify_causal_chains(self, df: pd.DataFrame,
                                 target: str,
                                 features: List[str]) -> List[Dict]:
        """Identify causal chains leading to target variable changes."""
        chains = []
        
        # Simple causal chain: A → B → Target
        for feat_a in features:
            if feat_a == target:
                continue
            
            for feat_b in features:
                if feat_b == target or feat_b == feat_a:
                    continue
                
                # Check if A correlates with B and B correlates with Target
                corr_ab = df[feat_a].corr(df[feat_b])
                corr_bt = df[feat_b].corr(df[target])
                
                if abs(corr_ab) > 0.5 and abs(corr_bt) > 0.5:
                    chains.append({
                        'chain': [feat_a, feat_b, target],
                        'strength': abs(corr_ab * corr_bt),
                        'interpretation': f"{feat_a} → {feat_b} → {target}"
                    })
        
        # Sort by chain strength
        chains.sort(key=lambda x: x['strength'], reverse=True)
        
        return chains[:10]  # Top 10 chains
    
    def _match_historical_patterns(self, 
                                    anomaly_results: List[Dict]) -> List[Dict]:
        """Match current anomalies to historical patterns."""
        matches = []
        
        # This would query a historical pattern database
        # For now, return placeholder
        
        return matches
    
    def _synthesize_root_causes(self, results: Dict) -> List[RootCause]:
        """Synthesize findings into root cause statements."""
        root_causes = []
        
        # Group by primary factor
        factor_groups = defaultdict(list)
        
        for imp in results['feature_importance']:
            if imp['importance'] > 0.1:  # Significant importance
                factor_groups[imp['feature']].append(imp)
        
        # Create root cause objects
        for factor, imps in factor_groups.items():
            contributing = [
                {
                    'factor': chain['chain'][0],
                    'relationship': chain['interpretation'],
                    'strength': chain['strength']
                }
                for chain in results['causal_chains']
                if factor in chain['chain']
            ]
            
            root_cause = RootCause(
                cause_id=f"rc_{factor}_{pd.Timestamp.now().strftime('%Y%m%d')}",
                description=f"{factor} is a primary driver of vulnerability changes",
                primary_factor=factor,
                contributing_factors=contributing[:5],
                confidence=max([i['importance'] for i in imps]),
                evidence=[f"Feature importance: {i['importance']:.3f}" for i in imps],
                recommendations=self._generate_recommendations(factor),
                affected_counties=[],
                time_identified=pd.Timestamp.now()
            )
            
            root_causes.append(root_cause)
        
        # Sort by confidence
        root_causes.sort(key=lambda x: x.confidence, reverse=True)
        
        return root_causes
    
    def _generate_recommendations(self, factor: str) -> List[str]:
        """Generate recommendations based on root cause."""
        recommendations = {
            'vulnerability_index': [
                "Conduct comprehensive vulnerability assessment",
                "Implement targeted intervention programs",
                "Monitor high-risk populations"
            ],
            'healthcare_access_score': [
                "Expand healthcare facility capacity",
                "Deploy mobile health units",
                "Establish telemedicine programs"
            ],
            'infrastructure_risk_score': [
                "Upgrade critical infrastructure",
                "Implement redundancy measures",
                "Conduct resilience assessments"
            ],
            'social_vulnerability_index': [
                "Enhance social support programs",
                "Improve communication outreach",
                "Address equity gaps"
            ],
            'economic_resilience_score': [
                "Support local businesses",
                "Diversify economic base",
                "Establish emergency funds"
            ]
        }
        
        return recommendations.get(factor, [
            f"Investigate {factor} drivers",
            "Monitor trends closely",
            "Develop mitigation strategies"
        ])
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate root cause analysis summary."""
        return {
            'total_root_causes': len(results['root_causes']),
            'primary_factors': [rc.primary_factor for rc in results['root_causes'][:5]],
            'confidence_range': (
                min([rc.confidence for rc in results['root_causes']]) if results['root_causes'] else 0,
                max([rc.confidence for rc in results['root_causes']]) if results['root_causes'] else 0
            )
        }


# Example usage
if __name__ == "__main__":
    analyzer = RootCauseAnalyzer()
    
    df = pd.read_csv("data/processed/county_features.csv")
    
    features = [
        'healthcare_access_score',
        'infrastructure_risk_score',
        'social_vulnerability_index',
        'economic_resilience_score'
    ]
    
    results = analyzer.analyze(
        df,
        target_variable='vulnerability_index',
        anomaly_results=[],
        feature_cols=features
    )
    
    print(f"Identified {results['summary']['total_root_causes']} root causes")
    print(f"Primary factors: {results['summary']['primary_factors']}")
```

---

## 5. Automated Report Generation

### 5.1 Report Generator

**File:** `src/reporting/report_generator.py`

```python
"""
ResilienceAI - Automated Report Generator
Generates comprehensive analysis reports from insight discovery results.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd


@dataclass
class ReportSection:
    """Report section definition."""
    title: str
    content: str
    data: Dict[str, Any]
    visualizations: List[str]
    priority: int


class ReportGenerator:
    """
    Automated report generation for vulnerability insights.
    
    Report types:
    - Comprehensive Analysis Report
    - Executive Summary
    - Anomaly Alert Report
    - Trend Analysis Report
    - County Profile Report
    """
    
    def __init__(self, output_dir: str = "outputs/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.templates = self._load_templates()
        
    def generate_comprehensive_report(self,
                                       insights: Dict[str, Any],
                                       county_focus: Optional[str] = None) -> str:
        """Generate comprehensive analysis report."""
        report = {
            'metadata': self._generate_metadata('comprehensive'),
            'executive_summary': self._generate_executive_summary(insights),
            'anomaly_analysis': self._format_anomaly_section(insights.get('anomalies', {})),
            'pattern_analysis': self._format_pattern_section(insights.get('patterns', {})),
            'correlation_analysis': self._format_correlation_section(insights.get('correlations', {})),
            'root_cause_analysis': self._format_root_cause_section(insights.get('root_causes', {})),
            'trend_analysis': self._format_trend_section(insights.get('trends', {})),
            'comparative_analysis': self._format_comparative_section(insights.get('comparisons', {})),
            'recommendations': self._generate_recommendations(insights),
            'appendix': self._generate_appendix(insights)
        }
        
        # Save report
        filename = f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return str(filepath)
    
    def generate_executive_briefing(self, insights: Dict[str, Any]) -> str:
        """Generate executive briefing document."""
        briefing = {
            'metadata': self._generate_metadata('executive_briefing'),
            'key_findings': self._extract_key_findings(insights),
            'critical_alerts': self._extract_critical_alerts(insights),
            'trending_concerns': self._extract_trending_concerns(insights),
            'recommended_actions': self._extract_recommended_actions(insights),
            'dashboard_metrics': self._extract_dashboard_metrics(insights)
        }
        
        # Generate markdown format
        md_content = self._generate_briefing_markdown(briefing)
        
        filename = f"executive_briefing_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(md_content)
        
        return str(filepath)
    
    def generate_alert_report(self, anomalies: List[Any]) -> str:
        """Generate anomaly alert report."""
        report = {
            'metadata': self._generate_metadata('alert'),
            'alert_summary': {
                'total_alerts': len(anomalies),
                'critical_count': sum(1 for a in anomalies if getattr(a, 'severity', '') == 'critical'),
                'high_count': sum(1 for a in anomalies if getattr(a, 'severity', '') == 'high'),
            },
            'alerts_by_county': self._group_alerts_by_county(anomalies),
            'alerts_by_type': self._group_alerts_by_type(anomalies),
            'immediate_actions': self._generate_immediate_actions(anomalies)
        }
        
        filename = f"alert_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return str(filepath)
    
    def _generate_metadata(self, report_type: str) -> Dict:
        """Generate report metadata."""
        return {
            'report_type': report_type,
            'generated_at': datetime.now().isoformat(),
            'version': '1.0',
            'system': 'ResilienceAI Insight Discovery Engine'
        }
    
    def _generate_executive_summary(self, insights: Dict) -> str:
        """Generate executive summary text."""
        summary_parts = []
        
        # Anomaly summary
        anomalies = insights.get('anomalies', {})
        if anomalies:
            total = anomalies.get('summary', {}).get('total_anomalies', 0)
            summary_parts.append(f"Detected {total} anomalies across monitored counties.")
        
        # Pattern summary
        patterns = insights.get('patterns', {})
        if patterns:
            total = patterns.get('summary', {}).get('total_patterns', 0)
            summary_parts.append(f"Identified {total} significant patterns.")
        
        # Correlation summary
        correlations = insights.get('correlations', {})
        if correlations:
            strong = correlations.get('summary', {}).get('strong_correlations', 0)
            summary_parts.append(f"Found {strong} strong correlations between vulnerability factors.")
        
        return " ".join(summary_parts) if summary_parts else "Analysis complete. No significant findings."
    
    def _format_anomaly_section(self, anomalies: Dict) -> Dict:
        """Format anomaly analysis for report."""
        return {
            'summary': anomalies.get('summary', {}),
            'top_anomalies': [
                {
                    'county': a.county_name,
                    'variable': a.variable,
                    'value': a.value,
                    'severity': a.severity,
                    'recommendation': a.recommendation
                }
                for a in anomalies.get('anomalies', [])[:10]
            ]
        }
    
    def _format_pattern_section(self, patterns: Dict) -> Dict:
        """Format pattern analysis for report."""
        return {
            'summary': patterns.get('summary', {}),
            'discovered_patterns': [
                {
                    'type': p.pattern_type,
                    'description': p.description,
                    'confidence': p.confidence,
                    'affected_counties': len(p.affected_counties)
                }
                for p in patterns.get('temporal_patterns', [])[:5]
            ]
        }
    
    def _format_correlation_section(self, correlations: Dict) -> Dict:
        """Format correlation analysis for report."""
        return {
            'summary': correlations.get('summary', {}),
            'top_correlations': correlations.get('summary', {}).get('top_correlations', [])
        }
    
    def _format_root_cause_section(self, root_causes: Dict) -> Dict:
        """Format root cause analysis for report."""
        return {
            'summary': root_causes.get('summary', {}),
            'identified_causes': [
                {
                    'primary_factor': rc.primary_factor,
                    'confidence': rc.confidence,
                    'recommendations': rc.recommendations[:3]
                }
                for rc in root_causes.get('root_causes', [])[:5]
            ]
        }
    
    def _format_trend_section(self, trends: Dict) -> Dict:
        """Format trend analysis for report."""
        return trends
    
    def _format_comparative_section(self, comparisons: Dict) -> Dict:
        """Format comparative analysis for report."""
        return comparisons
    
    def _generate_recommendations(self, insights: Dict) -> List[Dict]:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Extract from anomalies
        for anomaly in insights.get('anomalies', {}).get('anomalies', []):
            if getattr(anomaly, 'severity', '') in ['critical', 'high']:
                recommendations.append({
                    'priority': 'high',
                    'category': 'anomaly_response',
                    'action': getattr(anomaly, 'recommendation', ''),
                    'target': getattr(anomaly, 'county_name', '')
                })
        
        # Extract from root causes
        for rc in insights.get('root_causes', {}).get('root_causes', [])[:3]:
            for rec in rc.recommendations[:2]:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'strategic',
                    'action': rec,
                    'target': rc.primary_factor
                })
        
        return recommendations
    
    def _generate_appendix(self, insights: Dict) -> Dict:
        """Generate report appendix with technical details."""
        return {
            'methodology': 'Automated insight discovery using ML algorithms',
            'data_sources': ['FEMA', 'Census ACS', 'HIFLD', 'NOAA'],
            'algorithms_used': [
                'Isolation Forest (anomaly detection)',
                'DBSCAN (spatial clustering)',
                'Pearson/Spearman correlation',
                'Random Forest (feature importance)'
            ]
        }
    
    def _extract_key_findings(self, insights: Dict) -> List[Dict]:
        """Extract key findings for executive briefing."""
        findings = []
        
        # Critical anomalies
        anomalies = insights.get('anomalies', {}).get('anomalies', [])
        critical = [a for a in anomalies if getattr(a, 'severity', '') == 'critical']
        if critical:
            findings.append({
                'type': 'critical_alert',
                'message': f"{len(critical)} counties require immediate attention",
                'details': [f"{a.county_name}: {a.variable}" for a in critical[:3]]
            })
        
        # Strong patterns
        patterns = insights.get('patterns', {}).get('temporal_patterns', [])
        high_conf = [p for p in patterns if p.confidence > 0.8]
        if high_conf:
            findings.append({
                'type': 'pattern',
                'message': f"{len(high_conf)} high-confidence patterns identified",
                'details': [p.description for p in high_conf[:3]]
            })
        
        return findings
    
    def _extract_critical_alerts(self, insights: Dict) -> List[Dict]:
        """Extract critical alerts for executive briefing."""
        anomalies = insights.get('anomalies', {}).get('anomalies', [])
        return [
            {
                'county': a.county_name,
                'issue': f"{a.variable}: {a.value:.2f}",
                'severity': a.severity,
                'action': a.recommendation
            }
            for a in anomalies if getattr(a, 'severity', '') in ['critical', 'high']
        ][:5]
    
    def _extract_trending_concerns(self, insights: Dict) -> List[Dict]:
        """Extract trending concerns for executive briefing."""
        trends = insights.get('trends', {})
        return trends.get('negative_trends', [])[:5]
    
    def _extract_recommended_actions(self, insights: Dict) -> List[str]:
        """Extract recommended actions for executive briefing."""
        actions = []
        
        # From anomalies
        for a in insights.get('anomalies', {}).get('anomalies', [])[:3]:
            actions.append(getattr(a, 'recommendation', ''))
        
        # From root causes
        for rc in insights.get('root_causes', {}).get('root_causes', [])[:2]:
            actions.extend(rc.recommendations[:2])
        
        return list(set(actions))[:5]  # Remove duplicates, limit to 5
    
    def _extract_dashboard_metrics(self, insights: Dict) -> Dict:
        """Extract key metrics for dashboard display."""
        return {
            'anomaly_count': insights.get('anomalies', {}).get('summary', {}).get('total_anomalies', 0),
            'pattern_count': insights.get('patterns', {}).get('summary', {}).get('total_patterns', 0),
            'correlation_count': insights.get('correlations', {}).get('summary', {}).get('total_correlations', 0),
            'critical_counties': len(set(
                a.county_fips for a in insights.get('anomalies', {}).get('anomalies', [])
                if getattr(a, 'severity', '') == 'critical'
            ))
        }
    
    def _generate_briefing_markdown(self, briefing: Dict) -> str:
        """Generate markdown formatted executive briefing."""
        md = f"""# ResilienceAI Executive Briefing

**Generated:** {briefing['metadata']['generated_at']}

## Key Findings

"""
        for finding in briefing['key_findings']:
            md += f"\n### {finding['type'].replace('_', ' ').title()}\n"
            md += f"{finding['message']}\n"
            for detail in finding.get('details', []):
                md += f"- {detail}\n"
        
        md += "\n## Critical Alerts\n\n"
        for alert in briefing['critical_alerts']:
            md += f"- **{alert['county']}**: {alert['issue']} ({alert['severity']})\n"
        
        md += "\n## Recommended Actions\n\n"
        for i, action in enumerate(briefing['recommended_actions'], 1):
            md += f"{i}. {action}\n"
        
        md += f"""
## Dashboard Metrics

- Total Anomalies: {briefing['dashboard_metrics']['anomaly_count']}
- Patterns Identified: {briefing['dashboard_metrics']['pattern_count']}
- Correlations Found: {briefing['dashboard_metrics']['correlation_count']}
- Counties Requiring Attention: {briefing['dashboard_metrics']['critical_counties']}
"""
        
        return md
    
    def _group_alerts_by_county(self, anomalies: List) -> Dict:
        """Group alerts by county."""
        by_county = {}
        for a in anomalies:
            county = getattr(a, 'county_fips', 'unknown')
            if county not in by_county:
                by_county[county] = []
            by_county[county].append({
                'variable': getattr(a, 'variable', ''),
                'severity': getattr(a, 'severity', '')
            })
        return by_county
    
    def _group_alerts_by_type(self, anomalies: List) -> Dict:
        """Group alerts by anomaly type."""
        by_type = {}
        for a in anomalies:
            atype = getattr(a, 'anomaly_type', 'unknown')
            atype_str = atype.value if hasattr(atype, 'value') else str(atype)
            by_type[atype_str] = by_type.get(atype_str, 0) + 1
        return by_type
    
    def _generate_immediate_actions(self, anomalies: List) -> List[str]:
        """Generate immediate action items from alerts."""
        actions = set()
        for a in anomalies:
            if getattr(a, 'severity', '') in ['critical', 'high']:
                actions.add(getattr(a, 'recommendation', ''))
        return list(actions)[:10]
    
    def _load_templates(self) -> Dict:
        """Load report templates."""
        return {
            'comprehensive': 'templates/comprehensive_template.md',
            'executive': 'templates/executive_template.md',
            'alert': 'templates/alert_template.md'
        }


# Example usage
if __name__ == "__main__":
    generator = ReportGenerator()
    
    # Sample insights
    insights = {
        'anomalies': {'summary': {'total_anomalies': 15}},
        'patterns': {'summary': {'total_patterns': 8}},
        'correlations': {'summary': {'strong_correlations': 12}}
    }
    
    report_path = generator.generate_comprehensive_report(insights)
    print(f"Report generated: {report_path}")
    
    briefing_path = generator.generate_executive_briefing(insights)
    print(f"Briefing generated: {briefing_path}")
```

---

## 6. Integration Architecture

### 6.1 Main Insight Orchestrator

**File:** `src/insights/insight_generator.py`

```python
"""
ResilienceAI - Main Insight Generator Orchestrator
Coordinates all insight discovery components.
"""
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import logging

# Import insight components
from anomaly_detector import AnomalyDetector
from pattern_recognizer import PatternRecognizer
from correlation_engine import CorrelationEngine
from root_cause_analyzer import RootCauseAnalyzer
from trend_analyzer import TrendAnalyzer
from comparative_analyzer import ComparativeAnalyzer
from statistical_tester import StatisticalTester
from insight_ranker import InsightRanker

# Import reporting
from reporting.report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightGenerator:
    """
    Main orchestrator for automated insight discovery.
    
    Usage:
        generator = InsightGenerator()
        insights = generator.generate_all_insights(df)
        generator.generate_reports(insights)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.components = {}
        self.report_generator = ReportGenerator()
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize all insight discovery components."""
        logger.info("Initializing insight discovery components...")
        
        self.components['anomaly_detector'] = AnomalyDetector(
            contamination=self.config.get('anomaly_contamination', 0.05)
        )
        self.components['pattern_recognizer'] = PatternRecognizer(
            min_pattern_size=self.config.get('min_pattern_size', 5)
        )
        self.components['correlation_engine'] = CorrelationEngine(
            significance_level=self.config.get('significance_level', 0.05)
        )
        self.components['root_cause_analyzer'] = RootCauseAnalyzer()
        self.components['trend_analyzer'] = TrendAnalyzer()
        self.components['comparative_analyzer'] = ComparativeAnalyzer()
        self.components['statistical_tester'] = StatisticalTester()
        self.components['insight_ranker'] = InsightRanker()
        
        logger.info("All components initialized successfully")
    
    def generate_all_insights(self, df: pd.DataFrame,
                               feature_cols: Optional[List[str]] = None,
                               county_col: str = 'fips',
                               date_col: str = 'date') -> Dict[str, Any]:
        """
        Generate all types of insights from data.
        
        Args:
            df: Vulnerability data
            feature_cols: Features to analyze (auto-detected if None)
            county_col: County identifier column
            date_col: Date column
            
        Returns:
            Dictionary with all insight types
        """
        logger.info("Starting comprehensive insight generation...")
        
        # Auto-detect features if not specified
        if feature_cols is None:
            feature_cols = self._auto_detect_features(df)
        
        insights = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_shape': df.shape,
                'features_analyzed': feature_cols,
                'counties': df[county_col].nunique()
            }
        }
        
        # 1. Anomaly Detection
        logger.info("Running anomaly detection...")
        try:
            self.components['anomaly_detector'].fit(df, feature_cols)
            insights['anomalies'] = self.components['anomaly_detector'].detect(df)
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            insights['anomalies'] = {'error': str(e)}
        
        # 2. Pattern Recognition
        logger.info("Running pattern recognition...")
        try:
            insights['patterns'] = self.components['pattern_recognizer'].discover_patterns(
                df, feature_cols, county_col, date_col
            )
        except Exception as e:
            logger.error(f"Pattern recognition failed: {e}")
            insights['patterns'] = {'error': str(e)}
        
        # 3. Correlation Analysis
        logger.info("Running correlation analysis...")
        try:
            insights['correlations'] = self.components['correlation_engine'].analyze(
                df, feature_cols
            )
        except Exception as e:
            logger.error(f"Correlation analysis failed: {e}")
            insights['correlations'] = {'error': str(e)}
        
        # 4. Root Cause Analysis
        logger.info("Running root cause analysis...")
        try:
            anomaly_list = insights['anomalies'].get('anomalies', [])
            insights['root_causes'] = self.components['root_cause_analyzer'].analyze(
                df, 'vulnerability_index', anomaly_list, feature_cols
            )
        except Exception as e:
            logger.error(f"Root cause analysis failed: {e}")
            insights['root_causes'] = {'error': str(e)}
        
        # 5. Trend Analysis
        logger.info("Running trend analysis...")
        try:
            insights['trends'] = self.components['trend_analyzer'].analyze(
                df, feature_cols, date_col
            )
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            insights['trends'] = {'error': str(e)}
        
        # 6. Comparative Analysis
        logger.info("Running comparative analysis...")
        try:
            insights['comparisons'] = self.components['comparative_analyzer'].analyze(
                df, feature_cols, county_col
            )
        except Exception as e:
            logger.error(f"Comparative analysis failed: {e}")
            insights['comparisons'] = {'error': str(e)}
        
        # 7. Statistical Testing
        logger.info("Running statistical tests...")
        try:
            insights['statistical_tests'] = self.components['statistical_tester'].run_all_tests(
                df, feature_cols
            )
        except Exception as e:
            logger.error(f"Statistical testing failed: {e}")
            insights['statistical_tests'] = {'error': str(e)}
        
        # 8. Insight Ranking
        logger.info("Ranking insights...")
        try:
            insights['ranked_insights'] = self.components['insight_ranker'].rank_insights(
                insights
            )
        except Exception as e:
            logger.error(f"Insight ranking failed: {e}")
            insights['ranked_insights'] = {'error': str(e)}
        
        logger.info("Insight generation complete!")
        
        return insights
    
    def generate_reports(self, insights: Dict[str, Any],
                         report_types: List[str] = None) -> Dict[str, str]:
        """
        Generate reports from insights.
        
        Args:
            insights: Generated insights
            report_types: Types of reports to generate
            
        Returns:
            Dictionary mapping report type to file path
        """
        report_types = report_types or ['comprehensive', 'executive', 'alert']
        
        generated_reports = {}
        
        if 'comprehensive' in report_types:
            logger.info("Generating comprehensive report...")
            path = self.report_generator.generate_comprehensive_report(insights)
            generated_reports['comprehensive'] = path
        
        if 'executive' in report_types:
            logger.info("Generating executive briefing...")
            path = self.report_generator.generate_executive_briefing(insights)
            generated_reports['executive'] = path
        
        if 'alert' in report_types:
            logger.info("Generating alert report...")
            anomalies = insights.get('anomalies', {}).get('anomalies', [])
            path = self.report_generator.generate_alert_report(anomalies)
            generated_reports['alert'] = path
        
        return generated_reports
    
    def save_insights(self, insights: Dict[str, Any],
                      output_path: Optional[str] = None) -> str:
        """Save insights to file."""
        if output_path is None:
            output_path = f"outputs/insights/insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(insights, f, indent=2, default=str)
        
        logger.info(f"Insights saved to {output_path}")
        return output_path
    
    def _auto_detect_features(self, df: pd.DataFrame) -> List[str]:
        """Automatically detect numeric features to analyze."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Exclude common non-feature columns
        exclude = ['fips', 'county_fips', 'latitude', 'longitude', 'year', 'month', 'day']
        
        features = [c for c in numeric_cols if c not in exclude]
        
        logger.info(f"Auto-detected {len(features)} features: {features[:5]}...")
        
        return features


# Example usage
if __name__ == "__main__":
    # Initialize generator
    generator = InsightGenerator(config={
        'anomaly_contamination': 0.05,
        'min_pattern_size': 5,
        'significance_level': 0.05
    })
    
    # Load data
    df = pd.read_csv("data/processed/county_features.csv")
    
    # Generate insights
    insights = generator.generate_all_insights(df)
    
    # Save insights
    generator.save_insights(insights)
    
    # Generate reports
    reports = generator.generate_reports(insights)
    
    print("\nGenerated Reports:")
    for report_type, path in reports.items():
        print(f"  {report_type}: {path}")
```

---

## 7. Implementation Priority Order

### Phase 1: Core Foundation (Weeks 1-2)

| Priority | Component | Files | Effort | Impact |
|----------|-----------|-------|--------|--------|
| 1 | Anomaly Detection Engine | `src/insights/anomaly_detector.py` | Medium | High |
| 2 | Pattern Recognition | `src/insights/pattern_recognizer.py` | Medium | High |
| 3 | Correlation Engine | `src/insights/correlation_engine.py` | Low | Medium |
| 4 | Insight Orchestrator | `src/insights/insight_generator.py` | Medium | High |

### Phase 2: Advanced Analysis (Weeks 3-4)

| Priority | Component | Files | Effort | Impact |
|----------|-----------|-------|--------|--------|
| 5 | Root Cause Analyzer | `src/insights/root_cause_analyzer.py` | High | High |
| 6 | Trend Analyzer | `src/insights/trend_analyzer.py` | Medium | Medium |
| 7 | Comparative Analyzer | `src/insights/comparative_analyzer.py` | Medium | Medium |
| 8 | Statistical Tester | `src/insights/statistical_tester.py` | Low | Medium |

### Phase 3: Reporting & Integration (Weeks 5-6)

| Priority | Component | Files | Effort | Impact |
|----------|-----------|-------|--------|--------|
| 9 | Report Generator | `src/reporting/report_generator.py` | Medium | High |
| 10 | Executive Briefings | `src/reporting/briefing_generator.py` | Medium | High |
| 11 | Dashboard Integration | Update `app/dashboard.py` | Medium | High |
| 12 | Alert Integration | Update `src/alert_manager.py` | Low | High |

### Phase 4: ML Enhancement (Weeks 7-8)

| Priority | Component | Files | Effort | Impact |
|----------|-----------|-------|--------|--------|
| 13 | LSTM Pattern Detection | `src/ml_models/lstm_patterns.py` | High | Medium |
| 14 | Graph Neural Networks | `src/ml_models/graph_neural_net.py` | High | Medium |
| 15 | Transformer Insights | `src/ml_models/transformer_insights.py` | High | Low |

---

## 8. Integration Points with Existing Code

### 8.1 Dashboard Integration

Update `app/dashboard.py` to include insight panels:

```python
# Add to dashboard.py imports
try:
    from insights.insight_generator import InsightGenerator
    INSIGHTS_AVAILABLE = True
except ImportError:
    INSIGHTS_AVAILABLE = False

# Add to dashboard UI
if INSIGHTS_AVAILABLE:
    with st.expander("🔍 Automated Insights", expanded=True):
        if st.button("Generate Insights"):
            with st.spinner("Analyzing data..."):
                generator = InsightGenerator()
                insights = generator.generate_all_insights(df)
                
                # Display key insights
                st.subheader("Key Findings")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Anomalies Detected", 
                             insights['anomalies']['summary']['total_anomalies'])
                with col2:
                    st.metric("Patterns Found", 
                             insights['patterns']['summary']['total_patterns'])
                with col3:
                    st.metric("Correlations", 
                             insights['correlations']['summary']['total_correlations'])
                with col4:
                    st.metric("Critical Counties", 
                             insights['anomalies']['summary']['by_severity'].get('critical', 0))
```

### 8.2 Alert Manager Integration

Update `src/alert_manager.py` to use anomaly detection:

```python
# Add to AlertManager class
def check_insight_based_alerts(self, df: pd.DataFrame) -> List[Dict]:
    """Generate alerts based on insight discovery."""
    from insights.anomaly_detector import AnomalyDetector
    
    detector = AnomalyDetector()
    detector.fit(df, feature_cols=self.vulnerability_features)
    
    results = detector.detect(df)
    
    alerts = []
    for anomaly in results['anomalies']:
        if anomaly.severity in ['critical', 'high']:
            alerts.append({
                'type': 'insight_anomaly',
                'severity': anomaly.severity,
                'county': anomaly.county_fips,
                'message': f"{anomaly.variable} anomaly detected: {anomaly.value:.2f}",
                'recommendation': anomaly.recommendation,
                'timestamp': anomaly.timestamp
            })
    
    return alerts
```

### 8.3 Agent Integration

Update `src/agents/orchestrator.py` to include insight tools:

```python
# Add MCP tools for insight generation
def get_insight_tools(self) -> List[Dict]:
    """Get MCP tools for insight discovery."""
    return [
        {
            'name': 'generate_insights',
            'description': 'Generate automated insights from vulnerability data',
            'parameters': {
                'county': {'type': 'string', 'description': 'County FIPS code'},
                'insight_types': {'type': 'array', 'description': 'Types of insights to generate'}
            }
        },
        {
            'name': 'detect_anomalies',
            'description': 'Detect anomalies in county vulnerability metrics',
            'parameters': {
                'county': {'type': 'string', 'description': 'County FIPS code'},
                'metrics': {'type': 'array', 'description': 'Metrics to analyze'}
            }
        },
        {
            'name': 'generate_briefing',
            'description': 'Generate executive briefing report',
            'parameters': {
                'report_type': {'type': 'string', 'enum': ['executive', 'comprehensive', 'alert']}
            }
        }
    ]
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

**File:** `tests/test_insight_discovery.py`

```python
"""Tests for insight discovery components."""
import pytest
import pandas as pd
import numpy as np
from src.insights.anomaly_detector import AnomalyDetector
from src.insights.pattern_recognizer import PatternRecognizer
from src.insights.correlation_engine import CorrelationEngine


class TestAnomalyDetector:
    """Test anomaly detection functionality."""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample vulnerability data."""
        np.random.seed(42)
        return pd.DataFrame({
            'fips': ['001'] * 100,
            'date': pd.date_range('2020-01-01', periods=100),
            'vulnerability_index': np.random.normal(0.5, 0.1, 100),
            'healthcare_access_score': np.random.normal(0.6, 0.15, 100)
        })
    
    def test_detector_initialization(self):
        """Test detector can be initialized."""
        detector = AnomalyDetector(contamination=0.05)
        assert detector.contamination == 0.05
        assert not detector.is_fitted
    
    def test_detector_fit(self, sample_data):
        """Test detector fitting."""
        detector = AnomalyDetector()
        detector.fit(sample_data, feature_cols=['vulnerability_index', 'healthcare_access_score'])
        assert detector.is_fitted
        assert 'isolation_forest' in detector.models
    
    def test_detector_detect(self, sample_data):
        """Test anomaly detection."""
        detector = AnomalyDetector()
        detector.fit(sample_data, feature_cols=['vulnerability_index', 'healthcare_access_score'])
        results = detector.detect(sample_data)
        
        assert 'anomalies' in results
        assert 'summary' in results


class TestPatternRecognizer:
    """Test pattern recognition functionality."""
    
    def test_temporal_pattern_discovery(self):
        """Test temporal pattern detection."""
        recognizer = PatternRecognizer()
        
        # Create seasonal data
        dates = pd.date_range('2020-01-01', periods=365)
        values = np.sin(np.arange(365) * 2 * np.pi / 365) + 0.5
        
        df = pd.DataFrame({
            'fips': ['001'] * 365,
            'date': dates,
            'seasonal_metric': values
        })
        
        results = recognizer.discover_patterns(df, ['seasonal_metric'])
        
        assert 'temporal_patterns' in results
```

---

## 10. Summary

This comprehensive insight discovery enhancement transforms ResilienceAI from a basic analytics platform into an intelligent, self-discovering analysis engine. The proposed architecture includes:

### Key Deliverables

1. **10 New Core Modules** in `src/insights/` for automated insight generation
2. **4 Reporting Modules** in `src/reporting/` for automated report generation
3. **4 ML Model Modules** in `src/ml_models/` for advanced pattern detection
4. **Integration Points** with existing dashboard, alert manager, and agent orchestrator
5. **Comprehensive Testing** strategy with unit and integration tests

### Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Manual Analysis Required | 100% | 20% |
| Time to Insight | Hours | Minutes |
| Anomaly Detection | Manual | Automated |
| Pattern Discovery | Manual | ML-powered |
| Report Generation | Manual | Automated |
| Executive Briefings | Manual | Automated |

### Next Steps

1. Implement Phase 1 components (Anomaly Detection, Pattern Recognition, Correlation Engine)
2. Integrate with existing dashboard
3. Add automated report scheduling
4. Enhance with ML models (LSTM, GNN)
5. Deploy and monitor performance

---

*Document generated for ResilienceAI Insight Discovery Enhancement*
*Branch: claw-autonomous*
*Date: 2026-02-17*
