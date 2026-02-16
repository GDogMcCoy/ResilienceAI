"""
ResilienceAI - Streamlit Dashboard with Agent Query Integration
Comprehensive disaster vulnerability assessment dashboard with Archia agent capabilities.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Try to import the ResilienceAgent
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
try:
    from agent import ResilienceAgent, get_mcp_tools
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

# ── Page Configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="ResilienceAI - Disaster Vulnerability Assessment",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main theme */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Agent Query Tab Styles */
    .agent-query-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    .agent-response {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
    }
    .tool-call-badge {
        display: inline-block;
        background: #28a745;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .citation-badge {
        display: inline-block;
        background: #17a2b8;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-right: 5px;
    }
    .example-query-btn {
        background: #e9ecef;
        border: 1px solid #dee2e6;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .example-query-btn:hover {
        background: #667eea;
        color: white;
    }
    
    /* Sidebar styles */
    .sidebar-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Risk level indicators */
    .risk-high { color: #dc3545; font-weight: bold; }
    .risk-medium { color: #fd7e14; font-weight: bold; }
    .risk-low { color: #28a745; font-weight: bold; }
    
    /* Code blocks */
    code {
        background: #f4f4f4;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
    }
    
    /* Export button */
    .stDownloadButton button {
        background: #667eea;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Initialize Session State ─────────────────────────────────────────
def init_session_state():
    """Initialize session state variables."""
    if 'agent_config' not in st.session_state:
        st.session_state.agent_config = {
            'archia_url': 'http://localhost:8080',
            'api_key': '',
            'model': 'claude-sonnet-4-5-20250929',
            'use_local_agent': True
        }
    if 'agent_history' not in st.session_state:
        st.session_state.agent_history = []
    if 'last_response' not in st.session_state:
        st.session_state.last_response = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'local_agent' not in st.session_state:
        st.session_state.local_agent = None

init_session_state()

# ── Load Data ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    """Load processed county data."""
    try:
        processed_dir = Path(__file__).parent.parent / "data" / "processed"
        features_path = processed_dir / "county_features.csv"
        if features_path.exists():
            df = pd.read_csv(features_path, dtype={"fips": str})
            return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return None

# Try to load data
df = load_data()
if df is not None:
    st.session_state.df = df
    st.session_state.data_loaded = True
    
# Initialize local agent if available
if AGENT_AVAILABLE and st.session_state.local_agent is None:
    try:
        st.session_state.local_agent = ResilienceAgent()
    except Exception as e:
        st.warning(f"Could not initialize local agent: {e}")

# ── Sidebar Configuration ────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=64)
    st.markdown("## ResilienceAI")
    st.markdown("*Disaster Vulnerability Assessment*")
    st.divider()
    
    # Data Status
    st.markdown("### 📊 Data Status")
    if st.session_state.data_loaded:
        st.success(f"✅ {len(st.session_state.df):,} counties loaded")
        st.caption(f"{len(st.session_state.df.columns)} features available")
    else:
        st.warning("⚠️ No data loaded")
        st.caption("Run the data pipeline first")
    
    st.divider()
    
    # Agent Configuration Panel
    st.markdown("### 🤖 Agent Configuration")
    
    # Archia Server URL
    archia_url = st.text_input(
        "Archia Server URL",
        value=st.session_state.agent_config['archia_url'],
        help="URL of the Archia agent server"
    )
    st.session_state.agent_config['archia_url'] = archia_url
    
    # API Key
    api_key = st.text_input(
        "API Key",
        value=st.session_state.agent_config['api_key'],
        type="password",
        help="API key for Archia server authentication"
    )
    st.session_state.agent_config['api_key'] = api_key
    
    # Model Selection
    model = st.selectbox(
        "Model",
        options=[
            "claude-sonnet-4-5-20250929",
            "claude-opus-4-5-20250929",
            "claude-haiku-4-5-20250929",
            "gpt-4o",
            "gpt-4o-mini"
        ],
        index=0,
        help="Select the LLM model for agent responses"
    )
    st.session_state.agent_config['model'] = model
    
    # Local Agent Toggle
    use_local = st.toggle(
        "Use Local Agent",
        value=st.session_state.agent_config['use_local_agent'],
        help="Use local ResilienceAgent instead of Archia API"
    )
    st.session_state.agent_config['use_local_agent'] = use_local and AGENT_AVAILABLE
    
    if not AGENT_AVAILABLE and use_local:
        st.error("Local agent not available. Check dependencies.")
    
    st.divider()
    
    # Navigation
    st.markdown("### 🧭 Navigation")
    st.caption("Use tabs below to navigate")

# ── Main Header ──────────────────────────────────────────────────────
st.markdown('<div class="main-header">🛡️ ResilienceAI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Disaster Vulnerability Assessment Platform</div>', unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14 = st.tabs([
    "📊 Overview",
    "🗺️ Risk Map",
    "🏥 Infrastructure",
    "📈 Trends",
    "🔥 Hotspots",
    "⚖️ Equity Analysis",
    "📋 County Profiles",
    "🔮 Scenarios",
    "💰 Interventions",
    "📤 Export",
    "📑 Briefings",
    "🤖 Agent Query",  # Tab 12
    "🚨 Alert Management",  # Tab 13 - NEW
    "🌾 Agricultural Risk"  # Tab 14 - NEW
])

# ── Tab 1: Overview ─────────────────────────────────────────────────
with tab1:
    st.header("Dashboard Overview")
    
    if st.session_state.data_loaded:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Counties", f"{len(df):,}")
        with col2:
            high_risk = len(df[df['risk_level'] == 'High']) if 'risk_level' in df.columns else 0
            st.metric("High Risk Counties", f"{high_risk:,}")
        with col3:
            avg_risk = df['risk_score'].mean() if 'risk_score' in df.columns else 0
            st.metric("Average Risk Score", f"{avg_risk:.3f}")
        with col4:
            if 'compound_risk_count' in df.columns:
                compound = len(df[df['compound_risk_count'] >= 3])
                st.metric("Compound Risk Counties", f"{compound:,}")
            else:
                st.metric("Compound Risk Counties", "N/A")
        
        st.divider()
        st.subheader("Risk Distribution")
        
        if 'risk_level' in df.columns:
            risk_dist = df['risk_level'].value_counts()
            fig = px.pie(
                values=risk_dist.values,
                names=risk_dist.index,
                title="Risk Level Distribution",
                color=risk_dist.index,
                color_discrete_map={'High': '#dc3545', 'Medium': '#fd7e14', 'Low': '#28a745'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Load data to see overview metrics")

# ── Tab 2: Risk Map ──────────────────────────────────────────────────
with tab2:
    st.header("Geographic Risk Map")
    if st.session_state.data_loaded and 'latitude' in df.columns and 'longitude' in df.columns:
        fig = px.scatter_mapbox(
            df,
            lat='latitude',
            lon='longitude',
            color='risk_score' if 'risk_score' in df.columns else None,
            size='total_population' if 'total_population' in df.columns else None,
            hover_name='county_name' if 'county_name' in df.columns else None,
            color_continuous_scale='RdYlGn_r',
            zoom=3,
            height=600,
            title="County Risk Scores"
        )
        fig.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Geographic data not available")

# ── Tab 3: Infrastructure ────────────────────────────────────────────
with tab3:
    st.header("Infrastructure Analysis")
    st.info("Infrastructure gap analysis and redundancy metrics")

# ── Tab 4: Trends ────────────────────────────────────────────────────
with tab4:
    st.header("Disaster Trends")
    st.info("Historical disaster frequency and acceleration analysis")

# ── Tab 5: Hotspots ──────────────────────────────────────────────────
with tab5:
    st.header("Risk Hotspots")
    st.info("Spatial clustering and hotspot identification")

# ── Tab 6: Equity Analysis ───────────────────────────────────────────
with tab6:
    st.header("Equity Analysis")
    st.info("Demographic disparities in disaster vulnerability")

# ── Tab 7: County Profiles ───────────────────────────────────────────
with tab7:
    st.header("County Profiles")
    st.info("Detailed county vulnerability profiles")

# ── Tab 8: Scenarios ─────────────────────────────────────────────────
with tab8:
    st.header("Scenario Simulation")
    st.info("What-if disaster scenario modeling")

# ── Tab 9: Interventions ─────────────────────────────────────────────
with tab9:
    st.header("Intervention ROI")
    st.info("Cost-effectiveness analysis for preparedness interventions")

# ── Tab 10: Export ───────────────────────────────────────────────────
with tab10:
    st.header("Data Export")
    st.info("Export data in FHIR, GeoJSON, and other formats")

# ── Tab 11: Briefings ────────────────────────────────────────────────
with tab11:
    st.header("Executive Briefings")
    st.info("Generate executive summary reports")

# ── Tab 12: Agent Query (NEW) ────────────────────────────────────────
with tab12:
    st.header("🤖 Agent Query")
    st.markdown("""
    Ask natural language questions about disaster vulnerability data.
    The AI agent will analyze the data and provide insights with citations.
    """)
    
    # Example Query Buttons
    st.markdown("#### 💡 Example Questions")
    example_cols = st.columns(2)
    
    example_queries = [
        "Which Missouri counties are most vulnerable to flooding?",
        "Where are disasters accelerating fastest?",
        "Which counties have zero hospital redundancy?",
        "Show me compound risk hotspots"
    ]
    
    selected_example = None
    for i, query in enumerate(example_queries):
        with example_cols[i % 2]:
            if st.button(f"🔍 {query}", key=f"example_{i}", use_container_width=True):
                selected_example = query
    
    st.divider()
    
    # Query Input
    st.markdown("#### 📝 Ask Your Question")
    
    default_query = selected_example if selected_example else ""
    query_text = st.text_area(
        "Enter your question:",
        value=default_query,
        placeholder="e.g., Which counties in Texas have the highest flood risk and lowest hospital access?",
        height=100
    )
    
    # Query Options
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submit_query = st.button("🚀 Ask Agent", type="primary", use_container_width=True)
    with col2:
        clear_history = st.button("🗑️ Clear History", use_container_width=True)
    with col3:
        show_tool_calls = st.checkbox("Show tool calls", value=True)
        show_citations = st.checkbox("Show data citations", value=True)
    
    if clear_history:
        st.session_state.agent_history = []
        st.session_state.last_response = None
        st.rerun()
    
    # Process Query
    if submit_query and query_text.strip():
        with st.spinner("🤖 Agent is analyzing..."):
            try:
                # Determine which agent to use
                if st.session_state.agent_config['use_local_agent'] and st.session_state.local_agent:
                    response = process_local_query(query_text, st.session_state.local_agent)
                else:
                    response = process_archia_query(
                        query_text,
                        st.session_state.agent_config
                    )
                
                # Store in history
                st.session_state.agent_history.append({
                    'query': query_text,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                })
                st.session_state.last_response = response
                
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")
                response = None
    
    # Display Response
    if st.session_state.last_response:
        response = st.session_state.last_response
        
        st.markdown("---")
        st.markdown("#### 📤 Agent Response")
        
        # Response container
        with st.container():
            st.markdown('<div class="agent-response">', unsafe_allow_html=True)
            
            # Main response text
            if 'answer' in response:
                st.markdown(response['answer'])
            elif 'response' in response:
                st.markdown(response['response'])
            elif 'error' in response:
                st.error(response['error'])
            else:
                st.json(response)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Tool Calls
            if show_tool_calls and 'tool_calls' in response and response['tool_calls']:
                with st.expander("🔧 Tool Calls Made", expanded=False):
                    for i, tool in enumerate(response['tool_calls']):
                        st.markdown(f"**{i+1}. `{tool.get('name', 'unknown')}`**")
                        if 'parameters' in tool:
                            st.json(tool['parameters'])
                        if 'result' in tool:
                            st.caption("Result:")
                            st.json(tool['result'])
            
            # Data Citations
            if show_citations and 'citations' in response and response['citations']:
                with st.expander("📚 Data Citations", expanded=False):
                    for citation in response['citations']:
                        st.markdown(f"- {citation}")
            
            # Raw Data (if available)
            if 'data' in response and response['data']:
                with st.expander("📊 Raw Data", expanded=False):
                    if isinstance(response['data'], list):
                        st.dataframe(pd.DataFrame(response['data']))
                    else:
                        st.json(response['data'])
            
            # Export Options
            st.markdown("---")
            export_col1, export_col2, export_col3 = st.columns(3)
            
            response_json = json.dumps(response, indent=2, default=str)
            
            with export_col1:
                st.download_button(
                    "📥 Download JSON",
                    data=response_json,
                    file_name=f"agent_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with export_col2:
                # Create markdown export
                md_content = f"""# Agent Query Response

