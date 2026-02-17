"""
Backward Compatibility Layer

Provides field mappings, transformations, and compatibility handling
for supporting multiple API versions simultaneously.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import copy


@dataclass
class FieldCompatibility:
    """Defines field compatibility mapping between versions."""
    name: str
    versions: List[str]
    deprecated_in: Optional[str] = None
    replacement: Optional[str] = None
    transform: Optional[Callable] = None


class CompatibilityLayer:
    """
    Handles backward compatibility transformations between API versions.
    
    This class manages:
    - Field name mappings
    - Value transformations
    - Deprecation tracking
    - Response transformation
    """
    
    def __init__(self):
        self.field_mappings: Dict[str, Dict[str, str]] = {}
        self.transforms: Dict[str, Dict[str, Callable]] = {}
        self.deprecated_fields: Dict[str, List[str]] = {}
        self.added_fields: Dict[str, List[str]] = {}
    
    def register_field_mapping(
        self,
        source_version: str,
        target_version: str,
        old_name: str,
        new_name: str,
        transform: Optional[Callable] = None,
        reverse_transform: Optional[Callable] = None
    ):
        """
        Register a field name mapping between versions.
        
        Args:
            source_version: Source API version (e.g., "v1")
            target_version: Target API version (e.g., "v2")
            old_name: Field name in source version
            new_name: Field name in target version
            transform: Optional transformation function (source -> target)
            reverse_transform: Optional reverse transformation (target -> source)
        """
        version_pair = f"{source_version}_to_{target_version}"
        reverse_pair = f"{target_version}_to_{source_version}"
        
        if version_pair not in self.field_mappings:
            self.field_mappings[version_pair] = {}
            self.transforms[version_pair] = {}
        
        if reverse_pair not in self.field_mappings:
            self.field_mappings[reverse_pair] = {}
            self.transforms[reverse_pair] = {}
        
        # Forward mapping
        self.field_mappings[version_pair][old_name] = new_name
        if transform:
            self.transforms[version_pair][old_name] = transform
        
        # Reverse mapping
        self.field_mappings[reverse_pair][new_name] = old_name
        if reverse_transform:
            self.transforms[reverse_pair][new_name] = reverse_transform
    
    def register_deprecated_field(
        self,
        version: str,
        field_name: str,
        replacement: Optional[str] = None
    ):
        """
        Mark a field as deprecated in a specific version.
        
        Args:
            version: API version where field is deprecated
            field_name: Name of deprecated field
            replacement: Optional replacement field name
        """
        if version not in self.deprecated_fields:
            self.deprecated_fields[version] = []
        
        self.deprecated_fields[version].append({
            "field": field_name,
            "replacement": replacement,
            "deprecated_at": datetime.utcnow().isoformat()
        })
    
    def register_added_field(
        self,
        version: str,
        field_name: str,
        default_value: Any = None
    ):
        """
        Register a field that was added in a specific version.
        
        Args:
            version: API version where field was added
            field_name: Name of added field
            default_value: Default value for backward compatibility
        """
        if version not in self.added_fields:
            self.added_fields[version] = []
        
        self.added_fields[version].append({
            "field": field_name,
            "default_value": default_value,
            "added_at": datetime.utcnow().isoformat()
        })
    
    def transform_response(
        self,
        data: Dict[str, Any],
        source_version: str,
        target_version: str
    ) -> Dict[str, Any]:
        """
        Transform response data from source version to target version format.
        
        Args:
            data: Response data to transform
            source_version: Source API version
            target_version: Target API version
            
        Returns:
            Transformed response data
        """
        if source_version == target_version:
            return data
        
        version_pair = f"{source_version}_to_{target_version}"
        result = copy.deepcopy(data)
        
        # Apply field mappings
        if version_pair in self.field_mappings:
            for old_name, new_name in self.field_mappings[version_pair].items():
                if old_name in result:
                    value = result.pop(old_name)
                    
                    # Apply transformation if available
                    if version_pair in self.transforms and old_name in self.transforms[version_pair]:
                        value = self.transforms[version_pair][old_name](value)
                    
                    result[new_name] = value
        
        # Add deprecation metadata
        if target_version in self.deprecated_fields:
            deprecated = [
                f for f in self.deprecated_fields[target_version]
                if f["field"] in result
            ]
            if deprecated:
                result["_meta"] = result.get("_meta", {})
                result["_meta"]["deprecated_fields"] = deprecated
        
        # Add version info
        result["_meta"] = result.get("_meta", {})
        result["_meta"]["api_version"] = target_version
        result["_meta"]["transformed_from"] = source_version
        
        return result
    
    def transform_request(
        self,
        data: Dict[str, Any],
        source_version: str,
        target_version: str
    ) -> Dict[str, Any]:
        """
        Transform request data from source version to target version format.
        
        Args:
            data: Request data to transform
            source_version: Source API version of the request
            target_version: Target API version for processing
            
        Returns:
            Transformed request data
        """
        # Same logic as response transformation but in reverse
        return self.transform_response(data, source_version, target_version)
    
    def get_compatibility_report(self, version: str) -> Dict[str, Any]:
        """
        Get compatibility report for a specific version.
        
        Args:
            version: API version to report on
            
        Returns:
            Compatibility report
        """
        return {
            "version": version,
            "deprecated_fields": self.deprecated_fields.get(version, []),
            "added_fields": self.added_fields.get(version, []),
            "field_mappings": {
                k: v for k, v in self.field_mappings.items()
                if version in k
            }
        }


# Global compatibility layer instance
compatibility = CompatibilityLayer()

# Register V1 -> V2 mappings
compatibility.register_field_mapping(
    "v1", "v2",
    "incident_id", "id"
)

compatibility.register_field_mapping(
    "v1", "v2",
    "created_at", "created_timestamp"
)

compatibility.register_field_mapping(
    "v1", "v2",
    "severity_level", "severity"
)

# Register deprecated fields
compatibility.register_deprecated_field("v1", "legacy_field", replacement="new_field")
compatibility.register_deprecated_field("v1", "old_status", replacement="status")

# Register added fields in V2
compatibility.register_added_field("v2", "updated_timestamp")
compatibility.register_added_field("v2", "assignee", default_value=None)
compatibility.register_added_field("v2", "tags", default_value=[])
