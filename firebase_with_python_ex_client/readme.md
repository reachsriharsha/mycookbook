Key Components
1. Python Client (client.py)

Uses Firebase Auth REST API directly
Sends OTP request to Firebase (Firebase sends real SMS)
Collects OTP from user input
Verifies OTP with Firebase to get ID token
Sends ID token to your backend for validation

2. FastAPI Backend (main.py)

Receives Firebase ID tokens from clients
Uses Firebase Admin SDK to verify token authenticity
Provides protected endpoints that require valid tokens
Returns user information after token validation

3. Real SMS Flow

Firebase actually sends SMS to the phone number
User receives real OTP on their phone
No simulation - actual Firebase authentication

Authentication Flow

Client → Firebase: "Send OTP to +1234567890"
Firebase → Phone: Sends real SMS with OTP
User → Client: Enters OTP received on phone
Client → Firebase: "Verify OTP code 123456"
Firebase → Client: Returns JWT ID token
Client → Backend: "Verify this token"
Backend → Firebase: Validates token using Admin SDK
Backend → Client: Returns user info if valid

Key Differences from Previous Version

Real Firebase Auth: Uses Firebase Authentication service directly
Real SMS: Firebase sends actual SMS messages
ID Tokens: Uses Firebase ID tokens (JWT) instead of custom tokens
REST API: Client uses Firebase Auth REST API
Admin SDK: Backend uses Firebase Admin SDK for verification

Setup Requirements

Firebase Console Configuration:

Enable Phone Authentication
Get Web App API key
Download service account key


Update Configuration:

Replace firebase_config in client with your actual Firebase config
Place service account JSON file in project root


Test with Real Phone:

Use your actual phone number
Receive real SMS from Firebase
Enter the actual OTP code



This is a production-ready implementation that uses Firebase's actual authentication infrastructure. The sequence diagram shows the complete flow including error handling scenarios.

```mermaid
sequenceDiagram
    participant Client as Python Client
    participant Firebase as Firebase Auth
    participant Phone as User's Phone
    participant User as User
    participant Backend as FastAPI Backend

    Note over Client, Backend: Firebase OTP Authentication Flow

    %% Step 1: Send OTP Request
    Client->>Firebase: POST /sendVerificationCode<br/>{phoneNumber: "+1234567890", recaptchaToken}
    
    Firebase->>Firebase: Generate OTP<br/>Create session
    
    Firebase->>Phone: SMS: "Your verification code is 123456"
    
    Firebase->>Client: Response:<br/>{sessionInfo: "encrypted_session_data"}
    
    Client->>User: Display: "OTP sent! Check your phone"
    
    %% Step 2: User receives OTP
    Phone->>User: SMS: "Your verification code is 123456"
    
    %% Step 3: User enters OTP
    User->>Client: Enters OTP: "123456"
    
    %% Step 4: Verify OTP with Firebase
    Client->>Firebase: POST /signInWithPhoneNumber<br/>{sessionInfo, code: "123456"}
    
    Firebase->>Firebase: Verify OTP<br/>Generate ID Token
    
    Firebase->>Client: Response:<br/>{idToken: "JWT_TOKEN", localId: "user_id", phoneNumber}
    
    Client->>User: Display: "OTP verified! Token received"
    
    %% Step 5: Verify Token with Backend
    Client->>Backend: POST /auth/verify-token<br/>{id_token: "JWT_TOKEN"}
    
    Backend->>Firebase: Verify ID Token<br/>(Firebase Admin SDK)
    
    Firebase->>Backend: Token validation result<br/>{uid, phone_number, claims}
    
    Backend->>Client: Response:<br/>{uid, phone_number, firebase_claims}
    
    %% Step 6: Access Protected Resources
    Client->>Backend: GET /protected<br/>Authorization: Bearer JWT_TOKEN
    
    Backend->>Firebase: Verify ID Token<br/>(Firebase Admin SDK)
    
    Firebase->>Backend: Token validation result
    
    Backend->>Client: Response:<br/>{message: "Hello user!", user_info}
    
    Note over Client, Backend: Error Handling
    
    rect rgb(255, 230, 230)
        Note over Client, Backend: Error Cases
        alt Invalid Phone Number
            Client->>Firebase: sendVerificationCode
            Firebase->>Client: 400: "INVALID_PHONE_NUMBER"
        else Invalid OTP
            Client->>Firebase: signInWithPhoneNumber
            Firebase->>Client: 400: "INVALID_CODE"
        else Expired Session
            Client->>Firebase: signInWithPhoneNumber
            Firebase->>Client: 400: "SESSION_EXPIRED"
        else Invalid Token
            Client->>Backend: verify-token
            Backend->>Client: 401: "Invalid Firebase ID token"
        else Expired Token
            Client->>Backend: protected endpoint
            Backend->>Client: 401: "Firebase ID token has expired"
        end
    end

    Note over Client, Backend: Token Refresh Flow
    
    rect rgb(230, 255, 230)
        Note over Client, Firebase: Token Refresh (when needed)
        Client->>Firebase: POST /token<br/>{refresh_token, grant_type: "refresh_token"}
        Firebase->>Client: Response:<br/>{id_token: "NEW_JWT_TOKEN", refresh_token}
    end
```