# Proposal: Refactor Claude Skills to Agent-Centric Architecture

## Summary
Reorganize Claude Skills from functionality-based organization (destination, planning, pricing, reviews, weather) to agent-centric architecture where each skill is clearly owned by and aligned with a specific agent (InfoCollectionAgent, SearchAgent, RecommendationAgent, BookingAgent).

## Problem Statement
The current Claude Skills implementation organizes tools by functionality type, which creates several issues:

1. **Mixed Concerns**: Skills are grouped by what they do (destination, pricing, weather) rather than which agent needs them
2. **Unclear Ownership**: It's not obvious which agent uses which skill without reading the code
3. **Tight Coupling**: Current skills like `CreateTravelPlanSkill` contain logic that spans multiple agent responsibilities
4. **Violation of Single Responsibility**: Individual skills handle multiple concerns that should be separated
5. **Poor Discoverability**: Developers must search through all skill files to understand what each agent can do
6. **Testing Complexity**: Skills are harder to test in isolation due to mixed concerns

## Proposed Solution
Reorganize Skills to align with the four-agent architecture:

### InfoCollectionAgent Skills (3 skills)
Responsible for gathering and validating user preferences:
- `GetUserPreferencesSkill` - Collects destination, dates, budget, group size
- `ValidateUserInputSkill` - Validates and normalizes user input
- `SuggestDestinationsSkill` - Suggests destinations based on preferences

### SearchAgent Skills (4 skills)
Responsible for finding and comparing travel options:
- `SearchFlightsSkill` - Queries flight options
- `SearchHotelsSkill` - Queries hotel options
- `CompareSearchResultsSkill` - Ranks and compares options
- `FilterByBudgetSkill` - Filters results by budget constraints

### RecommendationAgent Skills (4 skills)
Responsible for providing destination insights:
- `GetDestinationInfoSkill` - Destination information and facts
- `GetAttractionsSkill` - Popular attractions and activities
- `GetWeatherForecastSkill` - Weather for travel dates
- `GetDestinationReviewsSkill` - User reviews and ratings

### BookingAgent Skills (4 skills)
Responsible for the booking workflow:
- `CreateBookingSkill` - Creates initial booking
- `ProcessPaymentSkill` - Handles payment processing
- `ConfirmBookingSkill` - Confirms booking and sends confirmation
- `GetBookingStatusSkill` - Checks booking status

**Total**: 15 independent, single-purpose skill modules

## Requirements

### Skill Organization
- [x] Each skill is completely independent with no shared state
- [x] Each skill belongs to exactly one agent type
- [x] Skills follow a consistent interface (BaseSkill)
- [x] Clear naming convention: `{Action}{Resource}Skill`

### Infrastructure
- [x] BaseSkill abstract class with required interface
- [x] SkillRegistry for managing and discovering skills
- [x] JSON Schema validation for inputs and outputs
- [x] Async execution support

### Agent Integration
- [x] Each agent knows which skills it needs
- [x] Agents request skills through the SkillRegistry
- [x] Clear documentation of agent-skill relationships
- [x] MCP Server acts as pure registry/dispatcher

### Testing
- [x] Each skill can be tested independently
- [x] Mock data provided for demo purposes
- [x] Unit tests for each skill module
- [x] Integration tests for agent-skill interaction

## Scope

### In Scope
- Reorganizing existing skill logic into agent-centric modules
- Creating BaseSkill interface and SkillRegistry
- Updating MCP Server to use new skill structure
- Updating agent classes to use new skills
- Creating comprehensive documentation
- Adding unit and integration tests
- Using mock data for demo implementation

### Out of Scope
- Real API integrations (flights, hotels, payments)
- Authentication and authorization for skills
- Skill versioning and migration system
- Dynamic skill loading/hot-reload
- Skill marketplace or third-party skills
- Advanced orchestration patterns (beyond basic agent workflow)

## Success Criteria
- [x] All 15 skills implemented and registered
- [x] Each skill has clear agent ownership
- [x] SkillRegistry can discover and execute all skills
- [x] MCP Server endpoints work with new structure
- [x] Agents can successfully execute their assigned skills
- [x] All existing functionality preserved
- [x] Improved code organization and maintainability
- [x] Clear documentation of skill architecture
- [x] Tests pass for all skills

## Timeline Estimate
- **Phase 1** (Infrastructure): 2 hours
  - BaseSkill class and SkillRegistry implementation
- **Phase 2-5** (Skill Implementation): 6 hours
  - 15 skills organized by agent (4 phases)
- **Phase 6** (Integration): 3 hours
  - Agent integration, API updates, documentation
- **Phase 7** (Cleanup): 1 hour
  - Remove old code, final testing

**Total Estimated Effort**: 12 hours

## Benefits

### Improved Code Organization
- Clear separation of concerns by agent responsibility
- Single Responsibility Principle applied to each skill
- Easier to navigate and understand codebase

### Better Maintainability
- Skills are independent and can be modified without affecting others
- Clear ownership makes it obvious where to add new functionality
- Reduced coupling between components

### Enhanced Testability
- Each skill can be tested in complete isolation
- Mock data is encapsulated within each skill
- Integration tests are clearer with explicit agent-skill relationships

### Foundation for Extensibility
- Easy to add new skills to specific agents
- Skills can be versioned independently
- Third-party skills could be added in the future
- Supports future skill marketplace concept

### Developer Experience
- Clear documentation of what each agent can do
- Intuitive file structure mirrors agent architecture
- Easier onboarding for new developers
- Better IDE navigation with organized structure

## Risks

### Risk 1: Breaking Changes
**Description**: Refactoring existing skills could break current workflows
**Mitigation**: 
- Implement new structure alongside old code first
- Thorough testing before removing old code
- Clear migration documentation

### Risk 2: Increased Number of Files
**Description**: 15 skill modules means more files to manage
**Mitigation**:
- Clear directory structure by agent
- Comprehensive documentation
- SkillRegistry handles discovery automatically

### Risk 3: Over-Engineering
**Description**: Current system works, refactor may add unnecessary complexity
**Mitigation**:
- Keep BaseSkill interface simple
- Focus on clear organization, not complex abstractions
- Document the rationale for the architecture

## Dependencies
- No external dependencies required
- Uses existing MCP server infrastructure
- Compatible with current agent implementation
- Existing Python dependencies (FastAPI, Pydantic) sufficient

## References
- Current implementation: `travel-assistant-agent/src/mcp_server/skills/`
- Current agents: `travel-assistant-agent/src/agents/`
- MCP Protocol: Model Context Protocol for agent-tool communication
- Related spec: `openspec/specs/backend-agent/spec.md`

## Migration Path

### For Developers
1. **Review new skill structure** in `src/mcp_server/skills/`
2. **Update agent code** to use SkillRegistry
3. **Remove deprecated skill imports** after testing
4. **Update tests** to work with new skill interface

### For API Consumers
- **No breaking changes** to external MCP API
- Skill names may change but functionality preserved
- API endpoints remain the same: `/mcp/skills`, `/mcp/execute`

## Future Enhancements
This refactor lays groundwork for:
- Real API integrations (Amadeus, Booking.com, Stripe)
- Skill versioning and compatibility management
- Dynamic skill discovery and loading
- Third-party skill plugins
- Advanced orchestration and skill composition
- Performance monitoring per skill
- Skill A/B testing and analytics
