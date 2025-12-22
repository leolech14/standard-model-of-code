# 🧱 The Matter of the System (Material Report)

You asked: **"What is the code made of?"**
Here is the raw material analysis. No laws. No theory. Just the stuff that exists.

---

## 1. WHAT WE ARE MISSING (The Unknown)
**47.0% of your codebase is currently "Dark Matter".**
We see it, but we don't recognize it.

*   **The Unknowns:** 16,133 particles.
*   **The Tests:** 14,040 particles (40.9% of the identifiable matter is just Test scaffolding).
*   **The Reality:** We currently only "know" about **13% of your production code**.
    *   This is why the system feels "low resolution". We are staring at a blurry picture.

---

## 2. WHAT THE CODE IS MADE OF (The Known List)
We have identified **130 Distinct Materials** (Atoms).
Here they are, grouped by what they assume.

### GROUP A: The "Red" Matter (Control & Logic)
*These act. They do things.*
`IfBranch`, `ElseBranch`, `LoopFor`, `LoopWhile`, `ReturnStmt`, `YieldFrom`, `BreakStmt`, `ContinueStmt`, `TryCatch`, `RaiseStmt`, `AssertStmt`, `AwaitExpr`, `AsyncFunction`...

### GROUP B: The "Blue" Matter (Data & Storage)
*These hold things.*
`Integer`, `Float`, `StringLiteral`, `Boolean`, `ListLiteral`, `DictLiteral`, `Assignment`, `LocalVar`, `InstanceField`, `DTO`, `ValueObject`, `Entity`...

### GROUP C: The "Green" Matter (Structure)
*These organize things.*
`Class`, `Function`, `Decorator`, `Import`, `ImportFrom`, `Module`, `Repository`, `Factory`, `ContextManager`...

### GROUP D: The "Yellow" Matter (Execution)
*These run things.*
`MainEntry`, `APIHandler`, `CommandHandler`, `EventHandler`, `Middleware`, `UseCase`...

---

## 3. COMMONALITIES (The Threads)
If you look closely, you see patterns among them:

1.  **The Recursive Ones**:
    *   `If`, `For`, `While`, `Function` -> All contain *other* atoms inside them. They are "Containers".

2.  **The Terminal Ones**:
    *   `Return`, `Break`, `Raise` -> These stop the flow. They are "Walls".

3.  **The Connectors**:
    *   `CallExpr`, `Import`, `Await` -> These bind one part of the code to another. They are "Glue".

---

## 4. THE 77 VS 53 (Discovery)
*   **77** were hardcoded "we expect this to exist" (e.g., `Class`, `Function`).
*   **53** were discovered by looking at the code (e.g., `YieldFrom`, `MatMul`, `AsyncGen`).
    *   *Observation:* The system is finding "modern" Python features (async, generators) that the original hardcoded rules missed.

---

**Summary:**
The code is currently **50% Dark Matter**, **40% Scaffolding (Tests)**, and **10% Logic/Data Structure**.
To get high resolution, we must illuminate the Dark Matter.
