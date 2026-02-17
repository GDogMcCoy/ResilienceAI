# ResilienceAI Dashboard: Comprehensive AI-Powered Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of the ResilienceAI dashboard codebase and designs AI-powered enhancements for data visualization, manipulation, query, and insight discovery. The current dashboard is built on Streamlit with 9 tabs, supporting 3,222 US counties with 66+ vulnerability features.

---

## 1. Current Dashboard Architecture Analysis

### 1.1 File Structure Overview

```
ResilienceAI/
├── app/
│   └── dashboard.py              # Main dashboard (380 lines, 17.3 KB)
├── src/
│   ├── agent.py                  # 45+ MCP tools for NL querying
│   ├── modern_ui.py              # UI components (322 lines)
│   ├── geo_visualizations.py     # 3D geospatial rendering
│   ├── realtime_pipeline.py      # Live data feeds
│   ├── scenario_simulator.py     # Disaster simulation
│   ├── predictive_models.py      # Risk forecasting
│   ├── network_analysis.py       # County network graphs
│   ├── dashboard_monitor.py      # Activity logging
│   ├── alert_manager.py          # Emergency alerts
│   └── agents/
│       └── orchestrator.py       # Multi-agent coordination
├── data/                         # 3,222 counties dataset
├── models/                       # Trained ML models
└── .streamlit/                   # Streamlit configuration
```

### 1.2 Current Tab Architecture (9 Tabs)

| Tab | Purpose | Key Features |
|-----|---------|--------------|
| 🧠 Strategic Intelligence | Agentic workflow engine | Natural language queries, preset buttons |
| 📍 Missouri Command | State-specific analysis | Scatter plots, county rankings |
| 🗺️ Resilience Map | National geospatial view | 3D landscape visualization |
| 🌪️ Scenario Simulator | Disaster impact modeling | Epicenter selection, impact analysis |
| 📈 Predictive Insights | Future risk trajectories | 10-year predictions, climate scenarios |
| 🌾 Agricultural Risk | Food security analysis | State crop summaries |
| 🚨 Emergency Ops | Command center | Alert subscriptions, intelligence feed |
| 📋 Strategic Roadmap | Policy optimization | Healthcare targets, infrastructure priority |
| 📡 Live Feed | Real-time monitoring | NOAA/USGS streams, activity log |

### 1.3 Current Technology Stack

```python
# Core Framework
streamlit>=1.28.0              # Dashboard framework
streamlit-antd-components      # UI components
streamlit-shadcn-ui            # Modern UI elements
streamlit-lottie               # Animations

# Visualization
plotly>=5.15.0                 # Interactive charts
matplotlib>=3.7.0              # Static plots
seaborn>=0.12.0                # Statistical visualization

# Data Processing
pandas>=2.0.0                  # Data manipulation
numpy>=1.24.0                  # Numerical computing
geopandas>=0.14.0              # Geospatial data

# Machine Learning
scikit-learn>=1.3.0            # ML models
shap<0.46.0                    # Model explainability
joblib>=1.3.0                  # Model serialization

# Vector & NLP
sentence-transformers>=2.2.0   # Text embeddings
faiss-cpu>=1.7.4               # Vector search

# External APIs
earthengine-api>=1.4.0         # Satellite data
requests>=2.31.0               # HTTP clients
```

### 1.4 Current UI Design System (Esoteric Noir)

```python
COLORS = {
    'primary': '#c084fc',      # Purple 400
    'secondary': '#818cf8',    # Indigo 400
    'success': '#4ade80',      # Green 400
    'warning': '#fbbf24',      # Amber 400
    'danger': '#f87171',       # Red 400
    'info': '#38bdf8',         # Sky 400
    'bg_dark': '#0f172a',      # Slate 900
    'bg_card': '#1e293b',      # Slate 800
    'text_main': '#f8fafc',    # Slate 50
    'text_muted': '#94a3b8',   # Slate 400
}
```

---

## 2. Proposed AI-Powered Enhancement Architecture

### 2.1 New Component Architecture

```
ResilienceAI/
├── app/
│   ├── dashboard.py                    # Main entry (refactored)
│   ├── components/
│   │   ├── __init__.py
│   │   ├── ai_chat_interface.py        # Natural language query UI
│   │   ├── chart_recommender.py        # AI-powered chart suggestions
│   │   ├── drill_down_explorer.py      # Interactive drill-down
│   │   ├── voice_interface.py          # Voice commands
│   │   ├── mobile_adapter.py           # Mobile-responsive wrapper
│   │   └── personalized_view.py        # User-specific dashboards
│   ├── websockets/
│   │   ├── __init__.py
│   │   ├── connection_manager.py       # WebSocket handler
│   │   └── realtime_updater.py         # Live data streaming
│   └── ar_vr/
│       ├── __init__.py
│       ├── scene_builder.py            # 3D scene generation
│       └── ar_overlay.py               # AR data overlays
├── src/
│   ├── ai_services/
│   │   ├── __init__.py
│   │   ├── nlp_engine.py               # Query understanding
│   │   ├── chart_llm.py                # Chart recommendation LLM
│   │   ├── insight_generator.py        # Automated insights
│   │   └── voice_processor.py          # Speech-to-text
│   ├── visualizations/
│   │   ├── __init__.py
│   │   ├── plotly_3d.py                # Enhanced 3D charts
│   │   ├── deckgl_maps.py              # Deck.gl integration
│   │   ├── network_graph.py            # D3.js network viz
│   │   └── time_series.py              # Advanced time series
│   └── caching/
│       ├── __init__.py
│       └── distributed_cache.py        # Redis caching layer
└── config/
    ├── dashboard_config.yaml           # Tab configuration
    └── feature_flags.yaml              # Feature toggles
```

### 2.2 Enhanced Tab Architecture (16 Tabs)

| Tab | Enhancement | AI Features |
|-----|-------------|-------------|
| 🧠 Strategic Intelligence | Chat-based NL interface | Intent classification, context awareness |
| 📍 Missouri Command | Drill-down county explorer | Anomaly detection, trend analysis |
| 🗺️ Resilience Map | 3D Deck.gl visualization | AI-powered hotspot detection |
| 🌪️ Scenario Simulator | Real-time simulation engine | Predictive impact modeling |
| 📈 Predictive Insights | Multi-model forecasting | Uncertainty quantification |
| 🌾 Agricultural Risk | Crop yield predictions | Climate impact modeling |
| 🚨 Emergency Ops | Live alert dashboard | Automated alert triage |
| 📋 Strategic Roadmap | ROI optimization engine | Intervention recommendation |
| 📡 Live Feed | WebSocket streaming | Event detection, anomaly alerts |
| 🔍 AI Query Hub | **NEW** | Natural language to visualization |
| 📊 Smart Charts | **NEW** | Auto-chart recommendations |
| 🌐 Network Analysis | **NEW** | County relationship graphs |
| 📱 Mobile Command | **NEW** | Touch-optimized interface |
| 🎙️ Voice Control | **NEW** | Hands-free navigation |
| 🥽 AR Explorer | **NEW** | Spatial data visualization |
| ⚙️ Settings | **NEW** | Personalized preferences |

---

## 3. Detailed Component Design

### 3.1 Natural Language Query Interface (Chat-Based)

**File:** `app/components/ai_chat_interface.py`

