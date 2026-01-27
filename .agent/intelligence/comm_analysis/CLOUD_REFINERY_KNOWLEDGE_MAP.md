# Cloud Refinery - Complete Knowledge Map
**Investigation Started:** 2026-01-27 04:00
**Principle:** Slow and steady - gather ALL knowledge before implementation
**Status:** IN PROGRESS

---

## INVESTIGATION PHASES

| Phase | Status | Objective |
|-------|--------|-----------|
| 1. Infrastructure Audit | PENDING | Map what exists in GCP |
| 2. Credential Verification | PENDING | Confirm all secrets accessible |
| 3. Cost Analysis | PENDING | Understand spending implications |
| 4. Failure Forensics | PENDING | Deep dive into socratic-audit failures |
| 5. Architecture Validation | PENDING | Verify L0-L5 design is sound |
| 6. Dependency Mapping | PENDING | What depends on what |
| 7. Risk Assessment | PENDING | What can break |
| 8. Implementation Path | PENDING | Step-by-step execution plan |

---

## PHASE 1: INFRASTRUCTURE AUDIT

### Objective
Map the EXACT current state of GCP infrastructure.

### Questions to Answer
1. What Cloud Run Jobs exist? (names, configs, last run, success rate)
2. What Cloud Schedulers exist? (triggers, schedules, targets)
3. What Docker images exist in GCR? (tags, sizes, build dates)
4. What GCS buckets/directories exist? (structure, sizes, permissions)
5. What Secrets exist in Secret Manager? (names, versions, last accessed)
6. What Service Accounts exist? (emails, roles, last used)
7. What APIs are enabled? (full list with usage)
8. What IAM policies are set? (who can access what)
9. What Cloud Scheduler triggers are active? (schedules, last run, success rate)
10. What Cloud Build history exists? (what was built, when, success rate)

### Data Collection Commands
```bash
# Cloud Run Jobs
gcloud run jobs list --region=us-central1 --format=json > /tmp/gcp_jobs.json

# Cloud Schedulers
gcloud scheduler jobs list --location=us-central1 --format=json > /tmp/gcp_schedulers.json

# Docker Images
gcloud artifacts docker images list gcr.io/elements-archive-2026 --format=json > /tmp/gcp_images.json

# GCS Buckets
gsutil ls -L gs://elements-archive-2026/** > /tmp/gcs_structure.txt

# Secrets
gcloud secrets list --format=json > /tmp/gcp_secrets.json

# Service Accounts
gcloud iam service-accounts list --format=json > /tmp/gcp_service_accounts.json

# Enabled APIs
gcloud services list --enabled --format=json > /tmp/gcp_services.json

# Cloud Build History
gcloud builds list --limit=50 --format=json > /tmp/gcp_builds.json
```

### Status
- [ ] Data collected
- [ ] Analysis complete
- [ ] Findings documented

---

## PHASE 2: CREDENTIAL VERIFICATION

### Objective
Verify ALL credentials are accessible and valid.

### Questions to Answer
1. Can we access Doppler from command line?
2. What secrets are in `gcloud-ops` project?
3. What secrets are in `ai-tools` project?
4. Are Doppler secrets in sync with Secret Manager?
5. Can local scripts authenticate to GCP?
6. Can Cloud Run jobs access secrets?
7. What API keys have rate limits? (Gemini, Vertex, etc.)
8. What are the current rate limit quotas?

### Data Collection Commands
```bash
# Doppler verification
doppler secrets --project gcloud-ops --config prd --format json > /tmp/doppler_gcloud.json
doppler secrets --project ai-tools --config dev --format json > /tmp/doppler_ai.json

# Secret Manager verification
gcloud secrets versions access latest --secret=gemini-api-key > /tmp/gemini_key.txt
gcloud secrets describe gemini-api-key --format=json > /tmp/gemini_key_meta.json

# Auth verification
gcloud auth list --format=json > /tmp/gcp_auth.json
gcloud auth application-default print-access-token > /tmp/gcp_token.txt

# Quota verification
gcloud alpha billing quotas list --service=aiplatform.googleapis.com --format=json > /tmp/vertex_quotas.json
```

### Security Checklist
- [ ] GEMINI_API_KEY accessible
- [ ] VERTEX_AI_API_KEY accessible
- [ ] GCP_SERVICE_ACCOUNT_JSON (if needed)
- [ ] Doppler↔Secret Manager sync verified
- [ ] Token expiration dates checked
- [ ] Rate limits documented

---

## PHASE 3: COST ANALYSIS

### Objective
Understand spending implications before deployment.

