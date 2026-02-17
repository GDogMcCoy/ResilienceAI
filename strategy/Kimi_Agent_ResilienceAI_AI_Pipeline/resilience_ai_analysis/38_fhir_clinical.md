# ResilienceAI FHIR Clinical Data Enhancement Guide

## Executive Summary

This document provides a comprehensive FHIR R4 clinical data integration strategy for ResilienceAI, transforming disaster vulnerability assessment data into standardized healthcare interoperability formats. The implementation enables seamless integration with EHR systems, public health agencies, and emergency response networks.

**Current State Analysis:**
- Basic FHIR export in `src/fhir_export.py` (382 lines)
- Limited to Location, RiskAssessment, and Observation resources
- No SMART on FHIR authentication
- Missing clinical terminology mappings (SNOMED CT, LOINC)
- No FHIR server integration capabilities
- Limited data privacy controls

**Target State:**
- Full FHIR R4 compliance with US Core profiles
- Complete SDOH (Social Determinants of Health) integration
- SMART on FHIR authentication
- Bulk FHIR export capabilities
- Clinical terminology standardization
- HIPAA-compliant data handling

---

## 1. FHIR Architecture Overview

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ResilienceAI FHIR Architecture                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Data       │    │   Feature    │    │  Predictive  │                   │
│  │   Ingestion  │───▶│  Engineering │───▶│    Models    │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                   │                   │                           │
│         ▼                   ▼                   ▼                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FHIR Resource Mapping Layer                       │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Location │ │RiskAssess│ │Observat. │ │ Condition│ │  Bundle  │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FHIR Enhancement Layer                            │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │   │
│  │  │   Patient  │ │  SDOH-CC   │ │   Group    │ │DocumentRef │       │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘       │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │   │
│  │  │  CarePlan  │ │  Consent   │ │Provenance  │ │  Endpoint  │       │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Integration & Security Layer                      │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │   │
│  │  │SMART on    │ │  FHIR      │ │  Bulk      │ │  Audit     │       │   │
│  │  │FHIR Auth   │ │  Server    │ │  Export    │ │  Logging   │       │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    External Systems                                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │   EHR    │ │  HIE     │ │  Public  │ │Emergency │ │  CMS     │  │   │
│  │  │ Systems  │ │ Networks │ │  Health  │ │Response  │ │  TEFCA   │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Resource Type Mapping

| ResilienceAI Data | FHIR R4 Resource | Profile | Use Case |
|-------------------|------------------|---------|----------|
| County Location | Location | US Core Location | Geographic reference |
| Risk Score | RiskAssessment | Standard | Vulnerability scoring |
| Demographics | Observation | US Core Observation | Population metrics |
| Vulnerability | Condition | SDOHCC Condition | Health disparities |
| Population Group | Group | Standard | Cohort management |
| Interventions | CarePlan | US Core CarePlan | Action planning |
| Data Source | Provenance | Standard | Data lineage |
| Consent | Consent | Standard | Privacy control |
| Reports | DocumentReference | US Core DocRef | Document sharing |

---

## 2. Enhanced FHIR Resource Implementation

### 2.1 Enhanced FHIRExporter Class

**File:** `src/fhir/fhir_exporter_enhanced.py`

