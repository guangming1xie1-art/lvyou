# Implementation Tasks: User Authentication Feature

## Phase 1: Backend (Java) - Auth Service

### Database & Entity
- [ ] Create `users` table in PostgreSQL
  - Script location: `travel-assistant/common/src/main/resources/db/migration/`
- [ ] Add `UserEntity` class
  - Location: `auth-service/src/main/java/com/travelassistant/auth/entity/UserEntity.java`
- [ ] Add `UserRepository` interface
  - Location: `auth-service/src/main/java/com/travelassistant/auth/repository/UserRepository.java`

### DTOs & Mappers
- [ ] Create request DTOs (`RegisterRequest`, `LoginRequest`)
  - Location: `auth-service/src/main/java/com/travelassistant/auth/dto/request/`
- [ ] Create response DTOs (`AuthResponse`, `UserResponse`)
  - Location: `auth-service/src/main/java/com/travelassistant/auth/dto/response/`
- [ ] Create `UserMapper`
  - Location: `auth-service/src/main/java/com/travelassistant/auth/mapper/UserMapper.java`

### Service Layer
- [ ] Implement `PasswordService` for bcrypt
  - Location: `auth-service/src/main/java/com/travelassistant/auth/service/PasswordService.java`
- [ ] Implement `JwtService` for token operations
  - Location: `auth-service/src/main/java/com/travelassistant/auth/service/JwtService.java`
- [ ] Implement `AuthService`
  - Location: `auth-service/src/main/java/com/travelassistant/auth/service/AuthService.java`

### Controller Layer
- [ ] Implement `AuthController`
  - Location: `auth-service/src/main/java/com/travelassistant/auth/controller/AuthController.java`
  - Endpoints: POST `/auth/register`, POST `/auth/login`, GET `/auth/me`

### Security Configuration
- [ ] Update `SecurityConfig` for auth endpoints
- [ ] Add `JwtAuthenticationFilter` in gateway
- [ ] Configure CORS for frontend origin

### Database Migration
- [ ] Create Liquibase/Flyway migration script for users table
- [ ] Test migration on clean database

## Phase 2: Backend (Java) - Gateway Integration

### Gateway Configuration
- [ ] Add JWT validation filter to gateway
  - Location: `gateway/src/main/java/com/travelassistant/gateway/JwtAuthenticationFilter.java`
- [ ] Configure protected routes in gateway
- [ ] Add user headers propagation to downstream services

### Update Existing Services
- [ ] Update `TravelRequestService` to use `X-User-Id` header
  - Filter queries by user ID
- [ ] Update `TravelPlanService` to use `X-User-Id` header
- [ ] Update `OrderService` to use `X-User-Id` header

### Error Handling
- [ ] Add global exception handler for auth errors
- [ ] Add error codes for authentication failures

## Phase 3: Frontend - Auth UI

### Auth Store
- [ ] Create `authStore` with Zustand
  - Location: `travel-assistant-front/src/store/authStore.ts`
- [ ] Implement login, register, logout actions
- [ ] Implement token persistence
- [ ] Implement session validation on app load

### API Service
- [ ] Create `authService`
  - Location: `travel-assistant-front/src/services/authService.ts`
- [ ] Update API client with auth interceptor
  - Location: `travel-assistant-front/src/utils/request.ts`

### Pages
- [ ] Create `Login` page
  - Location: `travel-assistant-front/src/pages/Login.tsx`
- [ ] Create `Register` page
  - Location: `travel-assistant-front/src/pages/Register.tsx`

### Components
- [ ] Create `ProtectedRoute` component
  - Location: `travel-assistant-front/src/components/auth/ProtectedRoute.tsx`
- [ ] Update `router.tsx` with protected routes
- [ ] Add auth header to navigation (show user info when logged in)

## Phase 4: Integration Testing

### Unit Tests (Java)
- [ ] Test `PasswordService`
- [ ] Test `JwtService`
- [ ] Test `AuthService`
- [ ] Test `AuthController`

### Unit Tests (Frontend)
- [ ] Test `authStore`
- [ ] Test `authService`

### Integration Tests
- [ ] Test full registration flow
- [ ] Test full login flow
- [ ] Test protected endpoint access
- [ ] Test token validation

### E2E Tests (Optional - Future)
- [ ] User registration E2E test
- [ ] Login/logout E2E test
- [ ] Protected page access E2E test

## Phase 5: Documentation & Cleanup

### Documentation
- [ ] Update API documentation for auth endpoints
- [ ] Update `openspec/specs/backend-java/spec.md` with new endpoints
- [ ] Update `openspec/specs/integration/spec.md` with auth flow

### Code Review Preparation
- [ ] Ensure all code is linted
- [ ] Ensure all tests pass
- [ ] Add code comments for complex logic
- [ ] Verify no sensitive data in logs

### Deployment Preparation
- [ ] Add database migration to deployment
- [ ] Configure JWT secret in environment
- [ ] Update docker-compose with database changes
