# ResilienceAI Healthcare Data Integration - Comprehensive Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of the current healthcare data capabilities in the ResilienceAI platform and proposes extensive enhancements for advanced healthcare intelligence, FHIR R4 interoperability, and clinical decision support.

**Repository:** https://github.com/GDogMcCoy/ResilienceAI  
**Branch:** claw-autonomous  
**Analysis Date:** February 2026  
**Document Version:** 1.0

---

## 1. Current Healthcare Capabilities Analysis

### 1.1 Existing Healthcare Data Sources

| Data Source | Current Implementation | File Location | Status |
|-------------|------------------------|---------------|--------|
| **CMS Nursing Homes** | Medicare Provider Data API | `src/download_data.py:167-230` | ✅ Active |
| **HIFLD Hospitals** | ArcGIS REST API | `src/download_data.py:62-165` | ✅ Active |
| **HIFLD Fire Stations** | ArcGIS REST API | `config.py:49-53` | ✅ Active |
| **HIFLD EMS Stations** | ArcGIS REST API | `config.py:49-53` | ✅ Active |
| **CDC SVI** | URL reference only | `config.py:39-42` | ⚠️ Partial |
| **FHIR R4 Export** | Custom implementation | `src/fhir_export.py` | ✅ Active |

### 1.2 Current FHIR R4 Implementation

**File:** `src/fhir_export.py` (382 lines, 14.8 KB)

#### Supported FHIR Resources:

```python
# Current FHIR Resources Implemented
FHIR_RESOURCES = {
    "Bundle": "Collection container for resources",
    "Location": "County geographic information with FIPS codes",
    "RiskAssessment": "Composite ML risk scoring with basis",
    "Observation": "County-level health metrics (10 types)"
}
```

#### Current Observation Types:

| Observation Code | Display Name | Unit | Category |
|------------------|--------------|------|----------|
| `vulnerability_index` | Vulnerability Index | 1 | survey |
| `isolation_index` | Infrastructure Isolation Index | 1 | survey |
| `poverty_pct` | Poverty Rate | % | survey |
| `elderly_pct` | Elderly Population Percentage | % | survey |
| `disability_pct` | Disability Rate | % | survey |
| `uninsured_pct` | Uninsured Rate | % | survey |
| `disaster_count` | Historical Disaster Count | 1 | survey |
| `disaster_count_recent` | Recent Disaster Count (2015+) | 1 | survey |
| `compound_risk_count` | Compound Risk Dimensions | 1 | survey |
| `dist_nearest_hospitals_km` | Distance to Nearest Hospital | km | survey |

### 1.3 Current Healthcare Metrics (66 Features)

**File:** `src/feature_engineering.py` (548 lines, 21.9 KB)

```python
# Healthcare-related features computed
HEALTHCARE_FEATURES = {
    # Distance-based metrics
    "dist_nearest_hospitals_km": "Distance to nearest hospital",
    "dist_2nd_nearest_hospitals_km": "Distance to 2nd nearest hospital",
    "dist_nearest_nursing_homes_km": "Distance to nearest nursing home",
    "dist_nearest_fire_stations_km": "Distance to fire station",
    "dist_nearest_ems_stations_km": "Distance to EMS station",
    
    # Count-based metrics
    "count_hospitals_50km": "Hospitals within 50km radius",
    "count_nursing_homes_50km": "Nursing homes within 50km",
    
    # Demographic vulnerability
    "elderly_pct": "Population 65+ percentage",
    "disability_pct": "Population with disabilities",
    "uninsured_pct": "Uninsured population percentage",
    "poverty_pct": "Population below poverty line"
}
```

---

## 2. Proposed Healthcare Intelligence Platform

### 2.1 Enhanced Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI HEALTHCARE INTELLIGENCE PLATFORM             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  DATA INGESTION │  │   FHIR SERVER   │  │  ANALYTICS      │              │
│  │  LAYER          │  │   INTERFACE     │  │  ENGINE         │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
│           │                    │                    │                        │
│  ┌────────▼────────────────────▼────────────────────▼────────┐              │
│  │              HEALTHCARE DATA LAKE (FHIR R4)               │              │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │              │
│  │  │ Patient  │ │ Location │ │ Provider │ │ Measure  │     │              │
│  │  │ Data     │ │ Data     │ │ Data     │ │ Reports  │     │              │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │              │
│  └──────────────────────────────────────────────────────────┘              │
│           │                    │                    │                        │
│  ┌────────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐              │
│  │  CLINICAL       │  │  PUBLIC HEALTH  │  │  HEALTH EQUITY  │              │
│  │  DECISION       │  │  REPORTING      │  │  ANALYSIS       │              │
│  │  SUPPORT        │  │  MODULE         │  │  MODULE         │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 New Healthcare Data Sources

| Data Source | API/URL | Priority | Implementation |
|-------------|---------|----------|----------------|
| **CMS Hospital Compare** | `data.cms.gov/provider-data/api` | P0 | `src/healthcare/cms_hospital_client.py` |
| **CMS Nursing Home Quality** | `data.cms.gov/provider-data/api` | P0 | Extend `download_data.py` |
| **HRSA Health Centers** | `data.hrsa.gov/tools/data-reporting` | P0 | `src/healthcare/hrsa_client.py` |
| **CDC SVI Data** | `svi.cdc.gov/data-and-documentation` | P0 | `src/healthcare/cdc_svi_client.py` |
| **Medicare Advantage** | `data.cms.gov/summary-statistics` | P1 | `src/healthcare/medicare_client.py` |
| **Medicaid State Data** | `medicaid.gov/medicaid/data` | P1 | `src/healthcare/medicaid_client.py` |
| **SAMHSA Facilities** | `findtreatment.gov/api` | P1 | `src/healthcare/samhsa_client.py` |
| **Dialysis Facility Compare** | `data.cms.gov/provider-data/api` | P2 | `src/healthcare/dialysis_client.py` |
| **Home Health Compare** | `data.cms.gov/provider-data/api` | P2 | `src/healthcare/homehealth_client.py` |
| **Physician Compare** | `data.cms.gov/provider-data/api` | P2 | `src/healthcare/physician_client.py` |

