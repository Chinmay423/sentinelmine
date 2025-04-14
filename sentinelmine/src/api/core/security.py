from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import jwt
from passlib.context import CryptContext
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import os
import secrets
import hashlib

from .config import settings

# Password encryption context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper functions for password hashing
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Token creation and verification
def create_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None, additional_data: Dict = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.API_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    if additional_data:
        to_encode.update(additional_data)
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.JWTError:
        raise ValueError("Invalid authentication credentials")

# Generate secure random token
def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)

# AES Encryption/decryption for sensitive data
def encrypt_data(data: str) -> str:
    """Encrypt data using AES-256-CBC."""
    if not data:
        return data
    
    key = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY.encode() + b'=' * (4 - len(settings.ENCRYPTION_KEY) % 4))
    iv = os.urandom(16)
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Combine IV and encrypted data
    return base64.urlsafe_b64encode(iv + encrypted_data).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt data using AES-256-CBC."""
    if not encrypted_data:
        return encrypted_data
    
    decoded_data = base64.urlsafe_b64decode(encrypted_data.encode() + b'=' * (4 - len(encrypted_data) % 4))
    iv = decoded_data[:16]
    ciphertext = decoded_data[16:]
    
    key = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY.encode() + b'=' * (4 - len(settings.ENCRYPTION_KEY) % 4))
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    
    return data.decode()

# HMAC verification for data integrity
def generate_hmac(data: str) -> str:
    """Generate HMAC for data integrity verification."""
    return hashlib.sha256((data + settings.API_SECRET_KEY).encode()).hexdigest()

def verify_hmac(data: str, hmac_signature: str) -> bool:
    """Verify HMAC signature for data integrity."""
    return secrets.compare_digest(
        generate_hmac(data),
        hmac_signature
    )

# Multi-factor authentication
def generate_totp_secret() -> str:
    """Generate a secret for TOTP-based two-factor authentication."""
    return base64.b32encode(os.urandom(20)).decode('utf-8')

def hash_ip_address(ip_address: str) -> str:
    """Hash IP address for anonymization in logs."""
    # Only hash the last octet for IPv4 addresses
    if ip_address.count('.') == 3:
        parts = ip_address.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}.xxx"
    return hashlib.sha256(ip_address.encode()).hexdigest()[:10] 