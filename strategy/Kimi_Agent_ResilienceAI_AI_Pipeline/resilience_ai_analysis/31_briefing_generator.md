# ResilienceAI Briefing Generator Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of the current briefing generator capabilities in the ResilienceAI repository (claw-autonomous branch) and proposes extensive enhancements for an automated, multi-format reporting platform. The current `briefing_generator.py` (414 lines, 16.1 KB) provides basic PDF and PPTX generation for county-level vulnerability briefings, but lacks advanced automation, NLP summarization, and collaborative features.

---

## 1. Current State Analysis

### 1.1 Existing Briefing Generator (`src/briefing_generator.py`)

**Current Capabilities:**
- **Output Formats:** PDF (ReportLab), PPTX (python-pptx), Text
- **Report Types:** Single-county briefings, State-level briefings
- **Data Integration:** County features CSV, risk scores, vulnerability indices
- **Key Metrics:** Risk score, population, disaster count, redundancy score, poverty %
- **Visual Elements:** Basic tables, color-coded headers

**Current Architecture:**
```python
class BriefingGenerator:
    def __init__(self, df=None):
        # Loads county_features.csv from PROCESSED_DIR
        
    def generate_county_brief(self, fips, output_format="pdf"):
        # Generates single-county briefing
        
    def generate_state_brief(self, state_abbrev, output_format="pdf"):
        # Generates state-level briefing
        
    def _generate_pdf_brief(self, county):
        # PDF generation with ReportLab
        
    def _generate_pptx_brief(self, county):
        # PowerPoint generation with python-pptx
        
    def _generate_text_brief(self, county):
        # Plain text briefing
```

**Current Limitations:**
1. No HTML output support
2. No DOCX (Word) output support
3. No executive summary generation with NLP
4. No automated insight extraction
5. No chart/visualization integration
6. No template customization system
7. No distribution list management
8. No scheduled report generation
9. No collaborative editing features
10. No data-driven storytelling capabilities

---

## 2. Proposed Enhanced Briefing Generator Architecture

### 2.1 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI BRIEFING GENERATOR PLATFORM                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  Data Ingestion │  │  NLP Processing │  │  Template Engine │              │
│  │     Layer       │  │     Layer       │  │      Layer       │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
│           │                    │                    │                        │
│           ▼                    ▼                    ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    BRIEFING ORCHESTRATOR                             │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │   │
│  │  │  Executive   │ │   Insight    │ │   Section    │ │ Distribution │ │   │
│  │  │  Summarizer  │ │  Extractor   │ │   Builder    │ │   Manager    │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│           │                    │                    │                        │
│           ▼                    ▼                    ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    MULTI-FORMAT OUTPUT ENGINE                        │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  │   │
│  │  │  PDF   │ │  HTML  │ │  DOCX  │ │  PPTX  │ │  JSON  │ │  CSV   │  │   │
│  │  │Generator│ │Generator│ │Generator│ │Generator│ │Export │ │Export │  │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SCHEDULER & COLLABORATION LAYER                   │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │   │
│  │  │   Cron Jobs  │ │  Webhooks    │ │  Version     │ │  Comment     │ │   │
│  │  │   Scheduler  │ │  Integration │ │  Control     │ │  System      │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Enhanced Folder Structure

```
ResilienceAI/
├── src/
│   ├── briefing/                          # NEW: Briefing generator package
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── generator.py               # Main briefing orchestrator
│   │   │   ├── config.py                  # Briefing configuration
│   │   │   └── exceptions.py              # Custom exceptions
│   │   ├── nlp/
│   │   │   ├── __init__.py
│   │   │   ├── summarizer.py              # Executive summary generation
│   │   │   ├── insight_extractor.py       # Key insights extraction
│   │   │   ├── storytelling.py            # Data-driven narrative
│   │   │   └── sentiment_analyzer.py      # Sentiment analysis for reports
│   │   ├── templates/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                    # Base template class
│   │   │   ├── county_brief.py            # County briefing template
│   │   │   ├── state_brief.py             # State briefing template
│   │   │   ├── executive_summary.py       # Executive summary template
│   │   │   ├── custom_template.py         # User-defined templates
│   │   │   └── registry.py                # Template registry
│   │   ├── formatters/
│   │   │   ├── __init__.py
│   │   │   ├── pdf_formatter.py           # PDF generation
│   │   │   ├── html_formatter.py          # HTML generation
│   │   │   ├── docx_formatter.py          # DOCX generation
│   │   │   ├── pptx_formatter.py          # PPTX generation
│   │   │   ├── json_formatter.py          # JSON export
│   │   │   └── csv_formatter.py           # CSV export
│   │   ├── visualizations/
│   │   │   ├── __init__.py
│   │   │   ├── chart_embedder.py          # Chart embedding
│   │   │   ├── map_embedder.py            # Map embedding
│   │   │   ├── table_formatter.py         # Table styling
│   │   │   └── image_processor.py         # Image optimization
│   │   ├── distribution/
│   │   │   ├── __init__.py
│   │   │   ├── email_sender.py            # Email distribution
│   │   │   ├── list_manager.py            # Distribution list management
│   │   │   ├── webhook_handler.py         # Webhook integration
│   │   │   └── notification_service.py    # Push notifications
│   │   ├── scheduling/
│   │   │   ├── __init__.py
│   │   │   ├── scheduler.py               # Report scheduler
│   │   │   ├── cron_jobs.py               # Cron job definitions
│   │   │   └── trigger_manager.py         # Event triggers
│   │   └── collaboration/
│   │       ├── __init__.py
│   │       ├── version_control.py         # Document versioning
│   │       ├── comment_system.py          # Comment/annotation system
│   │       ├── review_workflow.py         # Review approval workflow
│   │       └── sharing_manager.py         # Document sharing
│   ├── briefing_generator.py              # LEGACY: Original generator
│   └── ...
├── templates/                             # NEW: Report templates
│   ├── briefings/
│   │   ├── county_default.json
│   │   ├── state_default.json
│   │   ├── executive_summary.json
│   │   └── custom/
│   ├── styles/
│   │   ├── pdf_styles.css
│   │   ├── html_styles.css
│   │   └── docx_styles.xml
│   └── assets/
│       ├── logos/
│       ├── headers/
│       └── footers/
├── reports/                               # Generated reports
│   ├── pdf/
│   ├── html/
│   ├── docx/
│   ├── pptx/
│   └── archive/
├── data/
│   └── briefing_cache/                    # Briefing data cache
└── docs/
    └── briefing_api.md                    # API documentation
```

---

## 3. Implementation Components

### 3.1 Executive Summary Generation with NLP

**File:** `src/briefing/nlp/summarizer.py`

