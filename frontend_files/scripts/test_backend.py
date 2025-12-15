"""
============================================
FRONTEND CODE - API Test Script
============================================
Simple script to test if the Flask backend is working correctly
Run this after starting the Flask server with: python app.py
"""

import requests
import json

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure Flask is running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_upload_endpoint():
    """Test the upload endpoint (without actual file)"""
    print("\nTesting upload endpoint...")
    try:
        response = requests.post('http://localhost:5000/api/upload')
        if response.status_code == 400:
            print("✅ Upload endpoint responding correctly (no file provided)")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Flask Backend API Test")
    print("=" * 50)
    print("\nMake sure Flask backend is running: python app.py")
    print()
    
    health_ok = test_health_check()
    upload_ok = test_upload_endpoint()
    
    print("\n" + "=" * 50)
    if health_ok and upload_ok:
        print("✅ All tests passed! Backend is ready.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 50)
