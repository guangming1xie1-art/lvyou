#!/usr/bin/env python3
"""
Test script to verify MCP Server upgrade implementation
"""

import requests
import json
import sys

# Gateway MCP Server URL
MCP_URL = "http://localhost:9000/mcp"

def test_mcp_initialize():
    """Test MCP initialize endpoint"""
    print("\n" + "="*60)
    print("Test 1: MCP Initialize")
    print("="*60)

    response = requests.post(f"{MCP_URL}/initialize", json={})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    data = response.json()
    assert "protocolVersion" in data
    assert data["protocolVersion"] == "2024-11-05"
    assert "capabilities" in data
    assert "serverInfo" in data
    print("✅ MCP Initialize test PASSED")
    return True

def test_mcp_json_rpc_initialize():
    """Test MCP JSON-RPC 2.0 initialize"""
    print("\n" + "="*60)
    print("Test 2: MCP JSON-RPC 2.0 Initialize")
    print("="*60)

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }

    response = requests.post(MCP_URL, json=request)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    data = response.json()
    assert "jsonrpc" in data
    assert data["jsonrpc"] == "2.0"
    assert "id" in data
    assert data["id"] == 1
    assert "result" in data
    assert "protocolVersion" in data["result"]
    print("✅ MCP JSON-RPC 2.0 Initialize test PASSED")
    return True

def test_mcp_tools_list():
    """Test MCP tools/list"""
    print("\n" + "="*60)
    print("Test 3: MCP Tools List (JSON-RPC 2.0)")
    print("="*60)

    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }

    response = requests.post(MCP_URL, json=request)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    assert response.status_code == 200
    assert "result" in data
    assert "tools" in data["result"]
    tools = data["result"]["tools"]

    print(f"\n✅ Found {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool.get('name', tool.get('id'))}: {tool.get('description', 'N/A')}")

    expected_tools = [
        "search_hotels", "get_hotel_details",
        "search_flights", "get_flight_details",
        "search_attractions", "get_attraction_details",
        "create_booking", "get_booking_status", "cancel_booking",
        "get_recommendations", "get_hotel_recommendations"
    ]

    tool_names = [t.get('name') or t.get('id') for t in tools]
    for expected in expected_tools:
        assert expected in tool_names, f"Expected tool '{expected}' not found"

    print("✅ MCP Tools List test PASSED")
    return True

def test_mcp_rest_tools():
    """Test REST API tools endpoint"""
    print("\n" + "="*60)
    print("Test 4: REST API Tools Endpoint")
    print("="*60)

    response = requests.get(f"{MCP_URL}/tools")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    assert response.status_code == 200
    assert data["success"] == True
    assert "data" in data
    print(f"✅ REST API returned {len(data['data'])} tools")
    print("✅ REST API Tools test PASSED")
    return True

def test_mcp_health():
    """Test MCP health endpoint"""
    print("\n" + "="*60)
    print("Test 5: MCP Health Check")
    print("="*60)

    response = requests.get(f"{MCP_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    print("✅ MCP Health test PASSED")
    return True

def test_mcp_json_rpc_errors():
    """Test MCP JSON-RPC error handling"""
    print("\n" + "="*60)
    print("Test 6: MCP JSON-RPC Error Handling")
    print("="*60)

    # Test invalid method
    print("\n6.1: Testing invalid method...")
    request = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "invalid_method"
    }
    response = requests.post(MCP_URL, json=request)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    assert "error" in data
    assert data["error"]["code"] == -32601
    print("✅ Invalid method error handling PASSED")

    # Test missing method
    print("\n6.2: Testing missing method...")
    request = {
        "jsonrpc": "2.0",
        "id": 11
    }
    response = requests.post(MCP_URL, json=request)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    assert "error" in data
    assert data["error"]["code"] == -32600
    print("✅ Missing method error handling PASSED")

    print("✅ MCP JSON-RPC Error Handling test PASSED")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MCP Server Upgrade Verification Tests")
    print("="*60)
    print(f"Testing MCP Server at: {MCP_URL}")

    tests = [
        ("MCP Initialize", test_mcp_initialize),
        ("MCP JSON-RPC 2.0 Initialize", test_mcp_json_rpc_initialize),
        ("MCP Tools List", test_mcp_tools_list),
        ("REST API Tools", test_mcp_rest_tools),
        ("MCP Health", test_mcp_health),
        ("MCP Error Handling", test_mcp_json_rpc_errors),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"\n❌ {name} test FAILED: {e}")
            failed += 1
        except requests.exceptions.ConnectionError:
            print(f"\n❌ {name} test FAILED: Cannot connect to MCP Server")
            print(f"   Make sure the Gateway is running at {MCP_URL}")
            failed += 1
        except Exception as e:
            print(f"\n❌ {name} test FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
