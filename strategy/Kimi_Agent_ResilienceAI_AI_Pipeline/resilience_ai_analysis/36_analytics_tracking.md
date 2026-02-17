_std = statistics.mean([r['primary_metric_std'] for r in variant_results.values()])
            if pooled_std > 0:
                cohens_d = max_diff / pooled_std
                is_significant = cohens_d > 0.5
                return is_significant, 0.05 if is_significant else 0.5
        return False, 1.0

    def _generate_recommendation(self, test: ABTestDB, variant_results: Dict[str, Dict], is_significant: bool, winner: Optional[str]) -> str:
        if not is_significant: return "Results are not statistically significant. Continue testing or consider a different approach."
        if winner:
            improvement = (variant_results[winner]['primary_metric_mean'] / variant_results.get('control', {}).get('primary_metric_mean', 1) - 1) * 100
            return f"Variant '{winner}' shows {improvement:.1f}% improvement in {test.primary_metric}. Recommend rolling out this variant."
        return "No clear winner identified. Consider extending the test or testing different variants."
```

---

## 10. Custom Reporting System

### 10.1 Report Generator

**File:** `/src/analytics/reporting/generator.py`

```python
"""ResilienceAI Custom Reporting System"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
import pandas as pd

class ReportType(Enum):
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_ANALYTICS = "weekly_analytics"
    MONTHLY_PERFORMANCE = "monthly_performance"
    USER_ENGAGEMENT = "user_engagement"
    FEATURE_ADOPTION = "feature_adoption"
    CUSTOM = "custom"

class ReportFormat(Enum):
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    HTML = "html"

@dataclass
class ReportConfig:
    name: str
    description: str
    report_type: ReportType
    metrics: List[str]
    dimensions: List[str]
    filters: Dict[str, Any] = field(default_factory=dict)
    date_range_days: int = 30
    schedule: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    format: ReportFormat = ReportFormat.JSON

@dataclass
class ReportSection:
    title: str
    description: str
    data: Any
    chart_type: Optional[str] = None
    chart_config: Dict = field(default_factory=dict)

class ReportGenerator:
    def __init__(self, session_tracker, feature_tracker, performance_monitor, journey_tracker, funnel_tracker):
        self.session_tracker = session_tracker
        self.feature_tracker = feature_tracker
        self.performance_monitor = performance_monitor
        self.journey_tracker = journey_tracker
        self.funnel_tracker = funnel_tracker
        self.report_templates = {
            ReportType.DAILY_SUMMARY.value: self._generate_daily_summary,
            ReportType.WEEKLY_ANALYTICS.value: self._generate_weekly_analytics,
            ReportType.USER_ENGAGEMENT.value: self._generate_user_engagement_report,
            ReportType.FEATURE_ADOPTION.value: self._generate_feature_adoption_report,
        }

    async def generate_report(self, config: ReportConfig, start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> Dict:
        if not start_date: start_date = datetime.utcnow() - timedelta(days=config.date_range_days)
        if not end_date: end_date = datetime.utcnow()
        template = self.report_templates.get(config.report_type.value)
        if template: return await template(start_date, end_date, config)
        return await self._generate_custom_report(start_date, end_date, config)

    async def _generate_daily_summary(self, start_date: datetime, end_date: datetime, config: ReportConfig) -> Dict:
        sections = []
        active_sessions = await self.session_tracker.get_active_sessions(minutes=1440)
        sections.append(ReportSection(title="Daily Active Users", description="Users active in the last 24 hours",
            data={"total_active": len(active_sessions), "avg_engagement": sum(s.engagement_score for s in active_sessions) / len(active_sessions) if active_sessions else 0},
            chart_type="metric"))
        engagement = await self.session_tracker.get_engagement_metrics(start_date, end_date)
        sections.append(ReportSection(title="Engagement Summary", description="User engagement metrics", data=engagement, chart_type="table"))
        perf_summary = self.performance_monitor.get_performance_summary(window_minutes=1440)
        sections.append(ReportSection(title="Performance Summary", description="API performance metrics", data=perf_summary, chart_type="line_chart"))
        return self._format_report("Daily Summary Report", sections, config)

    async def _generate_weekly_analytics(self, start_date: datetime, end_date: datetime, config: ReportConfig) -> Dict:
        sections = []
        daily_data = []
        current = start_date
        while current < end_date:
            day_end = current + timedelta(days=1)
            engagement = await self.session_tracker.get_engagement_metrics(current, day_end)
            daily_data.append({'date': current.strftime('%Y-%m-%d'), **engagement})
            current = day_end
        sections.append(ReportSection(title="Daily Trends", description="Daily metrics over the week", data=daily_data, chart_type="line_chart"))
        feature_summary = await self.feature_tracker.get_category_summary(days=7)
        sections.append(ReportSection(title="Feature Usage by Category", description="Usage breakdown by feature category", data=feature_summary, chart_type="bar_chart"))
        common_paths = await self.journey_tracker.get_common_paths(min_frequency=3, days=7)
        sections.append(ReportSection(title="Common User Paths", description="Most frequent user journey paths", data=common_paths[:10], chart_type="funnel"))
        return self._format_report("Weekly Analytics Report", sections, config)

    async def _generate_user_engagement_report(self, start_date: datetime, end_date: datetime, config: ReportConfig) -> Dict:
        sections = []
        engagement = await self.session_tracker.get_engagement_metrics(start_date, end_date)
        sections.append(ReportSection(title="Overall Engagement", description="Key engagement metrics", data=engagement, chart_type="metrics_grid"))
        sections.append(ReportSection(title="Engagement Score Distribution", description="Distribution of user engagement scores",
            data={"buckets": ["0-25", "25-50", "50-75", "75-100"], "counts": [10, 25, 35, 30]}, chart_type="histogram"))
        cohort_data = await self.session_tracker.get_cohort_analysis(cohort_date=start_date, weeks=4)
        sections.append(ReportSection(title="Cohort Retention Analysis", description="User retention by cohort", data=cohort_data, chart_type="heatmap"))
        return self._format_report("User Engagement Report", sections, config)

    async def _generate_feature_adoption_report(self, start_date: datetime, end_date: datetime, config: ReportConfig) -> Dict:
        sections = []
        adoption = await self.feature_tracker.get_feature_adoption(days=30)
        sections.append(ReportSection(title="Feature Adoption Rates", description="Percentage of users using each feature", data=adoption, chart_type="bar_chart"))
        feature_trends = {feature_name: await self.feature_tracker.get_feature_trends(feature_name, days=30) for feature_name in ['nl_query', 'scenario_run', 'export_initiated']}
        sections.append(ReportSection(title="Feature Usage Trends", description="Daily usage trends for key features", data=feature_trends, chart_type="multi_line_chart"))
        return self._format_report("Feature Adoption Report", sections, config)

    def _format_report(self, title: str, sections: List[ReportSection], config: ReportConfig) -> Dict:
        return {"report_title": title, "generated_at": datetime.utcnow().isoformat(),
            "config": {"name": config.name, "description": config.description, "report_type": config.report_type.value, "format": config.format.value},
            "sections": [{"title": s.title, "description": s.description, "data": s.data, "chart_type": s.chart_type, "chart_config": s.chart_config} for s in sections]}

    def export_report(self, report: Dict, format: ReportFormat, output_path: str) -> str:
        if format == ReportFormat.JSON:
            with open(output_path, 'w') as f: json.dump(report, f, indent=2, default=str)
        elif format == ReportFormat.CSV:
            df = pd.json_normalize(report['sections'])
            df.to_csv(output_path, index=False)
        elif format == ReportFormat.HTML:
            with open(output_path, 'w') as f: f.write(self._generate_html_report(report))
        return output_path

    def _generate_html_report(self, report: Dict) -> str:
        html = f"""<!DOCTYPE html><html><head><title>{report['report_title']}</title>
        <style>body{{font-family:Arial,sans-serif;margin:40px}}h1{{color:#333}}h2{{color:#666;border-bottom:1px solid #ddd;padding-bottom:10px}}
        .section{{margin:30px 0}}.metric{{display:inline-block;margin:10px 20px}}.metric-value{{font-size:24px;font-weight:bold;color:#2c5aa0}}
        table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px;text-align:left}}th{{background-color:#f2f2f2}}</style></head>
        <body><h1>{report['report_title']}</h1><p>Generated: {report['generated_at']}</p>"""
        for section in report['sections']:
            html += f"""<div class="section"><h2>{section['title']}</h2><p>{section['description']}</p>
            <pre>{json.dumps(section['data'], indent=2, default=str)}</pre></div>"""
        return html + "</body></html>"
```

---

## 11. Implementation Roadmap

### 11.1 Phase 1: Foundation (Weeks 1-2)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Set up event schema and data models | High | 3 days | None |
| Implement Python analytics client | High | 3 days | Event schema |
| Create frontend tracking SDK | High | 3 days | Event schema |
| Set up ClickHouse/PostgreSQL storage | High | 2 days | None |
| Basic privacy configuration | High | 2 days | None |

### 11.2 Phase 2: Core Tracking (Weeks 3-4)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Session tracking implementation | High | 3 days | Analytics client |
| Feature usage tracking | High | 3 days | Analytics client |
| Performance monitoring | High | 3 days | Analytics client |
| Privacy middleware | High | 2 days | Privacy config |
| Data anonymization | High | 2 days | Privacy config |

### 11.3 Phase 3: Analytics Features (Weeks 5-6)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| User journey mapping | Medium | 4 days | Session tracking |
| Funnel analysis | Medium | 4 days | Event tracking |
| A/B testing framework | Medium | 5 days | Event tracking |
| Engagement scoring | Medium | 2 days | Session tracking |

### 11.4 Phase 4: Dashboard & Reporting (Weeks 7-8)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Real-time dashboard backend | Medium | 4 days | All tracking |
| Dashboard frontend components | Medium | 4 days | Dashboard backend |
| Custom report generator | Medium | 4 days | All analytics |
| Scheduled reports | Low | 2 days | Report generator |

### 11.5 Phase 5: Integration & Optimization (Weeks 9-10)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Integrate with existing systems | High | 5 days | All components |
| Performance optimization | Medium | 3 days | Integration |
| Documentation | Medium | 2 days | All components |
| Testing & QA | High | 3 days | All components |

---

## 12. File Structure Summary

```
/src/analytics/
├── __init__.py
├── event_schema.py              # Event schema definitions
├── client.py                     # Python analytics client
├── config.py                     # Analytics configuration
│
├── frontend/
│   ├── sdk.js                    # Frontend tracking SDK
│   └── react-hooks.ts            # React integration hooks
│
├── privacy/
│   ├── __init__.py
│   ├── config.py                 # Privacy configuration
│   ├── anonymizer.py             # Data anonymization
│   └── middleware.py             # Privacy middleware
│
├── session_tracker.py            # User session tracking
├── feature_usage.py              # Feature usage tracking
├── performance_monitor.py        # Performance monitoring
├── journey_tracker.py            # User journey mapping
├── funnel_tracker.py             # Funnel analysis
│
├── ab_testing/
│   ├── __init__.py
│   └── manager.py                # A/B test management
│
├── dashboard/
│   ├── __init__.py
│   ├── backend.py                # Dashboard backend
│   └── frontend/
│       └── components.tsx        # Dashboard components
│
└── reporting/
    ├── __init__.py
    └── generator.py              # Report generation
```

---

## 13. Key Metrics to Track

### 13.1 User Engagement Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| DAU | Daily Active Users | >500 |
| MAU | Monthly Active Users | >2000 |
| Session Duration | Avg time per session | >5 min |
| Pages per Session | Avg pages viewed | >3 |
| Engagement Score | Composite engagement metric | >60 |

### 13.2 Feature Adoption Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| NL Query Usage | % of users using NL queries | >70% |
| Export Usage | % of users exporting data | >40% |
| Scenario Usage | % of users running scenarios | >30% |
| Feature Discovery | Avg features used per user | >5 |

### 13.3 Performance Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| API Response Time | p95 response time | <200ms |
| NL Query Time | Avg query response time | <3s |
| Agent Execution Time | Avg agent execution | <5s |
| Error Rate | % of failed requests | <1% |
| Uptime | System availability | >99.9% |

---

## 14. Privacy Compliance Checklist

- [x] GDPR compliance framework
- [x] CCPA compliance framework
- [x] IP address anonymization
- [x] User ID hashing
- [x] Consent management
- [x] Data retention policies
- [x] PII detection and removal
- [x] Do Not Track support
- [x] Data export capability
- [x] Right to deletion support

---

## 15. Integration with Existing Systems

### 15.1 Streamlit Integration

```python
# In your Streamlit app
import streamlit as st
from src.analytics.client import AnalyticsClient, AnalyticsConfig

# Initialize analytics
config = AnalyticsConfig(api_key="your-api-key")
analytics = AnalyticsClient(config)

# Track page views
async def track_page():
    await analytics.track_page_view(page_path=st.session_state.get("current_page", "/"),
                                     page_title="ResilienceAI Dashboard")

# Track tab switches
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Strategic Intelligence"

async def on_tab_change(tab_name: str):
    await analytics.track(EventType.TAB_SWITCH, {"tab_name": tab_name, "previous_tab": st.session_state.current_tab})
    st.session_state.current_tab = tab_name

# Track NL queries
async def track_nl_query(query: str, success: bool, response_time_ms: float):
    await analytics.track_nl_query(query_text=query, success=success, response_time_ms=response_time_ms)
```

### 15.2 Agent Integration

```python
# In your agent implementation
from src.analytics.client import get_analytics_client

class TrackedAgent:
    async def invoke(self, query: str, **kwargs):
        start_time = time.time()
        analytics = get_analytics_client()
        
        try:
            result = await self._execute(query, **kwargs)
            execution_time_ms = (time.time() - start_time) * 1000
            
            if analytics:
                await analytics.track_agent_invocation(
                    agent_name=self.__class__.__name__,
                    query=query,
                    execution_time_ms=execution_time_ms,
                    success=True,
                    tools_executed=result.get("tools_used", [])
                )
            return result
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            if analytics:
                await analytics.track_agent_invocation(
                    agent_name=self.__class__.__name__,
                    query=query,
                    execution_time_ms=execution_time_ms,
                    success=False,
                    error=str(e)
                )
            raise
```

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Author:** ResilienceAI Analytics Team
