# Purpose Intelligence

> **Mirror**: [`purpose_intelligence.py`](../../../src/core/purpose_intelligence.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture
### Classes
- **`PurposeIntelligence`**: No docstring

### Functions
- **`compute_Q_alignment`**: Q_alignment: Rule adherence score.
- **`compute_Q_coherence`**: Q_coherence: Focus via entropy of atom categories.
- **`compute_Q_density`**: Q_density: Signal-to-noise ratio.
- **`compute_Q_completeness`**: Q_completeness: Expected children present.
- **`compute_Q_simplicity`**: Q_simplicity: Inverse of complexity.
- **`compute_Q_purity`**: Q_purity: Behavior matches classified dimensions.
- **`compute_intrinsic_quality`**: Compute I(H) - the intrinsic quality of a holon.
- **`propagate_quality`**: Q(H) = w_parts × Avg(Q_children) + w_intrinsic × I(H)
- **`compute_purpose_intelligence`**: Compute full Purpose Intelligence for a node.
- **`compute_codebase_intelligence`**: Compute Purpose Intelligence for an entire codebase.
- **`enrich_nodes_with_intelligence`**: Add purpose_intelligence fields to nodes.

## Waybill
- **ID**: `PARCEL-PURPOSE_INTELLIGENCE.PY`
- **Source**: `Codome://purpose_intelligence.py`
- **Refinery**: `SelfAnalysis-v1.0`
- **Generated**: `2026-01-28T19:17:39.161723Z`
- **Status**: REFINED
