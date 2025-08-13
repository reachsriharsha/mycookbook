# optimized_main.py - FastAPI Backend with Token Caching and JWT Validation

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, auth
from typing import Dict, Optional, Any
import jwt
import json
import time
import hashlib
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache
import redis.asyncio as redis

# Initialize FastAPI
app = FastAPI(title="Optimized Firebase Auth API", version="1.0.0")

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate("firebase-service-account.json")
    firebase_app = firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"❌ Firebase initialization error: {e}")

# Initialize Redis (optional - comment out if not using Redis)
try:
    redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
except Exception:
    redis_client = None
    print("⚠️  Redis not available, using in-memory cache")

# Security scheme
security = HTTPBearer()

# In-memory cache as fallback
token_cache = {}
CACHE_TTL = 3600  # 1 hour cache TTL

# Pydantic models
class UserInfo(BaseModel):
    uid: str
    phone_number: Optional[str]
    email: Optional[str]
    email_verified: bool
    firebase_claims: Dict
    cached_at: float

class TokenVerificationRequest(BaseModel):
    id_token: str

# Strategy 1: JWT Local Verification (Fastest)
class JWTValidator:
    def __init__(self):
        self.firebase_keys = {}
        self.keys_last_updated = 0
        self.keys_cache_ttl = 3600  # 1 hour
    
    async def get_firebase_public_keys(self) -> Dict[str, str]:
        """Get Firebase public keys for JWT verification"""
        current_time = time.time()
        
        # Check if keys are cached and still valid
        if (self.firebase_keys and 
            current_time - self.keys_last_updated < self.keys_cache_ttl):
            return self.firebase_keys
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
                )
                if response.status_code == 200:
                    self.firebase_keys = response.json()
                    self.keys_last_updated = current_time
                    return self.firebase_keys
        except Exception as e:
            print(f"Failed to fetch Firebase keys: {e}")
        
        return self.firebase_keys
    
    async def verify_jwt_locally(self, token: str, project_id: str) -> Optional[Dict]:
        """Verify JWT token locally without calling Firebase"""
        try:
            # Get public keys
            keys = await self.get_firebase_public_keys()
            if not keys:
                return None
            
            # Decode token header to get key ID
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')
            
            if kid not in keys:
                return None
            
            # Verify JWT signature and claims
            public_key = keys[kid]
            decoded_token = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=project_id,
                issuer=f"https://securetoken.google.com/{project_id}"
            )
            
            # Check token expiration
            if decoded_token.get('exp', 0) < time.time():
                return None
            
            return decoded_token
            
        except Exception as e:
            print(f"JWT local verification failed: {e}")
            return None

jwt_validator = JWTValidator()

# Strategy 2: Caching Layer
async def get_cached_user(token_hash: str) -> Optional[UserInfo]:
    """Get user info from cache"""
    if redis_client:
        try:
            cached_data = await redis_client.get(f"user:{token_hash}")
            if cached_data:
                user_data = json.loads(cached_data)
                return UserInfo(**user_data)
        except Exception as e:
            print(f"Redis cache read error: {e}")
    
    # Fallback to in-memory cache
    if token_hash in token_cache:
        cached_user, cached_time = token_cache[token_hash]
        if time.time() - cached_time < CACHE_TTL:
            return cached_user
        else:
            del token_cache[token_hash]
    
    return None

async def cache_user(token_hash: str, user_info: UserInfo):
    """Cache user info"""
    user_info.cached_at = time.time()
    
    if redis_client:
        try:
            await redis_client.setex(
                f"user:{token_hash}",
                CACHE_TTL,
                user_info.json()
            )
        except Exception as e:
            print(f"Redis cache write error: {e}")
    
    # Always maintain in-memory cache as fallback
    token_cache[token_hash] = (user_info, time.time())

async def verify_token_with_firebase(token: str) -> UserInfo:
    """Verify token with Firebase (fallback method)"""
    try:
        decoded_token = auth.verify_id_token(token)
        return UserInfo(
            uid=decoded_token.get('uid'),
            phone_number=decoded_token.get('phone_number'),
            email=decoded_token.get('email'),
            email_verified=decoded_token.get('email_verified', False),
            firebase_claims=decoded_token,
            cached_at=time.time()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )

# Strategy 3: Multi-tier Verification
async def verify_token_optimized(token: str) -> UserInfo:
    """
    Multi-tier token verification:
    1. Check cache first
    2. Try local JWT verification
    3. Fallback to Firebase verification
    """
    project_id = firebase_app.project_id
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Tier 1: Check cache
    cached_user = await get_cached_user(token_hash)
    if cached_user:
        print("✅ Token verified from cache")
        return cached_user
    
    # Tier 2: Local JWT verification
    jwt_claims = await jwt_validator.verify_jwt_locally(token, project_id)
    if jwt_claims:
        user_info = UserInfo(
            uid=jwt_claims.get('uid'),
            phone_number=jwt_claims.get('phone_number'),
            email=jwt_claims.get('email'),
            email_verified=jwt_claims.get('email_verified', False),
            firebase_claims=jwt_claims,
            cached_at=time.time()
        )
        await cache_user(token_hash, user_info)
        print("✅ Token verified locally (JWT)")
        return user_info
    
    # Tier 3: Firebase verification (fallback)
    print("⚠️  Falling back to Firebase verification")
    user_info = await verify_token_with_firebase(token)
    await cache_user(token_hash, user_info)
    return user_info

# Dependency for token verification
async def verify_token_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInfo:
    """Optimized token verification dependency"""
    try:
        token = credentials.credentials
        return await verify_token_optimized(token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Routes
@app.get("/")
async def root():
    return {"message": "Optimized Firebase Auth API is running"}

@app.post("/auth/verify-token")
async def verify_firebase_token(request: TokenVerificationRequest):
    """Manual token verification endpoint"""
    user_info = await verify_token_optimized(request.id_token)
    return user_info

@app.get("/protected")
async def protected_endpoint(user: UserInfo = Depends(verify_token_dependency)):
    """Fast protected endpoint with optimized auth"""
    return {
        "message": f"Hello {user.phone_number or user.email or user.uid}!",
        "user_info": user,
        "verification_method": "cached" if user.cached_at > time.time() - 60 else "verified"
    }

@app.get("/user/profile")
async def get_user_profile(user: UserInfo = Depends(verify_token_dependency)):
    """Get user profile - uses optimized verification"""
    return user

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    in_memory_count = len(token_cache)
    redis_info = {}
    
    if redis_client:
        try:
            redis_info = await redis_client.info()
        except Exception:
            redis_info = {"error": "Redis unavailable"}
    
    return {
        "in_memory_cache_entries": in_memory_count,
        "redis_info": redis_info,
        "cache_ttl": CACHE_TTL
    }

@app.delete("/cache/clear")
async def clear_cache():
    """Clear all caches"""
    global token_cache
    token_cache.clear()
    
    if redis_client:
        try:
            await redis_client.flushall()
        except Exception as e:
            return {"message": "In-memory cache cleared", "redis_error": str(e)}
    
    return {"message": "All caches cleared"}

 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)