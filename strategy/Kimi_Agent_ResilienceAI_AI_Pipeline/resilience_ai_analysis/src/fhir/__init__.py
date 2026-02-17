"""
ResilienceAI FHIR Module

This module provides comprehensive FHIR R4 integration capabilities for
disaster vulnerability assessment data.

Modules:
    fhir_exporter_enhanced: Enhanced FHIR resource generation
    fhir_auth: SMART on FHIR authentication and server client
    fhir_validator: FHIR resource validation
    bulk_exporter: Bulk FHIR export in NDJSON format
    privacy_controller: HIPAA compliance and audit logging

Usage:
    from src.fhir import EnhancedFHIRExporter, FHIRServerClient
    
    exporter = EnhancedFHIRExporter()
    location = exporter.create_location(county_data)
"""

from .fhir_exporter_enhanced import (
    EnhancedFHIRExporter,
    TerminologyMapper,
    FHIRConfig,
    FHIRVersion,
    RiskLevel
)

from .fhir_auth import (
    SMARTonFHIRAuth,
    FHIRServerClient,
    FHIRConfig as AuthConfig
)

from .fhir_validator import FHIRValidator

from .bulk_exporter import BulkFHIRExporter

from .privacy_controller import (
    PrivacyController,
    AuditLogger
)

__all__ = [
    'EnhancedFHIRExporter',
    'TerminologyMapper',
    'FHIRConfig',
    'FHIRVersion',
    'RiskLevel',
    'SMARTonFHIRAuth',
    'FHIRServerClient',
    'FHIRValidator',
    'BulkFHIRExporter',
    'PrivacyController',
    'AuditLogger'
]

__version__ = "2.0.0"
