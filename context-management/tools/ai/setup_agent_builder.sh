#!/bin/bash

# SETUP VERTEX AI AGENT BUILDER
# =============================
# This script guides you through setting up a "Chat with Codebase" app
# using the Google Cloud Console.

PROJECT_ID=$(gcloud config get-value project)
BUCKET_NAME="elements-archive-2026"
MIRROR_PATH="gs://${BUCKET_NAME}/repository_mirror/latest/"

echo "========================================================"
echo "   VERTEX AI AGENT BUILDER SETUP GUIDE"
echo "========================================================"
echo ""
echo "Current Project: $PROJECT_ID"
echo "Target Source:   $MIRROR_PATH"
echo ""
echo "Since CLI automation for Agent Builder is restricted,"
echo "please follow these steps in your browser:"
echo ""
echo "1. Open the Data Stores page:"
echo "   https://console.cloud.google.com/gen-app-builder/data-stores?project=$PROJECT_ID"
echo ""
echo "2. Click [CREATE DATA STORE]"
echo "   - Source: Cloud Storage"
echo "   - Folder: $MIRROR_PATH"
echo "   - Data type: Unstructured documents (content)"
echo ""
echo "3. Create a Search/Chat App"
echo "   - Link it to the Data Store you just created."
echo ""
echo "4. Done! You can now chat with your repo."
echo ""
echo "To open the console now, press Enter. (Ctrl+C to cancel)"
read -r response

open "https://console.cloud.google.com/gen-app-builder/data-stores?project=$PROJECT_ID"
