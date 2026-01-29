# MCP Server Implementation Guide

## Overview

This document describes the complete implementation of the MCP (Model Context Protocol) server in the Gateway service for the travel-assistant project.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent (Python)                          │
│  - MultiServerMCPClient                                   │
│  - Calls tools via HTTP                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ http://localhost:9000/mcp/tools/{name}/call
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Gateway (Spring Cloud)                        │
│  - MCPController: REST endpoints                          │
│  - MCPToolRegistry: Tool definitions                      │
│  - MCPToolRouter: Routes to microservices                 │
│  - WebClient: Makes requests with JWT forwarding            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Load Balanced (Nacos)
                     │
    ┌────────────────┼────────────────┬─────────────────┐
    │                │                │                 │
    ▼                ▼                ▼                 ▼
Hotel-service   Flight-service  Attraction-service  Booking-service
    │                │                │                 │
    └────────────────┴────────────────┴─────────────────┘
                      │
                      ▼
            Recommendation-service
```

## Implementation Details

### 1. Model Classes

#### ToolDefinition
- **Location**: `gateway/src/main/java/com/travelassistant/gateway/mcp/model/ToolDefinition.java`
- **Purpose**: Defines a single MCP tool
- **Fields**:
  - `id`: Tool identifier (e.g., "search_hotels")
  - `name`: Tool display name
  - `description`: Tool description
  - `inputSchema`: JSON Schema for input parameters
  - `serviceName`: Target microservice (e.g., "hotel-service")
  - `httpMethod`: HTTP method (GET, POST, etc.)
  - `endpoint`: API endpoint path
  - `paramMapping`: Parameter name mapping (snake_case → camelCase)

#### MCPResponse
- **Location**: `gateway/src/main/java/com/travelassistant/gateway/mcp/model/MCPResponse.java`
- **Purpose**: Unified response format for MCP endpoints
- **Fields**:
  - `success`: Boolean indicating success/failure
  - `data`: Response data on success
  - `error`: Error message on failure

### 2. MCPToolRegistry

- **Location**: `gateway/src/main/java/com/travelassistant/gateway/mcp/MCPToolRegistry.java`
- **Purpose**: Manages all available MCP tools
- **Initialization**: Registers all 10 tools on startup via `@PostConstruct`
- **Methods**:
  - `getAllTools()`: Returns all tool definitions
  - `getTool(String toolName)`: Returns specific tool definition
  - `hasTool(String toolName)`: Checks if tool exists

### 3. Registered Tools

| Tool Name | Service | HTTP Method | Endpoint | Parameters |
|-----------|---------|-------------|----------|------------|
| search_hotels | hotel-service | GET | /api/hotel | destination, min_price, max_price, min_rating, facility |
| get_hotel_details | hotel-service | GET | /api/hotel/{id} | id |
| search_flights | flight-service | GET | /api/flight | origin, destination, departure_date, min_price, max_price, airline |
| get_flight_details | flight-service | GET | /api/flight/{id} | id |
| search_attractions | attraction-service | GET | /api/attraction | destination, category, min_rating, tags |
| get_attraction_details | attraction-service | GET | /api/attraction/{id} | id |
| create_booking | booking-service | POST | /api/booking | user_id, booking_type, resource_id, booking_date, total_price, notes |
| get_booking_status | booking-service | GET | /api/booking/{id} | id |
| get_recommendations | recommendation-service | GET | /api/recommendation/comprehensive/{userId} | user_id, type, limit |
| get_hotel_recommendations | recommendation-service | GET | /api/recommendation/hotels/{userId} | user_id, limit |

### 4. MCPToolRouter

- **Location**: `gateway/src/main/java/com/travelassistant/gateway/mcp/MCPToolRouter.java`
- **Purpose**: Routes tool calls to appropriate microservices
- **Key Features**:
  - Uses WebClient (reactive) for HTTP requests
  - Supports path parameters (e.g., `/api/hotel/{id}`)
  - Supports query parameters (e.g., `/api/flight?origin=NYC`)
  - Supports request body for POST requests
  - Forwards Authorization header to downstream services
  - Converts parameter names from snake_case to camelCase
  - Includes comprehensive error handling

### 5. MCPController

- **Location**: `gateway/src/main/java/com/travelassistant/gateway/mcp/MCPController.java`
- **Purpose**: Provides REST endpoints for MCP protocol
- **Endpoints**:

#### GET /mcp/tools
- Returns all tool definitions
- Response: `{"success": true, "data": [ToolDefinition, ...]}`

#### GET /mcp/tools/{toolName}
- Returns specific tool definition
- Response: `{"success": true, "data": ToolDefinition}`

#### POST /mcp/tools/{toolName}/call
- Calls a tool with parameters
- Request body: `{"parameters": {...}}`
- Response: `{"success": true, "data": {...}}` or `{"success": false, "error": "..."}`

#### POST /mcp/initialize
- MCP protocol initialization
- Returns protocol version and capabilities
- Compatible with MultiServerMCPClient

#### GET /mcp/health
- Health check endpoint
- Returns service status and tool count

### 6. Gateway Configuration

- **Location**: `gateway/src/main/java/com/travelassistant/gateway/config/GatewayConfig.java`
- **Changes**:
  - Added `@LoadBalanced` WebClient.Builder bean
  - Configured timeouts (30s connect, 30s read)
  - Configured buffer size (10MB)

### 7. JWT Authentication

- **Location**: `gateway/src/main/java/com/travelassistant/gateway/filter/JwtAuthenticationFilter.java`
- **Changes**:
  - Added MCP endpoints to PUBLIC_ROUTES for tool listing
  - Tool calls still require JWT (forwarded to downstream services)
  - Public routes:
    - `/mcp`, `/mcp/`
    - `/mcp/initialize`
    - `/mcp/health`
    - `/mcp/tools`

### 8. Agent Configuration

- **Location**: `travel-assistant-agent/src/agents/mcp_client.py`
- **Changes**:
  - Changed default URL from `http://localhost:8081` to `http://localhost:9000`
  - Updated timeout from 10s to 30s
  - Modified `call_tool()` to use new MCP endpoint format
  - Now calls: `POST /mcp/tools/{toolName}/call` with `{"parameters": {...}}`