```python
"""
AI Chat Interface for Natural Language Data Queries
Enables conversational interaction with ResilienceAI data
"""
import streamlit as st
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import json

@dataclass
class ChatMessage:
    role: str  # 'user', 'assistant', 'system'
    content: str
    visualization: Optional[Dict] = None
    actions: Optional[List[Dict]] = None
    timestamp: Optional[str] = None

class AIChatInterface:
    """
    Conversational AI interface for dashboard queries.
    Supports context-aware multi-turn conversations.
    """
    
    def __init__(
        self,
        agent: 'ResilienceAgent',
        orchestrator: 'AgentOrchestrator',
        on_visualization: Optional[Callable] = None
    ):
        self.agent = agent
        self.orchestrator = orchestrator
        self.on_visualization = on_visualization
        self.context_window = 5  # Messages to retain
        
    def render(self, container: st.container):
        """Render the chat interface in a Streamlit container."""
        
        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'chat_context' not in st.session_state:
            st.session_state.chat_context = {
                'current_county': None,
                'current_state': None,
                'last_visualization': None,
                'filters': {}
            }
        
        # Chat container with custom styling
        with container:
            st.markdown("""
            <style>
            .chat-container {
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border-radius: 16px;
                padding: 20px;
                border: 1px solid rgba(192, 132, 252, 0.2);
                max-height: 600px;
                overflow-y: auto;
            }
            .chat-message-user {
                background: rgba(129, 140, 248, 0.15);
                border-radius: 12px 12px 4px 12px;
                padding: 12px 16px;
                margin: 8px 0;
                margin-left: 40px;
                border-left: 3px solid #818cf8;
            }
            .chat-message-assistant {
                background: rgba(192, 132, 252, 0.1);
                border-radius: 12px 12px 12px 4px;
                padding: 12px 16px;
                margin: 8px 0;
                margin-right: 40px;
                border-left: 3px solid #c084fc;
            }
            .chat-input {
                position: sticky;
                bottom: 0;
                background: #0f172a;
                padding: 10px 0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Display chat history
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for msg in st.session_state.chat_history:
                self._render_message(msg)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Quick action chips
            self._render_quick_actions()
            
            # Input area
            self._render_input_area()
    
    def _render_message(self, msg: ChatMessage):
        """Render a single chat message."""
        css_class = f"chat-message-{msg.role}"
        
        with st.container():
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            
            # Message content
            if msg.role == 'assistant':
                st.markdown(f"🤖 **ResilienceAI**")
            else:
                st.markdown(f"👤 **You**")
            st.markdown(msg.content)
            
            # Render visualization if present
            if msg.visualization:
                self._render_inline_viz(msg.visualization)
            
            # Render action buttons
            if msg.actions:
                cols = st.columns(len(msg.actions))
                for idx, action in enumerate(msg.actions):
                    with cols[idx]:
                        if st.button(
                            action['label'],
                            key=f"action_{action['id']}_{idx}
                        ):
                            self._handle_action(action)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_inline_viz(self, viz_config: Dict):
        """Render an inline visualization within chat."""
        viz_type = viz_config.get('type')
        
        if viz_type == 'choropleth':
            fig = self._create_choropleth(viz_config['data'])
            st.plotly_chart(fig, use_container_width=True, height=300)
        elif viz_type == 'metric_card':
            self._render_metric_cards(viz_config['metrics'])
        elif viz_type == 'chart':
            fig = self._create_chart(viz_config)
            st.plotly_chart(fig, use_container_width=True, height=250)
    
    def _render_quick_actions(self):
        """Render quick action suggestion chips."""
        suggestions = self._get_contextual_suggestions()
        
        st.markdown("**Quick Actions:**")
        cols = st.columns(min(len(suggestions), 4))
        
        for idx, suggestion in enumerate(suggestions[:4]):
            with cols[idx]:
                if st.button(
                    suggestion['icon'] + " " + suggestion['label'],
                    key=f"suggestion_{idx}",
                    use_container_width=True
                ):
                    self._process_query(suggestion['query'])
    
    def _render_input_area(self):
        """Render the chat input area with voice support."""
        st.markdown('<div class="chat-input">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([10, 1, 1])
        
        with col1:
            query = st.text_input(
                "Ask about disaster vulnerability...",
                key="chat_input",
                placeholder="e.g., 'Show me high-risk counties in Missouri'",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("🎤", key="voice_input", help="Voice input"):
                self._activate_voice_input()
        
        with col3:
            if st.button("📎", key="attach_context", help="Attach current view"):
                self._attach_current_context()
        
        if query:
            self._process_query(query)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _process_query(self, query: str):
        """Process user query through AI pipeline."""
        # Add user message to history
        user_msg = ChatMessage(role='user', content=query)
        st.session_state.chat_history.append(user_msg)
        
        # Intent classification
        intent = self._classify_intent(query)
        
        # Route to appropriate handler
        if intent['type'] == 'visualization':
            response = self._handle_viz_query(query, intent)
        elif intent['type'] == 'comparison':
            response = self._handle_comparison_query(query, intent)
        elif intent['type'] == 'prediction':
            response = self._handle_prediction_query(query, intent)
        elif intent['type'] == 'explanation':
            response = self._handle_explanation_query(query, intent)
        else:
            response = self._handle_general_query(query)
        
        # Add assistant response
        assistant_msg = ChatMessage(
            role='assistant',
            content=response['content'],
            visualization=response.get('visualization'),
            actions=response.get('actions')
        )
        st.session_state.chat_history.append(assistant_msg)
        
        # Trigger visualization callback if provided
        if self.on_visualization and 'visualization' in response:
            self.on_visualization(response['visualization'])
        
        st.rerun()
    
    def _classify_intent(self, query: str) -> Dict:
        """Classify user intent using NLP."""
        # Use local agent or orchestrator for intent classification
        intent_patterns = {
            'visualization': ['show', 'display', 'map', 'chart', 'plot', 'visualize'],
            'comparison': ['compare', 'versus', 'vs', 'difference', 'between'],
            'prediction': ['predict', 'forecast', 'future', 'will', 'trend'],
            'explanation': ['why', 'how', 'explain', 'what causes', 'reason'],
            'filtering': ['filter', 'only', 'where', 'with', 'without']
        }
        
        query_lower = query.lower()
        for intent_type, keywords in intent_patterns.items():
            if any(kw in query_lower for kw in keywords):
                return {'type': intent_type, 'confidence': 0.9}
        
        return {'type': 'general', 'confidence': 0.7}
    
    def _get_contextual_suggestions(self) -> List[Dict]:
        """Get context-aware query suggestions."""
        context = st.session_state.chat_context
        suggestions = []
        
        # Based on current view
        if context['current_county']:
            suggestions.append({
                'icon': '📍',
                'label': f"Analyze {context['current_county']}",
                'query': f"Detailed analysis of {context['current_county']}"
            })
        
        # Based on recent queries
        if st.session_state.chat_history:
            last_topic = self._extract_topic(
                st.session_state.chat_history[-1]['content']
            )
            suggestions.append({
                'icon': '🔍',
                'label': f"More on {last_topic}",
                'query': f"Tell me more about {last_topic}"
            })
        
        # Default suggestions
        suggestions.extend([
            {'icon': '🌾', 'label': 'Ag Risk', 'query': 'Agricultural vulnerability assessment'},
            {'icon': '🏥', 'label': 'Healthcare', 'query': 'Counties with zero hospital redundancy'},
            {'icon': '📈', 'label': 'Trends', 'query': 'Where are disasters accelerating?'}
        ])
        
        return suggestions

# Usage in dashboard.py
"""
from components.ai_chat_interface import AIChatInterface

# In tab_intel:
chat_interface = AIChatInterface(
    agent=st.session_state.local_agent,
    orchestrator=st.session_state.orchestrator,
    on_visualization=lambda viz: update_main_visualization(viz)
)

chat_container = st.container()
chat_interface.render(chat_container)
"""
```

### 3.2 AI-Powered Chart Recommendation Engine

**File:** `app/components/chart_recommender.py`

