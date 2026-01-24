# PURPOSE_ONTOLOGY: Visual Guide

> ASCII diagrams illustrating the ACTION vs WORD principle from the Purpose Ontology framework.

**Parent Document:** `PURPOSE_ONTOLOGY.md`

---

## The Core Distinction

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   WORD   = Content/syntax of code    = What it SAYS                │
│   ACTION = Position/relationships    = What it DOES                │
│                                                                     │
│   ┌───────────────────┐         ┌───────────────────┐              │
│   │                   │         │                   │              │
│   │   def foo():      │         │      ┌───┐        │              │
│   │     x = 1         │         │   ┌──│ A │──┐     │              │
│   │     return x * 2  │         │   │  └───┘  │     │              │
│   │                   │         │   ▼         ▼     │              │
│   │   (the text)      │         │ ┌───┐     ┌───┐   │              │
│   │                   │         │ │ B │     │ C │   │              │
│   └───────────────────┘         │ └───┘     └───┘   │              │
│         WORD                    │   (the graph)     │              │
│                                 └───────────────────┘              │
│                                       ACTION                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## WORD Approach (Novice)

```
┌─────────────────────────────────────────────────────────────────────┐
│ THE WORD APPROACH (Novice)                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   def calculate_rate(value, multiplier):                            │
│       return value * multiplier * 0.05                              │
│                                                                     │
│   Developer thinks: "It multiplies things... by 0.05... why?"       │
│                     "What is this for???"                           │
│                     "Who wrote this? What were they thinking?"      │
│                                                                     │
│   Result: CONFUSION. No context. No understanding.                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## ACTION Approach (Expert)

```
┌─────────────────────────────────────────────────────────────────────┐
│ THE ACTION APPROACH (Expert)                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   WHO CALLS calculate_rate()?                                       │
│                                                                     │
│   ┌──────────────────────────┐                                      │
│   │ calculate_loan_interest()│──────┐                               │
│   └──────────────────────────┘      │                               │
│                                     ▼                               │
│                              ┌─────────────────┐                    │
│                              │ calculate_rate()│                    │
│                              └─────────────────┘                    │
│                                     ▲                               │
│   ┌──────────────────────────┐      │                               │
│   │calculate_forex_fee()     │──────┘                               │
│   └──────────────────────────┘                                      │
│                                                                     │
│   Developer thinks: "Ah! Called by loan_interest and forex_fee!"   │
│                     "It's for FINANCIAL CALCULATIONS!"              │
│                     "The 0.05 must be a 5% rate constant!"          │
│                                                                     │
│   Result: UNDERSTANDING. Context reveals purpose.                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The Firth Principle

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  "You shall know a word by the company it keeps"                    │
│                                        — J.R. Firth, 1957           │
│                                                                     │
│  "You shall know a function by the functions it keeps"              │
│                                        — Standard Model of Code     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Cross-Domain Analogies

```
┌──────────────────┬──────────────────────────────────────────────────┐
│     DOMAIN       │              PRINCIPLE                           │
├──────────────────┼──────────────────────────────────────────────────┤
│                  │                                                  │
│   PHYSICS        │  Know a particle by its INTERACTIONS             │
│                  │                                                  │
│                  │       ?                                          │
│                  │      ╱│╲        We detect particles by           │
│                  │     ╱ │ ╲       how they interact with           │
│                  │    ╱  │  ╲      other particles, not by          │
│                  │   ●───┼───●     looking at them directly.        │
│                  │       │                                          │
│                  │       ▼                                          │
│                  │                                                  │
├──────────────────┼──────────────────────────────────────────────────┤
│                  │                                                  │
│   LINGUISTICS    │  Meaning emerges from CONTEXT                    │
│                  │                                                  │
│                  │  "bank" = ??? (river bank? money bank?)          │
│                  │                                                  │
│                  │  "I deposited money in the bank"  → FINANCIAL    │
│                  │  "I sat on the river bank"        → GEOGRAPHICAL │
│                  │                                                  │
│                  │  The WORD is the same. The CONTEXT differs.      │
│                  │                                                  │
├──────────────────┼──────────────────────────────────────────────────┤
│                  │                                                  │
│   NEUROSCIENCE   │  Neurons defined by CONNECTIONS                  │
│                  │                                                  │
│                  │      ●───●───●                                   │
│                  │     ╱│╲  │  ╱│╲    A neuron's function is       │
│                  │    ● │ ● │ ● │ ●   determined by WHAT it        │
│                  │      │   │   │     connects to, not its         │
│                  │      ●───●───●     internal structure alone.    │
│                  │                                                  │
├──────────────────┼──────────────────────────────────────────────────┤
│                  │                                                  │
│   SOFTWARE       │  Functions defined by RELATIONSHIPS              │
│                  │                                                  │
│                  │  ┌─────┐    ┌─────┐    ┌─────┐                   │
│                  │  │ API │───▶│Logic│───▶│ DB  │                   │
│                  │  └─────┘    └─────┘    └─────┘                   │
│                  │                                                  │
│                  │  Position in the flow = Purpose in the system    │
│                  │                                                  │
└──────────────────┴──────────────────────────────────────────────────┘
```