## Usage Examples

### 1. Get All Tools

```bash
curl -X GET http://localhost:9000/mcp/tools
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "search_hotels",
      "name": "search_hotels",
      "description": "Search for hotels with filters...",
      "inputSchema": {...},
      "serviceName": "hotel-service",
      "httpMethod": "GET",
      "endpoint": "/api/hotel",
      "paramMapping": {...}
    },
    ...
  ]
}
```

### 2. Call Search Hotels Tool

```bash
curl -X POST http://localhost:9000/mcp/tools/search_hotels/call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "parameters": {
      "destination": "New York",
      "min_price": 100,
      "max_price": 500,
      "min_rating": 4.0
    }
  }'
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Grand Hotel",
      "destination": "New York",
      "price": 250,
      "rating": 4.5,
      ...
    }
  ]
}
```

### 3. Call Get Hotel Details Tool

```bash
curl -X POST http://localhost:9000/mcp/tools/get_hotel_details/call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "parameters": {
      "id": "550e8400-e29b-41d4-a716-446655440000"
    }
  }'
```

### 4. Create Booking

```bash
curl -X POST http://localhost:9000/mcp/tools/create_booking/call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "parameters": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "booking_type": "HOTEL",
      "resource_id": "550e8400-e29b-41d4-a716-446655440001",
      "booking_date": "2024-12-01",
      "total_price": 500
    }
  }'
```

## Agent Integration

The Agent (travel-assistant-agent) connects to the Gateway MCP server using `MultiServerMCPClient`:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

connections = {
    "java_api": {
        "url": "http://localhost:9000/mcp",
        "transport": "http"
    }
}

client = MultiServerMCPClient(connections=connections)
tools = await client.get_tools()
```

## Testing

A test script is provided at `test_mcp_implementation.py`:

```bash
python test_mcp_implementation.py
```

The script tests:
- Health check
- MCP initialize
- Get all tools
- Get individual tool definitions
- Call various tools

## Configuration

### Gateway Configuration

**application.yml**:
```yaml
server:
  port: 9000

spring:
  application:
    name: gateway
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
    gateway:
      discovery:
        locator:
          enabled: true
          lower-case-service-id: true
```

### Environment Variables

- `SERVER_PORT`: Gateway port (default: 9000)
- `NACOS_ADDR`: Nacos server address (default: localhost:8848)
- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)

## Error Handling

The MCP implementation includes comprehensive error handling:

1. **Tool Not Found**: Returns 404 with error message
2. **Service Unavailable**: Returns 500 with error from downstream service
3. **Invalid Parameters**: Returns 400 with validation error
4. **Timeout**: Returns 504 with timeout error
5. **JWT Authentication**: Returns 401 if JWT is invalid or expired

## Security

1. **JWT Forwarding**: JWT tokens are forwarded to downstream services
2. **Service Discovery**: Uses Nacos for service discovery and load balancing
3. **CORS**: Configured for frontend origins
4. **Rate Limiting**: Can be enabled via Redis

## Performance Considerations

1. **Timeouts**: Configured 30s timeout for all MCP calls
2. **Buffer Size**: 10MB buffer for large responses
3. **Connection Pooling**: WebClient uses connection pooling
4. **Caching**: Agent-side caching (Redis, 1 hour) implemented in mcp_client.py

## Troubleshooting

### Gateway Won't Start

Check:
- Nacos is running at configured address
- Redis is running (if rate limiting is enabled)
- Port 9000 is not in use

### Tool Call Fails with 404

Check:
- Tool name is correct (matches MCPToolRegistry)
- Service is registered in Nacos
- Service is running

### Tool Call Fails with 500

Check:
- Downstream service logs
- JWT token is valid
- Request parameters are correct

### Tool Call Times Out

Check:
- Downstream service is responsive
- Network connectivity
- Consider increasing timeout in GatewayConfig

## Future Enhancements

1. **Tool Caching**: Add server-side caching for frequently used tools
2. **Batch Operations**: Support calling multiple tools in one request
3. **Streaming**: Add support for streaming responses
4. **Webhooks**: Add webhook support for long-running operations
5. **Rate Limiting**: Implement per-user rate limiting
6. **Metrics**: Add Prometheus metrics for MCP calls

## References

- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Spring Cloud Gateway Documentation](https://spring.io/projects/spring-cloud-gateway)
- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
