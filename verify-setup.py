#!/usr/bin/env python3
"""
Local setup verification script for Contact Reconciliation Service
"""

import sys
import subprocess
import requests
import time
import json
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_requirements():
    """Check if required tools are available"""
    print("🔍 Checking requirements...")
    
    # Check Docker
    success, stdout, stderr = run_command("docker --version", check=False)
    if not success:
        print("❌ Docker not found. Please install Docker.")
        return False
    print(f"✅ Docker: {stdout.strip()}")
    
    # Check Docker Compose
    success, stdout, stderr = run_command("docker-compose --version", check=False)
    if not success:
        print("❌ Docker Compose not found. Please install Docker Compose.")
        return False
    print(f"✅ Docker Compose: {stdout.strip()}")
    
    return True

def test_docker_build():
    """Test Docker build"""
    print("\n🏗️ Testing Docker build...")
    
    success, stdout, stderr = run_command("docker-compose build", check=False)
    if not success:
        print(f"❌ Docker build failed: {stderr}")
        return False
    
    print("✅ Docker build successful")
    return True

def test_service_startup():
    """Test service startup"""
    print("\n🚀 Starting service...")
    
    # Start the service
    success, stdout, stderr = run_command("docker-compose up -d", check=False)
    if not success:
        print(f"❌ Service startup failed: {stderr}")
        return False
    
    print("✅ Service started")
    
    # Wait for service to be ready
    print("⏳ Waiting for service to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Service is ready")
                return True
        except requests.RequestException:
            pass
        
        time.sleep(2)
        print(f"   Attempt {attempt + 1}/{max_attempts}")
    
    print("❌ Service failed to become ready")
    return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test identify endpoint
    try:
        test_data = {
            "email": "test@example.com",
            "phoneNumber": "1234567890"
        }
        response = requests.post(
            "http://localhost:8000/identify",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Identify endpoint working")
            print(f"   Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Identify endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Identify endpoint error: {e}")
        return False
    
    return True

def test_documentation():
    """Test documentation endpoints"""
    print("\n📚 Testing documentation...")
    
    endpoints = [
        ("Swagger UI", "http://localhost:8000/docs"),
        ("ReDoc", "http://localhost:8000/redoc"),
        ("OpenAPI JSON", "http://localhost:8000/openapi.json")
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ {name} accessible")
            else:
                print(f"❌ {name} failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {name} error: {e}")
            return False
    
    return True

def cleanup():
    """Clean up test resources"""
    print("\n🧹 Cleaning up...")
    run_command("docker-compose down", check=False)
    print("✅ Cleanup complete")

def main():
    """Main verification function"""
    print("🔍 Contact Reconciliation Service - Setup Verification")
    print("=" * 60)
    
    try:
        # Check requirements
        if not check_requirements():
            sys.exit(1)
        
        # Test Docker build
        if not test_docker_build():
            sys.exit(1)
        
        # Test service startup
        if not test_service_startup():
            cleanup()
            sys.exit(1)
        
        # Test API endpoints
        if not test_api_endpoints():
            cleanup()
            sys.exit(1)
        
        # Test documentation
        if not test_documentation():
            cleanup()
            sys.exit(1)
        
        print("\n🎉 All tests passed! Your setup is working correctly.")
        print("\n📋 Next steps:")
        print("1. Create a GitHub repository")
        print("2. Add Docker Hub secrets to GitHub")
        print("3. Push your code to trigger CI/CD")
        print("4. Check the setup-verification.md file for detailed instructions")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Verification interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