---

## Novice vs Expert Comprehension

### Novice: Bottom-Up (WORD)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NOVICE: BOTTOM-UP (WORD)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    File: user_service.py                                            │
│    ┌──────────────────────────────────────────────────────────┐     │
│    │  Line 1:  class UserService:              "OK a class"   │     │
│    │  Line 2:      def __init__(self):         "constructor"  │     │
│    │  Line 3:          self.db = Database()    "has a db"     │     │
│    │  Line 4:                                                 │     │
│    │  Line 5:      def get_user(self, id):     "gets user"    │     │
│    │  Line 6:          return self.db.find(id) "from db"      │     │
│    │  Line 7:                                                 │     │
│    │  Line 8:      def validate(self, user):   "validates"    │     │
│    │  ... 500 more lines ...                   "oh no..."     │     │
│    └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│    Process: Read line by line, build mental model incrementally     │
│    Problem: Slow, exhausting, loses the forest for the trees        │
│    Scales:  POORLY (what about the other 10,000 files?)             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Expert: Top-Down (ACTION)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EXPERT: TOP-DOWN (ACTION)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    Step 1: "Show me the entry points"                               │
│                                                                     │
│            ┌─────────────────┐                                      │
│            │   main.py       │                                      │
│            │   routes.py     │  ← "Ah, it's a web app"              │
│            │   cli.py        │                                      │
│            └─────────────────┘                                      │
│                                                                     │
│    Step 2: "Show me who calls UserService"                          │
│                                                                     │
│            ┌────────────┐     ┌─────────────┐                       │
│            │ routes.py  │────▶│ UserService │                       │
│            └────────────┘     └─────────────┘                       │
│                  │                   │                              │
│                  │                   ▼                              │
│                  │            ┌─────────────┐                       │
│                  │            │  Database   │                       │
│                  │            └─────────────┘                       │
│                  │                                                  │
│                  └── "UserService sits between API and DB"          │
│                      "It's the business logic layer!"               │
│                                                                     │
│    Step 3: Only NOW read the specific function I need               │
│                                                                     │
│    Process: Map first, read only what's needed                      │
│    Benefit: Fast, efficient, maintains big picture                  │
│    Scales:  WELL (works on million-line codebases)                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ATOM vs ROLE in Standard Model

