# Technical Design: Refactor Claude Skills to Agent-Centric Architecture

## Architecture Overview

### Current State (Functionality-Based)
```
src/mcp_server/skills/
├── base_skill.py
├── __init__.py (SKILL_REGISTRY)
├── destination.py       # SearchDestinationSkill
├── pricing.py           # QueryPricesSkill
├── reviews.py           # GetDestinationReviewsSkill
├── weather.py           # GetWeatherSkill
└── planning.py          # CreateTravelPlanSkill
```

**Problems:**
- Skills grouped by what they do, not who uses them
- Unclear which agent needs which skill
- Mixed concerns within individual skills
- Hard to extend for new agent capabilities

### Target State (Agent-Centric)
```
src/mcp_server/
├── base_skill.py          # BaseSkill abstract class
├── skill_registry.py      # SkillRegistry singleton
├── server.py              # MCP Server (refactored)
└── skills/
    ├── __init__.py        # Exports all skills
    ├── info_collection/
    │   ├── __init__.py
    │   ├── get_user_preferences.py
    │   ├── validate_user_input.py
    │   └── suggest_destinations.py
    ├── search/
    │   ├── __init__.py
    │   ├── search_flights.py
    │   ├── search_hotels.py
    │   ├── compare_search_results.py
    │   └── filter_by_budget.py
    ├── recommendation/
    │   ├── __init__.py
    │   ├── get_destination_info.py
    │   ├── get_attractions.py
    │   ├── get_weather_forecast.py
    │   └── get_destination_reviews.py
    └── booking/
        ├── __init__.py
        ├── create_booking.py
        ├── process_payment.py
        ├── confirm_booking.py
        └── get_booking_status.py
```

**Benefits:**
- Clear agent ownership of skills
- Single responsibility per skill
- Easy to discover what each agent can do
- Scalable for adding new skills

## Skill Organization by Agent

### InfoCollectionAgent (3 Skills)
**Responsibility**: Gather and validate user travel preferences

| Skill | Purpose | Inputs | Outputs |
|-------|---------|--------|---------|
| `GetUserPreferencesSkill` | Collect travel preferences | preference_type, context | preferences dict |
| `ValidateUserInputSkill` | Validate and normalize input | input_data, rules | is_valid, errors, normalized |
| `SuggestDestinationsSkill` | Suggest destinations | budget, interests, season | suggestions with scores |

**Usage Pattern:**
```python
agent = InfoCollectionAgent()
preferences = await agent.call_skill("get_user_preferences", 
    preference_type="budget", context={...})
validated = await agent.call_skill("validate_user_input",
    input_data=preferences, validation_rules={...})
suggestions = await agent.call_skill("suggest_destinations",
    budget=validated['budget'], interests=validated['interests'])
```

### SearchAgent (4 Skills)
**Responsibility**: Find and compare travel options

| Skill | Purpose | Inputs | Outputs |
|-------|---------|--------|---------|
| `SearchFlightsSkill` | Find flight options | origin, destination, dates, passengers | flights list |
| `SearchHotelsSkill` | Find hotel options | destination, dates, guests, stars | hotels list |
| `CompareSearchResultsSkill` | Compare options | results_list, criteria | comparison, recommendation |
| `FilterByBudgetSkill` | Filter by budget | results, budget, budget_type | filtered_results, analysis |

**Usage Pattern:**
```python
agent = SearchAgent()
flights = await agent.call_skill("search_flights",
    origin="NYC", destination="Tokyo", dates={...})
hotels = await agent.call_skill("search_hotels",
    destination="Tokyo", dates={...})
comparison = await agent.call_skill("compare_search_results",
    results_list=[flights, hotels], criteria={...})
```

### RecommendationAgent (4 Skills)
**Responsibility**: Provide destination insights and recommendations

| Skill | Purpose | Inputs | Outputs |
|-------|---------|--------|---------|
| `GetDestinationInfoSkill` | Get destination details | destination, info_type | destination info |
| `GetAttractionsSkill` | Get attractions | destination, type, limit | attractions list |
| `GetWeatherForecastSkill` | Get weather forecast | destination, dates | forecast by day |
| `GetDestinationReviewsSkill` | Get reviews | destination, review_type, limit | reviews with ratings |

**Usage Pattern:**
```python
agent = RecommendationAgent()
info = await agent.call_skill("get_destination_info",
    destination="Tokyo", info_type="overview")
attractions = await agent.call_skill("get_attractions",
    destination="Tokyo", attraction_type="landmarks")
weather = await agent.call_skill("get_weather_forecast",
    destination="Tokyo", dates={...})
```

### BookingAgent (4 Skills)
**Responsibility**: Handle booking workflow from creation to confirmation

| Skill | Purpose | Inputs | Outputs |
|-------|---------|--------|---------|
| `CreateBookingSkill` | Create initial booking | booking_type, details, user_info | booking_id, status |
| `ProcessPaymentSkill` | Process payment | booking_id, payment_method, amount | payment_status, transaction_id |
| `ConfirmBookingSkill` | Confirm booking | booking_id, confirmation_details | confirmation_code |
| `GetBookingStatusSkill` | Check booking status | booking_id or confirmation_code | status, details, timeline |

**Usage Pattern:**
```python
agent = BookingAgent()
booking = await agent.call_skill("create_booking",
    booking_type="flight", details={...})
payment = await agent.call_skill("process_payment",
    booking_id=booking['booking_id'], payment_method="card")
confirmation = await agent.call_skill("confirm_booking",
    booking_id=booking['booking_id'])
```

## BaseSkill Interface

### Class Definition
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum

class AgentType(Enum):
    """Agent types that use skills"""
    INFO_COLLECTION = "info_collection"
    SEARCH = "search"
    RECOMMENDATION = "recommendation"
    BOOKING = "booking"

class BaseSkill(ABC):
    """Base class for all Claude Skills"""
    
    # Required class attributes
    name: str                    # Unique skill identifier (snake_case)
    agent_type: AgentType        # Which agent uses this skill
    description: str             # Human-readable description
    category: str                # Functional category
    version: str = "1.0.0"       # Semantic version
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema for input validation"""
        pass
    
    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        """JSON Schema for output validation"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill with given parameters"""
        pass
    
    def validate_input(self, **kwargs) -> Dict[str, Any]:
        """Validate inputs against input_schema"""
        # Use jsonschema library
        pass
    
    def to_definition(self) -> Dict[str, Any]:
        """Convert skill to MCP definition format"""
        return {
            "name": self.name,
            "agent_type": self.agent_type.value,
            "description": self.description,
            "inputSchema": self.input_schema,
            "outputSchema": self.output_schema,
            "category": self.category,
            "version": self.version
        }
    
    def format_output(self, result: Dict[str, Any]) -> str:
        """Format result as readable string for agent"""
        import json
        return json.dumps(result, indent=2, ensure_ascii=False)
```

### Example Skill Implementation
```python
class SearchFlightsSkill(BaseSkill):
    """Search for flight options"""
    
    name = "search_flights"
    agent_type = AgentType.SEARCH
    description = "Search for flight options between origin and destination"
    category = "search"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Origin airport code"},
                "destination": {"type": "string", "description": "Destination code"},
                "departure_date": {"type": "string", "format": "date"},
                "return_date": {"type": "string", "format": "date"},
                "passengers": {"type": "integer", "minimum": 1},
                "cabin_class": {
                    "type": "string", 
                    "enum": ["economy", "business", "first"]
                }
            },
            "required": ["origin", "destination", "departure_date", "passengers"]
        }
    
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "flights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "flight_id": {"type": "string"},
                            "airline": {"type": "string"},
                            "price": {"type": "number"},
                            "duration": {"type": "string"},
                            "stops": {"type": "integer"}
                        }
                    }
                },
                "total_results": {"type": "integer"}
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        # Validate inputs
        validated = self.validate_input(**kwargs)
        
        # Mock flight search logic
        flights = self._search_flights_mock(validated)
        
        return {
            "flights": flights,
            "total_results": len(flights),
            "search_params": validated
        }
    
    def _search_flights_mock(self, params: Dict) -> List[Dict]:
        # Mock implementation with sample data
        return [
            {
                "flight_id": "AA123",
                "airline": "American Airlines",
                "price": 450.00,
                "duration": "14h 30m",
                "stops": 1
            },
            # More mock flights...
        ]
```

## SkillRegistry Design

### Class Definition
```python
from typing import Dict, List, Optional
from .base_skill import BaseSkill, AgentType

