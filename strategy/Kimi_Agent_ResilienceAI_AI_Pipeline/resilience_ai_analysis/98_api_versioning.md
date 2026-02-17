# ResilienceAI API Versioning Strategy

## Executive Summary

This document outlines a comprehensive API versioning strategy for ResilienceAI, designed to support continuous evolution while maintaining backward compatibility, clear communication with API consumers, and smooth migration paths.

---

## Table of Contents

1. [Versioning Strategy Overview](#1-versioning-strategy-overview)
2. [Versioning Approaches](#2-versioning-approaches)
3. [Backward Compatibility Framework](#3-backward-compatibility-framework)
4. [Deprecation Policy](#4-deprecation-policy)
5. [Migration Guides](#5-migration-guides)
6. [Version Negotiation](#6-version-negotiation)
7. [Documentation Strategy](#7-documentation-strategy)
8. [Testing Across Versions](#8-testing-across-versions)
9. [Sunset Policies](#9-sunset-policies)
10. [Client Communication](#10-client-communication)
11. [Version Analytics](#11-version-analytics)
12. [Implementation Roadmap](#12-implementation-roadmap)

---

## 1. Versioning Strategy Overview

### 1.1 Semantic Versioning for APIs

ResilienceAI adopts **Semantic Versioning 2.0.0** principles adapted for APIs:

```
MAJOR.MINOR.PATCH

Example: v2.3.1
```

| Component | API Changes | Example |
|-----------|-------------|---------|
| **MAJOR** | Breaking changes | Removing endpoints, changing response structure |
| **MINOR** | New features (backward compatible) | Adding new endpoints, optional parameters |
| **PATCH** | Bug fixes (backward compatible) | Fixing validation, performance improvements |

### 1.2 Versioning Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                    API VERSIONING PRINCIPLES                     │
├─────────────────────────────────────────────────────────────────┤
│ 1. NEVER break existing integrations without warning             │
│ 2. Provide clear migration paths for all breaking changes        │
│ 3. Support at least 2 major versions simultaneously              │
│ 4. Communicate deprecations 12 months in advance                 │
│ 5. Maintain comprehensive documentation for all versions         │
│ 6. Use analytics to understand version adoption                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Versioning Approaches

### 2.1 Recommended: URL Path Versioning (Primary)

**Implementation:**
```
https://api.resilienceai.com/v1/incidents
https://api.resilienceai.com/v2/incidents
```

**Advantages:**
- Clear and explicit
- Easy to test and debug
- Cache-friendly
- Self-documenting URLs
- Works with all HTTP clients

**Implementation:**

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/versions.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

class APIVersion(str, Enum):
    """Supported API versions."""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"  # Future version
    
    @classmethod
    def get_latest(cls) -> "APIVersion":
        return cls.V2
    
    @classmethod
    def get_supported(cls) -> list:
        return [cls.V1, cls.V2]

@dataclass
class VersionInfo:
    """Version metadata."""
    version: APIVersion
    release_date: datetime
    status: str  # "active", "deprecated", "sunset"
    sunset_date: Optional[datetime]
    documentation_url: str
    changelog_url: str

# Version registry
VERSION_REGISTRY: Dict[APIVersion, VersionInfo] = {
    APIVersion.V1: VersionInfo(
        version=APIVersion.V1,
        release_date=datetime(2023, 1, 15),
        status="deprecated",
        sunset_date=datetime(2025, 6, 30),
        documentation_url="/docs/api/v1",
        changelog_url="/docs/api/v1/changelog"
    ),
    APIVersion.V2: VersionInfo(
        version=APIVersion.V2,
        release_date=datetime(2024, 1, 10),
        status="active",
        sunset_date=None,
        documentation_url="/docs/api/v2",
        changelog_url="/docs/api/v2/changelog"
    )
}
```

### 2.2 Header-Based Versioning (Alternative)

**For advanced clients requiring version negotiation:**

```http
GET /incidents HTTP/1.1
Host: api.resilienceai.com
Accept: application/json
API-Version: 2024-01-10
```

**Implementation:**

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/header_versioning.py
from fastapi import Request, HTTPException, Header
from typing import Optional
from datetime import datetime
from .versions import APIVersion, VERSION_REGISTRY

class HeaderVersioning:
    """Header-based version negotiation."""
    
    VERSION_HEADER = "API-Version"
    DATE_FORMAT = "%Y-%m-%d"
    
    # Map dates to versions
    DATE_VERSION_MAP = {
        "2023-01-15": APIVersion.V1,
        "2024-01-10": APIVersion.V2,
    }
    
    @classmethod
    def get_version_from_header(
        cls,
        version_header: Optional[str] = Header(None, alias="API-Version")
    ) -> APIVersion:
        """Extract version from header."""
        if not version_header:
            return APIVersion.get_latest()
        
        # Try direct version match
        if version_header.lower() in [v.value for v in APIVersion]:
            return APIVersion(version_header.lower())
        
        # Try date-based version
        if version_header in cls.DATE_VERSION_MAP:
            return cls.DATE_VERSION_MAP[version_header]
        
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid API version",
                "message": f"Version '{version_header}' is not supported",
                "supported_versions": [v.value for v in APIVersion.get_supported()],
                "supported_dates": list(cls.DATE_VERSION_MAP.keys())
            }
        )
```

### 2.3 Content Negotiation (Advanced)

```http
GET /incidents HTTP/1.1
Host: api.resilienceai.com
Accept: application/vnd.resilienceai.v2+json
```

**Implementation:**

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/content_negotiation.py
import re
from fastapi import Request, HTTPException
from typing import Optional
from .versions import APIVersion

class ContentNegotiation:
    """Content negotiation for API versioning."""
    
    MEDIA_TYPE_PATTERN = re.compile(
        r"application/vnd\.resilienceai\.(v\d+)\+json"
    )
    
    @classmethod
    def get_version_from_accept(cls, request: Request) -> APIVersion:
        """Extract version from Accept header."""
        accept_header = request.headers.get("Accept", "")
        
        # Check for versioned media type
        match = cls.MEDIA_TYPE_PATTERN.search(accept_header)
        if match:
            version_str = match.group(1)
            try:
                return APIVersion(version_str)
            except ValueError:
                pass
        
        # Default to latest version
        return APIVersion.get_latest()
    
    @classmethod
    def get_content_type(cls, version: APIVersion) -> str:
        """Generate versioned content type."""
        return f"application/vnd.resilienceai.{version.value}+json"
```

---

## 3. Backward Compatibility Framework

### 3.1 Compatibility Rules

```
┌─────────────────────────────────────────────────────────────────┐
│              BACKWARD COMPATIBILITY RULES                        │
├─────────────────────────────────────────────────────────────────┤
│ ✓ ADD new endpoints                                              │
│ ✓ ADD optional request parameters                                │
│ ✓ ADD new fields to response (with null defaults)                │
│ ✓ ADD new enum values                                            │
│ ✓ ADD new webhook event types                                    │
│ ✓ DEPRECATE fields (keep in response, mark deprecated)           │
│ ✗ REMOVE or rename endpoints                                     │
│ ✗ REMOVE or rename request parameters                            │
│ ✗ REMOVE response fields                                         │
│ ✗ CHANGE field types                                             │
│ ✗ CHANGE authentication requirements                             │
│ ✗ CHANGE rate limiting behavior                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Compatibility Layer Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/compatibility.py
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class FieldCompatibility:
    """Defines field compatibility across versions."""
    name: str
    versions: List[str]
    deprecated_in: Optional[str] = None
    replacement: Optional[str] = None
    transform: Optional[Callable] = None

class CompatibilityLayer:
    """Handles backward compatibility transformations."""
    
    def __init__(self):
        self.field_mappings: Dict[str, Dict[str, str]] = {}
        self.transforms: Dict[str, Dict[str, Callable]] = {}
        self.deprecated_fields: Dict[str, List[str]] = {}
    
    def register_field_mapping(
        self,
        version: str,
        old_name: str,
        new_name: str,
        transform: Optional[Callable] = None
    ):
        """Register a field name mapping for a version."""
        if version not in self.field_mappings:
            self.field_mappings[version] = {}
            self.transforms[version] = {}
        
        self.field_mappings[version][old_name] = new_name
        if transform:
            self.transforms[version][old_name] = transform
    
    def register_deprecated_field(self, version: str, field_name: str):
        """Mark a field as deprecated in a version."""
        if version not in self.deprecated_fields:
            self.deprecated_fields[version] = []
        self.deprecated_fields[version].append(field_name)
    
    def transform_response(
        self,
        data: Dict[str, Any],
        target_version: str,
        source_version: str = "latest"
    ) -> Dict[str, Any]:
        """Transform response data to target version format."""
        result = data.copy()
        
        # Apply field mappings (reverse for downgrade)
        if target_version in self.field_mappings:
            for old_name, new_name in self.field_mappings[target_version].items():
                if new_name in result:
                    # Copy to old field name for backward compatibility
                    value = result[new_name]
                    if target_version in self.transforms and old_name in self.transforms[target_version]:
                        value = self.transforms[target_version][old_name](value)
                    result[old_name] = value
        
        # Add deprecation warnings
        if target_version in self.deprecated_fields:
            result["_meta"] = result.get("_meta", {})
            result["_meta"]["deprecated_fields"] = [
                f for f in self.deprecated_fields[target_version]
                if f in result
            ]
        
        return result

# Global compatibility layer instance
compatibility = CompatibilityLayer()

# Register V1 -> V2 mappings
compatibility.register_field_mapping("v1", "incident_id", "id")
compatibility.register_field_mapping("v1", "created_at", "created_timestamp")
compatibility.register_field_mapping("v1", "severity_level", "severity")
compatibility.register_deprecated_field("v1", "legacy_field")
```

### 3.3 Response Transformation Examples

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/transformers.py
from typing import Dict, Any
from datetime import datetime

def transform_severity_v1_to_v2(v1_severity: str) -> str:
    """Transform V1 severity levels to V2 format."""
    mapping = {
        "low": "P4",
        "medium": "P3",
        "high": "P2",
        "critical": "P1"
    }
    return mapping.get(v1_severity.lower(), "P3")

def transform_severity_v2_to_v1(v2_severity: str) -> str:
    """Transform V2 severity levels to V1 format."""
    mapping = {
        "P4": "low",
        "P3": "medium",
        "P2": "high",
        "P1": "critical"
    }
    return mapping.get(v2_severity, "medium")

def transform_timestamp_v1_to_v2(v1_timestamp: str) -> str:
    """Transform V1 timestamp to V2 ISO 8601 format."""
    # V1: "2024-01-15 10:30:00"
    # V2: "2024-01-15T10:30:00Z"
    try:
        dt = datetime.strptime(v1_timestamp, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return v1_timestamp

def transform_incident_v2_to_v1(v2_incident: Dict[str, Any]) -> Dict[str, Any]:
    """Transform V2 incident format to V1 for backward compatibility."""
    v1_incident = v2_incident.copy()
    
    # Map field names
    if "id" in v1_incident:
        v1_incident["incident_id"] = v1_incident.pop("id")
    
    if "created_timestamp" in v1_incident:
        v1_incident["created_at"] = v1_incident.pop("created_timestamp")
    
    if "severity" in v1_incident:
        v1_incident["severity_level"] = transform_severity_v2_to_v1(
            v1_incident.pop("severity")
        )
    
    # Add metadata
    v1_incident["_api_version"] = "v1"
    v1_incident["_deprecated_fields"] = ["legacy_field"]
    
    return v1_incident
```

---

## 4. Deprecation Policy

### 4.1 Deprecation Lifecycle

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   ACTIVE    │───▶│ DEPRECATED  │───▶│  SUNSET     │───▶│  RETIRED    │
│             │    │             │    │             │    │             │
│ Full support│    │ 12-month    │    │ 3-month     │    │ Removed     │
│             │    │ warning     │    │ grace period│    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                  │                  │                  │
      │            Add deprecation         Final              410 Gone
      │            headers & warnings      warnings
      │
   New version
   released
```

### 4.2 Deprecation Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/deprecation.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum
import warnings

class DeprecationStage(Enum):
    """Deprecation lifecycle stages."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"
    RETIRED = "retired"

@dataclass
class DeprecationNotice:
    """Deprecation notice configuration."""
    feature: str
    stage: DeprecationStage
    deprecated_date: datetime
    sunset_date: datetime
    replacement: Optional[str]
    migration_guide_url: str
    breaking_changes: list

class DeprecationManager:
    """Manages API deprecation lifecycle."""
    
    DEPRECATION_WARNING_MONTHS = 12
    SUNSET_GRACE_PERIOD_DAYS = 90
    
    def __init__(self):
        self.deprecations: Dict[str, DeprecationNotice] = {}
    
    def register_deprecation(
        self,
        feature: str,
        deprecated_date: datetime,
        replacement: Optional[str] = None,
        migration_guide_url: str = "",
        breaking_changes: list = None
    ) -> DeprecationNotice:
        """Register a new deprecation notice."""
        sunset_date = deprecated_date + timedelta(
            days=self.DEPRECATION_WARNING_MONTHS * 30
        )
        
        notice = DeprecationNotice(
            feature=feature,
            stage=DeprecationStage.DEPRECATED,
            deprecated_date=deprecated_date,
            sunset_date=sunset_date,
            replacement=replacement,
            migration_guide_url=migration_guide_url,
            breaking_changes=breaking_changes or []
        )
        
        self.deprecations[feature] = notice
        return notice
    
    def get_deprecation_headers(
        self,
        feature: str,
        request_version: str
    ) -> Dict[str, str]:
        """Generate deprecation headers for responses."""
        headers = {}
        
        if feature in self.deprecations:
            notice = self.deprecations[feature]
            
            # Standard deprecation headers (RFC 8594)
            headers["Deprecation"] = notice.deprecated_date.isoformat()
            headers["Sunset"] = notice.sunset_date.isoformat()
            
            # Custom ResilienceAI headers
            headers["X-API-Deprecation-Stage"] = notice.stage.value
            headers["X-API-Deprecation-Feature"] = notice.feature
            
            if notice.replacement:
                headers["X-API-Deprecation-Replacement"] = notice.replacement
            
            if notice.migration_guide_url:
                headers["Link"] = f'<{notice.migration_guide_url}>; rel="migration"'
        
        return headers
    
    def check_version_status(self, version: str) -> Dict[str, Any]:
        """Check the status of an API version."""
        now = datetime.utcnow()
        
        # Version-specific deprecations
        version_deprecations = [
            d for d in self.deprecations.values()
            if d.feature.startswith(f"v{version}")
        ]
        
        status = {
            "version": version,
            "status": "active",
            "warnings": [],
            "errors": []
        }
        
        for deprecation in version_deprecations:
            days_until_sunset = (deprecation.sunset_date - now).days
            
            if days_until_sunset <= 0:
                status["status"] = "retired"
                status["errors"].append({
                    "feature": deprecation.feature,
                    "message": f"This version has been retired. Please migrate to {deprecation.replacement}",
                    "migration_guide": deprecation.migration_guide_url
                })
            elif days_until_sunset <= self.SUNSET_GRACE_PERIOD_DAYS:
                status["status"] = "sunset"
                status["warnings"].append({
                    "feature": deprecation.feature,
                    "message": f"This version will be retired in {days_until_sunset} days",
                    "sunset_date": deprecation.sunset_date.isoformat()
                })
            else:
                status["warnings"].append({
                    "feature": deprecation.feature,
                    "message": f"This version is deprecated and will be retired on {deprecation.sunset_date.isoformat()}",
                    "replacement": deprecation.replacement
                })
        
        return status

# Global deprecation manager
deprecation_manager = DeprecationManager()

# Register V1 deprecation
deprecation_manager.register_deprecation(
    feature="v1-api",
    deprecated_date=datetime(2024, 1, 10),
    replacement="v2",
    migration_guide_url="https://docs.resilienceai.com/migration/v1-to-v2",
    breaking_changes=[
        "incident_id field renamed to id",
        "severity_level values changed from strings to P-levels",
        "created_at format changed to ISO 8601"
    ]
)
```

### 4.3 Deprecation Headers Example

```http
HTTP/1.1 200 OK
Content-Type: application/json
Deprecation: Sun, 01 Jan 2024 00:00:00 GMT
Sunset: Mon, 30 Jun 2025 00:00:00 GMT
X-API-Deprecation-Stage: deprecated
X-API-Deprecation-Feature: v1-api
X-API-Deprecation-Replacement: v2
Link: <https://docs.resilienceai.com/migration/v1-to-v2>; rel="migration"

{
  "data": {...},
  "meta": {
    "api_version": "v1",
    "deprecation_warning": "This API version is deprecated. Please migrate to v2.",
    "migration_guide": "https://docs.resilienceai.com/migration/v1-to-v2",
    "sunset_date": "2025-06-30T00:00:00Z"
  }
}
```

---

## 5. Migration Guides

### 5.1 Migration Guide Structure

```markdown
# Migration Guide: V1 to V2

## Overview
- **Source Version**: V1 (Deprecated)
- **Target Version**: V2 (Current)
- **Breaking Changes**: 3
- **Estimated Migration Time**: 2-4 hours
- **Sunset Date**: June 30, 2025

## Quick Start
```bash
# Update your base URL
curl https://api.resilienceai.com/v2/incidents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Breaking Changes

### 1. Field Renames
| V1 Field | V2 Field | Required Action |
|----------|----------|-----------------|
| incident_id | id | Update all references |
| created_at | created_timestamp | Update all references |
| severity_level | severity | Update all references |

### 2. Data Format Changes
| Field | V1 Format | V2 Format | Example |
|-------|-----------|-----------|---------|
| severity | "high" | "P2" | "P1", "P2", "P3", "P4" |
| created_at | "2024-01-15 10:30:00" | "2024-01-15T10:30:00Z" | ISO 8601 |

### 3. Endpoint Changes
| V1 Endpoint | V2 Endpoint | Change |
|-------------|-------------|--------|
| GET /v1/incidents/list | GET /v2/incidents | Simplified path |
| POST /v1/incidents/create | POST /v2/incidents | RESTful naming |

## Code Examples

### Before (V1)
```python
response = requests.get(
    "https://api.resilienceai.com/v1/incidents/list",
    headers={"Authorization": f"Bearer {token}"}
)
data = response.json()
incident_id = data["incident_id"]
severity = data["severity_level"]
```

### After (V2)
```python
response = requests.get(
    "https://api.resilienceai.com/v2/incidents",
    headers={"Authorization": f"Bearer {token}"}
)
data = response.json()
incident_id = data["id"]
severity = data["severity"]
```

## Validation Tools
- [Migration Validator](https://tools.resilienceai.com/migration-validator)
- [API Diff Tool](https://tools.resilienceai.com/api-diff)
- [Test Suite](https://github.com/resilienceai/migration-tests)

## Support
- Migration Support: migration@resilienceai.com
- Office Hours: Tuesdays 2-3 PM EST
- Slack Channel: #api-migration
```

### 5.2 Automated Migration Assistant

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/migration_assistant.py
from typing import Dict, Any, List
from dataclasses import dataclass
import json

@dataclass
class MigrationStep:
    """Single migration step."""
    description: str
    severity: str  # "info", "warning", "error"
    auto_fixable: bool
    fix_code: str = ""
    documentation_url: str = ""

class MigrationAssistant:
    """Assists with API version migrations."""
    
    def __init__(self, source_version: str, target_version: str):
        self.source_version = source_version
        self.target_version = target_version
        self.migration_rules = self._load_migration_rules()
    
    def _load_migration_rules(self) -> Dict[str, Any]:
        """Load migration rules for version pair."""
        rules = {
            ("v1", "v2"): {
                "field_mappings": {
                    "incident_id": "id",
                    "created_at": "created_timestamp",
                    "severity_level": "severity"
                },
                "value_transforms": {
                    "severity": {
                        "low": "P4",
                        "medium": "P3",
                        "high": "P2",
                        "critical": "P1"
                    }
                },
                "endpoint_changes": {
                    "/v1/incidents/list": "/v2/incidents",
                    "/v1/incidents/create": "/v2/incidents"
                }
            }
        }
        return rules.get((self.source_version, self.target_version), {})
    
    def analyze_code(self, code: str) -> List[MigrationStep]:
        """Analyze code for migration issues."""
        steps = []
        
        # Check for old field names
        for old_field, new_field in self.migration_rules.get("field_mappings", {}).items():
            if old_field in code:
                steps.append(MigrationStep(
                    description=f"Replace '{old_field}' with '{new_field}'",
                    severity="error",
                    auto_fixable=True,
                    fix_code=f"s/{old_field}/{new_field}/g",
                    documentation_url=f"/docs/migration/{self.source_version}-to-{self.target_version}#{new_field}"
                ))
        
        # Check for old endpoints
        for old_endpoint, new_endpoint in self.migration_rules.get("endpoint_changes", {}).items():
            if old_endpoint in code:
                steps.append(MigrationStep(
                    description=f"Update endpoint from '{old_endpoint}' to '{new_endpoint}'",
                    severity="error",
                    auto_fixable=True,
                    fix_code=f"s/{old_endpoint}/{new_endpoint}/g",
                    documentation_url=f"/docs/migration/{self.source_version}-to-{self.target_version}#endpoints"
                ))
        
        return steps
    
    def generate_migration_script(self, code: str) -> str:
        """Generate automated migration script."""
        steps = self.analyze_code(code)
        
        script = f"""#!/usr/bin/env python3
# Auto-generated migration script: {self.source_version} -> {self.target_version}
# Generated: {__import__('datetime').datetime.now().isoformat()}

import re

def migrate_code(source_code: str) -> str:
    code = source_code
"""
        
        for step in steps:
            if step.auto_fixable:
                script += f"""
    # {step.description}
    code = re.sub(r'{step.fix_code.split("/")[1]}', '{step.fix_code.split("/")[2]}', code)
"""
        
        script += """
    return code

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
        migrated = migrate_code(source)
        with open(sys.argv[1] + '.migrated', 'w') as f:
            f.write(migrated)
        print(f"Migrated {{sys.argv[1]}} -> {{sys.argv[1]}}.migrated")
"""
        
        return script
    
    def validate_migration(self, old_response: Dict, new_response: Dict) -> Dict[str, Any]:
        """Validate that migration produces equivalent results."""
        validation = {
            "passed": True,
            "warnings": [],
            "errors": []
        }
        
        # Check field presence
        field_mappings = self.migration_rules.get("field_mappings", {})
        for old_field, new_field in field_mappings.items():
            if old_field in old_response and new_field not in new_response:
                validation["passed"] = False
                validation["errors"].append(
                    f"Expected field '{new_field}' not found in V2 response"
                )
        
        return validation

# Usage example
assistant = MigrationAssistant("v1", "v2")
```

---

## 6. Version Negotiation

### 6.1 Negotiation Strategy

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/negotiation.py
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from fastapi import Request, HTTPException
from .versions import APIVersion, VERSION_REGISTRY

@dataclass
class VersionPreference:
    """Client version preference."""
    version: APIVersion
    priority: float  # q-value from Accept header

class VersionNegotiator:
    """Handles API version negotiation."""
    
    def __init__(self):
        self.supported_versions = APIVersion.get_supported()
    
    def negotiate_version(
        self,
        request: Request,
        url_version: Optional[str] = None
    ) -> APIVersion:
        """
        Negotiate API version using multiple strategies.
        Priority: URL > Header > Accept > Default
        """
        # 1. URL path version (highest priority)
        if url_version:
            return self._validate_version(url_version)
        
        # 2. Custom API-Version header
        header_version = request.headers.get("API-Version")
        if header_version:
            return self._validate_version(header_version)
        
        # 3. Accept header content negotiation
        accept_version = self._parse_accept_header(request)
        if accept_version:
            return accept_version
        
        # 4. Default to latest stable version
        return APIVersion.get_latest()
    
    def _validate_version(self, version_str: str) -> APIVersion:
        """Validate and return version."""
        version_str = version_str.lower().lstrip("v")
        
        try:
            version = APIVersion(f"v{version_str}")
            if version not in self.supported_versions:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Unsupported API version",
                        "requested_version": version_str,
                        "supported_versions": [v.value for v in self.supported_versions],
                        "latest_version": APIVersion.get_latest().value
                    }
                )
            return version
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid API version format",
                    "requested_version": version_str,
                    "expected_format": "v1, v2, etc."
                }
            )
    
    def _parse_accept_header(self, request: Request) -> Optional[APIVersion]:
        """Parse version from Accept header."""
        accept = request.headers.get("Accept", "")
        
        # Parse media types with q-values
        # Example: application/vnd.resilienceai.v2+json;q=0.9
        preferences: List[VersionPreference] = []
        
        for media_type in accept.split(","):
            media_type = media_type.strip()
            
            # Check for versioned media type
            if "vnd.resilienceai.v" in media_type:
                parts = media_type.split(";")
                main_type = parts[0].strip()
                
                # Extract version
                if "vnd.resilienceai.v" in main_type:
                    version_part = main_type.split("vnd.resilienceai.")[1]
                    version_str = version_part.split("+")[0]
                    
                    # Extract q-value
                    q_value = 1.0
                    for part in parts[1:]:
                        if "q=" in part:
                            try:
                                q_value = float(part.split("=")[1])
                            except ValueError:
                                pass
                    
                    try:
                        version = APIVersion(version_str)
                        if version in self.supported_versions:
                            preferences.append(VersionPreference(version, q_value))
                    except ValueError:
                        pass
        
        # Return highest priority version
        if preferences:
            preferences.sort(key=lambda x: x.priority, reverse=True)
            return preferences[0].version
        
        return None
    
    def get_version_info(self, version: APIVersion) -> Dict[str, Any]:
        """Get detailed version information."""
        info = VERSION_REGISTRY.get(version)
        if not info:
            return {"error": "Version not found"}
        
        return {
            "version": version.value,
            "release_date": info.release_date.isoformat(),
            "status": info.status,
            "sunset_date": info.sunset_date.isoformat() if info.sunset_date else None,
            "documentation_url": info.documentation_url,
            "changelog_url": info.changelog_url
        }

# Global negotiator instance
version_negotiator = VersionNegotiator()
```

### 6.2 FastAPI Integration

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/fastapi_integration.py
from fastapi import FastAPI, Request, Depends, APIRouter
from fastapi.responses import JSONResponse
from typing import Optional
from .negotiation import version_negotiator
from .deprecation import deprecation_manager
from .versions import APIVersion

app = FastAPI(title="ResilienceAI API")

def get_api_version(
    request: Request,
    version: Optional[str] = None  # From URL path
) -> APIVersion:
    """Dependency to extract and validate API version."""
    return version_negotiator.negotiate_version(request, version)

# Versioned router factory
def create_versioned_router(version: APIVersion) -> APIRouter:
    """Create a router for a specific API version."""
    router = APIRouter(prefix=f"/{version.value}")
    
    @router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def versioned_endpoint(
        request: Request,
        path: str,
        api_version: APIVersion = Depends(get_api_version)
    ):
        """Handle versioned requests."""
        # Add deprecation headers if applicable
        headers = deprecation_manager.get_deprecation_headers(
            f"{api_version.value}-api",
            api_version.value
        )
        
        # Route to appropriate handler
        response = await route_to_handler(request, path, api_version)
        
        # Add version headers
        headers["X-API-Version"] = api_version.value
        headers["X-API-Latest-Version"] = APIVersion.get_latest().value
        
        return JSONResponse(
            content=response,
            headers=headers
        )
    
    return router

# Register versioned routers
for v in APIVersion.get_supported():
    app.include_router(create_versioned_router(v))

@app.get("/versions")
async def list_versions():
    """List all available API versions."""
    return {
        "versions": [
            version_negotiator.get_version_info(v)
            for v in APIVersion.get_supported()
        ],
        "latest": APIVersion.get_latest().value,
        "documentation": "/docs"
    }

async def route_to_handler(request: Request, path: str, version: APIVersion):
    """Route request to appropriate version handler."""
    # Implementation would dispatch to version-specific handlers
    return {"message": f"Handled by {version.value}", "path": path}
```

---

## 7. Documentation Strategy

### 7.1 Multi-Version Documentation Structure

```
/docs/
├── index.html                    # Version selector landing page
├── versions.json                 # Machine-readable version list
├── v1/
│   ├── index.html               # V1 documentation
│   ├── openapi.json             # V1 OpenAPI spec
│   ├── changelog.md             # V1 changelog
│   └── migration/
│       └── v1-to-v2.md          # V1 to V2 migration guide
├── v2/
│   ├── index.html               # V2 documentation
│   ├── openapi.json             # V2 OpenAPI spec
│   ├── changelog.md             # V2 changelog
│   └── migration/
│       └── v2-to-v3.md          # V2 to V3 migration guide (future)
└── shared/
    ├── authentication.md
    ├── rate-limiting.md
    ├── error-handling.md
    └── webhooks.md
```

### 7.2 OpenAPI Multi-Version Support

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/openapi_config.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import json
from typing import Dict, Any
from .versions import APIVersion, VERSION_REGISTRY

def generate_openapi_spec(version: APIVersion) -> Dict[str, Any]:
    """Generate OpenAPI specification for a specific version."""
    
    base_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "ResilienceAI API",
            "description": f"ResilienceAI API - Version {version.value}",
            "version": version.value,
            "contact": {
                "name": "ResilienceAI Support",
                "email": "api@resilienceai.com",
                "url": "https://support.resilienceai.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            },
            "x-api-status": VERSION_REGISTRY[version].status,
            "x-sunset-date": VERSION_REGISTRY[version].sunset_date.isoformat() if VERSION_REGISTRY[version].sunset_date else None
        },
        "servers": [
            {
                "url": f"https://api.resilienceai.com/{version.value}",
                "description": "Production server"
            },
            {
                "url": f"https://staging-api.resilienceai.com/{version.value}",
                "description": "Staging server"
            }
        ],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                },
                "apiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            }
        }
    }
    
    # Add version-specific paths and schemas
    if version == APIVersion.V1:
        base_spec["paths"] = generate_v1_paths()
        base_spec["components"]["schemas"] = generate_v1_schemas()
    elif version == APIVersion.V2:
        base_spec["paths"] = generate_v2_paths()
        base_spec["components"]["schemas"] = generate_v2_schemas()
    
    return base_spec

def generate_v1_paths() -> Dict[str, Any]:
    """Generate V1 API paths."""
    return {
        "/incidents": {
            "get": {
                "summary": "List incidents",
                "deprecated": True,
                "description": "This endpoint is deprecated. Use /v2/incidents instead.",
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "List of incidents",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/IncidentListV1"}
                            }
                        }
                    },
                    "301": {
                        "description": "Redirect to V2",
                        "headers": {
                            "Location": {
                                "schema": {"type": "string"},
                                "description": "New V2 endpoint URL"
                            }
                        }
                    }
                }
            }
        }
    }

def generate_v2_paths() -> Dict[str, Any]:
    """Generate V2 API paths."""
    return {
        "/incidents": {
            "get": {
                "summary": "List incidents",
                "description": "Retrieve a paginated list of incidents",
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "schema": {"type": "string", "enum": ["open", "in_progress", "resolved", "closed"]}
                    },
                    {
                        "name": "severity",
                        "in": "query",
                        "schema": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]}
                    },
                    {
                        "name": "cursor",
                        "in": "query",
                        "description": "Pagination cursor",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "List of incidents",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/IncidentListV2"}
                            }
                        }
                    }
                }
            },
            "post": {
                "summary": "Create incident",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/IncidentCreateV2"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Incident created",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/IncidentV2"}
                            }
                        }
                    }
                }
            }
        }
    }

