"""
Security Module for ResilienceAI IoT
Implements encryption, authentication, and secure communication
"""

import os
import json
import base64
import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import jwt

logger = logging.getLogger(__name__)


@dataclass
class SecurityContext:
    """Security context for device communication"""
    device_id: str
    certificate_pem: Optional[str] = None
    private_key_pem: Optional[str] = None
    ca_certificate: Optional[str] = None
    shared_secret: Optional[bytes] = None
    token: Optional[str] = None
    token_expiry: Optional[datetime] = None


class DeviceCrypto:
    """Cryptographic operations for devices"""
    
    @staticmethod
    def generate_key_pair() -> Tuple[str, str]:
        """Generate RSA key pair for device"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        return private_pem, public_pem
    
    @staticmethod
    def encrypt_field(data: str, key: bytes) -> str:
        """Encrypt sensitive field data"""
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt_field(encrypted_data: str, key: bytes) -> str:
        """Decrypt sensitive field data"""
        f = Fernet(key)
        encrypted = base64.b64decode(encrypted_data.encode())
        return f.decrypt(encrypted).decode()
    
    @staticmethod
    def generate_device_secret(device_id: str, master_key: bytes) -> bytes:
        """Generate device-specific secret from master key"""
        return hmac.new(
            master_key,
            device_id.encode(),
            hashlib.sha256
        ).digest()


class SecureMQTTClient:
    """Secure MQTT client with certificate authentication"""
    
    def __init__(self, security_context: SecurityContext):
        self.security_context = security_context
        self.client = None
    
    def setup_tls(self, mqtt_client):
        """Configure TLS for MQTT client"""
        import ssl
        
        # Create SSL context
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        
        # Load certificates
        if self.security_context.ca_certificate:
            ssl_context.load_verify_locations(cadata=self.security_context.ca_certificate)
        
        if self.security_context.certificate_pem and self.security_context.private_key_pem:
            ssl_context.load_cert_chain(
                certfile=self._pem_to_temp_file(self.security_context.certificate_pem),
                keyfile=self._pem_to_temp_file(self.security_context.private_key_pem)
            )
        
        # Configure MQTT client
        mqtt_client.tls_set_context(ssl_context)
        mqtt_client.tls_insecure_set(False)
    
    def _pem_to_temp_file(self, pem_content: str) -> str:
        """Write PEM content to temporary file"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write(pem_content)
            return f.name


class PayloadEncryption:
    """Encrypt/decrypt sensor payloads"""
    
    def __init__(self, key: bytes):
        """Initialize with 256-bit key"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits)")
        self.key = key
    
    def encrypt(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """Encrypt payload"""
        # Generate nonce
        nonce = os.urandom(12)
        
        # Create AES-GCM cipher
        aesgcm = AESGCM(self.key)
        
        # Serialize and encrypt payload
        plaintext = json.dumps(payload).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        return {
            "encrypted": base64.b64encode(ciphertext).decode(),
            "nonce": base64.b64encode(nonce).decode()
        }
    
    def decrypt(self, encrypted_payload: Dict[str, str]) -> Dict[str, Any]:
        """Decrypt payload"""
        aesgcm = AESGCM(self.key)
        
        ciphertext = base64.b64decode(encrypted_payload["encrypted"])
        nonce = base64.b64decode(encrypted_payload["nonce"])
        
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(plaintext.decode())


class JWTTokenManager:
    """Manage JWT tokens for API authentication"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_token(
        self,
        device_id: str,
        scopes: list,
        expires_hours: int = 24
    ) -> str:
        """Generate JWT token for device"""
        payload = {
            "sub": device_id,
            "scopes": scopes,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_hours)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None


