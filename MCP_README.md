# MCP Server Implementation for Travel Assistant Gateway

## 🎯 What is this?

This implementation adds a complete **MCP (Model Context Protocol) server** to the Travel Assistant Gateway service. The Gateway now acts as a unified entry point for all AI tool calls, routing them to appropriate microservices.

## 📋 What Was Implemented

### ✅ Core Components

1. **ToolDefinition Model** - Defines MCP tool structure
2. **MCPResponse Model** - Unified response format
3. **MCPToolRegistry** - Registers and manages 10 tools
4. **MCPToolRouter** - Routes tool calls to microservices
5. **MCPController** - REST API endpoints

### ✅ 10 MCP Tools

| # | Tool | Service | Description |
|---|------|---------|-------------|
| 1 | `search_hotels` | hotel-service | Search hotels with filters |
| 2 | `get_hotel_details` | hotel-service | Get hotel details by ID |
| 3 | `search_flights` | flight-service | Search flights with filters |
| 4 | `get_flight_details` | flight-service | Get flight details by ID |
| 5 | `search_attractions` | attraction-service | Search attractions with filters |
| 6 | `get_attraction_details` | attraction-service | Get attraction details by ID |
| 7 | `create_booking` | booking-service | Create a new booking |
| 8 | `get_booking_status` | booking-service | Get booking status |
| 9 | `get_recommendations` | recommendation-service | Get comprehensive recommendations |
| 10 | `get_hotel_recommendations` | recommendation-service | Get hotel recommendations |

### ✅ Key Features

- **Unified Entry Point**: All tools accessible via Gateway (port 9000)
- **Service Discovery**: Uses Nacos for load balancing
- **JWT Forwarding**: Auth headers forwarded to downstream services
- **Parameter Mapping**: Automatic snake_case → camelCase conversion
- **Error Handling**: Structured error responses
- **MCP Compatible**: Works with `langchain_mcp_adapters.MultiServerMCPClient`

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│  Agent (Python)                   │
│  - MultiServerMCPClient           │
└────────────┬───────────────────────┘
             │
             │ http://localhost:9000/mcp/tools/{name}/call
             │
┌────────────▼───────────────────────┐
│  Gateway (Spring Cloud)           │
│  ├─ MCPController (REST API)      │
│  ├─ MCPToolRegistry (10 tools)    │
│  └─ MCPToolRouter (WebClient)    │
└────────────┬───────────────────────┘
             │
             │ Load Balanced (Nacos)
             │
    ┌────────┼────────┬────────┐
    │        │        │        │
   Hotel   Flight  Attraction Booking
```

## 🚀 Quick Start

### 1. Start Gateway

```bash
cd travel-assistant/gateway
mvn spring-boot:run
```

Gateway starts on port 9000.

### 2. Test MCP Endpoints

```bash
# Health check
curl http://localhost:9000/mcp/health

# Get all tools
curl http://localhost:9000/mcp/tools

# Get specific tool
curl http://localhost:9000/mcp/tools/search_hotels

# Call tool (without auth)
curl -X POST http://localhost:9000/mcp/tools/search_hotels/call \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"destination": "New York", "min_price": 100}}'

# Call tool (with JWT)
curl -X POST http://localhost:9000/mcp/tools/search_hotels/call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"parameters": {"destination": "New York"}}'
```

### 3. Use from Agent

```python
from travel_assistant_agent.src.agents.mcp_client import MCPClient

client = MCPClient()

# Search hotels
result = await client.call_tool(
    "search_hotels",
    {"destination": "New York", "min_price": 100}
)
print(result)

# Search flights
result = await client.call_tool(
    "search_flights",
    {"origin": "NYC", "destination": "LAX", "departure_date": "2024-12-01"}
)
print(result)

# Get recommendations
result = await client.call_tool(
    "get_recommendations",
    {"user_id": "550e8400-e29b-41d4-a716-446655440000", "type": "comprehensive"}
)
print(result)
```

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/mcp/health` | Health check | No |
| GET | `/mcp/tools` | Get all tool definitions | No |
| GET | `/mcp/tools/{toolName}` | Get specific tool definition | No |
| POST | `/mcp/tools/{toolName}/call` | Call a tool | Yes (JWT) |
| POST | `/mcp/initialize` | MCP protocol init | No |

### Request Format

#### Call Tool
```json
{
  "parameters": {
    "destination": "New York",
    "min_price": 100,
    "max_price": 500
  }
}
```

