# ResilienceAI FEMA Disaster Data Enhancement Framework

## Executive Summary

This document provides a comprehensive framework for enhancing FEMA disaster data integration in the ResilienceAI platform. The current implementation provides basic disaster declaration retrieval and simple feature engineering. This enhancement framework introduces advanced disaster analysis capabilities, pattern detection, predictive modeling, and comprehensive disaster intelligence.

---

## 1. Current State Analysis

### 1.1 Existing FEMA Integration

**Current Implementation Location:** `src/download_data.py`, `src/feature_engineering.py`

**Current Capabilities:**
- Basic FEMA OpenFEMA API v2 integration
- Disaster declaration summaries download (paginated)
- Simple disaster count per county
- Basic disaster type classification (Flood, Hurricane, Fire, Tornado, Severe Storm)
- Recent disaster filtering (2015+)
- Temporal disaster acceleration calculation

**Current Limitations:**
- No damage cost estimation
- Limited disaster severity assessment
- No geographic clustering analysis
- Basic temporal pattern detection
- No recovery time analysis
- Limited disaster prediction models
- No FEMA NRI (National Risk Index) integration
- Missing IA (Individual Assistance) and PA (Public Assistance) data

### 1.2 Current Data Sources

```python
# Current FEMA API endpoint
FEMA_API_URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"

# Current feature groups in config.py
FEATURE_GROUPS = {
    "disaster_history": [
        "disaster_count",
        "disasters_2015_2025",
        "disasters_2005_2014",
        "disaster_acceleration",
        "flood_count",
        "hurricane_count",
        "fire_count",
        "tornado_count"
    ]
}
```

---

## 2. Enhanced FEMA Data Architecture

### 2.1 Multi-Source FEMA Data Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENHANCED FEMA DATA ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   OpenFEMA API  │  │   FEMA NRI      │  │   FEMA IA/PA    │             │
│  │   v1/v2/v3      │  │   Data          │  │   Data          │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│           ▼                    ▼                    ▼                       │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │              FEMA Data Ingestion Layer                       │           │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │           │
│  │  │  Disaster    │ │  Risk Index  │ │  Assistance  │         │           │
│  │  │  Declarations│ │  Data        │ │  Data        │         │           │
│  │  └──────────────┘ └──────────────┘ └──────────────┘         │           │
│  └────────────────────────┬────────────────────────────────────┘           │
│                           │                                                 │
│                           ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │              FEMA Data Processing Layer                      │           │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │           │
│  │  │  Disaster    │ │  Severity    │ │  Cost        │         │           │
│  │  │  Classification│ Assessment   │ │  Estimation  │         │           │
│  │  └──────────────┘ └──────────────┘ └──────────────┘         │           │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │           │
│  │  │  Temporal    │ │  Geographic  │ │  Recovery    │         │           │
│  │  │  Analysis    │ │  Clustering  │ │  Analysis    │         │           │
│  │  └──────────────┘ └──────────────┘ └──────────────┘         │           │
│  └────────────────────────┬────────────────────────────────────┘           │
│                           │                                                 │
│                           ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │              FEMA Intelligence Layer                         │           │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │           │
│  │  │  Pattern     │ │  Prediction  │ │  Risk        │         │           │
│  │  │  Detection   │ │  Models      │ │  Scoring     │         │           │
│  │  └──────────────┘ └──────────────┘ └──────────────┘         │           │
│  └─────────────────────────────────────────────────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Enhanced Data Models

```python
# src/models/fema_models.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from enum import Enum
import pandas as pd
import numpy as np

class DisasterType(Enum):
    """FEMA disaster type classification."""
    FLOOD = "Flood"
    HURRICANE = "Hurricane"
    TORNADO = "Tornado"
    SEVERE_STORM = "Severe Storm(s)"
    WILDFIRE = "Fire"
    EARTHQUAKE = "Earthquake"
    DROUGHT = "Drought"
    WINTER_STORM = "Snowstorm"
    TROPICAL_STORM = "Tropical Storm"
    COASTAL_STORM = "Coastal Storm"
    MUDSLIDE = "Mud/Landslide"
    TSUNAMI = "Tsunami"
    VOLCANO = "Volcanic Eruption"
    CHEMICAL = "Chemical"
    BIOLOGICAL = "Biological"
    OTHER = "Other"

class DisasterSeverity(Enum):
    """Disaster severity classification."""
    MINOR = 1
    MODERATE = 2
    MAJOR = 3
    SEVERE = 4
    CATASTROPHIC = 5

class AssistanceType(Enum):
    """FEMA assistance types."""
    IA = "Individual Assistance"
    PA = "Public Assistance"
    HMGP = "Hazard Mitigation Grant Program"
    SBA = "Small Business Administration"

@dataclass
class FEMADeclaration:
    """Enhanced FEMA disaster declaration model."""
    disaster_number: str
    declaration_date: datetime
    incident_type: DisasterType
    declaration_title: str
    state: str
    state_fips: str
    county_fips: Optional[str]
    county_name: Optional[str]
    
    # Enhanced fields
    severity_score: float = 0.0
    estimated_damage: Optional[float] = None
    ia_approved: bool = False
    pa_approved: bool = False
    hmgp_approved: bool = False
    
    # Temporal fields
    incident_begin_date: Optional[datetime] = None
    incident_end_date: Optional[datetime] = None
    disaster_closeout_date: Optional[datetime] = None
    
    # Financial fields
    ia_amount: float = 0.0
    pa_amount: float = 0.0
    hmgp_amount: float = 0.0
    total_obligated: float = 0.0
    
    def calculate_duration_days(self) -> Optional[int]:
        """Calculate incident duration in days."""
        if self.incident_begin_date and self.incident_end_date:
            return (self.incident_end_date - self.incident_begin_date).days
        return None
    
    def calculate_recovery_time(self) -> Optional[int]:
        """Calculate recovery time (declaration to closeout)."""
        if self.disaster_closeout_date:
            return (self.disaster_closeout_date - self.declaration_date).days
        return None

@dataclass
class DisasterMetrics:
    """Comprehensive disaster metrics per geographic area."""
    fips: str
    county_name: str
    state: str
    
    # Count metrics
    total_disasters: int = 0
    disasters_by_type: Dict[DisasterType, int] = field(default_factory=dict)
    disasters_by_severity: Dict[DisasterSeverity, int] = field(default_factory=dict)
    
    # Temporal metrics
    first_disaster_date: Optional[datetime] = None
    last_disaster_date: Optional[datetime] = None
    avg_inter_disaster_days: Optional[float] = None
    disaster_acceleration: float = 0.0
    
    # Financial metrics
    total_ia_amount: float = 0.0
    total_pa_amount: float = 0.0
    total_hmgp_amount: float = 0.0
    total_obligated: float = 0.0
    avg_cost_per_disaster: float = 0.0
    
    # Recovery metrics
    avg_recovery_days: Optional[float] = None
    max_recovery_days: Optional[int] = None
    min_recovery_days: Optional[int] = None
    
    # Risk metrics
    composite_risk_score: float = 0.0
    frequency_trend: str = "stable"  # increasing, decreasing, stable
    severity_trend: str = "stable"

@dataclass
class TemporalPattern:
    """Temporal disaster pattern analysis."""
    fips: str
    seasonality_score: float = 0.0
    peak_months: List[int] = field(default_factory=list)
    trend_direction: str = "stable"
    trend_slope: float = 0.0
    cyclical_periods: List[int] = field(default_factory=list)
    anomaly_years: List[int] = field(default_factory=list)

@dataclass
class GeographicCluster:
    """Geographic disaster cluster analysis."""
    cluster_id: int
    center_lat: float
    center_lon: float
    counties: List[str] = field(default_factory=list)
    primary_disaster_types: List[DisasterType] = field(default_factory=list)
    cluster_risk_score: float = 0.0
    hotspot_score: float = 0.0
```

---

## 3. Enhanced FEMA API Client

### 3.1 Multi-Version FEMA API Client

