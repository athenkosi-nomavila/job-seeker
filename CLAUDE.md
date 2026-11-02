# job-seeker: working rules

A personal job application assistant, built in phases (see README roadmap).

## Code standards (from the owner)

- **Clean and readable.** Small functions with clear names. Docstrings say *why*, not just *what*. The owner is using this project to refresh their Python skills, so write code a reader can follow.
- **No redundancy.** One source of truth for each thing:
  - File paths come from `job_seeker.config.Settings`. Never hard-code `data/...` anywhere else.
  - Each CLI command is a `cmd_<name>(args, settings)` handler registered with `set_defaults(handler=...)`. Don't add branches to `main()`.
  - Errors caused by the user's files go in `USER_ERRORS` in `cli.py`, so they're handled in one place.
- **Scalable.** New job sources, matchers and so on plug in behind a common interface instead of adding `if source == ...` branches.
- Accurate type hints on every public function.

## Process

- **Small PRs** that are easy to review: one focused change each, split a phase into several PRs.
- Don't start a phase until its prerequisites (inputs, API keys, decisions) are confirmed with the owner.
- Personal data (CV, profile, database, letters) lives in `data/` and is never committed.
- Respect job sites' terms: only APIs, feeds or pages that allow automated access. Never submit an application without the owner's review.

## Checks

```bash
ruff check . && ruff format --check . && pytest
```
