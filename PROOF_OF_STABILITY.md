# Proof of Stability: Experiment Report

**Date**: 2025-12-20
**Subject**: Resilience of 'Single Truth' Architecture

## Experiment Summary
We ran a managed simulation mutating the configuration and analysis logic to verify that architectural identity (`stable_id`) decouples correctly from analysis state (`annotated_id`).

## Results

| Metric | Result | Verdict |
|:---|:---|:---:|
| **Config Evolution** | Hash changed from `426a5312` to `b1e95142` | ✅ PASS |
| **Identity Persistence** | `stable_id` remained identical | ✅ PASS |
| **Analysis Evolution** | `annotated_id` successfully captured new smells | ✅ PASS |

## Artifacts

**Baseline ID (V1)**:
`LOG.FNC.M|risk_engine.calculator|calculate_risk_score|9ff23a`

**Annotated ID (V2)**:
`LOG.FNC.M|risk_engine.calculator|calculate_risk_score|async:True|calls:1|confidence:80|io:True|lines:15|params:2|smell:magic_number=65.00|9ff23a`

## Conclusion
The architecture successfully supports non-breaking evolution. We can upgrade the ruleset, change confidence scoring, and add dimension smells without breaking historical tracking keys.
