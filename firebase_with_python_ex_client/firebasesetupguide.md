Firebase OTP Authentication Setup Guide
This guide shows how to implement OTP authentication using Firebase Auth directly, where:

Python client initiates OTP with Firebase
Firebase sends real SMS to phone
User enters OTP in Python client
Firebase returns ID token
Backend validates token with Firebase

Prerequisites

Python 3.8+ installed
Firebase Project with Phone Authentication enabled
Firebase Service Account Key for backend
Real phone number for testing

Step-by-Step Setup
1. Firebase Project Configuration
Enable Phone Authentication

Go to Firebase Console
Select your project or create new one
Navigate to Authentication > Sign-in method
Enable Phone authentication
Add your test phone numbers (optional for testing)

Get Firebase Config

Go to Project Settings (gear icon) > General
Scroll to "Your apps" section
If no web app exists, click "Add app" > Web
Copy the Firebase configuration object:

javascriptconst firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  // ... other config
};
Get Service Account Key (for backend)

Go to Project Settings > Service accounts
Click "Generate new private key"
Save as firebase-service-account.json

2. Project Structure
firebase-otp-auth/
├── main.py                           # FastAPI backend
├── client.py                         # Python OTP client
├── firebase-service-account.json     # Backend credentials
├── requirements.txt                  # Dependencies
├── .env                             # Environment variables
└── README.md                        # Setup guide
3. Install Dependencies
bash# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install fastapi uvicorn firebase-admin requests python-multipart pydantic
requirements.txt:
txtfastapi==0.104.1
uvicorn==0.24.0
firebase-admin==6.2.0
requests==2.31.0
python-multipart==0.0.6
pydantic==2.5.0
4. Configure Client
Update the firebase_config in client.py:
pythonfirebase_config = {
    "apiKey": "YOUR_ACTUAL_API_KEY",           # From Firebase Console
    "authDomain": "your-project.firebaseapp.com",
    "projectId": "your-project-id"
}
5. Configure Backend
Ensure firebase-service-account.json is in the project root with proper permissions:
bashchmod 600 firebase-service-account.json  # Restrict access
6. Running the Application
Terminal 1: Start Backend
bashpython main.py
Backend will start on http://localhost:8000
Terminal 2: Run Client
bashpython client.py
7. Complete Authentication Flow
Step 1: Client Initiates OTP
bashEnter phone number (with country code, e.g., +1234567890): +1234567890
Client sends request to Firebase:
POST https://identitytoolkit.googleapis.com/v1/accounts:sendVerificationCode
{
  "phoneNumber": "+1234567890",
  "recaptchaToken": "test"
}
Step 2: Firebase Sends SMS
Firebase sends real SMS to the phone number.
Step 3: User Enters OTP
bashEnter the OTP you received (6 digits): 123456
Client verifies with Firebase:
POST https://identitytoolkit.googleapis.com/v1/accounts:signInWithPhoneNumber
{
  "sessionInfo": "encrypted_session_data",
  "code": "123456"  
}
Step 4: Get Firebase ID Token
Firebase returns JWT token:
json{
  "idToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "localId": "firebase_user_id",
  "phoneNumber": "+1234567890"
}
Step 5: Backend Validates Token
Client sends token to backend:
POST http://localhost:8000/auth/verify-token
{
  "id_token": "eyJhbGciOiJSUzI1NiIs..."
}
Backend uses Firebase Admin SDK to verify token.
Step 6: Access Protected Resources
GET http://localhost:8000/protected
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
8. API Endpoints
Backend Endpoints

POST /auth/verify-token - Verify Firebase ID token
GET /protected - Protected endpoint requiring token
GET /user/profile - Get user profile
POST /user/custom-claims - Set custom user claims

Firebase REST API Endpoints

POST /accounts:sendVerificationCode - Send OTP
POST /accounts:signInWithPhoneNumber - Verify OTP
POST /token - Refresh token

9. Environment Variables
Create .env file:
envFIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_PROJECT_ID=your-project-id
API_HOST=0.0.0.0
API_PORT=8000
10. Production Considerations
Security

reCAPTCHA: Implement proper reCAPTCHA for OTP requests
Rate Limiting: Prevent abuse of OTP endpoints
HTTPS: Use HTTPS in production
Token Validation: Always validate tokens on backend
Environment Variables: Store sensitive data in environment variables

Error Handling

Network timeouts
Invalid phone numbers
Expired sessions
Invalid OTP codes
Token expiration

Testing
bash# Test backend health
curl http://localhost:8000/

# Test token verification (replace with actual token)
curl -X POST http://localhost:8000/auth/verify-token \
  -H "Content-Type: application/json" \
  -d '{"id_token": "your_firebase_token"}'

# Test protected endpoint
curl -H "Authorization: Bearer your_firebase_token" \
  http://localhost:8000/protected
11. Troubleshooting
Common Issues
"INVALID_PHONE_NUMBER"

Ensure phone number includes country code (+1, +91, etc.)
Phone number must be properly formatted

"CAPTCHA_CHECK_FAILED"

In production, implement proper reCAPTCHA
For testing, some Firebase projects allow bypassing reCAPTCHA

"SESSION_EXPIRED"

OTP sessions expire after few minutes
Request new OTP if expired

"INVALID_CODE"

Double-check OTP from SMS
Ensure OTP is entered quickly after receiving

Backend Token Verification Fails

Check Firebase service account key path
Ensure Firebase Admin SDK is properly initialized
Verify token hasn't expired

Debug Commands
bash# Check Firebase project settings
firebase projects:list

# Test Firebase Auth REST API directly
curl -X POST \
  "https://identitytoolkit.googleapis.com/v1/accounts:sendVerificationCode?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+1234567890", "recaptchaToken": "test"}'
12. Real-World Implementation
Mobile App Integration

Use Firebase SDK in mobile apps instead of REST API
Implement proper reCAPTCHA handling
Handle network failures gracefully

Web App Integration

Use Firebase JavaScript SDK
Implement reCAPTCHA v3
Handle token refresh automatically

Backend Integration

Store user data in database after first authentication
Implement user roles and permissions
Add logging and monitoring

13. Security Best Practices

Never expose API keys in client-side code
Validate all tokens on the backend
Implement rate limiting for OTP requests
Use HTTPS in production
Monitor for suspicious activity
Implement proper session management
Handle token expiration gracefully

This setup provides a complete, production-ready OTP authentication flow with Firebase!