```python
"""
ResilienceAI - Enhanced FHIR R4 Export Module
Comprehensive clinical data integration with FHIR R4 standards.

Features:
- Full US Core profile compliance
- SDOH Clinical Care integration
- SMART on FHIR authentication
- Bulk FHIR export capabilities
- Clinical terminology mapping (SNOMED CT, LOINC, ICD-10)
- HIPAA-compliant data handling
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import hashlib
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin

from config import PROCESSED_DIR, REPORTS_DIR, MODELS_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FHIRVersion(Enum):
    """FHIR version enumeration."""
    R4 = "4.0.1"
    R4B = "4.3.0"
    R5 = "5.0.0"


class RiskLevel(Enum):
    """Risk level enumeration for vulnerability assessment."""
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class FHIRConfig:
    """Configuration for FHIR server integration."""
    server_base_url: str = "http://localhost:8080/fhir"
    fhir_version: FHIRVersion = FHIRVersion.R4
    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True
    auth_type: str = "none"  # none, basic, bearer, smart
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    token_url: Optional[str] = None
    authorization_url: Optional[str] = None
    scope: str = "system/*.read system/*.write"


@dataclass
class TerminologyMapping:
    """Clinical terminology mapping configuration."""
    system: str
    code: str
    display: str
    version: Optional[str] = None


class TerminologyMapper:
    """Maps ResilienceAI metrics to standard clinical terminologies."""
    
    # SNOMED CT Mappings
    SNOMED_SOCIOECONOMIC_STATUS = TerminologyMapping(
        system="http://snomed.info/sct",
        code="269489006",
        display="Socioeconomic status"
    )
    
    SNOMED_DISASTER_VULNERABILITY = TerminologyMapping(
        system="http://snomed.info/sct",
        code="102455003",
        display="Disaster vulnerability"
    )
    
    SNOMED_SOCIAL_ISOLATION = TerminologyMapping(
        system="http://snomed.info/sct",
        code="160732007",
        display="Social isolation"
    )
    
    SNOMED_TRANSPORTATION_INSECURITY = TerminologyMapping(
        system="http://snomed.info/sct",
        code="160685001",
        display="Transportation insecurity"
    )
    
    SNOMED_FOOD_INSECURITY = TerminologyMapping(
        system="http://snomed.info/sct",
        code="733423003",
        display="Food insecurity"
    )
    
    SNOMED_HOUSING_INSTABILITY = TerminologyMapping(
        system="http://snomed.info/sct",
        code="711062002",
        display="Housing instability"
    )
    
    # LOINC Mappings
    LOINC_POVERTY_RATE = TerminologyMapping(
        system="http://loinc.org",
        code="76515-3",
        display="Poverty rate"
    )
    
    LOINC_INSURANCE_STATUS = TerminologyMapping(
        system="http://loinc.org",
        code="52556-8",
        display="Insurance status"
    )
    
    LOINC_DISABILITY_STATUS = TerminologyMapping(
        system="http://loinc.org",
        code="75275-8",
        display="Disability status"
    )
    
    # ICD-10-CM Mappings
    ICD10_SOCIAL_DETERMINANTS = TerminologyMapping(
        system="http://hl7.org/fhir/sid/icd-10-cm",
        code="Z55-Z65",
        display="Persons with potential health hazards related to socioeconomic circumstances"
    )
    
    # SDOH Clinical Care IG Mappings
    SDOH_DOMAIN_HOUSING = TerminologyMapping(
        system="http://hl7.org/fhir/us/sdoh-clinicalcare/CodeSystem/SDOHCC-CodeSystemTemporaryCodes",
        code="housing-instability",
        display="Housing Instability"
    )
    
    SDOH_DOMAIN_FOOD = TerminologyMapping(
        system="http://hl7.org/fhir/us/sdoh-clinicalcare/CodeSystem/SDOHCC-CodeSystemTemporaryCodes",
        code="food-insecurity",
        display="Food Insecurity"
    )
    
    SDOH_DOMAIN_TRANSPORTATION = TerminologyMapping(
        system="http://hl7.org/fhir/us/sdoh-clinicalcare/CodeSystem/SDOHCC-CodeSystemTemporaryCodes",
        code="transportation-insecurity",
        display="Transportation Insecurity"
    )
    
    SDOH_DOMAIN_SOCIAL_ISOLATION = TerminologyMapping(
        system="http://hl7.org/fhir/us/sdoh-clinicalcare/CodeSystem/SDOHCC-CodeSystemTemporaryCodes",
        code="social-isolation",
        display="Social Isolation"
    )
    
    @classmethod
    def get_vulnerability_observation_mapping(cls, metric_name: str) -> TerminologyMapping:
        """Get terminology mapping for vulnerability metrics."""
        mappings = {
            "vulnerability_index": cls.SNOMED_DISASTER_VULNERABILITY,
            "isolation_index": cls.SNOMED_SOCIAL_ISOLATION,
            "poverty_pct": cls.LOINC_POVERTY_RATE,
            "uninsured_pct": cls.LOINC_INSURANCE_STATUS,
            "disability_pct": cls.LOINC_DISABILITY_STATUS,
            "housing_instability": cls.SDOH_DOMAIN_HOUSING,
            "food_insecurity": cls.SDOH_DOMAIN_FOOD,
            "transportation_insecurity": cls.SDOH_DOMAIN_TRANSPORTATION,
        }
        return mappings.get(metric_name, cls.SNOMED_SOCIOECONOMIC_STATUS)


class EnhancedFHIRExporter:
    """
    Enhanced FHIR R4 exporter with clinical integration capabilities.
    
    This class provides comprehensive FHIR resource generation for disaster
    vulnerability data, supporting US Core profiles, SDOH Clinical Care IG,
    and SMART on FHIR authentication.
    """
    
    FHIR_VERSION = "4.0.1"
    US_CORE_VERSION = "6.1.0"
    SDOHCC_VERSION = "2.2.0"
    
    # Profile URLs
    US_CORE_PATIENT_PROFILE = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
    US_CORE_LOCATION_PROFILE = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-location"
    US_CORE_OBSERVATION_PROFILE = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation"
    SDOHCC_CONDITION_PROFILE = "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Condition"
    SDOHCC_OBSERVATION_PROFILE = "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Observation"
    
    def __init__(self, df: Optional[pd.DataFrame] = None, config: Optional[FHIRConfig] = None):
        """
        Initialize the Enhanced FHIR Exporter.
        
        Args:
            df: Optional DataFrame with county vulnerability data
            config: Optional FHIR server configuration
        """
        self.config = config or FHIRConfig()
        self.terminology = TerminologyMapper()
        self.session = self._create_session()
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        
        if df is None:
            path = PROCESSED_DIR / "county_features.csv"
            if path.exists():
                self.df = pd.read_csv(path, dtype={"fips": str})
                logger.info(f"Loaded {len(self.df)} counties from {path}")
            else:
                self.df = None
                logger.warning("No county data loaded")
        else:
            self.df = df
            logger.info(f"Using provided DataFrame with {len(df)} counties")
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic."""
        session = requests.Session()
        adapter = HTTPAdapter(
            max_retries=self.config.max_retries,
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers.update({
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        })
        return session
    
    def _generate_id(self, prefix: str, identifier: str) -> str:
        """Generate a unique FHIR resource ID."""
        hash_input = f"{prefix}-{identifier}-{datetime.now().isoformat()}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        return f"{prefix}-{hash_value}"
    
    def _get_fhir_datetime(self) -> str:
        """Get current datetime in FHIR format."""
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    def _get_meta(self, profile_url: str) -> Dict[str, Any]:
        """Generate FHIR resource metadata."""
        return {
            "versionId": "1",
            "lastUpdated": self._get_fhir_datetime(),
            "profile": [profile_url]
        }
    
    def _create_bundle(
        self, 
        resources: List[Dict[str, Any]], 
        bundle_type: str = "collection",
        identifier_system: str = "https://resilienceai.io/fhir/bundle-id"
    ) -> Dict[str, Any]:
        """
        Create a FHIR Bundle resource.
        
        Args:
            resources: List of FHIR resources to include
            bundle_type: Bundle type (collection, document, message, etc.)
            identifier_system: Identifier system for the bundle
            
        Returns:
            FHIR Bundle resource
        """
        bundle_id = self._generate_id("bundle", datetime.now().isoformat())
        
        return {
            "resourceType": "Bundle",
            "id": bundle_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": self._get_fhir_datetime()
            },
            "identifier": {
                "system": identifier_system,
                "value": f"rai-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            },
            "type": bundle_type,
            "timestamp": self._get_fhir_datetime(),
            "entry": [
                {
                    "fullUrl": f"urn:uuid:{str(uuid.uuid4())}",
                    "resource": resource
                }
                for resource in resources
            ]
        }
    
    def _risk_level_to_coding(self, risk_level: str) -> Dict[str, str]:
        """
        Map risk level to FHIR coding.
        
        Uses standard risk assessment severity codes.
        """
        mapping = {
            "Critical": {
                "system": "http://hl7.org/fhir/risk-assessment-severity",
                "code": "extreme",
                "display": "Extreme Risk"
            },
            "High": {
                "system": "http://hl7.org/fhir/risk-assessment-severity",
                "code": "high",
                "display": "High Risk"
            },
            "Medium": {
                "system": "http://hl7.org/fhir/risk-assessment-severity",
                "code": "moderate",
                "display": "Moderate Risk"
            },
            "Low": {
                "system": "http://hl7.org/fhir/risk-assessment-severity",
                "code": "low",
                "display": "Low Risk"
            },
            "Minimal": {
                "system": "http://hl7.org/fhir/risk-assessment-severity",
                "code": "negligible",
                "display": "Negligible Risk"
            }
        }
        return mapping.get(risk_level, mapping["Low"])
    
    def create_organization(self, county_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create FHIR Organization resource for county health department.
        
        Args:
            county_data: Dictionary containing county information
            
        Returns:
            FHIR Organization resource
        """
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        state = county_name.split(", ")[-1] if ", " in county_name else ""
        
        org_id = self._generate_id("org", fips)
        
        return {
            "resourceType": "Organization",
            "id": org_id,
            "meta": self._get_meta("http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization"),
            "identifier": [
                {
                    "system": "https://www.census.gov/geographies/reference-files.html",
                    "value": fips,
                    "type": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "FIPS",
                            "display": "FIPS County Code"
                        }]
                    }
                }
            ],
            "active": True,
            "type": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                    "code": "govt",
                    "display": "Government"
                }],
                "text": "County Health Department"
            }],
            "name": f"{county_name} Health Department",
            "address": [{
                "country": "USA",
                "state": state
            }]
        }
    
    def create_location(self, county_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create enhanced FHIR Location resource for county.
        
        Args:
            county_data: Dictionary containing county information
            
        Returns:
            FHIR Location resource with US Core profile
        """
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        state = county_name.split(", ")[-1] if ", " in county_name else ""
        
        location_id = self._generate_id("location", fips)
        
        # Build position with elevation if available
        position = {
            "longitude": float(county_data.get("longitude", 0)),
            "latitude": float(county_data.get("latitude", 0))
        }
        
        if "elevation_m" in county_data and pd.notna(county_data["elevation_m"]):
            position["altitude"] = float(county_data["elevation_m"])
        
        return {
            "resourceType": "Location",
            "id": location_id,
            "meta": self._get_meta(self.US_CORE_LOCATION_PROFILE),
            "identifier": [
                {
                    "system": "https://www.census.gov/geographies/reference-files.html",
                    "value": fips,
                    "type": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "FIPS",
                            "display": "FIPS County Code"
                        }]
                    }
                },
                {
                    "system": "https://resilienceai.io/fhir/county-id",
                    "value": county_name
                }
            ],
            "status": "active",
            "name": county_name,
            "description": f"US County - {county_name}. Population: {county_data.get('population', 'Unknown')}",
            "mode": "instance",
            "type": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                    "code": "COMM",
                    "display": "Community"
                }, {
                    "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
                    "code": "jdn",
                    "display": "Jurisdiction"
                }],
                "text": "County Jurisdiction"
            }],
            "address": {
                "country": "USA",
                "state": state
            },
            "position": position,
            "physicalType": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
                    "code": "jdn",
                    "display": "Jurisdiction"
                }]
            }
        }

    
    def create_group(self, county_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create FHIR Group resource for county population.
        
        This enables population-level health management and cohort tracking.
        
        Args:
            county_data: Dictionary containing county information
            
        Returns:
            FHIR Group resource
        """
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        population = int(county_data.get("population", 0)) if pd.notna(county_data.get("population")) else 0
        
        group_id = self._generate_id("group", fips)
        
        # Build characteristics for the group
        characteristics = []
        
        # Add demographic characteristics
        if "elderly_pct" in county_data and pd.notna(county_data["elderly_pct"]):
            characteristics.append({
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "75275-8",
                        "display": "Age group"
                    }]
                },
                "valueBoolean": True,
                "exclude": False
            })
        
        if "poverty_pct" in county_data and pd.notna(county_data["poverty_pct"]):
            characteristics.append({
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "76515-3",
                        "display": "Poverty status"
                    }]
                },
                "valueBoolean": county_data["poverty_pct"] > 20.0,
                "exclude": False
            })
        
        return {
            "resourceType": "Group",
            "id": group_id,
            "meta": self._get_meta("http://hl7.org/fhir/StructureDefinition/Group"),
            "identifier": [{
                "system": "https://resilienceai.io/fhir/group-id",
                "value": f"county-population-{fips}"
            }],
            "active": True,
            "type": "person",
            "actual": True,
            "name": f"{county_name} Population",
            "quantity": population,
            "characteristic": characteristics
        }
    
    def create_risk_assessment(self, county_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create enhanced FHIR RiskAssessment resource.
        
        Args:
            county_data: Dictionary containing county vulnerability data
            
        Returns:
            FHIR RiskAssessment resource
        """
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        risk_score = float(county_data.get("risk_score", 0))
        risk_level = county_data.get("risk_level", "Low")
        
        risk_id = self._generate_id("risk", fips)
        
        # Build prediction basis with all contributing factors
        basis = []
        
        # Vulnerability component
        if "vulnerability_index" in county_data and pd.notna(county_data["vulnerability_index"]):
            vuln_idx = float(county_data["vulnerability_index"])
            basis.append({
                "reference": f"Observation/obs-vulnerability-{fips}",
                "display": f"Vulnerability Index: {vuln_idx:.3f}"
            })
        
        # Isolation component
        if "isolation_index" in county_data and pd.notna(county_data["isolation_index"]):
            iso_idx = float(county_data["isolation_index"])
            basis.append({
                "reference": f"Observation/obs-isolation-{fips}",
                "display": f"Infrastructure Isolation Index: {iso_idx:.3f}"
            })
        
        # Disaster history
        if "disaster_count" in county_data and pd.notna(county_data["disaster_count"]):
            disaster_count = int(county_data["disaster_count"])
            basis.append({
                "reference": f"Observation/obs-disaster-{fips}",
                "display": f"Historical Disasters: {disaster_count}"
            })
        
        # Healthcare access
        if "dist_nearest_hospitals_km" in county_data and pd.notna(county_data["dist_nearest_hospitals_km"]):
            dist = float(county_data["dist_nearest_hospitals_km"])
            basis.append({
                "reference": f"Observation/obs-hospital-dist-{fips}",
                "display": f"Distance to Nearest Hospital: {dist:.1f} km"
            })
        
        # Build predictions for different disaster types
        predictions = []
        
        # Overall disaster vulnerability
        predictions.append({
            "outcome": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": "102455003",
                    "display": "Disaster vulnerability"
                }],
                "text": "Overall Disaster Vulnerability Risk"
            },
            "probabilityDecimal": risk_score,
            "qualitativeRisk": self._risk_level_to_coding(risk_level),
            "rationale": f"Composite risk score {risk_score:.3f} based on demographic vulnerability, infrastructure access, and historical disaster frequency"
        })
        
        # Add specific disaster type predictions if available
        disaster_types = [
            ("flood_risk", "Flood", "19140008"),
            ("hurricane_risk", "Hurricane", "22490002"),
            ("wildfire_risk", "Wildfire", "40956001"),
            ("tornado_risk", "Tornado", "22490002"),
            ("earthquake_risk", "Earthquake", "40956001")
        ]
        
        for risk_col, disaster_name, snomed_code in disaster_types:
            if risk_col in county_data and pd.notna(county_data[risk_col]):
                disaster_risk = float(county_data[risk_col])
                predictions.append({
                    "outcome": {
                        "coding": [{
                            "system": "http://snomed.info/sct",
                            "code": snomed_code,
                            "display": f"{disaster_name} exposure"
                        }],
                        "text": f"{disaster_name} Risk"
                    },
                    "probabilityDecimal": disaster_risk,
                    "qualitativeRisk": self._risk_level_to_coding(
                        "High" if disaster_risk > 0.7 else "Medium" if disaster_risk > 0.4 else "Low"
                    )
                })
        
        return {
            "resourceType": "RiskAssessment",
            "id": risk_id,
            "meta": self._get_meta("http://hl7.org/fhir/StructureDefinition/RiskAssessment"),
            "identifier": [{
                "system": "https://resilienceai.io/fhir/risk-id",
                "value": f"rai-risk-{fips}"
            }],
            "status": "final",
            "subject": {
                "reference": f"Location/location-{fips}",
                "display": county_name
            },
            "occurrenceDateTime": self._get_fhir_datetime(),
            "method": {
                "coding": [{
                    "system": "https://resilienceai.io/fhir/risk-method",
                    "code": "composite-ml",
                    "display": "Composite ML Risk Score"
                }, {
                    "system": "http://snomed.info/sct",
                    "code": "409063005",
                    "display": "Risk assessment"
                }],
                "text": "Weighted composite of vulnerability (40%), isolation (30%), and disaster exposure (30%) using machine learning models"
            },
            "basis": basis,
            "prediction": predictions,
            "mitigation": county_data.get("top_intervention", "No specific intervention identified"),
            "note": [{
                "text": f"Risk assessment generated by ResilienceAI v2.0. Model version: {county_data.get('model_version', 'unknown')}"
            }]
        }
    
    def create_observation(
        self, 
        county_data: Dict[str, Any], 
        metric_name: str, 
        metric_display: str,
        value: Any,
        unit: Optional[str] = None,
        category: str = "survey",
        interpretation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create FHIR Observation resource for a vulnerability metric.
        
        Args:
            county_data: Dictionary containing county information
            metric_name: Internal metric identifier
            metric_display: Human-readable metric name
            value: Observation value
            unit: Unit of measurement
            category: Observation category
            interpretation: Clinical interpretation
            
        Returns:
            FHIR Observation resource
        """
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        
        obs_id = self._generate_id("obs", f"{metric_name}-{fips}")
        
        # Get terminology mapping
        term_mapping = self.terminology.get_vulnerability_observation_mapping(metric_name)
        
        # Build category
        category_coding = {
            "survey": {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "survey",
                "display": "Survey"
            },
            "social-history": {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "social-history",
                "display": "Social History"
            },
            "vital-signs": {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }
        }
        
        observation = {
            "resourceType": "Observation",
            "id": obs_id,
            "meta": self._get_meta(self.SDOHCC_OBSERVATION_PROFILE),
            "status": "final",
            "category": [{
                "coding": [category_coding.get(category, category_coding["survey"])]
            }],
            "code": {
                "coding": [{
                    "system": term_mapping.system,
                    "code": term_mapping.code,
                    "display": term_mapping.display
                }, {
                    "system": "https://resilienceai.io/fhir/observation-code",
                    "code": metric_name,
                    "display": metric_display
                }],
                "text": metric_display
            },
            "subject": {
                "reference": f"Location/location-{fips}",
                "display": county_name
            },
            "effectiveDateTime": self._get_fhir_datetime(),
            "performer": [{
                "reference": f"Organization/org-{fips}",
                "display": f"{county_name} Health Department"
            }]
        }
        
        # Add value
        if isinstance(value, (int, float)):
            observation["valueQuantity"] = {
                "value": float(value),
                "unit": unit if unit else "1",
                "system": "http://unitsofmeasure.org",
                "code": unit if unit else "1"
            }
        elif isinstance(value, bool):
            observation["valueBoolean"] = value
        elif isinstance(value, str):
            observation["valueString"] = value
        
        # Add interpretation if provided
        if interpretation:
            observation["interpretation"] = [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    "code": interpretation.lower(),
                    "display": interpretation
                }]
            }]
        
        # Add reference ranges for known metrics
        reference_ranges = {
            "poverty_pct": {"low": 0, "high": 20, "unit": "%"},
            "elderly_pct": {"low": 0, "high": 15, "unit": "%"},
            "uninsured_pct": {"low": 0, "high": 10, "unit": "%"},
            "vulnerability_index": {"low": 0, "high": 0.5, "unit": "1"}
        }
        
        if metric_name in reference_ranges:
            ref = reference_ranges[metric_name]
            observation["referenceRange"] = [{
                "low": {"value": ref["low"], "unit": ref["unit"]},
                "high": {"value": ref["high"], "unit": ref["unit"]}
            }]
        
        return observation
    
    def create_condition(self, county_data: Dict[str, Any], condition_type: str) -> Dict[str, Any]:
        """
        Create FHIR Condition resource for SDOH factors.
        
        Args:
            county_data: Dictionary containing county information
            condition_type: Type of SDOH condition
            
        Returns:
            FHIR Condition resource with SDOHCC profile
        """
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        
        condition_id = self._generate_id("cond", f"{condition_type}-{fips}")
        
        # Define condition mappings
        condition_mappings = {
            "housing_instability": {
                "code": "711062002",
                "display": "Housing instability",
                "sdoh_code": "housing-instability"
            },
            "food_insecurity": {
                "code": "733423003",
                "display": "Food insecurity",
                "sdoh_code": "food-insecurity"
            },
            "transportation_insecurity": {
                "code": "160685001",
                "display": "Transportation insecurity",
                "sdoh_code": "transportation-insecurity"
            },
            "social_isolation": {
                "code": "160732007",
                "display": "Social isolation",
                "sdoh_code": "social-isolation"
            },
            "utility_insecurity": {
                "code": "710853007",
                "display": "Inadequate utilities",
                "sdoh_code": "utility-insecurity"
            }
        }
        
        mapping = condition_mappings.get(condition_type, condition_mappings["social_isolation"])
        
        # Determine severity based on metric value
        severity = "moderate"
        if condition_type == "housing_instability" and "housing_stress_pct" in county_data:
            severity = "severe" if county_data["housing_stress_pct"] > 30 else "moderate" if county_data["housing_stress_pct"] > 15 else "mild"
        
        return {
            "resourceType": "Condition",
            "id": condition_id,
            "meta": self._get_meta(self.SDOHCC_CONDITION_PROFILE),
            "identifier": [{
                "system": "https://resilienceai.io/fhir/condition-id",
                "value": f"{condition_type}-{fips}"
            }],
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                    "display": "Active"
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "confirmed",
                    "display": "Confirmed"
                }]
            },
            "category": [{
                "coding": [{
                    "system": "http://hl7.org/fhir/us/sdoh-clinicalcare/CodeSystem/SDOHCC-CodeSystemTemporaryCodes",
                    "code": "sdoh-category-unspecified",
                    "display": "SDOH Category Unspecified"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": mapping["code"],
                    "display": mapping["display"]
                }, {
                    "system": "http://hl7.org/fhir/us/sdoh-clinicalcare/CodeSystem/SDOHCC-CodeSystemTemporaryCodes",
                    "code": mapping["sdoh_code"],
                    "display": mapping["display"]
                }],
                "text": mapping["display"]
            },
            "subject": {
                "reference": f"Group/group-{fips}",
                "display": f"{county_name} Population"
            },
            "onsetDateTime": self._get_fhir_datetime(),
            "severity": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": "24484000" if severity == "severe" else "6736007" if severity == "moderate" else "255604002",
                    "display": severity.capitalize()
                }]
            },
            "note": [{
                "text": f"Population-level {mapping['display']} identified through vulnerability assessment"
            }]
        }
    
    def create_care_plan(self, county_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create FHIR CarePlan resource for interventions.
        
        Args:
            county_data: Dictionary containing county information
            
        Returns:
            FHIR CarePlan resource
        """
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        top_intervention = county_data.get("top_intervention", "")
        
        careplan_id = self._generate_id("careplan", fips)
        
        # Build activities based on interventions
        activities = []
        
        interventions = [
            ("mobile_health_units", "Mobile Health Units", "385767005"),
            ("telehealth_expansion", "Telehealth Expansion", "448337001"),
            ("emergency_preparedness", "Emergency Preparedness", "225340009"),
            ("transportation_services", "Transportation Services", "409063005"),
            ("food_assistance", "Food Assistance Programs", "710854001"),
            ("housing_support", "Housing Support", "710853007")
        ]
        
        for int_col, int_name, snomed_code in interventions:
            if int_col in county_data and county_data.get(int_col, False):
                activities.append({
                    "reference": {
                        "reference": f"ServiceRequest/sr-{int_col}-{fips}",
                        "display": int_name
                    },
                    "detail": {
                        "kind": "ServiceRequest",
                        "code": {
                            "coding": [{
                                "system": "http://snomed.info/sct",
                                "code": snomed_code,
                                "display": int_name
                            }]
                        },
                        "status": "scheduled",
                        "doNotPerform": False
                    }
                })
        
        return {
            "resourceType": "CarePlan",
            "id": careplan_id,
            "meta": self._get_meta("http://hl7.org/fhir/us/core/StructureDefinition/us-core-careplan"),
            "identifier": [{
                "system": "https://resilienceai.io/fhir/careplan-id",
                "value": f"intervention-{fips}"
            }],
            "status": "active",
            "intent": "plan",
            "title": f"Disaster Vulnerability Intervention Plan - {county_name}",
            "description": f"Comprehensive intervention plan for {county_name} based on vulnerability assessment. Priority: {top_intervention}",
            "subject": {
                "reference": f"Group/group-{fips}",
                "display": f"{county_name} Population"
            },
            "period": {
                "start": self._get_fhir_datetime(),
                "end": (datetime.utcnow() + timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            },
            "created": self._get_fhir_datetime(),
            "author": {
                "reference": f"Organization/org-{fips}",
                "display": f"{county_name} Health Department"
            },
            "activity": activities
        }

    
    def create_consent(self, county_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create FHIR Consent resource for data sharing.
        
        Args:
            county_data: Dictionary containing county information
            
        Returns:
            FHIR Consent resource
        """
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        
        consent_id = self._generate_id("consent", fips)
        
        return {
            "resourceType": "Consent",
            "id": consent_id,
            "meta": self._get_meta("http://hl7.org/fhir/StructureDefinition/Consent"),
            "identifier": [{
                "system": "https://resilienceai.io/fhir/consent-id",
                "value": f"data-sharing-{fips}"
            }],
            "status": "active",
            "scope": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/consentscope",
                    "code": "patient-privacy",
                    "display": "Privacy Consent"
                }]
            },
            "category": [{
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "59284-0",
                    "display": "Consent Document"
                }]
            }],
            "patient": {
                "reference": f"Group/group-{fips}",
                "display": f"{county_name} Population"
            },
            "dateTime": self._get_fhir_datetime(),
            "performer": [{
                "reference": f"Organization/org-{fips}",
                "display": f"{county_name} Health Department"
            }],
            "sourceAttachment": {
                "contentType": "application/pdf",
                "title": f"Data Sharing Agreement - {county_name}",
                "creation": self._get_fhir_datetime()
            },
            "policy": [{
                "authority": "https://resilienceai.io/privacy-policy",
                "uri": "https://resilienceai.io/privacy-policy"
            }],
            "provision": {
                "type": "permit",
                "provision": [
                    {
                        "type": "permit",
                        "purpose": [{
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                            "code": "PUBHLTH",
                            "display": "Public Health"
                        }]
                    },
                    {
                        "type": "deny",
                        "purpose": [{
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                            "code": "MARKET",
                            "display": "Marketing"
                        }]
                    }
                ]
            }
        }
    
    def create_provenance(self, county_data: Dict[str, Any], resources: List[str]) -> Dict[str, Any]:
        """
        Create FHIR Provenance resource for data lineage.
        
        Args:
            county_data: Dictionary containing county information
            resources: List of resource references
            
        Returns:
            FHIR Provenance resource
        """
        fips = county_data.get("fips", "")
        
        provenance_id = self._generate_id("provenance", fips)
        
        return {
            "resourceType": "Provenance",
            "id": provenance_id,
            "meta": self._get_meta("http://hl7.org/fhir/StructureDefinition/Provenance"),
            "target": [{"reference": ref} for ref in resources],
            "occurredDateTime": self._get_fhir_datetime(),
            "recorded": self._get_fhir_datetime(),
            "policy": ["https://resilienceai.io/data-policy"],
            "location": {
                "reference": f"Location/location-{fips}",
                "display": county_data.get("county_name", "Unknown")
            },
            "reason": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                    "code": "PUBHLTH",
                    "display": "Public Health"
                }]
            }],
            "activity": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/provenance-activity-type",
                    "code": "transform",
                    "display": "Transform"
                }]
            },
            "agent": [
                {
                    "type": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                            "code": "author",
                            "display": "Author"
                        }]
                    },
                    "who": {
                        "reference": "Device/resilienceai-system",
                        "display": "ResilienceAI System"
                    }
                },
                {
                    "type": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                            "code": "source",
                            "display": "Source"
                        }]
                    },
                    "who": {
                        "display": "CDC, FEMA, Census Bureau, HRSA"
                    }
                }
            ],
            "entity": [
                {
                    "role": "source",
                    "what": {
                        "reference": f"DocumentReference/doc-raw-{fips}",
                        "display": "Raw vulnerability data"
                    }
                }
            ]
        }
    
    def create_document_reference(self, county_data: Dict[str, Any], report_path: str) -> Dict[str, Any]:
        """
        Create FHIR DocumentReference resource for reports.
        
        Args:
            county_data: Dictionary containing county information
            report_path: Path to the generated report
            
        Returns:
            FHIR DocumentReference resource
        """
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        
        doc_id = self._generate_id("doc", fips)
        
        return {
            "resourceType": "DocumentReference",
            "id": doc_id,
            "meta": self._get_meta("http://hl7.org/fhir/us/core/StructureDefinition/us-core-documentreference"),
            "identifier": [{
                "system": "https://resilienceai.io/fhir/document-id",
                "value": f"report-{fips}"
            }],
            "status": "current",
            "type": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "55107-7",
                    "display": "Disaster risk assessment"
                }]
            },
            "category": [{
                "coding": [{
                    "system": "http://hl7.org/fhir/us/core/CodeSystem/us-core-documentreference-category",
                    "code": "clinical-note",
                    "display": "Clinical Note"
                }]
            }],
            "subject": {
                "reference": f"Location/location-{fips}",
                "display": county_name
            },
            "date": self._get_fhir_datetime(),
            "author": [{
                "reference": f"Organization/org-{fips}",
                "display": f"{county_name} Health Department"
            }],
            "content": [{
                "attachment": {
                    "contentType": "application/pdf",
                    "url": f"file://{report_path}",
                    "title": f"Vulnerability Assessment Report - {county_name}",
                    "creation": self._get_fhir_datetime()
                },
                "format": {
                    "system": "http://ihe.net/fhir/ValueSet/IHE.FormatCode.codesystem",
                    "code": "urn:ihe:iti:xds-sd:pdf:2008",
                    "display": "PDF"
                }
            }],
            "context": {
                "related": [{
                    "reference": f"RiskAssessment/risk-{fips}",
                    "display": "Risk Assessment"
                }]
            }
        }


# ============================================================================
# SMART on FHIR Authentication
# ============================================================================

class SMARTonFHIRAuth:
    """
    SMART on FHIR authentication handler.
    
    Implements OAuth2 authorization code flow and client credentials flow
    for FHIR server authentication.
    """
    
    def __init__(self, config: FHIRConfig):
        """
        Initialize SMART on FHIR authentication.
        
        Args:
            config: FHIR configuration with authentication details
        """
        self.config = config
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.session = requests.Session()
    
    def discover_auth_endpoints(self, fhir_base_url: str) -> Dict[str, str]:
        """
        Discover SMART on FHIR authorization endpoints.
        
        Args:
            fhir_base_url: Base URL of the FHIR server
            
        Returns:
            Dictionary containing authorization and token endpoints
        """
        try:
            # Fetch FHIR server capability statement
            response = self.session.get(
                f"{fhir_base_url}/metadata",
                headers={"Accept": "application/fhir+json"},
                timeout=30
            )
            response.raise_for_status()
            
            capability = response.json()
            
            # Extract security extensions
            rest = capability.get("rest", [{}])[0]
            security = rest.get("security", {})
            extensions = security.get("extension", [])
            
            endpoints = {}
            for ext in extensions:
                if ext.get("url") == "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris":
                    for inner_ext in ext.get("extension", []):
                        if inner_ext.get("url") == "authorize":
                            endpoints["authorization_endpoint"] = inner_ext.get("valueUri")
                        elif inner_ext.get("url") == "token":
                            endpoints["token_endpoint"] = inner_ext.get("valueUri")
                        elif inner_ext.get("url") == "introspect":
                            endpoints["introspection_endpoint"] = inner_ext.get("valueUri")
                        elif inner_ext.get("url") == "revoke":
                            endpoints["revocation_endpoint"] = inner_ext.get("valueUri")
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Failed to discover auth endpoints: {e}")
            return {}
    
    def authenticate_client_credentials(self) -> bool:
        """
        Authenticate using OAuth2 client credentials flow.
        
        Returns:
            True if authentication successful
        """
        if not self.config.token_url or not self.config.client_id:
            logger.error("Missing authentication configuration")
            return False
        
        try:
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "scope": self.config.scope
            }
            
            if self.config.client_secret:
                payload["client_secret"] = self.config.client_secret
            
            response = self.session.post(
                self.config.token_url,
                data=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            
            logger.info("Successfully authenticated with client credentials flow")
            return True
            
        except Exception as e:
            logger.error(f"Client credentials authentication failed: {e}")
            return False
    
    def get_access_token(self) -> Optional[str]:
        """
        Get valid access token, refreshing if necessary.
        
        Returns:
            Valid access token or None
        """
        if not self.access_token:
            if not self.authenticate_client_credentials():
                return None
        
        # Check if token is expired or about to expire
        if self.token_expiry and datetime.utcnow() >= self.token_expiry - timedelta(minutes=5):
            logger.info("Access token expired or expiring soon, refreshing...")
            if not self.authenticate_client_credentials():
                return None
        
        return self.access_token
    
    def add_auth_header(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Add authorization header to request.
        
        Args:
            headers: Existing headers dictionary
            
        Returns:
            Headers with authorization added
        """
        token = self.get_access_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers


# ============================================================================
# FHIR Server Integration
# ============================================================================

class FHIRServerClient:
    """
    Client for interacting with FHIR servers.
    
    Supports CRUD operations, search, and bulk export.
    """
    
    def __init__(self, config: FHIRConfig):
        """
        Initialize FHIR server client.
        
        Args:
            config: FHIR server configuration
        """
        self.config = config
        self.auth = SMARTonFHIRAuth(config) if config.auth_type == "smart" else None
        self.session = self._create_session()
        self.base_url = config.server_base_url.rstrip('/')
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic."""
        session = requests.Session()
        adapter = HTTPAdapter(
            max_retries=self.config.max_retries,
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers.update({
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        })
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication if configured."""
        headers = dict(self.session.headers)
        if self.auth:
            headers = self.auth.add_auth_header(headers)
        return headers
    
    def create_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a FHIR resource on the server.
        
        Args:
            resource: FHIR resource to create
            
        Returns:
            Server response
        """
        resource_type = resource.get("resourceType")
        if not resource_type:
            raise ValueError("Resource must have a resourceType")
        
        url = f"{self.base_url}/{resource_type}"
        
        try:
            response = self.session.post(
                url,
                json=resource,
                headers=self._get_headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            logger.info(f"Created {resource_type} resource")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to create resource: {e.response.text}")
            raise
    
    def read_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """
        Read a FHIR resource from the server.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            
        Returns:
            FHIR resource
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to read resource: {e.response.text}")
            raise
    
    def update_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a FHIR resource on the server.
        
        Args:
            resource: FHIR resource to update
            
        Returns:
            Server response
        """
        resource_type = resource.get("resourceType")
        resource_id = resource.get("id")
        
        if not resource_type or not resource_id:
            raise ValueError("Resource must have resourceType and id")
        
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        
        try:
            response = self.session.put(
                url,
                json=resource,
                headers=self._get_headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            logger.info(f"Updated {resource_type}/{resource_id}")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to update resource: {e.response.text}")
            raise
    
    def search_resources(
        self, 
        resource_type: str, 
        params: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Search for FHIR resources.
        
        Args:
            resource_type: Type of resource to search
            params: Search parameters
            
        Returns:
            Search results bundle
        """
        url = f"{self.base_url}/{resource_type}"
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Search failed: {e.response.text}")
            raise
    
    def transaction(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a FHIR transaction bundle.
        
        Args:
            bundle: Transaction bundle
            
        Returns:
            Transaction response
        """
        url = f"{self.base_url}"
        
        try:
            response = self.session.post(
                url,
                json=bundle,
                headers=self._get_headers(),
                timeout=self.config.timeout * 3,  # Longer timeout for transactions
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            logger.info(f"Executed transaction with {len(bundle.get('entry', []))} entries")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Transaction failed: {e.response.text}")
            raise
    
    def initiate_bulk_export(
        self, 
        resource_types: Optional[List[str]] = None,
        since: Optional[str] = None,
        type_filter: Optional[str] = None
    ) -> str:
        """
        Initiate FHIR bulk data export.
        
        Args:
            resource_types: List of resource types to export
            since: Export resources modified since this date
            type_filter: Additional filters
            
        Returns:
            Export status URL
        """
        url = f"{self.base_url}/$export"
        
        params = {}
        if resource_types:
            params["_type"] = ",".join(resource_types)
        if since:
            params["_since"] = since
        if type_filter:
            params["_typeFilter"] = type_filter
        
        headers = self._get_headers()
        headers["Prefer"] = "respond-async"
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            # Get status URL from Content-Location header
            status_url = response.headers.get("Content-Location")
            if not status_url:
                raise ValueError("No Content-Location header in export response")
            
            logger.info(f"Bulk export initiated: {status_url}")
            return status_url
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Bulk export initiation failed: {e.response.text}")
            raise
    
    def check_bulk_export_status(self, status_url: str) -> Dict[str, Any]:
        """
        Check bulk export status.
        
        Args:
            status_url: Export status URL
            
        Returns:
            Status information
        """
        try:
            response = self.session.get(
                status_url,
                headers=self._get_headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Status check failed: {e.response.text}")
            raise



# ============================================================================
# FHIR Validation
# ============================================================================

class FHIRValidator:
    """
    FHIR resource validator using HAPI FHIR and custom validation rules.
    
    Validates resources against:
    - FHIR R4 structure definition
    - US Core profiles
    - SDOH Clinical Care profiles
    - Custom business rules
    """
    
    def __init__(self, validation_server_url: Optional[str] = None):
        """
        Initialize FHIR validator.
        
        Args:
            validation_server_url: URL of FHIR validation server
        """
        self.validation_server_url = validation_server_url
        self.session = requests.Session()
        
        # Load validation profiles
        self.profiles = self._load_profiles()
    
    def _load_profiles(self) -> Dict[str, Any]:
        """Load validation profiles."""
        profiles = {}
        
        # US Core profiles
        profiles["us-core-patient"] = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
        profiles["us-core-location"] = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-location"
        profiles["us-core-observation"] = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation"
        profiles["us-core-careplan"] = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-careplan"
        
        # SDOH Clinical Care profiles
        profiles["sdohcc-condition"] = "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Condition"
        profiles["sdohcc-observation"] = "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Observation"
        profiles["sdohcc-service-request"] = "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-ServiceRequest"
        
        return profiles
    
    def validate_resource(
        self, 
        resource: Dict[str, Any], 
        profile: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a FHIR resource.
        
        Args:
            resource: FHIR resource to validate
            profile: Profile URL to validate against
            
        Returns:
            Validation result with issues
        """
        if not self.validation_server_url:
            return self._validate_locally(resource, profile)
        
        return self._validate_remotely(resource, profile)
    
    def _validate_locally(
        self, 
        resource: Dict[str, Any], 
        profile: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform basic local validation."""
        issues = []
        
        # Check resource type
        resource_type = resource.get("resourceType")
        if not resource_type:
            issues.append({
                "severity": "error",
                "code": "structure",
                "details": {"text": "Resource must have a resourceType"}
            })
        
        # Check required fields based on resource type
        required_fields = {
            "Patient": ["identifier", "name"],
            "Observation": ["status", "code", "subject"],
            "Condition": ["clinicalStatus", "verificationStatus", "code", "subject"],
            "Location": ["name"],
            "RiskAssessment": ["status", "subject"],
            "CarePlan": ["status", "intent", "subject"],
            "Group": ["type", "actual"],
            "Consent": ["status", "scope"],
            "Provenance": ["target"],
            "DocumentReference": ["status", "type", "content"]
        }
        
        if resource_type in required_fields:
            for field in required_fields[resource_type]:
                if field not in resource:
                    issues.append({
                        "severity": "error",
                        "code": "required",
                        "details": {"text": f"Missing required field: {field}"},
                        "expression": [field]
                    })
        
        # Check identifier format
        if "identifier" in resource:
            for i, ident in enumerate(resource["identifier"]):
                if not ident.get("system"):
                    issues.append({
                        "severity": "warning",
                        "code": "business-rule",
                        "details": {"text": f"Identifier[{i}] missing system"},
                        "expression": [f"identifier[{i}]"]
                    })
        
        # Check coding systems
        self._validate_codings(resource, issues)
        
        return {
            "valid": len([i for i in issues if i["severity"] == "error"]) == 0,
            "issues": issues
        }
    
    def _validate_codings(self, resource: Dict[str, Any], issues: List[Dict[str, Any]], path: str = ""):
        """Recursively validate coding systems."""
        if isinstance(resource, dict):
            if "coding" in resource:
                for i, coding in enumerate(resource["coding"]):
                    if not coding.get("system"):
                        issues.append({
                            "severity": "warning",
                            "code": "code-invalid",
                            "details": {"text": f"Coding missing system at {path}.coding[{i}]"},
                            "expression": [f"{path}.coding[{i}]"]
                        })
            
            for key, value in resource.items():
                new_path = f"{path}.{key}" if path else key
                self._validate_codings(value, issues, new_path)
        
        elif isinstance(resource, list):
            for i, item in enumerate(resource):
                new_path = f"{path}[{i}]"
                self._validate_codings(item, issues, new_path)
    
    def _validate_remotely(
        self, 
        resource: Dict[str, Any], 
        profile: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate using remote FHIR server."""
        url = f"{self.validation_server_url}/$validate"
        
        params = {}
        if profile:
            params["profile"] = profile
        
        try:
            response = self.session.post(
                url,
                json=resource,
                params=params,
                headers={
                    "Accept": "application/fhir+json",
                    "Content-Type": "application/fhir+json"
                },
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Parse OperationOutcome
            issues = result.get("issue", [])
            errors = [i for i in issues if i["severity"] in ["error", "fatal"]]
            warnings = [i for i in issues if i["severity"] == "warning"]
            
            return {
                "valid": len(errors) == 0,
                "issues": issues,
                "error_count": len(errors),
                "warning_count": len(warnings)
            }
            
        except Exception as e:
            logger.error(f"Remote validation failed: {e}")
            return self._validate_locally(resource, profile)
    
    def validate_bundle(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all resources in a bundle.
        
        Args:
            bundle: FHIR Bundle resource
            
        Returns:
            Validation results for all entries
        """
        results = {
            "valid": True,
            "entry_results": [],
            "total_errors": 0,
            "total_warnings": 0
        }
        
        entries = bundle.get("entry", [])
        
        for entry in entries:
            resource = entry.get("resource", {})
            validation = self.validate_resource(resource)
            
            results["entry_results"].append({
                "resourceType": resource.get("resourceType"),
                "id": resource.get("id"),
                "valid": validation["valid"],
                "issues": validation.get("issues", [])
            })
            
            if not validation["valid"]:
                results["valid"] = False
            
            results["total_errors"] += len([i for i in validation.get("issues", []) if i["severity"] == "error"])
            results["total_warnings"] += len([i for i in validation.get("issues", []) if i["severity"] == "warning"])
        
        return results


# ============================================================================
# Bulk FHIR Export
# ============================================================================

class BulkFHIRExporter:
    """
    Bulk FHIR export handler for large-scale data sharing.
    
    Implements FHIR Bulk Data Access (Flat FHIR) specification.
    """
    
    def __init__(self, exporter: EnhancedFHIRExporter, client: FHIRServerClient):
        """
        Initialize bulk FHIR exporter.
        
        Args:
            exporter: Enhanced FHIR exporter instance
            client: FHIR server client
        """
        self.exporter = exporter
        self.client = client
    
    def export_county_ndjson(
        self, 
        fips: str, 
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Export county data as NDJSON (Newline Delimited JSON).
        
        Args:
            fips: County FIPS code
            output_dir: Output directory
            
        Returns:
            Export summary
        """
        if self.exporter.df is None:
            return {"error": "Data not loaded"}
        
        match = self.exporter.df[self.exporter.df["fips"] == str(fips)]
        if match.empty:
            return {"error": f"County {fips} not found"}
        
        row = match.iloc[0].to_dict()
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        resources_by_type = {}
        
        # Generate all resource types
        resources_by_type["Location"] = [self.exporter.create_location(row)]
        resources_by_type["Organization"] = [self.exporter.create_organization(row)]
        resources_by_type["Group"] = [self.exporter.create_group(row)]
        resources_by_type["RiskAssessment"] = [self.exporter.create_risk_assessment(row)]
        resources_by_type["CarePlan"] = [self.exporter.create_care_plan(row)]
        resources_by_type["Consent"] = [self.exporter.create_consent(row)]
        
        # Generate observations
        observations = self._create_county_observations(row)
        resources_by_type["Observation"] = observations
        
        # Generate conditions
        conditions = self._create_county_conditions(row)
        resources_by_type["Condition"] = conditions
        
        # Write NDJSON files
        files_created = []
        for resource_type, resources in resources_by_type.items():
            if resources:
                file_path = output_dir / f"{resource_type}.ndjson"
                with open(file_path, 'w') as f:
                    for resource in resources:
                        f.write(json.dumps(resource) + '\n')
                files_created.append(str(file_path))
        
        return {
            "status": "success",
            "fips": fips,
            "county_name": row.get("county_name"),
            "files_created": files_created,
            "resource_counts": {rt: len(rs) for rt, rs in resources_by_type.items()}
        }
    
    def _create_county_observations(self, row: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create all observations for a county."""
        observations = []
        
        obs_definitions = [
            ("vulnerability_index", "Vulnerability Index", "{:.3f}", None, "survey"),
            ("isolation_index", "Infrastructure Isolation Index", "{:.3f}", None, "survey"),
            ("poverty_pct", "Poverty Rate", "{:.1f}", "%", "social-history"),
            ("elderly_pct", "Elderly Population Percentage", "{:.1f}", "%", "survey"),
            ("disability_pct", "Disability Rate", "{:.1f}", "%", "survey"),
            ("uninsured_pct", "Uninsured Rate", "{:.1f}", "%", "social-history"),
            ("disaster_count", "Historical Disaster Count", "{:d}", None, "survey"),
            ("disaster_count_recent", "Recent Disaster Count (2015+)", "{:d}", None, "survey"),
            ("compound_risk_count", "Compound Risk Dimensions", "{:d}", None, "survey"),
            ("dist_nearest_hospitals_km", "Distance to Nearest Hospital", "{:.1f}", "km", "survey"),
            ("dist_2nd_nearest_hospitals_km", "Distance to 2nd Nearest Hospital", "{:.1f}", "km", "survey"),
            ("count_hospitals_50km", "Hospitals Within 50km", "{:d}", None, "survey"),
            ("dist_nearest_fire_stations_km", "Distance to Nearest Fire Station", "{:.1f}", "km", "survey"),
            ("dist_nearest_ems_stations_km", "Distance to Nearest EMS Station", "{:.1f}", "km", "survey"),
            ("population", "Population", "{:d}", None, "survey"),
            ("population_density", "Population Density", "{:.1f}", "per km2", "survey"),
            ("median_income", "Median Household Income", "{:.0f}", "USD", "survey"),
            ("housing_stress_pct", "Housing Cost Burden", "{:.1f}", "%", "social-history"),
        ]
        
        for col, display, fmt, unit, category in obs_definitions:
            if col in row and pd.notna(row[col]):
                value = row[col]
                
                # Determine interpretation
                interpretation = None
                if col == "poverty_pct":
                    interpretation = "high" if value > 20 else "normal" if value > 10 else "low"
                elif col == "uninsured_pct":
                    interpretation = "high" if value > 15 else "normal" if value > 8 else "low"
                
                obs = self.exporter.create_observation(
                    row, col, display, value, unit, category, interpretation
                )
                observations.append(obs)
        
        return observations
    
    def _create_county_conditions(self, row: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create SDOH conditions for a county."""
        conditions = []
        
        # Check thresholds for SDOH conditions
        sdoh_thresholds = {
            "housing_instability": ("housing_stress_pct", 30),
            "food_insecurity": ("poverty_pct", 25),
            "transportation_insecurity": ("dist_nearest_hospitals_km", 30),
            "social_isolation": ("isolation_index", 0.6),
            "utility_insecurity": ("poverty_pct", 20)
        }
        
        for condition_type, (metric, threshold) in sdoh_thresholds.items():
            if metric in row and pd.notna(row[metric]):
                if row[metric] > threshold:
                    condition = self.exporter.create_condition(row, condition_type)
                    conditions.append(condition)
        
        return conditions
    
    def export_state_ndjson(
        self, 
        state_abbrev: str, 
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Export all counties in a state as NDJSON.
        
        Args:
            state_abbrev: State abbreviation
            output_dir: Output directory
            
        Returns:
            Export summary
        """
        if self.exporter.df is None:
            return {"error": "Data not loaded"}
        
        # State mapping
        state_mapping = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
        }
        
        state_name = state_mapping.get(state_abbrev.upper(), state_abbrev)
        
        state_df = self.exporter.df[self.exporter.df["county_name"].str.contains(
            f", {state_name}$", regex=True, na=False
        )]
        
        if state_df.empty:
            return {"error": f"No counties found for state {state_abbrev}"}
        
        output_dir = Path(output_dir) / f"state_{state_abbrev.lower()}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Aggregate resources by type
        all_resources = {
            "Location": [],
            "Organization": [],
            "Group": [],
            "RiskAssessment": [],
            "Observation": [],
            "Condition": [],
            "CarePlan": [],
            "Consent": [],
            "Provenance": []
        }
        
        for _, row in state_df.iterrows():
            row_dict = row.to_dict()
            fips = row_dict.get("fips", "")
            
            all_resources["Location"].append(self.exporter.create_location(row_dict))
            all_resources["Organization"].append(self.exporter.create_organization(row_dict))
            all_resources["Group"].append(self.exporter.create_group(row_dict))
            all_resources["RiskAssessment"].append(self.exporter.create_risk_assessment(row_dict))
            all_resources["Observation"].extend(self._create_county_observations(row_dict))
            all_resources["Condition"].extend(self._create_county_conditions(row_dict))
            all_resources["CarePlan"].append(self.exporter.create_care_plan(row_dict))
            all_resources["Consent"].append(self.exporter.create_consent(row_dict))
            
            # Create provenance with references to all resources for this county
            resource_refs = [
                f"Location/location-{fips}",
                f"Organization/org-{fips}",
                f"Group/group-{fips}",
                f"RiskAssessment/risk-{fips}",
                f"CarePlan/careplan-{fips}",
                f"Consent/consent-{fips}"
            ]
            all_resources["Provenance"].append(
                self.exporter.create_provenance(row_dict, resource_refs)
            )
        
        # Write NDJSON files
        files_created = []
        for resource_type, resources in all_resources.items():
            if resources:
                file_path = output_dir / f"{resource_type}.ndjson"
                with open(file_path, 'w') as f:
                    for resource in resources:
                        f.write(json.dumps(resource) + '\n')
                files_created.append(str(file_path))
        
        return {
            "status": "success",
            "state": state_abbrev,
            "state_name": state_name,
            "counties": len(state_df),
            "output_directory": str(output_dir),
            "files_created": files_created,
            "resource_counts": {rt: len(rs) for rt, rs in all_resources.items()}
        }
    
    def create_export_manifest(
        self, 
        export_result: Dict[str, Any], 
        output_path: Path
    ) -> None:
        """
        Create FHIR Bulk Data Export manifest.
        
        Args:
            export_result: Export result dictionary
            output_path: Path for manifest file
        """
        manifest = {
            "transactionTime": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            "request": f"$export?state={export_result.get('state', 'unknown')}",
            "requiresAccessToken": False,
            "output": [],
            "error": []
        }
        
        # Add output files
        for resource_type, count in export_result.get("resource_counts", {}).items():
            if count > 0:
                manifest["output"].append({
                    "type": resource_type,
                    "url": f"./{resource_type}.ndjson",
                    "count": count
                })
        
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)


# ============================================================================
# Usage Examples
# ============================================================================

def example_basic_export():
    """Example: Basic county export to FHIR Bundle."""
    
    # Initialize exporter
    exporter = EnhancedFHIRExporter()
    
    # Export single county
    fips = "29189"  # St. Louis County, MO
    
    if exporter.df is not None:
        match = exporter.df[exporter.df["fips"] == fips]
        if not match.empty:
            row = match.iloc[0].to_dict()
            
            # Create resources
            resources = []
            resources.append(exporter.create_location(row))
            resources.append(exporter.create_organization(row))
            resources.append(exporter.create_group(row))
            resources.append(exporter.create_risk_assessment(row))
            
            # Create observations
            observations = [
                exporter.create_observation(row, "vulnerability_index", "Vulnerability Index", 
                                           row.get("vulnerability_index", 0), None, "survey"),
                exporter.create_observation(row, "poverty_pct", "Poverty Rate", 
                                           row.get("poverty_pct", 0), "%", "social-history"),
                exporter.create_observation(row, "uninsured_pct", "Uninsured Rate", 
                                           row.get("uninsured_pct", 0), "%", "social-history"),
            ]
            resources.extend(observations)
            
            # Create bundle
            bundle = exporter._create_bundle(resources, bundle_type="collection")
            
            # Save to file
            output_path = REPORTS_DIR / f"fhir-county-{fips}-enhanced.json"
            with open(output_path, 'w') as f:
                json.dump(bundle, f, indent=2)
            
            print(f"Exported to: {output_path}")
            print(f"Resources: {len(resources)}")
            
            return bundle
    
    return None


def example_server_integration():
    """Example: Upload resources to FHIR server."""
    
    # Configure FHIR server
    config = FHIRConfig(
        server_base_url="https://hapi.fhir.org/baseR4",
        auth_type="none",  # Use "smart" for SMART on FHIR
        timeout=60
    )
    
    # Initialize client
    client = FHIRServerClient(config)
    
    # Create sample location
    location = {
        "resourceType": "Location",
        "id": "test-location-001",
        "status": "active",
        "name": "Test County",
        "mode": "instance",
        "address": {
            "country": "USA",
            "state": "Missouri"
        }
    }
    
    try:
        # Create resource on server
        result = client.create_resource(location)
        print(f"Created resource: {result.get('id')}")
        
        # Read back
        read_result = client.read_resource("Location", result.get("id"))
        print(f"Read resource: {read_result.get('name')}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_bulk_export():
    """Example: Bulk export to NDJSON."""
    
    # Initialize exporter
    exporter = EnhancedFHIRExporter()
    
    # Configure client (for server upload if needed)
    config = FHIRConfig(server_base_url="http://localhost:8080/fhir")
    client = FHIRServerClient(config)
    
    # Initialize bulk exporter
    bulk_exporter = BulkFHIRExporter(exporter, client)
    
    # Export state
    result = bulk_exporter.export_state_ndjson("MO", REPORTS_DIR / "bulk_export")
    
    print(json.dumps(result, indent=2))
    
    # Create manifest
    if result.get("status") == "success":
        bulk_exporter.create_export_manifest(
            result, 
            Path(result["output_directory"]) / "manifest.json"
        )


def example_validation():
    """Example: Validate FHIR resources."""
    
    # Initialize validator
    validator = FHIRValidator()
    
    # Sample observation
    observation = {
        "resourceType": "Observation",
        "id": "test-obs-001",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "survey",
                "display": "Survey"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "76515-3",
                "display": "Poverty rate"
            }]
        },
        "subject": {
            "reference": "Location/location-29189"
        },
        "valueQuantity": {
            "value": 15.5,
            "unit": "%",
            "system": "http://unitsofmeasure.org",
            "code": "%"
        }
    }
    
    # Validate
    result = validator.validate_resource(observation)
    
    print(f"Valid: {result['valid']}")
    print(f"Issues: {len(result['issues'])}")
    for issue in result['issues']:
        print(f"  [{issue['severity']}] {issue['code']}: {issue['details']['text']}")


if __name__ == "__main__":
    # Run examples
    print("=" * 60)
    print("FHIR Export Examples")
    print("=" * 60)
    
    print("\n1. Basic Export:")
    example_basic_export()
    
    print("\n2. Validation:")
    example_validation()
    
    print("\n3. Bulk Export:")
    example_bulk_export()


---

## 3. Clinical Terminology Mapping

### 3.1 SNOMED CT Mappings

| ResilienceAI Metric | SNOMED CT Code | Display | Domain |
|---------------------|----------------|---------|--------|
| vulnerability_index | 102455003 | Disaster vulnerability | Situation |
| isolation_index | 160732007 | Social isolation | Finding |
| poverty_pct | 269489006 | Socioeconomic status | Observation |
| disability_pct | 21134002 | Disability | Finding |
| elderly_pct | 424144002 | Current chronological age | Observation |
| housing_stress | 711062002 | Housing instability | Finding |
| food_insecurity | 733423003 | Food insecurity | Finding |
| transportation_issues | 160685001 | Transportation insecurity | Finding |
| uninsured_pct | 737038009 | Uninsured | Finding |
| disaster_exposure | 102455003 | Disaster vulnerability | Situation |

### 3.2 LOINC Mappings

| ResilienceAI Metric | LOINC Code | Display | Category |
|---------------------|------------|---------|----------|
| poverty_pct | 76515-3 | Poverty rate | Social History |
| uninsured_pct | 52556-8 | Insurance status | Social History |
| disability_pct | 75275-8 | Disability status | Social History |
| median_income | 77293-5 | Household income | Social History |
| population | 75275-8 | Population count | Demographics |
| elderly_pct | 75275-8 | Age group | Demographics |
| hospital_distance | 38214-3 | Distance to facility | Survey |
| disaster_count | 55107-7 | Disaster risk assessment | Survey |

### 3.3 SDOH Clinical Care IG Mappings

| ResilienceAI Metric | SDOHCC Code | Display | Category |
|---------------------|-------------|---------|----------|
| housing_stress_pct | housing-instability | Housing Instability | SDOH |
| food_insecurity_risk | food-insecurity | Food Insecurity | SDOH |
| transportation_barriers | transportation-insecurity | Transportation Insecurity | SDOH |
| social_isolation_risk | social-isolation | Social Isolation | SDOH |
| utility_insecurity | utility-insecurity | Utility Insecurity | SDOH |
| employment_status | employment-status | Employment Status | SDOH |
| education_level | education-level | Education Level | SDOH |

### 3.4 ICD-10-CM Social Determinant Codes

| Condition | ICD-10-CM Code | Display |
|-----------|----------------|---------|
| Housing instability | Z59.0-Z59.1 | Homelessness, inadequate housing |
| Food insecurity | Z59.4 | Lack of adequate food |
| Transportation barriers | Z59.82 | Transportation insecurity |
| Social isolation | Z60.2 | Problems related to living alone |
| Utility insecurity | Z59.9 | Problem related to housing and economic circumstances |
| Low income | Z59.6 | Low income |
| Unemployment | Z56.0 | Unemployment |
| Educational barriers | Z55.0-Z55.9 | Problems related to education and literacy |

---

## 4. Compliance and Security

### 4.1 HIPAA Compliance Matrix

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Access Control | SMART on FHIR OAuth2 | ✅ |
| Audit Controls | Provenance resources + audit logging | ✅ |
| Integrity | Digital signatures on bundles | ✅ |
| Transmission Security | TLS 1.3 for all connections | ✅ |
| Minimum Necessary | Field-level filtering in exports | ✅ |
| De-identification | Safe Harbor method implementation | ✅ |
| Business Associate | BAA templates for integrations | ✅ |
| Breach Notification | Automated breach detection | ⚠️ |

### 4.2 Data Privacy Controls

```python
"""
HIPAA-compliant data handling for ResilienceAI FHIR exports.
"""

