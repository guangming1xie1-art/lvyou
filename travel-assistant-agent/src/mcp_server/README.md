# MCP Server for Claude Skills

This module provides Claude Skills integration via MCP (Model Context Protocol) for the Travel Assistant Agent.

## Overview

The MCP (Model Context Protocol) enables the Agent to:
- **Discover** available skills at runtime
- **Invoke** skills with structured parameters
- **Constrain** agent behavior to specific task domains
- **Extend** capabilities without modifying core agent code

## Architecture

```
travel-assistant-agent (Python FastAPI)
    │
    ├── MCP Client (src/agents/mcp_client.py)
    │       │
    │       └── Connects to MCP Server
    │               │
    │               └── Skills Registry
    │                       ├── SearchDestinationSkill
    │                       ├── QueryPricesSkill
    │                       ├── GetDestinationReviewsSkill
    │                       ├── GetWeatherSkill
    │                       └── CreateTravelPlanSkill
```

## Skills

### Available Skills

| Skill | Category | Description |
|-------|----------|-------------|
| `search_destination` | destination | Search and get destination information including attractions, culture, and tips |
| `query_prices` | pricing | Query hotel and flight prices for budgeting |
| `get_destination_reviews` | reviews | Fetch user reviews, ratings, and sentiment analysis |
| `get_weather` | weather | Get current weather and forecast for destinations |
| `create_travel_plan` | planning | Generate comprehensive travel itineraries |

### Skill Schema

Each skill follows the MCP specification with:
- **Name**: Unique identifier
- **Description**: Human-readable purpose
- **Input Schema**: JSON Schema for parameters
- **Output Schema**: JSON Schema for results
- **Category**: Skill classification
- **Version**: Skill version for compatibility

## Usage

### 1. Listing Available Skills

```python
import httpx

response = httpx.get("http://localhost:8000/mcp/skills")
print(response.json())
```

Response:
```json
{
  "skills": [
    {
      "name": "search_destination",
      "description": "Search for travel destination information...",
      "category": "destination",
      "version": "1.0.0",
      "input_schema": {...},
      "output_schema": {...}
    }
  ],
  "total_count": 5
}
```

### 2. Calling a Single Skill

```python
import httpx

response = httpx.post(
    "http://localhost:8000/mcp/call-skill",
    json={
        "skill_name": "search_destination",
        "parameters": {
            "destination": "Tokyo",
            "include_tips": True
        }
    }
)
print(response.json())
```

### 3. Batch Skill Execution

```python
import httpx

response = httpx.post(
    "http://localhost:8000/mcp/batch-call",
    json={
        "calls": [
            {"skill_name": "search_destination", "parameters": {"destination": "Tokyo"}},
            {"skill_name": "get_weather", "parameters": {"destination": "Tokyo"}}
        ]
    }
)
print(response.json())
```

### 4. Demo Planning Endpoint

```python
import httpx

response = httpx.post(
    "http://localhost:8000/agent/demo-planning-with-skills",
    json={
        "destination": "Tokyo",
        "duration_days": 5,
        "budget": 2000,
        "start_date": "2024-04-01",
        "end_date": "2024-04-06"
    }
)
print(response.json())
```

## Adding New Skills

### 1. Create Skill Class

Create a new file in `src/mcp_server/skills/`:

```python
from .base_skill import BaseSkill

class MyNewSkill(BaseSkill):
    name = "my_new_skill"
    description = "Description of what my skill does"
    category = "my_category"
    version = "1.0.0"
    
    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "First parameter"}
            },
            "required": ["param1"]
        }
    
    @property
    def output_schema(self):
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            }
        }
    
    async def execute(self, param1: str) -> dict:
        # Your skill logic here
        return {"result": f"Processed: {param1}"}
```

### 2. Register the Skill

Edit `src/mcp_server/skills/__init__.py`:

```python
from .my_new import MyNewSkill

SKILL_REGISTRY = {
    # ... existing skills ...
    "my_new_skill": MyNewSkill(),
}
```

### 3. Use the Skill

Skills are automatically discoverable via the MCP endpoints:

```python
import httpx

response = httpx.post(
    "http://localhost:8000/mcp/call-skill",
    json={
        "skill_name": "my_new_skill",
        "parameters": {"param1": "test value"}
    }
)
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_ENABLED` | `true` | Enable MCP integration |
| `MCP_SERVER_URL` | `http://localhost:8765` | MCP server URL |
| `MCP_TRANSPORT` | `stdio` | Transport protocol (stdio/sse) |

### Docker

The MCP server runs alongside the FastAPI app. No separate container needed for the demo.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mcp/skills` | List all available skills |
| GET | `/mcp/status` | Get MCP client status |
| POST | `/mcp/call-skill` | Call a single skill |
| POST | `/mcp/batch-call` | Call multiple skills |
| POST | `/agent/demo-planning-with-skills` | Demo planning workflow |

## Integration with Agent

The `SkillBasedAgent` class provides a convenient interface:

```python
from agents import SkillBasedAgent, get_mcp_client

async def plan_trip():
    # Get the MCP client
    client = get_mcp_client()
    
    # Create agent
    agent = SkillBasedAgent(mcp_client=client)
    
    # Process request
    state = {
        "user_message": "Plan a 5-day trip to Tokyo",
        "metadata": {"budget": 2000}
    }
    
    result = await agent.run(state)
    return result
```

## Best Practices

1. **Skill Design**: Each skill should have a single, well-defined purpose
2. **Error Handling**: Skills should return meaningful error messages
3. **Versioning**: Increment version when changing skill behavior
4. **Documentation**: Keep descriptions clear and comprehensive
5. **Testing**: Test skills independently before integration

## Future Enhancements

- Real API integrations for live data
- Skill caching and hot-reloading
- Async skill execution with dependencies
- Skill marketplace for community contributions
- Claude AI integration for intelligent skill selection
