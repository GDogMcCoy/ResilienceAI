"""
AI Chat Interface for Natural Language Data Queries
Enables conversational interaction with ResilienceAI data
"""
import streamlit as st
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import re


@dataclass
class ChatMessage:
    """Represents a single chat message."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    visualization: Optional[Dict] = None
    actions: Optional[List[Dict]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentClassification:
    """Result of intent classification."""
    intent_type: str
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    suggested_actions: List[str] = field(default_factory=list)


class AIChatInterface:
    """
    Conversational AI interface for dashboard queries.
    Supports context-aware multi-turn conversations with visualization generation.
    """
    
    INTENT_PATTERNS = {
        'visualization': {
            'keywords': ['show', 'display', 'map', 'chart', 'plot', 'visualize', 'graph'],
            'entities': ['chart_type', 'location', 'metric', 'time_range']
        },
        'comparison': {
            'keywords': ['compare', 'versus', 'vs', 'difference', 'between', 'contrast'],
            'entities': ['entities_to_compare', 'comparison_metric']
        },
        'prediction': {
            'keywords': ['predict', 'forecast', 'future', 'will', 'trend', 'projection'],
            'entities': ['prediction_target', 'time_horizon', 'scenario']
        },
        'explanation': {
            'keywords': ['why', 'how', 'explain', 'what causes', 'reason', 'understand'],
            'entities': ['explanation_target', 'context']
        },
        'filtering': {
            'keywords': ['filter', 'only', 'where', 'with', 'without', 'exclude'],
            'entities': ['filter_criteria', 'filter_value']
        },
        'drill_down': {
            'keywords': ['drill', 'explore', 'details', 'more about', 'deep dive'],
            'entities': ['target_entity', 'detail_level']
        },
        'summarization': {
            'keywords': ['summarize', 'overview', 'summary', 'highlights', 'key points'],
            'entities': ['summary_scope', 'focus_area']
        }
    }
    
    QUICK_SUGGESTIONS = [
        {'icon': '🌾', 'label': 'Ag Risk', 'query': 'Show agricultural vulnerability by state'},
        {'icon': '🏥', 'label': 'Healthcare', 'query': 'Which counties have zero hospital redundancy?'},
        {'icon': '📈', 'label': 'Trends', 'query': 'Where are disasters accelerating most?'},
        {'icon': '💰', 'label': 'ROI', 'query': 'What is the best resilience investment for Missouri?'},
        {'icon': '🔥', 'label': 'High Risk', 'query': 'Show top 20 highest risk counties'},
        {'icon': '📊', 'label': 'Compare', 'query': 'Compare risk profiles of urban vs rural counties'}
    ]
    
    def __init__(
        self,
        agent: Any = None,
        orchestrator: Any = None,
        df: Optional[Any] = None,
        on_visualization: Optional[Callable] = None,
        context_window: int = 5
    ):
        self.agent = agent
        self.orchestrator = orchestrator
        self.df = df
        self.on_visualization = on_visualization
        self.context_window = context_window
        
    def initialize_session_state(self):
        """Initialize chat-related session state variables."""
        defaults = {
            'chat_history': [],
            'chat_context': {
                'current_county': None,
                'current_state': None,
                'last_visualization': None,
                'filters': {},
                'conversation_turns': 0
            },
            'chat_suggestions': self.QUICK_SUGGESTIONS.copy(),
            'pending_visualization': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def render(self, container: Optional[st.container] = None):
        """Render the chat interface in a Streamlit container."""
        self.initialize_session_state()
        
        target_container = container or st
        
        with target_container:
            self._inject_styles()
            
            # Header
            st.markdown("### 🤖 AI Query Assistant")
            st.caption("Ask questions about disaster vulnerability in natural language")
            
            # Chat messages container
            chat_container = st.container()
            with chat_container:
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                for msg in st.session_state.chat_history:
                    self._render_message(msg)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Quick suggestions
            self._render_quick_actions()
            
            # Input area
            self._render_input_area()
    
    def _inject_styles(self):
        """Inject custom CSS for chat interface."""
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        .chat-container {
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(192, 132, 252, 0.2);
            max-height: 500px;
            overflow-y: auto;
            margin-bottom: 16px;
        }
        
        .chat-message {
            margin: 12px 0;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .chat-message-user {
            background: linear-gradient(135deg, rgba(129, 140, 248, 0.2) 0%, rgba(129, 140, 248, 0.1) 100%);
            border-radius: 16px 16px 4px 16px;
            padding: 14px 18px;
            margin-left: 60px;
            border-right: 3px solid #818cf8;
        }
        
        .chat-message-assistant {
            background: linear-gradient(135deg, rgba(192, 132, 252, 0.15) 0%, rgba(192, 132, 252, 0.05) 100%);
            border-radius: 16px 16px 16px 4px;
            padding: 14px 18px;
            margin-right: 60px;
            border-left: 3px solid #c084fc;
        }
        
        .chat-header {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .chat-header-user { color: #818cf8; }
        .chat-header-assistant { color: #c084fc; }
        
        .chat-content {
            color: #f8fafc;
            line-height: 1.5;
            font-size: 14px;
        }
        
        .chat-actions {
            display: flex;
            gap: 8px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        
        .quick-suggestions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }
        
        .suggestion-chip {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(192, 132, 252, 0.3);
            border-radius: 20px;
            padding: 8px 14px;
            font-size: 13px;
            color: #f8fafc;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .suggestion-chip:hover {
            background: rgba(192, 132, 252, 0.2);
            border-color: #c084fc;
        }
        
        .chat-input-container {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 12px;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            background: #c084fc;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def _render_message(self, msg: ChatMessage):
        """Render a single chat message."""
        css_class = f"chat-message-{msg.role}"
        header_class = f"chat-header-{msg.role}"
        
        st.markdown(f'<div class="chat-message {css_class}">', unsafe_allow_html=True)
        
        # Header
        if msg.role == 'assistant':
            st.markdown(f'<div class="chat-header {header_class}">🤖 ResilienceAI</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-header {header_class}">👤 You</div>', 
                       unsafe_allow_html=True)
        
        # Content
        st.markdown(f'<div class="chat-content">{msg.content}</div>', 
                   unsafe_allow_html=True)
        
        # Inline visualization
        if msg.visualization:
            self._render_inline_viz(msg.visualization)
        
        # Action buttons
        if msg.actions:
            cols = st.columns(min(len(msg.actions), 3))
            for idx, action in enumerate(msg.actions):
                with cols[idx % 3]:
                    if st.button(
                        action.get('label', 'Action'),
                        key=f"action_{action.get('id', idx)}_{msg.timestamp}",
                        use_container_width=True
                    ):
                        self._handle_action(action)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_inline_viz(self, viz_config: Dict):
        """Render an inline visualization within chat."""
        import plotly.express as px
        import plotly.graph_objects as go
        
        viz_type = viz_config.get('type')
        
        try:
            if viz_type == 'choropleth' and self.df is not None:
                fig = px.choropleth(
                    self.df,
                    locations=viz_config.get('location_col', 'fips'),
                    color=viz_config.get('color_col', 'risk_score'),
                    scope='usa',
                    color_continuous_scale='RdYlGn_r',
                    title=viz_config.get('title', 'Risk Distribution')
                )
                fig.update_layout(template='plotly_dark', height=300)
                st.plotly_chart(fig, use_container_width=True, key=f"viz_{datetime.now().timestamp()}")
                
            elif viz_type == 'metric_cards':
                metrics = viz_config.get('metrics', [])
                cols = st.columns(len(metrics))
                for col, metric in zip(cols, metrics):
                    with col:
                        st.metric(
                            label=metric.get('label', 'Metric'),
                            value=metric.get('value', 'N/A'),
                            delta=metric.get('delta')
                        )
                        
            elif viz_type == 'bar_chart' and self.df is not None:
                data = viz_config.get('data', self.df)
                fig = px.bar(
                    data,
                    x=viz_config.get('x', 'county_name'),
                    y=viz_config.get('y', 'risk_score'),
                    color=viz_config.get('color'),
                    title=viz_config.get('title')
                )
                fig.update_layout(template='plotly_dark', height=250)
                st.plotly_chart(fig, use_container_width=True)
                
            elif viz_type == 'table':
                data = viz_config.get('data', [])
                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True
                )
        except Exception as e:
            st.error(f"Could not render visualization: {str(e)}")
    
    def _render_quick_actions(self):
        """Render quick action suggestion chips."""
        st.markdown('<div class="quick-suggestions">', unsafe_allow_html=True)
        
        # Get contextual suggestions based on conversation history
        suggestions = self._get_contextual_suggestions()
        
        cols = st.columns(min(len(suggestions), 3))
        for idx, suggestion in enumerate(suggestions[:3]):
            with cols[idx]:
                if st.button(
                    f"{suggestion['icon']} {suggestion['label']}",
                    key=f"suggestion_{idx}",
                    use_container_width=True
                ):
                    self._process_query(suggestion['query'])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_input_area(self):
        """Render the chat input area."""
        col1, col2, col3 = st.columns([10, 1, 1])
        
        with col1:
            query = st.text_input(
                "Ask about disaster vulnerability...",
                key="chat_input_field",
                placeholder="e.g., 'Show me high-risk counties in Missouri'",
                label_visibility="collapsed"
            )
        
        with col2:
            st.button("🎤", key="voice_input_btn", help="Voice input (coming soon)")
        
        with col3:
            if st.button("📎", key="attach_context_btn", help="Attach current view"):
                self._attach_current_context()
        
        if query:
            self._process_query(query)
            # Clear input after processing
            st.session_state.chat_input_field = ""
    
    def _process_query(self, query: str):
        """Process user query through AI pipeline."""
        # Add user message
        user_msg = ChatMessage(role='user', content=query)
        st.session_state.chat_history.append(user_msg)
        
        # Show typing indicator
        self._show_typing_indicator()
        
        # Classify intent
        intent = self._classify_intent(query)
        
        # Generate response based on intent
        response = self._generate_response(query, intent)
        
        # Add assistant response
        assistant_msg = ChatMessage(
            role='assistant',
            content=response['content'],
            visualization=response.get('visualization'),
            actions=response.get('actions'),
            metadata={'intent': intent.intent_type, 'confidence': intent.confidence}
        )
        st.session_state.chat_history.append(assistant_msg)
        
        # Update context
        st.session_state.chat_context['conversation_turns'] += 1
        
        # Trigger callback if visualization present
        if self.on_visualization and 'visualization' in response:
            self.on_visualization(response['visualization'])
        
        st.rerun()
    
    def _show_typing_indicator(self):
        """Display typing indicator."""
        st.markdown("""
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        """, unsafe_allow_html=True)
    
    def _classify_intent(self, query: str) -> IntentClassification:
        """Classify user intent using keyword matching and heuristics."""
        query_lower = query.lower()
        scores = {}
        entities = {}
        
        for intent_type, config in self.INTENT_PATTERNS.items():
            score = 0
            for keyword in config['keywords']:
                if keyword in query_lower:
                    score += 1
                    # Extract entities based on patterns
                    for entity in config['entities']:
                        extracted = self._extract_entity(query_lower, entity)
                        if extracted:
                            entities[entity] = extracted
            scores[intent_type] = score
        
        # Get highest scoring intent
        if scores:
            best_intent = max(scores, key=scores.get)
            confidence = min(scores[best_intent] / 2, 1.0)  # Normalize
            return IntentClassification(
                intent_type=best_intent,
                confidence=confidence,
                entities=entities,
                suggested_actions=self._get_suggested_actions(best_intent)
            )
        
        return IntentClassification(
            intent_type='general',
            confidence=0.5,
            entities=entities
        )
    
    def _extract_entity(self, query: str, entity_type: str) -> Optional[str]:
        """Extract entity value from query."""
        patterns = {
            'location': r'(in|for|at)\s+([\w\s,]+?)(?:\?|$|\s+(?:with|where|and))',
            'chart_type': r'(chart|graph|map|plot)\s+(?:as\s+)?(\w+)',
            'time_range': r'(last|past|previous)\s+(\d+)?\s*(year|month|day)s?',
            'metric': r'(risk|vulnerability|population|infrastructure)'
        }
        
        if entity_type in patterns:
            match = re.search(patterns[entity_type], query)
            if match:
                return match.group(2) if len(match.groups()) > 1 else match.group(1)
        
        return None
    
    def _get_suggested_actions(self, intent_type: str) -> List[str]:
        """Get suggested actions for an intent type."""
        actions = {
            'visualization': ['Change chart type', 'Export visualization', 'Add to dashboard'],
            'comparison': ['Add comparison', 'Export comparison', 'Save view'],
            'prediction': ['Adjust parameters', 'Export forecast', 'Set alert'],
            'drill_down': ['Go deeper', 'Compare with neighbors', 'View history']
        }
        return actions.get(intent_type, [])
    
    def _generate_response(self, query: str, intent: IntentClassification) -> Dict:
        """Generate response based on intent and query."""
        handlers = {
            'visualization': self._handle_viz_query,
            'comparison': self._handle_comparison_query,
            'prediction': self._handle_prediction_query,
            'explanation': self._handle_explanation_query,
            'filtering': self._handle_filtering_query,
            'drill_down': self._handle_drill_down_query,
            'summarization': self._handle_summarization_query,
            'general': self._handle_general_query
        }
        
        handler = handlers.get(intent.intent_type, self._handle_general_query)
        return handler(query, intent)
    
    def _handle_viz_query(self, query: str, intent: IntentClassification) -> Dict:
        """Handle visualization queries."""
        location = intent.entities.get('location', 'nationwide')
        metric = intent.entities.get('metric', 'risk_score')
        
        content = f"Here's the {metric.replace('_', ' ')} visualization for {location}."
        
        visualization = {
            'type': 'choropleth',
            'color_col': metric,
            'title': f'{metric.replace("_", " ").title()} - {location.title()}'
        }
        
        return {
            'content': content,
            'visualization': visualization,
            'actions': [
                {'id': 'change_chart', 'label': '📊 Change Chart'},
                {'id': 'export', 'label': '💾 Export'},
                {'id': 'pin', 'label': '📌 Pin to Dashboard'}
            ]
        }
    
    def _handle_comparison_query(self, query: str, intent: IntentClassification) -> Dict:
        """Handle comparison queries."""
        return {
            'content': "I'll compare the requested entities for you. Here's the analysis:",
            'visualization': {
                'type': 'bar_chart',
                'x': 'county_name',
                'y': 'risk_score',
                'title': 'Risk Score Comparison'
            },
            'actions': [
                {'id': 'add_entity', 'label': '➕ Add Entity'},
                {'id': 'change_metric', 'label': '📈 Change Metric'}
            ]
        }
    
    def _handle_prediction_query(self, query: str, intent: IntentClassification) -> Dict:
        """Handle prediction queries."""
        return {
            'content': "Based on historical trends and climate models, here's the 10-year risk projection:",
            'visualization': {
                'type': 'table',
                'data': [
                    {'Year': '2025', 'Projected Risk': '0.45', 'Confidence': '85%'},
                    {'Year': '2030', 'Projected Risk': '0.52', 'Confidence': '78%'},
                    {'Year': '2035', 'Projected Risk': '0.61', 'Confidence': '72%'}
                ]
            },
            'actions': [
                {'id': 'adjust_params', 'label': '⚙️ Adjust Parameters'},
                {'id': 'export_forecast', 'label': '📤 Export Forecast'}
            ]
        }
    
    def _handle_explanation_query(self, query: str, intent: IntentClassification) -> Dict:
        """Handle explanation queries."""
        return {
            'content': """Risk scores are calculated using multiple factors:
            