import hashlib
import hmac
from typing import Dict, Any, List, Optional


class PrivacyController:
    """Handle data privacy and de-identification."""
    
    # Safe Harbor identifiers to remove
    SAFE_HARBOR_IDENTIFIERS = [
        "name", "address", "dates", "telephone", "fax", "email",
        "ssn", "mrn", "health_plan", "account", "certificate",
        "vehicle", "device", "url", "ip", "biometric", "photo"
    ]
    
    def __init__(self, secret_key: str):
        """
        Initialize privacy controller.
        
        Args:
            secret_key: Secret key for pseudonymization
        """
        self.secret_key = secret_key.encode()
    
    def pseudonymize_id(self, identifier: str) -> str:
        """
        Create pseudonym for identifier.
        
        Args:
            identifier: Original identifier
            
        Returns:
            Pseudonymized identifier
        """
        return hmac.new(
            self.secret_key,
            identifier.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
    
    def deidentify_resource(
        self, 
        resource: Dict[str, Any], 
        method: str = "safe_harbor"
    ) -> Dict[str, Any]:
        """
        De-identify a FHIR resource.
        
        Args:
            resource: FHIR resource
            method: De-identification method
            
        Returns:
            De-identified resource
        """
        if method == "safe_harbor":
            return self._apply_safe_harbor(resource)
        elif method == "limited":
            return self._apply_limited_dataset(resource)
        else:
            return resource
    
    def _apply_safe_harbor(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Safe Harbor de-identification method."""
        deidentified = dict(resource)
        
        # Remove direct identifiers
        fields_to_remove = {
            "Patient": ["name", "telecom", "address", "photo", "contact"],
            "Location": ["name", "address"],  # Keep state only
            "Organization": ["name", "telecom", "address"],
            "Practitioner": ["name", "telecom", "photo", "address"]
        }
        
        resource_type = resource.get("resourceType")
        if resource_type in fields_to_remove:
            for field in fields_to_remove[resource_type]:
                if field in deidentified:
                    del deidentified[field]
        
        # Generalize dates to year only
        date_fields = ["birthDate", "deceasedDateTime", "effectiveDateTime"]
        for field in date_fields:
            if field in deidentified:
                try:
                    date_str = deidentified[field]
                    if len(date_str) >= 4:
                        deidentified[field] = date_str[:4]  # Year only
                except:
                    pass
        
        # Remove geographic data below state level
        if "address" in deidentified:
            address = deidentified["address"]
            if isinstance(address, dict):
                # Keep only state and country
                deidentified["address"] = {
                    k: v for k, v in address.items()
                    if k in ["state", "country"]
                }
        
        # Add de-identification tag
        if "meta" not in deidentified:
            deidentified["meta"] = {}
        if "security" not in deidentified["meta"]:
            deidentified["meta"]["security"] = []
        
        deidentified["meta"]["security"].append({
            "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
            "code": "N",
            "display": "Normal"
        })
        
        return deidentified
    
    def _apply_limited_dataset(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Apply limited dataset de-identification."""
        # Limited dataset allows more data but requires DUA
        deidentified = dict(resource)
        
        # Only remove direct identifiers
        direct_identifiers = ["name", "ssn", "mrn", "telecom"]
        
        for field in direct_identifiers:
            if field in deidentified:
                del deidentified[field]
        
        return deidentified
    
    def create_consent_resource(
        self, 
        patient_id: str, 
        purpose: List[str],
        policy_uri: str
    ) -> Dict[str, Any]:
        """
        Create Consent resource for data sharing.
        
        Args:
            patient_id: Patient identifier
            purpose: List of permitted purposes
            policy_uri: Privacy policy URI
            
        Returns:
            FHIR Consent resource
        """
        from datetime import datetime
        
        return {
            "resourceType": "Consent",
            "id": f"consent-{patient_id}",
            "status": "active",
            "scope": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/consentscope",
                    "code": "patient-privacy",
                    "display": "Privacy Consent"
                }]
            },
            "category": [{
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "59284-0",
                    "display": "Consent Document"
                }]
            }],
            "patient": {"reference": f"Patient/{patient_id}"},
            "dateTime": datetime.utcnow().isoformat() + "Z",
            "policy": [{"uri": policy_uri}],
            "provision": {
                "type": "permit",
                "provision": [
                    {
                        "type": "permit",
                        "purpose": [{
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                            "code": p
                        }]
                    }
                    for p in purpose
                ]
            }
        }


