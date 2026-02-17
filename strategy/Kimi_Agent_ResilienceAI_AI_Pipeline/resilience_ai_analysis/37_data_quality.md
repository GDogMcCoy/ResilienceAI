# ResilienceAI Data Quality Framework

## Executive Summary

This document presents a comprehensive data quality framework for ResilienceAI, designed to ensure data integrity, reliability, and trustworthiness across all data sources and pipelines.

---

## 1. Data Quality Framework Architecture

### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI DATA QUALITY FRAMEWORK                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Data       │  │   Schema     │  │   Missing    │  │   Outlier    │     │
│  │  Validation  │  │  Validation  │  │   Data       │  │  Detection   │     │
│  │   Engine     │  │   Engine     │  │   Handler    │  │   Engine     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         └─────────────────┴─────────────────┴─────────────────┘              │
│                              │                                               │
│                    ┌─────────┴─────────┐                                     │
│                    │  Quality Scoring  │                                     │
│                    └─────────┬─────────┘                                     │
│         ┌────────────────────┼────────────────────┐                         │
│  ┌──────▼──────┐    ┌────────▼────────┐  ┌───────▼───────┐                │
│  │   Data      │    │   Automated     │  │    Data       │                │
│  │  Profiling  │    │    Cleansing    │  │   Lineage     │                │
│  └──────┬──────┘    └────────┬────────┘  └───────┬───────┘                │
│         └────────────────────┼────────────────────┘                         │
│                    ┌─────────▼─────────┐                                     │
│                    │  Quality Monitor  │                                     │
│                    │   & Alerting      │                                     │
│                    └─────────┬─────────┘                                     │
│                    ┌─────────▼─────────┐                                     │
│                    │ Quality Dashboard │                                     │
│                    └───────────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Quality Dimensions

| Dimension | Description | Metrics |
|-----------|-------------|---------|
| **Completeness** | Presence of required data | Missing value %, Null count |
| **Accuracy** | Correctness of data values | Validation pass rate, Error rate |
| **Consistency** | Uniformity across datasets | Schema compliance %, Format consistency |
| **Timeliness** | Data freshness and latency | Age of data, Update frequency |
| **Validity** | Conformance to business rules | Rule pass rate, Constraint violations |
| **Uniqueness** | Absence of duplicates | Duplicate count, Uniqueness ratio |
| **Integrity** | Referential integrity | Foreign key violations, Orphan records |

---

## 2. Data Validation Rules

### 2.1 Validation Rule Types

```python
# File: /app/data_quality/validation/rules.py

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

class RuleType(Enum):
    SCHEMA = "schema"
    RANGE = "range"
    PATTERN = "pattern"
    ENUM = "enum"
    CUSTOM = "custom"
    RELATIONSHIP = "relationship"
    UNIQUENESS = "uniqueness"
    COMPLETENESS = "completeness"
    TIMELINESS = "timeliness"

class Severity(Enum):
    CRITICAL = "critical"    # Block pipeline execution
    HIGH = "high"            # Require manual review
    MEDIUM = "medium"        # Log warning
    LOW = "low"              # Informational only

@dataclass
class ValidationRule:
    name: str
    rule_type: RuleType
    column: Optional[str] = None
    severity: Severity = Severity.HIGH
    description: str = ""
    parameters: Dict[str, Any] = None
    enabled: bool = True

@dataclass
class ValidationResult:
    rule_name: str
    passed: bool
    severity: Severity
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    record_count: int
    violation_count: int
    violation_percentage: float
```

### 2.2 Schema Validation Rules

```python
# File: /app/data_quality/validation/schema_rules.py

import pandas as pd
from pandera import DataFrameSchema, Column, Check
import pandera as pa

class SchemaValidator:
    SCHEMAS = {
        "disaster_events": DataFrameSchema({
            "event_id": Column(str, checks=[
                Check.str_length(min_value=5, max_value=50),
                Check.not_null()
            ]),
            "event_type": Column(str, checks=[
                Check.isin(["earthquake", "flood", "hurricane", "wildfire", 
                           "tsunami", "drought", "tornado", "landslide"])
            ]),
            "severity": Column(str, checks=[
                Check.isin(["low", "medium", "high", "critical"])
            ]),
            "latitude": Column(float, checks=[
                Check.greater_than_or_equal_to(-90),
                Check.less_than_or_equal_to(90)
            ]),
            "longitude": Column(float, checks=[
                Check.greater_than_or_equal_to(-180),
                Check.less_than_or_equal_to(180)
            ]),
            "start_date": Column(pa.DateTime),
            "affected_population": Column(int, nullable=True),
            "economic_impact_usd": Column(float, checks=[
                Check.greater_than_or_equal_to(0)
            ], nullable=True),
        }, strict=True, coerce=True),
        
        "sensor_data": DataFrameSchema({
            "sensor_id": Column(str, checks=[Check.not_null()]),
            "timestamp": Column(pa.DateTime, checks=[Check.not_null()]),
            "sensor_type": Column(str, checks=[
                Check.isin(["seismic", "weather", "water_level", "air_quality",
                           "temperature", "humidity", "pressure"])
            ]),
            "value": Column(float, checks=[Check.not_null()]),
            "quality_flag": Column(str, checks=[
                Check.isin(["good", "suspect", "bad", "missing"])
            ], nullable=True),
        }, strict=True, coerce=True),
    }
    
    @classmethod
    def validate_schema(cls, df: pd.DataFrame, dataset_type: str) -> Dict[str, Any]:
        if dataset_type not in cls.SCHEMAS:
            return {"valid": False, "error": f"Unknown dataset type: {dataset_type}"}
        
        schema = cls.SCHEMAS[dataset_type]
        try:
            validated_df = schema.validate(df, lazy=True)
            return {
                "valid": True,
                "details": {
                    "rows_validated": len(validated_df),
                    "columns_validated": len(validated_df.columns)
                }
            }
        except pa.errors.SchemaErrors as err:
            return {
                "valid": False,
                "error": "Schema validation failed",
                "details": {"failure_cases": err.failure_cases.to_dict()}
            }
```

### 2.3 Business Rule Validation