def generate_v1_schemas() -> Dict[str, Any]:
    """Generate V1 schemas."""
    return {
        "IncidentV1": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "severity_level": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                "created_at": {"type": "string", "format": "date-time"},
                "status": {"type": "string"}
            },
            "deprecated": True
        },
        "IncidentListV1": {
            "type": "object",
            "properties": {
                "incidents": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/IncidentV1"}
                },
                "total": {"type": "integer"}
            }
        }
    }

def generate_v2_schemas() -> Dict[str, Any]:
    """Generate V2 schemas."""
    return {
        "IncidentV2": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Unique incident identifier"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "severity": {"type": "string", "enum": ["P1", "P2", "P3", "P4"], "description": "P1=critical, P4=low"},
                "created_timestamp": {"type": "string", "format": "date-time"},
                "updated_timestamp": {"type": "string", "format": "date-time"},
                "status": {"type": "string", "enum": ["open", "in_progress", "resolved", "closed"]},
                "assignee": {"type": "string", "nullable": True},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["id", "title", "severity", "status"]
        },
        "IncidentCreateV2": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "minLength": 1, "maxLength": 200},
                "description": {"type": "string", "maxLength": 5000},
                "severity": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
                "assignee": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["title", "severity"]
        },
        "IncidentListV2": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/IncidentV2"}
                },
                "pagination": {
                    "type": "object",
                    "properties": {
                        "next_cursor": {"type": "string", "nullable": True},
                        "has_more": {"type": "boolean"}
                    }
                }
            }
        }
    }