class AuditLogger:
    """Audit logging for FHIR operations."""
    
    def __init__(self, log_file: str = "fhir_audit.log"):
        """
        Initialize audit logger.
        
        Args:
            log_file: Path to audit log file
        """
        self.log_file = log_file
        import logging
        self.logger = logging.getLogger("fhir_audit")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_access(
        self, 
        user_id: str, 
        resource_type: str, 
        resource_id: str,
        action: str,
        outcome: str
    ):
        """
        Log resource access.
        
        Args:
            user_id: User identifier
            resource_type: Type of resource accessed
            resource_id: Resource identifier
            action: Action performed (read, create, update, delete)
            outcome: Outcome of action
        """
        self.logger.info(
            f"ACCESS: user={user_id}, resource={resource_type}/{resource_id}, "
            f"action={action}, outcome={outcome}"
        )
    
    def log_export(
        self, 
        user_id: str, 
        export_type: str,
        filters: Dict[str, Any],
        record_count: int
    ):
        """
        Log data export.
        
        Args:
            user_id: User identifier
            export_type: Type of export
            filters: Export filters applied
            record_count: Number of records exported
        """
        self.logger.info(
            f"EXPORT: user={user_id}, type={export_type}, "
            f"filters={filters}, records={record_count}"
        )
    
    def log_auth(
        self, 
        user_id: str, 
        action: str,
        success: bool
    ):
        """
        Log authentication event.
        
        Args:
            user_id: User identifier
            action: Authentication action
            success: Whether authentication succeeded
        """
        self.logger.info(
            f"AUTH: user={user_id}, action={action}, success={success}"
        )
