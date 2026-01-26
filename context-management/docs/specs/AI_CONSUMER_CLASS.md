# AI CONSUMER CLASS
# The Third Consumer in Software Engineering

> **Status:** CANONIZED (2026-01-25)
> **Validated:** Gemini 3 Pro (9/10 - "Genuine paradigm shift")
> **Theory Integration:** Axiom Group H in THEORY_AXIOMS.md

---

## Abstract

Software engineering has historically recognized two consumer classes: **End Users** and **Developers**. We identify a third class that emerged circa 2023: **AI Agents**.

This document formalizes the implications of AI Agents as primary consumers of software artifacts, APIs, and documentation.

**Key Claim:** Tools should be optimized for AI consumption. AI will mediate for humans.

---

## 1. THE THREE CONSUMER CLASSES

### 1.1 Historical View (Pre-2023)

```
SOFTWARE CONSUMERS:
  1. END_USER   - Humans using the software product
  2. DEVELOPER  - Humans building/maintaining the software
```

### 1.2 Current Reality (2023+)

```
SOFTWARE CONSUMERS:
  1. END_USER   - Humans using the software product
  2. DEVELOPER  - Humans building/maintaining the software
  3. AI_AGENT   - Non-human entities consuming/operating software
        │
        └── NEW CLASS: Not in traditional SE literature
```

### 1.3 Consumer Characteristics

| Consumer | Interface | Needs | Optimizes For |
|----------|-----------|-------|---------------|
| **END_USER** | GUI, voice | Usability, aesthetics | Experience |
| **DEVELOPER** | Code, CLI, docs | Clarity, maintainability | Productivity |
| **AI_AGENT** | Structured data, schemas | Parseability, predictability | Accuracy |

---

## 2. THE STONE TOOL ANALOGY

### 2.1 Historical Tool Evolution

| Era | Tool-User Interface | Tool Optimized For |
|-----|---------------------|-------------------|
| Stone Age | Human hand → Stone | Human grip |
| Bronze Age | Human hand → Metal | Human grip (improved) |
| Industrial | Human hand → Lever/Wheel | Human operation |
| Digital | Human finger → GUI | Human perception |
| **AI Age** | Human voice → AI → Tool | **AI parsing** |

### 2.2 The Discontinuity

The AI Age represents a **discontinuity**: Tools are being designed that humans CANNOT directly use.

```
STONE TOOL ERGONOMICS:
  - Shaped to fit human palm
  - Balanced for human swing
  - Sized for human strength

AI-AGE TOOL ERGONOMICS:
  - Structured for machine parsing (JSON, YAML)
  - Typed for validation (schemas)
  - Predictable for reasoning (consistent APIs)
```

### 2.3 The Stone Tool Test

> "Can a human use this tool directly, without AI mediation?"

| Tool | Human-Usable? | Designed For |
|------|---------------|--------------|
| Stone axe | ✓ Yes | Human hand |
| CLI with --help | ✓ Yes | Human developer |
| REST API + docs | ⚠️ Painful | Human developer |
| POM YAML output | ✗ No | AI agent |
| unified_analysis.json | ✗ No | AI agent |

When the answer is "No" - you've crossed into AI-native tooling.

---

## 3. THE MEDIATION PATTERN

### 3.1 Traditional Flow

```
Human ───► Tool ───► Output ───► Human reads output
```

### 3.2 AI-Mediated Flow

```
Human ───► AI ───► Tool ───► Output ───► AI ───► Human
               │                          │
               └────── machine layer ─────┘
```

### 3.3 Implications

| Component | Traditional Design | AI-Mediated Design |
|-----------|-------------------|-------------------|
| Tool output | Human-readable | Machine-parseable |
| Error messages | "Something went wrong" | `{"code": "E001", "detail": "..."}` |
| Documentation | Prose tutorials | Schemas + examples |
| API responses | Formatted for display | Structured for processing |

---

## 4. THE UNIVERSAL CONSUMER

### 4.1 Consumption Matrix

```
                    CONSUMES
                    ─────────────────────────────────
                    Code    Docs    Tools   Output
                    (L₀)    (L₁)    (L₂)
CONSUMER  ─────────────────────────────────────────
END_USER            ✗       ✗       ✗       ✓ (UI only)
DEVELOPER           ✓       ✓       ✓       ✓
AI_AGENT            ✓       ✓       ✓       ✓ (ALL)
```

### 4.2 Universal Consumer Property

```
AI_AGENT ∈ Consumer(L₀) ∩ Consumer(L₁) ∩ Consumer(L₂)

AI Agents consume ALL Tarski levels.
They are the UNIVERSAL consumer.
```

### 4.3 Design Implication

Since AI_AGENT consumes everything, and AI_AGENT can mediate for humans:

> **Optimize for AI_AGENT. AI will translate for humans.**

---

## 5. THE AMNESIAC STATE

### 5.1 Traditional Developer Problem

```
DEVELOPER knows:     CODOME (wrote it)
DEVELOPER forgets:   CONTEXTOME (didn't document)

Result: ORPHAN code (code without docs)
```

### 5.2 AI-Assisted Non-Programmer Problem

```
NON-PROGRAMMER knows:     CONTEXTOME (their intent, what they asked)
NON-PROGRAMMER forgets:   CODOME (what was actually created)

Result: AMNESIAC state (intent without structural knowledge)
```

### 5.3 The Symmetry Inversion

