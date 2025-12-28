# Backend Java Specification

> OpenSpec specification for travel-assistant (Spring Cloud microservices)

## Overview

This document defines the technical specifications, patterns, and standards for the Java Spring Cloud backend services.

## Microservice Responsibilities

### Service Boundaries

| Service | Port | Responsibility | Dependencies |
|---------|------|----------------|--------------|
| gateway | 8080 | Request routing, auth, rate limiting | Nacos, all downstream |
| auth-service | 8081 | JWT authentication, authorization | Nacos, PostgreSQL |
| travel-request-service | 8082 | Travel request management | Nacos, PostgreSQL |
| travel-plan-service | 8083 | Travel plan generation, order coordination | Nacos, PostgreSQL, Agent |
| order-service | 8084 | Order processing | Nacos, PostgreSQL |

### Common Module

The `common` module provides shared functionality:

- `ApiResponse<T>` - Standardized response wrapper
- `ResultCode` - Enumeration of result codes
- `BaseEntity` - Base entity with audit fields
- `JwtUtil` - JWT token generation and validation
- `BusinessException` - Custom business exception

## REST API Design Standards

### URL Naming Conventions

```plaintext
# Resource naming (plural, kebab-case)
/api/v1/travel-requests
/api/v1/travel-plans
/api/v1/orders

# Nested resources
/api/v1/travel-requests/{requestId}/plans

# Actions (use HTTP methods, not action verbs in URL)
POST   /api/v1/travel-requests          # Create
GET    /api/v1/travel-requests/{id}     # Read
PUT    /api/v1/travel-requests/{id}     # Update (full)
PATCH  /api/v1/travel-requests/{id}     # Update (partial)
DELETE /api/v1/travel-requests/{id}     # Delete
```

### HTTP Methods Semantics

| Method | Idempotent | Safe | Use Case |
|--------|------------|------|----------|
| GET | Yes | Yes | Retrieve resource |
| POST | No | No | Create resource, actions |
| PUT | Yes | No | Replace resource |
| PATCH | No | No | Partial update |
| DELETE | Yes | No | Remove resource |

### Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| Content-Type | Yes | application/json |
| Authorization | Yes (most) | Bearer {token} |
| Accept | No | application/json |
| Accept-Language | No | Language preference |

### Standard Response Format

```json
{
  "code": 0,
  "message": "OK",
  "data": {},
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### Success Response Examples

```json
// Single resource
{
  "code": 0,
  "message": "OK",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "destination": "Tokyo",
    "status": "pending"
  },
  "timestamp": "2025-01-01T00:00:00Z"
}

// List with pagination
{
  "code": 0,
  "message": "OK",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "totalPages": 5
    }
  },
  "timestamp": "2025-01-01T00:00:00Z"
}

// Empty list
{
  "code": 0,
  "message": "OK",
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 0,
      "totalPages": 0
    }
  }
}
```

### Error Response Format

```json
{
  "code": 40001,
  "message": "Validation failed",
  "data": null,
  "timestamp": "2025-01-01T00:00:00Z",
  "details": {
    "destination": ["Destination is required"],
    "budget": ["Budget must be positive"]
  }
}
```

## Request/Response Schemas

### DTO Pattern

```
src/main/java/com/travelassistant/{module}/
├── controller/
│   └── XxxController.java       # REST endpoints
├── service/
│   └── XxxService.java          # Business logic
├── repository/
│   └── XxxRepository.java       # Data access
├── entity/
│   └── XxxEntity.java           # JPA entity
├── dto/
│   ├── request/
│   │   ├── CreateXxxRequest.java
│   │   └── UpdateXxxRequest.java
│   └── response/
│       ├── XxxResponse.java
│       └── XxxListResponse.java
└── mapper/
    └── XxxMapper.java           # Entity-DTO mapping
```

### DTO Examples

```java
// Create Request DTO
@Data
public class CreateTravelRequestRequest {
    
    @NotBlank(message = "Destination is required")
    @Size(max = 255, message = "Destination must be less than 255 characters")
    private String destination;
    