```python
"""
AI-Powered Chart Recommendation System
Automatically suggests optimal visualizations based on data characteristics
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

class ChartRecommender:
    """
    Intelligent chart recommendation engine that analyzes data characteristics
    and suggests optimal visualization types.
    """
    
    CHART_TYPES = {
        'choropleth': {
            'icon': '🗺️',
            'name': 'Choropleth Map',
            'description': 'Geographic data visualization',
            'best_for': ['geographic', 'regional_comparison'],
            'score_weights': {'has_geo': 1.0, 'categorical': 0.7, 'numerical': 0.8}
        },
        'scatter_3d': {
            'icon': '📊',
            'name': '3D Scatter Plot',
            'description': 'Multi-dimensional relationships',
            'best_for': ['correlation', 'clustering', 'outliers'],
            'score_weights': {'numerical': 1.0, 'multi_dim': 0.9}
        },
        'heatmap': {
            'icon': '🔥',
            'name': 'Correlation Heatmap',
            'description': 'Feature relationships',
            'best_for': ['correlation', 'feature_analysis'],
            'score_weights': {'numerical': 1.0, 'multi_feature': 0.9}
        },
        'time_series': {
            'icon': '📈',
            'name': 'Time Series',
            'description': 'Temporal trends and patterns',
            'best_for': ['trends', 'forecasting', 'seasonality'],
            'score_weights': {'temporal': 1.0, 'numerical': 0.9}
        },
        'bar_chart': {
            'icon': '📊',
            'name': 'Bar Chart',
            'description': 'Categorical comparisons',
            'best_for': ['ranking', 'comparison', 'distribution'],
            'score_weights': {'categorical': 1.0, 'numerical': 0.8}
        },
        'network_graph': {
            'icon': '🕸️',
            'name': 'Network Graph',
            'description': 'Relationship visualization',
            'best_for': ['connections', 'hierarchy', 'flow'],
            'score_weights': {'relational': 1.0, 'network': 0.9}
        },
        'treemap': {
            'icon': '🌳',
            'name': 'Treemap',
            'description': 'Hierarchical proportions',
            'best_for': ['hierarchy', 'proportion', 'nested'],
            'score_weights': {'hierarchical': 1.0, 'categorical': 0.8}
        },
        'parallel_coords': {
            'icon': '📐',
            'name': 'Parallel Coordinates',
            'description': 'Multi-dimensional comparison',
            'best_for': ['multi_dim', 'comparison', 'patterns'],
            'score_weights': {'numerical': 1.0, 'multi_feature': 0.9}
        }
    }
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.data_profile = self._analyze_data_profile()
    
    def _analyze_data_profile(self) -> Dict[str, Any]:
        """Analyze data characteristics for recommendation scoring."""
        profile = {
            'row_count': len(self.df),
            'col_count': len(self.df.columns),
            'has_geo': any(col in self.df.columns for col in 
                          ['latitude', 'longitude', 'fips', 'geometry']),
            'has_temporal': any(col in self.df.columns for col in
                               ['date', 'year', 'timestamp', 'disaster_year']),
            'numerical_cols': self.df.select_dtypes(
                include=[np.number]
            ).columns.tolist(),
            'categorical_cols': self.df.select_dtypes(
                include=['object', 'category']
            ).columns.tolist(),
            'correlation_matrix': None,
            'hierarchical_cols': self._detect_hierarchy(),
            'network_cols': self._detect_network_potential()
        }
        
        # Compute correlation if enough numerical columns
        if len(profile['numerical_cols']) >= 2:
            profile['correlation_matrix'] = self.df[
                profile['numerical_cols']
            ].corr()
        
        return profile
    
    def _detect_hierarchy(self) -> List[str]:
        """Detect potential hierarchical relationships in data."""
        hierarchy_candidates = []
        
        # Check for state/county relationship
        if 'state' in self.df.columns and 'county' in self.df.columns:
            hierarchy_candidates.extend(['state', 'county'])
        
        # Check for region/state/county
        if 'region' in self.df.columns:
            hierarchy_candidates.append('region')
        
        return hierarchy_candidates
    
    def _detect_network_potential(self) -> Dict[str, Any]:
        """Detect potential for network visualization."""
        network_info = {'has_potential': False, 'columns': []}
        
        # Check for neighbor relationships
        if 'neighbor_counties' in self.df.columns:
            network_info['has_potential'] = True
            network_info['columns'].append('neighbor_counties')
        
        # Check for connection columns
        connection_cols = [c for c in self.df.columns if 'connect' in c.lower()]
        if connection_cols:
            network_info['has_potential'] = True
            network_info['columns'].extend(connection_cols)
        
        return network_info
    
    def recommend_charts(
        self,
        selected_columns: Optional[List[str]] = None,
        user_intent: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate chart recommendations based on data and user intent.
        
        Args:
            selected_columns: Columns user has selected
            user_intent: Description of what user wants to see
            top_k: Number of recommendations to return
        
        Returns:
            List of recommended chart configurations
        """
        scores = {}
        
        for chart_type, config in self.CHART_TYPES.items():
            score = self._calculate_chart_score(
                chart_type, selected_columns, user_intent
            )
            scores[chart_type] = score
        
        # Sort by score and return top_k
        sorted_charts = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        recommendations = []
        for chart_type, score in sorted_charts[:top_k]:
            rec = {
                'type': chart_type,
                'score': score,
                **self.CHART_TYPES[chart_type],
                'configuration': self._generate_chart_config(chart_type)
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _calculate_chart_score(
        self,
        chart_type: str,
        selected_columns: Optional[List[str]],
        user_intent: Optional[str]
    ) -> float:
        """Calculate recommendation score for a chart type."""
        weights = self.CHART_TYPES[chart_type]['score_weights']
        score = 0.0
        total_weight = 0.0
        
        # Geographic score
        if 'has_geo' in weights:
            score += weights['has_geo'] * (1.0 if self.data_profile['has_geo'] else 0.0)
            total_weight += weights['has_geo']
        
        # Temporal score
        if 'temporal' in weights:
            score += weights['temporal'] * (1.0 if self.data_profile['has_temporal'] else 0.0)
            total_weight += weights['temporal']
        
        # Numerical columns score
        if 'numerical' in weights:
            num_ratio = len(self.data_profile['numerical_cols']) / max(
                len(self.df.columns), 1
            )
            score += weights['numerical'] * num_ratio
            total_weight += weights['numerical']
        
        # Multi-dimensional score
        if 'multi_dim' in weights:
            multi_dim_score = 1.0 if len(self.data_profile['numerical_cols']) >= 3 else 0.5
            score += weights['multi_dim'] * multi_dim_score
            total_weight += weights['multi_dim']
        
        # Intent matching
        if user_intent:
            intent_score = self._match_intent(chart_type, user_intent)
            score += intent_score * 0.3  # Weight for intent
            total_weight += 0.3
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _match_intent(self, chart_type: str, user_intent: str) -> float:
        """Match user intent to chart capabilities."""
        intent_lower = user_intent.lower()
        best_for = self.CHART_TYPES[chart_type]['best_for']
        
        for capability in best_for:
            if capability.replace('_', ' ') in intent_lower:
                return 1.0
        
        return 0.3  # Base score for partial match
    
    def _generate_chart_config(self, chart_type: str) -> Dict[str, Any]:
        """Generate default configuration for chart type."""
        config = {'type': chart_type}
        
        if chart_type == 'choropleth':
            config.update({
                'location_column': 'fips',
                'color_column': 'risk_score',
                'scope': 'usa',
                'colorscale': 'RdYlGn_r'
            })
        elif chart_type == 'scatter_3d':
            config.update({
                'x': 'vulnerability_index',
                'y': 'isolation_index',
                'z': 'risk_score',
                'size': 'total_population',
                'color': 'risk_level'
            })
        elif chart_type == 'heatmap':
            config.update({
                'columns': self.data_profile['numerical_cols'][:10]
            })
        elif chart_type == 'time_series':
            config.update({
                'x': 'year',
                'y': 'disaster_count',
                'color': 'state'
            })
        elif chart_type == 'network_graph':
            config.update({
                'node_column': 'county_name',
                'edge_column': 'neighbor_counties',
                'node_size': 'risk_score',
                'node_color': 'vulnerability_index'
            })
        
        return config
    
    def render_recommendation_panel(self):
        """Render the recommendation panel in Streamlit."""
        st.markdown("### 🤖 AI Chart Recommendations")
        st.caption("Based on your data profile and selection")
        
        # Get recommendations
        recommendations = self.recommend_charts(top_k=4)
        
        # Display as cards
        cols = st.columns(2)
        for idx, rec in enumerate(recommendations):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                        border-radius: 12px;
                        padding: 16px;
                        border: 1px solid rgba(192, 132, 252, 0.2);
                        margin-bottom: 12px;
                    ">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 24px;">{rec['icon']}</span>
                            <div>
                                <strong>{rec['name']}</strong>
                                <div style="color: #94a3b8; font-size: 12px;">
                                    {rec['description']}
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 8px;">
                            <span style="
                                background: rgba(74, 222, 128, 0.2);
                                color: #4ade80;
                                padding: 2px 8px;
                                border-radius: 12px;
                                font-size: 11px;
                            ">
                                {rec['score']:.0%} match
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(
                        f"Create {rec['name']}",
                        key=f"create_chart_{idx}",
                        use_container_width=True
                    ):
                        st.session_state['selected_chart_config'] = rec['configuration']
                        st.session_state['selected_chart_type'] = rec['type']
                        st.rerun()

# Usage in dashboard.py
"""
from components.chart_recommender import ChartRecommender

# In visualization tab:
recommender = ChartRecommender(df)
recommender.render_recommendation_panel()

if 'selected_chart_config' in st.session_state:
    config = st.session_state['selected_chart_config']
    # Render the selected chart
"""
```

### 3.3 Interactive Drill-Down Component

**File:** `app/components/drill_down_explorer.py`

