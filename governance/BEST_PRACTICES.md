# BEST PRACTICES - PROJECT_elements Development

**Purpose:** Prevent common mistakes, maintain repo health
**Updated:** 2026-01-28
**Authority:** Lessons learned from 666K artifact cleanup incident

---

## ⚠️ MATURITY NOTICE

**This document is INCOMPLETE and will remain so until Refinery maturity.**

> Only after our code and documentation get mapped fully through the Refinery will we be able to reason on the totality of the good practices we implemented.

**Current Status:** Early lessons captured (incident-driven)

**What we have:**
- Specific incident learnings (666K artifact commit)
- Immediate prevention measures (.gitignore, Gate G9)
- Reactive solutions to problems encountered

**What we need before "best practices" is complete:**
- ✅ Refinery Pipeline fully mature (mapping all code + docs)
- ✅ Temporal Intelligence operational (file popularity, dead code detection)
- ✅ Multiple incident cycles (not just one)
- ✅ Pattern synthesis across experiences
- ✅ Validated practices (tried and proven)

**Timeline:** Write comprehensive best practices AFTER:
1. Refinery processes entire codebase (complete mapping)
2. Temporal Intelligence identifies all dead code
3. File Popularity Tracker validates what's actually used
4. We've experienced enough incidents to see patterns
5. Practices have been tested and refined

**For now:** This is a living incident log + immediate prevention guide.

**Later:** Synthesize into canonical best practices when mature.

---

## 🚫 NEVER COMMIT

### 1. Build Artifacts (Collider Outputs)

**What:**
- `unified_analysis.json` (22MB+ JSON files)
- `collider_report.html` (HTML visualizations)
- Any `.collider/`, `.collider-verify/`, `.collider-full/` directories

**Why:** These are GENERATED from source code
- Regenerate with: `./pe collider full . --output <dir>`
- Anyone can reproduce
- Bloats git history

**Prevention:** Covered by `.gitignore`

---

### 2. Vendor Libraries (Third-Party Code)

**What:**
- `libs/bootstrap/` (CSS frameworks)
- `libs/quarto-html/` (HTML dependencies)
- `node_modules/` (npm packages)
- `.venv/` (Python packages)

**Why:** Use package managers, not git
- Bootstrap: Use CDN `<link>` tags
- Node: Use `package.json` + `npm install`
- Python: Use `requirements.txt` + `pip install`

**Prevention:** Covered by `.gitignore`

---

### 3. Temporary Files

**What:**
- `.tmp_*/` directories
- `reproduce_crash*.py` (debugging scripts)
- `test*.html` (local test files)

**Why:** Ephemeral, should be in `/tmp/`

**Prevention:** Use `/tmp/` or clean up before committing

---

### 4. Session Artifacts (Unless Intentional)

**What:**
- `autopilot_logs/` older than 30 days
- Research dumps from single sessions
- AI conversation threads (unless archiving intentionally)

**Why:** These grow unbounded
- Keep recent logs (<30 days)
- Archive old sessions to cold storage

**Prevention:** Manual cleanup or automated archival

---

## ✅ ALWAYS DO

### 1. Check Before Commit

**Before `git commit`:**
```bash
# Check what you're committing
git status

# Review size of added files
git diff --stat

# If you see large JSON/HTML files - STOP
# They're probably artifacts
```

**Red flags:**
- Files >1MB (unless intentional)
- `.json` files >100KB
- `.html` files >500KB
- Directories with "output", "verify", "tmp" in name

---

### 2. Use .gitignore Patterns

**Add to .gitignore:**
```
# Generated outputs
output_*/
*_output/
.collider*/
.tmp_*/

# Vendor code
**/libs/
**/vendor/
node_modules/
.venv/

# Large data files
*.json  # (unless schema/config)
unified_analysis.json
collider_report.html
```

**Check patterns work:**
```bash
git status  # Should NOT show ignored files
git check-ignore -v <file>  # Test if file is ignored
```

---

### 3. Add Quality Gate

**Pre-commit hook:** (should exist in `.git/hooks/pre-commit`)

```bash
#!/bin/bash
# Prevent large artifacts

for file in $(git diff --cached --name-only); do
  # Check file size
  size=$(wc -c < "$file" 2>/dev/null || echo 0)

  if [ $size -gt 1000000 ]; then  # 1MB
    echo "❌ ERROR: Large file detected: $file ($size bytes)"
    echo "   This looks like a build artifact."
    echo "   Add to .gitignore or use git-lfs"
    exit 1
  fi

  # Check for artifact patterns
  if [[ "$file" =~ output_.*\.json$ ]]; then
    echo "❌ ERROR: Collider output detected: $file"
    echo "   Build artifacts shouldn't be committed"
    exit 1
  fi
done
```

---

### 4. Regular Cleanup

**Weekly:**
```bash
# Check for leaked artifacts
git ls-files | grep -E "output_|\.tmp_|libs/"

# If found:
git rm --cached <file>  # Untrack but keep locally
# Then add to .gitignore
```

**Before tagging release:**
```bash
# Deep clean
git clean -fdx  # Remove all untracked files
./pe verify v1  # Run quality gates
```

---

## 📋 QUALITY GATE G9: No Artifacts Committed

**Rule:** No generated files, vendor code, or temp files in git

**Check:**
```bash
python tools/verify_no_artifacts.py
# Scans git tree for:
# - Files >1MB
# - output_*.json
# - collider_report.html
# - libs/ directories
# - .tmp_* directories
```

**Threshold:** 0 violations

**Current status:** ❌ FAILED (666K lines were committed, then cleaned)

**Fix:**
1. ✅ Updated .gitignore (done)
2. ⏸️ Create verify_no_artifacts.py (todo)
3. ⏸️ Add pre-commit hook (todo)

---

## 🎓 LESSONS LEARNED

### Incident: 666K Artifact Commit (2026-01-28)

**What happened:**
- Collider test runs generated 630K lines of JSON/HTML
- Vendor libraries (35K lines) bundled in HTML reports
- All committed to git (bloated repo by 666K lines)
- Had to clean up in commit 34097ee

**Root cause:**
- `.gitignore` incomplete (missed `.collider-verify/`, `collider_pipeline_files/`)
- No pre-commit hook checking file sizes
- No quality gate preventing large commits

**Fix applied:**
- ✅ Updated .gitignore with missing patterns
- ✅ Documented in BEST_PRACTICES.md
- ⏸️ TODO: Add G9 gate + pre-commit hook

**Prevention:**
- Always check `git status` before commit
- Question any file >100KB
- Use `.gitignore` patterns liberally

---

## 🔍 HOW TO CHECK

**Before every commit:**
```bash
# 1. Check what's staged
git diff --cached --stat

# 2. Look for suspiciously large files
git diff --cached --stat | awk '{if($3>1000) print}'

# 3. Grep for artifact patterns
git diff --cached --name-only | grep -E "output_|libs/|tmp"

# If any matches, investigate before committing
```

**After cleanup:**
```bash
# Check repo is clean
du -sh .git/  # Should shrink after artifact removal

# Prune old history
git gc --aggressive --prune=now
```

---

## 📊 METRICS

**Healthy repo:**
- Source files: .py, .md, .yaml
- Small configs: <100KB
- No generated outputs
- No vendor directories

**Unhealthy repo:**
- Large JSON files (>1MB)
- Generated HTML (>500KB)
- Vendor libs committed
- Build artifacts tracked

**Our repo after cleanup:**
- Before: 666K artifact lines
- After: Clean ✅
- Lesson: Add gates to prevent recurrence

---

**This should be Gate G9 in QUALITY_GATES.md.**

Want me to add it?