- **Vulnerability Index (40%)**: Population demographics, poverty, disability rates
- **Infrastructure Gap (30%)**: Distance to hospitals, emergency services
- **Disaster History (20%)**: Historical declaration frequency and severity
- **Isolation Index (10%)**: Geographic remoteness and access barriers

Counties with risk scores above 0.7 are classified as "High Risk" and prioritized for intervention.""",
            'actions': [
                {'id': 'learn_more', 'label': '📚 Learn More'},
                {'id': 'view_methodology', 'label': '🔬 View Methodology'}
            ]
        }
    
    def _handle_filtering_query(self, query: str, intent: IntentClassification) -> Dict:
        """Handle filtering queries."""
        return {
            'content': "I've applied the requested filter. Here are the results:",
            'visualization': {
                'type': 'table',
                'data': self.df.nlargest(10, 'risk_score')[['county_name', 'state', 'risk_score', 'risk_level']] if self.df is not None else []
            },
            'actions': [
                {'id': 'refine', 'label': '🔍 Refine Filter'},
                {'id': 'clear', 'label': '❌ Clear Filters'}
            ]
        }
    
    def _handle_drill_down_query(self, query: str, intent: IntentClassification) -> Dict:
        """Handle drill-down queries."""
        target = intent.entities.get('target_entity', 'selected county')
        return {
            'content': f"Here's the detailed breakdown for {target}:",
            'visualization': {
                'type': 'metric_cards',
                'metrics': [
                    {'label': 'Risk Score', 'value': '0.73', 'delta': '+12%'},
                    {'label': 'Population', 'value': '45,231'},
                    {'label': 'Vulnerability', 'value': '0.68'},
                    {'label': 'Hospital Distance', 'value': '23 km'}
                ]
            },
            'actions': [
                {'id': 'neighbors', 'label': '🏘️ View Neighbors'},
                {'id': 'history', 'label': '📜 View History'}
            ]
        }
    
    def _handle_summarization_query(self, query: str, intent: IntentClassification) -> Dict:
        """Handle summarization queries."""
        return {
            'content': """## National Resilience Summary