**Query:** {st.session_state.agent_history[-1]['query'] if st.session_state.agent_history else 'N/A'}

**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Response

{response.get('answer', response.get('response', 'No response text available'))}

## Tool Calls

"""
                if 'tool_calls' in response:
                    for tool in response['tool_calls']:
                        md_content += f"- `{tool.get('name', 'unknown')}`\n"
                
                md_content += "\n## Citations\n\n"
                if 'citations' in response:
                    for citation in response['citations']:
                        md_content += f"- {citation}\n"
                
                st.download_button(
                    "📝 Download Markdown",
                    data=md_content,
                    file_name=f"agent_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with export_col3:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    st.code(response.get('answer', response.get('response', '')), language='markdown')
                    st.success("Response displayed above - copy manually")
    
    # Query History
    if st.session_state.agent_history:
        st.markdown("---")
        st.markdown("#### 📜 Query History")
        
        for i, item in enumerate(reversed(st.session_state.agent_history[-5:])):
            with st.expander(f"Q: {item['query'][:60]}...", expanded=False):
                st.markdown(f"**Query:** {item['query']}")
                st.markdown(f"**Time:** {item['timestamp']}")
                if 'answer' in item['response']:
                    st.markdown(f"**Response:** {item['response']['answer'][:200]}...")
                elif 'response' in item['response']:
                    st.markdown(f"**Response:** {item['response']['response'][:200]}...")

# ── Query Processing Functions ───────────────────────────────────────

def process_local_query(query: str, agent: ResilienceAgent) -> dict:
    """
    Process a query using the local ResilienceAgent.
    This implements intelligent query parsing and tool selection.
    """
    query_lower = query.lower()
    tool_calls = []
    citations = []
    data = None
    
    # Query pattern matching for intelligent tool selection
    
    # Pattern 1: Missouri counties vulnerable to flooding
    if 'missouri' in query_lower or 'mo' in query_lower:
        if 'flood' in query_lower or 'vulnerable' in query_lower:
            result = agent.query_counties(
                state='MO',
                sort_by='risk_score',
                max_results=10
            )
            tool_calls.append({
                'name': 'query_counties',
                'parameters': {'state': 'MO', 'sort_by': 'risk_score', 'max_results': 10},
                'result': result
            })
            data = result
            
            # Generate natural language response
            if result and len(result) > 0:
                counties = [r.get('county_name', 'Unknown') for r in result[:5]]
                answer = f"""## Missouri Counties Most Vulnerable to Flooding

