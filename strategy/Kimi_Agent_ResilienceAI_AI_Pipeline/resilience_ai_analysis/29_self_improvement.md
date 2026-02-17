# ResilienceAI Self-Improvement System Enhancement

## Executive Summary

This document provides a comprehensive analysis of the current self-improvement capabilities in ResilienceAI and proposes a next-generation self-improving platform architecture. The enhanced system will enable continuous learning, automated optimization, and adaptive behavior through sophisticated feedback loops and ML-driven improvement mechanisms.

---

## 1. Current State Analysis

### 1.1 Existing Self-Improvement Implementation

**File Location:** `src/self_improve.py` (306 lines, 11.1 KB)

#### Current Components:

| Component | Description | Limitations |
|-----------|-------------|-------------|
| `ResponseEvaluator` | Evaluates agent responses based on keyword matching | Rule-based, no ML, static thresholds |
| `ImprovementLogger` | Logs evaluations to JSON file | Simple file-based storage, no analytics |
| `SelfImproveEngine` | Combines evaluation and logging | No automated learning, no model updates |

#### Current Capabilities:

```python
# Current evaluation metrics (from self_improve.py)
TOOL_NAMES = [
    "query_counties", "get_county_detail", "compare_counties",
    "get_statistics", "predict_risk", "find_compound_risk_counties",
    "get_gap_analysis", "get_disaster_trends", "find_zero_redundancy",
    "get_state_rankings", "prioritize_by_impact",
    "simulate_scenario", "analyze_cascade_risk",
    "calculate_intervention_roi", "generate_executive_brief",
    "get_equity_analysis", "benchmark_county", "get_real_time_alerts",
]
```

#### Current Feedback Mechanism:
- **Confidence Scoring:** 0.0-1.0 based on rule deductions
- **Gap Detection:** Keyword-based capability gap identification
- **Tool Suggestions:** Pattern matching for unused tools
- **Logging:** JSON file storage (last 100 entries)

### 1.2 Identified Limitations

| Area | Current State | Gap |
|------|---------------|-----|
| **Response Quality** | Rule-based scoring | No semantic understanding |
| **Feedback Collection** | Implicit only | No explicit user feedback |
| **Performance Metrics** | Basic confidence | No comprehensive KPIs |
| **A/B Testing** | Not implemented | No experimentation framework |
| **Model Retraining** | Manual only | No automated pipelines |
| **Hyperparameter Tuning** | Static configs | No optimization |
| **Feature Importance** | Not tracked | No explainability |
| **User Satisfaction** | Not measured | No satisfaction metrics |
| **Continuous Learning** | Log-only | No model adaptation |
| **System Adaptation** | Static rules | No dynamic behavior |

---

## 2. Proposed Self-Improving Platform Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI SELF-IMPROVING PLATFORM                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Feedback   │  │   Response   │  │ Performance  │  │     A/B      │    │
│  │  Collection  │  │   Quality    │  │   Metrics    │  │   Testing    │    │
│  │   Engine     │  │  Evaluation  │  │   Tracker    │  │  Framework   │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         └─────────────────┴─────────────────┴─────────────────┘             │
│                                    │                                        │
│                         ┌──────────▼──────────┐                             │
│                         │   Feedback Loop     │                             │
│                         │     Processor       │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         │                          │                          │             │
│  ┌──────▼───────┐  ┌───────────────▼───────────────┐  ┌───────▼──────┐     │
│  │   Model      │  │   Hyperparameter              │  │   Feature    │     │
│  │  Retraining  │  │   Optimization Engine         │  │  Importance  │     │
│  │   Pipeline   │  │   (Optuna/Ray Tune)           │  │   Monitor    │     │
│  └──────┬───────┘  └───────────────┬───────────────┘  └───────┬──────┘     │
│         │                          │                          │             │
│         └──────────────────────────┼──────────────────────────┘             │
│                                    │                                        │
│                         ┌──────────▼──────────┐                             │
│                         │  Continuous Learning│                             │
│                         │      Pipeline       │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                        │
│                         ┌──────────▼──────────┐                             │
│                         │  System Adaptation  │                             │
│                         │      Engine         │                             │
│                         └─────────────────────┘                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 New Folder Structure

```
resilience_ai/
├── src/
│   ├── self_improve.py                    # Enhanced main module
│   ├── self_improve/                      # NEW: Self-improvement package
│   │   ├── __init__.py
│   │   ├── feedback_collector.py          # Feedback collection mechanisms
│   │   ├── quality_evaluator.py           # Response quality evaluation
│   │   ├── metrics_tracker.py             # Performance metrics tracking
│   │   ├── ab_testing.py                  # A/B testing framework
│   │   ├── model_retrainer.py             # Automated model retraining
│   │   ├── hyperparameter_optimizer.py    # Hyperparameter optimization
│   │   ├── feature_importance.py          # Feature importance monitoring
│   │   ├── satisfaction_tracker.py        # User satisfaction tracking
│   │   ├── learning_pipeline.py           # Continuous learning pipeline
│   │   ├── adaptation_engine.py           # System adaptation mechanisms
│   │   └── utils.py                       # Shared utilities
│   └── ...
├── data/
│   ├── feedback/                          # NEW: Feedback data storage
│   │   ├── explicit_feedback.jsonl
│   │   ├── implicit_feedback.jsonl
│   │   ├── satisfaction_scores.jsonl
│   │   └── feedback_metadata.db
│   ├── metrics/                           # NEW: Performance metrics
│   │   ├── daily_metrics.parquet
│   │   ├── model_performance.parquet
│   │   └── system_health.parquet
│   └── experiments/                       # NEW: A/B test data
│       ├── experiments.json
│       └── results/
├── models/
│   ├── self_improve/                      # NEW: Self-improvement models
│   │   ├── quality_classifier.pkl
│   │   ├── satisfaction_predictor.pkl
│   │   ├── feedback_encoder.pkl
│   │   └── adaptation_model.pkl
│   └── ...
├── config/
│   └── self_improve.yaml                  # NEW: Self-improvement config
└── logs/
    └── self_improve/                      # NEW: Self-improvement logs
        ├── feedback.log
        ├── metrics.log
        └── adaptation.log
```

---

## 3. Component Specifications

### 3.1 Feedback Collection Mechanisms

**File:** `src/self_improve/feedback_collector.py`

#### Explicit Feedback Collection

