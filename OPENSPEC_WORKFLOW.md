# OpenSpec Workflow Guide

> Complete guide for using OpenSpec with cto.new in the lvyou project

## Overview

This document provides step-by-step guidance for creating new features using OpenSpec specifications combined with cto.new AI-assisted development workflow.

## Prerequisites

Before starting, ensure you have:

1. **OpenSpec initialized** in the project root
2. **cto.new access** configured
3. **Understanding of the architecture** from `openspec/project.md`
4. **Relevant service specs** reviewed

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Feature Development Lifecycle                        │
└─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │   PROPOSE   │───►│   DESIGN    │───►│  IMPLEMENT  │───►│   ARCHIVE   │
  │             │    │             │    │             │    │             │
  │ Create      │    │ Technical   │    │ Code with   │    │ Update      │
  │ change      │    │ decisions   │    │ cto.new     │    │ specs       │
  │ proposal    │    │             │    │             │    │             │
  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
         │                   │                   │                   │
         ▼                   ▼                   ▼                   ▼
  openspec/changes/   proposal.md →        Code changes        openspec
  {feature-name}/     design.md           + Spec updates       archive
  proposal.md         tasks.md
```

## Step 1: Create Change Proposal

### 1.1 Initialize Change Folder

```bash
# Create change folder structure
mkdir -p openspec/changes/{feature-name}/specs
cd openspec/changes/{feature-name}
```

### 1.2 Create proposal.md

```markdown
# Proposal: {Feature Name}

## Summary
Brief description of the feature (1-2 sentences)

## Problem Statement
What problem does this solve? Why is it needed?

## Proposed Solution
High-level overview of the approach

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Scope
### In Scope
- What will be implemented

### Out of Scope
- What will NOT be implemented (for now)

## Success Criteria
- [ ] Criteria 1
- [ ] Criteria 2

## Timeline Estimate
- Phase 1: X days
- Phase 2: Y days

## Risks
- Risk 1 and mitigation

## Dependencies
- External dependencies
- Other features/services

## References
- Related tickets
- Documentation links
```

### 1.3 Create design.md

```markdown
# Technical Design: {Feature Name}

## Architecture Overview
Diagram or description of the architecture

## Data Flow
How data moves through the system

## API Contracts

### Frontend → Java Backend

#### New/Modified Endpoints

```http
POST /api/v1/resource
Content-Type: application/json

{
  "field": "value"
}
```

**Response (200 OK)**
```json
{
  "code": 0,
  "data": { ... }
}
```

### Java Backend → Agent

#### New/Modified Agent Calls

```http
POST /agent/endpoint
```

## Data Models

### Database Schema Changes

```sql
-- New tables
CREATE TABLE ...

-- Modified tables
ALTER TABLE ...

-- Indexes
CREATE INDEX ...
```

### API Schemas

```typescript
interface NewType {
  field1: string;
  field2: number;
}
```

## Component Design

### Frontend Components

```
src/components/
├── feature/
│   ├── NewComponent.tsx
│   ├── NewComponent.test.tsx
│   └── index.ts
```

### Backend Services (Java)

```
travel-assistant/{service}/
├── src/main/java/.../
│   ├── controller/
│   ├── service/
│   ├── dto/
│   └── entity/
```

### Agent Skills (Python)

```
travel-assistant-agent/src/
├── skills/
│   └── new_skill.py
└── workflows/
    └── new_workflow.py
```

## Implementation Details

### Key Algorithms
If applicable, describe key algorithms or logic

### Edge Cases
- Edge case 1 and handling
- Edge case 2 and handling

### Error Handling
- Error scenarios and responses

## Security Considerations
- Authentication requirements
- Data validation
- Rate limiting

## Performance Impact
- Expected performance characteristics
- Potential bottlenecks

## Testing Strategy

### Unit Tests
- What to test

### Integration Tests
- How services integrate

### E2E Tests
- User scenarios to test
```

### 1.4 Create tasks.md

```markdown
# Implementation Tasks: {Feature Name}

