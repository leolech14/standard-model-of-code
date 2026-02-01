#!/usr/bin/env python3
"""
Image Browser - Navigate reference images with a web UI.

Features:
- Directory tree visualization
- Tagging system (create, apply, group)
- Action queue (delete marks generate report, confirm before execute)

Usage:
    python image_browser.py                           # Default: wave/archive/references/images
    python image_browser.py /path/to/images          # Custom folder
    python image_browser.py --port 8080              # Custom port
"""

import sys
import json
import mimetypes
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote, parse_qs
import csv
from datetime import datetime

DEFAULT_PORT = 8765
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_IMAGES_DIR = PROJECT_ROOT / "wave/archive/references/images"
SCORES_FILE = PROJECT_ROOT / "tools/image_scores_precision.csv"
TAGS_FILE = PROJECT_ROOT / "tools/image_tags.json"
ACTIONS_FILE = PROJECT_ROOT / "tools/pending_actions.json"

# Global state
IMAGES_ROOT = None
SCORES = {}
TAGS = {}  # {image_path: [tag1, tag2, ...]}
TAG_DEFINITIONS = {}  # {tag_name: {color: ..., description: ...}}
PENDING_ACTIONS = []  # [{action: 'delete', path: ..., timestamp: ...}, ...]


def load_scores():
    """Load image scores from CSV if available."""
    global SCORES
    if SCORES_FILE.exists():
        try:
            with open(SCORES_FILE) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    path = row['path']
                    SCORES[path] = {
                        'score': float(row['score']) if row['score'] else 0,
                        'verdict': row['verdict'],
                        'reason': row['reason'],
                        'width': int(row['width']) if row['width'] else 0,
                        'height': int(row['height']) if row['height'] else 0,
                    }
            print(f"Loaded {len(SCORES)} image scores")
        except Exception as e:
            print(f"Could not load scores: {e}")


def load_tags():
    """Load tags from JSON file."""
    global TAGS, TAG_DEFINITIONS
    if TAGS_FILE.exists():
        try:
            with open(TAGS_FILE) as f:
                data = json.load(f)
                TAGS = data.get('image_tags', {})
                TAG_DEFINITIONS = data.get('tag_definitions', {})
            print(f"Loaded {len(TAGS)} image tags, {len(TAG_DEFINITIONS)} tag definitions")
        except Exception as e:
            print(f"Could not load tags: {e}")


def save_tags():
    """Save tags to JSON file."""
    with open(TAGS_FILE, 'w') as f:
        json.dump({
            'image_tags': TAGS,
            'tag_definitions': TAG_DEFINITIONS
        }, f, indent=2)


def load_actions():
    """Load pending actions from JSON file."""
    global PENDING_ACTIONS
    if ACTIONS_FILE.exists():
        try:
            with open(ACTIONS_FILE) as f:
                PENDING_ACTIONS = json.load(f)
            print(f"Loaded {len(PENDING_ACTIONS)} pending actions")
        except Exception as e:
            print(f"Could not load actions: {e}")