```python
"""
Explicit Feedback Collection System
Collects direct user feedback on response quality and usefulness.
"""
from dataclasses import dataclass
from typing import Optional, Dict, List, Any
from datetime import datetime
import json
from enum import Enum

class FeedbackType(Enum):
    THUMBS = "thumbs"           # 👍 / 👎
    RATING = "rating"           # 1-5 stars
    CATEGORY = "category"       # Predefined categories
    TEXT = "text"               # Free-form text
    MULTI_SELECT = "multi"      # Multiple choice

class FeedbackCategory(Enum):
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    CLARITY = "clarity"
    TIMELINESS = "timeliness"
    ACTIONABILITY = "actionability"

@dataclass
class ExplicitFeedback:
    """Structured explicit feedback from users."""
    feedback_id: str
    query_id: str
    user_id: Optional[str]
    timestamp: datetime
    feedback_type: FeedbackType
    rating: Optional[float]  # 0.0 to 1.0 normalized
    categories: List[FeedbackCategory]
    comments: Optional[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "feedback_id": self.feedback_id,
            "query_id": self.query_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "feedback_type": self.feedback_type.value,
            "rating": self.rating,
            "categories": [c.value for c in self.categories],
            "comments": self.comments,
            "metadata": self.metadata
        }

class ExplicitFeedbackCollector:
    """
    Collects and manages explicit user feedback.
    
    Features:
    - Multi-modal feedback collection (thumbs, ratings, text)
    - Category-based feedback for specific dimensions
    - Anonymous and authenticated feedback support
    - Real-time feedback streaming
    """
    
    def __init__(self, storage_path: str = "data/feedback/explicit"):
        self.storage_path = storage_path
        self.feedback_buffer: List[ExplicitFeedback] = []
        self.buffer_size = 100
        
    def collect_thumbs_feedback(
        self,
        query_id: str,
        is_helpful: bool,
        user_id: Optional[str] = None,
        comments: Optional[str] = None
    ) -> ExplicitFeedback:
        """Collect binary thumbs up/down feedback."""
        feedback = ExplicitFeedback(
            feedback_id=self._generate_id(),
            query_id=query_id,
            user_id=user_id,
            timestamp=datetime.now(),
            feedback_type=FeedbackType.THUMBS,
            rating=1.0 if is_helpful else 0.0,
            categories=[],
            comments=comments,
            metadata={"is_helpful": is_helpful}
        )
        self._buffer_feedback(feedback)
        return feedback
    
    def collect_rating_feedback(
        self,
        query_id: str,
        rating: int,  # 1-5
        categories: List[FeedbackCategory],
        user_id: Optional[str] = None,
        comments: Optional[str] = None
    ) -> ExplicitFeedback:
        """Collect star rating feedback with category breakdown."""
        normalized_rating = (rating - 1) / 4.0  # Normalize to 0-1
        feedback = ExplicitFeedback(
            feedback_id=self._generate_id(),
            query_id=query_id,
            user_id=user_id,
            timestamp=datetime.now(),
            feedback_type=FeedbackType.RATING,
            rating=normalized_rating,
            categories=categories,
            comments=comments,
            metadata={"original_rating": rating}
        )
        self._buffer_feedback(feedback)
        return feedback
    
    def collect_structured_feedback(
        self,
        query_id: str,
        ratings_by_category: Dict[FeedbackCategory, int],
        overall_rating: int,
        user_id: Optional[str] = None,
        comments: Optional[str] = None
    ) -> List[ExplicitFeedback]:
        """
        Collect detailed feedback across multiple dimensions.
        
        Args:
            ratings_by_category: Dict mapping categories to 1-5 ratings
            overall_rating: Overall satisfaction rating (1-5)
        """
        feedback_entries = []
        
        # Create individual feedback entries per category
        for category, rating in ratings_by_category.items():
            feedback = ExplicitFeedback(
                feedback_id=self._generate_id(),
                query_id=query_id,
                user_id=user_id,
                timestamp=datetime.now(),
                feedback_type=FeedbackType.CATEGORY,
                rating=(rating - 1) / 4.0,
                categories=[category],
                comments=None,
                metadata={"is_category_rating": True}
            )
            feedback_entries.append(feedback)
            self._buffer_feedback(feedback)
        
        # Create overall feedback entry
        overall_feedback = ExplicitFeedback(
            feedback_id=self._generate_id(),
            query_id=query_id,
            user_id=user_id,
            timestamp=datetime.now(),
            feedback_type=FeedbackType.RATING,
            rating=(overall_rating - 1) / 4.0,
            categories=list(ratings_by_category.keys()),
            comments=comments,
            metadata={"is_overall_rating": True}
        )
        feedback_entries.append(overall_feedback)
        self._buffer_feedback(overall_feedback)
        
        return feedback_entries
    
    def _buffer_feedback(self, feedback: ExplicitFeedback):
        """Add feedback to buffer and flush if needed."""
        self.feedback_buffer.append(feedback)
        if len(self.feedback_buffer) >= self.buffer_size:
            self._flush_buffer()
    
    def _flush_buffer(self):
        """Persist buffered feedback to storage."""
        if not self.feedback_buffer:
            return
            
        import os
        os.makedirs(self.storage_path, exist_ok=True)
        
        filename = f"{self.storage_path}/explicit_feedback_{datetime.now():%Y%m%d}.jsonl"
        with open(filename, "a") as f:
            for feedback in self.feedback_buffer:
                f.write(json.dumps(feedback.to_dict()) + "\n")
        
        self.feedback_buffer = []
    
    def _generate_id(self) -> str:
        """Generate unique feedback ID."""
        import uuid
        return str(uuid.uuid4())[:8]
```

#### Implicit Feedback Collection

```python
"""
Implicit Feedback Collection System
Infers user satisfaction from behavioral signals.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
import time

@dataclass
class InteractionSignals:
    """Behavioral signals indicating user engagement."""
    dwell_time_seconds: float
    scroll_depth: float  # 0.0 to 1.0
    click_count: int
    copy_events: int
    share_events: int
    export_events: int
    follow_up_queries: int
    return_visits: int
    
    def compute_engagement_score(self) -> float:
        """Compute composite engagement score from signals."""
        score = 0.0
        
        # Dwell time (optimal: 30-120 seconds)
        if 30 <= self.dwell_time_seconds <= 120:
            score += 0.25
        elif self.dwell_time_seconds > 120:
            score += 0.20
        elif self.dwell_time_seconds > 10:
            score += 0.10
            
        # Scroll depth
        score += self.scroll_depth * 0.20
        
        # Interactions
        score += min(self.click_count * 0.05, 0.15)
        score += min(self.copy_events * 0.10, 0.20)
        score += self.share_events * 0.10
        score += self.export_events * 0.10
        
        # Follow-up engagement
        score += min(self.follow_up_queries * 0.05, 0.10)
        score += min(self.return_visits * 0.05, 0.10)
        
        return min(score, 1.0)

class ImplicitFeedbackCollector:
    """
    Collects implicit feedback through behavioral tracking.
    
    Tracks:
    - Dwell time on responses
    - Scroll depth and reading patterns
    - Copy/share/export actions
    - Follow-up query patterns
    - Return visit frequency
    """
    
    def __init__(self, storage_path: str = "data/feedback/implicit"):
        self.storage_path = storage_path
        self.active_sessions: Dict[str, Dict] = {}
        
    def start_session(self, query_id: str, user_id: Optional[str] = None):
        """Start tracking a new user session."""
        self.active_sessions[query_id] = {
            "start_time": time.time(),
            "user_id": user_id,
            "scroll_events": [],
            "click_events": [],
            "copy_events": 0,
            "share_events": 0,
            "export_events": 0,
        }
    
    def record_scroll(self, query_id: str, depth: float):
        """Record scroll depth event."""
        if query_id in self.active_sessions:
            self.active_sessions[query_id]["scroll_events"].append({
                "depth": depth,
                "timestamp": time.time()
            })
    
    def record_interaction(
        self,
        query_id: str,
        interaction_type: str,
        metadata: Optional[Dict] = None
    ):
        """Record user interaction event."""
        if query_id not in self.active_sessions:
            return
            
        session = self.active_sessions[query_id]
        
        if interaction_type == "click":
            session["click_events"].append({
                "timestamp": time.time(),
                "metadata": metadata
            })
        elif interaction_type == "copy":
            session["copy_events"] += 1
        elif interaction_type == "share":
            session["share_events"] += 1
        elif interaction_type == "export":
            session["export_events"] += 1
    
    def end_session(self, query_id: str, follow_up: bool = False) -> InteractionSignals:
        """End session and compute engagement signals."""
        if query_id not in self.active_sessions:
            return InteractionSignals(0, 0, 0, 0, 0, 0, 0, 0)
            
        session = self.active_sessions[query_id]
        end_time = time.time()
        
        # Compute metrics
        dwell_time = end_time - session["start_time"]
        
        scroll_depth = 0.0
        if session["scroll_events"]:
            scroll_depth = max(e["depth"] for e in session["scroll_events"])
        
        signals = InteractionSignals(
            dwell_time_seconds=dwell_time,
            scroll_depth=scroll_depth,
            click_count=len(session["click_events"]),
            copy_events=session["copy_events"],
            share_events=session["share_events"],
            export_events=session["export_events"],
            follow_up_queries=1 if follow_up else 0,
            return_visits=0  # Tracked separately
        )
        
        # Persist signals
        self._persist_signals(query_id, session["user_id"], signals)
        
        # Clean up session
        del self.active_sessions[query_id]
        
        return signals
    
    def _persist_signals(
        self,
        query_id: str,
        user_id: Optional[str],
        signals: InteractionSignals
    ):
        """Persist interaction signals to storage."""
        import os
        import json
        
        os.makedirs(self.storage_path, exist_ok=True)
        
        record = {
            "query_id": query_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "dwell_time": signals.dwell_time_seconds,
            "scroll_depth": signals.scroll_depth,
            "click_count": signals.click_count,
            "copy_events": signals.copy_events,
            "share_events": signals.share_events,
            "export_events": signals.export_events,
            "engagement_score": signals.compute_engagement_score()
        }
        
        filename = f"{self.storage_path}/implicit_feedback_{datetime.now():%Y%m%d}.jsonl"
        with open(filename, "a") as f:
            f.write(json.dumps(record) + "\n")
```

---

### 3.2 Response Quality Evaluation

**File:** `src/self_improve/quality_evaluator.py`