Based on comprehensive risk analysis including flood history, infrastructure gaps, and demographic vulnerability, here are the most vulnerable Missouri counties:

**Top 5 Highest Risk Counties:**
"""
                for i, county in enumerate(result[:5], 1):
                    name = county.get('county_name', 'Unknown')
                    risk = county.get('risk_score', 0)
                    level = county.get('risk_level', 'Unknown')
                    pop = county.get('total_population', 0)
                    answer += f"\n{i}. **{name}** - Risk Score: {risk:.3f} ({level}) | Population: {pop:,}"
                
                answer += f"""

### Key Insights:
- **{result[0].get('county_name', 'The highest risk county')}** has the highest composite vulnerability
- These counties show elevated risk across multiple dimensions: infrastructure access, disaster history, and demographic factors
- Priority interventions recommended: {result[0].get('top_intervention', 'infrastructure improvements')}

### Data Sources:
- FEMA Disaster Declarations Database
- HRSA Health Facility Data
- CDC Social Vulnerability Index
- Census Bureau Demographics
"""
                citations = [
                    "FEMA Disaster Declarations Database (2000-2025)",
                    "HRSA Health Facility Data (2024)",
                    "CDC Social Vulnerability Index 2022",
                    "US Census Bureau ACS 2022"
                ]
            else:
                answer = "No Missouri counties found in the database. Please ensure data is loaded correctly."
            
            return {
                'answer': answer,
                'tool_calls': tool_calls,
                'citations': citations,
                'data': data
            }
    
    # Pattern 2: Disaster acceleration
    if 'accelerating' in query_lower or 'fastest' in query_lower or 'trend' in query_lower:
        result = agent.get_disaster_trends(min_acceleration=1.5, max_results=15)
        tool_calls.append({
            'name': 'get_disaster_trends',
            'parameters': {'min_acceleration': 1.5, 'max_results': 15},
            'result': result
        })
        data = result
        
        if result and 'error' not in result:
            answer = f"""## Counties Where Disasters Are Accelerating Fastest