```python
"""
Executive Summary Generator using NLP
Generates concise, actionable executive summaries from vulnerability data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from pathlib import Path
import json
import re

# NLP Libraries
try:
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class SummaryType(Enum):
    """Types of executive summaries."""
    EXECUTIVE = "executive"           # High-level overview
    TECHNICAL = "technical"           # Technical details
    OPERATIONAL = "operational"       # Action-oriented
    STRATEGIC = "strategic"           # Long-term planning
    CRISIS = "crisis"                 # Emergency response


@dataclass
class SummarySection:
    """A section of an executive summary."""
    title: str
    content: str
    priority: int  # 1-5, 5 being highest
    key_metrics: Dict[str, Any]
    recommendations: List[str]


@dataclass
class ExecutiveSummary:
    """Complete executive summary with metadata."""
    title: str
    generated_at: str
    summary_type: SummaryType
    sections: List[SummarySection]
    key_findings: List[str]
    critical_alerts: List[str]
    recommendations: List[str]
    confidence_score: float
    word_count: int
    reading_time_minutes: int


class NLPSummarizer:
    """
    NLP-based executive summary generator for disaster vulnerability reports.
    
    Features:
    - Abstractive summarization using transformer models
    - Extractive summarization for key points
    - Sentiment analysis for tone adjustment
    - Automatic highlight generation
    - Reading level optimization
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        """Initialize the NLP summarizer."""
        self.model_name = model_name
        self.summarizer = None
        self.sentiment_analyzer = None
        self.nlp = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self.summarizer = pipeline(
                    "summarization", model=model_name, max_length=150, min_length=30
                )
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
            except Exception as e:
                print(f"Warning: Could not load transformer models: {e}")
        
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                print("Warning: spaCy model not available")
    
    def generate_executive_summary(
        self,
        county_data: pd.Series,
        context_data: Optional[Dict] = None,
        summary_type: SummaryType = SummaryType.EXECUTIVE,
        max_length: int = 500
    ) -> ExecutiveSummary:
        """Generate an executive summary for a county."""
        from datetime import datetime
        
        sections = []
        key_findings = []
        critical_alerts = []
        recommendations = []
        
        # Generate overview section
        overview = self._generate_overview_section(county_data, summary_type)
        sections.append(overview)
        
        # Generate risk analysis section
        risk_section = self._generate_risk_section(county_data)
        sections.append(risk_section)
        key_findings.extend(risk_section.key_metrics.get("findings", []))
        
        # Generate vulnerability section
        vuln_section = self._generate_vulnerability_section(county_data)
        sections.append(vuln_section)
        
        # Generate infrastructure section
        infra_section = self._generate_infrastructure_section(county_data)
        sections.append(infra_section)
        
        # Generate recommendations section
        rec_section = self._generate_recommendations_section(county_data)
        sections.append(rec_section)
        recommendations.extend(rec_section.recommendations)
        
        # Extract critical alerts
        critical_alerts = self._extract_critical_alerts(county_data)
        
        # Calculate confidence and metrics
        confidence = self._calculate_confidence(county_data)
        total_words = sum(len(s.content.split()) for s in sections)
        reading_time = max(1, total_words // 200)  # ~200 WPM
        
        return ExecutiveSummary(
            title=f"Executive Summary: {county_data.get('county_name', 'Unknown County')}",
            generated_at=datetime.now().isoformat(),
            summary_type=summary_type,
            sections=sections,
            key_findings=key_findings,
            critical_alerts=critical_alerts,
            recommendations=recommendations,
            confidence_score=confidence,
            word_count=total_words,
            reading_time_minutes=reading_time
        )
    
    def _generate_overview_section(self, county_data: pd.Series, summary_type: SummaryType) -> SummarySection:
        """Generate the overview section."""
        county_name = county_data.get('county_name', 'Unknown County')
        state = county_data.get('state', 'Unknown State')
        population = county_data.get('total_population', 0)
        risk_score = county_data.get('risk_score', 0)
        risk_level = county_data.get('risk_level', 'Unknown')
        
        if risk_level == "High":
            narrative = (
                f"{county_name}, {state} is classified as HIGH RISK with a vulnerability "
                f"score of {risk_score:.3f}. With a population of {population:,}, this "
                f"county requires immediate attention for disaster preparedness and "
                f"infrastructure resilience improvements."
            )
        elif risk_level == "Medium":
            narrative = (
                f"{county_name}, {state} has a MODERATE risk profile (score: {risk_score:.3f}). "
                f"The county's population of {population:,} faces elevated vulnerability "
                f"that warrants proactive mitigation measures."
            )
        else:
            narrative = (
                f"{county_name}, {state} currently shows LOWER risk levels (score: {risk_score:.3f}) "
                f"but ongoing monitoring is recommended for its {population:,} residents."
            )
        
        return SummarySection(
            title="Overview", content=narrative, priority=5,
            key_metrics={"population": population, "risk_score": risk_score, "risk_level": risk_level},
            recommendations=[]
        )
    
    def _extract_critical_alerts(self, county_data: pd.Series) -> List[str]:
        """Extract critical alerts from county data."""
        alerts = []
        if county_data.get('zero_redundancy_flag', 0) == 1:
            alerts.append("ZERO REDUNDANCY: Healthcare single point of failure")
        if county_data.get('disaster_acceleration', 0) > 2.0:
            alerts.append("ACCELERATING DISASTERS: Frequency has more than doubled")
        if county_data.get('compound_risk_count', 0) >= 3:
            alerts.append("COMPOUND RISK: Multiple simultaneous vulnerability factors")
        if county_data.get('poverty_pct', 0) > 25:
            alerts.append("HIGH POVERTY: Economic vulnerability amplifies disaster impact")
        return alerts
    
    def _calculate_confidence(self, county_data: pd.Series) -> float:
        """Calculate confidence score based on data completeness."""
        required_fields = ['risk_score', 'total_population', 'disaster_count', 'redundancy_score', 'vulnerability_index']
        present = sum(1 for f in required_fields if pd.notna(county_data.get(f)))
        return present / len(required_fields)


# Convenience function
def generate_county_summary(county_data: pd.Series, output_format: str = "text") -> str:
    """Quick function to generate a county summary."""
    summarizer = NLPSummarizer()
    summary = summarizer.generate_executive_summary(county_data)
    
    if output_format == "json":
        return json.dumps({
            "title": summary.title,
            "generated_at": summary.generated_at,
            "sections": [{"title": s.title, "content": s.content} for s in summary.sections],
            "key_findings": summary.key_findings,
            "critical_alerts": summary.critical_alerts,
            "recommendations": summary.recommendations
        }, indent=2)
    else:
        lines = [f"# {summary.title}", f"Generated: {summary.generated_at}", ""]
        lines.extend(f"## {s.title}\n{s.content}\n" for s in summary.sections)
        return "\n".join(lines)
```

