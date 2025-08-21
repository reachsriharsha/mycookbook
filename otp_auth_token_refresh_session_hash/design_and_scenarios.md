
# so when user does not reqire the username and password, how the unique things are managed? since phone number passing over network is not considered good for security reason?

Excellent security question! You're absolutely right that passing phone numbers over the network repeatedly isn't ideal. Let me explain how unique identification is managed securely in phone-based authentication systems.

## How Unique Identity is Managed Without Username/Password

1. Phone Number → Unique User ID Mapping
During the initial authentication flow:

Phone number is sent only once during registration/first login
Server generates a permanent unique user ID (UUID/UID)
This UID is stored in the database linked to the phone number
Tokens contain the UID, not the phone number

```svg
<svg viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="1200" height="800" fill="#1a1a1a"/>
  
  <!-- Title -->
  <text x="600" y="30" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="bold">Secure Identity Management - Phone to UID Mapping</text>
  
  <!-- Phase 1: Initial Registration -->
  <rect x="50" y="60" width="350" height="200" fill="#263238" stroke="#4a90e2" stroke-width="2" rx="8"/>
  <text x="225" y="85" text-anchor="middle" fill="#ffeb3b" font-size="14" font-weight="bold">Phase 1: Initial Registration (Phone Number Used)</text>
  
  <!-- User -->
  <rect x="70" y="110" width="80" height="30" fill="#2d4059" stroke="#4a90e2" stroke-width="1" rx="5"/>
  <text x="110" y="130" text-anchor="middle" fill="#ffffff" font-size="10">User</text>
  
  <!-- Server -->
  <rect x="200" y="110" width="80" height="30" fill="#2d4059" stroke="#4a90e2" stroke-width="1" rx="5"/>
  <text x="240" y="130" text-anchor="middle" fill="#ffffff" font-size="10">Server</text>
  
  <!-- Database -->
  <rect x="310" y="110" width="80" height="30" fill="#2d4059" stroke="#4a90e2" stroke-width="1" rx="5"/>
  <text x="350" y="130" text-anchor="middle" fill="#ffffff" font-size="10">Database</text>
  
  <!-- Flow arrows and text -->
  <line x1="110" y1="150" x2="240" y2="150" stroke="#4a90e2" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="175" y="145" text-anchor="middle" fill="#4a90e2" font-size="9">+1234567890</text>
  
  <line x1="240" y1="170" x2="350" y2="170" stroke="#4a90e2" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="295" y="165" text-anchor="middle" fill="#4a90e2" font-size="9">Generate UID</text>
  
  <rect x="200" y="185" width="160" height="60" fill="#37474f" rx="5"/>
  <text x="280" y="200" text-anchor="middle" fill="#ffffff" font-size="9">Database Record:</text>
  <text x="280" y="215" text-anchor="middle" fill="#81c784" font-size="9">UID: usr_abc123xyz</text>
  <text x="280" y="230" text-anchor="middle" fill="#81c784" font-size="9">Phone: +1234567890</text>
  <text x="280" y="245" text-anchor="middle" fill="#81c784" font-size="9">Created: 2024-01-15</text>
  
  <!-- Phase 2: Subsequent API Calls -->
  <rect x="450" y="60" width="350" height="280" fill="#263238" stroke="#8bc34a" stroke-width="2" rx="8"/>
  <text x="625" y="85" text-anchor="middle" fill="#ffeb3b" font-size="14" font-weight="bold">Phase 2: All Future API Calls (No Phone Number)</text>
  
  <!-- Actors -->
  <rect x="470" y="110" width="80" height="30" fill="#2d4059" stroke="#8bc34a" stroke-width="1" rx="5"/>
  <text x="510" y="130" text-anchor="middle" fill="#ffffff" font-size="10">Mobile App</text>
  
  <rect x="610" y="110" width="80" height="30" fill="#2d4059" stroke="#8bc34a" stroke-width="1" rx="5"/>
  <text x="650" y="130" text-anchor="middle" fill="#ffffff" font-size="10">API Server</text>
  
  <rect x="720" y="110" width="70" height="30" fill="#2d4059" stroke="#8bc34a" stroke-width="1" rx="5"/>
  <text x="755" y="130" text-anchor="middle" fill="#ffffff" font-size="10">Database</text>
  
  <!-- API Call -->
  <line x1="510" y1="160" x2="650" y2="160" stroke="#8bc34a" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="580" y="155" text-anchor="middle" fill="#8bc34a" font-size="9">Authorization: Bearer TOKEN</text>
  
  <!-- Token Structure -->
  <rect x="470" y="180" width="190" height="80" fill="#37474f" rx="5"/>
  <text x="565" y="195" text-anchor="middle" fill="#ffffff" font-size="9">JWT Token Payload:</text>
  <text x="565" y="210" text-anchor="middle" fill="#81c784" font-size="9">{</text>
  <text x="565" y="225" text-anchor="middle" fill="#81c784" font-size="9">  "uid": "usr_abc123xyz",</text>
  <text x="565" y="240" text-anchor="middle" fill="#81c784" font-size="9">  "exp": 1640995200</text>
  <text x="565" y="255" text-anchor="middle" fill="#81c784" font-size="9">}</text>
  
  <!-- Database Query -->
  <line x1="650" y1="280" x2="755" y2="280" stroke="#8bc34a" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="702" y="275" text-anchor="middle" fill="#8bc34a" font-size="9">Query by UID</text>
  
  <rect x="680" y="295" width="150" height="40" fill="#37474f" rx="5"/>
  <text x="755" y="310" text-anchor="middle" fill="#ffffff" font-size="9">SELECT * FROM users</text>
  <text x="755" y="325" text-anchor="middle" fill="#ffffff" font-size="9">WHERE uid = 'usr_abc123xyz'</text>
  
  <!-- Security Benefits Box -->
  <rect x="850" y="60" width="320" height="400" fill="#1b5e20" stroke="#4caf50" stroke-width="2" rx="8"/>
  <text x="1010" y="85" text-anchor="middle" fill="#ffeb3b" font-size="14" font-weight="bold">Security Benefits</text>
  
  <text x="870" y="110" fill="#81c784" font-size="12" font-weight="bold">✓ Phone Number Protection:</text>
  <text x="870" y="130" fill="#ffffff" font-size="10">• Phone sent only during initial auth</text>
  <text x="870" y="145" fill="#ffffff" font-size="10">• Never included in API calls</text>
  <text x="870" y="160" fill="#ffffff" font-size="10">• Stored encrypted in database</text>
  
  <text x="870" y="185" fill="#81c784" font-size="12" font-weight="bold">✓ UID Benefits:</text>
  <text x="870" y="205" fill="#ffffff" font-size="10">• Random, non-guessable</text>
  <text x="870" y="220" fill="#ffffff" font-size="10">• No personal info revealed</text>
  <text x="870" y="235" fill="#ffffff" font-size="10">• Can be rotated if compromised</text>
  
  <text x="870" y="260" fill="#81c784" font-size="12" font-weight="bold">✓ Token Security:</text>
  <text x="870" y="280" fill="#ffffff" font-size="10">• Contains UID, not phone</text>
  <text x="870" y="295" fill="#ffffff" font-size="10">• Signed and encrypted (JWT)</text>
  <text x="870" y="310" fill="#ffffff" font-size="10">• Short expiration times</text>
  
  <text x="870" y="335" fill="#81c784" font-size="12" font-weight="bold">✓ Network Traffic:</text>
  <text x="870" y="355" fill="#ffffff" font-size="10">• No PII in regular API calls</text>
  <text x="870" y="370" fill="#ffffff" font-size="10">• Minimal attack surface</text>
  <text x="870" y="385" fill="#ffffff" font-size="10">• Phone stored securely server-side</text>
  
  <text x="870" y="410" fill="#81c784" font-size="12" font-weight="bold">✓ Compliance:</text>
  <text x="870" y="430" fill="#ffffff" font-size="10">• GDPR/privacy friendly</text>
  <text x="870" y="445" fill="#ffffff" font-size="10">• Reduced data exposure</text>
  
  <!-- Additional Security Measures -->
  <rect x="50" y="380" width="750" height="200" fill="#263238" stroke="#ff9800" stroke-width="2" rx="8"/>
  <text x="425" y="405" text-anchor="middle" fill="#ffeb3b" font-size="14" font-weight="bold">Additional Security Measures for Phone Number Protection</text>
  
  <!-- Column 1 -->
  <text x="70" y="435" fill="#ff9800" font-size="12" font-weight="bold">1. Encryption at Rest:</text>
  <text x="70" y="455" fill="#ffffff" font-size="10">• Phone numbers encrypted in DB</text>
  <text x="70" y="470" fill="#ffffff" font-size="10">• Use AES-256 encryption</text>
  <text x="70" y="485" fill="#ffffff" font-size="10">• Separate encryption keys</text>
  
  <text x="70" y="510" fill="#ff9800" font-size="12" font-weight="bold">2. Hashing for Lookups:</text>
  <text x="70" y="530" fill="#ffffff" font-size="10">• Hash phone for quick lookups</text>
  <text x="70" y="545" fill="#ffffff" font-size="10">• Use salt + bcrypt/scrypt</text>
  <text x="70" y="560" fill="#ffffff" font-size="10">• Store hash separately</text>
  
  <!-- Column 2 -->
  <text x="280" y="435" fill="#ff9800" font-size="12" font-weight="bold">3. Network Security:</text>
  <text x="280" y="455" fill="#ffffff" font-size="10">• HTTPS/TLS 1.3 encryption</text>
  <text x="280" y="470" fill="#ffffff" font-size="10">• Certificate pinning</text>
  <text x="280" y="485" fill="#ffffff" font-size="10">• Request/response encryption</text>
  
  <text x="280" y="510" fill="#ff9800" font-size="12" font-weight="bold">4. Access Controls:</text>
  <text x="280" y="530" fill="#ffffff" font-size="10">• Limited phone access roles</text>
  <text x="280" y="545" fill="#ffffff" font-size="10">• Audit logs for phone queries</text>
  <text x="280" y="560" fill="#ffffff" font-size="10">• Rate limiting on auth endpoints</text>
  
  <!-- Column 3 -->
  <text x="490" y="435" fill="#ff9800" font-size="12" font-weight="bold">5. Token Design:</text>
  <text x="490" y="455" fill="#ffffff" font-size="10">• UID-based tokens only</text>
  <text x="490" y="470" fill="#ffffff" font-size="10">• No phone in JWT payload</text>
  <text x="490" y="485" fill="#ffffff" font-size="10">• Short-lived access tokens</text>
  
  <text x="490" y="510" fill="#ff9800" font-size="12" font-weight="bold">6. Data Minimization:</text>
  <text x="490" y="530" fill="#ffffff" font-size="10">• Phone used only for auth</text>
  <text x="490" y="545" fill="#ffffff" font-size="10">• Never logged in plain text</text>
  <text x="490" y="560" fill="#ffffff" font-size="10">• Automatic data retention limits</text>
  
  <!-- Database Schema Example -->
  <rect x="50" y="620" width="400" height="150" fill="#37474f" stroke="#4a90e2" stroke-width="2" rx="8"/>
  <text x="250" y="645" text-anchor="middle" fill="#ffeb3b" font-size="14" font-weight="bold">Secure Database Schema</text>
  
  <text x="70" y="670" fill="#81c784" font-size="11" font-family="monospace">users_table:</text>
  <text x="70" y="690" fill="#ffffff" font-size="10" font-family="monospace">├── uid (PRIMARY KEY): "usr_abc123xyz789"</text>
  <text x="70" y="705" fill="#ffffff" font-size="10" font-family="monospace">├── phone_hash: "bcrypt_hash_of_phone"</text>
  <text x="70" y="720" fill="#ffffff" font-size="10" font-family="monospace">├── phone_encrypted: "AES_encrypted_phone"</text>
  <text x="70" y="735" fill="#ffffff" font-size="10" font-family="monospace">├── created_at: "2024-01-15T10:30:00Z"</text>
  <text x="70" y="750" fill="#ffffff" font-size="10" font-family="monospace">└── last_login: "2024-01-16T14:22:15Z"</text>
  
  <!-- Token Example -->
  <rect x="500" y="620" width="450" height="150" fill="#37474f" stroke="#4a90e2" stroke-width="2" rx="8"/>
  <text x="725" y="645" text-anchor="middle" fill="#ffeb3b" font-size="14" font-weight="bold">Secure JWT Token Structure</text>
  
  <text x="520" y="670" fill="#81c784" font-size="11" font-family="monospace">Header:</text>
  <text x="520" y="685" fill="#ffffff" font-size="10" font-family="monospace">{"alg": "HS256", "typ": "JWT"}</text>
  
  <text x="520" y="705" fill="#81c784" font-size="11" font-family="monospace">Payload:</text>
  <text x="520" y="720" fill="#ffffff" font-size="10" font-family="monospace">{</text>
  <text x="520" y="735" fill="#ffffff" font-size="10" font-family="monospace">  "uid": "usr_abc123xyz789",  // No phone!</text>
  <text x="520" y="750" fill="#ffffff" font-size="10" font-family="monospace">  "exp": 1640995200, "iat": 1640991600</text>
  <text x="520" y="765" fill="#ffffff" font-size="10" font-family="monospace">}</text>
  
  <!-- Arrow marker definition -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#4a90e2"/>
    </marker>
  </defs>
</svg>
```