    @NotNull(message = "Start date is required")
    @FutureOrPresent(message = "Start date must be in the future or today")
    private LocalDate startDate;
    
    @Future(message = "End date must be in the future")
    private LocalDate endDate;
    
    @DecimalMin(value = "0.0", message = "Budget must be positive")
    private BigDecimal budget;
    
    @Size(max = 1000, message = "Preferences must be less than 1000 characters")
    private String preferences;
    
    private Integer durationDays;
    private String accommodationType;
    private List<String> interests;
}

// Response DTO
@Data
public class TravelRequestResponse {
    private UUID id;
    private String destination;
    private LocalDate startDate;
    private LocalDate endDate;
    private BigDecimal budget;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

## Error Codes & HTTP Status Handling

### HTTP Status Codes

| Status | Code | Meaning |
|--------|------|---------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Client error (validation, format) |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Valid token, insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Custom Error Codes

```java
// ResultCode.java
public enum ResultCode {
    SUCCESS(0, "OK"),
    
    // Validation errors (40001-40099)
    VALIDATION_ERROR(40001, "Validation failed"),
    INVALID_REQUEST_BODY(40002, "Invalid request body"),
    
    // Authentication errors (40101-40199)
    UNAUTHORIZED(40101, "Authentication required"),
    INVALID_TOKEN(40102, "Invalid authentication token"),
    TOKEN_EXPIRED(40103, "Authentication token expired"),
    
    // Authorization errors (40301-40399)
    FORBIDDEN(40301, "Access denied"),
    
    // Resource errors (40401-40499)
    NOT_FOUND(40401, "Resource not found"),
    TRAVEL_REQUEST_NOT_FOUND(40402, "Travel request not found"),
    
    // Server errors (50001-50099)
    INTERNAL_ERROR(50001, "Internal server error"),
    SERVICE_UNAVAILABLE(50002, "Service temporarily unavailable"),
    
    // Business errors (60001-60999)
    BUSINESS_ERROR(60001, "Business rule violation"),
    INVALID_STATUS_TRANSITION(60002, "Invalid status transition");
    
    private final int code;
    private final String message;
    
    // getters
}
```

### Exception Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException ex) {
        log.warn("Business exception: {}", ex.getMessage());
        return ResponseEntity
            .status(HttpStatus.BAD_REQUEST)
            .body(ApiResponse.error(ex.getCode(), ex.getMessage()));
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Map<String, String>>> handleValidationException(
            MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error ->
            errors.put(error.getField(), error.getDefaultMessage())
        );
        return ResponseEntity
            .status(HttpStatus.BAD_REQUEST)
            .body(ApiResponse.error(40001, "Validation failed", errors));
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGenericException(Exception ex) {
        log.error("Unexpected error", ex);
        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(ApiResponse.error(50001, "Internal server error"));
    }
}
```

## Authentication & Authorization

### JWT Token Structure

```java
// JwtUtil.java
public class JwtUtil {
    private static final String SECRET = "your-256-bit-secret-key-min-32-chars";
    private static final long EXPIRATION = 12 * 60 * 60 * 1000; // 12 hours
    
    public String generateToken(String userId, String role) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + EXPIRATION);
        
        return Jwts.builder()
            .subject(userId)
            .claim("role", role)
            .issuedAt(now)
            .expiration(expiryDate)
            .signWith(SignatureAlgorithm.HS256, SECRET)
            .compact();
    }
    
    public Claims parseToken(String token) {
        return Jwts.parser()
            .setSigningKey(SECRET)
            .parseClaimsJws(token)
            .getBody();
    }
    
    public boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (JwtException e) {
            return false;
        }
    }
}
```

### Authentication Filter

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    @Autowired
    private JwtUtil jwtUtil;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String authHeader = request.getHeader("Authorization");
        
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            try {
                Claims claims = jwtUtil.parseToken(token);
                String userId = claims.getSubject();
                String role = claims.get("role", String.class);
                
                // Set authentication context
                UsernamePasswordAuthenticationToken authentication =
                    new UsernamePasswordAuthenticationToken(userId, null, 
                        Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role)));
                SecurityContextHolder.getContext().setAuthentication(authentication);
            } catch (Exception e) {
                // Clear context on invalid token
                SecurityContextHolder.clearContext();
            }
        }
        
        filterChain.doFilter(request, response);
    }
}
```

