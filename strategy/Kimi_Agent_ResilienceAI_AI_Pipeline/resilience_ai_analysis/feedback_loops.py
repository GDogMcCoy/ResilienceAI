"""
Feedback Loops for ResilienceAI
Implements real-time feedback collection and model updates
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import threading
import time


@dataclass
class FeedbackEvent:
    """User feedback event"""
    event_id: str
    user_id: str
    recommendation_id: str
    event_type: str  # 'impression', 'click', 'accept', 'reject', 'implement', 'outcome'
    timestamp: datetime
    context: Dict[str, Any]
    value: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class FeedbackCollector:
    """Collects and processes user feedback"""
    
    def __init__(
        self,
        max_buffer_size: int = 10000,
        flush_interval_seconds: int = 60
    ):
        self.max_buffer_size = max_buffer_size
        self.flush_interval = flush_interval_seconds
        
        self.feedback_buffer: deque = deque(maxlen=max_buffer_size)
        self.processed_feedback: List[FeedbackEvent] = []
        
        self.handlers: Dict[str, List[Callable]] = {}
        self.lock = threading.Lock()
        
        # Start background processing
        self._start_background_processor()
    
    def _start_background_processor(self) -> None:
        """Start background feedback processing"""
        
        def process_loop():
            while True:
                time.sleep(self.flush_interval)
                self._process_buffered_feedback()
        
        processor_thread = threading.Thread(target=process_loop, daemon=True)
        processor_thread.start()
    
    def collect(
        self,
        user_id: str,
        recommendation_id: str,
        event_type: str,
        context: Dict[str, Any],
        value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Collect a feedback event"""
        
        event = FeedbackEvent(
            event_id=self._generate_event_id(),
            user_id=user_id,
            recommendation_id=recommendation_id,
            event_type=event_type,
            timestamp=datetime.now(),
            context=context,
            value=value,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.feedback_buffer.append(event)
        
        # Trigger immediate processing if buffer is full
        if len(self.feedback_buffer) >= self.max_buffer_size * 0.9:
            self._process_buffered_feedback()
    
    def _process_buffered_feedback(self) -> None:
        """Process buffered feedback events"""
        
        with self.lock:
            events_to_process = list(self.feedback_buffer)
            self.feedback_buffer.clear()
        
        for event in events_to_process:
            self._process_single_event(event)
        
        self.processed_feedback.extend(events_to_process)
    
    def _process_single_event(self, event: FeedbackEvent) -> None:
        """Process a single feedback event"""
        
        # Trigger registered handlers
        if event.event_type in self.handlers:
            for handler in self.handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Handler error: {e}")
    
    def register_handler(
        self,
        event_type: str,
        handler: Callable[[FeedbackEvent], None]
    ) -> None:
        """Register a handler for an event type"""
        
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"evt_{timestamp}"
    
    def get_feedback_summary(
        self,
        recommendation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get summary of feedback"""
        
        # Filter feedback
        filtered = self.processed_feedback
        
        if recommendation_id:
            filtered = [e for e in filtered if e.recommendation_id == recommendation_id]
        
        if user_id:
            filtered = [e for e in filtered if e.user_id == user_id]
        
        if event_types:
            filtered = [e for e in filtered if e.event_type in event_types]
        
        if since:
            filtered = [e for e in filtered if e.timestamp >= since]
        
        # Calculate summary statistics
        summary = {
            'total_events': len(filtered),
            'events_by_type': {},
            'average_value': None,
            'timeline': []
        }
        
        for event in filtered:
            # Count by type
            if event.event_type not in summary['events_by_type']:
                summary['events_by_type'][event.event_type] = 0
            summary['events_by_type'][event.event_type] += 1
        
        # Calculate average value
        values = [e.value for e in filtered if e.value is not None]
        if values:
            summary['average_value'] = np.mean(values)
        
        # Timeline (events per day)
        if filtered:
            dates = [e.timestamp.date() for e in filtered]
            date_counts = pd.Series(dates).value_counts().sort_index()
            summary['timeline'] = [
                {'date': str(d), 'count': int(c)} 
                for d, c in date_counts.items()
            ]
        
        return summary


class OnlineLearningUpdater:
    """Updates models based on real-time feedback"""
    
    def __init__(
        self,
        recommender: Any,
        update_frequency: str = 'hourly',
        min_samples_for_update: int = 100
    ):
        self.recommender = recommender
        self.update_frequency = update_frequency
        self.min_samples_for_update = min_samples_for_update
        
        self.feedback_collector = FeedbackCollector()
        self.pending_updates: List[Dict[str, Any]] = []
        
        # Register feedback handlers
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register feedback event handlers"""
        
        self.feedback_collector.register_handler('accept', self._on_intervention_accepted)
        self.feedback_collector.register_handler('reject', self._on_intervention_rejected)
        self.feedback_collector.register_handler('implement', self._on_intervention_implemented)
        self.feedback_collector.register_handler('outcome', self._on_outcome_reported)
    
    def _on_intervention_accepted(self, event: FeedbackEvent) -> None:
        """Handle intervention acceptance"""
        
        self.pending_updates.append({
            'type': 'positive',
            'recommendation_id': event.recommendation_id,
            'context': event.context,
            'weight': 1.0
        })
    
    def _on_intervention_rejected(self, event: FeedbackEvent) -> None:
        """Handle intervention rejection"""
        
        self.pending_updates.append({
            'type': 'negative',
            'recommendation_id': event.recommendation_id,
            'context': event.context,
            'weight': -1.0
        })
    
    def _on_intervention_implemented(self, event: FeedbackEvent) -> None:
        """Handle intervention implementation"""
        
        self.pending_updates.append({
            'type': 'implementation',
            'recommendation_id': event.recommendation_id,
            'context': event.context,
            'weight': 2.0
        })
    
    def _on_outcome_reported(self, event: FeedbackEvent) -> None:
        """Handle outcome reporting"""
        
        outcome_score = event.value or 0.5
        
        self.pending_updates.append({
            'type': 'outcome',
            'recommendation_id': event.recommendation_id,
            'context': event.context,
            'outcome_score': outcome_score,
            'weight': outcome_score * 3.0
        })
    
    def update_model(self) -> bool:
        """Update model with pending feedback"""
        
        if len(self.pending_updates) < self.min_samples_for_update:
            return False
        
        # Prepare update data
        updates = self.pending_updates.copy()
        self.pending_updates = []
        
        # Perform model update (implementation depends on model type)
        if hasattr(self.recommender, 'partial_fit'):
            self._partial_fit_update(updates)
        elif hasattr(self.recommender, 'online_update'):
            self._online_update(updates)
        else:
            self._batch_retrain(updates)
        
        return True
    
    def _partial_fit_update(self, updates: List[Dict[str, Any]]) -> None:
        """Update using partial_fit method"""
        
        # Convert updates to training data
        X, y = self._prepare_training_data(updates)
        
        if len(X) > 0:
            self.recommender.partial_fit(X, y)
    
    def _online_update(self, updates: List[Dict[str, Any]]) -> None:
        """Update using online_update method"""
        
        for update in updates:
            if hasattr(self.recommender, 'online_update'):
                self.recommender.online_update(update)
    
    def _batch_retrain(self, updates: List[Dict[str, Any]]) -> None:
        """Fallback: batch retrain with accumulated data"""
        
        print(f"Batch retrain triggered with {len(updates)} updates")
    
    def _prepare_training_data(
        self,
        updates: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from updates"""
        
        X = []
        y = []
        
        for update in updates:
            context = update.get('context', {})
            
            # Extract features from context
            features = [
                context.get('county_risk_score', 0.5),
                context.get('intervention_cost', 0.5),
                context.get('historical_success_rate', 0.5),
                update.get('weight', 0)
            ]
            
            X.append(features)
            
            # Target is based on update type and weight
            if update['type'] == 'outcome':
                y.append(update.get('outcome_score', 0.5))
            else:
                y.append(1.0 if update['weight'] > 0 else 0.0)
        
        return np.array(X), np.array(y)


class FeedbackLoopMetrics:
    """Metrics for monitoring feedback loops"""
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
    
    def calculate_metrics(
        self,
        feedback_collector: FeedbackCollector,
        window_days: int = 7
    ) -> Dict[str, Any]:
        """Calculate feedback loop metrics"""
        
        since = datetime.now() - timedelta(days=window_days)
        
        # Get feedback summary
        summary = feedback_collector.get_feedback_summary(since=since)
        
        # Calculate derived metrics
        metrics = {
            'feedback_volume': summary['total_events'],
            'feedback_rate': summary['total_events'] / window_days,
            'average_value': summary.get('average_value', 0),
            'event_distribution': summary['events_by_type']
        }
        
        # Calculate acceptance rate
        accepts = summary['events_by_type'].get('accept', 0)
        rejects = summary['events_by_type'].get('reject', 0)
        total_decisions = accepts + rejects
        
        if total_decisions > 0:
            metrics['acceptance_rate'] = accepts / total_decisions
        
        # Calculate implementation rate
        implements = summary['events_by_type'].get('implement', 0)
        if accepts > 0:
            metrics['implementation_rate'] = implements / accepts
        
        # Calculate outcome quality
        outcomes = summary['events_by_type'].get('outcome', 0)
        if implements > 0:
            metrics['outcome_reporting_rate'] = outcomes / implements
        
        self.metrics_history.append({
            'timestamp': datetime.now(),
            'metrics': metrics
        })
        
        return metrics
    
    def detect_feedback_issues(self) -> List[Dict[str, Any]]:
        """Detect issues in feedback loops"""
        
        issues = []
        
        if len(self.metrics_history) < 2:
            return issues
        
        current = self.metrics_history[-1]['metrics']
        previous = self.metrics_history[-2]['metrics']
        
        # Check for declining acceptance rate
        if current.get('acceptance_rate', 1) < previous.get('acceptance_rate', 1) * 0.8:
            issues.append({
                'type': 'declining_acceptance',
                'severity': 'warning',
                'message': 'Acceptance rate has declined significantly'
            })
        
        # Check for low feedback volume
        if current['feedback_volume'] < 10:
            issues.append({
                'type': 'low_feedback_volume',
                'severity': 'info',
                'message': 'Feedback volume is very low'
            })
        
        # Check for outcome reporting gap
        if current.get('implementation_rate', 0) > 0.5 and \
           current.get('outcome_reporting_rate', 0) < 0.3:
            issues.append({
                'type': 'outcome_reporting_gap',
                'severity': 'warning',
                'message': 'Many implementations without outcome reports'
            })
        
        return issues


# Example usage
if __name__ == "__main__":
    # Create feedback collector
    collector = FeedbackCollector(max_buffer_size=1000, flush_interval_seconds=5)
    
    # Register custom handler
    def on_accept(event):
        print(f"Intervention accepted by {event.user_id}")
    
    collector.register_handler('accept', on_accept)
    
    # Collect feedback
    collector.collect(
        user_id="user_1",
        recommendation_id="rec_123",
        event_type="impression",
        context={"county_id": "county_1"}
    )
    
    collector.collect(
        user_id="user_1",
        recommendation_id="rec_123",
        event_type="click",
        context={"county_id": "county_1"}
    )
    
    collector.collect(
        user_id="user_1",
        recommendation_id="rec_123",
        event_type="accept",
        context={"county_id": "county_1", "intervention_id": "int_1"}
    )
    
    # Get summary
    time.sleep(6)  # Wait for background processing
    
    summary = collector.get_feedback_summary()
    print(f"\nFeedback Summary:")
    print(f"  Total Events: {summary['total_events']}")
    print(f"  Events by Type: {summary['events_by_type']}")
