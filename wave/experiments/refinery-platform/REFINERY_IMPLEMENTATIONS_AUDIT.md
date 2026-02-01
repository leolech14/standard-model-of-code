# Refinery/Dashboard Implementations Audit

**Date:** 2026-01-28
**Purpose:** Identify all implementations and eliminate duplicates
**Problem:** Multiple agents have built dashboard/refinery apps - need consolidation

---

## 🔍 **INVENTORY (Found 8 implementations!)**

### ✅ **ACTIVE: unified-dashboard** (MOST COMPLETE)

```
Location: wave/viz/unified-dashboard/
Stack: Next.js 15 + TypeScript + Tailwind
Status: BUILT & RUN (.next/ exists!)
Features:
  ✅ Collider 3D graph (GraphView.tsx)
  ✅ Refinery chunks integration
  ✅ Node click → chunks filter
  ✅ Split view (Collider | Refinery)
  ✅ API routes (collider/graph, refinery/chunks)
  ✅ Real-time data loading
  ✅ 14KB page.tsx (substantial implementation)

Who built: Previous agent(s)
Last modified: Jan 28 16:48 (TODAY!)
Ready to run: YES (just needs npm install)
```

**RECOMMENDATION: THIS IS THE CANONICAL ONE!** ⭐

---

### ⚠️ **DUPLICATE: refinery-platform** (What I built today)

```
Location: wave/experiments/refinery-platform/
Stack: Next.js 15 + TypeScript + Tailwind
Status: NEW (built today 18:00-18:30)
Features:
  ✅ 6 pages (Overview, Projects, Chunks, Search, Activity, Settings)
  ✅ 4 API routes
  ✅ Multi-tenant architecture
  ✅ Sidebar navigation
  ✅ L7 platform thinking

Who built: Me (Claude Gen 6)
Last modified: Jan 28 18:11 (1 hour ago)
Ready to run: Needs npm install
```

**PROBLEM:** Duplicates unified-dashboard! ❌

**OPTIONS:**
1. **DELETE refinery-platform** (use unified-dashboard instead)
2. **MERGE** best features from both
3. **KEEP BOTH** (different purposes? - unlikely)

---

### ⚠️ **EXPERIMENTAL: refinery-dashboard**

```
Location: wave/experiments/refinery-dashboard/
Stack: Next.js 15
Status: Minimal (just GCP job triggering)
Features:
  ⚠️ One button (triggers socratic-audit-job)
  ✅ Has reference_design/ from AI Studio (UI patterns)
  ⚠️ Incomplete

Last modified: Jan 28 01:41
Ready: Needs npm install
```

**RECOMMENDATION:** Archive or delete (superseded)

---

### 📦 **ARCHIVED: FastAPI Dashboard**

```
Location: particle/archive/legacy_experiments/dashboard/
Stack: FastAPI (Python) + static HTML/JS
Status: ARCHIVED (complete but old)
Features:
  ✅ 20 API endpoints (butlers, knowledge, cloud, health, etc.)
  ✅ Static HTML frontend
  ✅ Docker + Cloud Run ready
  ⚠️ Old stack (not Next.js)

Last modified: Jan 27 19:26
Ready: Yes (uvicorn main:app)
```

**RECOMMENDATION:** Keep archived as reference for API endpoints

---

### 🗄️ **ARCHIVED: palace-dashboard**

```
Location: wave/archive/intelligence/legacy/
Status: Old, archived
```

**RECOMMENDATION:** Keep archived

---

### 🗄️ **ARCHIVED: orphaned_dashboard_web_2025**

```
Location: wave/archive/
Status: Orphaned, archived
```

**RECOMMENDATION:** Can delete

---

### 🗄️ **ARCHIVED: temporal_dashboard**

```
Location: particle/archive/legacy_experiments/
Status: Old experiment
```

**RECOMMENDATION:** Keep archived

---

### ✅ **ACTIVE: Python Refinery Tools**

```
Location: wave/tools/refinery/
Type: CLI tools (NOT web dashboards)
Files:
  - corpus_inventory.py (scanner)
  - query_chunks.py (search)
  - refinery_report.py (reporting)
  - state_synthesizer.py
  - subsystem_registry.py
  - reference_analyzer.py

Status: ACTIVE - backend processing tools
```

**RECOMMENDATION:** Keep - these are tools, not dashboards

---

### ✅ **ACTIVE: ACI Refinery**

```
Location: wave/tools/ai/aci/refinery.py
Type: Chunking implementation (34KB)
Status: ACTIVE - core chunking logic
```

**RECOMMENDATION:** Keep - this is the backend

---

## ⚠️ **DUPLICATION ANALYSIS:**

### **Web Dashboards (3 active, 4 archived):**

**ACTIVE:**
1. **unified-dashboard** (complete, has Collider+Refinery)
2. **refinery-platform** (new, multi-tenant L7 platform) ← **I JUST BUILT THIS!**
3. **refinery-dashboard** (minimal, GCP trigger only)

**ARCHIVED:**
4. FastAPI dashboard
5. palace-dashboard
6. orphaned_dashboard_web_2025
7. temporal_dashboard

**PROBLEM:** unified-dashboard and refinery-platform OVERLAP!

---

## 🎯 **CONSOLIDATION PLAN:**

### **Option A: Use unified-dashboard (Recommended)**

**Why:**
- ✅ Already complete (Collider 3D + Refinery)
- ✅ Has been run (.next/ exists)
- ✅ Integrates both systems
- ✅ Built by previous agent(s)
- ✅ 14KB page.tsx (substantial)

**Action:**
1. Delete refinery-platform (duplicate)
2. Use unified-dashboard as canonical
3. Add missing features to unified-dashboard if needed

---

### **Option B: Merge Both**

**Why:**
- refinery-platform has multi-tenant architecture
- refinery-platform has more pages (6 vs unknown)
- refinery-platform has L7 platform thinking

**Action:**
1. Copy multi-tenant features to unified-dashboard
2. Delete refinery-platform
3. Consolidate into one

---

### **Option C: Keep Both (Not Recommended)**

**Why:**
- Different purposes?
  - unified-dashboard = Elements-specific
  - refinery-platform = Multi-project platform

**Problem:** Still duplication, maintenance burden 2×

---

## 💡 **MY HONEST RECOMMENDATION:**

### **STOP! CHECK unified-dashboard FIRST!**

**Before deciding:**
1. Run `cd wave/viz/unified-dashboard && npm install && npm run dev`
2. See what it actually does
3. Compare features with refinery-platform
4. THEN decide which to keep

**Likely outcome:**
- unified-dashboard has everything we need ✅
- Delete refinery-platform (my duplication) ❌
- Extract v6 reference to unified-dashboard for any missing UI ✅

---

## 🌍 **MAKING IT GLOBALLY DISCOVERABLE:**

### **After Consolidation:**

```bash
# 1. Symlink to ~/bin or ~/.local/bin
ln -s /Users/lech/PROJECTS_all/PROJECT_elements/wave/viz/unified-dashboard \
      ~/refinery-dashboard

# 2. Create global command
echo '#!/bin/bash
cd ~/refinery-dashboard && npm run dev' > ~/bin/refinery
chmod +x ~/bin/refinery

# 3. Add to PATH in ~/.zshrc
export PATH="$HOME/bin:$PATH"

# 4. Add to CLAUDE.md globally
# ~/.claude/CLAUDE.md:
## Refinery Platform
Location: ~/refinery-dashboard
Command: refinery (starts on :3001)
Purpose: Multi-tenant context processing
```

**Then any AI can:**
```
"Start Refinery" → runs ~/bin/refinery → opens :3001
"Where is Refinery?" → ~/refinery-dashboard
```

---

## 🎯 **IMMEDIATE ACTION NEEDED:**

**Leonardo, we need to:**
1. **Check unified-dashboard** (does it have everything?)
2. **Delete duplicates** (refinery-platform if unified-dashboard is complete)
3. **Extract v6 reference** (use newest UI from your download)
4. **Make globally discoverable** (symlink + command)

**Should I:**
- **Check unified-dashboard first** (see what it has)
- **Or continue with refinery-platform** (might be duplicate work)

**What do you want to do?**