---

## 3. Comprehensive FHIR R4 Implementation

### 3.1 Extended FHIR Resource Mapping

**New File:** `src/healthcare/fhir_resource_mapper.py`

```python
"""
ResilienceAI - Comprehensive FHIR R4 Resource Mapper
Maps healthcare data to FHIR R4 resources for interoperability.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import uuid

@dataclass
class FHIRMappingConfig:
    """Configuration for FHIR resource mapping."""
    profile_url: str
    resource_type: str
    version: str = "4.0.1"

class HealthcareFHIRMapper:
    """
    Comprehensive FHIR R4 resource mapper for healthcare data.
    Supports all major healthcare facility types and quality metrics.
    """
    
    FHIR_VERSION = "4.0.1"
    
    # Profile URLs for US Core and SDOH
    PROFILES = {
        "us_core_location": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-location",
        "us_core_organization": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization",
        "us_core_practitioner": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitioner",
        "sdoh_condition": "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Condition",
        "sdoh_observation": "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Observation",
        "cms_quality_measure": "http://cms.gov/fhir/StructureDefinition/quality-measure",
    }
    
    # SNOMED CT codes for healthcare concepts
    SNOMED_CODES = {
        "nursing_home": "42665001",
        "hospital": "22232009",
        "healthcare_desert": "722471000124101",
        "health_equity": "398090004",
        "social_vulnerability": "160476009",
    }
    
    # LOINC codes for observations
    LOINC_CODES = {
        "bed_occupancy_rate": "74285-1",
        "patient_satisfaction": "64750-3",
        "readmission_rate": "72571-2",
        "mortality_rate": "72570-4",
        "staffing_ratio": "74286-9",
    }

    def __init__(self):
        self.bundle_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def create_organization(self, facility_data: Dict[str, Any]) -> Dict:
        """Create FHIR Organization resource for healthcare facility."""
        return {
            "resourceType": "Organization",
            "id": f"org-{facility_data.get('provider_id', uuid.uuid4().hex[:8])}",
            "meta": {
                "versionId": "1",
                "lastUpdated": self.timestamp,
                "profile": [self.PROFILES["us_core_organization"]]
            },
            "identifier": [
                {
                    "system": "http://cms.gov/fhir/NPI",
                    "value": facility_data.get("npi", "unknown")
                },
                {
                    "system": "http://cms.gov/fhir/CMS Certification Number",
                    "value": facility_data.get("provider_id", "unknown")
                }
            ],
            "active": True,
            "name": facility_data.get("name", "Unknown Facility"),
            "alias": [facility_data.get("dba_name")] if facility_data.get("dba_name") else [],
            "telecom": self._create_telecom(facility_data),
            "address": [self._create_address(facility_data)],
            "type": self._create_organization_type(facility_data.get("facility_type", "unknown")),
        }

    def create_location(self, facility_data: Dict[str, Any]) -> Dict:
        """Create FHIR Location resource with geospatial data."""
        return {
            "resourceType": "Location",
            "id": f"loc-{facility_data.get('provider_id', uuid.uuid4().hex[:8])}",
            "meta": {
                "versionId": "1",
                "lastUpdated": self.timestamp,
                "profile": [self.PROFILES["us_core_location"]]
            },
            "identifier": [{
                "system": "http://hl7.org/fhir/sid/us-npi",
                "value": facility_data.get("npi", "unknown")
            }],
            "status": "active",
            "name": facility_data.get("name", "Unknown Location"),
            "description": f"{facility_data.get('facility_type', 'Healthcare')} facility",
            "mode": "instance",
            "type": self._create_location_type(facility_data.get("facility_type")),
            "address": self._create_address(facility_data),
            "position": {
                "longitude": float(facility_data.get("longitude", 0)),
                "latitude": float(facility_data.get("latitude", 0)),
            },
        }

    def create_healthcare_desert_observation(self, county_data: Dict[str, Any]) -> Dict:
        """Create FHIR Observation for healthcare desert identification."""
        return {
            "resourceType": "Observation",
            "id": f"obs-desert-{county_data.get('fips', uuid.uuid4().hex[:8])}",
            "meta": {
                "versionId": "1",
                "lastUpdated": self.timestamp,
                "profile": [self.PROFILES["sdoh_observation"]]
            },
            "status": "final",
            "category": [
                {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "social-history",
                        "display": "Social History"
                    }]
                }
            ],
            "code": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": self.SNOMED_CODES["healthcare_desert"],
                    "display": "Healthcare desert"
                }],
                "text": "Healthcare Desert Classification"
            },
            "subject": {
                "reference": f"Location/location-county-{county_data.get('fips', 'unknown')}",
                "display": county_data.get("county_name", "Unknown County")
            },
            "effectiveDateTime": self.timestamp,
            "valueCodeableConcept": {
                "coding": [{
                    "system": "http://hl7.org/fhir/us/sdoh-clinicalcare/CodeSystem/SDOHCC-CodeSystemTemporaryCodes",
                    "code": county_data.get("desert_classification", "not-classified"),
                    "display": self._get_desert_display(county_data.get("desert_classification"))
                }],
                "text": county_data.get("desert_description", "Not classified")
            },
        }

    def _create_telecom(self, data: Dict) -> List[Dict]:
        """Create telecom contact points."""
        telecom = []
        if data.get("phone"):
            telecom.append({"system": "phone", "value": data["phone"], "use": "work"})
        if data.get("email"):
            telecom.append({"system": "email", "value": data["email"], "use": "work"})
        return telecom

    def _create_address(self, data: Dict) -> Dict:
        """Create FHIR address."""
        return {
            "use": "work",
            "type": "both",
            "line": [data.get("address", "")] if data.get("address") else [],
            "city": data.get("city", ""),
            "district": data.get("county", ""),
            "state": data.get("state", ""),
            "postalCode": str(data.get("zip", "")).replace(".0", ""),
            "country": "USA"
        }

    def _create_organization_type(self, facility_type: str) -> List[Dict]:
        """Map facility type to FHIR organization type."""
        return [{"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/organization-type",
            "code": "prov",
            "display": "Healthcare Provider"
        }]}]

    def _create_location_type(self, facility_type: str) -> List[Dict]:
        """Map facility type to FHIR location type."""
        type_mapping = {
            "hospital": {"system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode", "code": "HOSP", "display": "Hospital"},
            "nursing_home": {"system": "http://snomed.info/sct", "code": "42665001", "display": "Nursing home"},
        }
        return [{"coding": [type_mapping.get(facility_type, type_mapping["hospital"])]}]

    def _get_desert_display(self, classification: str) -> str:
        """Get display text for desert classification."""
        displays = {
            "primary_care_desert": "Primary Care Desert",
            "hospital_desert": "Hospital Desert",
            "specialty_desert": "Specialty Care Desert",
            "mental_health_desert": "Mental Health Desert",
            "not_desert": "Not a Healthcare Desert",
        }
        return displays.get(classification, "Unknown Classification")
```

