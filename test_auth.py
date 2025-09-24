#!/usr/bin/env python3
"""
Test script for authentication system
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1/auth"

def test_signup():
    """Test user signup"""
    print("Testing user signup...")
    
    signup_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "password123",
        "phone": "+1234567890",
        "role": "user"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/signup", json=signup_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    
    login_data = {
        "username": "john.doe@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            return token
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_me_endpoint(token):
    """Test /me endpoint with token"""
    print("\nTesting /me endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_superuser_login():
    """Test superuser login"""
    print("\nTesting superuser login...")
    
    login_data = {
        "username": "admin@sevenhealerconsultants.in",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            return token
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("=== Authentication System Test ===\n")
    
    # Test signup
    signup_success = test_signup()
    
    # Test login
    token = test_login()
    
    # Test /me endpoint
    if token:
        me_success = test_me_endpoint(token)
    
    # Test superuser login
    superuser_token = test_superuser_login()
    
    print("\n=== Test Summary ===")
    print(f"Signup: {'✅ PASS' if signup_success else '❌ FAIL'}")
    print(f"Login: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"Me Endpoint: {'✅ PASS' if token and me_success else '❌ FAIL'}")
    print(f"Superuser Login: {'✅ PASS' if superuser_token else '❌ FAIL'}")