def save_actions():
    """Save pending actions to JSON file."""
    with open(ACTIONS_FILE, 'w') as f:
        json.dump(PENDING_ACTIONS, f, indent=2)


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Browser</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            min-height: 100vh;
        }

        .container {
            display: grid;
            grid-template-columns: 300px 1fr;
            min-height: 100vh;
        }

        /* Sidebar */
        .sidebar {
            background: linear-gradient(180deg, #12121a 0%, #0d0d12 100%);
            border-right: 1px solid #1e1e2e;
            overflow-y: auto;
            position: sticky;
            top: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid #1e1e2e;
        }

        .sidebar h1 {
            font-size: 1.2rem;
            color: #7c8aff;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .sidebar h1::before {
            content: "◈";
            font-size: 1.4rem;
        }

        .stats {
            font-size: 0.75rem;
            color: #666;
        }

        /* Tabs */
        .sidebar-tabs {
            display: flex;
            border-bottom: 1px solid #1e1e2e;
        }

        .sidebar-tab {
            flex: 1;
            padding: 12px;
            text-align: center;
            cursor: pointer;
            font-size: 0.8rem;
            color: #666;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }

        .sidebar-tab:hover {
            color: #aaa;
        }

        .sidebar-tab.active {
            color: #7c8aff;
            border-bottom-color: #7c8aff;
        }

        .sidebar-content {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
        }

        .tab-panel {
            display: none;
        }

        .tab-panel.active {
            display: block;
        }

        /* Folder tree */
        .folder-tree {
            list-style: none;
        }

        .folder-item {
            padding: 8px 10px;
            margin: 2px 0;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s;
            font-size: 0.85rem;
        }

        .folder-item:hover {
            background: #1a1a2e;
        }

        .folder-item.active {
            background: linear-gradient(90deg, #2a2a4e 0%, #1a1a2e 100%);
            border-left: 3px solid #7c8aff;
        }

        .folder-item .count {
            background: #1e1e2e;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            color: #666;
        }

        .folder-item.active .count {
            background: #7c8aff;
            color: #0a0a0f;
        }

        .folder-icon {
            margin-right: 8px;
            opacity: 0.6;
        }

        /* Tags panel */
        .tag-section {
            margin-bottom: 20px;
        }

        .tag-section h3 {
            font-size: 0.75rem;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .tag-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .tag-chip {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
        }

        .tag-chip:hover {
            transform: scale(1.05);
        }

        .tag-chip.active {
            border-color: #fff;
        }

        .new-tag-input {
            width: 100%;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #2a2a4e;
            background: #0a0a0f;
            color: #e0e0e0;
            font-size: 0.85rem;
            margin-top: 10px;
        }

        .new-tag-input:focus {
            outline: none;
            border-color: #7c8aff;
        }

        /* Actions panel */
        .action-queue {
            list-style: none;
        }

        .action-item {
            padding: 10px;
            margin: 4px 0;
            border-radius: 6px;
            background: #1a1a1a;
            font-size: 0.8rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .action-item.delete {
            border-left: 3px solid #f87171;
        }

        .action-item .remove-action {
            color: #666;
            cursor: pointer;
            padding: 4px;
        }

        .action-item .remove-action:hover {
            color: #f87171;
        }

        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .btn {
            flex: 1;
            padding: 10px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.2s;
        }

        .btn-primary {
            background: #7c8aff;
            color: #0a0a0f;
        }

        .btn-primary:hover {
            background: #9ba6ff;
        }

        .btn-danger {
            background: #3a1a1a;
            color: #f87171;
            border: 1px solid #f87171;
        }

        .btn-danger:hover {
            background: #f87171;
            color: #0a0a0f;
        }

        .btn-secondary {
            background: #1e1e2e;
            color: #888;
        }

        .btn-secondary:hover {
            background: #2a2a4e;
            color: #fff;
        }

        /* Main content */
        .main {
            padding: 20px 30px;
            overflow-y: auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #1e1e2e;
        }

        .header h2 {
            font-size: 1.4rem;
            color: #fff;
        }

        .controls {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .view-toggle {
            display: flex;
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid #2a2a4e;
        }

        .view-btn {
            padding: 6px 12px;
            background: transparent;
            border: none;
            color: #666;
            cursor: pointer;
            font-size: 0.8rem;
        }

        .view-btn:hover {
            color: #aaa;
        }

        .view-btn.active {
            background: #7c8aff;
            color: #0a0a0f;
        }

        .filter-btn {
            padding: 6px 14px;
            border-radius: 6px;
            border: 1px solid #2a2a4e;
            background: transparent;
            color: #888;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.2s;
        }

        .filter-btn:hover {
            border-color: #7c8aff;
            color: #7c8aff;
        }

        .filter-btn.active {
            background: #7c8aff;
            border-color: #7c8aff;
            color: #0a0a0f;
        }

        .size-slider {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8rem;
            color: #666;
        }

        .size-slider input {
            width: 80px;
        }

        /* Image grid */
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(var(--thumb-size, 180px), 1fr));
            gap: 16px;
        }

        /* Tree view */
        .tree-view {
            display: none;
        }

        .tree-view.active {
            display: block;
        }

        .image-grid.active {
            display: grid;
        }

        .tree-folder {
            margin-bottom: 30px;
        }

        .tree-folder-header {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 15px;
            background: #12121a;
            border-radius: 8px;
            margin-bottom: 15px;
            cursor: pointer;
        }

        .tree-folder-header:hover {
            background: #1a1a2e;
        }

        .tree-folder-header h3 {
            font-size: 1rem;
            color: #7c8aff;
        }

        .tree-folder-header .folder-count {
            font-size: 0.8rem;
            color: #666;
        }

        .tree-folder-images {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 12px;
            padding-left: 20px;
        }

        /* Image card */
        .image-card {
            background: #12121a;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #1e1e2e;
            transition: all 0.2s;
            cursor: pointer;
            position: relative;
        }

        .image-card:hover {
            border-color: #7c8aff;
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(124, 138, 255, 0.15);
        }

        .image-card.selected {
            border-color: #7c8aff;
            box-shadow: 0 0 0 2px #7c8aff;
        }

        .image-card.marked-delete {
            opacity: 0.5;
            border-color: #f87171;
        }

        .image-card .select-checkbox {
            position: absolute;
            top: 8px;
            left: 8px;
            width: 20px;
            height: 20px;
            border-radius: 4px;
            background: rgba(0,0,0,0.6);
            border: 2px solid #444;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: transparent;
            z-index: 10;
        }

        .image-card.selected .select-checkbox {
            background: #7c8aff;
            border-color: #7c8aff;
            color: #0a0a0f;
        }

        .image-card .thumb {
            width: 100%;
            aspect-ratio: 1;
            object-fit: contain;
            background: #0a0a0f;
            padding: 6px;
        }

        .image-card .info {
            padding: 8px 10px;
            border-top: 1px solid #1e1e2e;
        }

        .image-card .name {
            font-size: 0.7rem;
            color: #888;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 4px;
        }

        .image-card .meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.65rem;
            color: #555;
        }

        .image-card .tags {
            display: flex;
            gap: 3px;
            flex-wrap: wrap;
            margin-top: 4px;
        }

        .image-card .mini-tag {
            padding: 1px 5px;
            border-radius: 3px;
            font-size: 0.6rem;
        }

        .verdict {
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.6rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .verdict.keep { background: #1a3a1a; color: #4ade80; }
        .verdict.review { background: #3a3a1a; color: #facc15; }
        .verdict.delete { background: #3a1a1a; color: #f87171; }

        /* Selection toolbar */
        .selection-toolbar {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: #1a1a2e;
            border: 1px solid #2a2a4e;
            border-radius: 12px;
            padding: 12px 20px;
            display: none;
            gap: 15px;
            align-items: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            z-index: 100;
        }

        .selection-toolbar.active {
            display: flex;
        }

        .selection-toolbar .count {
            font-size: 0.9rem;
            color: #7c8aff;
            font-weight: 600;
        }

        .selection-toolbar .btn {
            padding: 8px 16px;
        }

        /* Tag modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 200;
            justify-content: center;
            align-items: center;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: #12121a;
            border: 1px solid #2a2a4e;
            border-radius: 12px;
            padding: 25px;
            width: 400px;
            max-width: 90%;
        }

        .modal-content h3 {
            margin-bottom: 20px;
            color: #fff;
        }

        .modal-content .tag-options {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }

        .modal-content input {
            width: 100%;
            padding: 10px 12px;
            border-radius: 6px;
            border: 1px solid #2a2a4e;
            background: #0a0a0f;
            color: #e0e0e0;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }

        .modal-buttons {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }

        /* Lightbox */
        .lightbox {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.95);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            padding: 40px;
        }

        .lightbox.active {
            display: flex;
        }

        .lightbox img {
            max-width: 90%;
            max-height: 75vh;
            object-fit: contain;
        }

        .lightbox .caption {
            margin-top: 20px;
            color: #888;
            font-size: 0.9rem;
            text-align: center;
        }

        .lightbox .close {
            position: absolute;
            top: 20px;
            right: 30px;
            font-size: 2rem;
            color: #666;
            cursor: pointer;
        }

        .lightbox .close:hover {
            color: #fff;
        }

        .lightbox .nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            font-size: 3rem;
            color: #444;
            cursor: pointer;
            padding: 20px;
        }

        .lightbox .nav:hover {
            color: #fff;
        }

        .lightbox .nav.prev { left: 20px; }
        .lightbox .nav.next { right: 20px; }

        .lightbox .image-actions {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }

        /* Confirmation modal */
        .confirm-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.9);
            z-index: 300;
            justify-content: center;
            align-items: center;
        }

        .confirm-modal.active {
            display: flex;
        }

        .confirm-content {
            background: #12121a;
            border: 1px solid #f87171;
            border-radius: 12px;
            padding: 30px;
            width: 500px;
            max-width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }

        .confirm-content h3 {
            color: #f87171;
            margin-bottom: 20px;
        }

        .confirm-list {
            list-style: none;
            margin-bottom: 20px;
            max-height: 300px;
            overflow-y: auto;
        }

        .confirm-list li {
            padding: 8px;
            font-size: 0.8rem;
            color: #888;
            border-bottom: 1px solid #1e1e2e;
        }

        /* Loading */
        .loading {
            text-align: center;
            padding: 60px;
            color: #666;
        }

        .empty {
            text-align: center;
            padding: 60px;
            color: #444;
        }
    </style>
</head>
<body>
    <div class="container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <h1>Image Browser</h1>
                <div class="stats" id="stats">Loading...</div>
            </div>

            <div class="sidebar-tabs">
                <div class="sidebar-tab active" data-tab="folders">Folders</div>
                <div class="sidebar-tab" data-tab="tags">Tags</div>
                <div class="sidebar-tab" data-tab="actions">Actions</div>
            </div>

            <div class="sidebar-content">
                <!-- Folders panel -->
                <div class="tab-panel active" id="panel-folders">
                    <ul class="folder-tree" id="folders"></ul>
                </div>

                <!-- Tags panel -->
                <div class="tab-panel" id="panel-tags">
                    <div class="tag-section">
                        <h3>Filter by Tag</h3>
                        <div class="tag-list" id="tag-filters"></div>
                    </div>
                    <div class="tag-section">
                        <h3>Create New Tag</h3>
                        <input type="text" class="new-tag-input" id="new-tag-input"
                               placeholder="Enter tag name, press Enter">
                    </div>
                    <div class="tag-section">
                        <h3>All Tags</h3>
                        <div class="tag-list" id="all-tags"></div>
                    </div>
                </div>

                <!-- Actions panel -->
                <div class="tab-panel" id="panel-actions">
                    <div class="tag-section">
                        <h3>Pending Actions (<span id="action-count">0</span>)</h3>
                        <ul class="action-queue" id="action-queue"></ul>
                    </div>
                    <div class="action-buttons">
                        <button class="btn btn-secondary" onclick="clearActions()">Clear All</button>
                        <button class="btn btn-danger" onclick="showConfirmation()">Execute</button>
                    </div>
                </div>
            </div>
        </aside>

        <main class="main">
            <div class="header">
                <h2 id="current-folder">All Images</h2>
                <div class="controls">
                    <div class="view-toggle">
                        <button class="view-btn active" data-view="grid">Grid</button>
                        <button class="view-btn" data-view="tree">Tree</button>
                    </div>
                    <button class="filter-btn active" data-filter="all">All</button>
                    <button class="filter-btn" data-filter="keep">Keep</button>
                    <button class="filter-btn" data-filter="review">Review</button>
                    <div class="size-slider">
                        <span>Size:</span>
                        <input type="range" min="100" max="300" value="180" id="thumb-size">
                    </div>
                </div>
            </div>

            <div class="image-grid active" id="images">
                <div class="loading">Loading images</div>
            </div>

            <div class="tree-view" id="tree-view"></div>
        </main>
    </div>

    <!-- Selection toolbar -->
    <div class="selection-toolbar" id="selection-toolbar">
        <span class="count"><span id="selected-count">0</span> selected</span>
        <button class="btn btn-primary" onclick="openTagModal()">Add Tag</button>
        <button class="btn btn-danger" onclick="markForDelete()">Mark Delete</button>
        <button class="btn btn-secondary" onclick="clearSelection()">Clear</button>
    </div>

    <!-- Tag modal -->
    <div class="modal" id="tag-modal">
        <div class="modal-content">
            <h3>Add Tags to Selected Images</h3>
            <div class="tag-options" id="tag-modal-options"></div>
            <input type="text" id="tag-modal-input" placeholder="Or create new tag...">
            <div class="modal-buttons">
                <button class="btn btn-secondary" onclick="closeTagModal()">Cancel</button>
                <button class="btn btn-primary" onclick="applyTags()">Apply</button>
            </div>
        </div>
    </div>

    <!-- Lightbox -->
    <div class="lightbox" id="lightbox">
        <span class="close" onclick="closeLightbox()">&times;</span>
        <span class="nav prev" onclick="navImage(-1)">&#8249;</span>
        <span class="nav next" onclick="navImage(1)">&#8250;</span>
        <img id="lightbox-img" src="">
        <div class="caption" id="lightbox-caption"></div>
        <div class="image-actions">
            <button class="btn btn-primary" onclick="tagCurrentImage()">Add Tag</button>
            <button class="btn btn-danger" onclick="deleteCurrentImage()">Mark Delete</button>
        </div>
    </div>

    <!-- Confirmation modal -->
    <div class="confirm-modal" id="confirm-modal">
        <div class="confirm-content">
            <h3>⚠️ Confirm Actions</h3>
            <p style="margin-bottom: 15px; color: #888;">The following files will be deleted:</p>
            <ul class="confirm-list" id="confirm-list"></ul>
            <div class="modal-buttons">
                <button class="btn btn-secondary" onclick="closeConfirmation()">Cancel</button>
                <button class="btn btn-danger" onclick="executeActions()">Delete Files</button>
            </div>
        </div>
    </div>

    <script>
        // State
        let allImages = [];
        let allFolders = [];
        let currentFolder = null;
        let currentFilter = 'all';
        let currentView = 'grid';
        let currentTagFilter = null;
        let selectedImages = new Set();
        let currentIndex = 0;
        let tagDefinitions = {};
        let pendingActions = [];

        const TAG_COLORS = [
            '#4ade80', '#facc15', '#f87171', '#60a5fa', '#c084fc',
            '#f472b6', '#34d399', '#fbbf24', '#a78bfa', '#fb923c'
        ];

        // API functions
        async function loadFolders() {
            const res = await fetch('/api/folders');
            const data = await res.json();
            allFolders = data.folders;

            const folderList = document.getElementById('folders');
            folderList.innerHTML = '';

            const allItem = document.createElement('li');
            allItem.className = 'folder-item active';
            allItem.innerHTML = `<span><span class="folder-icon">📁</span>All Sources</span><span class="count">${data.total}</span>`;
            allItem.onclick = () => selectFolder(null, allItem);
            folderList.appendChild(allItem);

            data.folders.forEach(f => {
                const li = document.createElement('li');
                li.className = 'folder-item';
                li.innerHTML = `<span><span class="folder-icon">📂</span>${f.name}</span><span class="count">${f.count}</span>`;
                li.onclick = () => selectFolder(f.name, li);
                folderList.appendChild(li);
            });

            document.getElementById('stats').textContent =
                `${data.total} images · ${data.folders.length} sources`;
        }

        async function loadTags() {
            const res = await fetch('/api/tags');
            const data = await res.json();
            tagDefinitions = data.definitions;
            renderTagFilters();
        }

        async function loadActions() {
            const res = await fetch('/api/actions');
            pendingActions = await res.json();
            renderActions();
        }

        async function selectFolder(folder, element) {
            document.querySelectorAll('.folder-item').forEach(el => el.classList.remove('active'));
            element.classList.add('active');
            currentFolder = folder;
            document.getElementById('current-folder').textContent = folder || 'All Images';
            await loadImages();
        }

        async function loadImages() {
            const grid = document.getElementById('images');
            grid.innerHTML = '<div class="loading">Loading images</div>';

            let url = '/api/images';
            if (currentFolder) url += `?folder=${encodeURIComponent(currentFolder)}`;

            const res = await fetch(url);
            allImages = await res.json();
            renderImages();
        }

        function renderImages() {
            let images = filterImages();

            if (currentView === 'grid') {
                renderGridView(images);
            } else {
                renderTreeView(images);
            }
        }

        function filterImages() {
            let images = allImages;

            if (currentFilter !== 'all') {
                images = images.filter(img => img.verdict === currentFilter);
            }

            if (currentTagFilter) {
                images = images.filter(img => img.tags && img.tags.includes(currentTagFilter));
            }

            return images;
        }

        function renderGridView(images) {
            const grid = document.getElementById('images');
            const treeView = document.getElementById('tree-view');

            grid.classList.add('active');
            treeView.classList.remove('active');

            if (images.length === 0) {
                grid.innerHTML = '<div class="empty"><p>No images match filters</p></div>';
                return;
            }

            grid.innerHTML = images.map((img, idx) => {
                const isSelected = selectedImages.has(img.path);
                const isMarkedDelete = pendingActions.some(a => a.path === img.path && a.action === 'delete');
                const tags = img.tags || [];

                return `
                <div class="image-card ${isSelected ? 'selected' : ''} ${isMarkedDelete ? 'marked-delete' : ''}"
                     data-path="${img.path}" data-idx="${idx}">
                    <div class="select-checkbox" onclick="toggleSelect(event, '${img.path}')">✓</div>
                    <img class="thumb" src="/image/${encodeURIComponent(img.path)}"
                         loading="lazy" onclick="openLightbox(${idx})">
                    <div class="info">
                        <div class="name" title="${img.name}">${img.name}</div>
                        <div class="meta">
                            <span>${img.width}×${img.height}</span>
                            ${img.verdict ? `<span class="verdict ${img.verdict}">${img.verdict}</span>` : ''}
                        </div>
                        ${tags.length ? `<div class="tags">${tags.map(t =>
                            `<span class="mini-tag" style="background:${getTagColor(t)}">${t}</span>`
                        ).join('')}</div>` : ''}
                    </div>
                </div>`;
            }).join('');
        }

        function renderTreeView(images) {
            const grid = document.getElementById('images');
            const treeView = document.getElementById('tree-view');

            grid.classList.remove('active');
            treeView.classList.add('active');

            // Group by folder
            const byFolder = {};
            images.forEach(img => {
                const parts = img.path.split('/');
                const folder = parts[parts.length - 2] || 'root';
                if (!byFolder[folder]) byFolder[folder] = [];
                byFolder[folder].push(img);
            });

            treeView.innerHTML = Object.entries(byFolder).map(([folder, imgs]) => `
                <div class="tree-folder">
                    <div class="tree-folder-header">
                        <span>📂</span>
                        <h3>${folder}</h3>
                        <span class="folder-count">${imgs.length} images</span>
                    </div>
                    <div class="tree-folder-images">
                        ${imgs.map((img, idx) => {
                            const globalIdx = images.indexOf(img);
                            const isSelected = selectedImages.has(img.path);
                            const isMarkedDelete = pendingActions.some(a => a.path === img.path);
                            return `
                            <div class="image-card ${isSelected ? 'selected' : ''} ${isMarkedDelete ? 'marked-delete' : ''}"
                                 data-path="${img.path}">
                                <div class="select-checkbox" onclick="toggleSelect(event, '${img.path}')">✓</div>
                                <img class="thumb" src="/image/${encodeURIComponent(img.path)}"
                                     loading="lazy" onclick="openLightbox(${globalIdx})">
                                <div class="info">
                                    <div class="name">${img.name}</div>
                                </div>
                            </div>`;
                        }).join('')}
                    </div>
                </div>
            `).join('');
        }

        // Selection
        function toggleSelect(event, path) {
            event.stopPropagation();
            if (selectedImages.has(path)) {
                selectedImages.delete(path);
            } else {
                selectedImages.add(path);
            }
            updateSelectionUI();
            renderImages();
        }

        function clearSelection() {
            selectedImages.clear();
            updateSelectionUI();
            renderImages();
        }

        function updateSelectionUI() {
            const toolbar = document.getElementById('selection-toolbar');
            const count = document.getElementById('selected-count');

            if (selectedImages.size > 0) {
                toolbar.classList.add('active');
                count.textContent = selectedImages.size;
            } else {
                toolbar.classList.remove('active');
            }
        }

        // Tags
        function getTagColor(tagName) {
            if (tagDefinitions[tagName]?.color) return tagDefinitions[tagName].color;
            const hash = tagName.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
            return TAG_COLORS[hash % TAG_COLORS.length];
        }

        function renderTagFilters() {
            const container = document.getElementById('tag-filters');
            const allTags = document.getElementById('all-tags');
            const tags = Object.keys(tagDefinitions);

            container.innerHTML = tags.length ? tags.map(t => `
                <span class="tag-chip ${currentTagFilter === t ? 'active' : ''}"
                      style="background:${getTagColor(t)}"
                      onclick="filterByTag('${t}')">${t}</span>
            `).join('') : '<span style="color:#666;font-size:0.8rem">No tags yet</span>';

            allTags.innerHTML = tags.map(t => `
                <span class="tag-chip" style="background:${getTagColor(t)}">${t}</span>
            `).join('');
        }

        function filterByTag(tag) {
            currentTagFilter = currentTagFilter === tag ? null : tag;
            renderTagFilters();
            renderImages();
        }

        function openTagModal() {
            const modal = document.getElementById('tag-modal');
            const options = document.getElementById('tag-modal-options');

            options.innerHTML = Object.keys(tagDefinitions).map(t => `
                <span class="tag-chip" style="background:${getTagColor(t)}"
                      onclick="this.classList.toggle('active')" data-tag="${t}">${t}</span>
            `).join('');

            document.getElementById('tag-modal-input').value = '';
            modal.classList.add('active');
        }

        function closeTagModal() {
            document.getElementById('tag-modal').classList.remove('active');
        }

        async function applyTags() {
            const selectedTags = [...document.querySelectorAll('#tag-modal-options .tag-chip.active')]
                .map(el => el.dataset.tag);
            const newTag = document.getElementById('tag-modal-input').value.trim();

            if (newTag) selectedTags.push(newTag);

            if (selectedTags.length === 0) {
                closeTagModal();
                return;
            }

            const paths = [...selectedImages];

            await fetch('/api/tags', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ paths, tags: selectedTags })
            });

            await loadTags();
            await loadImages();
            closeTagModal();
            clearSelection();
        }

        // Actions
        function markForDelete() {
            const paths = [...selectedImages];
            paths.forEach(path => {
                if (!pendingActions.some(a => a.path === path)) {
                    pendingActions.push({
                        action: 'delete',
                        path: path,
                        timestamp: new Date().toISOString()
                    });
                }
            });
            saveActions();
            clearSelection();
            renderImages();
        }

        function removeAction(idx) {
            pendingActions.splice(idx, 1);
            saveActions();
            renderImages();
        }

        function clearActions() {
            pendingActions = [];
            saveActions();
            renderImages();
        }

        async function saveActions() {
            await fetch('/api/actions', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(pendingActions)
            });
            renderActions();
        }

        function renderActions() {
            const queue = document.getElementById('action-queue');
            const count = document.getElementById('action-count');

            count.textContent = pendingActions.length;

            queue.innerHTML = pendingActions.length ? pendingActions.map((a, idx) => {
                const name = a.path.split('/').pop();
                return `
                <li class="action-item ${a.action}">
                    <span title="${a.path}">${name}</span>
                    <span class="remove-action" onclick="removeAction(${idx})">✕</span>
                </li>`;
            }).join('') : '<li style="color:#666;font-size:0.8rem;padding:10px">No pending actions</li>';
        }

        function showConfirmation() {
            if (pendingActions.length === 0) return;

            const list = document.getElementById('confirm-list');
            list.innerHTML = pendingActions.map(a => `<li>${a.path}</li>`).join('');
            document.getElementById('confirm-modal').classList.add('active');
        }

        function closeConfirmation() {
            document.getElementById('confirm-modal').classList.remove('active');
        }

        async function executeActions() {
            const res = await fetch('/api/execute', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(pendingActions)
            });
            const result = await res.json();

            alert(`Deleted ${result.deleted} files. ${result.failed} failed.`);

            pendingActions = [];
            saveActions();
            closeConfirmation();
            await loadFolders();
            await loadImages();
        }

        // Lightbox
        function openLightbox(idx) {
            const images = filterImages();
            currentIndex = idx;
            const img = images[idx];

            document.getElementById('lightbox-img').src = `/image/${encodeURIComponent(img.path)}`;
            document.getElementById('lightbox-caption').innerHTML = `
                <strong>${img.name}</strong><br>
                ${img.width}×${img.height} · Score: ${img.score?.toFixed(3) || 'N/A'} · ${img.verdict || ''}
                ${img.tags?.length ? '<br>Tags: ' + img.tags.join(', ') : ''}
            `;
            document.getElementById('lightbox').classList.add('active');
        }

        function closeLightbox() {
            document.getElementById('lightbox').classList.remove('active');
        }

        function navImage(delta) {
            const images = filterImages();
            currentIndex = (currentIndex + delta + images.length) % images.length;
            openLightbox(currentIndex);
        }

        function tagCurrentImage() {
            const images = filterImages();
            const img = images[currentIndex];
            selectedImages.clear();
            selectedImages.add(img.path);
            updateSelectionUI();
            openTagModal();
        }

        function deleteCurrentImage() {
            const images = filterImages();
            const img = images[currentIndex];
            if (!pendingActions.some(a => a.path === img.path)) {
                pendingActions.push({
                    action: 'delete',
                    path: img.path,
                    timestamp: new Date().toISOString()
                });
                saveActions();
            }
            navImage(1);
        }

        // Event listeners
        document.querySelectorAll('.sidebar-tab').forEach(tab => {
            tab.onclick = () => {
                document.querySelectorAll('.sidebar-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(`panel-${tab.dataset.tab}`).classList.add('active');
            };
        });

        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.onclick = () => {
                document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentView = btn.dataset.view;
                renderImages();
            };
        });

        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.onclick = () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                renderImages();
            };
        });

        document.getElementById('thumb-size').oninput = (e) => {
            document.querySelector('.image-grid').style.setProperty('--thumb-size', e.target.value + 'px');
        };

        document.getElementById('new-tag-input').onkeypress = async (e) => {
            if (e.key === 'Enter' && e.target.value.trim()) {
                await fetch('/api/tags/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name: e.target.value.trim() })
                });
                e.target.value = '';
                await loadTags();
            }
        };

        document.addEventListener('keydown', (e) => {
            if (document.getElementById('tag-modal').classList.contains('active')) return;
            if (document.getElementById('confirm-modal').classList.contains('active')) return;

            if (document.getElementById('lightbox').classList.contains('active')) {
                if (e.key === 'Escape') closeLightbox();
                if (e.key === 'ArrowLeft') navImage(-1);
                if (e.key === 'ArrowRight') navImage(1);
                if (e.key === 't') tagCurrentImage();
                if (e.key === 'd') deleteCurrentImage();
            }
        });

        // Init
        loadFolders();
        loadImages();
        loadTags();
        loadActions();
    </script>
