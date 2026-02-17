"""
ResilienceAI - Archia API Client
Client for communicating with Archia MCP agent runtime.
"""
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ArchiaConfig:
    """Configuration for Archia API connection."""
    base_url: str = "https://api.archia.app/v1"
    api_key: Optional[str] = None
    timeout: int = 30
    
    
class ArchiaClient:
    """
    Client for Archia MCP agent runtime.
    
    Provides methods to:
    - Send natural language queries to the agent
    - Execute MCP tools directly
    - Stream responses for long-running queries
    - Manage agent sessions
    """
    
"""
ResilienceAI - Archia Cloud API Client
Official Client for the MUIDSI Hackathon 2026.
"""
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ArchiaConfig:
    """Configuration for Archia Cloud API connection."""
    # Official Hackathon Registry URL
    base_url: str = "https://registry.archia.app/v1"
    api_key: Optional[str] = None
    timeout: int = 60
    
    
class ArchiaClient:
    """
    Client for Archia Cloud Agent Runtime.
    
    Implements the Patterns from the MUIDSI 2026 Hackathon Guide:
    - Base URL: https://registry.archia.app/v1
    - Endpoint: /v1/responses
    - Model Pattern: agent:your_agent_name
    """
    
    def __init__(self, config: Optional[ArchiaConfig] = None):
        """Initialize Archia Cloud client."""
        self.config = config or ArchiaConfig()
        self.session = requests.Session()
        
        if self.config.api_key:
            # Bearer token is used for Archia Cloud Registry
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "ResilienceAI-Orchestrator/3.0"
            })
    
    def query(self, 
              query: str, 
              agent_name: str = "ResilienceAI",
              stream: bool = False) -> Dict[str, Any]:
        """
        Invokes an Archia Agent in the Cloud.
        Follows the documentation: POST /v1/responses
        """
        import streamlit as st
        
        # Check for Local Mode Toggle
        use_local = True
        if 'agent_config' in st.session_state:
            use_local = st.session_state.agent_config.get('use_local_agent', True)
            
        if use_local:
            return self._fallback_to_local(query)
            
        # Official Cloud Registry Payload
        payload = {
            "model": f"agent:{agent_name}",
            "input": query,
            "stream": stream
        }
        
        try:
            # Official endpoint: /v1/responses
            # Using session defaults (Bearer Token)
            response = self.session.post(
                f"{self.config.base_url}/responses",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                # Archia Cloud returns { "output": [...] }
                data = response.json()
                # Adapt Cloud response to Dashboard format
                output = data.get("output", [])
                answer = ""
                if output and len(output) > 0:
                    # Extract text content from the first output item
                    content = output[0].get("content", [])
                    if content and len(content) > 0:
                        answer = content[0].get("text", "")
                
                return {
                    "answer": answer,
                    "data": data.get("metadata", {}).get("tool_data", []),
                    "thought": data.get("metadata", {}).get("reasoning", ""),
                    "tool_calls": data.get("metadata", {}).get("tool_calls", []),
                    "plan": data.get("metadata", {}).get("plan", []),
                    "mode": "Archia Cloud"
                }
            else:
                return {
                    "error": f"Archia Cloud Error ({response.status_code}): {response.text}",
                    "local_data": self._fallback_to_local(query),
                    "mode": "Cloud Fallback"
                }
                
        except Exception as e:
            return {
                "error": f"Connection Error: {str(e)}",
                "local_data": self._fallback_to_local(query),
                "mode": "Cloud Fallback"
            }

    def _fallback_to_local(self, query: str) -> Dict[str, Any]:
        """Fallback to local ResilienceAgent if Cloud unavailable or local mode active."""
        try:
            from src.agent import ResilienceAgent
            import streamlit as st
            
            # Reuse agent from session state if available
            if 'local_agent' in st.session_state and st.session_state.local_agent is not None:
                agent = st.session_state.local_agent
            else:
                agent = ResilienceAgent()
            
            # Call the agent's internal query router
            result = agent.query(query)
            result["mode"] = "Local Mode (Edge Node)"
            return result
                
        except Exception as e:
            return {
                "error": f"Local agent fallback failed: {str(e)}",
                "mode": "Critical Error"
            }

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents in the workspace."""
        try:
            response = self.session.get(
                f"{self.config.base_url}/agent",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return [{"error": str(e)}]


# Convenience function for quick queries
def ask_agent(query: str, 
              archia_url: str = "http://localhost:8080",
              api_key: Optional[str] = None) -> str:
    """
    Quick function to ask the ResilienceAI agent a question.
    
    Args:
        query: Natural language query
        archia_url: Archia server URL
        api_key: Optional API key
        
    Returns:
        Agent response text
    """
    config = ArchiaConfig(base_url=archia_url, api_key=api_key)
    client = ArchiaClient(config)
    
    result = client.query(query)
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    return result.get("response", "No response received")


if __name__ == "__main__":
    # Test the client
    client = ArchiaClient()
    
    # Check health
    health = client.health_check()
    print(f"Health: {health}")
    
    # Test query
    result = client.query("Which Missouri counties are most vulnerable?")
    print(f"\nQuery result: {json.dumps(result, indent=2)}")
