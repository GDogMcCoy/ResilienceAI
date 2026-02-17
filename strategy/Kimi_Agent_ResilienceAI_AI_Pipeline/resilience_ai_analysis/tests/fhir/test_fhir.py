"""
Unit tests for FHIR export functionality.
"""

import unittest
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "fhir"))

from fhir_exporter_enhanced import EnhancedFHIRExporter, TerminologyMapper
from fhir_validator import FHIRValidator
from privacy_controller import PrivacyController, AuditLogger


class TestTerminologyMapper(unittest.TestCase):
    """Test terminology mapping functionality."""
    
    def test_get_vulnerability_mapping(self):
        """Test getting vulnerability observation mapping."""
        mapping = TerminologyMapper.get_vulnerability_observation_mapping("vulnerability_index")
        self.assertEqual(mapping.system, "http://snomed.info/sct")
        self.assertEqual(mapping.code, "102455003")
    
    def test_get_poverty_mapping(self):
        """Test getting poverty rate mapping."""
        mapping = TerminologyMapper.get_vulnerability_observation_mapping("poverty_pct")
        self.assertEqual(mapping.system, "http://loinc.org")
        self.assertEqual(mapping.code, "76515-3")
    
    def test_default_mapping(self):
        """Test default mapping for unknown metric."""
        mapping = TerminologyMapper.get_vulnerability_observation_mapping("unknown_metric")
        self.assertEqual(mapping.system, "http://snomed.info/sct")
        self.assertEqual(mapping.code, "269489006")


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
        self.assertEqual(location["position"]["longitude"], -90.4125)
        
        # Check identifier
        self.assertIn("identifier", location)
        fips_ident = [i for i in location["identifier"] if i.get("type", {}).get("coding", [{}])[0].get("code") == "FIPS"]
        self.assertEqual(len(fips_ident), 1)
        self.assertEqual(fips_ident[0]["value"], "29189")
    
    def test_create_organization(self):
        """Test Organization resource creation."""
        org = self.exporter.create_organization(self.sample_county)
        
        self.assertEqual(org["resourceType"], "Organization")
        self.assertEqual(org["active"], True)
        self.assertIn("St. Louis County", org["name"])
        self.assertEqual(org["address"][0]["state"], "Missouri")
    
    def test_create_group(self):
        """Test Group resource creation."""
        group = self.exporter.create_group(self.sample_county)
        
        self.assertEqual(group["resourceType"], "Group")
        self.assertEqual(group["type"], "person")
        self.assertEqual(group["actual"], True)
        self.assertEqual(group["quantity"], 100123)
    
    def test_create_risk_assessment(self):
        """Test RiskAssessment resource creation."""
        risk = self.exporter.create_risk_assessment(self.sample_county)
        
        self.assertEqual(risk["resourceType"], "RiskAssessment")
        self.assertEqual(risk["status"], "final")
        self.assertIn("prediction", risk)
        self.assertEqual(risk["prediction"][0]["probabilityDecimal"], 0.72)
        
        # Check basis
        self.assertIn("basis", risk)
        self.assertTrue(len(risk["basis"]) > 0)
    
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
        
        # Check coding
        self.assertIn("code", obs)
        self.assertIn("coding", obs["code"])
    
    def test_create_condition(self):
        """Test Condition resource creation."""
        condition = self.exporter.create_condition(self.sample_county, "housing_instability")
        
        self.assertEqual(condition["resourceType"], "Condition")
        self.assertEqual(condition["clinicalStatus"]["coding"][0]["code"], "active")
        
        # Check SDOH coding
        codings = condition["code"]["coding"]
        sdoh_coding = [c for c in codings if "sdoh-clinicalcare" in c.get("system", "")]
        self.assertEqual(len(sdoh_coding), 1)
    
    def test_create_care_plan(self):
        """Test CarePlan resource creation."""
        careplan = self.exporter.create_care_plan(self.sample_county)
        
        self.assertEqual(careplan["resourceType"], "CarePlan")
        self.assertEqual(careplan["status"], "active")
        self.assertEqual(careplan["intent"], "plan")
        self.assertIn("St. Louis County", careplan["title"])
    
    def test_create_bundle(self):
        """Test Bundle creation."""
        resources = [
            self.exporter.create_location(self.sample_county),
            self.exporter.create_risk_assessment(self.sample_county)
        ]
        
        bundle = self.exporter._create_bundle(resources, bundle_type="collection")
        
        self.assertEqual(bundle["resourceType"], "Bundle")
        self.assertEqual(bundle["type"], "collection")
        self.assertEqual(len(bundle["entry"]), 2)


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
        }
        
        result = self.validator.validate_resource(observation)
        self.assertFalse(result["valid"])
        self.assertTrue(any(
            i["code"] == "required" for i in result["issues"]
        ))
    
    def test_validate_missing_resource_type(self):
        """Test validation catches missing resource type."""
        resource = {
            "id": "test",
            "status": "active"
        }
        
        result = self.validator.validate_resource(resource)
        self.assertFalse(result["valid"])
        self.assertTrue(any(
            i["code"] == "structure" for i in result["issues"]
        ))
    
    def test_validate_bundle(self):
        """Test bundle validation."""
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Observation",
                        "status": "final",
                        "code": {"text": "Test"},
                        "subject": {"reference": "Patient/test"}
                    }
                }
            ]
        }
        
        result = self.validator.validate_bundle(bundle)
        self.assertTrue(result["valid"])
        self.assertEqual(result["total_errors"], 0)


