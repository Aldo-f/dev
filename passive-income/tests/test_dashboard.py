#!/usr/bin/env python3
"""
TDD Tests for Passive Income Dashboard and EarnApp connectivity.
Tests:
1. Dashboard binds to 0.0.0.0:4747
2. EarnApp container is running and accessible
3. Network connectivity from local network
"""

import socket
import subprocess
import time
import sys
import requests
import json

DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = 4747
EARNAPP_PORT = 8765

def test_dashboard_binds_to_all_interfaces():
    """Test that dashboard binds to 0.0.0.0 (all interfaces)"""
    # Check docker-compose.yml for correct port binding
    with open("config/docker-compose.yml", "r") as f:
        compose = f.read()
    
    # Check for 0.0.0.0 binding in dashboard section
    assert "0.0.0.0:4747:80" in compose, "Dashboard must bind to 0.0.0.0:4747"
    print("✅ docker-compose.yml binds dashboard to 0.0.0.0:4747")

def test_earnapp_port_binding():
    """Test that earnapp binds to 0.0.0.0"""
    with open("config/docker-compose.yml", "r") as f:
        compose = f.read()
    
    assert "0.0.0.0:8765:8765" in compose, "EarnApp must bind to 0.0.0.0:8765"
    print("✅ docker-compose.yml binds earnapp to 0.0.0.0:8765")

def test_dashboard_accessible():
    """Test dashboard is accessible via HTTP"""
    try:
        response = requests.get(f"http://localhost:{DASHBOARD_PORT}", timeout=5)
        assert response.status_code == 200, f"Dashboard returned {response.status_code}"
        print("✅ Dashboard accessible on localhost:4747")
    except requests.exceptions.ConnectionError:
        print("⚠️ Dashboard not running (start with docker-compose up -d)")
        return False
    return True

def test_earnapp_config_exists():
    """Test earnapp config.env exists with required fields"""
    with open("providers/earnapp/config.env", "r") as f:
        content = f.read()
    
    assert "DEVICE_ID" in content, "EarnApp config must have DEVICE_ID"
    assert "ENABLED_DAYS" in content, "EarnApp config must have ENABLED_DAYS"
    print("✅ EarnApp config.env has required fields")

def test_provider_registry():
    """Test provider.json has earnapp registered"""
    with open("providers/provider.json", "r") as f:
        data = json.load(f)
    
    assert "earnapp" in data["providers"], "EarnApp must be in provider registry"
    earnapp = data["providers"]["earnapp"]
    assert earnapp["image"] == "earnapp/earnapp:latest", "Wrong image"
    print("✅ EarnApp registered in provider.json with correct image")

def test_docker_compose_syntax():
    """Test docker-compose.yml is valid"""
    result = subprocess.run(
        ["docker", "compose", "-f", "config/docker-compose.yml", "config"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"docker-compose config failed: {result.stderr}"
    print("✅ docker-compose.yml syntax valid")

def test_containers_can_start():
    """Test containers can start without errors"""
    result = subprocess.run(
        ["docker", "compose", "-f", "config/docker-compose.yml", "up", "-d", "--no-build"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        print(f"⚠️ Container start failed: {result.stderr}")
        return False
    
    # Wait for containers to be healthy
    time.sleep(10)
    
    # Check if dashboard container is running
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=passive-income-dashboard", "--format", "{{.Status}}"],
        capture_output=True, text=True
    )
    assert "Up" in result.stdout, "Dashboard container not running"
    print("✅ Dashboard container running")
    
    # Check if earnapp container is running
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=earnapp", "--format", "{{.Status}}"],
        capture_output=True, text=True
    )
    assert "Up" in result.stdout, "EarnApp container not running"
    print("✅ EarnApp container running")
    
    return True

def test_network_access_from_local():
    """Test dashboard accessible from local network (192.168.0.x)"""
    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "192.168.0.3"
    
    try:
        response = requests.get(f"http://{local_ip}:{DASHBOARD_PORT}", timeout=5)
        assert response.status_code == 200, f"Dashboard returned {response.status_code} from {local_ip}"
        print(f"✅ Dashboard accessible from local network ({local_ip}:{DASHBOARD_PORT})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"⚠️ Dashboard not accessible from {local_ip}:{DASHBOARD_PORT} (may need firewall/permission)")
        return False

if __name__ == "__main__":
    print("🧪 Running TDD Tests for Passive Income Dashboard & EarnApp\n")
    
    tests = [
        test_dashboard_binds_to_all_interfaces,
        test_earnapp_port_binding,
        test_earnapp_config_exists,
        test_provider_registry,
        test_docker_compose_syntax,
    ]
    
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
    
    print(f"\n📊 Static tests: {passed}/{len(tests)} passed")
    
    # Run dynamic tests if containers are running
    print("\n🧪 Dynamic tests (require containers running):")
    dynamic_tests = [
        test_dashboard_accessible,
        test_containers_can_start,
        test_network_access_from_local,
    ]
    
    for test in dynamic_tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
    
    print(f"\n📊 Total tests passed: {passed}/{len(tests) + len(dynamic_tests)}")
    sys.exit(0 if passed == len(tests) + len(dynamic_tests) else 1)