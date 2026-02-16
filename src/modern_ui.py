"""
Modern UI Components for ResilienceAI Dashboard
State-of-the-art visual design using Streamlit and custom CSS
"""

import streamlit as st

# Esoteric Noir color palette
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
    'accent_glow': '0 0 15px rgba(192, 132, 252, 0.4)'
}

# Modern CSS framework (Esoteric Noir Edition)
MODERN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    code, pre, .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header styling */
    .modern-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        border: 1px solid rgba(192, 132, 252, 0.2);
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.5), 0 0 10px rgba(192, 132, 252, 0.1);
    }
    
    .modern-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
        background: linear-gradient(to right, #f8fafc, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 20px rgba(192, 132, 252, 0.3);
    }
    
    .modern-header p {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-top: 0.75rem;
        font-weight: 300;
    }
    
    /* Card component */
    .metric-card {
        background: #1e293b;
        border-radius: 20px;
        padding: 1.75rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-6px);
        border-color: rgba(192, 132, 252, 0.4);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 0 15px rgba(192, 132, 252, 0.1);
    }
    
    .metric-value {
        font-size: 2.75rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        color: #f8fafc;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-weight: 600;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
        padding: 0.75rem 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1e293b;
        border-radius: 12px;
        padding: 0.875rem 1.75rem;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #94a3b8 !important;
        transition: all 0.3s;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border-color: rgba(192, 132, 252, 0.5);
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.3);
    }
    
    /* Risk level indicators */
    .risk-high {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid #f87171;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.7rem;
        text-shadow: 0 0 5px rgba(248, 113, 113, 0.3);
    }
    
    .risk-medium {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid #fbbf24;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.7rem;
    }
    
    .risk-low {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid #34d399;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.7rem;
    }

    /* Bento Grid Layout */
    .bento-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        grid-auto-rows: minmax(150px, auto);
        gap: 1.5rem;
        padding: 1rem 0;
    }
    
    .bento-item {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 24px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .bento-item:hover {
        transform: scale(1.02);
        border-color: rgba(192, 132, 252, 0.5);
        background: rgba(30, 41, 59, 0.9);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }

    .bento-large { grid-column: span 2; grid-row: span 2; }
    .bento-wide { grid-column: span 2; }
    .bento-tall { grid-row: span 2; }

    /* Vanta Background Fix */
    #vanta-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
    }
</style>

<div id="vanta-canvas"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.fog.min.js"></script>
<script>
    window.addEventListener('DOMContentLoaded', (event) => {
        VANTA.FOG({
            el: "#vanta-canvas",
            mouseControls: true,
            touchControls: true,
            gyroControls: false,
            minHeight: 200.00,
            minWidth: 200.00,
            highlightColor: 0x3f3f46,
            midtoneColor: 0x1e1b4b,
            lowlightColor: 0x0f172a,
            baseColor: 0x0f172a,
            blurFactor: 0.6,
            speed: 1.5,
            zoom: 1.00
        })
    });
</script>
"""
"""


def apply_modern_theme():
    """Apply modern theme to Streamlit app"""
    st.markdown(MODERN_CSS, unsafe_allow_html=True)


def render_modern_header(title: str, subtitle: str):
    """Render a modern gradient header"""
    st.markdown(f"""
    <div class="modern-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, delta: str = None, icon: str = "📊"):
    """Render a modern metric card"""
    delta_html = f"<span style='color: #10b981; font-size: 0.875rem;'>↗ {delta}</span>" if delta else ""
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
            <span class="metric-label">{label}</span>
        </div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_status_indicator(label: str, status: str = "online"):
    """Render a status indicator badge"""
    status_class = f"status-{status}"
    st.markdown(f'<span class="status-badge {status_class}">{label}</span>', unsafe_allow_html=True)


def render_risk_badge(level: str):
    """Render a risk level badge"""
    risk_class = f"risk-{level.lower()}"
    st.markdown(f'<span class="{risk_class}">{level.upper()}</span>', unsafe_allow_html=True)


# Animation components
LOADING_ANIMATION = """
<div style="display: flex; justify-content: center; align-items: center; height: 200px;">
    <div style="
        width: 50px;
        height: 50px;
        border: 4px solid #e2e8f0;
        border-top: 4px solid #4f46e5;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    "></div>
</div>
<style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
"""


def show_loading():
    """Show modern loading animation"""
    st.markdown(LOADING_ANIMATION, unsafe_allow_html=True)


# Chart themes
PLOTLY_THEME = {
    'template': 'plotly_white',
    'font': {'family': 'Inter, sans-serif'},
    'colorway': ['#4f46e5', '#7c3aed', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'],
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)'
}


def apply_plotly_theme(fig):
    """Apply modern theme to Plotly figure"""
    fig.update_layout(**PLOTLY_THEME)
    fig.update_layout(
        title_font_size=20,
        title_font_family='Inter, sans-serif',
        title_font_color='#1e293b',
        legend_title_font_size=14,
        legend_font_size=12,
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Inter, sans-serif'
        )
    )
    return fig