```

### 4.3 Security Best Practices

1. **Authentication**
   - Use SMART on FHIR for EHR integration
   - Implement OAuth2 client credentials flow
   - Support PKCE for public clients
   - Rotate access tokens every 15 minutes

2. **Authorization**
   - Implement scope-based access control
   - Use FHIR compartments for patient-specific data
   - Enforce minimum necessary principle

3. **Data Protection**
   - Encrypt data at rest (AES-256)
   - Use TLS 1.3 for data in transit
   - Implement field-level encryption for sensitive data

4. **Audit Logging**
   - Log all FHIR operations
   - Include user, resource, action, and outcome
   - Retain logs for 6 years (HIPAA requirement)

---

## 5. FHIR Server Integration Points

### 5.1 Supported FHIR Servers

| Server | Version | SMART Support | Bulk Export | Notes |
|--------|---------|---------------|-------------|-------|
| HAPI FHIR | R4/R5 | ✅ | ✅ | Open source, highly configurable |
| Microsoft FHIR | R4 | ✅ | ✅ | Azure cloud-based |
| Google FHIR | R4 | ✅ | ⚠️ | GCP Healthcare API |
| Amazon FHIR | R4 | ✅ | ⚠️ | AWS HealthLake |
| IBM FHIR | R4 | ✅ | ✅ | Enterprise focus |
| Firely Server | R4/R5 | ✅ | ✅ | .NET based |

### 5.2 Integration Configuration

```python
"""
FHIR server integration configurations for ResilienceAI.
"""

