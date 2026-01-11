# 📋 GENERATED TASKS
**Auto-Generated from Collider Analysis**
**Date**: 2025-12-27
**Source**: `src/core` analysis (571 nodes, 3,218 edges)

---

## 🔒 CRITICAL: Security Review (9 tasks)

### I/O Write Operations Requiring Security Audit

- [ ] SECURITY REVIEW: `save` (src/core/config.py:48) - Save config to a JSON file
  - Check: Path traversal, input validation, permissions

- [ ] SECURITY REVIEW: `create_unified_output` (src/core/unified_analysis.py:179) - Create a unified output from analysis results
  - Check: Output path validation, disk space, error handling

- [ ] SECURITY REVIEW: `save` (src/core/unified_analysis.py:173) - Save to JSON file
  - Check: File overwrite protection, permissions

- [ ] SECURITY REVIEW: `save_results` (src/core/stats_generator.py:198) - Save results to multiple output formats
  - Check: Format injection, path validation

- [ ] SECURITY REVIEW: `_write_particles_csv` (src/core/stats_generator.py:257) - Write particles to CSV
  - Check: CSV injection, special character escaping

- [ ] SECURITY REVIEW: `_create_nodes` (src/core/purpose_field.py:194) - Create PurposeNodes from analysis output
  - Check: Input validation, data integrity

- [ ] SECURITY REVIEW: `_write_components_csv` (src/core/report_generator.py:142) - Performs transformation operation
  - Check: CSV injection, file permissions

- [ ] SECURITY REVIEW: `detect_d4_boundary` (src/core/dimension_enricher.py:194) - D4: BOUNDARY - Does this node cross architectural boundaries?
  - Check: Boundary crossing validation

- [ ] SECURITY REVIEW: `detect_d6_effect` (src/core/dimension_enricher.py:329) - D6: EFFECT - What side effects does this node have?
  - Check: Side effect tracking accuracy

**Priority**: CRITICAL
**Total Effort**: ~4.5 hours (30 min each)
**Impact**: Prevent security vulnerabilities

---

## ⚡ HIGH PRIORITY: Performance Optimization (88 tasks)

### Top 20 Cacheable Functions (Pure + Stateless)

#### Quick Wins (< 5 min each)

- [ ] Add @lru_cache to `_tokenize_identifier` (tree_sitter_engine.py:89)
- [ ] Add @lru_cache to `analyze_directory` (tree_sitter_engine.py:156)
- [ ] Add @lru_cache to `_extract_touchpoints` (tree_sitter_engine.py:346)
- [ ] Add @lru_cache to `_fallback_analysis` (tree_sitter_engine.py:378)
- [ ] Add @lru_cache to `config_hash` (config.py:38)
- [ ] Add @lru_cache to `_check_ollama_available` (ollama_client.py:39)
- [ ] Add @lru_cache to `is_available` (ollama_client.py:117)
- [ ] Add @lru_cache to `analyze_repository` (god_class_detector_lite.py:110)
- [ ] Add @lru_cache to `_generate_refactor_suggestions` (god_class_detector_lite.py:355)
- [ ] Add @lru_cache to `generate_ascii_visualization` (god_class_detector_lite.py:437)
- [ ] Add @lru_cache to `to_dict` (unified_analysis.py:169)
- [ ] Add @lru_cache to `_extract_atoms` (atom_extractor.py:283)
- [ ] Add @lru_cache to `_has_io_calls` (atom_extractor.py:448)
- [ ] Add @lru_cache to `to_json` (atom_extractor.py:518)
- [ ] Add @lru_cache to `to_dict` (lens_interrogator.py:40)
- [ ] Add @lru_cache to `lens_r2_ontology` (lens_interrogator.py:135)
- [ ] Add @lru_cache to `_calculate_nesting_depth` (lens_interrogator.py:266)
- [ ] Add @lru_cache to `_get_attribute_name` (lens_interrogator.py:156)
- [ ] Add @lru_cache to `detect_d2_layer` (dimension_enricher.py:245)
- [ ] Add @lru_cache to `suggest_refactoring_cuts` (graph_analyzer.py:78)