```python
# File: /app/data_quality/validation/business_rules.py

class BusinessRuleValidator:
    RULES = {
        "event_date_consistency": {
            "description": "Event end date must be after start date",
            "check": lambda df: (df['end_date'].isna()) | (df['end_date'] >= df['start_date']),
            "severity": Severity.CRITICAL
        },
        "valid_coordinates": {
            "description": "Coordinates must be within valid ranges",
            "check": lambda df: (
                (df['latitude'].between(-90, 90)) &
                (df['longitude'].between(-180, 180))
            ),
            "severity": Severity.CRITICAL
        },
        "economic_impact_positive": {
            "description": "Economic impact must be non-negative",
            "check": lambda df: df['economic_impact_usd'].fillna(0) >= 0,
            "severity": Severity.CRITICAL
        },
    }
    
    @classmethod
    def validate_business_rules(cls, df: pd.DataFrame, rule_names: Optional[List[str]] = None):
        results = []
        rules_to_check = rule_names or cls.RULES.keys()
        
        for rule_name in rules_to_check:
            if rule_name not in cls.RULES:
                continue
            rule = cls.RULES[rule_name]
            
            try:
                passed = rule["check"](df)
                violation_count = (~passed).sum() if isinstance(passed, pd.Series) else 0
                
                results.append(ValidationResult(
                    rule_name=rule_name,
                    passed=violation_count == 0,
                    severity=rule["severity"],
                    message=rule["description"],
                    details={"violations": violation_count},
                    timestamp=datetime.now(),
                    record_count=len(df),
                    violation_count=violation_count,
                    violation_percentage=(violation_count / len(df) * 100) if len(df) > 0 else 0
                ))
            except Exception as e:
                results.append(ValidationResult(
                    rule_name=rule_name,
                    passed=False,
                    severity=Severity.CRITICAL,
                    message=f"Rule execution failed: {str(e)}",
                    details={"error": str(e)},
                    timestamp=datetime.now(),
                    record_count=len(df),
                    violation_count=len(df),
                    violation_percentage=100.0
                ))
        return results
```

---

## 3. Missing Data Detection & Handling

### 3.1 Missing Data Analyzer

```python
# File: /app/data_quality/missing_data/analyzer.py

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class MissingPattern(Enum):
    MCAR = "missing_completely_at_random"
    MAR = "missing_at_random"
    MNAR = "missing_not_at_random"

@dataclass
class MissingDataReport:
    column: str
    total_records: int
    missing_count: int
    missing_percentage: float
    pattern: MissingPattern
    recommendations: List[str]

class MissingDataAnalyzer:
    CRITICAL_COLUMNS = {
        "disaster_events": ["event_id", "event_type", "latitude", "longitude", "start_date"],
        "sensor_data": ["sensor_id", "timestamp", "sensor_type", "value"],
    }
    
    THRESHOLDS = {
        "critical": 0.0,
        "high": 0.05,
        "medium": 0.15,
        "low": 0.30
    }
    
    @classmethod
    def analyze_missing_data(cls, df: pd.DataFrame, dataset_type: str) -> Dict[str, MissingDataReport]:
        reports = {}
        total_records = len(df)
        
        for column in df.columns:
            missing_count = df[column].isna().sum()
            missing_percentage = (missing_count / total_records) * 100
            pattern = cls._detect_missing_pattern(df, column)
            recommendations = cls._generate_recommendations(column, missing_percentage, dataset_type, pattern)
            
            reports[column] = MissingDataReport(
                column=column,
                total_records=total_records,
                missing_count=missing_count,
                missing_percentage=missing_percentage,
                pattern=pattern,
                recommendations=recommendations
            )
        return reports
    
    @classmethod
    def _detect_missing_pattern(cls, df: pd.DataFrame, column: str) -> MissingPattern:
        missing_mask = df[column].isna()
        correlations = []
        for other_col in df.select_dtypes(include=[np.number]).columns:
            if other_col != column:
                corr = df[other_col].isna().corr(missing_mask)
                correlations.append(abs(corr))
        max_correlation = max(correlations) if correlations else 0
        
        if max_correlation < 0.1:
            return MissingPattern.MCAR
        elif max_correlation < 0.5:
            return MissingPattern.MAR
        else:
            return MissingPattern.MNAR
```

### 3.2 Missing Data Imputation

```python
# File: /app/data_quality/missing_data/imputation.py

from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.impute import IterativeImputer
import pandas as pd
import numpy as np

class ImputationStrategy:
    STRATEGIES = {
        "mean": {"description": "Replace missing with column mean", "applicable_types": ["numeric"]},
        "median": {"description": "Replace missing with column median", "applicable_types": ["numeric"]},
        "mode": {"description": "Replace missing with most frequent value", "applicable_types": ["categorical"]},
        "forward_fill": {"description": "Fill with previous valid value", "applicable_types": ["time_series"]},
        "knn": {"description": "K-nearest neighbors imputation", "applicable_types": ["numeric"]},
        "drop": {"description": "Remove records with missing values", "applicable_types": ["all"]},
    }
    
    @classmethod
    def impute(cls, df: pd.DataFrame, strategy: str, columns: List[str] = None, **kwargs):
        df_imputed = df.copy()
        columns = columns or df.columns.tolist()
        
        if strategy == "mean":
            imputer = SimpleImputer(strategy='mean')
            numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
            df_imputed[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        elif strategy == "median":
            imputer = SimpleImputer(strategy='median')
            numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
            df_imputed[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        elif strategy == "forward_fill":
            df_imputed[columns] = df[columns].fillna(method='ffill')
        elif strategy == "knn":
            n_neighbors = kwargs.get('n_neighbors', 5)
            imputer = KNNImputer(n_neighbors=n_neighbors)
            numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
            df_imputed[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        elif strategy == "drop":
            df_imputed = df.dropna(subset=columns)
        
        return df_imputed
```

---

## 4. Outlier Detection

### 4.1 Outlier Detection Engine