---

## 4. Healthcare Facility Ratings Module

**New File:** `src/healthcare/facility_ratings.py`

```python
"""
ResilienceAI - Healthcare Facility Ratings Module
Integrates CMS Star Ratings, quality measures, and patient satisfaction data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class RatingCategory(Enum):
    """CMS rating categories."""
    OVERALL = "overall"
    HEALTH_INSPECTION = "health_inspection"
    STAFFING = "staffing"
    QUALITY_MEASURES = "quality_measures"
    PATIENT_EXPERIENCE = "patient_experience"


@dataclass
class FacilityRating:
    """Structured facility rating data."""
    provider_id: str
    facility_name: str
    facility_type: str
    overall_rating: Optional[int]
    health_inspection_rating: Optional[int]
    staffing_rating: Optional[int]
    quality_measures_rating: Optional[int]
    patient_experience_rating: Optional[float]
    rating_year: int
    rating_quarter: Optional[int]
    total_measures: int
    measures_with_data: int


class FacilityRatingsAnalyzer:
    """
    Analyze and aggregate healthcare facility ratings.
    Supports CMS Star Ratings and custom quality metrics.
    """
    
    # CMS Star Rating weights (as of 2024)
    CMS_WEIGHTS = {
        "health_inspection": 0.40,
        "quality_measures": 0.30,
        "staffing": 0.30
    }
    
    # Rating thresholds
    RATING_THRESHOLDS = {
        "excellent": (4.5, 5.0),
        "good": (3.5, 4.5),
        "average": (2.5, 3.5),
        "below_average": (1.5, 2.5),
        "poor": (1.0, 1.5)
    }
    
    def __init__(self, nursing_home_df: Optional[pd.DataFrame] = None,
                 hospital_df: Optional[pd.DataFrame] = None):
        self.nursing_home_df = nursing_home_df
        self.hospital_df = hospital_df
        self.ratings_cache = {}
    
    def calculate_composite_rating(self, facility_data: Dict) -> float:
        """Calculate composite rating using CMS methodology."""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for component, weight in self.CMS_WEIGHTS.items():
            rating_key = f"{component}_rating"
            if rating_key in facility_data and facility_data[rating_key] is not None:
                weighted_sum += facility_data[rating_key] * weight
                total_weight += weight
        
        if total_weight == 0:
            return facility_data.get('overall_rating', 0)
        
        return round(weighted_sum / total_weight, 2)
    
    def get_county_rating_summary(self, fips: str) -> Dict:
        """Get aggregated rating summary for a county."""
        if self.nursing_home_df is None:
            return {"error": "No nursing home data available"}
        
        county_facilities = self.nursing_home_df[self.nursing_home_df['fips'] == fips]
        
        if county_facilities.empty:
            return {"fips": fips, "facility_count": 0, "has_ratings": False}
        
        summary = {
            "fips": fips,
            "facility_count": len(county_facilities),
            "has_ratings": True,
            "overall_rating": {
                "mean": county_facilities['overall_rating'].mean(),
                "median": county_facilities['overall_rating'].median(),
                "min": county_facilities['overall_rating'].min(),
                "max": county_facilities['overall_rating'].max(),
                "std": county_facilities['overall_rating'].std()
            },
            "rating_distribution": self._calculate_rating_distribution(county_facilities),
            "top_rated_facilities": self._get_top_rated(county_facilities, n=3),
            "facilities_without_ratings": len(county_facilities[county_facilities['overall_rating'].isna()]),
            "county_tier": self._classify_county_tier({
                'overall_rating': {'mean': county_facilities['overall_rating'].mean()}
            })
        }
        
        return summary
    
    def _calculate_rating_distribution(self, df: pd.DataFrame) -> Dict:
        """Calculate rating distribution."""
        ratings = df['overall_rating'].dropna()
        distribution = {}
        for tier, (low, high) in self.RATING_THRESHOLDS.items():
            count = len(ratings[(ratings >= low) & (ratings < high)])
            distribution[tier] = {
                "count": count,
                "percentage": round(count / len(ratings) * 100, 2) if len(ratings) > 0 else 0
            }
        return distribution
    
    def _get_top_rated(self, df: pd.DataFrame, n: int = 3) -> List[Dict]:
        """Get top-rated facilities."""
        top = df.nlargest(n, 'overall_rating')
        return [{"provider_id": row['provider_id'], "name": row.get('name', 'Unknown'), 
                 "rating": row['overall_rating']} for _, row in top.iterrows()]
    
    def _classify_county_tier(self, summary: Dict) -> str:
        """Classify county into rating tier."""
        mean_rating = summary.get('overall_rating', {}).get('mean', 0)
        if mean_rating >= 4.0: return "excellent"
        elif mean_rating >= 3.0: return "good"
        elif mean_rating >= 2.0: return "average"
        elif mean_rating >= 1.0: return "below_average"
        else: return "insufficient_data"
```

