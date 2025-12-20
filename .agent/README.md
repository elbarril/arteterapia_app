# Agent Documentation

This directory contains streamlined documentation for AI agents working on the Arteterapia application.

## Quick Start

**New to the project?**
1. Read [GUIDE.md](GUIDE.md) - Comprehensive development guide
2. Bookmark [REFERENCE.md](REFERENCE.md) - Quick reference for commands and patterns

**Working on specific features?**
- API development → [topics/api.md](topics/api.md)
- Frontend work → [topics/frontend.md](topics/frontend.md)
- Testing → [topics/testing.md](topics/testing.md)

**Common tasks?**
- Setup environment → [workflows/setup-environment.md](workflows/setup-environment.md)
- Modify models → [workflows/modify-models.md](workflows/modify-models.md)
- Reset database → [workflows/reset-database.md](workflows/reset-database.md)

## Documentation Structure

### Core Documentation

**[GUIDE.md](GUIDE.md)** - Comprehensive Development Guide
- Project overview and architecture
- Technology stack and design patterns
- Database models and relationships
- Authentication and security
- Frontend guidelines
- Common workflows

**[REFERENCE.md](REFERENCE.md)** - Quick Reference
- Technology stack summary
- Core models and routes
- Essential commands (setup, database, CLI)
- Security checklist
- Common pitfalls

### Topic-Specific Documentation

**[topics/api.md](topics/api.md)** - API Development
- RESTful API endpoints reference
- JWT authentication details
- Error handling patterns
- Testing and examples

**[topics/frontend.md](topics/frontend.md)** - Frontend Development
- Vanilla JS SPA architecture
- Component patterns
- Security and performance
- Deployment options

**[topics/testing.md](topics/testing.md)** - Testing Guide
- pytest configuration and fixtures
- Test organization and patterns
- Performance optimization
- Coverage and CI/CD

### Workflows

**[workflows/setup-environment.md](workflows/setup-environment.md)**
- Complete environment setup from scratch
- Installing dependencies and initializing database

**[workflows/modify-models.md](workflows/modify-models.md)**
- Safe database model modification
- Creating and applying migrations

**[workflows/reset-database.md](workflows/reset-database.md)**
- Database reset procedure (destructive)
- Sample data creation

## Using Workflows

Workflows can be referenced with slash commands:
- `/setup-environment`
- `/modify-models`
- `/reset-database`

Some workflows include `// turbo` annotations indicating steps safe to auto-run.

## Documentation Reading Strategy

**For agents starting a conversation:**
1. Always read GUIDE.md (sections 1-4 minimum)
2. Always read REFERENCE.md (quick scan)
3. Read topic-specific docs based on request type:
   - Backend/API work → topics/api.md
   - Frontend/UI work → topics/frontend.md
   - Test-related work → topics/testing.md

**For specific tasks:**
- Database changes → workflows/modify-models.md
- Environment issues → workflows/setup-environment.md
- Testing data → workflows/reset-database.md

## Maintenance

**When to update documentation:**
- Major architectural changes
- New models or significant schema changes
- New features or technologies
- Security mechanism updates
- Workflow process changes

**How to update:**
1. Edit relevant file
2. Update date if applicable
3. Ensure cross-references accurate
4. Commit with: `docs: Update [file] - [description]`

## Documentation Standards

**Writing Style:**
- Concise and scannable
- No excessive visual decorations
- Use tables for comparisons
- Code blocks for examples only
- Focus on how-to, not philosophy

**Structure:**
- Clear headers for navigation
- Short lines (max 100 chars when possible)
- Bullet lists for quick scanning
- Consistent formatting across files

---

**Version**: 2.0
**Last Updated**: December 2025
**Project**: Arteterapia - Art Therapy Workshop Management
