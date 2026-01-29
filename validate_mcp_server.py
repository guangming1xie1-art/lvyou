#!/usr/bin/env python3
"""
Quick validation script for MCP Server implementation
Checks key files and structure
"""

import os
import sys
from pathlib import Path

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'


def check_file(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"{GREEN}✓{RESET} {description}: {path}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {path}")
        return False


def check_file_contains(path, text, description):
    """Check if a file contains specific text"""
    if not os.path.exists(path):
        print(f"{RED}✗{RESET} {description}: File not found")
        return False

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        if text in content:
            print(f"{GREEN}✓{RESET} {description}")
            return True
        else:
            print(f"{RED}✗{RESET} {description}")
            return False


def main():
    print("=" * 60)
    print("MCP Server Implementation Validation")
    print("=" * 60)
    print()

    results = []

    # Check Gateway MCP files
    print("\n1. Gateway MCP Model Classes:")
    results.append(check_file(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/model/ToolDefinition.java",
        "ToolDefinition model"
    ))
    results.append(check_file(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/model/MCPResponse.java",
        "MCPResponse model"
    ))

    print("\n2. Gateway MCP Components:")
    results.append(check_file(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPToolRegistry.java",
        "MCPToolRegistry"
    ))
    results.append(check_file(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPToolRouter.java",
        "MCPToolRouter"
    ))
    results.append(check_file(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPController.java",
        "MCPController"
    ))

    print("\n3. Gateway Configuration:")
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/config/GatewayConfig.java",
        "WebClient.Builder webClientBuilder()",
        "WebClient.Builder bean with @LoadBalanced"
    ))

    print("\n4. MCP Tool Registry Content:")
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPToolRegistry.java",
        "search_hotels",
        "search_hotels tool registered"
    ))
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPToolRegistry.java",
        "search_flights",
        "search_flights tool registered"
    ))
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPToolRegistry.java",
        "search_attractions",
        "search_attractions tool registered"
    ))
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPToolRegistry.java",
        "create_booking",
        "create_booking tool registered"
    ))
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPToolRegistry.java",
        "get_recommendations",
        "get_recommendations tool registered"
    ))

    print("\n5. MCP Controller Endpoints:")
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPController.java",
        'GetMapping("/tools")',
        "GET /mcp/tools endpoint"
    ))
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPController.java",
        'GetMapping("/tools/{toolName}")',
        "GET /mcp/tools/{toolName} endpoint"
    ))
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPController.java",
        'PostMapping("/tools/{toolName}/call")',
        "POST /mcp/tools/{toolName}/call endpoint"
    ))
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/mcp/MCPController.java",
        'PostMapping("/initialize")',
        "POST /mcp/initialize endpoint"
    ))

    print("\n6. JWT Filter Configuration:")
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/filter/JwtAuthenticationFilter.java",
        '"/mcp/initialize"',
        "MCP initialize in public routes"
    ))
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/filter/JwtAuthenticationFilter.java",
        '"/mcp/health"',
        "MCP health in public routes"
    ))
    results.append(check_file_contains(
        "travel-assistant/gateway/src/main/java/com/travelassistant/gateway/filter/JwtAuthenticationFilter.java",
        '"/mcp/tools"',
        "MCP tools in public routes"
    ))

    print("\n7. Agent Configuration:")
    results.append(check_file_contains(
        "travel-assistant-agent/src/agents/mcp_client.py",
        '"http://localhost:9000"',
        "Agent MCP client points to Gateway port 9000"
    ))
    results.append(check_file_contains(
        "travel-assistant-agent/src/agents/mcp_client.py",
        'f"{self.java_api_url}/mcp/tools/{tool_name}/call"',
        "Agent calls Gateway MCP endpoint"
    ))

    print("\n8. Documentation:")
    results.append(check_file(
        "MCP_IMPLEMENTATION_GUIDE.md",
        "MCP Implementation Guide"
    ))

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Validation Results: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print(f"{GREEN}All checks passed!{RESET}")
        return 0
    else:
        print(f"{RED}Some checks failed. Please review the issues above.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