---

## 5. Healthcare Desert Identification Module

**New File:** `src/healthcare/healthcare_deserts.py`

```python
"""
ResilienceAI - Healthcare Desert Identification Module
Identifies areas with limited healthcare access based on multiple criteria.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DesertType(Enum):
    """Types of healthcare deserts."""
    PRIMARY_CARE = "primary_care_desert"
    HOSPITAL = "hospital_desert"
    SPECIALTY = "specialty_desert"
    MENTAL_HEALTH = "mental_health_desert"
    PHARMACY = "pharmacy_desert"


@dataclass
class DesertCriteria:
    """Criteria for identifying healthcare deserts."""
    max_distance_km: float
    min_providers_per_1000: float
    min_beds_per_1000: float
    max_travel_time_minutes: float
    population_threshold: int


class HealthcareDesertAnalyzer:
    """
    Identify and analyze healthcare deserts using multiple criteria.
    Based on HRSA and CMS guidelines for healthcare access.
    """
    
    # HRSA-designated shortage criteria
    DEFAULT_CRITERIA = {
        DesertType.PRIMARY_CARE: DesertCriteria(
            max_distance_km=50, min_providers_per_1000=0.5, min_beds_per_1000=0,
            max_travel_time_minutes=60, population_threshold=1000
        ),
        DesertType.HOSPITAL: DesertCriteria(
            max_distance_km=80, min_providers_per_1000=0, min_beds_per_1000=2.0,
            max_travel_time_minutes=90, population_threshold=5000
        ),
        DesertType.MENTAL_HEALTH: DesertCriteria(
            max_distance_km=60, min_providers_per_1000=0.1, min_beds_per_1000=0.5,
            max_travel_time_minutes=75, population_threshold=2000
        ),
    }
    
    def __init__(self, county_df: Optional[pd.DataFrame] = None,
                 facilities_df: Optional[pd.DataFrame] = None):
        self.county_df = county_df
        self.facilities_df = facilities_df
        self.criteria = self.DEFAULT_CRITERIA.copy()
    
    def identify_deserts(self, desert_types: Optional[List[DesertType]] = None) -> pd.DataFrame:
        """Identify healthcare deserts for specified types."""
        if self.county_df is None:
            raise ValueError("County data required")
        
        if desert_types is None:
            desert_types = list(DesertType)
        
        results = []
        for _, county in self.county_df.iterrows():
            county_deserts = self._analyze_county(county, desert_types)
            results.append(county_deserts)
        
        return pd.DataFrame(results)
    
    def _analyze_county(self, county: pd.Series, desert_types: List[DesertType]) -> Dict:
        """Analyze a single county for healthcare deserts."""
        fips = county.get('fips', '')
        county_name = county.get('county_name', 'Unknown')
        population = county.get('population', 0)
        
        result = {
            'fips': fips, 'county_name': county_name, 'population': population,
            'deserts': [], 'desert_score': 0, 'access_summary': {}
        }
        
        for desert_type in desert_types:
            is_desert, details = self._check_desert_criteria(county, desert_type)
            result['access_summary'][desert_type.value] = details
            if is_desert:
                result['deserts'].append({
                    'type': desert_type.value, 'severity': details['severity'],
                    'affected_population': population, 'details': details
                })
                result['desert_score'] += details['severity_score']
        
        result['overall_classification'] = self._classify_overall_desert(
            result['deserts'], result['desert_score']
        )
        return result
    
    def _check_desert_criteria(self, county: pd.Series, desert_type: DesertType) -> Tuple[bool, Dict]:
        """Check if county meets desert criteria for a specific type."""
        criteria = self.criteria[desert_type]
        population = county.get('population', 0)
        
        details = {'type': desert_type.value, 'criteria_met': [], 'criteria_failed': [],
                   'severity': 'none', 'severity_score': 0}
        
        if population < criteria.population_threshold:
            details['criteria_failed'].append('population_below_threshold')
            return False, details
        
        # Check distance criteria
        distance_col = f"dist_nearest_{desert_type.value.split('_')[0]}_km"
        if distance_col in county:
            distance = county[distance_col]
            if pd.notna(distance) and distance > criteria.max_distance_km:
                details['criteria_failed'].append('distance_exceeded')
                details['distance_km'] = distance
        
        is_desert = len(details['criteria_failed']) > 0
        if is_desert:
            details['severity_score'] = len(details['criteria_failed'])
            details['severity'] = 'severe' if details['severity_score'] >= 3 else \
                                 'moderate' if details['severity_score'] == 2 else 'mild'
        
        return is_desert, details
    
    def _classify_overall_desert(self, deserts: List[Dict], score: int) -> str:
        """Classify overall desert status."""
        if len(deserts) == 0: return "not_desert"
        desert_types = set(d['type'] for d in deserts)
        if len(desert_types) >= 4: return "comprehensive_desert"
        elif len(desert_types) >= 2: return "multi_type_desert"
        elif score >= 5: return "severe_single_desert"
        else: return "single_desert"
    
    def get_desert_statistics(self) -> Dict:
        """Get summary statistics for healthcare deserts."""
        if self.county_df is None:
            return {"error": "No county data available"}
        
        deserts_df = self.identify_deserts()
        total_counties = len(deserts_df)
        desert_counties = len(deserts_df[deserts_df['deserts'].apply(len) > 0])
        
        return {
            "total_counties_analyzed": total_counties,
            "desert_counties": desert_counties,
            "desert_percentage": round(desert_counties / total_counties * 100, 2),
            "affected_population": int(deserts_df[deserts_df['deserts'].apply(len) > 0]['population'].sum()),
            "desert_type_breakdown": {dt.value: sum(1 for d in deserts_df['deserts'] 
                                                     if any(x['type'] == dt.value for x in d))
                                      for dt in DesertType},
            "severity_distribution": {"severe": 0, "moderate": 0, "mild": 0}
        }
```

