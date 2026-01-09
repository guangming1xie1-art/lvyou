# Technical Design: User Authentication Feature

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Architecture                                  │
└─────────────────────────────────────────────────────────────────────────┘

                         User Browser
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  travel-assistant-front (React)                                         │
│  - Login/Register Pages                                                  │
│  - Auth Store (Zustand)                                                 │
│  - Axios Interceptor                                                    │
│  - Protected Routes                                                     │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ HTTP + JWT
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  travel-assistant (Spring Cloud Gateway)                                │
│  - JWT Authentication Filter                                            │
│  - Routes to downstream services                                        │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
               ┌──────────────────┴──────────────────┐
               ▼                                      ▼
┌─────────────────────────┐            ┌─────────────────────────┐
│ auth-service (8081)     │            │ Other Services          │
│ - /auth/register        │            │ - Validate JWT          │
│ - /auth/login           │            │ - Extract user info     │
│ - /auth/me              │            │ - Enforce permissions   │
└─────────────────────────┘            └─────────────────────────┘
               │
               │ PostgreSQL
               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  PostgreSQL Database                                                     │
│  - users table                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Login Flow

```
1. User submits credentials
   Frontend → POST /api/v1/auth/login

2. Gateway routes to auth-service

3. Auth service validates credentials
   - Check user exists
   - Verify password (bcrypt)

4. Generate JWT token
   - Payload: userId, email, role, expiration
   - Sign with HS256

5. Return token to frontend
   { "token": "eyJ...", "expiresIn": 43200 }

6. Frontend stores token
   - httpOnly cookie (preferred) OR
   - memory with secure storage

7. Subsequent requests include token
   Authorization: Bearer {token}

8. Gateway validates token
   - Verify signature
   - Check expiration
   - Extract claims

9. Forward to downstream services
   with user header: X-User-Id
```

### Protected Request Flow

```
1. Frontend makes request
   GET /api/v1/travel-requests
   Authorization: Bearer {token}

2. Gateway intercepts
   - Extract token
   - Validate JWT
   - Extract user claims
   - Add user headers

3. Forward to service
   GET /api/v1/travel-requests
   X-User-Id: {userId}
   X-User-Email: {email}

4. Service processes
   - Use X-User-Id for ownership check
   - Return user's resources only
```

## API Contracts

### Frontend → Java Backend

#### Register User

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe"
}
```

**Response (201 Created)**
```json
{
  "code": 0,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "name": "John Doe",
      "createdAt": "2025-01-01T00:00:00Z"
    }
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

**Response (400 Bad Request)**
```json
{
  "code": 40001,
  "message": "Validation failed",
  "details": {
    "email": ["Email already registered"],
    "password": ["Password must be at least 8 characters"]
  }
}
```

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK)**
```json
{
  "code": 0,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "tokenType": "Bearer",
    "expiresIn": 43200,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "name": "John Doe"
    }
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

**Response (401 Unauthorized)**
```json
{
  "code": 40101,
  "message": "Invalid email or password",
  "data": null
}
```

#### Get Current User

```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

**Response (200 OK)**
```json
{
  "code": 0,
  "message": "OK",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2025-01-01T00:00:00Z"
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Data Models

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

### Entity Class

```java
@Entity
@Table(name = "users")
public class UserEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    @Column(nullable = false, unique = true, length = 255)
    private String email;
    
    @Column(name = "password_hash", nullable = false, length = 255)
    private String passwordHash;
    
    @Column(nullable = false, length = 255)
    private String name;
    
    @Column(length = 50)
    private String role = "user";
    
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
```

### DTOs

```java
// Request DTOs
@Data
public class RegisterRequest {
    @NotBlank
    @Email
    private String email;
    
    @NotBlank
    @Size(min = 8)
    private String password;
    
    @NotBlank
    @Size(max = 255)
    private String name;
}

@Data
public class LoginRequest {
    @NotBlank
    @Email
    private String email;
    
    @NotBlank
    private String password;
}

// Response DTOs
@Data
public class AuthResponse {
    private String token;
    private String tokenType;
    private Long expiresIn;
    private UserResponse user;
}

@Data
public class UserResponse {
    private UUID id;
    private String email;
    private String name;
    private LocalDateTime createdAt;
}
```

## Component Design

### Frontend Components

```
travel-assistant-front/src/
├── pages/
│   ├── Login.tsx           # Login form
│   ├── Register.tsx        # Registration form
│   └── Profile.tsx         # User profile (future)
├── store/
│   └── authStore.ts        # Zustand auth state
├── hooks/
│   └── useAuth.ts          # Auth operations hook
├── services/
│   └── authService.ts      # Auth API client
└── components/
    └── auth/               # Auth-related components
        ├── ProtectedRoute.tsx
        └── AuthGuard.tsx
