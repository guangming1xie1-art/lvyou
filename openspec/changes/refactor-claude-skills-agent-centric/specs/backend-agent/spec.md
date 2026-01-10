# Spec Delta: Backend Agent Skills Architecture

> This document describes the changes to the Backend Agent specification for the Claude Skills refactor

## MODIFIED: Agent Responsibilities

### Previous: Core Capabilities Table
```markdown
| Capability | Description | Skills Used |
|------------|-------------|-------------|
| Travel Planning | Generate comprehensive travel itineraries | `create_travel_plan` |
| Destination Info | Provide destination details, tips, highlights | `search_destination` |
| Price查询 | Hotel and flight pricing information | `query_prices` |
| Reviews | User reviews and ratings for destinations | `get_destination_reviews` |
| Weather | Weather forecasts for travel dates | `get_weather` |
```

### New: Agent-Centric Capabilities
```markdown
| Agent | Capabilities | Skills |
|-------|--------------|--------|
| **InfoCollectionAgent** | Gather user preferences, validate input, suggest destinations | `get_user_preferences`, `validate_user_input`, `suggest_destinations` |
| **SearchAgent** | Find flights/hotels, compare results, filter by budget | `search_flights`, `search_hotels`, `compare_search_results`, `filter_by_budget` |
| **RecommendationAgent** | Destination insights, attractions, weather, reviews | `get_destination_info`, `get_attractions`, `get_weather_forecast`, `get_destination_reviews` |
| **BookingAgent** | Create bookings, process payments, confirmations, status tracking | `create_booking`, `process_payment`, `confirm_booking`, `get_booking_status` |
```

**Rationale**: Clear separation of responsibilities by agent type instead of by functionality

---

## ADDED: Skill Organization Structure

### Directory Structure
```
src/mcp_server/
├── base_skill.py          # BaseSkill abstract class
├── skill_registry.py      # SkillRegistry singleton
├── server.py              # MCP Server (dispatcher only)
└── skills/
    ├── __init__.py        # Exports + registration
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

**Total**: 15 independent skill modules

---

## ADDED REQUIREMENT: Skill Independence

### Specification
Each Skill SHALL be an independent module that:
- Inherits from `BaseSkill` abstract class
- Declares unique `name` and `agent_type`
- Defines `input_schema` as JSON Schema
- Defines `output_schema` as JSON Schema
- Implements async `execute(**kwargs)` method
- Implements input validation logic
- Handles errors gracefully
- Contains no shared state with other skills

#### Scenario: Skill Execution
```gherkin
GIVEN agent requests skill execution
WHEN agent calls skill with validated inputs
THEN skill executes independently
AND returns results matching output schema
AND handles errors without affecting other skills
```

#### Example: SearchFlightsSkill
```python
class SearchFlightsSkill(BaseSkill):
    name = "search_flights"
    agent_type = AgentType.SEARCH
    description = "Search for flight options"
    category = "search"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "destination": {"type": "string"},
                "departure_date": {"type": "string", "format": "date"},
                "passengers": {"type": "integer", "minimum": 1}
            },
            "required": ["origin", "destination", "departure_date", "passengers"]
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        validated = self.validate_input(**kwargs)
        flights = await self._search_flights(validated)
        return {"flights": flights, "total": len(flights)}
```

---

## ADDED REQUIREMENT: SkillRegistry

### Specification
The MCP Server SHALL maintain a SkillRegistry that:
- Implements singleton pattern for global access
- Loads all skills at application startup
- Provides skill discovery API by name, agent type, category
- Routes execution requests to appropriate skills
- Maintains skill metadata (schemas, descriptions)
- Validates skill registration (no duplicates)

#### Scenario: Skill Discovery
```gherkin
GIVEN agent needs to find available skills
WHEN agent queries registry by agent_type
THEN registry returns list of skills for that agent
AND each skill includes name, description, schemas
```

#### Scenario: Skill Execution via Registry
```gherkin
GIVEN registry has skill registered
WHEN agent executes skill by name with parameters
THEN registry validates skill exists
AND routes request to skill.execute()
AND returns result or error
```

#### API Methods
```python
class SkillRegistry:
    def register(self, skill: BaseSkill) -> None
    def get_skill(self, name: str) -> Optional[BaseSkill]
    def get_skills_by_agent(self, agent_type: AgentType) -> List[BaseSkill]
    def get_skills_by_category(self, category: str) -> List[BaseSkill]
    def get_all_skills(self) -> List[BaseSkill]
    def get_skill_definitions(self) -> List[Dict]
    async def execute_skill(self, name: str, **kwargs) -> Dict[str, Any]
```

---

## MODIFIED REQUIREMENT: MCP Server Responsibilities

### Previous: Mixed Registry + Business Logic
```python
# Old structure
SKILL_REGISTRY = {
    "search_destination": SearchDestinationSkill(),
    "query_prices": QueryPricesSkill(),
    # ... skills defined inline
}

@app.post("/mcp/execute/{skill_name}")
async def execute_skill(skill_name: str, params: Dict):
    skill = SKILL_REGISTRY.get(skill_name)
    return await skill.execute(**params)