```python
# File: /app/data_quality/outliers/detector.py

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

class OutlierDetector:
    DOMAIN_THRESHOLDS = {
        "seismic_magnitude": {"min": -2.0, "max": 10.0},
        "flood_depth_meters": {"min": 0, "max": 50},
        "wind_speed_kmh": {"min": 0, "max": 500},
        "temperature_celsius": {"min": -100, "max": 100},
        "affected_population": {"min": 0, "max": 100_000_000},
        "economic_impact_usd": {"min": 0, "max": 1e15},
    }
    
    @classmethod
    def detect_outliers_iqr(cls, df: pd.DataFrame, column: str, k: float = 1.5) -> pd.Series:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - k * IQR
        upper_bound = Q3 + k * IQR
        return (df[column] < lower_bound) | (df[column] > upper_bound)
    
    @classmethod
    def detect_outliers_zscore(cls, df: pd.DataFrame, column: str, threshold: float = 3.0) -> pd.Series:
        z_scores = np.abs(stats.zscore(df[column].dropna()))
        outlier_mask = pd.Series(False, index=df.index)
        outlier_mask[df[column].notna()] = z_scores > threshold
        return outlier_mask
    
    @classmethod
    def detect_outliers_isolation_forest(cls, df: pd.DataFrame, columns: List[str], contamination: float = 0.1):
        numeric_df = df[columns].select_dtypes(include=[np.number])
        if numeric_df.empty:
            return pd.Series(False, index=df.index)
        numeric_df = numeric_df.fillna(numeric_df.median())
        clf = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
        predictions = clf.fit_predict(numeric_df)
        return pd.Series(predictions == -1, index=df.index)
    
    @classmethod
    def comprehensive_outlier_analysis(cls, df: pd.DataFrame, numeric_columns: List[str] = None) -> Dict[str, Any]:
        if numeric_columns is None:
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = {"summary": {}, "column_analysis": {}, "recommendations": []}
        total_outliers = 0
        
        for col in numeric_columns:
            if df[col].isna().all():
                continue
            col_results = {
                "iqr_outliers": cls.detect_outliers_iqr(df, col).sum(),
                "zscore_outliers": cls.detect_outliers_zscore(df, col).sum(),
            }
            iqr_mask = cls.detect_outliers_iqr(df, col)
            zscore_mask = cls.detect_outliers_zscore(df, col)
            consensus_outliers = iqr_mask & zscore_mask
            col_results["consensus_outliers"] = consensus_outliers.sum()
            results["column_analysis"][col] = col_results
            total_outliers += col_results["consensus_outliers"]
        
        if len(numeric_columns) >= 2:
            results["multivariate"] = {
                "isolation_forest": cls.detect_outliers_isolation_forest(df, numeric_columns).sum(),
            }
        
        results["summary"] = {
            "total_records": len(df),
            "columns_analyzed": len(numeric_columns),
            "total_consensus_outliers": total_outliers,
            "outlier_percentage": (total_outliers / len(df)) * 100 if len(df) > 0 else 0
        }
        return results
```

---

## 5. Data Profiling

### 5.1 Data Profiler

```python
# File: /app/data_quality/profiling/profiler.py

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

@dataclass
class ColumnProfile:
    name: str
    dtype: str
    total_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None

@dataclass
class DatasetProfile:
    dataset_name: str
    timestamp: str
    total_rows: int
    total_columns: int
    memory_usage_mb: float
    column_profiles: Dict[str, ColumnProfile]
    data_quality_score: Optional[float] = None

class DataProfiler:
    @classmethod
    def profile_dataset(cls, df: pd.DataFrame, dataset_name: str) -> DatasetProfile:
        column_profiles = {}
        for col in df.columns:
            column_profiles[col] = cls._profile_column(df, col)
        
        quality_score = cls._calculate_quality_score(column_profiles)
        
        return DatasetProfile(
            dataset_name=dataset_name,
            timestamp=datetime.now().isoformat(),
            total_rows=len(df),
            total_columns=len(df.columns),
            memory_usage_mb=df.memory_usage(deep=True).sum() / (1024 * 1024),
            column_profiles=column_profiles,
            data_quality_score=quality_score
        )
    
    @classmethod
    def _profile_column(cls, df: pd.DataFrame, column: str) -> ColumnProfile:
        series = df[column]
        total_count = len(series)
        null_count = series.isna().sum()
        null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
        unique_count = series.nunique()
        unique_percentage = (unique_count / total_count) * 100 if total_count > 0 else 0
        
        profile = ColumnProfile(
            name=column,
            dtype=str(series.dtype),
            total_count=total_count,
            null_count=null_count,
            null_percentage=null_percentage,
            unique_count=unique_count,
            unique_percentage=unique_percentage
        )
        
        if pd.api.types.is_numeric_dtype(series):
            non_null_series = series.dropna()
            if len(non_null_series) > 0:
                profile.mean = non_null_series.mean()
                profile.median = non_null_series.median()
                profile.std = non_null_series.std()
                profile.min = non_null_series.min()
                profile.max = non_null_series.max()
        
        return profile
    
    @classmethod
    def _calculate_quality_score(cls, column_profiles: Dict[str, ColumnProfile]) -> float:
        if not column_profiles:
            return 0.0
        scores = []
        for profile in column_profiles.values():
            completeness_score = 100 - profile.null_percentage
            uniqueness_score = 100 if profile.unique_percentage > 1 else 50
            col_score = (completeness_score * 0.6) + (uniqueness_score * 0.4)
            scores.append(col_score)
        return np.mean(scores) if scores else 0.0
```

---

## 6. Quality Scoring

### 6.1 Quality Score Engine