# Key Security Strategies:
1. Phone Number → UID Mapping Process

Registration Flow:
Phone (+1234567890) → Server generates UID (usr_abc123xyz) → Stored in DB
Future API Calls:
Token contains UID → Server looks up user by UID → No phone in network traffic
2. What Travels Over Network vs What Doesn't
❌ Never sent after initial auth:

Phone number in plain text
Any personally identifiable information
Direct phone references

✅ Always sent in API calls:

JWT tokens containing only UID
Encrypted, signed tokens
Anonymous user identifiers

3. Database Security for Phone Numbers
Storage Strategy:

Encrypted: Phone numbers encrypted at rest using AES-256
Hashed: Create bcrypt hash for quick lookups during auth
Separated: Store encryption keys separately from data
Indexed: Hash-based indexing for performance without exposing data

4. Real-world Example Flow

Initial Registration:
User sends: "+1234567890" + OTP
Server creates: UID = "usr_7f8a9b2c1d"
Database stores: {uid: "usr_7f8a9b2c1d", phone_encrypted: "...", phone_hash: "..."}

All Future API Calls:
Token payload: {"uid": "usr_7f8a9b2c1d", "exp": 1640995200}
Network traffic: Only contains UID, never phone number

5. Why This Approach is Secure

Minimal PII Exposure: Phone number never travels in regular API calls
Unlinkability: UID cannot be traced back to phone without database access
Rotation Capability: UIDs can be changed if compromised
Compliance: Meets GDPR and privacy requirements
Performance: Fast lookups using UID instead of encrypted phone searches