```

### New: Pure Registry and Dispatcher
```python
# New structure
@app.on_event("startup")
async def startup_event():
    from . import skills  # Triggers skill registration
    registry = SkillRegistry()
    print(f"Registered {len(registry.get_all_skills())} skills")

@app.get("/mcp/skills")
async def list_skills(agent_type: Optional[str] = None):
    """List skills, optionally filtered by agent"""
    registry = SkillRegistry()
    if agent_type:
        skills = registry.get_skills_by_agent(AgentType(agent_type))
    else:
        skills = registry.get_all_skills()
    return {"skills": [s.to_definition() for s in skills], "total": len(skills)}

@app.post("/mcp/execute/{skill_name}")
async def execute_skill(skill_name: str, params: Dict):
    """Execute specific skill by name"""
    registry = SkillRegistry()
    try:
        result = await registry.execute_skill(skill_name, **params)
        return {"success": True, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**Changes:**
- MCP Server no longer contains skill business logic
- Acts as pure dispatcher to SkillRegistry
- Skills are loaded dynamically at startup
- Support for filtering skills by agent type

---

## ADDED: InfoCollectionAgent Skills

### GetUserPreferencesSkill
**Purpose**: Collect user travel preferences (destination, dates, budget, interests)

**Input Schema**:
```json
{
  "preference_type": "string (enum: all, destination, dates, budget, interests)",
  "context": "object (optional user input context)"
}
```

**Output Schema**:
```json
{
  "preferences": {
    "destination": "string",
    "dates": {"start": "date", "end": "date"},
    "budget": "number",
    "interests": ["string"]
  }
}
```

### ValidateUserInputSkill
**Purpose**: Validate and normalize user input data

**Input Schema**:
```json
{
  "input_data": "object",
  "validation_rules": "object"
}
```

**Output Schema**:
```json
{
  "is_valid": "boolean",
  "errors": ["string"],
  "normalized_data": "object"
}
```

### SuggestDestinationsSkill
**Purpose**: Suggest destinations based on user preferences

**Input Schema**:
```json
{
  "budget": "number",
  "interests": ["string"],
  "season": "string",
  "group_size": "integer"
}
```

**Output Schema**:
```json
{
  "suggestions": [
    {
      "destination": "string",
      "score": "number",
      "reasons": ["string"]
    }
  ]
}
```

---

## ADDED: SearchAgent Skills

### SearchFlightsSkill
**Purpose**: Search for flight options

**Input**: origin, destination, dates, passengers, cabin_class
**Output**: flights list with prices, airlines, durations

### SearchHotelsSkill
**Purpose**: Search for hotel options

**Input**: destination, check_in, check_out, guests, stars, amenities
**Output**: hotels list with prices, ratings, locations

### CompareSearchResultsSkill
**Purpose**: Compare and rank search results

**Input**: results_list, criteria (price weight, rating weight)
**Output**: comparison matrix, recommendation

### FilterByBudgetSkill
**Purpose**: Filter results by budget constraints

**Input**: results, budget, budget_type (total, per_person, per_night)
**Output**: filtered_results, budget_analysis

---

## ADDED: RecommendationAgent Skills

### GetDestinationInfoSkill
**Purpose**: Get destination information and facts

**Input**: destination, info_type (overview, details, tips)
**Output**: destination info (history, culture, language, currency)

### GetAttractionsSkill
**Purpose**: Get popular attractions and activities

**Input**: destination, attraction_type (landmarks, museums, nature), limit
**Output**: attractions list with descriptions, ratings

### GetWeatherForecastSkill
**Purpose**: Get weather forecast for travel dates

**Input**: destination, dates
**Output**: forecast by day (temperature, conditions, precipitation)

### GetDestinationReviewsSkill
**Purpose**: Get user reviews and ratings

**Input**: destination, review_type (general, attractions, food), limit
**Output**: reviews list with ratings, text, dates

---

## ADDED: BookingAgent Skills

### CreateBookingSkill
**Purpose**: Create initial booking for flights/hotels

**Input**: booking_type, booking_details, user_info
**Output**: booking_id, status, details

### ProcessPaymentSkill
**Purpose**: Process payment for booking

**Input**: booking_id, payment_method, amount
**Output**: payment_status, transaction_id

### ConfirmBookingSkill
**Purpose**: Confirm booking and send confirmation

**Input**: booking_id, confirmation_details
**Output**: confirmation_code, confirmation_email

### GetBookingStatusSkill
**Purpose**: Check booking status

**Input**: booking_id or confirmation_code
**Output**: status, details, timeline

---

## MODIFIED: Agent Integration Patterns

### Previous: Direct Skill Import
```python
from src.mcp_server.skills import SearchDestinationSkill

class RecommendationAgent:
    def __init__(self):
        self.destination_skill = SearchDestinationSkill()
    
    async def get_info(self, destination):
        return await self.destination_skill.execute(destination=destination)
```

### New: Registry-Based Access
```python
from src.mcp_server.skill_registry import SkillRegistry
from src.mcp_server.base_skill import AgentType

class RecommendationAgent:
    def __init__(self):
        self.registry = SkillRegistry()
        self.agent_type = AgentType.RECOMMENDATION
    
    async def call_skill(self, skill_name: str, **kwargs):
        return await self.registry.execute_skill(skill_name, **kwargs)
    
    def get_available_skills(self) -> List[BaseSkill]:
        return self.registry.get_skills_by_agent(self.agent_type)
    
    async def get_info(self, destination):
        return await self.call_skill("get_destination_info", 
                                    destination=destination)
```

---

## ADDED: MCP API Endpoints

### GET /mcp/skills
**Purpose**: List all available skills

**Query Parameters**:
- `agent_type` (optional): Filter by agent type

**Response**:
```json
{
  "skills": [
    {
      "name": "search_flights",
      "agent_type": "search",
      "description": "Search for flight options",
      "inputSchema": {...},
      "outputSchema": {...},
      "category": "search",
      "version": "1.0.0"
    }
  ],
  "total": 15
}
```

### POST /mcp/execute/{skill_name}
**Purpose**: Execute a specific skill

**Path Parameters**:
- `skill_name`: Skill to execute

**Body**:
```json
{
  "origin": "NYC",
  "destination": "LAX",
  "departure_date": "2025-06-01",
  "passengers": 2
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "flights": [...],
    "total": 5
  }
}
```

### POST /mcp/batch-execute
**Purpose**: Execute multiple skills in parallel

**Body**:
```json
{
  "requests": [
    {
      "skill_name": "search_flights",
      "params": {...}
    },
    {
      "skill_name": "search_hotels",
      "params": {...}
    }
  ]
}
```

**Response**:
```json
{
  "results": [
    {"success": true, "result": {...}},
    {"success": true, "result": {...}}
  ]
}
```

---

## REMOVED: Old Skill Files

The following files are REMOVED in this refactor:
- `src/mcp_server/skills/destination.py`
- `src/mcp_server/skills/pricing.py`
- `src/mcp_server/skills/reviews.py`
- `src/mcp_server/skills/weather.py`
- `src/mcp_server/skills/planning.py`

Their functionality is distributed across the new agent-centric skill modules.

---

## Migration Notes

### For Developers
1. **Update imports**: Change from direct skill imports to registry-based access
2. **Update agent classes**: Use `call_skill()` method instead of direct skill references
3. **Update tests**: Test skills individually via registry
4. **Review skill mapping**: Verify which agent uses which skill

### For API Consumers
- **No breaking changes** to MCP API endpoints
- Skill names have changed but can be aliased for backward compatibility
- API responses maintain same structure

### Backward Compatibility
Old skill names can be aliased in the registry:
```python
# Optional: Register aliases for old skill names
registry.register_alias("search_destination", "get_destination_info")
registry.register_alias("query_prices", "search_flights")  # Partial mapping
```

---

## Testing Requirements

### Unit Tests
Each skill MUST have unit tests covering:
- Valid input execution
- Invalid input validation
- Error handling
- Output schema compliance

### Integration Tests
Each agent MUST have integration tests covering:
- Calling multiple skills in sequence
- Error propagation from skills
- Complete workflow scenarios

### Example Test
```python
@pytest.mark.asyncio
async def test_search_flights_skill():
    skill = SearchFlightsSkill()
    result = await skill.execute(
        origin="NYC",
        destination="LAX",
        departure_date="2025-06-01",
        passengers=2
    )
    
    assert "flights" in result
    assert len(result["flights"]) > 0
    assert result["flights"][0]["price"] > 0
```

---

## Performance Considerations

### Parallel Execution
Skills are designed for parallel execution:
```python
results = await asyncio.gather(
    agent.call_skill("get_destination_info", destination="Tokyo"),
    agent.call_skill("get_attractions", destination="Tokyo"),
    agent.call_skill("get_weather_forecast", destination="Tokyo", dates={...}),
    agent.call_skill("get_destination_reviews", destination="Tokyo")
)
```

### Caching (Future)
Individual skills can implement caching without affecting others:
```python
class GetDestinationInfoSkill(BaseSkill):
    @lru_cache(maxsize=100)
    def _get_cached_info(self, destination: str):
        # Expensive operation
        pass
```

---

## Success Criteria

This refactor is complete when:
- [x] All 15 skills implemented and registered
- [x] SkillRegistry functional and tested
- [x] MCP Server refactored to use registry
- [x] All 4 agents updated to use new skills
- [x] Old skill files removed
- [x] All tests passing
- [x] Documentation updated
- [x] No breaking changes to MCP API

---

## Future Enhancements

This architecture enables:
1. **Skill Versioning**: Multiple versions of skills can coexist
2. **Dynamic Loading**: Skills can be loaded from plugins
3. **Third-Party Skills**: External skill packages
4. **Skill Marketplace**: Community-contributed skills
5. **Real API Integration**: Replace mock data with real APIs
6. **Performance Monitoring**: Track skill execution metrics