```python
"""
Response Quality Evaluation System
ML-powered evaluation of response quality across multiple dimensions.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import numpy as np
import json

# ML imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.pipeline import Pipeline
import joblib

@dataclass
class QualityDimensions:
    """Quality scores across different dimensions."""
    overall: float  # 0.0 to 1.0
    accuracy: float
    completeness: float
    relevance: float
    clarity: float
    actionability: float
    
    def to_dict(self) -> Dict:
        return {
            "overall": self.overall,
            "accuracy": self.accuracy,
            "completeness": self.completeness,
            "relevance": self.relevance,
            "clarity": self.clarity,
            "actionability": self.actionability
        }

@dataclass
class QualityEvaluation:
    """Complete quality evaluation result."""
    evaluation_id: str
    query_id: str
    query: str
    response: str
    dimensions: QualityDimensions
    confidence: float
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "evaluation_id": self.evaluation_id,
            "query_id": self.query_id,
            "query": self.query,
            "response": self.response[:500],  # Truncate for storage
            "dimensions": self.dimensions.to_dict(),
            "confidence": self.confidence,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp.isoformat()
        }

class MLQualityEvaluator:
    """
    Machine learning-based response quality evaluator.
    
    Uses ensemble models to evaluate responses across multiple dimensions:
    - Accuracy: Factual correctness
    - Completeness: Coverage of query aspects
    - Relevance: Alignment with query intent
    - Clarity: Understandability
    - Actionability: Practical utility
    """
    
    def __init__(self, models_dir: str = "models/self_improve"):
        self.models_dir = models_dir
        self.dimension_models: Dict[str, Any] = {}
        self.overall_model: Optional[Any] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained quality evaluation models."""
        import os
        
        model_path = f"{self.models_dir}/quality_classifier.pkl"
        vectorizer_path = f"{self.models_dir}/feedback_encoder.pkl"
        
        if os.path.exists(model_path):
            self.overall_model = joblib.load(model_path)
        else:
            self._initialize_default_models()
            
        if os.path.exists(vectorizer_path):
            self.vectorizer = joblib.load(vectorizer_path)
        else:
            self.vectorizer = TfidfVectorizer(max_features=5000)
    
    def _initialize_default_models(self):
        """Initialize default models when no trained models exist."""
        from sklearn.ensemble import RandomForestRegressor
        
        # Use rule-based fallback until models are trained
        self.overall_model = None
        self.dimension_models = {}
    
    def evaluate(
        self,
        query: str,
        response: str,
        context: Optional[Dict] = None
    ) -> QualityEvaluation:
        """
        Evaluate response quality using ML models and heuristics.
        
        Args:
            query: Original user query
            response: Generated response
            context: Optional context (tools used, data sources, etc.)
            
        Returns:
            QualityEvaluation with scores and improvement suggestions
        """
        # Extract features
        features = self._extract_features(query, response, context)
        
        # Evaluate each dimension
        dimensions = self._evaluate_dimensions(features, query, response)
        
        # Identify issues
        issues = self._identify_issues(query, response, dimensions)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(issues, dimensions)
        
        # Compute confidence
        confidence = self._compute_confidence(features, dimensions)
        
        return QualityEvaluation(
            evaluation_id=self._generate_id(),
            query_id=context.get("query_id", "unknown") if context else "unknown",
            query=query,
            response=response,
            dimensions=dimensions,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions,
            timestamp=datetime.now()
        )
    
    def _extract_features(
        self,
        query: str,
        response: str,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Extract features for quality evaluation."""
        features = {
            # Length features
            "query_length": len(query.split()),
            "response_length": len(response.split()),
            "response_char_length": len(response),
            
            # Ratio features
            "response_query_ratio": len(response.split()) / max(len(query.split()), 1),
            
            # Coverage features
            "query_terms_in_response": self._count_query_terms(query, response),
            
            # Structure features
            "has_bullet_points": "•" in response or "-" in response,
            "has_numbers": any(c.isdigit() for c in response),
            "has_tables": "|" in response,
            "paragraph_count": response.count("\n\n") + 1,
            
            # Context features
            "tools_used_count": len(context.get("tools_used", [])) if context else 0,
            "data_sources_count": len(context.get("data_sources", [])) if context else 0,
        }
        
        return features
    
    def _count_query_terms(self, query: str, response: str) -> float:
        """Count how many query terms appear in response."""
        query_terms = set(query.lower().split())
        response_lower = response.lower()
        matches = sum(1 for term in query_terms if term in response_lower)
        return matches / len(query_terms) if query_terms else 0.0
    
    def _evaluate_dimensions(
        self,
        features: Dict[str, Any],
        query: str,
        response: str
    ) -> QualityDimensions:
        """Evaluate quality across all dimensions."""
        
        # Use ML models if available, otherwise use heuristics
        if self.overall_model:
            return self._ml_evaluate_dimensions(features)
        else:
            return self._heuristic_evaluate_dimensions(features, query, response)
    
    def _heuristic_evaluate_dimensions(
        self,
        features: Dict[str, Any],
        query: str,
        response: str
    ) -> QualityDimensions:
        """Heuristic-based dimension evaluation."""
        
        # Accuracy heuristic: Check for data-backed statements
        accuracy = 0.7  # Base accuracy
        if features["has_numbers"]:
            accuracy += 0.1
        if features["data_sources_count"] > 0:
            accuracy += 0.1
        accuracy = min(accuracy, 1.0)
        
        # Completeness heuristic
        completeness = features["query_terms_in_response"]
        if features["response_length"] > 50:
            completeness = min(completeness + 0.2, 1.0)
        
        # Relevance heuristic
        relevance = features["query_terms_in_response"]
        if features["response_query_ratio"] > 1.0:
            relevance = min(relevance + 0.1, 1.0)
        
        # Clarity heuristic
        clarity = 0.7
        if features["has_bullet_points"]:
            clarity += 0.1
        if features["paragraph_count"] <= 3:
            clarity += 0.1
        if features["response_length"] < 200:
            clarity += 0.1
        clarity = min(clarity, 1.0)
        
        # Actionability heuristic
        actionability = 0.6
        action_keywords = ["recommend", "should", "can", "will", "next", "step"]
        if any(kw in response.lower() for kw in action_keywords):
            actionability += 0.2
        if features["has_bullet_points"]:
            actionability += 0.1
        actionability = min(actionability, 1.0)
        
        # Overall score (weighted average)
        overall = (
            accuracy * 0.25 +
            completeness * 0.20 +
            relevance * 0.25 +
            clarity * 0.15 +
            actionability * 0.15
        )
        
        return QualityDimensions(
            overall=round(overall, 3),
            accuracy=round(accuracy, 3),
            completeness=round(completeness, 3),
            relevance=round(relevance, 3),
            clarity=round(clarity, 3),
            actionability=round(actionability, 3)
        )
    
    def _identify_issues(
        self,
        query: str,
        response: str,
        dimensions: QualityDimensions
    ) -> List[Dict[str, Any]]:
        """Identify specific quality issues."""
        issues = []
        
        if dimensions.completeness < 0.5:
            issues.append({
                "type": "incomplete",
                "severity": "high",
                "description": "Response may not fully address query",
                "dimension": "completeness"
            })
        
        if dimensions.clarity < 0.6:
            issues.append({
                "type": "unclear",
                "severity": "medium",
                "description": "Response may be difficult to understand",
                "dimension": "clarity"
            })
        
        if dimensions.actionability < 0.5:
            issues.append({
                "type": "not_actionable",
                "severity": "medium",
                "description": "Response lacks actionable recommendations",
                "dimension": "actionability"
            })
        
        if len(response.split()) < 20:
            issues.append({
                "type": "too_short",
                "severity": "high",
                "description": "Response appears too brief",
                "dimension": "completeness"
            })
        
        return issues
    
    def _generate_suggestions(
        self,
        issues: List[Dict[str, Any]],
        dimensions: QualityDimensions
    ) -> List[str]:
        """Generate improvement suggestions based on issues."""
        suggestions = []
        
        for issue in issues:
            if issue["type"] == "incomplete":
                suggestions.append("Expand response to cover all aspects of the query")
            elif issue["type"] == "unclear":
                suggestions.append("Use bullet points and shorter paragraphs for clarity")
            elif issue["type"] == "not_actionable":
                suggestions.append("Include specific recommendations or next steps")
            elif issue["type"] == "too_short":
                suggestions.append("Provide more detailed information")
        
        if dimensions.accuracy < 0.7:
            suggestions.append("Include more data-backed statements with citations")
        
        return suggestions
    
    def _compute_confidence(
        self,
        features: Dict[str, Any],
        dimensions: QualityDimensions
    ) -> float:
        """Compute confidence in the quality evaluation."""
        # Higher confidence with more features
        feature_count = sum(1 for v in features.values() if v)
        base_confidence = min(feature_count / 10, 0.9)
        
        # Adjust based on dimension variance
        dimension_values = [
            dimensions.accuracy,
            dimensions.completeness,
            dimensions.relevance,
            dimensions.clarity,
            dimensions.actionability
        ]
        variance = np.var(dimension_values)
        
        # Lower confidence if dimensions vary widely
        confidence = base_confidence * (1 - variance)
        
        return round(max(confidence, 0.3), 3)
    
    def _generate_id(self) -> str:
        """Generate unique evaluation ID."""
        import uuid
        return str(uuid.uuid4())[:8]
```

