# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
firebase-admin==6.2.0
PyJWT==2.8.0
python-multipart==0.0.6
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9  # for PostgreSQL
python-dotenv==1.0.0
pydantic==2.5.0
bcrypt==4.1.2

# config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT Configuration
    jwt_secret: str = "your-super-secret-jwt-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 30
    
    # Database Configuration
    database_url: str = "postgresql://user:password@localhost/school_transport"
    
    # Firebase Configuration
    firebase_service_account_path: str = "firebase-service-account.json"
    
    # App Configuration
    app_name: str = "School Transport API"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()

# .env file example
"""
JWT_SECRET=your-super-secret-jwt-key-here
DATABASE_URL=postgresql://username:password@localhost/school_transport_db
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json
DEBUG=True
"""

# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Updated main.py with database integration
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User, DriverProfile
from config import settings
import firebase_admin
from firebase_admin import credentials, auth
import jwt
from datetime import datetime, timedelta
import hashlib

# Initialize Firebase
cred = credentials.Certificate(settings.firebase_service_account_path)
firebase_admin.initialize_app(cred)

app = FastAPI(title=settings.app_name)
security = HTTPBearer()

def hash_phone_number(phone: str) -> str:
    return hashlib.sha256(phone.encode()).hexdigest()

def create_jwt_token(user_id: str, firebase_uid: str) -> tuple[str, datetime]:
    expires_at = datetime.utcnow() + timedelta(days=settings.jwt_expiration_days)
    payload = {
        "user_id": user_id,
        "firebase_uid": firebase_uid,
        "exp": expires_at,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_at

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
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

@app.post("/auth/verify-phone")
async def verify_phone_and_authenticate(
    request: dict,  # {"firebase_id_token": "..."}
    db: Session = Depends(get_db)
):
    try:
        # Verify Firebase token
        decoded_token = auth.verify_id_token(request["firebase_id_token"])
        phone_number = decoded_token.get("phone_number")
        firebase_uid = decoded_token.get("uid")
        
        if not phone_number or not firebase_uid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token data"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        
        if not user:
            # Create new user
            phone_hash = hash_phone_number(phone_number)
            user = User(
                firebase_uid=firebase_uid,
                phone_hash=phone_hash,
                name=decoded_token.get("name")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create JWT token
        jwt_token, expires_at = create_jwt_token(user.id, firebase_uid)
        
        return {
            "token": jwt_token,
            "user_id": user.id,
            "expires_at": expires_at,
            "is_driver": user.is_driver,
            "is_parent": user.is_parent
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )