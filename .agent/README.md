# Agent Documentation

This directory contains comprehensive documentation for AI agents working on the Arteterapia application.

## Contents

### Main Documentation
- **[AGENT_GUIDELINES.md](AGENT_GUIDELINES.md)** - Comprehensive guide covering architecture, development standards, and best practices. **READ THIS FIRST** before starting any work.

### Workflows Directory
The `workflows/` directory contains step-by-step guides for common development tasks:

- **[setup-environment.md](workflows/setup-environment.md)** - Setup development environment from scratch
- **[modify-models.md](workflows/modify-models.md)** - Add or modify database models safely
- **[update-translations.md](workflows/update-translations.md)** - Update i18n translations
- **[reset-database.md](workflows/reset-database.md)** - Reset database for testing (⚠️ destructive)

## Quick Start for Agents

1. **Read** `AGENT_GUIDELINES.md` in full
2. **Review** the project structure section
3. **Check** relevant workflows for the task at hand
4. **Verify** understanding of:
   - Authentication system
   - Database models and relationships
   - Frontend design principles

## Using Workflows

Workflows are referenced with slash commands:
- `/setup-environment` - Setup workflow
- `/modify-models` - Model modification workflow
- `/reset-database` - Database reset workflow

Some workflows include `// turbo` annotations, which indicate that steps can be auto-run without user approval (when safe).

## Purpose

This documentation ensures that:
- Agents have complete context about the project
- Development follows established patterns and standards
- Common tasks have documented, repeatable procedures
- New agents can onboard quickly and effectively
- Code quality and consistency are maintained

## Maintenance

Keep documentation updated when:
- Architecture changes significantly
- New workflows are established
- Development standards evolve
- Critical bugs or edge cases are discovered

---

**Last Updated:** December 2025  
**Project:** Arteterapia - Art Therapy Workshop Management Application
