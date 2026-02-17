"""
API Version Negotiation

Handles version negotiation using multiple strategies with priority ordering.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from fastapi import Request, HTTPException
import re

from .versions import APIVersion, VERSION_REGISTRY


@dataclass
class VersionPreference:
    """Client version preference with priority (q-value)."""
    version: APIVersion
    priority: float  # q-value from Accept header (0.0 - 1.0)


class VersionNegotiator:
    """
    Handles API version negotiation using multiple strategies.
    
    Priority order:
    1. URL path version (highest priority)
    2. Custom API-Version header
    3. Accept header content negotiation
    4. Default to latest stable version (lowest priority)
    """
    
    MEDIA_TYPE_PATTERN = re.compile(
        r"application/vnd\.resilienceai\.(v\d+)\+json"
    )
    
    def __init__(self):
        self.supported_versions = APIVersion.get_supported()
    
    def negotiate_version(
        self,
        request: Request,
        url_version: Optional[str] = None
    ) -> APIVersion:
        """
        Negotiate API version using multiple strategies.
        
        Args:
            request: FastAPI request object
            url_version: Optional version from URL path
            
        Returns:
            Negotiated API version
            
        Raises:
            HTTPException: If requested version is invalid or unsupported
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
        """
        Validate and return version from string.
        
        Args:
            version_str: Version string (e.g., "v1", "v2")
            
        Returns:
            Validated APIVersion
            
        Raises:
            HTTPException: If version is invalid or unsupported
        """
        # Normalize version string
        version_str = version_str.lower().lstrip("v")
        
        try:
            version = APIVersion(f"v{version_str}")
            
            # Check if version is supported
            if version not in self.supported_versions:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Unsupported API version",
                        "requested_version": version_str,
                        "supported_versions": [v.value for v in self.supported_versions],
                        "latest_version": APIVersion.get_latest().value,
                        "message": f"Version 'v{version_str}' is not supported. Please use one of the supported versions."
                    }
                )
            
            # Check if version is retired
            version_info = VERSION_REGISTRY.get(version)
            if version_info and version_info.status == "retired":
                raise HTTPException(
                    status_code=410,
                    detail={
                        "error": "API version retired",
                        "requested_version": version_str,
                        "retired_date": version_info.sunset_date.isoformat() if version_info.sunset_date else None,
                        "latest_version": APIVersion.get_latest().value,
                        "migration_guide": version_info.migration_guide_url,
                        "message": f"Version 'v{version_str}' has been retired. Please migrate to the latest version."
                    }
                )
            
            return version
            
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid API version format",
                    "requested_version": version_str,
                    "expected_format": "v1, v2, etc.",
                    "message": f"Invalid version format '{version_str}'. Expected format: 'v1', 'v2', etc."
                }
            )
    
    def _parse_accept_header(self, request: Request) -> Optional[APIVersion]:
        """
        Parse version from Accept header.
        
        Supports media types like:
        - application/vnd.resilienceai.v2+json
        - application/vnd.resilienceai.v2+json;q=0.9
        
        Args:
            request: FastAPI request object
            
        Returns:
            APIVersion if found, None otherwise
        """
        accept = request.headers.get("Accept", "")
        
        if not accept:
            return None
        
        # Parse media types with q-values
        preferences: List[VersionPreference] = []
        
        for media_type in accept.split(","):
            media_type = media_type.strip()
            
            # Check for versioned media type
            if "vnd.resilienceai.v" in media_type:
                parts = media_type.split(";")
                main_type = parts[0].strip()
                
                # Extract version
                match = self.MEDIA_TYPE_PATTERN.search(main_type)
                if match:
                    version_str = match.group(1)
                    
                    # Extract q-value (default 1.0)
                    q_value = 1.0
                    for part in parts[1:]:
                        part = part.strip()
                        if part.startswith("q="):
                            try:
                                q_value = float(part[2:])
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
        
        return info.to_dict()
    
    def get_negotiation_summary(self, request: Request) -> Dict[str, Any]:
        """Get summary of version negotiation for debugging."""
        return {
            "url_version": request.path_params.get("version"),
            "header_version": request.headers.get("API-Version"),
            "accept_header": request.headers.get("Accept"),
            "negotiated_version": self.negotiate_version(request).value,
            "supported_versions": [v.value for v in self.supported_versions]
        }


# Global negotiator instance
version_negotiator = VersionNegotiator()