### Questions to Answer
1. What is current monthly GCP spend?
2. What is breakdown by service?
3. What will Cloud Refinery L0-L5 cost?
4. What are the rate limit costs? (Gemini API, Vertex AI)
5. What is storage growth rate?
6. What happens if we exceed free tier?
7. What are alert thresholds for budget?

### Data Collection Commands
```bash
# Current spend
gcloud billing accounts list --format=json > /tmp/billing_accounts.json
gcloud beta billing budgets list --billing-account=<account-id> --format=json > /tmp/budgets.json

# Service costs (estimate)
gcloud compute instances list --format=json > /tmp/compute_instances.json
gcloud run services list --format=json > /tmp/run_services.json

# Storage analysis
gsutil du -sh gs://elements-archive-2026/ > /tmp/storage_size.txt
```

### Cost Model to Build
| Service | Current Usage | Projected Usage | Monthly Cost |
|---------|---------------|-----------------|--------------|
| Cloud Storage | ? GB | +10GB (L0-L5) | $? |
| Cloud Run Jobs | ? runs | +30 runs/month | $? |
| Cloud Functions | 0 | 720 invocations/month | $? |
| Vertex AI (Gemini) | ? tokens | +5M tokens/month | $? |
| Cloud Scheduler | 5 jobs | +2 jobs | $? |

### Status
- [ ] Current spend documented
- [ ] Projected costs estimated
- [ ] Budget alerts configured
- [ ] Approval threshold clear

---

## PHASE 4: FAILURE FORENSICS

### Objective
FULLY understand why socratic-audit-job fails.

### Questions to Answer
1. What is the EXACT error message from each failure?
2. What token count is analyze.py loading?
3. Why is it 1.8M tokens when only 50 files loaded?
4. What --set is being used? (or is default loading everything?)
5. What model is being called? (gemini-3-pro vs 2.5-flash)
6. How many retry attempts happen?
7. What is the timeout sequence?
8. Does Doppler NEED to be in container? (or can use Secret Manager only?)
9. What's the repository_mirror sync latency?
10. Are there cloud-specific bugs in analyze.py?

### Data Collection Commands
```bash
# Get full logs from latest failed run
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=socratic-audit-job" \
    --limit=500 \
    --format=json \
    --freshness=3d > /tmp/socratic_logs_full.json

# Check analyze.py defaults
grep -A 10 "def main\|argparse\|--set\|--model" context-management/tools/ai/analyze.py > /tmp/analyze_defaults.txt

# Check what's in repository_mirror
gsutil ls -lh gs://elements-archive-2026/repository_mirror/latest/ > /tmp/mirror_contents.txt
```

### Root Cause Analysis Template
```
Symptom: Container exits with code 1 after 12m 42s
├── Direct Cause: ?
│   ├── Contributing Factor 1: ?
│   └── Contributing Factor 2: ?
├── Configuration Issue: ?
└── Code Bug: ?

Fix Options:
1. ?
2. ?
3. ?

Chosen Fix: ?
Rationale: ?
```

### Status
- [ ] Logs analyzed
- [ ] Root cause identified
- [ ] Fix options documented
- [ ] Test plan created

---

## PHASE 5: ARCHITECTURE VALIDATION

### Objective
Verify the Cloud Refinery L0-L5 design is theoretically and practically sound.

### Questions to Answer
1. Is the 6-layer distillation the right architecture?
2. Are layers sequential (L0→L1→L2...) or parallel?
3. What triggers each layer's processing?
4. What are the data dependencies between layers?
5. What happens if enrichment fails mid-pipeline?
6. How do we version the schema as it evolves?
7. What's the rollback strategy if L3 produces bad data?
8. How do we validate each layer's output?
9. What monitoring/observability exists per layer?
10. Is there a simpler architecture that achieves 80% of value?

### Validation Checklist
- [ ] Peirce's semiotics mapping reviewed
- [ ] Friston's Free Energy Principle applied correctly
- [ ] Layer dependencies validated
- [ ] Failure modes identified
- [ ] Simpler alternatives considered
- [ ] Academic grounding confirmed

---

## PHASE 6: DEPENDENCY MAPPING

### Objective
Understand what depends on what (avoid breaking existing systems).

### Questions to Answer
1. What local tools query GCS? (archive.py, sync scripts, etc.)
2. What cloud jobs read from `repository_mirror/`?
3. What expects `intelligence/` outputs?
4. Will creating `projectome/` conflict with existing structure?
5. What scripts parse `unified_analysis.json`?
6. What would break if we change output formats?
7. Are there race conditions in GCS writes?
8. What monitoring expects certain file structures?