---

## 4. Multi-Format Output System

### 4.1 HTML Formatter

**File:** `src/briefing/formatters/html_formatter.py`

```python
"""HTML Report Formatter - Generates interactive HTML reports with embedded charts."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
from jinja2 import Template


class HTMLFormatter:
    """Generate interactive HTML reports with Bootstrap, Plotly, and Leaflet."""
    
    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir or Path(__file__).parent / "templates"
        self.default_template = self._get_default_template()
    
    def generate_report(
        self, data: Dict[str, Any], output_path: Path,
        template_name: str = "default", include_charts: bool = True,
        include_maps: bool = True, theme: str = "light"
    ) -> Path:
        """Generate HTML report."""
        template = self._load_template(template_name)
        chart_data = self._prepare_chart_data(data) if include_charts else {}
        map_data = self._prepare_map_data(data) if include_maps else {}
        
        html_content = template.render(
            data=data, chart_data=json.dumps(chart_data), map_data=json.dumps(map_data),
            theme=theme, generated_at=datetime.now().isoformat(),
            css=self._get_css(theme), js=self._get_js()
        )
        
        output_path.write_text(html_content, encoding='utf-8')
        return output_path
    
    def _get_default_template(self) -> Template:
        """Get default HTML template with Bootstrap, Plotly, Leaflet."""
        template_str = '''<!DOCTYPE html>
<html lang="en" data-theme="{{ theme }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>{{ css }}</style>
</head>
<body>
    <div class="container-fluid">
        <header class="report-header">
            <div class="row">
                <div class="col-md-8">
                    <h1>{{ data.title }}</h1>
                    <p class="text-muted">Generated: {{ generated_at }}</p>
                </div>
                <div class="col-md-4 text-end">
                    <button class="btn btn-outline-secondary" onclick="toggleTheme()">Toggle Theme</button>
                    <button class="btn btn-outline-primary" onclick="window.print()">Print Report</button>
                </div>
            </div>
        </header>
        
        {% if data.executive_summary %}
        <section class="executive-summary">
            <h2>Executive Summary</h2>
            <div class="alert-container">
                {% for alert in data.executive_summary.critical_alerts %}
                <div class="alert alert-danger">{{ alert }}</div>
                {% endfor %}
            </div>
            {% for section in data.executive_summary.sections %}
            <div class="summary-section">
                <h3>{{ section.title }}</h3>
                <p>{{ section.content }}</p>
            </div>
            {% endfor %}
        </section>
        {% endif %}
        
        <section class="risk-overview">
            <h2>Risk Overview</h2>
            <div class="row">
                <div class="col-md-4">
                    <div class="metric-card">
                        <h4>Risk Score</h4>
                        <div class="metric-value {{ 'high' if data.risk_score > 0.7 else 'medium' if data.risk_score > 0.4 else 'low' }}">
                            {{ "%.3f"|format(data.risk_score) }}
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-card">
                        <h4>Risk Level</h4>
                        <div class="metric-value {{ data.risk_level|lower }}">{{ data.risk_level }}</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-card">
                        <h4>Population</h4>
                        <div class="metric-value">{{ "{:,}".format(data.population) }}</div>
                    </div>
                </div>
            </div>
        </section>
        
        {% if chart_data %}
        <section class="charts">
            <h2>Visualizations</h2>
            <div id="risk-chart" class="chart-container"></div>
            <div id="vulnerability-chart" class="chart-container"></div>
        </section>
        {% endif %}
        
        <footer class="report-footer">
            <p>ResilienceAI | MUIDSI 2026 | 100% Real Federal Data</p>
        </footer>
    </div>
    
    <script>{{ js }}</script>
    <script>
        {% if chart_data %}
        const chartData = {{ chart_data|safe }};
        Plotly.newPlot('risk-chart', chartData.riskChart.data, chartData.riskChart.layout);
        Plotly.newPlot('vulnerability-chart', chartData.vulnerabilityChart.data, chartData.vulnerabilityChart.layout);
        {% endif %}
    </script>
</body>
</html>'''
        return Template(template_str)
    
    def _get_css(self, theme: str) -> str:
        return """
        :root { --bg-color: #ffffff; --text-color: #333333; --header-bg: #1a1f2e; --header-text: #4fc3f7; --card-bg: #f8f9fa; --border-color: #dee2e6; }
        [data-theme="dark"] { --bg-color: #1a1f2e; --text-color: #e0e0e0; --header-bg: #0d1117; --card-bg: #212529; --border-color: #373b3e; }
        body { background-color: var(--bg-color); color: var(--text-color); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .report-header { background: var(--header-bg); color: var(--header-text); padding: 2rem; margin-bottom: 2rem; }
        .metric-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1.5rem; text-align: center; margin-bottom: 1rem; }
        .metric-value { font-size: 2.5rem; font-weight: bold; margin-top: 0.5rem; }
        .metric-value.high { color: #dc3545; } .metric-value.medium { color: #ffc107; } .metric-value.low { color: #28a745; }
        .chart-container { height: 400px; margin: 2rem 0; }
        section { margin-bottom: 3rem; padding: 0 1rem; }
        @media print { .btn, .alert-container { display: none; } section { page-break-inside: avoid; } }
        """
    
    def _get_js(self) -> str:
        return "function toggleTheme() { const html = document.documentElement; const current = html.getAttribute('data-theme'); html.setAttribute('data-theme', current === 'light' ? 'dark' : 'light'); }"
    
    def _prepare_chart_data(self, data: Dict) -> Dict:
        return {
            "riskChart": {
                "data": [{"type": "indicator", "mode": "gauge+number", "value": data.get('risk_score', 0) * 100,
                          "title": {"text": "Risk Score"}, "gauge": {"axis": {"range": [0, 100]}, "bar": {"color": "#4fc3f7"},
                          "steps": [{"range": [0, 40], "color": "#d4edda"}, {"range": [40, 70], "color": "#fff3cd"}, {"range": [70, 100], "color": "#f8d7da"}]}}],
                "layout": {"height": 300}
            },
            "vulnerabilityChart": {
                "data": [{"type": "bar", "x": ['Poverty', 'Elderly', 'Disability', 'Isolation'],
                          "y": [data.get('poverty_pct', 0), data.get('elderly_pct', 0), data.get('disability_pct', 0), data.get('isolation_index', 0) * 100],
                          "marker": {"color": '#4fc3f7'}}],
                "layout": {"title": "Vulnerability Factors", "height": 300}
            }
        }
    
    def _prepare_map_data(self, data: Dict) -> Dict:
        return {"center": data.get('coordinates', [39.0, -92.0]), "zoom": 8, "geojson": data.get('geojson', {})}
    
    def _load_template(self, template_name: str) -> Template:
        template_path = self.template_dir / f"{template_name}.html"
        if template_path.exists():
            return Template(template_path.read_text())
        return self.default_template
```

