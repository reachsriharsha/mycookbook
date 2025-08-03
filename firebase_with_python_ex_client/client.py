# client.py - Python Client for Firebase OTP Authentication

import requests
import json
from typing import Optional
import time

class FirebaseOTPClient:
    def __init__(self, firebase_config: dict, backend_url: str = "http://localhost:8000"):
        """
        Initialize Firebase OTP Client
        
        firebase_config should contain:
        {
            "apiKey": "your-api-key",
            "authDomain": "your-project.firebaseapp.com",
            "projectId": "your-project-id"
        }
        """
        self.firebase_config = firebase_config
        self.backend_url = backend_url
        self.session_info = None
        self.id_token = None
        
        # Firebase Auth REST API endpoints
        self.firebase_auth_url = "https://identitytoolkit.googleapis.com/v1/accounts"
        self.api_key = firebase_config["apiKey"]
    
    def send_otp(self, phone_number: str, recaptcha_token: str = "test") -> dict:
        """
        Send OTP to phone number using Firebase Auth REST API
        """
        url = f"{self.firebase_auth_url}:sendVerificationCode"
        
        payload = {
            "phoneNumber": phone_number,
            "recaptchaToken": recaptcha_token  # In production, get real recaptcha token
        }
        
        params = {"key": self.api_key}
        
        try:
            print(f"📱 Sending OTP to {phone_number}...")
            response = requests.post(url, json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.session_info = data.get("sessionInfo")
                
                print("✅ OTP sent successfully!")
                print(f"Session Info: {self.session_info[:20]}...")
                print("🔔 Check your phone for the OTP!")
                print("="*50)
                
                return data
            else:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                print(f"❌ Error sending OTP: {error_message}")
                print(f"Response: {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error sending OTP: {e}")
            return {}
    
    def verify_otp(self, otp_code: str) -> dict:
        """
        Verify OTP and get Firebase ID token
        """
        if not self.session_info:
            print("❌ No active session. Send OTP first.")
            return {}
        
        url = f"{self.firebase_auth_url}:signInWithPhoneNumber"
        
        payload = {
            "sessionInfo": self.session_info,
            "code": otp_code
        }
        
        params = {"key": self.api_key}
        
        try:
            print(f"🔐 Verifying OTP: {otp_code}")
            response = requests.post(url, json=payload, params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.id_token = data.get("idToken")
                
                print("✅ OTP verified successfully!")
                print(f"ID Token: {self.id_token[:50]}...")
                print(f"Local ID: {data.get('localId')}")
                print(f"Phone Number: {data.get('phoneNumber')}")
                
                return data
            else:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                print(f"❌ Error verifying OTP: {error_message}")
                print(f"Response: {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error verifying OTP: {e}")
            return {}
    
    def verify_token_with_backend(self) -> dict:
        """
        Send Firebase ID token to backend for verification
        """
        if not self.id_token:
            print("❌ No ID token available. Complete OTP verification first.")
            return {}
        
        url = f"{self.backend_url}/auth/verify-token"
        payload = {"id_token": self.id_token}
        
        try:
            print("🔍 Verifying token with backend...")
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Token verified by backend!")
                print(f"User ID: {data.get('uid')}")
                print(f"Phone: {data.get('phone_number')}")
                return data
            else:
                error_data = response.json()
                print(f"❌ Backend verification failed: {error_data.get('detail')}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error with backend: {e}")
            return {}
    
    def call_protected_endpoint(self) -> dict:
        """
        Call a protected endpoint using the Firebase ID token
        """
        if not self.id_token:
            print("❌ No ID token available. Complete authentication first.")
            return {}
        
        url = f"{self.backend_url}/protected"
        headers = {"Authorization": f"Bearer {self.id_token}"}
        
        try:
            print("🔒 Calling protected endpoint...")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Protected endpoint accessed successfully!")
                print(f"Message: {data.get('message')}")
                return data
            else:
                error_data = response.json()
                print(f"❌ Protected endpoint access failed: {error_data.get('detail')}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error accessing protected endpoint: {e}")
            return {}
    
    def get_user_profile(self) -> dict:
        """
        Get user profile from backend
        """
        if not self.id_token:
            print("❌ No ID token available. Complete authentication first.")
            return {}
        
        url = f"{self.backend_url}/user/profile"
        headers = {"Authorization": f"Bearer {self.id_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ User profile retrieved!")
                print(json.dumps(data, indent=2))
                return data
            else:
                error_data = response.json()
                print(f"❌ Failed to get user profile: {error_data.get('detail')}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error getting user profile: {e}")
            return {}

def main():
    print("🔐 Firebase OTP Authentication Client")
    print("="*50)
    
    # Firebase configuration - Replace with your actual config
    firebase_config = {
        "apiKey": "YOUR_FIREBASE_API_KEY",
        "authDomain": "your-project.firebaseapp.com",
        "projectId": "your-project-id"
    }
    
    # Check if config is updated
    if firebase_config["apiKey"] == "YOUR_FIREBASE_API_KEY":
        print("❌ Please update firebase_config with your actual Firebase configuration")
        print("Get these values from Firebase Console > Project Settings > General > Your apps")
        return
    
    client = FirebaseOTPClient(firebase_config)
    
    # Step 1: Get phone number
    phone_number = input("Enter phone number (with country code, e.g., +1234567890): ").strip()
    
    if not phone_number:
        print("❌ Phone number is required")
        return
    
    # Step 2: Send OTP
    result = client.send_otp(phone_number)
    if not result:
        return
    
    # Step 3: Get and verify OTP
    while True:
        print("\n" + "="*50)
        otp_code = input("Enter the OTP you received (6 digits): ").strip()
        
        if not otp_code:
            print("❌ OTP is required")
            continue
            
        if len(otp_code) != 6 or not otp_code.isdigit():
            print("❌ OTP must be 6 digits")
            continue
        
        # Verify OTP with Firebase
        result = client.verify_otp(otp_code)
        if result:
            break
        else:
            retry = input("\nWould you like to try again? (y/n): ").strip().lower()
            if retry != 'y':
                return
    
    # Step 4: Verify token with backend
    print("\n" + "="*50)
    client.verify_token_with_backend()
    
    # Step 5: Test protected endpoints
    print("\n" + "="*50)
    client.call_protected_endpoint()
    
    # Step 6: Get user profile
    print("\n" + "="*50)
    client.get_user_profile()
    
    print("\n🎉 Authentication flow completed successfully!")

if __name__ == "__main__":
    main()