# HAPI FHIR (local/self-hosted)
HAPI_LOCAL_CONFIG = FHIRConfig(
    server_base_url="http://localhost:8080/fhir",
    auth_type="none",
    timeout=30
)

# HAPI FHIR with authentication
HAPI_SECURE_CONFIG = FHIRConfig(
    server_base_url="https://hapi.fhir.org/baseR4",
    auth_type="bearer",
    timeout=60,
    verify_ssl=True
)

# Microsoft Azure FHIR
AZURE_FHIR_CONFIG = FHIRConfig(
    server_base_url="https://<workspace>.fhir.azurehealthcareapis.com",
    auth_type="smart",
    client_id="<client-id>",
    client_secret="<client-secret>",
    token_url="https://login.microsoftonline.com/<tenant>/oauth2/v2.0/token",
    scope="https://<workspace>.fhir.azurehealthcareapis.com/.default",
    timeout=60
)

# Google Cloud Healthcare FHIR
GCP_FHIR_CONFIG = FHIRConfig(
    server_base_url="https://healthcare.googleapis.com/v1/projects/<project>/locations/<location>/datasets/<dataset>/fhirStores/<store>/fhir",
    auth_type="bearer",
    timeout=60
)

# AWS HealthLake
AWS_FHIR_CONFIG = FHIRConfig(
    server_base_url="https://<datastore>.healthlake.<region>.amazonaws.com",
    auth_type="smart",
    client_id="<client-id>",
    client_secret="<client-secret>",
    token_url="https://<domain>.auth.<region>.amazoncognito.com/oauth2/token",
    timeout=60
)
```

---

## 6. Implementation Priority

### 6.1 Phase 1: Core FHIR Resources (Weeks 1-2)

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| P0 | Enhanced Location resource | 2 days | High |
| P0 | RiskAssessment improvements | 2 days | High |
| P0 | Observation standardization | 3 days | High |
| P1 | Group resource for populations | 2 days | Medium |
| P1 | Organization for health depts | 1 day | Medium |

### 6.2 Phase 2: Clinical Integration (Weeks 3-4)

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| P0 | SDOH Condition resources | 3 days | High |
| P0 | CarePlan for interventions | 2 days | High |
| P1 | DocumentReference for reports | 2 days | Medium |
| P1 | Provenance for data lineage | 2 days | Medium |
| P2 | Consent management | 2 days | Low |

### 6.3 Phase 3: Server Integration (Weeks 5-6)

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| P0 | FHIR server client | 3 days | High |
| P0 | SMART on FHIR auth | 3 days | High |
| P1 | Transaction support | 2 days | Medium |
| P1 | Search operations | 2 days | Medium |
| P2 | Server-side validation | 2 days | Low |

### 6.4 Phase 4: Bulk Export & Compliance (Weeks 7-8)

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| P0 | NDJSON export | 3 days | High |
| P0 | Bulk FHIR export | 3 days | High |
| P1 | FHIR validation | 2 days | Medium |
| P1 | HIPAA compliance controls | 3 days | High |
| P2 | Audit logging | 2 days | Medium |

### 6.5 Phase 5: Advanced Features (Weeks 9-10)

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| P1 | Clinical terminology mapping | 3 days | Medium |
| P1 | US Core profile compliance | 3 days | Medium |
| P2 | Custom profiles | 2 days | Low |
| P2 | Subscription support | 3 days | Low |
| P2 | Real-time notifications | 3 days | Low |

---

## 7. Testing Strategy

### 7.1 Unit Tests

```python
"""
Unit tests for FHIR export functionality.
"""

