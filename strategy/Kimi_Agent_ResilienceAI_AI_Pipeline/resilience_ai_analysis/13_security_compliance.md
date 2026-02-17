# ResilienceAI Security & Compliance Architecture
## Comprehensive Security Enhancement Plan

**Repository:** https://github.com/GDogMcCoy/ResilienceAI  
**Branch:** claw-autonomous  
**Document Version:** 1.0  
**Date:** February 2026  
**Classification:** Internal - Security Architecture

---

## Executive Summary

This document provides a comprehensive security and compliance enhancement plan for ResilienceAI, a disaster vulnerability and health infrastructure assessment platform. The analysis identifies current security gaps and proposes enterprise-grade security architecture including OAuth 2.0/JWT authentication, RBAC, encryption, FHIR R4 compliance, and continuous security monitoring.

### Current Security Posture Assessment

| Area | Current State | Risk Level | Priority |
|------|--------------|------------|----------|
| API Key Management | Environment variables only | MEDIUM | High |
| Authentication | None | HIGH | Critical |
| Authorization | None | HIGH | Critical |
| Data Encryption | None | HIGH | Critical |
| PII Handling | No anonymization | HIGH | Critical |
| Audit Logging | None | MEDIUM | High |
| FHIR Compliance | Basic export only | MEDIUM | High |
| Security Headers | None | MEDIUM | Medium |
| Vulnerability Scanning | None | HIGH | High |

---

## Table of Contents

