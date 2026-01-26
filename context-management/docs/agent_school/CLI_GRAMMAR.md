# CLI Grammar for AI Agents

> **Purpose:** Teach AI agents (Claude Code, Gemini, etc.) how to use the `./pe` unified CLI.

## The ./pe Command

`./pe` is the **single entry point** for all PROJECT_elements operations. It eliminates:
- Virtual environment activation
- Path memorization
- Tool discovery overhead

**Location:** Repository root (`/Users/lech/PROJECTS_all/PROJECT_elements/pe`)

## Two Abstraction Layers

### Layer 1: Explicit Commands (Deterministic)

Use these when you know exactly what tool you need.

| Command | Purpose | Speed |
|---------|---------|-------|
| `./pe status` | System health overview | <10ms |
| `./pe ask "question"` | Ask AI (Gemini) a question | 1-3s |
| `./pe research "topic"` | Deep research with cross-validation | 5-15s |
| `./pe collider <args>` | Run Collider analysis | 10-60s |
| `./pe viz` | Start 3D visualization server | <1s |
| `./pe verify` | Run HSL Socratic audit | 5-30s |
| `./pe sync` | Mirror to cloud (GCS) | 5-60s |
| `./pe autopilot <cmd>` | Automation control | <1s |
| `./pe tdj <cmd>` | Temporal index queries | <1s |
| `./pe boot` | Run boot sequence | 1-5s |
| `./pe test` | Run all tests | 10-30s |
| `./pe deck [cmd]` | Decision Deck - certified moves | <10ms |

### Layer 2: Intent Routing (Natural Language)

When uncertain which tool to use, describe what you want. Pattern matching resolves in <10ms.

| Intent Pattern | Routes To |
|----------------|-----------|
| "how is the system doing" | `status` |
| "analyze the codebase" | `collider full` |
| "fix the auth bug" | AI analysis |
| "what files were added today" | `tdj recent` |
| "check for stale code" | `tdj stale` |
| "run tests" | `pytest` |
| "check drift" | `collider symmetry` |
| "verify the docs" | HSL audit |
| "sync to cloud" | archive mirror |
| "show the graph" | 3D visualization |

## When to Use What

### Use Explicit Commands When:
- You know the exact operation needed
- Speed is critical
- Scripting or chaining commands

### Use Intent Routing When:
- Uncertain which tool applies
- Translating user requests
- Exploring capabilities

## Command Reference

### Status & Health

```bash
# Quick health check
./pe status

# Full status with TDJ summary
./pe "how is everything"
```

### Analysis & Exploration

```bash
# Full Collider analysis
./pe collider full . --output .collider

# Symmetry check (doc/code drift)
./pe collider symmetry . --docs docs

# Intent-based
./pe "analyze the code structure"
./pe "check for doc drift"
```

### AI Queries

```bash
# Quick question
./pe ask "what is the purpose of topology_reasoning.py"

# Deep research with validation
./pe research "best practices for code health metrics"

# Intent-based (routes to ask)
./pe "explain how the pipeline works"
./pe "why does the visualizer use Three.js"
```

### Temporal Queries

```bash
# Recent files
./pe tdj recent 7

# Stale files
./pe tdj stale 30

# Summary
./pe tdj summary

# Intent-based
./pe "what files changed this week"
./pe "find unused code"
```

### Automation

```bash
# Autopilot status
./pe autopilot status

# Autopilot operations
./pe autopilot run
./pe autopilot pause
```

### Validation & Sync

```bash
# HSL Socratic audit
./pe verify

# Cloud mirror
./pe sync

# Intent-based
./pe "audit the documentation"
./pe "backup to cloud"
```

### Visualization

```bash
# Start server and open browser
./pe viz

# Intent-based
./pe "show me the code graph"
./pe "visualize the architecture"
```

## Routing Priority

1. **Pattern Matching** (<10ms) - Regex patterns match common intents
2. **Ollama Local LLM** (~100ms) - If installed, classifies unclear intents
3. **AI Fallback** (1-3s) - Routes to Gemini as last resort

## For AI Agent Usage

**Preferred pattern:**

```bash
# Instead of remembering complex paths:
source .tools_venv/bin/activate
python context-management/tools/ai/analyze.py "query" --set brain

# Just use:
./pe ask "query"
```

**Benefits for AI agents:**
- Lower token cost (shorter commands)
- Higher reliability (pre-tested paths)
- Self-documenting (run `./pe` for help)

## Error Handling

All commands return standard exit codes:
- `0` - Success
- `1` - Command failed
- `2` - Invalid arguments

Intent routing that fails to match:
1. Tries pattern matching
2. Falls back to Ollama (if available)
3. Falls back to AI analysis

## Integration with MCP

Future: `./pe` can be exposed as an MCP server for direct tool invocation from Claude Desktop.

```
# Conceptual (not yet implemented)
pe_status() → ./pe status
pe_analyze(path) → ./pe collider full <path>
pe_ask(query) → ./pe ask "<query>"
```

## Decision Deck (Certified Moves)

The Deck provides **constrained action space** for AI agents. Instead of free-form improvisation, agents SELECT from certified moves with preconditions, steps, outcomes, and rollback procedures.

```bash
./pe deck list              # Show all cards
./pe deck deal              # Show available cards (preconditions satisfied)
./pe deck route "intent"    # Route natural language to card
./pe deck show CARD-ANA-001 # Show card details
./pe deck play CARD-ANA-001 # Execute the card (interactive)
./pe deck play CARD-ANA-001 --dry-run  # Preview without executing
./pe deck play CARD-ANA-001 --auto     # Execute without prompts
```

### Card Structure

Each card has:
- **preconditions**: What must be true before executing
- **steps**: Sequence of actions with checkpoints
- **outcomes**: Expected success/failure states
- **rollback**: How to undo if needed
- **cost/risk**: Token estimate and risk level
- **meters**: How success/failure affects focus, reliability, discovery, debt

### Why Two Layers?

| Layer | Purpose | Speed |
|-------|---------|-------|
| Intent Routing (Layer 1) | Fast pattern matching → direct execution | <10ms |
| Decision Deck (Layer 2) | Constrained actions with governance | <10ms |

Per Perplexity validation: "Keep them separate for modularity, scalability, and progressive enforcement."

## Quick Reference Card

```
./pe                    # Help
./pe status             # Health check
./pe ask "..."          # AI query
./pe research "..."     # Deep research
./pe deck list          # Show certified moves
./pe collider full .    # Full analysis
./pe verify             # Audit docs
./pe sync               # Cloud backup
./pe viz                # 3D graph
./pe test               # Run tests
./pe "natural language" # Intent routing
```
