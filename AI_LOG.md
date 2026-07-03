# AI Collaboration Log

A short, honest "peek behind the curtain" of how this project was built with an AI assistant.

## AI tech stack

- **Cursor** (agent mode) as the coding environment, driving file edits, terminal commands, and git.
- **Claude** as the underlying LLM.

The workflow was plan-first: agree on a plan, then build the backend and frontend on separate branches with small, reviewable commits.

## The prompts that shipped it

These are the actual, paraphrased instructions that produced the core layers.

**Planning:**
> "Read the PDF in this project." → "Let's create the plan of action and mention all the deliverables... make sure we cover the entire assignment and no requirement is left."

This produced [PLAN.md](PLAN.md): FastAPI + PostgreSQL backend, React + Vite frontend, Docker Compose, and the required README/AI_LOG/deployment sketch.

**Backend (generated first):**
> "From the todo list, pick backend first and finish it before the frontend." → "Create separate branches for backend and frontend, push them for me to merge." → "Divide the work into parts so we have multiple commits instead of one giant commit. Keep commit messages crisp, clean, and human."

This generated the FastAPI app: SQLAlchemy `Monitor`/`HealthCheck` models, register/list/delete/history endpoints, the `httpx`-based async checker, and an APScheduler job that pings every URL every 60s (plus an immediate check on registration).

**Frontend:**
> Same branch-and-commit workflow, building the React dashboard against the real API: a table of monitors with up/down badges, response times, relative "last checked" times, an add-URL form, delete, and 10s polling.

## Course corrections

Real blocks we hit and how we resolved them:

1. **Shell assumption (bad command).** The assistant chained commands with `&&`, which the local PowerShell rejected (`The token '&&' is not a valid statement separator`). Fixed by switching to `;`-separated statements for all subsequent commands.

2. **Unwanted commit attribution.** Cursor's IDE integration auto-appended a `Co-authored-by: Cursor <cursoragent@cursor.com>` trailer to commits, which we did not want. We caught it via `git log`, disabled attribution (Cursor Settings > Agent > Attribution), and rewrote the affected (un-pushed) commits with `git filter-branch --msg-filter` to strip the trailer. We also set a repo-local git identity so commits use the correct personal author rather than the machine's global (work) identity.

3. **Compose startup race (broken-architecture fix).** The first `docker-compose.yml` only ordered container *start* (`depends_on`), not readiness. That risks two failures: nginx failing on an unresolved/not-ready `backend` upstream, and a blank dashboard while the API is still booting. We hardened it by adding a backend `/health` healthcheck and gating the frontend on `depends_on: condition: service_healthy`, and the backend already retries the DB connection on startup.

4. **Plan quality push-back.** An initial plan was "checklist-complete" but generic. On review it was pushed to add senior-level touches: classifying *why* a URL is down (timeout vs connection failed vs HTTP error), showing relative check times so "real-time" is visible, and calling out in the deployment sketch that the scheduler must run as a single instance to avoid duplicate pings.
