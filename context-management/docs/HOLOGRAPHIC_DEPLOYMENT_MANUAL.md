# Holographic Deployment Manual
> **Precision Guide for Re-instantiating the Socratic Layer**

**Artifact ID**: `HOLOGRAPHIC_DEPLOYMENT_MANUAL`
**Generation**: 1
**Status**: ACTIVE

---

## 🏗️ 1. Architecture

The system runs as a **Google Cloud Run Job** (Batch processing), not a service.
- **Engine**: Docker (Python 3.10 + Tree-sitter + GCloud SDK)
- **Context**: Dynamic Runtime Sync (Pulls from GCS Mirror)
- **Output**: JSON Intelligence Pushed to GCS

## 🛠️ 2. Capabilities Profile
The container includes the "Full Power" suite:
- `tree-sitter` (Python, Rust, Go, Java, JS, TS)
- `networkx` (Graph Analysis)
- `google-cloud-sdk` (Synchronization)

## 🚀 3. Deployment Procedure

### A. Pre-requisites
Ensure these files exist in `PROJECT_elements/`:
1. `Dockerfile` (The Engine)
2. `cloud-entrypoint.sh` (The Bootloader)
3. `cloud-run-deploy.sh` (The Launcher)

### B. One-Click Deployment
To build the image and update the job definition:

```bash
./cloud-run-deploy.sh
```

*(This script handles the sticky `apt-key` GPG issues automatically via the updated Dockerfile).*

### C. The Triggers (Slow & Steady)
The system is designed for a "Quartet Watchdog" schedule (every 6 hours).

**1. Establish Trigger Identity (Critical)**
Cloud Scheduler needs a dedicated identity to invoke Cloud Run.
```bash
# Create Service Account
gcloud iam service-accounts create socratic-trigger-sa --display-name "Socratic Trigger Service Account"

# Grant Invoker Permission
gcloud projects add-iam-policy-binding elements-archive-2026 \
  --member="serviceAccount:socratic-trigger-sa@elements-archive-2026.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

**2. Create the Midnight Trigger**
```bash
gcloud scheduler jobs create http socratic-audit-job-trigger-midnight \
  --schedule="0 0 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/elements-archive-2026/jobs/socratic-audit-job:run" \
  --http-method=POST \
  --location=us-central1 \
  --oidc-service-account-email=socratic-trigger-sa@elements-archive-2026.iam.gserviceaccount.com \
  --oidc-token-audience="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/elements-archive-2026/jobs/socratic-audit-job:run"
```

**3. Create the Morning Trigger (6 AM)**
```bash
gcloud scheduler jobs create http socratic-audit-job-trigger-morning \
  --schedule="0 6 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/elements-archive-2026/jobs/socratic-audit-job:run" \
  --http-method=POST \
  --location=us-central1 \
  --oidc-service-account-email=socratic-trigger-sa@elements-archive-2026.iam.gserviceaccount.com \
  --oidc-token-audience="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/elements-archive-2026/jobs/socratic-audit-job:run"
```

*(Repeat for 12 PM `0 12 * * *` and 6 PM `0 18 * * *`)*

## 🔍 4. Verification

**Manual Run:**
```bash
gcloud run jobs execute socratic-audit-job --region us-central1
```

**Check Logs:**
```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=socratic-audit-job" --limit 20
```

## ⚠️ 5. Troubleshooting Reference

**Issue: `apt-key` errors during build**
- **Fix**: Don't use `apt-key add`. Use `signed-by` in `sources.list.d`. The current `Dockerfile` implements this fix.

**Issue: `PERMISSION_DENIED` on Cloud Build**
- **Fix**: Grant the Cloud Build Service Account (`[PROJECT_NUMBER]@cloudbuild.gserviceaccount.com`) the `roles/run.admin` and `roles/iam.serviceAccountUser` roles.

---
*Created by the Holographic-Socratic Layer - Generation 1*