---

## 5. Template System

### 5.1 Template Registry

**File:** `src/briefing/templates/registry.py`

```python
"""Template Registry for Briefing Generator - Manages report templates."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
from enum import Enum


class SectionType(Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    RISK_OVERVIEW = "risk_overview"
    VULNERABILITY_ANALYSIS = "vulnerability_analysis"
    INFRASTRUCTURE_ASSESSMENT = "infrastructure_assessment"
    DISASTER_HISTORY = "disaster_history"
    RECOMMENDATIONS = "recommendations"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    APPENDIX = "appendix"


@dataclass
class SectionConfig:
    section_type: SectionType
    title: str
    enabled: bool = True
    order: int = 0
    collapsible: bool = False
    default_collapsed: bool = False
    required_metrics: List[str] = field(default_factory=list)
    chart_type: Optional[str] = None


@dataclass
class TemplateConfig:
    name: str
    description: str
    version: str
    author: str
    created_at: str
    updated_at: str
    target_audience: str  # 'executive', 'technical', 'operational', 'public'
    output_formats: List[str] = field(default_factory=lambda: ['pdf', 'html'])
    sections: List[SectionConfig] = field(default_factory=list)
    styling: Dict[str, Any] = field(default_factory=dict)
    branding: Dict[str, Any] = field(default_factory=dict)


class TemplateRegistry:
    """Registry for managing briefing templates with customization support."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(__file__).parent / "../../../templates/briefings"
        self.templates: Dict[str, TemplateConfig] = {}
        self.section_generators: Dict[SectionType, Callable] = {}
        self._register_default_templates()
    
    def _register_default_templates(self):
        """Register built-in templates."""
        # County Executive Brief
        self.register_template(TemplateConfig(
            name="county_executive",
            description="Executive briefing for county-level vulnerability assessment",
            version="1.0.0", author="ResilienceAI", created_at="2026-01-01", updated_at="2026-01-01",
            target_audience="executive", output_formats=["pdf", "html", "docx", "pptx"],
            sections=[
                SectionConfig(section_type=SectionType.EXECUTIVE_SUMMARY, title="Executive Summary", order=1, required_metrics=["risk_score", "risk_level"]),
                SectionConfig(section_type=SectionType.RISK_OVERVIEW, title="Risk Overview", order=2, required_metrics=["risk_score", "disaster_count"]),
                SectionConfig(section_type=SectionType.VULNERABILITY_ANALYSIS, title="Population Vulnerability", order=3, required_metrics=["poverty_pct", "elderly_pct"]),
                SectionConfig(section_type=SectionType.INFRASTRUCTURE_ASSESSMENT, title="Infrastructure Assessment", order=4, required_metrics=["redundancy_score", "hospital_count"]),
                SectionConfig(section_type=SectionType.RECOMMENDATIONS, title="Strategic Recommendations", order=5, required_metrics=["top_intervention"])
            ],
            styling={"primary_color": "#4FC3F7", "secondary_color": "#1A1F2E", "font_family": "Helvetica", "font_size": 11},
            branding={"logo_path": "assets/logos/resilienceai.png", "header_text": "ResilienceAI Executive Briefing", "footer_text": "ResilienceAI | MUIDSI 2026"}
        ))
        
        # State Brief
        self.register_template(TemplateConfig(
            name="state_executive", description="State-level comparative briefing",
            version="1.0.0", author="ResilienceAI", created_at="2026-01-01", updated_at="2026-01-01",
            target_audience="executive", output_formats=["pdf", "html", "pptx"],
            sections=[
                SectionConfig(section_type=SectionType.EXECUTIVE_SUMMARY, title="State Overview", order=1),
                SectionConfig(section_type=SectionType.COMPARATIVE_ANALYSIS, title="County Comparison", order=2, chart_type="bar_chart"),
                SectionConfig(section_type=SectionType.RISK_OVERVIEW, title="Risk Distribution", order=3, chart_type="map"),
                SectionConfig(section_type=SectionType.RECOMMENDATIONS, title="Statewide Priorities", order=4)
            ]
        ))
        
        # Crisis Brief
        self.register_template(TemplateConfig(
            name="crisis_response", description="Emergency response briefing with critical alerts",
            version="1.0.0", author="ResilienceAI", created_at="2026-01-01", updated_at="2026-01-01",
            target_audience="operational", output_formats=["pdf", "html"],
            sections=[
                SectionConfig(section_type=SectionType.EXECUTIVE_SUMMARY, title="CRITICAL ALERTS", order=1),
                SectionConfig(section_type=SectionType.RISK_OVERVIEW, title="Immediate Risk Factors", order=2),
                SectionConfig(section_type=SectionType.INFRASTRUCTURE_ASSESSMENT, title="Infrastructure Status", order=3),
                SectionConfig(section_type=SectionType.RECOMMENDATIONS, title="Immediate Actions Required", order=4)
            ],
            styling={"primary_color": "#DC3545", "alert_highlight": "#FFF3CD"}
        ))
    
    def register_template(self, config: TemplateConfig) -> None:
        self.templates[config.name] = config
    
    def get_template(self, name: str) -> Optional[TemplateConfig]:
        return self.templates.get(name)
    
    def list_templates(self, audience: Optional[str] = None, format: Optional[str] = None) -> List[TemplateConfig]:
        templates = list(self.templates.values())
        if audience:
            templates = [t for t in templates if t.target_audience == audience]
        if format:
            templates = [t for t in templates if format in t.output_formats]
        return templates
    
    def save_template(self, name: str, output_path: Path) -> None:
        template = self.templates.get(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        data = {
            "name": template.name, "description": template.description, "version": template.version,
            "author": template.author, "created_at": template.created_at, "updated_at": template.updated_at,
            "target_audience": template.target_audience, "output_formats": template.output_formats,
            "sections": [{"section_type": s.section_type.value, "title": s.title, "enabled": s.enabled,
                          "order": s.order, "collapsible": s.collapsible, "required_metrics": s.required_metrics,
                          "chart_type": s.chart_type} for s in template.sections],
            "styling": template.styling, "branding": template.branding
        }
        output_path.write_text(json.dumps(data, indent=2))


# Global registry instance
_registry = None
def get_registry() -> TemplateRegistry:
    global _registry
    if _registry is None:
        _registry = TemplateRegistry()
    return _registry
```

---

## 6. Distribution List Management

### 6.1 Distribution Manager

**File:** `src/briefing/distribution/list_manager.py`

