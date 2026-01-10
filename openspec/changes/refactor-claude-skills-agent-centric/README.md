# Change: Refactor Claude Skills to Agent-Centric Architecture

> OpenSpec change proposal for reorganizing Claude Skills from functionality-based to agent-centric organization

## Status
🟡 **Proposed** - Ready for review and implementation

## Quick Summary
Reorganize Claude Skills from 5 functionality-based modules (destination, pricing, reviews, weather, planning) to 15 agent-centric skills organized by the four-agent architecture (InfoCollectionAgent, SearchAgent, RecommendationAgent, BookingAgent).

## Structure

```
openspec/changes/refactor-claude-skills-agent-centric/
├── README.md              # This file
├── proposal.md            # Why and what we're changing
├── tasks.md               # Implementation checklist (7 phases, 60+ tasks)
├── design.md              # Technical architecture and decisions
└── specs/
    └── backend-agent/
        └── spec.md        # Specification delta (what changes in the spec)
```

## Key Documents

### 📋 [proposal.md](./proposal.md)
- **Problem**: Current skills organized by functionality, unclear ownership
- **Solution**: 15 independent skills organized by agent type
- **Benefits**: Better organization, maintainability, testability, extensibility
- **Timeline**: 12 hours estimated effort

### ✅ [tasks.md](./tasks.md)
- **Phase 1**: Infrastructure (BaseSkill, SkillRegistry)
- **Phase 2-5**: Implement skills for each agent (3-4 skills each)
- **Phase 6**: Integration and documentation
- **Phase 7**: Cleanup and finalization

### 🏗️ [design.md](./design.md)
- **Architecture**: Agent-centric directory structure
- **BaseSkill Interface**: Abstract class with JSON Schema validation
- **SkillRegistry**: Singleton registry for skill discovery and execution
- **MCP Server**: Pure registry/dispatcher pattern
- **Agent Integration**: Registry-based skill access

### 📝 [specs/backend-agent/spec.md](./specs/backend-agent/spec.md)
- **ADDED**: 15 new skills with input/output schemas
- **MODIFIED**: Agent responsibilities and skill mapping
- **MODIFIED**: MCP Server responsibilities
- **REMOVED**: Old functionality-based skill files

## Skill Organization

### InfoCollectionAgent (3 skills)
- `GetUserPreferencesSkill` - Collect travel preferences
- `ValidateUserInputSkill` - Validate and normalize input
- `SuggestDestinationsSkill` - Suggest destinations

### SearchAgent (4 skills)
- `SearchFlightsSkill` - Find flight options
- `SearchHotelsSkill` - Find hotel options
- `CompareSearchResultsSkill` - Compare and rank results
- `FilterByBudgetSkill` - Filter by budget

### RecommendationAgent (4 skills)
- `GetDestinationInfoSkill` - Destination information
- `GetAttractionsSkill` - Popular attractions
- `GetWeatherForecastSkill` - Weather forecast
- `GetDestinationReviewsSkill` - User reviews

### BookingAgent (4 skills)
- `CreateBookingSkill` - Create booking
- `ProcessPaymentSkill` - Process payment
- `ConfirmBookingSkill` - Confirm booking
- `GetBookingStatusSkill` - Check status

## Implementation Highlights

### Before (Functionality-Based)
```python
# Old structure
from src.mcp_server.skills import SearchDestinationSkill

skill = SearchDestinationSkill()
result = await skill.execute(destination="Tokyo")
```

### After (Agent-Centric)
```python
# New structure
from src.mcp_server.skill_registry import SkillRegistry

registry = SkillRegistry()
agent = RecommendationAgent()

result = await agent.call_skill("get_destination_info", destination="Tokyo")
```

## Key Benefits

✅ **Clear Ownership**: Each skill belongs to exactly one agent  
✅ **Single Responsibility**: Each skill does one thing well  
✅ **Better Testing**: Skills can be tested independently  
✅ **Easier Discovery**: Clear what each agent can do  
✅ **Foundation for Growth**: Easy to add new skills  

## Migration Path

1. **Phase 1-5**: New skills implemented alongside old code
2. **Phase 6**: Agents updated to use new skills
3. **Phase 7**: Old skill files removed

**No breaking changes** to external MCP API during migration.

## Next Steps

### For Reviewers
1. Read [proposal.md](./proposal.md) for rationale
2. Review [design.md](./design.md) for technical approach
3. Check [tasks.md](./tasks.md) for implementation plan
4. Review [specs/backend-agent/spec.md](./specs/backend-agent/spec.md) for spec changes

### For Implementers
1. Start with Phase 1 (Infrastructure) in [tasks.md](./tasks.md)
2. Reference [design.md](./design.md) for implementation details
3. Follow code patterns in design examples
4. Mark tasks complete as you progress

### For Approvers
- [ ] Proposal approved
- [ ] Design reviewed
- [ ] Tasks breakdown validated
- [ ] Spec delta approved
- [ ] Ready for implementation

## Related Documents

- **Current Implementation**: `travel-assistant-agent/src/mcp_server/skills/`
- **Agent Spec**: `openspec/specs/backend-agent/spec.md`
- **Agent Implementation**: `travel-assistant-agent/src/agents/`

## Metadata

- **Change ID**: `refactor-claude-skills-agent-centric`
- **Type**: Refactor
- **Scope**: Backend Agent (Python)
- **Breaking Changes**: None (to external API)
- **Estimated Effort**: 12 hours
- **Created**: 2025-01-10
- **Status**: Proposed

---

## Usage with cto.new

When implementing with cto.new, use this context:

```
Task: Implement Claude Skills refactor

Context:
- Change: openspec/changes/refactor-claude-skills-agent-centric/
- Read proposal.md for rationale
- Follow design.md for architecture
- Complete tasks.md in order
- Update specs per specs/backend-agent/spec.md
```

## OpenSpec Commands

```bash
# View this change
openspec show refactor-claude-skills-agent-centric

# Validate specs
openspec validate

# After implementation, archive this change
openspec archive refactor-claude-skills-agent-centric
```
