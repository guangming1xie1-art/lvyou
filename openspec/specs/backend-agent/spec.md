# Backend Agent Specification

> OpenSpec specification for travel-assistant-agent (Python FastAPI + LangGraph + Claude)

## Overview

This document defines the technical specifications, patterns, and standards for the Python AI Agent service powered by FastAPI, LangGraph, and Claude.

## Agent Responsibilities

### Core Capabilities

| Capability | Description | Skills Used |
|------------|-------------|-------------|
| Travel Planning | Generate comprehensive travel itineraries | `create_travel_plan` |
| Destination Info | Provide destination details, tips, highlights | `search_destination` |
| Price查询 | Hotel and flight pricing information | `query_prices` |
| Reviews | User reviews and ratings for destinations | `get_destination_reviews` |
| Weather | Weather forecasts for travel dates | `get_weather` |
| Multi-tool Planning | Coordinated multi-skill travel planning | `create_travel_plan` (integrated) |

### Agent Types

| Agent | Responsibility | Input | Output |
|-------|----------------|-------|--------|
| InfoCollectionAgent | Extract user requirements | User message | Structured request |
| SearchAgent | Gather destination/price info | Request | Search results |
| RecommendationAgent | Generate personalized plans | Search results | Travel plans |
| BookingAgent | Handle booking requests | Plan selection | Booking status |
| SkillBasedAgent | Use MCP skills for planning | Parameters | Skill results + plan |

## LangGraph Workflow Patterns

### Workflow Architecture

```
User Input
    │
    ▼
┌─────────────────────┐
│ InfoCollectionAgent │  Extract destination, dates, budget, preferences
│     (StateGraph)    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    Router Node      │  Determine next step based on collected info
└─────────┬───────────┘
          │
          ├──▶ Missing Info ──▶ Request Clarification
          │
          ▼
┌─────────────────────┐
│    SearchAgent      │  Query destinations, prices, weather, reviews
│     (StateGraph)    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ RecommendationAgent │  Synthesize findings into travel plans
│     (StateGraph)    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│    BookingAgent     │  Optional: Process booking requests
│     (StateGraph)    │
└─────────┬───────────┘
          │
          ▼
       Output
```

### State Definition

```python
from typing import Optional
from pydantic import BaseModel
from enum import Enum
from datetime import date
from decimal import Decimal


class TravelRequestState(BaseModel):
    """Shared state for travel planning workflow."""
    
    # User input
    user_message: str
    user_id: Optional[str] = None
    
    # Extracted requirements
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    duration_days: Optional[int] = None
    preferences: list[str] = []
    accommodation_type: Optional[str] = None
    pace: str = "moderate"  # relaxed, moderate, intensive
    
    # Search results
    destination_info: Optional[dict] = None
    weather_info: Optional[dict] = None
    price_info: Optional[dict] = None
    reviews_info: Optional[list[dict]] = None
    
    # Generated plans
    travel_plan: Optional[dict] = None
    alternative_plans: list[dict] = []
    
    # Status
    current_step: str = "info_collection"
    status: str = "in_progress"  # in_progress, completed, failed
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### LangGraph Node Pattern

```python
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage


def info_collection_node(state: TravelRequestState) -> TravelRequestState:
    """Extract travel requirements from user message."""
    
    # Use Claude to extract structured information
    prompt = f"""
    Extract travel requirements from this message: "{state.user_message}"
    
    Return a JSON object with:
    - destination: where they want to go
    - start_date: when they want to start (ISO format)
    - end_date: when they want to return (ISO format)
    - budget: their budget in USD
    - duration_days: number of days
    - preferences: list of interests (culture, food, nature, etc.)
    - accommodation_type: hotel preference (budget, mid-range, luxury)
    """
    
    response = claude_client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    
    extracted = parse_json_response(response.content)
    
    return TravelRequestState(
        **state.model_dump(),
        destination=extracted.get("destination"),
        start_date=extracted.get("start_date"),
        end_date=extracted.get("end_date"),
        budget=extracted.get("budget"),
        duration_days=extracted.get("duration_days"),
        preferences=extracted.get("preferences", []),
        accommodation_type=extracted.get("accommodation_type"),
        current_step="search"
    )