import unittest
import json
from pathlib import Path
from src.fhir.fhir_exporter_enhanced import EnhancedFHIRExporter, FHIRValidator


class TestFHIRExporter(unittest.TestCase):
    """Test FHIR exporter functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.exporter = EnhancedFHIRExporter()
        self.sample_county = {
            "fips": "29189",
            "county_name": "St. Louis County, Missouri",
            "latitude": 38.6103,
            "longitude": -90.4125,
            "population": 100123,
            "vulnerability_index": 0.65,
            "isolation_index": 0.45,
            "risk_score": 0.72,
            "risk_level": "High",
            "poverty_pct": 12.5,
            "elderly_pct": 15.2,
            "uninsured_pct": 8.3,
            "disaster_count": 15,
            "dist_nearest_hospitals_km": 5.2
        }
    
    def test_create_location(self):
        """Test Location resource creation."""
        location = self.exporter.create_location(self.sample_county)
        
        self.assertEqual(location["resourceType"], "Location")
        self.assertEqual(location["status"], "active")
        self.assertIn("position", location)
        self.assertEqual(location["position"]["latitude"], 38.6103)
    
    def test_create_risk_assessment(self):
        """Test RiskAssessment resource creation."""
        risk = self.exporter.create_risk_assessment(self.sample_county)
        
        self.assertEqual(risk["resourceType"], "RiskAssessment")
        self.assertEqual(risk["status"], "final")
        self.assertIn("prediction", risk)
        self.assertEqual(risk["prediction"][0]["probabilityDecimal"], 0.72)
    
    def test_create_observation(self):
        """Test Observation resource creation."""
        obs = self.exporter.create_observation(
            self.sample_county,
            "poverty_pct",
            "Poverty Rate",
            12.5,
            "%",
            "social-history"
        )
        
        self.assertEqual(obs["resourceType"], "Observation")
        self.assertEqual(obs["status"], "final")
        self.assertEqual(obs["valueQuantity"]["value"], 12.5)
        self.assertEqual(obs["valueQuantity"]["unit"], "%")


class TestFHIRValidator(unittest.TestCase):
    """Test FHIR validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = FHIRValidator()
    
    def test_validate_valid_observation(self):
        """Test validation of valid observation."""
        observation = {
            "resourceType": "Observation",
            "id": "test-obs",
            "status": "final",
            "code": {"text": "Test"},
            "subject": {"reference": "Patient/test"}
        }
        
        result = self.validator.validate_resource(observation)
        self.assertTrue(result["valid"])
    
    def test_validate_missing_required(self):
        """Test validation catches missing required fields."""
        observation = {
            "resourceType": "Observation",
            "id": "test-obs"
            # Missing status, code, subject
        }
        
        result = self.validator.validate_resource(observation)
        self.assertFalse(result["valid"])
        self.assertTrue(any(
            i["code"] == "required" for i in result["issues"]
        ))


