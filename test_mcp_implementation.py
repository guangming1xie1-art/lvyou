#!/usr/bin/env python3
"""
MCP Gateway Implementation Test Script

This script tests the MCP server implementation in the Gateway service.
It verifies all 10 MCP tools and their endpoints.
"""

import requests
import json
from typing import Dict, Any

# Configuration
GATEWAY_URL = "http://localhost:9000"
MCP_BASE_URL = f"{GATEWAY_URL}/mcp"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_test(test_name: str):
    print(f"\n{YELLOW}Testing: {test_name}{RESET}")


def print_success(message: str):
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    print(f"{RED}✗ {message}{RESET}")


def print_info(message: str):
    print(f"  {message}")


def test_health():
    """Test MCP health endpoint"""
    print_test("MCP Health Check")

    try:
        response = requests.get(f"{MCP_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed - Status: {data.get('status')}, Tools count: {data.get('toolsCount')}")
            return True
        else:
            print_error(f"Health check failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check failed - Error: {e}")
        return False


def test_initialize():
    """Test MCP initialize endpoint (MultiServerMCPClient compatibility)"""
    print_test("MCP Initialize")

    try:
        response = requests.post(f"{MCP_BASE_URL}/initialize")
        if response.status_code == 200:
            data = response.json()
            protocol_version = data.get("protocolVersion")
            capabilities = data.get("capabilities", {})
            server_info = data.get("serverInfo", {})

            print_success(f"Initialize passed")
            print_info(f"Protocol version: {protocol_version}")
            print_info(f"Server: {server_info.get('name')} v{server_info.get('version')}")
            print_info(f"Capabilities: {list(capabilities.keys())}")
            return True
        else:
            print_error(f"Initialize failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Initialize failed - Error: {e}")
        return False


def test_get_all_tools():
    """Test getting all tools"""
    print_test("Get All Tools")

    try:
        response = requests.get(f"{MCP_BASE_URL}/tools")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                tools = data.get("data", [])
                print_success(f"Found {len(tools)} tools")
                for tool in tools:
                    print_info(f"  - {tool['id']}: {tool['name']} -> {tool['serviceName']}")
                return len(tools) == 10  # Should have exactly 10 tools
            else:
                print_error(f"Get tools failed - Error: {data.get('error')}")
                return False
        else:
            print_error(f"Get tools failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get tools failed - Error: {e}")
        return False


def test_get_tool(tool_name: str):
    """Test getting a specific tool"""
    print_test(f"Get Tool: {tool_name}")

    try:
        response = requests.get(f"{MCP_BASE_URL}/tools/{tool_name}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                tool = data.get("data")
                print_success(f"Found tool: {tool['name']}")
                print_info(f"  Description: {tool['description']}")
                print_info(f"  Service: {tool['serviceName']}")
                print_info(f"  Endpoint: {tool['endpoint']}")
                print_info(f"  Method: {tool['httpMethod']}")
                return True
            else:
                print_error(f"Get tool failed - Error: {data.get('error')}")
                return False
        else:
            print_error(f"Get tool failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get tool failed - Error: {e}")
        return False


def test_call_tool(tool_name: str, parameters: Dict[str, Any], jwt_token: str = None):
    """Test calling a tool"""
    print_test(f"Call Tool: {tool_name}")

    url = f"{MCP_BASE_URL}/tools/{tool_name}/call"
    headers = {"Content-Type": "application/json"}
    body = {"parameters": parameters}

    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"

    try:
        response = requests.post(url, json=body, headers=headers)
        print_info(f"Status: {response.status_code}")

        if response.status_code in [200, 201]:
            data = response.json()
            if data.get("success"):
                print_success(f"Tool call succeeded")
                print_info(f"  Data type: {type(data.get('data')).__name__}")
                return True
            else:
                print_error(f"Tool call failed - Error: {data.get('error')}")
                return False
        else:
            print_error(f"Tool call failed - Status: {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Tool call failed - Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP Gateway Implementation Test Suite")
    print("=" * 60)

    results = []

    # 1. Health check
    results.append(("Health Check", test_health()))

    # 2. Initialize
    results.append(("Initialize", test_initialize()))

    # 3. Get all tools
    results.append(("Get All Tools", test_get_all_tools()))

    # 4. Test individual tools
    tool_names = [
        "search_hotels",
        "get_hotel_details",
        "search_flights",
        "get_flight_details",
        "search_attractions",
        "get_attraction_details",
        "create_booking",
        "get_booking_status",
        "get_recommendations",
        "get_hotel_recommendations"
    ]

    for tool_name in tool_names:
        results.append((f"Get Tool: {tool_name}", test_get_tool(tool_name)))

    # 5. Test tool calls (with mock parameters)
    # These will likely fail if backend services aren't running, but we can test the routing

    # Test search_hotels
    results.append(("Call search_hotels", test_call_tool(
        "search_hotels",
        {"destination": "New York", "min_price": 100, "max_price": 500}
    )))

    # Test search_flights
    results.append(("Call search_flights", test_call_tool(
        "search_flights",
        {"origin": "NYC", "destination": "LAX", "departure_date": "2024-12-01"}
    )))

    # Test search_attractions
    results.append(("Call search_attractions", test_call_tool(
        "search_attractions",
        {"destination": "Paris", "category": "Museum"}
    )))

    # Test get_recommendations
    results.append(("Call get_recommendations", test_call_tool(
        "get_recommendations",
        {"user_id": "550e8400-e29b-41d4-a716-446655440000", "type": "comprehensive", "limit": 5}
    )))

    # Test create_booking (will likely fail without valid data)
    results.append(("Call create_booking", test_call_tool(
        "create_booking",
        {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "booking_type": "HOTEL",
            "resource_id": "550e8400-e29b-41d4-a716-446655440001",
            "booking_date": "2024-12-01",
            "total_price": 500
        }
    )))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status}: {test_name}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