This approach gives you the convenience of phone-based auth while maintaining the security principle of data minimization - only the minimum necessary data (UID) travels over the network for regular operations.

# How to generate the access token, refresh token and expirey time? and after expeiry who initiates to get new token? show me fastapi code for the same.

```python 
#Refer code in otp_auth.py file

```
Key Points About Token Management:
1. Who Initiates Token Refresh?
CLIENT initiates refresh, not the server!
The client is responsible for:

Checking token expiry before API calls
Calling /auth/refresh when needed
Retrying failed requests with new tokens

2. Token Generation Process:

```python
# Access Token (Short-lived - 1 hour)
{
  "uid": "usr_abc123",
  "phone_hash": "bcrypt_hash", 
  "token_id": "tok_unique_id",
  "exp": 1640995200,
  "type": "access"
}


# Refresh Token (Long-lived - 7 days)
{
  "uid": "usr_abc123", 
  "token_id": "tok_unique_id",
  "exp": 1641600000,
  "type": "refresh"
}
```
3. Client-Side Token Refresh Logic:

```python
# Client checks before each API call:
if token_expires_in_5_minutes():
    await refresh_tokens()

# Make API call with fresh token
response = await api_call_with_token()

# If 401, try refresh once more
if response.status == 401:
    await refresh_tokens()
    response = await retry_api_call()
```
4. Security Best Practices Implemented:

Token Rotation: New refresh token issued on each refresh
Server-side Storage: Refresh tokens stored in Redis (can be revoked)
Unique Token IDs: Each token has unique ID for tracking/revocation
No PII in Tokens: Only UID and phone hash, never actual phone number
Automatic Expiry: Redis automatically deletes expired tokens


# what is the purpose of including the token_id int the payload  , which is being sent to jwt.encode?

Excellent question! The token_id in the JWT payload serves several critical security and operational purposes. Let me explain why it's essential:
1. Token Revocation & Blacklisting
Without token_id, you cannot revoke individual JWT tokens because JWTs are stateless. The token_id makes them "semi-stateless" by allowing server-side tracking.


```python
# Without token_id - PROBLEM:
# If user's phone is stolen, you can't revoke just that device's token
# You'd have to revoke ALL tokens by changing the SECRET_KEY (affects all users!)

# With token_id - SOLUTION:
@app.post("/auth/revoke-token")
async def revoke_token(token_id: str):
    # Add to blacklist
    redis_client.set(f"blacklisted_token:{token_id}", "revoked", ex=3600)
    return {"message": "Token revoked"}

# Check blacklist in token validation
def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    token_id = payload.get("token_id")
    
    # Check if token is blacklisted
    if redis_client.exists(f"blacklisted_token:{token_id}"):
        raise HTTPException(status_code=401, detail="Token revoked")
    
    return payload
```
2. Multi-Device Session Management
Users can have multiple devices logged in simultaneously. token_id helps track and manage each session independently.

