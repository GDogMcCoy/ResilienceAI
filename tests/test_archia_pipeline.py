import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.archia")

API_KEY = os.getenv("ARCHIA_API_KEY")
ENDPOINT = os.getenv("ARCHIA_ENDPOINT", "https://api.archia.app/v1")

def test_health_check():
    """Test basic connectivity and auth."""
    print(f"Testing connectivity to {ENDPOINT}...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Simple GET to health
        response = requests.get(f"{ENDPOINT}/health", headers=headers)
        print(f"GET /health: {response.status_code}")
        if response.status_code == 464:
            print("❌ 464 Error: Likely protocol mismatch (HTTP/2 vs HTTP/1.1) or header issue.")
        else:
            print(f"Response: {response.text}")

        # Test 2: Agent status
        response = requests.get(f"{ENDPOINT}/agents/resilienceai/status", headers=headers)
        print(f"GET /agents/resilienceai/status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

if __name__ == "__main__":
    if not API_KEY:
        print("❌ Error: ARCHIA_API_KEY not found in .env.archia")
    else:
        test_health_check()
