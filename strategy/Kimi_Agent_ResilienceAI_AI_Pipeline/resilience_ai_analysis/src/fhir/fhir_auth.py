"""
SMART on FHIR Authentication Module
Implements OAuth2 authorization for FHIR server integration.
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FHIRConfig:
    """Configuration for FHIR server integration."""
    server_base_url: str = "http://localhost:8080/fhir"
    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True
    auth_type: str = "none"  # none, basic, bearer, smart
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    token_url: Optional[str] = None
    authorization_url: Optional[str] = None
    scope: str = "system/*.read system/*.write"


class SMARTonFHIRAuth:
    """
    SMART on FHIR authentication handler.
    
    Implements OAuth2 authorization code flow and client credentials flow
    for FHIR server authentication.
    """
    
    def __init__(self, config: FHIRConfig):
        """
        Initialize SMART on FHIR authentication.
        
        Args:
            config: FHIR configuration with authentication details
        """
        self.config = config
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.session = requests.Session()
    
    def discover_auth_endpoints(self, fhir_base_url: str) -> Dict[str, str]:
        """
        Discover SMART on FHIR authorization endpoints.
        
        Args:
            fhir_base_url: Base URL of the FHIR server
            
        Returns:
            Dictionary containing authorization and token endpoints
        """
        try:
            # Fetch FHIR server capability statement
            response = self.session.get(
                f"{fhir_base_url}/metadata",
                headers={"Accept": "application/fhir+json"},
                timeout=30
            )
            response.raise_for_status()
            
            capability = response.json()
            
            # Extract security extensions
            rest = capability.get("rest", [{}])[0]
            security = rest.get("security", {})
            extensions = security.get("extension", [])
            
            endpoints = {}
            for ext in extensions:
                if ext.get("url") == "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris":
                    for inner_ext in ext.get("extension", []):
                        if inner_ext.get("url") == "authorize":
                            endpoints["authorization_endpoint"] = inner_ext.get("valueUri")
                        elif inner_ext.get("url") == "token":
                            endpoints["token_endpoint"] = inner_ext.get("valueUri")
                        elif inner_ext.get("url") == "introspect":
                            endpoints["introspection_endpoint"] = inner_ext.get("valueUri")
                        elif inner_ext.get("url") == "revoke":
                            endpoints["revocation_endpoint"] = inner_ext.get("valueUri")
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Failed to discover auth endpoints: {e}")
            return {}
    
    def authenticate_client_credentials(self) -> bool:
        """
        Authenticate using OAuth2 client credentials flow.
        
        Returns:
            True if authentication successful
        """
        if not self.config.token_url or not self.config.client_id:
            logger.error("Missing authentication configuration")
            return False
        
        try:
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "scope": self.config.scope
            }
            
            if self.config.client_secret:
                payload["client_secret"] = self.config.client_secret
            
            response = self.session.post(
                self.config.token_url,
                data=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            
            logger.info("Successfully authenticated with client credentials flow")
            return True
            
        except Exception as e:
            logger.error(f"Client credentials authentication failed: {e}")
            return False
    
    def get_access_token(self) -> Optional[str]:
        """
        Get valid access token, refreshing if necessary.
        
        Returns:
            Valid access token or None
        """
        if not self.access_token:
            if not self.authenticate_client_credentials():
                return None
        
        # Check if token is expired or about to expire
        if self.token_expiry and datetime.utcnow() >= self.token_expiry - timedelta(minutes=5):
            logger.info("Access token expired or expiring soon, refreshing...")
            if not self.authenticate_client_credentials():
                return None
        
        return self.access_token
    
    def add_auth_header(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Add authorization header to request.
        
        Args:
            headers: Existing headers dictionary
            
        Returns:
            Headers with authorization added
        """
        token = self.get_access_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers


class FHIRServerClient:
    """
    Client for interacting with FHIR servers.
    
    Supports CRUD operations, search, and bulk export.
    """
    
    def __init__(self, config: FHIRConfig):
        """
        Initialize FHIR server client.
        
        Args:
            config: FHIR server configuration
        """
        self.config = config
        self.auth = SMARTonFHIRAuth(config) if config.auth_type == "smart" else None
        self.session = self._create_session()
        self.base_url = config.server_base_url.rstrip('/')
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic."""
        session = requests.Session()
        from requests.adapters import HTTPAdapter
        adapter = HTTPAdapter(
            max_retries=self.config.max_retries,
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers.update({
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        })
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication if configured."""
        headers = dict(self.session.headers)
        if self.auth:
            headers = self.auth.add_auth_header(headers)
        return headers
    
    def create_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a FHIR resource on the server.
        
        Args:
            resource: FHIR resource to create
            
        Returns:
            Server response
        """
        resource_type = resource.get("resourceType")
        if not resource_type:
            raise ValueError("Resource must have a resourceType")
        
        url = f"{self.base_url}/{resource_type}"
        
        try:
            response = self.session.post(
                url,
                json=resource,
                headers=self._get_headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            logger.info(f"Created {resource_type} resource")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to create resource: {e.response.text}")
            raise
    
    def read_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """
        Read a FHIR resource from the server.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource ID
            
        Returns:
            FHIR resource
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to read resource: {e.response.text}")
            raise
    
    def update_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a FHIR resource on the server.
        
        Args:
            resource: FHIR resource to update
            
        Returns:
            Server response
        """
        resource_type = resource.get("resourceType")
        resource_id = resource.get("id")
        
        if not resource_type or not resource_id:
            raise ValueError("Resource must have resourceType and id")
        
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        
        try:
            response = self.session.put(
                url,
                json=resource,
                headers=self._get_headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            logger.info(f"Updated {resource_type}/{resource_id}")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to update resource: {e.response.text}")
            raise
    
    def search_resources(
        self, 
        resource_type: str, 
        params: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Search for FHIR resources.
        
        Args:
            resource_type: Type of resource to search
            params: Search parameters
            
        Returns:
            Search results bundle
        """
        url = f"{self.base_url}/{resource_type}"
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Search failed: {e.response.text}")
            raise
    
    def transaction(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a FHIR transaction bundle.
        
        Args:
            bundle: Transaction bundle
            
        Returns:
            Transaction response
        """
        url = f"{self.base_url}"
        
        try:
            response = self.session.post(
                url,
                json=bundle,
                headers=self._get_headers(),
                timeout=self.config.timeout * 3,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            logger.info(f"Executed transaction with {len(bundle.get('entry', []))} entries")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Transaction failed: {e.response.text}")
            raise
    
    def initiate_bulk_export(
        self, 
        resource_types: Optional[list] = None,
        since: Optional[str] = None,
        type_filter: Optional[str] = None
    ) -> str:
        """
        Initiate FHIR bulk data export.
        
        Args:
            resource_types: List of resource types to export
            since: Export resources modified since this date
            type_filter: Additional filters
            
        Returns:
            Export status URL
        """
        url = f"{self.base_url}/$export"
        
        params = {}
        if resource_types:
            params["_type"] = ",".join(resource_types)
        if since:
            params["_since"] = since
        if type_filter:
            params["_typeFilter"] = type_filter
        
        headers = self._get_headers()
        headers["Prefer"] = "respond-async"
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            status_url = response.headers.get("Content-Location")
            if not status_url:
                raise ValueError("No Content-Location header in export response")
            
            logger.info(f"Bulk export initiated: {status_url}")
            return status_url
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Bulk export initiation failed: {e.response.text}")
            raise
    
    def check_bulk_export_status(self, status_url: str) -> Dict[str, Any]:
        """
        Check bulk export status.
        
        Args:
            status_url: Export status URL
            
        Returns:
            Status information
        """
        try:
            response = self.session.get(
                status_url,
                headers=self._get_headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Status check failed: {e.response.text}")
            raise


if __name__ == "__main__":
    # Example usage
    config = FHIRConfig(
        server_base_url="https://hapi.fhir.org/baseR4",
        auth_type="none",
        timeout=60
    )
    
    client = FHIRServerClient(config)
    
    # Create sample location
    location = {
        "resourceType": "Location",
        "id": "test-location-001",
        "status": "active",
        "name": "Test County",
        "mode": "instance",
        "address": {
            "country": "USA",
            "state": "Missouri"
        }
    }
    
    try:
        result = client.create_resource(location)
        print(f"Created resource: {result.get('id')}")
        
        read_result = client.read_resource("Location", result.get("id"))
        print(f"Read resource: {read_result.get('name')}")
        
    except Exception as e:
        print(f"Error: {e}")
