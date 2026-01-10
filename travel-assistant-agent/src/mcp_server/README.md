# MCP Server for Claude Skills

This module provides Claude Skills integration via MCP (Model Context Protocol) for the Travel Assistant Agent.

> **Architecture Update (v2.0)**: Skills are now organized by **Agent responsibility** rather than functionality type. See [SKILLS_ARCHITECTURE.md](./SKILLS_ARCHITECTURE.md) for detailed documentation.

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
    ├── Four Agent Types
    │   ├── InfoCollectionAgent (信息收集代理)
    │   ├── SearchAgent (搜索代理)
    │   ├── RecommendationAgent (推荐代理)
    │   └── BookingAgent (预订代理)
    │
    ├── MCP Client (src/agents/mcp_client.py)
    │       │
    │       └── Connects to MCP Server
    │               │
    │               └── Skill Registry (15 skills)
    │                       ├── Info Collection (3 skills)
    │                       ├── Search (4 skills)
    │                       ├── Recommendation (4 skills)
    │                       └── Booking (4 skills)
```

## Skills by Agent Type

### InfoCollectionAgent (3 skills)
| Skill | Description |
|-------|-------------|
| `get_user_preferences` | Extract and structure user travel requirements |
| `validate_user_input` | Validate and normalize user input data |
| `suggest_destinations` | Recommend destinations based on preferences |

### SearchAgent (4 skills)
| Skill | Description |
|-------|-------------|
| `search_flights` | Search for available flights |
| `search_hotels` | Search for available hotels |
| `compare_results` | Compare and rank search results |
| `filter_by_budget` | Filter options within budget |

### RecommendationAgent (4 skills)
| Skill | Description |
|-------|-------------|
| `get_destination_info` | General destination information |
| `get_attractions` | Popular attractions and activities |
| `get_weather_forecast` | Weather forecast for travel dates |
| `get_destination_reviews` | User reviews and ratings |

### BookingAgent (4 skills)
| Skill | Description |
|-------|-------------|
| `create_booking` | Create initial booking order |
| `process_payment` | Handle payment processing |
| `confirm_booking` | Confirm booking and send confirmation |
| `get_booking_status` | Check booking status |

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

# List all skills
response = httpx.get("http://localhost:8000/mcp/skills")
print(response.json())

# Filter by agent type
response = httpx.get("http://localhost:8000/mcp/skills?agent_type=search")
print(response.json())
```

Response:
```json
{
  "skills": [
    {
      "name": "search_flights",
      "description": "Search and return available flights...",
      "category": "search",
      "version": "1.0.0",
      "input_schema": {...},
      "output_schema": {...}
    }
  ],
  "total_count": 4
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

### 1. Choose Agent Type

Determine which agent should own this skill:
- `info_collection` - User requirements and preferences
- `search` - Finding flights, hotels, options
- `recommendation` - Destination insights and activities
- `booking` - Booking process and payments

### 2. Create Skill Class

Create a new file in the appropriate agent directory:
`src/mcp_server/skills/{agent_type}/my_new_skill.py`

```python
from ..base_skill import BaseSkill

class MyNewSkill(BaseSkill):
    name = "my_new_skill"
    agent_type = "search"  # Choose appropriate agent type
    description = "Description of what my skill does"
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
    
    async def execute(self, param1: str, **kwargs) -> dict:
        # Validate input
        if not self.validate_input({"param1": param1}):
            raise ValueError("Invalid input")
        
        # Your skill logic here
        return {"result": f"Processed: {param1}"}
```

### 3. Export from Agent Module

Edit `src/mcp_server/skills/{agent_type}/__init__.py`:

```python
from .my_new_skill import MyNewSkill

__all__ = [
    # ... existing skills ...
    "MyNewSkill",
]
```

### 4. Register the Skill

Edit `src/mcp_server/skill_registry.py`:

```python
from .skills.search import MyNewSkill

class SkillRegistry:
    def _register_all_skills(self):
        # ... existing registrations ...
        self.register(MyNewSkill())
```

Also add to `src/mcp_server/skills/__init__.py`:

```python
from .search import MyNewSkill

SKILL_REGISTRY["my_new_skill"] = MyNewSkill()
```

### 5. Use the Skill

Skills are automatically discoverable via the MCP endpoints:

```python
import httpx

# List skills for specific agent
response = httpx.get("http://localhost:8000/mcp/skills?agent_type=search")

# Call the new skill
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