```python
"""
Interactive Drill-Down Explorer
Enables hierarchical exploration from national to county level
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Callable
import pandas as pd

class DrillDownExplorer:
    """
    Multi-level drill-down explorer for hierarchical data analysis.
    Supports: National -> State -> County -> Census Tract navigation.
    """
    
    HIERARCHY_LEVELS = ['national', 'state', 'county', 'tract']
    
    def __init__(
        self,
        df: pd.DataFrame,
        geo_df: Optional[pd.DataFrame] = None,
        on_drill_down: Optional[Callable] = None,
        on_drill_up: Optional[Callable] = None
    ):
        self.df = df
        self.geo_df = geo_df
        self.on_drill_down = on_drill_down
        self.on_drill_up = on_drill_up
        self.breadcrumbs = []
        
    def render(self, container: st.container):
        """Render the drill-down explorer interface."""
        
        # Initialize navigation state
        if 'drill_level' not in st.session_state:
            st.session_state.drill_level = 'national'
        if 'drill_selection' not in st.session_state:
            st.session_state.drill_selection = None
        if 'drill_history' not in st.session_state:
            st.session_state.drill_history = []
        
        with container:
            # Breadcrumb navigation
            self._render_breadcrumbs()
            
            # Current level visualization
            self._render_current_level()
            
            # Detail panel
            self._render_detail_panel()
    
    def _render_breadcrumbs(self):
        """Render breadcrumb navigation trail."""
        st.markdown("""
        <style>
        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px;
            background: rgba(30, 41, 59, 0.5);
            border-radius: 8px;
            margin-bottom: 16px;
        }
        .breadcrumb-item {
            color: #94a3b8;
            cursor: pointer;
        }
        .breadcrumb-item:hover {
            color: #c084fc;
        }
        .breadcrumb-item.active {
            color: #f8fafc;
            font-weight: 600;
        }
        .breadcrumb-separator {
            color: #64748b;
        }
        </style>
        """, unsafe_allow_html=True)
        
        cols = st.columns([1, 8, 1])
        
        with cols[0]:
            if st.button("⬅️ Back", disabled=len(st.session_state.drill_history) == 0):
                self._drill_up()
        
        with cols[1]:
            breadcrumbs = ['🏠 National'] + [
                f"📍 {s['name']}" for s in st.session_state.drill_history
            ]
            st.markdown(
                ' <span class="breadcrumb-separator">›</span> '.join(breadcrumbs),
                unsafe_allow_html=True
            )
        
        with cols[2]:
            if st.button("🔄 Reset"):
                self._reset_navigation()
    
    def _render_current_level(self):
        """Render visualization for current hierarchy level."""
        level = st.session_state.drill_level
        
        if level == 'national':
            self._render_national_view()
        elif level == 'state':
            self._render_state_view()
        elif level == 'county':
            self._render_county_view()
        elif level == 'tract':
            self._render_tract_view()
    
    def _render_national_view(self):
        """Render national-level overview."""
        st.subheader("🗺️ National Resilience Overview")
        
        # Aggregate by state
        state_data = self.df.groupby('state').agg({
            'risk_score': 'mean',
            'vulnerability_index': 'mean',
            'total_population': 'sum',
            'county_name': 'count'
        }).reset_index()
        state_data.columns = ['state', 'avg_risk', 'avg_vulnerability', 
                              'total_pop', 'county_count']
        
        # Choropleth map
        fig = px.choropleth(
            state_data,
            locations='state',
            locationmode='USA-states',
            color='avg_risk',
            scope='usa',
            color_continuous_scale='RdYlGn_r',
            hover_data=['avg_vulnerability', 'total_pop', 'county_count'],
            title='Average Risk Score by State'
        )
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            geo_bgcolor='rgba(0,0,0,0)'
        )
        
        # Make clickable
        selected_state = st.plotly_chart(
            fig, 
            use_container_width=True,
            key='national_map',
            on_select=self._on_state_click
        )
        
        # State ranking table
        st.markdown("### 📊 State Rankings")
        top_states = state_data.nlargest(10, 'avg_risk')
        st.dataframe(
            top_states[['state', 'avg_risk', 'avg_vulnerability', 'county_count']],
            use_container_width=True,
            hide_index=True
        )
    
    def _render_state_view(self):
        """Render state-level detail view."""
        state = st.session_state.drill_selection
        st.subheader(f"📍 {state} - County Analysis")
        
        # Filter to state
        state_df = self.df[self.df['state'] == state]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # County-level choropleth
            fig = px.choropleth(
                state_df,
                geojson=self.geo_df,
                locations='fips',
                color='risk_score',
                color_continuous_scale='RdYlGn_r',
                scope='usa',
                title=f'Risk Score by County in {state}'
            )
            fig.update_geos(fitbounds='locations', visible=False)
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # County metrics
            st.metric("Total Counties", len(state_df))
            st.metric("Avg Risk Score", f"{state_df['risk_score'].mean():.3f}")
            st.metric("High Risk Counties", 
                     len(state_df[state_df['risk_level'] == 'High']))
            
            # County selector
            selected_county = st.selectbox(
                "Select County for Details",
                state_df['county_name'].tolist()
            )
            
            if st.button("🔍 Explore County"):
                self._drill_down('county', selected_county)
    
    def _render_county_view(self):
        """Render county-level detailed view."""
        county = st.session_state.drill_selection
        st.subheader(f"🏘️ {county} - Detailed Analysis")
        
        county_data = self.df[self.df['county_name'] == county].iloc[0]
        
        # Key metrics
        cols = st.columns(4)
        metrics = [
            ('Risk Score', f"{county_data['risk_score']:.3f}", 
             county_data['risk_level']),
            ('Population', f"{county_data['total_population']:,}", None),
            ('Vulnerability', f"{county_data['vulnerability_index']:.3f}", None),
            ('Isolation', f"{county_data['isolation_index']:.3f}", None)
        ]
        
        for col, (label, value, delta) in zip(cols, metrics):
            with col:
                st.metric(label, value, delta)
        
        # Infrastructure analysis
        st.markdown("### 🏥 Infrastructure Analysis")
        infra_cols = st.columns(3)
        
        with infra_cols[0]:
            st.markdown("**Healthcare Access**")
            st.write(f"Nearest Hospital: {county_data.get('nearest_hospital_km', 'N/A')} km")
            st.write(f"Hospital Redundancy: {'✅' if county_data.get('zero_redundancy_flag') == 0 else '❌ None'}")
        
        with infra_cols[1]:
            st.markdown("**Emergency Services**")
            st.write(f"Fire Station: {county_data.get('nearest_fire_station_km', 'N/A')} km")
            st.write(f"EMS: {county_data.get('nearest_ems_km', 'N/A')} km")
        
        with infra_cols[2]:
            st.markdown("**Disaster History**")
            st.write(f"Total Declarations: {county_data.get('total_disaster_declarations', 0)}")
            st.write(f"Recent (2015-2025): {county_data.get('recent_disaster_declarations', 0)}")
        
        # Risk breakdown radar chart
        st.markdown("### 📊 Risk Profile")
        risk_factors = [
            'vulnerability_index',
            'isolation_index', 
            'infrastructure_gap',
            'disaster_frequency',
            'demographic_risk'
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[county_data.get(f, 0.5) for f in risk_factors],
            theta=risk_factors,
            fill='toself',
            name=county
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            title=f'Risk Profile: {county}'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _drill_down(self, level: str, selection: str):
        """Navigate to a deeper level in the hierarchy."""
        st.session_state.drill_history.append({
            'level': st.session_state.drill_level,
            'name': st.session_state.drill_selection or 'National'
        })
        st.session_state.drill_level = level
        st.session_state.drill_selection = selection
        
        if self.on_drill_down:
            self.on_drill_down(level, selection)
        
        st.rerun()
    
    def _drill_up(self):
        """Navigate to parent level in hierarchy."""
        if st.session_state.drill_history:
            parent = st.session_state.drill_history.pop()
            st.session_state.drill_level = parent['level']
            st.session_state.drill_selection = parent['name'] if parent['name'] != 'National' else None
            
            if self.on_drill_up:
                self.on_drill_up(parent['level'], parent['name'])
            
            st.rerun()
    
    def _reset_navigation(self):
        """Reset to national view."""
        st.session_state.drill_level = 'national'
        st.session_state.drill_selection = None
        st.session_state.drill_history = []
        st.rerun()

# Usage in dashboard.py
"""
from components.drill_down_explorer import DrillDownExplorer

# In tab_map:
explorer = DrillDownExplorer(
    df=df,
    geo_df=geo_df,
    on_drill_down=lambda lvl, sel: log_navigation(lvl, sel)
)
explorer.render(st.container())
"""
```

---

## 4. WebSocket Real-Time Updates

### 4.1 WebSocket Connection Manager

**File:** `app/websockets/connection_manager.py`

```python
"""
WebSocket Connection Manager for Real-Time Dashboard Updates
Handles live data streaming from NOAA, USGS, and internal sources
"""
import streamlit as st
import asyncio
import websockets
import json
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import threading
import queue

@dataclass
class DataUpdate:
    source: str
    timestamp: datetime
    data_type: str
    payload: Dict
    priority: str = 'normal'  # 'low', 'normal', 'high', 'critical'

class WebSocketManager:
    """
    Manages WebSocket connections for real-time data streaming.
    Supports multiple data sources with automatic reconnection.
    """
    
    DATA_SOURCES = {
        'noaa_alerts': {
            'url': 'wss://api.weather.gov/alerts/active',
            'description': 'NOAA Weather Alerts',
            'reconnect_interval': 30
        },
        'usgs_earthquakes': {
            'url': 'wss://earthquake.usgs.gov/streams/websocket',
            'description': 'USGS Earthquake Feed',
            'reconnect_interval': 60
        },
        'internal_metrics': {
            'url': 'ws://localhost:8765/metrics',
            'description': 'Internal System Metrics',
            'reconnect_interval': 10
        }
    }
    
    def __init__(self):
        self.connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.update_queue: queue.Queue = queue.Queue()
        self.subscribers: Dict[str, List[Callable]] = {}
        self.is_running = False
        self._lock = threading.Lock()
    
    def subscribe(self, source: str, callback: Callable):
        """Subscribe to updates from a data source."""
        with self._lock:
            if source not in self.subscribers:
                self.subscribers[source] = []
            self.subscribers[source].append(callback)
    
    def unsubscribe(self, source: str, callback: Callable):
        """Unsubscribe from a data source."""
        with self._lock:
            if source in self.subscribers:
                self.subscribers[source].remove(callback)
    
    async def connect(self, source_name: str):
        """Establish WebSocket connection to a data source."""
        if source_name not in self.DATA_SOURCES:
            raise ValueError(f"Unknown data source: {source_name}")
        
        config = self.DATA_SOURCES[source_name]
        reconnect_interval = config['reconnect_interval']
        
        while self.is_running:
            try:
                async with websockets.connect(config['url']) as ws:
                    self.connections[source_name] = ws
                    st.toast(f"Connected to {config['description']}")
                    
                    async for message in ws:
                        if not self.is_running:
                            break
                        
                        try:
                            data = json.loads(message)
                            update = DataUpdate(
                                source=source_name,
                                timestamp=datetime.now(),
                                data_type=data.get('type', 'unknown'),
                                payload=data,
                                priority=data.get('priority', 'normal')
                            )
                            self.update_queue.put(update)
                            self._notify_subscribers(update)
                        except json.JSONDecodeError:
                            continue
                            
            except websockets.exceptions.ConnectionClosed:
                st.warning(f"{source_name} connection closed. Reconnecting...")
            except Exception as e:
                st.error(f"{source_name} error: {str(e)}")
            
            await asyncio.sleep(reconnect_interval)
    
    def _notify_subscribers(self, update: DataUpdate):
        """Notify all subscribers of a new update."""
        with self._lock:
            callbacks = self.subscribers.get(update.source, [])
        
        for callback in callbacks:
            try:
                callback(update)
            except Exception as e:
                st.error(f"Subscriber error: {str(e)}")
    
    def start(self):
        """Start all WebSocket connections."""
        self.is_running = True
        
        # Start connections in background threads
        for source_name in self.DATA_SOURCES:
            thread = threading.Thread(
                target=self._run_async_connection,
                args=(source_name,),
                daemon=True
            )
            thread.start()
    
    def stop(self):
        """Stop all WebSocket connections."""
        self.is_running = False
        for ws in self.connections.values():
            asyncio.create_task(ws.close())
    
    def _run_async_connection(self, source_name: str):
        """Run async connection in a thread."""
        asyncio.run(self.connect(source_name))

# Streamlit-specific WebSocket component
class StreamlitRealtimeFeed:
    """
    Streamlit component for displaying real-time WebSocket data.
    """
    
    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self.received_updates: List[DataUpdate] = []
        
    def render(self):
        """Render the real-time feed component."""
        st.markdown("### 📡 Live Data Feed")
        
        # Connection status
        cols = st.columns(len(self.ws_manager.DATA_SOURCES))
        for idx, (source, config) in enumerate(self.ws_manager.DATA_SOURCES.items()):
            with cols[idx]:
                is_connected = source in self.ws_manager.connections
                status_color = '🟢' if is_connected else '🔴'
                st.markdown(f"{status_color} **{config['description']}**")
        
        # Subscribe to updates
        self.ws_manager.subscribe('noaa_alerts', self._on_noaa_update)
        self.ws_manager.subscribe('usgs_earthquakes', self._on_usgs_update)
        
        # Display recent updates
        st.markdown("#### Recent Events")
        
        # Use st.empty() for dynamic updates
        updates_container = st.empty()
        
        with updates_container.container():
            for update in self.received_updates[-10:]:
                self._render_update_card(update)
    
    def _render_update_card(self, update: DataUpdate):
        """Render a single update card."""
        priority_colors = {
            'critical': '#ef4444',
            'high': '#f97316',
            'normal': '#3b82f6',
            'low': '#6b7280'
        }
        
        color = priority_colors.get(update.priority, '#6b7280')
        
        st.markdown(f"""
        <div style="
            background: rgba(30, 41, 59, 0.8);
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
        ">
            <div style="display: flex; justify-content: space-between;">
                <strong>{update.data_type}</strong>
                <span style="color: #94a3b8; font-size: 12px;">
                    {update.timestamp.strftime('%H:%M:%S')}
                </span>
            </div>
            <div style="color: #cbd5e1; font-size: 14px; margin-top: 4px;">
                {str(update.payload)[:100]}...
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _on_noaa_update(self, update: DataUpdate):
        """Handle NOAA alert updates."""
        self.received_updates.append(update)
        # Trigger Streamlit rerun for live updates
        st.session_state['last_noaa_update'] = update.timestamp
    
    def _on_usgs_update(self, update: DataUpdate):
        """Handle USGS earthquake updates."""
        self.received_updates.append(update)
        st.session_state['last_usgs_update'] = update.timestamp

# Usage in dashboard.py
"""
from websockets.connection_manager import WebSocketManager, StreamlitRealtimeFeed

# Initialize in session state
if 'ws_manager' not in st.session_state:
    st.session_state.ws_manager = WebSocketManager()
    st.session_state.ws_manager.start()

# In tab_live:
realtime_feed = StreamlitRealtimeFeed(st.session_state.ws_manager)
realtime_feed.render()
"""
```

