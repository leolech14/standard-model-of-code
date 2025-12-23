# Mini-Validation Results

## Summary

- **Total samples**: 500
- **Correct predictions**: 361
- **Accuracy**: 72.2%

❌ **FAIL**: Accuracy < 75% - Significant issues

**Recommendation**: Debug patterns before proceeding

## Per-Role Performance

| Role | Precision | Recall | F1 | Support |
|------|-----------|--------|----|---------|
| utility | 95.2% | 60.2% | 73.8% | 294 |
| test | 93.7% | 100.0% | 96.7% | 178 |
| query | 13.8% | 100.0% | 24.2% | 4 |
| entity | 0.0% | 0.0% | 0.0% | 4 |
| repository | 0.0% | 0.0% | 0.0% | 4 |
| configuration | 33.3% | 33.3% | 33.3% | 3 |
| validator | 4.8% | 50.0% | 8.7% | 2 |
| factory | 0.0% | 0.0% | 0.0% | 2 |
| adapter | 0.0% | 0.0% | 0.0% | 2 |
| mock | 0.0% | 0.0% | 0.0% | 2 |
| view | 0.0% | 0.0% | 0.0% | 2 |
| middleware | 0.0% | 0.0% | 0.0% | 1 |
| transformer | 0.0% | 0.0% | 0.0% | 1 |
| constant | 0.0% | 0.0% | 0.0% | 1 |
| command | 0.0% | 0.0% | 0.0% | 0 |
| fixture | 0.0% | 0.0% | 0.0% | 0 |
| observer | 0.0% | 0.0% | 0.0% | 0 |
| controller | 0.0% | 0.0% | 0.0% | 0 |
| eventhandler | 0.0% | 0.0% | 0.0% | 0 |

## Most Common Errors

| Actual | Predicted | Count |
|--------|-----------|-------|
| Utility | Query | 21 |
| Utility | Entity | 20 |
| Utility | Command | 17 |
| Utility | Validator | 17 |
| Utility | Test | 10 |
| Utility | Factory | 10 |
| Utility | Fixture | 6 |
| Utility | Transformer | 5 |
| Utility | Controller | 4 |
| Entity | Validator | 3 |

---

**Next Steps:**
1. Analyze errors (see table above)
2. Refine pattern matching rules
3. Re-sample and re-test