```

### Auth Store (Zustand)

```typescript
// store/authStore.ts
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  login: (credentials: LoginParams) => Promise<void>;
  register: (data: RegisterParams) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      
      login: async ({ email, password }) => {
        set({ isLoading: true });
        try {
          const response = await authService.login({ email, password });
          set({
            user: response.data.user,
            token: response.data.token,
            isAuthenticated: true,
            isLoading: false
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },
      
      register: async ({ email, password, name }) => {
        set({ isLoading: true });
        try {
          const response = await authService.register({ email, password, name });
          set({
            user: response.data.user,
            token: response.data.token,
            isAuthenticated: true,
            isLoading: false
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },
      
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },
      
      checkAuth: async () => {
        const { token } = get();
        if (!token) {
          set({ isAuthenticated: false });
          return;
        }
        try {
          const response = await authService.getMe();
          set({
            user: response.data,
            isAuthenticated: true
          });
        } catch {
          set({ user: null, token: null, isAuthenticated: false });
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token })
    }
  )
);
```

### Protected Route Component

```typescript
// components/auth/ProtectedRoute.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

export function ProtectedRoute() {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <Outlet />;
}
```

### API Client with Interceptor

```typescript
// services/api.ts
import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

// Request interceptor - add token
http.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle 401
http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export { http };
```

### Java Backend Services

```
travel-assistant/auth-service/
├── src/main/java/com/travelassistant/auth/
│   ├── controller/
│   │   └── AuthController.java
│   ├── service/
│   │   └── AuthService.java
│   ├── repository/
│   │   └── UserRepository.java
│   ├── entity/
│   │   └── UserEntity.java
│   ├── dto/
│   │   ├── request/
│   │   │   ├── RegisterRequest.java
│   │   │   └── LoginRequest.java
│   │   └── response/
│   │       ├── AuthResponse.java
│   │       └── UserResponse.java
│   ├── mapper/
│   │   └── UserMapper.java
│   ├── security/
│   │   └── JwtService.java
│   └── config/
│       ├── SecurityConfig.java
│       └── WebConfig.java
```

### JWT Service

```java
@Service
public class JwtService {
    
    @Value("${app.jwt.secret}")
    private String secret;
    
    @Value("${app.jwt.expiration}")
    private long expiration;
    
    public String generateToken(UserEntity user) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);
        
        return Jwts.builder()
            .subject(user.getId().toString())
            .claim("email", user.getEmail())
            .claim("role", user.getRole())
            .issuedAt(now)
            .expiration(expiryDate)
            .signWith(SignatureAlgorithm.HS256, secret)
            .compact();
    }
    
    public UUID extractUserId(String token) {
        Claims claims = parseToken(token);
        return UUID.fromString(claims.getSubject());
    }
    
    public String extractEmail(String token) {
        return parseToken(token).get("email", String.class);
    }
    
    public boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }
    
    public long getExpirationMs() {
        return expiration;
    }
}
```

### Gateway Authentication Filter

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    @Autowired
    private JwtService jwtService;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        
        String authHeader = request.getHeader("Authorization");
        
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            
            if (jwtService.validateToken(token)) {
                UUID userId = jwtService.extractUserId(token);
                String email = jwtService.extractEmail(token);
                
                // Add user info to request headers for downstream services
                request.setAttribute("userId", userId);
                request.setAttribute("userEmail", email);
                
                // Also add as response headers for debugging
                response.addHeader("X-User-Id", userId.toString());
                response.addHeader("X-User-Email", email);
            }
        }
        
        filterChain.doFilter(request, response);
    }
    
    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getRequestURI();
        return path.startsWith("/api/auth/") || 
               path.equals("/health") ||
               path.startsWith("/actuator/");
    }
}
```

## Implementation Details

### Password Hashing

```java
@Service
public class PasswordService {
    
    private static final int SALT_ROUNDS = 12;
    
    public String hashPassword(String plainPassword) {
        return BCrypt.hashpw(plainPassword, BCrypt.gensalt(SALT_ROUNDS));
    }
    
    public boolean verifyPassword(String plainPassword, String hashedPassword) {
        return BCrypt.checkpw(plainPassword, hashedPassword);
    }
}
```

### Registration Flow

```java
@Service
public class AuthService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private PasswordService passwordService;
    
    @Autowired
    private JwtService jwtService;
    
    public AuthResponse register(RegisterRequest request) {
        // Check if email exists
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException(EMAIL_ALREADY_REGISTERED);
        }
        
        // Create user
        UserEntity user = new UserEntity();
        user.setEmail(request.getEmail());
        user.setPasswordHash(passwordService.hashPassword(request.getPassword()));
        user.setName(request.getName());
        user.setRole("user");
        
        user = userRepository.save(user);
        
        // Generate token
        String token = jwtService.generateToken(user);
        
        return AuthResponse.builder()
            .token(token)
            .tokenType("Bearer")
            .expiresIn(jwtService.getExpirationMs() / 1000)
            .user(UserMapper.toResponse(user))
            .build();
    }
}
```

## Security Considerations

### Token Storage (Frontend)

**Preferred: httpOnly Cookie**
- Set by backend on login response
- Not accessible via JavaScript
- Protected against XSS

**Fallback: Secure Storage**
- Use sessionStorage for short-lived tokens
- Clear on tab close

### CORS Configuration

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("http://localhost:3000")
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
            .allowedHeaders("*")
            .allowCredentials(true)
            .maxAge(3600);
    }
}
```

### Rate Limiting

```java
// On auth endpoints
@RateLimited(key = "auth:login", limit = 5, window = 60)  // 5 attempts per minute
public ResponseEntity<ApiResponse<AuthResponse>> login(@Valid @RequestBody LoginRequest request) {
    // ...
}
```

## Testing Strategy

### Unit Tests
- Password hashing/verification
- JWT generation/validation
- DTO validation
- Service logic

### Integration Tests
- Full login flow
- Registration with database
- Protected endpoint access
- Token refresh (if implemented)

### E2E Tests
- User registration flow
- Login and session persistence
- Protected page access

## Performance Considerations

- JWT validation is fast (no DB lookup required)
- Password hashing is CPU-intensive (intentional)
- Consider caching user data in gateway
- Token expiration should balance security/usability

## Error Handling

| Error | Code | HTTP Status | Message |
|-------|------|-------------|---------|
| Email already exists | 40001 | 400 | Email already registered |
| Invalid credentials | 40101 | 401 | Invalid email or password |
| Missing token | 40102 | 401 | Authentication required |
| Invalid token | 40103 | 401 | Invalid authentication token |
| Token expired | 40104 | 401 | Authentication token expired |
