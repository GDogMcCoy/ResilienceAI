"""
ResilienceAI Task Tracker Dashboard
Real-time monitoring of development tasks and subagent progress
"""

import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path

# Page config
st.set_page_config(
    page_title="ResilienceAI Task Tracker",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
    }
    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    }
    .task-card {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #6366f1;
    }
    .status-running {
        color: #10b981;
        font-weight: bold;
    }
    .status-complete {
        color: #3b82f6;
        font-weight: bold;
    }
    .status-pending {
        color: #f59e0b;
        font-weight: bold;
    }
    .metric-card {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #6366f1;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📋 ResilienceAI Task Tracker")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Auto-refresh
auto_refresh = st.checkbox("🔄 Auto-refresh (10 seconds)", value=True)

# Task data structure
tasks = {
    "DevOps & Deployment": {
        "Fix Archia security (API key)": "pending",
        "Add missing MCP tool mappings": "pending",
        "Create docker-compose.yml": "pending",
        "Create deploy.sh script": "pending",
    },
    "Frontend UI": {
        "Fix auto-refresh blocking": "pending",
        "Fix 3D landscape NaN values": "pending",
        "Add empty DataFrame handling": "pending",
        "Fix deprecation warnings": "pending",
    },
    "Backend & Data": {
        "Create data directory structure": "pending",
        "Add API error handling": "pending",
        "Add caching for external APIs": "pending",
        "Fix import errors": "pending",
    },
    "QA & Testing": {
        "Create E2E dashboard tests": "pending",
        "Create agent method tests": "pending",
        "Create API integration tests": "pending",
        "Create data pipeline tests": "pending",
    }
}

# Load status from files if they exist
def load_task_status():
    status_file = Path("task_status.json")
    if status_file.exists():
        with open(status_file) as f:
            return json.load(f)
    return {}

# Save task status
def save_task_status(status):
    with open("task_status.json", "w") as f:
        json.dump(status, f)

# Load current status
current_status = load_task_status()

# Update tasks with current status
for category, items in tasks.items():
    for task in items:
        if task in current_status:
            tasks[category][task] = current_status[task]

# Metrics
st.subheader("📊 Progress Overview")
col1, col2, col3, col4 = st.columns(4)

total_tasks = sum(len(items) for items in tasks.values())
completed_tasks = sum(1 for items in tasks.values() for status in items.values() if status == "complete")
running_tasks = sum(1 for items in tasks.values() for status in items.values() if status == "running")
pending_tasks = total_tasks - completed_tasks - running_tasks

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_tasks}</div>
        <div>Total Tasks</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #10b981;">{completed_tasks}</div>
        <div>Complete</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #f59e0b;">{running_tasks}</div>
        <div>Running</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color: #6366f1;">{pending_tasks}</div>
        <div>Pending</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Task lists
st.subheader("📝 Task Details")

for category, items in tasks.items():
    with st.expander(f"**{category}** ({sum(1 for s in items.values() if s == 'complete')}/{len(items)} complete)"):
        for task, status in items.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"• {task}")
            with col2:
                if status == "complete":
                    st.markdown("<span class='status-complete'>✅ Complete</span>", unsafe_allow_html=True)
                elif status == "running":
                    st.markdown("<span class='status-running'>🔄 Running</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='status-pending'>⏳ Pending</span>", unsafe_allow_html=True)
            
            # Allow manual status update
            new_status = st.selectbox(
                "Update status",
                ["pending", "running", "complete"],
                index=["pending", "running", "complete"].index(status),
                key=f"{category}_{task}",
                label_visibility="collapsed"
            )
            if new_status != status:
                current_status[task] = new_status
                save_task_status(current_status)
                st.rerun()

st.divider()

# Quick actions
st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 View Main Dashboard", use_container_width=True):
        st.info("Run: `python run_dashboard.py` in terminal")

with col2:
    if st.button("🧪 Run Tests", use_container_width=True):
        st.info("Run: `pytest tests/` in terminal")

with col3:
    if st.button("🚀 Deploy to Archia", use_container_width=True):
        st.info("Run: `./deploy.sh` in terminal")

# Git status
st.divider()
st.subheader("📦 Git Status")

try:
    import subprocess
    result = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        st.code(result.stdout, language="bash")
    else:
        st.info("Git status unavailable")
except Exception as e:
    st.info(f"Git check failed: {e}")

# Footer
st.divider()
st.caption("🛡️ ResilienceAI Development Tracker | Updates every 10 seconds if auto-refresh enabled")

# Auto-refresh
if auto_refresh:
    time.sleep(10)
    st.rerun()