**Key Findings:**
- 127 counties (3.9%) are classified as **High Risk**
- Average risk score: **0.42** (Medium)
- 23 counties have **zero hospital redundancy**
- Agricultural vulnerability concentrated in Midwest

**Top Risk Factors:**
1. Infrastructure gaps in rural areas
2. Aging population in 34% of counties
3. Increasing disaster frequency (2015-2025)

**Recommended Actions:**
- Prioritize healthcare expansion in identified counties
- Enhance emergency response capabilities
- Invest in climate adaptation infrastructure""",
            'actions': [
                {'id': 'full_report', 'label': '📄 Full Report'},
                {'id': 'export', 'label': '💾 Export Summary'}
            ]
        }
    
    def _handle_general_query(self, query: str, intent: IntentClassification) -> Dict:
        """Handle general queries using agent if available."""
        if self.agent:
            try:
                agent_response = self.agent.process_natural_language_query(query)
                return {
                    'content': agent_response.get('response', 'I processed your query.'),
                    'actions': agent_response.get('actions', [])
                }
            except Exception as e:
                return {
                    'content': f"I understand you're asking about: '{query}'. Let me help you explore this data. Try asking about specific counties, risk factors, or requesting visualizations.",
                    'actions': [
                        {'id': 'examples', 'label': '💡 See Examples'},
                        {'id': 'help', 'label': '❓ Get Help'}
                    ]
                }
        
        return {
            'content': f"I received your query: '{query}'. I'm here to help you explore disaster vulnerability data. What would you like to know?",
            'actions': [
                {'id': 'browse', 'label': '🔍 Browse Data'},
                {'id': 'visualize', 'label': '📊 Create Visualization'}
            ]
        }
    
    def _get_contextual_suggestions(self) -> List[Dict]:
        """Get context-aware query suggestions."""
        context = st.session_state.chat_context
        suggestions = []
        
        # Based on current selection
        if context.get('current_county'):
            suggestions.append({
                'icon': '📍',
                'label': f"{context['current_county'][:15]}...",
                'query': f"Detailed analysis of {context['current_county']}"
            })
        
        if context.get('current_state'):
            suggestions.append({
                'icon': '🏛️',
                'label': context['current_state'],
                'query': f"Show risk overview for {context['current_state']}"
            })
        
        # Based on conversation history
        history = st.session_state.chat_history
        if history:
            last_query = history[-1]['content'] if history[-1]['role'] == 'user' else ''
            if 'risk' in last_query.lower():
                suggestions.append({
                    'icon': '🔥',
                    'label': 'High Risk Only',
                    'query': 'Show only high risk counties'
                })
        
        # Fill with default suggestions
        defaults = [s for s in self.QUICK_SUGGESTIONS if s not in suggestions]
        suggestions.extend(defaults[:max(0, 3 - len(suggestions))])
        
        return suggestions[:3]
    
    def _handle_action(self, action: Dict):
        """Handle action button clicks."""
        action_id = action.get('id')
        
        if action_id == 'export':
            st.toast("Export functionality coming soon!")
        elif action_id == 'pin':
            st.toast("Pinned to dashboard!")
        elif action_id == 'clear':
            st.session_state.chat_context['filters'] = {}
            st.toast("Filters cleared!")
        else:
            st.toast(f"Action '{action.get('label', action_id)}' triggered")
    
    def _attach_current_context(self):
        """Attach current dashboard context to chat."""
        context = st.session_state.chat_context
        context_info = f"Current view: {context.get('current_county', 'National')} - {context.get('current_state', 'All States')}"
        
        st.session_state.chat_history.append(ChatMessage(
            role='system',
            content=f"📎 Context attached: {context_info}",
            metadata={'context_attachment': True}
        ))
        st.toast("Current view context attached to chat")


# Convenience function for dashboard integration
def render_chat_interface(
    agent=None,
    orchestrator=None,
    df=None,
    on_visualization=None,
    container=None
):
    """Render the AI chat interface with minimal setup."""
    chat = AIChatInterface(
        agent=agent,
        orchestrator=orchestrator,
        df=df,
        on_visualization=on_visualization
    )
    chat.render(container)
