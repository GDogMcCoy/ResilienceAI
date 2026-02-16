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
    print("Features: 45 MCP tools | 16 tabs | Real-time streaming")
    print("=" * 50)
    
    # Import and run streamlit
    import subprocess
    import webbrowser
    import socket
    from time import sleep
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], check=True)
        print("✅ Streamlit installed")
    
    # Find available port
    def find_free_port(start_port=8501, max_port=8510):
        for port in range(start_port, max_port + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) != 0:
                    return port
        return 8511  # Fallback
    
    PORT = find_free_port()
    
    # Launch dashboard
    dashboard_path = Path(__file__).parent / "app" / "dashboard.py"
    
    print(f"📊 Loading dashboard from: {dashboard_path}")
    print(f"🌐 Opening browser at: http://localhost:{PORT}")
    print("\nPress Ctrl+C to stop\n")
    
    # Open browser after short delay
    def open_browser():
        sleep(3)
        webbrowser.open(f"http://localhost:{PORT}")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(dashboard_path),
        "--server.port", str(PORT),
        "--server.headless", "false"
    ])
