"""
FastAPI Integration for API Versioning

Provides FastAPI middleware, dependencies, and routers for version handling.
"""

from fastapi import FastAPI, Request, Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.base import BaseHTTPMiddleware
from typing import Optional, Callable, Dict, Any
import time

from .versions import APIVersion, VERSION_REGISTRY
from .negotiation import version_negotiator
from .deprecation import deprecation_manager
from .sunset import sunset_manager
from .analytics import version_analytics
from .compatibility import compatibility


class VersionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API version handling.
    
    - Extracts version from request
    - Records analytics
    - Adds version headers to responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Start timing
        start_time = time.time()
        
        # Extract version from URL path
        path = request.url.path
        version = self._extract_version_from_path(path)
        
        # Store version in request state
        request.state.api_version = version
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Record analytics
        client_id = request.headers.get("X-Client-ID", "anonymous")
        endpoint = path
        status_code = response.status_code
        
        if version:
            version_analytics.record_request(
                version=version.value if isinstance(version, APIVersion) else str(version),
                client_id=client_id,
                endpoint=endpoint,
                status_code=status_code,
                response_time_ms=response_time_ms
            )
        
        # Add version headers
        if version:
            response.headers["X-API-Version"] = (
                version.value if isinstance(version, APIVersion) else str(version)
            )
            response.headers["X-API-Latest-Version"] = APIVersion.get_latest().value
            
            # Add deprecation headers if applicable
            deprecation_headers = deprecation_manager.get_deprecation_headers(
                f"{version.value}-api" if isinstance(version, APIVersion) else f"{version}-api",
                version.value if isinstance(version, APIVersion) else str(version)
            )
            for header, value in deprecation_headers.items():
                response.headers[header] = value
            
            # Add sunset headers if applicable
            if isinstance(version, APIVersion):
                sunset_headers = sunset_manager.get_sunset_headers(version)
                for header, value in sunset_headers.items():
                    response.headers[header] = value
        
        return response
    
    def _extract_version_from_path(self, path: str) -> Optional[APIVersion]:
        """Extract API version from URL path."""
        parts = path.strip("/").split("/")
        if parts and parts[0].startswith("v"):
            try:
                return APIVersion(parts[0])
            except ValueError:
                pass
        return None


def get_api_version(request: Request) -> APIVersion:
    """
    FastAPI dependency to extract and validate API version.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Validated API version
    """
    # Check if version is already extracted by middleware
    if hasattr(request.state, "api_version") and request.state.api_version:
        return request.state.api_version
    
    # Extract from URL path
    path_version = request.path_params.get("version")
    
    # Negotiate version
    version = version_negotiator.negotiate_version(request, path_version)
    
    # Check if version is sunset
    if isinstance(version, APIVersion):
        sunset_manager.enforce_sunset(version)
    
    return version


def get_versioned_response(
    data: Dict[str, Any],
    version: APIVersion,
    source_version: str = "latest"
) -> Dict[str, Any]:
    """
    Get response data transformed for target version.
    
    Args:
        data: Response data
        version: Target API version
        source_version: Source version of data
        
    Returns:
        Transformed response data
    """
    if source_version != version.value:
        return compatibility.transform_response(
            data, source_version, version.value
        )
    return data


# Versioned router factory
def create_versioned_router(version: APIVersion) -> APIRouter:
    """
    Create a router for a specific API version.
    
    Args:
        version: API version
        
    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix=f"/{version.value}")
    
    @router.get("/incidents")
    async def list_incidents(
        request: Request,
        api_version: APIVersion = Depends(get_api_version)
    ):
        """List incidents (versioned)."""
        # This would call your actual service
        data = {
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
                "next_cursor": None,
                "has_more": False
            }
        }
        
        # Transform for V1 if needed
        if api_version == APIVersion.V1:
            from .transformers import transform_incident_list_v2_to_v1
            data = transform_incident_list_v2_to_v1(data)
        
        return data
    
    @router.get("/incidents/{incident_id}")
    async def get_incident(
        incident_id: str,
        api_version: APIVersion = Depends(get_api_version)
    ):
        """Get incident by ID (versioned)."""
        data = {
            "id": incident_id,
            "title": "Test Incident",
            "description": "Test description",
            "severity": "P2",
            "status": "open",
            "created_timestamp": "2024-01-15T10:30:00Z",
            "updated_timestamp": "2024-01-15T10:30:00Z",
            "assignee": None,
            "tags": []
        }
        
        # Transform for V1 if needed
        if api_version == APIVersion.V1:
            from .transformers import transform_incident_v2_to_v1
            data = transform_incident_v2_to_v1(data)
        
        return data
    
    @router.post("/incidents")
    async def create_incident(
        request: Request,
        api_version: APIVersion = Depends(get_api_version)
    ):
        """Create incident (V2+ only)."""
        if api_version == APIVersion.V1:
            raise HTTPException(
                status_code=400,
                detail="Incident creation is not supported in V1. Please use V2."
            )
        
        # Process creation
        return {"id": "inc-new", "status": "created"}
    
    return router


def create_versioned_app() -> FastAPI:
    """
    Create a FastAPI application with versioning support.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="ResilienceAI API",
        description="ResilienceAI API with versioning support",
        version="2.0.0"
    )
    
    # Add version middleware
    app.add_middleware(VersionMiddleware)
    
    # Register versioned routers
    for v in APIVersion.get_supported():
        app.include_router(create_versioned_router(v))
    
    # Version info endpoint
    @app.get("/versions")
    async def list_versions():
        """List all available API versions."""
        return {
            "versions": [
                {
                    "version": v.value,
                    "status": VERSION_REGISTRY[v].status,
                    "documentation_url": VERSION_REGISTRY[v].documentation_url
                }
                for v in APIVersion.get_supported()
            ],
            "latest": APIVersion.get_latest().value,
            "documentation": "/docs"
        }
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "versions": [v.value for v in APIVersion.get_supported()]
        }
    
    # Analytics endpoints (admin only)
    @app.get("/admin/analytics/version-adoption")
    async def get_version_adoption():
        """Get version adoption statistics."""
        return version_analytics.get_version_adoption()
    
    @app.get("/admin/analytics/deprecated-usage")
    async def get_deprecated_usage():
        """Get deprecated version usage."""
        return {
            "deprecated_versions": version_analytics.get_deprecated_version_usage()
        }
    
    @app.get("/admin/analytics/migration-report")
    async def get_migration_report():
        """Get migration report."""
        return version_analytics.generate_migration_report()
    
    return app


# Example usage
if __name__ == "__main__":
    import uvicorn
    
    app = create_versioned_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
