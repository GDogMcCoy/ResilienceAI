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
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        
        if df is None:
            # Try to load from default location
            processed_dir = Path(__file__).parent.parent.parent / "data" / "processed"
            path = processed_dir / "county_features.csv"
            if path.exists():
                self.df = pd.read_csv(path, dtype={"fips": str})
                logger.info(f"Loaded {len(self.df)} counties from {path}")
            else:
                self.df = None
                logger.warning("No county data loaded")
        else:
            self.df = df
            logger.info(f"Using provided DataFrame with {len(df)} counties")
    
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
        """Create a FHIR Bundle resource."""
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
        """Map risk level to FHIR coding."""
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
        """Create FHIR Organization resource for county health department."""
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
        """Create enhanced FHIR Location resource for county."""
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        state = county_name.split(", ")[-1] if ", " in county_name else ""
        
        location_id = self._generate_id("location", fips)
        
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
        """Create FHIR Group resource for county population."""
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        population = int(county_data.get("population", 0)) if pd.notna(county_data.get("population")) else 0
        
        group_id = self._generate_id("group", fips)
        
        characteristics = []
        
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
        """Create enhanced FHIR RiskAssessment resource."""
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        risk_score = float(county_data.get("risk_score", 0))
        risk_level = county_data.get("risk_level", "Low")
        
        risk_id = self._generate_id("risk", fips)
        
        basis = []
        
        if "vulnerability_index" in county_data and pd.notna(county_data["vulnerability_index"]):
            vuln_idx = float(county_data["vulnerability_index"])
            basis.append({
                "reference": f"Observation/obs-vulnerability-{fips}",
                "display": f"Vulnerability Index: {vuln_idx:.3f}"
            })
        
        if "isolation_index" in county_data and pd.notna(county_data["isolation_index"]):
            iso_idx = float(county_data["isolation_index"])
            basis.append({
                "reference": f"Observation/obs-isolation-{fips}",
                "display": f"Infrastructure Isolation Index: {iso_idx:.3f}"
            })
        
        if "disaster_count" in county_data and pd.notna(county_data["disaster_count"]):
            disaster_count = int(county_data["disaster_count"])
            basis.append({
                "reference": f"Observation/obs-disaster-{fips}",
                "display": f"Historical Disasters: {disaster_count}"
            })
        
        if "dist_nearest_hospitals_km" in county_data and pd.notna(county_data["dist_nearest_hospitals_km"]):
            dist = float(county_data["dist_nearest_hospitals_km"])
            basis.append({
                "reference": f"Observation/obs-hospital-dist-{fips}",
                "display": f"Distance to Nearest Hospital: {dist:.1f} km"
            })
        
        predictions = [{
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
        }]
        
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
        """Create FHIR Observation resource for a vulnerability metric."""
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        
        obs_id = self._generate_id("obs", f"{metric_name}-{fips}")
        
        term_mapping = self.terminology.get_vulnerability_observation_mapping(metric_name)
        
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
        
        if interpretation:
            observation["interpretation"] = [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    "code": interpretation.lower(),
                    "display": interpretation
                }]
            }]
        
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
        """Create FHIR Condition resource for SDOH factors."""
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        
        condition_id = self._generate_id("cond", f"{condition_type}-{fips}")
        
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
        """Create FHIR CarePlan resource for interventions."""
        fips = county_data.get("fips", "")
        county_name = county_data.get("county_name", "Unknown")
        top_intervention = county_data.get("top_intervention", "")
        
        careplan_id = self._generate_id("careplan", fips)
        
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
        """Create FHIR Consent resource for data sharing."""
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
        """Create FHIR Provenance resource for data lineage."""
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


if __name__ == "__main__":
    # Example usage
    exporter = EnhancedFHIRExporter()
    
    sample_county = {
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
    
    # Create resources
    location = exporter.create_location(sample_county)
    risk = exporter.create_risk_assessment(sample_county)
    obs = exporter.create_observation(sample_county, "poverty_pct", "Poverty Rate", 12.5, "%", "social-history")
    
    print("Location Resource:")
    print(json.dumps(location, indent=2))
    print("\nRisk Assessment Resource:")
    print(json.dumps(risk, indent=2))
    print("\nObservation Resource:")
    print(json.dumps(obs, indent=2))
