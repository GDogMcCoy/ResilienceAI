"""
Response Quality Evaluation System for ResilienceAI

ML-powered evaluation of response quality across multiple dimensions.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from pathlib import Path
import json
import re
import numpy as np

# Optional ML imports - gracefully handle if not available
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import cross_val_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False


@dataclass
class QualityDimensions:
    """Quality scores across different dimensions."""
    overall: float = 0.0  # 0.0 to 1.0
    accuracy: float = 0.0
    completeness: float = 0.0
    relevance: float = 0.0
    clarity: float = 0.0
    actionability: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "overall": round(self.overall, 3),
            "accuracy": round(self.accuracy, 3),
            "completeness": round(self.completeness, 3),
            "relevance": round(self.relevance, 3),
            "clarity": round(self.clarity, 3),
            "actionability": round(self.actionability, 3)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'QualityDimensions':
        """Create from dictionary."""
        return cls(
            overall=data.get("overall", 0.0),
            accuracy=data.get("accuracy", 0.0),
            completeness=data.get("completeness", 0.0),
            relevance=data.get("relevance", 0.0),
            clarity=data.get("clarity", 0.0),
            actionability=data.get("actionability", 0.0)
        )
    
    def get_weakest_dimension(self) -> Tuple[str, float]:
        """Get the dimension with the lowest score."""
        dimensions = {
            "accuracy": self.accuracy,
            "completeness": self.completeness,
            "relevance": self.relevance,
            "clarity": self.clarity,
            "actionability": self.actionability
        }
        return min(dimensions.items(), key=lambda x: x[1])


@dataclass
class QualityIssue:
    """Identified quality issue."""
    issue_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    dimension: str
    suggestion: str


@dataclass
class QualityEvaluation:
    """Complete quality evaluation result."""
    evaluation_id: str
    query_id: str
    query: str
    response: str
    dimensions: QualityDimensions
    confidence: float
    issues: List[QualityIssue]
    suggestions: List[str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "evaluation_id": self.evaluation_id,
            "query_id": self.query_id,
            "query": self.query,
            "response": self.response[:500] if len(self.response) > 500 else self.response,
            "dimensions": self.dimensions.to_dict(),
            "confidence": round(self.confidence, 3),
            "issues": [
                {
                    "type": i.issue_type,
                    "severity": i.severity,
                    "description": i.description,
                    "dimension": i.dimension,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ],
            "suggestions": self.suggestions,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class MLQualityEvaluator:
    """
    Machine learning-based response quality evaluator.
    
    Uses ensemble models to evaluate responses across multiple dimensions:
    - Accuracy: Factual correctness and data-backed statements
    - Completeness: Coverage of query aspects
    - Relevance: Alignment with query intent
    - Clarity: Understandability and structure
    - Actionability: Practical utility and recommendations
    
    Features:
    - Heuristic-based evaluation (default)
    - ML model-based evaluation (when trained)
    - Multi-dimensional scoring
    - Issue identification
    - Improvement suggestions
    """
    
    # Quality thresholds
    QUALITY_THRESHOLDS = {
        "excellent": 0.85,
        "good": 0.70,
        "acceptable": 0.55,
        "poor": 0.40
    }
    
    # Dimension weights for overall score
    DIMENSION_WEIGHTS = {
        "accuracy": 0.25,
        "completeness": 0.20,
        "relevance": 0.25,
        "clarity": 0.15,
        "actionability": 0.15
    }
    
    def __init__(
        self,
        models_dir: str = "models/self_improve",
        use_ml: bool = False
    ):
        """
        Initialize the quality evaluator.
        
        Args:
            models_dir: Directory for ML models
            use_ml: Whether to use ML models (if available)
        """
        self.models_dir = Path(models_dir)
        self.use_ml = use_ml and SKLEARN_AVAILABLE
        
        self.dimension_models: Dict[str, Any] = {}
        self.overall_model: Optional[Any] = None
        self.vectorizer: Optional[Any] = None
        
        if self.use_ml:
            self._load_models()
    
    def _load_models(self):
        """Load pre-trained quality evaluation models."""
        if not JOBLIB_AVAILABLE:
            return
        
        model_path = self.models_dir / "quality_classifier.pkl"
        vectorizer_path = self.models_dir / "feedback_encoder.pkl"
        
        try:
            if model_path.exists():
                self.overall_model = joblib.load(model_path)
            
            if vectorizer_path.exists():
                self.vectorizer = joblib.load(vectorizer_path)
            else:
                self.vectorizer = TfidfVectorizer(max_features=5000)
        except Exception as e:
            print(f"Warning: Could not load ML models: {e}")
            self.use_ml = False
    
    def evaluate(
        self,
        query: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
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
        context = context or {}
        
        # Extract features
        features = self._extract_features(query, response, context)
        
        # Evaluate each dimension
        dimensions = self._evaluate_dimensions(features, query, response)
        
        # Identify issues
        issues = self._identify_issues(query, response, dimensions, features)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(issues, dimensions, features)
        
        # Compute confidence
        confidence = self._compute_confidence(features, dimensions)
        
        return QualityEvaluation(
            evaluation_id=self._generate_id(),
            query_id=context.get("query_id", "unknown"),
            query=query,
            response=response,
            dimensions=dimensions,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions,
            timestamp=datetime.now(),
            metadata={
                "features": features,
                "tools_used": context.get("tools_used", []),
                "data_sources": context.get("data_sources", [])
            }
        )
    
    def _extract_features(
        self,
        query: str,
        response: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract features for quality evaluation.
        
        Features include:
        - Length and structure metrics
        - Query coverage
        - Data-backed content
        - Actionability indicators
        """
        query_words = set(query.lower().split())
        response_lower = response.lower()
        response_words = response_lower.split()
        
        features = {
            # Length features
            "query_length": len(query_words),
            "response_length": len(response_words),
            "response_char_length": len(response),
            "query_response_ratio": len(response_words) / max(len(query_words), 1),
            
            # Coverage features
            "query_terms_in_response": self._count_query_terms(query, response),
            "unique_query_terms_covered": len(
                [w for w in query_words if w in response_lower]
            ),
            
            # Structure features
            "has_bullet_points": "•" in response or "- " in response,
            "has_numbered_list": bool(re.search(r'\n\d+\.', response)),
            "has_numbers": bool(re.search(r'\d+', response)),
            "has_percentages": "%" in response,
            "has_tables": "|" in response,
            "paragraph_count": response.count("\n\n") + 1,
            "sentence_count": len(re.findall(r'[.!?]+', response)),
            
            # Data-backed features
            "has_citations": any(marker in response for marker in [
                "according to", "source:", "data from", "reported by"
            ]),
            "has_statistics": bool(re.search(r'\d+\.?\d*\s*(percent|%|million|thousand)', response_lower)),
            
            # Actionability features
            "has_recommendations": any(kw in response_lower for kw in [
                "recommend", "should", "suggest", "advise"
            ]),
            "has_next_steps": any(kw in response_lower for kw in [
                "next", "step", "action", "implement", "proceed"
            ]),
            "has_warnings": any(kw in response_lower for kw in [
                "warning", "caution", "alert", "risk", "danger"
            ]),
            
            # Context features
            "tools_used_count": len(context.get("tools_used", [])),
            "data_sources_count": len(context.get("data_sources", [])),
            "has_prediction": "predict" in query_lower or "forecast" in query_lower,
        }
        
        return features
    
    def _count_query_terms(self, query: str, response: str) -> float:
        """Count how many query terms appear in response."""
        query_terms = set(query.lower().split())
        response_lower = response.lower()
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", 
                     "in", "on", "at", "to", "for", "of", "and", "or"}
        query_terms = query_terms - stop_words
        
        if not query_terms:
            return 1.0
        
        matches = sum(1 for term in query_terms if term in response_lower)
        return matches / len(query_terms)
    
    def _evaluate_dimensions(
        self,
        features: Dict[str, Any],
        query: str,
        response: str
    ) -> QualityDimensions:
        """Evaluate quality across all dimensions."""
        
        # Use ML models if available, otherwise use heuristics
        if self.use_ml and self.overall_model:
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
        accuracy = 0.6  # Base accuracy
        if features["has_numbers"]:
            accuracy += 0.1
        if features["has_statistics"]:
            accuracy += 0.1
        if features["has_citations"]:
            accuracy += 0.1
        if features["data_sources_count"] > 0:
            accuracy += 0.1
        accuracy = min(accuracy, 1.0)
        
        # Completeness heuristic
        completeness = features["query_terms_in_response"]
        if features["response_length"] > 50:
            completeness = min(completeness + 0.15, 1.0)
        if features["unique_query_terms_covered"] >= features["query_length"] * 0.7:
            completeness = min(completeness + 0.1, 1.0)
        
        # Relevance heuristic
        relevance = features["query_terms_in_response"]
        if features["query_response_ratio"] > 1.0:
            relevance = min(relevance + 0.1, 1.0)
        if features["tools_used_count"] > 0:
            relevance = min(relevance + 0.1, 1.0)
        
        # Clarity heuristic
        clarity = 0.65
        if features["has_bullet_points"]:
            clarity += 0.1
        if features["has_numbered_list"]:
            clarity += 0.05
        if features["paragraph_count"] <= 3:
            clarity += 0.1
        if features["response_length"] < 200:
            clarity += 0.05
        if features["sentence_count"] > 0:
            avg_sentence_length = features["response_length"] / features["sentence_count"]
            if 10 <= avg_sentence_length <= 25:
                clarity += 0.05
        clarity = min(clarity, 1.0)
        
        # Actionability heuristic
        actionability = 0.55
        if features["has_recommendations"]:
            actionability += 0.15
        if features["has_next_steps"]:
            actionability += 0.15
        if features["has_warnings"]:
            actionability += 0.05
        if features["has_bullet_points"]:
            actionability += 0.05
        actionability = min(actionability, 1.0)
        
        # Overall score (weighted average)
        overall = (
            accuracy * self.DIMENSION_WEIGHTS["accuracy"] +
            completeness * self.DIMENSION_WEIGHTS["completeness"] +
            relevance * self.DIMENSION_WEIGHTS["relevance"] +
            clarity * self.DIMENSION_WEIGHTS["clarity"] +
            actionability * self.DIMENSION_WEIGHTS["actionability"]
        )
        
        return QualityDimensions(
            overall=round(overall, 3),
            accuracy=round(accuracy, 3),
            completeness=round(completeness, 3),
            relevance=round(relevance, 3),
            clarity=round(clarity, 3),
            actionability=round(actionability, 3)
        )
    
    def _ml_evaluate_dimensions(
        self,
        features: Dict[str, Any]
    ) -> QualityDimensions:
        """ML-based dimension evaluation (placeholder)."""
        # This would use trained models to predict quality scores
        # For now, fall back to heuristics
        return self._heuristic_evaluate_dimensions(features, "", "")
    
    def _identify_issues(
        self,
        query: str,
        response: str,
        dimensions: QualityDimensions,
        features: Dict[str, Any]
    ) -> List[QualityIssue]:
        """Identify specific quality issues."""
        issues = []
        
        # Completeness issues
        if dimensions.completeness < 0.5:
            issues.append(QualityIssue(
                issue_type="incomplete",
                severity="high",
                description="Response may not fully address all aspects of the query",
                dimension="completeness",
                suggestion="Expand response to cover all mentioned topics and requirements"
            ))
        
        # Clarity issues
        if dimensions.clarity < 0.6:
            severity = "high" if dimensions.clarity < 0.4 else "medium"
            issues.append(QualityIssue(
                issue_type="unclear",
                severity=severity,
                description="Response may be difficult to understand or poorly structured",
                dimension="clarity",
                suggestion="Use bullet points, shorter paragraphs, and clearer organization"
            ))
        
        # Actionability issues
        if dimensions.actionability < 0.5:
            issues.append(QualityIssue(
                issue_type="not_actionable",
                severity="medium",
                description="Response lacks actionable recommendations or next steps",
                dimension="actionability",
                suggestion="Include specific recommendations, next steps, or action items"
            ))
        
        # Length issues
        if features["response_length"] < 20:
            issues.append(QualityIssue(
                issue_type="too_short",
                severity="high",
                description="Response appears too brief for the query complexity",
                dimension="completeness",
                suggestion="Provide more detailed information and context"
            ))
        
        # Accuracy issues
        if dimensions.accuracy < 0.6:
            issues.append(QualityIssue(
                issue_type="lacks_data",
                severity="medium",
                description="Response lacks data-backed statements or citations",
                dimension="accuracy",
                suggestion="Include more data-backed statements with citations to sources"
            ))
        
        # Relevance issues
        if dimensions.relevance < 0.5:
            issues.append(QualityIssue(
                issue_type="off_topic",
                severity="high",
                description="Response may not directly address the query",
                dimension="relevance",
                suggestion="Focus response more closely on the specific query asked"
            ))
        
        return issues
    
    def _generate_suggestions(
        self,
        issues: List[QualityIssue],
        dimensions: QualityDimensions,
        features: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement suggestions based on issues."""
        suggestions = []
        
        # Add suggestions from issues
        for issue in issues:
            if issue.suggestion not in suggestions:
                suggestions.append(issue.suggestion)
        
        # Add dimension-specific suggestions
        weakest_dim, weakest_score = dimensions.get_weakest_dimension()
        
        if weakest_dim == "accuracy" and weakest_score < 0.7:
            suggestions.append("Include specific statistics, data points, or source citations")
        
        if weakest_dim == "completeness" and weakest_score < 0.7:
            suggestions.append("Review query for all mentioned topics and ensure each is addressed")
        
        if weakest_dim == "relevance" and weakest_score < 0.7:
            suggestions.append("Ensure response directly answers the specific question asked")
        
        if weakest_dim == "clarity" and weakest_score < 0.7:
            suggestions.append("Break long paragraphs into shorter ones and use formatting for readability")
        
        if weakest_dim == "actionability" and weakest_score < 0.7:
            suggestions.append("Add specific recommendations, next steps, or decision guidance")
        
        # Structure suggestions
        if not features["has_bullet_points"] and features["response_length"] > 100:
            suggestions.append("Consider using bullet points for lists or multiple items")
        
        if not features["has_numbers"] and features["has_prediction"]:
            suggestions.append("Include specific numerical predictions or estimates")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _compute_confidence(
        self,
        features: Dict[str, Any],
        dimensions: QualityDimensions
    ) -> float:
        """
        Compute confidence in the quality evaluation.
        
        Confidence is based on:
        - Feature richness (more features = higher confidence)
        - Dimension consistency (similar scores = higher confidence)
        - Response length (very short = lower confidence)
        """
        # Base confidence from feature count
        feature_count = sum(1 for v in features.values() if v)
        base_confidence = min(feature_count / 15, 0.9)
        
        # Adjust based on dimension variance
        dimension_values = [
            dimensions.accuracy,
            dimensions.completeness,
            dimensions.relevance,
            dimensions.clarity,
            dimensions.actionability
        ]
        variance = np.var(dimension_values) if len(dimension_values) > 1 else 0
        
        # Lower confidence if dimensions vary widely
        confidence = base_confidence * (1 - variance)
        
        # Penalize very short responses
        if features["response_length"] < 30:
            confidence *= 0.7
        
        return round(max(confidence, 0.3), 3)
    
    def _generate_id(self) -> str:
        """Generate unique evaluation ID."""
        import uuid
        return str(uuid.uuid4())[:12]
    
    def get_quality_label(self, score: float) -> str:
        """Get quality label for a score."""
        if score >= self.QUALITY_THRESHOLDS["excellent"]:
            return "excellent"
        elif score >= self.QUALITY_THRESHOLDS["good"]:
            return "good"
        elif score >= self.QUALITY_THRESHOLDS["acceptable"]:
            return "acceptable"
        elif score >= self.QUALITY_THRESHOLDS["poor"]:
            return "poor"
        else:
            return "critical"


class QualityEvaluatorTrainer:
    """
    Trainer for ML-based quality evaluation models.
    
    Trains models using collected feedback as ground truth labels.
    """
    
    def __init__(self, models_dir: str = "models/self_improve"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def train(
        self,
        feedback_data: List[Dict[str, Any]],
        quality_evaluations: List[QualityEvaluation]
    ) -> Dict[str, Any]:
        """
        Train quality evaluation models.
        
        Args:
            feedback_data: Collected user feedback
            quality_evaluations: Historical quality evaluations
            
        Returns:
            Training metrics
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for training")
        
        # Prepare training data
        # This is a simplified version - real implementation would
        # create proper feature vectors and labels from feedback
        
        # For now, return placeholder metrics
        return {
            "status": "not_implemented",
            "message": "Training pipeline requires labeled dataset"
        }


# Convenience function
def quick_evaluate(
    query: str,
    response: str,
    evaluator: Optional[MLQualityEvaluator] = None
) -> QualityDimensions:
    """
    Quick quality evaluation.
    
    Args:
        query: Query string
        response: Response string
        evaluator: Optional evaluator (creates default if None)
        
    Returns:
        QualityDimensions with scores
    """
    if evaluator is None:
        evaluator = MLQualityEvaluator(use_ml=False)
    
    evaluation = evaluator.evaluate(query, response)
    return evaluation.dimensions