# Export specs for all versions
def export_openapi_specs(output_dir: str = "./docs"):
    """Export OpenAPI specifications for all versions."""
    for version in APIVersion.get_supported():
        spec = generate_openapi_spec(version)
        filepath = f"{output_dir}/{version.value}/openapi.json"
        with open(filepath, "w") as f:
            json.dump(spec, f, indent=2)
        print(f"Exported OpenAPI spec for {version.value} to {filepath}")
```

---

## 8. Testing Across Versions

### 8.1 Version Compatibility Testing Framework

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/version_testing.py
import pytest
import requests
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
from .versions import APIVersion

@dataclass
class VersionTestCase:
    """Test case for version compatibility."""
    name: str
    endpoint: str
    method: str
    versions: List[APIVersion]
    request_data: Dict[str, Any] = None
    expected_status: int = 200
    response_validators: List[Callable] = None

class VersionCompatibilityTester:
    """Test API compatibility across versions."""
    
    BASE_URL = "https://api.resilienceai.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}
        })
    
    def test_endpoint_across_versions(self, test_case: VersionTestCase):
        """Test an endpoint across multiple versions."""
        results = []
        
        for version in test_case.versions:
            url = f"{self.BASE_URL}/{version.value}{test_case.endpoint}"
            
            response = self.session.request(
                method=test_case.method,
                url=url,
                json=test_case.request_data
            )
            
            result = {
                "version": version.value,
                "status_code": response.status_code,
                "passed": response.status_code == test_case.expected_status
            }
            
            if response.status_code == test_case.expected_status:
                data = response.json()
                result["response"] = data
                
                # Run validators
                if test_case.response_validators:
                    for validator in test_case.response_validators:
                        try:
                            validator(data, version)
                        except AssertionError as e:
                            result["passed"] = False
                            result["error"] = str(e)
            
            results.append(result)
        
        return results
    
    def test_backward_compatibility(self, v1_endpoint: str, v2_endpoint: str):
        """Test that V2 responses can be transformed to V1 format."""
        # Get V1 response
        v1_response = self.session.get(f"{self.BASE_URL}/v1{v1_endpoint}")
        v1_data = v1_response.json()
        
        # Get V2 response
        v2_response = self.session.get(f"{self.BASE_URL}/v2{v2_endpoint}")
        v2_data = v2_response.json()
        
        # Transform V2 to V1
        from .transformers import transform_incident_v2_to_v1
        transformed = transform_incident_v2_to_v1(v2_data)
        
        # Compare key fields
        assert "incident_id" in transformed
        assert "severity_level" in transformed
        
        return {
            "v1_response": v1_data,
            "v2_response": v2_data,
            "transformed": transformed,
            "compatible": True
        }

# Test cases
INCIDENT_LIST_TEST = VersionTestCase(
    name="List incidents",
    endpoint="/incidents",
    method="GET",
    versions=[APIVersion.V1, APIVersion.V2],
    expected_status=200,
    response_validators=[
        lambda data, v: assert "data" in data or "incidents" in data,
        lambda data, v: assert isinstance(data.get("data", data.get("incidents", [])), list)
    ]
)

INCIDENT_CREATE_TEST = VersionTestCase(
    name="Create incident",
    endpoint="/incidents",
    method="POST",
    versions=[APIVersion.V2],  # V1 doesn't support creation
    request_data={
        "title": "Test Incident",
        "severity": "P3",
        "description": "Test description"
    },
    expected_status=201,
    response_validators=[
        lambda data, v: assert "id" in data,
        lambda data, v: assert data["status"] == "open"
    ]
)

# Pytest fixtures and tests
@pytest.fixture
def version_tester():
    return VersionCompatibilityTester(api_key="test-key")

def test_list_incidents_across_versions(version_tester):
    results = version_tester.test_endpoint_across_versions(INCIDENT_LIST_TEST)
    assert all(r["passed"] for r in results)

def test_create_incident_v2(version_tester):
    results = version_tester.test_endpoint_across_versions(INCIDENT_CREATE_TEST)
    assert all(r["passed"] for r in results)

def assert(condition, message="Assertion failed"):
    if not condition:
        raise AssertionError(message)
```