class SecureStorage:
    """Secure storage for sensitive data"""
    
    def __init__(self, encryption_key: bytes):
        self.encryption_key = encryption_key
        self.fernet = Fernet(base64.urlsafe_b64encode(encryption_key[:32]))
    
    def store(self, key: str, data: Dict) -> str:
        """Encrypt and store data"""
        serialized = json.dumps(data)
        encrypted = self.fernet.encrypt(serialized.encode())
        return base64.b64encode(encrypted).decode()
    
    def retrieve(self, encrypted_data: str) -> Dict:
        """Retrieve and decrypt data"""
        encrypted = base64.b64decode(encrypted_data.encode())
        decrypted = self.fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())


class SecurityAudit:
    """Security audit logging"""
    
    def __init__(self, log_path: str = "security_audit.log"):
        self.log_path = log_path
        
        # Setup audit logger
        self.audit_logger = logging.getLogger("security_audit")
        handler = logging.FileHandler(log_path)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.audit_logger.addHandler(handler)
        self.audit_logger.setLevel(logging.INFO)
    
    def log_event(
        self,
        event_type: str,
        device_id: str,
        details: Dict,
        success: bool = True
    ):
        """Log security event"""
        event = {
            "event_type": event_type,
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "details": details
        }
        
        level = logging.INFO if success else logging.WARNING
        self.audit_logger.log(level, json.dumps(event))
    
    def log_authentication(
        self,
        device_id: str,
        method: str,
        success: bool,
        ip_address: Optional[str] = None
    ):
        """Log authentication attempt"""
        self.log_event(
            "authentication",
            device_id,
            {"method": method, "ip_address": ip_address},
            success
        )
    
    def log_data_access(
        self,
        device_id: str,
        resource: str,
        action: str,
        success: bool
    ):
        """Log data access event"""
        self.log_event(
            "data_access",
            device_id,
            {"resource": resource, "action": action},
            success
        )


# Security best practices checklist
SECURITY_CHECKLIST = {
    "device_security": [
        "Enable secure boot on all devices",
        "Use hardware security modules where available",
        "Implement certificate-based authentication",
        "Store private keys in secure elements",
        "Disable debug interfaces in production",
        "Implement firmware signing and verification"
    ],
    "communication_security": [
        "Use TLS 1.3 for all connections",
        "Implement certificate pinning",
        "Enable perfect forward secrecy",
        "Use strong cipher suites only",
        "Implement connection rate limiting"
    ],
    "network_security": [
        "Segment IoT devices into isolated VLANs",
        "Implement firewall rules for device traffic",
        "Deploy intrusion detection systems",
        "Use VPN for remote device management",
        "Monitor network traffic for anomalies"
    ],
    "application_security": [
        "Validate all input data",
        "Implement rate limiting on APIs",
        "Use parameterized queries for databases",
        "Implement proper error handling",
        "Regular security code reviews"
    ],
    "data_security": [
        "Encrypt data at rest (AES-256)",
        "Encrypt sensitive fields individually",
        "Implement data retention policies",
        "Regular backup with encryption",
        "Secure key management (KMS/HSM)"
    ]
}


# Example usage
if __name__ == "__main__":
    # Generate device key pair
    private_key, public_key = DeviceCrypto.generate_key_pair()
    print(f"Generated key pair for device")
    
    # Initialize payload encryption
    encryption_key = os.urandom(32)
    payload_crypto = PayloadEncryption(encryption_key)
    
    # Encrypt sample payload
    sample_payload = {
        "device_id": "sensor_001",
        "readings": {"temperature": 25.5, "humidity": 60},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    encrypted = payload_crypto.encrypt(sample_payload)
    print(f"Encrypted payload: {encrypted}")
    
    # Decrypt
    decrypted = payload_crypto.decrypt(encrypted)
    print(f"Decrypted payload: {decrypted}")
    
    # JWT token management
    token_manager = JWTTokenManager(secret_key="your-secret-key-here")
    token = token_manager.generate_token(
        device_id="sensor_001",
        scopes=["read", "write"],
        expires_hours=24
    )
    print(f"Generated token: {token[:50]}...")
    
    # Verify token
    verified = token_manager.verify_token(token)
    print(f"Token verified: {verified is not None}")
