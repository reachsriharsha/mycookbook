from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: f"usr_{uuid.uuid4().hex[:12]}")
    firebase_uid = Column(String, unique=True, nullable=False, index=True)
    phone_hash = Column(String, nullable=False)  # Hashed phone number
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_driver = Column(Boolean, default=False)
    is_parent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver_profile = relationship("DriverProfile", back_populates="user", uselist=False)
    parent_profile = relationship("ParentProfile", back_populates="user", uselist=False)

class DriverProfile(Base):
    __tablename__ = "driver_profiles"
    
    id = Column(String, primary_key=True, default=lambda: f"drv_{uuid.uuid4().hex[:12]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    license_number = Column(String, nullable=False)
    license_expiry = Column(DateTime, nullable=True)
    vehicle_registration = Column(String, nullable=True)
    vehicle_model = Column(String, nullable=True)
    vehicle_capacity = Column(String, nullable=True)
    background_check_status = Column(String, default="pending")  # pending, approved, rejected
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="driver_profile")

class ParentProfile(Base):
    __tablename__ = "parent_profiles"
    
    id = Column(String, primary_key=True, default=lambda: f"par_{uuid.uuid4().hex[:12]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    emergency_contact = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="parent_profile")
    children = relationship("Child", back_populates="parent")

class Child(Base):
    __tablename__ = "children"
    
    id = Column(String, primary_key=True, default=lambda: f"chd_{uuid.uuid4().hex[:12]}")
    parent_id = Column(String, ForeignKey("parent_profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    school_name = Column(String, nullable=True)
    grade = Column(String, nullable=True)
    pickup_address = Column(Text, nullable=True)
    drop_address = Column(Text, nullable=True)
    emergency_contact = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    parent = relationship("ParentProfile", back_populates="children")

# Database operations example
from sqlalchemy.orm import Session

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_firebase_uid(self, firebase_uid: str) -> User:
        return self.db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    def create_user(self, firebase_uid: str, phone_hash: str, name: str = None) -> User:
        user = User(
            firebase_uid=firebase_uid,
            phone_hash=phone_hash,
            name=name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: str) -> User:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_driver_profile(self, user_id: str, license_number: str, **kwargs) -> DriverProfile:
        # Update user to be a driver
        user = self.get_user_by_id(user_id)
        user.is_driver = True
        
        driver_profile = DriverProfile(
            user_id=user_id,
            license_number=license_number,
            **kwargs
        )
        self.db.add(driver_profile)
        self.db.commit()
        self.db.refresh(driver_profile)
        return driver_profile