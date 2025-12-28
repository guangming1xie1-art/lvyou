# Integration Specification

> OpenSpec specification for API contracts and data flow between services

## Overview

This document defines the API contracts, data flow patterns, and integration standards between the three sub-projects:
- `travel-assistant-front` (React Frontend)
- `travel-assistant` (Java Spring Cloud Backend)
- `travel-assistant-agent` (Python FastAPI Agent)

## Service Communication Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           User Browser                                  │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────────────────┐
│  travel-assistant-front (Port 3000)                                     │
│  - User Interface                                                        │
│  - Form Input                                                            │
│  - Plan Display                                                          │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ HTTP/REST
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  travel-assistant (Spring Cloud Gateway - Port 8080)                    │
│  - Request Routing                                                       │
│  - Authentication/Authorization                                          │
│  - Rate Limiting                                                         │
│  - Request/Response Transformation                                       │
└──────┬────────────────────┬────────────────────┬────────────────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────────────┐
│ auth-service│    │ travel-request  │    │ travel-plan-service     │
│  Port 8081  │    │  Port 8082      │    │  Port 8083              │
│ JWT Token   │    │  Request Mgmt   │    │  Plan Generation        │
│ Generation  │    │                 │    │  - Calls Agent Service  │
└─────────────┘    └─────────────────┘    └─────────────────────────┘
       │                    │                    │
       │                    │                    │
       │                    │         HTTP/REST (Internal)
       │                    │                    │
       │                    │                    ▼
       │                    │    ┌─────────────────────────────┐
       │                    │    │ travel-assistant-agent      │
       │                    │    │ Port 8000                   │
       │                    │    │ - Claude AI Integration     │
       │                    │    │ - MCP Skills                │
       │                    │    │ - Travel Planning           │
       │                    │    └─────────────────────────────┘
       │                    │
       └────────────────────┴──────────────────────────────────┐
                                                              │
                                               PostgreSQL DB   │
                                               (Port 5432)     │
```

## API Contracts: Frontend → Java Backend

### Base URL Configuration

```typescript
// Frontend environment configuration
// .env
VITE_API_BASE_URL=http://localhost:8080/api/v1
```

### API Endpoints

#### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Login and get JWT token |
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/logout` | Logout (invalidate token) |
| GET | `/api/v1/auth/me` | Get current user profile |

##### Login Request/Response

```typescript
// Request
interface LoginRequest {
  email: string;
  password: string;
}

// Response
interface LoginResponse {
  code: number;
  message: string;
  data: {
    token: string;
    tokenType: "Bearer";
    expiresIn: number; // seconds
    user: UserProfile;
  };
  timestamp: string;
}

interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}
```

#### Travel Requests

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/travel-requests` | Create travel request |
| GET | `/api/v1/travel-requests` | List user's travel requests |
| GET | `/api/v1/travel-requests/:id` | Get travel request details |
| PUT | `/api/v1/travel-requests/:id` | Update travel request |
| DELETE | `/api/v1/travel-requests/:id` | Delete travel request |

##### Create Travel Request

```typescript
// Request
interface CreateTravelRequest {
  destination: string;
  startDate: string; // ISO 8601 date
  endDate: string;   // ISO 8601 date
  budget: number;
  preferences?: string[];
  durationDays?: number;
  accommodationType?: "budget" | "mid-range" | "luxury";
  interests?: string[];
  notes?: string;
}

// Response
interface TravelRequest {
  id: string;
  userId: string;
  destination: string;
  startDate: string;
  endDate: string;
  budget: number;
  status: "pending" | "processing" | "completed" | "cancelled";
  preferences?: string;
  durationDays?: number;
  accommodationType?: string;
  interests?: string;
  createdAt: string;
  updatedAt: string;
}
```

#### Travel Plans

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/travel-requests/:requestId/plans` | Get plans for a request |
| GET | `/api/v1/plans/:id` | Get plan details |
| POST | `/api/v1/plans` | Create plan (via Agent) |
| PUT | `/api/v1/plans/:id` | Update plan |
| POST | `/api/v1/plans/:id/book` | Book a plan |

##### Travel Plan Response

```typescript
interface TravelPlan {
  id: string;
  travelRequestId: string;
  title: string;
  overview: string;
  itinerary: DayPlan[];
  budgetBreakdown: BudgetBreakdown;
  packingList: string[];
  tips: string[];
  status: "generated" | "reviewed" | "selected" | "booked" | "cancelled";
  agentExecutionTimeMs: number;
  createdAt: string;
  updatedAt: string;
}

interface DayPlan {
  day: number;
  date: string;
  morning: Activity[];
  afternoon: Activity[];
  evening: Activity[];
}

interface Activity {
  time: string;
  description: string;
  location: string;
  durationHours: number;
  cost?: number;
  notes?: string;
}

interface BudgetBreakdown {
  total: number;
  accommodation: number;
  transportation: number;
  food: number;
  activities: number;
  misc: number;
  currency: string;
}
```

#### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/orders` | Create order |
| GET | `/api/v1/orders/:id` | Get order details |
| GET | `/api/v1/orders` | List user's orders |
| PUT | `/api/v1/orders/:id/status` | Update order status |

## API Contracts: Java Backend → Python Agent

### Base URL Configuration

```yaml
# travel-assistant/travel-plan-service/application.yml
agent:
  base-url: http://localhost:8000
  timeout: 60s
```

### API Endpoints

| Method | Agent Endpoint | Description |
|--------|----------------|-------------|
| POST | `/agent/generate-plan` | Generate travel plan |
| POST | `/agent/demo-planning-with-skills` | Plan with MCP skills |
| GET | `/mcp/skills` | List available skills |
| POST | `/mcp/call-skill` | Call specific skill |
| GET | `/health` | Health check |

#### Generate Plan

```java
// Java DTOs
@Data
public class AgentPlanRequest {
    private String destination;
    private LocalDate startDate;
    private LocalDate endDate;
    private BigDecimal budget;
    private List<String> preferences;
    private Integer durationDays;
    private String accommodationType;
    private String pace; // relaxed, moderate, intensive
}

@Data
public class AgentPlanResponse {
    private String requestId;
    private String destination;
    private List<String> skillsUsed;
    private Map<String, Object> skillResults;
    private AgentTravelPlan travelPlan;
    private Long executionTimeMs;
}

@Data
public class AgentTravelPlan {
    private String title;
    private String overview;
    private List<AgentDayPlan> itinerary;
    private AgentBudgetBreakdown budgetBreakdown;
    private List<String> packingList;
    private List<String> tips;
}
```

#### Call Skill

```java
// Java DTOs for skill invocation
@Data
public class SkillCallRequest {
    private String skillName;
    private Map<String, Object> parameters;
}

@Data
public class SkillCallResponse {
    private boolean success;
    private String skillName;
    private Map<String, Object> result;
    private Double executionTimeMs;
}
```

## Data Flow Standards

### Travel Planning Flow

```
1. User submits requirements
   Frontend → POST /api/v1/travel-requests
   ← TravelRequest with ID

2. Request plans
   Frontend → POST /api/v1/plans
   (Triggers Agent call internally)
   ← TravelPlan with itinerary

3. Review plans
   Frontend → GET /api/v1/travel-requests/{id}/plans
   ← List<TravelPlan>

4. Select plan
   Frontend → POST /api/v1/plans/{id}/book
   ← Order confirmation

5. Create order
   Frontend → POST /api/v1/orders
   ← Order confirmation
```

### Asynchronous Flow (Future Enhancement)

For longer-running AI operations:

```
1. User submits request
   Frontend → POST /api/v1/plans (async)
   ← PlanRequest with status "processing"

2. Poll for completion
   Frontend → GET /api/v1/plans/{id}
   ← Plan with status "completed" or "failed"

3. WebSocket notification (optional)
   Backend → Frontend (status update)
```

## Error Propagation & Handling

### Error Flow Across Services

```
Frontend Request
       │
       ▼
┌──────────────────┐
│ Java Gateway     │  → 400 (Validation), 401 (Auth), 429 (Rate limit)
└────────┬─────────┘
         │ (valid request)
         ▼
┌──────────────────┐
│ Java Service     │  → 404 (Not found), 500 (Service error)
└────────┬─────────┘
         │ (needs AI processing)
         ▼
┌──────────────────┐
│ Agent Service    │  → Agent-specific errors
│                  │  → LLM timeout/failure
└────────┬─────────┘
         │ (success)
         ▼
Java returns plan to Frontend
```

### Error Response Format (Cross-Service)

```json
{
  "code": 60001,
  "message": "Failed to generate travel plan",
  "data": null,
  "timestamp": "2025-01-01T00:00:00Z",
  "details": {
    "service": "agent",
    "error_type": "LLM_ERROR",
    "retryable": true,
    "suggestion": "Please try again in a few moments"
  }
}
```

### Error Codes for Integration

| Code | Service | Description | Retryable |
|------|---------|-------------|-----------|
| 60001 | Agent | LLM API failure | Yes |
| 60002 | Agent | Skill execution error | Yes |
| 60003 | Agent | Invalid parameters | No |
| 60004 | Agent | Timeout | Yes |
| 60101 | Integration | Service unavailable | Yes |
| 60102 | Integration | Request timeout | Yes |
| 60103 | Integration | Invalid response format | No |

## Request/Response Timeout Expectations

### Timeouts by Operation

| Operation | Expected Max Time | Timeout Config |
|-----------|-------------------|----------------|
| Login | < 500ms | 5s |
| CRUD operations | < 500ms | 10s |
| Health check | < 100ms | 5s |
| Plan generation | < 30s | 60s |
| Skill call | < 10s | 15s |
| Batch skills | < 30s | 45s |