class SkillRegistry:
    """Central registry for all Claude Skills"""
    
    _instance = None  # Singleton instance
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._skills = {}
        return cls._instance
    
    def register(self, skill: BaseSkill) -> None:
        """Register a skill in the registry"""
        if skill.name in self._skills:
            raise ValueError(f"Skill {skill.name} already registered")
        self._skills[skill.name] = skill
    
    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """Get a skill by name"""
        return self._skills.get(name)
    
    def get_skills_by_agent(self, agent_type: AgentType) -> List[BaseSkill]:
        """Get all skills for a specific agent"""
        return [
            skill for skill in self._skills.values()
            if skill.agent_type == agent_type
        ]
    
    def get_skills_by_category(self, category: str) -> List[BaseSkill]:
        """Get skills by functional category"""
        return [
            skill for skill in self._skills.values()
            if skill.category == category
        ]
    
    def get_all_skills(self) -> List[BaseSkill]:
        """Get all registered skills"""
        return list(self._skills.values())
    
    def get_skill_definitions(self) -> List[Dict]:
        """Get all skill definitions for MCP"""
        return [skill.to_definition() for skill in self._skills.values()]
    
    async def execute_skill(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a skill by name"""
        skill = self.get_skill(name)
        if not skill:
            raise ValueError(f"Skill {name} not found")
        return await skill.execute(**kwargs)
```

### Registry Initialization
```python
# In src/mcp_server/skills/__init__.py

from ..skill_registry import SkillRegistry
from .info_collection import *
from .search import *
from .recommendation import *
from .booking import *

# Get singleton registry
registry = SkillRegistry()

# Register all skills
registry.register(GetUserPreferencesSkill())
registry.register(ValidateUserInputSkill())
registry.register(SuggestDestinationsSkill())
registry.register(SearchFlightsSkill())
registry.register(SearchHotelsSkill())
# ... register all 15 skills

__all__ = ["registry"]
```

## MCP Server Changes

### Current MCP Server
```python
# src/mcp_server/server.py (OLD)
from .skills import SKILL_REGISTRY, get_skill

@app.get("/mcp/skills")
async def list_skills():
    return {"skills": [s.to_definition() for s in SKILL_REGISTRY.values()]}

@app.post("/mcp/execute/{skill_name}")
async def execute_skill(skill_name: str, params: Dict):
    skill = get_skill(skill_name)
    return await skill.execute(**params)
```

### New MCP Server (Registry-Based)
```python
# src/mcp_server/server.py (NEW)
from .skill_registry import SkillRegistry

# Initialize registry at startup
@app.on_event("startup")
async def startup_event():
    # Import skills package to trigger registration
    from . import skills
    registry = SkillRegistry()
    print(f"Registered {len(registry.get_all_skills())} skills")

@app.get("/mcp/skills")
async def list_skills(agent_type: Optional[str] = None):
    """List all skills, optionally filtered by agent"""
    registry = SkillRegistry()
    
    if agent_type:
        skills = registry.get_skills_by_agent(AgentType(agent_type))
    else:
        skills = registry.get_all_skills()
    
    return {
        "skills": [s.to_definition() for s in skills],
        "total": len(skills)
    }

@app.post("/mcp/execute/{skill_name}")
async def execute_skill(skill_name: str, params: Dict):
    """Execute a specific skill by name"""
    registry = SkillRegistry()
    
    try:
        result = await registry.execute_skill(skill_name, **params)
        return {"success": True, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/batch-execute")
async def batch_execute_skills(requests: List[Dict]):
    """Execute multiple skills in parallel"""
    registry = SkillRegistry()
    
    tasks = [
        registry.execute_skill(req["skill_name"], **req.get("params", {}))
        for req in requests
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        "results": [
            {"success": not isinstance(r, Exception), "result": r}
            for r in results
        ]
    }
```

## Agent Integration

### BaseAgent Updates
```python
# src/agents/base.py
from src.mcp_server.skill_registry import SkillRegistry

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self):
        self.registry = SkillRegistry()
        self.agent_type = None  # Override in subclass
    
    async def call_skill(self, skill_name: str, **kwargs) -> Dict[str, Any]:
        """Call a skill by name"""
        return await self.registry.execute_skill(skill_name, **kwargs)
    
    def get_available_skills(self) -> List[BaseSkill]:
        """Get all skills available to this agent"""
        return self.registry.get_skills_by_agent(self.agent_type)
```

### InfoCollectionAgent Example
```python
# src/agents/info_collection.py
from .base import BaseAgent
from src.mcp_server.base_skill import AgentType

class InfoCollectionAgent(BaseAgent):
    """Agent for collecting user travel preferences"""
    
    def __init__(self):
        super().__init__()
        self.agent_type = AgentType.INFO_COLLECTION
    
    async def collect_preferences(self, user_input: str) -> Dict:
        """Collect and validate user preferences"""
        
        # Get preferences
        preferences = await self.call_skill(
            "get_user_preferences",
            preference_type="all",
            context={"user_input": user_input}
        )
        
        # Validate
        validated = await self.call_skill(
            "validate_user_input",
            input_data=preferences,
            validation_rules={"required": ["destination", "dates"]}
        )
        
        if not validated["is_valid"]:
            return {"error": validated["errors"]}
        
        # Get suggestions
        suggestions = await self.call_skill(
            "suggest_destinations",
            budget=validated["normalized_data"]["budget"],
            interests=validated["normalized_data"]["interests"]
        )
        
        return {
            "preferences": validated["normalized_data"],
            "suggestions": suggestions
        }
```

## Data Flow

### End-to-End Travel Planning Flow
```
User Request
    ↓
InfoCollectionAgent
    → get_user_preferences
    → validate_user_input
    → suggest_destinations
    ↓
SearchAgent
    → search_flights (parallel)
    → search_hotels (parallel)
    → compare_search_results
    → filter_by_budget
    ↓
RecommendationAgent
    → get_destination_info (parallel)
    → get_attractions (parallel)
    → get_weather_forecast (parallel)
    → get_destination_reviews (parallel)
    ↓
BookingAgent
    → create_booking
    → process_payment
    → confirm_booking
    → get_booking_status
    ↓
Final Travel Plan
```

## Key Design Decisions

### 1. Independent Skills
**Decision**: Each skill is completely independent with no shared state
**Rationale**: Enables parallel execution, easier testing, and better scalability
**Trade-off**: Some duplication of validation logic across skills

### 2. Agent Type Property
**Decision**: Each skill declares which agent uses it via `agent_type`
**Rationale**: Makes ownership explicit and enables agent-based filtering
**Trade-off**: Skills are tightly coupled to agent architecture

### 3. JSON Schema Validation
**Decision**: Use JSON Schema for input/output validation
**Rationale**: Standard, well-documented, tool support
**Trade-off**: More verbose than simple type hints

### 4. Mock Data Implementation
**Decision**: Use mock data for demo, not real APIs
**Rationale**: Faster development, no API key dependencies, predictable testing
**Trade-off**: Need to replace with real APIs later

### 5. Singleton Registry
**Decision**: SkillRegistry is a singleton
**Rationale**: Global skill discovery, consistent state
**Trade-off**: Harder to test with multiple registries

### 6. Async Execution
**Decision**: All skills use async/await
**Rationale**: Supports concurrent execution, non-blocking I/O
**Trade-off**: More complex than synchronous code

## Error Handling

### Skill-Level Errors
```python
class SkillExecutionError(Exception):
    """Raised when skill execution fails"""
    pass

class SkillValidationError(Exception):
    """Raised when input validation fails"""
    pass

# In skill execute method
async def execute(self, **kwargs) -> Dict[str, Any]:
    try:
        validated = self.validate_input(**kwargs)
    except jsonschema.ValidationError as e:
        raise SkillValidationError(f"Invalid input: {e.message}")
    
    try:
        result = await self._do_work(validated)
        return result
    except Exception as e:
        raise SkillExecutionError(f"Skill execution failed: {str(e)}")
```

### Agent-Level Error Handling
```python
async def call_skill(self, skill_name: str, **kwargs) -> Dict[str, Any]:
    try:
        return await self.registry.execute_skill(skill_name, **kwargs)
    except SkillValidationError as e:
        logger.error(f"Validation error in {skill_name}: {e}")
        return {"error": "validation_error", "message": str(e)}
    except SkillExecutionError as e:
        logger.error(f"Execution error in {skill_name}: {e}")
        return {"error": "execution_error", "message": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in {skill_name}: {e}")
        return {"error": "internal_error", "message": "Skill execution failed"}
```

## Testing Strategy

### Unit Tests (Per Skill)
```python
# tests/test_skills/test_search_flights.py
import pytest
from src.mcp_server.skills.search import SearchFlightsSkill

@pytest.mark.asyncio
async def test_search_flights_valid_input():
    skill = SearchFlightsSkill()
    result = await skill.execute(
        origin="NYC",
        destination="LAX",
        departure_date="2025-06-01",
        passengers=2
    )
    
    assert "flights" in result
    assert len(result["flights"]) > 0
    assert result["flights"][0]["airline"]

@pytest.mark.asyncio
async def test_search_flights_invalid_input():
    skill = SearchFlightsSkill()
    
    with pytest.raises(SkillValidationError):
        await skill.execute(
            origin="NYC",
            # Missing required 'destination'
            departure_date="2025-06-01"
        )
```

### Integration Tests (Agent + Skills)
```python
# tests/test_agents/test_search_agent.py
import pytest
from src.agents.search import SearchAgent

@pytest.mark.asyncio
async def test_search_agent_workflow():
    agent = SearchAgent()
    
    # Search flights
    flights = await agent.call_skill(
        "search_flights",
        origin="NYC", destination="LAX",
        departure_date="2025-06-01", passengers=2
    )
    
    # Search hotels
    hotels = await agent.call_skill(
        "search_hotels",
        destination="LAX",
        check_in="2025-06-01", check_out="2025-06-05",
        guests=2
    )
    
    # Compare results
    comparison = await agent.call_skill(
        "compare_search_results",
        results_list=[flights, hotels],
        criteria={"price": 0.7, "rating": 0.3}
    )
    
    assert comparison["recommendation"]
```

## Performance Considerations

### Parallel Skill Execution
```python
# Execute multiple independent skills in parallel
async def gather_destination_insights(destination: str, dates: Dict):
    agent = RecommendationAgent()
    
    results = await asyncio.gather(
        agent.call_skill("get_destination_info", destination=destination),
        agent.call_skill("get_attractions", destination=destination),
        agent.call_skill("get_weather_forecast", destination=destination, dates=dates),
        agent.call_skill("get_destination_reviews", destination=destination)
    )
    
    return {
        "info": results[0],
        "attractions": results[1],
        "weather": results[2],
        "reviews": results[3]
    }
```

### Caching (Future Enhancement)
```python
# Add caching decorator for expensive skills
from functools import lru_cache

class GetDestinationInfoSkill(BaseSkill):
    @lru_cache(maxsize=100)
    def _get_cached_info(self, destination: str) -> Dict:
        # Expensive operation
        pass
    
    async def execute(self, destination: str, **kwargs) -> Dict:
        return self._get_cached_info(destination)
```

## Migration Path

### Phase 1: Coexistence
- New skills implemented alongside old skills
- Both structures functional
- No breaking changes

### Phase 2: Agent Migration
- Update agents to use new skills
- Keep old skills as fallback
- Gradual rollout

### Phase 3: Cleanup
- Remove old skill files
- Update all imports
- Clean documentation

## Security Considerations

### Input Validation
- All skills validate inputs against JSON Schema
- Prevent injection attacks through strict type checking
- Sanitize string inputs

### Rate Limiting (Future)
```python
from slowapi import Limiter

@app.post("/mcp/execute/{skill_name}")
@limiter.limit("100/minute")
async def execute_skill(request: Request, skill_name: str, params: Dict):
    # Rate limited execution
    pass
```

### Audit Logging (Future)
```python
async def execute_skill(self, name: str, **kwargs) -> Dict:
    logger.info(f"Executing skill: {name}", extra={
        "skill": name,
        "params": kwargs,
        "timestamp": datetime.now()
    })
    
    result = await self._execute(name, **kwargs)
    
    logger.info(f"Skill completed: {name}", extra={
        "skill": name,
        "duration_ms": ...,
        "success": True
    })
    
    return result
```

## Future Enhancements

1. **Skill Versioning**: Support multiple versions of skills
2. **Dynamic Loading**: Load skills from plugins
3. **Skill Composition**: Combine skills into workflows
4. **Real API Integration**: Replace mock data with real APIs
5. **Performance Monitoring**: Track skill execution metrics
6. **A/B Testing**: Test different skill implementations
7. **Skill Marketplace**: Third-party skill plugins
