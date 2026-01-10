# Implementation Tasks: Refactor Claude Skills to Agent-Centric Architecture

## Phase 1: Infrastructure (Base Classes & Registry)

### 1.1 Create BaseSkill Interface
- [x] Define BaseSkill abstract class with required properties
  - `name`: Unique skill identifier
  - `agent_type`: Which agent uses this skill
  - `description`: Human-readable description
  - `category`: Functional category
  - `version`: Skill version
- [x] Add `input_schema` property returning JSON Schema
- [x] Add `output_schema` property returning JSON Schema
- [x] Add abstract `execute()` method
- [x] Add `validate_input()` method for input validation
- [x] Add `to_definition()` method for MCP format
- [x] Add `format_output()` method for agent consumption

### 1.2 Implement SkillRegistry
- [x] Create `SkillRegistry` class for managing skills
- [x] Implement skill registration method
- [x] Implement skill discovery by name
- [x] Implement skill discovery by agent type
- [x] Implement skill discovery by category
- [x] Add skill metadata retrieval
- [x] Add skill validation on registration
- [x] Add singleton pattern for global registry

### 1.3 Update MCP Server
- [x] Refactor MCP Server to use SkillRegistry
- [x] Update `/mcp/skills` endpoint to use registry
- [x] Update `/mcp/execute` endpoint to use registry
- [x] Update `/mcp/batch-execute` endpoint to use registry
- [x] Remove skill-specific logic from server
- [x] Add registry initialization on startup

## Phase 2: InfoCollectionAgent Skills

### 2.1 Implement GetUserPreferencesSkill
- [x] Create `src/mcp_server/skills/info_collection/get_user_preferences.py`
- [x] Define input schema (preference_type, context)
- [x] Define output schema (preferences dict)
- [x] Implement `execute()` method with mock logic
- [x] Add validation for preference types
- [x] Add test data for destinations, budgets, dates

### 2.2 Implement ValidateUserInputSkill
- [x] Create `src/mcp_server/skills/info_collection/validate_user_input.py`
- [x] Define input schema (input_data, validation_rules)
- [x] Define output schema (is_valid, errors, normalized_data)
- [x] Implement validation logic for dates, budgets, locations
- [x] Add normalization logic (date formats, currencies)
- [x] Add detailed error messages

### 2.3 Implement SuggestDestinationsSkill
- [x] Create `src/mcp_server/skills/info_collection/suggest_destinations.py`
- [x] Define input schema (budget, interests, season, group_size)
- [x] Define output schema (suggestions list with scores)
- [x] Implement suggestion logic based on preferences
- [x] Add ranking/scoring algorithm
- [x] Add mock destination database

### 2.4 Create __init__.py for info_collection
- [x] Export all info_collection skills
- [x] Register skills in SkillRegistry

### 2.5 Add Unit Tests
- [x] Test GetUserPreferencesSkill with various inputs
- [x] Test ValidateUserInputSkill validation rules
- [x] Test SuggestDestinationsSkill ranking logic
- [x] Test error handling for invalid inputs

## Phase 3: SearchAgent Skills

### 3.1 Implement SearchFlightsSkill
- [x] Create `src/mcp_server/skills/search/search_flights.py`
- [x] Define input schema (origin, destination, dates, passengers)
- [x] Define output schema (flights list with details)
- [x] Implement mock flight search logic
- [x] Add mock flight data (airlines, prices, times)
- [x] Add filtering by cabin class, stops

### 3.2 Implement SearchHotelsSkill
- [x] Create `src/mcp_server/skills/search/search_hotels.py`
- [x] Define input schema (destination, dates, guests, stars)
- [x] Define output schema (hotels list with details)
- [x] Implement mock hotel search logic
- [x] Add mock hotel data (names, prices, ratings)
- [x] Add filtering by amenities, location

### 3.3 Implement CompareSearchResultsSkill
- [x] Create `src/mcp_server/skills/search/compare_search_results.py`
- [x] Define input schema (results_list, criteria)
- [x] Define output schema (comparison matrix, recommendation)
- [x] Implement comparison logic (price, rating, location)
- [x] Add scoring algorithm
- [x] Add side-by-side comparison output

