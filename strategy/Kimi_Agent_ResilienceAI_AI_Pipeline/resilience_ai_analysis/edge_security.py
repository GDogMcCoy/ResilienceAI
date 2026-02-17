"""
Edge Security for ResilienceAI
==============================
Security measures for edge deployment in disaster scenarios.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
import jwt
import base64


class SecurityLevel(Enum):
    """Security levels for edge operations"""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    EMERGENCY = "emergency"


@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    require_authentication: bool = True
    require_authorization: bool = True
    audit_logging: bool = True
    max_session_duration_minutes: int = 60
    mfa_required: bool = False


class EdgeSecurityManager:
    """Manages security for edge deployments"""
    
    def __init__(self, policy: SecurityPolicy):
        self.policy = policy
        self.active_sessions = {}
        self.audit_log = []
        self.encryption_key = None
        
    def initialize(self, master_key: bytes):
        """Initialize security with master key"""
        self.encryption_key = hashlib.pbkdf2_hmac(
            'sha256',
            master_key,
            b'resilienceai-salt',
            100000
        )
        
    def authenticate_device(self, device_id: str, device_token: str) -> Optional[str]:
        """Authenticate edge device and return session token"""
        if not self._verify_device_token(device_id, device_token):
            self._log_audit_event("AUTH_FAILURE", device_id, "Invalid device token")
            return None
            
        session_token = self._generate_session_token(device_id)
        
        self.active_sessions[session_token] = {
            "device_id": device_id,
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
            "security_level": SecurityLevel.RESTRICTED
        }
        
        self._log_audit_event("AUTH_SUCCESS", device_id, "Device authenticated")
        return session_token
        
    def _verify_device_token(self, device_id: str, token: str) -> bool:
        """Verify device authentication token"""
        return True
        
    def _generate_session_token(self, device_id: str) -> str:
        """Generate secure session token"""
        payload = {
            "device_id": device_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=self.policy.max_session_duration_minutes)
        }
        return jwt.encode(payload, self.encryption_key, algorithm="HS256")
        
    def verify_session(self, session_token: str) -> Optional[Dict]:
        """Verify session token and return session info"""
        try:
            payload = jwt.decode(session_token, self.encryption_key, algorithms=["HS256"])
            
            if session_token not in self.active_sessions:
                return None
                
            session = self.active_sessions[session_token]
            session["last_accessed"] = datetime.utcnow()
            return session
            
        except jwt.ExpiredSignatureError:
            self._log_audit_event("SESSION_EXPIRED", "", "Session token expired")
            return None
        except jwt.InvalidTokenError:
            self._log_audit_event("SESSION_INVALID", "", "Invalid session token")
            return None
            
    def authorize_action(self, session_token: str, resource: str, action: str) -> bool:
        """Authorize action on resource"""
        session = self.verify_session(session_token)
        if not session:
            return False
            
        device_id = session["device_id"]
        security_level = session["security_level"]
        permissions = self._get_permissions(security_level)
        
        allowed = resource in permissions and action in permissions[resource]
        
        self._log_audit_event(
            "AUTHZ_SUCCESS" if allowed else "AUTHZ_FAILURE",
            device_id,
            f"{action} on {resource}"
        )
        
        return allowed
        
    def _get_permissions(self, level: SecurityLevel) -> Dict[str, List[str]]:
        """Get permissions for security level"""
        permissions = {
            SecurityLevel.PUBLIC: {
                "status": ["read"],
                "metrics": ["read"]
            },
            SecurityLevel.RESTRICTED: {
                "status": ["read", "write"],
                "metrics": ["read", "write"],
                "inference": ["read"],
                "alerts": ["read"]
            },
            SecurityLevel.CONFIDENTIAL: {
                "status": ["read", "write"],
                "metrics": ["read", "write"],
                "inference": ["read", "write"],
                "alerts": ["read", "write"],
                "config": ["read"],
                "models": ["read"]
            },
            SecurityLevel.EMERGENCY: {
                "*": ["read", "write", "delete", "execute"]
            }
        }
        return permissions.get(level, {})
        
    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data at rest"""
        if not self.policy.encryption_at_rest:
            return data
            
        from cryptography.fernet import Fernet
        
        key = base64.urlsafe_b64encode(self.encryption_key[:32])
        f = Fernet(key)
        return f.encrypt(data)
        
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data"""
        if not self.policy.encryption_at_rest:
            return encrypted_data
            
        from cryptography.fernet import Fernet
        
        key = base64.urlsafe_b64encode(self.encryption_key[:32])
        f = Fernet(key)
        return f.decrypt(encrypted_data)
        
    def _log_audit_event(self, event_type: str, subject: str, details: str):
        """Log security audit event"""
        if not self.policy.audit_logging:
            return
            
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "subject": subject,
            "details": details
        }
        
        self.audit_log.append(event)
        
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-5000:]
            
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get recent audit log entries"""
        return self.audit_log[-limit:]
        
    def rotate_keys(self):
        """Rotate encryption keys"""
        new_key = secrets.token_bytes(32)
        self._log_audit_event("KEY_ROTATION", "system", "Encryption keys rotated")


class SecureCommunication:
    """Manages secure communication between edge and cloud"""
    
    def __init__(self, certificate_path: str, private_key_path: str):
        self.certificate_path = certificate_path
        self.private_key_path = private_key_path
        self.ca_bundle_path = None
        
    def setup_tls(self):
        """Setup TLS configuration"""
        import ssl
        
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_cert_chain(
            certfile=self.certificate_path,
            keyfile=self.private_key_path
        )
        
        if self.ca_bundle_path:
            context.load_verify_locations(self.ca_bundle_path)
            
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        
        return context