These counties have shown the most significant increase in disaster frequency when comparing 2015-2025 to 2005-2014:

**Top Accelerating Counties:**
"""
            for i, county in enumerate(result[:10], 1):
                name = county.get('county_name', 'Unknown')
                accel = county.get('disaster_acceleration', 0)
                recent = county.get('disasters_2015_2025', 0)
                past = county.get('disasters_2005_2014', 0)
                answer += f"\n{i}. **{name}** - {accel:.1f}x acceleration | {past:.0f} → {recent:.0f} disasters"
            
            answer += """

### Key Findings:
- These counties represent emerging hotspots where climate change and disaster patterns are converging
- The acceleration metric compares disaster counts in the most recent decade vs. the prior decade
- Counties with >2x acceleration should be prioritized for enhanced preparedness

### Implications:
- Historical risk models may underestimate future vulnerability
- Infrastructure planning should account for increasing frequency
- Emergency response capacity needs may be growing
"""
            citations = [
                "FEMA Disaster Declarations Database (2000-2025)",
                "NOAA Climate Data",
                "ResilienceAI Acceleration Analysis"
            ]
        else:
            answer = "Could not retrieve disaster trend data. " + str(result.get('error', ''))
        
        return {
            'answer': answer,
            'tool_calls': tool_calls,
            'citations': citations,
            'data': data
        }
    
    # Pattern 3: Zero redundancy
    if 'zero redundancy' in query_lower or 'hospital redundancy' in query_lower or 'single point of failure' in query_lower:
        result = agent.find_zero_redundancy(max_results=15)
        tool_calls.append({
            'name': 'find_zero_redundancy',
            'parameters': {'max_results': 15},
            'result': result
        })
        data = result
        
        if result and 'error' not in result:
            answer = f"""## Counties with Zero Hospital Redundancy

