# /mnt/okcomputer/output/resilience_ai_analysis/code/encryption_service.py
"""
Encryption Service for ResilienceAI
Provides AES-256-GCM encryption with key management.
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import hashlib
import hmac
import os
import base64
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class EncryptionKey:
    """Encryption key metadata."""
    key_id: str
    key_bytes: bytes
    algorithm: str
    created_at: datetime
    expires_at: datetime
    key_version: int
    is_active: bool


class EncryptionService:
    """Encryption service for ResilienceAI archival data."""
    
    def __init__(self, key_management_service=None):
        self.kms = key_management_service
        self.keys: Dict[str, EncryptionKey] = {}
        self.current_key_id: Optional[str] = None
        
        # Encryption configuration
        self.config = {
            "algorithm": "AES-256-GCM",
            "key_size": 32,  # 256 bits
            "nonce_size": 12,  # 96 bits for GCM
            "tag_size": 16,    # 128 bits for GCM
            "kdf_iterations": 100000,
            "key_rotation_days": 90
        }
    
    def generate_key(self, key_id: Optional[str] = None) -> EncryptionKey:
        """Generate a new encryption key."""
        if key_id is None:
            key_id = base64.urlsafe_b64encode(os.urandom(16)).decode('ascii')
        
        key_bytes = AESGCM.generate_key(bit_length=256)
        
        key = EncryptionKey(
            key_id=key_id,
            key_bytes=key_bytes,
            algorithm=self.config["algorithm"],
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=self.config["key_rotation_days"]),
            key_version=1,
            is_active=True
        )
        
        self.keys[key_id] = key
        self.current_key_id = key_id
        
        return key
    
    def encrypt(self, data: bytes, key_id: Optional[str] = None,
               associated_data: Optional[bytes] = None) -> Dict:
        """Encrypt data using AES-256-GCM."""
        # Get encryption key
        if key_id is None:
            key_id = self.current_key_id
        
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")
        
        key = self.keys[key_id]
        
        # Generate nonce
        nonce = os.urandom(self.config["nonce_size"])
        
        # Create AESGCM cipher
        aesgcm = AESGCM(key.key_bytes)
        
        # Encrypt data
        ciphertext = aesgcm.encrypt(nonce, data, associated_data)
        
        # Build encrypted payload
        encrypted_payload = {
            "version": 1,
            "algorithm": "AES-256-GCM",
            "key_id": key_id,
            "nonce": base64.b64encode(nonce).decode('ascii'),
            "ciphertext": base64.b64encode(ciphertext).decode('ascii'),
            "associated_data": base64.b64encode(associated_data).decode('ascii') if associated_data else None,
            "encrypted_at": datetime.now().isoformat()
        }
        
        return encrypted_payload
    
    def decrypt(self, encrypted_payload: Dict) -> bytes:
        """Decrypt data using AES-256-GCM."""
        key_id = encrypted_payload["key_id"]
        
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")
        
        key = self.keys[key_id]
        
        # Decode components
        nonce = base64.b64decode(encrypted_payload["nonce"])
        ciphertext = base64.b64decode(encrypted_payload["ciphertext"])
        associated_data = None
        if encrypted_payload.get("associated_data"):
            associated_data = base64.b64decode(encrypted_payload["associated_data"])
        
        # Create AESGCM cipher
        aesgcm = AESGCM(key.key_bytes)
        
        # Decrypt data
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
        
        return plaintext
    
    def derive_key_from_password(self, password: str, 
                                 salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Derive encryption key from password using PBKDF2."""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=self.config["key_size"],
            salt=salt,
            iterations=self.config["kdf_iterations"],
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return key, salt
    
    def create_hmac(self, data: bytes, key: bytes) -> bytes:
        """Create HMAC-SHA256 for data integrity."""
        return hmac.new(key, data, hashlib.sha256).digest()
    
    def verify_hmac(self, data: bytes, hmac_value: bytes, key: bytes) -> bool:
        """Verify HMAC-SHA256 for data integrity."""
        expected_hmac = self.create_hmac(data, key)
        return hmac.compare_digest(hmac_value, expected_hmac)
    
    def rotate_key(self, old_key_id: str) -> EncryptionKey:
        """Rotate an encryption key."""
        if old_key_id not in self.keys:
            raise ValueError(f"Key {old_key_id} not found")
        
        old_key = self.keys[old_key_id]
        
        # Generate new key
        new_key_id = f"{old_key_id}_v{old_key.key_version + 1}"
        new_key = self.generate_key(new_key_id)
        new_key.key_version = old_key.key_version + 1
        
        # Mark old key as inactive
        old_key.is_active = False
        
        return new_key
    
    def get_key_status(self, key_id: str) -> Dict:
        """Get status of an encryption key."""
        if key_id not in self.keys:
            return {"status": "not_found"}
        
        key = self.keys[key_id]
        
        return {
            "key_id": key_id,
            "algorithm": key.algorithm,
            "created_at": key.created_at.isoformat(),
            "expires_at": key.expires_at.isoformat(),
            "key_version": key.key_version,
            "is_active": key.is_active,
            "days_until_expiry": (key.expires_at - datetime.now()).days
        }
    
    def encrypt_with_password(self, data: bytes, password: str) -> Dict:
        """Encrypt data with password-derived key."""
        key, salt = self.derive_key_from_password(password)
        
        # Generate nonce
        nonce = os.urandom(self.config["nonce_size"])
        
        # Create AESGCM cipher
        aesgcm = AESGCM(key)
        
        # Encrypt data
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        return {
            "version": 1,
            "algorithm": "AES-256-GCM",
            "kdf": "PBKDF2-SHA256",
            "iterations": self.config["kdf_iterations"],
            "salt": base64.b64encode(salt).decode('ascii'),
            "nonce": base64.b64encode(nonce).decode('ascii'),
            "ciphertext": base64.b64encode(ciphertext).decode('ascii')
        }
    
    def decrypt_with_password(self, encrypted_payload: Dict, password: str) -> bytes:
        """Decrypt data with password-derived key."""
        salt = base64.b64decode(encrypted_payload["salt"])
        
        # Derive key
        key, _ = self.derive_key_from_password(password, salt)
        
        # Decode components
        nonce = base64.b64decode(encrypted_payload["nonce"])
        ciphertext = base64.b64decode(encrypted_payload["ciphertext"])
        
        # Create AESGCM cipher
        aesgcm = AESGCM(key)
        
        # Decrypt data
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext


if __name__ == "__main__":
    # Example usage
    service = EncryptionService()
    
    # Generate key
    key = service.generate_key("key-001")
    print(f"Generated key: {key.key_id}")
    
    # Sample data
    sample_data = b"Sensitive incident data for ResilienceAI"
    
    # Encrypt
    encrypted = service.encrypt(sample_data)
    print(f"\nEncrypted payload keys: {list(encrypted.keys())}")
    
    # Decrypt
    decrypted = service.decrypt(encrypted)
    print(f"Decrypted data: {decrypted.decode()}")
    
    # Verify integrity
    assert decrypted == sample_data, "Decryption failed!"
    print("\nEncryption/Decryption successful!")
    
    # Key rotation
    new_key = service.rotate_key("key-001")
    print(f"\nRotated to new key: {new_key.key_id}")
    
    # Check key status
    status = service.get_key_status(new_key.key_id)
    print(f"Key status: {status}")
