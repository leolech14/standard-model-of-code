# Dashboard Quick Reference Card

**Created:** 2026-01-28
**Status:** Ready to test
**Global Commands:** `projectome` | `refinery`

---

## 🎯 **TWO DASHBOARDS - DIFFERENT PURPOSES:**

```
┌─────────────────────────────────────────────────────────┐
│ PROJECTOME VIEWER                                       │
│ (unified-dashboard)                                     │
├─────────────────────────────────────────────────────────┤
│ Purpose:  ONE project deep analysis                     │
│ Shows:    Collider 3D graph + Refinery chunks           │
│ View:     Split screen (Code | Context)                 │
│ Port:     :3000                                         │
│ Command:  projectome                                    │
│ Use when: Analyzing Elements architecture               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ REFINERY PLATFORM                                       │
│ (refinery-platform)                                     │
├─────────────────────────────────────────────────────────┤
│ Purpose:  MULTIPLE projects management                  │
│ Shows:    Projects list, search, activity, metrics      │
│ View:     Platform dashboard (multi-tenant)             │
│ Port:     :3001                                         │
│ Command:  refinery                                      │
│ Level:    L7 → L8 (independent spinoff)                 │
│ Use when: Managing all projects, cross-project search   │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 **TO TEST RIGHT NOW:**

### **Option 1: Use Test Script**
```bash
chmod +x test-dashboards.sh
./test-dashboards.sh
# Installs both, guides you through testing
```

### **Option 2: Manual Test**

**Projectome Viewer:**
```bash
cd wave/viz/unified-dashboard
npm install
npm run dev
# Open http://localhost:3000
```

**Refinery Platform:**
```bash
cd wave/experiments/refinery-platform
npm install
npm run dev
# Open http://localhost:3001
```

### **Option 3: Global Commands (after install)**
```bash
projectome  # Starts :3000
refinery    # Starts :3001
```

---

## 📊 **WHAT EACH SHOWS:**

### **Projectome Viewer (:3000):**
- **LEFT:** Collider 3D force graph
  - Nodes = functions, classes, files
  - Edges = calls, imports, dependencies
  - Interactive (rotate, zoom, click)
  - Click node → filters chunks on right

- **RIGHT:** Refinery chunks
  - Semantic chunks from docs/code
  - Filtered by selected node
  - 2,673 chunks total
  - 539K tokens

**Integration:** Click graph node → see relevant chunks ✅

---

### **Refinery Platform (:3001):**

**6 Pages:**
1. **/** - Overview (platform stats)
2. **/projects** - All projects grid
3. **/chunks** - Chunk browser with detail panel
4. **/search** - Cross-project search with highlights
5. **/activity** - Event timeline (6h/12h/24h/48h/7d filters)
6. **/settings** - Platform configuration

**4 APIs:**
- `GET /api/v1/projects` - List tenants
- `GET /api/v1/projects/:id/chunks` - Project chunks
- `POST /api/v1/chunks/search` - Search
- `GET /api/v1/metrics` - Platform metrics

---

## 🎨 **VISUAL:**

Both use **same design system:**
- Dark theme (neutral-950 background)
- Emerald accent (#10b981)
- Glassmorphic cards (backdrop-blur)
- Smooth transitions
- Reference design from AI Studio

---

## ⚠️ **FIRST TIME SETUP:**

**Both need `npm install` once:**
```bash
# Projectome
cd wave/viz/unified-dashboard
npm install  # ~1-2 min

# Refinery
cd wave/experiments/refinery-platform
npm install  # ~1-2 min
```

**After install, commands work:**
```bash
projectome  # Just type this!
refinery    # Or this!
```

---

## 🎯 **READY TO TEST?**

**Run:**
```bash
chmod +x test-dashboards.sh
./test-dashboards.sh
```

**Or manually start one:**
```bash
cd wave/viz/unified-dashboard
npm install && npm run dev
```

**Which one do you want to test first?**
- Projectome (unified view)
- Refinery (platform)
- Both?
