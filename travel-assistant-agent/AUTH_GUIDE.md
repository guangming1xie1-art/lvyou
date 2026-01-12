# Authentication Guide

## Overview

This guide explains how to use the JWT-based authentication system in the Travel Assistant application.

## Backend API

### Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!",
    "confirm_password": "Test123!"
  }'
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "created_at": "2025-01-12T12:00:00Z",
  "last_login": null
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!"
  }'
```

**Response** (200 OK):
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "created_at": "2025-01-12T12:00:00Z",
    "last_login": "2025-01-12T12:30:00Z"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

### Refresh Access Token

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

### Get Current User

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "created_at": "2025-01-12T12:00:00Z",
  "last_login": "2025-01-12T12:30:00Z"
}
```

### Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

## Frontend Integration

### Using the Auth Service

```typescript
import { authService } from '@/services/authService';

// Register
const user = await authService.register('username', 'email@example.com', 'Password123!');

// Login
const response = await authService.login('username', 'Password123!');
console.log(response.user);
console.log(response.tokens.access_token);

// Get current user
const currentUser = await authService.getCurrentUser();

// Check authentication status
if (authService.isAuthenticated()) {
  // User is logged in
}

// Get access token
const token = authService.getAccessToken();

// Logout
await authService.logout();
```

### Using the Auth Hook

```typescript
import { useAuth } from '@/hooks/useAuth';

function MyComponent() {
  const { user, isAuthenticated, login, logout, isLoading } = useAuth();

  const handleLogin = async () => {
    try {
      await login('username', 'Password123!');
      // User is now logged in
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  if (isLoading) return <div>Loading...</div>;

  if (!isAuthenticated) {
    return <button onClick={handleLogin}>Login</button>;
  }

  return (
    <div>
      <p>Welcome, {user?.username}!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Using Protected Routes

```tsx
import ProtectedRoute from '@/components/ProtectedRoute';

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/search"
          element={
            <ProtectedRoute>
              <Search />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}
```

### Making Authenticated API Calls

```typescript
import { agentApi } from '@/services/agentApi';

// The auth interceptor will automatically inject the token
const result = await agentApi.search({
  origin: 'Beijing',
  destination: 'Tokyo',
  departure_date: '2025-02-01',
  passengers: 2
});
```

## Password Requirements

Passwords must meet the following criteria:
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&*(),.?":{}|<>)
- Must not contain the username

## Token Management

### Access Token
- **Lifetime**: 15 minutes
- **Storage**: sessionStorage (cleared on tab close)
- **Usage**: Included in Authorization header for API calls

### Refresh Token
- **Lifetime**: 7 days
- **Storage**: localStorage (persists across sessions)
- **Usage**: To obtain new access tokens when expired

### Automatic Token Refresh

The frontend automatically handles token refresh:
1. When an API call returns 401 Unauthorized
2. The auth interceptor uses the refresh token to get a new access token
3. The original request is retried with the new token
4. If refresh fails, the user is redirected to login

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Username already registered"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

#### 403 Forbidden
```json
{
  "detail": "Inactive user"
}
```

#### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters long",
      "type": "value_error"
    }
  ]
}
```

### Frontend Error Handling

```typescript
try {
  await authService.login('username', 'password');
} catch (error) {
  if (error.message.includes('Invalid username or password')) {
    // Show login error to user
  } else if (error.message.includes('User account is disabled')) {
    // Show account disabled message
  } else {
    // Show generic error
  }
}
```

## Configuration

### Environment Variables (Backend)

```env
# JWT Settings
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
REQUIRE_HTTPS=false  # Set to true in production
MIN_PASSWORD_LENGTH=8
REQUIRE_SPECIAL_CHARS=true
```

### Environment Variables (Frontend)

```env
# Agent API
VITE_AGENT_API_BASE_URL=http://localhost:8000

# Token Settings
VITE_TOKEN_REFRESH_THRESHOLD=300000  # 5 minutes
VITE_SESSION_TIMEOUT=604800000  # 7 days
```

## Security Best Practices

### For Users
1. Use strong, unique passwords
2. Don't share your refresh token
3. Log out from shared devices
4. Report suspicious activity

### For Developers
1. Never commit `.env` files
2. Use strong JWT secrets in production
3. Enable HTTPS in production
4. Monitor audit logs
5. Implement proper error handling
6. Don't store access tokens in localStorage (use sessionStorage)

### For Administrators
1. Regularly rotate JWT secret keys
2. Monitor failed login attempts
3. Review audit logs regularly
4. Keep dependencies updated
5. Use strong database passwords

## Testing

### Test Authentication Flow

```bash
# 1. Register a new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!",
    "confirm_password": "Test123!"
  }'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!"
  }' | jq -r '.tokens.access_token')

# 3. Use the token to access protected endpoint
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Test search endpoint (requires authentication)
curl -X POST http://localhost:8000/api/agent/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Beijing",
    "destination": "Tokyo",
    "departure_date": "2025-02-01",
    "passengers": 2
  }'
```

## Troubleshooting

### Login Issues
- **"Invalid username or password"**: Check credentials, ensure account exists
- **"User account is disabled"**: Contact administrator

### Token Issues
- **401 Unauthorized**: Token may be expired. Refresh token should handle this automatically
- **"Session expired. Please login again"**: Refresh token expired, user must log in again

### CORS Issues
- Ensure `CORS_ORIGINS` includes your frontend URL
- Check that no extensions are blocking requests

## Additional Resources

- [Security Documentation](./SECURITY.md)
- [API Documentation](./API_REST_README.md)
- [Development Guide](./DEVELOPMENT.md)
