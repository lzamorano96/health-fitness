# Pull Request

## Type of Change

- [ ] `feat` — New feature or capability
- [ ] `fix` — Bug fix
- [ ] `refactor` — Code restructure, no behavior change
- [ ] `docs` — Documentation only
- [ ] `data` — Data file or schema change
- [ ] `ci` — Workflow or tooling change
- [ ] `chore` — Housekeeping (deps, config)

## Summary

<!-- 2-3 sentences: what changed and why. Link to the issue if applicable. -->

Closes #

## Version Bump

<!-- What SemVer component does this warrant? -->
- [ ] PATCH (`0.1.x`)
- [ ] MINOR (`0.x.0`)
- [ ] MAJOR (`x.0.0`)
- [ ] No version bump (docs, chore)

## Checklist

- [ ] Commit messages follow Conventional Commits format
- [ ] `plugin.json` version updated (if warranted)
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] All JSON files remain valid (`python -m json.tool <file>`)
- [ ] Python scripts pass syntax check (`python -m py_compile scripts/*.py`)
- [ ] No secrets, credentials, or absolute paths introduced
- [ ] Error messages are user-facing and do not expose system internals

## Testing

<!-- Describe how you verified this works. -->

## Notes for Reviewer

<!-- Anything non-obvious the reviewer should know. -->