### 8.2 Contract Testing

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/contract_testing.py
from pact import Consumer, Provider
import pytest
from .versions import APIVersion

@pytest.fixture
def pact():
    return Consumer("resilienceai-client").has_pact_with(
        Provider("resilienceai-api"),
        pact_dir="./pacts"
    )

def test_get_incident_v2_contract(pact):
    """Contract test for V2 get incident endpoint."""
    expected = {
        "id": "inc-123",
        "title": "Test Incident",
        "description": "Test description",
        "severity": "P2",
        "status": "open",
        "created_timestamp": "2024-01-15T10:30:00Z",
        "updated_timestamp": "2024-01-15T10:30:00Z",
        "assignee": None,
        "tags": []
    }
    
    (pact
     .given("an incident exists")
     .upon_receiving("a request for incident details")
     .with_request("GET", "/v2/incidents/inc-123")
     .will_respond_with(200, body=expected))
    
    with pact:
        result = requests.get("http://localhost:1234/v2/incidents/inc-123")
        assert result.status_code == 200
        assert result.json() == expected

def test_list_incidents_v2_contract(pact):
    """Contract test for V2 list incidents endpoint."""
    expected = {
        "data": [
            {
                "id": "inc-123",
                "title": "Test Incident",
                "severity": "P2",
                "status": "open",
                "created_timestamp": "2024-01-15T10:30:00Z"
            }
        ],
        "pagination": {
            "next_cursor": "cursor123",
            "has_more": True
        }
    }
    
    (pact
     .given("multiple incidents exist")
     .upon_receiving("a request to list incidents")
     .with_request("GET", "/v2/incidents", query={"limit": "10"})
     .will_respond_with(200, body=expected))
    
    with pact:
        result = requests.get("http://localhost:1234/v2/incidents?limit=10")
        assert result.status_code == 200
