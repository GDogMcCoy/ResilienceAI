"""
HIPAA-compliant Data Handling for ResilienceAI FHIR Exports
Implements privacy controls, de-identification, and audit logging.
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


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
            "Location": ["name", "address"],
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
                        deidentified[field] = date_str[:4]
                except:
                    pass
        
        # Remove geographic data below state level
        if "address" in deidentified:
            address = deidentified["address"]
            if isinstance(address, dict):
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


if __name__ == "__main__":
    # Example usage
    controller = PrivacyController(secret_key="my-secret-key")
    
    # Sample resource
    resource = {
        "resourceType": "Patient",
        "id": "patient-001",
        "name": [{"given": ["John"], "family": "Doe"}],
        "telecom": [{"system": "phone", "value": "555-1234"}],
        "address": [{"city": "St. Louis", "state": "MO", "country": "USA"}],
        "birthDate": "1980-05-15"
    }
    
    # De-identify
    deidentified = controller.deidentify_resource(resource, method="safe_harbor")
    
    print("Original:")
    print(json.dumps(resource, indent=2))
    print("\nDe-identified:")
    print(json.dumps(deidentified, indent=2))
    
    # Test audit logging
    audit = AuditLogger()
    audit.log_access("user-123", "Patient", "patient-001", "read", "success")
    audit.log_export("user-123", "county", {"state": "MO"}, 115)