---

## 5. 3D Geospatial Visualizations

### 5.1 Enhanced 3D Visualization Component

**File:** `src/visualizations/plotly_3d.py`

```python
"""
Enhanced 3D Geospatial Visualizations
Advanced 3D charts using Plotly and Deck.gl integration
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

class Geospatial3DVisualizer:
    """
    Advanced 3D geospatial visualization with multiple rendering modes.
    Supports: 3D scatter, surface, mesh, and Deck.gl integration.
    """
    
    def __init__(self, df: pd.DataFrame, geo_df: Optional[pd.DataFrame] = None):
        self.df = df
        self.geo_df = geo_df
        
    def create_3d_risk_landscape(
        self,
        x_col: str = 'longitude',
        y_col: str = 'latitude',
        z_col: str = 'risk_score',
        color_col: str = 'vulnerability_index',
        size_col: str = 'total_population',
        hover_cols: Optional[List[str]] = None
    ) -> go.Figure:
        """
        Create an interactive 3D risk landscape visualization.
        """
        hover_data = hover_cols or ['county_name', 'state', 'risk_level']
        
        fig = go.Figure(data=[go.Scatter3d(
            x=self.df[x_col],
            y=self.df[y_col],
            z=self.df[z_col],
            mode='markers',
            marker=dict(
                size=np.log(self.df[size_col] + 1) * 2,
                color=self.df[color_col],
                colorscale='RdYlGn_r',
                opacity=0.8,
                colorbar=dict(title=color_col.replace('_', ' ').title()),
                line=dict(width=0.5, color='rgba(0,0,0,0.3)')
            ),
            text=self.df.apply(
                lambda row: '<br>'.join(
                    [f"{col}: {row[col]}" for col in hover_data]
                ),
                axis=1
            ),
            hoverinfo='text',
            name='Risk Landscape'
        )])
        
        fig.update_layout(
            title='3D Risk Landscape Visualization',
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title='Risk Score',
                bgcolor='rgba(15, 23, 42, 0.9)',
                xaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)'),
                yaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)'),
                zaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)'),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.0),
                    up=dict(x=0, y=0, z=1)
                )
            ),
            paper_bgcolor='rgba(15, 23, 42, 1)',
            font=dict(color='#f8fafc'),
            margin=dict(l=0, r=0, t=40, b=0),
            height=700
        )
        
        return fig
    
    def create_3d_surface(
        self,
        value_col: str = 'risk_score',
        grid_resolution: int = 50
    ) -> go.Figure:
        """
        Create a 3D surface visualization of risk across geography.
        """
        from scipy.interpolate import griddata
        
        # Create grid
        x = self.df['longitude'].values
        y = self.df['latitude'].values
        z = self.df[value_col].values
        
        xi = np.linspace(x.min(), x.max(), grid_resolution)
        yi = np.linspace(y.min(), y.max(), grid_resolution)
        xi, yi = np.meshgrid(xi, yi)
        
        # Interpolate
        zi = griddata((x, y), z, (xi, yi), method='cubic')
        
        fig = go.Figure(data=[go.Surface(
            x=xi,
            y=yi,
            z=zi,
            colorscale='RdYlGn_r',
            colorbar=dict(title=value_col.replace('_', ' ').title()),
            contours=dict(
                z=dict(show=True, usecolormap=True, project_z=True)
            ),
            lighting=dict(
                ambient=0.6,
                diffuse=0.8,
                roughness=0.4,
                specular=0.5
            )
        )])
        
        fig.update_layout(
            title=f'3D Risk Surface: {value_col.replace("_", " ").title()}',
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title=value_col.replace('_', ' ').title(),
                bgcolor='rgba(15, 23, 42, 0.9)',
                aspectratio=dict(x=1, y=1, z=0.5)
            ),
            paper_bgcolor='rgba(15, 23, 42, 1)',
            font=dict(color='#f8fafc'),
            height=700
        )
        
        return fig
    
    def create_network_3d(
        self,
        node_col: str = 'county_name',
        edge_connections: Optional[List[Tuple[str, str]]] = None,
        node_size_col: str = 'risk_score',
        node_color_col: str = 'vulnerability_index'
    ) -> go.Figure:
        """
        Create a 3D network graph visualization.
        """
        # Get node positions (using coordinates if available)
        if 'longitude' in self.df.columns and 'latitude' in self.df.columns:
            pos = {
                row[node_col]: (row['longitude'], row['latitude'], row[node_size_col])
                for _, row in self.df.iterrows()
            }
        else:
            # Generate positions using spring layout
            from sklearn.manifold import TSNE
            coords = TSNE(n_components=3, random_state=42).fit_transform(
                self.df[[node_size_col, node_color_col]].values
            )
            pos = {
                row[node_col]: tuple(coords[idx])
                for idx, row in self.df.iterrows()
            }
        
        # Create edge traces
        edge_traces = []
        if edge_connections:
            for edge in edge_connections:
                if edge[0] in pos and edge[1] in pos:
                    x = [pos[edge[0]][0], pos[edge[1]][0], None]
                    y = [pos[edge[0]][1], pos[edge[1]][1], None]
                    z = [pos[edge[0]][2], pos[edge[1]][2], None]
                    
                    edge_traces.append(go.Scatter3d(
                        x=x, y=y, z=z,
                        mode='lines',
                        line=dict(color='rgba(192, 132, 252, 0.3)', width=1),
                        hoverinfo='none'
                    ))
        
        # Create node trace
        node_trace = go.Scatter3d(
            x=[pos[node][0] for node in pos],
            y=[pos[node][1] for node in pos],
            z=[pos[node][2] for node in pos],
            mode='markers',
            marker=dict(
                size=self.df[node_size_col] * 20,
                color=self.df[node_color_col],
                colorscale='RdYlGn_r',
                colorbar=dict(title=node_color_col.replace('_', ' ').title()),
                line=dict(width=1, color='rgba(255,255,255,0.5)')
            ),
            text=self.df[node_col],
            hoverinfo='text'
        )
        
        fig = go.Figure(data=edge_traces + [node_trace])
        
        fig.update_layout(
            title='3D County Network Visualization',
            scene=dict(
                bgcolor='rgba(15, 23, 42, 0.9)',
                xaxis=dict(showgrid=False, showticklabels=False, title=''),
                yaxis=dict(showgrid=False, showticklabels=False, title=''),
                zaxis=dict(showgrid=False, showticklabels=False, title='Risk')
            ),
            paper_bgcolor='rgba(15, 23, 42, 1)',
            font=dict(color='#f8fafc'),
            showlegend=False,
            height=700
        )
        
        return fig
    
    def create_time_series_3d(
        self,
        time_col: str = 'year',
        value_cols: List[str] = ['risk_score', 'vulnerability_index'],
        group_col: str = 'state'
    ) -> go.Figure:
        """
        Create a 3D time series ribbon visualization.
        """
        # Aggregate by time and group
        agg_df = self.df.groupby([time_col, group_col])[value_cols].mean().reset_index()
        
        fig = go.Figure()
        
        for idx, group in enumerate(agg_df[group_col].unique()):
            group_df = agg_df[agg_df[group_col] == group]
            
            fig.add_trace(go.Scatter3d(
                x=group_df[time_col],
                y=[idx] * len(group_df),
                z=group_df[value_cols[0]],
                mode='lines',
                name=group,
                line=dict(width=4),
                surfaceaxis=1,
                surfacecolor=group_df[value_cols[1]] if len(value_cols) > 1 else None
            ))
        
        fig.update_layout(
            title=f'3D Time Series: {value_cols[0].replace("_", " ").title()}',
            scene=dict(
                xaxis_title='Time',
                yaxis_title='Group',
                zaxis_title=value_cols[0].replace('_', ' ').title(),
                bgcolor='rgba(15, 23, 42, 0.9)'
            ),
            paper_bgcolor='rgba(15, 23, 42, 1)',
            font=dict(color='#f8fafc'),
            height=700
        )
        
        return fig

# Usage in dashboard.py
"""
from visualizations.plotly_3d import Geospatial3DVisualizer

viz_3d = Geospatial3DVisualizer(df)

# In tab_map:
tab_3d_scatter, tab_3d_surface, tab_3d_network = st.tabs([
    '3D Scatter', '3D Surface', '3D Network'
])

with tab_3d_scatter:
    fig = viz_3d.create_3d_risk_landscape()
    st.plotly_chart(fig, use_container_width=True)

with tab_3d_surface:
    fig = viz_3d.create_3d_surface()
    st.plotly_chart(fig, use_container_width=True)
"""
```