</body>
</html>
'''


class ImageBrowserHandler(SimpleHTTPRequestHandler):
    """Custom handler for image browser."""

    def do_GET(self):
        path = unquote(self.path)

        if path == '/' or path == '/index.html':
            self.send_html(HTML_TEMPLATE)
        elif path == '/api/folders':
            self.send_json(self.get_folders())
        elif path.startswith('/api/images'):
            folder = None
            if '?' in path:
                qs = parse_qs(path.split('?')[1])
                folder = qs.get('folder', [None])[0]
            self.send_json(self.get_images(folder))
        elif path == '/api/tags':
            self.send_json({'definitions': TAG_DEFINITIONS, 'image_tags': TAGS})
        elif path == '/api/actions':
            self.send_json(PENDING_ACTIONS)
        elif path.startswith('/image/'):
            self.serve_image(path[7:])
        else:
            self.send_error(404)

    def do_POST(self):
        path = unquote(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body) if body else {}

        if path == '/api/tags':
            self.apply_tags(data)
        elif path == '/api/tags/create':
            self.create_tag(data)
        elif path == '/api/actions':
            global PENDING_ACTIONS
            PENDING_ACTIONS = data
            save_actions()
            self.send_json({'ok': True})
        elif path == '/api/execute':
            result = self.execute_actions(data)
            self.send_json(result)
        else:
            self.send_error(404)

    def get_folders(self):
        folders = []
        total = 0

        for item in sorted(IMAGES_ROOT.iterdir()):
            if item.is_dir():
                count = len(list(item.rglob('*.png')))
                if count > 0:
                    folders.append({'name': item.name, 'count': count})
                    total += count

        root_images = len(list(IMAGES_ROOT.glob('*.png')))
        if root_images > 0:
            folders.insert(0, {'name': '(root)', 'count': root_images})
            total += root_images

        return {'folders': folders, 'total': total}

    def get_images(self, folder=None):
        if folder and folder != '(root)':
            search_path = IMAGES_ROOT / folder
        else:
            search_path = IMAGES_ROOT

        images = []
        pattern = '*.png' if folder == '(root)' else '**/*.png'

        for img_path in sorted(search_path.glob(pattern)):
            rel_path = str(img_path.relative_to(PROJECT_ROOT))
            score_info = SCORES.get(rel_path, {})
            image_tags = TAGS.get(rel_path, [])

            images.append({
                'name': img_path.name,
                'path': rel_path,
                'width': score_info.get('width', 0),
                'height': score_info.get('height', 0),
                'score': score_info.get('score'),
                'verdict': score_info.get('verdict'),
                'reason': score_info.get('reason'),
                'tags': image_tags,
            })

        return images

    def apply_tags(self, data):
        paths = data.get('paths', [])
        tags = data.get('tags', [])

        for tag in tags:
            if tag not in TAG_DEFINITIONS:
                TAG_DEFINITIONS[tag] = {'color': None}

        for path in paths:
            if path not in TAGS:
                TAGS[path] = []
            for tag in tags:
                if tag not in TAGS[path]:
                    TAGS[path].append(tag)

        save_tags()
        self.send_json({'ok': True})

    def create_tag(self, data):
        name = data.get('name', '').strip()
        if name and name not in TAG_DEFINITIONS:
            TAG_DEFINITIONS[name] = {'color': None}
            save_tags()
        self.send_json({'ok': True})

    def execute_actions(self, actions):
        deleted = 0
        failed = 0

        for action in actions:
            if action['action'] == 'delete':
                filepath = PROJECT_ROOT / action['path']
                try:
                    if filepath.exists():
                        filepath.unlink()
                        deleted += 1
                        # Remove from scores and tags
                        SCORES.pop(action['path'], None)
                        TAGS.pop(action['path'], None)
                except Exception as e:
                    print(f"Failed to delete {action['path']}: {e}")
                    failed += 1

        global PENDING_ACTIONS
        PENDING_ACTIONS = []
        save_actions()
        save_tags()

        return {'deleted': deleted, 'failed': failed}

    def serve_image(self, rel_path):
        img_path = PROJECT_ROOT / rel_path

        if not img_path.exists() or not img_path.is_file():
            self.send_error(404)
            return

        try:
            img_path.relative_to(PROJECT_ROOT)
        except ValueError:
            self.send_error(403)
            return

        mime_type = mimetypes.guess_type(str(img_path))[0] or 'application/octet-stream'

        self.send_response(200)
        self.send_header('Content-Type', mime_type)
        self.send_header('Cache-Control', 'max-age=3600')
        self.end_headers()

        with open(img_path, 'rb') as f:
            self.wfile.write(f.read())

    def send_html(self, content):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode())

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass


def main():
    global IMAGES_ROOT

    import argparse
    parser = argparse.ArgumentParser(description='Image Browser')
    parser.add_argument('path', nargs='?', default=str(DEFAULT_IMAGES_DIR),
                        help='Root folder for images')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                        help=f'Port (default: {DEFAULT_PORT})')
    parser.add_argument('--no-browser', action='store_true',
                        help='Do not open browser')
    args = parser.parse_args()

    IMAGES_ROOT = Path(args.path).resolve()

    if not IMAGES_ROOT.exists():
        print(f"Error: Path does not exist: {IMAGES_ROOT}")
        sys.exit(1)

    load_scores()
    load_tags()
    load_actions()

    image_count = len(list(IMAGES_ROOT.rglob('*.png')))
    print(f"Image Browser")
    print(f"  Root: {IMAGES_ROOT}")
    print(f"  Images: {image_count}")
    print(f"  URL: http://localhost:{args.port}")
    print(f"\nPress Ctrl+C to stop\n")

    if not args.no_browser:
        webbrowser.open(f'http://localhost:{args.port}')

    server = HTTPServer(('', args.port), ImageBrowserHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == '__main__':
    main()
