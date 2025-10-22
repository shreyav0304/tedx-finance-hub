#!/usr/bin/env python
"""
Health check script to validate critical endpoints.
Usage: python test_health.py
"""
import sys
import time
import requests
from urllib.parse import urljoin

# Base URL for the application
BASE_URL = "http://127.0.0.1:8000"

# Endpoints to test (path, expected_status, requires_auth)
ENDPOINTS = [
    ("/", 302, False),  # Root redirects to login
    ("/accounts/login/", 200, False),  # Django auth URLs
    ("/signup/", 200, False),
    ("/proofs/", 302, False),  # Redirects to login if not authenticated
    ("/", 302, False),  # Dashboard via root redirect
]

def check_endpoint(path, expected_status, session=None):
    """Check if an endpoint returns the expected status code."""
    url = urljoin(BASE_URL, path)
    try:
        if session:
            response = session.get(url, allow_redirects=False, timeout=5)
        else:
            response = requests.get(url, allow_redirects=False, timeout=5)
        
        if response.status_code == expected_status:
            print(f"✅ {path} - Status {response.status_code}")
            return True
        else:
            print(f"❌ {path} - Expected {expected_status}, got {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {path} - Connection refused (server not running?)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {path} - Request timeout")
        return False
    except Exception as e:
        print(f"❌ {path} - Error: {str(e)}")
        return False

def main():
    """Run health checks on all endpoints."""
    print("🏥 Starting health check...\n")
    print(f"Testing against: {BASE_URL}")
    print("-" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(0.5)
    
    results = []
    for path, expected_status, _ in ENDPOINTS:
        result = check_endpoint(path, expected_status)
        results.append(result)
    
    print("-" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} health checks passed!")
        return 0
    else:
        print(f"❌ {passed}/{total} health checks passed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