```python
# src/clients/fema_client.py

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Iterator
from pathlib import Path
import json
import time
from dataclasses import asdict

class FEMAAPIClient:
    """
    Enhanced FEMA OpenFEMA API client with multi-version support.
    
    Supports:
    - OpenFEMA API v1, v2, v3
    - FEMA NRI (National Risk Index)
    - FEMA IA/PA data
    - Pagination and caching
    - Rate limiting
    """
    
    BASE_URLS = {
        "v1": "https://www.fema.gov/api/open/v1",
        "v2": "https://www.fema.gov/api/open/v2",
        "v3": "https://www.fema.gov/api/open/v3",
        "nri": "https://hazards.fema.gov/nri",
    }
    
    def __init__(self, version: str = "v2", cache_dir: Optional[Path] = None):
        self.version = version
        self.base_url = self.BASE_URLS.get(version, self.BASE_URLS["v2"])
        self.cache_dir = cache_dir or Path("data/cache/fema")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ResilienceAI/1.0 (Research Tool)",
            "Accept": "application/json"
        })
        self._rate_limit_delay = 0.5  # seconds between requests
        
    def _make_request(self, endpoint: str, params: Dict = None, 
                      use_cache: bool = True) -> Dict:
        """Make API request with caching and rate limiting."""
        url = f"{self.base_url}/{endpoint}"
        cache_key = f"{endpoint}_{hash(str(params))}.json"
        cache_path = self.cache_dir / cache_key
        
        if use_cache and cache_path.exists():
            cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if cache_age < timedelta(hours=24):
                with open(cache_path) as f:
                    return json.load(f)
        
        time.sleep(self._rate_limit_delay)
        response = self.session.get(url, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()
        
        if use_cache:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        
        return data
    
    def get_disaster_declarations(
        self,
        state: Optional[str] = None,
        county: Optional[str] = None,
        disaster_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_ia: bool = True,
        include_pa: bool = True,
        include_hmgp: bool = True,
        max_records: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch disaster declarations with comprehensive filtering.
        
        Args:
            state: State abbreviation (e.g., 'MO')
            county: County name
            disaster_type: Incident type filter
            start_date: Filter declarations after this date
            end_date: Filter declarations before this date
            include_ia: Include Individual Assistance data
            include_pa: Include Public Assistance data
            include_hmgp: Include Hazard Mitigation data
            max_records: Maximum records to fetch
            
        Returns:
            DataFrame with disaster declarations
        """
        all_records = []
        skip = 0
        page_size = 10000
        
        # Build filter string
        filters = []
        if state:
            filters.append(f"state eq '{state}'")
        if county:
            filters.append(f"designatedArea eq '{county}'")
        if disaster_type:
            filters.append(f"incidentType eq '{disaster_type}'")
        if start_date:
            filters.append(f"declarationDate ge '{start_date.isoformat()}'")
        if end_date:
            filters.append(f"declarationDate le '{end_date.isoformat()}'")
        
        filter_str = " and ".join(filters) if filters else None
        
        while True:
            params = {
                "$skip": skip,
                "$top": page_size,
                "$format": "json",
                "$orderby": "declarationDate desc"
            }
            if filter_str:
                params["$filter"] = filter_str
            
            data = self._make_request(
                "DisasterDeclarationsSummaries",
                params=params
            )
            
            records = data.get("DisasterDeclarationsSummaries", [])
            if not records:
                break
            
            all_records.extend(records)
            
            if max_records and len(all_records) >= max_records:
                all_records = all_records[:max_records]
                break
            
            if len(records) < page_size:
                break
            
            skip += page_size
            print(f"  Fetched {len(all_records)} disaster records...")
        
        df = pd.DataFrame(all_records)
        
        # Enhance with additional data
        if include_ia and len(df) > 0:
            df = self._enrich_with_ia_data(df)
        if include_pa and len(df) > 0:
            df = self._enrich_with_pa_data(df)
        if include_hmgp and len(df) > 0:
            df = self._enrich_with_hmgp_data(df)
        
        return df
    
    def _enrich_with_ia_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich declarations with Individual Assistance data."""
        # Fetch IA program declarations
        ia_data = self._fetch_all_records("IndividualAssistanceProgramDeclarations")
        ia_df = pd.DataFrame(ia_data)
        
        if len(ia_df) > 0:
            # Merge on disasterNumber
            df = df.merge(
                ia_df[["disasterNumber", "iaProgramDeclared", "totalDamage"]],
                on="disasterNumber",
                how="left"
            )
        
        return df
    
    def _enrich_with_pa_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich declarations with Public Assistance data."""
        pa_data = self._fetch_all_records("PublicAssistanceProgramDeclarations")
        pa_df = pd.DataFrame(pa_data)
        
        if len(pa_df) > 0:
            df = df.merge(
                pa_df[["disasterNumber", "paProgramDeclared", "projectAmount"]],
                on="disasterNumber",
                how="left"
            )
        
        return df
    
    def _enrich_with_hmgp_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich declarations with Hazard Mitigation data."""
        hmgp_data = self._fetch_all_records("HazardMitigationProgramDeclarations")
        hmgp_df = pd.DataFrame(hmgp_data)
        
        if len(hmgp_df) > 0:
            df = df.merge(
                hmgp_df[["disasterNumber", "hmProgramDeclared"]],
                on="disasterNumber",
                how="left"
            )
        
        return df
    
    def _fetch_all_records(self, endpoint: str) -> List[Dict]:
        """Fetch all records from an endpoint with pagination."""
        all_records = []
        skip = 0
        page_size = 10000
        
        while True:
            params = {"$skip": skip, "$top": page_size, "$format": "json"}
            data = self._make_request(endpoint, params)
            
            # Get the actual records (key varies by endpoint)
            records_key = endpoint
            if endpoint.startswith("I"):
                records_key = "IndividualAssistanceProgramDeclarations"
            elif endpoint.startswith("P"):
                records_key = "PublicAssistanceProgramDeclarations"
            elif endpoint.startswith("H"):
                records_key = "HazardMitigationProgramDeclarations"
            
            records = data.get(records_key, [])
            if not records:
                break
            
            all_records.extend(records)
            
            if len(records) < page_size:
                break
            
            skip += page_size
        
        return all_records
    
    def get_nri_data(self, state: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch FEMA National Risk Index data.
        
        The NRI provides standardized risk scores for 18 natural hazards
        plus social vulnerability and community resilience factors.
        """
        # NRI data is available as a downloadable dataset
        nri_url = "https://hazards.fema.gov/nri/Content/StaticDocuments/data-download/NRI_Table_Counties.zip"
        
        cache_path = self.cache_dir / "nri_counties.csv"
        
        if cache_path.exists():
            df = pd.read_csv(cache_path)
        else:
            import urllib.request
            import zipfile
            import io
            
            print("Downloading NRI data...")
            with urllib.request.urlopen(nri_url) as response:
                with zipfile.ZipFile(io.BytesIO(response.read())) as z:
                    # Find the CSV file
                    csv_file = [f for f in z.namelist() if f.endswith('.csv')][0]
                    with z.open(csv_file) as f:
                        df = pd.read_csv(f)
            
            df.to_csv(cache_path, index=False)
        
        if state:
            df = df[df['STATE'] == state]
        
        return df


class FEMADataEnhancer:
    """Enhance FEMA data with additional computed fields."""
    
    DISASTER_SEVERITY_WEIGHTS = {
        "Flood": 3,
        "Hurricane": 5,
        "Tornado": 4,
        "Severe Storm(s)": 2,
        "Fire": 3,
        "Earthquake": 5,
        "Drought": 2,
        "Snowstorm": 2,
        "Tropical Storm": 3,
        "Coastal Storm": 3,
    }
    
    def __init__(self, fema_client: FEMAAPIClient):
        self.client = fema_client
    
    def enhance_disaster_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add computed fields to disaster declarations."""
        df = df.copy()
        
        # Parse dates
        date_cols = ['declarationDate', 'incidentBeginDate', 'incidentEndDate', 'disasterCloseoutDate']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Add severity scores
        df['severity_score'] = df['incidentType'].map(
            self.DISASTER_SEVERITY_WEIGHTS
        ).fillna(2)
        
        # Calculate duration
        df['incident_duration_days'] = (
            df['incidentEndDate'] - df['incidentBeginDate']
        ).dt.days
        
        # Calculate recovery time
        df['recovery_days'] = (
            df['disasterCloseoutDate'] - df['declarationDate']
        ).dt.days
        
        # Create FIPS codes
        if 'fipsStateCode' in df.columns and 'fipsCountyCode' in df.columns:
            df['state_fips'] = df['fipsStateCode'].astype(str).str.zfill(2)
            df['county_fips'] = df['fipsCountyCode'].astype(str).str.zfill(3)
            df['fips'] = df['state_fips'] + df['county_fips']
        
        # Extract year and month for temporal analysis
        df['declaration_year'] = df['declarationDate'].dt.year
        df['declaration_month'] = df['declarationDate'].dt.month
        df['declaration_quarter'] = df['declarationDate'].dt.quarter
        
        return df
    
    def estimate_damage_costs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Estimate damage costs using FEMA assistance data."""
        df = df.copy()
        
        # Calculate total obligated amount
        amount_cols = ['iaAmount', 'paAmount', 'hmAmount', 'totalObligated']
        for col in amount_cols:
            if col not in df.columns:
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['estimated_total_damage'] = (
            df['iaAmount'] + df['paAmount'] + df['hmAmount']
        )
        
        # Calculate per-capita damage if population data available
        if 'population' in df.columns:
            df['damage_per_capita'] = df['estimated_total_damage'] / df['population']
        
        return df
```

---

## 4. Disaster Analysis Framework

### 4.1 Disaster Type Classification System

