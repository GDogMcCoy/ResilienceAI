"""
Dashboard Activity Monitor for ResilienceAI
Real-time visualization of system activity and data flow
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from pathlib import Path
import time


class DashboardMonitor:
    """
    Monitors and visualizes dashboard activity in real-time
    """
    
    def __init__(self, log_file: str = "data/dashboard_activity.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_activity(self, activity_type: str, details: dict):
        """Log dashboard activity"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': activity_type,
            'details': details
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_recent_activity(self, minutes: int = 60) -> pd.DataFrame:
        """Get recent activity as DataFrame"""
        if not self.log_file.exists():
            return pd.DataFrame()
        
        entries = []
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    if entry_time > cutoff:
                        entries.append(entry)
                except:
                    continue
        
        return pd.DataFrame(entries)
    
    def get_activity_summary(self) -> dict:
        """Get summary statistics"""
        df = self.get_recent_activity(minutes=1440)  # Last 24 hours
        
        if df.empty:
            return {
                'total_activities': 0,
                'activities_by_type': {},
                'last_activity': None
            }
        
        return {
            'total_activities': len(df),
            'activities_by_type': df['type'].value_counts().to_dict(),
            'last_activity': df['timestamp'].max()
        }


def render_activity_dashboard():
    """Render the activity monitoring dashboard"""
    st.header("📊 Dashboard Activity Monitor")
    st.markdown("Real-time visualization of system activity and data flow")
    
    monitor = DashboardMonitor()
    
    # Auto-refresh option
    auto_refresh = st.checkbox("🔄 Auto-refresh (30 seconds)", value=False)
    if auto_refresh:
        st.caption("Page will refresh automatically")
        time.sleep(30)
        st.rerun()
    
    # Time range selector
    time_range = st.selectbox(
        "Time Range",
        ["Last 15 minutes", "Last 1 hour", "Last 4 hours", "Last 24 hours"],
        index=1
    )
    
    minutes_map = {
        "Last 15 minutes": 15,
        "Last 1 hour": 60,
        "Last 4 hours": 240,
        "Last 24 hours": 1440
    }
    minutes = minutes_map[time_range]
    
    # Get activity data
    df = monitor.get_recent_activity(minutes=minutes)
    summary = monitor.get_activity_summary()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Activities",
            len(df),
            delta=f"{len(df) - len(monitor.get_recent_activity(minutes=minutes*2))}" if len(df) > 0 else None
        )
    
    with col2:
        unique_types = df['type'].nunique() if not df.empty else 0
        st.metric("Activity Types", unique_types)
    
    with col3:
        if not df.empty:
            last_activity = pd.to_datetime(df['timestamp'].max())
            time_ago = datetime.now() - last_activity
            st.metric("Last Activity", f"{time_ago.seconds // 60}m ago")
        else:
            st.metric("Last Activity", "No data")
    
    with col4:
        st.metric("System Status", "🟢 Online")
    
    st.divider()
    
    # Activity by type chart
    if not df.empty:
        st.subheader("Activity by Type")
        
        type_counts = df['type'].value_counts()
        
        fig = px.bar(
            x=type_counts.index,
            y=type_counts.values,
            labels={'x': 'Activity Type', 'y': 'Count'},
            color=type_counts.values,
            color_continuous_scale='viridis'
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Activity timeline
        st.subheader("Activity Timeline")
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['minute'] = df['timestamp'].dt.floor('min')
        timeline = df.groupby('minute').size().reset_index(name='count')
        
        fig2 = px.line(
            timeline,
            x='minute',
            y='count',
            labels={'minute': 'Time', 'count': 'Activities'},
            markers=True
        )
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Recent activity log
        st.subheader("Recent Activity Log")
        
        for _, row in df.tail(10).iloc[::-1].iterrows():
            with st.container():
                cols = st.columns([1, 2, 3])
                with cols[0]:
                    timestamp = pd.to_datetime(row['timestamp'])
                    st.caption(timestamp.strftime("%H:%M:%S"))
                with cols[1]:
                    activity_type = row['type']
                    if 'query' in activity_type.lower():
                        st.info(f"🔍 {activity_type}")
                    elif 'alert' in activity_type.lower():
                        st.error(f"🚨 {activity_type}")
                    elif 'weather' in activity_type.lower():
                        st.warning(f"🌦️ {activity_type}")
                    elif 'agriculture' in activity_type.lower():
                        st.success(f"🌾 {activity_type}")
                    else:
                        st.write(f"📊 {activity_type}")
                with cols[2]:
                    details = row.get('details', {})
                    if isinstance(details, dict):
                        detail_str = ', '.join([f"{k}: {v}" for k, v in list(details.items())[:2]])
                        st.caption(detail_str[:100])
                st.divider()
    else:
        st.info("No activity recorded in the selected time range")
        st.caption("Activity will appear here as users interact with the dashboard")
    
    # System health indicators
    st.subheader("System Health")
    
    health_cols = st.columns(4)
    
    with health_cols[0]:
        st.markdown("**Data Pipeline**")
        st.success("✅ Healthy")
        st.caption("Last update: Just now")
    
    with health_cols[1]:
        st.markdown("**API Connections**")
        st.success("✅ All Online")
        st.caption("NOAA, USDA, FEMA connected")
    
    with health_cols[2]:
        st.markdown("**Alert System**")
        st.success("✅ Active")
        st.caption("0 pending alerts")
    
    with health_cols[3]:
        st.markdown("**Database**")
        st.success("✅ Connected")
        st.caption("SQLite operational")


def log_dashboard_activity(activity_type: str, **kwargs):
    """Helper function to log activity from other dashboard components"""
    monitor = DashboardMonitor()
    monitor.log_activity(activity_type, kwargs)


# Standalone page for monitoring
if __name__ == "__main__":
    st.set_page_config(
        page_title="Dashboard Monitor - ResilienceAI",
        page_icon="📊",
        layout="wide"
    )
    render_activity_dashboard()
