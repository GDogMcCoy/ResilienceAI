# ResilienceAI Self-Improvement System

A comprehensive self-improving platform for continuous learning and optimization of the ResilienceAI disaster vulnerability assessment system.

## Overview

The Self-Improvement System enables ResilienceAI to:
- **Learn from feedback**: Collect explicit and implicit user feedback
- **Evaluate quality**: ML-powered assessment of response quality
- **Track performance**: Comprehensive metrics and monitoring
- **Experiment**: A/B testing for improvements
- **Retrain models**: Automated model improvement pipelines
- **Optimize**: Hyperparameter tuning and feature importance
- **Adapt**: Dynamic system behavior based on performance

## Components

### 1. Feedback Collection (`feedback_collector.py`)

Collects user feedback through multiple channels:

```python
from feedback_collector import ExplicitFeedbackCollector, FeedbackCategory

# Initialize collector
collector = ExplicitFeedbackCollector()

# Collect thumbs up/down feedback
feedback = collector.collect_thumbs_feedback(
    query_id="abc123",
    is_helpful=True,
    comments="Very helpful!"
)

# Collect star rating feedback
feedback = collector.collect_rating_feedback(
    query_id="abc123",
    rating=4,
    categories=[FeedbackCategory.ACCURACY, FeedbackCategory.CLARITY]
)
```

**Features:**
- Explicit feedback (thumbs, ratings, text)
- Implicit feedback (dwell time, scroll depth, interactions)
- Anonymous and authenticated support
- Real-time streaming
- Efficient buffer management

### 2. Quality Evaluation (`quality_evaluator.py`)

Evaluates response quality across multiple dimensions:

```python
from quality_evaluator import MLQualityEvaluator

# Initialize evaluator
evaluator = MLQualityEvaluator(use_ml=False)

# Evaluate response
evaluation = evaluator.evaluate(
    query="Which counties are most vulnerable?",
    response="Based on FEMA data, the top 3 counties are...",
    context={"tools_used": ["query_counties"], "data_sources": ["fema"]}
)

# Access quality scores
print(evaluation.dimensions.overall)  # 0.0 to 1.0
print(evaluation.dimensions.accuracy)
print(evaluation.suggestions)
```

**Dimensions:**
- **Accuracy**: Factual correctness
- **Completeness**: Coverage of query aspects
- **Relevance**: Alignment with query intent
- **Clarity**: Understandability and structure
- **Actionability**: Practical utility

### 3. Metrics Tracking (`metrics_tracker.py`)

Tracks comprehensive system metrics:

```python
from metrics_tracker import MetricsTracker, ModelPerformanceMetrics

# Initialize tracker
tracker = MetricsTracker()

# Record query metrics
tracker.record_query_metrics(
    query_id="abc123",
    query="Which counties are most vulnerable?",
    latency_ms=250.0,
    tools_used=["query_counties"],
    quality_score=0.85
)

# Get summary
summary = tracker.get_metrics_summary("query")
print(summary)
```

**Metrics Types:**
- Model performance (accuracy, latency, drift)
- System health (uptime, error rate, throughput)
- User experience (engagement, satisfaction)
- Custom business metrics

### 4. Integration (`integration_example.py`)

Complete integration with existing ResilienceAI:

```python
from integration_example import SelfImprovingAgent

# Create self-improving agent
agent = SelfImprovingAgent(base_agent=existing_agent)

# Process query with tracking
response = agent.process_query(
    query="Which Missouri counties are most vulnerable?",
    user_id="user123"
)

# Response includes quality metrics
print(response['quality']['overall'])
print(response['suggestions'])

# Submit feedback
agent.submit_feedback(
    query_id=response['query_id'],
    feedback_type="rating",
    rating=4
)
```

## Quick Start

### Installation

```bash
# Install dependencies
pip install numpy pandas scikit-learn joblib

# Optional: For advanced features
pip install optuna  # Hyperparameter optimization
pip install pyyaml  # Configuration management
```

### Basic Usage