---

## 6. Mobile-Responsive Design

### 6.1 Mobile Adapter Component

**File:** `app/components/mobile_adapter.py`

```python
"""
Mobile-Responsive Adapter for ResilienceAI Dashboard
Automatically adapts layout and interactions for mobile devices
"""
import streamlit as st
from typing import Dict, List, Callable, Optional
import re

class MobileAdapter:
    """
    Detects mobile devices and adapts dashboard layout accordingly.
    Provides touch-optimized controls and simplified navigation.
    """
    
    MOBILE_BREAKPOINT = 768  # pixels
    
    # Simplified tab structure for mobile
    MOBILE_TABS = {
        '📊 Overview': ['metrics', 'alerts', 'quick_stats'],
        '🗺️ Map': ['choropleth', 'drill_down'],
        '🔍 Search': ['ai_chat', 'county_finder'],
        '⚙️ Settings': ['preferences', 'filters']
    }
    
    def __init__(self):
        self.is_mobile = self._detect_mobile()
        self.screen_width = self._get_screen_width()
    
    def _detect_mobile(self) -> bool:
        """Detect if user is on a mobile device."""
        # Check user agent via JavaScript injection
        user_agent = st.browser_user_agent if hasattr(st, 'browser_user_agent') else ''
        
        mobile_patterns = [
            r'Android', r'iPhone', r'iPad', r'iPod', r'Windows Phone',
            r'BlackBerry', r'Mobile', r'Tablet'
        ]
        
        return any(re.search(pattern, user_agent) for pattern in mobile_patterns)
    
    def _get_screen_width(self) -> int:
        """Get screen width via JavaScript."""
        # Use st.components.v1.html to get screen dimensions
        return st.session_state.get('screen_width', 1200)
    
    def adapt_layout(self, content_renderer: Callable):
        """
        Wrap content with mobile adaptations.
        """
        if self.is_mobile or self.screen_width < self.MOBILE_BREAKPOINT:
            return self._render_mobile_layout(content_renderer)
        else:
            return self._render_desktop_layout(content_renderer)
    
    def _render_mobile_layout(self, content_renderer: Callable):
        """Render mobile-optimized layout."""
        # Inject mobile CSS
        st.markdown("""
        <style>
        @media (max-width: 768px) {
            .stApp {
                font-size: 14px;
            }
            .stTabs [data-baseweb="tab-list"] {
                flex-wrap: wrap;
            }
            .stTabs [data-baseweb="tab"] {
                padding: 8px 12px !important;
                font-size: 12px !important;
            }
            .stMetric {
                padding: 8px !important;
            }
            .stMetric label {
                font-size: 11px !important;
            }
            .stMetric .css-1xarl3l {
                font-size: 18px !important;
            }
            .stButton > button {
                width: 100%;
                padding: 12px;
                font-size: 14px;
            }
            .stSelectbox > div > div {
                min-height: 44px;
            }
            /* Bottom navigation */
            .mobile-nav {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: #1e293b;
                display: flex;
                justify-content: space-around;
                padding: 10px 0;
                border-top: 1px solid rgba(192, 132, 252, 0.3);
                z-index: 1000;
            }
            .mobile-nav-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                color: #94a3b8;
                font-size: 11px;
                padding: 5px 15px;
            }
            .mobile-nav-item.active {
                color: #c084fc;
            }
            .mobile-nav-item span {
                font-size: 20px;
                margin-bottom: 2px;
            }
            /* Add padding for bottom nav */
            .main-content {
                padding-bottom: 70px;
            }
            /* Touch-friendly cards */
            .touch-card {
                min-height: 60px;
                padding: 16px;
                margin: 8px 0;
                border-radius: 12px;
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(192, 132, 252, 0.2);
                touch-action: manipulation;
            }
            /* Swipe indicators */
            .swipe-hint {
                text-align: center;
                color: #64748b;
                font-size: 12px;
                padding: 8px;
            }
        }
        </style>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        """, unsafe_allow_html=True)
        
        # Render simplified mobile navigation
        self._render_mobile_bottom_nav()
        
        # Render content with mobile wrapper
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        content_renderer(mobile=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_mobile_bottom_nav(self):
        """Render bottom navigation bar for mobile."""
        current_tab = st.session_state.get('mobile_tab', '📊 Overview')
        
        nav_html = '<div class="mobile-nav">'
        for tab_name in self.MOBILE_TABS.keys():
            active_class = 'active' if tab_name == current_tab else ''
            nav_html += f'''
            <div class="mobile-nav-item {active_class}" onclick="
                window.parent.postMessage({{type: 'streamlit:setComponentValue', 
                value: '{tab_name}'}}, '*');
            ">
                <span>{tab_name[0]}</span>
                {tab_name[2:]}
            </div>
            '''
        nav_html += '</div>'
        
        st.markdown(nav_html, unsafe_allow_html=True)
    
    def _render_desktop_layout(self, content_renderer: Callable):
        """Render standard desktop layout."""
        content_renderer(mobile=False)
    
    def adapt_chart_config(self, config: Dict, is_mobile: bool) -> Dict:
        """Adapt chart configuration for mobile screens."""
        if not is_mobile:
            return config
        
        mobile_config = config.copy()
        
        # Reduce chart height
        if 'height' in mobile_config:
            mobile_config['height'] = min(mobile_config['height'], 400)
        
        # Simplify hover info
        mobile_config['hovermode'] = 'closest'
        
        # Reduce margins
        mobile_config['margin'] = dict(l=30, r=30, t=40, b=30)
        
        # Disable complex interactions
        mobile_config['dragmode'] = False
        
        return mobile_config
    
    def render_touch_card(
        self,
        title: str,
        value: str,
        subtitle: Optional[str] = None,
        on_tap: Optional[Callable] = None,
        icon: Optional[str] = None
    ):
        """Render a touch-friendly metric card."""
        card_html = f'''
        <div class="touch-card" {'onclick="handleTap()"' if on_tap else ''}>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: #94a3b8; font-size: 12px;">{title}</div>
                    <div style="color: #f8fafc; font-size: 24px; font-weight: 600;">
                        {icon + ' ' if icon else ''}{value}
                    </div>
                    {f'<div style="color: #64748b; font-size: 11px;">{subtitle}</div>' if subtitle else ''}
                </div>
                <div style="color: #c084fc; font-size: 20px;">›</div>
            </div>
        </div>
        '''
        st.markdown(card_html, unsafe_allow_html=True)
        
        if on_tap:
            if st.button(f"Tap {title}", key=f"tap_{title}", visible=False):
                on_tap()

# Usage in dashboard.py
"""
from components.mobile_adapter import MobileAdapter

mobile_adapter = MobileAdapter()

def render_dashboard_content(mobile: bool):
    if mobile:
        # Simplified mobile layout
        st.metric("Active Alerts", "5")
        st.metric("High Risk Counties", "127")
    else:
        # Full desktop layout
        # ... existing tab code ...

mobile_adapter.adapt_layout(render_dashboard_content)
"""
```

---

## 7. Voice Interface Integration

### 7.1 Voice Command Processor

**File:** `src/ai_services/voice_processor.py`