```python
# File: /app/data_quality/scoring/engine.py

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np

class QualityDimension(Enum):
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    INTEGRITY = "integrity"

@dataclass
class DimensionScore:
    dimension: QualityDimension
    score: float
    weight: float
    details: Dict[str, Any]

@dataclass
class QualityScore:
    dataset_name: str
    overall_score: float
    dimension_scores: List[DimensionScore]
    timestamp: str
    recommendations: List[str]

class QualityScoringEngine:
    DEFAULT_WEIGHTS = {
        QualityDimension.COMPLETENESS: 0.20,
        QualityDimension.ACCURACY: 0.20,
        QualityDimension.CONSISTENCY: 0.15,
        QualityDimension.TIMELINESS: 0.15,
        QualityDimension.VALIDITY: 0.15,
        QualityDimension.UNIQUENESS: 0.10,
        QualityDimension.INTEGRITY: 0.05
    }
    
    THRESHOLDS = {
        "excellent": 90,
        "good": 75,
        "acceptable": 60,
        "poor": 40,
        "critical": 0
    }
    
    @classmethod
    def calculate_quality_score(cls, df: pd.DataFrame, dataset_name: str, 
                                validation_results: List[Any], 
                                weights: Dict[QualityDimension, float] = None) -> QualityScore:
        weights = weights or cls.DEFAULT_WEIGHTS
        dimension_scores = []
        
        dimension_scores.append(cls._calculate_completeness(df, weights))
        dimension_scores.append(cls._calculate_accuracy(validation_results, weights))
        dimension_scores.append(cls._calculate_consistency(df, validation_results, weights))
        dimension_scores.append(cls._calculate_timeliness(df, weights))
        dimension_scores.append(cls._calculate_validity(validation_results, weights))
        dimension_scores.append(cls._calculate_uniqueness(df, weights))
        dimension_scores.append(cls._calculate_integrity(df, weights))
        
        overall_score = sum(ds.score * ds.weight for ds in dimension_scores)
        recommendations = cls._generate_recommendations(dimension_scores)
        
        return QualityScore(
            dataset_name=dataset_name,
            overall_score=round(overall_score, 2),
            dimension_scores=dimension_scores,
            timestamp=pd.Timestamp.now().isoformat(),
            recommendations=recommendations
        )
    
    @classmethod
    def _calculate_completeness(cls, df: pd.DataFrame, weights: Dict[QualityDimension, float]):
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100
        return DimensionScore(
            dimension=QualityDimension.COMPLETENESS,
            score=round(completeness, 2),
            weight=weights[QualityDimension.COMPLETENESS],
            details={"total_cells": total_cells, "missing_cells": missing_cells}
        )
    
    @classmethod
    def _calculate_accuracy(cls, validation_results: List[Any], weights: Dict[QualityDimension, float]):
        if not validation_results:
            return DimensionScore(dimension=QualityDimension.ACCURACY, score=100.0,
                                  weight=weights[QualityDimension.ACCURACY], details={})
        total_checks = len(validation_results)
        passed_checks = sum(1 for r in validation_results if getattr(r, 'passed', True))
        accuracy = (passed_checks / total_checks) * 100 if total_checks > 0 else 100
        return DimensionScore(dimension=QualityDimension.ACCURACY, score=round(accuracy, 2),
                              weight=weights[QualityDimension.ACCURACY],
                              details={"total_checks": total_checks, "passed_checks": passed_checks})
    
    @classmethod
    def _calculate_consistency(cls, df: pd.DataFrame, validation_results: List[Any], weights: Dict):
        type_issues = 0
        for col in df.select_dtypes(include=['object']).columns:
            types = df[col].dropna().apply(type).unique()
            if len(types) > 1:
                type_issues += 1
        consistency = max(0, 100 - (type_issues * 10))
        return DimensionScore(dimension=QualityDimension.CONSISTENCY, score=round(consistency, 2),
                              weight=weights[QualityDimension.CONSISTENCY], details={"type_issues": type_issues})
    
    @classmethod
    def _calculate_timeliness(cls, df: pd.DataFrame, weights: Dict[QualityDimension, float]):
        timestamp_cols = df.select_dtypes(include=['datetime64']).columns
        if len(timestamp_cols) == 0:
            return DimensionScore(dimension=QualityDimension.TIMELINESS, score=100.0,
                                  weight=weights[QualityDimension.TIMELINESS], details={})
        timestamp_col = timestamp_cols[0]
        max_timestamp = df[timestamp_col].max()
        days_since_update = (pd.Timestamp.now() - max_timestamp).days
        timeliness = max(0, 100 - (days_since_update * 2))
        return DimensionScore(dimension=QualityDimension.TIMELINESS, score=round(timeliness, 2),
                              weight=weights[QualityDimension.TIMELINESS],
                              details={"days_since_update": days_since_update})
    
    @classmethod
    def _calculate_validity(cls, validation_results: List[Any], weights: Dict):
        return cls._calculate_accuracy(validation_results, weights)
    
    @classmethod
    def _calculate_uniqueness(cls, df: pd.DataFrame, weights: Dict[QualityDimension, float]):
        duplicate_count = df.duplicated().sum()
        uniqueness = ((len(df) - duplicate_count) / len(df)) * 100 if len(df) > 0 else 100
        return DimensionScore(dimension=QualityDimension.UNIQUENESS, score=round(uniqueness, 2),
                              weight=weights[QualityDimension.UNIQUENESS], details={"duplicates": duplicate_count})
    
    @classmethod
    def _calculate_integrity(cls, df: pd.DataFrame, weights: Dict[QualityDimension, float]):
        return DimensionScore(dimension=QualityDimension.INTEGRITY, score=100.0,
                              weight=weights[QualityDimension.INTEGRITY], details={})
    
    @classmethod
    def _generate_recommendations(cls, dimension_scores: List[DimensionScore]):
        recommendations = []
        for ds in dimension_scores:
            if ds.score < cls.THRESHOLDS["acceptable"]:
                recommendations.append(f"CRITICAL: {ds.dimension.value} score is {ds.score:.2f}. Immediate attention required.")
            elif ds.score < cls.THRESHOLDS["good"]:
                recommendations.append(f"WARNING: {ds.dimension.value} score is {ds.score:.2f}. Consider improvement actions.")
        return recommendations
    
    @classmethod
    def get_quality_grade(cls, score: float) -> str:
        if score >= cls.THRESHOLDS["excellent"]:
            return "A (Excellent)"
        elif score >= cls.THRESHOLDS["good"]:
            return "B (Good)"
        elif score >= cls.THRESHOLDS["acceptable"]:
            return "C (Acceptable)"
        elif score >= cls.THRESHOLDS["poor"]:
            return "D (Poor)"
        else:
            return "F (Critical)"
```

---

## 7. Automated Cleansing Pipeline

### 7.1 Cleansing Pipeline