```python
"""Distribution List Manager - Manages recipient lists for automated report distribution."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime
from enum import Enum


class RecipientType(Enum):
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    EXTERNAL = "external"


class DeliveryMethod(Enum):
    EMAIL = "email"
    WEBHOOK = "webhook"
    API = "api"
    FILE_SHARE = "file_share"


@dataclass
class Recipient:
    id: str
    name: str
    email: Optional[str] = None
    recipient_type: RecipientType = RecipientType.EXECUTIVE
    delivery_methods: List[DeliveryMethod] = field(default_factory=lambda: [DeliveryMethod.EMAIL])
    preferences: Dict[str, Any] = field(default_factory=dict)
    report_types: List[str] = field(default_factory=lambda: ["county_executive"])
    formats: List[str] = field(default_factory=lambda: ["pdf"])
    schedule: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_delivery: Optional[str] = None


@dataclass
class DistributionList:
    id: str
    name: str
    description: str
    recipients: List[str] = field(default_factory=list)
    report_types: List[str] = field(default_factory=list)
    schedule: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    active: bool = True


class DistributionManager:
    """Manage distribution lists and recipient preferences."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(__file__).parent / "../../../data/distribution"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.recipients_file = self.storage_path / "recipients.json"
        self.lists_file = self.storage_path / "lists.json"
        self.recipients: Dict[str, Recipient] = {}
        self.distribution_lists: Dict[str, DistributionList] = {}
        self._load_data()
    
    def _load_data(self):
        if self.recipients_file.exists():
            data = json.loads(self.recipients_file.read_text())
            for r in data:
                self.recipients[r["id"]] = Recipient(
                    id=r["id"], name=r["name"], email=r.get("email"),
                    recipient_type=RecipientType(r.get("recipient_type", "executive")),
                    delivery_methods=[DeliveryMethod(m) for m in r.get("delivery_methods", ["email"])],
                    preferences=r.get("preferences", {}), report_types=r.get("report_types", ["county_executive"]),
                    formats=r.get("formats", ["pdf"]), schedule=r.get("schedule"), filters=r.get("filters", {}),
                    active=r.get("active", True), created_at=r.get("created_at"), last_delivery=r.get("last_delivery")
                )
        if self.lists_file.exists():
            data = json.loads(self.lists_file.read_text())
            for l in data:
                self.distribution_lists[l["id"]] = DistributionList(
                    id=l["id"], name=l["name"], description=l["description"],
                    recipients=l.get("recipients", []), report_types=l.get("report_types", []),
                    schedule=l.get("schedule"), created_at=l.get("created_at"), updated_at=l.get("updated_at"),
                    active=l.get("active", True)
                )
    
    def _save_data(self):
        recipients_data = [{"id": r.id, "name": r.name, "email": r.email, "recipient_type": r.recipient_type.value,
                            "delivery_methods": [m.value for m in r.delivery_methods], "preferences": r.preferences,
                            "report_types": r.report_types, "formats": r.formats, "schedule": r.schedule,
                            "filters": r.filters, "active": r.active, "created_at": r.created_at,
                            "last_delivery": r.last_delivery} for r in self.recipients.values()]
        self.recipients_file.write_text(json.dumps(recipients_data, indent=2))
        lists_data = [{"id": l.id, "name": l.name, "description": l.description, "recipients": l.recipients,
                       "report_types": l.report_types, "schedule": l.schedule, "created_at": l.created_at,
                       "updated_at": l.updated_at, "active": l.active} for l in self.distribution_lists.values()]
        self.lists_file.write_text(json.dumps(lists_data, indent=2))
    
    def add_recipient(self, name: str, email: Optional[str] = None, recipient_type: RecipientType = RecipientType.EXECUTIVE,
                      report_types: Optional[List[str]] = None, formats: Optional[List[str]] = None, **kwargs) -> Recipient:
        recipient_id = f"recipient_{len(self.recipients) + 1:04d}"
        recipient = Recipient(id=recipient_id, name=name, email=email, recipient_type=recipient_type,
                              report_types=report_types or ["county_executive"], formats=formats or ["pdf"], **kwargs)
        self.recipients[recipient_id] = recipient
        self._save_data()
        return recipient
    
    def create_distribution_list(self, name: str, description: str, recipient_ids: Optional[List[str]] = None,
                                 report_types: Optional[List[str]] = None, schedule: Optional[str] = None) -> DistributionList:
        list_id = f"list_{len(self.distribution_lists) + 1:04d}"
        dist_list = DistributionList(id=list_id, name=name, description=description, recipients=recipient_ids or [],
                                     report_types=report_types or ["county_executive"], schedule=schedule)
        self.distribution_lists[list_id] = dist_list
        self._save_data()
        return dist_list
    
    def get_recipients_for_report(self, report_type: str, county_fips: Optional[str] = None,
                                   risk_level: Optional[str] = None) -> List[Recipient]:
        matching = []
        for recipient in self.recipients.values():
            if not recipient.active or report_type not in recipient.report_types:
                continue
            filters = recipient.filters
            if county_fips and filters.get("counties") and county_fips not in filters["counties"]:
                continue
            if risk_level and filters.get("risk_levels") and risk_level not in filters["risk_levels"]:
                continue
            matching.append(recipient)
        return matching
```

---

## 7. Scheduled Report Generation

### 7.1 Report Scheduler

**File:** `src/briefing/scheduling/scheduler.py`