class TestPrivacyController(unittest.TestCase):
    """Test privacy controller functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = PrivacyController(secret_key="test-secret-key")
    
    def test_pseudonymize_id(self):
        """Test ID pseudonymization."""
        identifier = "patient-123"
        pseudonym = self.controller.pseudonymize_id(identifier)
        
        # Should be deterministic
        pseudonym2 = self.controller.pseudonymize_id(identifier)
        self.assertEqual(pseudonym, pseudonym2)
        
        # Should be different for different IDs
        pseudonym3 = self.controller.pseudonymize_id("patient-456")
        self.assertNotEqual(pseudonym, pseudonym3)
        
        # Should be 16 characters
        self.assertEqual(len(pseudonym), 16)
    
    def test_deidentify_patient(self):
        """Test patient de-identification."""
        patient = {
            "resourceType": "Patient",
            "id": "patient-001",
            "name": [{"given": ["John"], "family": "Doe"}],
            "telecom": [{"system": "phone", "value": "555-1234"}],
            "address": [{"city": "St. Louis", "state": "MO", "country": "USA"}],
            "birthDate": "1980-05-15"
        }
        
        deidentified = self.controller.deidentify_resource(patient, method="safe_harbor")
        
        # Name should be removed
        self.assertNotIn("name", deidentified)
        
        # Telecom should be removed
        self.assertNotIn("telecom", deidentified)
        
        # Birth date should be year only
        self.assertEqual(deidentified["birthDate"], "1980")
    
    def test_create_consent_resource(self):
        """Test consent resource creation."""
        consent = self.controller.create_consent_resource(
            patient_id="patient-001",
            purpose=["PUBHLTH", "HCOMPL"],
            policy_uri="https://example.com/privacy-policy"
        )
        
        self.assertEqual(consent["resourceType"], "Consent")
        self.assertEqual(consent["status"], "active")
        self.assertEqual(consent["patient"]["reference"], "Patient/patient-001")
        
        # Check provisions
        self.assertEqual(len(consent["provision"]["provision"]), 2)


class TestAuditLogger(unittest.TestCase):
    """Test audit logger functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        import tempfile
        self.temp_log = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_log.close()
        self.audit = AuditLogger(log_file=self.temp_log.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import os
        os.unlink(self.temp_log.name)
    
    def test_log_access(self):
        """Test access logging."""
        self.audit.log_access("user-123", "Patient", "patient-001", "read", "success")
        
        # Read log file
        with open(self.temp_log.name, 'r') as f:
            log_content = f.read()
        
        self.assertIn("ACCESS", log_content)
        self.assertIn("user-123", log_content)
        self.assertIn("Patient/patient-001", log_content)
    
    def test_log_export(self):
        """Test export logging."""
        self.audit.log_export("user-123", "county", {"state": "MO"}, 115)
        
        # Read log file
        with open(self.temp_log.name, 'r') as f:
            log_content = f.read()
        
        self.assertIn("EXPORT", log_content)
        self.assertIn("county", log_content)
        self.assertIn("115", log_content)


if __name__ == "__main__":
    unittest.main()
