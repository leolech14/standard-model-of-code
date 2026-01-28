# Graph Framework

> **Mirror**: [`graph_framework.py`](../../../src/core/graph_framework.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture

### Functions
- **`build_nx_graph`**: Build NetworkX DiGraph from Collider analysis output.
- **`compute_degree_metrics`**: Compute in-degree and out-degree for each node.
- **`classify_node_role`**: Classify architectural role from degree metrics.
- **`find_entry_points`**: Find likely entry points (nodes with 0 in-degree or special names).
- **`propagate_context`**: Propagate context via BFS from root nodes downstream.
- **`get_node_neighborhood`**: Get the local neighborhood of a node.
- **`analyze_graph`**: Complete graph analysis pipeline.

## Waybill
- **ID**: `PARCEL-GRAPH_FRAMEWORK.PY`
- **Source**: `Codome://graph_framework.py`
- **Refinery**: `SelfAnalysis-v1.0`
- **Generated**: `2026-01-28T17:50:51.684525Z`
- **Status**: REFINED