```
┌─────────────────────────────────────────────────────────────────────┐
│           STANDARD MODEL OF CODE: ATOM vs ROLE                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    ┌──────────────────────────────────────────────────────────┐     │
│    │                                                          │     │
│    │   ATOM (Entity Type)              ROLE (Relationship)    │     │
│    │   ═══════════════════            ═══════════════════     │     │
│    │                                                          │     │
│    │   • Function                      • Controller           │     │
│    │   • Class                         • Service              │     │
│    │   • Variable                      • Repository           │     │
│    │   • Module                        • Utility              │     │
│    │                                   • Factory              │     │
│    │         ↓                               ↓                │     │
│    │                                                          │     │
│    │      WORD                            ACTION              │     │
│    │   (what it IS)                    (what it DOES)         │     │
│    │                                                          │     │
│    └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│    INSIGHT: A Function (ATOM) can be a Controller OR a Utility      │
│             depending on its ROLE in the system.                    │
│                                                                     │
│             Purpose is determined by ROLE, not by ATOM type.        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Same ATOM, Different ROLES

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Same ATOM type (Function), different ROLES:                    │
│                                                                 │
│  ┌──────────────┐        ┌──────────────┐                       │
│  │ handleLogin()│        │  formatDate()│                       │
│  │              │        │              │                       │
│  │ ATOM:Function│        │ ATOM:Function│                       │
│  │ ROLE:Control │        │ ROLE:Utility │                       │
│  │              │        │              │                       │
│  │ Called by: 1 │        │ Called by:47 │                       │
│  │ Calls: 12    │        │ Calls: 0     │                       │
│  └──────────────┘        └──────────────┘                       │
│        │                        │                               │
│        ▼                        ▼                               │
│   ORCHESTRATES            SERVES MANY                           │
│   (high out-degree)       (high in-degree)                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## The Mathematical Formulation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE MATHEMATICAL FORMULATION                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    GRAPH G = (V, E)                                                 │
│                                                                     │
│    V = Nodes = Atoms (functions, classes, modules)                  │
│    E = Edges = Actions (calls, contains, depends-on)                │
│                                                                     │
│    ┌─────────────────────────────────────────────────────────┐      │
│    │                                                         │      │
│    │              PURPOSE = f(edges)                         │      │
│    │                                                         │      │
│    │              NOT                                        │      │
│    │                                                         │      │
│    │              PURPOSE = f(node_content)                  │      │
│    │                                                         │      │
│    └─────────────────────────────────────────────────────────┘      │
│                                                                     │
│    PURPOSE IS A FUNCTION OF RELATIONSHIPS, NOT CONTENT              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Graph Metrics That Reveal Purpose

### High In-Degree: Utility Function

```
┌─────────────────────────────────────────────────────────────┐
│  HIGH IN-DEGREE → UTILITY FUNCTION                          │
│                                                             │
│       ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐                    │
│       │ A │  │ B │  │ C │  │ D │  │ E │                    │
│       └─┬─┘  └─┬─┘  └─┬─┘  └─┬─┘  └─┬─┘                    │
│         │      │      │      │      │                      │
│         └──────┴──────┼──────┴──────┘                      │
│                       ▼                                     │
│                   ┌───────┐                                 │
│                   │ log() │  ← Called by EVERYONE           │
│                   └───────┘    = UTILITY                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### High Out-Degree: Orchestrator

```
┌─────────────────────────────────────────────────────────────┐
│  HIGH OUT-DEGREE → ORCHESTRATOR/CONTROLLER                  │
│                                                             │
│                   ┌───────────┐                             │
│                   │ handleReq │  ← Calls MANY others        │
│                   └─────┬─────┘    = ORCHESTRATOR           │
│         ┌───────┬───────┼───────┬───────┐                  │
│         ▼       ▼       ▼       ▼       ▼                  │
│       ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐               │
│       │ A │   │ B │   │ C │   │ D │   │ E │               │
│       └───┘   └───┘   └───┘   └───┘   └───┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Clustering: Cohesive Modules

```
┌─────────────────────────────────────────────────────────────┐
│  CLUSTERING → COHESIVE MODULE WITH SHARED PURPOSE           │
│                                                             │
│    ┌─────────────────────┐   ┌─────────────────────┐       │
│    │  AUTH CLUSTER       │   │  PAYMENT CLUSTER    │       │
│    │  ┌───┐     ┌───┐    │   │   ┌───┐    ┌───┐    │       │
│    │  │ A │◄───▶│ B │    │   │   │ X │◄──▶│ Y │    │       │
│    │  └─┬─┘     └─┬─┘    │   │   └─┬─┘    └─┬─┘    │       │
│    │    │    ┌────┘      │   │     │   ┌───┘      │       │
│    │    ▼    ▼           │   │     ▼   ▼          │       │
│    │  ┌───────┐          │   │   ┌───────┐        │       │
│    │  │   C   │          │   │   │   Z   │        │       │
│    │  └───────┘          │   │   └───────┘        │       │
│    │                     │   │                    │       │
│    │ Purpose: Security   │   │ Purpose: Billing   │       │
│    └─────────────────────┘   └─────────────────────┘       │
│              ▲                         ▲                    │
│              │    SPARSE CONNECTIONS   │                    │
│              └─────────────────────────┘                    │
│           (clusters identified by dense internal            │
│            connections, sparse external connections)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Centrality: Critical Infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│  CENTRALITY → ARCHITECTURALLY SIGNIFICANT                   │
│                                                             │
│         ┌───┐         ┌───┐                                 │
│         │ A │─────────│ B │                                 │
│         └─┬─┘         └─┬─┘                                 │
│           │             │                                   │
│           └──────┬──────┘                                   │
│                  ▼                                           │
│              ┌───────┐                                       │
│              │ CORE  │  ← High betweenness centrality       │
│              └───┬───┘    = Critical infrastructure         │
│                  │                                           │
│           ┌──────┴──────┐                                   │
│           ▼             ▼                                   │
│         ┌───┐         ┌───┐                                 │
│         │ C │         │ D │                                 │
│         └───┘         └───┘                                 │
│                                                             │
│   (Remove CORE and the graph splits = critical node)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## When WORD Trumps ACTION

