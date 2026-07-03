# AI Collaboration Log

## My approach

I treated the AI as a fast pair-programmer, not an autopilot. I owned the decisions that matter, the architecture, the tech-stack choices, how the work was broken down, the git workflow, and the final verification, and I used the AI to generate the code quickly, especially the frontend, which is outside my day-to-day. Nothing reached `main` without my review and merge.

## AI tech stack

- **Cursor** (agent mode) as my coding environment for edits, terminal commands, and git.
- **Claude** as the underlying LLM I prompted.

## What I drove vs. what I delegated

| I owned (the decisions) | I delegated to the AI (the execution) |
| --- | --- |
| Reading the brief and defining the plan and deliverables | First-pass boilerplate: models, schemas, endpoints, React components |
| Choosing the stack: FastAPI + PostgreSQL, React + Vite | Wiring the `httpx` checks, the APScheduler job, and the nginx proxy |
| Branch-per-feature workflow and small, reviewable commits | Producing each file to my spec |
| Reviewing and merging every PR myself | Drafting the docs (README, this log) |
| Git hygiene: personal identity, no AI attribution | — |
| Running the containerized stack and verifying up/down | — |

## How I directed the build

- **Plan first.** I had the AI read the assignment PDF, then made it write a full plan and challenged whether it was actually good, not just complete. I explicitly asked it to prove the plan would impress a reviewer before I let it write any code.
- **I chose the architecture.** FastAPI + PostgreSQL for a clean async backend, React + Vite for the dashboard, and polling instead of WebSockets to keep the MVP simple. I made the trade-off calls and the AI implemented them.
- **I enforced the workflow.** Separate `backend` and `frontend` branches, work split into several small commits, clean human-sounding commit messages, and each branch pushed for me to review and merge into `main`.
- **I kept authorship clean.** I required my personal git identity on every commit and no work-account data, and I caught and removed the tool's auto-added co-author attribution.
- **I verified it myself.** I ran `docker compose up --build` on my own machine and confirmed both the UP (`https://example.com`) and DOWN (invalid domain) states before calling it done.

## The prompts that shipped it

These are the actual instructions I gave (lightly trimmed).

Planning:
> "Let's first create the plan of action and mention all the deliverables that we will be working on. Make sure we cover the entire assignment and no requirement is left."

Pushing on quality before any code:
> "First, is this plan good? Like, should an interviewer or reviewer read this and think it's good, and think that as a developer I did good?"

Workflow and commit discipline:
> "Let's create separate branches for backend and then frontend. Push to them, I will merge, then we'll get to main, pull latest, and switch to the frontend branch. Make sure the commit messages are not very long, they're crisp and explain cleanly, such that a person wrote it themselves. Divide the work into parts so we have multiple commits instead of one giant commit."

Git hygiene:
> "Make sure you use my personal id for pushing, no [work] data should be pushed." ... "Make sure you don't add co-author Cursor or anything."

Verification gate:
> "Before push, check if everything works, if we are able to compile things."

These drove the FastAPI backend (SQLAlchemy `Monitor`/`HealthCheck` models, register/list/delete/history endpoints, the `httpx` async checker, and the APScheduler job that pings every URL every 60s plus an immediate check on registration) and the React dashboard (up/down badges, response times, relative "last checked" times, add/delete, 10s polling).

## Course corrections I caught and directed

1. **Wrong shell syntax.** The AI chained commands with `&&`, which my PowerShell rejected (`The token '&&' is not a valid statement separator`). I flagged it and had it switch to `;`-separated commands.
2. **Unwanted commit attribution.** I noticed the tool was auto-adding a `Co-authored-by: Cursor` trailer to commits. I stopped the work, made it disable attribution, rewrite the un-pushed commits to strip the trailer, and set a repo-local personal git identity so authorship was correctly mine, not my work account.
3. **Container startup race.** The first `docker-compose.yml` only ordered container *start*, not readiness, which could break nginx's upstream or show a blank dashboard on boot. I had it add a backend `/health` healthcheck and gate the frontend on `depends_on: condition: service_healthy`.
4. **Raising the quality bar.** When the first plan read as generic, I pushed for senior-level details: classifying *why* a URL is down (timeout vs connection-failed vs HTTP error), showing relative check times so "real-time" is visible, and noting the scheduler must run as a single instance in the cloud to avoid duplicate pings.
5. **A UI bug from my own run.** During my verification run, a "Failed to fetch" banner stayed on screen even after the data loaded. I traced it to the error state never being cleared on a successful poll and had it fixed.