```python
# src/analysis/disaster_classification.py

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.preprocessing import LabelEncoder
from collections import Counter

class DisasterClassifier:
    """
    Advanced disaster classification system with multi-level categorization.
    """
    
    # Primary disaster categories
    HYDROLOGICAL = ['Flood', 'Flash Flood', 'Coastal Flood', 'Storm Surge']
    METEOROLOGICAL = ['Hurricane', 'Tropical Storm', 'Severe Storm(s)', 'Tornado', 
                      'Winter Storm', 'Snowstorm', 'Ice Storm', 'Extreme Cold']
    CLIMATOLOGICAL = ['Drought', 'Heat Wave', 'Wildfire', 'Fire']
    GEOPHYSICAL = ['Earthquake', 'Tsunami', 'Volcanic Eruption', 'Mud/Landslide']
    BIOLOGICAL = ['Biological', 'Pandemic', 'Epidemic']
    TECHNOLOGICAL = ['Chemical', 'Radiological', 'Toxic Substances']
    
    DISASTER_CATEGORIES = {
        'hydrological': HYDROLOGICAL,
        'meteorological': METEOROLOGICAL,
        'climatological': CLIMATOLOGICAL,
        'geophysical': GEOPHYSICAL,
        'biological': BIOLOGICAL,
        'technological': TECHNOLOGICAL
    }
    
    # Severity indicators
    SEVERITY_INDICATORS = {
        'major_disaster': ['major', 'catastrophic', 'severe', 'extensive'],
        'emergency': ['emergency', 'urgent'],
        'fire_management': ['fire management', 'fire suppression']
    }
    
    def __init__(self):
        self.label_encoder = LabelEncoder()
    
    def classify_disaster_category(self, incident_type: str) -> str:
        """Classify disaster into primary category."""
        incident_lower = incident_type.lower()
        
        for category, types in self.DISASTER_CATEGORIES.items():
            if any(t.lower() in incident_lower for t in types):
                return category
        
        return 'other'
    
    def classify_disaster_severity(self, row: pd.Series) -> int:
        """
        Classify disaster severity (1-5 scale) based on multiple factors.
        """
        severity_score = 0
        
        # Base severity from incident type
        type_weights = {
            'Hurricane': 5, 'Earthquake': 5, 'Tsunami': 5,
            'Tornado': 4, 'Flood': 3, 'Fire': 3,
            'Severe Storm(s)': 2, 'Winter Storm': 2,
            'Drought': 2
        }
        severity_score += type_weights.get(row.get('incidentType', ''), 2)
        
        # Adjust based on declaration type
        if 'declarationTitle' in row:
            title_lower = row['declarationTitle'].lower()
            if any(kw in title_lower for kw in self.SEVERITY_INDICATORS['major_disaster']):
                severity_score += 1
            elif any(kw in title_lower for kw in self.SEVERITY_INDICATORS['emergency']):
                severity_score -= 0.5
        
        # Adjust based on financial impact
        if 'totalObligated' in row and row['totalObligated'] > 0:
            if row['totalObligated'] > 1e9:  # > $1B
                severity_score += 1
            elif row['totalObligated'] > 100e6:  # > $100M
                severity_score += 0.5
        
        # Adjust based on duration
        if 'incident_duration_days' in row and row['incident_duration_days'] > 0:
            if row['incident_duration_days'] > 30:
                severity_score += 0.5
            elif row['incident_duration_days'] > 7:
                severity_score += 0.25
        
        return min(5, max(1, int(severity_score)))
    
    def classify_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all classifications to disaster data."""
        df = df.copy()
        
        # Classify category
        df['disaster_category'] = df['incidentType'].apply(
            self.classify_disaster_category
        )
        
        # Classify severity
        df['severity_level'] = df.apply(self.classify_disaster_severity, axis=1)
        
        # Create severity labels
        severity_labels = {1: 'Minor', 2: 'Moderate', 3: 'Major', 4: 'Severe', 5: 'Catastrophic'}
        df['severity_label'] = df['severity_level'].map(severity_labels)
        
        return df
    
    def get_category_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get distribution of disaster categories."""
        return df['disaster_category'].value_counts().to_dict()
    
    def get_severity_distribution(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get distribution of disaster severity levels."""
        return df['severity_label'].value_counts().to_dict()
```

### 4.2 Temporal Pattern Analysis

```python
# src/analysis/temporal_analysis.py

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from scipy import stats
from scipy.fft import fft
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
import warnings

class TemporalPatternAnalyzer:
    """
    Comprehensive temporal pattern analysis for disaster data.
    
    Features:
    - Seasonality detection
    - Trend analysis
    - Cyclical pattern identification
    - Anomaly detection
    - Forecasting preparation
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.patterns = {}
        
        # Ensure date column exists and is datetime
        if 'declarationDate' in self.df.columns:
            self.df['declarationDate'] = pd.to_datetime(self.df['declarationDate'])
    
    def analyze_seasonality(self, fips: Optional[str] = None) -> Dict:
        """
        Analyze seasonal patterns in disaster occurrences.
        
        Returns:
            Dictionary with seasonality metrics
        """
        df = self.df.copy()
        
        if fips:
            df = df[df['fips'] == fips]
        
        if len(df) == 0:
            return {'error': 'No data available'}
        
        # Extract month from declaration date
        df['month'] = df['declarationDate'].dt.month
        
        # Count disasters by month
        monthly_counts = df.groupby('month').size()
        
        # Calculate seasonality strength using coefficient of variation
        mean_count = monthly_counts.mean()
        std_count = monthly_counts.std()
        cv = std_count / mean_count if mean_count > 0 else 0
        
        # Identify peak months (above 75th percentile)
        threshold = monthly_counts.quantile(0.75)
        peak_months = monthly_counts[monthly_counts >= threshold].index.tolist()
        
        # Calculate chi-square test for uniformity
        expected = mean_count
        chi2_stat = ((monthly_counts - expected) ** 2 / expected).sum()
        
        # Seasonality score (0-1, higher = more seasonal)
        seasonality_score = min(1.0, cv)
        
        return {
            'seasonality_score': round(seasonality_score, 4),
            'peak_months': peak_months,
            'monthly_distribution': monthly_counts.to_dict(),
            'chi2_uniformity': round(chi2_stat, 4),
            'is_seasonal': seasonality_score > 0.3
        }
    
    def analyze_trends(self, fips: Optional[str] = None, 
                       window: int = 5) -> Dict:
        """
        Analyze disaster frequency trends over time.
        
        Args:
            fips: County FIPS code (optional)
            window: Years for trend calculation
            
        Returns:
            Dictionary with trend metrics
        """
        df = self.df.copy()
        
        if fips:
            df = df[df['fips'] == fips]
        
        if len(df) == 0:
            return {'error': 'No data available'}
        
        # Group by year
        df['year'] = df['declarationDate'].dt.year
        yearly_counts = df.groupby('year').size().sort_index()
        
        if len(yearly_counts) < window * 2:
            return {'error': 'Insufficient data for trend analysis'}
        
        # Calculate linear trend
        x = np.arange(len(yearly_counts))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, yearly_counts.values)
        
        # Determine trend direction
        if p_value > 0.05:
            trend_direction = 'stable'
        elif slope > 0.01:
            trend_direction = 'increasing'
        elif slope < -0.01:
            trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'
        
        # Calculate acceleration (change in slope)
        recent = yearly_counts.iloc[-window:].mean()
        older = yearly_counts.iloc[-(window*2):-window].mean()
        acceleration = (recent - older) / max(older, 1)
        
        # Mann-Kendall trend test
        mk_result = self._mann_kendall_test(yearly_counts.values)
        
        return {
            'trend_direction': trend_direction,
            'trend_slope': round(slope, 6),
            'trend_r2': round(r_value ** 2, 4),
            'trend_pvalue': round(p_value, 6),
            'acceleration_ratio': round(acceleration, 4),
            'is_accelerating': acceleration > 0.2,
            'mann_kendall': mk_result,
            'yearly_counts': yearly_counts.to_dict()
        }
    
    def _mann_kendall_test(self, data: np.ndarray) -> Dict:
        """Perform Mann-Kendall trend test."""
        n = len(data)
        if n < 3:
            return {'error': 'Insufficient data'}
        
        # Calculate S statistic
        s = 0
        for i in range(n - 1):
            for j in range(i + 1, n):
                s += np.sign(data[j] - data[i])
        
        # Calculate variance
        var_s = n * (n - 1) * (2 * n + 5) / 18
        
        # Calculate Z statistic
        if s > 0:
            z = (s - 1) / np.sqrt(var_s)
        elif s < 0:
            z = (s + 1) / np.sqrt(var_s)
        else:
            z = 0
        
        # Calculate p-value
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        # Determine trend
        if p_value < 0.05:
            trend = 'increasing' if s > 0 else 'decreasing'
        else:
            trend = 'no trend'
        
        return {
            's_statistic': int(s),
            'z_statistic': round(z, 4),
            'p_value': round(p_value, 6),
            'trend': trend
        }
    
    def detect_cyclical_patterns(self, fips: Optional[str] = None) -> Dict:
        """
        Detect cyclical patterns using Fourier analysis.
        
        Returns:
            Dictionary with cyclical pattern information
        """
        df = self.df.copy()
        
        if fips:
            df = df[df['fips'] == fips]
        
        if len(df) < 24:  # Need at least 2 years of monthly data
            return {'error': 'Insufficient data for cyclical analysis'}
        
        # Create monthly time series
        df['year_month'] = df['declarationDate'].dt.to_period('M')
        monthly_counts = df.groupby('year_month').size()
        
        # Fill missing months with zeros
        full_range = pd.period_range(
            start=monthly_counts.index.min(),
            end=monthly_counts.index.max(),
            freq='M'
        )
        monthly_counts = monthly_counts.reindex(full_range, fill_value=0)
        
        # Apply FFT
        fft_result = fft(monthly_counts.values)
        frequencies = np.fft.fftfreq(len(fft_result))
        
        # Find dominant frequencies (excluding DC component)
        magnitudes = np.abs(fft_result)
        positive_freq_idx = frequencies > 0
        
        dominant_idx = np.argsort(magnitudes[positive_freq_idx])[-3:][::-1]
        dominant_periods = []
        
        for idx in dominant_idx:
            freq = frequencies[positive_freq_idx][idx]
            if freq > 0:
                period = 1 / freq  # in months
                if 2 <= period <= len(monthly_counts) / 2:
                    dominant_periods.append(round(period, 1))
        
        return {
            'dominant_periods_months': dominant_periods[:3],
            'has_annual_cycle': any(10 <= p <= 14 for p in dominant_periods),
            'has_multi_year_cycle': any(p > 12 for p in dominant_periods)
        }
    
    def detect_anomalies(self, fips: Optional[str] = None, 
                         threshold: float = 2.0) -> Dict:
        """
        Detect anomalous disaster years using statistical methods.
        
        Args:
            fips: County FIPS code
            threshold: Z-score threshold for anomaly detection
            
        Returns:
            Dictionary with anomaly information
        """
        df = self.df.copy()
        
        if fips:
            df = df[df['fips'] == fips]
        
        if len(df) < 5:
            return {'error': 'Insufficient data for anomaly detection'}
        
        # Group by year
        df['year'] = df['declarationDate'].dt.year
        yearly_counts = df.groupby('year').size()
        
        # Calculate Z-scores
        mean = yearly_counts.mean()
        std = yearly_counts.std()
        z_scores = (yearly_counts - mean) / std
        
        # Identify anomalies
        anomalies = yearly_counts[abs(z_scores) > threshold]
        
        # Identify extreme values
        q75 = yearly_counts.quantile(0.75)
        q25 = yearly_counts.quantile(0.25)
        iqr = q75 - q25
        upper_bound = q75 + 1.5 * iqr
        lower_bound = q25 - 1.5 * iqr
        
        outliers = yearly_counts[(yearly_counts > upper_bound) | 
                                  (yearly_counts < lower_bound)]
        
        return {
            'anomaly_years': anomalies.index.tolist(),
            'anomaly_counts': anomalies.to_dict(),
            'outlier_years': outliers.index.tolist(),
            'z_scores': z_scores.to_dict(),
            'mean_annual': round(mean, 2),
            'std_annual': round(std, 2)
        }
    
    def analyze_disaster_types_over_time(self, fips: Optional[str] = None) -> Dict:
        """
        Analyze how disaster type distribution changes over time.
        
        Returns:
            Dictionary with disaster type evolution
        """
        df = self.df.copy()
        
        if fips:
            df = df[df['fips'] == fips]
        
        df['year'] = df['declarationDate'].dt.year
        df['decade'] = (df['year'] // 10) * 10
        
        # Calculate type distribution by decade
        type_by_decade = df.groupby(['decade', 'incidentType']).size().unstack(fill_value=0)
        
        # Calculate percentage distribution
        type_pct = type_by_decade.div(type_by_decade.sum(axis=1), axis=0) * 100
        
        # Identify emerging types (increasing trend)
        emerging_types = []
        for col in type_pct.columns:
            if len(type_pct) >= 2:
                early_avg = type_pct[col].iloc[:2].mean()
                recent_avg = type_pct[col].iloc[-2:].mean()
                if recent_avg > early_avg * 1.5 and recent_avg > 5:
                    emerging_types.append(col)
        
        return {
            'type_by_decade': type_by_decade.to_dict(),
            'type_percentage': type_pct.to_dict(),
            'emerging_types': emerging_types,
            'dominant_types': type_pct.iloc[-1].nlargest(3).to_dict() if len(type_pct) > 0 else {}
        }
    
    def get_comprehensive_analysis(self, fips: Optional[str] = None) -> Dict:
        """Run all temporal analyses and return comprehensive results."""
        return {
            'seasonality': self.analyze_seasonality(fips),
            'trends': self.analyze_trends(fips),
            'cyclical_patterns': self.detect_cyclical_patterns(fips),
            'anomalies': self.detect_anomalies(fips),
            'type_evolution': self.analyze_disaster_types_over_time(fips)
        }
```

