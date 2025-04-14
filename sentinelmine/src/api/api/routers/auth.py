from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import json

from core.config import settings
from core.security import (
    verify_password, create_token, verify_token, 
    generate_totp_secret, generate_secure_token, 
    hash_ip_address
)
from core.logging import get_request_logger

# Mock database - In a real application, this would be replaced with a database model
# This is just for demonstration purposes
USERS_DB = {
    "john.analyst": {
        "id": "user-001",
        "username": "john.analyst",
        "email": "john.analyst@securedept.gov",
        "full_name": "John Analyst",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secure_password"
        "disabled": False,
        "role": "analyst",
        "department": "intelligence",
        "totp_secret": "JBSWY3DPEHPK3PXP",
        "last_login": None,
        "security_clearance": "top_secret",
        "refresh_tokens": []
    }
}

logger = get_request_logger()

router = APIRouter()

# Request and response models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_at: int

class RefreshToken(BaseModel):
    refresh_token: str

class TOTPRequest(BaseModel):
    username: str
    totp_code: str
    device_info: Dict[str, Any] = Field(default_factory=dict)

class LoginResponse(BaseModel):
    requires_mfa: bool
    mfa_type: Optional[str] = None
    mfa_token: Optional[str] = None
    token: Optional[Token] = None
    user_info: Optional[Dict[str, Any]] = None

# Utility functions
def authenticate_user(username: str, password: str):
    if username not in USERS_DB:
        return False
    user = USERS_DB[username]
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_login_tokens(user_id: str, username: str, security_clearance: str, 
                        request: Request, remember_me: bool = False):
    # Create access token
    access_token_expires = timedelta(minutes=settings.API_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {
        "sub": user_id,
        "username": username,
        "security_clearance": security_clearance,
        "ip_hash": hash_ip_address(request.client.host or ""),
        "iat": datetime.utcnow().timestamp()
    }
    access_token = create_token(
        subject=user_id,
        expires_delta=access_token_expires,
        additional_data=access_token_data
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=settings.API_REFRESH_TOKEN_EXPIRE_DAYS if remember_me else 1)
    refresh_token = generate_secure_token()
    
    # In a real application, store the refresh token in the database with expiry
    # Here we just store it in memory for demonstration
    user = USERS_DB[username]
    user["refresh_tokens"].append({
        "token": refresh_token,
        "expires_at": (datetime.utcnow() + refresh_token_expires).timestamp(),
        "user_agent": request.headers.get("User-Agent", ""),
        "ip_address": hash_ip_address(request.client.host or "")
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_at": int((datetime.utcnow() + access_token_expires).timestamp())
    }

# Routes
@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(
            f"Failed login attempt",
            extra={
                "username": form_data.username,
                "ip": request.client.host,
                "reason": "invalid_credentials"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user["disabled"]:
        logger.warning(
            f"Login attempt on disabled account",
            extra={
                "username": form_data.username,
                "ip": request.client.host,
                "user_id": user["id"]
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if MFA is enabled
    if settings.MFA_ENABLED:
        # Generate temporary MFA token
        mfa_token = create_token(
            subject=user["id"],
            expires_delta=timedelta(minutes=5),
            additional_data={
                "username": user["username"],
                "mfa_purpose": "totp_verification",
                "ip_hash": hash_ip_address(request.client.host or "")
            }
        )
        
        return {
            "requires_mfa": True,
            "mfa_type": "totp",
            "mfa_token": mfa_token,
            "token": None,
            "user_info": None
        }
    else:
        # MFA not required, proceed with token generation
        token = create_login_tokens(
            user["id"], 
            user["username"], 
            user["security_clearance"], 
            request,
            remember_me=form_data.scopes and "remember_me" in form_data.scopes
        )
        
        # Update last login time
        user["last_login"] = datetime.utcnow().isoformat()
        
        logger.info(
            f"User logged in",
            extra={
                "username": user["username"],
                "user_id": user["id"],
                "ip": request.client.host
            }
        )
        
        # Return minimal user info
        user_info = {
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "department": user["department"],
            "security_clearance": user["security_clearance"]
        }
        
        return {
            "requires_mfa": False,
            "token": token,
            "user_info": user_info
        }

@router.post("/verify-totp", response_model=LoginResponse)
async def verify_totp(request: Request, totp_data: TOTPRequest):
    """Verify TOTP code and complete login"""
    # In a real application, you would verify the TOTP code against the user's secret
    # For this demo, we'll just check if the username exists and pretend the code is valid
    
    if totp_data.username not in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    user = USERS_DB[totp_data.username]
    
    # For demo, we'll accept any 6-digit code
    if not totp_data.totp_code.isdigit() or len(totp_data.totp_code) != 6:
        logger.warning(
            f"Invalid TOTP code submitted",
            extra={
                "username": user["username"],
                "user_id": user["id"],
                "ip": request.client.host
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )
    
    # Generate tokens
    token = create_login_tokens(
        user["id"], 
        user["username"], 
        user["security_clearance"], 
        request,
        remember_me=False
    )
    
    # Update last login time
    user["last_login"] = datetime.utcnow().isoformat()
    
    logger.info(
        f"User logged in with MFA",
        extra={
            "username": user["username"],
            "user_id": user["id"],
            "ip": request.client.host,
            "device_info": json.dumps(totp_data.device_info)
        }
    )
    
    # Return minimal user info
    user_info = {
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "department": user["department"],
        "security_clearance": user["security_clearance"]
    }
    
    return {
        "requires_mfa": False,
        "token": token,
        "user_info": user_info
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, refresh_data: RefreshToken):
    """Refresh access token using a valid refresh token"""
    # In a real app, look up the refresh token in your database
    # For this demo, we'll just search through our in-memory user DB
    
    for username, user_data in USERS_DB.items():
        for stored_token in user_data["refresh_tokens"]:
            if stored_token["token"] == refresh_data.refresh_token:
                # Check if token is expired
                if datetime.utcnow().timestamp() > stored_token["expires_at"]:
                    # Remove expired token
                    user_data["refresh_tokens"].remove(stored_token)
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Refresh token expired",
                    )
                    
                # Check if the token is from the same IP (basic security check)
                if stored_token["ip_address"] != hash_ip_address(request.client.host or ""):
                    logger.warning(
                        f"Refresh token used from different IP",
                        extra={
                            "username": user_data["username"],
                            "user_id": user_data["id"],
                            "ip": request.client.host,
                            "original_ip": stored_token["ip_address"]
                        }
                    )
                    
                # Generate new tokens
                tokens = create_login_tokens(
                    user_data["id"], 
                    user_data["username"], 
                    user_data["security_clearance"], 
                    request
                )
                
                # Remove the used refresh token (one-time use)
                user_data["refresh_tokens"].remove(stored_token)
                
                return tokens
                
    # If we get here, the refresh token was not found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
    )

@router.post("/logout")
async def logout(request: Request, refresh_data: RefreshToken):
    """Invalidate a refresh token on logout"""
    # This would remove the token from the database in a real application
    # Here we just remove it from our in-memory dictionary
    
    for username, user_data in USERS_DB.items():
        for stored_token in user_data["refresh_tokens"]:
            if stored_token["token"] == refresh_data.refresh_token:
                user_data["refresh_tokens"].remove(stored_token)
                logger.info(
                    f"User logged out",
                    extra={
                        "username": user_data["username"],
                        "user_id": user_data["id"],
                        "ip": request.client.host
                    }
                )
                return {"message": "Successfully logged out"}
                
    # Still return success even if token not found to avoid leaking information
    return {"message": "Successfully logged out"} 