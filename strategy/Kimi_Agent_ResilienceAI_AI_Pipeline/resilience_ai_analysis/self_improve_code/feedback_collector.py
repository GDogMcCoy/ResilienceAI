"""
Feedback Collection System for ResilienceAI

Collects explicit and implicit user feedback for continuous improvement.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import time
import threading
import uuid


class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    THUMBS = "thumbs"           # 👍 / 👎
    RATING = "rating"           # 1-5 stars
    CATEGORY = "category"       # Predefined categories
    TEXT = "text"               # Free-form text
    MULTI_SELECT = "multi"      # Multiple choice


class FeedbackCategory(Enum):
    """Categories for structured feedback."""
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
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExplicitFeedback':
        """Create from dictionary."""
        return cls(
            feedback_id=data["feedback_id"],
            query_id=data["query_id"],
            user_id=data.get("user_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            feedback_type=FeedbackType(data["feedback_type"]),
            rating=data.get("rating"),
            categories=[FeedbackCategory(c) for c in data.get("categories", [])],
            comments=data.get("comments"),
            metadata=data.get("metadata", {})
        )


@dataclass
class InteractionSignals:
    """Behavioral signals indicating user engagement."""
    dwell_time_seconds: float = 0.0
    scroll_depth: float = 0.0  # 0.0 to 1.0
    click_count: int = 0
    copy_events: int = 0
    share_events: int = 0
    export_events: int = 0
    follow_up_queries: int = 0
    return_visits: int = 0
    
    # Computed scores
    engagement_score: float = field(init=False)
    satisfaction_proxy: float = field(init=False)
    
    def __post_init__(self):
        """Compute derived scores after initialization."""
        self.engagement_score = self.compute_engagement_score()
        self.satisfaction_proxy = self.compute_satisfaction_proxy()
    
    def compute_engagement_score(self) -> float:
        """
        Compute composite engagement score from signals.
        
        Weights optimized for disaster response context:
        - Dwell time: 25% (optimal reading: 30-120 seconds)
        - Scroll depth: 20% (full content consumption)
        - Interactions: 15% (active engagement)
        - Sharing: 20% (value recognition)
        - Follow-up: 10% (continued interest)
        - Retention: 10% (return visits)
        """
        score = 0.0
        
        # Dwell time (optimal: 30-120 seconds for disaster briefings)
        if 30 <= self.dwell_time_seconds <= 120:
            score += 0.25
        elif self.dwell_time_seconds > 120:
            score += 0.20  # Longer isn't always better
        elif self.dwell_time_seconds > 10:
            score += 0.10
            
        # Scroll depth
        score += self.scroll_depth * 0.20
        
        # Interactions (clicks, selections)
        score += min(self.click_count * 0.03, 0.15)
        
        # Sharing/Exporting (strong signal of value)
        score += min(self.copy_events * 0.05, 0.10)
        score += self.share_events * 0.05
        score += self.export_events * 0.05
        
        # Follow-up engagement
        score += min(self.follow_up_queries * 0.05, 0.10)
        score += min(self.return_visits * 0.05, 0.10)
        
        return min(score, 1.0)
    
    def compute_satisfaction_proxy(self) -> float:
        """
        Compute satisfaction proxy from engagement signals.
        
        This is a heuristic-based estimate of user satisfaction
        when explicit feedback is not available.
        """
        # High engagement generally correlates with satisfaction
        base_score = self.engagement_score
        
        # Adjust based on specific signals
        if self.share_events > 0 or self.export_events > 0:
            base_score = min(base_score + 0.1, 1.0)
        
        if self.follow_up_queries > 0:
            base_score = min(base_score + 0.05, 1.0)
        
        # Penalize very short sessions (likely dissatisfaction)
        if self.dwell_time_seconds < 5:
            base_score *= 0.5
        
        return round(base_score, 3)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dwell_time_seconds": self.dwell_time_seconds,
            "scroll_depth": self.scroll_depth,
            "click_count": self.click_count,
            "copy_events": self.copy_events,
            "share_events": self.share_events,
            "export_events": self.export_events,
            "follow_up_queries": self.follow_up_queries,
            "return_visits": self.return_visits,
            "engagement_score": self.engagement_score,
            "satisfaction_proxy": self.satisfaction_proxy
        }


class ExplicitFeedbackCollector:
    """
    Collects and manages explicit user feedback.
    
    Features:
    - Multi-modal feedback collection (thumbs, ratings, text)
    - Category-based feedback for specific dimensions
    - Anonymous and authenticated feedback support
    - Real-time feedback streaming
    - Buffer management for efficient I/O
    """
    
    def __init__(
        self,
        storage_path: str = "data/feedback/explicit",
        buffer_size: int = 100,
        auto_flush: bool = True
    ):
        """
        Initialize the feedback collector.
        
        Args:
            storage_path: Directory for feedback storage
            buffer_size: Number of feedback items to buffer before flushing
            auto_flush: Whether to auto-flush on buffer full
        """
        self.storage_path = Path(storage_path)
        self.buffer_size = buffer_size
        self.auto_flush = auto_flush
        
        self.feedback_buffer: List[ExplicitFeedback] = []
        self.buffer_lock = threading.Lock()
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def collect_thumbs_feedback(
        self,
        query_id: str,
        is_helpful: bool,
        user_id: Optional[str] = None,
        comments: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExplicitFeedback:
        """
        Collect binary thumbs up/down feedback.
        
        Args:
            query_id: ID of the query being rated
            is_helpful: True for thumbs up, False for thumbs down
            user_id: Optional user identifier
            comments: Optional text comments
            metadata: Additional metadata
            
        Returns:
            ExplicitFeedback object
        """
        feedback = ExplicitFeedback(
            feedback_id=self._generate_id(),
            query_id=query_id,
            user_id=user_id,
            timestamp=datetime.now(),
            feedback_type=FeedbackType.THUMBS,
            rating=1.0 if is_helpful else 0.0,
            categories=[],
            comments=comments,
            metadata={"is_helpful": is_helpful, **(metadata or {})}
        )
        
        self._buffer_feedback(feedback)
        return feedback
    
    def collect_rating_feedback(
        self,
        query_id: str,
        rating: int,  # 1-5
        categories: Optional[List[FeedbackCategory]] = None,
        user_id: Optional[str] = None,
        comments: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExplicitFeedback:
        """
        Collect star rating feedback with optional category breakdown.
        
        Args:
            query_id: ID of the query being rated
            rating: Star rating (1-5)
            categories: Categories the rating applies to
            user_id: Optional user identifier
            comments: Optional text comments
            metadata: Additional metadata
            
        Returns:
            ExplicitFeedback object
        """
        # Normalize rating to 0-1 scale
        normalized_rating = (rating - 1) / 4.0
        
        feedback = ExplicitFeedback(
            feedback_id=self._generate_id(),
            query_id=query_id,
            user_id=user_id,
            timestamp=datetime.now(),
            feedback_type=FeedbackType.RATING,
            rating=normalized_rating,
            categories=categories or [],
            comments=comments,
            metadata={"original_rating": rating, **(metadata or {})}
        )
        
        self._buffer_feedback(feedback)
        return feedback
    
    def collect_structured_feedback(
        self,
        query_id: str,
        ratings_by_category: Dict[FeedbackCategory, int],
        overall_rating: int,
        user_id: Optional[str] = None,
        comments: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[ExplicitFeedback]:
        """
        Collect detailed feedback across multiple dimensions.
        
        Args:
            query_id: ID of the query being rated
            ratings_by_category: Dict mapping categories to 1-5 ratings
            overall_rating: Overall satisfaction rating (1-5)
            user_id: Optional user identifier
            comments: Optional text comments
            metadata: Additional metadata
            
        Returns:
            List of ExplicitFeedback objects
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
                metadata={"is_category_rating": True, **(metadata or {})}
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
            metadata={"is_overall_rating": True, **(metadata or {})}
        )
        feedback_entries.append(overall_feedback)
        self._buffer_feedback(overall_feedback)
        
        return feedback_entries
    
    def collect_text_feedback(
        self,
        query_id: str,
        comments: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExplicitFeedback:
        """
        Collect free-form text feedback.
        
        Args:
            query_id: ID of the query being rated
            comments: Text feedback
            user_id: Optional user identifier
            metadata: Additional metadata
            
        Returns:
            ExplicitFeedback object
        """
        feedback = ExplicitFeedback(
            feedback_id=self._generate_id(),
            query_id=query_id,
            user_id=user_id,
            timestamp=datetime.now(),
            feedback_type=FeedbackType.TEXT,
            rating=None,
            categories=[],
            comments=comments,
            metadata=metadata or {}
        )
        
        self._buffer_feedback(feedback)
        return feedback
    
    def get_feedback_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        query_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get summary of collected feedback.
        
        Args:
            start_date: Filter by start date
            end_date: Filter by end date
            query_id: Filter by specific query
            
        Returns:
            Summary dictionary with statistics
        """
        # Load all feedback files
        all_feedback = []
        for file_path in self.storage_path.glob("explicit_feedback_*.jsonl"):
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        feedback = ExplicitFeedback.from_dict(data)
                        
                        # Apply filters
                        if start_date and feedback.timestamp < start_date:
                            continue
                        if end_date and feedback.timestamp > end_date:
                            continue
                        if query_id and feedback.query_id != query_id:
                            continue
                        
                        all_feedback.append(feedback)
        
        # Compute summary statistics
        if not all_feedback:
            return {"total_feedback": 0}
        
        ratings = [f.rating for f in all_feedback if f.rating is not None]
        
        summary = {
            "total_feedback": len(all_feedback),
            "date_range": {
                "start": min(f.timestamp for f in all_feedback).isoformat(),
                "end": max(f.timestamp for f in all_feedback).isoformat()
            },
            "by_type": {}
        }
        
        # Count by type
        for feedback_type in FeedbackType:
            count = sum(1 for f in all_feedback if f.feedback_type == feedback_type)
            summary["by_type"][feedback_type.value] = count
        
        # Rating statistics
        if ratings:
            summary["rating_stats"] = {
                "count": len(ratings),
                "mean": sum(ratings) / len(ratings),
                "min": min(ratings),
                "max": max(ratings)
            }
        
        return summary
    
    def _buffer_feedback(self, feedback: ExplicitFeedback):
        """Add feedback to buffer and flush if needed."""
        with self.buffer_lock:
            self.feedback_buffer.append(feedback)
            
            if len(self.feedback_buffer) >= self.buffer_size and self.auto_flush:
                self._flush_buffer()
    
    def _flush_buffer(self):
        """Persist buffered feedback to storage."""
        if not self.feedback_buffer:
            return
        
        filename = self.storage_path / f"explicit_feedback_{datetime.now():%Y%m%d}.jsonl"
        
        with open(filename, "a") as f:
            for feedback in self.feedback_buffer:
                f.write(json.dumps(feedback.to_dict()) + "\n")
        
        # Clear buffer
        self.feedback_buffer = []
    
    def flush(self):
        """Manually flush the buffer."""
        with self.buffer_lock:
            self._flush_buffer()
    
    def _generate_id(self) -> str:
        """Generate unique feedback ID."""
        return str(uuid.uuid4())[:12]


class ImplicitFeedbackCollector:
    """
    Collects implicit feedback through behavioral tracking.
    
    Tracks:
    - Dwell time on responses
    - Scroll depth and reading patterns
    - Copy/share/export actions
    - Follow-up query patterns
    - Return visit frequency
    
    Features:
    - Session-based tracking
    - Real-time signal computation
    - Privacy-preserving aggregation
    """
    
    def __init__(
        self,
        storage_path: str = "data/feedback/implicit",
        session_timeout_seconds: float = 300
    ):
        """
        Initialize the implicit feedback collector.
        
        Args:
            storage_path: Directory for storage
            session_timeout_seconds: Session timeout in seconds
        """
        self.storage_path = Path(storage_path)
        self.session_timeout_seconds = session_timeout_seconds
        
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lock = threading.Lock()
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def start_session(
        self,
        query_id: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Start tracking a new user session.
        
        Args:
            query_id: ID of the query
            user_id: Optional user identifier
            context: Additional context (page, device, etc.)
        """
        with self.session_lock:
            self.active_sessions[query_id] = {
                "start_time": time.time(),
                "user_id": user_id,
                "context": context or {},
                "scroll_events": [],
                "click_events": [],
                "copy_events": 0,
                "share_events": 0,
                "export_events": 0,
                "last_activity": time.time()
            }
    
    def record_scroll(
        self,
        query_id: str,
        depth: float,
        element_id: Optional[str] = None
    ):
        """
        Record scroll depth event.
        
        Args:
            query_id: Query ID
            depth: Scroll depth (0.0 to 1.0)
            element_id: Optional element identifier
        """
        with self.session_lock:
            if query_id not in self.active_sessions:
                return
            
            self.active_sessions[query_id]["scroll_events"].append({
                "depth": depth,
                "element_id": element_id,
                "timestamp": time.time()
            })
            self.active_sessions[query_id]["last_activity"] = time.time()
    
    def record_interaction(
        self,
        query_id: str,
        interaction_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record user interaction event.
        
        Args:
            query_id: Query ID
            interaction_type: Type of interaction (click, copy, share, export)
            metadata: Additional metadata
        """
        with self.session_lock:
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
            
            session["last_activity"] = time.time()
    
    def end_session(
        self,
        query_id: str,
        follow_up: bool = False
    ) -> InteractionSignals:
        """
        End session and compute engagement signals.
        
        Args:
            query_id: Query ID
            follow_up: Whether user submitted a follow-up query
            
        Returns:
            InteractionSignals with computed metrics
        """
        with self.session_lock:
            if query_id not in self.active_sessions:
                return InteractionSignals()
            
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
            self._persist_signals(query_id, session["user_id"], signals, session.get("context"))
            
            # Clean up session
            del self.active_sessions[query_id]
            
            return signals
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = time.time()
        expired = []
        
        with self.session_lock:
            for query_id, session in self.active_sessions.items():
                if current_time - session["last_activity"] > self.session_timeout_seconds:
                    expired.append(query_id)
            
            for query_id in expired:
                # End session without follow-up
                self.end_session(query_id, follow_up=False)
    
    def _persist_signals(
        self,
        query_id: str,
        user_id: Optional[str],
        signals: InteractionSignals,
        context: Optional[Dict[str, Any]] = None
    ):
        """Persist interaction signals to storage."""
        record = {
            "query_id": query_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            **signals.to_dict(),
            "context": context or {}
        }
        
        filename = self.storage_path / f"implicit_feedback_{datetime.now():%Y%m%d}.jsonl"
        
        with open(filename, "a") as f:
            f.write(json.dumps(record) + "\n")
    
    def get_signals_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get summary of interaction signals.
        
        Args:
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            Summary dictionary with statistics
        """
        # Load all signal files
        all_signals = []
        for file_path in self.storage_path.glob("implicit_feedback_*.jsonl"):
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        timestamp = datetime.fromisoformat(data["timestamp"])
                        
                        # Apply filters
                        if start_date and timestamp < start_date:
                            continue
                        if end_date and timestamp > end_date:
                            continue
                        
                        all_signals.append(data)
        
        if not all_signals:
            return {"total_sessions": 0}
        
        # Compute summary statistics
        engagement_scores = [s["engagement_score"] for s in all_signals]
        satisfaction_proxies = [s["satisfaction_proxy"] for s in all_signals]
        dwell_times = [s["dwell_time_seconds"] for s in all_signals]
        
        summary = {
            "total_sessions": len(all_signals),
            "date_range": {
                "start": min(datetime.fromisoformat(s["timestamp"]) for s in all_signals).isoformat(),
                "end": max(datetime.fromisoformat(s["timestamp"]) for s in all_signals).isoformat()
            },
            "engagement": {
                "mean": sum(engagement_scores) / len(engagement_scores),
                "median": sorted(engagement_scores)[len(engagement_scores) // 2],
                "high_engagement_rate": sum(1 for s in engagement_scores if s > 0.7) / len(engagement_scores)
            },
            "satisfaction_proxy": {
                "mean": sum(satisfaction_proxies) / len(satisfaction_proxies),
                "median": sorted(satisfaction_proxies)[len(satisfaction_proxies) // 2]
            },
            "dwell_time": {
                "mean_seconds": sum(dwell_times) / len(dwell_times),
                "median_seconds": sorted(dwell_times)[len(dwell_times) // 2]
            }
        }
        
        return summary


# Convenience function for quick feedback collection
def collect_quick_feedback(
    query_id: str,
    rating: int,
    collector: Optional[ExplicitFeedbackCollector] = None
) -> ExplicitFeedback:
    """
    Quick function to collect rating feedback.
    
    Args:
        query_id: Query ID
        rating: Rating (1-5)
        collector: Optional collector instance (creates default if None)
        
    Returns:
        ExplicitFeedback object
    """
    if collector is None:
        collector = ExplicitFeedbackCollector()
    
    return collector.collect_rating_feedback(
        query_id=query_id,
        rating=rating
    )