---

## 6. Medicare/Medicaid Data Integration Module

**New File:** `src/healthcare/medicare_medicaid_client.py`

```python
"""
ResilienceAI - Medicare/Medicaid Data Integration Client
Integrates CMS Medicare and Medicaid data for comprehensive analysis.
"""

import pandas as pd
import requests
from typing import Dict, List, Optional
from pathlib import Path
import json

from config import CACHE_DIR, RAW_DIR


class CMSDataClient:
    """Client for CMS Medicare and Medicaid data APIs."""
    
    CMS_APIS = {
        "provider_data": "https://data.cms.gov/provider-data/api/1/datastore/query",
        "nursing_home": "https://data.cms.gov/provider-data/api/1/datastore/query/4pq5-n9py",
    }
    
    DATASET_IDS = {
        "hospital_general": "77hc-ibv8",
        "nursing_home_quality": "4pq5-n9py",
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def download_hospital_data(self, state: Optional[str] = None, force: bool = False) -> pd.DataFrame:
        """Download Hospital Compare data from CMS."""
        cache_name = f"cms_hospitals_{state or 'all'}"
        cache_path = CACHE_DIR / f"{cache_name}.csv"
        
        if cache_path.exists() and not force:
            return pd.read_csv(cache_path)
        
        url = f"{self.CMS_APIS['provider_data']}/{self.DATASET_IDS['hospital_general']}"
        all_records = []
        offset, limit = 0, 500
        
        while True:
            params = {"offset": offset, "limit": limit, "format": "json"}
            if state:
                params["conditions[0][property]"] = "state"
                params["conditions[0][value]"] = state
                params["conditions[0][operator]"] = "="
            
            response = self.session.get(url, params=params, timeout=120)
            response.raise_for_status()
            data = response.json()
            records = data.get("results", [])
            
            if not records: break
            all_records.extend(records)
            offset += limit
            if len(records) < limit: break
        
        df = pd.DataFrame(all_records)
        df.to_csv(cache_path, index=False)
        return df
    
    def download_nursing_home_quality(self, force: bool = False) -> pd.DataFrame:
        """Download Nursing Home Compare quality data."""
        cache_path = CACHE_DIR / "cms_nursing_home_quality.csv"
        if cache_path.exists() and not force:
            return pd.read_csv(cache_path)
        
        url = self.CMS_APIS['nursing_home']
        all_records, offset, limit = [], 0, 1000
        
        while True:
            params = {"offset": offset, "limit": limit, "format": "json"}
            response = self.session.get(url, params=params, timeout=120)
            response.raise_for_status()
            data = response.json()
            records = data.get("results", [])
            
            if not records: break
            all_records.extend(records)
            offset += limit
            if len(records) < limit: break
        
        df = pd.DataFrame(all_records)
        column_mapping = {
            "federal_provider_number": "provider_id", "provider_name": "name",
            "overall_rating": "overall_rating", "health_inspection_rating": "health_inspection_rating",
            "staffing_rating": "staffing_rating"
        }
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        df.to_csv(cache_path, index=False)
        return df
    
    def get_state_summary(self, state: str, year: int = 2023) -> Dict:
        """Get summary statistics for a state."""
        hospital_df = self.download_hospital_data(state=state)
        nursing_df = self.download_nursing_home_quality()
        nursing_df = nursing_df[nursing_df['state'] == state]
        
        return {
            "state": state, "year": year,
            "hospitals": {
                "count": len(hospital_df),
                "beds_total": hospital_df.get('bed_count', pd.Series()).sum(),
            },
            "nursing_homes": {
                "count": len(nursing_df),
                "avg_overall_rating": nursing_df.get('overall_rating', pd.Series()).mean(),
            }
        }
```

---

## 7. Health Equity Analysis Module

**New File:** `src/healthcare/health_equity_analyzer.py`

```python
"""
ResilienceAI - Health Equity Analysis Module
Analyzes healthcare disparities across demographic and socioeconomic dimensions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class HealthEquityAnalyzer:
    """Analyze health equity across counties and populations."""
    
    SVI_THEMES = {
        "socioeconomic": {"weight": 0.25, "variables": ["EPL_POV", "EPL_UNEMP", "EPL_PCI", "EPL_NOHSDP"]},
        "household_composition": {"weight": 0.25, "variables": ["EPL_AGE65", "EPL_AGE17", "EPL_DISABL"]},
        "minority_status": {"weight": 0.25, "variables": ["EPL_MINRTY", "EPL_LIMENG"]},
    }
    
    EQUITY_DIMENSIONS = ["insurance_status", "income_level", "race_ethnicity", "geographic_access"]
    
    def __init__(self, svi_df: Optional[pd.DataFrame] = None,
                 census_df: Optional[pd.DataFrame] = None):
        self.svi_df = svi_df
        self.census_df = census_df
    
    def calculate_health_equity_index(self, fips: str) -> Dict:
        """Calculate comprehensive health equity index for a county."""
        equity_data = {
            "fips": fips, "overall_equity_score": 0,
            "dimension_scores": {}, "disparities": [], "vulnerable_populations": []
        }
        
        if self.svi_df is not None:
            svi_data = self.svi_df[self.svi_df['FIPS'] == fips]
            if not svi_data.empty:
                equity_data["svi_score"] = svi_data.iloc[0].get('RPL_THEMES', 0)
        
        equity_data["dimension_scores"]["access"] = 0.5  # Placeholder
        equity_data["dimension_scores"]["quality"] = 0.5
        equity_data["dimension_scores"]["outcomes"] = 0.5
        
        dimension_scores = [v for v in equity_data["dimension_scores"].values() if isinstance(v, (int, float))]
        if dimension_scores:
            equity_data["overall_equity_score"] = np.mean(dimension_scores)
        
        return equity_data
    
    def identify_health_equity_hotspots(self, threshold: float = 0.7) -> List[Dict]:
        """Identify counties with significant health equity challenges."""
        if self.svi_df is None:
            return []
        
        hotspots = []
        for _, row in self.svi_df.iterrows():
            svi_score = row.get('RPL_THEMES', 0)
            if svi_score >= threshold:
                hotspots.append({
                    "fips": row.get('FIPS'), "county_name": row.get('LOCATION'),
                    "state": row.get('ST_ABBR'), "svi_score": svi_score
                })
        
        hotspots.sort(key=lambda x: x["svi_score"], reverse=True)
        return hotspots
```