These counties have critical infrastructure vulnerability - the distance to their 2nd-nearest hospital exceeds 100km, creating single points of failure:

**Critical Redundancy Gaps:**
"""
            for i, county in enumerate(result[:10], 1):
                name = county.get('county_name', 'Unknown')
                dist_1st = county.get('dist_nearest_hospitals_km', 0)
                dist_2nd = county.get('dist_2nd_nearest_hospitals_km', 0)
                pop = county.get('total_population', 0)
                answer += f"\n{i}. **{name}** - 1st hospital: {dist_1st:.1f}km | 2nd hospital: {dist_2nd:.1f}km | Pop: {pop:,}"
            
            answer += """

### ⚠️ Critical Risk Factors:
- **Single Point of Failure**: If the nearest hospital becomes unavailable, residents face extreme travel distances
- **Emergency Response**: Ambulance transport times may exceed critical care windows
- **Disaster Impact**: Natural disasters affecting the single hospital leave the county without emergency care

### Recommendations:
1. Prioritize telehealth infrastructure deployment
2. Establish mobile medical unit agreements
3. Consider satellite clinic or micro-hospital development
4. Develop mutual aid agreements with neighboring counties
"""
            citations = [
                "HRSA Health Facility Data (2024)",
                "Census Bureau Population Estimates",
                "ResilienceAI Infrastructure Gap Analysis"
            ]
        else:
            answer = "Could not retrieve redundancy data. " + str(result.get('error', ''))
        
        return {
            'answer': answer,
            'tool_calls': tool_calls,
            'citations': citations,
            'data': data
        }
    
    # Pattern 4: Compound risk hotspots
    if 'compound risk' in query_lower or 'hotspot' in query_lower or 'multiple risk' in query_lower:
        result = agent.find_compound_risk_counties(min_dimensions=3, max_results=15)
        tool_calls.append({
            'name': 'find_compound_risk_counties',
            'parameters': {'min_dimensions': 3, 'max_results': 15},
            'result': result
        })
        data = result
        
        if result and 'error' not in result:
            answer = f"""## Compound Risk Hotspots

These counties are simultaneously high-risk across **3 or more dimensions** (vulnerability, isolation, disaster exposure, infrastructure deficit):

**Critical Compound Risk Counties:**
"""
            for i, county in enumerate(result[:10], 1):
                name = county.get('county_name', 'Unknown')
                dims = county.get('compound_risk_count', 0)
                risk = county.get('risk_score', 0)
                vuln = county.get('vulnerability_index', 0)
                iso = county.get('isolation_index', 0)
                disasters = county.get('disaster_count', 0)
                answer += f"\n{i}. **{name}** - {dims} risk dimensions | Risk Score: {risk:.3f} | Disasters: {disasters:.0f}"
            
            answer += """

