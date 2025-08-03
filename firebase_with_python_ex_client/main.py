# main.py - FastAPI Backend for Firebase Token Verification

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, auth
from typing import Dict, Optional
import json

# Initialize FastAPI
app = FastAPI(title="Firebase Auth Token Verification API", version="1.0.0")

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate("firebase-service-account.json")
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"❌ Firebase initialization error: {e}")

# Security scheme
security = HTTPBearer()

# Pydantic models
class TokenVerificationRequest(BaseModel):
    id_token: str

class UserInfo(BaseModel):
    uid: str
    phone_number: Optional[str]
    email: Optional[str]
    email_verified: bool
    firebase_claims: Dict

class ProtectedResponse(BaseModel):
    message: str
    user_info: UserInfo

@app.get("/")
async def root():
    return {"message": "Firebase Auth Token Verification API is running"}

@app.post("/auth/verify-token", response_model=UserInfo)
async def verify_firebase_token(request: TokenVerificationRequest):
    """
    Verify Firebase ID token and return user information
    """
    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(request.id_token)
        
        # Extract user information
        user_info = UserInfo(
            uid=decoded_token.get('uid'),
            phone_number=decoded_token.get('phone_number'),
            email=decoded_token.get('email'),
            email_verified=decoded_token.get('email_verified', False),
            firebase_claims=decoded_token
        )
        
        print(f"✅ Token verified successfully for user: {user_info.uid}")
        print(f"📱 Phone: {user_info.phone_number}")
        
        return user_info
        
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token"
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token has expired"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token verification failed: {str(e)}"
        )

async def verify_token_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInfo:
    """
    Dependency to verify Firebase token from Authorization header
    """
    try:
        # Extract token from Bearer authorization
        id_token = credentials.credentials
        
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(id_token)
        
        return UserInfo(
            uid=decoded_token.get('uid'),
            phone_number=decoded_token.get('phone_number'),
            email=decoded_token.get('email'),
            email_verified=decoded_token.get('email_verified', False),
            firebase_claims=decoded_token
        )
        
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token verification failed: {str(e)}"
        )

@app.get("/protected", response_model=ProtectedResponse)
async def protected_endpoint(user: UserInfo = Depends(verify_token_dependency)):
    """
    Protected endpoint that requires valid Firebase token
    """
    return ProtectedResponse(
        message=f"Hello {user.phone_number or user.email or user.uid}! This is a protected endpoint.",
        user_info=user
    )

@app.get("/user/profile", response_model=UserInfo)
async def get_user_profile(user: UserInfo = Depends(verify_token_dependency)):
    """
    Get user profile information
    """
    return user

@app.post("/user/custom-claims")
async def set_custom_claims(
    request: dict,
    user: UserInfo = Depends(verify_token_dependency)
):
    """
    Set custom claims for the authenticated user (admin only in real app)
    """
    try:
        # In production, check if user has admin privileges
        auth.set_custom_user_claims(user.uid, request.get("claims", {}))
        return {"message": "Custom claims set successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set custom claims: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)