### Timeout Configuration

```yaml
# Java Backend
spring:
  cloud:
    gateway:
      httpclient:
        connect-timeout: 5000
        response-timeout: 60s

# Agent Service
uvicorn:
  timeout_keep_alive: 30
```

## Rate Limiting & Throttling

### Rate Limits by Client

| Client Type | Requests/minute | Burst | Notes |
|-------------|-----------------|-------|-------|
| Frontend (Web) | 60 | 10 | Per user |
| Frontend (API) | 300 | 50 | Per IP |
| Internal (Java→Agent) | 120 | 20 | Service-to-service |

### Rate Limit Response

```json
{
  "code": 42901,
  "message": "Rate limit exceeded",
  "data": {
    "retryAfter": 30,
    "limit": 60,
    "remaining": 0
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Implementation

```java
// Java Gateway Rate Limiting
@Component
public class RateLimitFilter implements GatewayFilter {
    
    @Autowired
    private RedisTemplate<String, String> redisTemplate;
    
    private static final String RATE_LIMIT_PREFIX = "ratelimit:";
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String key = RATE_LIMIT_PREFIX + getClientId(exchange);
        String[] limits = {"60", "10"}; // per minute, burst
        
        return executeRateLimit(key, limits)
            .flatMap(allowed -> {
                if (!allowed) {
                    exchange.getResponse().setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
                    return exchange.getResponse().setComplete();
                }
                return chain.filter(exchange);
            });
    }
}
```

## Version Compatibility & Deprecation

### API Versioning Strategy

```
/api/v1/{resource}      # Current stable version
/api/v2/{resource}      # Next version (when breaking changes)
```

### Version Lifecycle

| Stage | Duration | Description |
|-------|----------|-------------|
| Active | - | Fully supported, latest features |
| Deprecated | 6 months | Supported but flagged for removal |
| Sunset | 3 months | Warning responses, no new features |
| Removed | - | Endpoint no longer available |

### Deprecation Header

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 01 Jan 2026 00:00:00 GMT
Link: </api/v2/plans>; rel="successor-version"
```

### Breaking Change Definition

A breaking change requires version bump:
- Removing or renaming fields in request/response
- Changing field types
- Adding required fields
- Changing HTTP status codes for existing behavior
- Removing endpoints

### Non-Breaking Changes (Backward Compatible)

- Adding optional fields
- Adding new endpoints
- Adding new enum values
- Changing field descriptions/documentation

## Data Transformation Standards

### Field Mapping

| Source (Agent) | Target (Java) | Transformation |
|---------------|---------------|----------------|
| `execution_time_ms` | `agentExecutionTimeMs` | Direct (ms → ms) |
| `budget_breakdown.total` | `budgetBreakdown.total` | Direct |
| `itinerary[].activities` | `itinerary[].morning/afternoon/evening` | Array split |
| `tips` | `tips` | Direct |

### Null Handling

- Frontend should handle null fields gracefully
- Agent should not return null for required fields (use empty array instead)
- Java should use Optional for nullable fields

### Date/Time Format

```typescript
// All timestamps: ISO 8601 with timezone
// Examples:
"2025-01-15T10:30:00Z"     // UTC
"2025-01-15T18:30:00+08:00" // With offset

// Dates without time (local date):
"2025-01-15"
```

### Currency Format

```typescript
interface Money {
  amount: number;     // Numeric (not string)
  currency: string;   // ISO 4217 code: "USD", "CNY", "JPY"
}
```

## Circuit Breaker (Future Enhancement)

```java
// Resilience4j configuration
@CircuitBreaker(name = "agentService", fallbackMethod = "agentFallback")
@Retry(name = "agentService")
public AgentPlanResponse generatePlan(AgentPlanRequest request) {
    // Call agent service
}

public AgentPlanResponse agentFallback(AgentPlanRequest request, Exception ex) {
    // Return cached plan or graceful degradation
    return getCachedPlan(request);
}
```

## Security Considerations

### Authentication Flow

```
1. User logs in
   Frontend ← JWT Token

2. Frontend includes token in requests
   Authorization: Bearer {token}

3. Gateway validates token
   - Verify signature
   - Check expiration
   - Extract user info

4. Services receive authenticated user
   - From security context
   - User ID in request header
```

### Internal Service Authentication

For Java → Agent communication (future enhancement):

```yaml
# Use service-to-service JWT or API key
agent:
  api-key: ${AGENT_API_KEY}
```

### CORS Configuration

```java
// Java Gateway CORS
@Bean
public CorsWebFilter corsWebFilter() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(Arrays.asList(
        "http://localhost:3000",
        "https://your-domain.com"
    ));
    config.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(Arrays.asList("*"));
    config.setAllowCredentials(true);
    config.setMaxAge(3600L);
    
    return new CorsWebFilter(corsConfigurationSource());
}
```

---

*This specification is managed by OpenSpec. Refer to project.md for cross-project conventions.*