---

### 3.3 Performance Metrics Tracking

**File:** `src/self_improve/metrics_tracker.py`

```python
"""
Performance Metrics Tracking System
Comprehensive tracking of system performance and model effectiveness.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from collections import defaultdict
import threading

@dataclass
class ModelPerformanceMetrics:
    """Metrics for model performance tracking."""
    model_name: str
    model_version: str
    timestamp: datetime
    
    # Prediction metrics
    prediction_count: int = 0
    prediction_latency_ms: float = 0.0
    prediction_latency_p95_ms: float = 0.0
    prediction_latency_p99_ms: float = 0.0
    
    # Accuracy metrics
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mae: Optional[float] = None  # Mean Absolute Error
    rmse: Optional[float] = None  # Root Mean Square Error
    
    # Drift metrics
    data_drift_score: Optional[float] = None
    concept_drift_score: Optional[float] = None
    feature_drift_scores: Dict[str, float] = field(default_factory=dict)
    
    # Resource metrics
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

@dataclass
class SystemHealthMetrics:
    """System-level health metrics."""
    timestamp: datetime
    
    # Availability
    uptime_seconds: float = 0.0
    availability_percent: float = 100.0
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_rate: float = 0.0
    
    # Latency metrics
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    
    # Throughput
    requests_per_second: float = 0.0
    
    # Resource utilization
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage_percent: float = 0.0

@dataclass
class UserExperienceMetrics:
    """User experience and satisfaction metrics."""
    timestamp: datetime
    period: str  # "daily", "weekly", "monthly"
    
    # Engagement
    active_users: int = 0
    total_sessions: int = 0
    avg_session_duration_seconds: float = 0.0
    
    # Satisfaction
    explicit_feedback_count: int = 0
    avg_satisfaction_score: float = 0.0
    nps_score: Optional[float] = None  # Net Promoter Score
    
    # Quality
    avg_response_quality: float = 0.0
    high_quality_response_percent: float = 0.0
    
    # Retention
    return_user_percent: float = 0.0
    churn_rate: float = 0.0

class MetricsTracker:
    """
    Comprehensive metrics tracking and aggregation system.
    
    Tracks:
    - Model performance over time
    - System health and availability
    - User experience metrics
    - Custom business metrics
    
    Features:
    - Real-time metric collection
    - Automatic aggregation (hourly, daily, weekly)
    - Anomaly detection
    - Trend analysis
    """
    
    def __init__(self, storage_path: str = "data/metrics"):
        self.storage_path = storage_path
        self.metrics_buffer: Dict[str, List[Dict]] = defaultdict(list)
        self.buffer_lock = threading.Lock()
        self.buffer_size = 1000
        
        # Aggregation windows
        self.aggregation_windows = {
            "hourly": timedelta(hours=1),
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
        }
        
        # Initialize storage
        import os
        os.makedirs(storage_path, exist_ok=True)
    
    def record_model_prediction(
        self,
        model_name: str,
        model_version: str,
        latency_ms: float,
        prediction: Any,
        actual: Optional[Any] = None
    ):
        """Record a single model prediction."""
        metric = {
            "type": "model_prediction",
            "model_name": model_name,
            "model_version": model_version,
            "timestamp": datetime.now().isoformat(),
            "latency_ms": latency_ms,
            "prediction": prediction,
            "actual": actual
        }
        self._buffer_metric(metric)
    
    def record_model_performance(
        self,
        metrics: ModelPerformanceMetrics
    ):
        """Record comprehensive model performance metrics."""
        metric = {
            "type": "model_performance",
            **self._dataclass_to_dict(metrics)
        }
        self._buffer_metric(metric)
    
    def record_system_health(
        self,
        metrics: SystemHealthMetrics
    ):
        """Record system health metrics."""
        metric = {
            "type": "system_health",
            **self._dataclass_to_dict(metrics)
        }
        self._buffer_metric(metric)
    
    def record_user_experience(
        self,
        metrics: UserExperienceMetrics
    ):
        """Record user experience metrics."""
        metric = {
            "type": "user_experience",
            **self._dataclass_to_dict(metrics)
        }
        self._buffer_metric(metric)
    
    def record_custom_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ):
        """Record a custom metric."""
        metric = {
            "type": "custom",
            "metric_name": metric_name,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "tags": tags or {}
        }
        self._buffer_metric(metric)
    
    def _buffer_metric(self, metric: Dict):
        """Add metric to buffer and flush if needed."""
        with self.buffer_lock:
            metric_type = metric["type"]
            self.metrics_buffer[metric_type].append(metric)
            
            if len(self.metrics_buffer[metric_type]) >= self.buffer_size:
                self._flush_buffer(metric_type)
    
    def _flush_buffer(self, metric_type: str):
        """Persist buffered metrics to storage."""
        import os
        
        if metric_type not in self.metrics_buffer:
            return
            
        metrics = self.metrics_buffer[metric_type]
        if not metrics:
            return
        
        # Create parquet file for efficient storage
        df = pd.DataFrame(metrics)
        
        filename = f"{self.storage_path}/{metric_type}_{datetime.now():%Y%m%d}.parquet"
        
        # Append to existing file if it exists
        if os.path.exists(filename):
            existing_df = pd.read_parquet(filename)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_parquet(filename, index=False)
        
        # Clear buffer
        self.metrics_buffer[metric_type] = []
    
    def get_metrics_summary(
        self,
        metric_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get summary statistics for a metric type."""
        import os
        
        # Load relevant parquet files
        dfs = []
        for filename in os.listdir(self.storage_path):
            if filename.startswith(metric_type) and filename.endswith(".parquet"):
                filepath = os.path.join(self.storage_path, filename)
                dfs.append(pd.read_parquet(filepath))
        
        if not dfs:
            return {"error": "No metrics found"}
        
        df = pd.concat(dfs, ignore_index=True)
        
        # Apply date filters
        if start_date or end_date:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            if start_date:
                df = df[df["timestamp"] >= start_date]
            if end_date:
                df = df[df["timestamp"] <= end_date]
        
        # Compute summary statistics
        summary = {
            "total_records": len(df),
            "date_range": {
                "start": df["timestamp"].min() if len(df) > 0 else None,
                "end": df["timestamp"].max() if len(df) > 0 else None
            }
        }
        
        # Add numeric column statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col != "timestamp":
                summary[col] = {
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "p95": df[col].quantile(0.95),
                    "p99": df[col].quantile(0.99)
                }
        
        return summary
    
    def detect_anomalies(
        self,
        metric_name: str,
        window_hours: int = 24,
        threshold_std: float = 3.0
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in metric values."""
        # Load recent metrics
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=window_hours)
        
        summary = self.get_metrics_summary("custom", start_date, end_date)
        
        if "error" in summary or metric_name not in summary:
            return []
        
        metric_stats = summary[metric_name]
        mean = metric_stats["mean"]
        std = metric_stats["std"]
        
        threshold = threshold_std * std
        
        # This is a simplified anomaly detection
        # In practice, you'd load the actual time series data
        anomalies = []
        
        if metric_stats["max"] > mean + threshold:
            anomalies.append({
                "type": "high",
                "value": metric_stats["max"],
                "threshold": mean + threshold,
                "severity": "warning" if metric_stats["max"] < mean + 2*threshold else "critical"
            })
        
        if metric_stats["min"] < mean - threshold:
            anomalies.append({
                "type": "low",
                "value": metric_stats["min"],
                "threshold": mean - threshold,
                "severity": "warning" if metric_stats["min"] > mean - 2*threshold else "critical"
            })
        
        return anomalies
    
    def _dataclass_to_dict(self, obj: Any) -> Dict:
        """Convert dataclass to dictionary."""
        if hasattr(obj, "__dataclass_fields__"):
            return {
                field: getattr(obj, field)
                for field in obj.__dataclass_fields__
            }
        return {}
```

---

