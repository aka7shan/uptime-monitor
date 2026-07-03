# AI Collaboration Log

## Overview

I built this with Cursor (agent mode), using Claude as the underlying model. The AI did a lot of the actual typing, especially on the frontend, while I set the direction: the plan, the stack, how the work was split into commits, and checking the result. It was a back-and-forth: I'd describe what I wanted, review what came back, and correct course when something was off.

## AI tech stack

- **Cursor** (agent mode) for editing, running commands, and git.
- **Claude** as the underlying LLM.

## How it went

I started by having it read the assignment and draft a plan, then went a few rounds on that plan before any code was written, mostly to make sure it covered every requirement and wasn't just generic. Once the approach was settled (FastAPI + PostgreSQL backend, React + Vite dashboard, Docker Compose, and polling instead of WebSockets to keep the MVP simple), I had it build the backend first on its own branch and then the frontend on another, each split into small commits. Nothing went straight to `main`: every branch was pushed for me to review and merge only once it was working, which kept `main` clean and working the whole way through. Even the later docs and a small UI fix each went through their own branch.

At the end I ran the whole stack myself with `docker compose up --build` and tested the up and down cases before calling it done.

## Prompts

A few of the actual prompts that shaped the work:

- Planning: "Let's first create the plan of action and mention all the deliverables... make sure we cover the entire assignment and no requirement is left."
- Sanity-checking the plan: "Is this plan good? Would a reviewer read this and think I did well?"
- Workflow: "Create separate branches for backend and frontend, push them, I'll merge... divide the work into parts so we have multiple commits instead of one giant commit, and keep the messages crisp and human."
- Before pushing: "Before push, check if everything works, if we're able to compile things."

These produced the FastAPI backend (the models, the register/list/delete/history endpoints, the `httpx` checker, and the APScheduler job that pings every URL every 60s plus an immediate check when a URL is added) and the React dashboard (up/down badges, response times, relative "last checked" times, add/delete, and 10s polling).

## Course corrections

A few things the AI got wrong or missed, and how we sorted them out:

- **Shell syntax:** it kept chaining commands with `&&`, which my PowerShell doesn't accept, so we switched to `;`.
- **Compose startup:** the first `docker-compose.yml` only waited for containers to start, not to be ready, which could leave the dashboard blank or break the nginx proxy on boot. We added a backend healthcheck and made the frontend wait for it.
- **Plan depth:** the first plan was a bit generic, so I asked for more thought-through details, like showing *why* a URL is down (timeout vs connection failed vs HTTP error) and noting the scheduler should run as a single instance in the cloud to avoid duplicate pings.
- **A UI bug I hit while testing:** a "Failed to fetch" message stayed on screen even after the data loaded. It turned out the error wasn't being cleared after a successful refresh, so we fixed that.
