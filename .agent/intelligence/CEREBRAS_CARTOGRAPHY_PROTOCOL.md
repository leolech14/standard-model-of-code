# Cerebras Cartography Protocol

**Purpose:** Systematic external description of PROJECT_elements using AI-powered spiraling investigation
**Model:** Cerebras llama-3.3-70b (3000 t/s)
**Created:** 2026-02-02

---

## The Spiraling Technique

### Philosophy
Build understanding from the outside in, layer by layer. Each spiral adds detail while maintaining coherence. Complexity is managed by chunking at natural boundaries.

### Spiral Levels

```
SPIRAL 0: ORBIT (What is this thing?)
├── Purpose, identity, value proposition
├── Who built it, why, for whom
└── 1-paragraph summary

SPIRAL 1: ATMOSPHERE (Major subsystems)
├── The Trinity: Particle / Wave / Observer
├── How they relate
└── What each does at 10,000 ft

SPIRAL 2: CONTINENTS (Directory structure)
├── Each major directory's purpose
├── File counts, language breakdown
└── Dependency directions

SPIRAL 3: NATIONS (Key modules)
├── Core files in each subsystem
├── Entry points, pipelines, schemas
└── Data flow patterns

SPIRAL 4: CITIES (Critical implementations)
├── Key classes/functions
├── Algorithms, patterns used
├── Where complexity lives

SPIRAL 5: STREETS (Implementation details)
├── Specific code sections
├── Edge cases, gotchas
└── Technical debt locations
```

### Gap-Filling Protocol

After each spiral:
1. Identify UNKNOWN zones
2. Generate targeted questions
3. Next spiral prioritizes unknowns
4. Mark confidence levels (HIGH/MEDIUM/LOW/UNKNOWN)

### Complexity Management

When a section grows too large:
1. Split into sub-documents
2. Maintain index in parent
3. Cross-reference liberally
4. Never lose the forest for trees

---

## Output Structure

**Location:** `.agent/intelligence/` (alongside existing system descriptions)

```
.agent/intelligence/
├── SYSTEM_OVERVIEW.md          # Spiral 0-1 synthesis (high-level)
├── PARTICLE_MAP.md             # Collider deep dive
├── WAVE_MAP.md                 # AI/Context layer
├── OBSERVER_MAP.md             # Control Room UI
├── SCHEMA_MAP.md               # Data structures
├── THEORY_MAP.md               # Documentation layer
├── GAPS_AND_QUESTIONS.md       # What we don't know
└── ... (existing intel files)
```

**Note:** These files live alongside existing intelligence artifacts like:
- `REPO_INDEX.md` - Repository index
- `SELF_PORTRAIT.md` - System self-description
- `THEORY_SECTION_INDEX.md` - Theory documentation map

---

## Execution Protocol

Each Cerebras call:
1. State the spiral level and focus
2. Provide relevant file contents
3. Ask specific questions
4. Capture output verbatim
5. Synthesize into map document
6. Update gaps list

---

## Quality Criteria

A good cartography entry:
- States what IS, not what SHOULD BE
- Cites specific files/lines
- Acknowledges uncertainty
- Connects to adjacent concepts
- Fits the spiral level (not too detailed, not too vague)