### 3.4 Implement FilterByBudgetSkill
- [x] Create `src/mcp_server/skills/search/filter_by_budget.py`
- [x] Define input schema (results, budget, budget_type)
- [x] Define output schema (filtered_results, budget_analysis)
- [x] Implement budget filtering logic
- [x] Add budget breakdown (flights, hotels, activities)
- [x] Add affordability scoring

### 3.5 Create __init__.py for search
- [x] Export all search skills
- [x] Register skills in SkillRegistry

### 3.6 Add Unit Tests
- [x] Test SearchFlightsSkill with various routes
- [x] Test SearchHotelsSkill with various locations
- [x] Test CompareSearchResultsSkill comparison logic
- [x] Test FilterByBudgetSkill budget calculations
- [x] Test error handling for invalid searches

## Phase 4: RecommendationAgent Skills

### 4.1 Implement GetDestinationInfoSkill
- [x] Create `src/mcp_server/skills/recommendation/get_destination_info.py`
- [x] Define input schema (destination, info_type)
- [x] Define output schema (destination details)
- [x] Implement mock destination info retrieval
- [x] Add mock data (history, culture, language, currency)
- [x] Add info type filtering (overview, details, tips)

### 4.2 Implement GetAttractionsSkill
- [x] Create `src/mcp_server/skills/recommendation/get_attractions.py`
- [x] Define input schema (destination, attraction_type, limit)
- [x] Define output schema (attractions list)
- [x] Implement mock attractions retrieval
- [x] Add mock attractions data (landmarks, museums, nature)
- [x] Add filtering by type, popularity, distance

### 4.3 Implement GetWeatherForecastSkill
- [x] Create `src/mcp_server/skills/recommendation/get_weather_forecast.py`
- [x] Define input schema (destination, dates)
- [x] Define output schema (forecast by day)
- [x] Implement mock weather forecast generation
- [x] Add realistic weather patterns by season
- [x] Add packing suggestions based on weather

### 4.4 Implement GetDestinationReviewsSkill
- [x] Create `src/mcp_server/skills/recommendation/get_destination_reviews.py`
- [x] Define input schema (destination, review_type, limit)
- [x] Define output schema (reviews list with ratings)
- [x] Implement mock reviews retrieval
- [x] Add mock review data (user reviews, ratings, tips)
- [x] Add filtering by rating, date, review type

### 4.5 Create __init__.py for recommendation
- [x] Export all recommendation skills
- [x] Register skills in SkillRegistry

### 4.6 Add Unit Tests
- [x] Test GetDestinationInfoSkill for various destinations
- [x] Test GetAttractionsSkill filtering logic
- [x] Test GetWeatherForecastSkill date ranges
- [x] Test GetDestinationReviewsSkill sorting
- [x] Test error handling for unknown destinations

## Phase 5: BookingAgent Skills

### 5.1 Implement CreateBookingSkill
- [x] Create `src/mcp_server/skills/booking/create_booking.py`
- [x] Define input schema (booking_type, booking_details, user_info)
- [x] Define output schema (booking_id, status, details)
- [x] Implement mock booking creation logic
- [x] Add booking ID generation
- [x] Add booking validation

### 5.2 Implement ProcessPaymentSkill
- [x] Create `src/mcp_server/skills/booking/process_payment.py`
- [x] Define input schema (booking_id, payment_method, amount)
- [x] Define output schema (payment_status, transaction_id)
- [x] Implement mock payment processing
- [x] Add payment validation
- [x] Add transaction ID generation

### 5.3 Implement ConfirmBookingSkill
- [x] Create `src/mcp_server/skills/booking/confirm_booking.py`
- [x] Define input schema (booking_id, confirmation_details)
- [x] Define output schema (confirmation_code, details)
- [x] Implement mock booking confirmation
- [x] Add confirmation code generation
- [x] Add confirmation email simulation

### 5.4 Implement GetBookingStatusSkill
- [x] Create `src/mcp_server/skills/booking/get_booking_status.py`
- [x] Define input schema (booking_id or confirmation_code)
- [x] Define output schema (status, details, timeline)
- [x] Implement mock status retrieval
- [x] Add mock booking database
- [x] Add status history tracking

### 5.5 Create __init__.py for booking
- [x] Export all booking skills
- [x] Register skills in SkillRegistry

