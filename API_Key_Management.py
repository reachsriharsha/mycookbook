# API Key Management System - Complete Implementation

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
import sqlite3
import bcrypt
from functools import wraps
import logging

# Configuration
class APIKeyConfig:
    KEY_LENGTH = 32
    PREFIX = "sk-"  # Similar to OpenAI's format
    HASH_ROUNDS = 12
    DEFAULT_RATE_LIMIT = 1000  # requests per hour
    DEFAULT_EXPIRY_DAYS = 365

class APIKeyStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"

@dataclass
class APIKey:
    id: str
    name: str
    key_hash: str
    user_id: str
    status: APIKeyStatus
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    rate_limit: int
    permissions: List[str]
    usage_count: int = 0

@dataclass
class RateLimitInfo:
    requests_made: int
    window_start: datetime
    limit: int

class APIKeyManager:
    def __init__(self, db_path: str = "api_keys.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
        self._rate_limit_cache = {}  # In production, use Redis
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # API Keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                key_hash TEXT NOT NULL UNIQUE,
                user_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP,
                last_used_at TIMESTAMP,
                rate_limit INTEGER NOT NULL,
                permissions TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0
            )
        """)
        
        # Usage logs table for analytics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key_id TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                response_code INTEGER,
                FOREIGN KEY (api_key_id) REFERENCES api_keys (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def generate_api_key(self, 
                        name: str, 
                        user_id: str, 
                        permissions: List[str] = None,
                        rate_limit: int = None,
                        expires_in_days: int = None) -> tuple[str, APIKey]:
        """Generate a new API key"""
        # Generate random key
        random_bytes = secrets.token_bytes(APIKeyConfig.KEY_LENGTH)
        key_string = APIKeyConfig.PREFIX + secrets.token_urlsafe(APIKeyConfig.KEY_LENGTH)
        
        # Hash the key for storage
        key_hash = bcrypt.hashpw(key_string.encode(), bcrypt.gensalt(rounds=APIKeyConfig.HASH_ROUNDS))
        
        # Create API key object
        api_key = APIKey(
            id=secrets.token_urlsafe(16),
            name=name,
            key_hash=key_hash.decode(),
            user_id=user_id,
            status=APIKeyStatus.ACTIVE,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days or APIKeyConfig.DEFAULT_EXPIRY_DAYS),
            last_used_at=None,
            rate_limit=rate_limit or APIKeyConfig.DEFAULT_RATE_LIMIT,
            permissions=permissions or ["read"],
            usage_count=0
        )
        
        # Store in database
        self._store_api_key(api_key)
        
        return key_string, api_key
    
    def _store_api_key(self, api_key: APIKey):
        """Store API key in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO api_keys 
            (id, name, key_hash, user_id, status, created_at, expires_at, 
             last_used_at, rate_limit, permissions, usage_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            api_key.id, api_key.name, api_key.key_hash, api_key.user_id,
            api_key.status.value, api_key.created_at, api_key.expires_at,
            api_key.last_used_at, api_key.rate_limit, 
            ",".join(api_key.permissions), api_key.usage_count
        ))
        
        conn.commit()
        conn.close()
    
    def validate_api_key(self, key_string: str) -> Optional[APIKey]:
        """Validate an API key and return APIKey object if valid"""
        if not key_string.startswith(APIKeyConfig.PREFIX):
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all active keys (in production, add indexing)
        cursor.execute("""
            SELECT * FROM api_keys 
            WHERE status = ? AND (expires_at IS NULL OR expires_at > ?)
        """, (APIKeyStatus.ACTIVE.value, datetime.utcnow()))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Check each key hash
        for row in rows:
            stored_hash = row[2].encode()  # key_hash column
            if bcrypt.checkpw(key_string.encode(), stored_hash):
                # Convert row to APIKey object
                api_key = APIKey(
                    id=row[0],
                    name=row[1],
                    key_hash=row[2],
                    user_id=row[3],
                    status=APIKeyStatus(row[4]),
                    created_at=datetime.fromisoformat(row[5]),
                    expires_at=datetime.fromisoformat(row[6]) if row[6] else None,
                    last_used_at=datetime.fromisoformat(row[7]) if row[7] else None,
                    rate_limit=row[8],
                    permissions=row[9].split(",") if row[9] else [],
                    usage_count=row[10]
                )
                
                # Update last used timestamp
                self._update_last_used(api_key.id)
                return api_key
        
        return None
    
    def check_rate_limit(self, api_key: APIKey) -> tuple[bool, RateLimitInfo]:
        """Check if API key has exceeded rate limit"""
        key_id = api_key.id
        now = datetime.utcnow()
        window_start = now.replace(minute=0, second=0, microsecond=0)  # Hourly window
        
        if key_id not in self._rate_limit_cache:
            self._rate_limit_cache[key_id] = RateLimitInfo(0, window_start, api_key.rate_limit)
        
        rate_info = self._rate_limit_cache[key_id]
        
        # Reset if new window
        if rate_info.window_start < window_start:
            rate_info.requests_made = 0
            rate_info.window_start = window_start
        
        # Check limit
        if rate_info.requests_made >= rate_info.limit:
            return False, rate_info
        
        # Increment counter
        rate_info.requests_made += 1
        return True, rate_info
    
    def _update_last_used(self, api_key_id: str):
        """Update last used timestamp and increment usage count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE api_keys 
            SET last_used_at = ?, usage_count = usage_count + 1
            WHERE id = ?
        """, (datetime.utcnow(), api_key_id))
        
        conn.commit()
        conn.close()
    
    def revoke_api_key(self, api_key_id: str) -> bool:
        """Revoke an API key"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE api_keys SET status = ? WHERE id = ?
        """, (APIKeyStatus.REVOKED.value, api_key_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def log_api_usage(self, api_key_id: str, endpoint: str, method: str, 
                     ip_address: str = None, user_agent: str = None, 
                     response_code: int = 200):
        """Log API usage for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO api_usage_logs 
            (api_key_id, endpoint, method, timestamp, ip_address, user_agent, response_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (api_key_id, endpoint, method, datetime.utcnow(), 
              ip_address, user_agent, response_code))
        
        conn.commit()
        conn.close()

# Flask/FastAPI Integration
from flask import Flask, request, jsonify, g

app = Flask(__name__)
api_manager = APIKeyManager()

def require_api_key(permissions_required: List[str] = None):
    """Decorator to require API key authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key from header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Missing or invalid Authorization header'}), 401
            
            api_key_string = auth_header.split(' ')[1]
            
            # Validate API key
            api_key = api_manager.validate_api_key(api_key_string)
            if not api_key:
                return jsonify({'error': 'Invalid API key'}), 401
            
            # Check permissions
            if permissions_required:
                if not any(perm in api_key.permissions for perm in permissions_required):
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Check rate limit
            allowed, rate_info = api_manager.check_rate_limit(api_key)
            if not allowed:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': 3600  # seconds until next window
                }), 429
            
            # Log usage
            api_manager.log_api_usage(
                api_key.id, 
                request.endpoint or request.path,
                request.method,
                request.remote_addr,
                request.user_agent.string if request.user_agent else None
            )
            
            # Store API key in request context
            g.api_key = api_key
            g.rate_limit_remaining = rate_info.limit - rate_info.requests_made
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Example API endpoints
@app.route('/api/data', methods=['GET'])
@require_api_key(['read', 'data'])
def get_data():
    """Example protected endpoint"""
    return jsonify({
        'data': 'This is protected data',
        'user_id': g.api_key.user_id,
        'rate_limit_remaining': g.rate_limit_remaining
    })

@app.route('/api/admin/keys', methods=['POST'])
@require_api_key(['admin'])
def create_api_key():
    """Create new API key (admin only)"""
    data = request.json
    key_string, api_key = api_manager.generate_api_key(
        name=data['name'],
        user_id=data['user_id'],
        permissions=data.get('permissions', ['read']),
        rate_limit=data.get('rate_limit'),
        expires_in_days=data.get('expires_in_days')
    )
    
    return jsonify({
        'key': key_string,  # Only return once!
        'id': api_key.id,
        'name': api_key.name,
        'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None
    })

if __name__ == '__main__':
    # Example usage
    manager = APIKeyManager()
    
    # Generate a test API key
    key, api_key_obj = manager.generate_api_key(
        name="Test Key",
        user_id="user123",
        permissions=["read", "write"]
    )
    
    print(f"Generated API Key: {key}")
    print(f"Key ID: {api_key_obj.id}")
    
    # Test validation
    validated = manager.validate_api_key(key)
    print(f"Validation result: {validated.name if validated else 'Invalid'}")