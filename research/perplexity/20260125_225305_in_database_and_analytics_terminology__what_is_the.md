# Research: In database and analytics terminology, what is the standard name for a system that tracks all file c...

> **Date:** 2026-01-25 22:53:05
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:189714c92e92445a97861a127ae57eaa3e6c8474bcbb3eda68e59d3eafdee203`
> **Raw JSON:** `raw/20260125_225305_in_database_and_analytics_terminology__what_is_the.json`

---

## Query

In database and analytics terminology, what is the standard name for a system that tracks all file creation and modification events across a repository or filesystem, allowing temporal queries like 'what changed in the last 7 days' or 'what files are stale'? Consider terms from: event sourcing, change data capture, temporal databases, audit logging, activity streams, data lineage. What would a data engineer or query specialist call this?

---

## Response

**A temporal database (specifically a transaction-time or bitemporal database) is the standard term in database terminology for a system that tracks file creation and modification events with timestamps, enabling temporal queries like "what changed in the last 7 days" or "what files are stale."**[1][3][5]

Data engineers and query specialists would call this a **transaction-time relation** or **bitemporal relation**, where each record (e.g., file event) is associated with **transaction time**—the period when the fact was present in the database—and optionally **valid time**—when the fact was true in the real world. These support queries over time intervals without overwriting historical data.[1][3][6]

### Key Concepts from Temporal Databases
- **Transaction Time**: Time interval during which a fact (e.g., file modification) is stored in the database; immutable and cannot extend beyond now. Used for auditing changes and identifying stale files (e.g., no updates since a cutoff).[1][3][8]
- **Valid Time**: Time when the fact holds true (e.g., a file's content was active); allows "what changed" queries.[1][3]
- **Types of Relations**:
  | Type | Description | Use Case Fit |
  |------|-------------|--------------|
  | Uni-temporal (Transaction-time) | Tracks only storage times | File audit logs, staleness checks[3] |
  | Bi-temporal | Tracks both valid and transaction times | Full event history with real-world validity[1][3] |
  | Tri-temporal | Adds decision time | Less common for filesystems[1] |

This differs from related terms:
- **Event Sourcing**: Stores event streams for state reconstruction, not inherently filesystem-focused.[4]
- **Change Data Capture (CDC)**: Captures database row changes for replication, not file-level.[not in results]
- **Audit Logging**: Basic event recording without built-in temporal querying.[not specialized in results]
- **Activity Streams/Data Lineage**: Track user actions or data flow, not comprehensive filesystem timestamps.[not in results]

Temporal databases address filesystem needs by natively supporting time-based queries (e.g., AS OF, BETWEEN timestamps) on historical versions, though they require more storage for versions.[1][2][3] Standard SQL:2011 includes basic temporal support, but full features often need extensions.[3]

---

## Citations

1. https://www.geeksforgeeks.org/dbms/introduction-to-temporal-database/
2. https://www.scribd.com/document/827153803/Temporal-Databases
3. https://sigmodrecord.org/publications/sigmodRecord/9209/pdfs/140979.140996.pdf
4. https://docs.temporal.io/glossary
5. https://dl.acm.org/doi/10.1145/140979.140996
6. https://infolab.usc.edu/csci599/Fall2001/paper/glossary.pdf
7. https://homes.cs.aau.dk/~csj/Papers/Files/1993_jensenCGTDC-TR93-2035.pdf
8. https://docs.progress.com/bundle/marklogic-server-use-bi-temporal-features-12/page/topics/intro.html

---

## Usage Stats

- Prompt tokens: 83
- Completion tokens: 497
- Total tokens: 580