```

---

## 9. Sunset Policies

### 9.1 Sunset Timeline

```
┌────────────────────────────────────────────────────────────────────────┐
│                    API VERSION SUNSET TIMELINE                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  V1 Release    V2 Release   Deprecation   Sunset Notice   Retirement   │
│      │             │            │             │              │         │
│      ▼             ▼            ▼             ▼              ▼         │
│  ┌──────┐     ┌──────┐    ┌────────┐   ┌─────────┐    ┌─────────┐    │
│  │  V1  │────▶│  V2  │───▶│ V1 Dep │──▶│ V1 Sun  │───▶│ V1 Ret  │    │
│  │Active│     │Active│    │ 12mo   │   │  3mo    │    │  Gone   │    │
│  └──────┘     └──────┘    └────────┘   └─────────┘    └─────────┘    │
│                                                                        │
│  Timeline:                                                             │
│  ──────────────────────────────────────────────────────────────────    │
│  2023-01      2024-01      2024-01      2025-03        2025-06        │
│                                                                        │
│  Status Codes:                                                         │
│  ──────────────────────────────────────────────────────────────────    │
│  Active:     200 OK                                                    │
│  Deprecated: 200 OK + Deprecation headers                              │
│  Sunset:     200 OK + Sunset headers + Warning logs                    │
│  Retired:    410 Gone + Migration link                                 │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Sunset Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/sunset.py
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException
from .versions import APIVersion, VERSION_REGISTRY

class SunsetManager:
    """Manages API version sunset lifecycle."""
    
    SUNSET_WARNING_DAYS = 90
    FINAL_WARNING_DAYS = 30
    
    def __init__(self):
        self.sunset_schedule: Dict[APIVersion, datetime] = {}
    
    def schedule_sunset(
        self,
        version: APIVersion,
        sunset_date: datetime,
        replacement_version: APIVersion
    ):
        """Schedule a version for sunset."""
        self.sunset_schedule[version] = {
            "date": sunset_date,
            "replacement": replacement_version,
            "notifications_sent": []
        }
    
    def check_sunset_status(self, version: APIVersion) -> Dict[str, Any]:
        """Check sunset status for a version."""
        now = datetime.utcnow()
        version_info = VERSION_REGISTRY.get(version)
        
        if not version_info or not version_info.sunset_date:
            return {"status": "active", "sunset_scheduled": False}
        
        days_until_sunset = (version_info.sunset_date - now).days
        
        if days_until_sunset <= 0:
            return {
                "status": "retired",
                "sunset_scheduled": True,
                "days_overdue": abs(days_until_sunset),
                "action_required": "Migrate immediately",
                "migration_url": f"/docs/migration/{version.value}-to-{APIVersion.get_latest().value}"
            }
        elif days_until_sunset <= self.FINAL_WARNING_DAYS:
            return {
                "status": "critical",
                "sunset_scheduled": True,
                "days_remaining": days_until_sunset,
                "action_required": "URGENT: Migrate within 30 days",
                "migration_url": f"/docs/migration/{version.value}-to-{APIVersion.get_latest().value}"
            }
        elif days_until_sunset <= self.SUNSET_WARNING_DAYS:
            return {
                "status": "warning",
                "sunset_scheduled": True,
                "days_remaining": days_until_sunset,
                "action_required": "Plan migration",
                "migration_url": f"/docs/migration/{version.value}-to-{APIVersion.get_latest().value}"
            }
        else:
            return {
                "status": "deprecated",
                "sunset_scheduled": True,
                "days_remaining": days_until_sunset,
                "action_required": "Monitor for updates",
                "migration_url": f"/docs/migration/{version.value}-to-{APIVersion.get_latest().value}"
            }
    
    def get_sunset_headers(self, version: APIVersion) -> Dict[str, str]:
        """Get sunset-related headers for responses."""
        status = self.check_sunset_status(version)
        headers = {}
        
        if status["sunset_scheduled"]:
            version_info = VERSION_REGISTRY.get(version)
            if version_info and version_info.sunset_date:
                headers["Sunset"] = version_info.sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
                headers["X-API-Sunset-Status"] = status["status"]
                headers["X-API-Sunset-Days-Remaining"] = str(status.get("days_remaining", 0))
        
        return headers
    
    def enforce_sunset(self, version: APIVersion):
        """Enforce sunset - return 410 Gone for retired versions."""
        status = self.check_sunset_status(version)
        
        if status["status"] == "retired":
            raise HTTPException(
                status_code=410,
                detail={
                    "error": "Gone",
                    "message": f"API version {version.value} has been retired",
                    "retired_date": VERSION_REGISTRY[version].sunset_date.isoformat(),
                    "latest_version": APIVersion.get_latest().value,
                    "migration_guide": f"https://docs.resilienceai.com/migration/{version.value}-to-{APIVersion.get_latest().value}",
                    "support_email": "migration@resilienceai.com"
                },
                headers={
                    "Sunset": VERSION_REGISTRY[version].sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                    "Link": f'<https://docs.resilienceai.com/migration/{version.value}-to-{APIVersion.get_latest().value}>; rel="migration"'
                }
            )