### 5.6 Add Unit Tests
- [x] Test CreateBookingSkill with various booking types
- [x] Test ProcessPaymentSkill payment validation
- [x] Test ConfirmBookingSkill confirmation generation
- [x] Test GetBookingStatusSkill status tracking
- [x] Test error handling for invalid booking IDs

## Phase 6: Integration & Documentation

### 6.1 Update Agent Classes
- [x] Update InfoCollectionAgent to use new skills
- [x] Update SearchAgent to use new skills
- [x] Update RecommendationAgent to use new skills
- [x] Update BookingAgent to use new skills
- [x] Remove references to old skill structure
- [x] Update agent initialization with SkillRegistry

### 6.2 Update API Endpoints
- [x] Verify `/mcp/skills` returns all 15 skills
- [x] Verify `/mcp/execute/<skill_name>` works for all skills
- [x] Verify `/mcp/batch-execute` works with multiple skills
- [x] Update endpoint documentation
- [x] Add examples for each skill in API docs

### 6.3 Create Skill Documentation
- [x] Create README.md in `src/mcp_server/skills/`
- [x] Document each agent's skills
- [x] Add usage examples for each skill
- [x] Add input/output schema documentation
- [x] Add troubleshooting guide

### 6.4 Update Main README.md
- [x] Update architecture section with new skill structure
- [x] Add agent-skill mapping diagram
- [x] Update API examples
- [x] Add section on skill development guidelines
- [x] Update setup/installation instructions

### 6.5 Add Integration Tests
- [x] Test InfoCollectionAgent workflow with skills
- [x] Test SearchAgent workflow with skills
- [x] Test RecommendationAgent workflow with skills
- [x] Test BookingAgent workflow with skills
- [x] Test complete end-to-end travel planning workflow
- [x] Test skill error propagation to agents

## Phase 7: Cleanup & Finalization

### 7.1 Remove Old Skill Implementation
- [x] Remove `src/mcp_server/skills/destination.py`
- [x] Remove `src/mcp_server/skills/pricing.py`
- [x] Remove `src/mcp_server/skills/reviews.py`
- [x] Remove `src/mcp_server/skills/weather.py`
- [x] Remove `src/mcp_server/skills/planning.py`
- [x] Update imports in remaining files

### 7.2 Remove Deprecated MCP Endpoints
- [x] Remove any old skill-specific endpoints
- [x] Update API routing
- [x] Update endpoint tests

### 7.3 Final Code Review
- [x] Review all new skill implementations
- [x] Check for code duplication
- [x] Verify consistent naming conventions
- [x] Verify all docstrings are complete
- [x] Run linter (ruff) on all new code
- [x] Run formatter (black) on all new code

### 7.4 Final Testing
- [x] Run all unit tests
- [x] Run all integration tests
- [x] Manual testing of API endpoints
- [x] Test error scenarios
- [x] Performance testing (if applicable)

### 7.5 Documentation Review
- [x] Verify all documentation is complete
- [x] Check for broken links
- [x] Verify code examples work
- [x] Update OpenSpec specifications
- [x] Create migration guide

### 7.6 Commit and Prepare for Merge
- [x] Stage all changes
- [x] Commit with descriptive message
- [x] Push to feature branch
- [x] Create pull request
- [x] Update OpenSpec with final delta

## Completion Checklist

Before marking this change as complete:

- [x] All 15 skills implemented and working
- [x] SkillRegistry functional and tested
- [x] All agents updated to use new skills
- [x] All tests passing
- [x] Documentation complete and accurate
- [x] Old code removed
- [x] Code reviewed and approved
- [x] OpenSpec updated with changes
- [x] Migration guide created
- [x] No breaking changes to external APIs

## Notes

### Development Order Rationale
- Phase 1 first to establish foundation
- Phases 2-5 can be parallelized (one per agent)
- Phase 6 requires all skills complete
- Phase 7 is cleanup after everything works

### Testing Strategy
- Unit tests for each skill individually
- Integration tests for agent-skill interaction
- End-to-end tests for complete workflows
- Mock data keeps tests fast and deterministic

### Migration Notes
- New structure coexists with old during Phase 1-5
- Old code removed only after new code is tested
- No breaking changes to external MCP API
- Skill names may change but can be aliased for compatibility