---

## 5. Geographic Clustering Analysis

### 5.1 Spatial Clustering System

```python
# src/analysis/geographic_clustering.py

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
import geopandas as gpd

class DisasterGeographicClustering:
    """
    Geographic clustering analysis for disaster hotspots.
    
    Features:
    - Spatial hotspot detection
    - Risk cluster identification
    - Proximity-based grouping
    - Multi-scale clustering
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.clusters = None
        
        # Ensure required columns exist
        required = ['latitude', 'longitude', 'fips']
        for col in required:
            if col not in self.df.columns:
                raise ValueError(f"Required column '{col}' not found in data")
    
    def detect_hotspots_dbscan(self, eps_km: float = 50, 
                                min_samples: int = 3) -> pd.DataFrame:
        """
        Detect disaster hotspots using DBSCAN clustering.
        
        Args:
            eps_km: Maximum distance between samples in a cluster (km)
            min_samples: Minimum samples to form a cluster
            
        Returns:
            DataFrame with cluster assignments
        """
        df = self.df.copy()
        
        # Convert km to approximate degrees
        eps_degrees = eps_km / 111.0
        
        # Prepare coordinates
        coords = df[['latitude', 'longitude']].values
        
        # Apply DBSCAN
        clustering = DBSCAN(eps=eps_degrees, min_samples=min_samples)
        df['cluster_id'] = clustering.fit_predict(coords)
        
        # -1 indicates noise points (not in any cluster)
        self.clusters = df
        
        return df
    
    def cluster_by_risk_profile(self, n_clusters: int = 5) -> pd.DataFrame:
        """
        Cluster counties by disaster risk profile.
        
        Args:
            n_clusters: Number of risk clusters to create
            
        Returns:
            DataFrame with risk cluster assignments
        """
        df = self.df.copy()
        
        # Select features for clustering
        feature_cols = [
            'disaster_count', 'disaster_count_recent',
            'flood_count', 'hurricane_count', 'fire_count', 'tornado_count',
            'severity_level_avg', 'estimated_damage_avg'
        ]
        
        # Filter to available columns
        available_features = [c for c in feature_cols if c in df.columns]
        
        if len(available_features) < 3:
            raise ValueError("Insufficient features for risk clustering")
        
        # Prepare features
        X = df[available_features].fillna(0)
        
        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Apply K-means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['risk_cluster'] = kmeans.fit_predict(X_scaled)
        
        # Calculate cluster characteristics
        cluster_profiles = df.groupby('risk_cluster')[available_features].mean()
        
        # Label clusters by risk level
        risk_scores = cluster_profiles.sum(axis=1)
        risk_labels = risk_scores.rank().astype(int)
        risk_label_map = {
            1: 'Very Low', 2: 'Low', 3: 'Moderate', 4: 'High', 5: 'Very High'
        }
        
        df['risk_cluster_label'] = df['risk_cluster'].map(
            {k: risk_label_map.get(v, 'Unknown') for k, v in risk_labels.items()}
        )
        
        return df
    
    def calculate_spatial_autocorrelation(self, 
                                          variable: str = 'disaster_count') -> Dict:
        """
        Calculate spatial autocorrelation (Moran's I) for disaster data.
        
        Args:
            variable: Variable to analyze
            
        Returns:
            Dictionary with spatial autocorrelation metrics
        """
        try:
            from pysal.explore import esda
            from pysal.lib import weights
        except ImportError:
            return {'error': 'pysal not installed'}
        
        df = self.df.copy()
        
        if variable not in df.columns:
            return {'error': f'Variable {variable} not found'}
        
        # Create spatial weights matrix
        coords = df[['longitude', 'latitude']].values
        w = weights.distance.KNN.from_array(coords, k=5)
        w.transform = 'r'
        
        # Calculate Moran's I
        moran = esda.Moran(df[variable].fillna(0), w)
        
        return {
            'moran_i': round(moran.I, 4),
            'p_value': round(moran.p_sim, 6),
            'z_score': round(moran.z_sim, 4),
            'is_clustered': moran.p_sim < 0.05 and moran.I > 0,
            'interpretation': (
                'Significant clustering' if moran.p_sim < 0.05 and moran.I > 0
                else 'Significant dispersion' if moran.p_sim < 0.05 and moran.I < 0
                else 'Random distribution'
            )
        }
    
    def identify_multi_county_events(self, 
                                      time_window_days: int = 7,
                                      distance_km: float = 100) -> List[Dict]:
        """
        Identify disasters that affected multiple counties simultaneously.
        
        Args:
            time_window_days: Time window for grouping events
            distance_km: Maximum distance for spatial grouping
            
        Returns:
            List of multi-county event groups
        """
        df = self.df.copy()
        df = df.sort_values('declarationDate')
        
        events = []
        processed = set()
        
        for idx, row in df.iterrows():
            if idx in processed:
                continue
            
            # Find nearby events in time window
            time_window = pd.Timedelta(days=time_window_days)
            nearby_time = df[
                (df['declarationDate'] >= row['declarationDate'] - time_window) &
                (df['declarationDate'] <= row['declarationDate'] + time_window)
            ]
            
            # Calculate distances
            nearby_time['distance_km'] = self._haversine_distance(
                row['latitude'], row['longitude'],
                nearby_time['latitude'], nearby_time['longitude']
            )
            
            # Filter by distance
            nearby = nearby_time[nearby_time['distance_km'] <= distance_km]
            
            if len(nearby) > 1:
                event = {
                    'center_lat': nearby['latitude'].mean(),
                    'center_lon': nearby['longitude'].mean(),
                    'affected_counties': nearby['fips'].tolist(),
                    'county_count': len(nearby),
                    'disaster_types': nearby['incidentType'].unique().tolist(),
                    'primary_date': row['declarationDate'],
                    'date_range': (
                        nearby['declarationDate'].min(),
                        nearby['declarationDate'].max()
                    ),
                    'total_damage': nearby.get('estimated_total_damage', pd.Series([0])).sum()
                }
                events.append(event)
                processed.update(nearby.index.tolist())
        
        return events
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                            lat2: pd.Series, lon2: pd.Series) -> pd.Series:
        """Calculate haversine distance between points."""
        R = 6371  # Earth radius in km
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = (np.sin(dlat/2) ** 2 + 
             np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2) ** 2)
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def get_cluster_summary(self) -> Dict:
        """Get summary statistics for identified clusters."""
        if self.clusters is None:
            return {'error': 'No clusters computed. Run detect_hotspots_dbscan first.'}
        
        df = self.clusters
        
        # Filter out noise points
        valid_clusters = df[df['cluster_id'] >= 0]
        
        if len(valid_clusters) == 0:
            return {'error': 'No valid clusters found'}
        
        summary = []
        
        for cluster_id in valid_clusters['cluster_id'].unique():
            cluster_data = valid_clusters[valid_clusters['cluster_id'] == cluster_id]
            
            cluster_summary = {
                'cluster_id': int(cluster_id),
                'county_count': len(cluster_data),
                'center_latitude': round(cluster_data['latitude'].mean(), 4),
                'center_longitude': round(cluster_data['longitude'].mean(), 4),
                'total_disasters': int(cluster_data['disaster_count'].sum()) if 'disaster_count' in cluster_data.columns else 0,
                'primary_disaster_types': cluster_data['incidentType'].value_counts().head(3).to_dict() if 'incidentType' in cluster_data.columns else {},
                'states': cluster_data['state'].unique().tolist() if 'state' in cluster_data.columns else []
            }
            summary.append(cluster_summary)
        
        return {
            'total_clusters': len(summary),
            'counties_in_clusters': sum(s['county_count'] for s in summary),
            'clusters': sorted(summary, key=lambda x: x['county_count'], reverse=True)
        }
```

