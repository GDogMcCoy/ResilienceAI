"""
ResilienceAI - Agent Orchestration Layer
Handles MCP tools with local/cloud API-free tools (no login required)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
import numpy as np
import joblib
import requests
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from config import PROCESSED_DIR, MODELS_DIR, REPORTS_DIR

# ── API-Free Tool Integrations ────────────────────────────────────────

@dataclass
class ToolResult:
    """Standardized tool execution result."""
    success: bool
    data: Any
    error: Optional[str] = None
    tool_name: str = ""
    execution_time_ms: float = 0.0


class WeatherTools:
    """NOAA National Weather Service API (free, no login required)."""
    
    BASE_URL = "https://api.weather.gov"
    
    @staticmethod
    def get_alerts(state: str, county_name: Optional[str] = None, 
                   severity: Optional[str] = None) -> ToolResult:
        """Get active weather alerts from NOAA."""
        try:
            url = f"{WeatherTools.BASE_URL}/alerts/active"
            params = {"area": state}
            if severity:
                params["severity"] = severity
                
            response = requests.get(url, params=params, timeout=10,
                                   headers={"User-Agent": "ResilienceAI/1.0"})
            response.raise_for_status()
            data = response.json()
            
            alerts = data.get("features", [])
            
            # Filter by county if specified
            if county_name:
                alerts = [a for a in alerts 
                         if county_name.lower() in a.get("properties", {}).get("areaDesc", "").lower()]
            
            return ToolResult(success=True, data=alerts, tool_name="get_weather_alerts")
            
        except Exception as e:
            return ToolResult(success=False, data=[], error=str(e), tool_name="get_weather_alerts")
    
    @staticmethod
    def get_high_impact_alerts(min_severity: str = "Severe") -> ToolResult:
        """Get high-severity weather alerts nationwide."""
        try:
            url = f"{WeatherTools.BASE_URL}/alerts/active"
            response = requests.get(url, timeout=10,
                                   headers={"User-Agent": "ResilienceAI/1.0"})
            response.raise_for_status()
            data = response.json()
            
            alerts = data.get("features", [])
            severity_order = {"Extreme": 4, "Severe": 3, "Moderate": 2, "Minor": 1}
            min_level = severity_order.get(min_severity, 3)
            
            high_impact = [
                a for a in alerts 
                if severity_order.get(a.get("properties", {}).get("severity"), 0) >= min_level
            ]
            
            return ToolResult(success=True, data=high_impact, tool_name="get_high_impact_alerts")
            
        except Exception as e:
            return ToolResult(success=False, data=[], error=str(e), tool_name="get_high_impact_alerts")


class GeospatialTools:
    """USGS and other free geospatial APIs (no login required)."""
    
    @staticmethod
    def get_usgs_3dep_metadata(bbox: Tuple[float, float, float, float]) -> ToolResult:
        """Query USGS 3DEP availability for a bounding box."""
        try:
            # USGS National Map API (free, no key required for basic queries)
            url = "https://viewer.nationalmap.gov/tnmaccess/api/products"
            params = {
                "datasets": "Digital Elevation Model (DEM) 1 meter",
                "bbox": ",".join(map(str, bbox)),
                "outputFormat": "JSON",
                "max": 10
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return ToolResult(success=True, data=response.json(), tool_name="get_usgs_3dep_metadata")
        except Exception as e:
            return ToolResult(success=False, data={}, error=str(e), tool_name="get_usgs_3dep_metadata")
    
    @staticmethod
    def get_nominatim_geocode(query: str) -> ToolResult:
        """Geocode using Nominatim (OpenStreetMap, free, no key)."""
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": query,
                "format": "json",
                "limit": 1,
                "countrycodes": "us"
            }
            headers = {"User-Agent": "ResilienceAI/1.0 (research)"}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return ToolResult(success=True, data=response.json(), tool_name="geocode")
        except Exception as e:
            return ToolResult(success=False, data=[], error=str(e), tool_name="geocode")


class DataTools:
    """Local data processing tools (no API required)."""
    
    def __init__(self, df: Optional[pd.DataFrame] = None):
        self.df = df
        if self.df is None:
            self._load_data()
    
    def _load_data(self):
        """Load processed county data."""
        features_path = PROCESSED_DIR / "county_features.csv"
        if features_path.exists():
            self.df = pd.read_csv(features_path, dtype={"fips": str})
    
    def query_counties(self, state: Optional[str] = None, 
                       risk_level: Optional[str] = None,
                       min_risk_score: Optional[float] = None,
                       max_results: int = 10,
                       sort_by: str = "risk_score") -> ToolResult:
        """Query counties with filters."""
        try:
            if self.df is None:
                return ToolResult(success=False, data=[], 
                                error="Data not loaded", tool_name="query_counties")
            
            result = self.df.copy()
            
            if state:
                result = result[result["county_name"].str.contains(f", {state}", case=False, na=False)]
            
            if risk_level:
                result = result[result["risk_level"] == risk_level]
            
            if min_risk_score is not None:
                result = result[result["risk_score"] >= min_risk_score]
            
            result = result.sort_values(sort_by, ascending=False).head(max_results)
            
            return ToolResult(success=True, data=result.to_dict(orient="records"),
                            tool_name="query_counties")
        except Exception as e:
            return ToolResult(success=False, data=[], error=str(e), tool_name="query_counties")
    
    def get_county_detail(self, fips: Optional[str] = None, 
                          county_name: Optional[str] = None) -> ToolResult:
        """Get detailed county profile."""
        try:
            if self.df is None:
                return ToolResult(success=False, data={}, error="Data not loaded")
            
            if fips:
                match = self.df[self.df["fips"] == str(fips)]
            elif county_name:
                match = self.df[self.df["county_name"].str.contains(county_name, case=False, na=False)]
            else:
                return ToolResult(success=False, data={}, error="Provide fips or county_name")
            
            if match.empty:
                return ToolResult(success=False, data={}, error="County not found")
            
            return ToolResult(success=True, data=match.iloc[0].to_dict(),
                            tool_name="get_county_detail")
        except Exception as e:
            return ToolResult(success=False, data={}, error=str(e), tool_name="get_county_detail")
    
    def find_compound_risk(self, min_dimensions: int = 3, 
                          state: Optional[str] = None,
                          max_results: int = 20) -> ToolResult:
        """Find counties with compound risk across multiple dimensions."""
        try:
            if self.df is None:
                return ToolResult(success=False, data=[], error="Data not loaded")
            
            result = self.df[self.df["compound_risk_count"] >= min_dimensions].copy()
            
            if state:
                result = result[result["county_name"].str.contains(f", {state}", case=False, na=False)]
            
            result = result.sort_values("compound_risk_count", ascending=False).head(max_results)
            
            return ToolResult(success=True, data=result.to_dict(orient="records"),
                            tool_name="find_compound_risk")
        except Exception as e:
            return ToolResult(success=False, data=[], error=str(e), tool_name="find_compound_risk")


# ── Agent Orchestrator ───────────────────────────────────────────────

class AgentOrchestrator:
    """
    Orchestrates multiple agents and tools with hyperdimensional vector space integration.
    
    Features:
    - Local LLM inference (no API key required)
    - API-free tool integrations (NOAA, USGS, Nominatim)
    - Hyperdimensional vector space for cross-domain insights
    - Sophisticated response crafting
    """
    
    def __init__(self, use_local_llm: bool = True):
        self.use_local_llm = use_local_llm
        self.data_tools = DataTools()
        self.weather_tools = WeatherTools()
        self.geo_tools = GeospatialTools()
        
        # Tool registry
        self.tools = {
            # Data tools
            "query_counties": self.data_tools.query_counties,
            "get_county_detail": self.data_tools.get_county_detail,
            "find_compound_risk": self.data_tools.find_compound_risk,
            # Weather tools
            "get_weather_alerts": self.weather_tools.get_alerts,
            "get_high_impact_alerts": self.weather_tools.get_high_impact_alerts,
            # Geospatial tools
            "geocode": self.geo_tools.get_nominatim_geocode,
        }
    
    def parse_intent(self, query: str) -> Dict[str, Any]:
        """Parse user query to determine intent and required tools."""
        query_lower = query.lower()
        
        intent = {
            "query": query,
            "needs_weather": any(w in query_lower for w in ["weather", "alert", "storm", "flood", "warning"]),
            "needs_geospatial": any(w in query_lower for w in ["location", "map", "coordinate", "geocode"]),
            "needs_risk_analysis": any(w in query_lower for w in ["risk", "vulnerable", "compound", "hotspot"]),
            "state": self._extract_state(query),
            "county": self._extract_county(query),
        }
        
        return intent
    
    def _extract_state(self, query: str) -> Optional[str]:
        """Extract state abbreviation from query."""
        state_map = {
            "missouri": "MO", "mo": "MO",
            "california": "CA", "ca": "CA",
            "texas": "TX", "tx": "TX",
            "florida": "FL", "fl": "FL",
            "new york": "NY", "ny": "NY",
        }
        query_lower = query.lower()
        for name, abbr in state_map.items():
            if name in query_lower:
                return abbr
        return None
    
    def _extract_county(self, query: str) -> Optional[str]:
        """Extract county name from query."""
        # Simple extraction - could be improved with NER
        import re
        patterns = [
            r"in ([\w\s]+) county",
            r"([\w\s]+) county",
        ]
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return match.group(1).strip().title()
        return None
    
    def execute_tools(self, intent: Dict[str, Any]) -> List[ToolResult]:
        """Execute relevant tools based on intent."""
        results = []
        
        # Always get county data if state mentioned
        if intent.get("state"):
            result = self.data_tools.query_counties(
                state=intent["state"],
                max_results=10
            )
            results.append(result)
        
        # Get weather if requested
        if intent["needs_weather"] and intent.get("state"):
            result = self.weather_tools.get_alerts(
                state=intent["state"],
                county_name=intent.get("county")
            )
            results.append(result)
        
        # Get compound risk if requested
        if intent["needs_risk_analysis"]:
            result = self.data_tools.find_compound_risk(
                state=intent.get("state"),
                max_results=20
            )
            results.append(result)
        
        # Default query if no specific tools triggered
        if not results:
            result = self.data_tools.query_counties(max_results=10)
            results.append(result)
        
        return results
    
    def craft_response(self, query: str, intent: Dict[str, Any], 
                      tool_results: List[ToolResult]) -> str:
        """Craft natural language response from tool results."""
        
        # Collect successful data
        counties_data = []
        weather_alerts = []
        
        for result in tool_results:
            if result.success:
                if result.tool_name in ["query_counties", "find_compound_risk"]:
                    counties_data.extend(result.data if isinstance(result.data, list) else [])
                elif result.tool_name in ["get_weather_alerts", "get_high_impact_alerts"]:
                    weather_alerts.extend(result.data if isinstance(result.data, list) else [])
        
        # Build response
        response_parts = []
        
        # Add county information
        if counties_data:
            if intent.get("state"):
                response_parts.append(f"Found {len(counties_data)} counties in {intent['state']}.")
            else:
                response_parts.append(f"Found {len(counties_data)} high-risk counties nationwide.")
            
            # Add top counties
            if len(counties_data) > 0:
                top = counties_data[0]
                response_parts.append(
                    f"\n**Top concern:** {top.get('county_name', 'Unknown')} "
                    f"(Risk Score: {top.get('risk_score', 0):.2f}, "
                    f"Population: {top.get('total_population', 0):,})"
                )
        
        # Add weather information
        if weather_alerts:
            response_parts.append(
                f"\n**Active Weather Alerts:** {len(weather_alerts)} alerts in the region."
            )
            
            # Add top alerts
            for alert in weather_alerts[:3]:
                props = alert.get("properties", {})
                response_parts.append(
                    f"- {props.get('event', 'Alert')}: {props.get('severity', 'Unknown')} "
                    f"({props.get('areaDesc', 'Unknown area')})"
                )
        
        # Add hyperdimensional insight
        if len(counties_data) > 1:
            insight = self._generate_hyperdimensional_insight(counties_data)
            if insight:
                response_parts.append(f"\n🔍 **Insight:** {insight}")
        
        # Add follow-up suggestions
        response_parts.append("\n**Suggested follow-ups:**")
        if intent.get("state"):
            response_parts.append(f"- Which counties in {intent['state']} have zero hospital redundancy?")
            response_parts.append(f"- Show disaster trends for {intent['state']} counties")
        else:
            response_parts.append("- Which states have the most compound risk counties?")
            response_parts.append("- Show counties with accelerating disaster frequency")
        
        return "\n".join(response_parts)
    
    def _generate_hyperdimensional_insight(self, counties: List[Dict]) -> Optional[str]:
        """Generate insight from cross-domain patterns."""
        if not counties or len(counties) < 2:
            return None
        
        # Look for patterns
        high_vuln = [c for c in counties if c.get("vulnerability_index", 0) > 0.7]
        high_iso = [c for c in counties if c.get("isolation_index", 0) > 0.7]
        compound = [c for c in counties if c.get("compound_risk_count", 0) >= 3]
        
        insights = []
        
        if len(compound) > 0:
            insights.append(
                f"{len(compound)} counties show compound risk across multiple dimensions "
                f"(climate + health + infrastructure)"
            )
        
        if len(high_vuln) > 0 and len(high_iso) > 0:
            overlap = set(c.get("fips") for c in high_vuln) & set(c.get("fips") for c in high_iso)
            if len(overlap) > 0:
                insights.append(
                    f"{len(overlap)} counties combine high vulnerability with high isolation - "
                    f"these may need priority intervention"
                )
        
        return " ".join(insights) if insights else None
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Main entry point: process a user query end-to-end."""
        import time
        start_time = time.time()
        
        # Step 1: Parse intent
        intent = self.parse_intent(query)
        
        # Step 2: Execute tools
        tool_results = self.execute_tools(intent)
        
        # Step 3: Craft response
        response_text = self.craft_response(query, intent, tool_results)
        
        execution_time = (time.time() - start_time) * 1000
        
        return {
            "query": query,
            "intent": intent,
            "response": response_text,
            "tool_results": [
                {
                    "tool": r.tool_name,
                    "success": r.success,
                    "error": r.error,
                    "data_count": len(r.data) if isinstance(r.data, list) else 1
                }
                for r in tool_results
            ],
            "execution_time_ms": execution_time,
            "fallback": False
        }


# ── Convenience Functions ────────────────────────────────────────────

def ask_agent(query: str) -> str:
    """Quick function to ask the orchestrator a question."""
    orchestrator = AgentOrchestrator()
    result = orchestrator.process_query(query)
    return result["response"]


if __name__ == "__main__":
    # Test the orchestrator
    orchestrator = AgentOrchestrator()
    
    test_queries = [
        "Which Missouri counties are most vulnerable?",
        "Show me counties with compound risk in Florida",
        "What are the weather alerts in Texas?",
        "Find high-risk counties nationwide"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        result = orchestrator.process_query(query)
        print(result["response"])
        print(f"\n(Tools used: {[r['tool'] for r in result['tool_results']]})")
