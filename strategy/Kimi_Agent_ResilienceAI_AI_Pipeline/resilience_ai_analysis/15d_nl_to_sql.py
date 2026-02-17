"""
ResilienceAI - Natural Language to SQL Translator
Converts natural language queries to SQL for direct database access.

File: src/nl_interface/nl_to_sql.py
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

try:
    import sqlparse
    SQLPARSE_AVAILABLE = True
except ImportError:
    SQLPARSE_AVAILABLE = False


@dataclass
class SQLQuery:
    """Represents a generated SQL query."""
    query: str
    params: Dict[str, Any]
    explanation: str
    confidence: float


class NLToSQLTranslator:
    """
    Translate natural language to SQL queries.
    
    Uses a hybrid approach:
    1. Pattern-based query generation for common queries
    2. LLM-based generation for complex queries
    3. Schema-aware validation
    """
    
    # Database schema context
    SCHEMA_CONTEXT = """
    Table: county_vulnerability
    Primary Key: fips (TEXT)
    
    Location Columns:
    - fips (TEXT): 5-digit county FIPS code
    - county_name (TEXT): County name
    - state (TEXT): State abbreviation (e.g., MO, CA)
    - state_name (TEXT): Full state name
    
    Demographic Columns:
    - population (INTEGER): Total population
    - median_income (INTEGER): Median household income (USD)
    - poverty_pct (FLOAT): Percentage below poverty line (0-100)
    - elderly_pct (FLOAT): Percentage 65+ years (0-100)
    - uninsured_pct (FLOAT): Percentage without health insurance (0-100)
    - disability_pct (FLOAT): Percentage with disabilities (0-100)
    
    Infrastructure Columns:
    - nearest_hospital_km (FLOAT): Distance to nearest hospital (km)
    - nearest_ems_km (FLOAT): Distance to nearest EMS station (km)
    - hospital_density_50km (FLOAT): Hospitals per 10k population within 50km
    
    Disaster History Columns:
    - total_disasters (INTEGER): Total disaster declarations
    - flood_count (INTEGER): Number of flood declarations
    - tornado_count (INTEGER): Number of tornado declarations
    - fire_count (INTEGER): Number of fire declarations
    
    Risk Score Columns:
    - vulnerability_index (FLOAT): Composite vulnerability (0-1)
    - isolation_index (FLOAT): Infrastructure isolation (0-1)
    - compound_risk_score (FLOAT): Overall risk score (0-1)
    """
    
    # Query templates for common patterns
    QUERY_TEMPLATES = {
        "county_by_name": """
            SELECT * FROM county_vulnerability 
            WHERE county_name = :county_name
            {state_filter}
        """,
        
        "counties_by_state": """
            SELECT * FROM county_vulnerability 
            WHERE state = :state
            ORDER BY compound_risk_score DESC
            LIMIT :limit
        """,
        
        "high_risk_counties": """
            SELECT * FROM county_vulnerability 
            WHERE compound_risk_score > :threshold
            {state_filter}
            ORDER BY compound_risk_score DESC
            LIMIT :limit
        """,
        
        "compound_risk_hotspots": """
            SELECT * FROM county_vulnerability 
            WHERE vulnerability_index > 0.7 
            AND isolation_index > 0.7
            AND compound_risk_score > 0.8
            {state_filter}
            ORDER BY compound_risk_score DESC
            LIMIT :limit
        """,
        
        "worst_hospital_access": """
            SELECT * FROM county_vulnerability 
            WHERE nearest_hospital_km > :distance
            {state_filter}
            ORDER BY nearest_hospital_km DESC
            LIMIT :limit
        """,
        
        "flood_prone_counties": """
            SELECT * FROM county_vulnerability 
            WHERE flood_count > :min_floods
            {state_filter}
            ORDER BY flood_count DESC
            LIMIT :limit
        """,
        
        "compare_counties": """
            SELECT 
                county_name,
                state,
                compound_risk_score,
                vulnerability_index,
                isolation_index,
                nearest_hospital_km,
                total_disasters
            FROM county_vulnerability 
            WHERE fips IN (:fips_list)
            ORDER BY compound_risk_score DESC
        """,
        
        "state_statistics": """
            SELECT 
                state,
                COUNT(*) as num_counties,
                AVG(compound_risk_score) as avg_risk,
                MAX(compound_risk_score) as max_risk,
                AVG(nearest_hospital_km) as avg_hospital_distance,
                SUM(total_disasters) as total_disasters
            FROM county_vulnerability 
            WHERE state = :state
            GROUP BY state
        """,
    }
    
    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize NL-to-SQL translator."""
        self.llm_client = llm_client
    
    def translate(
        self,
        natural_language: str,
        entities: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> SQLQuery:
        """Translate natural language to SQL."""
        text_lower = natural_language.lower()
        
        # Step 1: Try pattern-based translation
        pattern_result = self._try_pattern_translation(text_lower, entities)
        if pattern_result and pattern_result.confidence > 0.8:
            return pattern_result
        
        # Step 2: Use LLM for complex queries
        if self.llm_client:
            llm_result = self._llm_translation(natural_language, entities)
            if llm_result.confidence > 0.7:
                return llm_result
        
        # Step 3: Fall back to best pattern match
        if pattern_result:
            return pattern_result
        
        # Step 4: Return error query
        return SQLQuery(
            query="",
            params={},
            explanation="Could not translate query to SQL",
            confidence=0.0
        )
    
    def _try_pattern_translation(
        self,
        text: str,
        entities: Optional[Dict[str, Any]]
    ) -> Optional[SQLQuery]:
        """Try to match query to a known pattern."""
        entities = entities or {}
        counties = entities.get("counties", [])
        states = entities.get("states", [])
        fips_codes = entities.get("fips_codes", [])
        thresholds = entities.get("risk_thresholds", [])
        
        # Pattern: County by name
        if counties and not states:
            return SQLQuery(
                query=self.QUERY_TEMPLATES["county_by_name"].format(state_filter=""),
                params={"county_name": counties[0]},
                explanation=f"Query for {counties[0]} County",
                confidence=0.9
            )
        
        # Pattern: County by name with state
        if counties and states:
            state_filter = f"AND state = '{states[0]}'"
            return SQLQuery(
                query=self.QUERY_TEMPLATES["county_by_name"].format(state_filter=state_filter),
                params={"county_name": counties[0]},
                explanation=f"Query for {counties[0]} County, {states[0]}",
                confidence=0.95
            )
        
        # Pattern: Counties by state
        if states and not counties:
            return SQLQuery(
                query=self.QUERY_TEMPLATES["counties_by_state"],
                params={"state": states[0], "limit": 10},
                explanation=f"Top 10 highest risk counties in {states[0]}",
                confidence=0.85
            )
        
        # Pattern: High risk counties
        if "high risk" in text or "highest risk" in text:
            threshold = 0.7
            for t in thresholds:
                if t.get("type") == "score":
                    threshold = t.get("value", 0.7)
            
            state_filter = ""
            params = {"threshold": threshold, "limit": 10}
            
            if states:
                state_filter = f"AND state = '{states[0]}'"
                params["state"] = states[0]
            
            return SQLQuery(
                query=self.QUERY_TEMPLATES["high_risk_counties"].format(state_filter=state_filter),
                params=params,
                explanation=f"Counties with risk score above {threshold}",
                confidence=0.85
            )
        
        # Pattern: Compound risk / hotspots
        if "compound risk" in text or "hotspot" in text:
            state_filter = ""
            params = {"limit": 20}
            
            if states:
                state_filter = f"AND state = '{states[0]}'"
                params["state"] = states[0]
            
            return SQLQuery(
                query=self.QUERY_TEMPLATES["compound_risk_hotspots"].format(state_filter=state_filter),
                params=params,
                explanation="Counties with high compound risk",
                confidence=0.85
            )
        
        # Pattern: Worst hospital access
        if "hospital" in text and ("worst" in text or "far" in text or "distance" in text):
            state_filter = ""
            params = {"distance": 50, "limit": 10}
            
            if states:
                state_filter = f"AND state = '{states[0]}'"
                params["state"] = states[0]
            
            return SQLQuery(
                query=self.QUERY_TEMPLATES["worst_hospital_access"].format(state_filter=state_filter),
                params=params,
                explanation="Counties with worst hospital access (>50km)",
                confidence=0.8
            )
        
        # Pattern: Flood-prone counties
        if "flood" in text:
            state_filter = ""
            params = {"min_floods": 5, "limit": 10}
            
            if states:
                state_filter = f"AND state = '{states[0]}'"
                params["state"] = states[0]
            
            return SQLQuery(
                query=self.QUERY_TEMPLATES["flood_prone_counties"].format(state_filter=state_filter),
                params=params,
                explanation="Counties with most flood declarations",
                confidence=0.8
            )
        
        # Pattern: Compare counties
        if fips_codes and len(fips_codes) >= 2:
            return SQLQuery(
                query=self.QUERY_TEMPLATES["compare_counties"],
                params={"fips_list": fips_codes},
                explanation=f"Comparison of {len(fips_codes)} counties",
                confidence=0.85
            )
        
        # Pattern: State statistics
        if "statistics" in text or "summary" in text or "overview" in text:
            if states:
                return SQLQuery(
                    query=self.QUERY_TEMPLATES["state_statistics"],
                    params={"state": states[0]},
                    explanation=f"Summary statistics for {states[0]}",
                    confidence=0.8
                )
        
        return None
    
    def _llm_translation(
        self,
        natural_language: str,
        entities: Optional[Dict[str, Any]]
    ) -> SQLQuery:
        """Use LLM to translate complex queries."""
        if not self.llm_client:
            return SQLQuery(
                query="",
                params={},
                explanation="LLM not available",
                confidence=0.0
            )
        
        prompt = f"""Given the following database schema, translate the natural language query to SQL.

Schema:
{self.SCHEMA_CONTEXT}

Natural Language Query:
{natural_language}

Extracted Entities:
{entities}

Generate a SQL query that answers this question. Return ONLY the SQL query, no explanation.

SQL:"""
        
        try:
            response = self.llm_client.complete(prompt)
            sql_query = response.strip()
            
            if self._validate_query(sql_query):
                return SQLQuery(
                    query=sql_query,
                    params={},
                    explanation="Generated by LLM",
                    confidence=0.75
                )
        except Exception as e:
            print(f"LLM translation failed: {e}")
        
        return SQLQuery(
            query="",
            params={},
            explanation="LLM translation failed",
            confidence=0.0
        )
    
    def _validate_query(self, query: str) -> bool:
        """Validate that generated SQL is safe and correct."""
        dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE"]
        query_upper = query.upper()
        
        for op in dangerous:
            if op in query_upper:
                return False
        
        if not query.strip().upper().startswith("SELECT"):
            return False
        
        return True