---

## 6. Severity Assessment & Damage Cost Estimation

### 6.1 Damage Cost Estimation Model

```python
# src/analysis/damage_estimation.py

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

class DamageCostEstimator:
    """
    Disaster damage cost estimation using FEMA data and predictive modeling.
    
    Features:
    - Historical cost analysis
    - Predictive cost modeling
    - Per-capita damage estimation
    - Regional cost adjustment
    """
    
    # Regional cost multipliers (based on construction costs, population density, etc.)
    REGIONAL_MULTIPLIERS = {
        'CA': 1.5, 'NY': 1.4, 'HI': 1.3, 'MA': 1.3, 'NJ': 1.2,
        'TX': 1.0, 'FL': 1.1, 'IL': 1.0, 'PA': 0.9, 'OH': 0.8,
        'MS': 0.7, 'AR': 0.7, 'WV': 0.7, 'KY': 0.7, 'AL': 0.8
    }
    
    # Disaster type base costs (in millions)
    DISASTER_BASE_COSTS = {
        'Hurricane': 500,
        'Earthquake': 400,
        'Flood': 150,
        'Tornado': 80,
        'Fire': 100,
        'Severe Storm(s)': 50,
        'Winter Storm': 40,
        'Drought': 200
    }
    
    def __init__(self):
        self.model = None
        self.is_fitted = False
    
    def estimate_from_historical(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estimate damage costs based on historical FEMA assistance data.
        
        Args:
            df: Disaster declarations DataFrame
            
        Returns:
            DataFrame with estimated damage costs
        """
        df = df.copy()
        
        # Use actual FEMA data if available
        cost_columns = ['iaAmount', 'paAmount', 'hmAmount', 'totalObligated']
        for col in cost_columns:
            if col not in df.columns:
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Calculate total known costs
        df['known_total_cost'] = df['iaAmount'] + df['paAmount'] + df['hmAmount']
        
        # For records without cost data, estimate based on type and severity
        mask = df['known_total_cost'] == 0
        
        if mask.any():
            df.loc[mask, 'estimated_cost'] = df.loc[mask].apply(
                self._estimate_single_disaster, axis=1
            )
        
        df.loc[~mask, 'estimated_cost'] = df.loc[~mask, 'known_total_cost']
        
        # Apply regional adjustment
        if 'state' in df.columns:
            df['regional_multiplier'] = df['state'].map(
                self.REGIONAL_MULTIPLIERS
            ).fillna(1.0)
            df['adjusted_cost'] = df['estimated_cost'] * df['regional_multiplier']
        else:
            df['adjusted_cost'] = df['estimated_cost']
        
        return df
    
    def _estimate_single_disaster(self, row: pd.Series) -> float:
        """Estimate cost for a single disaster event."""
        # Base cost by type
        base_cost = self.DISASTER_BASE_COSTS.get(
            row.get('incidentType', 'Other'), 50
        )
        
        # Adjust by severity
        severity = row.get('severity_level', 3)
        severity_multiplier = severity / 3.0
        
        # Adjust by duration
        duration = row.get('incident_duration_days', 1)
        duration_multiplier = min(3.0, 1 + (duration / 30))
        
        # Adjust by affected area (if available)
        if 'affected_counties' in row and isinstance(row['affected_counties'], list):
            area_multiplier = len(row['affected_counties']) ** 0.5
        else:
            area_multiplier = 1.0
        
        estimated = base_cost * severity_multiplier * duration_multiplier * area_multiplier
        
        return estimated * 1e6  # Convert to dollars
    
    def fit_predictive_model(self, df: pd.DataFrame) -> Dict:
        """
        Train a predictive model for damage cost estimation.
        
        Args:
            df: Training data with known costs
            
        Returns:
            Model performance metrics
        """
        # Filter to records with known costs
        train_df = df[df['known_total_cost'] > 0].copy()
        
        if len(train_df) < 100:
            return {'error': 'Insufficient training data'}
        
        # Feature engineering
        feature_cols = [
            'severity_level', 'incident_duration_days',
            'declaration_month', 'declaration_year'
        ]
        
        # Add disaster type one-hot encoding
        type_dummies = pd.get_dummies(train_df['incidentType'], prefix='type')
        train_df = pd.concat([train_df, type_dummies], axis=1)
        feature_cols.extend(type_dummies.columns.tolist())
        
        # Filter to available features
        available_features = [c for c in feature_cols if c in train_df.columns]
        
        X = train_df[available_features].fillna(0)
        y = np.log1p(train_df['known_total_cost'])  # Log transform for skewed data
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        self.is_fitted = True
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        
        metrics = {
            'mae': round(mean_absolute_error(y_test, y_pred), 4),
            'r2': round(r2_score(y_test, y_pred), 4),
            'feature_importance': dict(zip(
                available_features,
                self.model.feature_importances_.round(4)
            ))
        }
        
        return metrics
    
    def predict_cost(self, row: pd.Series) -> float:
        """Predict damage cost for a single disaster using trained model."""
        if not self.is_fitted:
            return self._estimate_single_disaster(row)
        
        # Prepare features
        features = pd.DataFrame([row])
        
        # Add type dummies
        type_dummies = pd.get_dummies(features['incidentType'], prefix='type')
        features = pd.concat([features, type_dummies], axis=1)
        
        # Predict
        log_pred = self.model.predict(features.fillna(0))[0]
        
        return np.expm1(log_pred)  # Reverse log transform
    
    def calculate_per_capita_damage(self, df: pd.DataFrame, 
                                    population_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate per-capita damage costs.
        
        Args:
            df: Disaster data with costs
            population_df: Population data by FIPS
            
        Returns:
            DataFrame with per-capita damage
        """
        df = df.copy()
        
        # Merge population data
        df = df.merge(
            population_df[['fips', 'population']],
            on='fips',
            how='left'
        )
        
        # Calculate per-capita damage
        df['damage_per_capita'] = df['adjusted_cost'] / df['population'].replace(0, np.nan)
        
        # Calculate damage as percentage of median income (if available)
        if 'median_income' in df.columns:
            df['damage_pct_income'] = (
                df['damage_per_capita'] / df['median_income'].replace(0, np.nan) * 100
            )
        
        return df
    
    def aggregate_costs_by_region(self, df: pd.DataFrame, 
                                   group_by: str = 'state') -> pd.DataFrame:
        """
        Aggregate damage costs by region.
        
        Args:
            df: Disaster data with costs
            group_by: Column to group by
            
        Returns:
            Aggregated cost summary
        """
        agg_dict = {
            'adjusted_cost': ['sum', 'mean', 'std', 'count'],
            'damage_per_capita': ['mean', 'median', 'std']
        }
        
        summary = df.groupby(group_by).agg(agg_dict)
        
        # Flatten column names
        summary.columns = ['_'.join(col).strip() for col in summary.columns]
        
        # Add rank columns
        summary['total_cost_rank'] = summary['adjusted_cost_sum'].rank(ascending=False)
        summary['per_capita_rank'] = summary['damage_per_capita_mean'].rank(ascending=False)
        
        return summary.reset_index()
```

---

## 7. Recovery Time Analysis

### 7.1 Recovery Metrics System