```python
"""Report Scheduler - Manages automated report generation and distribution schedules."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime, timedelta
from enum import Enum
import threading
import time


class ScheduleType(Enum):
    CRON = "cron"
    INTERVAL = "interval"
    EVENT = "event"
    ONE_TIME = "one_time"


class ReportTrigger(Enum):
    SCHEDULED = "scheduled"
    RISK_THRESHOLD = "risk_threshold"
    DISASTER_EVENT = "disaster_event"
    WEATHER_ALERT = "weather_alert"
    MANUAL = "manual"
    API_CALL = "api_call"


@dataclass
class ScheduleConfig:
    id: str
    name: str
    report_type: str
    template: str
    output_formats: List[str]
    recipients: List[str]
    schedule_type: ScheduleType
    cron_expression: Optional[str] = None
    interval_minutes: Optional[int] = None
    event_triggers: List[ReportTrigger] = field(default_factory=list)
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    parameters: Dict[str, Any] = field(default_factory=dict)


class ReportScheduler:
    """Schedule and manage automated report generation."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path(__file__).parent / "../../../data/schedules"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.schedules_file = self.storage_path / "schedules.json"
        self.schedules: Dict[str, ScheduleConfig] = {}
        self.running = False
        self.scheduler_thread = None
        self.job_queue = []
        self.callbacks: Dict[str, Callable] = {}
        self._load_schedules()
    
    def _load_schedules(self):
        if self.schedules_file.exists():
            data = json.loads(self.schedules_file.read_text())
            for s in data:
                self.schedules[s["id"]] = ScheduleConfig(
                    id=s["id"], name=s["name"], report_type=s["report_type"], template=s["template"],
                    output_formats=s["output_formats"], recipients=s["recipients"],
                    schedule_type=ScheduleType(s["schedule_type"]), cron_expression=s.get("cron_expression"),
                    interval_minutes=s.get("interval_minutes"),
                    event_triggers=[ReportTrigger(t) for t in s.get("event_triggers", [])],
                    enabled=s.get("enabled", True), last_run=s.get("last_run"), next_run=s.get("next_run"),
                    created_at=s.get("created_at"), parameters=s.get("parameters", {})
                )
    
    def _save_schedules(self):
        data = [{"id": s.id, "name": s.name, "report_type": s.report_type, "template": s.template,
                 "output_formats": s.output_formats, "recipients": s.recipients,
                 "schedule_type": s.schedule_type.value, "cron_expression": s.cron_expression,
                 "interval_minutes": s.interval_minutes, "event_triggers": [t.value for t in s.event_triggers],
                 "enabled": s.enabled, "last_run": s.last_run, "next_run": s.next_run,
                 "created_at": s.created_at, "parameters": s.parameters} for s in self.schedules.values()]
        self.schedules_file.write_text(json.dumps(data, indent=2))
    
    def create_schedule(self, name: str, report_type: str, template: str, output_formats: List[str],
                        recipients: List[str], schedule_type: ScheduleType, cron_expression: Optional[str] = None,
                        interval_minutes: Optional[int] = None, event_triggers: Optional[List[ReportTrigger]] = None,
                        parameters: Optional[Dict] = None) -> ScheduleConfig:
        schedule_id = f"schedule_{len(self.schedules) + 1:04d}"
        next_run = None
        if schedule_type == ScheduleType.INTERVAL and interval_minutes:
            next_run = (datetime.now() + timedelta(minutes=interval_minutes)).isoformat()
        schedule = ScheduleConfig(id=schedule_id, name=name, report_type=report_type, template=template,
                                  output_formats=output_formats, recipients=recipients, schedule_type=schedule_type,
                                  cron_expression=cron_expression, interval_minutes=interval_minutes,
                                  event_triggers=event_triggers or [], next_run=next_run, parameters=parameters or {})
        self.schedules[schedule_id] = schedule
        self._save_schedules()
        return schedule
    
    def register_callback(self, event: str, callback: Callable):
        self.callbacks[event] = callback
    
    def trigger_event(self, trigger: ReportTrigger, data: Dict[str, Any]):
        for schedule in self.schedules.values():
            if not schedule.enabled or trigger not in schedule.event_triggers:
                continue
            self.job_queue.append({"schedule_id": schedule.id, "trigger": trigger.value, "data": data,
                                   "queued_at": datetime.now().isoformat()})
            if "generate_report" in self.callbacks:
                self.callbacks["generate_report"](schedule, data)
    
    def start(self):
        if self.running:
            return
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop(self):
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def _run_scheduler(self):
        while self.running:
            now = datetime.now()
            for schedule in self.schedules.values():
                if not schedule.enabled:
                    continue
                should_run = False
                if schedule.schedule_type == ScheduleType.INTERVAL and schedule.next_run:
                    if now >= datetime.fromisoformat(schedule.next_run):
                        should_run = True
                        schedule.next_run = (now + timedelta(minutes=schedule.interval_minutes)).isoformat()
                elif schedule.schedule_type == ScheduleType.CRON and schedule.cron_expression:
                    if self._should_run_cron(schedule.cron_expression, now):
                        should_run = True
                if should_run and "generate_report" in self.callbacks:
                    schedule.last_run = now.isoformat()
                    self.callbacks["generate_report"](schedule, {})
            self._save_schedules()
            time.sleep(60)
    
    def _should_run_cron(self, cron_expr: str, now: datetime) -> bool:
        try:
            parts = cron_expr.split()
            if len(parts) != 5:
                return False
            minute, hour, day, month, weekday = parts
            if minute != "*" and now.minute != int(minute): return False
            if hour != "*" and now.hour != int(hour): return False
            if day != "*" and now.day != int(day): return False
            if month != "*" and now.month != int(month): return False
            if weekday != "*" and now.weekday() != int(weekday): return False
            return True
        except:
            return False


# Convenience functions
def create_daily_schedule(scheduler: ReportScheduler, name: str, report_type: str, hour: int = 8,
                          minute: int = 0, recipients: Optional[List[str]] = None) -> ScheduleConfig:
    return scheduler.create_schedule(name=name, report_type=report_type, template="county_executive",
                                     output_formats=["pdf"], recipients=recipients or [],
                                     schedule_type=ScheduleType.CRON, cron_expression=f"{minute} {hour} * * *")


def create_weekly_schedule(scheduler: ReportScheduler, name: str, report_type: str, weekday: int = 0,
                           hour: int = 8, recipients: Optional[List[str]] = None) -> ScheduleConfig:
    return scheduler.create_schedule(name=name, report_type=report_type, template="county_executive",
                                     output_formats=["pdf", "html"], recipients=recipients or [],
                                     schedule_type=ScheduleType.CRON, cron_expression=f"0 {hour} * * {weekday}")


def create_risk_threshold_trigger(scheduler: ReportScheduler, name: str, risk_threshold: float = 0.7,
                                  recipients: Optional[List[str]] = None) -> ScheduleConfig:
    return scheduler.create_schedule(name=name, report_type="crisis_response", template="crisis_response",
                                     output_formats=["pdf", "html"], recipients=recipients or [],
                                     schedule_type=ScheduleType.EVENT, event_triggers=[ReportTrigger.RISK_THRESHOLD],
                                     parameters={"risk_threshold": risk_threshold})
```

---

## 8. Enhanced Briefing Generator Main Class

### 8.1 Main Orchestrator

**File:** `src/briefing/core/generator.py`

