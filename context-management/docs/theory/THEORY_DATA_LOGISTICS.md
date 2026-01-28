# Theory of Data Logistics

> "What is the first thing we do with data? We Categorize it, Describe it, Act on it (or not), and Preserve the original."

## The First Thing Ritual
Every data entity entering the **Refinery** must undergo the following mechanical steps, verified by code.

### 1. Categorization (Identity)
**"Give it a name."**
- **Mechanism**: `corpus_inventory.py` mints a `Parcel ID` (`pcl_...`).
- **Theory**: Data without identity is noise. We assign a unique, persistent identifier immediately upon contact.

### 2. Description (Metadata)
**"Describe it."**
- **Mechanism**: The `Waybill` system (`waybill={...}`).
- **Theory**: A parcel must carry its history. The Waybill tracks provenance, route, and handling events (Who touched it? When? Why?).

### 3. Action (The Gate)
**"Do something with it (or not)."**
- **Mechanism**: The **Attention Mechanism Gate** in `Refinery.py`.
- **Theory**: Not all data deserves to become Context using resources.
    - **Laminar Flow**: High purity, selective retention.
    - **Turbulent Flow**: Broad retention for exploration.
    - **No-Act**: Filtered data is acknowledged but not processed into chunks.

### 4. Preservation (Immutable Source)
**"We always keep the original files."**
- **Mechanism**: Read-only access by all extractors.
- **Theory**: The Source (`Codome`) is sacred. The Refinery produces *refined goods* (`Nodes`, `Chunks`) but never alters the raw material during ingestion.

## Logistics Architecture

| Component | Ritual Step | Implementation |
|-----------|-------------|----------------|
| `corpus_inventory.py` | Identity & Preservation | Scans files, mints IDs, treats FS as read-only. |
| `pipeline.py` | Description | Initializes Batch IDs and orchestrates Waybills. |
| `refinery.py` | Action | Applies Semantic Gates to filter Flows. |

