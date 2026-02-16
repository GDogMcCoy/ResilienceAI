#!/usr/bin/env python3
"""
ResilienceAI Dashboard Launcher
Main entry point for running the dashboard
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Run the dashboard
if __name__ == "__main__":
    print("🚀 Starting ResilienceAI Dashboard...")
    print("=" * 50)
    print("Features: 38 MCP tools | 16 tabs | Real-time streaming")
    print("=" * 50)
    
    # Import and run streamlit
    import subprocess
    import webbrowser
    from time import sleep
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], check=True)
        print("✅ Streamlit installed")
    
    # Launch dashboard
    dashboard_path = Path(__file__).parent / "app" / "dashboard.py"
    
    print(f"📊 Loading dashboard from: {dashboard_path}")
    print("🌐 Opening browser at: http://localhost:8501")
    print("\nPress Ctrl+C to stop\n")
    
    # Open browser after short delay
    def open_browser():
        sleep(3)
        webbrowser.open("http://localhost:8501")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(dashboard_path),
        "--server.port", "8501",
        "--server.headless", "false"
    ])