```python
"""Enhanced Briefing Generator - Main Orchestrator integrating all capabilities."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
from datetime import datetime
import logging

from config import PROCESSED_DIR, REPORTS_DIR
from ..nlp.summarizer import NLPSummarizer, generate_county_summary
from ..templates.registry import TemplateRegistry, get_registry
from ..formatters.html_formatter import HTMLFormatter
from ..distribution.list_manager import DistributionManager
from ..scheduling.scheduler import ReportScheduler, ScheduleType, ReportTrigger

logger = logging.getLogger(__name__)


class EnhancedBriefingGenerator:
    """
    Enhanced briefing generator with comprehensive automation capabilities.
    
    Features:
    - Multi-format output (PDF, HTML, DOCX, PPTX, JSON, CSV)
    - NLP-powered executive summaries
    - Automated insight extraction
    - Template-based report generation
    - Chart and visualization integration
    - Distribution list management
    - Scheduled report generation
    """
    
    def __init__(self, df: Optional[pd.DataFrame] = None, template_registry: Optional[TemplateRegistry] = None,
                 distribution_manager: Optional[DistributionManager] = None, scheduler: Optional[ReportScheduler] = None):
        # Load data
        if df is None:
            path = PROCESSED_DIR / "county_features.csv"
            if path.exists():
                self.df = pd.read_csv(path, dtype={"fips": str})
            else:
                self.df = None
                logger.warning("County features data not found")
        else:
            self.df = df
        
        # Initialize components
        self.nlp_summarizer = NLPSummarizer()
        self.template_registry = template_registry or get_registry()
        self.distribution_manager = distribution_manager or DistributionManager()
        self.scheduler = scheduler or ReportScheduler()
        self.formatters = {"html": HTMLFormatter()}  # Add more formatters as needed
        
        # Register scheduler callback
        self.scheduler.register_callback("generate_report", self._on_schedule_trigger)
        logger.info("EnhancedBriefingGenerator initialized")
    
    def generate_county_briefing(self, fips: str, output_formats: List[str] = ["pdf"],
                                  template: str = "county_executive", include_nlp_summary: bool = True,
                                  include_charts: bool = True, custom_parameters: Optional[Dict] = None) -> Dict[str, Path]:
        """Generate comprehensive county briefing."""
        if self.df is None:
            raise ValueError("County data not loaded")
        match = self.df[self.df["fips"] == str(fips)]
        if match.empty:
            raise ValueError(f"County {fips} not found")
        county = match.iloc[0]
        county_name = county.get("county_name", "Unknown County")
        logger.info(f"Generating briefing for {county_name} ({fips})")
        
        report_data = self._prepare_report_data(county, include_nlp_summary)
        template_config = self.template_registry.get_template(template)
        if not template_config:
            logger.warning(f"Template '{template}' not found, using default")
            template_config = self.template_registry.get_template("county_executive")
        
        outputs = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for fmt in output_formats:
            if fmt not in self.formatters:
                logger.warning(f"Unsupported format: {fmt}")
                continue
            formatter = self.formatters[fmt]
            output_path = REPORTS_DIR / fmt / f"briefing_{fips}_{timestamp}.{fmt}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                formatter.generate_report(report_data, output_path, template_name=template,
                                          include_charts=include_charts, include_maps=True)
                outputs[fmt] = output_path
                logger.info(f"Generated {fmt.upper()}: {output_path}")
            except Exception as e:
                logger.error(f"Failed to generate {fmt}: {e}")
        return outputs
    
    def generate_state_briefing(self, state_abbrev: str, output_formats: List[str] = ["pdf"],
                                 template: str = "state_executive", top_n_counties: int = 10) -> Dict[str, Path]:
        """Generate state-level briefing."""
        if self.df is None:
            raise ValueError("County data not loaded")
        state_df = self.df[self.df["state"] == state_abbrev]
        if state_df.empty:
            raise ValueError(f"No counties found for state {state_abbrev}")
        logger.info(f"Generating state briefing for {state_abbrev}")
        
        report_data = {
            "title": f"State Briefing: {state_abbrev}", "state": state_abbrev,
            "total_counties": len(state_df), "avg_risk_score": state_df["risk_score"].mean(),
            "high_risk_count": (state_df["risk_level"] == "High").sum(),
            "total_population": state_df["total_population"].sum(), "top_counties": []
        }
        top_counties = state_df.nlargest(top_n_counties, "risk_score")
        for _, county in top_counties.iterrows():
            county_data = self._prepare_report_data(county, include_nlp_summary=True)
            report_data["top_counties"].append(county_data)
        
        outputs = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for fmt in output_formats:
            if fmt not in self.formatters:
                continue
            formatter = self.formatters[fmt]
            output_path = REPORTS_DIR / fmt / f"briefing_state_{state_abbrev}_{timestamp}.{fmt}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                formatter.generate_report(report_data, output_path)
                outputs[fmt] = output_path
                logger.info(f"Generated state {fmt.upper()}: {output_path}")
            except Exception as e:
                logger.error(f"Failed to generate state {fmt}: {e}")
        return outputs
    
    def schedule_report(self, name: str, report_type: str, schedule_type: str, recipients: List[str], **kwargs) -> str:
        """Schedule automated report generation."""
        if schedule_type == "daily":
            schedule = self.scheduler.create_schedule(
                name=name, report_type=report_type, template=kwargs.get("template", "county_executive"),
                output_formats=kwargs.get("formats", ["pdf"]), recipients=recipients,
                schedule_type=ScheduleType.CRON, cron_expression=f"0 {kwargs.get('hour', 8)} * * *")
        elif schedule_type == "weekly":
            schedule = self.scheduler.create_schedule(
                name=name, report_type=report_type, template=kwargs.get("template", "county_executive"),
                output_formats=kwargs.get("formats", ["pdf", "html"]), recipients=recipients,
                schedule_type=ScheduleType.CRON, cron_expression=f"0 {kwargs.get('hour', 8)} * * {kwargs.get('weekday', 1)}")
        elif schedule_type == "event":
            triggers = [ReportTrigger(t) for t in kwargs.get("triggers", ["risk_threshold"])]
            schedule = self.scheduler.create_schedule(
                name=name, report_type=report_type, template=kwargs.get("template", "crisis_response"),
                output_formats=kwargs.get("formats", ["pdf", "html"]), recipients=recipients,
                schedule_type=ScheduleType.EVENT, event_triggers=triggers, parameters=kwargs.get("parameters", {}))
        else:
            raise ValueError(f"Unknown schedule type: {schedule_type}")
        logger.info(f"Created schedule: {schedule.name} ({schedule.id})")
        return schedule.id
    
    def _prepare_report_data(self, county: pd.Series, include_nlp_summary: bool = True) -> Dict[str, Any]:
        """Prepare comprehensive report data for a county."""
        data = {
            "title": f"Executive Briefing: {county.get('county_name', 'Unknown County')}",
            "fips": county.get("fips"), "county_name": county.get("county_name"), "state": county.get("state"),
            "population": county.get("total_population", 0), "risk_score": county.get("risk_score", 0),
            "risk_level": county.get("risk_level", "Unknown"), "vulnerability_index": county.get("vulnerability_index", 0),
            "isolation_index": county.get("isolation_index", 0), "disaster_count": county.get("disaster_count", 0),
            "disaster_acceleration": county.get("disaster_acceleration", 0), "redundancy_score": county.get("redundancy_score", 0),
            "zero_redundancy": county.get("zero_redundancy_flag", 0) == 1, "hospital_count": county.get("hospital_count", 0),
            "poverty_pct": county.get("poverty_pct", 0), "elderly_pct": county.get("elderly_pct", 0),
            "disability_pct": county.get("disability_pct", 0), "compound_risk_count": county.get("compound_risk_count", 0),
            "top_intervention": county.get("top_intervention", ""), "top_intervention_score": county.get("top_intervention_score", 0),
            "generated_at": datetime.now().isoformat()
        }
        if include_nlp_summary:
            summary = self.nlp_summarizer.generate_executive_summary(county)
            data["executive_summary"] = {
                "sections": [{"title": s.title, "content": s.content} for s in summary.sections],
                "key_findings": summary.key_findings, "critical_alerts": summary.critical_alerts,
                "recommendations": summary.recommendations, "confidence_score": summary.confidence_score,
                "reading_time_minutes": summary.reading_time_minutes
            }
        data["metrics"] = [
            {"name": "Risk Score", "value": f"{data['risk_score']:.3f}", "benchmark": "< 0.4",
             "status": "critical" if data['risk_score'] > 0.7 else "elevated" if data['risk_score'] > 0.4 else "normal"},
            {"name": "Disaster Count", "value": str(data['disaster_count']), "benchmark": "< 5",
             "status": "critical" if data['disaster_count'] > 10 else "elevated" if data['disaster_count'] > 5 else "normal"},
            {"name": "Redundancy Score", "value": f"{data['redundancy_score']:.3f}", "benchmark": "> 0.5",
             "status": "critical" if data['redundancy_score'] < 0.2 else "elevated" if data['redundancy_score'] < 0.5 else "normal"},
            {"name": "Poverty %", "value": f"{data['poverty_pct']:.1f}%", "benchmark": "< 15%",
             "status": "critical" if data['poverty_pct'] > 25 else "elevated" if data['poverty_pct'] > 15 else "normal"},
        ]
        return data
    
    def _on_schedule_trigger(self, schedule, event_data):
        """Handle scheduled report generation."""
        logger.info(f"Schedule triggered: {schedule.name}")
        if schedule.report_type == "state_executive":
            for state in schedule.parameters.get("states", ["MO"]):
                self.generate_state_briefing(state, output_formats=schedule.output_formats)
        else:
            counties_to_report = schedule.parameters.get("counties", [])
            if "risk_threshold" in schedule.parameters:
                threshold = schedule.parameters["risk_threshold"]
                high_risk = self.df[self.df["risk_score"] >= threshold]
                counties_to_report = high_risk["fips"].tolist()
            elif not counties_to_report:
                top = self.df.nlargest(10, "risk_score")
                counties_to_report = top["fips"].tolist()
            for fips in counties_to_report:
                try:
                    outputs = self.generate_county_briefing(fips, output_formats=schedule.output_formats, template=schedule.template)
                    for recipient_id in schedule.recipients:
                        recipient = self.distribution_manager.recipients.get(recipient_id)
                        if recipient:
                            self._distribute_report(outputs, recipient)
                except Exception as e:
                    logger.error(f"Failed to generate report for {fips}: {e}")
    
    def _distribute_report(self, outputs: Dict[str, Path], recipient):
        """Distribute report to recipient."""
        logger.info(f"Distributing report to {recipient.name}")
        for fmt, path in outputs.items():
            if fmt in recipient.formats:
                for method in recipient.delivery_methods:
                    if method.value == "email":
                        pass  # Send email with attachment
                    elif method.value == "webhook":
                        pass  # POST to webhook


def create_generator(df=None) -> EnhancedBriefingGenerator:
    """Factory function to create enhanced generator."""
    return EnhancedBriefingGenerator(df=df)


if __name__ == "__main__":
    gen = create_generator()
    if gen.df is not None:
        fips = gen.df.iloc[0]["fips"]
        outputs = gen.generate_county_briefing(fips, output_formats=["html"], include_nlp_summary=True, include_charts=True)
        print(f"Generated reports:")
        for fmt, path in outputs.items():
            print(f"  {fmt.upper()}: {path}")
```

