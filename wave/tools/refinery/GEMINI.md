# Data Logistics Subsystem

> Managing the flow of data "Parcels" from Ingestion to Refined Intelligence.

## Architecture

This subsystem implements the **Logistics Hyper-Layer**. Every data object processed here is wrapped in a **Waybill** for provenance tracking.

| Tool | Role | Description |
|------|------|-------------|
| `pipeline.py` | **Orchestrator** | Coordinates Scanner -> Chunker handoff. Mints Batch IDs. |
| `corpus_inventory.py` | **Ingestion** | Mints initial Parcel IDs for raw files. |
| `../ai/aci/refinery.py` | **Refinement** | Consumes Parcels, produces tracked Sub-Parcels (Chunks). |

## Usage

```bash
# Run the full pipeline on a directory
python3 pipeline.py /path/to/source
```

## Key Concept: Copresence
We track not just "what" but "who else was in the room". All data processed in a single `pipeline.py` run shares a `batch_id`, which acts as a topological hyperedge linking those concepts.

## Extended Context
@../../intelligence/concepts/THEORY_DATA_LOGISTICS.md
