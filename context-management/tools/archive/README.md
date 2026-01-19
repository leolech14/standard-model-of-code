# Archive Module

Manages offloading large files to Google Cloud Storage (GCS) and restoring them.

## Quick Start

```bash
# Preview what would be uploaded
./tools/archive/archive.py offload --dry-run

# Upload to GCS (keep local copies)
./tools/archive/archive.py offload

# Upload and delete local copies (free disk space)
./tools/archive/archive.py offload --delete

# List all archives
./tools/archive/archive.py list --remote

# Restore an entire archive
./tools/archive/archive.py restore archive_20260118_135934

# Restore a specific path
./tools/archive/archive.py restore archive_20260118_135934 standard-model-of-code/output/audit
```

## Structure

```
tools/archive/
├── README.md           # This file
├── config.yaml         # Configuration (bucket, paths, options)
├── archive.py          # Main script (offload, restore, list, status)
└── manifests/          # JSON manifests of each archive
    └── archive_YYYYMMDD_HHMMSS.json
```

## Configuration

Edit `config.yaml` to customize:

```yaml
gcloud:
  bucket: gs://elements-archive-2026
  account: leonardolech3@gmail.com
  storage_class: ARCHIVE

offload_paths:
  - standard-model-of-code/output/audit
  - standard-model-of-code/.collider
  # ... add more paths as needed
```

## Commands

### `offload`

Uploads configured paths to GCS.

```bash
# Preview only
./tools/archive/archive.py offload --dry-run

# Upload (keep local)
./tools/archive/archive.py offload

# Upload and delete local
./tools/archive/archive.py offload --delete
```

Each offload creates:
- A timestamped archive in GCS: `gs://bucket/archive_YYYYMMDD_HHMMSS/`
- A local manifest: `manifests/archive_YYYYMMDD_HHMMSS.json`

### `restore`

Downloads files from GCS back to local.

```bash
# Restore entire archive
./tools/archive/archive.py restore archive_20260118_135934

# Restore specific path
./tools/archive/archive.py restore archive_20260118_135934 path/to/restore
```

### `list`

Lists archives.

```bash
# Local manifests
./tools/archive/archive.py list

# Remote archives in GCS
./tools/archive/archive.py list --remote
```

### `status`

Shows current state and what's offloadable.

```bash
./tools/archive/archive.py status
```

## GCS Details

| Property | Value |
|----------|-------|
| Bucket | `gs://elements-archive-2026` |
| Account | `leonardolech3@gmail.com` |
| Storage Class | ARCHIVE |
| Cost | ~$0.0012/GB/month |

### Cost Estimation

| Data Size | Monthly Cost |
|-----------|--------------|
| 1 GB | $0.001 |
| 10 GB | $0.012 |
| 100 GB | $0.12 |
| 1 TB | $1.20 |

**Note:** ARCHIVE class has minimum 365-day storage and retrieval fees. Good for data you rarely need but want to keep.

## Manifests

Each archive creates a JSON manifest tracking:

```json
{
  "archive_id": "archive_20260118_135934",
  "created": "2026-01-18T13:59:34",
  "bucket": "gs://elements-archive-2026",
  "total_size": 3664028308,
  "total_files": 656,
  "items": [...],
  "local_deleted": true
}
```

Manifests enable:
- Easy restore without remembering paths
- Tracking what was archived when
- Verification of uploads

## Troubleshooting

### gcloud not authenticated

```bash
gcloud auth login leonardolech3@gmail.com
```

### Upload stalls

The script automatically configures sequential uploads to avoid gcloud multiprocessing bugs. If issues persist:

```bash
gcloud config set storage/process_count 1
gcloud config set storage/thread_count 1
```

### Restore fails

Check the archive exists:
```bash
gcloud storage ls gs://elements-archive-2026/archive_YYYYMMDD_HHMMSS/
```

## Migration from Old Scripts

The old `tools/offload_to_gcloud.sh` is deprecated. Use this module instead:

```bash
# Old way (deprecated)
./tools/offload_to_gcloud.sh --upload --delete

# New way
./tools/archive/archive.py offload --delete
```

Benefits of new module:
- Config-driven (no hardcoded paths)
- Manifest tracking (know what was archived)
- Proper error handling (no wildcard bugs)
- Restore capability
- Python (more robust than bash)
