# job-seeker
Having gone through over 100 job applications with limited success. The whole process has become draining and cumbersome, so I've decided to enlist claude to help me out with job applications.

## What it does

job-seeker is a personal assistant for job hunting. It finds jobs, scores them against my CV, and writes a tailored CV and cover letter for each one I pick. It also tracks every application. **I review and submit every application myself.** It never applies on its own, and it only uses job sources that allow automated access.

## Roadmap

Each phase is delivered as small pull requests.

| Phase | What | Command |
|---|---|---|
| 0 | Project skeleton, config, database, CI | `job-seeker init` |
| 1 | Turn my CV into a structured profile (`profile.example.yaml`) | `job-seeker profile` |
| 2 | Fetch jobs (Adzuna, Greenhouse, Lever, Remotive, LinkedIn alert emails) | `job-seeker fetch` |
| 3 | Score jobs against my profile and shortlist them | `job-seeker match` |
| 4 | Tailored CV and cover letter per job, written with Claude | `job-seeker tailor` |
| 5 | Track application status and follow-ups | `job-seeker track` |
| 6 | Pre-fill application forms for me to review and submit | `job-seeker apply` |

## Setup

Requires Python 3.12+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

cp config.example.yaml config.yaml   # edit roles, locations, sources
cp .env.example .env                 # add API keys when a phase needs them
mkdir -p data && cp profile.example.yaml data/profile.yaml  # fill in from your CV
job-seeker profile                   # check it and print a summary
job-seeker init                      # creates data/job_seeker.db
```

Personal files (CV, database, generated letters) go in `data/`. That folder, `config.yaml` and `.env` are gitignored, so they never get committed.

## Development

```bash
ruff check .
pytest
```
