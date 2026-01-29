# MCP Server Quick Reference

## Quick Start

### 1. Start Gateway
```bash
cd travel-assistant/gateway
mvn spring-boot:run
```

Gateway will start on port 9000.

### 2. Test MCP Endpoints

```bash
# Health check
curl http://localhost:9000/mcp/health

# Get all tools
curl http://localhost:9000/mcp/tools

# Get specific tool
curl http://localhost:9000/mcp/tools/search_hotels

# Call tool
curl -X POST http://localhost:9000/mcp/tools/search_hotels/call \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"destination": "New York"}}'
```

### 3. Test with Agent
```python
from travel_assistant_agent.src.agents.mcp_client import MCPClient

client = MCPClient()
result = await client.call_tool(
    "search_hotels",
    {"destination": "New York", "min_price": 100}
)
print(result)
```

## Available Tools

### Hotels
- **search_hotels**: Search hotels by destination, price, rating, facilities
- **get_hotel_details**: Get hotel details by ID

### Flights
- **search_flights**: Search flights by route, date, price, airline
- **get_flight_details**: Get flight details by ID

### Attractions
- **search_attractions**: Search attractions by location, category, rating, tags
- **get_attraction_details**: Get attraction details by ID

### Bookings
- **create_booking**: Create a new booking
- **get_booking_status**: Get booking status by ID

### Recommendations
- **get_recommendations**: Get comprehensive recommendations
- **get_hotel_recommendations**: Get hotel recommendations

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /mcp/health | Health check |
| GET | /mcp/tools | Get all tools |
| GET | /mcp/tools/{toolName} | Get tool definition |
| POST | /mcp/tools/{toolName}/call | Call tool |
| POST | /mcp/initialize | MCP initialize |

## Request Format

### Call Tool Request
```json
{
  "parameters": {
    "destination": "New York",
    "min_price": 100,
    "max_price": 500
  }
}
```

### Success Response
```json
{
  "success": true,
  "data": [...]
}
```

### Error Response
```json
{
  "success": false,
  "error": "Tool not found: invalid_tool"
}
```

## Authentication

Tool calls require JWT authentication:
```bash
curl -X POST http://localhost:9000/mcp/tools/search_hotels/call \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"parameters": {...}}'
```

## Files Structure

```
travel-assistant/gateway/src/main/java/com/travelassistant/gateway/
├── mcp/
│   ├── model/
│   │   ├── ToolDefinition.java
│   │   └── MCPResponse.java
│   ├── MCPToolRegistry.java
│   ├── MCPToolRouter.java
│   └── MCPController.java
├── config/
│   └── GatewayConfig.java (with WebClient.Builder)
└── filter/
    └── JwtAuthenticationFilter.java (MCP public routes)
```

## Troubleshooting

### Gateway won't start
- Check Nacos is running
- Check port 9000 is not in use
- Check Redis is running (if rate limiting enabled)

### Tool call returns 404
- Verify tool name is correct
- Check tool is registered in MCPToolRegistry
- Verify service is registered in Nacos

### Tool call returns 500
- Check downstream service logs
- Verify JWT token is valid
- Check network connectivity

### Agent can't connect
- Verify Gateway is running on port 9000
- Check Agent configuration (mcp_client.py)
- Verify network connectivity

## Documentation

- **Full Guide**: `MCP_IMPLEMENTATION_GUIDE.md`
- **Summary**: `MCP_IMPLEMENTATION_SUMMARY.md`
- **Validation**: Run `python validate_mcp_server.py`
- **Testing**: Run `python test_mcp_implementation.py`
