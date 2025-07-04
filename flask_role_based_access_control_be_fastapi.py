# backend_api.py - Example backend API using FastAPI
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import jwt
from datetime import datetime, timedelta

app = FastAPI()

# Secret key for JWT
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# Dummy database
USERS_DB = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # In production, use hashed passwords
        "role": "admin",
        "groups": ["admin", "users"],
        "permissions": ["read", "write", "delete", "edit_content", "manage_users"]
    },
    "manager": {
        "username": "manager",
        "password": "manager123",
        "role": "manager",
        "groups": ["managers", "users"],
        "permissions": ["read", "write", "edit_content"]
    },
    "user1": {
        "username": "user1",
        "password": "user123",
        "role": "user",
        "groups": ["users"],
        "permissions": ["read"]
    }
}

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict

class UserResponse(BaseModel):
    username: str
    role: str
    groups: List[str]
    permissions: List[str]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except jwt.PyJWTError:
        return None

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    user = USERS_DB.get(login_data.username)
    
    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_access_token(
        data={"sub": user["username"], "type": "refresh"}, expires_delta=refresh_token_expires
    )
    
    user_data = {
        "username": user["username"],
        "role": user["role"],
        "groups": user["groups"],
        "permissions": user["permissions"]
    }
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user_data
    }

@app.get("/api/auth/user", response_model=UserResponse)
async def get_current_user(token: str = Depends(lambda: None)):
    # In a real implementation, you'd extract the token from the Authorization header
    # For this example, we'll assume it's passed somehow
    
    # This is a simplified example - in reality, you'd use FastAPI's security utilities
    # to extract the token from the Authorization header
    pass

# Simplified version for demonstration
@app.get("/api/auth/user")
async def get_current_user_simple():
    # This endpoint should validate the Bearer token from Authorization header
    # and return user info. For demo purposes, returning a sample response
    return {
        "username": "admin",
        "role": "admin",
        "groups": ["admin", "users"],
        "permissions": ["read", "write", "delete", "edit_content", "manage_users"]
    }

@app.post("/api/auth/refresh")
async def refresh_token(refresh_data: dict):
    # Implement token refresh logic here
    # Verify refresh token and issue new access token
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)