### 3.4 A/B Testing Framework

**File:** `src/self_improve/ab_testing.py`

```python
"""
A/B Testing Framework for ResilienceAI
Enables controlled experimentation for system improvements.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import random
import hashlib
import pandas as pd
import numpy as np
from scipy import stats

class ExperimentStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ExperimentType(Enum):
    AB_TEST = "ab_test"           # Two variants
    MULTIVARIATE = "multivariate"  # Multiple variants
    BANDIT = "bandit"              # Multi-armed bandit

@dataclass
class Variant:
    """Experiment variant configuration."""
    variant_id: str
    name: str
    description: str
    config: Dict[str, Any]
    traffic_percentage: float  # 0.0 to 1.0
    
    # Metrics
    impressions: int = 0
    conversions: int = 0
    metrics: Dict[str, List[float]] = field(default_factory=dict)

@dataclass
class Experiment:
    """Experiment definition and state."""
    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    status: ExperimentStatus
    
    # Variants
    variants: List[Variant]
    control_variant_id: str
    
    # Configuration
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_sample_size: Optional[int] = None
    min_confidence_level: float = 0.95
    
    # Metrics configuration
    primary_metric: str = "conversion_rate"
    secondary_metrics: List[str] = field(default_factory=list)
    
    # Results
    results: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class ABTestingFramework:
    """
    Comprehensive A/B testing framework for ResilienceAI.
    
    Features:
    - Multiple experiment types (A/B, multivariate, bandit)
    - Automatic traffic allocation
    - Statistical significance testing
    - Real-time results monitoring
    - Automatic winner selection
    """
    
    def __init__(self, storage_path: str = "data/experiments"):
        self.storage_path = storage_path
        self.experiments: Dict[str, Experiment] = {}
        self.active_assignments: Dict[str, str] = {}  # user_id -> variant_id
        
        import os
        os.makedirs(storage_path, exist_ok=True)
        self._load_experiments()
    
    def create_experiment(
        self,
        name: str,
        description: str,
        experiment_type: ExperimentType,
        variants: List[Dict[str, Any]],
        control_variant_id: str,
        primary_metric: str = "conversion_rate",
        secondary_metrics: Optional[List[str]] = None,
        target_sample_size: Optional[int] = None,
        min_confidence_level: float = 0.95
    ) -> Experiment:
        """
        Create a new experiment.
        
        Args:
            name: Experiment name
            description: Experiment description
            experiment_type: Type of experiment
            variants: List of variant configurations
            control_variant_id: ID of control variant
            primary_metric: Primary success metric
            secondary_metrics: Additional metrics to track
            target_sample_size: Target number of samples
            min_confidence_level: Minimum confidence for significance
            
        Returns:
            Created Experiment object
        """
        experiment_id = self._generate_experiment_id(name)
        
        # Create variant objects
        variant_objects = []
        for v in variants:
            variant_objects.append(Variant(
                variant_id=v["id"],
                name=v["name"],
                description=v.get("description", ""),
                config=v["config"],
                traffic_percentage=v.get("traffic_percentage", 1.0 / len(variants))
            ))
        
        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            experiment_type=experiment_type,
            status=ExperimentStatus.DRAFT,
            variants=variant_objects,
            control_variant_id=control_variant_id,
            primary_metric=primary_metric,
            secondary_metrics=secondary_metrics or [],
            target_sample_size=target_sample_size,
            min_confidence_level=min_confidence_level
        )
        
        self.experiments[experiment_id] = experiment
        self._save_experiment(experiment)
        
        return experiment
    
    def start_experiment(self, experiment_id: str) -> Experiment:
        """Start a draft experiment."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.RUNNING
        experiment.start_date = datetime.now()
        experiment.updated_at = datetime.now()
        
        self._save_experiment(experiment)
        return experiment
    
    def assign_variant(
        self,
        experiment_id: str,
        user_id: str,
        context: Optional[Dict] = None
    ) -> Variant:
        """
        Assign a variant to a user.
        
        Uses consistent hashing for sticky assignments.
        """
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        
        if experiment.status != ExperimentStatus.RUNNING:
            # Return control variant if experiment not running
            return next(v for v in experiment.variants 
                       if v.variant_id == experiment.control_variant_id)
        
        # Check for existing assignment
        assignment_key = f"{experiment_id}:{user_id}"
        if assignment_key in self.active_assignments:
            variant_id = self.active_assignments[assignment_key]
            return next(v for v in experiment.variants if v.variant_id == variant_id)
        
        # Consistent hash assignment
        hash_input = f"{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Weighted random selection based on traffic percentages
        variants = experiment.variants
        weights = [v.traffic_percentage for v in variants]
        
        # Use hash to make deterministic
        random.seed(hash_value)
        selected_variant = random.choices(variants, weights=weights)[0]
        random.seed()  # Reset seed
        
        # Record assignment
        self.active_assignments[assignment_key] = selected_variant.variant_id
        selected_variant.impressions += 1
        
        self._save_experiment(experiment)
        
        return selected_variant
    
    def record_event(
        self,
        experiment_id: str,
        user_id: str,
        event_type: str,
        value: Optional[float] = None,
        metadata: Optional[Dict] = None
    ):
        """Record an event for a user in an experiment."""
        if experiment_id not in self.experiments:
            return
        
        experiment = self.experiments[experiment_id]
        assignment_key = f"{experiment_id}:{user_id}"
        
        if assignment_key not in self.active_assignments:
            return
        
        variant_id = self.active_assignments[assignment_key]
        variant = next(v for v in experiment.variants if v.variant_id == variant_id)
        
        # Record conversion
        if event_type == "conversion":
            variant.conversions += 1
        
        # Record metric value
        if value is not None:
            if event_type not in variant.metrics:
                variant.metrics[event_type] = []
            variant.metrics[event_type].append(value)
        
        experiment.updated_at = datetime.now()
        self._save_experiment(experiment)
        
        # Check for automatic winner selection
        self._check_winner_selection(experiment)
    
    def get_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get statistical results for an experiment."""
        if experiment_id not in self.experiments:
            return {"error": "Experiment not found"}
        
        experiment = self.experiments[experiment_id]
        
        results = {
            "experiment_id": experiment_id,
            "name": experiment.name,
            "status": experiment.status.value,
            "primary_metric": experiment.primary_metric,
            "variants": []
        }
        
        control_variant = next(
            v for v in experiment.variants 
            if v.variant_id == experiment.control_variant_id
        )
        
        for variant in experiment.variants:
            variant_result = {
                "variant_id": variant.variant_id,
                "name": variant.name,
                "impressions": variant.impressions,
                "conversions": variant.conversions,
                "conversion_rate": variant.conversions / max(variant.impressions, 1),
                "metrics": {}
            }
            
            # Compute metric statistics
            for metric_name, values in variant.metrics.items():
                if values:
                    variant_result["metrics"][metric_name] = {
                        "count": len(values),
                        "mean": np.mean(values),
                        "std": np.std(values),
                        "median": np.median(values)
                    }
            
            # Statistical comparison with control
            if variant.variant_id != experiment.control_variant_id:
                variant_result["comparison"] = self._compare_variants(
                    control_variant, variant, experiment.primary_metric
                )
            
            results["variants"].append(variant_result)
        
        return results
    
    def _compare_variants(
        self,
        control: Variant,
        treatment: Variant,
        metric: str
    ) -> Dict[str, Any]:
        """Statistically compare two variants."""
        # Get metric values
        control_values = control.metrics.get(metric, [])
        treatment_values = treatment.metrics.get(metric, [])
        
        if not control_values or not treatment_values:
            return {"error": "Insufficient data for comparison"}
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(treatment_values, control_values)
        
        # Compute lift
        control_mean = np.mean(control_values)
        treatment_mean = np.mean(treatment_values)
        lift = (treatment_mean - control_mean) / control_mean if control_mean != 0 else 0
        
        # Compute confidence interval
        ci = stats.tconfint(
            treatment_mean - control_mean,
            np.sqrt(np.var(treatment_values)/len(treatment_values) + 
                   np.var(control_values)/len(control_values)),
            df=len(treatment_values) + len(control_values) - 2,
            alpha=0.05
        )
        
        return {
            "lift_percent": lift * 100,
            "p_value": p_value,
            "is_significant": p_value < 0.05,
            "confidence_interval": {
                "lower": ci[0],
                "upper": ci[1]
            },
            "control_mean": control_mean,
            "treatment_mean": treatment_mean
        }
    
    def _check_winner_selection(self, experiment: Experiment):
        """Check if a winner can be automatically selected."""
        if not experiment.target_sample_size:
            return
        
        total_impressions = sum(v.impressions for v in experiment.variants)
        
        if total_impressions < experiment.target_sample_size:
            return
        
        # Check if any variant is significantly better
        results = self.get_results(experiment.experiment_id)
        
        best_variant = None
        best_lift = 0
        
        for variant_result in results["variants"]:
            if "comparison" in variant_result:
                comparison = variant_result["comparison"]
                if comparison.get("is_significant") and comparison["lift_percent"] > best_lift:
                    best_lift = comparison["lift_percent"]
                    best_variant = variant_result["variant_id"]
        
        if best_variant:
            # Auto-complete experiment with winner
            experiment.status = ExperimentStatus.COMPLETED
            experiment.end_date = datetime.now()
            experiment.results = {
                "winner_variant_id": best_variant,
                "lift_percent": best_lift,
                "total_samples": total_impressions
            }
            self._save_experiment(experiment)
    
    def _generate_experiment_id(self, name: str) -> str:
        """Generate unique experiment ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_input = f"{name}:{timestamp}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:6]
        return f"exp_{timestamp}_{hash_suffix}"
    
    def _save_experiment(self, experiment: Experiment):
        """Persist experiment to storage."""
        filepath = f"{self.storage_path}/{experiment.experiment_id}.json"
        
        # Convert to dict
        experiment_dict = {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "description": experiment.description,
            "experiment_type": experiment.experiment_type.value,
            "status": experiment.status.value,
            "variants": [
                {
                    "variant_id": v.variant_id,
                    "name": v.name,
                    "description": v.description,
                    "config": v.config,
                    "traffic_percentage": v.traffic_percentage,
                    "impressions": v.impressions,
                    "conversions": v.conversions,
                    "metrics": v.metrics
                }
                for v in experiment.variants
            ],
            "control_variant_id": experiment.control_variant_id,
            "start_date": experiment.start_date.isoformat() if experiment.start_date else None,
            "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
            "target_sample_size": experiment.target_sample_size,
            "min_confidence_level": experiment.min_confidence_level,
            "primary_metric": experiment.primary_metric,
            "secondary_metrics": experiment.secondary_metrics,
            "results": experiment.results,
            "created_at": experiment.created_at.isoformat(),
            "updated_at": experiment.updated_at.isoformat()
        }
        
        with open(filepath, "w") as f:
            json.dump(experiment_dict, f, indent=2)
    
    def _load_experiments(self):
        """Load existing experiments from storage."""
        import os
        
        if not os.path.exists(self.storage_path):
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                filepath = os.path.join(self.storage_path, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)
                
                # Reconstruct experiment object
                # (Simplified - full implementation would parse all fields)
                pass
```