---

## 8. Public Health Reporting Module

**New File:** `src/healthcare/public_health_reporter.py`

```python
"""
ResilienceAI - Public Health Reporting Module
Generates public health reports compliant with CDC and state requirements.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json

from config import REPORTS_DIR


class PublicHealthReporter:
    """Generate public health reports for various stakeholders."""
    
    REPORT_TEMPLATES = {
        "cdc_svi": {"name": "CDC Social Vulnerability Index Report", "frequency": "annual"},
        "cms_quality": {"name": "CMS Quality Measures Report", "frequency": "quarterly"},
        "health_equity": {"name": "Health Equity Assessment Report", "frequency": "annual"},
    }
    
    def __init__(self, county_df: Optional[pd.DataFrame] = None,
                 facilities_df: Optional[pd.DataFrame] = None):
        self.county_df = county_df
        self.facilities_df = facilities_df
    
    def generate_cdc_svi_report(self, state: Optional[str] = None) -> Dict:
        """Generate CDC Social Vulnerability Index report."""
        if self.county_df is None:
            return {"error": "County data required"}
        
        df = self.county_df.copy()
        if state:
            df = df[df['state'] == state]
        
        return {
            "report_type": "CDC SVI",
            "generated_at": datetime.utcnow().isoformat(),
            "reporting_period": f"{datetime.utcnow().year}",
            "geographic_scope": state or "national",
            "summary": {
                "counties_reported": len(df),
                "total_population": int(df.get('population', pd.Series()).sum()),
                "avg_svi_score": df.get('svi_score', pd.Series()).mean(),
                "high_vulnerability_counties": len(df[df.get('svi_score', pd.Series()) > 0.75]),
            },
            "county_data": [{"fips": row.get('fips'), "county_name": row.get('county_name'),
                           "svi_score": row.get('svi_score')} for _, row in df.iterrows()]
        }
    
    def export_report(self, report: Dict, format: str = "json",
                      output_path: Optional[Path] = None) -> Dict:
        """Export report to specified format."""
        report_type = report.get("report_type", "report").replace(" ", "_").lower()
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        if output_path is None:
            output_path = REPORTS_DIR / f"{report_type}_{timestamp}"
        
        if format == "json":
            output_path = output_path.with_suffix('.json')
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif format == "csv" and "county_data" in report:
            output_path = output_path.with_suffix('.csv')
            pd.DataFrame(report["county_data"]).to_csv(output_path, index=False)
        
        return {"output_path": str(output_path), "format": format, "report_type": report.get("report_type")}
```

---

## 9. Healthcare Resource Allocation Module

**New File:** `src/healthcare/resource_allocator.py`

```python
"""
ResilienceAI - Healthcare Resource Allocation Module
Optimizes allocation of healthcare resources based on need and impact.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class ResourceAllocator:
    """Optimize healthcare resource allocation using multi-criteria decision analysis."""
    
    RESOURCE_TYPES = {
        "facility": {
            "primary_care_clinic": {"cost": 2000000, "capacity": 5000},
            "hospital": {"cost": 50000000, "capacity": 50000},
            "nursing_home": {"cost": 10000000, "capacity": 120},
        },
    }
    
    CRITERIA_WEIGHTS = {
        "population_need": 0.30, "current_access_gap": 0.25,
        "vulnerability_index": 0.20, "existing_capacity": 0.15, "cost_effectiveness": 0.10
    }
    
    def __init__(self, county_df: Optional[pd.DataFrame] = None):
        self.county_df = county_df
    
    def optimize_facility_placement(self, budget: float, facility_type: str,
                                     state: Optional[str] = None) -> List[Dict]:
        """Optimize facility placement given budget constraints."""
        if self.county_df is None:
            return []
        
        df = self.county_df.copy()
        if state:
            df = df[df['state'] == state]
        
        df['priority_score'] = df.apply(self._calculate_priority_score, axis=1)
        df = df.sort_values('priority_score', ascending=False)
        
        facility_info = self.RESOURCE_TYPES["facility"].get(facility_type)
        if not facility_info:
            return []
        
        placements, remaining_budget = [], budget
        
        for _, county in df.iterrows():
            if remaining_budget < facility_info["cost"]:
                break
            
            placements.append({
                "fips": county['fips'], "county_name": county['county_name'],
                "facility_type": facility_type, "priority_score": county['priority_score'],
                "estimated_cost": facility_info["cost"],
                "population_served": county.get('population', 0)
            })
            remaining_budget -= facility_info["cost"]
        
        return placements
    
    def _calculate_priority_score(self, county: pd.Series) -> float:
        """Calculate priority score for resource allocation."""
        score = 0
        population = county.get('population', 0)
        score += min(population / 10000, 10) * self.CRITERIA_WEIGHTS["population_need"]
        
        vulnerability = county.get('vulnerability_index', 0)
        score += vulnerability * 10 * self.CRITERIA_WEIGHTS["vulnerability_index"]
        
        return round(score, 2)
    
    def calculate_roi(self, intervention: Dict, timeframe_years: int = 5) -> Dict:
        """Calculate return on investment for healthcare interventions."""
        initial_cost = intervention.get("cost", 0)
        annual_operating_cost = intervention.get("annual_cost", initial_cost * 0.1)
        people_served = intervention.get("people_served", 0)
        
        hospitalizations_avoided = people_served * 0.05
        annual_benefit = hospitalizations_avoided * 10000
        
        total_cost = initial_cost + (annual_operating_cost * timeframe_years)
        total_benefit = annual_benefit * timeframe_years
        roi = (total_benefit - total_cost) / total_cost if total_cost > 0 else 0
        
        return {
            "intervention": intervention.get("name", "Unknown"),
            "initial_cost": initial_cost, "total_cost_5yr": total_cost,
            "total_benefit_5yr": total_benefit, "roi_5yr": round(roi, 3),
            "people_served": people_served
        }
```

