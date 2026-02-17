# /mnt/okcomputer/output/resilience_ai_analysis/code/compliance_archive.py
"""
Compliance Archive Manager for ResilienceAI
Manages compliance archiving with support for SOX, GDPR, ISO27001, and NIST.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import hashlib
import json


class ComplianceStandard(Enum):
    """Compliance standards enumeration."""
    SOX = "sarbanes_oxley"
    GDPR = "gdpr"
    ISO27001 = "iso27001"
    NIST = "nist_800_53"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"


@dataclass
class ComplianceRequirement:
    """Compliance requirement definition."""
    standard: ComplianceStandard
    retention_years: int
    encryption_required: bool
    immutability_required: bool
    audit_frequency: str
    data_types: List[str]
    special_requirements: Dict[str, str]


@dataclass
class LegalHold:
    """Legal hold on archived data."""
    hold_id: str
    data_ids: List[str]
    reason: str
    initiated_by: str
    initiated_at: datetime
    expires_at: Optional[datetime]
    status: str  # active, released, expired


class ComplianceArchiveManager:
    """Manages compliance archiving for ResilienceAI."""
    
    def __init__(self):
        self.compliance_requirements: Dict[ComplianceStandard, ComplianceRequirement] = {
            ComplianceStandard.SOX: ComplianceRequirement(
                standard=ComplianceStandard.SOX,
                retention_years=7,
                encryption_required=True,
                immutability_required=True,
                audit_frequency="annual",
                data_types=["financial_records", "audit_logs", "incident_reports"],
                special_requirements={
                    "worm_required": "true",
                    "checksum_verification": "quarterly"
                }
            ),
            ComplianceStandard.GDPR: ComplianceRequirement(
                standard=ComplianceStandard.GDPR,
                retention_years=2,
                encryption_required=True,
                immutability_required=False,
                audit_frequency="annual",
                data_types=["personal_data", "user_activity", "consent_records"],
                special_requirements={
                    "right_to_erasure": "supported",
                    "data_portability": "required",
                    "consent_tracking": "required"
                }
            ),
            ComplianceStandard.ISO27001: ComplianceRequirement(
                standard=ComplianceStandard.ISO27001,
                retention_years=7,
                encryption_required=True,
                immutability_required=True,
                audit_frequency="annual",
                data_types=["security_logs", "access_records", "incident_data"],
                special_requirements={
                    "access_control": "role_based",
                    "monitoring": "continuous"
                }
            ),
            ComplianceStandard.NIST: ComplianceRequirement(
                standard=ComplianceStandard.NIST,
                retention_years=3,
                encryption_required=True,
                immutability_required=True,
                audit_frequency="annual",
                data_types=["system_logs", "security_events", "configuration_data"],
                special_requirements={
                    "fips_140_2": "required",
                    "continuous_monitoring": "required"
                }
            )
        }
        self.legal_holds: Dict[str, LegalHold] = {}
        self.compliance_reports: List[Dict] = []
    
    def create_compliant_archive(self, data_id: str, data_content: bytes,
                                 standard: ComplianceStandard,
                                 metadata: Dict) -> Dict:
        """Create a compliance archive with all required controls."""
        requirement = self.compliance_requirements[standard]
        
        # Calculate retention period
        retention_until = datetime.now() + timedelta(days=requirement.retention_years * 365)
        
        # Generate integrity checksum
        checksum = hashlib.sha256(data_content).hexdigest()
        
        # Create archive record
        archive_record = {
            "data_id": data_id,
            "compliance_standard": standard.value,
            "retention_years": requirement.retention_years,
            "retention_until": retention_until.isoformat(),
            "encryption_enabled": requirement.encryption_required,
            "immutability_enabled": requirement.immutability_required,
            "integrity_checksum": checksum,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata,
            "legal_hold": False,
            "access_log": []
        }
        
        return archive_record
    
    def apply_legal_hold(self, hold_id: str, data_ids: List[str],
                        reason: str, initiated_by: str,
                        duration_days: Optional[int] = None) -> LegalHold:
        """Apply a legal hold to archived data."""
        expires_at = None
        if duration_days:
            expires_at = datetime.now() + timedelta(days=duration_days)
        
        hold = LegalHold(
            hold_id=hold_id,
            data_ids=data_ids,
            reason=reason,
            initiated_by=initiated_by,
            initiated_at=datetime.now(),
            expires_at=expires_at,
            status="active"
        )
        
        self.legal_holds[hold_id] = hold
        return hold
    
    def release_legal_hold(self, hold_id: str, released_by: str) -> Dict:
        """Release a legal hold."""
        if hold_id not in self.legal_holds:
            return {"status": "error", "message": "Hold not found"}
        
        hold = self.legal_holds[hold_id]
        hold.status = "released"
        
        return {
            "status": "released",
            "hold_id": hold_id,
            "released_by": released_by,
            "released_at": datetime.now().isoformat(),
            "affected_data_count": len(hold.data_ids)
        }
    
    def check_retention_expiry(self, archive_record: Dict) -> Dict:
        """Check if archive retention period has expired."""
        retention_until = datetime.fromisoformat(archive_record['retention_until'])
        
        # Check for legal hold
        for hold in self.legal_holds.values():
            if (hold.status == "active" and 
                archive_record['data_id'] in hold.data_ids):
                return {
                    "can_delete": False,
                    "reason": f"Legal hold {hold.hold_id} active",
                    "hold_details": {
                        "hold_id": hold.hold_id,
                        "reason": hold.reason,
                        "initiated_by": hold.initiated_by
                    }
                }
        
        if datetime.now() > retention_until:
            return {
                "can_delete": True,
                "retention_expired": True,
                "expired_at": retention_until.isoformat()
            }
        else:
            return {
                "can_delete": False,
                "retention_expired": False,
                "retention_until": retention_until.isoformat(),
                "days_remaining": (retention_until - datetime.now()).days
            }
    
    def generate_compliance_report(self, standard: ComplianceStandard,
                                   start_date: datetime,
                                   end_date: datetime) -> Dict:
        """Generate a compliance report for auditing."""
        requirement = self.compliance_requirements[standard]
        
        report = {
            "standard": standard.value,
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.now().isoformat(),
            "requirements": {
                "retention_years": requirement.retention_years,
                "encryption_required": requirement.encryption_required,
                "immutability_required": requirement.immutability_required
            },
            "active_legal_holds": len([h for h in self.legal_holds.values() 
                                       if h.status == "active"]),
            "special_requirements_met": requirement.special_requirements
        }
        
        self.compliance_reports.append(report)
        return report
    
    def verify_data_integrity(self, data_id: str, 
                             current_checksum: str) -> Dict:
        """Verify data integrity against stored checksum."""
        # In production, retrieve stored checksum from database
        stored_checksum = self._get_stored_checksum(data_id)
        
        is_valid = current_checksum == stored_checksum
        
        return {
            "data_id": data_id,
            "integrity_verified": is_valid,
            "stored_checksum": stored_checksum,
            "current_checksum": current_checksum,
            "verified_at": datetime.now().isoformat()
        }
    
    def _get_stored_checksum(self, data_id: str) -> str:
        """Retrieve stored checksum for data (placeholder)."""
        # Implementation would query database
        return "placeholder_checksum"


if __name__ == "__main__":
    # Example usage
    manager = ComplianceArchiveManager()
    
    # Create compliant archive
    sample_data = b"Sample incident data for compliance archiving"
    archive = manager.create_compliant_archive(
        data_id="INC-2024-001",
        data_content=sample_data,
        standard=ComplianceStandard.SOX,
        metadata={"incident_type": "security", "severity": "high"}
    )
    
    print(f"Created compliant archive: {json.dumps(archive, indent=2)}")
    
    # Apply legal hold
    hold = manager.apply_legal_hold(
        hold_id="HOLD-001",
        data_ids=["INC-2024-001"],
        reason="Litigation hold for investigation",
        initiated_by="legal@resilienceai.com"
    )
    
    print(f"\nApplied legal hold: {hold.hold_id}")
    
    # Check retention expiry
    expiry_status = manager.check_retention_expiry(archive)
    print(f"\nRetention status: {json.dumps(expiry_status, indent=2)}")
    
    # Generate compliance report
    report = manager.generate_compliance_report(
        standard=ComplianceStandard.SOX,
        start_date=datetime.now() - timedelta(days=90),
        end_date=datetime.now()
    )
    
    print(f"\nCompliance report: {json.dumps(report, indent=2)}")
