"""
ResilienceAI - Entity Extractor
Extracts structured entities from natural language queries.

File: src/nl_interface/entity_extractor.py
"""

import re
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# Try to import spaCy for NER
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


@dataclass
class ExtractedEntities:
    """Container for extracted entities."""
    counties: List[str] = field(default_factory=list)
    states: List[str] = field(default_factory=list)
    fips_codes: List[str] = field(default_factory=list)
    disaster_types: List[str] = field(default_factory=list)
    date_ranges: List[Dict[str, Any]] = field(default_factory=list)
    risk_thresholds: List[Dict[str, Any]] = field(default_factory=list)
    intervention_types: List[str] = field(default_factory=list)
    comparison_ops: List[str] = field(default_factory=list)
    numbers: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "counties": self.counties,
            "states": self.states,
            "fips_codes": self.fips_codes,
            "disaster_types": self.disaster_types,
            "date_ranges": self.date_ranges,
            "risk_thresholds": self.risk_thresholds,
            "intervention_types": self.intervention_types,
            "comparison_ops": self.comparison_ops,
            "numbers": self.numbers
        }
    
    def is_empty(self) -> bool:
        """Check if any entities were extracted."""
        return not any([
            self.counties, self.states, self.fips_codes,
            self.disaster_types, self.risk_thresholds
        ])