---

## 10. Clinical Decision Support Module

**New File:** `src/healthcare/clinical_decision_support.py`

```python
"""
ResilienceAI - Clinical Decision Support Module
Provides evidence-based recommendations for healthcare planning and response.
"""

import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ClinicalGuideline:
    """Clinical guideline reference."""
    guideline_id: str
    title: str
    source: str
    evidence_level: str
    recommendations: List[str]


class ClinicalDecisionSupport:
    """Provide clinical decision support for healthcare planning."""
    
    GUIDELINES = {
        "disaster_preparedness": ClinicalGuideline(
            guideline_id="CDC-DP-2024",
            title="Healthcare Disaster Preparedness Guidelines",
            source="CDC", evidence_level="A",
            recommendations=["Maintain 96-hour supply of critical medications",
                           "Establish redundant communication systems"]
        ),
        "chronic_care_management": ClinicalGuideline(
            guideline_id="CMS-CCM-2024",
            title="Chronic Care Management Guidelines",
            source="CMS", evidence_level="A",
            recommendations=["Implement care coordination programs",
                           "Use remote patient monitoring"]
        ),
    }
    
    RISK_THRESHOLDS = {"low": 0.3, "moderate": 0.6, "high": 0.8}
    
    def __init__(self, county_df: Optional[pd.DataFrame] = None):
        self.county_df = county_df
    
    def assess_disaster_readiness(self, fips: str) -> Dict:
        """Assess healthcare disaster readiness for a county."""
        if self.county_df is None:
            return {"error": "County data required"}
        
        county = self.county_df[self.county_df['fips'] == fips]
        if county.empty:
            return {"error": f"County {fips} not found"}
        
        row = county.iloc[0]
        
        # Calculate readiness scores
        facility_redundancy = min(row.get('count_hospitals_50km', 0) / 3, 1.0)
        access_diversity = 1.0 if row.get('dist_nearest_hospitals_km', 100) < 50 else 0.5
        
        readiness_score = (facility_redundancy * 0.4 + access_diversity * 0.6)
        
        return {
            "fips": fips, "county_name": row.get('county_name'),
            "readiness_score": round(readiness_score, 3),
            "risk_level": self._classify_risk(readiness_score),
            "recommendations": self._generate_readiness_recommendations(readiness_score),
            "applicable_guidelines": ["disaster_preparedness"]
        }
    
    def _classify_risk(self, score: float) -> str:
        """Classify risk level based on score."""
        if score >= self.RISK_THRESHOLDS["high"]: return "low"
        elif score >= self.RISK_THRESHOLDS["moderate"]: return "moderate"
        else: return "high"
    
    def _generate_readiness_recommendations(self, score: float) -> List[str]:
        """Generate readiness recommendations based on score."""
        if score >= 0.8:
            return ["Maintain current preparedness levels", "Conduct regular drills"]
        elif score >= 0.5:
            return ["Increase facility redundancy", "Improve communication systems"]
        else:
            return ["Urgent: Establish backup facilities", "Implement emergency protocols"]
```

---

## 11. Proposed Folder Structure

```
resilienceai/
├── src/
│   ├── healthcare/                    # NEW: Healthcare intelligence modules
│   │   ├── __init__.py
│   │   ├── fhir_resource_mapper.py    # FHIR R4 resource mapping
│   │   ├── fhir_bundle_exporter.py    # Enhanced FHIR export
│   │   ├── facility_ratings.py        # CMS ratings integration
│   │   ├── patient_outcomes.py        # Patient outcome metrics
│   │   ├── healthcare_deserts.py      # Desert identification
│   │   ├── medicare_medicaid_client.py # CMS data integration
│   │   ├── health_equity_analyzer.py  # Health equity analysis
│   │   ├── public_health_reporter.py  # Public health reporting
│   │   ├── resource_allocator.py      # Resource optimization
│   │   ├── clinical_decision_support.py # Clinical DSS
│   │   ├── data_clients/              # Healthcare data clients
│   │   │   ├── __init__.py
│   │   │   ├── cms_client.py
│   │   │   ├── hrsa_client.py
│   │   │   ├── cdc_svi_client.py
│   │   │   └── samhsa_client.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── fhir_validators.py
│   │       └── quality_calculators.py
│   ├── fhir_export.py                 # EXISTING: Basic FHIR export
│   ├── download_data.py               # EXISTING: Data acquisition
│   └── ...
├── data/
│   ├── raw/
│   │   ├── cms/                       # NEW: CMS data
│   │   │   ├── nursing_homes/
│   │   │   ├── hospitals/
│   │   │   └── quality_measures/
│   │   └── healthcare/                # NEW: Healthcare data
│   │       ├── facility_ratings/
│   │       ├── patient_outcomes/
│   │       └── health_equity/
│   └── processed/
│       └── healthcare/                # NEW: Processed healthcare data
├── reports/
│   └── healthcare/                    # NEW: Healthcare reports
│       ├── fhir/
│       ├── public_health/
│       └── equity/
└── tests/
    └── healthcare/                    # NEW: Healthcare module tests
        ├── test_fhir_mapper.py
        ├── test_facility_ratings.py
        └── test_healthcare_deserts.py
```