1. [Security Architecture Overview](#1-security-architecture-overview)
2. [Authentication & Authorization](#2-authentication--authorization)
3. [API Security](#3-api-security)
4. [Data Encryption](#4-data-encryption)
5. [PII Handling & Anonymization](#5-pii-handling--anonymization)
6. [FHIR R4 Compliance](#6-fhir-r4-compliance)
7. [Security Headers & Middleware](#7-security-headers--middleware)
8. [Audit Logging & Monitoring](#8-audit-logging--monitoring)
9. [Vulnerability Management](#9-vulnerability-management)
10. [Compliance Framework](#10-compliance-framework)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Security Policies](#12-security-policies)

---

## 1. Security Architecture Overview

### 1.1 Proposed Security Architecture

```
CLIENT LAYER (Web App, Mobile, API Clients, Dashboard)
         |
         | HTTPS/TLS 1.3
         v
API GATEWAY (Kong/AWS/Azure) - Rate Limiting, WAF, DDoS Protection
         |
         v
AUTHENTICATION (OAuth 2.0 + OIDC) - JWT, MFA, Session Management
         |
         v
AUTHORIZATION (RBAC + ABAC) - Role Definitions, Permission Matrix
         |
         v
APPLICATION LAYER (Resilience API, Agent Orchestrator, FHIR Service)
         |
         v
DATA LAYER (Encrypted PostgreSQL, Secure Redis, Object Store with SSE)
```

### 1.2 Security Zones

| Zone | Description | Security Controls |
|------|-------------|-------------------|
| **Public Zone** | External-facing interfaces | WAF, DDoS, Rate Limiting |
| **DMZ Zone** | API Gateway, Load Balancers | TLS termination, Request validation |
| **Application Zone** | Microservices, APIs | Authentication, Authorization |
| **Data Zone** | Databases, Storage | Encryption, Access controls |
| **Management Zone** | Monitoring, Logging | Audit trails, SIEM integration |

---

## 2. Authentication & Authorization

### 2.1 OAuth 2.0 + OpenID Connect Implementation

**File:** `/src/security/auth/oauth_config.py`

```python
"""ResilienceAI - OAuth 2.0 and OIDC Configuration"""
import os
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class GrantType(Enum):
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    PKCE = "pkce"

@dataclass
class OAuthProviderConfig:
    provider_name: str
    client_id: str
    client_secret: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    jwks_uri: str
    issuer: str
    redirect_uri: str
    scopes: List[str]
    pkce_enabled: bool = True
    mfa_required: bool = False

# Auth0 Configuration
AUTH0_CONFIG = OAuthProviderConfig(
    provider_name="auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID", ""),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET", ""),
    authorization_endpoint=f"https://{os.environ.get('AUTH0_DOMAIN', '')}/authorize",
    token_endpoint=f"https://{os.environ.get('AUTH0_DOMAIN', '')}/oauth/token",
    userinfo_endpoint=f"https://{os.environ.get('AUTH0_DOMAIN', '')}/userinfo",
    jwks_uri=f"https://{os.environ.get('AUTH0_DOMAIN', '')}/.well-known/jwks.json",
    issuer=f"https://{os.environ.get('AUTH0_DOMAIN', '')}/",
    redirect_uri=os.environ.get("AUTH0_REDIRECT_URI", "http://localhost:8501/callback"),
    scopes=["openid", "profile", "email", "resilienceai:read", "resilienceai:write"],
    pkce_enabled=True,
    mfa_required=True
)
```

### 2.2 JWT Token Management

**File:** `/src/security/auth/jwt_manager.py`

```python
"""ResilienceAI - JWT Token Manager"""
import jwt
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import hashlib

class JWTManager:
    def __init__(self, provider_config):
        self.config = provider_config
        self.jwks_cache = None
        self.jwks_cache_time = None
        self.jwks_cache_ttl = 3600
        
    def validate_token(self, token: str, required_scopes: List[str] = None) -> Dict:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise jwt.InvalidTokenError("Token missing key ID")
        
        signing_key = self._get_signing_key(kid)
        payload = jwt.decode(
            token, signing_key, algorithms=["RS256"],
            audience=self.config.client_id, issuer=self.config.issuer
        )
        
        if required_scopes:
            token_scopes = payload.get("scope", "").split()
            missing = set(required_scopes) - set(token_scopes)
            if missing:
                raise PermissionError(f"Missing scopes: {missing}")
        return payload
    
    def is_token_expired(self, token: str, buffer_seconds: int = 300) -> bool:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get("exp")
        if not exp:
            return True
        return datetime.utcnow() + timedelta(seconds=buffer_seconds) >= datetime.utcfromtimestamp(exp)
```

### 2.3 Role-Based Access Control (RBAC)

**File:** `/src/security/auth/rbac.py`

```python
"""ResilienceAI - Role-Based Access Control"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Set

class Permission(Enum):
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_EXPORT = "data:export"
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXECUTE = "analytics:execute"
    MODEL_READ = "model:read"
    MODEL_TRAIN = "model:train"
    FHIR_READ = "fhir:read"
    FHIR_WRITE = "fhir:write"
    FHIR_EXPORT = "fhir:export"
    AGENT_EXECUTE = "agent:execute"
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    AUDIT_READ = "audit:read"
    COUNTY_READ_OWN = "county:read:own"
    COUNTY_READ_REGION = "county:read:region"
    COUNTY_READ_ALL = "county:read:all"

class Role(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    DATA_MANAGER = "data_manager"
    ANALYST = "analyst"
    CLINICIAN = "clinician"
    RESEARCHER = "researcher"
    EMERGENCY_RESPONDER = "emergency_responder"
    READ_ONLY = "read_only"

ROLE_DEFINITIONS = {
    Role.SUPER_ADMIN.value: {
        "name": "Super Administrator",
        "permissions": set(Permission),
        "data_scope": "national"
    },
    Role.ADMIN.value: {
        "name": "Administrator",
        "permissions": {
            Permission.DATA_READ, Permission.DATA_WRITE, Permission.DATA_EXPORT,
            Permission.ANALYTICS_READ, Permission.ANALYTICS_EXECUTE,
            Permission.MODEL_READ, Permission.MODEL_TRAIN,
            Permission.FHIR_READ, Permission.FHIR_WRITE, Permission.FHIR_EXPORT,
            Permission.AGENT_EXECUTE, Permission.USER_READ, Permission.USER_CREATE,
            Permission.AUDIT_READ, Permission.COUNTY_READ_ALL
        },
        "data_scope": "national"
    },
    Role.ANALYST.value: {
        "name": "Data Analyst",
        "permissions": {
            Permission.DATA_READ, Permission.DATA_EXPORT,
            Permission.ANALYTICS_READ, Permission.ANALYTICS_EXECUTE,
            Permission.MODEL_READ, Permission.FHIR_READ, Permission.FHIR_EXPORT,
            Permission.AGENT_EXECUTE, Permission.COUNTY_READ_REGION
        },
        "data_scope": "region"
    },
    Role.CLINICIAN.value: {
        "name": "Clinician",
        "permissions": {
            Permission.DATA_READ, Permission.ANALYTICS_READ,
            Permission.FHIR_READ, Permission.FHIR_EXPORT,
            Permission.COUNTY_READ_OWN
        },
        "data_scope": "own"
    }
}

class RBACManager:
    def __init__(self):
        self.role_definitions = ROLE_DEFINITIONS
        self.user_roles: Dict[str, List[str]] = {}
    
    def assign_role(self, user_id: str, role: str):
        if role not in self.role_definitions:
            raise ValueError(f"Invalid role: {role}")
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        if role not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role)
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        permissions = set()
        for role in self.user_roles.get(user_id, []):
            role_def = self.role_definitions.get(role, {})
            permissions.update(role_def.get("permissions", set()))
        return permission in permissions
```

---

## 3. API Security

### 3.1 API Security Middleware

**File:** `/src/security/api/security_middleware.py`

```python
"""ResilienceAI - API Security Middleware"""
import time
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import re

class RateLimiter:
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self._memory_buckets = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        now = time.time()
        bucket_key = f"rate_limit:{key}"
        
        if self.redis:
            pipe = self.redis.pipeline()
            pipe.zremrangebyscore(bucket_key, 0, now - window)
            pipe.zcard(bucket_key)
            pipe.zadd(bucket_key, {str(now): now})
            pipe.expire(bucket_key, window)
            _, current_count, _, _ = pipe.execute()
            return current_count < limit
        else:
            if bucket_key not in self._memory_buckets:
                self._memory_buckets[bucket_key] = []
            self._memory_buckets[bucket_key] = [
                t for t in self._memory_buckets[bucket_key] if t > now - window
            ]
            if len(self._memory_buckets[bucket_key]) < limit:
                self._memory_buckets[bucket_key].append(now)
                return True
            return False

class APIKeyManager:
    def __init__(self, db_client=None):
        self.db = db_client
        self._key_prefix = "rai_"
    
    def generate_api_key(self, name: str, owner: str, permissions: List[str], expires_days: int = 365) -> Dict:
        key_id = secrets.token_hex(16)
        secret = secrets.token_urlsafe(32)
        api_key = f"{self._key_prefix}{key_id}_{secret}"
        
        key_data = {
            "id": key_id, "name": name, "owner": owner,
            "permissions": permissions,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=expires_days)).isoformat(),
            "active": True, "hashed_secret": self._hash_secret(secret)
        }
        if self.db:
            self.db.store_api_key(key_id, key_data)
        return {"api_key": api_key, "key_id": key_id, "expires_at": key_data["expires_at"]}
    
    def _hash_secret(self, secret: str) -> str:
        return hashlib.sha256(secret.encode()).hexdigest()

class InputValidator:
    SQLI_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE)\b)",
        r"(--|#|/\*|\*/)",
    ]
    XSS_PATTERNS = [
        r"<script[^>]*>[\s\S]*?</script>",
        r"javascript:", r"on\w+\s*=",
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        if not isinstance(value, str):
            return ""
        value = value[:max_length].replace("\x00", "")
        for pattern in cls.SQLI_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potential SQL injection detected")
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potential XSS attack detected")
        return value
    
    @classmethod
    def validate_fips(cls, fips: str) -> str:
        fips = re.sub(r"\D", "", fips)
        if len(fips) != 5:
            raise ValueError("FIPS code must be 5 digits")
        return fips
```

---

## 4. Data Encryption

### 4.1 Encryption at Rest

**File:** `/src/security/encryption/encryption_manager.py`

```python
"""ResilienceAI - Encryption Manager"""
import os
import base64
from typing import Union, Optional
from cryptography.fernet import Fernet

class EncryptionManager:
    def __init__(self, master_key: Optional[str] = None):
        self.master_key = master_key or os.environ.get("ENCRYPTION_MASTER_KEY")
        if not self.master_key:
            raise ValueError("Encryption master key required")
        self._fernet = Fernet(self.master_key.encode() if isinstance(self.master_key, str) else self.master_key)
    
    def encrypt_field(self, plaintext: Union[str, bytes]) -> str:
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        encrypted = self._fernet.encrypt(plaintext)
        return base64.urlsafe_b64encode(encrypted).decode('ascii')
    
    def decrypt_field(self, ciphertext: str) -> str:
        encrypted = base64.urlsafe_b64decode(ciphertext.encode('ascii'))
        decrypted = self._fernet.decrypt(encrypted)
        return decrypted.decode('utf-8')

class FieldLevelEncryption:
    PII_FIELDS = ["patient_id", "patient_name", "ssn", "date_of_birth", 
                  "address", "phone", "email", "medical_record_number"]
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption = encryption_manager
    
    def encrypt_record(self, record: dict) -> dict:
        encrypted = record.copy()
        for field in self.PII_FIELDS:
            if field in encrypted and encrypted[field] is not None:
                encrypted[field] = self.encryption.encrypt_field(str(encrypted[field]))
                encrypted[f"{field}_encrypted"] = True
        return encrypted
```

### 4.2 TLS/SSL Configuration

**File:** `/src/security/encryption/tls_config.py`

```python
"""ResilienceAI - TLS/SSL Configuration"""
import ssl
import certifi

class TLSConfig:
    MIN_TLS_VERSION = ssl.TLSVersion.TLSv1_3
    CIPHER_SUITES = ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256", "TLS_AES_128_GCM_SHA256"]
    
    @classmethod
    def create_ssl_context(cls, purpose=ssl.Purpose.SERVER_AUTH) -> ssl.SSLContext:
        context = ssl.SSLContext(purpose)
        context.minimum_version = cls.MIN_TLS_VERSION
        context.set_ciphers(":".join(cls.CIPHER_SUITES))
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_verify_locations(certifi.where())
        context.options |= ssl.OP_NO_COMPRESSION | ssl.OP_NO_TICKET
        return context
```

---

## 5. PII Handling & Anonymization

### 5.1 PII Detection and Anonymization

**File:** `/src/security/pii/pii_detector.py`

```python
"""ResilienceAI - PII Detector and Anonymizer"""
import re
import hashlib
from typing import List, Dict
from enum import Enum

class PIIType(Enum):
    SSN = "ssn"
    EMAIL = "email"
    PHONE = "phone"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"

class PIIAnonymizer:
    def __init__(self, salt: str = None):
        self.salt = salt or "resilienceai_default_salt"
    
    def hash_identifier(self, value: str) -> str:
        return hashlib.sha256(f"{value}:{self.salt}".encode()).hexdigest()[:16]
    
    def mask_ssn(self, ssn: str) -> str:
        digits = re.sub(r"\D", "", ssn)
        return f"XXX-XX-{digits[-4:]}" if len(digits) == 9 else "XXX-XX-XXXX"
    
    def mask_email(self, email: str) -> str:
        if "@" not in email:
            return "***@***.***"
        local, domain = email.split("@")
        return f"{local[0]}***@{domain[0]}***.{domain.split('.')[-1]}"
    
    def generalize_age(self, age: int) -> str:
        ranges = [(18, "<18"), (30, "18-29"), (40, "30-39"), (50, "40-49"),
                  (60, "50-59"), (70, "60-69"), (80, "70-79")]
        for max_age, label in ranges:
            if age < max_age:
                return label
        return "80+"
    
    def generalize_zip(self, zip_code: str) -> str:
        digits = re.sub(r"\D", "", zip_code)
        return digits[:3] + "XX" if len(digits) >= 3 else "XXXXX"

class HIPAADeIdentifier:
    HIPAA_IDENTIFIERS = ["name", "geographic_subdivision", "dates", "telephone",
                         "fax", "email", "ssn", "mrn", "health_plan_numbers"]
    
    @classmethod
    def de_identify(cls, data: Dict) -> Dict:
        de_identified = data.copy()
        for identifier in cls.HIPAA_IDENTIFIERS:
            de_identified.pop(identifier, None)
        for key in list(de_identified.keys()):
            if "date" in key.lower():
                value = de_identified[key]
                if isinstance(value, str) and len(value) >= 4:
                    de_identified[key] = value[:4]
            if "zip" in key.lower():
                zip_value = str(de_identified[key])
                if len(zip_value) > 3:
                    de_identified[key] = zip_value[:3] + "00"
        return de_identified
```

---

## 6. FHIR R4 Compliance

### 6.1 Secure FHIR Export

**File:** `/src/security/fhir/fhir_security_export.py`

```python
"""ResilienceAI - Secure FHIR R4 Export"""
import uuid
from datetime import datetime
from typing import Dict, List
from enum import Enum

class FHIRSecurityLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"

class SecureFHIRExporter:
    FHIR_VERSION = "4.0.1"
    PROFILE_URL = "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Condition"
    
    def __init__(self, security_level: FHIRSecurityLevel = FHIRSecurityLevel.INTERNAL):
        self.security_level = security_level
    
    def create_secure_bundle(self, resources: List[Dict], de_identify: bool = True) -> Dict:
        bundle_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        secured_resources = [self._secure_resource(r, de_identify) for r in resources]
        
        return {
            "resourceType": "Bundle",
            "id": bundle_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": timestamp.isoformat() + "Z",
                "security": [{"system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
                              "code": self.security_level.value.upper()[:1]}]
            },
            "type": "collection",
            "timestamp": timestamp.isoformat() + "Z",
            "entry": [{"resource": r} for r in secured_resources]
        }
    
    def _secure_resource(self, resource: Dict, de_identify: bool) -> Dict:
        secured = resource.copy()
        if de_identify:
            secured = self._de_identify_resource(secured)
        return secured
    
    def _de_identify_resource(self, resource: Dict) -> Dict:
        de_identified = resource.copy()
        resource_type = de_identified.get("resourceType", "")
        
        if resource_type == "Patient":
            de_identified.pop("name", None)
            de_identified.pop("telecom", None)
            de_identified.pop("address", None)
            if "birthDate" in de_identified:
                de_identified["birthDate"] = de_identified["birthDate"][:4]
        
        return de_identified
    
    def create_risk_assessment_resource(self, county_fips: str, county_name: str,
                                        state: str, risk_score: float, 
                                        risk_level: str, risk_factors: List[str]) -> Dict:
        risk_coding = {"high": {"code": "high", "display": "High Risk"},
                       "moderate": {"code": "moderate", "display": "Moderate Risk"},
                       "low": {"code": "low", "display": "Low Risk"}}.get(risk_level.lower())
        
        return {
            "resourceType": "RiskAssessment",
            "id": str(uuid.uuid4()),
            "status": "final",
            "code": {"coding": [{"system": "https://resilienceai.io/fhir/risk-assessment-type",
                                  "code": "disaster-vulnerability"}]},
            "subject": {"reference": f"Location/{county_fips}", "display": f"{county_name}, {state}"},
            "prediction": [{"probabilityDecimal": risk_score, "qualitativeRisk": risk_coding}]
        }
```

---

## 7. Security Headers & Middleware

### 7.1 Security Headers for Streamlit

**File:** `/src/security/headers/streamlit_security.py`

```python
"""ResilienceAI - Streamlit Security"""
import streamlit as st
from datetime import datetime

class StreamlitSecurity:
    @staticmethod
    def configure_security_headers():
        st.set_page_config(
            page_title="ResilienceAI | Secure Dashboard",
            page_icon="🛡️",
            layout="wide",
            menu_items={
                "Get Help": "https://docs.resilienceai.io",
                "Report a bug": "https://github.com/GDogMcCoy/ResilienceAI/issues"
            }
        )
    
    @staticmethod
    def initialize_secure_session():
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user" not in st.session_state:
            st.session_state.user = None
        if "session_start" not in st.session_state:
            st.session_state.session_start = datetime.utcnow()
        
        if st.session_state.authenticated:
            session_age = (datetime.utcnow() - st.session_state.session_start).total_seconds()
            if session_age > 1800:  # 30 minutes
                StreamlitSecurity.logout_user()
                st.warning("Session expired. Please log in again.")
                st.stop()
    
    @staticmethod
    def logout_user():
        for key in ["authenticated", "user", "access_token", "session_start"]:
            if key in st.session_state:
                del st.session_state[key]
```

### 7.2 Nginx Security Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name dashboard.resilienceai.io;
    
    ssl_certificate /etc/ssl/certs/resilienceai.crt;
    ssl_certificate_key /etc/ssl/private/resilienceai.key;
    ssl_protocols TLSv1.3;
    ssl_ciphers TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256;
    
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none';" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 8. Audit Logging & Monitoring

### 8.1 Audit Logger

**File:** `/src/security/audit/audit_logger.py`

```python
"""ResilienceAI - Audit Logger"""
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Optional
from enum import Enum
from dataclasses import dataclass

class AuditEventType(Enum):
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"
    DATA_READ = "DATA_READ"
    DATA_EXPORT = "DATA_EXPORT"
    FHIR_EXPORT = "FHIR_EXPORT"
    ACCESS_DENIED = "ACCESS_DENIED"

class AuditSeverity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class AuditEvent:
    timestamp: str
    event_type: str
    severity: str
    user_id: Optional[str]
    ip_address: Optional[str]
    resource_type: Optional[str]
    action: str
    outcome: str
    details: Dict
    request_id: str

class AuditLogger:
    def __init__(self, log_file: str = "/var/log/resilienceai/audit.log"):
        self.logger = logging.getLogger("resilienceai_audit")
        self.logger.setLevel(logging.INFO)
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(log_file, maxBytes=100*1024*1024, backupCount=10)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
    
    def log_event(self, event: AuditEvent):
        self.logger.info(json.dumps(event.__dict__, default=str))
    
    def log_authentication(self, event_type: AuditEventType, user_id: str, ip_address: str, outcome: str = "success"):
        self.log_event(AuditEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type=event_type.value,
            severity=AuditSeverity.INFO.value if outcome == "success" else AuditSeverity.WARNING.value,
            user_id=user_id, ip_address=ip_address,
            resource_type="authentication", action=event_type.value,
            outcome=outcome, details={},
            request_id=hashlib.sha256(datetime.utcnow().isoformat().encode()).hexdigest()[:16]
        ))
```

---

## 9. Vulnerability Management

### 9.1 Vulnerability Scanner

**File:** `/src/security/scanning/vulnerability_scanner.py`

```python
"""ResilienceAI - Vulnerability Scanner"""
import subprocess
import json
import os
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class Vulnerability:
    id: str
    title: str
    severity: Severity
    package: str
    file_path: Optional[str] = None

class DependencyScanner:
    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_file = requirements_file
    
    def scan_with_safety(self) -> List[Vulnerability]:
        vulnerabilities = []
        try:
            result = subprocess.run(["safety", "check", "--json", "--file", self.requirements_file],
                                    capture_output=True, text=True, timeout=300)
            if result.returncode in [0, 64]:
                data = json.loads(result.stdout)
                for v in data.get("vulnerabilities", []):
                    vulnerabilities.append(Vulnerability(
                        id=v.get("vulnerability_id", ""),
                        title=v.get("advisory", ""),
                        severity=Severity(v.get("severity", "MEDIUM").upper()),
                        package=v.get("package_name", "")
                    ))
        except Exception:
            pass
        return vulnerabilities

class SecretScanner:
    SECRET_PATTERNS = [
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
        (r"gh[pousr]_[A-Za-z0-9_]{36,}", "GitHub Token"),
        (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API Key"),
        (r"sk_live_[a-zA-Z0-9]{20,}", "Stripe Live Key"),
    ]
    
    def scan_file(self, file_path: str) -> List[Vulnerability]:
        vulnerabilities = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    for pattern, secret_type in self.SECRET_PATTERNS:
                        if re.search(pattern, line):
                            vulnerabilities.append(Vulnerability(
                                id=f"SECRET_{secret_type.upper().replace(' ', '_')}",
                                title=f"Potential {secret_type} Exposed",
                                severity=Severity.CRITICAL,
                                package="code",
                                file_path=file_path
                            ))
        except Exception:
            pass
        return vulnerabilities
```

---

## 10. Compliance Framework

### 10.1 HIPAA Compliance Checklist

| Safeguard | Status | Implementation |
|-----------|--------|----------------|
| Access Control - Unique User ID | ✅ | OAuth 2.0 / OIDC |
| Access Control - Emergency Access | ⚠️ | Document break-glass procedures |
| Access Control - Automatic Logoff | ✅ | 30-minute session timeout |
| Access Control - Encryption | ✅ | AES-256-GCM at rest, TLS 1.3 in transit |
| Audit Controls | ✅ | Comprehensive audit logging |
| Integrity Controls | ✅ | Hash verification for audit logs |
| Authentication | ✅ | MFA for privileged access |
| Transmission Security | ✅ | TLS 1.3 with strong ciphers |

### 10.2 NIST Cybersecurity Framework Mapping

| Function | Category | Implementation |
|----------|----------|----------------|
| **Identify** | Asset Management | Data source inventory |
| | Risk Assessment | Vulnerability scanning |
| **Protect** | Access Control | OAuth 2.0, RBAC, MFA |
| | Data Security | Encryption at rest/transit |
| **Detect** | Anomalies & Events | Audit logging |
| | Continuous Monitoring | Security monitoring |
| **Respond** | Response Planning | Incident response procedures |
| **Recover** | Recovery Planning | Backup and disaster recovery |

---

## 11. Implementation Roadmap

### Phase 1: Critical Security (Weeks 1-4)

| Week | Task | Priority | Effort |
|------|------|----------|--------|
| 1 | OAuth 2.0 / OIDC authentication | Critical | 5 days |
| 1 | JWT token management | Critical | 3 days |
| 2 | RBAC system | Critical | 5 days |
| 2 | API key management | Critical | 3 days |
| 3 | Encryption at rest | Critical | 4 days |
| 3 | TLS 1.3 configuration | Critical | 2 days |
| 4 | Audit logging | Critical | 4 days |
| 4 | Rate limiting | High | 2 days |

### Phase 2: Data Protection (Weeks 5-8)

| Week | Task | Priority | Effort |
|------|------|----------|--------|
| 5 | PII detection | High | 4 days |
| 5 | Data anonymization | High | 3 days |
| 6 | FHIR security enhancements | High | 5 days |
| 6 | Field-level encryption | High | 3 days |
| 7 | k-anonymity support | Medium | 3 days |
| 7 | HIPAA de-identification | High | 3 days |

### Phase 3: Monitoring & Compliance (Weeks 9-12)

| Week | Task | Priority | Effort |
|------|------|----------|--------|
| 9 | Vulnerability scanning | High | 3 days |
| 9 | Secret scanning | High | 2 days |
| 10 | Security headers | Medium | 2 days |
| 11 | Anomaly detection | Medium | 4 days |
| 12 | Compliance reports | Medium | 3 days |

### Phase 4: Hardening & Testing (Weeks 13-16)

| Week | Task | Priority | Effort |
|------|------|----------|--------|
| 13 | Penetration testing | High | 5 days |
| 14 | Fix vulnerabilities | Critical | 5 days |
| 15 | Load testing | Medium | 3 days |
| 16 | Final security audit | Critical | 3 days |

---

## 12. Security Policies

### 12.1 Password Policy

```yaml
password_policy:
  minimum_length: 12
  require_uppercase: true
  require_lowercase: true
  require_numbers: true
  require_special_chars: true
  max_age_days: 90
  lockout_attempts: 5
  lockout_duration_minutes: 30
```

### 12.2 Session Policy

```yaml
session_policy:
  timeout_minutes: 30
  absolute_timeout_hours: 8
  secure_cookie: true
  http_only_cookie: true
  same_site_cookie: strict
```

### 12.3 API Security Policy

```yaml
api_security_policy:
  rate_limiting:
    default: 100 requests/minute
    authenticated: 1000 requests/minute
  authentication:
    required: true
    methods: [oauth2, api_key]
  encryption:
    min_tls_version: "1.3"
```

### 12.4 Data Classification

| Classification | Description | Handling |
|----------------|-------------|----------|
| **Public** | Non-sensitive | Standard |
| **Internal** | Business data | Access control |
| **Confidential** | Sensitive | Encryption + access |
| **Restricted** | PHI/PII | Encryption + strict access + audit |

---

## Appendix: Environment Variables

```bash
# Authentication
export OAUTH_PROVIDER=auth0
export AUTH0_DOMAIN=resilienceai.auth0.com
export AUTH0_CLIENT_ID=your_client_id
export AUTH0_CLIENT_SECRET=your_client_secret

# Encryption
export ENCRYPTION_MASTER_KEY=your_base64_encoded_key

# Database Security
export DB_SSL_CA_PATH=/etc/ssl/certs/ca.crt
export DB_SSL_CERT_PATH=/etc/ssl/certs/client.crt

# API Security
export API_RATE_LIMIT=1000

# Audit Logging
export AUDIT_LOG_PATH=/var/log/resilienceai/audit.log

# Session Security
export SESSION_TIMEOUT=1800
```

---

## Document Information

| Field | Value |
|-------|-------|
| **Document ID** | RAI-SEC-001 |
| **Version** | 1.0 |
| **Author** | Security Architecture Team |
| **Review Date** | Quarterly |
| **Classification** | Internal - Security |

---

*This document is a living document and should be updated as the security landscape evolves.*