# Global sunset manager
sunset_manager = SunsetManager()

# Configure sunset for V1
sunset_manager.schedule_sunset(
    version=APIVersion.V1,
    sunset_date=datetime(2025, 6, 30),
    replacement_version=APIVersion.V2
)
```

### 9.3 Sunset Notification Templates

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/sunset_notifications.py
from datetime import datetime
from typing import Dict, Any

class SunsetNotificationTemplates:
    """Templates for sunset notifications."""
    
    @staticmethod
    def deprecation_notice(version: str, sunset_date: datetime, replacement: str) -> Dict[str, Any]:
        return {
            "subject": f"Action Required: ResilienceAI API {version} Deprecation Notice",
            "body": f"""
Dear ResilienceAI API User,

We are writing to inform you that API version {version} will be deprecated on {sunset_date.strftime('%B %d, %Y')}.

Key Dates:
- Deprecation Date: {sunset_date.strftime('%B %d, %Y')} (12 months notice)
- Sunset Date: {(sunset_date + __import__('datetime').timedelta(days=365)).strftime('%B %d, %Y')}
- Retirement Date: {(sunset_date + __import__('datetime').timedelta(days=455)).strftime('%B %d, %Y')}

What You Need to Do:
1. Review the migration guide: https://docs.resilienceai.com/migration/{version}-to-{replacement}
2. Update your API calls to use {replacement}
3. Test your integration in our sandbox environment
4. Deploy changes before the sunset date

Breaking Changes:
- Field renames (incident_id → id)
- Severity format changes ("high" → "P2")
- Timestamp format changes to ISO 8601

Need Help?
- Migration Guide: https://docs.resilienceai.com/migration/{version}-to-{replacement}
- Office Hours: Tuesdays 2-3 PM EST
- Email: migration@resilienceai.com
- Slack: #api-migration

Best regards,
The ResilienceAI Team
            """,
            "html": f"""
<!DOCTYPE html>
<html>
<head><title>API Deprecation Notice</title></head>
<body>
    <h1>API Version {version} Deprecation Notice</h1>
    <p>API version {version} will be deprecated on <strong>{sunset_date.strftime('%B %d, %Y')}</strong>.</p>
    
    <h2>Timeline</h2>
    <ul>
        <li>Deprecation: {sunset_date.strftime('%B %d, %Y')}</li>
        <li>Sunset: {(sunset_date + __import__('datetime').timedelta(days=365)).strftime('%B %d, %Y')}</li>
        <li>Retirement: {(sunset_date + __import__('datetime').timedelta(days=455)).strftime('%B %d, %Y')}</li>
    </ul>
    
    <h2>Action Required</h2>
    <ol>
        <li>Review the <a href="https://docs.resilienceai.com/migration/{version}-to-{replacement}">migration guide</a></li>
        <li>Update to {replacement}</li>
        <li>Test in sandbox</li>
        <li>Deploy before sunset</li>
    </ol>
</body>
</html>
            """
        }
    
    @staticmethod
    def final_warning(version: str, days_remaining: int, replacement: str) -> Dict[str, Any]:
        return {
            "subject": f"URGENT: ResilienceAI API {version} Sunset in {days_remaining} Days",
            "body": f"""
URGENT: API Version {version} Sunset Notice

Your integration is using ResilienceAI API {version}, which will be retired in {days_remaining} days.

IMMEDIATE ACTION REQUIRED:
1. Migrate to {replacement} immediately
2. Test your integration: https://sandbox-api.resilienceai.com
3. Deploy before {(datetime.utcnow() + __import__('datetime').timedelta(days=days_remaining)).strftime('%B %d, %Y')}

After retirement, all {version} requests will return 410 Gone.

Migration Resources:
- Quick Start: https://docs.resilienceai.com/migration/{version}-to-{replacement}
- Migration Validator: https://tools.resilienceai.com/migration-validator
- Support: migration@resilienceai.com

This is your final warning before API retirement.
            """
        }
    
    @staticmethod
    def retirement_notice(version: str, replacement: str) -> Dict[str, Any]:
        return {
            "subject": f"ResilienceAI API {version} Has Been Retired",
            "body": f"""
API Version {version} Has Been Retired

As of today, ResilienceAI API {version} has been permanently retired.

All requests to {version} endpoints now return 410 Gone.

To restore service:
1. Update your API integration to {replacement}
2. Follow the migration guide: https://docs.resilienceai.com/migration/{version}-to-{replacement}
3. Contact support for assistance: migration@resilienceai.com

We apologize for any inconvenience and are here to help with your migration.
            """
        }
```

---

## 10. Client Communication

### 10.1 Communication Channels

```
┌─────────────────────────────────────────────────────────────────┐
│              CLIENT COMMUNICATION STRATEGY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Email     │  │  Dashboard  │  │   API       │             │
│  │  Campaigns  │  │   Notices   │  │  Headers    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │               │               │                       │
│         ▼               ▼               ▼                       │
│  ┌─────────────────────────────────────────────────┐           │
│  │              CLIENT NOTIFICATION SYSTEM          │           │
│  └─────────────────────────────────────────────────┘           │
│         │               │               │                       │
│         ▼               ▼               ▼                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Slack     │  │   Blog      │  │  Webhooks   │             │
│  │   Channel   │  │   Posts     │  │   Events    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Communication Manager

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/communication.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class NotificationChannel(Enum):
    EMAIL = "email"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    SLACK = "slack"

@dataclass
class ClientNotification:
    """Client notification configuration."""
    client_id: str
    channel: NotificationChannel
    version: str
    notification_type: str  # "deprecation", "sunset", "retirement"
    sent_at: datetime
    opened_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None

class ClientCommunicationManager:
    """Manages client communications for API versioning."""
    
    def __init__(self):
        self.notifications: List[ClientNotification] = []
        self.webhook_subscriptions: Dict[str, List[str]] = {}
    
    def register_webhook(self, client_id: str, webhook_url: str, events: List[str]):
        """Register a webhook for version-related events."""
        if client_id not in self.webhook_subscriptions:
            self.webhook_subscriptions[client_id] = []
        
        self.webhook_subscriptions[client_id].append({
            "url": webhook_url,
            "events": events,
            "registered_at": datetime.utcnow()
        })
    
    def notify_deprecation(
        self,
        client_id: str,
        version: str,
        sunset_date: datetime,
        channels: List[NotificationChannel] = None
    ):
        """Send deprecation notification to client."""
        channels = channels or [NotificationChannel.EMAIL]
        
        for channel in channels:
            notification = ClientNotification(
                client_id=client_id,
                channel=channel,
                version=version,
                notification_type="deprecation",
                sent_at=datetime.utcnow()
            )
            self.notifications.append(notification)
            
            if channel == NotificationChannel.WEBHOOK:
                self._send_webhook_notification(client_id, {
                    "event": "api_version.deprecated",
                    "version": version,
                    "sunset_date": sunset_date.isoformat(),
                    "migration_guide": f"https://docs.resilienceai.com/migration/{version}",
                    "timestamp": datetime.utcnow().isoformat()
                })
            elif channel == NotificationChannel.EMAIL:
                self._send_email_notification(client_id, version, sunset_date)
    
    def _send_webhook_notification(self, client_id: str, payload: Dict[str, Any]):
        """Send webhook notification."""
        import requests
        
        webhooks = self.webhook_subscriptions.get(client_id, [])
        for webhook in webhooks:
            if payload["event"] in webhook.get("events", []):
                try:
                    requests.post(
                        webhook["url"],
                        json=payload,
                        headers={
                            "X-ResilienceAI-Event": payload["event"],
                            "X-ResilienceAI-Signature": self._sign_payload(payload)
                        },
                        timeout=10
                    )
                except Exception as e:
                    print(f"Webhook delivery failed: {e}")
    
    def _send_email_notification(self, client_id: str, version: str, sunset_date: datetime):
        """Send email notification."""
        # Integration with email service
        pass
    
    def _sign_payload(self, payload: Dict[str, Any]) -> str:
        """Sign webhook payload for verification."""
        import hmac
        import hashlib
        import json
        
        secret = "webhook-secret"  # Load from config
        payload_str = json.dumps(payload, sort_keys=True)
        return hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def get_client_notification_history(
        self,
        client_id: str,
        version: Optional[str] = None
    ) -> List[ClientNotification]:
        """Get notification history for a client."""
        notifications = [
            n for n in self.notifications
            if n.client_id == client_id
        ]
        
        if version:
            notifications = [n for n in notifications if n.version == version]
        
        return notifications

# Webhook event types
WEBHOOK_EVENTS = {
    "api_version.deprecated": "API version has been deprecated",
    "api_version.sunset_warning": "Sunset warning for API version",
    "api_version.retired": "API version has been retired",
    "api_version.released": "New API version released",
    "api_version.breaking_change": "Breaking change announced"
}
```

