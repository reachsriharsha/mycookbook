# FastAPI JWT Token Management System
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import jwt
import secrets
import uuid
from passlib.context import CryptContext
import redis
import json

app = FastAPI()

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 days

# Security setup
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis for storing refresh tokens (use your preferred database)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Pydantic Models
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires
    expires_at: int  # Unix timestamp

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserClaims(BaseModel):
    uid: str
    phone_hash: str  # Don't store actual phone in token
    token_id: str    # Unique token ID for revocation

# Token Generation Functions
def generate_uid() -> str:
    """Generate unique user ID"""
    return f"usr_{uuid.uuid4().hex[:12]}"

def generate_token_id() -> str:
    """Generate unique token ID for tracking/revocation"""
    return f"tok_{uuid.uuid4().hex[:16]}"

def create_access_token(uid: str, phone_hash: str) -> tuple[str, datetime]:
    """
    Create JWT access token with expiration
    Returns: (token, expiration_datetime)
    """
    token_id = generate_token_id()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "uid": uid,
        "phone_hash": phone_hash,
        "token_id": token_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire

def create_refresh_token(uid: str, phone_hash: str) -> tuple[str, datetime]:
    """
    Create refresh token and store in Redis
    Returns: (token, expiration_datetime)
    """
    token_id = generate_token_id()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Refresh token payload (simpler than access token)
    payload = {
        "uid": uid,
        "phone_hash": phone_hash,
        "token_id": token_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Store refresh token in Redis with expiration
    redis_key = f"refresh_token:{uid}:{token_id}"
    redis_client.setex(
        redis_key, 
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        json.dumps({
            "token": token,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expire.isoformat()
        })
    )
    
    return token, expire

def generate_token_pair(uid: str, phone_hash: str) -> TokenResponse:
    """
    Generate both access and refresh tokens
    """
    access_token, access_expire = create_access_token(uid, phone_hash)
    refresh_token, refresh_expire = create_refresh_token(uid, phone_hash)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        expires_at=int(access_expire.timestamp())
    )

# Token Validation Functions
def verify_token(token: str, token_type: str = "access") -> dict:
    """
    Verify JWT token and return payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Check if token is expired
        if datetime.utcnow() > datetime.fromtimestamp(payload.get("exp", 0)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def verify_refresh_token(token: str, uid: str) -> dict:
    """
    Verify refresh token and check if it exists in Redis
    """
    payload = verify_token(token, "refresh")
    
    # Verify the token exists in Redis (not revoked)
    token_id = payload.get("token_id")
    redis_key = f"refresh_token:{uid}:{token_id}"
    
    if not redis_client.exists(redis_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or invalid"
        )
    
    return payload

# Dependency for protecting routes
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to extract and validate access token from request
    """
    token = credentials.credentials
    payload = verify_token(token, "access")
    return payload

# API Endpoints