```python
# File: /app/data_quality/cleansing/pipeline.py

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class CleansingStep:
    name: str
    function: Callable
    params: Dict[str, Any]
    enabled: bool = True
    critical: bool = False

@dataclass
class CleansingResult:
    success: bool
    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    steps_executed: List[str]
    steps_failed: List[str]
    changes: Dict[str, Any]
    timestamp: str

class DataCleansingPipeline:
    def __init__(self, name: str = "default"):
        self.name = name
        self.steps: List[CleansingStep] = []
    
    def add_step(self, name: str, function: Callable, params: Dict = None, 
                 enabled: bool = True, critical: bool = False):
        self.steps.append(CleansingStep(name=name, function=function, params=params or {},
                                        enabled=enabled, critical=critical))
        return self
    
    def execute(self, df: pd.DataFrame) -> CleansingResult:
        rows_before = len(df)
        columns_before = len(df.columns)
        df_cleansed = df.copy()
        steps_executed = []
        steps_failed = []
        changes = {"rows_removed": 0, "columns_removed": [], "duplicates_removed": 0}
        
        for step in self.steps:
            if not step.enabled:
                continue
            try:
                logger.info(f"Executing step: {step.name}")
                result = step.function(df_cleansed, **step.params)
                if isinstance(result, pd.DataFrame):
                    df_cleansed = result
                elif isinstance(result, tuple):
                    df_cleansed, step_changes = result
                    self._merge_changes(changes, step_changes)
                steps_executed.append(step.name)
            except Exception as e:
                logger.error(f"Step '{step.name}' failed: {str(e)}")
                steps_failed.append(step.name)
                if step.critical:
                    break
        
        rows_after = len(df_cleansed)
        columns_after = len(df_cleansed.columns)
        changes["rows_removed"] = rows_before - rows_after
        changes["columns_removed"] = list(set(df.columns) - set(df_cleansed.columns))
        
        return CleansingResult(
            success=len(steps_failed) == 0 or not any(s.critical for s in self.steps if s.name in steps_failed),
            rows_before=rows_before, rows_after=rows_after,
            columns_before=columns_before, columns_after=columns_after,
            steps_executed=steps_executed, steps_failed=steps_failed,
            changes=changes, timestamp=datetime.now().isoformat()
        )
    
    def _merge_changes(self, base: Dict, new: Dict):
        for key, value in new.items():
            if key in base:
                if isinstance(base[key], dict) and isinstance(value, dict):
                    base[key].update(value)
                elif isinstance(base[key], list) and isinstance(value, list):
                    base[key].extend(value)
                elif isinstance(base[key], int) and isinstance(value, int):
                    base[key] += value
                else:
                    base[key] = value
            else:
                base[key] = value

class CleansingFunctions:
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: List[str] = None, keep: str = 'first'):
        before_count = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep=keep)
        after_count = len(df_clean)
        return df_clean, {"duplicates_removed": before_count - after_count}
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: str = 'drop', 
                              columns: List[str] = None, threshold: float = 0.5, **kwargs):
        columns = columns or df.columns.tolist()
        nulls_filled = {}
        
        if strategy == 'drop':
            min_non_null = int(len(columns) * (1 - threshold))
            df_clean = df.dropna(thresh=min_non_null)
            nulls_filled["rows_dropped"] = len(df) - len(df_clean)
        elif strategy == 'drop_columns':
            missing_pct = df[columns].isna().mean()
            cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()
            df_clean = df.drop(columns=cols_to_drop)
            nulls_filled["columns_dropped"] = cols_to_drop
        elif strategy in ['mean', 'median']:
            from sklearn.impute import SimpleImputer
            imputer = SimpleImputer(strategy=strategy)
            numeric_cols = df[columns].select_dtypes(include=[np.number]).columns
            df_clean = df.copy()
            df_clean[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        else:
            df_clean = df.copy()
        return df_clean, {"nulls_filled": nulls_filled}
    
    @staticmethod
    def handle_outliers(df: pd.DataFrame, columns: List[str], method: str = 'iqr', 
                        action: str = 'cap', **kwargs):
        df_clean = df.copy()
        outliers_treated = {}
        
        for col in columns:
            if method == 'iqr':
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_mask = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
            else:
                continue
            
            outlier_count = outlier_mask.sum()
            if action == 'remove':
                df_clean = df_clean[~outlier_mask]
            elif action == 'cap':
                df_clean[col] = df_clean[col].clip(lower_bound, upper_bound)
            elif action == 'flag':
                df_clean[f"{col}_outlier_flag"] = outlier_mask.astype(int)
            outliers_treated[col] = outlier_count
        return df_clean, {"outliers_treated": outliers_treated}

class PipelineConfigs:
    @staticmethod
    def standard_pipeline():
        pipeline = DataCleansingPipeline("standard")
        pipeline.add_step("remove_duplicates", CleansingFunctions.remove_duplicates, {"keep": "first"})
        pipeline.add_step("handle_missing_values", CleansingFunctions.handle_missing_values, {"strategy": "median"})
        return pipeline
    
    @staticmethod
    def strict_pipeline():
        pipeline = DataCleansingPipeline("strict")
        pipeline.add_step("remove_duplicates", CleansingFunctions.remove_duplicates, {}, critical=True)
        pipeline.add_step("drop_high_missing", CleansingFunctions.handle_missing_values, 
                         {"strategy": "drop_columns", "threshold": 0.3})
        pipeline.add_step("drop_rows_missing", CleansingFunctions.handle_missing_values, 
                         {"strategy": "drop", "threshold": 0.2})
        return pipeline
```

---

## 8. Data Lineage Tracking

### 8.1 Lineage Tracker

```python
# File: /app/data_quality/lineage/tracker.py

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import hashlib
import uuid

class TransformationType(Enum):
    INGESTION = "ingestion"
    VALIDATION = "validation"
    CLEANSING = "cleansing"
    ENRICHMENT = "enrichment"
    AGGREGATION = "aggregation"
    JOIN = "join"
    FILTER = "filter"
    TRANSFORMATION = "transformation"
    EXPORT = "export"

@dataclass
class DataAsset:
    asset_id: str
    name: str
    asset_type: str
    schema: Dict[str, str]
    location: str
    format: str
    created_at: str
    row_count: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Transformation:
    transformation_id: str
    transformation_type: TransformationType
    name: str
    description: str
    timestamp: str
    input_assets: List[str]
    output_assets: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"

@dataclass
class DataLineage:
    lineage_id: str
    pipeline_name: str
    assets: Dict[str, DataAsset] = field(default_factory=dict)
    transformations: Dict[str, Transformation] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

class LineageTracker:
    def __init__(self, pipeline_name: str):
        self.lineage = DataLineage(lineage_id=str(uuid.uuid4()), pipeline_name=pipeline_name)
    
    def register_asset(self, name: str, asset_type: str, schema: Dict[str, str], 
                       location: str, format: str, row_count: int = None, metadata: Dict = None):
        asset_id = self._generate_asset_id(name, location)
        asset = DataAsset(
            asset_id=asset_id, name=name, asset_type=asset_type, schema=schema,
            location=location, format=format, created_at=datetime.now().isoformat(),
            row_count=row_count, metadata=metadata or {}
        )
        self.lineage.assets[asset_id] = asset
        self._update_timestamp()
        return asset_id
    
    def record_transformation(self, transformation_type: TransformationType, name: str,
                              description: str, input_assets: List[str], output_assets: List[str],
                              parameters: Dict = None, statistics: Dict = None, status: str = "success"):
        transformation_id = str(uuid.uuid4())
        transformation = Transformation(
            transformation_id=transformation_id, transformation_type=transformation_type,
            name=name, description=description, timestamp=datetime.now().isoformat(),
            input_assets=input_assets, output_assets=output_assets,
            parameters=parameters or {}, statistics=statistics or {}, status=status
        )
        self.lineage.transformations[transformation_id] = transformation
        self._update_timestamp()
        return transformation_id
    
    def get_lineage_for_asset(self, asset_id: str, direction: str = "both"):
        if asset_id not in self.lineage.assets:
            return {"error": "Asset not found"}
        result = {"asset": asdict(self.lineage.assets[asset_id]), "upstream": [], "downstream": []}
        if direction in ["upstream", "both"]:
            result["upstream"] = self._trace_upstream(asset_id)
        if direction in ["downstream", "both"]:
            result["downstream"] = self._trace_downstream(asset_id)
        return result
    
    def _trace_upstream(self, asset_id: str, visited: set = None):
        if visited is None:
            visited = set()
        if asset_id in visited:
            return []
        visited.add(asset_id)
        upstream = []
        for trans in self.lineage.transformations.values():
            if asset_id in trans.output_assets:
                for input_asset_id in trans.input_assets:
                    upstream.append({"transformation": asdict(trans), 
                                    "asset": asdict(self.lineage.assets.get(input_asset_id, DataAsset(
                                        asset_id=input_asset_id, name="Unknown", asset_type="unknown",
                                        schema={}, location="unknown", format="unknown", created_at=""))})
                    upstream.extend(self._trace_upstream(input_asset_id, visited))
        return upstream
    
    def _trace_downstream(self, asset_id: str, visited: set = None):
        if visited is None:
            visited = set()
        if asset_id in visited:
            return []
        visited.add(asset_id)
        downstream = []
        for trans in self.lineage.transformations.values():
            if asset_id in trans.input_assets:
                for output_asset_id in trans.output_assets:
                    downstream.append({"transformation": asdict(trans),
                                      "asset": asdict(self.lineage.assets.get(output_asset_id, DataAsset(
                                          asset_id=output_asset_id, name="Unknown", asset_type="unknown",
                                          schema={}, location="unknown", format="unknown", created_at=""))})
                    downstream.extend(self._trace_downstream(output_asset_id, visited))
        return downstream
    
    def generate_impact_analysis(self, asset_id: str):
        downstream = self._trace_downstream(asset_id)
        affected_assets = set()
        affected_transformations = set()
        for item in downstream:
            affected_assets.add(item["asset"]["asset_id"])
            affected_transformations.add(item["transformation"]["transformation_id"])
        return {
            "source_asset": asset_id,
            "direct_dependencies": len([d for d in downstream if d["transformation"]["input_assets"] == [asset_id]]),
            "total_affected_assets": len(affected_assets),
            "total_affected_transformations": len(affected_transformations),
            "risk_level": "high" if len(affected_assets) > 10 else "medium" if len(affected_assets) > 5 else "low"
        }
    
    def export_lineage(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(asdict(self.lineage), f, indent=2, default=str)
    
    def _generate_asset_id(self, name: str, location: str) -> str:
        content = f"{name}:{location}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _update_timestamp(self):
        self.lineage.updated_at = datetime.now().isoformat()
```

