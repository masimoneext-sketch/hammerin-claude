# Hammerin'Claude

**Intelligent multi-agent orchestrator for Claude Code — Constructor Method.**

Build software like you build a building: from the ground up, layer by layer, verifying each floor before building the next one.

---

## The Idea

When an AI agent needs to develop a complex feature — database, API, auth, frontend — it faces a critical choice: do everything inline or launch sub-agents in parallel. Both choices have a cost. Going inline on a 600-line task produces messy code. Launching 4 agents on a 20-line task wastes tokens and coordination time.

Hammerin'Claude solves this with a simple insight: **don't choose upfront**. Always start at the lightest level and scale only if the work demands it. Exactly like a construction site that starts with a small crew and calls for reinforcements only when the ground turns out to be harder than expected.

> Named after *Hammerin' Harry* (Irem, 1990) — a construction worker armed with a mallet who builds and fights. Hammerin'Claude does the same: builds software layer by layer, with the tenacity of a worker and the intelligence of an architect.

---

## The Constructor Method

| Layer | Construction | Software |
|-------|-------------|----------|
| 1 — Foundation | Excavation + concrete | DB schema, types, interfaces, contracts |
| 2 — Structure | Load-bearing pillars | API routes, controllers, business logic |
| 3 — Walls | Enclosures + partitions | Frontend HTML/JS, UI components |
| 4 — Systems | Electrical + plumbing | Auth, logging, validation |
| 5 — Finishing | Plaster + paint | Empty states, loading, UX polish |

**Core principle: Opus designs, Sonnet builds.** Never reversed.

- **Opus** (claude-opus-4-6) acts as the architect — reads the codebase, decides strategy, defines contracts between layers with exact function names, endpoints, and DB columns.
- **Sonnet** (claude-sonnet-4-6) acts as the specialized worker — receives precise instructions and implements without deviation.

---

## Architecture

### Auto-trigger

The skill activates automatically across all sessions and projects when the user asks to develop a new feature, add a section, refactor, or any development task requiring planning. No manual invocation needed.

**Does NOT trigger for:** single-file bug fixes, questions, code explanations, pure CSS/UI changes, or deployments.

### Stack-agnostic

Works with any tech stack: React, Node.js, Laravel, Python, React Native, Docker. The layers and verifications are universal — only the specific content of each layer changes.

---

## The 5 Phases

### Phase 1 — Site Survey

Reads the minimum needed to understand the task weight:

1. **Project memory** — known context and conventions
2. **Entrypoint** — overall codebase structure
3. **1 pattern file** — the file most similar to what needs to be created
4. **(adaptive) 1-2 extra files** — only if the first pattern isn't enough

After the first pattern, a **confidence check** evaluates whether the pattern covers the task domain, conventions are clear, and volume estimation is reliable. If not, reads up to 2 additional files (max 3 total). If the codebase remains opaque after 3 files, flags it and starts with "inline + escalation" to reduce estimation risk.

### Phase 2 — Design & Foundation

Foundations are what everything rests on: DB schema, types, interfaces, contracts. If working inline, reads the files to modify and proceeds. If calling the crew, an Opus (Plan) agent designs all layers with exact contracts.

### Phase 3 — Construction

Proceeds layer by layer, bottom to top. Within a layer, independent agents work in parallel. Between layers, verification before ascending.

**Checkpoint after layer 2:** if remaining volume has grown, scale to the crew. If it has shrunk, cancel the crew and finish inline. Zero wasted work — foundations and structure are already done.

### Phase 4 — Inspection

- **Structural verification** — functional tests: server started, endpoints respond, build compiles
- **Systems verification** — auth, logging, validation work correctly
- **Interior verification** — UI visible, empty states, loading states, role-based permissions
- **Regression check** — existing features are not broken

### Phase 5 — Delivery

Report to the user: completed layers, agents used, decisions made during construction, and precise instructions to verify in person.

---

## Dynamic Scaling

The heart of the innovation. Instead of deciding upfront how many agents to use, the skill always starts at the lightest level and scales only if necessary.

| Mode | When | Example |
|------|------|---------|
| **Inline safe** | Pattern replication, few dozen lines | Add 1 field to DB + API + frontend |
| **Inline + escalation** | Uncertain volume, might grow | New section with partially new logic |
| **Direct crew** | Full feature, 3+ domains, new logic | Complete CRUD + auth + import/export |

Transitions can happen at any time. Start inline and discover the frontend is bigger than expected? Scale to the crew — foundations are already done. Start with a crew and Opus shows only 2 small blocks remain? Cancel and finish solo.

**Dynamic scaling is not failure — it's intelligent adaptation.**

---

## Graceful Degradation

The method works best with Opus (design) + Sonnet (build), but must work even when conditions aren't ideal.

| Scenario | Fallback |
|----------|----------|
| **Opus unavailable** | Plan inline in the main thread (already running on Opus) |
| **Sonnet rate-limited** | Reduce parallelism (3→2 agents), wait 60s, retry |
| **Both limited** | Full inline mode — same layers, same verifications, main thread executes |

**Principle:** the Constructor Method is the layered structure with verification, not the presence of sub-agents. Sub-agents are a speed optimization, not a requirement.

---

## Benchmark

Tested on 3 tasks at increasing complexity, comparing results with and without the skill.

| Metric | With skill | Without skill | Delta |
|--------|-----------|---------------|-------|
| Assertion pass rate | **100%** | 67% | **+33%** |
| Avg tokens | **30,241** | 52,894 | **-42%** |
| Avg time | **149.6s** | 202.2s | **-26%** |

The skill uses **fewer tokens** than the baseline while producing **better results**. The adaptive survey avoids reading unnecessary files and dynamic scaling avoids launching unnecessary agents.

---

## Use Cases

- Full-stack features (DB + API + auth + frontend + UX in one coordinated flow)
- Large-scale refactoring across DB, API, and frontend
- Adding sections to existing portals (reads patterns, replicates, verifies)
- Stack migrations (rebuild layer by layer with verification)
- Ambiguous tasks (dynamic scaling discovers complexity during construction)
- Enterprise portals, SaaS platforms, mobile apps with dedicated backends

---

## Installation

The skill is a single `SKILL.md` file. Place it in your Claude Code skills directory:

```
~/.claude/skills/hammerin-claude/SKILL.md
```

It will auto-trigger on all sessions and projects. No configuration needed.

---

## Rules

- **Opus designs, Sonnet builds** — never reverse
- **Read before write** — always, at every layer
- **No file overlap** — never assign the same file to two agents in the same layer
- **Contracts from Opus** — function names, endpoints, types decided by the architect
- **Verify before ascending** — don't build layer N+1 without inspecting layer N
- **Nothing generic** — exact names, not "create an appropriate function"
- **Economic decision** — if agent cost exceeds work cost, go inline
- **Stack-agnostic** — works with any stack

---

*Created by Marco Simone — April 2026*