## Phase 1: Foundation

### Frontend
- [ ] Task 1
- [ ] Task 2

### Backend (Java)
- [ ] Task 3
- [ ] Task 4

### Agent (Python)
- [ ] Task 5

## Phase 2: Integration

### Frontend Integration
- [ ] Task 6
- [ ] Task 7

### Backend Integration  
- [ ] Task 8
- [ ] Task 9

### Testing
- [ ] Task 10
- [ ] Task 11

## Phase 3: Polish

### Bug Fixes
- [ ] Task 12

### Documentation
- [ ] Task 13
- [ ] Task 14
```

### 1.5 Review Proposal

```bash
# Show the complete proposal
openspec show {feature-name}
```

## Step 2: Execute with cto.new

### 2.1 Start cto.new Task

When creating a cto.new task, reference the change:

```
Task: Implement {Feature Name}

Context:
- Change: openspec/changes/{feature-name}
- Specs: openspec/specs/{service}/spec.md

Reference the proposal and design documents before implementation.
```

### 2.2 Implementation Workflow

```bash
# 1. Review relevant specifications
cat openspec/specs/{service}/spec.md

# 2. Check the change design
cat openspec/changes/{feature-name}/design.md

# 3. Start implementation with cto.new
# (cto.new will read AGENTS.md for guidance)

# 4. Mark tasks as complete in tasks.md as you progress
```

### 2.3 Updating Specifications

During implementation, if you discover spec gaps:

1. Update the relevant spec file (`openspec/specs/{service}/spec.md`)
2. Document the change in `openspec/changes/{feature-name}/specs/`
3. Use the delta format:

```markdown
# Spec Delta: {feature-name}

## Added to openspec/specs/frontend/spec.md

```markdown
### New Section
Content added
```

## Modified in openspec/specs/backend-java/spec.md

```markdown
### API Endpoint
- Before: ...
- After: ...
```
```

### 2.4 Validating Changes

```bash
# Validate spec consistency
openspec validate

# Review pending changes
openspec show {feature-name}
```

## Step 3: Complete and Archive

### 3.1 Final Review Checklist

Before archiving, ensure:

- [ ] All tasks completed in `tasks.md`
- [ ] Code reviewed and tested
- [ ] Specifications updated
- [ ] Tests added/updated
- [ ] Documentation updated

### 3.2 Create Spec Delta

Create `openspec/changes/{feature-name}/specs/final-delta.md`:

```markdown
# Final Spec Delta: {Feature Name}

## Summary of Changes

### Frontend (`openspec/specs/frontend/spec.md`)
- Added: New API client methods
- Added: New component patterns

### Backend Java (`openspec/specs/backend-java/spec.md`)
- Added: New REST endpoints
- Added: New DTOs
- Modified: Updated error codes

### Backend Agent (`openspec/specs/backend-agent/spec.md`)
- Added: New MCP skill
- Added: New workflow node

### Integration (`openspec/specs/integration/spec.md`)
- Added: API contract for new endpoints
- Added: Data flow diagram
```

### 3.3 Archive the Change

```bash
# Archive the change (merges specs into main, archives the change)
openspec archive {feature-name}
```

### 3.4 Commit Changes

```bash
# Commit all changes including updated specs
git add .
git commit -m "feat: implement {feature-name}

- Add new frontend components and API integration
- Add Java backend endpoints and services
- Add Agent skill and workflow integration
- Update OpenSpec specifications

Refs: openspec/changes/{feature-name}"
```

## Example: Complete Feature Workflow

### Example: Adding User Preferences Feature

```bash
# 1. Create change folder
mkdir -p openspec/changes/user-preferences/specs

# 2. Create proposal.md
cat > openspec/changes/user-preferences/proposal.md << 'EOF'
# Proposal: User Preferences Feature

## Summary
Add ability for users to save and manage travel preferences.

## Problem Statement
Users currently must re-enter preferences for each travel request.
Saving preferences will improve user experience.