---

## 9. Quality Monitoring & Alerting

### 9.1 Quality Monitor

```python
# File: /app/data_quality/monitoring/monitor.py

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class QualityAlert:
    alert_id: str
    severity: AlertSeverity
    category: str
    message: str
    dataset: str
    timestamp: str
    details: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class QualityMetric:
    metric_name: str
    dataset: str
    value: float
    timestamp: str

class QualityMonitor:
    DEFAULT_THRESHOLDS = {
        "completeness_min": 95.0,
        "accuracy_min": 90.0,
        "consistency_min": 95.0,
        "timeliness_max_hours": 24,
        "uniqueness_min": 99.0,
        "null_percentage_max": 5.0,
        "duplicate_percentage_max": 1.0,
        "outlier_percentage_max": 5.0,
    }
    
    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self.alerts: List[QualityAlert] = []
        self.metrics_history: List[QualityMetric] = []
        self.alert_handlers: List[callable] = []
    
    def register_alert_handler(self, handler: callable):
        self.alert_handlers.append(handler)
    
    def evaluate_quality_score(self, quality_score, dataset_name: str) -> List[QualityAlert]:
        alerts = []
        overall = quality_score.overall_score
        
        if overall < 60:
            alerts.append(self._create_alert(AlertSeverity.CRITICAL, "overall_quality",
                f"CRITICAL: Overall quality score is {overall:.2f}/100 for {dataset_name}",
                dataset_name, {"score": overall}))
        elif overall < 75:
            alerts.append(self._create_alert(AlertSeverity.HIGH, "overall_quality",
                f"HIGH: Overall quality score is {overall:.2f}/100 for {dataset_name}",
                dataset_name, {"score": overall}))
        
        for ds in quality_score.dimension_scores:
            threshold = self.thresholds.get(f"{ds.dimension.value}_min", 80)
            if ds.score < threshold:
                severity = AlertSeverity.CRITICAL if ds.score < 50 else AlertSeverity.HIGH
                alerts.append(self._create_alert(severity, f"dimension_{ds.dimension.value}",
                    f"{severity.value.upper()}: {ds.dimension.value} score is {ds.score:.2f}/100",
                    dataset_name, {"dimension": ds.dimension.value, "score": ds.score}))
        
        self._store_metric("overall_quality_score", dataset_name, overall)
        for alert in alerts:
            self._process_alert(alert)
        return alerts
    
    def evaluate_validation_results(self, validation_results: List[Any], dataset_name: str):
        alerts = []
        failed_validations = [r for r in validation_results if not getattr(r, 'passed', True)]
        for result in failed_validations:
            severity = getattr(result, 'severity', AlertSeverity.HIGH)
            alerts.append(self._create_alert(severity, "validation_failure",
                f"Validation '{result.rule_name}' failed for {dataset_name}",
                dataset_name, {"rule_name": result.rule_name}))
        for alert in alerts:
            self._process_alert(alert)
        return alerts
    
    def evaluate_missing_data(self, missing_data_report: Dict[str, Any], dataset_name: str):
        alerts = []
        for column, report in missing_data_report.items():
            null_pct = report.missing_percentage
            if null_pct > self.thresholds["null_percentage_max"]:
                severity = AlertSeverity.CRITICAL if null_pct > 50 else AlertSeverity.HIGH
                alerts.append(self._create_alert(severity, "missing_data",
                    f"Column '{column}' has {null_pct:.2f}% missing values in {dataset_name}",
                    dataset_name, {"column": column, "missing_percentage": null_pct}))
            self._store_metric(f"null_percentage_{column}", dataset_name, null_pct)
        for alert in alerts:
            self._process_alert(alert)
        return alerts
    
    def _create_alert(self, severity: AlertSeverity, category: str, message: str, 
                      dataset: str, details: Dict[str, Any]):
        alert = QualityAlert(
            alert_id=str(uuid.uuid4()), severity=severity, category=category,
            message=message, dataset=dataset, timestamp=datetime.now().isoformat(),
            details=details
        )
        self.alerts.append(alert)
        return alert
    
    def _process_alert(self, alert: QualityAlert):
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    def _store_metric(self, metric_name: str, dataset: str, value: float):
        self.metrics_history.append(QualityMetric(
            metric_name=metric_name, dataset=dataset, value=value,
            timestamp=datetime.now().isoformat()
        ))
    
    def get_active_alerts(self, severity: AlertSeverity = None, dataset: str = None):
        alerts = [a for a in self.alerts if not a.resolved]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if dataset:
            alerts = [a for a in alerts if a.dataset == dataset]
        return alerts
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                return True
        return False
```

---

## 10. Quality Dashboard API