### 1. Algorithmic Kernels

```
┌────────────────────────────────────────────────────────────┐
│ ALGORITHMIC KERNELS                                        │
│                                                            │
│    The purpose of quickSort() IS its implementation.       │
│                                                            │
│    ACTION view:   list = quickSort(list)                   │
│                   "It sorts... somehow"                    │
│                                                            │
│    WORD view:     def quickSort(arr):                      │
│                       if len(arr) <= 1: return arr         │
│                       pivot = arr[len(arr)//2]             │
│                       left = [x for x in arr if x < pivot] │
│                       ...                                  │
│                   "Ah! Divide-and-conquer with pivot!"     │
│                                                            │
│    The HOW is the WHAT. Implementation IS purpose.         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 2. Low-Level / Hardware

```
┌────────────────────────────────────────────────────────────┐
│ LOW-LEVEL / HARDWARE INTERACTION                           │
│                                                            │
│    ACTION view:   initialize_dma()                         │
│                   "Sets up DMA... somehow"                 │
│                                                            │
│    WORD view:     REG_DMA_CTRL |= (1 << 7)  // Enable     │
│                   REG_DMA_ADDR = buffer_ptr  // Set addr   │
│                   REG_DMA_SIZE = 4096        // Set size   │
│                                                            │
│    The bit manipulation IS the purpose.                    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 3. Debugging

```
┌────────────────────────────────────────────────────────────┐
│ DEBUGGING                                                  │
│                                                            │
│    ACTION view:   "The architecture looks correct"         │
│                   "Data flows from A → B → C as expected"  │
│                                                            │
│    WORD view:     for i in range(len(arr)):  # Bug: <=    │
│                       if arr[i] = target:    # Bug: ==     │
│                                                            │
│    Bugs hide in WORD, not in ACTION.                       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 4. Polymorphism

```
┌────────────────────────────────────────────────────────────┐
│ HEAVY ABSTRACTION / POLYMORPHISM                           │
│                                                            │
│    ACTION view:                                            │
│                                                            │
│        for plugin in plugins:                              │
│            plugin.run()   ← Calls abstract method          │
│                             ACTION is HIDDEN               │
│                                                            │
│    WORD view:                                              │
│                                                            │
│        class ImagePlugin(Plugin):                          │
│            def run(self):                                  │
│                self.process_images()  ← Concrete impl      │
│                                                            │
│    When polymorphism hides the call graph,                 │
│    you must read the concrete implementations (WORD).      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## The Synthesis: Map Before Terrain

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│    ╔═══════════════════════════════════════════════════════════╗    │
│    ║                                                           ║    │
│    ║  "ACTION provides the map, WORD provides the details      ║    │
│    ║   of the location. You must read the map before you       ║    │
│    ║   study the terrain."                                     ║    │
│    ║                                                           ║    │
│    ║                    — Gemini 2.5 Pro validation            ║    │
│    ║                       2026-01-23                          ║    │
│    ║                                                           ║    │
│    ╚═══════════════════════════════════════════════════════════╝    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### The Correct Order of Operations

```
┌─────────────────────────────────────────────┐
│                                             │
│   STEP 1: Build the MAP (ACTION)            │
│                                             │
│   • Parse call graph                        │
│   • Identify modules and clusters           │
│   • Find entry points and central nodes     │
│   • Map data flow paths                     │
│                                             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│                                             │
│   STEP 2: Navigate to LOCATION (ACTION)     │
│                                             │
│   • "Where is the auth logic?"              │
│   • Follow edges to the cluster             │
│   • Identify key nodes by centrality        │
│                                             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│                                             │
│   STEP 3: Study the TERRAIN (WORD)          │
│                                             │
│   • NOW read the specific function          │
│   • Understand the algorithm                │
│   • Debug if necessary                      │
│                                             │
└─────────────────────────────────────────────┘
```

### Summary

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ACTION first, WORD second.                                │
│   Map first, terrain second.                                │
│   Structure first, content second.                          │
│   Relationships first, implementation second.               │
│                                                             │
│   This is how experts comprehend code.                      │
│   This is how we should build tools.                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

*Visual companion to PURPOSE_ONTOLOGY.md*
*Created: 2026-01-23*