def search_node(state: TravelRequestState) -> TravelRequestState:
    """Gather destination information from multiple sources."""
    import asyncio
    
    async def gather_info():
        tasks = [
            search_destination_skill.execute({"destination": state.destination}),
            get_weather_skill.execute({
                "destination": state.destination,
                "start_date": state.start_date.isoformat() if state.start_date else None
            }),
            query_prices_skill.execute({
                "destination": state.destination,
                "start_date": state.start_date.isoformat() if state.start_date else None,
                "duration_days": state.duration_days
            }),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    results = asyncio.run(gather_info())
    
    return TravelRequestState(
        **state.model_dump(),
        destination_info=results[0] if not isinstance(results[0], Exception) else None,
        weather_info=results[1] if not isinstance(results[1], Exception) else None,
        price_info=results[2] if not isinstance(results[2], Exception) else None,
        current_step="recommendation"
    )
```

### Workflow Builder

```python
def create_planning_workflow() -> StateGraph:
    """Create the travel planning LangGraph workflow."""
    
    workflow = StateGraph(TravelRequestState)
    
    # Add nodes
    workflow.add_node("info_collection", info_collection_node)
    workflow.add_node("search", search_node)
    workflow.add_node("recommendation", recommendation_node)
    workflow.add_node("booking", booking_node)
    
    # Define edges
    workflow.set_entry_point("info_collection")
    workflow.add_edge("info_collection", "search")
    workflow.add_edge("search", "recommendation")
    workflow.add_edge("recommendation", "booking")
    workflow.add_edge("booking", END)
    
    return workflow.compile()
```

## Claude Skills & MCP Integration

### MCP Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                          │
│                     (src/main.py)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌──────────────────┐         ┌──────────────────┐
    │ MCP Server       │         │ LangGraph        │
    │ (skills registry)│◄────────┤ (workflows)      │
    └────────┬─────────┘         └──────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌───────────┐  ┌───────────────┐
│ Skill A   │  │ Skill B       │
├───────────┤  ├───────────────┤
│ destination│  │ query_prices  │
│ search    │  │               │
└───────────┘  └───────────────┘
```

### Skill Definition Pattern

```python
from abc import ABC, abstractmethod
from typing import Any, Dict
import json


class BaseSkill(ABC):
    """Base class for all Claude Skills."""
    
    name: str = "base_skill"
    description: str = "Base skill"
    category: str = "general"
    version: str = "1.0.0"
    
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {}
    }
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the skill with given parameters."""
        pass
    
    def validate_input(self, parameters: Dict[str, Any]) -> bool:
        """Validate input parameters against schema."""
        required_fields = self.input_schema.get("required", [])
        for field in required_fields:
            if field not in parameters:
                raise ValueError(f"Missing required field: {field}")
        return True
```

### Skill Implementation Example

```python
from .base_skill import BaseSkill
from typing import Any, Dict
import time


class SearchDestinationSkill(BaseSkill):
    """Search for travel destination information."""
    
    name = "search_destination"
    description = "Search for travel destination information including attractions, best time to visit, cultural tips, and highlights"
    category = "destination"
    version = "1.0.0"
    
    input_schema = {
        "type": "object",
        "properties": {
            "destination": {
                "type": "string",
                "description": "The destination city or region to search for",
                "examples": ["Tokyo", "Paris", "Bali"]
            },
            "include_tips": {
                "type": "boolean",
                "description": "Include travel tips and local customs",
                "default": True
            },
            "language": {
                "type": "string",
                "description": "Response language",
                "default": "en"
            }
        },
        "required": ["destination"]
    }
    
    output_schema = {
        "type": "object",
        "properties": {
            "destination": {"type": "string"},
            "country": {"type": "string"},
            "highlights": {
                "type": "array",
                "items": {"type": "string"}
            },
            "best_time_to_visit": {"type": "string"},
            "local_customs": {"type": "array", "items": {"type": "string"}},
            "practical_info": {"type": "object"}
        }
    }
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        
        self.validate_input(parameters)
        
        destination = parameters["destination"]
        include_tips = parameters.get("include_tips", True)
        language = parameters.get("language", "en")
        
        # Use Claude to get destination information
        prompt = f"""
        Provide comprehensive travel information about {destination}.
        
        Include:
        - Country and basic info
        - Top 10 attractions and highlights
        - Best time to visit
        - Local customs and etiquette (if include_tips)
        - Practical travel tips
        
        Response in {language}.
        Format as JSON matching this structure:
        {{
            "destination": "...",
            "country": "...",
            "highlights": ["...", "..."],
            "best_time_to_visit": "...",
            "local_customs": ["...", "..."],
            "practical_info": {{
                "currency": "...",
                "language": "...",
                "time_zone": "...",
                "visa_requirements": "..."
            }}
        }}
        """
        
        response = await claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = parse_json_response(response.content)
        result["execution_time_ms"] = (time.time() - start_time) * 1000
        
        return result
```

### Skill Registry

```python
from typing import Dict, Type
from .base_skill import BaseSkill
from .destination import SearchDestinationSkill
from .pricing import QueryPricesSkill
from .reviews import GetDestinationReviewsSkill
from .weather import GetWeatherSkill
from .planning import CreateTravelPlanSkill


class SkillRegistry:
    """Registry of available MCP skills."""
    
    _skills: Dict[str, BaseSkill] = {}
    
    @classmethod
    def register(cls, skill: BaseSkill):
        cls._skills[skill.name] = skill
    
    @classmethod
    def get_skill(cls, name: str) -> BaseSkill:
        if name not in cls._skills:
            raise ValueError(f"Skill not found: {name}")
        return cls._skills[name]
    
    @classmethod
    def list_skills(cls) -> list[Dict]:
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "category": skill.category,
                "version": skill.version,
                "input_schema": skill.input_schema,
                "output_schema": skill.output_schema
            }
            for skill in cls._skills.values()
        ]
    
    @classmethod
    async def execute_skill(cls, name: str, parameters: Dict) -> Dict:
        skill = cls.get_skill(name)
        return await skill.execute(parameters)


# Register all skills
SkillRegistry.register(SearchDestinationSkill())
SkillRegistry.register(QueryPricesSkill())
SkillRegistry.register(GetDestinationReviewsSkill())
SkillRegistry.register(GetWeatherSkill())
SkillRegistry.register(CreateTravelPlanSkill())
```

## Tool/Skill Input-Output Contracts

### Input Schema Standards

```python
# All skills must define JSON Schema compatible input
input_schema = {
    "type": "object",
    "properties": {
        "destination": {
            "type": "string",
            "description": "Clear description",
            "examples": ["Tokyo", "Paris"]
        },
        "date": {
            "type": "string",
            "format": "date",
            "description": "ISO 8601 date format"
        },
        "amount": {
            "type": "number",
            "description": "Numeric value with units"
        },
        "options": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of options"
        }
    },
    "required": ["destination"],
    "additionalProperties": False
}
```

### Output Schema Standards

```python
# All skills must define JSON Schema compatible output
output_schema = {
    "type": "object",
    "properties": {
        "success": {
            "type": "boolean",
            "description": "Whether the operation succeeded"
        },
        "data": {
            "type": "object",
            "description": "Result data"
        },
        "error": {
            "type": "object",
            "description": "Error details if failed",
            "properties": {
                "code": {"type": "string"},
                "message": {"type": "string"}
            }
        },
        "execution_time_ms": {
            "type": "number",
            "description": "Execution time in milliseconds"
        }
    },
    "required": ["success", "execution_time_ms"]
}
```

## State Management in Workflows

### Workflow State Persistence

```python
from datetime import datetime
from typing import Optional
from enum import Enum


class WorkflowState(Enum):
    """Possible states for a workflow execution."""
    CREATED = "created"
    RUNNING = "running"
    WAITING = "waiting"  # Waiting for user input
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowExecution:
    """Tracks a single workflow execution."""
    
    def __init__(self, workflow_id: str, user_id: str, initial_state: TravelRequestState):
        self.execution_id = str(uuid.uuid4())
        self.workflow_id = workflow_id
        self.user_id = user_id
        self.state = initial_state
        self.status = WorkflowState.CREATED
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        self.history: list[dict] = []
    
    def update_state(self, new_state: TravelRequestState):
        """Update workflow state and track changes."""
        self.state = new_state
        self.updated_at = datetime.utcnow()
        self.history.append({
            "timestamp": self.updated_at.isoformat(),
            "step": new_state.current_step,
            "status": new_state.status
        })
    
    def mark_running(self):
        """Mark workflow as running."""
        self.status = WorkflowState.RUNNING
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self):
        """Mark workflow as completed."""
        self.status = WorkflowState.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self, error: str):
        """Mark workflow as failed."""
        self.status = WorkflowState.FAILED
        self.state.error_message = error
        self.updated_at = datetime.utcnow()
```

## Error Handling & Fallback Strategies

### Error Classification

```python
class AgentError(Exception):
    """Base exception for agent errors."""
    def __init__(self, message: str, code: str, recoverable: bool = False):
        super().__init__(message)
        self.message = message
        self.code = code
        self.recoverable = recoverable


class LLMError(AgentError):
    """Error from LLM API."""
    def __init__(self, message: str):
        super().__init__(message, "LLM_ERROR", recoverable=True)


class SkillExecutionError(AgentError):
    """Error executing a skill."""
    def __init__(self, skill_name: str, message: str):
        super().__init__(f"Skill '{skill_name}' failed: {message}", 
                         "SKILL_ERROR", recoverable=True)


class ValidationError(AgentError):
    """Input validation error."""
    def __init__(self, message: str, field: str = None):
        code = "VALIDATION_ERROR"
        super().__init__(message, code, recoverable=False)
        self.field = field


class RateLimitError(AgentError):
    """Rate limit exceeded."""
    def __init__(self, retry_after: int = 60):
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s",
                         "RATE_LIMIT", recoverable=True)
        self.retry_after = retry_after
```

### Error Handler

```python
from contextlib import asynccontextmanager
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(AgentError)
async def agent_error_handler(request: Request, exc: AgentError):
    """Handle agent errors consistently."""
    logger.error(f"Agent error: {exc.code} - {exc.message}")
    
    return JSONResponse(
        status_code=429 if exc.code == "RATE_LIMIT" else 400,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "recoverable": exc.recoverable
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.exception(f"Unexpected error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "recoverable": False
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### Retry Strategy

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class ClaudeClient:
    """Claude API client with retry logic."""
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((RateLimitError, LLMError))
    )
    async def messages_create(self, **kwargs) -> Any:
        """Create a message with retry on rate limit."""
        try:
            return await self._client.messages.create(**kwargs)
        except RateLimitError as e:
            logger.warning(f"Rate limited, retrying in {e.retry_after}s")
            raise
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise LLMError(str(e))
```

## Integration with Java Backend API

### API Client Configuration

```python
from httpx import AsyncClient, Timeout
from typing import Optional


class JavaBackendClient:
    """Client for communicating with Java Spring Cloud backend."""
    
    def __init__(self, base_url: str = "http://localhost:8080/api/v1"):
        self.base_url = base_url
        self.client = AsyncClient(
            timeout=Timeout(30.0),
            follow_redirects=True
        )
    
    async def get_travel_request(self, request_id: str) -> dict:
        """Get travel request details from Java backend."""
        response = await self.client.get(
            f"{self.base_url}/travel-requests/{request_id}"
        )
        response.raise_for_status()
        return response.json()["data"]
    
    async def create_plan(self, plan_data: dict) -> dict:
        """Create a new travel plan."""
        response = await self.client.post(
            f"{self.base_url}/plans",
            json=plan_data
        )
        response.raise_for_status()
        return response.json()["data"]
    
    async def update_request_status(self, request_id: str, status: str) -> dict:
        """Update travel request status."""
        response = await self.client.patch(
            f"{self.base_url}/travel-requests/{request_id}/status",
            json={"status": status}
        )
        response.raise_for_status()
        return response.json()["data"]
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
```

### API Contract

```python
# API contracts for agent -> Java backend communication

class TravelPlanSubmission(BaseModel):
    """Data structure for submitting a travel plan to Java backend."""
    
    travel_request_id: str
    title: str
    overview: str
    itinerary: list[DayPlan]
    budget_breakdown: BudgetBreakdown
    packing_list: list[str]
    tips: list[str]
    agent_execution_time_ms: float
    
    class DayPlan(BaseModel):
        day: int
        date: str
        morning: list[Activity]
        afternoon: list[Activity]
        evening: list[Activity]
    
    class Activity(BaseModel):
        time: str
        description: str
        location: str
        duration_hours: float
        cost: Optional[float] = None
        notes: Optional[str] = None
    
    class BudgetBreakdown(BaseModel):
        total_budget: float
        accommodation: float
        transportation: float
        food: float
        activities: float
        misc: float
        currency: str = "USD"
```

## Logging & Observability Requirements

### Structured Logging

```python
from loguru import logger
import sys
import json
from datetime import datetime


# Configure structured JSON logging for production
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
    level="INFO",
    serialize=True  # JSON output
)


class AgentLogger:
    """Structured logger for agent operations."""
    
    @staticmethod
    def log_skill_execution(
        skill_name: str,
        parameters: dict,
        result: dict,
        duration_ms: float
    ):
        """Log skill execution with structured data."""
        logger.info(
            "Skill executed",
            extra={
                "event_type": "skill_execution",
                "skill_name": skill_name,
                "duration_ms": duration_ms,
                "success": result.get("success", True),
                "input_size": len(json.dumps(parameters))
            }
        )
    
    @staticmethod
    def log_workflow_step(
        workflow_id: str,
        step: str,
        status: str,
        duration_ms: float = None
    ):
        """Log workflow step transitions."""
        logger.info(
            "Workflow step",
            extra={
                "event_type": "workflow_step",
                "workflow_id": workflow_id,
                "step": step,
                "status": status,
                "duration_ms": duration_ms
            }
        )
    
    @staticmethod
    def log_error(
        error_type: str,
        message: str,
        context: dict = None
    ):
        """Log errors with context."""
        logger.error(
            message,
            extra={
                "event_type": "error",
                "error_type": error_type,
                "message": message,
                "context": context or {}
            }
        )
```

### Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Prometheus metrics
SKILL_EXECUTIONS = Counter(
    'skill_executions_total',
    'Total number of skill executions',
    ['skill_name', 'status']
)

SKILL_DURATION = Histogram(
    'skill_execution_duration_seconds',
    'Skill execution duration',
    ['skill_name'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

WORKFLOW_IN_PROGRESS = Gauge(
    'workflows_in_progress',
    'Number of workflows currently running',
    ['workflow_type']
)

LLM_REQUESTS = Counter(
    'llm_requests_total',
    'Total LLM API requests',
    ['model', 'status']
)

LLM_DURATION = Histogram(
    'llm_request_duration_seconds',
    'LLM API request duration',
    ['model'],
    buckets=[1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
)
```

## Performance Requirements

### Response Time Targets

| Operation | P95 Target | P99 Target |
|-----------|-----------|-----------|
| Skill Execution (cached) | < 100ms | < 200ms |
| Skill Execution (LLM call) | < 5s | < 10s |
| Travel Plan Generation | < 30s | < 60s |
| Health Check | < 50ms | < 100ms |
| Skills List API | < 20ms | < 50ms |

### Concurrency Requirements

- **Max concurrent requests**: 100 per instance
- **Max concurrent LLM calls**: 10 per request
- **Request timeout**: 60s (configurable)
- **Queue timeout**: 30s

### Resource Limits

```yaml
# docker-compose.yml resource limits
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

*This specification is managed by OpenSpec. Refer to project.md for cross-project conventions.*