### Security Configuration

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/actuator/**").permitAll()
                .requestMatchers("/health").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter, 
                UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }
}
```

## Database Models & Relationships

### Base Entity

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Getters and setters
}
```

### TravelRequest Entity

```java
@Entity
@Table(name = "travel_requests")
public class TravelRequestEntity extends BaseEntity {
    
    @Column(name = "user_id", nullable = false)
    private UUID userId;
    
    @Column(nullable = false, length = 255)
    private String destination;
    
    @Column(name = "start_date")
    private LocalDate startDate;
    
    @Column(name = "end_date")
    private LocalDate endDate;
    
    @Column(precision = 10, scale = 2)
    private BigDecimal budget;
    
    @Enumerated(EnumType.STRING)
    @Column(length = 50)
    private RequestStatus status = RequestStatus.PENDING;
    
    @Column(columnDefinition = "TEXT")
    private String preferences;
    
    @Column(name = "duration_days")
    private Integer durationDays;
    
    @Column(name = "accommodation_type", length = 100)
    private String accommodationType;
    
    @Column(columnDefinition = "TEXT")
    private String interests; // JSON array stored as text
    
    // Relationships
    @OneToMany(mappedBy = "travelRequest", cascade = CascadeType.ALL)
    private List<TravelPlanEntity> plans;
    
    // Enums
    public enum RequestStatus {
        PENDING,
        PROCESSING,
        COMPLETED,
        CANCELLED
    }
}
```

### TravelPlan Entity

```java
@Entity
@Table(name = "travel_plans")
public class TravelPlanEntity extends BaseEntity {
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "travel_request_id", nullable = false)
    private TravelRequestEntity travelRequest;
    
    @Column(nullable = false, length = 255)
    private String title;
    
    @Column(columnDefinition = "TEXT")
    private String overview;
    
    @Column(columnDefinition = "JSONB")
    private String itinerary; // JSON itinerary data
    
    @Column(columnDefinition = "JSONB")
    private String budgetBreakdown;
    
    @Column(columnDefinition = "TEXT")
    private String packingList;
    
    @Column(columnDefinition = "TEXT")
    private String tips;
    
    @Enumerated(EnumType.STRING)
    @Column(length = 50)
    private PlanStatus status = PlanStatus.GENERATED;
    
    @Column(name = "agent_execution_time_ms")
    private Long agentExecutionTimeMs;
    
    public enum PlanStatus {
        GENERATED,
        REVIEWED,
        SELECTED,
        BOOKED,
        CANCELLED
    }
}
```

### Repository Pattern

```java
public interface TravelRequestRepository extends JpaRepository<TravelRequestEntity, UUID> {
    
    List<TravelRequestEntity> findByUserIdAndStatus(UUID userId, RequestStatus status);
    
    Page<TravelRequestEntity> findByUserId(UUID userId, Pageable pageable);
    
    @Query("SELECT t FROM TravelRequestEntity t WHERE t.status = :status ORDER BY t.createdAt DESC")
    List<TravelRequestEntity> findPendingRequests(@Param("status") RequestStatus status);
    
    @EntityGraph(attributePaths = {"plans"})
    Optional<TravelRequestEntity> findWithPlansById(UUID id);
}
```

## Caching Strategy

### Cache Configuration

```yaml
# application.yml
spring:
  cache:
    type: redis
    redis:
      host: localhost
      port: 6379
      timeout: 2000ms
```

### Cache Usage

```java
@Service
public class TravelRequestService {
    
    private static final String TRAVEL_REQUESTS_CACHE = "travelRequests";
    private static final String TRAVEL_REQUEST_CACHE = "travelRequest";
    
    @Cacheable(value = TRAVEL_REQUEST_CACHE, key = "#id")
    public TravelRequestResponse getById(UUID id) {
        return entityToResponse(findById(id));
    }
    
    @CacheEvict(value = TRAVEL_REQUESTS_CACHE, allEntries = true)
    public TravelRequestResponse create(CreateTravelRequestRequest request) {
        // Create logic
    }
    
    @CachePut(value = TRAVEL_REQUEST_CACHE, key = "#id")
    public TravelRequestResponse update(UUID id, UpdateTravelRequestRequest request) {
        // Update logic
    }
    
    @CacheEvict(value = {TRAVEL_REQUEST_CACHE, TRAVEL_REQUESTS_CACHE}, allEntries = true)
    public void delete(UUID id) {
        // Delete logic
    }
}
```

## Logging & Monitoring Requirements

### Log Pattern

```xml
<!-- logback-spring.xml -->
<Pattern>
    %d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n
</Pattern>
```

### Log Levels

| Level | When to Use |
|-------|------------|
| DEBUG | Detailed debugging info, query parameters |
| INFO | Normal operation, key events |
| WARN | Recoverable issues, degraded functionality |
| ERROR | Exceptions, failures requiring attention |

### Structured Logging Example

```java
@Service
@RequiredArgsConstructor
public class TravelRequestService {
    
    private final Logger logger = LoggerFactory.getLogger(TravelRequestService.class);
    
    public TravelRequestResponse create(CreateTravelRequestRequest request) {
        logger.info("Creating travel request for user: {}, destination: {}",
            SecurityContextHolder.getContext().getAuthentication().getName(),
            request.getDestination());
        
        try {
            // Business logic
            logger.info("Travel request created successfully: {}", requestId);
            return response;
        } catch (Exception e) {
            logger.error("Failed to create travel request: {}", e.getMessage(), e);
            throw e;
        }
    }
}
```

### Health Checks

```java
@RestController
@RequestMapping("/health")
public class HealthController {
    
    @Autowired
    private DataSource dataSource;
    
    @GetMapping
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("database", checkDatabase());
        health.put("timestamp", Instant.now().toString());
        
        return ResponseEntity.ok(health);
    }
    
    private String checkDatabase() {
        try (Connection conn = dataSource.getConnection()) {
            return "UP";
        } catch (SQLException e) {
            return "DOWN";
        }
    }
}
```

## Integration Points

### Agent Service Integration

```java
@Service
@RequiredArgsConstructor
public class TravelPlanService {
    
    private final RestTemplate agentRestTemplate;
    private final TravelPlanRepository planRepository;
    
    public TravelPlanResponse generatePlan(UUID requestId) {
        TravelRequest request = travelRequestRepository.findById(requestId)
            .orElseThrow(() -> new BusinessException(NOT_FOUND));
        
        // Call Agent service
        AgentPlanRequest agentRequest = AgentPlanRequest.builder()
            .destination(request.getDestination())
            .startDate(request.getStartDate())
            .endDate(request.getEndDate())
            .budget(request.getBudget())
            .preferences(request.getPreferences())
            .durationDays(request.getDurationDays())
            .build();
        
        ResponseEntity<AgentPlanResponse> agentResponse = agentRestTemplate.postForEntity(
            "/agent/generate-plan",
            agentRequest,
            AgentPlanResponse.class
        );
        
        // Save plan
        TravelPlanEntity plan = mapToEntity(agentResponse.getBody());
        plan.setTravelRequest(request);
        return entityToResponse(planRepository.save(plan));
    }
}
```

### Feign Client (Service-to-Service)

```java
@FeignClient(name = "travel-assistant-agent")
public interface AgentServiceClient {
    
    @PostMapping("/agent/generate-plan")
    AgentPlanResponse generatePlan(@RequestBody AgentPlanRequest request);
    
    @GetMapping("/agent/status")
    AgentStatusResponse getStatus();
}
```

### WebClient (Non-blocking)

```java
@Configuration
public class WebClientConfig {
    
    @Bean
    public WebClient webClient() {
        return WebClient.builder()
            .baseUrl("http://localhost:8000")
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .build();
    }
}
```

---

*This specification is managed by OpenSpec. Refer to project.md for cross-project conventions.*
