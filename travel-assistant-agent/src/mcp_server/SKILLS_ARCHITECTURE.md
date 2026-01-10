# Claude Skills Architecture

## Overview

Claude Skills are now organized by **Agent responsibility** rather than functionality type. Each skill is an independent tool unit that belongs to a specific agent.

## Architecture Principles

1. **Agent-Centric Organization**: Skills are grouped by which agent uses them
2. **Single Responsibility**: Each skill does one thing well
3. **Independent Units**: Skills can be tested and used independently
4. **Clear Schemas**: Every skill has well-defined input/output schemas
5. **Registry Pattern**: Central registry manages all skills

## Four Agent Types

### 1. InfoCollectionAgent (信息收集代理)
**Responsibility**: Gathering user requirements and preferences

**Skills**:
- `get_user_preferences` - Extract travel requirements from user input
- `validate_user_input` - Validate and normalize user data
- `suggest_destinations` - Recommend destinations based on preferences

**Use Case**: Initial conversation with user to understand their needs

### 2. SearchAgent (搜索代理)
**Responsibility**: Finding flights, hotels, and comparing options

**Skills**:
- `search_flights` - Query available flights
- `search_hotels` - Query available hotels
- `compare_results` - Compare and rank search results
- `filter_by_budget` - Filter options within budget

**Use Case**: Finding and comparing travel options

### 3. RecommendationAgent (推荐代理)
**Responsibility**: Providing destination insights and activity recommendations

**Skills**:
- `get_destination_info` - General destination information
- `get_attractions` - Popular attractions and activities
- `get_weather_forecast` - Weather forecast for travel dates
- `get_destination_reviews` - User reviews and ratings

**Use Case**: Enriching trip planning with destination insights

### 4. BookingAgent (预订代理)
**Responsibility**: Managing the booking process

**Skills**:
- `create_booking` - Create initial booking order
- `process_payment` - Handle payment processing
- `confirm_booking` - Confirm booking and send confirmation
- `get_booking_status` - Check booking status

**Use Case**: Completing the booking transaction

## Directory Structure

```
src/mcp_server/
├── __init__.py                   # Package exports
├── server.py                     # MCP Server (registry & dispatcher)
├── config.py                     # Configuration
├── skill_registry.py             # Central skill registry
├── skills/
│   ├── __init__.py               # Skills exports
│   ├── base_skill.py             # BaseSkill class
│   ├── info_collection/
│   │   ├── __init__.py
│   │   ├── get_user_preferences.py
│   │   ├── validate_user_input.py
│   │   └── suggest_destinations.py
│   ├── search/
│   │   ├── __init__.py
│   │   ├── search_flights.py
│   │   ├── search_hotels.py
│   │   ├── compare_results.py
│   │   └── filter_by_budget.py
│   ├── recommendation/
│   │   ├── __init__.py
│   │   ├── get_destination_info.py
│   │   ├── get_attractions.py
│   │   ├── get_weather_forecast.py
│   │   └── get_destination_reviews.py
│   └── booking/
│       ├── __init__.py
│       ├── create_booking.py
│       ├── process_payment.py
│       ├── confirm_booking.py
│       └── get_booking_status.py
```

## BaseSkill Class

All skills inherit from `BaseSkill`:

```python
class BaseSkill(ABC):
    name: str                      # Unique skill name
    agent_type: str               # Which agent uses this
    description: str              # Human-readable description
    version: str                  # Skill version
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema for inputs"""
        
    @property
    def output_schema(self) -> Dict[str, Any]:
        """JSON Schema for outputs"""
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill"""
    
    def validate_input(self, data: Dict) -> bool:
        """Validate input against schema"""
    
    def to_definition(self) -> Dict[str, Any]:
        """Convert to MCP definition format"""
```

## Skill Registry

The `SkillRegistry` manages all skills:

```python
from mcp_server import get_skill_registry

registry = get_skill_registry()

# Get all skills
all_skills = registry.get_all()

# Get skills by agent type
search_skills = registry.get_by_agent_type("search")

# Get specific skill
flight_skill = registry.get("search_flights")

# Execute skill
result = await flight_skill.execute(
    origin="NYC",
    destination="Tokyo",
    departure_date="2024-05-01",
    passengers=2
)
```

## MCP Server

The MCP Server acts as a registry and dispatcher:

### Endpoints

```python
# List all skills (optionally filtered by agent_type)
GET /mcp/skills?agent_type=search

# Get specific skill info
GET /mcp/skills/{skill_name}

# Execute a skill
POST /mcp/call-skill
{
    "skill_name": "search_flights",
    "parameters": {...}
}

# Execute multiple skills
POST /mcp/batch-call
{
    "calls": [
        {"skill_name": "search_flights", "parameters": {...}},
        {"skill_name": "search_hotels", "parameters": {...}}
    ]
}
```

## Agent Integration

Each agent knows which skills it needs:

```python
class SearchAgent:
    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client
        
        # Get specific skills this agent needs
        self.search_flights = mcp_client.get_skill("search_flights")
        self.search_hotels = mcp_client.get_skill("search_hotels")
        self.compare = mcp_client.get_skill("compare_results")
        self.filter = mcp_client.get_skill("filter_by_budget")
    
    async def search(self, request):
        # Use skills in sequence
        flights = await self.search_flights.execute(...)
        hotels = await self.search_hotels.execute(...)
        compared = await self.compare.execute(...)
        filtered = await self.filter.execute(...)
        return SearchResults(...)
```

## Creating a New Skill

1. Create a new file in the appropriate agent directory
2. Inherit from `BaseSkill`
3. Define metadata (name, agent_type, description)
4. Define input/output schemas
5. Implement `execute()` method
6. Register in `skill_registry.py`
7. Export in `skills/__init__.py`
8. Add tests

### Example:

```python
from ..base_skill import BaseSkill

class NewSkill(BaseSkill):
    name = "new_skill"
    agent_type = "search"
    description = "Does something useful"
    version = "1.0.0"
    
    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
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
    
    async def execute(self, param1: str, **kwargs):
        if not self.validate_input({"param1": param1}):
            raise ValueError("Invalid input")
        
        # Implementation
        return {"result": f"Processed {param1}"}
```

## Testing Skills

Each skill should have unit tests:

```python
import pytest
from mcp_server.skills.search import SearchFlightsSkill

@pytest.mark.asyncio
async def test_search_flights():
    skill = SearchFlightsSkill()
    
    result = await skill.execute(
        origin="NYC",
        destination="Tokyo",
        departure_date="2024-05-01",
        passengers=2
    )
    
    assert "outbound_flights" in result
    assert len(result["outbound_flights"]) > 0
    assert result["search_metadata"]["passengers"] == 2
```

## Migration from Old Structure

### Old (Function-based):
- `destination.py` - SearchDestinationSkill
- `pricing.py` - QueryPricesSkill
- `reviews.py` - GetDestinationReviewsSkill
- `weather.py` - GetWeatherSkill
- `planning.py` - CreateTravelPlanSkill

### New (Agent-based):
Skills distributed across 4 agent types with 15 total skills

**Legacy support** is maintained for backward compatibility.

## Benefits

1. **Clear Ownership**: Each agent owns its skills
2. **Better Testing**: Skills can be tested in isolation
3. **Easier Maintenance**: Find skills by agent responsibility
4. **Scalability**: Add new skills to appropriate agent
5. **Reusability**: Skills are independent units
6. **Type Safety**: Clear input/output contracts

## Future Enhancements

- Skill versioning and deprecation
- Skill composition (skills calling other skills)
- Skill caching and memoization
- Skill metrics and monitoring
- Skill A/B testing
- Real API integrations (replace mock data)
