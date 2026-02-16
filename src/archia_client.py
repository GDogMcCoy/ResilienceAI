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
    base_url: str = "http://localhost:8080"
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
    
    def __init__(self, config: Optional[ArchiaConfig] = None):
        """Initialize Archia client."""
        self.config = config or ArchiaConfig()
        self.session = requests.Session()
        
        if self.config.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            })
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Archia server is running."""
        try:
            response = self.session.get(
                f"{self.config.base_url}/health",
                timeout=5
            )
            response.raise_for_status()
            return {"status": "healthy", "data": response.json()}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Cannot connect to Archia server"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def query(self, 
              query: str, 
              session_id: Optional[str] = None,
              stream: bool = False) -> Dict[str, Any]:
        """
        Processes a query using the local ResilienceAgent by default.
        Remote connectivity is disabled until a valid deployment endpoint is confirmed.
        """
        # Always fallback to local for development/hackathon stability
        return self._fallback_to_local(query)
    
    def _stream_query(self, payload: Dict) -> Dict[str, Any]:
        """Stream query response from Archia."""
        response = self.session.post(
            f"{self.config.base_url}/v1/query",
            json=payload,
            stream=True,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        # Collect streamed chunks
        chunks = []
        for line in response.iter_lines():
            if line:
                chunks.append(json.loads(line))
        
        return {"streamed": True, "chunks": chunks}
    
    def _fallback_to_local(self, query: str) -> Dict[str, Any]:
        """Fallback to local ResilienceAgent if Archia unavailable."""
        try:
            from src.agent import ResilienceAgent
            agent = ResilienceAgent()
            
            # Simple keyword-based routing for demo
            query_lower = query.lower()
            
            if "missouri" in query_lower or "mo " in query_lower:
                state = "MO"
                if "flood" in query_lower:
                    result = agent.query_counties(state=state, max_results=10)
                    return {
                        "response": f"Top vulnerable Missouri counties: {len(result)} counties found",
                        "data": result,
                        "tool_calls": [{"tool": "query_counties", "params": {"state": state}}],
                        "fallback": True
                    }
                else:
                    result = agent.get_state_rankings(state, max_results=10)
                    return {
                        "response": f"Missouri county rankings by risk score",
                        "data": result,
                        "tool_calls": [{"tool": "get_state_rankings", "params": {"state": state}}],
                        "fallback": True
                    }
            
            elif "compound risk" in query_lower or "hotspot" in query_lower:
                result = agent.find_compound_risk_counties(min_dimensions=3, max_results=20)
                return {
                    "response": f"Found {len(result)} counties with compound risk (3+ dimensions)",
                    "data": result,
                    "tool_calls": [{"tool": "find_compound_risk_counties", "params": {"min_dimensions": 3}}],
                    "fallback": True
                }
            
            elif "zero redundancy" in query_lower or "single point" in query_lower:
                result = agent.find_zero_redundancy(max_results=20)
                return {
                    "response": f"Found {len(result)} counties with zero hospital redundancy",
                    "data": result,
                    "tool_calls": [{"tool": "find_zero_redundancy", "params": {}}],
                    "fallback": True
                }
            
            elif "accelerating" in query_lower or "trend" in query_lower:
                result = agent.get_disaster_trends(min_acceleration=2.0, max_results=20)
                return {
                    "response": f"Found {len(result)} counties with accelerating disaster frequency",
                    "data": result,
                    "tool_calls": [{"tool": "get_disaster_trends", "params": {"min_acceleration": 2.0}}],
                    "fallback": True
                }
            
            else:
                # Generic query
                result = agent.query_counties(max_results=10)
                return {
                    "response": f"Top 10 highest-risk counties nationwide",
                    "data": result,
                    "tool_calls": [{"tool": "query_counties", "params": {"max_results": 10}}],
                    "fallback": True
                }
                
        except Exception as e:
            return {
                "error": f"Archia server unavailable and local fallback failed: {str(e)}",
                "fallback": True
            }
    
    def execute_tool(self, 
                     tool_name: str, 
                     params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific MCP tool directly.
        
        Args:
            tool_name: Name of the MCP tool
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        payload = {
            "tool": tool_name,
            "params": params,
            "agent": "resilienceai"
        }
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/v1/tools/execute",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of the ResilienceAI agent."""
        try:
            response = self.session.get(
                f"{self.config.base_url}/v1/agents/resilienceai/status",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available MCP tools."""
        try:
            response = self.session.get(
                f"{self.config.base_url}/v1/agents/resilienceai/tools",
                timeout=5
            )
            response.raise_for_status()
            return response.json().get("tools", [])
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