#### Success Response
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Grand Hotel",
      "destination": "New York",
      "price": 250,
      "rating": 4.5
    }
  ]
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Tool not found: invalid_tool"
}
```

## 🧪 Testing

### Validation Script

```bash
python validate_mcp_server.py
```

Validates all files and configurations.

### Test Script

```bash
python test_mcp_implementation.py
```

Tests all MCP endpoints and tool calls.

### Expected Results

- ✅ 21/21 validation checks pass
- ✅ Gateway starts without errors
- ✅ All 10 tools registered
- ✅ Tool calls routed correctly
- ✅ JWT forwarding works

## 📁 File Structure

```
travel-assistant/gateway/src/main/java/com/travelassistant/gateway/
├── mcp/
│   ├── model/
│   │   ├── ToolDefinition.java      # Tool definition model
│   │   └── MCPResponse.java        # Unified response format
│   ├── MCPToolRegistry.java        # Tool registry (10 tools)
│   ├── MCPToolRouter.java          # Router using WebClient
│   └── MCPController.java         # REST endpoints
├── config/
│   └── GatewayConfig.java         # WebClient configuration
└── filter/
    └── JwtAuthenticationFilter.java # MCP public routes
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `SERVER_PORT` | Gateway port | 9000 |
| `NACOS_ADDR` | Nacos address | localhost:8848 |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |

### Timeout Settings

- Connect timeout: 5 seconds
- Read timeout: 30 seconds
- Write timeout: 30 seconds
- Response buffer: 10 MB

## 🔐 Security

### Authentication

- Tool listing (GET /mcp/tools): **No auth required**
- Tool calling (POST /mcp/tools/{tool}/call): **JWT required**
- JWT is forwarded to all downstream services

### JWT Forwarding

The Gateway forwards the Authorization header to downstream services:

```http
POST /mcp/tools/search_hotels/call
Authorization: Bearer YOUR_JWT_TOKEN

↓ Gateway routes to hotel-service

GET /api/hotel?destination=NewYork
Authorization: Bearer YOUR_JWT_TOKEN  # Forwarded
```

## 📖 Documentation

| Document | Description |
|----------|-------------|
| `MCP_QUICK_REFERENCE.md` | Quick reference guide |
| `MCP_IMPLEMENTATION_GUIDE.md` | Comprehensive implementation guide |
| `MCP_IMPLEMENTATION_SUMMARY.md` | Implementation summary |
| This README | Overview and quick start |

## ✅ Verification Checklist

- [x] All 10 MCP tools registered
- [x] Tool definitions with valid JSON Schema
- [x] MCPController with all required endpoints
- [x] MCPToolRouter with proper routing
- [x] WebClient configuration with timeouts
- [x] JWT forwarding to downstream services
- [x] MCP endpoints in public routes (for listing)
- [x] Agent configuration updated (port 9000)
- [x] Comprehensive error handling
- [x] Validation scripts created
- [x] Documentation complete

## 🐛 Troubleshooting

### Gateway won't start

**Problem**: Gateway fails to start

**Solutions**:
- Check Nacos is running at configured address
- Check Redis is running (if rate limiting enabled)
- Check port 9000 is not in use
- Check Java version (requires Java 17+)

### Tool call returns 404

**Problem**: `{"success": false, "error": "Tool not found: ..."}`

**Solutions**:
- Verify tool name is correct (use `GET /mcp/tools` to list)
- Check tool is registered in MCPToolRegistry
- Check service is registered in Nacos

### Tool call returns 500

**Problem**: `{"success": false, "error": "Service error: ..."}`

**Solutions**:
- Check downstream service logs
- Verify JWT token is valid and not expired
- Check request parameters match tool schema
- Verify network connectivity to service

### Tool call times out

**Problem**: Request takes too long and times out

**Solutions**:
- Check downstream service is responsive
- Check network latency
- Increase timeout in GatewayConfig (currently 30s)
- Check service logs for long-running queries

### Agent can't connect

**Problem**: Agent fails to connect to MCP server

**Solutions**:
- Verify Gateway is running on port 9000
- Check Agent configuration in `mcp_client.py`
- Verify network connectivity
- Check Firewall settings

## 🎓 Learning Resources

- [MCP Protocol](https://modelcontextprotocol.io)
- [Spring Cloud Gateway](https://spring.io/projects/spring-cloud-gateway)
- [Nacos Discovery](https://nacos.io/)
- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)

## 🚀 Next Steps

### Optional Enhancements

1. **Server-Side Caching**
   - Cache frequently used tool results
   - Reduce load on downstream services

2. **Batch Operations**
   - Call multiple tools in one request
   - Reduce network round trips

3. **Streaming Responses**
   - Stream large datasets
   - Improve response times

4. **Rate Limiting**
   - Implement per-user limits
   - Protect against abuse

5. **Metrics & Monitoring**
   - Add Prometheus metrics
   - Track tool usage

6. **Webhooks**
   - Support long-running operations
   - Enable async processing

## 📝 Summary

This implementation successfully adds a complete MCP server to the Gateway service. All validation checks pass, and the system is fully compatible with the existing Agent and microservice architecture.

**Benefits**:
- ✅ Simplified Agent integration
- ✅ Better security with centralized auth
- ✅ Improved scalability via load balancing
- ✅ Better maintainability
- ✅ Enhanced observability

**Result**: A production-ready MCP server that enables AI agents to call travel booking tools through a unified, secure gateway.

---

**Questions?** Check the detailed documentation in `MCP_IMPLEMENTATION_GUIDE.md`
