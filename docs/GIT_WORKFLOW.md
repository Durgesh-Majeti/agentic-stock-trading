# Git Workflow Guide

**Version**: 1.1.0  
**Last Updated**: January 2025

---

## Branch Structure

```
main (parent branch - production/stable)
  └── development (child branch - active development)
```

### Branch Roles

- **`main`**: Production/stable branch
  - Contains tested, production-ready code
  - Protected branch (should not be directly committed to)
  - Only updated via merges from `development`
  - Tagged with version numbers for releases

- **`development`**: Active development branch
  - All new features and fixes are developed here
  - Testing and validation happens here
  - After proper testing, changes are merged to `main`

---

## Workflow

### Daily Development

1. **Start working on a feature/fix**:
   ```bash
   git checkout development
   git pull origin development
   ```

2. **Create a feature branch** (optional, for larger features):
   ```bash
   git checkout -b feature/your-feature-name
   # ... make changes ...
   git commit -m "feat: Description of changes"
   git push origin feature/your-feature-name
   ```

3. **Merge feature branch to development** (if you created one):
   ```bash
   git checkout development
   git merge feature/your-feature-name
   git push origin development
   ```

### Testing and Validation

1. **Test your changes on development branch**
2. **Run all tests**: `pytest tests/`
3. **Verify functionality**
4. **Update documentation if needed**

### Releasing to Main (Production)

1. **Ensure development is up to date**:
   ```bash
   git checkout development
   git pull origin development
   ```

2. **Update version number**:
   - Update `docs/11_STATUS_AND_CHANGELOG.md`
   - Update `README.md` (if needed)
   - Create changelog entry

3. **Merge development to main**:
   ```bash
   git checkout main
   git pull origin main
   git merge development -m "Release vX.X.X: Description"
   ```

4. **Create version tag**:
   ```bash
   git tag -a vX.X.X -m "Release vX.X.X: Description"
   git push origin main
   git push origin vX.X.X
   ```

5. **Return to development**:
   ```bash
   git checkout development
   ```

---

## Commit Message Format

Follow conventional commits format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks

Example:
```
feat: Add news sentiment analysis integration

- Implemented News Sentiment Analyst agent
- Added sentiment repository
- Integrated with Strategy Specialist

Version: 1.1.0
```

---

## Branch Protection Rules (Recommended)

Set up on GitHub:

1. **Main branch**:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date
   - Do not allow force pushes

2. **Development branch**:
   - Require status checks to pass
   - Allow force pushes (for development flexibility)

---

## Version Numbering

Follow Semantic Versioning (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Current version: **1.1.0**

---

## Quick Reference

```bash
# Switch to development
git checkout development

# Create feature branch
git checkout -b feature/name

# Commit changes
git add .
git commit -m "feat: Description"

# Push to development
git push origin development

# Merge to main (after testing)
git checkout main
git merge development
git tag -a vX.X.X -m "Release vX.X.X"
git push origin main
git push origin vX.X.X
git checkout development
```

---

## Troubleshooting

### If development gets out of sync with main:

```bash
git checkout development
git fetch origin
git merge origin/main
# Resolve conflicts if any
git push origin development
```

### If you need to update main from development:

```bash
git checkout main
git pull origin main
git merge development
git push origin main
```

---

**Last Updated**: January 2025