**Implementation Template**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def function_name(...):
    # existing code...
```

**Priority**: HIGH
**Total Effort**: ~1.5 hours (20 × 5 min)
**Impact**: 20-50% speedup for cached functions

#### Remaining Functions (68 more)

- [ ] Batch-apply @lru_cache to remaining 68 pure, stateless functions
  - Use automated script to add decorators
  - Priority: MEDIUM
  - Effort: 3-4 hours
  - Impact: 10-15% overall performance improvement

---

## 🔍 MEDIUM PRIORITY: Code Review (144+ tasks)

### Functions Requiring Manual Review

#### Top 15 Review Items

- [ ] REVIEW: `_enrich_with_how` (enrichment_helpers.py:7)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `_enrich_with_where` (enrichment_helpers.py:48)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `_enrich_with_why` (enrichment_helpers.py:81)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `__init__` (tree_sitter_engine.py:53)
  - Reasons: Role is unknown, Low classification confidence, No documentation

- [ ] REVIEW: `_tokenize_identifier` (tree_sitter_engine.py:89)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `analyze_file` (tree_sitter_engine.py:109)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `analyze_directory` (tree_sitter_engine.py:156)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `_extract_python_simple` (tree_sitter_engine.py:180)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `_get_decorator_name` (tree_sitter_engine.py:258)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `_get_base_name` (tree_sitter_engine.py:271)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `_extract_particles` (tree_sitter_engine.py:279)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `_classify_class_pattern` (tree_sitter_engine.py:332)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `_classify_function_pattern` (tree_sitter_engine.py:336)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `_classify_extracted_symbol` (tree_sitter_engine.py:340)
  - Reasons: Role is unknown, Low classification confidence

- [ ] REVIEW: `_extract_touchpoints` (tree_sitter_engine.py:346)
  - Reasons: Role is unknown, Low classification confidence

**Priority**: MEDIUM
**Total Effort**: ~15 hours (144 × 5-10 min each)
**Impact**: Better classification, improved code quality

#### Action: Add Classification Patterns

- [ ] Create classification patterns for common function names:
  - `__init__` → Constructor
  - `to_dict` → Serializer
  - `from_dict` → Deserializer
  - `_extract_*` → Extractor
  - `_classify_*` → Classifier
  - `analyze_*` → Analyzer

**File**: `src/patterns/particle_defs.json`
**Effort**: 1 hour
**Impact**: Auto-classify ~50 functions

---

## 🧪 TESTING TASKS (155 stateful functions)

### High-Priority: Test Stateful Functions

- [ ] Identify stateful functions with complexity > 10
- [ ] Add unit tests for I/O operations (9 functions)
- [ ] Add integration tests for graph operations
- [ ] Test edge cases in dimension enrichment
- [ ] Add tests for lens interrogation

**Priority**: HIGH
**Effort**: 8-12 hours
**Impact**: Prevent regression bugs

---

## 🔧 PIPELINE FIXES (2 critical issues)

### Stage 6: Fix boundary_detector

- [ ] Debug `boundary_detector.analyze()` return format
  - File: `src/core/boundary_detector.py`
  - Issue: Returns `None` instead of expected dict
  - Priority: HIGH
  - Effort: 1-2 hours
  - Impact: Enable full 8D enrichment

### R5 Lens: Fix edge-to-node linking

- [ ] Fix edge connection logic in R5 lens
  - File: `src/core/lens_interrogator.py` (R5 section)
  - Issue: Nodes show 0 connections despite 3,218 edges existing
  - Priority: HIGH
  - Effort: 1 hour
  - Impact: Full graph topology metrics

**Total Effort**: 2-3 hours
**Impact**: Complete Theory v2 implementation

---

## 📚 DOCUMENTATION TASKS

### Low Priority Improvements

- [ ] Add docstrings to undocumented functions
- [ ] Generate API reference from pure functions
- [ ] Create architecture diagrams from high-confidence nodes
- [ ] Document dimensional patterns discovered

**Priority**: LOW
**Effort**: 4-6 hours
**Impact**: Better code understanding

---

## 🏗️ ARCHITECTURE REVIEW

### DTO Consolidation (100 DTOs found)

- [ ] Review necessity of 100 DTOs (17.5% of codebase)
  - Find DTOs with < 3 fields (too simple?)
  - Find DTOs used only once (unnecessary?)
  - Consolidate similar DTOs

**Priority**: MEDIUM
**Effort**: 2-3 hours
**Impact**: Reduce over-engineering

---

## 📊 TASK SUMMARY

| Category | Count | Priority | Effort | Impact |
|----------|-------|----------|--------|--------|
| Security Review | 9 | CRITICAL | 4.5h | High |
| Performance (Cache) | 88 | HIGH/MED | 7.5h | High |
| Code Review | 144 | MEDIUM | 15h | Medium |
| Testing | 155 | HIGH | 12h | High |
| Pipeline Fixes | 2 | HIGH | 3h | High |
| Documentation | ~60 | LOW | 6h | Low |
| Architecture | 100 | MEDIUM | 3h | Medium |

**Total Tasks**: 558 tasks
**Total Effort**: ~51 hours
**High ROI Tasks**: 99 tasks (~15 hours)

---

## 🎯 RECOMMENDED SPRINT PLAN

### Week 1: Critical & Quick Wins

**Monday-Tuesday** (8h):
- [ ] Complete all 9 security reviews (CRITICAL)
- [ ] Cache top 10 pure functions

**Wednesday-Thursday** (8h):
- [ ] Fix boundary_detector (Stage 6)
- [ ] Fix edge-to-node linking (R5)
- [ ] Add classification patterns

**Friday** (4h):
- [ ] Cache remaining 10 high-impact functions
- [ ] Test coverage for I/O operations

**Total**: 20 hours, 32 tasks completed
**ROI**: Maximum impact tasks

### Week 2: Testing & Performance

**Monday-Tuesday** (8h):
- [ ] Batch-cache remaining 68 pure functions
- [ ] Add tests for stateful functions (high complexity)

**Wednesday-Friday** (12h):
- [ ] Complete testing for stateful functions
- [ ] Manual review of top 20 unknown functions

**Total**: 20 hours, ~110 tasks completed

### Week 3+: Architecture & Documentation

- [ ] DTO consolidation review
- [ ] Documentation improvements
- [ ] LLM-powered classification for unknowns

---

## 🤖 AUTOMATION SCRIPTS

### Generate Task Files

```bash
# Security tasks
cat src/core/collider_output/unified_analysis.json | jq -r '
  .nodes[] |
  select(
    (.dimensions.D4_BOUNDARY == "Output" or .dimensions.D4_BOUNDARY == "I-O") and
    .dimensions.D6_EFFECT == "Write"
  ) |
  "- [ ] SECURITY: \(.name) (\(.file_path):\(.start_line))"
