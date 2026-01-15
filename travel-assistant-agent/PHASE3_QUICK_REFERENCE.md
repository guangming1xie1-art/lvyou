# Phase 3 Quick Reference Guide

## Quick Start

### 1. Verify Implementation
```bash
cd travel-assistant-agent
python verify_phase3_syntax.py
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Server
```bash
cd travel-assistant-agent
python src/main.py
```

### 4. Access API Documentation
```
http://localhost:8000/docs
```

---

## MCP V2 (Phase 3.1)

### Import and Use
```python
from src.mcp import MCPServerV2, MCPProtocolHandler, MCPToolFactory
from src.mcp.resources import create_default_resources

# Create server
handler = MCPProtocolHandler()
resource_manager = create_default_resources()
server = MCPServerV2(handler, resource_manager)

# Register tools
for tool in MCPToolFactory.get_all_tools():
    handler.register_tool(tool)

# Get FastAPI router
router = server.create_router()
app.include_router(router)
```

### Available Tools
- `search_flights`
- `search_hotels`
- `get_recommendations`
- `get_destination_info`
- `book_flight`
- `book_hotel`
- `get_weather`
- `get_reviews`

### Endpoints
```
GET    /mcp-v2/status
GET    /mcp/tools
POST   /mcp/tools/call
GET    /mcp/resources
WS      /ws/mcp-v2
```

---

## Agent Skills Framework (Phase 3.2)

### Create a Custom Skill
```python
from src.skills import Skill

class MyCustomSkill(Skill):
    def __init__(self):
        super().__init__(
            name="my_custom_skill",
            description="My custom skill",
            version="1.0.0",
            enabled=True,
            cost_estimate=0.001,
            category="custom"
        )
    
    async def execute(self, input_data):
        # Your skill logic here
        return {"result": "success"}
    
    def get_required_fields(self):
        return ["required_field"]

# Register skill
from src.skills import get_skill_registry
registry = get_skill_registry()
registry.register(MyCustomSkill())
```

### Use Skills
```python
from src.skills import get_skill_registry

registry = get_skill_registry()

# List skills
all_skills = registry.list_all()
search_skills = registry.list_by_category("search")

# Execute skill
result = await registry.execute(
    "search_flight",
    {"destination": "Tokyo", "departure_date": "2024-03-01"}
)

# Parallel execution
results = await registry.execute_parallel([
    {"name": "search_flight", "input": {...}},
    {"name": "search_hotel", "input": {...}}
])

# Sequential execution
results = await registry.execute_sequence([
    {"name": "search_flight", "input": {...}},
    {"name": "book_flight", "input": {...}}
])
```

### Built-in Skills

#### Search Category
- `search_destination`
- `search_flight`
- `search_hotel`

#### Recommendation Category
- `recommend_flight`
- `recommend_hotel`
- `recommend_destination`

#### Booking Category
- `book_flight`
- `book_hotel`
- `get_booking_status`
- `cancel_booking`

### Endpoints
```
GET    /skills/list?category=X
GET    /skills/{skill_name}
POST   /skills/execute
POST   /skills/batch-execute
GET    /skills/categories
POST   /skills/{skill_name}/enable
POST   /skills/{skill_name}/disable
GET    /skills/statistics
```

---

## Concurrency (Phase 3.3)

### Connection Pool
```python
from src.concurrency import APIConnectionPool

pool = APIConnectionPool(
    max_connections=100,
    timeout=10.0,
    max_retries=3
)

# Use context manager
async with pool:
    await pool.make_request(my_api_function, arg1, arg2)

# Get statistics
stats = pool.get_stats()
print(f"Utilization: {stats['utilization']:.2%}")
```

### Memory Pool
```python
from src.concurrency import MemoryPool

pool = MemoryPool(max_size=100, item_size_limit=10*1024*1024)

# Allocate
await pool.allocate("key1", 1024)

# Free
await pool.free("key1")

# Get statistics
stats = pool.get_stats()
print(f"Current: {stats['current']}, Utilization: {stats['utilization']:.2%}")
```

### Rate Limiter
```python
from src.concurrency import RateLimiter

limiter = RateLimiter(rate=100, burst=200)

# Wait if needed
await limiter.wait_if_needed(tokens=1)

# Non-blocking check
if await limiter.acquire(tokens=1):
    # Proceed with request
    pass

# Get statistics
stats = limiter.get_stats()
print(f"Allow rate: {stats['allow_rate']:.2%}")
```

### Streaming
```python
from src.concurrency import StreamingManager

async def items_generator():
    for i in range(100):
        yield {"id": i}

# JSON array streaming
response = await StreamingManager.stream_json_array(items_generator())

# Server-Sent Events
response = await StreamingManager.stream_server_sent_events(items_generator())

