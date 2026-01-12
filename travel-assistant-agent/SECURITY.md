# Security Documentation

## Overview

This document describes the security measures implemented in the Travel Assistant Agent system to protect user data, prevent unauthorized access, and ensure secure communication.

## Authentication

### JWT-Based Authentication

The system uses JSON Web Tokens (JWT) for authentication:

- **Access Tokens**: Short-lived tokens (15 minutes) used for API authentication
- **Refresh Tokens**: Long-lived tokens (7 days) used to obtain new access tokens
- **Token Storage**:
  - Access Token: Stored in sessionStorage (cleared when tab closes)
  - Refresh Token: Stored in localStorage (persistent across sessions)

### Token Lifecycle

1. **Login**: User provides credentials → Server returns access + refresh tokens
2. **API Request**: Access token included in `Authorization: Bearer {token}` header
3. **Token Expiry**: When access token expires (401 response), client:
   - Uses refresh token to get new access token
   - Retries the original request
4. **Logout**: Client discards all tokens

### Password Security

- **Hashing**: All passwords are hashed using bcrypt before storage
- **Requirements**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character
- **Validation**: Passwords cannot contain the username

## API Security

### Rate Limiting

All authenticated endpoints are protected by rate limiting:

- **Per Minute**: 100 requests per user
- **Per Hour**: 5000 requests per user
- **Headers**:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: When limit resets (Unix timestamp)
  - `Retry-After`: Seconds to wait (on 429 response)

### CORS Configuration

Cross-Origin Resource Sharing is configured to allow access only from authorized origins:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Security Headers

All responses include the following security headers:

- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - Enables XSS protection
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (production only) - Enforces HTTPS

### HTTPS Enforcement

In production, HTTP requests are automatically redirected to HTTPS:

```env
REQUIRE_HTTPS=true
```

## Protected Endpoints

The following endpoints require authentication:

### Authentication Endpoints
- `POST /api/auth/register` - Public
- `POST /api/auth/login` - Public
- `POST /api/auth/refresh` - Public (uses refresh token)
- `GET /api/auth/me` - Requires authentication
- `POST /api/auth/logout` - Requires authentication

### Agent Endpoints
All agent endpoints require valid authentication:

- `POST /api/agent/search` - Search flights and hotels
- `POST /api/agent/recommend` - Get travel recommendations
- `POST /api/agent/book` - Create a booking
- `GET /api/agent/status/{task_id}` - Get task status
- `GET /api/agent/tasks` - List all tasks

### Public Endpoints
- `GET /health` - Health check
- `GET /` - Service information

## Audit Logging

All API calls are logged for security monitoring and compliance:

### Logged Information
- User ID
- Action performed
- Endpoint and HTTP method
- Request parameters (sensitive data filtered)
- Result (success/failure)
- IP address
- User agent
- Timestamp

### Sensitive Data Filtering
The following fields are automatically filtered from logs:
- `password`
- `token`
- `credit_card`
- `cvv`
- `ssn`
- `api_key`
- `secret`

### Security Events
Special security events are logged with severity levels:
- `auth_failure` - Failed authentication
- `rate_limit_exceeded` - Rate limit violations
- `invalid_token` - Invalid/expired tokens

## Input Validation

### SQL Injection Prevention
- Use SQLAlchemy ORM for all database queries
- Parameterized queries only
- No dynamic SQL construction

### XSS Prevention
- React automatically escapes JSX content
- Avoid `dangerouslySetInnerHTML`
- Input validation on all user inputs

### CSRF Protection
- Same-site cookie policies
- Origin header validation
- State verification on sensitive operations

## Database Security

### User Table
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### Audit Log Table
```sql
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    action VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255),
    method VARCHAR(10),
    params TEXT,
    result VARCHAR(50),
    error_message TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Environment Variables

### Required Security Variables

```env
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security Settings
REQUIRE_HTTPS=false  # true in production
MIN_PASSWORD_LENGTH=8
REQUIRE_SPECIAL_CHARS=true

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong JWT secret keys** in production (at least 32 characters)
3. **Enable HTTPS** in production
4. **Restrict CORS origins** to only your frontend domains
5. **Regularly rotate JWT secret keys** (requires all users to re-login)
6. **Monitor audit logs** for suspicious activity
7. **Keep dependencies updated** to address security vulnerabilities
8. **Use environment-specific configurations**

## Troubleshooting

### Common Issues

#### 401 Unauthorized
- Access token expired
- Token missing from request
- Invalid token format

**Solution**: Client should automatically refresh token using refresh token

#### 429 Too Many Requests
- Rate limit exceeded

**Solution**: Wait and retry (check `Retry-After` header)

#### 403 Forbidden
- User account is disabled
- Insufficient permissions

**Solution**: Contact administrator

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