```python
# Track active sessions per user
@app.get("/auth/sessions")
async def get_active_sessions(current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    
    # Find all active tokens for this user
    pattern = f"refresh_token:{uid}:*"
    active_sessions = []
    
    for key in redis_client.keys(pattern):
        session_data = redis_client.get(key)
        token_id = key.split(":")[-1]  # Extract token_id
        active_sessions.append({
            "token_id": token_id,
            "created_at": session_data["created_at"],
            "device_info": "iPhone 14",  # You can store device info
        })
    
    return {"active_sessions": active_sessions}

@app.post("/auth/revoke-session/{token_id}")
async def revoke_specific_session(token_id: str, current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    
    # Revoke specific device/session
    redis_client.delete(f"refresh_token:{uid}:{token_id}")
    redis_client.set(f"blacklisted_token:{token_id}", "revoked", ex=3600)
    
    return {"message": f"Session {token_id} revoked"}
```
3. Security Breach Response
If you detect suspicious activity, you can revoke specific tokens without affecting other users or sessions.
```python
# Emergency: Revoke all tokens for a compromised user
@app.post("/admin/emergency-revoke/{uid}")
async def emergency_revoke_user(uid: str):
    # Get all active token IDs for this user
    pattern = f"refresh_token:{uid}:*"
    token_keys = redis_client.keys(pattern)
    
    for key in token_keys:
        token_id = key.split(":")[-1]
        # Blacklist the access token
        redis_client.set(f"blacklisted_token:{token_id}", "security_breach", ex=3600)
        # Delete refresh token
        redis_client.delete(key)
    
    return {"message": f"All tokens revoked for user {uid}"}
```