---

## 12. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-4)

| Priority | Module | Effort | Impact |
|----------|--------|--------|--------|
| P0 | FHIR Resource Mapper | 5 days | High |
| P0 | CMS Data Client Enhancement | 3 days | High |
| P0 | Healthcare Desert Identification | 4 days | High |
| P0 | Facility Ratings Integration | 3 days | Medium |

### Phase 2: Analytics (Weeks 5-8)

| Priority | Module | Effort | Impact |
|----------|--------|--------|--------|
| P1 | Patient Outcomes Module | 5 days | High |
| P1 | Health Equity Analyzer | 4 days | High |
| P1 | Public Health Reporter | 3 days | Medium |
| P1 | Medicare/Medicaid Integration | 4 days | High |

### Phase 3: Optimization (Weeks 9-12)

| Priority | Module | Effort | Impact |
|----------|--------|--------|--------|
| P2 | Resource Allocator | 5 days | Medium |
| P2 | Clinical Decision Support | 4 days | Medium |
| P2 | Enhanced FHIR Bundle Exporter | 3 days | Medium |
| P2 | Integration & Testing | 5 days | High |

---

## 13. Compliance Considerations

### 13.1 HIPAA Compliance

- **De-identification**: All patient data must be de-identified per Safe Harbor method
- **Data Minimization**: Only collect necessary data elements
- **Access Controls**: Implement role-based access for healthcare data
- **Audit Logging**: Log all access to healthcare data

### 13.2 FHIR Compliance

- **US Core Profiles**: Implement US Core 6.1.0 profiles
- **SDOH Clinical Care**: Support SDOH Clinical Care IG
- **Bulk Data Access**: Implement FHIR Bulk Data API for exports

### 13.3 CMS Data Use

- **Terms of Service**: Comply with CMS data use agreements
- **Attribution**: Properly attribute CMS as data source
- **Updates**: Regular data refresh per CMS schedules

---

## 14. Integration Points

### 14.1 Existing Code Integration

```python
# Integration with existing fhir_export.py
from src.healthcare.fhir_bundle_exporter import EnhancedFHIRExporter

class FHIRExportIntegration:
    """Integrate enhanced FHIR export with existing code."""
    
    def __init__(self, df=None):
        self.enhanced_exporter = EnhancedFHIRExporter(df)
    
    def export_with_healthcare_data(self, fips, format="json"):
        """Export with enhanced healthcare data."""
        # Use existing county export
        basic_export = self._export_county_basic(fips)
        
        # Add healthcare-specific resources
        healthcare_resources = self.enhanced_exporter.export_county_healthcare(fips)
        
        # Merge and return
        return self._merge_exports(basic_export, healthcare_resources)
```

### 14.2 Dashboard Integration

```python
# Integration with Streamlit dashboard
import streamlit as st

def render_healthcare_dashboard():
    """Render healthcare intelligence dashboard."""
    st.header("Healthcare Intelligence")
    
    # Facility ratings
    st.subheader("Facility Ratings")
    ratings_data = get_facility_ratings(selected_county)
    st.dataframe(ratings_data)
    
    # Healthcare deserts
    st.subheader("Healthcare Desert Analysis")
    desert_data = analyze_healthcare_deserts(selected_county)
    st.map(desert_data)
    
    # Health equity
    st.subheader("Health Equity Metrics")
    equity_data = calculate_health_equity(selected_county)
    st.bar_chart(equity_data)
```

---

## 15. Summary

This comprehensive healthcare data enhancement plan provides:

1. **Advanced FHIR R4 Implementation**: Full support for healthcare interoperability
2. **Comprehensive Data Integration**: CMS, HRSA, CDC, and Medicaid data sources
3. **Healthcare Intelligence**: Desert identification, equity analysis, outcome metrics
4. **Clinical Decision Support**: Evidence-based recommendations and risk assessment
5. **Public Health Reporting**: CDC and CMS compliant reporting
6. **Resource Optimization**: Data-driven resource allocation

**Total Estimated Effort**: 12 weeks (3 developers)  
**Key Deliverables**: 10 new modules, enhanced FHIR export, comprehensive healthcare analytics

---

## Appendix A: FHIR Resource Types Summary

| Resource Type | Purpose | Profile |
|---------------|---------|---------|
| Organization | Healthcare facilities | US Core Organization |
| Location | Geographic locations | US Core Location |
| Practitioner | Healthcare providers | US Core Practitioner |
| Observation | Health metrics | SDOHCC Observation |
| MeasureReport | Quality measures | CMS Quality Measure |
| RiskAssessment | Risk scores | Custom Profile |
| Condition | Health conditions | SDOHCC Condition |
| Bundle | Resource collections | FHIR R4 Bundle |

## Appendix B: Data Source URLs

| Source | URL | Update Frequency |
|--------|-----|------------------|
| CMS Provider Data | data.cms.gov/provider-data | Monthly |
| CDC SVI | svi.cdc.gov | Annual |
| HRSA Data | data.hrsa.gov | Quarterly |
| Medicaid | medicaid.gov/data | Annual |
| SAMHSA | findtreatment.gov | Monthly |

---

*Document generated for ResilienceAI Healthcare Data Enhancement Initiative*
*Version 1.0 - February 2026*
