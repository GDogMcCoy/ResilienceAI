"""
Version Transformation Functions

Provides transformation functions for converting data between API versions.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime


def transform_severity_v1_to_v2(v1_severity: str) -> str:
    """
    Transform V1 severity levels to V2 P-level format.
    
    V1: "low", "medium", "high", "critical"
    V2: "P4", "P3", "P2", "P1"
    
    Args:
        v1_severity: Severity string in V1 format
        
    Returns:
        Severity string in V2 format
    """
    mapping = {
        "low": "P4",
        "medium": "P3",
        "high": "P2",
        "critical": "P1"
    }
    return mapping.get(v1_severity.lower(), "P3")


def transform_severity_v2_to_v1(v2_severity: str) -> str:
    """
    Transform V2 P-level severity to V1 format.
    
    Args:
        v2_severity: Severity string in V2 format
        
    Returns:
        Severity string in V1 format
    """
    mapping = {
        "P4": "low",
        "P3": "medium",
        "P2": "high",
        "P1": "critical"
    }
    return mapping.get(v2_severity.upper(), "medium")


def transform_timestamp_v1_to_v2(v1_timestamp: str) -> str:
    """
    Transform V1 timestamp to V2 ISO 8601 format.
    
    V1: "2024-01-15 10:30:00"
    V2: "2024-01-15T10:30:00Z"
    
    Args:
        v1_timestamp: Timestamp in V1 format
        
    Returns:
        Timestamp in V2 ISO 8601 format
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(v1_timestamp, fmt)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            continue
    
    # Return original if parsing fails
    return v1_timestamp


def transform_timestamp_v2_to_v1(v2_timestamp: str) -> str:
    """
    Transform V2 ISO 8601 timestamp to V1 format.
    
    Args:
        v2_timestamp: Timestamp in V2 ISO 8601 format
        
    Returns:
        Timestamp in V1 format
    """
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S+00:00"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(v2_timestamp, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    
    return v2_timestamp


def transform_status_v1_to_v2(v1_status: str) -> str:
    """
    Transform V1 status to V2 format.
    
    Args:
        v1_status: Status string in V1 format
        
    Returns:
        Status string in V2 format
    """
    # Status values are the same in V1 and V2
    # This is a placeholder for future changes
    mapping = {
        "open": "open",
        "in_progress": "in_progress",
        "resolved": "resolved",
        "closed": "closed"
    }
    return mapping.get(v1_status.lower(), v1_status)


def transform_incident_v2_to_v1(v2_incident: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform V2 incident format to V1 for backward compatibility.
    
    Args:
        v2_incident: Incident data in V2 format
        
    Returns:
        Incident data in V1 format
    """
    v1_incident = v2_incident.copy()
    
    # Map field names
    if "id" in v1_incident:
        v1_incident["incident_id"] = v1_incident.pop("id")
    
    if "created_timestamp" in v1_incident:
        v1_incident["created_at"] = transform_timestamp_v2_to_v1(
            v1_incident.pop("created_timestamp")
        )
    
    if "severity" in v1_incident:
        v1_incident["severity_level"] = transform_severity_v2_to_v1(
            v1_incident.pop("severity")
        )
    
    # Remove V2-only fields
    v2_only_fields = ["updated_timestamp", "assignee", "tags"]
    for field in v2_only_fields:
        v1_incident.pop(field, None)
    
    # Add metadata
    v1_incident["_meta"] = {
        "api_version": "v1",
        "transformed_from": "v2",
        "deprecated_fields": ["legacy_field", "old_status"]
    }
    
    return v1_incident


def transform_incident_v1_to_v2(v1_incident: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform V1 incident format to V2.
    
    Args:
        v1_incident: Incident data in V1 format
        
    Returns:
        Incident data in V2 format
    """
    v2_incident = v1_incident.copy()
    
    # Map field names
    if "incident_id" in v2_incident:
        v2_incident["id"] = v2_incident.pop("incident_id")
    
    if "created_at" in v2_incident:
        v2_incident["created_timestamp"] = transform_timestamp_v1_to_v2(
            v2_incident.pop("created_at")
        )
    
    if "severity_level" in v2_incident:
        v2_incident["severity"] = transform_severity_v1_to_v2(
            v2_incident.pop("severity_level")
        )
    
    # Add V2-only fields with defaults
    if "updated_timestamp" not in v2_incident:
        v2_incident["updated_timestamp"] = v2_incident.get("created_timestamp")
    
    if "assignee" not in v2_incident:
        v2_incident["assignee"] = None
    
    if "tags" not in v2_incident:
        v2_incident["tags"] = []
    
    # Add metadata
    v2_incident["_meta"] = {
        "api_version": "v2",
        "transformed_from": "v1"
    }
    
    return v2_incident


def transform_incident_list_v2_to_v1(v2_list: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform V2 incident list to V1 format.
    
    Args:
        v2_list: Incident list in V2 format
        
    Returns:
        Incident list in V1 format
    """
    v1_list = {
        "incidents": [],
        "total": len(v2_list.get("data", []))
    }
    
    for incident in v2_list.get("data", []):
        v1_list["incidents"].append(transform_incident_v2_to_v1(incident))
    
    return v1_list


def transform_incident_list_v1_to_v2(v1_list: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform V1 incident list to V2 format.
    
    Args:
        v1_list: Incident list in V1 format
        
    Returns:
        Incident list in V2 format
    """
    v2_list = {
        "data": [],
        "pagination": {
            "next_cursor": None,
            "has_more": False
        }
    }
    
    for incident in v1_list.get("incidents", []):
        v2_list["data"].append(transform_incident_v1_to_v2(incident))
    
    return v2_list


# Transformation registry for automated transformations
TRANSFORMATION_REGISTRY = {
    ("v1", "v2", "incident"): transform_incident_v1_to_v2,
    ("v2", "v1", "incident"): transform_incident_v2_to_v1,
    ("v1", "v2", "incident_list"): transform_incident_list_v1_to_v2,
    ("v2", "v1", "incident_list"): transform_incident_list_v2_to_v1,
    ("v1", "v2", "severity"): transform_severity_v1_to_v2,
    ("v2", "v1", "severity"): transform_severity_v2_to_v1,
    ("v1", "v2", "timestamp"): transform_timestamp_v1_to_v2,
    ("v2", "v1", "timestamp"): transform_timestamp_v2_to_v1,
}


def get_transformer(
    source_version: str,
    target_version: str,
    data_type: str
) -> Optional[callable]:
    """
    Get transformation function for version and data type.
    
    Args:
        source_version: Source API version
        target_version: Target API version
        data_type: Type of data to transform
        
    Returns:
        Transformation function or None
    """
    return TRANSFORMATION_REGISTRY.get((source_version, target_version, data_type))


def transform_data(
    data: Any,
    source_version: str,
    target_version: str,
    data_type: str
) -> Any:
    """
    Transform data between versions.
    
    Args:
        data: Data to transform
        source_version: Source API version
        target_version: Target API version
        data_type: Type of data
        
    Returns:
        Transformed data
    """
    transformer = get_transformer(source_version, target_version, data_type)
    
    if transformer:
        return transformer(data)
    
    # Return original if no transformer found
    return data
