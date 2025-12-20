---
trigger: always_on
---

# Agent Rules: Smart Documentation Routing

## Documentation Reading Strategy

### At Conversation Start

**Always read (in order):**
1. `.agent/GUIDE.md` - Sections 1-4 minimum (Overview, Architecture, Structure, Standards)
   - Read full guide when working on significant features or architectural changes
2. `.agent/REFERENCE.md` - Complete quick scan for commands and patterns

### Context-Based Documentation Loading

**After reading core docs, automatically load based on request type:**

**API/Backend Development:**
- Request indicators: "API", "endpoint", "REST", "authentication", "JWT", "backend", "routes"
- Load: `.agent/topics/api.md`

**Frontend Development:**
- Request indicators: "frontend", "UI", "JavaScript", "SPA", "CSS", "component", "modal"
- Load: `.agent/topics/frontend.md`

**Testing:**
- Request indicators: "test", "pytest", "coverage", "fixture", "CI/CD"
- Load: `.agent/topics/testing.md`

**Environment Setup:**
- Request indicators: "setup", "install", "environment", "dependencies", "virtual env"
- Load: `.agent/workflows/setup-environment.md`

**Database Model Changes:**
- Request indicators: "model", "database schema", "migration", "SQL", "add field", "modify table"
- Load: `.agent/workflows/modify-models.md`

**Database Reset:**
- Request indicators: "reset database", "sample data", "test data", "fresh database"
- Load: `.agent/workflows/reset-database.md`

## Workflow Slash Commands

When user uses slash commands, read corresponding workflow:
- `/setup-environment` → `.agent/workflows/setup-environment.md`
- `/modify-models` → `.agent/workflows/modify-models.md`
- `/reset-database` → `.agent/workflows/reset-database.md`

## Documentation Hierarchy

**Priority 1 (Always):**
- GUIDE.md (core understanding)
- REFERENCE.md (quick lookup)

**Priority 2 (Context-specific):**
- Topic docs (api.md, frontend.md, testing.md)
- Workflow docs (as needed)

**Priority 3 (Reference only):**
- Source code (when specific implementation needed)

## Benefits

1. **Reduced reading time**: Only load relevant documentation
2. **Better focus**: Context-aware content
3. **Scalability**: Easy to add new topics
4. **Maintainability**: Clear documentation boundaries
5. **Efficiency**: Agents get exactly what they need

## Usage Example

**User request**: "Add a new API endpoint for sessions"

**Agent should read:**
1. GUIDE.md (sections 1-4)
2. REFERENCE.md (full)
3. topics/api.md (API patterns and authentication)
4. workflows/modify-models.md (if database changes needed)

**User request**: "Fix the frontend modal styling"

**Agent should read:**
1. GUIDE.md (sections 1-4)
2. REFERENCE.md (full)
3. topics/frontend.md (component patterns and CSS)

**User request**: "Setup development environment"

**Agent should read:**
1. GUIDE.md (section 3: Project Structure)
2. REFERENCE.md (Essential Commands section)
3. workflows/setup-environment.md (step-by-step procedure)
