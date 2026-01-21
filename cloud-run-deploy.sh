#!/bin/bash
# cloud-run-deploy.sh - Deploy the Socratic Audit to Google Cloud Run Jobs

# Configuration
PROJECT_ID=$(gcloud config get-value project)
IMAGE_NAME="gcr.io/$PROJECT_ID/socratic-audit"
JOB_NAME="socratic-audit-job"
REGION="us-central1"

echo "Using Project ID: $PROJECT_ID"

# 1. Build and Submit to Artifact Registry / GCR
echo "Building and pushing container image to GCR..."
gcloud builds submit --tag "$IMAGE_NAME" .

# 2. Create or Update the Cloud Run Job
# We use Jobs because this is a batch task, not a service.
echo "Deploying Cloud Run Job: $JOB_NAME..."
gcloud run jobs deploy "$JOB_NAME" \
    --image "$IMAGE_NAME" \
    --region "$REGION" \
    --tasks 1 \
    --max-retries 1 \
    --task-timeout 60m \
    --memory 2Gi \
    --cpu 1 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

echo "Deployment complete!"
echo "To run the job manually:"
echo "  gcloud run jobs execute $JOB_NAME --region $REGION"
echo ""
echo "To schedule it for the 'Slow & Steady' 6-hour Watchdog:"
echo "  gcloud scheduler jobs create http ${JOB_NAME}-trigger-midnight \\"
echo "    --schedule='0 0 * * *' \\"
echo "    --uri='https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run' \\"
echo "    --http-method=POST \\"
echo "    --oauth-service-account-email=$(gcloud config get-value account)"
echo ""
echo "  # Repeat for 6am, 12pm, 6pm..."