```python
# File: /app/data_quality/dashboard/api.py

from typing import Dict, List, Any
from datetime import datetime, timedelta

class QualityDashboardAPI:
    def __init__(self, monitor, scoring_engine):
        self.monitor = monitor
        self.scoring_engine = scoring_engine
    
    def get_overview(self) -> Dict[str, Any]:
        active_alerts = self.monitor.get_active_alerts()
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_active_alerts": len(active_alerts),
                "critical_alerts": len([a for a in active_alerts if a.severity.value == "critical"]),
                "high_alerts": len([a for a in active_alerts if a.severity.value == "high"]),
                "medium_alerts": len([a for a in active_alerts if a.severity.value == "medium"]),
            },
            "recent_alerts": [
                {"id": a.alert_id, "severity": a.severity.value, "message": a.message,
                 "dataset": a.dataset, "timestamp": a.timestamp}
                for a in sorted(active_alerts, key=lambda x: x.timestamp, reverse=True)[:10]
            ]
        }
    
    def get_dataset_quality(self, dataset_name: str) -> Dict[str, Any]:
        alerts = self.monitor.get_active_alerts(dataset=dataset_name)
        return {
            "dataset": dataset_name,
            "active_alerts": [
                {"id": a.alert_id, "severity": a.severity.value, "category": a.category,
                 "message": a.message, "timestamp": a.timestamp}
                for a in alerts
            ],
            "metrics_trend": self._get_metrics_trend_summary(dataset_name)
        }
    
    def _get_metrics_trend_summary(self, dataset: str, hours: int = 24):
        metrics = {}
        for metric in self.monitor.metrics_history:
            if metric.dataset == dataset:
                if metric.metric_name not in metrics:
                    metrics[metric.metric_name] = []
                metrics[metric.metric_name].append({"value": metric.value, "timestamp": metric.timestamp})
        return metrics
    
    def get_alerts_summary(self, hours: int = 24) -> Dict[str, Any]:
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_alerts = [a for a in self.monitor.alerts if datetime.fromisoformat(a.timestamp) > cutoff]
        by_severity, by_category, by_dataset = {}, {}, {}
        for alert in recent_alerts:
            by_severity[alert.severity.value] = by_severity.get(alert.severity.value, 0) + 1
            by_category[alert.category] = by_category.get(alert.category, 0) + 1
            by_dataset[alert.dataset] = by_dataset.get(alert.dataset, 0) + 1
        return {
            "period_hours": hours,
            "total_alerts": len(recent_alerts),
            "by_severity": by_severity,
            "by_category": by_category,
            "by_dataset": by_dataset,
        }
```

---

## 11. Pipeline Integration

```python
# File: /app/data_quality/integration/pipeline_integration.py

import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime

class DataQualityPipelineIntegration:
    def __init__(self, dataset_type: str, dataset_name: str,
                 enable_validation: bool = True, enable_cleansing: bool = True,
                 enable_profiling: bool = True, enable_lineage: bool = True,
                 enable_monitoring: bool = True):
        self.dataset_type = dataset_type
        self.dataset_name = dataset_name
        self.validation_enabled = enable_validation
        self.cleansing_enabled = enable_cleansing
        self.profiling_enabled = enable_profiling
        self.lineage_enabled = enable_lineage
        self.monitoring_enabled = enable_monitoring
        
        if enable_lineage:
            from ..lineage.tracker import LineageTracker
            self.lineage_tracker = LineageTracker(dataset_name)
        if enable_monitoring:
            from ..monitoring.monitor import QualityMonitor
            self.monitor = QualityMonitor()
            self.monitor.register_alert_handler(lambda a: print(f"[ALERT] {a.message}"))
    
    def process_dataframe(self, df: pd.DataFrame, source_location: str, 
                          cleansing_pipeline = None) -> Dict[str, Any]:
        results = {
            "success": True,
            "dataset": self.dataset_name,
            "timestamp": datetime.now().isoformat(),
            "steps": {}
        }
        
        try:
            # Step 1: Register lineage
            if self.lineage_enabled:
                input_asset_id = self.lineage_tracker.register_asset(
                    self.dataset_name, "dataframe",
                    {col: str(dtype) for col, dtype in df.dtypes.items()},
                    source_location, "dataframe", len(df)
                )
                results["steps"]["lineage_ingestion"] = {"asset_id": input_asset_id}
            
            # Step 2: Schema validation
            if self.validation_enabled:
                from ..validation.schema_rules import SchemaValidator
                schema_result = SchemaValidator.validate_schema(df, self.dataset_type)
                results["steps"]["schema_validation"] = schema_result
                if not schema_result["valid"]:
                    results["success"] = False
                    results["error"] = "Schema validation failed"
                    return results
            
            # Step 3: Data profiling
            if self.profiling_enabled:
                from ..profiling.profiler import DataProfiler
                profile = DataProfiler.profile_dataset(df, self.dataset_name)
                results["steps"]["profiling"] = {
                    "quality_score": profile.data_quality_score,
                    "row_count": profile.total_rows
                }
            
            # Step 4: Business rule validation
            if self.validation_enabled:
                from ..validation.business_rules import BusinessRuleValidator
                validation_results = BusinessRuleValidator.validate_business_rules(df)
                results["steps"]["business_validation"] = {
                    "total_rules": len(validation_results),
                    "passed": sum(1 for r in validation_results if r.passed),
                }
                if self.monitoring_enabled:
                    self.monitor.evaluate_validation_results(validation_results, self.dataset_name)
            
            # Step 5: Missing data analysis
            from ..missing_data.analyzer import MissingDataAnalyzer
            missing_report = MissingDataAnalyzer.analyze_missing_data(df, self.dataset_type)
            results["steps"]["missing_data_analysis"] = {"columns_analyzed": len(missing_report)}
            if self.monitoring_enabled:
                self.monitor.evaluate_missing_data(missing_report, self.dataset_name)
            
            # Step 6: Outlier detection
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                from ..outliers.detector import OutlierDetector
                outlier_analysis = OutlierDetector.comprehensive_outlier_analysis(df, numeric_cols)
                results["steps"]["outlier_detection"] = outlier_analysis["summary"]
                if self.monitoring_enabled:
                    self.monitor.evaluate_outliers(outlier_analysis, self.dataset_name)
            
            # Step 7: Quality scoring
            from ..scoring.engine import QualityScoringEngine
            quality_score = QualityScoringEngine.calculate_quality_score(
                df, self.dataset_name, validation_results if self.validation_enabled else []
            )
            results["steps"]["quality_scoring"] = {
                "overall_score": quality_score.overall_score,
                "grade": QualityScoringEngine.get_quality_grade(quality_score.overall_score)
            }
            if self.monitoring_enabled:
                self.monitor.evaluate_quality_score(quality_score, self.dataset_name)
            
            # Step 8: Data cleansing
            df_cleansed = df.copy()
            if self.cleansing_enabled and cleansing_pipeline:
                cleansing_result = cleansing_pipeline.execute(df)
                results["steps"]["cleansing"] = {
                    "success": cleansing_result.success,
                    "rows_before": cleansing_result.rows_before,
                    "rows_after": cleansing_result.rows_after
                }
            
            results["output_dataframe"] = df_cleansed
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            results["error_type"] = type(e).__name__
        
        return results
```

