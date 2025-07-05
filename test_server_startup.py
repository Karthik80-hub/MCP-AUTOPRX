#!/usr/bin/env python3
"""
Simple test script to verify server startup
"""

import os
import sys
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_server_startup():
    """Test if the server can be initialized without errors."""
    try:
        print("Testing server startup...")
        
        # Test imports
        print("✓ Testing imports...")
        from unified_server import UnifiedServer
        
        # Test server initialization
        print("✓ Testing server initialization...")
        server = UnifiedServer()
        
        # Test FastAPI app creation
        print("✓ Testing FastAPI app...")
        assert hasattr(server, 'app'), "Server should have FastAPI app"
        
        # Test health endpoint
        print("✓ Testing health endpoint...")
        from fastapi.testclient import TestClient
        client = TestClient(server.app)
        response = client.get("/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        
        print("✅ All tests passed! Server should work correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_server_startup()
    sys.exit(0 if success else 1) 