---

## 11. Version Analytics

### 11.1 Analytics Framework

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/analytics.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json

@dataclass
class VersionMetrics:
    """Metrics for an API version."""
    version: str
    total_requests: int = 0
    unique_clients: set = field(default_factory=set)
    endpoints: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    error_rates: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    response_times: List[float] = field(default_factory=list)
    last_seen: Optional[datetime] = None

class VersionAnalytics:
    """Analytics collection for API versions."""
    
    def __init__(self):
        self.metrics: Dict[str, VersionMetrics] = defaultdict(
            lambda: VersionMetrics(version="unknown")
        )
        self.daily_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    def record_request(
        self,
        version: str,
        client_id: str,
        endpoint: str,
        status_code: int,
        response_time_ms: float
    ):
        """Record a request for analytics."""
        metrics = self.metrics[version]
        metrics.version = version
        metrics.total_requests += 1
        metrics.unique_clients.add(client_id)
        metrics.endpoints[endpoint] += 1
        metrics.error_rates[status_code] += 1
        metrics.response_times.append(response_time_ms)
        metrics.last_seen = datetime.utcnow()
    
    def get_version_adoption(self) -> Dict[str, Any]:
        """Get version adoption statistics."""
        total_requests = sum(m.total_requests for m in self.metrics.values())
        
        adoption = {}
        for version, metrics in self.metrics.items():
            adoption[version] = {
                "requests": metrics.total_requests,
                "percentage": (metrics.total_requests / total_requests * 100) if total_requests > 0 else 0,
                "unique_clients": len(metrics.unique_clients),
                "avg_response_time_ms": sum(metrics.response_times) / len(metrics.response_times) if metrics.response_times else 0,
                "last_seen": metrics.last_seen.isoformat() if metrics.last_seen else None
            }
        
        return {
            "total_requests": total_requests,
            "versions": adoption,
            "latest_version_adoption": adoption.get("v2", {}).get("percentage", 0)
        }
    
    def get_deprecated_version_usage(self) -> List[Dict[str, Any]]:
        """Get usage statistics for deprecated versions."""
        deprecated = []
        
        for version, metrics in self.metrics.items():
            if version in ["v1"]:  # Deprecated versions
                deprecated.append({
                    "version": version,
                    "requests_24h": metrics.total_requests,
                    "unique_clients": len(metrics.unique_clients),
                    "top_endpoints": sorted(
                        metrics.endpoints.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5],
                    "clients_to_migrate": list(metrics.unique_clients),
                    "estimated_migration_effort": self._estimate_migration_effort(
                        metrics.total_requests,
                        len(metrics.unique_clients)
                    )
                })
        
        return deprecated
    
    def _estimate_migration_effort(
        self,
        request_volume: int,
        client_count: int
    ) -> Dict[str, Any]:
        """Estimate migration effort for deprecated version users."""
        if request_volume < 1000 and client_count < 5:
            effort = "low"
            estimated_days = 7
        elif request_volume < 10000 and client_count < 20:
            effort = "medium"
            estimated_days = 30
        else:
            effort = "high"
            estimated_days = 90
        
        return {
            "level": effort,
            "estimated_days": estimated_days,
            "recommendation": f"Allocate {estimated_days} days for migration"
        }
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate comprehensive migration report."""
        deprecated_usage = self.get_deprecated_version_usage()
        
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_deprecated_requests": sum(
                    d["requests_24h"] for d in deprecated_usage
                ),
                "total_clients_to_migrate": sum(
                    len(d["clients_to_migrate"]) for d in deprecated_usage
                ),
                "overall_risk": self._calculate_migration_risk(deprecated_usage)
            },
            "deprecated_versions": deprecated_usage,
            "recommendations": self._generate_recommendations(deprecated_usage)
        }
    
    def _calculate_migration_risk(
        self,
        deprecated_usage: List[Dict[str, Any]]
    ) -> str:
        """Calculate overall migration risk level."""
        total_requests = sum(d["requests_24h"] for d in deprecated_usage)
        total_clients = sum(len(d["clients_to_migrate"]) for d in deprecated_usage)
        
        if total_requests > 100000 or total_clients > 50:
            return "critical"
        elif total_requests > 10000 or total_clients > 20:
            return "high"
        elif total_requests > 1000 or total_clients > 5:
            return "medium"
        return "low"
    
    def _generate_recommendations(
        self,
        deprecated_usage: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate migration recommendations."""
        recommendations = []
        
        total_requests = sum(d["requests_24h"] for d in deprecated_usage)
        
        if total_requests > 10000:
            recommendations.append(
                "Schedule direct outreach to top 10 API consumers"
            )
        
        recommendations.append(
            "Enable enhanced deprecation headers for all deprecated version responses"
        )
        
        recommendations.append(
            "Schedule office hours for migration support"
        )
        
        return recommendations

# Global analytics instance
version_analytics = VersionAnalytics()
```

### 11.2 Analytics Dashboard Endpoints

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/analytics_api.py
from fastapi import APIRouter, Depends
from typing import Dict, Any
from .analytics import version_analytics
from .versions import APIVersion

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/version-adoption")
async def get_version_adoption() -> Dict[str, Any]:
    """Get API version adoption statistics."""
    return version_analytics.get_version_adoption()

@router.get("/deprecated-usage")
async def get_deprecated_usage() -> Dict[str, Any]:
    """Get usage statistics for deprecated versions."""
    return {
        "deprecated_versions": version_analytics.get_deprecated_version_usage()
    }

@router.get("/migration-report")
async def get_migration_report() -> Dict[str, Any]:
    """Get comprehensive migration report."""
    return version_analytics.generate_migration_report()

@router.get("/version/{version}/metrics")
async def get_version_metrics(version: str) -> Dict[str, Any]:
    """Get detailed metrics for a specific version."""
    metrics = version_analytics.metrics.get(version)
    
    if not metrics:
        return {"error": "No metrics found for version"}
    
    return {
        "version": version,
        "total_requests": metrics.total_requests,
        "unique_clients": len(metrics.unique_clients),
        "top_endpoints": dict(sorted(
            metrics.endpoints.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]),
        "error_distribution": dict(metrics.error_rates),
        "avg_response_time_ms": (
            sum(metrics.response_times) / len(metrics.response_times)
            if metrics.response_times else 0
        ),
        "last_seen": metrics.last_seen.isoformat() if metrics.last_seen else None
    }
```

---

## 12. Implementation Roadmap

### 12.1 Priority Order