if __name__ == "__main__":
    unittest.main()
```

### 7.2 Integration Tests

```python
"""
Integration tests for FHIR server connectivity.
"""

import unittest
import os
from src.fhir.fhir_exporter_enhanced import FHIRServerClient, FHIRConfig


@unittest.skipIf(
    not os.getenv("FHIR_TEST_SERVER"),
    "FHIR_TEST_SERVER not set"
)
class TestFHIRServerIntegration(unittest.TestCase):
    """Test FHIR server integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = FHIRConfig(
            server_base_url=os.getenv("FHIR_TEST_SERVER"),
            auth_type="none"
        )
        self.client = FHIRServerClient(self.config)
    
    def test_server_connectivity(self):
        """Test basic server connectivity."""
        # Search for any patients
        result = self.client.search_resources("Patient", {"_count": "1"})
        self.assertEqual(result["resourceType"], "Bundle")
    
    def test_create_and_read(self):
        """Test create and read operations."""
        # Create test location
        location = {
            "resourceType": "Location",
            "status": "active",
            "name": "Test Location",
            "mode": "instance"
        }
        
        created = self.client.create_resource(location)
        self.assertIn("id", created)
        
        # Read back
        read = self.client.read_resource("Location", created["id"])
        self.assertEqual(read["name"], "Test Location")


if __name__ == "__main__":
    unittest.main()
```

---

## 8. Deployment Considerations

### 8.1 Environment Configuration

```python
"""
Environment-specific FHIR configuration.
"""

import os
from src.fhir.fhir_exporter_enhanced import FHIRConfig


def get_fhir_config() -> FHIRConfig:
    """Get FHIR configuration based on environment."""
    
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return FHIRConfig(
            server_base_url=os.getenv("FHIR_SERVER_URL"),
            auth_type="smart",
            client_id=os.getenv("FHIR_CLIENT_ID"),
            client_secret=os.getenv("FHIR_CLIENT_SECRET"),
            token_url=os.getenv("FHIR_TOKEN_URL"),
            scope=os.getenv("FHIR_SCOPE", "system/*.read system/*.write"),
            timeout=60,
            verify_ssl=True
        )
    
    elif env == "staging":
        return FHIRConfig(
            server_base_url=os.getenv("FHIR_SERVER_URL", "https://hapi.fhir.org/baseR4"),
            auth_type="none",
            timeout=60,
            verify_ssl=True
        )
    
    else:  # development
        return FHIRConfig(
            server_base_url=os.getenv("FHIR_SERVER_URL", "http://localhost:8080/fhir"),
            auth_type="none",
            timeout=30,
            verify_ssl=False
        )
```

### 8.2 Docker Deployment

```dockerfile
# Dockerfile.fhir
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.fhir.txt .
RUN pip install --no-cache-dir -r requirements.fhir.txt

# Copy source
COPY src/ ./src/
COPY config.py .

# Environment
ENV PYTHONPATH=/app
ENV FHIR_VERSION=R4

# Run FHIR export service
CMD ["python", "-m", "src.fhir.fhir_service"]
```

```yaml
# docker-compose.fhir.yml
version: '3.8'

services:
  fhir-export:
    build:
      context: .
      dockerfile: Dockerfile.fhir
    environment:
      - ENVIRONMENT=production
      - FHIR_SERVER_URL=${FHIR_SERVER_URL}
      - FHIR_CLIENT_ID=${FHIR_CLIENT_ID}
      - FHIR_CLIENT_SECRET=${FHIR_CLIENT_SECRET}
    volumes:
      - ./data:/app/data
      - ./reports:/app/reports
    networks:
      - fhir-network

  hapi-fhir:
    image: hapiproject/hapi:v6.8.0
    ports:
      - "8080:8080"
    environment:
      - spring.datasource.url=jdbc:postgresql://postgres:5432/hapi
      - spring.datasource.username=admin
      - spring.datasource.password=admin
      - hapi.fhir.subscription.websocket_enabled=true
    depends_on:
      - postgres
    networks:
      - fhir-network

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=hapi
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=admin
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - fhir-network

volumes:
  postgres-data:

networks:
  fhir-network:
    driver: bridge
```

---

## 9. Summary

This comprehensive FHIR clinical data enhancement guide provides:

1. **Complete FHIR R4 Implementation**: Enhanced resources with US Core and SDOH Clinical Care profiles
2. **SMART on FHIR Authentication**: Secure OAuth2 integration for EHR connectivity
3. **Clinical Terminology**: Full SNOMED CT, LOINC, and SDOH code mappings
4. **Bulk FHIR Export**: NDJSON export for large-scale data sharing
5. **HIPAA Compliance**: Privacy controls, audit logging, and de-identification
6. **Server Integration**: Support for major FHIR servers (HAPI, Azure, GCP, AWS)
7. **Validation**: Resource validation against FHIR profiles
8. **Testing**: Comprehensive unit and integration tests

### Key Files Created

| File | Description | Path |
|------|-------------|------|
| fhir_exporter_enhanced.py | Enhanced FHIR exporter | `src/fhir/` |
| fhir_server_client.py | FHIR server integration | `src/fhir/` |
| fhir_validator.py | Resource validation | `src/fhir/` |
| bulk_exporter.py | Bulk FHIR export | `src/fhir/` |
| privacy_controller.py | HIPAA compliance | `src/fhir/` |
| test_fhir.py | Unit tests | `tests/fhir/` |

### Next Steps

1. Implement Phase 1 core resources (Weeks 1-2)
2. Set up HAPI FHIR test server
3. Create clinical terminology mappings
4. Implement SMART on FHIR authentication
5. Develop bulk export functionality
6. Add comprehensive test coverage
7. Deploy to staging environment
8. Conduct security audit
9. Production deployment
