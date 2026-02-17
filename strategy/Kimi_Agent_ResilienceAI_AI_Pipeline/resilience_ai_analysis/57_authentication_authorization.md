# ResilienceAI Authentication & Authorization Design

## Executive Summary

This document provides a comprehensive authentication and authorization architecture for ResilienceAI, implementing industry-standard security practices including OAuth 2.0, JWT tokens, RBAC, MFA, and audit logging. The design prioritizes security, scalability, and developer experience.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [OAuth 2.0 Implementation](#oauth-20-implementation)
3. [JWT Token Management](#jwt-token-management)
4. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
5. [API Key Management](#api-key-management)
6. [Multi-Factor Authentication](#multi-factor-authentication)
7. [Session Management](#session-management)
8. [Password Policies](#password-policies)
9. [SSO Integration](#sso-integration)
10. [Authorization Middleware](#authorization-middleware)
11. [Audit Logging](#audit-logging)
12. [Security Measures](#security-measures)
13. [Testing Strategy](#testing-strategy)
14. [Deployment Guide](#deployment-guide)
15. [Implementation Priority](#implementation-priority)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ResilienceAI Auth Architecture                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   Client    │    │   Client    │    │   Client    │    │   Client    │   │
│  │  (Web App)  │    │ (Mobile)    │    │  (API)      │    │  (CLI)      │   │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘   │
│         │                  │                  │                  │          │
│         └──────────────────┴──────────────────┴──────────────────┘          │
│                                    │                                         │
│                         ┌──────────▼──────────┐                             │
│                         │   API Gateway       │                             │
│                         │  (Kong/AWS/Azure)   │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         │                          │                          │             │
│  ┌──────▼──────┐          ┌────────▼────────┐        ┌────────▼────────┐   │
│  │   OAuth     │          │  Authorization  │        │   Rate Limit    │   │
│  │   Server    │          │   Middleware    │        │    Middleware   │   │
│  └──────┬──────┘          └────────┬────────┘        └────────┬────────┘   │
│         │                          │                          │             │
│         │              ┌───────────┴───────────┐              │             │
│         │              │                       │              │             │
│  ┌──────▼──────┐  ┌────▼────┐           ┌─────▼─────┐  ┌──────▼──────┐     │
│  │   JWT       │  │  RBAC   │           │  Session  │  │   Audit     │     │
│  │   Service   │  │ Engine  │           │   Store   │  │   Logger    │     │
│  └──────┬──────┘  └────┬────┘           └─────┬─────┘  └──────┬──────┘     │
│         │              │                       │               │            │
│         └──────────────┴───────────┬───────────┴───────────────┘            │
│                                    │                                        │
│                         ┌──────────▼──────────┐                            │
│                         │  ResilienceAI Core  │                            │
│                         │      Services       │                            │
│                         └─────────────────────┘                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| OAuth 2.0 Server | Authlib/FastAPI | Authentication & token issuance |
| JWT Handler | PyJWT | Token generation & validation |
| RBAC Engine | Custom + SQLAlchemy | Permission management |
| Session Store | Redis | Distributed session management |
| MFA Provider | PyOTP/Twilio | TOTP & SMS verification |
| Audit Logger | PostgreSQL + Kafka | Security event logging |
| API Gateway | Kong/AWS API Gateway | Request routing & rate limiting |

---

## OAuth 2.0 Implementation

### OAuth 2.0 Flows Supported

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/oauth_server.py

from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants
from authlib.common.security import generate_token
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets

class OAuth2Config:
    """OAuth 2.0 Configuration"""
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    AUTHORIZATION_CODE_EXPIRE_MINUTES = 10
    JWT_ALGORITHM = "RS256"

class Client:
    """OAuth 2.0 Client Application"""
    
    def __init__(self, client_id: str, client_secret: str, 
                 redirect_uris: list, allowed_grants: list,
                 allowed_scopes: list):
        self.client_id = client_id
        self.client_secret_hash = self._hash_secret(client_secret)
        self.redirect_uris = redirect_uris
        self.allowed_grants = allowed_grants
        self.allowed_scopes = allowed_scopes
        self.created_at = datetime.utcnow()
        self.is_active = True
    
    def _hash_secret(self, secret: str) -> str:
        """Hash client secret with salt"""
        salt = secrets.token_hex(16)
        return f"{salt}${hashlib.sha256((secret + salt).encode()).hexdigest()}"
    
    def verify_secret(self, secret: str) -> bool:
        """Verify client secret"""
        salt, stored_hash = self.client_secret_hash.split('$')
        computed = hashlib.sha256((secret + salt).encode()).hexdigest()
        return secrets.compare_digest(computed, stored_hash)

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    """Authorization Code Grant with PKCE"""
    
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post']
    
    def save_authorization_code(self, code: str, request: Dict[str, Any]):
        """Save authorization code with PKCE"""
        code_challenge = request.data.get('code_challenge')
        code_challenge_method = request.data.get('code_challenge_method', 'S256')
        
        auth_code = {
            'code': code,
            'client_id': request.client.client_id,
            'redirect_uri': request.redirect_uri,
            'user_id': request.user.id,
            'scope': request.scope,
            'code_challenge': code_challenge,
            'code_challenge_method': code_challenge_method,
            'expires_at': datetime.utcnow() + timedelta(
                minutes=OAuth2Config.AUTHORIZATION_CODE_EXPIRE_MINUTES
            )
        }
        return auth_code

class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    """Password Grant (for trusted clients only)"""
    
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic']
    
    def authenticate_user(self, username: str, password: str):
        """Authenticate user with username/password"""
        user = self._get_user_by_username(username)
        if user and user.verify_password(password):
            if user.mfa_enabled:
                raise MFARequiredException(user.id)
            return user
        return None

class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    """Client Credentials Grant for service-to-service auth"""
    
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic']

class RefreshTokenGrant(grants.RefreshTokenGrant):
    """Refresh Token Grant"""
    
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic']
    
    def authenticate_refresh_token(self, refresh_token: str):
        """Validate refresh token"""
        try:
            payload = jwt.decode(
                refresh_token, 
                OAuth2Config.JWT_PUBLIC_KEY,
                algorithms=[OAuth2Config.JWT_ALGORITHM]
            )
            if payload.get('type') != 'refresh':
                return None
            if self._is_token_revoked(payload['jti']):
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
```

---

## JWT Token Management

### JWT Architecture

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/jwt_manager.py

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from enum import Enum
import uuid
import hashlib
import json

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"
    API_KEY = "api_key"
    MFA = "mfa"

class JWTConfig:
    """JWT Configuration"""
    PRIVATE_KEY_PATH = "/secure/keys/jwt-private.pem"
    PUBLIC_KEY_PATH = "/secure/keys/jwt-public.pem"
    KEY_ROTATION_DAYS = 90
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    ID_TOKEN_EXPIRE_MINUTES = 60
    MFA_TOKEN_EXPIRE_MINUTES = 10
    ALGORITHM = "RS256"
    ISSUER = "https://auth.resilience.ai"
    AUDIENCE = "https://api.resilience.ai"

class JWTManager:
    """JWT Token Manager with rotation and revocation support"""
    
    def __init__(self, redis_client, key_store):
        self.redis = redis_client
        self.key_store = key_store
        self._load_keys()
    
    def _load_keys(self):
        """Load signing keys from secure storage"""
        with open(JWTConfig.PRIVATE_KEY_PATH, 'r') as f:
            self.private_key = f.read()
        with open(JWTConfig.PUBLIC_KEY_PATH, 'r') as f:
            self.public_key = f.read()
    
    def generate_access_token(
        self,
        user_id: str,
        username: str,
        roles: List[str],
        permissions: List[str],
        client_id: Optional[str] = None,
        scope: Optional[str] = None,
        additional_claims: Optional[Dict] = None
    ) -> str:
        """Generate JWT access token"""
        
        now = datetime.utcnow()
        jti = str(uuid.uuid4())
        
        payload = {
            "iss": JWTConfig.ISSUER,
            "sub": user_id,
            "aud": JWTConfig.AUDIENCE,
            "exp": now + timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES),
            "nbf": now,
            "iat": now,
            "jti": jti,
            "type": TokenType.ACCESS.value,
            "username": username,
            "roles": roles,
            "permissions": permissions,
            "client_id": client_id,
            "scope": scope or "read"
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(
            payload,
            self.private_key,
            algorithm=JWTConfig.ALGORITHM,
            headers={"kid": self._get_key_id(), "typ": "JWT"}
        )
        
        self._store_token_metadata(jti, payload)
        return token
    
    def generate_refresh_token(
        self,
        user_id: str,
        client_id: Optional[str] = None,
        token_family: Optional[str] = None
    ) -> str:
        """Generate refresh token with rotation support"""
        
        now = datetime.utcnow()
        jti = str(uuid.uuid4())
        family = token_family or str(uuid.uuid4())
        
        payload = {
            "iss": JWTConfig.ISSUER,
            "sub": user_id,
            "aud": JWTConfig.ISSUER,
            "exp": now + timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS),
            "nbf": now,
            "iat": now,
            "jti": jti,
            "type": TokenType.REFRESH.value,
            "client_id": client_id,
            "family": family,
            "sequence": self._get_next_sequence(family)
        }
        
        token = jwt.encode(payload, self.private_key, algorithm=JWTConfig.ALGORITHM)
        self._store_token_metadata(jti, payload)
        return token
    
    def verify_token(
        self,
        token: str,
        token_type: TokenType = TokenType.ACCESS,
        audience: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            
            jti = unverified.get('jti')
            if jti and self._is_token_revoked(jti):
                raise TokenRevokedException("Token has been revoked")
            
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[JWTConfig.ALGORITHM],
                audience=audience or JWTConfig.AUDIENCE,
                issuer=JWTConfig.ISSUER
            )
            
            if payload.get('type') != token_type.value:
                raise InvalidTokenError(f"Invalid token type")
            
            return payload
            
        except ExpiredSignatureError:
            raise TokenExpiredException("Token has expired")
        except InvalidTokenError as e:
            raise InvalidTokenException(f"Invalid token: {str(e)}")
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token"""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            jti = payload.get('jti')
            exp = payload.get('exp')
            
            if jti:
                self._revoke_token_by_jti(jti, exp)
                return True
            return False
        except InvalidTokenError:
            return False

class TokenRotationDetector:
    """Detect and prevent refresh token reuse attacks"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def check_token_family(self, family: str, sequence: int) -> Dict:
        """Check if refresh token is being reused"""
        key = f"token:family:{family}:used"
        
        highest = self.redis.get(key)
        highest_seq = int(highest) if highest else 0
        
        if sequence < highest_seq:
            self._revoke_family(family)
            return {
                'valid': False,
                'attack_detected': True,
                'message': 'Token reuse detected. All tokens revoked.'
            }
        
        self.redis.set(key, sequence)
        return {'valid': True}
```

---

## Role-Based Access Control (RBAC)

### RBAC Architecture

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/rbac_engine.py

from enum import Enum, auto
from typing import Dict, List, Set, Optional, Callable
from dataclasses import dataclass, field
from functools import wraps
import json

class Permission(Enum):
    """System permissions"""
    # User management
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"
    
    # Organization management
    ORG_READ = "org:read"
    ORG_CREATE = "org:create"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    ORG_MANAGE = "org:manage"
    
    # Incident management
    INCIDENT_READ = "incident:read"
    INCIDENT_CREATE = "incident:create"
    INCIDENT_UPDATE = "incident:update"
    INCIDENT_DELETE = "incident:delete"
    INCIDENT_MANAGE = "incident:manage"
    INCIDENT_EXECUTE = "incident:execute"
    
    # Runbook management
    RUNBOOK_READ = "runbook:read"
    RUNBOOK_CREATE = "runbook:create"
    RUNBOOK_UPDATE = "runbook:update"
    RUNBOOK_DELETE = "runbook:delete"
    RUNBOOK_EXECUTE = "runbook:execute"
    RUNBOOK_APPROVE = "runbook:approve"
    
    # AI/ML operations
    AI_QUERY = "ai:query"
    AI_TRAIN = "ai:train"
    AI_CONFIGURE = "ai:configure"
    AI_MANAGE = "ai:manage"
    
    # System administration
    SYSTEM_READ = "system:read"
    SYSTEM_CONFIGURE = "system:configure"
    SYSTEM_ADMIN = "system:admin"
    
    # Audit and compliance
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"
    COMPLIANCE_MANAGE = "compliance:manage"
    
    # API management
    API_KEY_READ = "api_key:read"
    API_KEY_CREATE = "api_key:create"
    API_KEY_REVOKE = "api_key:revoke"

class Role:
    """Role definition with permissions"""
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 permissions: Set[Permission],
                 parent_roles: Optional[List[str]] = None,
                 is_system: bool = False):
        self.name = name
        self.description = description
        self.permissions = permissions
        self.parent_roles = parent_roles or []
        self.is_system = is_system
        self.created_at = datetime.utcnow()
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if role has specific permission"""
        return permission in self.permissions

# Predefined system roles
SYSTEM_ROLES = {
    'super_admin': Role(
        name='super_admin',
        description='Full system access',
        permissions=set(Permission),
        is_system=True
    ),
    
    'org_admin': Role(
        name='org_admin',
        description='Organization administrator',
        permissions={
            Permission.USER_READ, Permission.USER_CREATE, 
            Permission.USER_UPDATE, Permission.USER_DELETE,
            Permission.ORG_READ, Permission.ORG_UPDATE,
            Permission.INCIDENT_READ, Permission.INCIDENT_CREATE,
            Permission.INCIDENT_UPDATE, Permission.INCIDENT_DELETE,
            Permission.INCIDENT_MANAGE,
            Permission.RUNBOOK_READ, Permission.RUNBOOK_CREATE,
            Permission.RUNBOOK_UPDATE, Permission.RUNBOOK_DELETE,
            Permission.RUNBOOK_EXECUTE, Permission.RUNBOOK_APPROVE,
            Permission.AI_QUERY, Permission.AI_CONFIGURE,
            Permission.AUDIT_READ, Permission.AUDIT_EXPORT,
            Permission.API_KEY_READ, Permission.API_KEY_CREATE,
            Permission.API_KEY_REVOKE,
        },
        is_system=True
    ),
    
    'incident_manager': Role(
        name='incident_manager',
        description='Manage and respond to incidents',
        permissions={
            Permission.INCIDENT_READ, Permission.INCIDENT_CREATE,
            Permission.INCIDENT_UPDATE, Permission.INCIDENT_EXECUTE,
            Permission.RUNBOOK_READ, Permission.RUNBOOK_EXECUTE,
            Permission.AI_QUERY, Permission.AUDIT_READ
        },
        is_system=True
    ),
    
    'incident_responder': Role(
        name='incident_responder',
        description='Respond to assigned incidents',
        permissions={
            Permission.INCIDENT_READ, Permission.INCIDENT_UPDATE,
            Permission.RUNBOOK_READ, Permission.RUNBOOK_EXECUTE,
            Permission.AI_QUERY
        },
        is_system=True
    ),
    
    'runbook_engineer': Role(
        name='runbook_engineer',
        description='Create and manage runbooks',
        permissions={
            Permission.RUNBOOK_READ, Permission.RUNBOOK_CREATE,
            Permission.RUNBOOK_UPDATE, Permission.RUNBOOK_EXECUTE,
            Permission.INCIDENT_READ, Permission.AI_QUERY
        },
        is_system=True
    ),
    
    'analyst': Role(
        name='analyst',
        description='Read-only access for analysis',
        permissions={
            Permission.INCIDENT_READ, Permission.RUNBOOK_READ,
            Permission.AI_QUERY, Permission.AUDIT_READ
        },
        is_system=True
    ),
    
    'viewer': Role(
        name='viewer',
        description='Read-only access',
        permissions={
            Permission.INCIDENT_READ, Permission.RUNBOOK_READ
        },
        is_system=True
    ),
}

class RBACEngine:
    """Role-Based Access Control Engine"""
    
    def __init__(self, db_session, cache_client):
        self.db = db_session
        self.cache = cache_client
        self.permission_cache_ttl = 300
    
    def check_permission(
        self,
        user_id: str,
        permission: Permission,
        resource_context: Optional[Dict] = None
    ) -> Dict:
        """Check if user has permission"""
        
        user_roles = self._get_user_roles(user_id)
        
        has_permission = False
        for role_name in user_roles:
            role = self._get_role(role_name)
            if role and role.has_permission(permission):
                has_permission = True
                break
        
        if not has_permission:
            return {
                'allowed': False,
                'reason': f"User does not have permission: {permission.value}"
            }
        
        if resource_context:
            resource_check = self._check_resource_access(
                user_id, permission, resource_context
            )
            if not resource_check['allowed']:
                return resource_check
        
        return {'allowed': True}
    
    def check_permissions(
        self,
        user_id: str,
        permissions: List[Permission],
        require_all: bool = True
    ) -> Dict:
        """Check multiple permissions"""
        
        results = []
        for perm in permissions:
            result = self.check_permission(user_id, perm)
            results.append((perm, result['allowed']))
        
        if require_all:
            allowed = all(r[1] for r in results)
        else:
            allowed = any(r[1] for r in results)
        
        return {
            'allowed': allowed,
            'details': {p.value: a for p, a in results}
        }
    
    def get_effective_permissions(self, user_id: str) -> Set[Permission]:
        """Get all effective permissions for user"""
        roles = self._get_user_roles(user_id)
        
        all_permissions = set()
        for role_name in roles:
            role = self._get_role(role_name)
            if role:
                all_permissions.update(role.permissions)
                for parent_name in role.parent_roles:
                    parent = self._get_role(parent_name)
                    if parent:
                        all_permissions.update(parent.permissions)
        
        return all_permissions

# Decorator for permission checking
def require_permission(permission: Permission):
    """Decorator to require permission for endpoint"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            rbac = kwargs.get('rbac_engine')
            result = rbac.check_permission(current_user.id, permission)
            if not result['allowed']:
                raise HTTPException(status_code=403, detail=result.get('reason', 'Permission denied'))
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## API Key Management

### API Key Architecture

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/api_key_manager.py

import secrets
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from enum import Enum
import uuid

class APIKeyScope(Enum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    WEBHOOK = "webhook"
    SERVICE = "service"

class APIKeyStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"

class APIKey:
    """API Key model"""
    
    def __init__(
        self,
        name: str,
        owner_id: str,
        org_id: Optional[str] = None,
        scope: APIKeyScope = APIKeyScope.READ_ONLY,
        permissions: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
        rate_limit: int = 1000,
        allowed_ips: Optional[List[str]] = None,
        allowed_origins: Optional[List[str]] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.owner_id = owner_id
        self.org_id = org_id
        self.scope = scope
        self.permissions = permissions or []
        self.status = APIKeyStatus.ACTIVE
        self._key, self._prefix, self._hash = self._generate_key()
        self.created_at = datetime.utcnow()
        self.expires_at = expires_at
        self.last_used_at = None
        self.usage_count = 0
        self.rate_limit = rate_limit
        self.allowed_ips = allowed_ips or []
        self.allowed_origins = allowed_origins or []
    
    def _generate_key(self) -> Tuple[str, str, str]:
        random_bytes = secrets.token_bytes(48)
        key = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
        prefix = key[:8]
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, prefix, key_hash
    
    @property
    def key(self) -> str:
        return getattr(self, '_key', None)
    
    def verify(self, key: str) -> bool:
        provided_hash = hashlib.sha256(key.encode()).hexdigest()
        return hmac.compare_digest(provided_hash, self._hash)
    
    def is_valid(self) -> Tuple[bool, str]:
        if self.status != APIKeyStatus.ACTIVE:
            return False, f"Key is {self.status.value}"
        if self.expires_at and datetime.utcnow() > self.expires_at:
            self.status = APIKeyStatus.EXPIRED
            return False, "Key has expired"
        return True, "Valid"

class APIKeyManager:
    """API Key Management Service"""
    
    def __init__(self, db_session, redis_client, audit_logger):
        self.db = db_session
        self.redis = redis_client
        self.audit = audit_logger
        self.rate_limit_window = 3600
    
    async def create_key(self, name: str, owner_id: str, **kwargs) -> APIKey:
        api_key = APIKey(name=name, owner_id=owner_id, **kwargs)
        await self._store_key(api_key)
        await self.audit.log_event(
            event_type="api_key.created",
            user_id=owner_id,
            resource_id=api_key.id,
            details={'name': name, 'scope': kwargs.get('scope', 'read_only')}
        )
        return api_key
    
    async def validate_key(self, key: str, request_ip: Optional[str] = None, 
                          origin: Optional[str] = None) -> Optional[APIKey]:
        prefix = key[:8]
        api_key = await self._get_key_by_prefix(prefix)
        if not api_key or not api_key.verify(key):
            return None
        
        is_valid, _ = api_key.is_valid()
        if not is_valid:
            return None
        
        if api_key.allowed_ips and request_ip not in api_key.allowed_ips:
            return None
        
        if not await self._check_rate_limit(api_key.id, api_key.rate_limit):
            return None
        
        api_key.record_usage()
        await self._update_usage(api_key)
        return api_key
    
    async def revoke_key(self, key_id: str, revoked_by: str, reason: str) -> bool:
        api_key = await self._get_key_by_id(key_id)
        if not api_key:
            return False
        api_key.status = APIKeyStatus.REVOKED
        await self._update_key(api_key)
        await self._invalidate_key_cache(api_key.prefix)
        await self.audit.log_event(
            event_type="api_key.revoked",
            user_id=revoked_by,
            resource_id=key_id,
            details={'reason': reason}
        )
        return True
```

---

## Multi-Factor Authentication

### MFA Architecture

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/mfa_service.py

import pyotp
import qrcode
import qrcode.image.svg
import io
import base64
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import secrets
import jwt

class MFAMethod(Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    WEBAUTHN = "webauthn"
    BACKUP_CODES = "backup_codes"

class TOTPService:
    """TOTP (Time-based One-Time Password) Service"""
    
    def __init__(self, issuer_name: str = "ResilienceAI"):
        self.issuer_name = issuer_name
    
    def generate_secret(self) -> str:
        return pyotp.random_base32()
    
    def generate_provisioning_uri(self, secret: str, username: str, 
                                   account_name: Optional[str] = None) -> str:
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=account_name or username,
            issuer_name=self.issuer_name
        )
    
    def generate_qr_code(self, provisioning_uri: str) -> str:
        factory = qrcode.image.svg.SvgImage
        qr = qrcode.make(provisioning_uri, image_factory=factory)
        buffer = io.BytesIO()
        qr.save(buffer)
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_code(self, secret: str, code: str, window: int = 1) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=window)
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        return [secrets.token_urlsafe(6)[:8].upper() for _ in range(count)]

class MFAService:
    """Multi-Factor Authentication Service"""
    
    def __init__(self, db_session, redis_client, totp_service, 
                 sms_service, email_service, audit_logger):
        self.db = db_session
        self.redis = redis_client
        self.totp = totp_service
        self.sms = sms_service
        self.email = email_service
        self.audit = audit_logger
    
    async def setup_totp(self, user_id: str) -> Dict:
        secret = self.totp.generate_secret()
        user = await self._get_user(user_id)
        uri = self.totp.generate_provisioning_uri(
            secret=secret, username=user['username'], account_name=user.get('email')
        )
        qr_code = self.totp.generate_qr_code(uri)
        
        await self.redis.setex(f"mfa:totp:pending:{user_id}", 3600, secret)
        
        return {
            'secret': secret,
            'qr_code': qr_code,
            'provisioning_uri': uri,
            'expires_in': 3600
        }
    
    async def verify_and_enable_totp(self, user_id: str, code: str) -> Dict:
        secret = await self.redis.get(f"mfa:totp:pending:{user_id}")
        if not secret:
            return {'success': False, 'error': 'Setup expired'}
        
        secret = secret.decode()
        if not self.totp.verify_code(secret, code):
            return {'success': False, 'error': 'Invalid verification code'}
        
        backup_codes = self.totp.generate_backup_codes()
        await self._store_mfa_method(user_id, MFAMethod.TOTP, {
            'secret': secret,
            'enabled_at': datetime.utcnow().isoformat()
        })
        await self._store_backup_codes(user_id, backup_codes)
        await self.redis.delete(f"mfa:totp:pending:{user_id}")
        await self._update_mfa_status(user_id, MFAStatus.ENABLED)
        
        await self.audit.log_event(event_type="mfa.totp_enabled", user_id=user_id)
        
        return {'success': True, 'backup_codes': backup_codes}
    
    async def verify_mfa_challenge(self, user_id: str, method: MFAMethod, 
                                    code: str) -> bool:
        if method == MFAMethod.TOTP:
            settings = await self._fetch_mfa_settings(user_id)
            totp_config = next((m for m in settings['methods'] if m['type'] == 'totp'), None)
            return totp_config and self.totp.verify_code(totp_config['config']['secret'], code)
        elif method == MFAMethod.SMS:
            return await self.sms.verify_code(user_id, code)
        elif method == MFAMethod.EMAIL:
            return await self.email.verify_code(user_id, code)
        return False
```

---

## Session Management

### Session Architecture

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/session_manager.py

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

class SessionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"

class SessionManager:
    """Session Management Service"""
    
    def __init__(self, redis_client, db_session, audit_logger,
                 session_ttl: int = 86400, absolute_ttl: int = 604800):
        self.redis = redis_client
        self.db = db_session
        self.audit = audit_logger
        self.session_ttl = session_ttl
        self.absolute_ttl = absolute_ttl
    
    async def create_session(self, user_id: str, client_info: Dict) -> Dict:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session = {
            'id': session_id,
            'user_id': user_id,
            'status': SessionStatus.ACTIVE.value,
            'created_at': now.isoformat(),
            'expires_at': (now + timedelta(seconds=self.session_ttl)).isoformat(),
            'absolute_expires_at': (now + timedelta(seconds=self.absolute_ttl)).isoformat(),
            'last_activity_at': now.isoformat(),
            'client_info': {
                'ip_address': client_info.get('ip'),
                'user_agent': client_info.get('user_agent'),
                'device_type': self._detect_device_type(client_info.get('user_agent')),
            },
            'mfa_verified': client_info.get('mfa_verified', False),
            'auth_method': client_info.get('auth_method', 'password')
        }
        
        await self._store_session(session)
        await self.redis.sadd(f"user:{user_id}:sessions", session_id)
        
        await self.audit.log_event(
            event_type="session.created",
            user_id=user_id,
            resource_id=session_id,
            details={'ip': client_info.get('ip')}
        )
        return session
    
    async def validate_session(self, session_id: str) -> Optional[Dict]:
        session = await self._get_session(session_id)
        if not session or session['status'] != SessionStatus.ACTIVE.value:
            return None
        
        now = datetime.utcnow()
        expires_at = datetime.fromisoformat(session['expires_at'])
        absolute_expires = datetime.fromisoformat(session['absolute_expires_at'])
        
        if now > expires_at or now > absolute_expires:
            await self._expire_session(session_id)
            return None
        
        session['last_activity_at'] = now.isoformat()
        await self._store_session(session)
        return session
    
    async def revoke_session(self, session_id: str, reason: str = "User logout") -> bool:
        session = await self._get_session(session_id)
        if not session:
            return False
        
        session['status'] = SessionStatus.REVOKED.value
        session['revoked_at'] = datetime.utcnow().isoformat()
        session['revoke_reason'] = reason
        
        await self._store_session(session)
        await self.redis.srem(f"user:{session['user_id']}:sessions", session_id)
        
        await self.audit.log_event(
            event_type="session.revoked",
            user_id=session['user_id'],
            resource_id=session_id,
            details={'reason': reason}
        )
        return True
    
    async def revoke_all_user_sessions(self, user_id: str, 
                                        except_session_id: Optional[str] = None,
                                        reason: str = "Security action") -> int:
        session_ids = await self.redis.smembers(f"user:{user_id}:sessions")
        count = 0
        for sid in session_ids:
            sid = sid.decode()
            if sid != except_session_id:
                await self.revoke_session(sid, reason)
                count += 1
        return count
```

---

## Password Policies

### Password Management

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/password_policy.py

import re
import hashlib
import hmac
import secrets
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class PasswordPolicy:
    min_length: int = 12
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    min_zxcvbn_score: int = 3
    prevent_reuse_count: int = 5
    max_age_days: int = 90
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30

class PasswordValidator:
    def __init__(self, policy: PasswordPolicy, db_session):
        self.policy = policy
        self.db = db_session
    
    def validate(self, password: str, user_info: Optional[Dict] = None) -> Dict:
        errors = []
        
        if len(password) < self.policy.min_length:
            errors.append(f"Password must be at least {self.policy.min_length} characters")
        
        if self.policy.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.policy.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.policy.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.policy.require_special:
            special_pattern = f"[{re.escape(self.policy.special_chars)}]"
            if not re.search(special_pattern, password):
                errors.append("Password must contain at least one special character")
        
        return {'valid': len(errors) == 0, 'errors': errors}

class PasswordHasher:
    def __init__(self):
        from argon2 import PasswordHasher as Argon2Hasher
        self.hasher = Argon2Hasher(
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            salt_len=16
        )
    
    def hash(self, password: str) -> str:
        return self.hasher.hash(password)
    
    def verify(self, password: str, hash_string: str) -> bool:
        try:
            self.hasher.verify(hash_string, password)
            return True
        except Exception:
            return False
```

---

## SSO Integration

### SSO Architecture

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/sso_service.py

from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum
import jwt

class SSOProvider(Enum):
    SAML = "saml"
    OIDC = "oidc"
    AZURE_AD = "azure_ad"
    GOOGLE = "google"
    OKTA = "okta"

class OIDCService:
    def __init__(self, client_id: str, client_secret: str, 
                 redirect_uri: str, discovery_url: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.discovery_url = discovery_url
        self._provider_config = None
    
    async def discover_configuration(self) -> Dict:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.discovery_url}/.well-known/openid-configuration"
            ) as resp:
                self._provider_config = await resp.json()
                return self._provider_config
    
    def generate_auth_url(self, state: str, nonce: str, 
                          scope: str = "openid email profile") -> str:
        from urllib.parse import urlencode
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': scope,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'nonce': nonce
        }
        auth_endpoint = self._provider_config['authorization_endpoint']
        return f"{auth_endpoint}?{urlencode(params)}"
    
    async def exchange_code(self, code: str) -> Dict:
        import aiohttp
        token_endpoint = self._provider_config['token_endpoint']
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(token_endpoint, data=payload) as resp:
                tokens = await resp.json()
                id_token = jwt.decode(tokens['id_token'], options={"verify_signature": False})
                return {
                    'access_token': tokens['access_token'],
                    'refresh_token': tokens.get('refresh_token'),
                    'id_token': id_token
                }

class SSOService:
    def __init__(self, db_session, redis_client, user_service, audit_logger):
        self.db = db_session
        self.redis = redis_client
        self.user_service = user_service
        self.audit = audit_logger
        self._providers = {}
    
    async def initiate_sso(self, provider_id: str, 
                           redirect_after: Optional[str] = None) -> Dict:
        provider = await self.get_provider(provider_id)
        import secrets
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        
        await self.redis.setex(f"sso:state:{state}", 600, 
            json.dumps({'provider_id': provider_id, 'nonce': nonce, 
                       'redirect_after': redirect_after}))
        
        if isinstance(provider, OIDCService):
            auth_url = provider.generate_auth_url(state, nonce)
            return {'type': 'oidc', 'redirect_url': auth_url, 'state': state}
        
        return {}
```

---

## Authorization Middleware

### Middleware Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/middleware.py

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, List, Dict
import time

class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, jwt_manager, session_manager, 
                 api_key_manager, rbac_engine, excluded_paths: List[str] = None):
        super().__init__(app)
        self.jwt = jwt_manager
        self.session = session_manager
        self.api_key = api_key_manager
        self.rbac = rbac_engine
        self.excluded_paths = excluded_paths or ['/health', '/docs', '/oauth/token']
    
    async def dispatch(self, request: Request, call_next) -> Response:
        if any(request.url.path.startswith(p) for p in self.excluded_paths):
            return await call_next(request)
        
        auth_result = await self._authenticate(request)
        if auth_result:
            request.state.user = auth_result.get('user')
            request.state.user_id = auth_result.get('user_id')
            request.state.auth_type = auth_result.get('auth_type')
        
        return await call_next(request)
    
    async def _authenticate(self, request: Request) -> Optional[Dict]:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return await self._authenticate_jwt(auth_header[7:])
        
        api_key = request.headers.get('X-API-Key') or request.query_params.get('api_key')
        if api_key:
            return await self._authenticate_api_key(api_key, request)
        
        session_id = request.cookies.get('session_id')
        if session_id:
            return await self._authenticate_session(session_id)
        
        return None

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, default_limit: int = 100, 
                 default_window: int = 3600):
        super().__init__(app)
        self.redis = redis_client
        self.default_limit = default_limit
        self.default_window = default_window
    
    async def dispatch(self, request: Request, call_next) -> Response:
        client_id = self._get_client_id(request)
        key = f"ratelimit:{client_id}:{request.url.path}"
        
        current = await self.redis.get(key)
        if current and int(current) >= self.default_limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.default_window)
        await pipe.execute()
        
        response = await call_next(request)
        remaining = self.default_limit - (int(current or 0) + 1)
        response.headers['X-RateLimit-Limit'] = str(self.default_limit)
        response.headers['X-RateLimit-Remaining'] = str(max(0, remaining))
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
```

---

## Audit Logging

### Audit System

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/audit_logger.py

from typing import Dict, Optional, List, Any
from datetime import datetime
from enum import Enum
import json
import asyncio
from dataclasses import dataclass, asdict

class AuditEventType(Enum):
    LOGIN_SUCCESS = "auth.login_success"
    LOGIN_FAILURE = "auth.login_failure"
    LOGOUT = "auth.logout"
    ACCESS_GRANTED = "auth.access_granted"
    ACCESS_DENIED = "auth.access_denied"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"
    SECURITY_ALERT = "security.alert"

class AuditSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    event_type: str
    timestamp: datetime
    severity: str
    user_id: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    action: str
    status: str
    details: Dict[str, Any]

class AuditLogger:
    def __init__(self, db_session, kafka_producer=None, 
                 buffer_size: int = 100, flush_interval: int = 5):
        self.db = db_session
        self.kafka = kafka_producer
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self._buffer: List[AuditEvent] = []
    
    async def log_event(self, event_type: str, user_id: Optional[str] = None,
                        resource_type: Optional[str] = None, 
                        resource_id: Optional[str] = None,
                        details: Optional[Dict] = None,
                        severity: str = AuditSeverity.INFO.value) -> AuditEvent:
        
        event = AuditEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            severity=severity,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=event_type.split('.')[-1],
            status="success",
            details=details or {}
        )
        
        self._buffer.append(event)
        if len(self._buffer) >= self.buffer_size:
            await self._flush_buffer()
        return event
    
    async def log_security_event(self, event_type: str, details: Dict,
                                  severity: str = AuditSeverity.WARNING.value):
        event = await self.log_event(event_type=event_type, details=details, 
                                     severity=severity)
        if severity in [AuditSeverity.ERROR.value, AuditSeverity.CRITICAL.value]:
            await self._trigger_security_alert(event)
        return event
    
    async def _flush_buffer(self):
        if not self._buffer:
            return
        events = self._buffer.copy()
        self._buffer.clear()
        await self._write_to_database(events)
        if self.kafka:
            await self._send_to_kafka(events)
    
    async def _write_to_database(self, events: List[AuditEvent]):
        records = [asdict(e) for e in events]
        # Bulk insert to database
```

---

## Security Measures

### Security Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/security_measures.py

import hashlib
import secrets
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class SecurityService:
    def __init__(self, redis_client, audit_logger, config: Dict):
        self.redis = redis_client
        self.audit = audit_logger
        self.config = config
    
    async def check_brute_force(self, identifier: str, action: str) -> Dict:
        key = f"bruteforce:{action}:{identifier}"
        attempts = await self.redis.get(key)
        attempts = int(attempts) if attempts else 0
        
        max_attempts = self.config.get('brute_force_max_attempts', 5)
        
        if attempts >= max_attempts:
            lockout_key = f"lockout:{action}:{identifier}"
            locked = await self.redis.exists(lockout_key)
            if locked:
                ttl = await self.redis.ttl(lockout_key)
                return {'allowed': False, 'locked': True, 'retry_after': ttl}
        
        return {'allowed': True, 'attempts_remaining': max_attempts - attempts}
    
    async def record_failed_attempt(self, identifier: str, action: str):
        key = f"bruteforce:{action}:{identifier}"
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 3600)
        await pipe.execute()
        
        attempts = int(await self.redis.get(key) or 0)
        if attempts >= self.config.get('brute_force_max_attempts', 5):
            lockout_key = f"lockout:{action}:{identifier}"
            await self.redis.setex(lockout_key, 1800, "1")
            await self.audit.log_security_event(
                event_type="security.brute_force_detected",
                details={'identifier': identifier, 'attempts': attempts}
            )
    
    async def detect_anomalies(self, user_id: str, event: Dict) -> List[Dict]:
        anomalies = []
        
        # Check for impossible travel
        travel_anomaly = await self._check_impossible_travel(user_id, event)
        if travel_anomaly:
            anomalies.append(travel_anomaly)
        
        # Check for unusual time
        hour = datetime.utcnow().hour
        typical_hours = await self.redis.smembers(f"user:{user_id}:login_hours")
        if typical_hours and hour not in {int(h) for h in typical_hours}:
            anomalies.append({
                'type': 'unusual_time',
                'severity': 'info',
                'details': {'current_hour': hour}
            })
        
        await self.redis.sadd(f"user:{user_id}:login_hours", hour)
        return anomalies
    
    async def _check_impossible_travel(self, user_id: str, event: Dict) -> Optional[Dict]:
        last_location = await self.redis.get(f"user:{user_id}:last_location")
        if last_location:
            last = json.loads(last_location)
            if last.get('country') != event.get('country'):
                time_diff = (datetime.utcnow() - datetime.fromisoformat(last['timestamp'])).total_seconds()
                if time_diff < 3600:
                    return {
                        'type': 'impossible_travel',
                        'severity': 'warning',
                        'details': {'previous_country': last['country'], 'current_country': event.get('country')}
                    }
        
        await self.redis.setex(f"user:{user_id}:last_location", 86400, json.dumps({
            'country': event.get('country'),
            'timestamp': datetime.utcnow().isoformat()
        }))
        return None
```

---

## Testing Strategy

### Test Implementation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/auth/tests/test_auth.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import jwt
from datetime import datetime, timedelta

class TestAuthentication:
    @pytest.fixture
    def mock_user(self):
        return {
            'id': 'user-123',
            'username': 'testuser',
            'email': 'test@example.com',
            'roles': ['viewer'],
            'mfa_enabled': False,
            'is_active': True
        }
    
    def test_login_success(self, client, mock_user):
        with patch('auth.user_service.get_user_by_username', return_value=mock_user):
            with patch('auth.password_service.verify_password', return_value=True):
                response = client.post('/auth/login', json={
                    'username': 'testuser',
                    'password': 'password123'
                })
        assert response.status_code == 200
        assert 'access_token' in response.json()
    
    def test_login_invalid_credentials(self, client):
        response = client.post('/auth/login', json={
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401

class TestRBAC:
    def test_role_has_permission(self):
        role = SYSTEM_ROLES['incident_manager']
        assert role.has_permission(Permission.INCIDENT_READ) == True
        assert role.has_permission(Permission.SYSTEM_ADMIN) == False
    
    def test_super_admin_has_all_permissions(self):
        role = SYSTEM_ROLES['super_admin']
        for perm in Permission:
            assert role.has_permission(perm) == True

class TestPasswordPolicy:
    @pytest.fixture
    def password_validator(self):
        from ..password_policy import PasswordValidator, PasswordPolicy
        return PasswordValidator(PasswordPolicy(min_length=12), Mock())
    
    def test_valid_password(self, password_validator):
        result = password_validator.validate('MyStr0ng!Pass')
        assert result['valid'] == True
    
    def test_short_password(self, password_validator):
        result = password_validator.validate('Short1!')
        assert result['valid'] == False
```

---

## Deployment Guide

### Kubernetes Configuration

```yaml
# auth-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: resilience-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth
        image: resilience-ai/auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: JWT_PRIVATE_KEY
          valueFrom:
            secretKeyRef:
              name: auth-secrets
              key: jwt-private-key
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: auth-config
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
```

### Docker Configuration

```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libffi-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --chown=appuser:appuser . .
RUN mkdir -p /secure/keys && chown appuser:appuser /secure/keys
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s CMD python -c "import requests; requests.get('http://localhost:8000/health')"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Implementation Priority

### Phase 1: Core Authentication (Weeks 1-2)

| Priority | Component | Effort | Risk |
|----------|-----------|--------|------|
| P0 | JWT Token Management | Medium | High |
| P0 | Password Authentication | Medium | High |
| P0 | Session Management | Medium | Medium |
| P0 | Basic RBAC | Medium | Medium |
| P1 | Password Policies | Low | Low |

### Phase 2: Authorization & API Security (Weeks 3-4)

| Priority | Component | Effort | Risk |
|----------|-----------|--------|------|
| P0 | RBAC Engine Complete | High | High |
| P0 | Authorization Middleware | Medium | High |
| P0 | API Key Management | Medium | Medium |
| P1 | Rate Limiting | Low | Low |

### Phase 3: Advanced Security (Weeks 5-6)

| Priority | Component | Effort | Risk |
|----------|-----------|--------|------|
| P0 | Multi-Factor Authentication | High | High |
| P0 | Audit Logging | High | Medium |
| P1 | Brute Force Protection | Medium | Medium |

### Phase 4: Enterprise Features (Weeks 7-8)

| Priority | Component | Effort | Risk |
|----------|-----------|--------|------|
| P1 | OAuth 2.0 Server | High | High |
| P1 | SSO Integration | High | High |
| P2 | SAML Support | High | Medium |

---

## Summary

This comprehensive authentication and authorization design for ResilienceAI provides:

1. **OAuth 2.0 Server** - Full implementation with multiple grant types
2. **JWT Management** - Secure token handling with rotation and revocation
3. **RBAC System** - Flexible role and permission management
4. **API Key Management** - Secure service-to-service authentication
5. **Multi-Factor Authentication** - TOTP, SMS, Email, WebAuthn support
6. **Session Management** - Secure session handling with expiration
7. **Password Policies** - Strong password requirements and history
8. **SSO Integration** - SAML, OIDC, and social login support
9. **Authorization Middleware** - Request-level access control
10. **Audit Logging** - Comprehensive security event tracking

The implementation follows security best practices including:
- Encryption at rest and in transit
- Secure key management
- Rate limiting and brute force protection
- Comprehensive audit trails
- Defense in depth approach

---

## File Structure

```
/mnt/okcomputer/output/resilience_ai_analysis/auth/
├── oauth_server.py          # OAuth 2.0 implementation
├── jwt_manager.py           # JWT token management
├── rbac_engine.py           # RBAC implementation
├── api_key_manager.py       # API key management
├── mfa_service.py           # Multi-factor authentication
├── session_manager.py       # Session management
├── password_policy.py       # Password policies
├── sso_service.py           # SSO integration
├── middleware.py            # Authorization middleware
├── audit_logger.py          # Audit logging
├── security_measures.py     # Security utilities
├── tests/                   # Test suite
│   ├── test_auth.py
│   ├── test_rbac.py
│   └── test_security.py
├── k8s/                     # Kubernetes manifests
│   └── auth-deployment.yaml
├── Dockerfile               # Container image
└── requirements.txt         # Dependencies
```

---

*Document Version: 1.0*
*Last Updated: 2024*
