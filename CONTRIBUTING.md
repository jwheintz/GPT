# Contributing

Thanks for contributing! This document explains how to make contributions smoothly.

Principles
- Keep changes small and focused.
- Add tests for new functionality and bug fixes.
- Update documentation for behavior changes.

Development workflow
1. Fork (if necessary) and clone.
2. Create a branch:
```bash
git checkout -b feat/<short-description>
```
3. Make changes and run tests and linters locally.
4. Commit with a clear message:
```
git commit -m "feat: add X to support Y"
```
5. Push and open a PR targeting `main` (or default branch).

Branch naming
- feat/<short-desc>
- fix/<short-desc>
- docs/<short-desc>
- chore/<short-desc>

Commit message style (recommended)
- Use imperative mood and a type prefix: feat, fix, docs, chore, test, refactor
- Example: `fix: handle nil pointer in preprocess`

Testing
- Add tests next to the code they exercise and ensure they pass:
```bash
npm test
pytest
go test ./...
```

Code review checklist
- Is the scope small and clear?
- Are there tests for new behavior?
- Any security implications? (secrets, injection risks)
- Is documentation updated?
- Is code style consistent?

Pull request template (suggested)
- Title: concise and prefixed with the type (feat/fix/docs)
- Body:
  - Summary of changes
  - Related issue (if any)
  - How to test
  - Screenshots / logs (if relevant)

Maintainers
- Primary contact: @jwheintz

License and CLA
- Ensure your contribution complies with the repository license.