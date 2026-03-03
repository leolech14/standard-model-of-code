# ORPHANS - The Disconnection Taxonomy

> "Orphan" is a misclassification bucket. Only ~9% of orphans are truly dead code.

---

## The Problem

Static analysis tools label any node with zero in-degree AND zero out-degree as an "orphan" and suggest deletion. This is almost always wrong.

An orphan is disconnected from the **statically visible** graph. But many nodes are connected through channels that static analysis cannot see.

---

## The 7 Disconnection Types

| Type | Example | Actually Dead? | Action |
|------|---------|----------------|--------|
| **test_entry** | Called by pytest/jest runner | No | Leave it |
| **entry_point** | `__main__`, CLI handler, `main()` | No | Leave it |
| **framework_managed** | Dataclass, DI container, ORM model | No | Leave it |
| **cross_language** | Python called from JavaScript | Maybe | Check |
| **external_boundary** | Public API endpoint | Maybe | Check |
| **dynamic_target** | Called via reflection, `getattr()` | Maybe | Check |
| **unreachable** | True dead code | **Yes** | Delete |

---

## The Distribution

Typical codebase:

```
test_entry:         ~35%  ─── Safe (framework invokes them)
entry_point:        ~20%  ─── Safe (OS/CLI invokes them)
framework_managed:  ~15%  ─── Safe (DI/ORM/decorator magic)
cross_language:     ~8%   ─── Needs investigation
external_boundary:  ~7%   ─── Needs investigation
dynamic_target:     ~6%   ─── Needs investigation
unreachable:        ~9%   ─── Actually delete
```

**Only ~9% of "orphans" are genuinely dead code.** The rest are alive through invisible channels.

---

## Why This Matters

If you blindly delete all orphans in a codebase:
- **35%** of your tests break
- **20%** of your entry points vanish
- **15%** of framework-managed code disappears
- You've just destroyed a working application

The orphan taxonomy turns a dangerous boolean (dead/alive) into a **rich classification** that prevents false-positive deletions.

---

## Detection Heuristics

The Collider classifies orphans using:

| Signal | Detects |
|--------|---------|
| Path contains `/test/` or `_test.py` | test_entry |
| Has `if __name__` or `@click.command` | entry_point |
| Has `@dataclass`, `@Injectable`, ORM base | framework_managed |
| File extension mismatch in project | cross_language |
| Has `@api_view`, `@app.route` | external_boundary |
| Referenced in strings, `getattr`, config files | dynamic_target |
| None of the above | unreachable (candidate) |

---

## In the Graph

```
orphan = { n ∈ N : in_degree(n) = 0 ∧ out_degree(n) = 0 }
```

But this definition only captures **static** connectivity. The taxonomy adds **semantic** connectivity -- understanding that a test runner, CLI, or framework provides the missing edges.

---

*Source: MODEL.md (§3), L2_PRINCIPLES.md*
*See also: [GRAPH.md](GRAPH.md) for topology roles, [../essentials/THEORY_WINS.md](../essentials/THEORY_WINS.md) (Idea #11)*