| Consumer Type | Knows | Lacks | Failure Mode |
|---------------|-------|-------|--------------|
| Traditional Developer | Structure (CODOME) | Purpose (CONTEXTOME) | ORPHAN |
| AI-Assisted Non-Dev | Purpose (CONTEXTOME) | Structure (CODOME) | AMNESIAC |

### 5.4 AMNESIAC Definition

```
AMNESIAC STATE:
  - Code exists (CODOME populated)
  - Intent was expressed (session logs exist)
  - Human has NO STRUCTURAL MEMORY of what was built

  Human remembers: "I asked for user authentication"
  Human doesn't know: auth.py, UserModel, validate_token() exist
```

### 5.5 Solution: Structural Orientation

Tools like POM should provide "What exists in your project" summaries:

```
SESSION SUMMARY:
  You asked for: "Add user authentication"

  Created entities:
    - auth.py (module)
      - UserModel (class)
      - validate_token() (function)
      - hash_password() (function)
    - templates/login.html (template)
    - migrations/001_users.sql (schema)
```

---

## 6. TARSKI HIERARCHY INTEGRATION

### 6.1 Consumer-Level Mapping

```
TARSKI LEVEL          PRIMARY CONSUMER
─────────────────────────────────────────────────
L₃  Foundations       DEVELOPER (theory authors)
L₂  Theory/Tools      AI_AGENT (operates tools)
L₁  Meta (Docs)       HUMAN + AI_AGENT (shared)
L₀  Object (Code)     AI_AGENT (primary), DEVELOPER (secondary)
```

### 6.2 The Human's Natural Level

Humans naturally operate at L₁ (natural language, documentation, intent).

AI bridges L₁ ↔ L₀ and L₁ ↔ L₂.

```
HUMAN ─── L₁ (natural language) ───► AI ───► L₀, L₂
                                         │
                                         └── AI operates lower/higher levels
```

---

## 7. DESIGN PRINCIPLES

### 7.1 For Tool Builders

```
PRINCIPLE 1: Structure Over Pretty
  Output JSON/YAML, not formatted text

PRINCIPLE 2: Schema Over Docs
  Provide JSON Schema, OpenAPI specs
  AI learns from structure, not prose

PRINCIPLE 3: Examples Over Explanations
  Include input/output examples
  AI learns from examples

PRINCIPLE 4: Codes Over Messages
  Error codes + details, not just messages
  AI can branch on codes

PRINCIPLE 5: Predictability Over Flexibility
  Consistent response shapes
  AI expects patterns
```

### 7.2 For API Designers

```python
# OLD: Human-centric
def get_user(id):
    user = db.find(id)
    if not user:
        print("User not found!")
        return None
    return user

# NEW: AI-agent-aware
def get_user(id: int) -> Result[User, Error]:
    """
    Get user by ID.

    Returns:
        Ok(User) or Err(Error) with code and detail

    Example:
        >>> get_user(42)
        Ok(User(id=42, name="Alice"))
        >>> get_user(-1)
        Err(Error(code="INVALID_ID", detail="ID must be positive"))
    """
    # Typed, structured, predictable
```

---

## 8. THE PARADIGM SHIFT

### 8.1 Before (Human-Centric SE)

```
Software Engineering = Writing code for computers to execute
Senior Engineer = Best at writing complex functions
Output = Source code files
```

### 8.2 After (Agent-Centric SE)

```
Software Engineering = Writing CONTEXT for agents to consume
Senior Engineer = Best at CONTEXT ENGINEERING (curating truth)
Output = Query profiles, truth datasets, schemas
```

### 8.3 Gemini's Summary

> "We are no longer writing code for computers to execute. We are writing **Context** for Agents to consume, so *they* can write code for computers to execute."

---

## 9. CONNECTION TO SMoC

### 9.1 CODOME / CONTEXTOME

- **CODOME**: Optimized for AI_AGENT execution
- **CONTEXTOME**: Shared interface for HUMAN and AI_AGENT

### 9.2 Observability Triad

All three observers output AI-consumable formats:
- POM → YAML
- observability.py → JSON
- observe_session.py → JSONL

### 9.3 Lawvere Applies to AI Too

AI Agents cannot derive meaning from syntax alone (same Lawvere limit).
AI_AGENT needs CONTEXTOME just like humans do.

---

## 10. VALIDATION

### 10.1 Gemini 3 Pro Analysis (2026-01-25)

| Aspect | Score | Notes |
|--------|-------|-------|
| Novelty | HIGH | "Genuine paradigm shift" |
| Theoretical grounding | STRONG | Connects to Constructal Law, Category Theory |
| Operational implications | SIGNIFICANT | Three mandates identified |
| Overall | **9/10** | |

### 10.2 Supporting Literature

| Source | Relevance |
|--------|-----------|
| Constructal Law (Bejan) | Code evolves for flow optimization |
| Category Theory | Mathematical basis for transformations |
| Popper's Three Worlds | Maps to Physical/Virtual/Semantic planes |

### 10.3 Tensions Identified

| Existing Paradigm | Tension |
|-------------------|---------|
| "Code is Law" (Lessig) | Requires static, auditable code |
| Traditional DevOps | Assumes static artifacts |
| Human-centered design | Assumes human is end consumer |

---

## CHANGELOG

| Date | Change |
|------|--------|
| 2026-01-25 | Initial canonization, Gemini validation |

---

*"The senior engineer's job is becoming: NOT write functions, BUT write Query Profiles and Truth Datasets."*