## Requirements
- [ ] User can set default destination preferences
- [ ] User can set budget preferences
- [ ] User can set accommodation preferences
- [ ] Preferences are applied automatically to new requests
EOF

# 3. Create design.md with technical details...

# 4. Create tasks.md with implementation checklist...

# 5. Show proposal
openspec show user-preferences

# 6. Start cto.new task with context
# (In cto.new interface, reference the change)

# 7. Implement with cto, update tasks.md as you go

# 8. Update specifications in openspec/specs/*/spec.md

# 9. Validate
openspec validate

# 10. Archive
openspec archive user-preferences

# 11. Commit
git add .
git commit -m "feat: add user preferences feature"
```

## Best Practices

### Keep Specs Current
- Update specs during implementation, not after
- Use diff format to show what changed

### Small, Incremental Changes
- Create separate changes for separate features
- Makes review and rollback easier

### Link Tickets to Changes
- Reference ticket numbers in proposal and commits
- Helps track the evolution of features

### Review Before Implementation
- Use `openspec show` to visualize the complete plan
- Catch issues early

### Document Decisions
- Record why certain decisions were made
- Helps future maintainers understand the codebase

## Common Patterns

### Pattern: Adding a New API Endpoint

```markdown
# Change: add-user-endpoint
## proposal.md
- Create endpoint to get user profile

## design.md
### API Contract
GET /api/v1/users/{id}

## tasks.md
- [ ] Backend: Add endpoint in UserController
- [ ] Frontend: Add API client method
- [ ] Frontend: Add user profile component
```

### Pattern: Adding a New Agent Skill

```markdown
# Change: add-weather-skill
## proposal.md
- Add weather lookup skill for travel planning

## design.md
### Skill Definition
- Input: destination, date
- Output: weather forecast

## tasks.md
- [ ] Agent: Implement GetWeatherSkill
- [ ] Agent: Register in SkillRegistry
- [ ] Integration: Add to integration spec
```

### Pattern: Database Schema Change

```markdown
# Change: add-user-preferences
## design.md
### Schema
ALTER TABLE users ADD COLUMN preferences JSONB;

## tasks.md
- [ ] Backend: Add entity field
- [ ] Backend: Add migration
- [ ] Frontend: Update types
```

## Troubleshooting

### Issue: Spec Validation Fails

```bash
# Check for syntax errors
openspec validate

# Common issues:
# - Missing required fields
# - Invalid YAML/JSON syntax
# - Circular references
```

### Issue: cto.new Doesn't Understand Specs

```bash
# Ensure AGENTS.md exists
cat openspec/AGENTS.md

# Provide explicit references in task
# "See openspec/specs/backend-java/spec.md section on API Design"
```

### Issue: Change Conflicts with Existing Spec

```bash
# Review existing specs
cat openspec/specs/*/spec.md

# Document the conflict in design.md
# Decide: Update existing spec OR create variant approach
```

## Quick Reference

### Commands

| Command | Description |
|---------|-------------|
| `openspec init` | Initialize OpenSpec in project |
| `openspec show <change>` | Show change details |
| `openspec validate` | Validate spec consistency |
| `openspec archive <change>` | Archive and merge specs |

### File Locations

| File | Location |
|------|----------|
| Project conventions | `openspec/project.md` |
| Frontend specs | `openspec/specs/frontend/spec.md` |
| Java backend specs | `openspec/specs/backend-java/spec.md` |
| Agent specs | `openspec/specs/backend-agent/spec.md` |
| Integration specs | `openspec/specs/integration/spec.md` |
| Agent guidance | `openspec/AGENTS.md` |

### Workflow Checklist

- [ ] Create change folder
- [ ] Write proposal.md
- [ ] Write design.md
- [ ] Write tasks.md
- [ ] Review with `openspec show`
- [ ] Execute with cto.new
- [ ] Update specs as needed
- [ ] Validate with `openspec validate`
- [ ] Archive with `openspec archive`
- [ ] Commit all changes

---

*This guide is maintained as part of the OpenSpec documentation.*