class EntityExtractor:
    """
    Extract entities from natural language using:
    1. spaCy NER for locations
    2. Custom patterns for domain-specific entities
    3. Gazetteer lookups for counties and states
    """
    
    # Disaster type keywords
    DISASTER_TYPES = {
        "flood": ["flood", "flooding", "flash flood", "river flood"],
        "tornado": ["tornado", "twister", "funnel cloud"],
        "hurricane": ["hurricane", "tropical storm", "cyclone"],
        "wildfire": ["wildfire", "forest fire", "brush fire", "fire"],
        "earthquake": ["earthquake", "seismic", "tremor"],
        "severe_storm": ["severe storm", "thunderstorm", "hail", "wind"],
        "drought": ["drought", "water shortage", "dry spell"],
        "winter_storm": ["winter storm", "blizzard", "ice storm", "snow"],
    }
    
    # Intervention types
    INTERVENTION_TYPES = {
        "add_hospital": ["add hospital", "new hospital", "build hospital"],
        "add_ems": ["add ems", "new ems", "ems station"],
        "reduce_poverty": ["reduce poverty", "poverty reduction"],
        "increase_insurance": ["increase insurance", "expand coverage"],
        "improve_access": ["improve access", "better access"],
        "climate_adaptation": ["climate adaptation", "climate resilience"],
    }
    
    # Comparison operators
    COMPARISON_OPS = {
        "greater_than": ["higher than", "greater than", "above", "more than", "over"],
        "less_than": ["lower than", "less than", "below", "under", "fewer than"],
        "equal_to": ["equal to", "same as", "exactly"],
        "similar_to": ["similar to", "like", "comparable to"],
    }
    
    # State abbreviations and names
    STATE_MAP = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
        "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
        "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
        "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
        "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
        "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
        "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
        "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"
    }
    
    def __init__(self, county_gazetteer_path: Optional[str] = None):
        """Initialize entity extractor."""
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("spaCy model not found. Using rule-based extraction only.")
        
        # Load county gazetteer
        self.county_gazetteer: Dict[str, List[str]] = {}
        self.ambiguous_counties: Set[str] = set()
        self._build_county_gazetteer_from_data()
    
    def _build_county_gazetteer_from_data(self):
        """Build county gazetteer from ResilienceAI data."""
        try:
            import pandas as pd
            from config import PROCESSED_DIR
            
            df = pd.read_parquet(Path(PROCESSED_DIR) / "county_vulnerability.parquet")
            
            for _, row in df.iterrows():
                county_name = row['county_name']
                state = row['state']
                
                if county_name not in self.county_gazetteer:
                    self.county_gazetteer[county_name] = []
                self.county_gazetteer[county_name].append(state)
            
            # Identify ambiguous counties
            for county, states in self.county_gazetteer.items():
                if len(states) > 1:
                    self.ambiguous_counties.add(county)
                    
        except Exception as e:
            print(f"Could not build county gazetteer: {e}")
    
    def extract(
        self,
        text: str,
        intent: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract all entities from text."""
        entities = ExtractedEntities()
        text_lower = text.lower()
        
        # Extract locations (counties, states)
        counties, states = self._extract_locations(text)
        entities.counties = counties
        entities.states = states
        
        # Extract FIPS codes
        entities.fips_codes = self._extract_fips_codes(text)
        
        # Extract disaster types
        entities.disaster_types = self._extract_disaster_types(text_lower)
        
        # Extract date ranges
        entities.date_ranges = self._extract_date_ranges(text_lower)
        
        # Extract risk thresholds
        entities.risk_thresholds = self._extract_risk_thresholds(text_lower)
        
        # Extract intervention types
        entities.intervention_types = self._extract_intervention_types(text_lower)
        
        # Extract comparison operators
        entities.comparison_ops = self._extract_comparison_ops(text_lower)
        
        # Extract numbers
        entities.numbers = self._extract_numbers(text)
        
        return entities.to_dict()
    
    def _extract_locations(self, text: str) -> Tuple[List[str], List[str]]:
        """Extract county and state mentions."""
        counties = []
        states = []
        text_lower = text.lower()
        
        # Use spaCy NER if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "GPE":
                    state_abbr = self._get_state_abbr(ent.text)
                    if state_abbr:
                        states.append(state_abbr)
                    elif "county" in ent.text.lower():
                        county_name = self._normalize_county_name(ent.text)
                        if county_name in self.county_gazetteer:
                            counties.append(county_name)
        
        # Rule-based extraction
        county_patterns = [
            r'([\w\s]+?)(?:\s+county)',
            r'county\s+of\s+([\w\s]+)',
        ]
        
        for pattern in county_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                county_name = self._normalize_county_name(match)
                if county_name in self.county_gazetteer and county_name not in counties:
                    counties.append(county_name)
        
        # Extract state abbreviations and names
        for abbr, name in self.STATE_MAP.items():
            if re.search(r'\b' + abbr + r'\b', text.upper()):
                if abbr not in states:
                    states.append(abbr)
            if re.search(r'\b' + re.escape(name.lower()) + r'\b', text_lower):
                if abbr not in states:
                    states.append(abbr)
        
        return counties, states
    
    def _extract_fips_codes(self, text: str) -> List[str]:
        """Extract FIPS codes (5-digit or 2-3 digit format)."""
        fips_codes = []
        
        # 5-digit FIPS
        pattern5 = r'\b(\d{5})\b'
        matches = re.findall(pattern5, text)
        fips_codes.extend(matches)
        
        # 2-3 format (state-county)
        pattern23 = r'\b(\d{2})[-\s]*(\d{3})\b'
        matches = re.findall(pattern23, text)
        for state, county in matches:
            fips_codes.append(f"{state}{county}")
        
        return fips_codes
    
    def _extract_disaster_types(self, text: str) -> List[str]:
        """Extract disaster type mentions."""
        disaster_types = []
        
        for dtype, keywords in self.DISASTER_TYPES.items():
            for keyword in keywords:
                if keyword in text:
                    if dtype not in disaster_types:
                        disaster_types.append(dtype)
                    break
        
        return disaster_types
    
    def _extract_date_ranges(self, text: str) -> List[Dict[str, Any]]:
        """Extract date range mentions."""
        date_ranges = []
        
        # Pattern: "last X years"
        last_years = re.findall(r'last\s+(\d+)\s+years?', text)
        for years in last_years:
            date_ranges.append({
                "type": "relative",
                "years_back": int(years),
                "description": f"last {years} years"
            })
        
        # Pattern: "between X and Y" or "from X to Y"
        year_range = re.findall(r'(?:between|from)\s+(\d{4})\s+(?:and|to)\s+(\d{4})', text)
        for start, end in year_range:
            date_ranges.append({
                "type": "absolute",
                "start_year": int(start),
                "end_year": int(end),
                "description": f"{start} to {end}"
            })
        
        # Pattern: single year
        single_year = re.findall(r'\b(20\d{2})\b', text)
        for year in single_year:
            date_ranges.append({
                "type": "single",
                "year": int(year),
                "description": str(year)
            })
        
        return date_ranges
    
    def _extract_risk_thresholds(self, text: str) -> List[Dict[str, Any]]:
        """Extract risk threshold mentions."""
        thresholds = []
        
        # Pattern: "above X", "greater than X"
        above_patterns = [
            r'(?:above|greater than|more than|over)\s+(0?\.\d+|\d+\.\d+)',
            r'(?:top|highest)\s+(\d+)',
        ]
        
        for pattern in above_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if float(match) <= 1:
                    thresholds.append({
                        "operator": ">",
                        "value": float(match),
                        "type": "score"
                    })
                else:
                    thresholds.append({
                        "operator": "top_n",
                        "value": int(match),
                        "type": "rank"
                    })
        
        # Pattern: "below X"
        below_match = re.search(r'(?:below|under|less than)\s+(0?\.\d+|\d+\.\d+)', text)
        if below_match:
            thresholds.append({
                "operator": "<",
                "value": float(below_match.group(1)),
                "type": "score"
            })
        
        return thresholds
    
    def _extract_intervention_types(self, text: str) -> List[str]:
        """Extract intervention type mentions."""
        interventions = []
        
        for itype, keywords in self.INTERVENTION_TYPES.items():
            for keyword in keywords:
                if keyword in text:
                    if itype not in interventions:
                        interventions.append(itype)
                    break
        
        return interventions
    
    def _extract_comparison_ops(self, text: str) -> List[str]:
        """Extract comparison operators."""
        ops = []
        
        for op, keywords in self.COMPARISON_OPS.items():
            for keyword in keywords:
                if keyword in text:
                    if op not in ops:
                        ops.append(op)
                    break
        
        return ops
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values from text."""
        numbers = []
        
        # Pattern: decimal numbers
        matches = re.findall(r'\b(\d+\.\d+)\b', text)
        numbers.extend([float(m) for m in matches])
        
        # Pattern: integers (but not FIPS codes)
        matches = re.findall(r'\b(\d{1,3})\b', text)
        numbers.extend([float(m) for m in matches])
        
        return numbers
    
    def _normalize_county_name(self, name: str) -> str:
        """Normalize county name for gazetteer lookup."""
        name = re.sub(r'\s+county$', '', name, flags=re.IGNORECASE).strip()
        name = name.title()
        return name
    
    def _get_state_abbr(self, text: str) -> Optional[str]:
        """Get state abbreviation from text."""
        text_upper = text.upper()
        for abbr, name in self.STATE_MAP.items():
            if text_upper == abbr or text_upper == name.upper():
                return abbr
        return None
    
    def is_ambiguous_county(self, county_name: str) -> bool:
        """Check if county name exists in multiple states."""
        return county_name in self.ambiguous_counties
    
    def get_county_states(self, county_name: str) -> List[str]:
        """Get all states that have a county with this name."""
        return self.county_gazetteer.get(county_name, [])
