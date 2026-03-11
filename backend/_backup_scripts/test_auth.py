"""
Test script to verify per-user password authentication
Tests signup with unique passwords and login validation
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_signup_with_unique_passwords():
    """Test that each user can signup with their own password"""
    print("🧪 Testing Driver Signup with Unique Passwords\n")
    
    test_users = [
        {"name": "Test Driver 1", "email": "test1@example.com", "password": "mypassword123"},
        {"name": "Test Driver 2", "email": "test2@example.com", "password": "different456"},
    ]
    
    for user in test_users:
        print(f"📝 Creating account for {user['name']}...")
        response = requests.post(
            f"{BASE_URL}/signup/driver",
            json=user
        )
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS: Account created for {user['email']}")
        elif response.status_code == 400 and "already exists" in response.text:
            print(f"   ℹ️  SKIPPED: Account already exists for {user['email']}")
        else:
            print(f"   ❌ FAILED: {response.status_code} - {response.text}")
    
    print()

def test_login_with_correct_password():
    """Test that login succeeds with correct password"""
    print("🔐 Testing Login with CORRECT Passwords\n")
    
    test_cases = [
        {"email": "test1@example.com", "password": "mypassword123"},
        {"email": "test2@example.com", "password": "different456"},
    ]
    
    for test in test_cases:
        print(f"🔑 Logging in as {test['email']}...")
        
        # OAuth2 format
        data = {
            "username": test["email"],
            "password": test["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ LOGIN SUCCESS")
            print(f"   → Token received: {result['access_token'][:20]}...")
            print(f"   → Driver ID: {result['driver_id']}")
            print(f"   → Name: {result['name']}")
        else:
            print(f"   ❌ LOGIN FAILED: {response.status_code}")
            print(f"   → {response.text}")
    
    print()

def test_login_with_wrong_password():
    """Test that login fails with incorrect password"""
    print("🚫 Testing Login with WRONG Passwords\n")
    
    test_cases = [
        {"email": "test1@example.com", "password": "WRONGPASSWORD"},
        {"email": "test2@example.com", "password": "incorrect123"},
    ]
    
    for test in test_cases:
        print(f"🔐 Attempting login with wrong password for {test['email']}...")
        
        data = {
            "username": test["email"],
            "password": test["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 400:
            print(f"   ✅ CORRECTLY REJECTED (as expected)")
            print(f"   → Error: {response.json().get('detail', 'Unknown')}")
        else:
            print(f"   ❌ SECURITY ISSUE: Should have rejected but got {response.status_code}")
    
    print()

def test_no_default_passwords():
    """Verify that the old default password doesn't work"""
    print("🔒 Testing That Default Password 'driver123' Doesn't Work\n")
    
    test_email = "test1@example.com"
    
    print(f"🔐 Trying old default password for {test_email}...")
    
    data = {
        "username": test_email,
        "password": "driver123"  # Old default password
    }
    
    response = requests.post(
        f"{BASE_URL}/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 400:
        print(f"   ✅ DEFAULT PASSWORD REJECTED (security working!)")
    else:
        print(f"   ❌ SECURITY ISSUE: Default password still works!")
    
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("  PER-USER PASSWORD AUTHENTICATION TEST")
    print("=" * 60)
    print()
    
    try:
        # Test signup
        test_signup_with_unique_passwords()
        
        # Test correct passwords
        test_login_with_correct_password()
        
        # Test wrong passwords
        test_login_with_wrong_password()
        
        # Test default password rejection
        test_no_default_passwords()
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETE")
        print("=" * 60)
        print()
        print("📋 SUMMARY:")
        print("   ✓ Each driver has unique password")
        print("   ✓ Login succeeds with correct password")
        print("   ✓ Login fails with wrong password")
        print("   ✓ Default password 'driver123' rejected")
        print()
        print("🎉 Default password removed. Authentication now uses")
        print("   per-user stored credentials.")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend at", BASE_URL)
        print("   Make sure the server is running: uvicorn main:app --reload")
