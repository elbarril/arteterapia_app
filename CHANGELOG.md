# Changelog

All notable changes to the Arteterapia project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CHANGELOG.md to track all project changes following Keep a Changelog format
- Changelog management section in agent documentation (`.agent/README.md`)
- Changelog update step in development workflows

### Changed
- Updated `.agent/GUIDE.md` to include changelog in critical files and workflows
- Updated `.agent/REFERENCE.md` to include changelog in key files and development workflow
- Updated `.agent/workflows/modify-models.md` to include changelog update step
- Agent documentation now instructs to use changelog instead of creating implementation summaries

## Guidelines for Updating

### When to Add Entries
- After implementing new features
- After fixing bugs
- After making significant changes to existing functionality
- After updating dependencies or configuration
- After refactoring code

### How to Add Entries

1. **Always add to the [Unreleased] section** at the top
2. **Use the appropriate category:**
   - `Added` - New features
   - `Changed` - Changes to existing functionality
   - `Deprecated` - Soon-to-be removed features
   - `Removed` - Removed features
   - `Fixed` - Bug fixes
   - `Security` - Security improvements

3. **Write clear, concise entries:**
   - Start with a verb (Added, Fixed, Updated, etc.)
   - Be specific about what changed
   - Include relevant file paths or component names when helpful
   - Keep it user-focused (what changed, not how)

### Examples

```markdown
### Added
- New observation service for automatic record creation when participants are added
- JWT authentication support for API endpoints
- Frontend modal component for participant management

### Changed
- Updated observation questions structure to include 8 main categories
- Refactored session routes to use service layer pattern

### Fixed
- Resolved datetime UTC compatibility issue in setup_db.py
- Fixed cascade delete behavior for session-observation relationships

### Security
- Implemented token expiration for password reset (24 hours)
- Added CSRF protection to all forms
```

### Version Releases

When creating a release:
1. Change `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`
2. Add a new `[Unreleased]` section above it
3. Update version numbers in relevant files

---

## Version History

<!-- Versions will be added here as releases are made -->
