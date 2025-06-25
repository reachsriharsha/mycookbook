from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, auth
import jwt
from datetime import datetime, timedelta
import hashlib
import uuid
from typing import Optional
import os

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/your/firebase-service-account.json")
firebase_admin.initialize_app(cred)

app = FastAPI()
security = HTTPBearer()

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 30

# Pydantic Models
class PhoneAuthRequest(BaseModel):
    firebase_id_token: str

class AuthResponse(BaseModel):
    token: str
    user_id: str
    expires_at: datetime

class User(BaseModel):
    id: str
    firebase_uid: str
    phone_hash: str
    name: Optional[str] = None
    driver_license: Optional[str] = None
    created_at: datetime

# In-memory storage (replace with your database)
users_db = {}

def hash_phone_number(phone: str) -> str:
    """Hash phone number for privacy"""
    return hashlib.sha256(phone.encode()).hexdigest()

def generate_user_id() -> str:
    """Generate unique user ID"""
    return f"usr_{uuid.uuid4().hex[:12]}"

def create_jwt_token(user_id: str, firebase_uid: str) -> tuple[str, datetime]:
    """Create JWT token for the user"""
    expires_at = datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    payload = {
        "user_id": user_id,
        "firebase_uid": firebase_uid,
        "exp": expires_at,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expires_at

async def verify_firebase_token(firebase_token: str) -> dict:
    """Verify Firebase ID token and return decoded claims"""
    try:
        decoded_token = auth.verify_id_token(firebase_token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {str(e)}"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        user = users_db.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.post("/auth/verify-phone", response_model=AuthResponse)
async def verify_phone_and_authenticate(request: PhoneAuthRequest):
    """
    Verify Firebase OTP token and create backend session
    """
    # Verify Firebase ID token
    firebase_claims = await verify_firebase_token(request.firebase_id_token)
    
    phone_number = firebase_claims.get("phone_number")
    firebase_uid = firebase_claims.get("uid")
    
    if not phone_number or not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number or UID not found in token"
        )
    
    # Hash phone number for privacy
    phone_hash = hash_phone_number(phone_number)
    
    # Check if user exists
    existing_user = None
    for user in users_db.values():
        if user["firebase_uid"] == firebase_uid:
            existing_user = user
            break
    
    if existing_user:
        user_id = existing_user["id"]
    else:
        # Create new user
        user_id = generate_user_id()
        new_user = {
            "id": user_id,
            "firebase_uid": firebase_uid,
            "phone_hash": phone_hash,
            "name": firebase_claims.get("name"),
            "created_at": datetime.utcnow()
        }
        users_db[user_id] = new_user
    
    # Create JWT token
    jwt_token, expires_at = create_jwt_token(user_id, firebase_uid)
    
    return AuthResponse(
        token=jwt_token,
        user_id=user_id,
        expires_at=expires_at
    )

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "user_id": current_user["id"],
        "name": current_user.get("name"),
        "created_at": current_user["created_at"]
        # Don't return sensitive data like phone_hash
    }

@app.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (in production, you'd add token to blacklist)"""
    return {"message": "Logged out successfully"}

# Protected route example
@app.get("/rides/my-rides")
async def get_my_rides(current_user: dict = Depends(get_current_user)):
    """Get rides for the current user"""
    user_id = current_user["id"]
    # Your business logic here
    return {"rides": [], "driver_id": user_id}

@app.post("/driver/register")
async def register_driver(
    license_number: str,
    vehicle_details: dict,
    current_user: dict = Depends(get_current_user)
):
    """Register user as a driver"""
    user_id = current_user["id"]
    
    # Update user with driver information
    users_db[user_id].update({
        "driver_license": license_number,
        "vehicle_details": vehicle_details,
        "is_driver": True,
        "driver_registered_at": datetime.utcnow()
    })
    
    return {"message": "Driver registration successful", "driver_id": user_id}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)