```
┌────────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION PRIORITY ORDER                       │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  PHASE 1: FOUNDATION (Weeks 1-2)                                      │
│  ──────────────────────────────────────────────────────────────────    │
│  [HIGH] 1. Implement URL path versioning                              │
│  [HIGH] 2. Create version registry and metadata                       │
│  [HIGH] 3. Set up backward compatibility layer                        │
│  [HIGH] 4. Implement deprecation headers                              │
│                                                                        │
│  PHASE 2: DOCUMENTATION (Weeks 3-4)                                   │
│  ──────────────────────────────────────────────────────────────────    │
│  [HIGH] 5. Generate OpenAPI specs for all versions                    │
│  [HIGH] 6. Create migration guides                                    │
│  [MED]  7. Set up multi-version documentation site                    │
│  [MED]  8. Implement version selector UI                              │
│                                                                        │
│  PHASE 3: TESTING (Weeks 5-6)                                         │
│  ──────────────────────────────────────────────────────────────────    │
│  [HIGH] 9. Implement version compatibility tests                      │
│  [HIGH] 10. Set up contract testing                                   │
│  [MED]  11. Create migration validation tools                         │
│  [MED]  12. Implement automated regression tests                      │
│                                                                        │
│  PHASE 4: COMMUNICATION (Weeks 7-8)                                   │
│  ──────────────────────────────────────────────────────────────────    │
│  [HIGH] 13. Implement client notification system                      │
│  [HIGH] 14. Set up webhook events for version changes                 │
│  [MED]  15. Create email notification templates                       │
│  [MED]  16. Implement in-app notifications                            │
│                                                                        │
│  PHASE 5: ANALYTICS (Weeks 9-10)                                      │
│  ──────────────────────────────────────────────────────────────────    │
│  [MED]  17. Implement version usage analytics                         │
│  [MED]  18. Create migration reports                                  │
│  [LOW]  19. Build analytics dashboard                                 │
│  [LOW]  20. Set up alerting for deprecated version usage              │
│                                                                        │
│  PHASE 6: SUNSET (Ongoing)                                            │
│  ──────────────────────────────────────────────────────────────────    │
│  [HIGH] 21. Implement sunset enforcement                              │
│  [HIGH] 22. Create sunset notification campaigns                      │
│  [MED]  23. Implement 410 Gone responses for retired versions         │
│  [MED]  24. Archive retired version documentation                     │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 12.2 Implementation Checklist

```python
# /mnt/okcomputer/output/resilience_ai_analysis/api_versioning/checklist.py
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Status(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

@dataclass
class ImplementationTask:
    """API versioning implementation task."""
    id: str
    description: str
    priority: Priority
    status: Status
    phase: int
    dependencies: List[str]
    estimated_hours: int
    assigned_to: Optional[str] = None
    completed_at: Optional[str] = None

# Implementation tasks
IMPLEMENTATION_TASKS = [
    # Phase 1: Foundation
    ImplementationTask("V-001", "Implement URL path versioning", Priority.HIGH, Status.NOT_STARTED, 1, [], 8),
    ImplementationTask("V-002", "Create version registry and metadata", Priority.HIGH, Status.NOT_STARTED, 1, ["V-001"], 4),
    ImplementationTask("V-003", "Set up backward compatibility layer", Priority.HIGH, Status.NOT_STARTED, 1, ["V-001"], 16),
    ImplementationTask("V-004", "Implement deprecation headers", Priority.HIGH, Status.NOT_STARTED, 1, ["V-002"], 4),
    
    # Phase 2: Documentation
    ImplementationTask("V-005", "Generate OpenAPI specs for all versions", Priority.HIGH, Status.NOT_STARTED, 2, ["V-001"], 8),
    ImplementationTask("V-006", "Create migration guides", Priority.HIGH, Status.NOT_STARTED, 2, ["V-002"], 16),
    ImplementationTask("V-007", "Set up multi-version documentation site", Priority.MEDIUM, Status.NOT_STARTED, 2, ["V-005"], 12),
    ImplementationTask("V-008", "Implement version selector UI", Priority.MEDIUM, Status.NOT_STARTED, 2, ["V-007"], 8),
    
    # Phase 3: Testing
    ImplementationTask("V-009", "Implement version compatibility tests", Priority.HIGH, Status.NOT_STARTED, 3, ["V-003"], 16),
    ImplementationTask("V-010", "Set up contract testing", Priority.HIGH, Status.NOT_STARTED, 3, ["V-009"], 12),
    ImplementationTask("V-011", "Create migration validation tools", Priority.MEDIUM, Status.NOT_STARTED, 3, ["V-006"], 8),
    ImplementationTask("V-012", "Implement automated regression tests", Priority.MEDIUM, Status.NOT_STARTED, 3, ["V-009"], 12),
    
    # Phase 4: Communication
    ImplementationTask("V-013", "Implement client notification system", Priority.HIGH, Status.NOT_STARTED, 4, ["V-004"], 12),
    ImplementationTask("V-014", "Set up webhook events for version changes", Priority.HIGH, Status.NOT_STARTED, 4, ["V-013"], 8),
    ImplementationTask("V-015", "Create email notification templates", Priority.MEDIUM, Status.NOT_STARTED, 4, ["V-013"], 4),
    ImplementationTask("V-016", "Implement in-app notifications", Priority.MEDIUM, Status.NOT_STARTED, 4, ["V-013"], 8),
    
    # Phase 5: Analytics
    ImplementationTask("V-017", "Implement version usage analytics", Priority.MEDIUM, Status.NOT_STARTED, 5, ["V-001"], 12),
    ImplementationTask("V-018", "Create migration reports", Priority.MEDIUM, Status.NOT_STARTED, 5, ["V-017"], 8),
    ImplementationTask("V-019", "Build analytics dashboard", Priority.LOW, Status.NOT_STARTED, 5, ["V-017"], 16),
    ImplementationTask("V-020", "Set up alerting for deprecated version usage", Priority.LOW, Status.NOT_STARTED, 5, ["V-017"], 8),
    
    # Phase 6: Sunset
    ImplementationTask("V-021", "Implement sunset enforcement", Priority.HIGH, Status.NOT_STARTED, 6, ["V-004"], 8),
    ImplementationTask("V-022", "Create sunset notification campaigns", Priority.HIGH, Status.NOT_STARTED, 6, ["V-013"], 8),
    ImplementationTask("V-023", "Implement 410 Gone responses for retired versions", Priority.MEDIUM, Status.NOT_STARTED, 6, ["V-021"], 4),
    ImplementationTask("V-024", "Archive retired version documentation", Priority.MEDIUM, Status.NOT_STARTED, 6, ["V-023"], 4),
]

def get_tasks_by_phase(phase: int) -> List[ImplementationTask]:
    """Get tasks for a specific phase."""
    return [t for t in IMPLEMENTATION_TASKS if t.phase == phase]

def get_tasks_by_priority(priority: Priority) -> List[ImplementationTask]:
    """Get tasks by priority."""
    return [t for t in IMPLEMENTATION_TASKS if t.priority == priority]

def get_critical_path() -> List[ImplementationTask]:
    """Get tasks on the critical path."""
    return [t for t in IMPLEMENTATION_TASKS if t.priority == Priority.HIGH]

def calculate_total_effort() -> Dict[str, int]:
    """Calculate total implementation effort."""
    total_hours = sum(t.estimated_hours for t in IMPLEMENTATION_TASKS)
    high_hours = sum(t.estimated_hours for t in IMPLEMENTATION_TASKS if t.priority == Priority.HIGH)
    
    return {
        "total_hours": total_hours,
        "total_days": total_hours // 8,
        "high_priority_hours": high_hours,
        "high_priority_days": high_hours // 8
    }
```

---

## Summary

This comprehensive API versioning strategy for ResilienceAI provides:

1. **Versioning Approaches**: URL path (primary), header-based, and content negotiation
2. **Backward Compatibility**: Field mappings, transformers, and compatibility layers
3. **Deprecation Policy**: 12-month deprecation notice with clear lifecycle stages
4. **Migration Guides**: Automated tools and comprehensive documentation
5. **Version Negotiation**: Multi-strategy negotiation with fallback to latest
6. **Documentation**: Multi-version OpenAPI specs and interactive docs
7. **Testing**: Compatibility testing, contract testing, and validation tools
8. **Sunset Policies**: Gradual enforcement with 410 Gone for retired versions
9. **Client Communication**: Multi-channel notifications and webhook events
10. **Analytics**: Version adoption tracking and migration reporting

### Key Files Created

| File | Description |
|------|-------------|
| `versions.py` | Version registry and metadata |
| `header_versioning.py` | Header-based version negotiation |
| `content_negotiation.py` | Accept header version parsing |
| `compatibility.py` | Backward compatibility layer |
| `transformers.py` | Version transformation functions |
| `deprecation.py` | Deprecation lifecycle management |
| `migration_assistant.py` | Automated migration tools |
| `negotiation.py` | Version negotiation logic |
| `fastapi_integration.py` | FastAPI integration example |
| `openapi_config.py` | OpenAPI spec generation |
| `version_testing.py` | Version compatibility testing |
| `contract_testing.py` | Contract testing with Pact |
| `sunset.py` | Sunset lifecycle management |
| `sunset_notifications.py` | Sunset notification templates |
| `communication.py` | Client communication manager |
| `analytics.py` | Version analytics framework |
| `analytics_api.py` | Analytics API endpoints |
| `checklist.py` | Implementation task checklist |

### Next Steps

1. Implement Phase 1 foundation components
2. Set up CI/CD for multi-version testing
3. Create developer portal for version documentation
4. Establish regular version review meetings
5. Monitor analytics and adjust policies as needed