---

## 12. Configuration

```yaml
# File: /app/config/data_quality.yaml

data_quality:
  enabled: true
  fail_on_critical: true
  log_level: INFO
  
  validation:
    enabled: true
    schema_validation: true
    business_rules: true
    
  cleansing:
    enabled: true
    auto_cleanse: false
    default_pipeline: "standard"
    
  monitoring:
    enabled: true
    metrics_retention_days: 30
    alert_retention_days: 90
    
    thresholds:
      completeness_min: 95.0
      accuracy_min: 90.0
      consistency_min: 95.0
      timeliness_max_hours: 24
      uniqueness_min: 99.0
      null_percentage_max: 5.0
      outlier_percentage_max: 5.0
      overall_quality_min: 75.0
    
    alerts:
      critical:
        - type: email
          recipients: ["data-team@resilience.ai"]
        - type: webhook
          url: "https://alerts.resilience.ai/critical"
      high:
        - type: email
          recipients: ["data-team@resilience.ai"]
        - type: slack
          channel: "#data-quality"
      medium:
        - type: slack
          channel: "#data-quality"
  
  datasets:
    disaster_events:
      critical_columns: ["event_id", "event_type", "latitude", "longitude", "start_date"]
      quality_threshold: 90.0
    sensor_data:
      critical_columns: ["sensor_id", "timestamp", "sensor_type", "value"]
      quality_threshold: 85.0
    infrastructure:
      critical_columns: ["infrastructure_id", "name", "type", "latitude", "longitude"]
      quality_threshold: 95.0
  
  lineage:
    enabled: true
    storage:
      type: "postgresql"
  
  dashboard:
    enabled: true
    refresh_interval_seconds: 60
    default_time_range: "24h"
```

---

## 13. Implementation Priority

| Priority | Component | Timeline | Dependencies |
|----------|-----------|----------|--------------|
| **P0 - Critical** | | | |
| 1 | Schema Validation | Week 1 | None |
| 2 | Missing Data Detection | Week 1 | None |
| 3 | Basic Quality Scoring | Week 2 | Schema Validation |
| 4 | Quality Monitoring | Week 2 | Quality Scoring |
| **P1 - High** | | | |
| 5 | Business Rule Validation | Week 3 | Schema Validation |
| 6 | Outlier Detection | Week 3 | None |
| 7 | Data Profiling | Week 4 | None |
| 8 | Alerting System | Week 4 | Quality Monitoring |
| **P2 - Medium** | | | |
| 9 | Automated Cleansing | Week 5-6 | All P0, P1 |
| 10 | Data Lineage | Week 5-6 | None |
| 11 | Quality Dashboard | Week 6-7 | All P0, P1 |
| **P3 - Low** | | | |
| 12 | Advanced Analytics | Week 7-8 | Dashboard |
| 13 | ML-based Detection | Week 8+ | Outlier Detection |

---

## 14. Quick Start Example

```python
# File: /app/data_quality/quickstart.py

import pandas as pd
from data_quality.integration.pipeline_integration import DataQualityPipelineIntegration
from data_quality.cleansing.pipeline import PipelineConfigs

def quickstart_example():
    # 1. Load your data
    df = pd.read_csv("/data/disaster_events.csv")
    
    # 2. Create quality integration
    quality = DataQualityPipelineIntegration(
        dataset_type="disaster_events",
        dataset_name="raw_disaster_events",
        enable_validation=True,
        enable_cleansing=True,
        enable_profiling=True,
        enable_monitoring=True
    )
    
    # 3. Get cleansing pipeline
    cleansing_pipeline = PipelineConfigs.standard_pipeline()
    
    # 4. Process data
    results = quality.process_dataframe(
        df=df,
        source_location="/data/disaster_events.csv",
        cleansing_pipeline=cleansing_pipeline
    )
    
    # 5. Check results
    print(f"Quality Score: {results['steps']['quality_scoring']['overall_score']}")
    print(f"Grade: {results['steps']['quality_scoring']['grade']}")
    
    if results['success']:
        df_cleansed = results['output_dataframe']
        print(f"Cleansed data: {len(df_cleansed)} rows")
    else:
        print(f"Error: {results.get('error')}")
    
    return results

if __name__ == "__main__":
    quickstart_example()
```

---

## 15. Summary

This comprehensive data quality framework for ResilienceAI provides:

### Key Features

1. **Data Validation** - Schema and business rule validation with multi-severity handling
2. **Missing Data Management** - Pattern detection (MCAR, MAR, MNAR) with multiple imputation strategies
3. **Outlier Detection** - Statistical (IQR, Z-score) and ML-based (Isolation Forest) methods
4. **Data Profiling** - Comprehensive column statistics and quality score calculation
5. **Quality Scoring** - 7-dimension quality model with weighted scoring
6. **Automated Cleansing** - Configurable pipelines with pre-built strategies
7. **Data Lineage** - Full transformation tracking with impact analysis
8. **Monitoring & Alerting** - Real-time quality monitoring with multi-channel alerts
9. **Dashboard Integration** - RESTful API for quality overview and metrics

### File Structure

```
/app/data_quality/
├── __init__.py
├── config.py
├── quickstart.py
├── validation/
│   ├── __init__.py
│   ├── rules.py
│   ├── schema_rules.py
│   └── business_rules.py
├── missing_data/
│   ├── __init__.py
│   ├── analyzer.py
│   └── imputation.py
├── outliers/
│   ├── __init__.py
│   └── detector.py
├── profiling/
│   ├── __init__.py
│   └── profiler.py
├── scoring/
│   ├── __init__.py
│   └── engine.py
├── cleansing/
│   ├── __init__.py
│   └── pipeline.py
├── lineage/
│   ├── __init__.py
│   └── tracker.py
├── monitoring/
│   ├── __init__.py
│   └── monitor.py
├── dashboard/
│   ├── __init__.py
│   └── api.py
└── integration/
    ├── __init__.py
    └── pipeline_integration.py
```

### Next Steps

1. **Week 1**: Implement schema validation and missing data detection
2. **Week 2**: Deploy quality monitoring and basic scoring
3. **Week 3-4**: Add business rules and outlier detection
4. **Week 5-6**: Implement automated cleansing and lineage
5. **Week 7-8**: Deploy dashboard and advanced features

---

*Document Version: 1.0*
*Author: Data Quality Engineering Team*