```python
"""
Voice Interface for Hands-Free Dashboard Control
Speech-to-text with natural language command processing
"""
import streamlit as st
from typing import Dict, List, Optional, Callable
import json

class VoiceInterface:
    """
    Voice-controlled interface for dashboard navigation and queries.
    Supports continuous listening and command recognition.
    """
    
    VOICE_COMMANDS = {
        'navigation': {
            'patterns': [
                r'(go to|show|open|switch to)\s+(\w+)\s+(tab|view)',
                r'(navigate to|take me to)\s+(\w+)'
            ],
            'handler': '_handle_navigation'
        },
        'filtering': {
            'patterns': [
                r'(show|filter|only)\s+(high risk|medium risk|low risk)',
                r'(filter by|show)\s+(state|county)\s+(\w+)',
                r'(clear|reset)\s+(filters|filter)'
            ],
            'handler': '_handle_filtering'
        },
        'query': {
            'patterns': [
                r'(what is|tell me|show me|find)\s+(.+)',
                r'(compare|analyze)\s+(.+)',
                r'(predict|forecast)\s+(.+)'
            ],
            'handler': '_handle_query'
        },
        'visualization': {
            'patterns': [
                r'(zoom in|zoom out|pan|rotate)',
                r'(change|switch)\s+(chart|map|view)\s+to\s+(\w+)',
                r'(show|hide)\s+(labels|legend|grid)'
            ],
            'handler': '_handle_visualization'
        },
        'emergency': {
            'patterns': [
                r'(emergency|alert|critical|urgent)',
                r'(show|display)\s+(alerts|warnings)'
            ],
            'handler': '_handle_emergency'
        }
    }
    
    def __init__(
        self,
        agent: 'ResilienceAgent',
        on_command: Optional[Callable] = None
    ):
        self.agent = agent
        self.on_command = on_command
        self.is_listening = False
        self.command_history = []
    
    def render_voice_button(self):
        """Render voice activation button with visual feedback."""
        col1, col2 = st.columns([1, 5])
        
        with col1:
            # Animated microphone button
            button_style = """
            <style>
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(192, 132, 252, 0.7); }
                70% { box-shadow: 0 0 0 15px rgba(192, 132, 252, 0); }
                100% { box-shadow: 0 0 0 0 rgba(192, 132, 252, 0); }
            }
            .voice-button {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: linear-gradient(135deg, #c084fc 0%, #818cf8 100%);
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .voice-button:hover {
                transform: scale(1.1);
            }
            .voice-button.listening {
                animation: pulse 1.5s infinite;
            }
            </style>
            """
            st.markdown(button_style, unsafe_allow_html=True)
            
            if st.button(
                "🎤",
                key="voice_toggle",
                help="Click to start voice command"
            ):
                self._toggle_listening()
        
        with col2:
            if self.is_listening:
                st.markdown("""
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    color: #c084fc;
                    animation: fadeIn 0.3s ease;
                ">
                    <span class="listening-indicator">●</span>
                    <span>Listening... Say a command like "Show high risk counties"</span>
                </div>
                <style>
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                .listening-indicator {
                    animation: blink 1s infinite;
                }
                @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
                </style>
                """, unsafe_allow_html=True)
                
                # Start voice recognition
                self._start_voice_recognition()
    
    def _toggle_listening(self):
        """Toggle voice listening state."""
        self.is_listening = not self.is_listening
        if self.is_listening:
            st.session_state['voice_listening'] = True
        else:
            st.session_state['voice_listening'] = False
    
    def _start_voice_recognition(self):
        """Initialize browser-based speech recognition."""
        # Inject Web Speech API JavaScript
        speech_js = """
        <script>
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                // Send to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: transcript
                }, '*');
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
            };
            
            recognition.start();
        } else {
            alert('Voice recognition not supported in this browser');
        }
        </script>
        """
        st.components.v1.html(speech_js, height=0)
    
    def process_voice_input(self, transcript: str) -> Dict:
        """Process voice transcript and execute command."""
        import re
        
        # Log command
        self.command_history.append({
            'transcript': transcript,
            'timestamp': pd.Timestamp.now()
        })
        
        # Classify command type
        for command_type, config in self.VOICE_COMMANDS.items():
            for pattern in config['patterns']:
                match = re.search(pattern, transcript.lower())
                if match:
                    handler = getattr(self, config['handler'])
                    return handler(match, transcript)
        
        # Default: treat as query
        return self._handle_query(None, transcript)
    
    def _handle_navigation(self, match, transcript: str) -> Dict:
        """Handle navigation commands."""
        # Extract destination
        destination = match.group(2) if match else None
        
        tab_mapping = {
            'strategic': 'tab_intel',
            'missouri': 'tab_mo',
            'map': 'tab_map',
            'simulator': 'tab_sim',
            'predictive': 'tab_pred',
            'agricultural': 'tab_ag',
            'emergency': 'tab_ops',
            'roadmap': 'tab_road',
            'live': 'tab_live'
        }
        
        if destination:
            for key, tab_id in tab_mapping.items():
                if key in destination.lower():
                    return {
                        'type': 'navigation',
                        'action': 'switch_tab',
                        'target': tab_id,
                        'message': f"Switching to {destination} view"
                    }
        
        return {
            'type': 'navigation',
            'action': 'unknown',
            'message': "I didn't understand which tab to open"
        }
    
    def _handle_filtering(self, match, transcript: str) -> Dict:
        """Handle filtering commands."""
        # Extract filter criteria
        if 'high risk' in transcript.lower():
            return {
                'type': 'filtering',
                'action': 'apply_filter',
                'filter': {'risk_level': 'High'},
                'message': 'Filtering to high risk counties'
            }
        elif 'clear' in transcript.lower() or 'reset' in transcript.lower():
            return {
                'type': 'filtering',
                'action': 'clear_filters',
                'message': 'Clearing all filters'
            }
        
        return {
            'type': 'filtering',
            'action': 'unknown',
            'message': 'Filter command not recognized'
        }
    
    def _handle_query(self, match, transcript: str) -> Dict:
        """Handle natural language queries."""
        # Pass to agent for processing
        response = self.agent.process_natural_language_query(transcript)
        
        return {
            'type': 'query',
            'action': 'process_nl',
            'query': transcript,
            'response': response,
            'message': response.get('summary', 'Query processed')
        }
    
    def _handle_visualization(self, match, transcript: str) -> Dict:
        """Handle visualization control commands."""
        if 'zoom in' in transcript.lower():
            return {'type': 'visualization', 'action': 'zoom_in'}
        elif 'zoom out' in transcript.lower():
            return {'type': 'visualization', 'action': 'zoom_out'}
        elif 'chart' in transcript.lower() or 'map' in transcript.lower():
            # Extract chart type
            chart_types = ['scatter', 'bar', 'line', 'choropleth', 'heatmap']
            for ct in chart_types:
                if ct in transcript.lower():
                    return {
                        'type': 'visualization',
                        'action': 'change_chart',
                        'chart_type': ct
                    }
        
        return {'type': 'visualization', 'action': 'unknown'}
    
    def _handle_emergency(self, match, transcript: str) -> Dict:
        """Handle emergency-related commands."""
        return {
            'type': 'emergency',
            'action': 'show_alerts',
            'message': 'Displaying active emergency alerts'
        }

# Usage in dashboard.py
"""
from ai_services.voice_processor import VoiceInterface

voice_interface = VoiceInterface(agent=st.session_state.local_agent)

# In sidebar or header:
voice_interface.render_voice_button()

# Check for voice input
if 'voice_transcript' in st.session_state:
    result = voice_interface.process_voice_input(
        st.session_state.voice_transcript
    )
    st.success(result['message'])
"""
```

---

## 8. AR/VR Data Exploration

### 8.1 AR Scene Builder

**File:** `app/ar_vr/scene_builder.py`