---

### 3.5 Automated Model Retraining

**File:** `src/self_improve/model_retrainer.py`

```python
"""
Automated Model Retraining Pipeline
Manages continuous model improvement through automated retraining.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

class RetrainTrigger(Enum):
    SCHEDULED = "scheduled"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DATA_DRIFT = "data_drift"
    MANUAL = "manual"
    NEW_DATA_THRESHOLD = "new_data_threshold"

@dataclass
class ModelVersion:
    """Model version metadata."""
    model_name: str
    version: str
    training_date: datetime
    metrics: Dict[str, float]
    training_data_hash: str
    hyperparameters: Dict[str, Any]
    artifacts_path: str
    is_production: bool = False

class AutomatedModelRetrainer:
    """
    Automated model retraining pipeline.
    
    Features:
    - Scheduled retraining (daily, weekly, monthly)
    - Performance-based triggers
    - Data drift detection
    - A/B testing for new models
    - Automatic rollback on degradation
    - Model versioning and lineage
    """
    
    def __init__(
        self,
        models_dir: str = "models",
        retraining_config: Optional[Dict] = None
    ):
        self.models_dir = models_dir
        self.config = retraining_config or self._default_config()
        self.model_registry: Dict[str, List[ModelVersion]] = {}
        self.training_jobs: List[Dict] = []
        
        os.makedirs(models_dir, exist_ok=True)
        self._load_model_registry()
    
    def _default_config(self) -> Dict:
        """Default retraining configuration."""
        return {
            "scheduled_retraining": {
                "enabled": True,
                "frequency": "weekly",  # daily, weekly, monthly
                "day_of_week": 0,  # Monday
                "hour": 2  # 2 AM
            },
            "performance_triggers": {
                "enabled": True,
                "accuracy_threshold": 0.05,  # Retrain if accuracy drops 5%
                "latency_threshold": 1.5,  # Retrain if latency increases 50%
            },
            "data_drift_triggers": {
                "enabled": True,
                "drift_threshold": 0.1,
                "check_frequency_hours": 24
            },
            "new_data_triggers": {
                "enabled": True,
                "min_new_samples": 1000,
                "min_new_sample_percent": 0.1  # 10% new data
            },
            "validation": {
                "test_size": 0.2,
                "min_test_samples": 100,
                "cross_validation_folds": 5
            },
            "deployment": {
                "auto_deploy": False,
                "require_ab_test": True,
                "min_improvement_percent": 2.0
            }
        }
    
    def register_model(
        self,
        model_name: str,
        model: Any,
        training_data: pd.DataFrame,
        metrics: Dict[str, float],
        hyperparameters: Dict[str, Any]
    ) -> ModelVersion:
        """
        Register a new model version.
        
        Args:
            model_name: Name of the model
            model: Trained model object
            training_data: Data used for training
            metrics: Performance metrics
            hyperparameters: Model hyperparameters
            
        Returns:
            ModelVersion with version info
        """
        # Generate version
        version = self._generate_version(model_name)
        
        # Compute data hash
        data_hash = self._compute_data_hash(training_data)
        
        # Save model artifacts
        artifacts_path = f"{self.models_dir}/{model_name}/{version}"
        os.makedirs(artifacts_path, exist_ok=True)
        
        # Save model
        model_path = f"{artifacts_path}/model.pkl"
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata = {
            "model_name": model_name,
            "version": version,
            "training_date": datetime.now().isoformat(),
            "metrics": metrics,
            "training_data_hash": data_hash,
            "hyperparameters": hyperparameters
        }
        
        metadata_path = f"{artifacts_path}/metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Create version object
        version_obj = ModelVersion(
            model_name=model_name,
            version=version,
            training_date=datetime.now(),
            metrics=metrics,
            training_data_hash=data_hash,
            hyperparameters=hyperparameters,
            artifacts_path=artifacts_path
        )
        
        # Register
        if model_name not in self.model_registry:
            self.model_registry[model_name] = []
        self.model_registry[model_name].append(version_obj)
        
        self._save_registry()
        
        return version_obj
    
    def check_retraining_needed(
        self,
        model_name: str,
        current_metrics: Optional[Dict[str, float]] = None,
        new_data: Optional[pd.DataFrame] = None
    ) -> List[RetrainTrigger]:
        """
        Check if retraining is needed based on triggers.
        
        Returns:
            List of triggers that indicate retraining is needed
        """
        triggers = []
        
        # Check scheduled retraining
        if self._is_scheduled_retraining_due():
            triggers.append(RetrainTrigger.SCHEDULED)
        
        # Check performance degradation
        if current_metrics and self._check_performance_degradation(
            model_name, current_metrics
        ):
            triggers.append(RetrainTrigger.PERFORMANCE_DEGRADATION)
        
        # Check data drift
        if new_data is not None and self._check_data_drift(model_name, new_data):
            triggers.append(RetrainTrigger.DATA_DRIFT)
        
        # Check new data threshold
        if new_data is not None and self._check_new_data_threshold(
            model_name, new_data
        ):
            triggers.append(RetrainTrigger.NEW_DATA_THRESHOLD)
        
        return triggers
    
    def retrain_model(
        self,
        model_name: str,
        training_data: pd.DataFrame,
        target_column: str,
        model_trainer: Callable,
        trigger: RetrainTrigger = RetrainTrigger.MANUAL
    ) -> ModelVersion:
        """
        Execute model retraining pipeline.
        
        Args:
            model_name: Name of model to retrain
            training_data: New training data
            target_column: Name of target column
            model_trainer: Function that trains and returns (model, metrics)
            trigger: What triggered the retraining
            
        Returns:
            New ModelVersion
        """
        from sklearn.model_selection import train_test_split
        
        # Log training job
        job_id = self._log_training_job(model_name, trigger)
        
        try:
            # Split data
            test_size = self.config["validation"]["test_size"]
            train_df, test_df = train_test_split(
                training_data, test_size=test_size, random_state=42
            )
            
            # Train model
            X_train = train_df.drop(columns=[target_column])
            y_train = train_df[target_column]
            X_test = test_df.drop(columns=[target_column])
            y_test = test_df[target_column]
            
            model, metrics = model_trainer(X_train, y_train, X_test, y_test)
            
            # Register new version
            version = self.register_model(
                model_name=model_name,
                model=model,
                training_data=training_data,
                metrics=metrics,
                hyperparameters={}  # Extract from trainer if needed
            )
            
            # Update job status
            self._update_training_job(job_id, "completed", metrics)
            
            # Check if should auto-deploy
            if self.config["deployment"]["auto_deploy"]:
                self._evaluate_for_deployment(model_name, version)
            
            return version
            
        except Exception as e:
            self._update_training_job(job_id, "failed", {"error": str(e)})
            raise
    
    def deploy_model(self, model_name: str, version: str) -> bool:
        """
        Deploy a model version to production.
        
        Args:
            model_name: Name of the model
            version: Version to deploy
            
        Returns:
            True if deployment successful
        """
        # Find version
        versions = self.model_registry.get(model_name, [])
        version_obj = next((v for v in versions if v.version == version), None)
        
        if not version_obj:
            raise ValueError(f"Version {version} not found for model {model_name}")
        
        # Undeploy current production version
        for v in versions:
            if v.is_production:
                v.is_production = False
        
        # Deploy new version
        version_obj.is_production = True
        
        # Create production symlink
        production_path = f"{self.models_dir}/{model_name}/production"
        if os.path.exists(production_path):
            os.remove(production_path)
        os.symlink(version_obj.artifacts_path, production_path)
        
        self._save_registry()
        
        return True
    
    def rollback_model(self, model_name: str) -> Optional[ModelVersion]:
        """
        Rollback to previous production version.
        
        Returns:
            Previous version or None if no rollback possible
        """
        versions = self.model_registry.get(model_name, [])
        
        # Find current production
        current = next((v for v in versions if v.is_production), None)
        if not current:
            return None
        
        # Find previous version
        current_idx = versions.index(current)
        if current_idx == 0:
            return None  # No previous version
        
        previous = versions[current_idx - 1]
        self.deploy_model(model_name, previous.version)
        
        return previous
    
    def _is_scheduled_retraining_due(self) -> bool:
        """Check if scheduled retraining is due."""
        config = self.config["scheduled_retraining"]
        if not config["enabled"]:
            return False
        
        now = datetime.now()
        
        if config["frequency"] == "daily":
            return now.hour == config["hour"]
        elif config["frequency"] == "weekly":
            return (now.weekday() == config["day_of_week"] and 
                    now.hour == config["hour"])
        elif config["frequency"] == "monthly":
            return (now.day == 1 and now.hour == config["hour"])
        
        return False
    
    def _check_performance_degradation(
        self,
        model_name: str,
        current_metrics: Dict[str, float]
    ) -> bool:
        """Check if model performance has degraded."""
        versions = self.model_registry.get(model_name, [])
        if not versions:
            return False
        
        # Get best production metrics
        production = next((v for v in versions if v.is_production), versions[-1])
        baseline_metrics = production.metrics
        
        # Check accuracy degradation
        threshold = self.config["performance_triggers"]["accuracy_threshold"]
        
        for metric, current_value in current_metrics.items():
            if metric in baseline_metrics:
                baseline_value = baseline_metrics[metric]
                if baseline_value > 0:
                    degradation = (baseline_value - current_value) / baseline_value
                    if degradation > threshold:
                        return True
        
        return False
    
    def _check_data_drift(
        self,
        model_name: str,
        new_data: pd.DataFrame
    ) -> bool:
        """Check for data drift."""
        # Simplified drift detection using statistical tests
        # In production, use dedicated drift detection libraries
        
        versions = self.model_registry.get(model_name, [])
        if not versions:
            return False
        
        # Get training data hash from latest version
        latest = versions[-1]
        
        # Compute new data hash
        new_hash = self._compute_data_hash(new_data)
        
        # If hashes differ significantly, consider it drift
        # (This is a simplified check - real implementation would use
        # statistical tests like KS test, PSI, etc.)
        
        return new_hash != latest.training_data_hash
    
    def _check_new_data_threshold(
        self,
        model_name: str,
        new_data: pd.DataFrame
    ) -> bool:
        """Check if enough new data is available."""
        config = self.config["new_data_triggers"]
        if not config["enabled"]:
            return False
        
        # Check absolute threshold
        if len(new_data) >= config["min_new_samples"]:
            return True
        
        # Check percentage threshold
        versions = self.model_registry.get(model_name, [])
        if versions:
            # Estimate original training size from data hash
            # (In practice, store this explicitly)
            return False  # Simplified
        
        return False
    
    def _generate_version(self, model_name: str) -> str:
        """Generate new version string."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        versions = self.model_registry.get(model_name, [])
        version_num = len(versions) + 1
        return f"v{version_num}_{timestamp}"
    
    def _compute_data_hash(self, data: pd.DataFrame) -> str:
        """Compute hash of training data."""
        import hashlib
        
        # Use first 1000 rows and summary stats for hash
        sample = data.head(1000)
        stats = data.describe().values.tobytes()
        
        hash_input = str(sample.values.tobytes()) + str(stats)
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def _log_training_job(
        self,
        model_name: str,
        trigger: RetrainTrigger
    ) -> str:
        """Log training job start."""
        job_id = f"{model_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        job = {
            "job_id": job_id,
            "model_name": model_name,
            "trigger": trigger.value,
            "status": "started",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "metrics": None
        }
        
        self.training_jobs.append(job)
        return job_id
    
    def _update_training_job(
        self,
        job_id: str,
        status: str,
        metrics: Dict
    ):
        """Update training job status."""
        for job in self.training_jobs:
            if job["job_id"] == job_id:
                job["status"] = status
                job["end_time"] = datetime.now().isoformat()
                job["metrics"] = metrics
                break
    
    def _evaluate_for_deployment(self, model_name: str, version: ModelVersion):
        """Evaluate if new version should be auto-deployed."""
        # Compare with current production
        versions = self.model_registry.get(model_name, [])
        production = next((v for v in versions if v.is_production), None)
        
        if not production:
            # No production version, deploy
            self.deploy_model(model_name, version.version)
            return
        
        # Check improvement threshold
        min_improvement = self.config["deployment"]["min_improvement_percent"]
        
        # Compare primary metric (e.g., accuracy)
        primary_metric = "accuracy"  # Configurable
        
        if primary_metric in version.metrics and primary_metric in production.metrics:
            new_value = version.metrics[primary_metric]
            old_value = production.metrics[primary_metric]
            
            if old_value > 0:
                improvement = (new_value - old_value) / old_value * 100
                if improvement >= min_improvement:
                    self.deploy_model(model_name, version.version)
    
    def _save_registry(self):
        """Save model registry to disk."""
        registry_path = f"{self.models_dir}/registry.json"
        
        registry_data = {}
        for model_name, versions in self.model_registry.items():
            registry_data[model_name] = [
                {
                    "model_name": v.model_name,
                    "version": v.version,
                    "training_date": v.training_date.isoformat(),
                    "metrics": v.metrics,
                    "training_data_hash": v.training_data_hash,
                    "hyperparameters": v.hyperparameters,
                    "artifacts_path": v.artifacts_path,
                    "is_production": v.is_production
                }
                for v in versions
            ]
        
        with open(registry_path, "w") as f:
            json.dump(registry_data, f, indent=2)
    
    def _load_model_registry(self):
        """Load model registry from disk."""
        registry_path = f"{self.models_dir}/registry.json"
        
        if not os.path.exists(registry_path):
            return
        
        with open(registry_path, "r") as f:
            registry_data = json.load(f)
        
        for model_name, versions_data in registry_data.items():
            self.model_registry[model_name] = []
            for v_data in versions_data:
                version = ModelVersion(
                    model_name=v_data["model_name"],
                    version=v_data["version"],
                    training_date=datetime.fromisoformat(v_data["training_date"]),
                    metrics=v_data["metrics"],
                    training_data_hash=v_data["training_data_hash"],
                    hyperparameters=v_data["hyperparameters"],
                    artifacts_path=v_data["artifacts_path"],
                    is_production=v_data.get("is_production", False)
                )
                self.model_registry[model_name].append(version)
```