```python
from feedback_collector import ExplicitFeedbackCollector
from quality_evaluator import MLQualityEvaluator
from metrics_tracker import MetricsTracker

# Initialize components
feedback = ExplicitFeedbackCollector()
evaluator = MLQualityEvaluator()
tracker = MetricsTracker()

# Process a query
query = "Which counties are most vulnerable to flooding?"
response = "Based on FEMA data..."

# Evaluate quality
evaluation = evaluator.evaluate(query, response)
print(f"Quality Score: {evaluation.dimensions.overall}")

# Track metrics
tracker.record_custom_metric("response_quality", evaluation.dimensions.overall)

# Collect feedback
feedback.collect_rating_feedback(query_id="abc123", rating=4)
```

## Configuration

Configure the system using `config.yaml`:

```yaml
feedback:
  enabled: true
  explicit:
    buffer_size: 100
    storage_path: "data/feedback/explicit"

quality_evaluation:
  enabled: true
  dimension_weights:
    accuracy: 0.25
    completeness: 0.20

metrics:
  enabled: true
  storage:
    path: "data/metrics"
    buffer_size: 1000
```

## Folder Structure

```
resilience_ai/
├── src/self_improve/              # Self-improvement package
│   ├── __init__.py
│   ├── feedback_collector.py      # Feedback collection
│   ├── quality_evaluator.py       # Quality evaluation
│   ├── metrics_tracker.py         # Metrics tracking
│   ├── ab_testing.py              # A/B testing (future)
│   ├── model_retrainer.py         # Model retraining (future)
│   └── integration_example.py     # Integration demo
├── data/
│   ├── feedback/                  # Feedback storage
│   ├── metrics/                   # Metrics storage
│   └── experiments/               # A/B test data
├── models/self_improve/           # ML models
├── logs/self_improve/             # System logs
└── config.yaml                    # Configuration
```

## Dashboard Integration

### Streamlit Dashboard

```python
from integration_example import render_feedback_ui, render_quality_dashboard
import streamlit as st

# Render feedback UI
render_feedback_ui(agent, query_id="abc123")

# Render quality dashboard
render_quality_dashboard(agent)
```

## API Endpoints

### Feedback API

```python
# Submit feedback
POST /api/feedback
{
    "query_id": "abc123",
    "type": "rating",
    "rating": 4,
    "comments": "Very helpful!"
}

# Get feedback summary
GET /api/feedback/summary
```

### Metrics API

```python
# Get metrics
GET /api/metrics?type=query&days=7

# Get system health
GET /api/metrics/health
```

### Quality API

```python
# Evaluate quality
POST /api/quality/evaluate
{
    "query": "Which counties are most vulnerable?",
    "response": "Based on FEMA data..."
}
```

## Performance Considerations

### Buffer Management
- Metrics are buffered and flushed to disk periodically
- Default buffer size: 1000 metrics
- Configurable auto-flush behavior

### Storage Efficiency
- JSONL format for human-readable logs
- Parquet option for large-scale analytics
- Automatic rotation and retention policies

### Memory Usage
- Bounded history for anomaly detection (max 1000 values)
- Session cleanup for implicit feedback
- Configurable buffer sizes

## Testing

```python
# Run integration example
python integration_example.py

# Test individual components
python -m pytest tests/test_feedback_collector.py
python -m pytest tests/test_quality_evaluator.py
python -m pytest tests/test_metrics_tracker.py
```

## Future Enhancements

### Phase 1: Foundation (Complete)
- ✅ Feedback collection
- ✅ Quality evaluation
- ✅ Metrics tracking
- ✅ Basic integration

### Phase 2: ML Enhancement
- 🔄 Train quality evaluation models
- 🔄 Sentiment analysis for text feedback
- 🔄 Automated issue classification

### Phase 3: Advanced Features
- ⏳ A/B testing framework
- ⏳ Automated model retraining
- ⏳ Hyperparameter optimization
- ⏳ Feature importance monitoring

### Phase 4: Automation
- ⏳ Continuous learning pipeline
- ⏳ System adaptation engine
- ⏳ Automated deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is part of the ResilienceAI disaster vulnerability assessment system.

## Support

For questions or issues:
- Open an issue on GitHub
- Contact the development team
- Check the documentation

## References

- [ResilienceAI Repository](https://github.com/GDogMcCoy/ResilienceAI)
- [Self-Improvement Analysis Document](../29_self_improvement.md)
- [MUIDSI Hackathon 2026](https://archia.com/hackathon)
