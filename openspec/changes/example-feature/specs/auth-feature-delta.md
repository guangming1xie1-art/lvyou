# Spec Delta: User Authentication Feature

## Summary of Changes

This document tracks all specification changes required to implement the User Authentication feature.

---

## Added to `openspec/specs/backend-java/spec.md`

### New Section: Authentication

```markdown
## Authentication & Authorization

### JWT Token Structure

The auth-service generates JWT tokens using HS256 algorithm:

```java
// JwtUtil.java
public class JwtUtil {
    private static final String SECRET = "your-256-bit-secret-key-min-32-chars";
    private static final long EXPIRATION = 12 * 60 * 60 * 1000; // 12 hours

    public String generateToken(String userId, String role, String email) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + EXPIRATION);

        return Jwts.builder()
            .subject(userId)
            .claim("email", email)
            .claim("role", role)
            .issuedAt(now)
            .expiration(expiryDate)
            .signWith(SignatureAlgorithm.HS256, SECRET)
            .compact();
    }
}
```

### Token Payload

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "user",
  "iat": 1704067200,
  "exp": 1704153600
}
```

### New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT |
| POST | `/api/v1/auth/logout` | Logout (client-side) |
| GET | `/api/v1/auth/me` | Get current user profile |

### Register Request/Response

```typescript
interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

interface RegisterResponse {
  code: number;
  message: string;
  data: {
    user: UserProfile;
    token: string;
    expiresIn: number;
  };
}
```

### Login Request/Response

```typescript
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  code: number;
  message: string;
  data: {
    token: string;
    tokenType: "Bearer";
    expiresIn: number;  // seconds
    user: UserProfile;
  };
}
```

### New Error Codes

```java
public enum ResultCode {
    // ... existing codes

    // Authentication errors (40101-40199)
    UNAUTHORIZED(40101, "Authentication required"),
    INVALID_TOKEN(40102, "Invalid authentication token"),
    TOKEN_EXPIRED(40103, "Authentication token expired"),
    EMAIL_ALREADY_REGISTERED(40104, "Email already registered"),
    INVALID_CREDENTIALS(40105, "Invalid email or password"),

    // ... rest of codes
}
```

### New Entity

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

### Database Schema

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

### Password Requirements

- Minimum 8 characters
- No maximum length (but consider practical limits)
- Store as bcrypt hash with salt rounds = 12

### Session Management

- JWT tokens expire in 12 hours
- Frontend stores token securely
- No server-side session storage required
- Token refresh is future enhancement
```

---

## Added to `openspec/specs/frontend/spec.md`

### New Section: Authentication

```markdown
## Authentication

### Auth Store (Zustand)

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

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
        const response = await authService.login({ email, password });
        set({
          user: response.data.user,
          token: response.data.token,
          isAuthenticated: true,
          isLoading: false
        });
      },

      register: async ({ email, password, name }) => {
        set({ isLoading: true });
        const response = await authService.register({ email, password, name });
        set({
          user: response.data.user,
          token: response.data.token,
          isAuthenticated: true,
          isLoading: false
        });
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
        const response = await authService.getMe();
        set({ user: response.data, isAuthenticated: true });
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token })
    }
  )
);
```

### Protected Routes

```typescript
// router.tsx
const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        path: 'login',
        element: <Login />
      },
      {
        path: 'register',
        element: <Register />
      },
      {
        element: <ProtectedRoute />,
        children: [
          {
            path: 'travel-requests',
            element: <TravelRequests />
          },
          {
            path: 'plans',
            element: <Plans />
          }
        ]
      }
    ]
  }
]);
```

### Auth API Service

```typescript
// services/authService.ts
export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    return http.post('/auth/login', data);
  },

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    return http.post('/auth/register', data);
  },

  async getMe(): Promise<User> {
    return http.get('/auth/me');
  },

  async logout(): Promise<void> {
    // Client-side logout only
    await http.post('/auth/logout');
  }
};
```

### API Client with Auth Interceptor

```typescript
// utils/request.ts
const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

// Request interceptor
http.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }
);

// Response interceptor
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
```

### New Pages

| Path | Component | Auth Required |
|------|-----------|---------------|
| `/login` | `Login.tsx` | No |
| `/register` | `Register.tsx` | No |
| `/profile` | `Profile.tsx` | Yes (future) |

### Login Page Requirements

- Email input with validation
- Password input with toggle visibility
- "Remember me" checkbox (optional)
- "Forgot password" link (future)
- Submit button with loading state
- Error message display
- Link to registration page

### Registration Page Requirements

- Name input
- Email input with validation
- Password input with requirements display
- Confirm password input
- Submit button with loading state
- Error message display
- Link to login page
```

---

## Added to `openspec/specs/integration/spec.md`

### Updated Section: Authentication Flow

```markdown
### Authentication Flow

```
User Browser                              Gateway (8080)              Auth Service (8081)
    │                                           │                           │
    │ POST /api/v1/auth/login                   │                           │
    │ {email, password}                         │                           │
    │ ─────────────────────────────────────────►│                           │
    │                                           │ POST /auth/login          │
    │                                           │ {email, password}         │
    │                                           │───────────────────────────►
    │                                           │                           │
    │                                           │     {token, user}         │
    │                                           │◄───────────────────────────
    │ {token, user}                             │                           │
    │◄──────────────────────────────────────────│                           │
    │                                           │                           │
    │ (Store token)                             │                           │
    │                                           │                           │
    │ GET /api/v1/travel-requests               │                           │
    │ Authorization: Bearer {token}             │                           │
    │ ─────────────────────────────────────────►│                           │
    │                                           │ Validate JWT              │
    │                                           │ Add X-User-Id header      │
    │                                           │───────────────────────────►│
    │                                           │ GET /travel-requests      │
    │                                           │ X-User-Id: {userId}       │
    │                                           │───────────────────────────►│
    │                                           │                           │
    │ [User's travel requests]                  │     [Filtered by user]    │
    │◄──────────────────────────────────────────│◄───────────────────────────
```

### Token Validation

All protected endpoints require a valid JWT token:

```http
GET /api/v1/travel-requests HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Error Responses for Authentication

```json
{
  "code": 40101,
  "message": "Authentication required",
  "details": {
    "reason": "Missing Authorization header"
  }
}
```

```json
{
  "code": 40105,
  "message": "Invalid email or password"
}
```

```json
{
  "code": 40103,
  "message": "Authentication token expired"
}
```
```

---

## Modified: `openspec/specs/backend-java/spec.md`

### Modified: Service Responsibilities Table

| Service | Port | Responsibility | Dependencies |
|---------|------|----------------|--------------|
| auth-service | 8081 | JWT authentication, authorization | Nacos, PostgreSQL |

**Note**: This service already existed but now has full functionality.

---

## Modified: `openspec/specs/integration/spec.md`

### Modified: Rate Limits

| Client Type | Requests/minute | Burst | Notes |
|-------------|-----------------|-------|-------|
| Frontend (Web) | 60 | 10 | Per user |
| Frontend (Auth) | 5 | 2 | Login attempts per minute |
| Internal (Java→Agent) | 120 | 20 | Service-to-service |

**Note**: Added rate limiting for auth endpoints specifically.
