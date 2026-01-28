# Level Classifier

> **Mirror**: [`level_classifier.py`](../../../src/core/level_classifier.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture

### Functions
- **`classify_level`**: Assign a holarchy level to a node based on its `kind` field.
- **`_infer_level_from_properties`**: Infer level from node properties when kind doesn't map directly.
- **`classify_level_batch`**: Assign holarchy levels to all nodes in a batch.
- **`infer_package_levels`**: Promote directory-grouping nodes to L6 (PACKAGE) based on
- **`compute_level_statistics`**: Compute the distribution of nodes across holarchy levels.
- **`compute_zone_statistics`**: Compute the distribution of nodes across zones.
- **`get_level_info`**: Get full information about a holarchy level.
- **`format_level_summary`**: Format a human-readable summary of level distribution.

## Waybill
- **ID**: `PARCEL-LEVEL_CLASSIFIER.PY`
- **Source**: `Codome://level_classifier.py`
- **Refinery**: `SelfAnalysis-v1.0`
- **Generated**: `2026-01-28T17:50:51.684171Z`
- **Status**: REFINED