---

## 9. Implementation Priority Order

### Phase 1: Core Enhancements (Weeks 1-2)
1. **HTML Formatter** - Add interactive HTML output
2. **DOCX Formatter** - Add Word document support
3. **Enhanced PDF** - Improve existing PDF with charts
4. **Template System** - Basic template registry

### Phase 2: NLP Integration (Weeks 3-4)
1. **Executive Summarizer** - NLP-powered summaries
2. **Insight Extractor** - Automated key findings
3. **Data Storytelling** - Narrative generation
4. **Sentiment Analysis** - Tone adjustment

### Phase 3: Automation (Weeks 5-6)
1. **Distribution Manager** - Recipient management
2. **Report Scheduler** - Automated scheduling
3. **Event Triggers** - Risk threshold alerts
4. **Webhook Integration** - External notifications

### Phase 4: Advanced Features (Weeks 7-8)
1. **Collaboration System** - Comments and versioning
2. **Chart Integration** - Embedded visualizations
3. **Map Embedding** - Interactive maps
4. **Custom Templates** - User-defined templates

---

## 10. Dependencies

### Required Packages
```
# Core
pandas>=1.5.0
numpy>=1.23.0
jinja2>=3.1.0

# NLP
transformers>=4.30.0
torch>=2.0.0
spacy>=3.6.0

# Output Formats
reportlab>=3.6.0
python-pptx>=0.6.21
python-docx>=0.8.11

# Scheduling
APScheduler>=3.10.0
croniter>=1.4.0

# Visualization
plotly>=5.15.0
folium>=0.14.0

# Email/Distribution
sendgrid>=6.10.0
requests>=2.31.0
```

---

## 11. Summary

This comprehensive briefing generator enhancement provides:

1. **Multi-format output** - PDF, HTML, DOCX, PPTX, JSON, CSV
2. **NLP-powered summaries** - Executive summary generation with transformers
3. **Automated insights** - Key findings and recommendations extraction
4. **Data storytelling** - Narrative generation from vulnerability data
5. **Template system** - Customizable report templates with inheritance
6. **Chart integration** - Embedded visualizations and interactive maps
7. **Distribution management** - Recipient lists and preferences
8. **Scheduled generation** - Cron-based and event-driven automation
9. **Collaboration features** - Comments, versioning, and review workflows

The enhanced system integrates seamlessly with the existing ResilienceAI codebase while providing a modern, extensible platform for automated vulnerability reporting.

---

*Document generated for ResilienceAI claw-autonomous branch analysis*
*Analysis Date: 2026-02-17*