4. Token Rotation Security
token_id ensures that when you refresh tokens, the old ones become invalid.

```python
@app.post("/auth/refresh")
async def refresh_access_token(request: RefreshTokenRequest):
    # Verify old refresh token
    payload = verify_refresh_token(request.refresh_token, uid)
    old_token_id = payload["token_id"]
    
    # Generate NEW tokens with NEW token_ids
    new_tokens = generate_token_pair(uid, phone_hash)
    
    # CRITICAL: Revoke old tokens using token_id
    redis_client.delete(f"refresh_token:{uid}:{old_token_id}")
    redis_client.set(f"blacklisted_token:{old_token_id}", "rotated", ex=3600)
    
    return new_tokens
```


5. Audit Logging & Analytics
Track token usage patterns, detect anomalies, and maintain security logs.

```python
def log_token_usage(token_id: str, action: str, ip_address: str):
    log_entry = {
        "token_id": token_id,
        "action": action,
        "ip_address": ip_address,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Store in audit log
    redis_client.lpush(f"token_audit:{token_id}", json.dumps(log_entry))
    redis_client.expire(f"token_audit:{token_id}", 86400 * 30)  # 30 days

# In your protected endpoint
@app.get("/protected/data")
async def protected_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    # Log token usage
    log_token_usage(
        token_id=current_user["token_id"],
        action="data_access",
        ip_address=request.client.host
    )
    
    return {"data": "sensitive information"}
```
6. Rate Limiting Per Token
Implement rate limiting per token/session rather than per user.

```python
from fastapi import Request
import time

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Extract token_id from JWT
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_id = payload.get("token_id")
            
            if token_id:
                # Rate limit per token_id
                rate_key = f"rate_limit:{token_id}"
                current_count = redis_client.incr(rate_key)
                
                if current_count == 1:
                    redis_client.expire(rate_key, 60)  # 1 minute window
                
                if current_count > 100:  # 100 requests per minute per token
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Rate limit exceeded for this session"}
                    )
        except:
            pass
    
    response = await call_next(request)
    return response
```

What Happens WITHOUT token_id?

```python
# WITHOUT token_id - Security problems:
{
  "uid": "usr_abc123",
  "exp": 1640995200
}

# Problems:
# ❌ Can't revoke individual tokens
# ❌ Can't track multiple sessions
# ❌ Can't rotate tokens securely  
# ❌ No audit trail per session
# ❌ All-or-nothing token management
```
Summary:
The token_id transforms JWT from being purely stateless to semi-stateless, giving you:

Individual token control (revoke, track, audit)
Multi-session management (different devices)
Security breach response (surgical token revocation)
Token rotation (invalidate old tokens)
Granular rate limiting (per session, not per user)
Audit logging (track token usage patterns)

It's a small addition that provides massive security and operational benefits without significantly impacting the stateless nature of JWTs.

# Then what is the reason of storing the phone hash in the payload which is sent to jwt token. provide the reason behind these, no need to change code or any other thing

1. Fast Authorization Without Database Lookups
Without phone_hash in JWT, every protected API call would require a database query to get user info:

```python
# WITHOUT phone_hash in JWT - SLOW:
def get_current_user(token):
    payload = jwt.decode(token)  # Only has UID
    uid = payload["uid"]
    
    # DATABASE QUERY on EVERY API call
    user = database.query("SELECT * FROM users WHERE uid = ?", uid)
    return user

# WITH phone_hash in JWT - FAST:
def get_current_user(token):
    payload = jwt.decode(token)  # Has UID + phone_hash
    # No database query needed for basic operations
    return {
        "uid": payload["uid"],
        "phone_hash": payload["phone_hash"]
    }
```

2. Phone Number Verification During Token Lifecycle
When user wants to perform sensitive operations, you can verify their phone without storing/exposing the actual number:

```python
@app.post("/sensitive-operation")
async def sensitive_op(current_user: dict = Depends(get_current_user)):
    stored_phone_hash = current_user["phone_hash"]
    
    # User enters their phone for verification
    entered_phone = "+1234567890"
    
    # Verify phone matches without exposing stored phone
    if not pwd_context.verify(entered_phone, stored_phone_hash):
        raise HTTPException(401, "Phone verification failed")
    
    # Proceed with sensitive operation
    return {"message": "Operation completed"}
```

3. Multi-Factor Authentication Context
For step-up authentication scenarios:
```python
@app.post("/transfer-money")
async def transfer_money(current_user: dict = Depends(get_current_user)):
    # High-risk operation requires phone re-verification
    phone_hash = current_user["phone_hash"]
    
    # Send OTP to phone (we can derive phone from hash in secure context)
    # or require user to re-enter phone for verification
    # This provides context about which phone should receive OTP
    
    return {"message": "OTP sent for verification"}
```

4. Preventing Token Misuse Across Phone Numbers
If somehow tokens get mixed up or reused, phone_hash provides validation:

```python
@app.post("/change-phone")
async def change_phone(new_phone: str, current_user: dict = Depends(get_current_user)):
    old_phone_hash = current_user["phone_hash"]
    
    # Verify current phone before allowing change
    # This prevents someone from changing phone if they somehow got wrong token
    current_phone = input("Enter current phone for verification: ")
    
    if not pwd_context.verify(current_phone, old_phone_hash):
        raise HTTPException(401, "Current phone verification failed")
    
    # Proceed with phone change...
```

5. Audit Logging Without Exposing PII
You can log activities with phone context without storing actual phone numbers in logs:

```python
def log_user_activity(action: str, current_user: dict):
    audit_log = {
        "action": action,
        "uid": current_user["uid"],
        "phone_hash": current_user["phone_hash"],  # Identifies user without PII
        "timestamp": datetime.utcnow()
    }
    
    # Logs contain phone_hash, not actual phone number
    # Good for compliance - no PII in logs, but still traceable
    logger.info(f"User activity: {audit_log}")
```
6. Session Validation Against User Changes
If user changes their phone number, old tokens become invalid:

```python
@app.get("/protected-data")
async def get_data(current_user: dict = Depends(get_current_user)):
    token_phone_hash = current_user["phone_hash"]
    
    # Optional: Verify token's phone_hash matches current user's phone
    # If user changed phone, this token should be invalid
    user_record = get_user_from_db(current_user["uid"])
    
    if user_record["current_phone_hash"] != token_phone_hash:
        raise HTTPException(401, "Token invalid - user phone changed")
    
    return {"data": "sensitive info"}

```

7. Compliance & Privacy Benefits

GDPR Compliant: Hash instead of actual phone number in tokens
Data Minimization: Only hash travels in network traffic
Non-Reversible: Can't extract phone number from hash
Consistent Identity: Same hash for same phone across sessions

### What if we DON'T include phone_hash?

```python
# Token without phone_hash:
{
  "uid": "usr_abc123",
  "token_id": "tok_xyz789",
  "exp": 1640995200
}

# Problems:
# ❌ Database query needed for every phone-related operation
# ❌ No fast way to verify phone without DB lookup
# ❌ Harder to implement step-up authentication
# ❌ More complex audit logging
# ❌ Can't detect phone changes in token lifecycle
```
### Why hash specifically, not encrypted phone?

One-way: Hash can't be reversed to get phone number
Verification: Can verify entered phone against hash
Consistent: Same phone always produces same hash
Compact: Smaller than encrypted phone number
Secure: Even if token is compromised, actual phone isn't exposed

### Summary:
Including phone_hash in JWT payload provides:

Performance: Avoid DB queries for phone-related operations
Security: Phone verification without exposing actual number
Compliance: GDPR-friendly logging and audit trails
Validation: Detect user changes and prevent token misuse
Flexibility: Enable multi-factor auth and step-up authentication
Privacy: Phone context without PII exposure

It's a balance between stateless efficiency (JWT benefits) and practical security needs (phone verification context).
