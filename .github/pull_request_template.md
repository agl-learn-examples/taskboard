## What changed

## Why

## Checklist
- [ ] One idea, small enough to review
- [ ] Commit messages follow Conventional Commits (feat:, fix:, docs: ...)
- [ ] Tests added or updated, and `pytest` passes
- [ ] Lint passes: `ruff check .` in `api/`, `npm run lint` in `web/`
- [ ] README updated if behaviour changed
- [ ] No secrets, tokens or real passwords in the diff
- [ ] AI-assisted? Say which parts, and what you checked yourself (ran it, read every line, tested the edge cases)

## For the reviewer
- [ ] I ran it, or read the tests and they test the change
- [ ] Names and comments say what the code does
- [ ] Errors are handled: what happens with bad input, or when the database is down?