```python
# src/analysis/recovery_analysis.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from scipy import stats

class RecoveryTimeAnalyzer:
    """
    Analyze disaster recovery times and factors affecting recovery.
    
    Features:
    - Recovery time distribution analysis
    - Recovery factor identification
    - Recovery prediction modeling
    - Cross-disaster comparison
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.recovery_data = None
    
    def calculate_recovery_metrics(self) -> pd.DataFrame:
        """
        Calculate recovery time metrics for each disaster.
        
        Returns:
            DataFrame with recovery metrics
        """
        df = self.df.copy()
        
        # Parse dates
        date_cols = ['declarationDate', 'incidentBeginDate', 
                     'incidentEndDate', 'disasterCloseoutDate']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Calculate recovery time (declaration to closeout)
        df['recovery_days'] = (
            df['disasterCloseoutDate'] - df['declarationDate']
        ).dt.days
        
        # Calculate incident duration
        df['incident_duration_days'] = (
            df['incidentEndDate'] - df['incidentBeginDate']
        ).dt.days
        
        # Categorize recovery speed
        df['recovery_category'] = pd.cut(
            df['recovery_days'],
            bins=[0, 180, 365, 730, 1460, float('inf')],
            labels=['Very Fast (<6mo)', 'Fast (6-12mo)', 
                    'Normal (1-2yr)', 'Slow (2-4yr)', 'Very Slow (>4yr)']
        )
        
        self.recovery_data = df
        
        return df
    
    def analyze_recovery_factors(self) -> Dict:
        """
        Identify factors that influence recovery time.
        
        Returns:
            Dictionary with factor analysis
        """
        if self.recovery_data is None:
            self.calculate_recovery_metrics()
        
        df = self.recovery_data.dropna(subset=['recovery_days'])
        
        if len(df) < 10:
            return {'error': 'Insufficient data for factor analysis'}
        
        factors = {}
        
        # Factor 1: Disaster type
        type_recovery = df.groupby('incidentType')['recovery_days'].agg([
            'count', 'mean', 'median', 'std'
        ]).round(2)
        factors['by_disaster_type'] = type_recovery.to_dict()
        
        # Factor 2: Severity level
        if 'severity_level' in df.columns:
            severity_recovery = df.groupby('severity_level')['recovery_days'].agg([
                'count', 'mean', 'median'
            ]).round(2)
            factors['by_severity'] = severity_recovery.to_dict()
        
        # Factor 3: Financial impact
        if 'adjusted_cost' in df.columns:
            df['cost_quartile'] = pd.qcut(df['adjusted_cost'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
            cost_recovery = df.groupby('cost_quartile')['recovery_days'].mean().round(2)
            factors['by_cost_quartile'] = cost_recovery.to_dict()
        
        # Factor 4: Duration of incident
        duration_corr = df['incident_duration_days'].corr(df['recovery_days'])
        factors['incident_duration_correlation'] = round(duration_corr, 4)
        
        # Factor 5: Geographic region
        if 'state' in df.columns:
            state_recovery = df.groupby('state')['recovery_days'].mean().round(2)
            factors['by_state'] = state_recovery.nlargest(10).to_dict()
        
        # Statistical significance tests
        # ANOVA for disaster type
        type_groups = [group['recovery_days'].values for name, group in 
                       df.groupby('incidentType') if len(group) > 5]
        if len(type_groups) > 1:
            f_stat, p_value = stats.f_oneway(*type_groups)
            factors['disaster_type_anova'] = {
                'f_statistic': round(f_stat, 4),
                'p_value': round(p_value, 6),
                'significant': p_value < 0.05
            }
        
        return factors
    
    def predict_recovery_time(self, disaster_features: Dict) -> Dict:
        """
        Predict recovery time based on disaster characteristics.
        
        Args:
            disaster_features: Dictionary with disaster characteristics
            
        Returns:
            Dictionary with predicted recovery time and confidence
        """
        if self.recovery_data is None:
            return {'error': 'No recovery data available'}
        
        df = self.recovery_data.dropna(subset=['recovery_days'])
        
        # Simple prediction based on similar disasters
        similar = df.copy()
        
        # Filter by disaster type
        if 'incidentType' in disaster_features:
            similar = similar[similar['incidentType'] == disaster_features['incidentType']]
        
        # Filter by severity
        if 'severity_level' in disaster_features and 'severity_level' in similar.columns:
            similar = similar[
                abs(similar['severity_level'] - disaster_features['severity_level']) <= 1
            ]
        
        if len(similar) < 5:
            # Fall back to all data
            similar = df
        
        # Calculate prediction
        predicted_days = similar['recovery_days'].median()
        
        # Calculate confidence interval
        std = similar['recovery_days'].std()
        n = len(similar)
        
        # 95% confidence interval
        margin = 1.96 * (std / np.sqrt(n))
        ci_lower = max(0, predicted_days - margin)
        ci_upper = predicted_days + margin
        
        return {
            'predicted_recovery_days': int(predicted_days),
            'predicted_recovery_months': round(predicted_days / 30, 1),
            'confidence_interval_95': (int(ci_lower), int(ci_upper)),
            'similar_disasters_count': n,
            'prediction_basis': f"Based on {n} similar disasters"
        }
    
    def get_recovery_benchmarks(self) -> Dict:
        """
        Get recovery time benchmarks by disaster type.
        
        Returns:
            Dictionary with benchmark data
        """
        if self.recovery_data is None:
            self.calculate_recovery_metrics()
        
        df = self.recovery_data.dropna(subset=['recovery_days'])
        
        benchmarks = {}
        
        for disaster_type in df['incidentType'].unique():
            type_data = df[df['incidentType'] == disaster_type]['recovery_days']
            
            if len(type_data) < 5:
                continue
            
            benchmarks[disaster_type] = {
                'count': len(type_data),
                'mean_days': int(type_data.mean()),
                'median_days': int(type_data.median()),
                'std_days': int(type_data.std()),
                'min_days': int(type_data.min()),
                'max_days': int(type_data.max()),
                'percentile_25': int(type_data.quantile(0.25)),
                'percentile_75': int(type_data.quantile(0.75)),
                'typical_range_months': (
                    int(type_data.quantile(0.25) / 30),
                    int(type_data.quantile(0.75) / 30)
                )
            }
        
        return benchmarks
    
    def compare_recovery_periods(self, period1: Tuple[str, str], 
                                  period2: Tuple[str, str]) -> Dict:
        """
        Compare recovery times between two historical periods.
        
        Args:
            period1: (start_date, end_date) for first period
            period2: (start_date, end_date) for second period
            
        Returns:
            Comparison results
        """
        if self.recovery_data is None:
            self.calculate_recovery_metrics()
        
        df = self.recovery_data.dropna(subset=['recovery_days'])
        
        # Filter by periods
        p1_data = df[
            (df['declarationDate'] >= period1[0]) &
            (df['declarationDate'] <= period1[1])
        ]['recovery_days']
        
        p2_data = df[
            (df['declarationDate'] >= period2[0]) &
            (df['declarationDate'] <= period2[1])
        ]['recovery_days']
        
        if len(p1_data) < 5 or len(p2_data) < 5:
            return {'error': 'Insufficient data for comparison'}
        
        # T-test for difference in means
        t_stat, p_value = stats.ttest_ind(p1_data, p2_data)
        
        return {
            'period1': {
                'date_range': period1,
                'count': len(p1_data),
                'mean_days': int(p1_data.mean()),
                'median_days': int(p1_data.median())
            },
            'period2': {
                'date_range': period2,
                'count': len(p2_data),
                'mean_days': int(p2_data.mean()),
                'median_days': int(p2_data.median())
            },
            'difference_mean': int(p2_data.mean() - p1_data.mean()),
            'percent_change': round(
                (p2_data.mean() - p1_data.mean()) / p1_data.mean() * 100, 2
            ),
            't_test': {
                't_statistic': round(t_stat, 4),
                'p_value': round(p_value, 6),
                'significant': p_value < 0.05
            }
        }
```

---

## 8. Disaster Prediction Models

### 8.1 Comprehensive Prediction Framework