```python
"""
AR/VR Scene Builder for Spatial Data Exploration
Generates 3D scenes for AR/VR data visualization
"""
import streamlit as st
from typing import Dict, List, Optional, Tuple
import json
import numpy as np

class ARSceneBuilder:
    """
    Builds AR/VR-compatible 3D scenes for immersive data exploration.
    Supports WebXR, ARCore, and ARKit.
    """
    
    def __init__(self, df):
        self.df = df
        self.scene_objects = []
        
    def create_risk_terrain(self, scale: float = 0.001) -> Dict:
        """
        Create a 3D terrain visualization of risk scores.
        Returns A-Frame compatible scene description.
        """
        # Normalize coordinates
        lats = self.df['latitude'].values
        lons = self.df['longitude'].values
        risks = self.df['risk_score'].values
        
        # Center coordinates
        lat_center = (lats.min() + lats.max()) / 2
        lon_center = (lons.min() + lons.max()) / 2
        
        # Create terrain mesh
        entities = []
        
        for idx, row in self.df.iterrows():
            # Calculate position relative to center
            x = (row['longitude'] - lon_center) / scale
            z = (row['latitude'] - lat_center) / scale
            y = row['risk_score'] * 10  # Height based on risk
            
            # Color based on risk level
            color = self._risk_to_color(row['risk_score'])
            
            # Create entity
            entity = {
                'type': 'a-cylinder',
                'attributes': {
                    'position': f'{x} {y/2} {z}',
                    'height': y,
                    'radius': 0.5,
                    'color': color,
                    'opacity': 0.8,
                    'class': 'clickable',
                    'data-county': row['county_name'],
                    'data-risk': row['risk_score']
                }
            }
            entities.append(entity)
        
        return {
            'scene': {
                'sky': {'color': '#0f172a'},
                'lighting': {
                    'ambient': {'color': '#ffffff', 'intensity': 0.5},
                    'directional': {'color': '#ffffff', 'intensity': 0.8}
                },
                'camera': {
                    'position': f'0 {risks.max() * 15} {max(x, z) * 2}',
                    'lookAt': '0 0 0'
                },
                'entities': entities
            }
        }
    
    def _risk_to_color(self, risk: float) -> str:
        """Convert risk score to color."""
        if risk >= 0.7:
            return '#ef4444'  # Red
        elif risk >= 0.4:
            return '#fbbf24'  # Amber
        else:
            return '#4ade80'  # Green
    
    def create_network_graph_3d(self) -> Dict:
        """Create a 3D network graph for county relationships."""
        # Use existing network analysis
        from network_analysis import build_county_network
        
        G = build_county_network(self.df)
        
        # Position nodes using 3D force-directed layout
        pos = self._compute_3d_layout(G)
        
        entities = []
        
        # Create nodes
        for node, position in pos.items():
            node_data = self.df[self.df['county_name'] == node].iloc[0]
            
            entity = {
                'type': 'a-sphere',
                'attributes': {
                    'position': f'{position[0]} {position[1]} {position[2]}',
                    'radius': node_data['risk_score'] * 2,
                    'color': self._risk_to_color(node_data['risk_score']),
                    'class': 'clickable node',
                    'data-county': node
                }
            }
            entities.append(entity)
        
        # Create edges
        for edge in G.edges():
            start = pos[edge[0]]
            end = pos[edge[1]]
            
            entity = {
                'type': 'a-line',
                'attributes': {
                    'start': f'{start[0]} {start[1]} {start[2]}',
                    'end': f'{end[0]} {end[1]} {end[2]}',
                    'color': 'rgba(192, 132, 252, 0.3)'
                }
            }
            entities.append(entity)
        
        return {
            'scene': {
                'sky': {'color': '#0f172a'},
                'entities': entities
            }
        }
    
    def _compute_3d_layout(self, G) -> Dict:
        """Compute 3D positions for network nodes."""
        # Use spring layout extended to 3D
        import networkx as nx
        
        pos_2d = nx.spring_layout(G, dim=2, k=2/np.sqrt(len(G.nodes())))
        
        # Add z-coordinate based on risk score
        pos_3d = {}
        for node, (x, y) in pos_2d.items():
            node_data = self.df[self.df['county_name'] == node]
            if not node_data.empty:
                z = node_data.iloc[0]['risk_score'] * 10
            else:
                z = 5
            pos_3d[node] = (x * 20, y * 20, z)
        
        return pos_3d
    
    def render_ar_button(self):
        """Render AR activation button."""
        st.markdown("""
        <style>
        .ar-button {
            background: linear-gradient(135deg, #c084fc 0%, #818cf8 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .ar-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(192, 132, 252, 0.4);
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🥽 Enter AR Mode", key="ar_mode"):
            self._launch_ar_experience()
    
    def _launch_ar_experience(self):
        """Launch AR experience with WebXR."""
        scene = self.create_risk_terrain()
        
        # Generate A-Frame HTML
        aframe_html = self._generate_aframe_html(scene)
        
        # Display in iframe or new window
        st.components.v1.html(aframe_html, height=600)
    
    def _generate_aframe_html(self, scene: Dict) -> str:
        """Generate A-Frame HTML for AR scene."""
        entities_html = ''
        for entity in scene['scene']['entities']:
            attrs = ' '.join([f'{k}="{v}"' for k, v in entity['attributes'].items()])
            entities_html += f'<{entity["type"]} {attrs}></{entity["type"]}>\n'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://aframe.io/releases/1.4.0/aframe.min.js"></script>
            <script src="https://rawgit.com/jeromeetienne/AR.js/master/aframe/build/aframe-ar.js"></script>
            <style>
                body {{ margin: 0; overflow: hidden; }}
            </style>
        </head>
        <body>
            <a-scene embedded arjs="sourceType: webcam; debugUIEnabled: false;">
                <!-- Lighting -->
                <a-light type="ambient" color="{scene['scene']['lighting']['ambient']['color']}" 
                         intensity="{scene['scene']['lighting']['ambient']['intensity']}"></a-light>
                <a-light type="directional" color="{scene['scene']['lighting']['directional']['color']}"
                         intensity="{scene['scene']['lighting']['directional']['intensity']}" 
                         position="-1 1 1"></a-light>
                
                <!-- Sky -->
                <a-sky color="{scene['scene']['sky']['color']}"></a-sky>
                
                <!-- Camera -->
                <a-camera position="{scene['scene']['camera']['position']}" 
                          look-at="{scene['scene']['camera']['lookAt']}">
                    <a-cursor color="#c084fc"></a-cursor>
                </a-camera>
                
                <!-- Entities -->
                {entities_html}
                
                <!-- Ground plane -->
                <a-plane position="0 0 0" rotation="-90 0 0" 
                         width="100" height="100" 
                         color="#1e293b" opacity="0.5"></a-plane>
            </a-scene>
            
            <script>
                // Add click handlers
                document.querySelectorAll('.clickable').forEach(function(el) {{
                    el.addEventListener('click', function() {{
                        var county = this.getAttribute('data-county');
                        var risk = this.getAttribute('data-risk');
                        alert('County: ' + county + '\\nRisk: ' + risk);
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        return html

# Usage in dashboard.py
"""
from ar_vr.scene_builder import ARSceneBuilder

ar_builder = ARSceneBuilder(df)

# In map tab:
ar_builder.render_ar_button()
"""
```

---

## 9. Technology Recommendations

### 9.1 Additional Dependencies

```txt
# requirements-ai-enhancements.txt

# Real-time communication
websockets>=11.0.0
python-socketio>=5.8.0

# Advanced visualizations
dash>=2.14.0
dash-deck>=0.0.1
pydeck>=0.8.0
keplergl>=0.3.0

# Voice processing
SpeechRecognition>=3.10.0
pyttsx3>=2.90

# AR/VR
aiohttp>=3.9.0

# Performance optimization
redis>=5.0.0
polars>=0.19.0
pyarrow>=14.0.0

# Advanced caching
diskcache>=5.6.0
joblib-memory>=0.1.0

# Mobile detection
user-agents>=2.2.0

# 3D graphics
pyvista>=0.43.0
vtk>=9.3.0

# Network visualization
networkx>=3.2.0
pyvis>=0.3.0
```

### 9.2 Recommended Architecture Patterns

| Pattern | Implementation | Use Case |
|---------|---------------|----------|
| Component-Based | React-style components in Python | Reusable UI elements |
| Observer Pattern | WebSocket pub/sub | Real-time updates |
| Strategy Pattern | Chart type selection | AI recommendations |
| Factory Pattern | Visualization creation | Chart generation |
| Command Pattern | Voice commands | Action processing |
| Cache-Aside | Redis caching | Performance optimization |

---

## 10. Implementation Priority Order

### Phase 1: Core AI Features (Weeks 1-2)
1. Natural language query interface
2. AI-powered chart recommendations
3. Interactive drill-down explorer

### Phase 2: Real-Time Features (Weeks 3-4)
4. WebSocket connection manager
5. Live data feed integration
6. Activity monitoring dashboard

### Phase 3: Advanced Visualizations (Weeks 5-6)
7. Enhanced 3D geospatial views
8. Network graph visualizations
9. Time series forecasting charts

### Phase 4: Mobile & Accessibility (Weeks 7-8)
10. Mobile-responsive adapter
11. Touch-optimized controls
12. Simplified mobile navigation

### Phase 5: Voice & AR/VR (Weeks 9-10)
13. Voice command interface
14. AR scene builder
15. Spatial data exploration

### Phase 6: Performance & Polish (Weeks 11-12)
16. Distributed caching layer
17. Performance optimization
18. Production hardening

---

## 11. Integration Points with Existing Code

### 11.1 Dashboard.py Modifications

```python
# Add to imports
from components.ai_chat_interface import AIChatInterface
from components.chart_recommender import ChartRecommender
from components.drill_down_explorer import DrillDownExplorer
from components.mobile_adapter import MobileAdapter
from ai_services.voice_processor import VoiceInterface
from websockets.connection_manager import WebSocketManager
from visualizations.plotly_3d import Geospatial3DVisualizer

# Add to session state initialization
if 'ws_manager' not in st.session_state:
    st.session_state.ws_manager = WebSocketManager()
if 'chat_interface' not in st.session_state:
    st.session_state.chat_interface = None

# Enhanced tab structure
tabs = st.tabs([
    "🧠 Strategic Intelligence",
    "📍 Missouri Command", 
    "🗺️ Resilience Map",
    "🌪️ Scenario Simulator",
    "📈 Predictive Insights",
    "🌾 Agricultural Risk",
    "🚨 Emergency Ops",
    "📋 Strategic Roadmap",
    "📡 Live Feed",
    "🔍 AI Query Hub",      # NEW
    "📊 Smart Charts",       # NEW
    "🌐 Network Analysis",   # NEW
    "📱 Mobile Command",     # NEW
    "🎙️ Voice Control",      # NEW
    "🥽 AR Explorer",        # NEW
    "⚙️ Settings"            # NEW
])
```

### 11.2 Component Registration System

```python
# app/components/__init__.py
"""Component registration and discovery system."""

from typing import Dict, Type
import importlib
import pkgutil

COMPONENT_REGISTRY: Dict[str, Type] = {}

def register_component(name: str, component_class: Type):
    """Register a component for dynamic loading."""
    COMPONENT_REGISTRY[name] = component_class

def get_component(name: str) -> Type:
    """Get a registered component by name."""
    return COMPONENT_REGISTRY.get(name)

def discover_components():
    """Auto-discover and register all components."""
    package_dir = Path(__file__).parent
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        try:
            module = importlib.import_module(f".{module_name}", __package__)
            # Register components that have a register() function
            if hasattr(module, 'register'):
                module.register()
        except Exception as e:
            print(f"Failed to load component {module_name}: {e}")

# Auto-discover on import
discover_components()
```

---

## 12. Summary

This comprehensive enhancement plan transforms the ResilienceAI dashboard from a 9-tab Streamlit application into a cutting-edge, AI-powered strategic intelligence platform with:

- **16 interactive tabs** with specialized functionality
- **Natural language query interface** for conversational data exploration
- **AI-powered chart recommendations** based on data characteristics
- **Interactive drill-down** from national to county level
- **Real-time WebSocket integration** for live data feeds
- **Advanced 3D visualizations** using Plotly and Deck.gl
- **Mobile-responsive design** with touch-optimized controls
- **Voice command interface** for hands-free operation
- **AR/VR capabilities** for spatial data exploration

The architecture maintains backward compatibility with existing code while providing clear extension points for future enhancements. Implementation follows a phased approach to minimize risk and enable iterative delivery.

---

*Document Version: 1.0*
*Generated for ResilienceAI Dashboard Enhancement Project*
*Target Branch: claw-autonomous*
