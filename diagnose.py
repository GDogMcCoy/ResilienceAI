#!/usr/bin/env python3
"""
Quick diagnostic script for ResilienceAI connection issues
"""

import socket
import subprocess
import sys
import os

print("🔍 ResilienceAI Connection Diagnostic")
print("=" * 50)

# Check localhost resolution
print("\n1. Checking localhost resolution...")
try:
    localhost_ip = socket.gethostbyname('localhost')
    print(f"   ✅ localhost resolves to {localhost_ip}")
except Exception as e:
    print(f"   ❌ localhost resolution failed: {e}")

# Test ports 8501-8510
print("\n2. Testing ports 8501-8510...")
for port in range(8501, 8511):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', port))
        if result == 0:
            print(f"   ⚠️  Port {port} is IN USE")
        else:
            print(f"   ✅ Port {port} is FREE")

# Check if Python/Streamlit is installed
print("\n3. Checking Python environment...")
try:
    result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
    print(f"   ✅ Python: {result.stdout.strip()}")
except Exception as e:
    print(f"   ❌ Python check failed: {e}")

try:
    result = subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ Streamlit: {result.stdout.strip()}")
    else:
        print(f"   ❌ Streamlit not found")
except Exception as e:
    print(f"   ❌ Streamlit check failed: {e}")

# Check data files
print("\n4. Checking data files...")
data_file = "data/processed/county_features.csv"
if os.path.exists(data_file):
    size = os.path.getsize(data_file)
    print(f"   ✅ {data_file} exists ({size:,} bytes)")
else:
    print(f"   ❌ {data_file} NOT FOUND")

# Network interface check
print("\n5. Checking network interfaces...")
try:
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    print(f"   ✅ Hostname: {hostname}")
    print(f"   ✅ IP: {ip}")
except Exception as e:
    print(f"   ❌ Network check failed: {e}")

print("\n" + "=" * 50)
print("💡 Recommendations:")
print("   1. Use a FREE port from the list above")
print("   2. Run: streamlit run app/dashboard.py --server.port PORT")
print("   3. If all ports in use, kill existing Python processes")
print("   4. Check Windows Defender/Firewall settings")
