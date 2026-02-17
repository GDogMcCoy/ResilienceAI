"""
FHIR Resource Validator
Validates FHIR resources against profiles and business rules.
"""

import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


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


if __name__ == "__main__":
    # Example usage
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
