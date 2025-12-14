# 🗂️ The Categorization Strategy (Taming the Chaos)

You noticed that the Unknowns "repeat a lot".
You are correct. `StringStart`, `StringEnd`, and `StringContent` are all fragments of the same thing.

We do not want 16,000 types. We want order.
Here is the **2-Tier Classification Strategy** we use to turn Chaos into Physics.

---

## TIER 1: THE CONTINENT (The "Force")
Every particle must belong to one of the **4 Fundamental Forces**.
This is the first filter.

1.  **DATA (Cyan)**: Is it "stuff"? (e.g., `StringStart`, `StringEnd`, `Float`).
2.  **LOGIC (Magenta)**: Does it "think"? (e.g., `If`, `While`, `YieldFrom`).
3.  **ORGANIZATION (Green)**: Does it "group"? (e.g., `Class`, `Import`, `Module`).
4.  **EXECUTION (Amber)**: Is it "runtime"? (e.g., `MainEntry`, `Thread`).

*Example:* `StringStart` -> **DATA**.

---

## TIER 2: THE FUNDAMENTAL (The "Family")
Once inside a continent, what *kind* of thing is it?

*   **Primitives:** The bottom-level raw values (`StringStart`, `Integer`).
*   **Expressions:** Things that return a value (`BinaryOperator`, `Await`).
*   **Statements:** Things that perform an action (`Return`, `Print`).
*   **Control Structures:** Things that direct flow (`Match`, `Case`).
*   **Aggregates:** Things that hold other things (`Class`, `Struct`).

*Example:* `StringStart` -> **Primitives**.

---

## THE PROCESS: How we label them?

### Step 1: Heuristic Deduction (Fast)
The Discovery Engine guesses based on the AST type name.
*   If name contains "stmt" -> **LOGIC / Statement**.
*   If name contains "literal" -> **DATA / Primitive**.
*   *(This handles 60% of cases automatically)*.

### Step 2: LLM Consensus (Smart)
For tricky ones, we ask the LLM (The Professor).
*   *Input:* `YieldFrom`
*   *Context:* "It appears inside generator functions."
*   *Verdict:* **LOGIC / Control Structure**.

### Step 3: Human Canonization (Final)
We review the proposed candidates and promote them to the **Canonical Registry** (Atom 131, 132...).

---

**Result:**
The `StringStart`, `StringEnd`, and `StringContent` will all be grouped under **Family: Primitives**, **Continent: DATA**.
They stop being noise. They become part of the table.