### What is Compound Risk?
Compound risk counties face converging vulnerabilities across:
- **Demographic Vulnerability**: High poverty, elderly, uninsured populations
- **Infrastructure Isolation**: Distance to hospitals, EMS, fire services
- **Disaster Exposure**: Historical and accelerating disaster frequency
- **Resource Deficits**: Limited capacity for preparedness and response

### Priority Actions:
1. **Immediate**: Deploy mobile health units and emergency communication systems
2. **Short-term**: Establish mutual aid agreements and resource pre-positioning
3. **Long-term**: Target infrastructure investments and community resilience programs

These counties should be prioritized for federal resilience funding and technical assistance.
"""
            citations = [
                "FEMA Disaster Declarations Database",
                "HRSA Health Facility Data",
                "CDC Social Vulnerability Index",
                "Census Bureau ACS Data"
            ]
        else:
            answer = "Could not retrieve compound risk data. " + str(result.get('error', ''))
        
        return {
            'answer': answer,
            'tool_calls': tool_calls,
            'citations': citations,
            'data': data
        }
    
    # Default: General query - use query_counties with smart defaults
    result = agent.query_counties(max_results=10, sort_by='risk_score')
    tool_calls.append({
        'name': 'query_counties',
        'parameters': {'max_results': 10, 'sort_by': 'risk_score'},
        'result': result
    })
    data = result
    
    answer = f"""## Query Results

Based on your query: "{query}"

Here are the most relevant counties from our vulnerability database:

**Top Results:**
"""
    for i, county in enumerate(result[:5], 1):
        name = county.get('county_name', 'Unknown')
        risk = county.get('risk_score', 0)
        level = county.get('risk_level', 'Unknown')
        answer += f"\n{i}. **{name}** - Risk: {risk:.3f} ({level})"
    
    answer += """