' > tasks_security.txt

# Caching tasks
cat src/core/collider_output/unified_analysis.json | jq -r '
  .nodes[] |
  select(
    .dimensions.D5_STATE == "Stateless" and
    .dimensions.D6_EFFECT == "Pure"
  ) |
  "- [ ] CACHE: \(.name) (\(.file_path):\(.start_line))"
' > tasks_performance.txt

# Review tasks
cat src/core/collider_output/unified_analysis.json | jq -r '
  .nodes[] |
  select(.lenses.R8_EPISTEMOLOGY.requires_review == true) |
  "- [ ] REVIEW: \(.name) (\(.file_path):\(.start_line))"
' > tasks_review.txt
```

---

## ✅ COMPLETION CRITERIA

**Security**: All 9 I/O operations audited and secured
**Performance**: Top 20 pure functions cached (20-50% speedup)
**Pipeline**: 8/8 stages working (currently 7/8)
**Classification**: < 30% unknowns (currently 63%)
**Testing**: All stateful functions have tests
**Documentation**: 95%+ coverage (currently 89.5%)

---

**Generated by**: Collider v3.0.0 (8D + 8L Analysis)
**Source Data**: `src/core/collider_output/unified_analysis.json`
**Total Nodes Analyzed**: 571
**Total Edges Analyzed**: 3,218
**Analysis Time**: 1.9 seconds