# NDJSON streaming
response = await StreamingManager.stream_ndjson(items_generator())
```

### Endpoints
```
GET    /concurrency/stats
GET    /concurrency/pool-stats
GET    /concurrency/rate-limit-stats
```

---

## Configuration

### MCP V2
```bash
MCP_V2_ENABLED=true
MCP_V2_MAX_WEBSOCKETS=100
MCP_V2_REQUEST_TIMEOUT=30.0
```

### Skills
```bash
SKILLS_ENABLED=true
SKILLS_AUTO_LOAD=true
SKILLS_MAX_EXECUTION_TIME=30.0
SKILLS_PARALLEL_ENABLED=true
```

### Concurrency
```bash
CONNECTION_POOL_MAX_CONNECTIONS=100
RATE_LIMITING_ENABLED=true
RATE_LIMIT_DEFAULT_RATE=1000.0
STREAMING_ENABLED=true
```

---

## Common Patterns

### Pattern 1: Execute Multiple Skills
```python
from src.skills import get_skill_registry

registry = get_skill_registry()

# Parallel (when no dependencies)
results = await registry.execute_parallel([
    {"name": "search_flight", "input": {...}},
    {"name": "search_hotel", "input": {...}}
])

# Sequential (when dependencies exist)
results = await registry.execute_sequence([
    {"name": "search_flight", "input": {...}},
    {"name": "book_flight", "input": {...}}
])
```

### Pattern 2: Rate-Limited API Calls
```python
from src.concurrency import APIConnectionPool, RateLimiter

pool = APIConnectionPool(max_connections=100)
limiter = RateLimiter(rate=1000, burst=2000)

async with pool:
    await limiter.wait_if_needed()
    result = await pool.make_request(api_function)
```

### Pattern 3: Streaming Large Results
```python
from src.concurrency import StreamingManager
from fastapi import FastAPI

app = FastAPI()

@app.get("/stream-results")
async def stream_large_dataset():
    async def generator():
        async for item in get_large_dataset():
            yield item
    
    return await StreamingManager.stream_json_array(generator())
```

### Pattern 4: Custom Skill with Cost Tracking
```python
from src.skills import Skill

class ExpensiveSkill(Skill):
    def __init__(self):
        super().__init__(
            name="expensive_operation",
            description="High-cost operation",
            cost_estimate=0.10  # $0.10 per execution
        )
    
    async def execute(self, input_data):
        # Do expensive work
        result = await expensive_api_call()
        
        # Track actual cost if different from estimate
        actual_cost = calculate_cost(result)
        await self.on_success(0.0, actual_cost)
        
        return result

# Check total cost
skill = ExpensiveSkill()
# ... execute multiple times ...
stats = skill.get_metadata()
print(f"Total spent: ${skill.total_cost:.2f}")
```

---

## Troubleshooting

### Issue: Skill Not Found
```
Error: Unknown skill: my_skill
```
**Solution**: Ensure skill is registered:
```python
from src.skills import get_skill_registry
registry = get_skill_registry()
registry.register(MySkill())
```

### Issue: Rate Limiting
```
Error: Request denied by rate limiter
```
**Solution**: Adjust rate limits or use rate limiter:
```bash
# Increase rate in .env
RATE_LIMIT_DEFAULT_RATE=2000.0

# Or wait before retrying
await limiter.wait_if_needed()
```

### Issue: Connection Pool Exhausted
```
Error: Connection acquisition timeout
```
**Solution**: Increase pool size or check for leaks:
```bash
CONNECTION_POOL_MAX_CONNECTIONS=200

# Check for connection leaks
stats = pool.get_stats()
print(f"Active: {stats['active']}, Rejected: {stats['rejected']}")
```

---

## Performance Tips

1. **Use Parallel Execution**: When skills are independent
   ```python
   results = await registry.execute_parallel(calls)
   ```

2. **Reuse Connections**: Connection pooling reduces overhead
   ```python
   async with pool:
       await pool.make_request(...)
   ```

3. **Stream Large Responses**: Reduce memory footprint
   ```python
   return await StreamingManager.stream_json_array(generator())
   ```

4. **Track Costs**: Monitor skill execution costs
   ```python
   stats = skill.get_metadata()
   print(f"Total cost: ${stats['total_cost']}")
   ```

5. **Use Rate Limiting**: Prevent API overuse
   ```python
   await limiter.wait_if_needed()
   ```

---

## Further Reading

- [Phase 3 Advanced Features Documentation](./PHASE3_ADVANCED_FEATURES.md)
- [Phase 3 Implementation Summary](./PHASE3_IMPLEMENTATION_SUMMARY.md)
- [API Documentation](http://localhost:8000/docs)
- [Configuration Reference](./.env.example)

---

## Version History

- **1.0.0** (2024): Initial implementation of Phase 3
  - MCP Integration (Phase 3.1)
  - Agent Skills Framework (Phase 3.2)
  - High Concurrency Optimization (Phase 3.3)