```python
# src/models/disaster_prediction.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

class DisasterPredictionModel:
    """
    Comprehensive disaster prediction framework.
    
    Features:
    - Disaster occurrence prediction
    - Disaster type prediction
    - Severity prediction
    - Risk score forecasting
    - Multi-horizon predictions
    """
    
    def __init__(self, model_type: str = 'gradient_boosting'):
        self.model_type = model_type
        self.occurrence_model = None
        self.type_model = None
        self.severity_model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names = None
    
    def prepare_features(self, df: pd.DataFrame, 
                         target_horizon_months: int = 12) -> pd.DataFrame:
        """
        Prepare features for disaster prediction.
        
        Args:
            df: Historical disaster data
            target_horizon_months: Prediction horizon
            
        Returns:
            Feature-engineered DataFrame
        """
        features = df.copy()
        
        # Temporal features
        features['month'] = features['declarationDate'].dt.month
        features['quarter'] = features['declarationDate'].dt.quarter
        features['year'] = features['declarationDate'].dt.year
        
        # Lag features (previous period disaster counts)
        features = features.sort_values(['fips', 'declarationDate'])
        
        for lag in [1, 2, 3, 6, 12]:
            features[f'disaster_count_lag_{lag}m'] = features.groupby('fips')[
                'disaster_count'
            ].shift(lag)
        
        # Rolling statistics
        features['disaster_count_rolling_mean_6m'] = features.groupby('fips')[
            'disaster_count'
        ].rolling(6, min_periods=1).mean().reset_index(0, drop=True)
        
        features['disaster_count_rolling_std_6m'] = features.groupby('fips')[
            'disaster_count'
        ].rolling(6, min_periods=1).std().reset_index(0, drop=True)
        
        # Trend features
        features['disaster_trend'] = features.groupby('fips').apply(
            lambda x: x['disaster_count'].diff().rolling(6).mean()
        ).reset_index(0, drop=True)
        
        # Seasonal features
        features['is_hurricane_season'] = features['month'].isin([6, 7, 8, 9, 10, 11])
        features['is_winter_storm_season'] = features['month'].isin([12, 1, 2, 3])
        features['is_tornado_season'] = features['month'].isin([3, 4, 5, 6])
        
        # Historical frequency features
        features['historical_annual_avg'] = features.groupby('fips')[
            'disaster_count'
        ].expanding().mean().reset_index(0, drop=True)
        
        # Cyclical encoding for month
        features['month_sin'] = np.sin(2 * np.pi * features['month'] / 12)
        features['month_cos'] = np.cos(2 * np.pi * features['month'] / 12)
        
        return features
    
    def fit_occurrence_model(self, df: pd.DataFrame, 
                             feature_cols: List[str]) -> Dict:
        """
        Train disaster occurrence prediction model.
        
        Args:
            df: Training data
            feature_cols: Feature column names
            
        Returns:
            Model performance metrics
        """
        # Prepare target variable (disaster occurred or not)
        df['disaster_occurred'] = (df['disaster_count'] > 0).astype(int)
        
        # Filter to complete cases
        available_features = [c for c in feature_cols if c in df.columns]
        train_df = df.dropna(subset=available_features + ['disaster_occurred'])
        
        X = train_df[available_features]
        y = train_df['disaster_occurred']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        if self.model_type == 'gradient_boosting':
            self.occurrence_model = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            self.occurrence_model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                random_state=42
            )
        
        # Time-series cross-validation
        tscv = TimeSeriesSplit(n_splits=5)
        cv_scores = cross_val_score(
            self.occurrence_model, X_scaled, y, cv=tscv, scoring='roc_auc'
        )
        
        # Fit on full data
        self.occurrence_model.fit(X_scaled, y)
        
        # Feature importance
        importance = dict(zip(
            available_features,
            self.occurrence_model.feature_importances_.round(4)
        ))
        
        self.feature_names = available_features
        self.is_fitted = True
        
        return {
            'cv_auc_mean': round(cv_scores.mean(), 4),
            'cv_auc_std': round(cv_scores.std(), 4),
            'feature_importance': importance,
            'training_samples': len(train_df),
            'positive_rate': round(y.mean(), 4)
        }
    
    def predict_occurrence(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Predict disaster occurrence probability.
        
        Args:
            features: Feature DataFrame
            
        Returns:
            DataFrame with predictions
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit_occurrence_model first.")
        
        X = features[self.feature_names].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        features['disaster_probability'] = self.occurrence_model.predict_proba(X_scaled)[:, 1]
        features['disaster_predicted'] = (features['disaster_probability'] > 0.5).astype(int)
        
        return features
    
    def predict_disaster_type(self, df: pd.DataFrame, 
                              fips: str, 
                              month: int) -> Dict:
        """
        Predict most likely disaster type for a county and month.
        
        Args:
            df: Historical data
            fips: County FIPS code
            month: Target month
            
        Returns:
            Dictionary with type probabilities
        """
        county_data = df[df['fips'] == fips]
        
        if len(county_data) < 5:
            return {'error': 'Insufficient historical data'}
        
        # Calculate historical type distribution for this month
        month_data = county_data[county_data['declarationDate'].dt.month == month]
        
        if len(month_data) == 0:
            # Use all data for this county
            type_dist = county_data['incidentType'].value_counts(normalize=True)
        else:
            type_dist = month_data['incidentType'].value_counts(normalize=True)
        
        # Calculate seasonal patterns
        seasonal_types = {}
        for m in range(1, 13):
            m_data = county_data[county_data['declarationDate'].dt.month == m]
            if len(m_data) > 0:
                top_type = m_data['incidentType'].value_counts().index[0]
                seasonal_types[m] = top_type
        
        return {
            'predicted_types': type_dist.head(3).to_dict(),
            'most_likely_type': type_dist.index[0],
            'confidence': round(type_dist.iloc[0], 4),
            'seasonal_pattern': seasonal_types.get(month, 'Unknown'),
            'historical_basis': f"Based on {len(county_data)} historical disasters"
        }
    
    def forecast_risk_trajectory(self, 
                                  historical_data: pd.DataFrame,
                                  forecast_months: int = 12) -> pd.DataFrame:
        """
        Forecast disaster risk trajectory over time.
        
        Args:
            historical_data: Historical disaster data
            forecast_months: Number of months to forecast
            
        Returns:
            DataFrame with risk forecasts
        """
        from prophet import Prophet
        
        # Prepare time series
        ts_data = historical_data.groupby(
            historical_data['declarationDate'].dt.to_period('M')
        ).agg({
            'disaster_count': 'sum',
            'severity_level': 'mean',
            'adjusted_cost': 'sum'
        }).reset_index()
        
        ts_data['ds'] = ts_data['declarationDate'].dt.to_timestamp()
        ts_data = ts_data.rename(columns={'disaster_count': 'y'})
        
        # Fit Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )
        
        model.fit(ts_data[['ds', 'y']])
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=forecast_months, freq='MS')
        
        # Generate forecast
        forecast = model.predict(future)
        
        # Add risk categories
        forecast['risk_level'] = pd.cut(
            forecast['yhat'],
            bins=[0, 1, 3, 5, float('inf')],
            labels=['Low', 'Moderate', 'High', 'Severe']
        )
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'risk_level']]


class EnsembleDisasterPredictor:
    """
    Ensemble predictor combining multiple models and data sources.
    """
    
    def __init__(self):
        self.models = {}
        self.weights = {}
    
    def add_model(self, name: str, model, weight: float = 1.0):
        """Add a prediction model to the ensemble."""
        self.models[name] = model
        self.weights[name] = weight
    
    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Generate ensemble predictions.
        
        Args:
            features: Feature DataFrame
            
        Returns:
            DataFrame with ensemble predictions
        """
        predictions = []
        
        for name, model in self.models.items():
            pred = model.predict(features)
            if hasattr(pred, 'disaster_probability'):
                predictions.append(
                    pred['disaster_probability'] * self.weights[name]
                )
        
        # Weighted average
        total_weight = sum(self.weights.values())
        ensemble_prob = sum(predictions) / total_weight
        
        features['ensemble_probability'] = ensemble_prob
        features['ensemble_prediction'] = (ensemble_prob > 0.5).astype(int)
        
        # Prediction confidence
        features['prediction_confidence'] = np.abs(ensemble_prob - 0.5) * 2
        
        return features
```

---

## 9. Integration Points

### 9.1 Enhanced Configuration

```python
# config.py - Enhanced FEMA Configuration

# Enhanced FEMA data sources
FEMA_CONFIG = {
    "api_versions": ["v1", "v2", "v3"],
    "default_version": "v2",
    "endpoints": {
        "disaster_declarations": "DisasterDeclarationsSummaries",
        "ia_program": "IndividualAssistanceProgramDeclarations",
        "pa_program": "PublicAssistanceProgramDeclarations",
        "hmgp_program": "HazardMitigationProgramDeclarations",
        "registration_intake": "RegistrationIntakeIndividualsHouseholds",
        "public_assistance": "PublicAssistanceFundedProjectsDetails"
    },
    "nri_url": "https://hazards.fema.gov/nri/Content/StaticDocuments/data-download/NRI_Table_Counties.zip",
    "cache_hours": 24,
    "rate_limit_delay": 0.5
}

# Enhanced feature groups
ENHANCED_FEATURE_GROUPS = {
    "disaster_history": [
        "disaster_count",
        "disaster_count_recent",
        "disaster_count_5yr",
        "disaster_count_10yr",
        "disaster_acceleration",
        "disaster_frequency_trend",
        "avg_inter_disaster_days"
    ],
    "disaster_types": [
        "flood_count",
        "hurricane_count",
        "tornado_count",
        "fire_count",
        "severe_storm_count",
        "winter_storm_count",
        "drought_count",
        "earthquake_count",
        "primary_disaster_type",
        "disaster_type_diversity"
    ],
    "disaster_severity": [
        "avg_severity_score",
        "max_severity_score",
        "severity_trend",
        "catastrophic_events_count",
        "major_events_count"
    ],
    "damage_costs": [
        "total_damage_estimated",
        "avg_damage_per_event",
        "damage_per_capita",
        "ia_amount_total",
        "pa_amount_total",
        "hmgp_amount_total"
    ],
    "recovery_metrics": [
        "avg_recovery_days",
        "recovery_trend",
        "fast_recovery_rate",
        "slow_recovery_rate"
    ],
    "temporal_patterns": [
        "seasonality_score",
        "peak_months",
        "cyclical_periods",
        "anomaly_years"
    ],
    "spatial_patterns": [
        "cluster_id",
        "hotspot_score",
        "spatial_autocorrelation",
        "neighbor_avg_risk"
    ]
}

# Risk scoring weights
RISK_SCORING_WEIGHTS = {
    "disaster_frequency": 0.25,
    "disaster_severity": 0.20,
    "damage_costs": 0.20,
    "recovery_capacity": 0.15,
    "temporal_acceleration": 0.10,
    "spatial_clustering": 0.10
}
```

### 9.2 Pipeline Integration