---

## 4. Integration Points

### 4.1 Integration with Existing Agent System

**File:** `src/agent.py` integration

```python
# Add to src/agent.py

from src.self_improve.feedback_collector import (
    ExplicitFeedbackCollector, 
    ImplicitFeedbackCollector
)
from src.self_improve.quality_evaluator import MLQualityEvaluator
from src.self_improve.metrics_tracker import MetricsTracker

class ResilienceAgent:
    """Enhanced agent with self-improvement capabilities."""
    
    def __init__(self, ...):
        # ... existing initialization ...
        
        # Initialize self-improvement components
        self.feedback_collector = ExplicitFeedbackCollector()
        self.implicit_collector = ImplicitFeedbackCollector()
        self.quality_evaluator = MLQualityEvaluator()
        self.metrics_tracker = MetricsTracker()
        
    def process_query(self, query: str, user_id: Optional[str] = None) -> Dict:
        """Process query with self-improvement tracking."""
        import time
        import uuid
        
        query_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Start implicit tracking
        self.implicit_collector.start_session(query_id, user_id)
        
        # Process query (existing logic)
        response = self._generate_response(query)
        
        # Evaluate quality
        context = {
            "query_id": query_id,
            "user_id": user_id,
            "tools_used": response.get("tools_used", []),
            "data_sources": response.get("data_sources", [])
        }
        
        quality_eval = self.quality_evaluator.evaluate(
            query=query,
            response=response["text"],
            context=context
        )
        
        # Record metrics
        latency_ms = (time.time() - start_time) * 1000
        self.metrics_tracker.record_custom_metric(
            metric_name="query_latency_ms",
            value=latency_ms,
            tags={"query_id": query_id}
        )
        
        self.metrics_tracker.record_custom_metric(
            metric_name="response_quality",
            value=quality_eval.dimensions.overall,
            tags={"query_id": query_id}
        )
        
        # Add quality info to response
        response["quality"] = quality_eval.dimensions.to_dict()
        response["query_id"] = query_id
        
        return response
    
    def submit_feedback(
        self,
        query_id: str,
        feedback_type: str,
        rating: Optional[int] = None,
        comments: Optional[str] = None
    ):
        """Submit explicit feedback for a query."""
        if feedback_type == "thumbs":
            self.feedback_collector.collect_thumbs_feedback(
                query_id=query_id,
                is_helpful=rating == 1,
                comments=comments
            )
        elif feedback_type == "rating":
            self.feedback_collector.collect_rating_feedback(
                query_id=query_id,
                rating=rating or 3,
                categories=[],  # Add category selection in UI
                comments=comments
            )
```

