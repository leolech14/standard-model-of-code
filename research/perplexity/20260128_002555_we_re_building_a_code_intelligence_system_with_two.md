# Research: We're building a code intelligence system with TWO pipelines:

1. Analysis Pipeline: Processes code ...

> **Date:** 2026-01-28 00:25:55
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:a5cedcc8f04a61281c81f64824fd17cf85970d1a9e892eaaddb05a556dbb9832`
> **Raw JSON:** `raw/20260128_002555_we_re_building_a_code_intelligence_system_with_two.json`

---

## Query

We're building a code intelligence system with TWO pipelines:

1. Analysis Pipeline: Processes code → generates graph/metrics
2. Refinery Pipeline: Processes docs/config → generates semantic chunks

Now adding: File Popularity Tracker (tracks modification history, identifies dead/popular files)

Architectural question: Should this be:
A) A stage INSIDE Refinery pipeline?
B) A separate subsystem that FEEDS both pipelines?
C) Part of monitoring/observability subsystem?

Considerations:
- Separation of concerns
- Reusability (multiple consumers)
- Pipeline complexity
- Similar patterns in production systems

What do production code intelligence systems (like Sourcegraph, CodeScene, GitPrime) do? How do they architect temporal/activity analysis relative to their core analysis pipelines?

---

## Response

**Option B (a separate subsystem that feeds both pipelines) best aligns with separation of concerns, reusability, and production patterns in code intelligence systems.**

This architecture treats the File Popularity Tracker as an independent data ingestion and enrichment layer that captures modification history (e.g., via Git logs or filesystem events) and computes metrics like recency, commit frequency, and activity scores. It then exposes these as shared features (e.g., via a feature store, Kafka topics, or a metadata database) for consumption by both the Analysis Pipeline (to weight graphs/metrics by file activity) and Refinery Pipeline (to prioritize semantic chunks from popular files).[2][3]

### Key Considerations and Rationale
- **Separation of Concerns**: File popularity tracking is a distinct **temporal/metadata ingestion** responsibility, not core analysis (code graphs) or semantic processing (docs/config). Embedding it inside Refinery (Option A) mixes codebase activity signals with documentation handling, violating modularity; core pipelines stay focused on transformation.[2][3]
- **Reusability (Multiple Consumers)**: As a feeder subsystem, it serves **both pipelines plus future consumers** (e.g., UI prioritization, cost optimization). Production systems use this pattern for cross-pipeline features like usage telemetry.[2][7]
- **Pipeline Complexity**: Adding it as a stage increases Refinery's state (Option A) or Analysis's (if misplaced); a separate subsystem uses **event-driven or batch feeding** (e.g., Airflow/Dagster orchestration) to decouple timing—track continuously, feed on-demand.[2][3]
- **Monitoring/Observability Fit (Option C)**: Observability tracks **runtime metrics** (latency, errors); this is **historical data enrichment**, better as a feature pipeline than pure monitoring.[2]

| Option | Pros | Cons | Fit for Your System |
|--------|------|------|---------------------|
| **A) Inside Refinery** | Simple integration for docs. | Couples file activity to docs/config; not reusable for code analysis; bloats pipeline.[3] | Poor—ignores Analysis Pipeline needs. |
| **B) Separate Feeder** | Reusable; modular; scales independently; feeds both.[2][3] | Slight added infra (e.g., feature store). | **Best**—matches production data pipelines. |
| **C) Monitoring** | Easy alerting on trends. | Not for feature feeding; observability ≠ enrichment.[2] | Weak—temporal analysis is input data, not just logs. |

### Patterns in Production Code Intelligence Systems
Direct details on Sourcegraph, CodeScene, and GitPrime are limited in results, but analogous systems follow **modular ingestion + shared features**:
- **Sourcegraph**: Uses separate **event tracking** (commit/search history) via Prometheus/ClickHouse, feeding code intelligence (graphs, search ranking) independently of core indexing pipelines.[inferred from pipeline modularity in [2]]
- **CodeScene/GitPrime**: Treat **temporal analysis** (hotspot detection via commit frequency) as a **standalone behavioral pipeline**, enriching code metrics without altering core static analysis. They ingest Git history separately, compute scores (e.g., churn), and feed to visualization/query layers—mirroring your dual-pipeline setup.[3][7]
- **General Patterns**: AI/data pipelines (e.g., Dagster, Airflow examples) make **metadata trackers** (like popularity) modular ingestion stages with feedback loops, using idempotent ops for reliability. This avoids tight coupling, enabling batch/streaming (e.g., nightly Git scans or real-time hooks).[2][3][4]

Implement as a lightweight service: poll Git/VCS for deltas, compute rolling metrics (e.g., 30-day mods), store in a lakehouse/Redis, and trigger pipeline jobs on thresholds. This scales with your system while minimizing complexity.[2][3]

---

## Citations

1. https://dev.to/apssouza22/a-deep-dive-into-deep-agent-architecture-for-ai-coding-assistants-3c8b
2. https://www.domo.com/blog/the-complete-guide-to-building-the-ai-data-pipeline
3. https://dagster.io/guides/data-pipeline-architecture-5-design-patterns-with-examples
4. https://www.databricks.com/blog/ai-etl-how-artificial-intelligence-automates-data-pipelines
5. https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1660912/full
6. https://www.cloudbees.com/blog/pipeline-as-code-simple-explanation-with-examples
7. https://www.montecarlodata.com/blog-data-pipeline-architecture-explained/
8. https://snowplow.io/blog/data-pipeline-architecture-for-ai-traditional-approaches

---

## Usage Stats

- Prompt tokens: 158
- Completion tokens: 813
- Total tokens: 971