```python
# src/pipeline/fema_pipeline.py

import pandas as pd
from pathlib import Path
from typing import Dict, Optional

class FEMADataPipeline:
    """
    Integrated FEMA data pipeline for ResilienceAI.
    
    Orchestrates data ingestion, processing, analysis, and feature generation.
    """
    
    def __init__(self, cache_dir: Path = None):
        from src.clients.fema_client import FEMAAPIClient
        from src.analysis.disaster_classification import DisasterClassifier
        from src.analysis.temporal_analysis import TemporalPatternAnalyzer
        from src.analysis.geographic_clustering import DisasterGeographicClustering
        from src.analysis.damage_estimation import DamageCostEstimator
        from src.analysis.recovery_analysis import RecoveryTimeAnalyzer
        
        self.client = FEMAAPIClient(cache_dir=cache_dir)
        self.classifier = DisasterClassifier()
        self.damage_estimator = DamageCostEstimator()
        
        self.raw_data = None
        self.processed_data = None
        self.features = None
    
    def run_full_pipeline(self, 
                          state: Optional[str] = None,
                          start_year: int = 2000,
                          end_year: int = 2024) -> Dict:
        """
        Execute the complete FEMA data pipeline.
        
        Args:
            state: Filter by state (optional)
            start_year: Start year for data
            end_year: End year for data
            
        Returns:
            Dictionary with pipeline results
        """
        from datetime import datetime
        
        print("=" * 60)
        print("FEMA Data Pipeline - Starting")
        print("=" * 60)
        
        # Step 1: Data Ingestion
        print("\n[1/6] Data Ingestion...")
        self.raw_data = self.client.get_disaster_declarations(
            state=state,
            start_date=datetime(start_year, 1, 1),
            end_date=datetime(end_year, 12, 31),
            include_ia=True,
            include_pa=True,
            include_hmgp=True
        )
        print(f"  Downloaded {len(self.raw_data)} disaster declarations")
        
        # Step 2: Data Enhancement
        print("\n[2/6] Data Enhancement...")
        from src.clients.fema_client import FEMADataEnhancer
        enhancer = FEMADataEnhancer(self.client)
        self.processed_data = enhancer.enhance_disaster_data(self.raw_data)
        self.processed_data = enhancer.estimate_damage_costs(self.processed_data)
        print(f"  Enhanced {len(self.processed_data)} records")
        
        # Step 3: Classification
        print("\n[3/6] Disaster Classification...")
        self.processed_data = self.classifier.classify_all(self.processed_data)
        print("  Classification complete")
        
        # Step 4: Temporal Analysis
        print("\n[4/6] Temporal Pattern Analysis...")
        temporal_analyzer = TemporalPatternAnalyzer(self.processed_data)
        temporal_results = temporal_analyzer.get_comprehensive_analysis()
        print("  Temporal analysis complete")
        
        # Step 5: Geographic Clustering
        print("\n[5/6] Geographic Clustering...")
        # Requires county coordinates
        if 'latitude' in self.processed_data.columns:
            geo_analyzer = DisasterGeographicClustering(self.processed_data)
            clustered = geo_analyzer.detect_hotspots_dbscan(eps_km=50)
            cluster_summary = geo_analyzer.get_cluster_summary()
            print(f"  Identified {cluster_summary.get('total_clusters', 0)} clusters")
        else:
            cluster_summary = {}
            print("  Skipped (no coordinate data)")
        
        # Step 6: Recovery Analysis
        print("\n[6/6] Recovery Time Analysis...")
        recovery_analyzer = RecoveryTimeAnalyzer(self.processed_data)
        recovery_data = recovery_analyzer.calculate_recovery_metrics()
        recovery_factors = recovery_analyzer.analyze_recovery_factors()
        print("  Recovery analysis complete")
        
        # Generate County-Level Features
        print("\n[Bonus] Generating County-Level Features...")
        county_features = self._generate_county_features()
        
        print("\n" + "=" * 60)
        print("FEMA Data Pipeline - Complete")
        print("=" * 60)
        
        return {
            'raw_count': len(self.raw_data),
            'processed_count': len(self.processed_data),
            'temporal_patterns': temporal_results,
            'cluster_summary': cluster_summary,
            'recovery_factors': recovery_factors,
            'county_features': county_features
        }
    
    def _generate_county_features(self) -> pd.DataFrame:
        """Generate county-level aggregated features."""
        if self.processed_data is None:
            raise ValueError("Pipeline not run. Call run_full_pipeline first.")
        
        df = self.processed_data
        
        # Aggregate by county
        county_features = df.groupby('fips').agg({
            'disaster_number': 'count',
            'severity_level': ['mean', 'max'],
            'adjusted_cost': ['sum', 'mean'],
            'recovery_days': 'mean',
            'incident_duration_days': 'mean',
            'iaAmount': 'sum',
            'paAmount': 'sum',
            'hmAmount': 'sum'
        }).reset_index()
        
        # Flatten column names
        county_features.columns = [
            'fips', 'disaster_count', 'avg_severity', 'max_severity',
            'total_damage', 'avg_damage', 'avg_recovery_days',
            'avg_incident_duration', 'total_ia', 'total_pa', 'total_hmgp'
        ]
        
        # Add disaster type counts
        type_counts = df.groupby(['fips', 'incidentType']).size().unstack(fill_value=0)
        type_counts.columns = [f'{c.lower().replace(" ", "_")}_count' 
                               for c in type_counts.columns]
        county_features = county_features.merge(
            type_counts.reset_index(), on='fips', how='left'
        )
        
        return county_features
    
    def save_results(self, output_dir: Path):
        """Save pipeline results to disk."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.raw_data is not None:
            self.raw_data.to_csv(output_dir / 'fema_raw.csv', index=False)
        
        if self.processed_data is not None:
            self.processed_data.to_csv(output_dir / 'fema_processed.csv', index=False)
        
        print(f"Results saved to {output_dir}")
```

---

## 10. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)
1. **Enhanced FEMA API Client** (`src/clients/fema_client.py`)
   - Multi-version API support
   - IA/PA/HMGP data integration
   - Robust caching and rate limiting

2. **Data Enhancement Pipeline** (`src/clients/fema_client.py` - FEMADataEnhancer)
   - Date parsing and standardization
   - FIPS code generation
   - Basic severity scoring

3. **Disaster Classification** (`src/analysis/disaster_classification.py`)
   - Multi-level disaster categorization
   - Severity classification
   - Category distribution analysis

### Phase 2: Analysis Core (Weeks 3-4)
4. **Temporal Pattern Analysis** (`src/analysis/temporal_analysis.py`)
   - Seasonality detection
   - Trend analysis
   - Anomaly detection

5. **Geographic Clustering** (`src/analysis/geographic_clustering.py`)
   - DBSCAN hotspot detection
   - Risk profile clustering
   - Spatial autocorrelation

6. **Damage Cost Estimation** (`src/analysis/damage_estimation.py`)
   - Historical cost analysis
   - Predictive cost modeling
   - Per-capita damage calculation

### Phase 3: Advanced Features (Weeks 5-6)
7. **Recovery Time Analysis** (`src/analysis/recovery_analysis.py`)
   - Recovery metrics calculation
   - Recovery factor identification
   - Recovery prediction

8. **Disaster Prediction Models** (`src/models/disaster_prediction.py`)
   - Occurrence prediction
   - Type prediction
   - Risk trajectory forecasting

### Phase 4: Integration (Week 7)
9. **Pipeline Integration** (`src/pipeline/fema_pipeline.py`)
   - Orchestrated data flow
   - Feature generation
   - Result persistence

10. **Dashboard Integration**
    - Visualization components
    - Interactive exploration
    - Alert system integration

---

## 11. File Structure

```
resilience_ai/
├── src/
│   ├── clients/
│   │   ├── __init__.py
│   │   └── fema_client.py          # Enhanced FEMA API client
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── disaster_classification.py  # Disaster type & severity
│   │   ├── temporal_analysis.py        # Temporal patterns
│   │   ├── geographic_clustering.py    # Spatial clustering
│   │   ├── damage_estimation.py        # Cost estimation
│   │   └── recovery_analysis.py        # Recovery metrics
│   ├── models/
│   │   ├── __init__.py
│   │   ├── fema_models.py          # Data models
│   │   └── disaster_prediction.py  # Prediction models
│   └── pipeline/
│       ├── __init__.py
│       └── fema_pipeline.py        # Integrated pipeline
├── config.py                       # Enhanced configuration
└── tests/
    └── test_fema_integration.py    # Unit tests
```

---

## 12. Key Metrics & KPIs

### Data Coverage Metrics
- **Disaster Records**: Target > 50,000 historical declarations
- **Geographic Coverage**: All US counties + territories
- **Temporal Coverage**: 1953-present (70+ years)
- **Data Completeness**: > 90% for key fields

### Analysis Quality Metrics
- **Prediction Accuracy**: AUC-ROC > 0.75 for occurrence prediction
- **Cost Estimation**: MAPE < 30% for damage estimates
- **Recovery Prediction**: Within 20% of actual recovery time
- **Cluster Detection**: > 80% precision for hotspot identification

### Performance Metrics
- **API Response Time**: < 2 seconds for cached queries
- **Pipeline Runtime**: < 5 minutes for full county analysis
- **Memory Usage**: < 4GB for national dataset
- **Cache Hit Rate**: > 80% for repeated queries

---

## 13. Conclusion

This comprehensive FEMA disaster data enhancement framework provides ResilienceAI with:

1. **Robust Data Foundation**: Multi-source FEMA integration with intelligent caching
2. **Advanced Analytics**: Temporal, spatial, and predictive analysis capabilities
3. **Actionable Insights**: Risk scoring, cost estimation, and recovery prediction
4. **Scalable Architecture**: Modular design supporting incremental enhancement
5. **Production Ready**: Comprehensive error handling, monitoring, and performance optimization

The implementation follows a phased approach, allowing for iterative development and validation while delivering value at each stage.

---

*Document Version: 1.0*
*Last Updated: 2026-02-17*
*Author: FEMA Disaster Analyst Agent*
