# Newman Suite

> **Mirror**: [`newman_suite.py`](../../../src/core/newman_suite.py)
> **Role**: Core Component

## Purpose
Deterministic probe suite for Collider runtime integrity checks.

`NewmanSuite` validates:

- Universal detector initialization
- God-class regex behavior
- IR graph serialization integrity
- Local LLM connectivity (Ollama)

This module is the active backend for:

- `collider health`
- `collider audit` (step 1/2)

## Architecture
### Classes
- **`ProbeResult`**: Probe result envelope (`component`, `status`, `latency_ms`, `details`, `error`)
- **`NewmanSuite`**: Probe orchestrator exposing `run_all()`

## Waybill
- **ID**: `PARCEL-NEWMAN_SUITE.PY`
- **Source**: `Codome://newman_suite.py`
- **Refinery**: `SelfAnalysis-v1.0`
- **Generated**: `2026-01-28T19:17:39.164853Z`
- **Status**: REFINED