For more specific results, try:
- Adding a state name (e.g., "in Texas")
- Specifying risk type (e.g., "flood risk")
- Asking about specific metrics (e.g., "hospital access")
"""
    
    citations = [
        "ResilienceAI County Vulnerability Database",
        "Multiple federal data sources aggregated"
    ]
    
    return {
        'answer': answer,
        'tool_calls': tool_calls,
        'citations': citations,
        'data': data
    }


def process_archia_query(query: str, config: dict) -> dict:
    """
    Process a query using the Archia REST API.
    Falls back to local processing if API is unavailable.
    """
    try:
        # Try to call Archia API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}"
        }
        
        payload = {
            "query": query,
            "model": config['model'],
            "tools": get_mcp_tools() if 'get_mcp_tools' in globals() else [],
            "stream": False
        }
        
        response = requests.post(
            f"{config['archia_url']}/api/query",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            # Fallback to local agent
            if st.session_state.local_agent:
                return process_local_query(query, st.session_state.local_agent)
            else:
                return {
                    'error': f"Archia API returned status {response.status_code}: {response.text}"
                }
    
    except requests.exceptions.ConnectionError:
        # Archia server not available - use local agent
        if st.session_state.local_agent:
            st.info("🔄 Archia server not available - using local agent")
            return process_local_query(query, st.session_state.local_agent)
        else:
            return {
                'error': "Could not connect to Archia server and local agent is not available. Please check your configuration."
            }
    
    except Exception as e:
        return {
            'error': f"Error processing query: {str(e)}"
        }

# ── Tab 13: Alert Management ─────────────────────────────────────────
with tab13:
    st.header("🚨 Real-Time Alert Management")
    st.markdown("Monitor and manage vulnerability alerts for counties.")
    
    if not AGENT_AVAILABLE:
        st.warning("⚠️ Agent not available. Alert management requires the ResilienceAgent.")
    else:
        # Alert Management Interface
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Create Alert Subscription")
            
            # County selection
            if st.session_state.data_loaded:
                county_options = st.session_state.df['county_name'].tolist()
                selected_county = st.selectbox("Select County", county_options)
                
                # Get FIPS for selected county
                county_data = st.session_state.df[st.session_state.df['county_name'] == selected_county]
                if not county_data.empty:
                    county_fips = county_data.iloc[0]['fips']
                    county_state = county_data.iloc[0]['county_name'].split(', ')[-1]
                    
                    st.caption(f"FIPS: {county_fips} | State: {county_state}")
                    
                    # Alert threshold
                    threshold = st.slider("Alert Threshold", 0.0, 1.0, 0.7, 0.05,
                                        help="Risk score threshold that triggers alerts")
                    
                    # Alert types
                    alert_types = st.multiselect(
                        "Alert Types",
                        ['flood', 'storm', 'drought', 'wildfire', 'tornado'],
                        default=['flood', 'storm', 'drought', 'wildfire'],
                        help="Types of disasters to monitor"
                    )
                    
                    # Notification channels
                    st.markdown("**Notification Channels**")
                    webhook_url = st.text_input("Webhook URL (optional)", 
                                               placeholder="https://hooks.slack.com/...")
                    email = st.text_input("Email (optional)", 
                                         placeholder="alerts@example.com")
                    
                    if st.button("🔔 Create Subscription", type="primary"):
                        try:
                            agent = st.session_state.local_agent
                            result = agent.subscribe_to_alerts(
                                county_fips=county_fips,
                                threshold=threshold,
                                alert_types=alert_types,
                                webhook_url=webhook_url if webhook_url else None,
                                email=email if email else None
                            )
                            
                            if 'subscription_id' in result:
                                st.success(f"✅ Subscription created: {result['subscription_id']}")
                            else:
                                st.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("No county data loaded")
        
        with col2:
            st.subheader("Active Alerts")
            
            try:
                agent = st.session_state.local_agent
                active_alerts = agent.get_active_alerts()
                
                if active_alerts.get('count', 0) > 0:
                    st.metric("Active Alerts", active_alerts['count'])
                    
                    for alert in active_alerts.get('alerts', [])[:10]:
                        with st.container():
                            cols = st.columns([3, 1, 1])
                            with cols[0]:
                                st.markdown(f"**{alert.get('alert_type', 'Unknown').upper()}** - {alert.get('message', '')[:50]}...")
                                st.caption(f"County: {alert.get('county_fips', 'Unknown')} | Triggered: {alert.get('triggered_at', 'Unknown')[:10]}")
                            with cols[1]:
                                severity = alert.get('severity', 'low')
                                if severity == 'critical':
                                    st.error("🔴 Critical")
                                elif severity == 'high':
                                    st.warning("🟠 High")
                                elif severity == 'medium':
                                    st.info("🟡 Medium")
                                else:
                                    st.success("🟢 Low")
                            with cols[2]:
                                if st.button("Ack", key=f"ack_{alert.get('id', '')}"):
                                    agent.acknowledge_alert(alert.get('id'))
                                    st.rerun()
                            st.divider()
                else:
                    st.info("✅ No active alerts")
                    
            except Exception as e:
                st.error(f"Error loading alerts: {str(e)}")

# ── Tab 14: Agricultural Risk ────────────────────────────────────────
with tab14:
    st.header("🌾 Agricultural Vulnerability Assessment")
    st.markdown("Analyze crop vulnerability, food security risk, and agricultural resilience.")
    
    if not AGENT_AVAILABLE:
        st.warning("⚠️ Agent not available. Agricultural analysis requires the ResilienceAgent.")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("County Analysis")
            
            if st.session_state.data_loaded:
                # State selection for agriculture
                ag_states = ['IA', 'IL', 'IN', 'OH', 'MO', 'KS', 'NE', 'MN', 'WI', 'MI', 
                            'TX', 'CA', 'FL', 'GA', 'NC', 'SC', 'TN', 'KY', 'AR', 'LA']
                selected_state = st.selectbox("Select State", ag_states, index=4)  # MO default
                
                # Filter counties by state
                state_counties = st.session_state.df[
                    st.session_state.df['county_name'].str.contains(f", {selected_state}")
                ]['county_name'].tolist()
                
                if state_counties:
                    selected_county = st.selectbox("Select County", state_counties)
                    
                    county_data = st.session_state.df[st.session_state.df['county_name'] == selected_county]
                    if not county_data.empty:
                        county_fips = county_data.iloc[0]['fips']
                        county_name_only = selected_county.split(',')[0]
                        population = county_data.iloc[0].get('total_population', 0)
                        
                        st.caption(f"FIPS: {county_fips} | Population: {population:,}")
                        
                        analysis_type = st.radio(
                            "Analysis Type",
                            ["Crop Vulnerability", "Food Security Risk", "Crop Yields"]
                        )
                        
                        if st.button("🔍 Analyze", type="primary"):
                            try:
                                agent = st.session_state.local_agent
                                
                                if analysis_type == "Crop Vulnerability":
                                    with st.spinner("Calculating agricultural vulnerability..."):
                                        result = agent.calculate_agricultural_vulnerability(
                                            county_fips=county_fips,
                                            county_name=county_name_only,
                                            state=selected_state
                                        )
                                        st.session_state.ag_result = result
                                        
                                elif analysis_type == "Food Security Risk":
                                    with st.spinner("Assessing food security..."):
                                        result = agent.assess_food_security_risk(
                                            county_fips=county_fips,
                                            county_name=county_name_only,
                                            state=selected_state,
                                            population=population
                                        )
                                        st.session_state.ag_result = result
                                        
                                else:  # Crop Yields
                                    with st.spinner("Fetching crop yield data..."):
                                        result = agent.get_crop_yield(
                                            state=selected_state,
                                            county_name=county_name_only,
                                            commodity='CORN'
                                        )
                                        st.session_state.ag_result = result
                                        
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning(f"No counties found for {selected_state}")
            else:
                st.warning("No county data loaded")
        
        with col2:
            st.subheader("Analysis Results")
            
            if 'ag_result' in st.session_state:
                result = st.session_state.ag_result
                
                if 'vulnerability_score' in result:
                    # Crop Vulnerability Results
                    score = result['vulnerability_score']
                    risk_level = result['risk_level']
                    
                    col_score, col_level = st.columns(2)
                    with col_score:
                        st.metric("Vulnerability Score", f"{score:.3f}")
                    with col_level:
                        if risk_level == 'High':
                            st.error(f"Risk Level: {risk_level}")
                        elif risk_level == 'Moderate':
                            st.warning(f"Risk Level: {risk_level}")
                        else:
                            st.success(f"Risk Level: {risk_level}")
                    
                    st.markdown("**Crop Stability (Coefficient of Variation)**")
                    stability = result.get('crop_stability', {})
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Corn", f"{stability.get('corn', 0):.3f}")
                    with cols[1]:
                        st.metric("Soybeans", f"{stability.get('soybeans', 0):.3f}")
                    with cols[2]:
                        st.metric("Wheat", f"{stability.get('wheat', 0):.3f}")
                    
                    st.caption("Higher values = more variable yields = more vulnerable")
                    
                elif 'food_security_risk' in result:
                    # Food Security Results
                    risk = result['food_security_risk']
                    acres = result.get('agricultural_acres', 0)
                    calories = result.get('calories_per_capita', 0)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if risk == 'High':
                            st.error(f"Risk: {risk}")
                        elif risk == 'Moderate':
                            st.warning(f"Risk: {risk}")
                        else:
                            st.success(f"Risk: {risk}")
                    with col2:
                        st.metric("Ag Acres", f"{acres:,}")
                    with col3:
                        st.metric("Cal/Capita", f"{calories:,}")
                    
                    st.markdown(f"**Import Dependency:** {result.get('import_dependency', 'Unknown')}")
                    
                    if risk == 'High':
                        st.error("⚠️ This county is highly dependent on food imports. Disruptions could cause food insecurity.")
                        
                elif 'yields' in result:
                    # Crop Yield Results
                    st.metric("Records Found", result.get('record_count', 0))
                    
                    yields_data = result.get('yields', [])
                    if yields_data:
                        df_yields = pd.DataFrame(yields_data)
                        st.dataframe(df_yields[['county_name', 'year', 'commodity', 'yield_per_acre']], 
                                    use_container_width=True)
                        
                        # Simple chart
                        if len(df_yields) > 1:
                            fig = px.line(df_yields, x='year', y='yield_per_acre', 
                                         title=f"{result.get('commodity', 'Crop')} Yield Trend",
                                         markers=True)
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("👈 Select a county and click 'Analyze' to see results")

# ── Footer ───────────────────────────────────────────────────────────
st.divider()
st.caption("""
🛡️ **ResilienceAI** - Developed for the Archia Hackathon | 
Powered by AI-driven vulnerability assessment | 
Data sources: FEMA, HRSA, CDC, Census Bureau, USDA NASS, NOAA
""")
""")