### 4.2 Integration with Dashboard

**File:** `app/main.py` integration

```python
# Add to Streamlit dashboard

import streamlit as st
from src.self_improve.feedback_collector import FeedbackCategory

def render_feedback_ui(query_id: str, response: str):
    """Render feedback collection UI."""
    st.subheader("Was this response helpful?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👍 Helpful"):
            agent.submit_feedback(query_id, "thumbs", 1)
            st.success("Thank you for your feedback!")
    
    with col2:
        if st.button("👎 Not Helpful"):
            agent.submit_feedback(query_id, "thumbs", 0)
            
            # Show detailed feedback form
            with st.expander("Tell us more"):
                categories = st.multiselect(
                    "What was the issue?",
                    [c.value for c in FeedbackCategory]
                )
                comments = st.text_area("Additional comments")
                if st.button("Submit"):
                    # Submit detailed feedback
                    pass
    
    # Rating slider
    rating = st.slider("Rate this response", 1, 5, 3)
    if st.button("Submit Rating"):
        agent.submit_feedback(query_id, "rating", rating)

def render_quality_metrics():
    """Render quality metrics dashboard."""
    st.header("Response Quality Metrics")
    
    # Get metrics summary
    summary = metrics_tracker.get_metrics_summary("custom")
    
    if "error" not in summary:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Avg Response Quality",
                f"{summary['response_quality']['mean']:.2f}"
            )
        
        with col2:
            st.metric(
                "Avg Latency (ms)",
                f"{summary['query_latency_ms']['mean']:.0f}"
            )
        
        with col3:
            st.metric(
                "Total Queries",
                summary["total_records"]
            )
```

---

## 5. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)
| Component | Priority | Effort | Impact |
|-----------|----------|--------|--------|
| Feedback Collection (Explicit) | P0 | Medium | High |
| Basic Quality Evaluation | P0 | Medium | High |
| Metrics Tracking | P0 | Low | Medium |
| Data Storage Setup | P0 | Low | Medium |

### Phase 2: Core ML (Weeks 3-4)
| Component | Priority | Effort | Impact |
|-----------|----------|--------|--------|
| ML Quality Evaluator | P1 | High | High |
| Implicit Feedback | P1 | Medium | Medium |
| Performance Metrics | P1 | Medium | Medium |
| Dashboard Integration | P1 | Medium | Medium |

### Phase 3: Advanced Features (Weeks 5-6)
| Component | Priority | Effort | Impact |
|-----------|----------|--------|--------|
| A/B Testing Framework | P2 | High | High |
| Model Retraining Pipeline | P2 | High | High |
| Hyperparameter Optimization | P2 | Medium | Medium |
| Feature Importance | P2 | Medium | Medium |

### Phase 4: Automation (Weeks 7-8)
| Component | Priority | Effort | Impact |
|-----------|----------|--------|--------|
| Continuous Learning Pipeline | P3 | High | High |
| System Adaptation Engine | P3 | High | High |
| Automated Model Deployment | P3 | Medium | High |
| Full Integration Testing | P3 | Medium | Critical |

---

## 6. Configuration

**File:** `config/self_improve.yaml`

```yaml
# Self-Improvement System Configuration

feedback:
  explicit:
    enabled: true
    buffer_size: 100
    storage_format: "jsonl"
    
  implicit:
    enabled: true
    session_timeout_seconds: 300
    engagement_score_weights:
      dwell_time: 0.25
      scroll_depth: 0.20
      interactions: 0.15
      sharing: 0.20
      follow_up: 0.10
      retention: 0.10

quality_evaluation:
  model_path: "models/self_improve/quality_classifier.pkl"
  use_ml: false  # Start with heuristics, enable ML after training
  dimensions:
    - accuracy
    - completeness
    - relevance
    - clarity
    - actionability
  min_confidence_threshold: 0.5

metrics:
  storage_path: "data/metrics"
  buffer_size: 1000
  aggregation_windows:
    - hourly
    - daily
    - weekly
  retention_days: 90

ab_testing:
  enabled: true
  min_sample_size: 100
  confidence_level: 0.95
  auto_winner_selection: false

model_retraining:
  enabled: true
  triggers:
    scheduled:
      enabled: true
      frequency: "weekly"
    performance:
      enabled: true
      degradation_threshold: 0.05
    data_drift:
      enabled: true
      threshold: 0.1
  deployment:
    auto_deploy: false
    require_approval: true
    min_improvement_percent: 2.0

hyperparameter_optimization:
  enabled: true
  framework: "optuna"  # or "ray_tune"
  n_trials: 100
  timeout_seconds: 3600

continuous_learning:
  enabled: true
  check_interval_hours: 24
  min_feedback_samples: 100
  retrain_threshold: 0.1
```

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Quality Score | >0.80 | ML evaluator overall score |
| User Satisfaction | >4.0/5 | Explicit feedback average |
| Feedback Collection Rate | >30% | % of queries with feedback |
| Model Accuracy | >85% | On validation set |
| System Uptime | >99.5% | Availability percentage |
| A/B Test Velocity | 2/week | Experiments completed |
| Retraining Frequency | Weekly | Models retrained |
| Time to Improvement | <1 week | From feedback to deployment |

---

## 8. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Feedback spam | Rate limiting, user validation |
| Model degradation | A/B testing, rollback capability |
| Data privacy | Anonymization, consent management |
| Performance impact | Async processing, caching |
| Overfitting | Cross-validation, regularization |
| Bias amplification | Fairness metrics, diverse training data |

---

## 9. Conclusion

This comprehensive self-improvement system will transform ResilienceAI from a static tool into a continuously learning, adaptive platform. The phased implementation approach ensures incremental value delivery while managing complexity and risk.

Key deliverables:
1. **Immediate Value** (Phase 1-2): Feedback collection, quality metrics, basic ML evaluation
2. **Competitive Advantage** (Phase 3-4): A/B testing, automated retraining, system adaptation

The system is designed to be modular, allowing components to be developed and deployed independently while working together as a cohesive self-improving platform.