### Dependency Graph to Build
```
Local Tools
├── wire.py → writes where?
├── archive.py → reads/writes what?
├── analyze.py → expects what in GCS?
└── enrichment_orchestrator.py → depends on what?

Cloud Jobs
├── socratic-audit-job → reads repository_mirror/, writes intelligence/
└── (future) refinery-L0-L1 → reads projectome/L0_raw/, writes L1_indexed/

GCS Structure
├── repository_mirror/ → who writes? who reads?
├── intelligence/ → who writes? who reads?
└── projectome/ (NEW) → who will write? who will read?
```

### Status
- [ ] Dependency graph created
- [ ] Breaking changes identified
- [ ] Migration path documented

---

## PHASE 7: RISK ASSESSMENT

### Objective
Identify what can go wrong and how to mitigate.

### Risks to Assess

**Infrastructure Risks:**
- [ ] GCS bucket permissions misconfigured
- [ ] Cloud Run job pulls wrong repo version
- [ ] Secret Manager key rotation breaks jobs
- [ ] Rate limits cause cascade failures
- [ ] Storage costs spiral out of control

**Data Risks:**
- [ ] Corrupt unified_analysis.json uploaded
- [ ] Schema changes break downstream consumers
- [ ] Duplicate snapshots waste storage
- [ ] Historical data lost during migration

**Operational Risks:**
- [ ] Jobs run during high-activity periods
- [ ] Multiple jobs write to same file (race condition)
- [ ] Monitoring alerts not configured
- [ ] No rollback procedure if deployment fails

**Cost Risks:**
- [ ] Vertex AI costs exceed budget
- [ ] Storage growth unbounded
- [ ] API call costs uncapped
- [ ] No spending alerts configured

### Mitigation Strategies
Each risk needs:
1. Prevention: How to avoid
2. Detection: How to know it happened
3. Recovery: How to fix if it happens

### Status
- [ ] Risks enumerated
- [ ] Mitigations planned
- [ ] Rollback procedures documented

---

## PHASE 8: IMPLEMENTATION PATH

### Objective
Create step-by-step execution plan with verification at each step.

### Implementation Principles
1. **Idempotent** - Safe to run multiple times
2. **Reversible** - Can roll back any step
3. **Observable** - Verify success before proceeding
4. **Minimal** - Deploy smallest working unit first
5. **Tested** - Verify locally before cloud deployment

### Execution Sequence (TBD after Phases 1-7)
```
Step 1: ?
  Command: ?
  Verification: ?
  Rollback: ?
  Risk: ?

Step 2: ?
  ...
```

### Status
- [ ] Execution plan created
- [ ] Each step has verification
- [ ] Rollback procedures defined
- [ ] Risk assessment per step complete

---

## KNOWLEDGE GAPS (To Be Filled)

### Critical Unknowns
- [ ] What is the EXACT token count analyze.py is loading?
- [ ] Why does it think 50 files = 1.8M tokens?
- [ ] What context sets exist and what's their size?
- [ ] What's in repository_mirror/latest/ right now?
- [ ] Are there multiple versions of analyze.py?
- [ ] What's the --set flag default?
- [ ] Is Doppler required or optional in cloud?

### Research Questions
- [ ] Best practices for Cloud Run + Gemini API (2026 patterns)
- [ ] Vertex AI Pipelines vs Cloud Functions for batch enrichment
- [ ] Cost optimization for continuous AI processing
- [ ] GCS lifecycle policies for L0 retention
- [ ] Monitoring setup for AI pipeline failures

### Documentation Gaps
- [ ] No runbook for Cloud Run job maintenance
- [ ] No troubleshooting guide for rate limits
- [ ] No deployment checklist
- [ ] No rollback procedures documented
- [ ] No cost monitoring setup

---

## NEXT STEPS - KNOWLEDGE GATHERING

### Immediate (Next 30 minutes)
1. Collect all GCP state (commands in Phase 1)
2. Analyze socratic-audit logs in detail
3. Map analyze.py behavior with different --set flags
4. Document current GCS structure fully

### Short-term (Next 2 hours)
5. Verify all credentials accessible via Doppler
6. Build cost model for Cloud Refinery L0-L5
7. Create dependency graph
8. Document risks and mitigations

### Before Implementation
9. Create complete execution plan
10. Get user approval on approach
11. Set up monitoring/alerts
12. Define success criteria

---

## INVESTIGATION LOG

### Entry 001 - 2026-01-27 04:00

**Action:** Starting comprehensive knowledge gathering

**Principle:** "Refinery" mode - slow, steady, complete understanding before action.

**Plan:**
- Phase 1-7: Gather knowledge (investigation)
- Phase 8: Plan implementation (design)
- Phase 9: Execute deployment (only after 1-8 complete)

**Status:** Phase 1 starting now.

---
