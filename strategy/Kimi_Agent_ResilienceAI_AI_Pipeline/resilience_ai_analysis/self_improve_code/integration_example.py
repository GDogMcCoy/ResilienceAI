"""
Integration Example: Self-Improvement System with ResilienceAI

This example demonstrates how to integrate the self-improvement system
with the existing ResilienceAI agent and dashboard.
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import time

# Import self-improvement components
from feedback_collector import (
    ExplicitFeedbackCollector,
    ImplicitFeedbackCollector,
    FeedbackCategory
)
from quality_evaluator import MLQualityEvaluator
from metrics_tracker import MetricsTracker


class SelfImprovingAgent:
    """
    Enhanced ResilienceAI Agent with self-improvement capabilities.
    
    This wraps the existing agent and adds:
    - Quality evaluation
    - Feedback collection
    - Metrics tracking
    - Continuous improvement
    """
    
    def __init__(
        self,
        base_agent: Optional[Any] = None,
        enable_feedback: bool = True,
        enable_quality_eval: bool = True,
        enable_metrics: bool = True
    ):
        """
        Initialize the self-improving agent.
        
        Args:
            base_agent: Existing ResilienceAI agent (optional)
            enable_feedback: Enable feedback collection
            enable_quality_eval: Enable quality evaluation
            enable_metrics: Enable metrics tracking
        """
        self.base_agent = base_agent
        
        # Initialize self-improvement components
        self.feedback_collector = ExplicitFeedbackCollector() if enable_feedback else None
        self.implicit_collector = ImplicitFeedbackCollector() if enable_feedback else None
        self.quality_evaluator = MLQualityEvaluator(use_ml=False) if enable_quality_eval else None
        self.metrics_tracker = MetricsTracker() if enable_metrics else None
        
        # Track active sessions
        self.active_queries: Dict[str, Dict] = {}
    
    def process_query(
        self,
        query: str,
        user_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a query with self-improvement tracking.
        
        Args:
            query: User query
            user_id: Optional user identifier
            context: Additional context
            
        Returns:
            Response with quality metrics and feedback options
        """
        query_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Start implicit tracking
        if self.implicit_collector:
            self.implicit_collector.start_session(query_id, user_id, context)
        
        try:
            # Generate response using base agent
            if self.base_agent:
                response = self.base_agent.process_query(query)
            else:
                # Fallback response for demo
                response = self._generate_demo_response(query)
            
            # Extract response text
            response_text = response.get("text", str(response))
            tools_used = response.get("tools_used", [])
            
            # Evaluate quality
            quality_result = None
            if self.quality_evaluator:
                eval_context = {
                    "query_id": query_id,
                    "user_id": user_id,
                    "tools_used": tools_used,
                    "data_sources": response.get("data_sources", [])
                }
                quality_result = self.quality_evaluator.evaluate(
                    query=query,
                    response=response_text,
                    context=eval_context
                )
            
            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            if self.metrics_tracker:
                self.metrics_tracker.record_query_metrics(
                    query_id=query_id,
                    query=query,
                    latency_ms=latency_ms,
                    tools_used=tools_used,
                    quality_score=quality_result.dimensions.overall if quality_result else None,
                    success=True
                )
            
            # Store query info for feedback
            self.active_queries[query_id] = {
                "query": query,
                "response": response_text,
                "user_id": user_id,
                "timestamp": datetime.now(),
                "quality_evaluation": quality_result.to_dict() if quality_result else None
            }
            
            # Build enhanced response
            enhanced_response = {
                "query_id": query_id,
                "text": response_text,
                "tools_used": tools_used,
                "latency_ms": round(latency_ms, 2),
                "quality": quality_result.dimensions.to_dict() if quality_result else None,
                "suggestions": quality_result.suggestions if quality_result else [],
                "feedback_url": f"/feedback/{query_id}"
            }
            
            return enhanced_response
            
        except Exception as e:
            # Record error
            if self.metrics_tracker:
                self.metrics_tracker.record_custom_metric(
                    metric_name="query_error",
                    value=1.0,
                    tags={"error_type": type(e).__name__}
                )
            
            # End implicit session
            if self.implicit_collector:
                self.implicit_collector.end_session(query_id, follow_up=False)
            
            raise
    
    def submit_feedback(
        self,
        query_id: str,
        feedback_type: str,
        rating: Optional[int] = None,
        categories: Optional[List[str]] = None,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit explicit feedback for a query.
        
        Args:
            query_id: Query identifier
            feedback_type: Type of feedback (thumbs, rating, text)
            rating: Numeric rating (1-5)
            categories: Feedback categories
            comments: Text comments
            
        Returns:
            Feedback confirmation
        """
        if not self.feedback_collector:
            return {"error": "Feedback collection not enabled"}
        
        if query_id not in self.active_queries:
            return {"error": "Query not found"}
        
        query_info = self.active_queries[query_id]
        
        # Collect feedback based on type
        if feedback_type == "thumbs":
            feedback = self.feedback_collector.collect_thumbs_feedback(
                query_id=query_id,
                is_helpful=rating == 1,
                user_id=query_info.get("user_id"),
                comments=comments
            )
        elif feedback_type == "rating":
            category_enums = [FeedbackCategory(c) for c in (categories or [])]
            feedback = self.feedback_collector.collect_rating_feedback(
                query_id=query_id,
                rating=rating or 3,
                categories=category_enums,
                user_id=query_info.get("user_id"),
                comments=comments
            )
        elif feedback_type == "text":
            feedback = self.feedback_collector.collect_text_feedback(
                query_id=query_id,
                comments=comments or "",
                user_id=query_info.get("user_id")
            )
        else:
            return {"error": f"Unknown feedback type: {feedback_type}"}
        
        # Record feedback metric
        if self.metrics_tracker:
            self.metrics_tracker.record_custom_metric(
                metric_name="feedback_received",
                value=1.0,
                tags={"feedback_type": feedback_type}
            )
        
        return {
            "success": True,
            "feedback_id": feedback.feedback_id,
            "message": "Thank you for your feedback!"
        }
    
    def record_interaction(
        self,
        query_id: str,
        interaction_type: str,
        metadata: Optional[Dict] = None
    ):
        """
        Record user interaction for implicit feedback.
        
        Args:
            query_id: Query identifier
            interaction_type: Type of interaction
            metadata: Additional metadata
        """
        if self.implicit_collector:
            self.implicit_collector.record_interaction(
                query_id=query_id,
                interaction_type=interaction_type,
                metadata=metadata
            )
    
    def end_session(
        self,
        query_id: str,
        follow_up: bool = False
    ) -> Dict[str, Any]:
        """
        End user session and compute engagement.
        
        Args:
            query_id: Query identifier
            follow_up: Whether user submitted follow-up
            
        Returns:
            Engagement signals
        """
        if not self.implicit_collector:
            return {"error": "Implicit tracking not enabled"}
        
        signals = self.implicit_collector.end_session(query_id, follow_up)
        
        # Record engagement metric
        if self.metrics_tracker:
            self.metrics_tracker.record_custom_metric(
                metric_name="engagement_score",
                value=signals.engagement_score,
                tags={"query_id": query_id}
            )
        
        return {
            "engagement_score": signals.engagement_score,
            "satisfaction_proxy": signals.satisfaction_proxy,
            "dwell_time_seconds": signals.dwell_time_seconds
        }
    
    def get_quality_report(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get quality report for recent queries.
        
        Args:
            days: Number of days to include
            
        Returns:
            Quality report
        """
        if not self.metrics_tracker:
            return {"error": "Metrics tracking not enabled"}
        
        # Get query metrics summary
        summary = self.metrics_tracker.get_metrics_summary("query")
        
        # Get feedback summary
        if self.feedback_collector:
            feedback_summary = self.feedback_collector.get_feedback_summary()
        else:
            feedback_summary = {"total_feedback": 0}
        
        return {
            "period_days": days,
            "query_metrics": summary,
            "feedback_summary": feedback_summary,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_system_health(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get system health status.
        
        Args:
            hours: Number of hours to include
            
        Returns:
            Health report
        """
        if not self.metrics_tracker:
            return {"error": "Metrics tracking not enabled"}
        
        return self.metrics_tracker.get_system_health_summary(hours)
    
    def _generate_demo_response(self, query: str) -> Dict[str, Any]:
        """Generate a demo response for testing."""
        return {
            "text": f"This is a demo response for: '{query}'. In production, this would use the actual ResilienceAI agent.",
            "tools_used": ["query_counties"],
            "data_sources": ["fema"]
        }


# Streamlit Dashboard Integration

def render_feedback_ui(agent: SelfImprovingAgent, query_id: str):
    """
    Render feedback collection UI for Streamlit.
    
    Args:
        agent: Self-improving agent instance
        query_id: Query identifier
    """
    try:
        import streamlit as st
    except ImportError:
        print("Streamlit not available")
        return
    
    st.subheader("Was this response helpful?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👍 Helpful", key=f"thumbs_up_{query_id}"):
            result = agent.submit_feedback(query_id, "thumbs", rating=1)
            if result.get("success"):
                st.success("Thank you for your feedback!")
    
    with col2:
        if st.button("👎 Not Helpful", key=f"thumbs_down_{query_id}"):
            result = agent.submit_feedback(query_id, "thumbs", rating=0)
            
            # Show detailed feedback form
            with st.expander("Tell us more"):
                categories = st.multiselect(
                    "What was the issue?",
                    ["accuracy", "completeness", "relevance", "clarity", "actionability"],
                    key=f"categories_{query_id}"
                )
                comments = st.text_area("Additional comments", key=f"comments_{query_id}")
                if st.button("Submit Detailed Feedback", key=f"submit_{query_id}"):
                    agent.submit_feedback(
                        query_id=query_id,
                        feedback_type="rating",
                        rating=2,
                        categories=categories,
                        comments=comments
                    )
                    st.success("Thank you for your detailed feedback!")
    
    # Rating slider
    rating = st.slider("Rate this response (1-5)", 1, 5, 3, key=f"rating_{query_id}")
    if st.button("Submit Rating", key=f"submit_rating_{query_id}"):
        result = agent.submit_feedback(query_id, "rating", rating=rating)
        if result.get("success"):
            st.success("Thank you for your rating!")


def render_quality_dashboard(agent: SelfImprovingAgent):
    """
    Render quality metrics dashboard for Streamlit.
    
    Args:
        agent: Self-improving agent instance
    """
    try:
        import streamlit as st
    except ImportError:
        print("Streamlit not available")
        return
    
    st.header("Response Quality Dashboard")
    
    # Get quality report
    report = agent.get_quality_report(days=7)
    
    if "error" in report:
        st.error(report["error"])
        return
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    query_metrics = report.get("query_metrics", {})
    stats = query_metrics.get("statistics", {})
    
    with col1:
        st.metric(
            "Total Queries",
            query_metrics.get("total_records", 0)
        )
    
    with col2:
        st.metric(
            "Avg Quality Score",
            f"{stats.get('mean', 0):.2f}"
        )
    
    with col3:
        st.metric(
            "Feedback Received",
            report.get("feedback_summary", {}).get("total_feedback", 0)
        )
    
    # Quality distribution
    if stats:
        st.subheader("Quality Distribution")
        st.bar_chart({
            "P95": stats.get("p95", 0),
            "Mean": stats.get("mean", 0),
            "Median": stats.get("median", 0),
            "P5": stats.get("min", 0)
        })
    
    # System health
    st.subheader("System Health")
    health = agent.get_system_health(hours=24)
    
    if "error" not in health:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Avg Latency (ms)", f"{health.get('avg_response_time_ms', 0):.0f}")
        
        with col2:
            st.metric("Error Rate", f"{health.get('avg_error_rate', 0):.4f}")
        
        with col3:
            st.metric("Availability", f"{health.get('latest_availability', 100):.1f}%")


# Example usage
if __name__ == "__main__":
    # Create self-improving agent
    agent = SelfImprovingAgent()
    
    # Process a query
    print("=" * 60)
    print("Self-Improving Agent Demo")
    print("=" * 60)
    
    query = "Which Missouri counties are most vulnerable to flooding?"
    print(f"\nQuery: {query}")
    
    response = agent.process_query(query, user_id="demo_user")
    
    print(f"\nResponse ID: {response['query_id']}")
    print(f"Response: {response['text'][:200]}...")
    print(f"Latency: {response['latency_ms']}ms")
    print(f"Quality Score: {response['quality']['overall']}")
    print(f"Quality Breakdown:")
    for dim, score in response['quality'].items():
        if dim != 'overall':
            print(f"  - {dim}: {score}")
    
    if response['suggestions']:
        print(f"\nImprovement Suggestions:")
        for suggestion in response['suggestions']:
            print(f"  - {suggestion}")
    
    # Simulate feedback
    print("\n" + "=" * 60)
    print("Simulating user feedback...")
    print("=" * 60)
    
    feedback_result = agent.submit_feedback(
        query_id=response['query_id'],
        feedback_type="rating",
        rating=4,
        comments="Good response, very helpful!"
    )
    print(f"Feedback submitted: {feedback_result}")
    
    # Get quality report
    print("\n" + "=" * 60)
    print("Quality Report")
    print("=" * 60)
    
    report = agent.get_quality_report()
    print(f"Report: {report}")