@app.post("/auth/login", response_model=TokenResponse)
async def login_with_otp(phone: str, otp: str):
    """
    Simulate OTP login - In real implementation, verify OTP first
    """
    # TODO: Verify OTP here
    # For demo, assume OTP is valid
    
    # Hash the phone number for storage
    phone_hash = pwd_context.hash(phone)
    
    # Generate or get existing UID (simulate database lookup)
    uid = generate_uid()  # In real app, get from database
    
    # Generate token pair
    tokens = generate_token_pair(uid, phone_hash)
    
    return tokens

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """
    CLIENT INITIATES: When access token expires, client calls this endpoint
    """
    try:
        # Decode refresh token to get user info
        temp_payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = temp_payload.get("uid")
        
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify refresh token is valid and not revoked
        payload = verify_refresh_token(request.refresh_token, uid)
        
        # Generate new token pair
        new_tokens = generate_token_pair(
            uid=payload["uid"],
            phone_hash=payload["phone_hash"]
        )
        
        # Optionally: Revoke old refresh token for security
        old_token_id = payload.get("token_id")
        if old_token_id:
            redis_client.delete(f"refresh_token:{uid}:{old_token_id}")
        
        return new_tokens
        
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@app.get("/protected/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Protected endpoint example - requires valid access token
    """
    return {
        "uid": current_user["uid"],
        "message": "This is protected data",
        "token_expires_at": current_user["exp"]
    }

@app.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Revoke refresh token(s) for the user
    """
    uid = current_user["uid"]
    
    # Find and delete all refresh tokens for this user
    pattern = f"refresh_token:{uid}:*"
    keys = redis_client.keys(pattern)
    
    if keys:
        redis_client.delete(*keys)
    
    return {"message": "Logged out successfully"}

# Utility endpoint to check token status
@app.get("/auth/token/status")
async def token_status(current_user: dict = Depends(get_current_user)):
    """
    Check current access token status and expiration
    """
    exp_timestamp = current_user["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    time_remaining = exp_datetime - datetime.utcnow()
    
    return {
        "valid": True,
        "uid": current_user["uid"],
        "expires_at": exp_timestamp,
        "expires_in_seconds": int(time_remaining.total_seconds()),
        "token_id": current_user["token_id"]
    }

# Client-side helper functions (for reference)
class TokenManager:
    """
    Client-side token management class
    This shows how CLIENT initiates refresh
    """
    
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
    
    def store_tokens(self, token_response: TokenResponse):
        """Store tokens after login/refresh"""
        self.access_token = token_response.access_token
        self.refresh_token = token_response.refresh_token
        self.expires_at = token_response.expires_at
    
    def is_token_expired(self) -> bool:
        """Check if access token is expired or will expire in 5 minutes"""
        if not self.expires_at:
            return True
        
        # Add 5-minute buffer for refresh
        buffer_time = 5 * 60  # 5 minutes in seconds
        current_timestamp = datetime.utcnow().timestamp()
        
        return current_timestamp >= (self.expires_at - buffer_time)
    
    async def get_valid_token(self) -> str:
        """
        CLIENT LOGIC: Get valid access token, refresh if needed
        This is where CLIENT INITIATES the refresh process
        """
        if self.is_token_expired():
            await self.refresh_tokens()
        
        return self.access_token
    
    async def refresh_tokens(self):
        """
        CLIENT INITIATES: Call refresh endpoint when token expires
        """
        if not self.refresh_token:
            raise Exception("No refresh token available")
        
        # Call the refresh endpoint
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            
            if response.status_code == 200:
                token_data = TokenResponse(**response.json())
                self.store_tokens(token_data)
            else:
                # Refresh failed - redirect to login
                raise Exception("Refresh failed, need to re-authenticate")
    
    async def make_authenticated_request(self, url: str, method: str = "GET", **kwargs):
        """
        Example of how client automatically handles token refresh
        """
        token = await self.get_valid_token()
        
        import httpx
        async with httpx.AsyncClient() as client:
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {token}"
            
            response = await client.request(method, url, headers=headers, **kwargs)
            
            # If token expired during request, try refresh once
            if response.status_code == 401:
                await self.refresh_tokens()
                token = await self.get_valid_token()
                headers["Authorization"] = f"Bearer {token}"
                response = await client.request(method, url, headers=headers, **kwargs)
            
            return response

# Example usage documentation
"""
FLOW SUMMARY:

1. TOKEN GENERATION:
   - Server generates access token (1 hour) + refresh token (7 days)
   - Access token contains: uid, phone_hash, token_id, exp
   - Refresh token stored in Redis with expiration

2. WHO INITIATES REFRESH?
   - CLIENT initiates refresh (not server)
   - Client checks token expiry before each API call
   - Client calls /auth/refresh when needed

3. CLIENT BEHAVIOR:
   - Store both tokens after login
   - Check expiry before API calls (with 5-min buffer)
   - Auto-refresh if expired
   - Retry failed request with new token
   - Redirect to login if refresh fails

4. SERVER BEHAVIOR:
   - Validate tokens on protected endpoints
   - Return 401 if token invalid/expired
   - Generate new token pair on refresh
   - Store refresh tokens in Redis
   - Revoke old tokens on logout

5. SECURITY FEATURES:
   - JWT signed with secret key
   - Refresh token stored server-side (can be revoked)
   - Token rotation on refresh
   - Unique token IDs for tracking
   - No phone numbers in tokens
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)