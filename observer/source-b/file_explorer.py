#!/usr/bin/env python3
"""
File Explorer - Higgsfield-style full preview grid.

100% of screen is preview tiles. Each tile shows actual content.
Click to expand, double-click to open in app.

Usage:
    python file_explorer.py                    # Browse PROJECT_elements
    python file_explorer.py /path/to/folder   # Browse custom folder
"""

import os
import sys
import json
import mimetypes
import subprocess
import webbrowser
import shutil
import time
import secrets
import zipfile
import tarfile
import io
import hashlib
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote, parse_qs

DEFAULT_PORT = 9000

# Authentication state
AUTH_TOKEN = None
AUTH_VERIFIED = False
MAX_SERVE_SIZE = 100 * 1024 * 1024  # 100MB max file serve
MAX_PREVIEW_SIZE = 2000  # Characters for tile preview
MAX_CONTENT_SIZE = 2 * 1024 * 1024  # 2MB max for full content
MAX_VISIBLE_ITEMS = 200  # Limit items for performance
SELECT_ZONE_RATIO = 0.35  # 35% left = select, 65% right = open
PROJECT_ROOT = Path(__file__).parent.parent

EXCLUDE_DIRS = {
    '.git', 'node_modules', '.venv', '.tools_venv', '__pycache__',
    '.pytest_cache', '.mypy_cache', 'dist', 'build', '.eggs',
    '.next', '.cache', '.parcel-cache', '.collider'
}

BROWSE_ROOT = None
TRASH_DIR = None  # Will be set to BROWSE_ROOT/.file_explorer_trash
ACTION_HISTORY = []  # Stack of actions for undo
REDO_STACK = []  # Stack of undone actions for redo

# Language mappings for syntax highlighting
LANG_MAP = {
    'py': 'python', 'js': 'javascript', 'ts': 'typescript',
    'jsx': 'javascript', 'tsx': 'typescript', 'html': 'xml',
    'css': 'css', 'scss': 'scss', 'sass': 'scss', 'less': 'less',
    'json': 'json', 'jsonc': 'json', 'json5': 'json',
    'yaml': 'yaml', 'yml': 'yaml', 'xml': 'xml', 'svg': 'xml',
    'sql': 'sql', 'sh': 'bash', 'bash': 'bash', 'zsh': 'bash',
    'rs': 'rust', 'go': 'go', 'rb': 'ruby', 'php': 'php',
    'java': 'java', 'c': 'c', 'cpp': 'cpp', 'h': 'c', 'hpp': 'cpp',
    'swift': 'swift', 'kt': 'kotlin', 'kts': 'kotlin',
    'toml': 'ini', 'ini': 'ini', 'cfg': 'ini', 'conf': 'ini',
    'md': 'markdown', 'mdx': 'markdown', 'txt': 'plaintext',
    'csv': 'plaintext', 'log': 'plaintext', 'diff': 'diff',
    'env': 'bash', 'dockerfile': 'dockerfile', 'makefile': 'makefile',
    'lua': 'lua', 'r': 'r', 'pl': 'perl', 'pm': 'perl',
    'scala': 'scala', 'groovy': 'groovy', 'gradle': 'groovy',
    'clj': 'clojure', 'cljs': 'clojure', 'ex': 'elixir', 'exs': 'elixir',
    'hs': 'haskell', 'ml': 'ocaml', 'fs': 'fsharp',
    'vim': 'vim', 'el': 'lisp', 'lisp': 'lisp',
    'graphql': 'graphql', 'gql': 'graphql', 'prisma': 'prisma',
    'tf': 'hcl', 'tfvars': 'hcl', 'hcl': 'hcl',
    'proto': 'protobuf', 'cmake': 'cmake',
    'rst': 'plaintext', 'tex': 'latex', 'cls': 'latex', 'sty': 'latex',
    'properties': 'properties', 'gitignore': 'plaintext',
}


def validate_path(path_str: str) -> Path | None:
    """Validate and resolve path, ensuring it's within BROWSE_ROOT.

    Returns resolved Path if valid, None if path is outside allowed root.
    """
    if BROWSE_ROOT is None:
        return None

    if not path_str:
        return BROWSE_ROOT

    # Resolve the path
    if path_str.startswith('/'):
        resolved = Path(path_str).resolve()
    else:
        resolved = (BROWSE_ROOT / path_str.lstrip('/')).resolve()

    # Security: Ensure path is within BROWSE_ROOT
    try:
        resolved.relative_to(BROWSE_ROOT)
        return resolved
    except ValueError:
        # Path is outside BROWSE_ROOT - reject
        return None


def request_biometric_auth(reason: str = "File Explorer requires authentication") -> bool:
    """Request Touch ID / Face ID authentication via macOS LocalAuthentication.

    Returns True if authenticated successfully, False otherwise.
    """
    # Swift code to trigger biometric auth
    swift_code = f'''
import LocalAuthentication
import Foundation

let context = LAContext()
var error: NSError?

if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {{
    let semaphore = DispatchSemaphore(value: 0)
    var success = false

    context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                          localizedReason: "{reason}") {{ result, _ in
        success = result
        semaphore.signal()
    }}

    semaphore.wait()
    exit(success ? 0 : 1)
}} else {{
    // Fallback to device passcode if biometrics unavailable
    if context.canEvaluatePolicy(.deviceOwnerAuthentication, error: &error) {{
        let semaphore = DispatchSemaphore(value: 0)
        var success = false

        context.evaluatePolicy(.deviceOwnerAuthentication,
                              localizedReason: "{reason}") {{ result, _ in
            success = result
            semaphore.signal()
        }}

        semaphore.wait()
        exit(success ? 0 : 1)
    }}
    exit(1)
}}
'''
    try:
        result = subprocess.run(
            ['swift', '-e', swift_code],
            capture_output=True,
            timeout=60  # 60 second timeout for user interaction
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        print(f"Biometric auth error: {e}")
        return False


def generate_auth_token() -> str:
    """Generate a secure random token for session auth."""
    return secrets.token_urlsafe(32)


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_preview_type(ext):
    ext = ext.lower()
    if ext in ('png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'ico', 'tiff', 'tif'):
        return 'image'
    if ext == 'svg':  # SVG is both image and code
        return 'image'
    if ext in ('mp4', 'webm', 'mov', 'avi', 'mkv', 'm4v', 'wmv', 'flv'):
        return 'video'
    if ext in ('mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac', 'wma', 'aiff'):
        return 'audio'
    if ext == 'pdf':
        return 'pdf'
    if ext in LANG_MAP:
        return 'code'
    # Additional text-based formats
    text_exts = {'txt', 'log', 'csv', 'tsv', 'diff', 'patch', 'rst', 'asciidoc',
                 'gitignore', 'gitattributes', 'editorconfig', 'npmrc', 'nvmrc',
                 'env', 'env.local', 'env.development', 'env.production',
                 'babelrc', 'eslintrc', 'prettierrc', 'stylelintrc',
                 'dockerignore', 'htaccess', 'htpasswd'}
    if ext in text_exts:
        return 'code'
    return 'binary'


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Explorer</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <!-- 3D Model Viewer -->
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
    <!-- Three.js for STL -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <!-- PDF.js for PDF previews -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            /* macOS Dark Mode Colors */
            --bg: #1e1e1e;
            --bg-secondary: #2d2d2d;
            --card-bg: #323232;
            --card-bg-hover: #3a3a3a;
            --border: #424242;
            --border-light: #4a4a4a;
            --text: #ffffff;
            --text-secondary: #ebebeb;
            --text-dim: #8e8e93;
            --accent: #0a84ff;
            --accent-hover: #409cff;
            --selection: rgba(10, 132, 255, 0.3);

            /* macOS System Colors */
            --system-red: #ff453a;
            --system-orange: #ff9f0a;
            --system-yellow: #ffd60a;
            --system-green: #30d158;
            --system-blue: #0a84ff;
            --system-purple: #bf5af2;
            --system-pink: #ff375f;

            /* OKLCH Base colors for file types */
            /* Intense file type colors - OKLCH with high chroma */
            --color-folder: oklch(0.70 0.22 85);      /* Vibrant yellow-gold */
            --color-image: oklch(0.68 0.26 145);      /* Vivid green */
            --color-vector: oklch(0.65 0.24 180);     /* Turquoise */
            --color-video: oklch(0.62 0.28 300);      /* Electric purple */
            --color-audio: oklch(0.65 0.25 330);      /* Hot pink */
            --color-code: oklch(0.62 0.24 250);       /* Bright blue */
            --color-doc: oklch(0.60 0.22 230);        /* Royal blue */
            --color-pdf: oklch(0.58 0.28 25);         /* Bold red */
            --color-data: oklch(0.65 0.24 160);       /* Cyan-teal */
            --color-config: oklch(0.62 0.22 55);      /* Orange */
            --color-archive: oklch(0.58 0.20 45);     /* Amber */
            --color-model3d: oklch(0.65 0.26 320);    /* Magenta */
            --color-font: oklch(0.60 0.22 280);       /* Violet */
            --color-notebook: oklch(0.65 0.24 35);    /* Orange-red */
            --color-executable: oklch(0.55 0.20 0);   /* Red */
            --color-database: oklch(0.58 0.22 200);   /* Steel blue */
            --color-binary: oklch(0.50 0.12 260);     /* Muted purple */

            --depth-factor: 0.88;
        }

        /* Minimal SVG Icon System */
        .icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1em;
            height: 1em;
            vertical-align: middle;
        }
        .icon svg {
            width: 100%;
            height: 100%;
            fill: none;
            stroke: currentColor;
            stroke-width: 1.5;
            stroke-linecap: round;
            stroke-linejoin: round;
        }
        .icon-sm { font-size: 14px; }
        .icon-md { font-size: 18px; }
        .icon-lg { font-size: 24px; }
        .icon-xl { font-size: 32px; }

        :root {
            /* Shadows */
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
            --shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
            --shadow-hover: 0 8px 20px rgba(0,0,0,0.45);

            /* Animation */
            --transition-fast: 0.15s ease;
            --transition-normal: 0.2s ease;
            --transition-spring: 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        html, body {
            height: 100%;
            overflow: hidden;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', sans-serif;
            background: var(--bg);
            color: var(--text);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* macOS-style Top bar */
        .topbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 52px;
            background: linear-gradient(180deg, #3d3d3d 0%, #323232 100%);
            border-bottom: 1px solid #1a1a1a;
            box-shadow: 0 1px 0 rgba(255,255,255,0.05) inset;
            display: flex;
            align-items: center;
            padding: 0 12px;
            gap: 8px;
            z-index: 100;
        }

        /* Traffic light placeholder */
        .topbar::before {
            content: "";
            width: 68px;
            height: 100%;
        }

        .nav-btn {
            width: 30px;
            height: 24px;
            border-radius: 5px;
            border: none;
            background: linear-gradient(180deg, #525252 0%, #424242 100%);
            box-shadow: 0 1px 1px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.08);
            color: var(--text-secondary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            font-weight: 500;
            transition: var(--transition-fast);
        }

        .nav-btn:hover {
            background: linear-gradient(180deg, #5a5a5a 0%, #4a4a4a 100%);
            color: var(--text);
        }

        .nav-btn:active {
            background: linear-gradient(180deg, #3a3a3a 0%, #323232 100%);
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
        }

        .nav-btn:disabled {
            opacity: 0.35;
            cursor: not-allowed;
            background: #3a3a3a;
            box-shadow: none;
        }

        .nav-group {
            display: flex;
            gap: 1px;
            background: #2a2a2a;
            border-radius: 6px;
            padding: 1px;
        }

        .nav-group .nav-btn {
            border-radius: 4px;
        }

        .history-btns {
            display: flex;
            gap: 1px;
            background: #2a2a2a;
            border-radius: 6px;
            padding: 1px;
            margin-left: 12px;
        }

        .history-btns .nav-btn {
            border-radius: 4px;
            font-size: 0.9rem;
        }

        /* macOS Breadcrumb Path */
        .path-display {
            flex: 1;
            font-size: 13px;
            font-weight: 400;
            color: var(--text-dim);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: flex;
            align-items: center;
            gap: 2px;
            margin-left: 16px;
        }

        .path-display .separator {
            color: var(--text-dim);
            opacity: 0.5;
            margin: 0 2px;
        }

        .path-display span:not(.separator) {
            color: var(--text-secondary);
            cursor: pointer;
            padding: 3px 8px;
            border-radius: 4px;
            transition: var(--transition-fast);
        }

        .path-display span:not(.separator):hover {
            background: rgba(255,255,255,0.1);
            color: var(--text);
        }

        .path-display span:last-of-type:not(.separator) {
            color: var(--text);
            font-weight: 500;
        }

        .path-display span:hover {
            background: var(--border);
        }

        /* macOS-style Search */
        .search-input {
            width: 180px;
            padding: 5px 10px 5px 28px;
            border-radius: 6px;
            border: none;
            background: rgba(255,255,255,0.08);
            color: var(--text);
            font-size: 12px;
            transition: var(--transition-fast);
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%238e8e93' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: 8px center;
        }

        .search-input::placeholder {
            color: var(--text-dim);
        }

        .search-input:focus {
            outline: none;
            background-color: rgba(255,255,255,0.12);
            box-shadow: 0 0 0 3px var(--selection);
        }

        /* macOS-style Slider */
        /* Selection Mode Toggle */
        .select-mode-toggle {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: var(--text-dim);
            padding: 4px 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: var(--transition-fast);
            user-select: none;
        }

        .select-mode-toggle:hover {
            background: rgba(255,255,255,0.08);
        }

        .select-mode-toggle.active {
            background: var(--selection);
            color: var(--accent);
        }

        .select-mode-toggle input[type="checkbox"] {
            display: none;
        }

        .select-mode-toggle .toggle-switch {
            width: 28px;
            height: 16px;
            background: rgba(255,255,255,0.15);
            border-radius: 8px;
            position: relative;
            transition: var(--transition-fast);
        }

        .select-mode-toggle .toggle-switch::after {
            content: "";
            position: absolute;
            top: 2px;
            left: 2px;
            width: 12px;
            height: 12px;
            background: white;
            border-radius: 50%;
            transition: var(--transition-fast);
            box-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }

        .select-mode-toggle.active .toggle-switch {
            background: var(--accent);
        }

        .select-mode-toggle.active .toggle-switch::after {
            left: 14px;
        }

        .size-control {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11px;
            color: var(--text-dim);
        }

        .size-control input[type="range"] {
            width: 80px;
            height: 4px;
            -webkit-appearance: none;
            background: rgba(255,255,255,0.15);
            border-radius: 2px;
            cursor: pointer;
        }

        .size-control input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 14px;
            height: 14px;
            background: linear-gradient(180deg, #fafafa 0%, #e0e0e0 100%);
            border-radius: 50%;
            box-shadow: 0 1px 3px rgba(0,0,0,0.4);
            cursor: pointer;
        }

        /* Memory stats indicator */
        .memory-stats {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 6px;
            font-size: 11px;
            color: var(--text-dim);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .memory-stats:hover {
            background: rgba(0,0,0,0.4);
            color: var(--text);
        }
        .memory-stats .mem-label {
            opacity: 0.6;
        }
        .memory-stats .mem-value {
            font-weight: 600;
            color: oklch(0.75 0.15 145);
        }
        .memory-stats .mem-value.warning {
            color: oklch(0.8 0.18 80);
        }
        .memory-stats .mem-value.critical {
            color: oklch(0.75 0.2 25);
        }

        /* Grid container */
        /* Main layout with sidebar */
        .main-layout {
            position: fixed;
            top: 52px;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
        }

        /* Sidebar - previous level */
        .sidebar {
            width: 260px;
            min-width: 260px;
            background: var(--bg-secondary);
            border-right: 1px solid rgba(255,255,255,0.06);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .sidebar.collapsed {
            width: 0;
            min-width: 0;
            border-right: none;
        }

        .sidebar-header {
            padding: 12px 14px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            cursor: pointer;
            transition: var(--transition-fast);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .sidebar-header:hover {
            background: rgba(255,255,255,0.05);
        }

        .sidebar-header .back-icon {
            font-size: 14px;
            color: var(--text-dim);
        }

        .sidebar-header .sidebar-title {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .sidebar-header .sidebar-path {
            font-size: 10px;
            color: var(--text-dim);
        }

        .sidebar-content {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
        }

        /* Sidebar items - compact list */
        .sidebar-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: var(--transition-fast);
            margin-bottom: 2px;
        }

        .sidebar-item:hover {
            background: rgba(255,255,255,0.08);
        }

        .sidebar-item.active {
            background: var(--selection);
        }

        .sidebar-item.selected {
            background: rgba(10, 132, 255, 0.2);
            box-shadow: inset 0 0 0 1px var(--accent);
        }

        .sidebar-item .item-icon {
            width: 32px;
            height: 32px;
            border-radius: 6px;
            background: var(--card-bg);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            flex-shrink: 0;
            overflow: hidden;
        }

        .sidebar-item .item-icon img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .sidebar-item .item-info {
            flex: 1;
            min-width: 0;
        }

        .sidebar-item .item-name {
            font-size: 14px;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .sidebar-item .item-meta {
            font-size: 10px;
            color: var(--text-dim);
        }

        .sidebar-empty {
            padding: 20px;
            text-align: center;
            color: var(--text-dim);
            font-size: 12px;
        }

        /* Sidebar Mode Toggle */
        .sidebar-mode-toggle {
            display: flex;
            gap: 4px;
            padding: 6px 8px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }

        .sidebar-mode-btn {
            flex: 1;
            padding: 4px 8px;
            background: transparent;
            border: none;
            color: var(--text-dim);
            font-size: 10px;
            cursor: pointer;
            border-radius: 4px;
            transition: var(--transition-fast);
        }

        .sidebar-mode-btn:hover {
            background: rgba(255,255,255,0.08);
        }

        .sidebar-mode-btn.active {
            background: var(--accent);
            color: white;
        }

        /* Type Group Drawer */
        .type-drawer {
            margin-bottom: 2px;
        }

        .type-drawer-header {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 10px;
            background: rgba(255,255,255,0.03);
            border-radius: 6px;
            cursor: pointer;
            transition: var(--transition-fast);
            user-select: none;
        }

        .type-drawer-header:hover {
            background: rgba(255,255,255,0.08);
        }

        .type-drawer.open .type-drawer-header {
            border-radius: 6px 6px 0 0;
            background: rgba(255,255,255,0.06);
        }

        .type-drawer-icon {
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }

        .type-drawer-icon .icon {
            font-size: 16px;
        }

        .type-drawer-label {
            flex: 1;
            font-size: 12px;
            font-weight: 500;
            color: var(--text-secondary);
        }

        .type-drawer-count {
            font-size: 10px;
            color: var(--text-dim);
            background: rgba(255,255,255,0.1);
            padding: 2px 6px;
            border-radius: 10px;
        }

        .type-drawer-chevron {
            width: 16px;
            height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-dim);
            transition: transform 0.2s ease;
        }

        .type-drawer.open .type-drawer-chevron {
            transform: rotate(90deg);
        }

        .type-drawer-content {
            display: none;
            background: rgba(0,0,0,0.15);
            border-radius: 0 0 6px 6px;
            padding: 4px;
            margin-bottom: 4px;
        }

        .type-drawer.open .type-drawer-content {
            display: block;
        }

        .type-drawer-content .sidebar-item {
            padding: 6px 8px;
            margin-bottom: 1px;
        }

        .type-drawer-content .sidebar-item .item-icon {
            width: 24px;
            height: 24px;
            font-size: 12px;
        }

        .type-drawer-content .sidebar-item .item-name {
            font-size: 12px;
        }

        .type-drawer-content .sidebar-item .item-meta {
            font-size: 9px;
        }

        /* Main content area */
        .grid-container {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(var(--tile-size, 280px), 1fr));
            gap: 17px;
            animation: fadeIn 0.3s ease;
            position: relative;
        }

        /* Selection rectangle */
        .selection-rect {
            position: fixed;
            border: 1px solid var(--accent);
            background: var(--selection);
            pointer-events: none;
            z-index: 50;
            border-radius: 2px;
        }

        /* Selection dragging state */
        .grid.is-selecting {
            cursor: crosshair;
        }

        .grid.is-selecting .tile {
            pointer-events: none;
        }

        /* Drag ghost */
        .drag-ghost {
            position: fixed;
            padding: 12px 16px;
            background: rgba(24, 24, 27, 0.95);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--accent);
            border-radius: 12px;
            z-index: 1000;
            pointer-events: none;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            animation: dragGhostIn 0.1s ease-out;
        }

        @keyframes dragGhostIn {
            from { transform: scale(0.9); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        .drag-ghost .drag-icon {
            font-size: 24px;
        }

        .drag-ghost .drag-label {
            font-size: 13px;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.9);
        }

        body.is-dragging * {
            cursor: grabbing !important;
        }

        /* Drop targets */
        .tile.drop-target {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.3), var(--shadow-hover);
            transform: scale(1.02);
        }

        .tile.drop-folder::after {
            content: 'Move here';
            position: absolute;
            bottom: 8px;
            left: 50%;
            transform: translateX(-50%);
            padding: 4px 10px;
            background: var(--accent);
            color: white;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            z-index: 10;
        }

        .tile.drop-file::after {
            content: 'Create folder';
            position: absolute;
            bottom: 8px;
            left: 50%;
            transform: translateX(-50%);
            padding: 4px 10px;
            background: oklch(0.65 0.2 140);
            color: white;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            z-index: 10;
        }

        /* Folder dialog */
        .folder-dialog-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
            animation: fadeIn 0.15s ease-out;
        }

        .folder-dialog {
            background: rgba(32, 32, 36, 0.98);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            min-width: 320px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            animation: dialogIn 0.2s ease-out;
        }

        @keyframes dialogIn {
            from { transform: scale(0.95); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        .folder-dialog h3 {
            margin: 0 0 8px 0;
            font-size: 16px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.95);
        }

        .folder-dialog p {
            margin: 0 0 16px 0;
            font-size: 13px;
            color: rgba(255, 255, 255, 0.6);
        }

        .folder-name-input {
            width: 100%;
            padding: 12px 14px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 14px;
            margin-bottom: 16px;
            outline: none;
            transition: border-color 0.15s;
        }

        .folder-name-input:focus {
            border-color: var(--accent);
        }

        .dialog-buttons {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }

        .dialog-buttons button {
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: all 0.15s;
        }

        .dialog-cancel {
            background: rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.8);
        }

        .dialog-cancel:hover {
            background: rgba(255, 255, 255, 0.15);
        }

        .dialog-confirm {
            background: var(--accent);
            color: white;
        }

        .dialog-confirm:hover {
            filter: brightness(1.1);
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* Tile */
        .tile {
            background: var(--card-bg);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            transition: transform var(--transition-spring), box-shadow var(--transition-normal), border-color var(--transition-fast);
            display: flex;
            flex-direction: column;
            position: relative;
            box-shadow: var(--shadow-sm);
        }

        .tile:hover {
            transform: translateY(-3px) scale(1.01);
            box-shadow: var(--shadow-hover);
            border-color: rgba(255,255,255,0.12);
        }

        .tile:active {
            transform: translateY(-1px) scale(0.99);
            transition: transform 0.1s ease;
        }

        .tile-preview {
            height: 200px;
            overflow: hidden;
            position: relative;
            background: var(--bg-secondary);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .tile-preview img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }

        .tile-preview video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .tile-preview .code-preview {
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-size: 0.65rem;
            line-height: 1.4;
            padding: 12px;
            background: #0d1117;
        }

        .tile-preview .code-preview pre {
            margin: 0;
            white-space: pre-wrap;
            word-break: break-all;
        }

        .tile-preview .md-preview {
            width: 100%;
            height: 100%;
            overflow: hidden;
            padding: 12px;
            font-size: 0.7rem;
            line-height: 1.4;
            background: #0d1117;
            color: var(--text-dim);
        }

        .tile-preview .md-preview h1,
        .tile-preview .md-preview h2,
        .tile-preview .md-preview h3 {
            font-size: 0.85rem;
            color: var(--text);
            margin: 0 0 8px 0;
        }

        .tile-preview .folder-icon,
        .tile-preview .binary-icon {
            font-size: 4rem;
            opacity: 0.6;
        }

        .tile-preview .folder-icon { color: #f7c94b; }
        .tile-preview .pdf-icon { color: #ef4444; font-size: 4rem; }
        .tile-preview .audio-icon { color: #22c55e; font-size: 4rem; }

        .tile-preview .file-ext {
            position: absolute;
            bottom: 8px;
            right: 8px;
            padding: 2px 8px;
            background: rgba(0,0,0,0.7);
            border-radius: 4px;
            font-size: 0.7rem;
            color: var(--text-dim);
            text-transform: uppercase;
        }

        /* Enhanced preview styles */
        .tile-preview .csv-preview {
            width: 100%;
            height: 100%;
            overflow: hidden;
            padding: 8px;
            background: #0d1117;
        }

        .tile-preview .csv-preview table {
            width: 100%;
            font-size: 0.55rem;
            border-collapse: collapse;
            color: var(--text-dim);
        }

        .tile-preview .csv-preview td {
            padding: 2px 4px;
            border: 1px solid #21262d;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 60px;
        }

        .tile-preview .csv-preview tr:first-child td {
            background: #161b22;
            color: var(--text);
            font-weight: 500;
        }

        .audio-preview, .pdf-preview, .data-preview, .doc-preview,
        .archive-preview, .model-preview, .font-preview, .notebook-preview,
        .binary-preview {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .audio-preview .audio-icon { font-size: 2.5rem; }
        .audio-preview .audio-wave {
            width: 60%;
            height: 24px;
            background: linear-gradient(90deg,
                transparent 0%, var(--color-audio) 10%, transparent 20%,
                var(--color-audio) 30%, transparent 40%, var(--color-audio) 50%,
                transparent 60%, var(--color-audio) 70%, transparent 80%,
                var(--color-audio) 90%, transparent 100%);
            opacity: 0.4;
            border-radius: 4px;
        }

        .pdf-preview .pdf-icon { font-size: 3rem; }
        .pdf-preview .pdf-label { font-size: 0.7rem; color: var(--color-pdf); font-weight: 600; }

        .pdf-canvas-preview {
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #fff;
        }

        .pdf-canvas-preview .pdf-canvas {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }

        .pdf-canvas-preview .pdf-page-label {
            position: absolute;
            bottom: 4px;
            right: 4px;
            font-size: 9px;
            color: var(--color-pdf);
            background: rgba(0,0,0,0.6);
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 600;
        }

        .data-preview .data-icon { font-size: 3rem; }
        .data-preview .data-label { font-size: 0.7rem; color: var(--color-data); font-weight: 600; }

        .doc-preview .doc-icon { font-size: 3rem; }
        .doc-preview .doc-label { font-size: 0.7rem; color: #4a90d9; font-weight: 600; }

        .archive-preview .archive-icon { font-size: 3rem; }
        .archive-preview .archive-label { font-size: 0.7rem; color: #f59e0b; font-weight: 600; }

        .model-preview .model-icon { font-size: 3rem; }
        .model-preview .model-label { font-size: 0.7rem; color: #f472b6; font-weight: 600; }

        .font-preview .font-icon { font-size: 3rem; }
        .font-preview .font-label { font-size: 0.7rem; color: #a78bfa; font-weight: 600; }

        .notebook-preview .notebook-icon { font-size: 3rem; }
        .notebook-preview .notebook-label { font-size: 0.7rem; color: #f97316; font-weight: 600; }

        .binary-preview .binary-icon { font-size: 2.5rem; opacity: 0.6; }
        .binary-preview .binary-label { font-size: 0.65rem; color: var(--text-dim); text-transform: uppercase; }

        .tile-info {
            padding: 10px 12px;
            border-top: 1px solid rgba(255,255,255,0.05);
            background: linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.1) 100%);
        }

        .tile-name {
            font-size: 14px;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 3px;
            letter-spacing: -0.01em;
        }

        .tile-meta {
            font-size: 11px;
            color: var(--text-dim);
            display: flex;
            justify-content: space-between;
        }

        /* Folder tile */
        .tile.folder .tile-preview {
            background: var(--bg);
            padding: 0;
            position: relative;
        }

        .tile.folder .folder-grid {
            display: grid;
            grid-template-columns: repeat(var(--folder-cols, 3), 1fr);
            grid-template-rows: repeat(var(--folder-rows, 2), 1fr);
            width: 100%;
            height: 100%;
            gap: 1px;
            background: #18181b;
        }

        .tile.folder .folder-grid .mini-item {
            background: #0a0a0c;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }

        .tile.folder .folder-grid .mini-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .tile.folder .folder-grid .mini-item .mini-code {
            width: 100%;
            height: 100%;
            font-size: 0.35rem;
            line-height: 1.15;
            padding: 2px;
            overflow: hidden;
            color: #6b7280;
            background: #0d1117;
            font-family: monospace;
        }

        .tile.folder .folder-grid .mini-item .mini-icon {
            font-size: 0.9rem;
            opacity: 0.7;
        }

        /* Nested folder - shows its own mini-grid with clear frame */
        .tile.folder .folder-grid .mini-item.is-folder {
            background: #0c0c0f;
            border: 2px solid color-mix(in oklch, var(--color-folder) 50%, transparent);
            border-radius: 4px;
            padding: 2px;
            position: relative;
        }

        .tile.folder .folder-grid .mini-item.is-folder::before {
            content: "▪";
            position: absolute;
            top: -1px;
            left: 2px;
            font-size: 0.5rem;
            z-index: 2;
            color: var(--color-folder);
            text-shadow: 0 1px 2px rgba(0,0,0,0.8);
        }

        .tile.folder .folder-grid .mini-item .nested-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            grid-template-rows: repeat(2, 1fr);
            width: 100%;
            height: 100%;
            gap: 2px;
            background: color-mix(in oklch, var(--color-folder) 15%, #0a0a0c);
            border-radius: 2px;
            overflow: hidden;
        }

        .tile.folder .folder-grid .mini-item .nested-grid .nested-cell {
            background: #08080a;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }

        .tile.folder .folder-grid .mini-item .nested-grid .nested-cell img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .tile.folder .folder-grid .mini-item .nested-grid .nested-cell .tiny-icon {
            font-size: 0.45rem;
            opacity: 0.6;
        }

        /* Level 2 nested folder (folder inside folder inside folder) */
        .tile.folder .folder-grid .mini-item .nested-grid .nested-cell.is-nested-folder {
            border: 1px solid color-mix(in oklch, var(--color-folder) 40%, transparent);
            border-radius: 2px;
            background: #060608;
        }

        /* 3D Model Preview */
        .tile-preview .model-3d-preview {
            width: 100%;
            height: 100%;
            position: relative;
            background: linear-gradient(135deg, #0a0a0f 0%, #151520 100%);
        }

        .tile-preview model-viewer {
            width: 100%;
            height: 100%;
            --poster-color: transparent;
        }

        .tile-preview .stl-canvas {
            width: 100%;
            height: 100%;
        }

        .tile-preview .model-3d-label {
            position: absolute;
            bottom: 8px;
            left: 8px;
            padding: 2px 8px;
            background: rgba(0,0,0,0.7);
            border-radius: 4px;
            font-size: 0.65rem;
            color: #f472b6;
            font-weight: 600;
        }

        .tile.folder .folder-label {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(transparent, rgba(0,0,0,0.85));
            padding: 20px 8px 6px;
            pointer-events: none;
        }

        .tile.folder .folder-label .folder-name {
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .tile.folder .folder-label .folder-count {
            font-size: 0.65rem;
            color: var(--text-dim);
        }

        /* macOS Quick Look style Lightbox */
        .lightbox {
            display: none;
            position: fixed;
            z-index: 200;
        }

        .lightbox-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.33);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            cursor: pointer;
        }

        .lightbox.active {
            display: block;
        }

        /* Main container - sidebar + content */
        .lightbox-container {
            position: fixed;
            top: 40px;
            left: 40px;
            right: 40px;
            bottom: 40px;
            z-index: 201;
            display: flex;
            gap: 0;
            pointer-events: none;
        }

        /* Edit Sidebar */
        .lightbox-sidebar {
            width: 280px;
            background: rgba(24, 24, 27, 0.95);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 16px 0 0 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-right: none;
            pointer-events: auto;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .lightbox-sidebar.collapsed {
            width: 0;
            border: none;
            padding: 0;
        }

        .sidebar-header {
            padding: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .sidebar-header .format-badge {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .sidebar-header .file-info {
            flex: 1;
            min-width: 0;
        }

        .sidebar-header .file-name {
            font-size: 15px;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.9);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .sidebar-header .file-meta {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.5);
            margin-top: 2px;
        }

        .sidebar-tools {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        /* Format Badge in Sidebar */
        .sidebar-format-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 16px;
            margin: 16px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .sidebar-format-badge .format-icon {
            font-size: 24px;
        }

        .sidebar-format-badge .format-name {
            font-size: 14px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.9);
        }

        /* Sidebar Sections */
        .sidebar-section {
            padding: 12px 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }

        .sidebar-section-title {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: rgba(255, 255, 255, 0.4);
            margin-bottom: 10px;
        }

        /* File Info Grid */
        .sidebar-info {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
        }

        .info-row span:first-child {
            color: rgba(255, 255, 255, 0.5);
        }

        .info-row span:last-child {
            color: rgba(255, 255, 255, 0.8);
        }

        .tool-section {
            margin-bottom: 20px;
        }

        .tool-section h4 {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: rgba(255, 255, 255, 0.4);
            margin: 0 0 10px 0;
        }

        .tool-row {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }

        .tool-btn {
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.8);
            font-size: 12px;
            cursor: pointer;
            transition: all 0.1s;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            min-width: 56px;
        }

        .tool-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .tool-icon {
            font-size: 16px;
        }

        .tool-label {
            font-size: 10px;
            color: rgba(255, 255, 255, 0.6);
        }

        .tool-slider {
            width: 100%;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 0;
        }

        .tool-slider label {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
            min-width: 80px;
        }

        .tool-slider input[type="range"] {
            flex: 1;
        }

        .tool-slider .value {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.5);
            min-width: 40px;
            text-align: right;
        }

        .sidebar-footer {
            padding: 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            display: flex;
            gap: 8px;
        }

        .sidebar-footer button {
            flex: 1;
            padding: 10px;
            border-radius: 8px;
            border: none;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s;
        }

        .sidebar-footer .btn-export {
            background: var(--accent);
            color: white;
        }

        .sidebar-footer .btn-reset {
            background: rgba(255, 255, 255, 0.08);
            color: rgba(255, 255, 255, 0.7);
        }

        /* Main Content Panel */
        .lightbox-inner {
            flex: 1;
            display: flex;
            flex-direction: column;
            pointer-events: auto;
            background: rgba(24, 24, 27, 0.95);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 0 16px 16px 0;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-left: 1px solid rgba(255, 255, 255, 0.04);
        }

        .lightbox-inner.no-sidebar {
            border-radius: 16px;
        }

        .lightbox-header {
            height: 40px;
            background: transparent;
            display: flex;
            align-items: center;
            padding: 0 12px;
            gap: 8px;
            flex-shrink: 0;
        }

        .lightbox-title {
            flex: 1;
            font-size: 13px;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
        }

        /* Zoom Controls */
        .zoom-controls {
            display: flex;
            align-items: center;
            gap: 4px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 4px;
        }

        .zoom-btn {
            width: 28px;
            height: 28px;
            border: none;
            background: transparent;
            color: rgba(255, 255, 255, 0.6);
            cursor: pointer;
            border-radius: 6px;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .zoom-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }

        .zoom-level {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.5);
            min-width: 40px;
            text-align: center;
        }

        .lightbox-btn {
            padding: 6px 12px;
            border-radius: 6px;
            border: none;
            background: rgba(255,255,255,0.08);
            color: rgba(255, 255, 255, 0.7);
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.1s;
        }

        .lightbox-btn:hover {
            background: rgba(255,255,255,0.15);
            color: white;
        }

        .lightbox-close {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            border: none;
            background: transparent;
            color: rgba(255, 255, 255, 0.5);
            cursor: pointer;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.1s;
        }

        .lightbox-close:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }

        .lightbox-content {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
            overflow: auto;
            background: transparent;
            position: relative;
        }

        /* Zoomable content wrapper */
        .zoom-wrapper {
            transform-origin: center center;
            transition: transform 0.1s ease-out;
        }

        .lightbox-content img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 8px;
        }

        .lightbox-content video,
        .lightbox-content audio {
            max-width: 100%;
            max-height: 100%;
            border-radius: 8px;
        }

        .lightbox-content .code-full {
            width: 100%;
            max-width: 1000px;
            height: 100%;
            overflow: auto;
            background: rgba(13, 17, 23, 0.85);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .lightbox-content .code-full pre {
            margin: 0;
            font-size: 0.85rem;
            line-height: 1.6;
        }

        .lightbox-content .md-full {
            width: 100%;
            max-width: 800px;
            height: 100%;
            overflow: auto;
            background: var(--card-bg);
            border-radius: 12px;
            padding: 32px;
        }

        .lightbox-content .md-full h1 { font-size: 2rem; margin: 0 0 1rem; }
        .lightbox-content .md-full h2 { font-size: 1.5rem; margin: 1.5rem 0 0.75rem; color: var(--text); }
        .lightbox-content .md-full h3 { font-size: 1.2rem; margin: 1.25rem 0 0.5rem; color: var(--text); }
        .lightbox-content .md-full p { margin: 0.75rem 0; color: var(--text-dim); }
        .lightbox-content .md-full code { background: var(--bg); padding: 2px 6px; border-radius: 4px; }
        .lightbox-content .md-full pre { background: var(--bg); padding: 16px; border-radius: 8px; overflow-x: auto; }
        .lightbox-content .md-full pre code { padding: 0; }
        .lightbox-content .md-full ul, .lightbox-content .md-full ol { margin: 0.5rem 0; padding-left: 1.5rem; color: var(--text-dim); }
        .lightbox-content .md-full a { color: var(--accent); }
        .lightbox-content .md-full blockquote { border-left: 3px solid var(--accent); padding-left: 1rem; margin: 1rem 0; color: var(--text-dim); }

        .lightbox-content iframe {
            width: 100%;
            height: 100%;
            border: none;
            border-radius: 8px;
        }

        .lightbox-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: rgba(255, 255, 255, 0.7);
            cursor: pointer;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.15s ease;
        }

        .lightbox-nav:hover {
            background: rgba(255, 255, 255, 0.15);
            color: white;
            transform: translateY(-50%) scale(1.08);
        }

        .lightbox-nav:active {
            transform: translateY(-50%) scale(0.95);
        }

        .lightbox-nav.prev { left: 24px; }
        .lightbox-nav.next { right: 24px; }

        /* Color-coded tiles */
        /* Color-coded tiles by file type */
        .tile[data-type="folder"] { --tile-color: var(--color-folder); }
        .tile[data-type="image"] { --tile-color: var(--color-image); }
        .tile[data-type="vector"] { --tile-color: var(--color-vector); }
        .tile[data-type="video"] { --tile-color: var(--color-video); }
        .tile[data-type="audio"] { --tile-color: var(--color-audio); }
        .tile[data-type="code"] { --tile-color: var(--color-code); }
        .tile[data-type="doc"] { --tile-color: var(--color-doc); }
        .tile[data-type="pdf"] { --tile-color: var(--color-pdf); }
        .tile[data-type="data"] { --tile-color: var(--color-data); }
        .tile[data-type="config"] { --tile-color: var(--color-config); }
        .tile[data-type="archive"] { --tile-color: var(--color-archive); }
        .tile[data-type="model3d"] { --tile-color: var(--color-model3d); }
        .tile[data-type="font"] { --tile-color: var(--color-font); }
        .tile[data-type="notebook"] { --tile-color: var(--color-notebook); }
        .tile[data-type="executable"] { --tile-color: var(--color-executable); }
        .tile[data-type="database"] { --tile-color: var(--color-database); }
        .tile[data-type="binary"] { --tile-color: var(--color-binary); }

        .tile {
            border-color: color-mix(in oklch, var(--tile-color, var(--border)) 20%, transparent);
            background: linear-gradient(180deg, var(--card-bg) 0%, color-mix(in oklch, var(--tile-color, var(--card-bg)) 5%, var(--card-bg)) 100%);
        }

        .tile:hover {
            border-color: color-mix(in oklch, var(--tile-color, var(--accent)) 50%, transparent);
            box-shadow: var(--shadow-hover), 0 0 0 1px color-mix(in oklch, var(--tile-color) 20%, transparent);
        }

        /* Selected state - macOS style */
        .tile.selected {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--selection), var(--shadow-md);
            background: linear-gradient(180deg, color-mix(in srgb, var(--accent) 8%, var(--card-bg)) 0%, var(--card-bg) 100%);
        }

        .tile.selected::after {
            content: "✓";
            position: absolute;
            top: 8px;
            left: 8px;
            width: 22px;
            height: 22px;
            background: var(--accent);
            border-radius: 50%;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            justify-content: center;
            font-size: 0.7rem;
            color: white;
            z-index: 10;
        }

        /* Zone hint icons - 35% select / 65% open */
        .tile .zone-hint {
            position: absolute;
            bottom: 50%;
            transform: translateY(50%);
            font-size: 0.75rem;
            opacity: 0;
            transition: opacity var(--transition-fast);
            pointer-events: none;
            z-index: 15;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        }

        .tile .zone-hint.left {
            left: 12%; /* Centered in 35% zone */
        }

        .tile .zone-hint.right {
            right: 25%; /* Centered in 65% zone */
        }

        .tile:hover .zone-hint {
            opacity: 0.5;
        }

        /* Visual zone indicator on hover */
        .tile::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 35%;
            height: 100%;
            background: transparent;
            z-index: 5;
            pointer-events: none;
            transition: background var(--transition-fast);
            border-right: 1px dashed transparent;
        }

        .tile:hover::before {
            background: linear-gradient(90deg, rgba(10, 132, 255, 0.06) 0%, transparent 100%);
            border-right-color: rgba(10, 132, 255, 0.15);
        }

        /* Cut items appear faded */
        .tile.is-cut {
            opacity: 0.5;
        }

        .tile.is-cut::after {
            content: "—";
            position: absolute;
            top: 8px;
            right: 8px;
            font-size: 1rem;
            z-index: 10;
            color: var(--system-orange);
        }

        /* External drop zone */
        .grid-container.external-drop-active {
            background: rgba(10, 132, 255, 0.1);
            border: 2px dashed var(--accent);
            border-radius: 12px;
        }

        .grid-container.external-drop-active::before {
            content: "Drop files here to upload";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: var(--accent);
            font-size: 1.2rem;
            font-weight: 600;
            z-index: 100;
            pointer-events: none;
        }

        /* Toast notifications */
        /* macOS-style Toast */
        .toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            background: rgba(50, 50, 50, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 500;
            color: var(--text);
            opacity: 0;
            transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
            z-index: 500;
            box-shadow: var(--shadow-lg);
        }

        .toast.show {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }

        .toast.error {
            background: rgba(255, 69, 58, 0.9);
            border-color: rgba(255, 100, 90, 0.3);
            color: white;
        }

        /* macOS-style Selection Toolbar */
        .selection-bar {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(10px);
            background: rgba(50, 50, 50, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 8px 12px;
            display: none;
            align-items: center;
            gap: 8px;
            z-index: 100;
            box-shadow: var(--shadow-lg);
            opacity: 0;
            transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        .selection-bar.active {
            display: flex;
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }

        .selection-bar .count {
            font-size: 12px;
            color: var(--accent);
            font-weight: 600;
            padding: 0 8px;
            border-right: 1px solid rgba(255,255,255,0.1);
            margin-right: 4px;
        }

        .selection-bar button {
            padding: 5px 10px;
            border-radius: 6px;
            border: none;
            background: rgba(255,255,255,0.08);
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: var(--transition-fast);
        }

        .selection-bar button:hover {
            background: rgba(255,255,255,0.15);
            color: var(--text);
        }

        .selection-bar button:active {
            background: rgba(255,255,255,0.08);
        }

        .selection-bar button.danger:hover {
            background: rgba(255, 69, 58, 0.3);
            color: var(--system-red);
        }

        .tile .tile-info {
            border-top-color: color-mix(in oklch, var(--tile-color, var(--border)) 30%, transparent);
        }

        .tile .file-ext {
            background: color-mix(in oklch, var(--tile-color) 80%, black 60%);
            color: var(--tile-color);
        }

        /* Depth-based coloring for nested previews */
        .tile.folder .folder-grid .mini-item {
            background: color-mix(in oklch, var(--bg) 100%, black calc(var(--depth, 0) * 15%));
        }

        .tile.folder .folder-grid .mini-item.is-folder {
            box-shadow: inset 0 0 0 1px color-mix(in oklch, var(--color-folder) 30%, transparent);
        }

        .tile.folder .folder-grid .mini-item .nested-grid .nested-cell {
            background: color-mix(in oklch, var(--bg) 100%, black calc((var(--depth, 0) + 1) * 15%));
        }

        /* Filter dropdown */
        .filter-dropdown {
            position: relative;
        }

        .filter-btn {
            padding: 5px 12px;
            border-radius: 6px;
            border: none;
            background: rgba(255,255,255,0.08);
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: var(--transition-fast);
        }

        .filter-btn:hover {
            background: rgba(255,255,255,0.15);
            color: var(--text);
        }

        .filter-btn.active {
            background: var(--accent);
            color: white;
        }

        .filter-btn .filter-count {
            background: rgba(255,255,255,0.2);
            padding: 1px 6px;
            border-radius: 10px;
            font-size: 10px;
        }

        .filter-menu {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            margin-top: 6px;
            background: rgba(40, 40, 40, 0.98);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 6px;
            min-width: 180px;
            z-index: 200;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }

        .filter-menu.show {
            display: block;
            animation: fadeIn 0.15s ease;
        }

        .filter-menu label {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            color: var(--text-secondary);
            transition: var(--transition-fast);
        }

        .filter-menu label:hover {
            background: rgba(255,255,255,0.1);
            color: var(--text);
        }

        .filter-menu label input {
            accent-color: var(--accent);
        }

        .filter-menu label .color-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
        }

        .filter-menu .divider {
            height: 1px;
            background: rgba(255,255,255,0.1);
            margin: 6px 0;
        }

        /* Sort dropdown */
        .sort-dropdown {
            position: relative;
        }

        .sort-btn {
            padding: 5px 12px;
            border-radius: 6px;
            border: none;
            background: rgba(255,255,255,0.08);
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: var(--transition-fast);
        }

        .sort-btn:hover {
            background: rgba(255,255,255,0.15);
            color: var(--text);
        }

        .sort-menu {
            display: none;
            position: absolute;
            top: 100%;
            left: 0;
            margin-top: 6px;
            background: rgba(40, 40, 40, 0.98);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 6px;
            min-width: 160px;
            z-index: 200;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        }

        .sort-menu.show {
            display: block;
            animation: fadeIn 0.15s ease;
        }

        .sort-option {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            padding: 8px 12px;
            border: none;
            border-radius: 6px;
            background: transparent;
            color: var(--text-secondary);
            font-size: 13px;
            cursor: pointer;
            text-align: left;
            transition: var(--transition-fast);
        }

        .sort-option:hover {
            background: rgba(255,255,255,0.1);
            color: var(--text);
        }

        .sort-option .sort-check {
            opacity: 0;
            color: var(--accent);
        }

        .sort-option.active .sort-check {
            opacity: 1;
        }

        .sort-menu .divider {
            height: 1px;
            background: rgba(255,255,255,0.1);
            margin: 6px 0;
        }

        /* View mode toggle */
        .view-toggle {
            display: flex;
            gap: 2px;
            background: rgba(255,255,255,0.05);
            padding: 3px;
            border-radius: 8px;
        }

        .view-btn {
            padding: 6px 8px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            cursor: pointer;
            border-radius: 5px;
            transition: var(--transition-fast);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .view-btn:hover {
            background: rgba(255,255,255,0.1);
            color: var(--text);
        }

        .view-btn.active {
            background: rgba(255,255,255,0.15);
            color: var(--accent);
        }

        /* List view mode */
        .grid.view-list {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .grid.view-list .tile {
            width: 100% !important;
            height: 48px !important;
            aspect-ratio: auto;
            flex-direction: row;
            gap: 12px;
            padding: 8px 16px;
            border-radius: 8px;
        }

        .grid.view-list .tile .preview {
            width: 32px;
            height: 32px;
            min-width: 32px;
            flex-shrink: 0;
            border-radius: 4px;
        }

        .grid.view-list .tile .label {
            position: static;
            background: none;
            padding: 0;
            flex: 1;
            text-align: left;
            font-size: 13px;
        }

        .grid.view-list .tile .file-meta {
            display: flex;
            gap: 16px;
            color: var(--text-secondary);
            font-size: 11px;
        }

        .grid.view-list .tile .file-meta-item {
            min-width: 80px;
        }

        /* Column view mode */
        .grid.view-column {
            display: flex;
            flex-direction: row;
            gap: 1px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            overflow: hidden;
        }

        .grid.view-column .column-pane {
            flex: 1;
            min-width: 200px;
            max-width: 300px;
            background: rgba(30, 30, 30, 0.8);
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }

        .grid.view-column .column-item {
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            transition: var(--transition-fast);
        }

        .grid.view-column .column-item:hover {
            background: rgba(255,255,255,0.08);
        }

        .grid.view-column .column-item.selected {
            background: rgba(10, 132, 255, 0.3);
        }

        .grid.view-column .column-item.folder::after {
            content: '›';
            margin-left: auto;
            color: var(--text-secondary);
        }

        .grid.view-column .column-item-icon {
            width: 20px;
            height: 20px;
            border-radius: 3px;
            overflow: hidden;
            flex-shrink: 0;
        }

        .grid.view-column .column-item-icon img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .grid.view-column .column-item-name {
            flex: 1;
            font-size: 12px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        /* New folder button */
        .new-folder-btn {
            padding: 5px 12px;
            border-radius: 6px;
            border: none;
            background: rgba(48, 209, 88, 0.2);
            color: var(--system-green);
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: var(--transition-fast);
        }

        .new-folder-btn:hover {
            background: rgba(48, 209, 88, 0.35);
        }

        /* Context menu */
        .context-menu {
            display: none;
            position: fixed;
            background: rgba(40, 40, 40, 0.98);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px;
            padding: 6px;
            min-width: 220px;
            z-index: 300;
            box-shadow: 0 12px 40px rgba(0,0,0,0.5);
        }

        .context-menu.show {
            display: block;
            animation: fadeIn 0.1s ease;
        }

        .context-menu-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            color: var(--text-secondary);
            transition: background 0.1s ease;
        }

        .context-menu-item:hover {
            background: var(--accent);
            color: white;
        }

        .context-menu-item.danger:hover {
            background: var(--system-red);
        }

        .context-menu-item .label {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .context-menu-item .shortcut {
            font-size: 11px;
            opacity: 0.5;
            font-family: -apple-system, sans-serif;
        }

        .context-menu-item.disabled {
            opacity: 0.4;
            pointer-events: none;
        }

        .context-menu .divider {
            height: 1px;
            background: rgba(255,255,255,0.1);
            margin: 6px 0;
        }

        /* Rename input */
        .rename-input {
            width: 100%;
            padding: 6px 10px;
            border-radius: 6px;
            border: 2px solid var(--accent);
            background: var(--bg);
            color: var(--text);
            font-size: 12px;
            font-weight: 500;
            outline: none;
        }

        /* Settings panel */
        .settings-toggle {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: transparent;
            color: var(--text-dim);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        }

        .settings-toggle:hover {
            background: var(--border);
            color: var(--text);
        }

        .settings-panel {
            display: none;
            position: fixed;
            top: 48px;
            right: 0;
            width: 320px;
            height: calc(100vh - 48px);
            background: var(--card-bg);
            border-left: 1px solid var(--border);
            z-index: 150;
            overflow-y: auto;
            padding: 20px;
        }

        .settings-panel.active {
            display: block;
        }

        .settings-panel h3 {
            font-size: 0.9rem;
            color: var(--text);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .settings-section {
            margin-bottom: 24px;
        }

        .settings-section h4 {
            font-size: 0.75rem;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }

        .color-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
            padding: 8px;
            background: var(--bg);
            border-radius: 8px;
        }

        .color-preview {
            width: 24px;
            height: 24px;
            border-radius: 6px;
            flex-shrink: 0;
        }

        .color-label {
            flex: 1;
            font-size: 0.8rem;
            color: var(--text);
        }

        .oklch-inputs {
            display: flex;
            gap: 4px;
        }

        .oklch-input {
            width: 48px;
            padding: 4px 6px;
            border-radius: 4px;
            border: 1px solid var(--border);
            background: var(--card-bg);
            color: var(--text);
            font-size: 0.75rem;
            text-align: center;
        }

        .oklch-input:focus {
            outline: none;
            border-color: var(--accent);
        }

        .depth-slider-row {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .depth-slider-row label {
            font-size: 0.8rem;
            color: var(--text-dim);
            flex: 1;
        }

        .depth-slider-row input[type="range"] {
            width: 100px;
        }

        .depth-slider-row .value {
            font-size: 0.8rem;
            color: var(--text);
            width: 40px;
            text-align: right;
        }

        /* Settings Popup (Comprehensive) */
        .settings-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            z-index: 500;
            backdrop-filter: blur(4px);
        }
        .settings-overlay.active { display: flex; align-items: center; justify-content: center; }

        .settings-popup {
            background: var(--card-bg);
            border-radius: 16px;
            width: 560px;
            max-height: 85vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            border: 1px solid var(--border);
        }

        .settings-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 24px;
            border-bottom: 1px solid var(--border);
        }
        .settings-header h2 {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text);
            margin: 0;
        }
        .settings-close {
            width: 32px;
            height: 32px;
            border: none;
            background: transparent;
            color: var(--text-dim);
            font-size: 1.4rem;
            cursor: pointer;
            border-radius: 8px;
        }
        .settings-close:hover { background: var(--border); color: var(--text); }

        .settings-tabs {
            display: flex;
            border-bottom: 1px solid var(--border);
            padding: 0 24px;
            gap: 4px;
        }
        .settings-tab {
            padding: 12px 16px;
            background: transparent;
            border: none;
            color: var(--text-dim);
            font-size: 0.85rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -1px;
            transition: all 0.15s;
        }
        .settings-tab:hover { color: var(--text); }
        .settings-tab.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
        }

        .settings-body {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
        }

        .settings-tab-content { display: none; }
        .settings-tab-content.active { display: block; }

        .setting-group {
            margin-bottom: 24px;
        }
        .setting-group:last-child { margin-bottom: 0; }
        .setting-group h4 {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-dim);
            margin: 0 0 12px 0;
        }

        .setting-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 16px;
            background: var(--bg);
            border-radius: 10px;
            margin-bottom: 8px;
        }
        .setting-row:last-child { margin-bottom: 0; }
        .setting-row label {
            font-size: 0.85rem;
            color: var(--text);
        }
        .setting-row .setting-desc {
            font-size: 0.75rem;
            color: var(--text-dim);
            margin-top: 2px;
        }

        /* Setting Controls */
        .setting-toggle {
            position: relative;
            width: 44px;
            height: 24px;
            background: var(--border);
            border-radius: 12px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .setting-toggle.active { background: var(--accent); }
        .setting-toggle::after {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            transition: transform 0.2s;
        }
        .setting-toggle.active::after { transform: translateX(20px); }

        .setting-select {
            padding: 8px 12px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            font-size: 0.85rem;
            min-width: 140px;
        }
        .setting-select:focus { outline: none; border-color: var(--accent); }

        .setting-slider {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .setting-slider input[type="range"] {
            width: 120px;
        }
        .setting-slider .slider-value {
            font-size: 0.8rem;
            color: var(--text);
            min-width: 40px;
            text-align: right;
        }

        .setting-input {
            padding: 8px 12px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            font-size: 0.85rem;
            width: 100px;
        }

        .theme-selector {
            display: flex;
            gap: 8px;
        }
        .theme-option {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            border: 2px solid transparent;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }
        .theme-option.dark-theme { background: #18181b; }
        .theme-option.light-theme { background: #f4f4f5; }
        .theme-option.active { border-color: var(--accent); }

        .keyboard-shortcuts {
            display: grid;
            gap: 8px;
        }
        .shortcut-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: var(--bg);
            border-radius: 8px;
        }
        .shortcut-key {
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }
        .shortcut-key kbd {
            background: var(--border);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-family: monospace;
        }
        .shortcut-action {
            color: var(--text-dim);
            font-size: 0.8rem;
        }

        .settings-footer {
            padding: 16px 24px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .settings-footer button {
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.85rem;
            cursor: pointer;
        }
        .btn-reset {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-dim);
        }
        .btn-reset:hover { border-color: var(--text-dim); color: var(--text); }
        .btn-save {
            background: var(--accent);
            border: none;
            color: white;
        }
        .btn-save:hover { opacity: 0.9; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #2a2a32; }

        /* Loading state */
        .loading-tile .tile-preview {
            background: linear-gradient(90deg, var(--card-bg) 25%, #1a1a1f 50%, var(--card-bg) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
        }

        @keyframes shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
    </style>
</head>
<body>
    <div class="topbar">
        <div class="nav-group">
            <button class="nav-btn" id="btn-back" onclick="goBack()" title="Back (History)">‹</button>
            <button class="nav-btn" id="btn-up" onclick="goUp()" title="Enclosing Folder">↑</button>
        </div>
        <div class="history-btns">
            <button class="nav-btn" id="undo-btn" onclick="performUndo()" disabled title="Undo (Cmd+Z)">⟲</button>
            <button class="nav-btn" id="redo-btn" onclick="performRedo()" disabled title="Redo (Cmd+Shift+Z)">⟳</button>
        </div>
        <div class="path-display" id="path-display"></div>

        <!-- Filter Dropdown -->
        <div class="filter-dropdown">
            <button class="filter-btn" id="filter-btn" onclick="toggleFilterMenu()">
                <span>Filter</span>
                <span class="filter-count" id="filter-count" style="display:none">0</span>
                <span>▾</span>
            </button>
            <div class="filter-menu" id="filter-menu">
                <label><input type="checkbox" value="all" checked onchange="toggleAllFilters(this)"> <span>All Files</span></label>
                <div class="divider"></div>
                <label><input type="checkbox" value="folder" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-folder)"></span> Folders</label>
                <label><input type="checkbox" value="image" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-image)"></span> Images</label>
                <label><input type="checkbox" value="vector" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-vector)"></span> Vector</label>
                <label><input type="checkbox" value="video" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-video)"></span> Videos</label>
                <label><input type="checkbox" value="audio" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-audio)"></span> Audio</label>
                <label><input type="checkbox" value="code" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-code)"></span> Code</label>
                <label><input type="checkbox" value="doc" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-doc)"></span> Documents</label>
                <label><input type="checkbox" value="pdf" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-pdf)"></span> PDFs</label>
                <label><input type="checkbox" value="data" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-data)"></span> Data</label>
                <label><input type="checkbox" value="config" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-config)"></span> Config</label>
                <label><input type="checkbox" value="archive" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-archive)"></span> Archives</label>
                <label><input type="checkbox" value="model3d" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-model3d)"></span> 3D Models</label>
                <label><input type="checkbox" value="font" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-font)"></span> Fonts</label>
                <label><input type="checkbox" value="notebook" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-notebook)"></span> Notebooks</label>
                <label><input type="checkbox" value="executable" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-executable)"></span> Executables</label>
                <label><input type="checkbox" value="database" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-database)"></span> Databases</label>
                <label><input type="checkbox" value="binary" checked onchange="updateFilters()"> <span class="color-dot" style="background:var(--color-binary)"></span> Other</label>
            </div>
        </div>

        <!-- Sort Dropdown -->
        <div class="sort-dropdown">
            <button class="sort-btn" id="sort-btn" onclick="toggleSortMenu()">
                <span id="sort-label">Name</span>
                <span id="sort-dir">↑</span>
            </button>
            <div class="sort-menu" id="sort-menu">
                <button class="sort-option active" data-sort="name" onclick="setSort('name')">
                    <span>Name</span>
                    <span class="sort-check">✓</span>
                </button>
                <button class="sort-option" data-sort="date" onclick="setSort('date')">
                    <span>Date Modified</span>
                    <span class="sort-check">✓</span>
                </button>
                <button class="sort-option" data-sort="size" onclick="setSort('size')">
                    <span>Size</span>
                    <span class="sort-check">✓</span>
                </button>
                <button class="sort-option" data-sort="type" onclick="setSort('type')">
                    <span>Type</span>
                    <span class="sort-check">✓</span>
                </button>
                <div class="divider"></div>
                <button class="sort-option" id="sort-asc" onclick="setSortDirection('asc')">
                    <span>Ascending ↑</span>
                    <span class="sort-check">✓</span>
                </button>
                <button class="sort-option" id="sort-desc" onclick="setSortDirection('desc')">
                    <span>Descending ↓</span>
                    <span class="sort-check">✓</span>
                </button>
            </div>
        </div>

        <!-- View Mode Toggle -->
        <div class="view-toggle">
            <button class="view-btn active" data-view="grid" onclick="setViewMode('grid')" title="Grid View">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <rect x="1" y="1" width="6" height="6" rx="1"/>
                    <rect x="9" y="1" width="6" height="6" rx="1"/>
                    <rect x="1" y="9" width="6" height="6" rx="1"/>
                    <rect x="9" y="9" width="6" height="6" rx="1"/>
                </svg>
            </button>
            <button class="view-btn" data-view="list" onclick="setViewMode('list')" title="List View">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <rect x="1" y="2" width="3" height="3" rx="0.5"/>
                    <rect x="6" y="2" width="9" height="3" rx="0.5"/>
                    <rect x="1" y="7" width="3" height="3" rx="0.5"/>
                    <rect x="6" y="7" width="9" height="3" rx="0.5"/>
                    <rect x="1" y="12" width="3" height="3" rx="0.5"/>
                    <rect x="6" y="12" width="9" height="3" rx="0.5"/>
                </svg>
            </button>
            <button class="view-btn" data-view="column" onclick="setViewMode('column')" title="Column View">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <rect x="1" y="1" width="4" height="14" rx="1"/>
                    <rect x="6" y="1" width="4" height="14" rx="1"/>
                    <rect x="11" y="1" width="4" height="14" rx="1"/>
                </svg>
            </button>
        </div>

        <!-- New Folder Button -->
        <button class="new-folder-btn" onclick="createNewFolder()" title="New Folder (Cmd+Shift+N)">+ New</button>

        <input type="text" class="search-input" id="search" placeholder="Search">
        <label class="select-mode-toggle" id="select-mode-toggle" title="Selection Mode: Click anywhere to select">
            <input type="checkbox" id="select-mode-checkbox">
            <span class="toggle-switch"></span>
            <span>Select</span>
        </label>
        <div class="size-control">
            <span>Size</span>
            <input type="range" min="180" max="450" value="280" id="tile-size">
        </div>
        <div class="memory-stats" id="memory-stats" title="Memory usage (click to force cleanup)">
            <span class="mem-label">MEM:</span>
            <span class="mem-value" id="mem-value">--</span>
        </div>
        <button class="settings-toggle" id="settings-toggle" title="Color Settings"><span class="icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg></span></button>
    </div>

    <!-- Settings Panel (Old - kept for color settings render) -->
    <div class="settings-panel" id="settings-panel" style="display:none"></div>

    <!-- Comprehensive Settings Popup -->
    <div class="settings-overlay" id="settings-overlay">
        <div class="settings-popup">
            <div class="settings-header">
                <h2>Settings</h2>
                <button class="settings-close" onclick="closeSettings()">×</button>
            </div>
            <div class="settings-tabs">
                <button class="settings-tab active" data-tab="display">Display</button>
                <button class="settings-tab" data-tab="behavior">Behavior</button>
                <button class="settings-tab" data-tab="colors">Colors</button>
                <button class="settings-tab" data-tab="shortcuts">Shortcuts</button>
                <button class="settings-tab" data-tab="about">About</button>
            </div>
            <div class="settings-body">
                <!-- Display Tab -->
                <div class="settings-tab-content active" id="tab-display">
                    <div class="setting-group">
                        <h4>Theme</h4>
                        <div class="setting-row">
                            <div>
                                <label>Appearance</label>
                                <div class="setting-desc">Choose light or dark theme</div>
                            </div>
                            <div class="theme-selector">
                                <div class="theme-option dark-theme active" data-theme="dark" onclick="setTheme('dark')">🌙</div>
                                <div class="theme-option light-theme" data-theme="light" onclick="setTheme('light')">☀️</div>
                            </div>
                        </div>
                    </div>
                    <div class="setting-group">
                        <h4>Grid Layout</h4>
                        <div class="setting-row">
                            <div>
                                <label>Card Size</label>
                                <div class="setting-desc">Default size for file cards</div>
                            </div>
                            <div class="setting-slider">
                                <input type="range" min="180" max="450" value="280" id="settings-tile-size" oninput="updateTileSize(this.value)">
                                <span class="slider-value" id="tile-size-value">280px</span>
                            </div>
                        </div>
                        <div class="setting-row">
                            <div>
                                <label>Grid Gap</label>
                                <div class="setting-desc">Space between cards</div>
                            </div>
                            <div class="setting-slider">
                                <input type="range" min="8" max="32" value="17" id="settings-grid-gap" oninput="updateGridGap(this.value)">
                                <span class="slider-value" id="grid-gap-value">17px</span>
                            </div>
                        </div>
                        <div class="setting-row">
                            <div>
                                <label>Items Per Page</label>
                                <div class="setting-desc">Max visible items for performance</div>
                            </div>
                            <select class="setting-select" id="settings-max-items" onchange="updateMaxItems(this.value)">
                                <option value="100">100 items</option>
                                <option value="200" selected>200 items</option>
                                <option value="500">500 items</option>
                                <option value="1000">1000 items</option>
                            </select>
                        </div>
                    </div>
                    <div class="setting-group">
                        <h4>Visibility</h4>
                        <div class="setting-row">
                            <div>
                                <label>Show Hidden Files</label>
                                <div class="setting-desc">Display files starting with dot</div>
                            </div>
                            <div class="setting-toggle" id="toggle-hidden" onclick="toggleSetting('showHidden')"></div>
                        </div>
                        <div class="setting-row">
                            <div>
                                <label>Show File Extensions</label>
                                <div class="setting-desc">Display file extensions in names</div>
                            </div>
                            <div class="setting-toggle active" id="toggle-extensions" onclick="toggleSetting('showExtensions')"></div>
                        </div>
                        <div class="setting-row">
                            <div>
                                <label>Show Sidebar</label>
                                <div class="setting-desc">Parent folder preview panel</div>
                            </div>
                            <div class="setting-toggle active" id="toggle-sidebar" onclick="toggleSetting('showSidebar')"></div>
                        </div>
                    </div>
                </div>

                <!-- Behavior Tab -->
                <div class="settings-tab-content" id="tab-behavior">
                    <div class="setting-group">
                        <h4>File Operations</h4>
                        <div class="setting-row">
                            <div>
                                <label>Confirm Delete</label>
                                <div class="setting-desc">Ask before moving to trash</div>
                            </div>
                            <div class="setting-toggle active" id="toggle-confirm-delete" onclick="toggleSetting('confirmDelete')"></div>
                        </div>
                        <div class="setting-row">
                            <div>
                                <label>Auto Refresh</label>
                                <div class="setting-desc">Reload folder on file changes</div>
                            </div>
                            <div class="setting-toggle" id="toggle-auto-refresh" onclick="toggleSetting('autoRefresh')"></div>
                        </div>
                    </div>
                    <div class="setting-group">
                        <h4>Sorting</h4>
                        <div class="setting-row">
                            <div>
                                <label>Sort By</label>
                                <div class="setting-desc">Default sort order for files</div>
                            </div>
                            <select class="setting-select" id="settings-sort-by" onchange="updateSortBy(this.value)">
                                <option value="name">Name</option>
                                <option value="modified">Date Modified</option>
                                <option value="size">Size</option>
                                <option value="type">Type</option>
                            </select>
                        </div>
                        <div class="setting-row">
                            <div>
                                <label>Sort Order</label>
                                <div class="setting-desc">Ascending or descending</div>
                            </div>
                            <select class="setting-select" id="settings-sort-order" onchange="updateSortOrder(this.value)">
                                <option value="asc">Ascending (A-Z)</option>
                                <option value="desc">Descending (Z-A)</option>
                            </select>
                        </div>
                        <div class="setting-row">
                            <div>
                                <label>Folders First</label>
                                <div class="setting-desc">Always show folders at the top</div>
                            </div>
                            <div class="setting-toggle active" id="toggle-folders-first" onclick="toggleSetting('foldersFirst')"></div>
                        </div>
                    </div>
                    <div class="setting-group">
                        <h4>Interaction</h4>
                        <div class="setting-row">
                            <div>
                                <label>Double-Click Action</label>
                                <div class="setting-desc">What happens on double-click</div>
                            </div>
                            <select class="setting-select" id="settings-double-click" onchange="updateDoubleClick(this.value)">
                                <option value="open">Open in App</option>
                                <option value="preview">Quick Look</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Colors Tab -->
                <div class="settings-tab-content" id="tab-colors">
                    <div class="setting-group">
                        <h4>Depth Darkening</h4>
                        <div class="setting-row">
                            <div>
                                <label>Factor per Level</label>
                                <div class="setting-desc">How much to darken nested folders</div>
                            </div>
                            <div class="setting-slider">
                                <input type="range" min="70" max="100" value="85" id="settings-depth-factor" oninput="updateDepthFactor(this.value)">
                                <span class="slider-value" id="depth-factor-value">0.85</span>
                            </div>
                        </div>
                    </div>
                    <div class="setting-group">
                        <h4>File Type Colors (OKLCH)</h4>
                        <div id="color-settings"></div>
                    </div>
                </div>

                <!-- Shortcuts Tab -->
                <div class="settings-tab-content" id="tab-shortcuts">
                    <div class="setting-group">
                        <h4>Navigation</h4>
                        <div class="keyboard-shortcuts">
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⌘</kbd><kbd>↑</kbd></span>
                                <span class="shortcut-action">Go to parent folder</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⌘</kbd><kbd>[</kbd></span>
                                <span class="shortcut-action">Go back in history</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>Enter</kbd></span>
                                <span class="shortcut-action">Open selected item</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>Space</kbd></span>
                                <span class="shortcut-action">Quick Look preview</span>
                            </div>
                        </div>
                    </div>
                    <div class="setting-group">
                        <h4>File Operations</h4>
                        <div class="keyboard-shortcuts">
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⌘</kbd><kbd>C</kbd></span>
                                <span class="shortcut-action">Copy</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⌘</kbd><kbd>X</kbd></span>
                                <span class="shortcut-action">Cut</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⌘</kbd><kbd>V</kbd></span>
                                <span class="shortcut-action">Paste</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⌘</kbd><kbd>⌫</kbd></span>
                                <span class="shortcut-action">Move to Trash</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⌘</kbd><kbd>D</kbd></span>
                                <span class="shortcut-action">Duplicate</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⇧</kbd><kbd>⌘</kbd><kbd>N</kbd></span>
                                <span class="shortcut-action">New Folder</span>
                            </div>
                        </div>
                    </div>
                    <div class="setting-group">
                        <h4>Selection</h4>
                        <div class="keyboard-shortcuts">
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⌘</kbd><kbd>A</kbd></span>
                                <span class="shortcut-action">Select All</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>Esc</kbd></span>
                                <span class="shortcut-action">Clear selection / Close</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⌘</kbd><kbd>Z</kbd></span>
                                <span class="shortcut-action">Undo</span>
                            </div>
                            <div class="shortcut-row">
                                <span class="shortcut-key"><kbd>⇧</kbd><kbd>⌘</kbd><kbd>Z</kbd></span>
                                <span class="shortcut-action">Redo</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- About Tab -->
                <div class="settings-tab-content" id="tab-about">
                    <div class="setting-group">
                        <h4>File Explorer</h4>
                        <div class="setting-row" style="flex-direction: column; align-items: flex-start;">
                            <label style="font-size: 1rem; font-weight: 600;">Higgsfield-style File Explorer</label>
                            <div class="setting-desc" style="margin-top: 8px;">
                                A modern, visual file browser with full preview tiles. Features include Touch ID / Face ID authentication,
                                undo/redo for file operations, drag-select, lightbox preview, and 17 color categories for 150+ file formats.
                            </div>
                        </div>
                    </div>
                    <div class="setting-group">
                        <h4>Features</h4>
                        <div class="setting-row" style="flex-direction: column; align-items: flex-start; gap: 8px;">
                            <div>✓ Touch ID / Face ID authentication</div>
                            <div>✓ Path traversal security</div>
                            <div>✓ 17 color categories with OKLCH colors</div>
                            <div>✓ 150+ file format mappings</div>
                            <div>✓ Undo/redo for file operations</div>
                            <div>✓ Selection mode with drag-select</div>
                            <div>✓ Lightbox preview with navigation</div>
                            <div>✓ Context menu with full operations</div>
                            <div>✓ Type filters and search</div>
                            <div>✓ 3D model preview (GLTF, GLB, OBJ)</div>
                        </div>
                    </div>
                    <div class="setting-group">
                        <h4>Security</h4>
                        <div class="setting-row" style="flex-direction: column; align-items: flex-start;">
                            <div class="setting-desc">
                                • Bound to localhost only (127.0.0.1)<br>
                                • Path traversal protection enabled<br>
                                • Biometric authentication required<br>
                                • Session tokens with HttpOnly cookies
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="settings-footer">
                <button class="btn-reset" onclick="resetSettings()">Reset to Defaults</button>
                <button class="btn-save" onclick="saveAndCloseSettings()">Done</button>
            </div>
        </div>
    </div>

    <div class="main-layout">
        <!-- Sidebar - Previous Level -->
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header" id="sidebar-header" onclick="navigateToParent()">
                <span class="back-icon">‹</span>
                <div>
                    <div class="sidebar-title" id="sidebar-title">Parent</div>
                    <div class="sidebar-path" id="sidebar-path"></div>
                </div>
            </div>
            <div class="sidebar-mode-toggle">
                <button class="sidebar-mode-btn active" id="mode-grouped" onclick="setSidebarMode('grouped')">Grouped</button>
                <button class="sidebar-mode-btn" id="mode-flat" onclick="setSidebarMode('flat')">List</button>
            </div>
            <div class="sidebar-content" id="sidebar-content"></div>
        </div>

        <!-- Main Grid -->
        <div class="grid-container">
            <div class="grid" id="grid"></div>
        </div>
    </div>

    <!-- Selection toolbar -->
    <div class="selection-bar" id="selection-bar">
        <span class="count"><span id="sel-count">0</span> selected</span>
        <button onclick="copySelected()"><span class="icon"><svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg></span> Copy</button>
        <button onclick="cutSelected()"><span class="icon"><svg viewBox="0 0 24 24"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg></span> Cut</button>
        <button onclick="pasteToCurrentFolder()" id="paste-btn" style="display:none"><span class="icon"><svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg></span> Paste</button>
        <button onclick="deleteSelected()" class="danger"><span class="icon"><svg viewBox="0 0 24 24"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6"/><path d="M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg></span> Delete</button>
        <button onclick="selectedFiles.clear(); renderGrid();">✕</button>
    </div>

    <div class="lightbox" id="lightbox">
        <div class="lightbox-backdrop" onclick="closeLightbox()"></div>
        <div class="lightbox-container">
            <!-- Edit Sidebar -->
            <div class="lightbox-sidebar" id="lightbox-sidebar">
                <div class="sidebar-format-badge" id="format-badge">
                    <span class="format-icon"><span class="icon"><svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/><polyline points="14 2 14 8 20 8"/></svg></span></span>
                    <span class="format-name">Unknown</span>
                </div>
                <div class="sidebar-section">
                    <div class="sidebar-section-title">File Info</div>
                    <div class="sidebar-info" id="sidebar-file-info">
                        <div class="info-row"><span>Size:</span><span id="info-size">-</span></div>
                        <div class="info-row"><span>Modified:</span><span id="info-modified">-</span></div>
                        <div class="info-row"><span>Type:</span><span id="info-type">-</span></div>
                    </div>
                </div>
                <div class="sidebar-section">
                    <div class="sidebar-section-title">Quick Actions</div>
                    <div class="sidebar-tools" id="sidebar-tools">
                        <button class="tool-btn" onclick="openInApp()" title="Open in default app">
                            <span class="tool-icon"><span class="icon"><svg viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg></span></span>
                            <span class="tool-label">Open</span>
                        </button>
                        <button class="tool-btn" onclick="downloadFile()" title="Download file">
                            <span class="tool-icon"><span class="icon"><svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></span></span>
                            <span class="tool-label">Download</span>
                        </button>
                        <button class="tool-btn" onclick="copyFilePath()" title="Copy file path">
                            <span class="tool-icon"><span class="icon"><svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg></span></span>
                            <span class="tool-label">Path</span>
                        </button>
                        <button class="tool-btn" onclick="showFileInfo()" title="Show metadata">
                            <span class="tool-icon"><span class="icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg></span></span>
                            <span class="tool-label">Info</span>
                        </button>
                    </div>
                </div>
                <div class="sidebar-section" id="format-tools-section" style="display:none;">
                    <div class="sidebar-section-title">Format Tools</div>
                    <div class="sidebar-tools" id="format-tools">
                        <!-- Populated dynamically based on file type -->
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="lightbox-inner">
                <div class="lightbox-header">
                    <div class="lightbox-title" id="lightbox-title"></div>
                    <div class="zoom-controls">
                        <button class="zoom-btn" onclick="zoomOut()" title="Zoom out">−</button>
                        <span class="zoom-level" id="zoom-level">100%</span>
                        <button class="zoom-btn" onclick="zoomIn()" title="Zoom in">+</button>
                        <button class="zoom-btn" onclick="zoomReset()" title="Reset zoom">⟲</button>
                    </div>
                    <button class="lightbox-close" onclick="closeLightbox()">×</button>
                </div>
                <div class="lightbox-content" id="lightbox-content"></div>
                <button class="lightbox-nav prev" onclick="navLightbox(-1)">‹</button>
                <button class="lightbox-nav next" onclick="navLightbox(1)">›</button>
            </div>
        </div>
    </div>

    <!-- Context Menu -->
    <div class="context-menu" id="context-menu"></div>

    <script>
        const INITIAL_PATH = '{{BROWSE_ROOT}}';
        let currentPath = '';
        let files = [];
        let filteredFiles = [];
        let history = [];
        let historyIndex = -1;
        let currentLightboxIndex = -1;
        let parentPath = null;
        let parentFiles = [];

        // Minimal SVG Icons - geometric shapes only
        const ICONS = {
            folder: `<svg viewBox="0 0 24 24"><path d="M3 7v10c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V9c0-1.1-.9-2-2-2h-6l-2-2H5c-1.1 0-2 .9-2 2z"/></svg>`,
            folderOpen: `<svg viewBox="0 0 24 24"><path d="M5 19h14l3-8H8l-3 8zm0 0V7c0-1.1.9-2 2-2h4l2 2h6c1.1 0 2 .9 2 2v1"/></svg>`,
            file: `<svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/><polyline points="14 2 14 8 20 8"/></svg>`,
            image: `<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`,
            video: `<svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><polygon points="10 9 15 12 10 15"/></svg>`,
            audio: `<svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>`,
            code: `<svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
            pdf: `<svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/><path d="M9 13h2v4H9z M13 11h2v6h-2z"/></svg>`,
            archive: `<svg viewBox="0 0 24 24"><path d="M21 8v13H3V8"/><path d="M1 3h22v5H1z"/><path d="M10 12h4"/></svg>`,
            data: `<svg viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>`,
            copy: `<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>`,
            compress: `<svg viewBox="0 0 24 24"><path d="M21 8v13H3V8"/><path d="M1 3h22v5H1z"/><path d="M12 11v6m-3-3l3 3 3-3"/></svg>`,
            eye: `<svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
            newFolder: `<svg viewBox="0 0 24 24"><path d="M3 7v10c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V9c0-1.1-.9-2-2-2h-6l-2-2H5c-1.1 0-2 .9-2 2z"/><line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/></svg>`,
            duplicate: `<svg viewBox="0 0 24 24"><rect x="8" y="8" width="14" height="14" rx="2"/><path d="M4 16V4a2 2 0 012-2h12"/></svg>`,
            filter: `<svg viewBox="0 0 24 24"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>`,
            resize: `<svg viewBox="0 0 24 24"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>`,
            extract: `<svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>`,
            lock: `<svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>`,
            stats: `<svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`,
            edit: `<svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`,
            scale: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v8m-4-4h8"/></svg>`,
            info: `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`,
            model3d: `<svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>`,
        };

        function icon(name, size = '') {
            const sizeClass = size ? `icon-${size}` : '';
            return `<span class="icon ${sizeClass}">${ICONS[name] || ICONS.file}</span>`;
        }

        // Memory management - track resources for cleanup
        const resourceTracker = {
            threeRenderers: new Map(),  // canvasId -> {renderer, scene, camera, animationId}
            modelViewers: new Set(),    // model-viewer elements
            intersectionObserver: null,
            pendingFetches: new Set(),  // track in-flight requests
            maxConcurrentFetches: 4,    // limit concurrent folder preview fetches
            fetchQueue: [],             // queued fetch requests
        };

        // Cleanup all Three.js resources before grid re-render
        function cleanupThreeResources() {
            resourceTracker.threeRenderers.forEach((resources, canvasId) => {
                try {
                    if (resources.animationId) {
                        cancelAnimationFrame(resources.animationId);
                    }
                    if (resources.renderer) {
                        resources.renderer.dispose();
                        resources.renderer.forceContextLoss();
                    }
                    if (resources.scene) {
                        resources.scene.traverse((obj) => {
                            if (obj.geometry) obj.geometry.dispose();
                            if (obj.material) {
                                if (Array.isArray(obj.material)) {
                                    obj.material.forEach(m => m.dispose());
                                } else {
                                    obj.material.dispose();
                                }
                            }
                        });
                    }
                } catch (e) { console.warn('Cleanup error:', e); }
            });
            resourceTracker.threeRenderers.clear();

            // Cleanup model-viewer elements - find all in grid and stop them
            const grid = document.getElementById('grid');
            if (grid) {
                const modelViewers = grid.querySelectorAll('model-viewer');
                modelViewers.forEach(mv => {
                    try {
                        // model-viewer cleanup
                        mv.remove();
                    } catch (e) {}
                });
            }

            // Cancel pending fetches
            resourceTracker.pendingFetches.clear();
            resourceTracker.fetchQueue = [];
        }

        // Throttled fetch for folder previews
        async function throttledFetch(url) {
            return new Promise((resolve, reject) => {
                const doFetch = async (fetchUrl, res, rej) => {
                    resourceTracker.pendingFetches.add(fetchUrl);
                    try {
                        const response = await fetch(fetchUrl);
                        const data = await response.json();
                        res(data);
                    } catch (e) {
                        rej(e);
                    } finally {
                        resourceTracker.pendingFetches.delete(fetchUrl);
                        // Process next in queue
                        if (resourceTracker.fetchQueue.length > 0) {
                            const next = resourceTracker.fetchQueue.shift();
                            doFetch(next.url, next.resolve, next.reject);
                        }
                    }
                };

                if (resourceTracker.pendingFetches.size >= resourceTracker.maxConcurrentFetches) {
                    // Queue the request
                    resourceTracker.fetchQueue.push({ url, resolve, reject });
                } else {
                    doFetch(url, resolve, reject);
                }
            });
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // STL Preview with Three.js
        function initSTLPreview(canvasId, filePath) {
            const canvas = document.getElementById(canvasId);
            if (!canvas || !window.THREE) return;

            // Skip if already initialized
            if (resourceTracker.threeRenderers.has(canvasId)) return;

            const rect = canvas.parentElement.getBoundingClientRect();
            const width = rect.width || 200;
            const height = rect.height || 200;

            canvas.width = width;
            canvas.height = height;

            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0f);

            const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
            camera.position.set(0, 0, 100);

            const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
            renderer.setSize(width, height);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            // Register with resource tracker
            resourceTracker.threeRenderers.set(canvasId, { renderer, scene, camera, animationId: null });

            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
            directionalLight.position.set(1, 1, 1);
            scene.add(directionalLight);

            const directionalLight2 = new THREE.DirectionalLight(0x6366f1, 0.5);
            directionalLight2.position.set(-1, -1, -1);
            scene.add(directionalLight2);

            // Load STL
            const loader = new THREE.STLLoader();
            loader.load('/file' + filePath, (geometry) => {
                geometry.computeBoundingBox();
                geometry.center();

                const material = new THREE.MeshPhongMaterial({
                    color: 0x6366f1,
                    specular: 0x444444,
                    shininess: 100
                });

                const mesh = new THREE.Mesh(geometry, material);

                // Scale to fit
                const box = geometry.boundingBox;
                const maxDim = Math.max(
                    box.max.x - box.min.x,
                    box.max.y - box.min.y,
                    box.max.z - box.min.z
                );
                const scale = 50 / maxDim;
                mesh.scale.set(scale, scale, scale);

                scene.add(mesh);

                // Auto-rotate animation
                function animate() {
                    const tracked = resourceTracker.threeRenderers.get(canvasId);
                    if (!tracked) return; // Cleaned up, stop animating
                    tracked.animationId = requestAnimationFrame(animate);
                    mesh.rotation.y += 0.01;
                    mesh.rotation.x += 0.005;
                    renderer.render(scene, camera);
                }
                animate();
            }, undefined, (error) => {
                console.warn('STL load error:', filePath, error);
            });
        }

        // PDF Preview with PDF.js
        async function initPDFPreview(canvasId, filePath) {
            const canvas = document.getElementById(canvasId);
            if (!canvas || !window.pdfjsLib) return;

            try {
                // Set worker path
                pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

                const loadingTask = pdfjsLib.getDocument('/file' + filePath);
                const pdf = await loadingTask.promise;
                const page = await pdf.getPage(1);

                // Calculate scale to fit the preview
                const container = canvas.parentElement;
                const containerWidth = container.clientWidth || 200;
                const containerHeight = container.clientHeight || 200;

                const viewport = page.getViewport({ scale: 1 });
                const scale = Math.min(
                    containerWidth / viewport.width,
                    containerHeight / viewport.height
                ) * window.devicePixelRatio;

                const scaledViewport = page.getViewport({ scale });

                canvas.width = scaledViewport.width;
                canvas.height = scaledViewport.height;
                canvas.style.width = (scaledViewport.width / window.devicePixelRatio) + 'px';
                canvas.style.height = (scaledViewport.height / window.devicePixelRatio) + 'px';

                const ctx = canvas.getContext('2d');
                await page.render({
                    canvasContext: ctx,
                    viewport: scaledViewport
                }).promise;

                // Update label with page count
                const label = container.querySelector('.pdf-page-label');
                if (label) {
                    label.textContent = pdf.numPages > 1 ? `${pdf.numPages} pages` : 'PDF';
                }
            } catch (error) {
                console.warn('PDF preview error:', filePath, error);
                // Fallback to icon
                const container = canvas.parentElement;
                if (container) {
                    container.innerHTML = `<span class="pdf-icon">${icon('pdf', 'lg')}</span><span class="pdf-label">PDF</span>`;
                }
            }
        }

        // STL Lightbox with OrbitControls
        function initSTLLightbox(canvasId, filePath) {
            const canvas = document.getElementById(canvasId);
            if (!canvas || !window.THREE) return;

            const width = canvas.clientWidth || 800;
            const height = canvas.clientHeight || 600;

            canvas.width = width * window.devicePixelRatio;
            canvas.height = height * window.devicePixelRatio;

            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0d1117);

            const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 2000);
            camera.position.set(100, 100, 100);

            const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
            renderer.setSize(width, height);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;

            // Orbit controls
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            // Lighting
            const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
            directionalLight.position.set(50, 100, 50);
            directionalLight.castShadow = true;
            scene.add(directionalLight);

            const fillLight = new THREE.DirectionalLight(0x6366f1, 0.4);
            fillLight.position.set(-50, -50, -50);
            scene.add(fillLight);

            // Grid helper
            const gridHelper = new THREE.GridHelper(200, 20, 0x303030, 0x202020);
            scene.add(gridHelper);

            // Load STL
            const loader = new THREE.STLLoader();
            loader.load('/file' + filePath, (geometry) => {
                geometry.computeBoundingBox();
                geometry.center();

                const material = new THREE.MeshPhongMaterial({
                    color: 0x6366f1,
                    specular: 0x666666,
                    shininess: 80
                });

                const mesh = new THREE.Mesh(geometry, material);
                mesh.castShadow = true;
                mesh.receiveShadow = true;

                // Scale to fit
                const box = geometry.boundingBox;
                const maxDim = Math.max(
                    box.max.x - box.min.x,
                    box.max.y - box.min.y,
                    box.max.z - box.min.z
                );
                const scale = 80 / maxDim;
                mesh.scale.set(scale, scale, scale);
                mesh.position.y = (box.max.y - box.min.y) * scale / 2;

                scene.add(mesh);

                // Adjust camera
                camera.position.set(100, 80, 100);
                controls.target.set(0, (box.max.y - box.min.y) * scale / 2, 0);
                controls.update();
            }, undefined, (error) => {
                console.warn('STL lightbox load error:', filePath, error);
            });

            let animationId;
            function animate() {
                animationId = requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }
            animate();

            // Cleanup
            const checkLightbox = setInterval(() => {
                if (!document.getElementById('lightbox').classList.contains('active')) {
                    cancelAnimationFrame(animationId);
                    renderer.dispose();
                    controls.dispose();
                    clearInterval(checkLightbox);
                }
            }, 500);
        }

        // OKLCH Color System
        const FILE_COLORS = {
            // Intense OKLCH colors (higher chroma = more vivid)
            folder: { l: 0.70, c: 0.22, h: 85, name: 'Folder' },       // Vibrant yellow-gold
            image: { l: 0.68, c: 0.26, h: 145, name: 'Image' },        // Vivid green
            video: { l: 0.62, c: 0.28, h: 300, name: 'Video' },        // Electric purple
            audio: { l: 0.65, c: 0.25, h: 330, name: 'Audio' },        // Hot pink
            code: { l: 0.62, c: 0.24, h: 250, name: 'Code' },          // Bright blue
            pdf: { l: 0.58, c: 0.28, h: 25, name: 'PDF' },             // Bold red
            data: { l: 0.65, c: 0.24, h: 160, name: 'Data' },          // Cyan-teal
            config: { l: 0.62, c: 0.22, h: 55, name: 'Config' },       // Orange
            doc: { l: 0.60, c: 0.22, h: 230, name: 'Document' },       // Royal blue
            archive: { l: 0.58, c: 0.20, h: 45, name: 'Archive' },     // Amber
            model3d: { l: 0.65, c: 0.26, h: 320, name: '3D Model' },   // Magenta
            font: { l: 0.60, c: 0.22, h: 280, name: 'Font' },          // Violet
            notebook: { l: 0.65, c: 0.24, h: 35, name: 'Notebook' },   // Orange-red
            executable: { l: 0.55, c: 0.20, h: 0, name: 'Executable' },// Red
            database: { l: 0.58, c: 0.22, h: 200, name: 'Database' },  // Steel blue
            vector: { l: 0.65, c: 0.24, h: 180, name: 'Vector' },      // Turquoise
            binary: { l: 0.50, c: 0.12, h: 260, name: 'Binary' },      // Muted purple
        };

        let depthFactor = 0.85;

        function oklch(l, c, h) {
            return `oklch(${l} ${c} ${h})`;
        }

        function getColorForDepth(baseColor, depth) {
            // Reduce lightness based on depth
            const l = baseColor.l * Math.pow(depthFactor, depth);
            // Slightly reduce chroma too for more natural darkening
            const c = baseColor.c * Math.pow(0.95, depth);
            return oklch(Math.max(0.15, l), Math.max(0.02, c), baseColor.h);
        }

        function getFileTypeCategory(ext, isDir) {
            if (isDir) return 'folder';
            ext = (ext || '').toLowerCase();

            const categories = {
                // Images - raster and vector
                image: ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'ico', 'tiff', 'tif',
                        'raw', 'cr2', 'nef', 'arw', 'dng', 'heic', 'heif', 'avif', 'jxl'],
                vector: ['svg', 'eps', 'ai', 'sketch', 'fig', 'xd'],

                // Video
                video: ['mp4', 'webm', 'mov', 'avi', 'mkv', 'm4v', 'wmv', 'flv', 'ogv',
                        'mpeg', 'mpg', '3gp', 'ts', 'mts', 'm2ts', 'vob'],

                // Audio
                audio: ['mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac', 'wma', 'aiff', 'aif',
                        'opus', 'mid', 'midi', 'ape', 'alac', 'dsd', 'dsf'],

                // Code & scripts
                code: ['py', 'js', 'ts', 'jsx', 'tsx', 'mjs', 'cjs',
                       'html', 'htm', 'css', 'scss', 'sass', 'less', 'styl',
                       'json', 'jsonc', 'json5', 'yaml', 'yml', 'xml', 'xsl', 'xslt',
                       'sql', 'sh', 'bash', 'zsh', 'fish', 'ps1', 'psm1', 'bat', 'cmd',
                       'rs', 'go', 'rb', 'php', 'java', 'kt', 'kts', 'groovy', 'gradle',
                       'c', 'cpp', 'cc', 'cxx', 'h', 'hpp', 'hxx', 'm', 'mm',
                       'swift', 'scala', 'clj', 'cljs', 'cljc', 'edn',
                       'ex', 'exs', 'erl', 'hrl', 'hs', 'lhs', 'ml', 'mli', 'fs', 'fsi', 'fsx',
                       'lua', 'r', 'rmd', 'jl', 'nim', 'zig', 'v', 'vhdl', 'verilog',
                       'pl', 'pm', 'tcl', 'awk', 'sed',
                       'vue', 'svelte', 'astro', 'mdx',
                       'graphql', 'gql', 'prisma', 'proto', 'thrift',
                       'tf', 'tfvars', 'hcl', 'nix', 'dhall',
                       'cmake', 'make', 'makefile', 'dockerfile', 'containerfile',
                       'asm', 's', 'wasm', 'wat'],

                // Markup & docs
                doc: ['md', 'markdown', 'txt', 'text', 'rst', 'asciidoc', 'adoc',
                      'tex', 'latex', 'bib', 'org', 'wiki', 'rtf'],

                // PDF
                pdf: ['pdf'],

                // Data & spreadsheets
                data: ['csv', 'tsv', 'xls', 'xlsx', 'xlsm', 'xlsb', 'ods',
                       'parquet', 'arrow', 'feather', 'avro', 'orc',
                       'ndjson', 'jsonl', 'geojson', 'topojson', 'kml', 'gpx'],

                // Config files
                config: ['toml', 'ini', 'cfg', 'conf', 'config', 'properties',
                         'env', 'envrc', 'editorconfig', 'gitconfig', 'gitignore', 'gitattributes',
                         'npmrc', 'nvmrc', 'yarnrc', 'babelrc', 'eslintrc', 'prettierrc',
                         'dockerignore', 'htaccess', 'nginx', 'apache',
                         'plist', 'reg', 'inf'],

                // Archives
                archive: ['zip', 'tar', 'gz', 'tgz', 'bz2', 'xz', 'lz', 'lzma', 'zst',
                          'rar', '7z', 'cab', 'iso', 'dmg', 'pkg', 'deb', 'rpm', 'apk',
                          'jar', 'war', 'ear'],

                // 3D models
                model3d: ['glb', 'gltf', 'obj', 'fbx', 'stl', 'dae', '3ds', 'blend',
                          'usd', 'usda', 'usdc', 'usdz', 'ply', 'abc', 'step', 'stp', 'iges'],

                // Fonts
                font: ['ttf', 'otf', 'woff', 'woff2', 'eot', 'fnt', 'fon'],

                // Notebooks
                notebook: ['ipynb', 'rmd', 'qmd'],

                // Executables & binaries
                executable: ['exe', 'msi', 'app', 'bin', 'run', 'out', 'elf',
                            'dll', 'so', 'dylib', 'a', 'lib', 'o', 'ko'],

                // Databases
                database: ['db', 'sqlite', 'sqlite3', 'mdb', 'accdb', 'frm', 'ibd',
                          'sql', 'dump', 'bak'],
            };

            for (const [category, exts] of Object.entries(categories)) {
                if (exts.includes(ext)) return category;
            }
            return 'binary';
        }

        function updateCSSColors() {
            const root = document.documentElement;
            for (const [type, color] of Object.entries(FILE_COLORS)) {
                root.style.setProperty(`--color-${type}`, oklch(color.l, color.c, color.h));
            }
            root.style.setProperty('--depth-factor', depthFactor);
        }

        function renderColorSettings() {
            const container = document.getElementById('color-settings');
            container.innerHTML = Object.entries(FILE_COLORS).map(([type, color]) => `
                <div class="color-row">
                    <div class="color-preview" style="background: ${oklch(color.l, color.c, color.h)}"></div>
                    <div class="color-label">${color.name}</div>
                    <div class="oklch-inputs">
                        <input type="number" class="oklch-input" data-type="${type}" data-param="l"
                               value="${color.l}" min="0" max="1" step="0.05" title="Lightness">
                        <input type="number" class="oklch-input" data-type="${type}" data-param="c"
                               value="${color.c}" min="0" max="0.4" step="0.02" title="Chroma">
                        <input type="number" class="oklch-input" data-type="${type}" data-param="h"
                               value="${color.h}" min="0" max="360" step="5" title="Hue">
                    </div>
                </div>
            `).join('');

            // Add event listeners
            container.querySelectorAll('.oklch-input').forEach(input => {
                input.addEventListener('change', (e) => {
                    const type = e.target.dataset.type;
                    const param = e.target.dataset.param;
                    FILE_COLORS[type][param] = parseFloat(e.target.value);
                    updateCSSColors();
                    renderColorSettings();
                    renderGrid();
                });
            });
        }

        // Language mappings for syntax highlighting (synced with Python LANG_MAP)
        const LANG_MAP = {
            'py': 'python', 'js': 'javascript', 'ts': 'typescript',
            'jsx': 'javascript', 'tsx': 'typescript', 'html': 'xml',
            'css': 'css', 'scss': 'scss', 'sass': 'scss', 'less': 'less',
            'json': 'json', 'jsonc': 'json', 'json5': 'json',
            'yaml': 'yaml', 'yml': 'yaml', 'xml': 'xml', 'svg': 'xml',
            'sql': 'sql', 'sh': 'bash', 'bash': 'bash', 'zsh': 'bash',
            'rs': 'rust', 'go': 'go', 'rb': 'ruby', 'php': 'php',
            'java': 'java', 'c': 'c', 'cpp': 'cpp', 'h': 'c', 'hpp': 'cpp',
            'swift': 'swift', 'kt': 'kotlin', 'kts': 'kotlin',
            'toml': 'ini', 'ini': 'ini', 'cfg': 'ini', 'conf': 'ini',
            'md': 'markdown', 'mdx': 'markdown', 'txt': 'plaintext',
            'csv': 'plaintext', 'log': 'plaintext', 'diff': 'diff',
            'env': 'bash', 'dockerfile': 'dockerfile', 'makefile': 'makefile',
            'lua': 'lua', 'r': 'r', 'pl': 'perl', 'pm': 'perl',
            'scala': 'scala', 'groovy': 'groovy', 'gradle': 'groovy',
            'clj': 'clojure', 'cljs': 'clojure', 'ex': 'elixir', 'exs': 'elixir',
            'hs': 'haskell', 'ml': 'ocaml', 'fs': 'fsharp',
            'vim': 'vim', 'el': 'lisp', 'lisp': 'lisp',
            'graphql': 'graphql', 'gql': 'graphql', 'prisma': 'prisma',
            'tf': 'hcl', 'tfvars': 'hcl', 'hcl': 'hcl',
            'proto': 'protobuf', 'cmake': 'cmake',
            'rst': 'plaintext', 'tex': 'latex', 'cls': 'latex', 'sty': 'latex',
            'properties': 'properties', 'gitignore': 'plaintext'
        };

        async function navigate(path, addToHistory = true) {
            if (addToHistory && path !== currentPath) {
                history = history.slice(0, historyIndex + 1);
                history.push(path);
                historyIndex = history.length - 1;
            }

            currentPath = path;
            updateNav();

            const grid = document.getElementById('grid');
            grid.innerHTML = '<div class="tile loading-tile"><div class="tile-preview"></div></div>'.repeat(8);

            try {
                // Fetch current directory
                const res = await fetch(`/api/list?path=${encodeURIComponent(path)}`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                files = await res.json();

                // Sort: folders first, then by name
                files.sort((a, b) => {
                    if (a.is_dir !== b.is_dir) return b.is_dir - a.is_dir;
                    return a.name.localeCompare(b.name);
                });

                // Fetch parent directory for sidebar
                await updateSidebar(path);

                applyFilter();
            } catch (e) {
                console.error('Navigate error:', e);
                grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--text-dim)">
                    Failed to load: ${e.message}<br>
                    <button onclick="navigate('${path}')" style="margin-top:12px;padding:8px 16px;cursor:pointer">Retry</button>
                </div>`;
            }
        }

        async function updateSidebar(path) {
            const sidebarContent = document.getElementById('sidebar-content');
            const sidebarTitle = document.getElementById('sidebar-title');
            const sidebarPath = document.getElementById('sidebar-path');

            // Calculate parent path
            const parts = path.split('/').filter(Boolean);
            const initialParts = INITIAL_PATH.split('/').filter(Boolean);

            // Check if we're at the browse root
            const atRoot = parts.length <= initialParts.length;

            if (atRoot) {
                // At browse root - show current folder contents in sidebar
                parentPath = null;
                const rootName = initialParts[initialParts.length - 1] || 'Root';
                sidebarTitle.textContent = rootName;
                sidebarPath.textContent = INITIAL_PATH;

                // Fetch current folder contents for sidebar
                try {
                    const res = await fetch(`/api/list?path=${encodeURIComponent(INITIAL_PATH)}`);
                    parentFiles = await res.json();
                    if (parentFiles.length === 0) {
                        sidebarContent.innerHTML = '<div class="sidebar-empty">Empty folder</div>';
                        return;
                    }
                    parentFiles.sort((a, b) => {
                        if (a.is_dir !== b.is_dir) return b.is_dir - a.is_dir;
                        return a.name.localeCompare(b.name);
                    });
                    renderSidebar();
                } catch (e) {
                    sidebarContent.innerHTML = '<div class="sidebar-empty">Could not load</div>';
                }
                return;
            }

            // Not at root - show parent folder contents
            parts.pop();
            parentPath = '/' + parts.join('/');

            const parentName = parts.length > 0 ? parts[parts.length - 1] : 'Root';
            sidebarTitle.textContent = parentName;
            sidebarPath.textContent = parentPath || '/';

            try {
                const res = await fetch(`/api/list?path=${encodeURIComponent(parentPath)}`);
                parentFiles = await res.json();
                if (parentFiles.length === 0) {
                    sidebarContent.innerHTML = '<div class="sidebar-empty">Empty folder</div>';
                    return;
                }
                parentFiles.sort((a, b) => {
                    if (a.is_dir !== b.is_dir) return b.is_dir - a.is_dir;
                    return a.name.localeCompare(b.name);
                });
                renderSidebar();
            } catch (e) {
                sidebarContent.innerHTML = '<div class="sidebar-empty">Could not load</div>';
            }
        }

        // Sidebar mode: 'grouped' (default) or 'flat'
        let sidebarMode = localStorage.getItem('sidebarMode') || 'grouped';

        // Drawer states per parent path
        function getDrawerStates(path) {
            try {
                const states = JSON.parse(localStorage.getItem('drawerStates') || '{}');
                return states[path] || {};
            } catch { return {}; }
        }

        function setDrawerState(path, type, isOpen) {
            try {
                const states = JSON.parse(localStorage.getItem('drawerStates') || '{}');
                if (!states[path]) states[path] = {};
                states[path][type] = isOpen;
                localStorage.setItem('drawerStates', JSON.stringify(states));
            } catch {}
        }

        function setSidebarMode(mode) {
            sidebarMode = mode;
            localStorage.setItem('sidebarMode', mode);
            document.getElementById('mode-grouped').classList.toggle('active', mode === 'grouped');
            document.getElementById('mode-flat').classList.toggle('active', mode === 'flat');
            renderSidebar();
        }

        function toggleDrawer(type) {
            const drawer = document.querySelector(`.type-drawer[data-type="${type}"]`);
            if (drawer) {
                const isOpen = drawer.classList.toggle('open');
                setDrawerState(parentPath, type, isOpen);
            }
        }

        // Type grouping configuration
        const TYPE_GROUPS = {
            folder: { label: 'Folders', iconName: 'folder', order: 0 },
            image: { label: 'Images', iconName: 'image', order: 1 },
            video: { label: 'Videos', iconName: 'video', order: 2 },
            audio: { label: 'Audio', iconName: 'audio', order: 3 },
            code: { label: 'Code', iconName: 'code', order: 4 },
            document: { label: 'Documents', iconName: 'file', order: 5 },
            pdf: { label: 'PDFs', iconName: 'pdf', order: 6 },
            data: { label: 'Data', iconName: 'data', order: 7 },
            archive: { label: 'Archives', iconName: 'archive', order: 8 },
            model3d: { label: '3D Models', iconName: 'model3d', order: 9 },
            other: { label: 'Other', iconName: 'file', order: 10 }
        };

        function getFileTypeGroup(f) {
            if (f.is_dir) return 'folder';
            const ext = (f.ext || '').toLowerCase();
            const type = f.preview_type;

            // Map to groups
            const extMap = {
                jpg: 'image', jpeg: 'image', png: 'image', gif: 'image', webp: 'image', svg: 'image', bmp: 'image', heic: 'image', avif: 'image', ico: 'image',
                mp4: 'video', webm: 'video', mov: 'video', avi: 'video', mkv: 'video', m4v: 'video',
                mp3: 'audio', wav: 'audio', flac: 'audio', ogg: 'audio', m4a: 'audio', aac: 'audio',
                pdf: 'pdf',
                doc: 'document', docx: 'document', txt: 'document', rtf: 'document', odt: 'document', md: 'document',
                xls: 'data', xlsx: 'data', csv: 'data', json: 'data', yaml: 'data', yml: 'data', xml: 'data', sqlite: 'data', db: 'data',
                zip: 'archive', tar: 'archive', gz: 'archive', rar: 'archive', '7z': 'archive', bz2: 'archive',
                glb: 'model3d', gltf: 'model3d', obj: 'model3d', stl: 'model3d', fbx: 'model3d', usdz: 'model3d',
                js: 'code', ts: 'code', py: 'code', java: 'code', c: 'code', cpp: 'code', h: 'code', go: 'code', rs: 'code', rb: 'code',
                php: 'code', html: 'code', css: 'code', scss: 'code', less: 'code', sh: 'code', bash: 'code', sql: 'code',
                swift: 'code', kt: 'code', scala: 'code', r: 'code', lua: 'code', perl: 'code', pl: 'code'
            };

            if (extMap[ext]) return extMap[ext];
            if (type === 'code') return 'code';
            if (type === 'image') return 'image';
            if (type === 'video') return 'video';
            if (type === 'audio') return 'audio';
            return 'other';
        }

        function renderSidebar() {
            const sidebarContent = document.getElementById('sidebar-content');
            const currentFolderName = currentPath.split('/').filter(Boolean).pop() || '';

            if (parentFiles.length === 0) {
                sidebarContent.innerHTML = '<div class="sidebar-empty">Empty folder</div>';
                return;
            }

            if (sidebarMode === 'flat') {
                // Flat list mode
                const items = parentFiles.map((f, idx) => {
                    const isActive = f.name === currentFolderName && f.is_dir;
                    const isSelected = selectedFiles.has(f.path);
                    const fileIcon = getFileIcon(f);

                    return `
                        <div class="sidebar-item ${isActive ? 'active' : ''} ${isSelected ? 'selected' : ''}"
                             data-path="${f.path}"
                             data-idx="${idx}"
                             onclick="handleSidebarClick(event, ${idx})">
                            <div class="item-icon">${fileIcon}</div>
                            <div class="item-info">
                                <div class="item-name">${f.name}</div>
                                <div class="item-meta">${f.is_dir ? f.item_count + ' items' : f.size_fmt}</div>
                            </div>
                        </div>
                    `;
                }).join('');
                sidebarContent.innerHTML = items;
                return;
            }

            // Grouped mode - group files by type
            const groups = {};
            parentFiles.forEach((f, idx) => {
                const type = getFileTypeGroup(f);
                if (!groups[type]) groups[type] = [];
                groups[type].push({ file: f, idx });
            });

            // Get saved drawer states for this parent
            const drawerStates = getDrawerStates(parentPath);

            // Sort groups by order
            const sortedTypes = Object.keys(groups).sort((a, b) =>
                (TYPE_GROUPS[a]?.order || 99) - (TYPE_GROUPS[b]?.order || 99)
            );

            const html = sortedTypes.map(type => {
                const group = TYPE_GROUPS[type] || TYPE_GROUPS.other;
                const files = groups[type];
                // Default: folders open, others closed (unless saved state exists)
                const isOpen = drawerStates[type] !== undefined ? drawerStates[type] : (type === 'folder');

                const items = files.map(({ file: f, idx }) => {
                    const isActive = f.name === currentFolderName && f.is_dir;
                    const isSelected = selectedFiles.has(f.path);
                    const fileIcon = getFileIcon(f);

                    return `
                        <div class="sidebar-item ${isActive ? 'active' : ''} ${isSelected ? 'selected' : ''}"
                             data-path="${f.path}"
                             data-idx="${idx}"
                             onclick="handleSidebarClick(event, ${idx})">
                            <div class="item-icon">${fileIcon}</div>
                            <div class="item-info">
                                <div class="item-name">${f.name}</div>
                                <div class="item-meta">${f.is_dir ? f.item_count + ' items' : f.size_fmt}</div>
                            </div>
                        </div>
                    `;
                }).join('');

                return `
                    <div class="type-drawer ${isOpen ? 'open' : ''}" data-type="${type}">
                        <div class="type-drawer-header" onclick="toggleDrawer('${type}')">
                            <div class="type-drawer-icon">${icon(group.iconName)}</div>
                            <div class="type-drawer-label">${group.label}</div>
                            <div class="type-drawer-count">${files.length}</div>
                            <div class="type-drawer-chevron">›</div>
                        </div>
                        <div class="type-drawer-content">
                            ${items}
                        </div>
                    </div>
                `;
            }).join('');

            sidebarContent.innerHTML = html;
        }

        function getFileIcon(f) {
            if (f.is_dir) return icon('folder');
            if (f.preview_type === 'image') {
                return `<img src="/file${f.path}" loading="lazy">`;
            }
            const iconMap = {
                'video': 'video', 'audio': 'audio', 'pdf': 'pdf', 'code': 'code'
            };
            return icon(iconMap[f.preview_type] || 'file');
        }

        function handleSidebarClick(event, idx) {
            const f = parentFiles[idx];
            if (!f) return;

            // Get click zone (35% left = select, 65% right = open)
            const item = event.currentTarget;
            const rect = item.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const selectZone = rect.width * 0.35;

            if (selectionMode || clickX < selectZone) {
                // Toggle selection
                if (selectedFiles.has(f.path)) {
                    selectedFiles.delete(f.path);
                } else {
                    selectedFiles.add(f.path);
                }
                renderSidebar();
                renderGrid();
            } else {
                // Navigate or open
                if (f.is_dir) {
                    navigate(f.path);
                } else {
                    // Open file in lightbox (need to switch context)
                    navigateToParent();
                    setTimeout(() => {
                        const newIdx = filteredFiles.findIndex(file => file.path === f.path);
                        if (newIdx >= 0) openLightbox(newIdx);
                    }, 100);
                }
            }
        }

        function navigateToParent() {
            if (parentPath !== null) {
                navigate(parentPath);
            }
        }

        let MAX_VISIBLE_ITEMS = 200;  // Limit for performance

        function applyFilter() {
            const query = document.getElementById('search').value.toLowerCase();
            let result = files;

            // Apply search filter
            if (query) {
                result = result.filter(f => f.name.toLowerCase().includes(query));
            }

            // Apply type filters
            const allTypesCount = 17; // Total filter categories
            if (activeFilters.size < allTypesCount) {
                result = result.filter(f => {
                    if (f.is_dir) {
                        return activeFilters.has('folder');
                    }
                    const category = getFileTypeCategory(f.name);
                    return activeFilters.has(category);
                });
            }

            // Apply sorting
            result = sortFiles(result);

            // Limit items for performance
            if (result.length > MAX_VISIBLE_ITEMS) {
                console.log(`Limiting display from ${result.length} to ${MAX_VISIBLE_ITEMS} items`);
                filteredFiles = result.slice(0, MAX_VISIBLE_ITEMS);
            } else {
                filteredFiles = result;
            }
            renderGrid();
        }

        function updateNav() {
            document.getElementById('btn-back').disabled = historyIndex <= 0;

            // Disable up button when at browse root
            const currentParts = currentPath.split('/').filter(Boolean);
            const initialParts = INITIAL_PATH.split('/').filter(Boolean);
            const atRoot = currentParts.length <= initialParts.length;
            document.getElementById('btn-up').disabled = atRoot;

            const pathDisplay = document.getElementById('path-display');
            if (!currentPath || currentPath === INITIAL_PATH) {
                const rootName = initialParts[initialParts.length - 1] || 'Root';
                pathDisplay.innerHTML = `<span onclick="navigate('${INITIAL_PATH}')">${icon('folder')} ${rootName}</span>`;
            } else {
                const parts = currentPath.split('/').filter(Boolean);
                let html = `<span onclick="navigate('${INITIAL_PATH}')">${icon('folder')}</span>`;
                let accPath = '';
                // Only show path segments from INITIAL_PATH onwards
                parts.forEach((part, i) => {
                    accPath += '/' + part;
                    if (accPath.length > INITIAL_PATH.length) {
                        html += ` / <span onclick="navigate('${accPath}')">${part}</span>`;
                    }
                });
                pathDisplay.innerHTML = html;
            }
        }

        function goBack() {
            if (historyIndex > 0) {
                historyIndex--;
                navigate(history[historyIndex], false);
            }
        }

        function goUp() {
            const currentParts = currentPath.split('/').filter(Boolean);
            const initialParts = INITIAL_PATH.split('/').filter(Boolean);

            // Don't go above browse root
            if (currentParts.length <= initialParts.length) {
                return;
            }

            currentParts.pop();
            const newPath = '/' + currentParts.join('/');

            // Ensure we don't go above INITIAL_PATH
            if (newPath.length >= INITIAL_PATH.length) {
                navigate(newPath);
            } else {
                navigate(INITIAL_PATH);
            }
        }

        async function renderGrid() {
            const grid = document.getElementById('grid');

            // Cleanup all Three.js resources before re-render to prevent memory leaks
            cleanupThreeResources();

            if (filteredFiles.length === 0) {
                grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--text-dim)">No files found</div>';
                grid.className = 'grid';
                return;
            }

            // Use different rendering based on view mode
            if (currentViewMode === 'list') {
                renderListView(filteredFiles, grid);
                updateSelectionUI();
                return;
            } else if (currentViewMode === 'column') {
                renderColumnView(filteredFiles, grid);
                updateSelectionUI();
                return;
            }

            // Default grid view
            grid.className = 'grid';

            // Generate tiles with previews
            const tiles = await Promise.all(filteredFiles.map(async (f, idx) => {
                const previewHtml = await getPreviewHtml(f, 0);  // depth 0 for root
                const typeCategory = getFileTypeCategory(f.ext, f.is_dir);
                const color = FILE_COLORS[typeCategory];
                const tileColor = getColorForDepth(color, 0);

                const isSelected = selectedFiles.has(f.path);
                const isCut = clipboard.operation === 'cut' && clipboard.files.includes(f.path);
                return `
                    <div class="tile ${f.is_dir ? 'folder' : ''} ${isSelected ? 'selected' : ''} ${isCut ? 'is-cut' : ''}"
                         data-type="${typeCategory}"
                         data-path="${f.path}"
                         style="--tile-color: ${tileColor}; --depth: 0"
                         onclick="handleClick(${idx}, event)"
                         ondblclick="handleDblClick(${idx})">
                        <span class="zone-hint left">✓</span>
                        <span class="zone-hint right">${f.is_dir ? icon('folderOpen') : icon('eye')}</span>
                        <div class="tile-preview">
                            ${previewHtml}
                            ${!f.is_dir && f.ext ? `<span class="file-ext">${f.ext}</span>` : ''}
                        </div>
                        <div class="tile-info">
                            <div class="tile-name" title="${f.name}">${f.name}</div>
                            <div class="tile-meta">
                                <span>${f.is_dir ? f.item_count + ' items' : f.size_fmt}</span>
                                <span>${f.modified}</span>
                            </div>
                        </div>
                    </div>`;
            }));

            grid.innerHTML = tiles.join('');

            // Update selection bar
            const selBar = document.getElementById('selection-bar');
            const selCount = document.getElementById('sel-count');
            const pasteBtn = document.getElementById('paste-btn');

            if (selectedFiles.size > 0) {
                selBar.classList.add('active');
                selCount.textContent = selectedFiles.size;
            } else {
                selBar.classList.remove('active');
            }

            // Show paste button if clipboard has items
            if (clipboard.files.length > 0) {
                pasteBtn.style.display = 'flex';
                pasteBtn.textContent = `${icon('extract')} Paste (${clipboard.files.length})`;
            } else {
                pasteBtn.style.display = 'none';
            }
        }

        function updateSelectionUI() {
            // Update selection bar
            const selBar = document.getElementById('selection-bar');
            const selCount = document.getElementById('sel-count');
            const pasteBtn = document.getElementById('paste-btn');

            if (selectedFiles.size > 0) {
                selBar.classList.add('active');
                selCount.textContent = selectedFiles.size;
            } else {
                selBar.classList.remove('active');
            }

            // Show paste button if clipboard has items
            if (clipboard.files.length > 0) {
                pasteBtn.style.display = 'flex';
                pasteBtn.textContent = `${icon('extract')} Paste (${clipboard.files.length})`;
            } else {
                pasteBtn.style.display = 'none';
            }
        }

        // Calculate grid dimensions based on container
        function getGridDimensions() {
            const tileSize = parseInt(document.getElementById('tile-size').value);
            const containerWidth = document.querySelector('.grid-container').clientWidth - 24;
            const cols = Math.floor(containerWidth / (tileSize + 12));
            return { cols: Math.max(2, cols), rows: 2 };
        }

        async function getPreviewHtml(file, depth = 0) {
            if (file.is_dir) {
                const { cols, rows } = getGridDimensions();
                const totalSlots = cols * rows;
                const folderColor = getColorForDepth(FILE_COLORS.folder, depth);

                try {
                    // Use throttled fetch to limit concurrent requests
                    const items = await throttledFetch(`/api/folder-preview?path=${encodeURIComponent(file.path)}&limit=${totalSlots}&depth=2`);

                    if (items.length === 0) {
                        return `<div class="folder-grid" style="--folder-cols:1;--folder-rows:1;--depth:${depth}">
                            <div class="mini-item"><span class="mini-icon">${icon('folder')}</span></div>
                        </div>
                        <div class="folder-label">
                            <div class="folder-name" style="color:${folderColor}">${icon('folder')} ${file.name}</div>
                            <div class="folder-count">Empty</div>
                        </div>`;
                    }

                    const miniItems = items.slice(0, totalSlots).map(item => {
                        const itemType = getFileTypeCategory(item.ext, item.is_dir);
                        const itemColor = getColorForDepth(FILE_COLORS[itemType], depth + 1);
                        const bgDarkness = Math.min(90, (depth + 1) * 15);
                        const ext = (item.ext || '').toLowerCase();

                        if (item.preview_type === 'image') {
                            return `<div class="mini-item" style="--depth:${depth+1}"><img src="/file${item.path}" loading="lazy"></div>`;
                        } else if (['glb', 'gltf'].includes(ext)) {
                            // 3D model preview in folder
                            return `<div class="mini-item" style="--depth:${depth+1}">
                                <model-viewer src="/file${item.path}" auto-rotate
                                    style="width:100%;height:100%;pointer-events:none">
                                </model-viewer>
                            </div>`;
                        } else if (ext === 'stl') {
                            const canvasId = 'stl-mini-' + Math.random().toString(36).substr(2, 9);
                            setTimeout(() => initSTLPreview(canvasId, item.path), 150);
                            return `<div class="mini-item" style="--depth:${depth+1}">
                                <canvas id="${canvasId}" class="stl-canvas" style="width:100%;height:100%"></canvas>
                            </div>`;
                        } else if (item.is_dir && item.children && item.children.length > 0) {
                            // Nested folder with its own preview - one level deeper
                            const nestedDepth = depth + 2;
                            const folderFrameColor = getColorForDepth(FILE_COLORS.folder, depth + 1);
                            const nestedCells = item.children.slice(0, 4).map(child => {
                                const childType = getFileTypeCategory(child.ext, child.is_dir);
                                const childColor = getColorForDepth(FILE_COLORS[childType], nestedDepth);

                                if (child.preview_type === 'image') {
                                    return `<div class="nested-cell" style="--depth:${nestedDepth}"><img src="/file${child.path}" loading="lazy"></div>`;
                                } else if (child.is_dir) {
                                    // Folder inside folder - show with frame
                                    return `<div class="nested-cell is-nested-folder" style="--depth:${nestedDepth};border-color:${childColor}"><span class="tiny-icon" style="color:${childColor}">${icon('folder')}</span></div>`;
                                } else {
                                    const iconMap = {'code': 'code', 'video': 'video', 'audio': 'audio', 'pdf': 'pdf', 'image': 'image'};
                                    return `<div class="nested-cell" style="--depth:${nestedDepth}"><span class="tiny-icon" style="color:${childColor}">${icon(iconMap[child.preview_type] || 'file')}</span></div>`;
                                }
                            });
                            while (nestedCells.length < 4) nestedCells.push(`<div class="nested-cell" style="--depth:${nestedDepth}"></div>`);
                            return `<div class="mini-item is-folder" style="--depth:${depth+1};--folder-frame-color:${folderFrameColor}"><div class="nested-grid">${nestedCells.join('')}</div></div>`;
                        } else if (item.is_dir) {
                            return `<div class="mini-item is-folder" style="--depth:${depth+1}"><span class="mini-icon" style="color:${itemColor}">${icon('folder')}</span></div>`;
                        } else if (item.preview_type === 'code' && item.preview_content) {
                            return `<div class="mini-item" style="--depth:${depth+1}"><div class="mini-code">${escapeHtml(item.preview_content.slice(0, 150))}</div></div>`;
                        } else {
                            const iconMap = {'video': 'video', 'audio': 'audio', 'pdf': 'pdf'};
                            return `<div class="mini-item" style="--depth:${depth+1}"><span class="mini-icon" style="color:${itemColor}">${icon(iconMap[item.preview_type] || 'file')}</span></div>`;
                        }
                    });

                    // Pad remaining slots
                    while (miniItems.length < totalSlots) {
                        miniItems.push(`<div class="mini-item" style="--depth:${depth+1}"></div>`);
                    }

                    return `<div class="folder-grid" style="--folder-cols:${cols};--folder-rows:${rows};--depth:${depth}">${miniItems.join('')}</div>
                        <div class="folder-label">
                            <div class="folder-name" style="color:${folderColor}">${icon('folder')} ${file.name}</div>
                            <div class="folder-count">${file.item_count} items</div>
                        </div>`;
                } catch (e) {
                    return `<div class="folder-grid" style="--folder-cols:1;--folder-rows:1;--depth:${depth}">
                        <div class="mini-item"><span class="mini-icon">${icon('folder')}</span></div>
                    </div>
                    <div class="folder-label">
                        <div class="folder-name" style="color:${folderColor}">${icon('folder')} ${file.name}</div>
                        <div class="folder-count">${file.item_count} items</div>
                    </div>`;
                }
            }

            const type = file.preview_type;
            const ext = (file.ext || '').toLowerCase();

            if (type === 'image') {
                return `<img src="/file${file.path}" loading="lazy">`;
            }

            if (type === 'video') {
                return `<video src="/file${file.path}" muted loop onmouseenter="this.play()" onmouseleave="this.pause();this.currentTime=0"></video>`;
            }

            if (type === 'audio') {
                return `<div class="audio-preview"><span class="audio-icon">${icon('audio', 'lg')}</span><div class="audio-wave"></div></div>`;
            }

            if (type === 'pdf') {
                const canvasId = 'pdf-' + Math.random().toString(36).substr(2, 9);
                setTimeout(() => initPDFPreview(canvasId, file.path), 100);
                return `<div class="pdf-preview pdf-canvas-preview">
                    <canvas id="${canvasId}" class="pdf-canvas"></canvas>
                    <span class="pdf-page-label">PDF</span>
                </div>`;
            }

            // Try to get text preview for code/text files
            const textExts = ['py', 'js', 'ts', 'jsx', 'tsx', 'html', 'css', 'scss', 'sass', 'less',
                              'json', 'yaml', 'yml', 'toml', 'xml', 'sql', 'sh', 'bash', 'zsh',
                              'rs', 'go', 'rb', 'php', 'java', 'c', 'cpp', 'h', 'hpp', 'swift', 'kt',
                              'md', 'txt', 'csv', 'log', 'env', 'gitignore', 'dockerfile', 'makefile',
                              'r', 'lua', 'pl', 'pm', 'tcl', 'vim', 'el', 'clj', 'ex', 'exs',
                              'hs', 'ml', 'fs', 'scala', 'groovy', 'gradle', 'cmake', 'ini', 'cfg',
                              'conf', 'properties', 'plist', 'rst', 'tex', 'sty', 'cls', 'bib',
                              'graphql', 'gql', 'prisma', 'tf', 'tfvars', 'hcl', 'proto'];

            const isTextFile = textExts.includes(ext) || type === 'code';

            if (isTextFile) {
                try {
                    const res = await fetch(`/api/preview?path=${encodeURIComponent(file.path)}`);
                    const data = await res.json();
                    if (data.content && data.content.trim()) {
                        const lang = LANG_MAP[ext] || 'plaintext';
                        if (ext === 'md') {
                            return `<div class="md-preview">${marked.parse(data.content.slice(0, 600))}</div>`;
                        }
                        if (ext === 'csv') {
                            // Simple CSV preview as table
                            const lines = data.content.split('\\n').slice(0, 8);
                            const cells = lines.map(l => l.split(',').slice(0, 5));
                            return `<div class="csv-preview"><table>${cells.map(row =>
                                '<tr>' + row.map(c => `<td>${escapeHtml(c.slice(0,15))}</td>`).join('') + '</tr>'
                            ).join('')}</table></div>`;
                        }
                        if (ext === 'json') {
                            try {
                                const parsed = JSON.parse(data.content.slice(0, 2000));
                                const formatted = JSON.stringify(parsed, null, 2).slice(0, 800);
                                const highlighted = hljs.highlight(formatted, {language: 'json', ignoreIllegals: true}).value;
                                return `<div class="code-preview"><pre><code>${highlighted}</code></pre></div>`;
                            } catch {}
                        }
                        const highlighted = hljs.highlight(data.content.slice(0, 800), {language: lang, ignoreIllegals: true}).value;
                        return `<div class="code-preview"><pre><code>${highlighted}</code></pre></div>`;
                    }
                } catch (e) {
                    console.log('Preview failed for', file.path, e);
                }
            }

            // Data files
            if (['xls', 'xlsx'].includes(ext)) {
                return `<div class="data-preview"><span class="data-icon">${icon('data', 'lg')}</span><span class="data-label">Excel</span></div>`;
            }
            if (['doc', 'docx'].includes(ext)) {
                return `<div class="doc-preview"><span class="doc-icon">${icon('file', 'lg')}</span><span class="doc-label">Word</span></div>`;
            }

            // Archive files
            if (['zip', 'tar', 'gz', 'rar', '7z', 'bz2', 'xz'].includes(ext)) {
                return `<div class="archive-preview"><span class="archive-icon">${icon('archive', 'lg')}</span><span class="archive-label">${ext.toUpperCase()}</span></div>`;
            }

            // 3D files - use model-viewer for GLB/GLTF, Three.js for STL
            if (['glb', 'gltf'].includes(ext)) {
                const modelId = 'model-' + Math.random().toString(36).substr(2, 9);
                return `<div class="model-3d-preview">
                    <model-viewer src="/file${file.path}"
                                  auto-rotate camera-controls
                                  shadow-intensity="1"
                                  environment-image="neutral"
                                  style="width:100%;height:100%">
                    </model-viewer>
                    <span class="model-3d-label">${ext.toUpperCase()}</span>
                </div>`;
            }
            if (ext === 'stl') {
                const canvasId = 'stl-' + Math.random().toString(36).substr(2, 9);
                setTimeout(() => initSTLPreview(canvasId, file.path), 100);
                return `<div class="model-3d-preview">
                    <canvas id="${canvasId}" class="stl-canvas"></canvas>
                    <span class="model-3d-label">STL</span>
                </div>`;
            }
            if (['obj', 'fbx', 'dae', '3ds'].includes(ext)) {
                return `<div class="model-preview"><span class="model-icon">${icon('model3d', 'lg')}</span><span class="model-label">${ext.toUpperCase()}</span></div>`;
            }

            // Font files
            if (['ttf', 'otf', 'woff', 'woff2', 'eot'].includes(ext)) {
                return `<div class="font-preview"><span class="font-icon">${icon('file', 'lg')}</span><span class="font-label">Font</span></div>`;
            }

            // Jupyter notebooks
            if (ext === 'ipynb') {
                return `<div class="notebook-preview"><span class="notebook-icon">${icon('code', 'lg')}</span><span class="notebook-label">Notebook</span></div>`;
            }

            // Binary/unknown - try to read first bytes to check if it's actually text
            try {
                const res = await fetch(`/api/preview?path=${encodeURIComponent(file.path)}`);
                const data = await res.json();
                if (data.content && data.content.trim() && !data.content.includes('\\u0000')) {
                    // It's readable text
                    const highlighted = hljs.highlightAuto(data.content.slice(0, 600)).value;
                    return `<div class="code-preview"><pre><code>${highlighted}</code></pre></div>`;
                }
            } catch {}

            return `<div class="binary-preview"><span class="binary-icon">${icon('file', 'lg')}</span><span class="binary-label">${ext || 'file'}</span></div>`;
        }

        let selectionMode = false;

        function handleClick(idx, event) {
            const file = filteredFiles[idx];

            // If selection mode is on, always select
            if (selectionMode) {
                toggleSelect(file.path);
                return;
            }

            // Get click position relative to the tile
            const tile = event.currentTarget;
            const rect = tile.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const selectZone = rect.width * 0.35; // 35% left = select

            // Left 35% = select, Right 65% = preview/navigate
            if (clickX < selectZone) {
                toggleSelect(file.path);
            } else {
                if (file.is_dir) {
                    navigate(file.path);
                } else {
                    openLightbox(idx);
                }
            }
        }

        function toggleSelect(path) {
            if (selectedFiles.has(path)) {
                selectedFiles.delete(path);
            } else {
                selectedFiles.add(path);
            }
            renderGrid();
        }

        let selectedFiles = new Set();
        let clipboard = { files: [], operation: null }; // 'copy' or 'cut'

        function copySelected() {
            if (selectedFiles.size === 0) return;
            clipboard = { files: [...selectedFiles], operation: 'copy' };
            showToast(`Copied ${clipboard.files.length} item(s)`);
        }

        function cutSelected() {
            if (selectedFiles.size === 0) return;
            clipboard = { files: [...selectedFiles], operation: 'cut' };
            showToast(`Cut ${clipboard.files.length} item(s)`);
            renderGrid(); // Show cut items as faded
        }

        async function pasteToCurrentFolder() {
            if (clipboard.files.length === 0) return;

            const targetPath = currentPath || '/';
            const result = await fetch('/api/paste', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    files: clipboard.files,
                    target: targetPath,
                    operation: clipboard.operation
                })
            });
            const data = await result.json();

            if (data.success) {
                showToast(`${clipboard.operation === 'cut' ? 'Moved' : 'Copied'} ${data.count} item(s)`);
                if (clipboard.operation === 'cut') {
                    clipboard = { files: [], operation: null };
                }
                selectedFiles.clear();
                navigate(currentPath, false);
                checkHistoryStatus();
            } else {
                showToast(`Error: ${data.error}`, true);
            }
        }

        async function deleteSelected() {
            if (selectedFiles.size === 0) return;

            const confirmed = confirm(`Move ${selectedFiles.size} item(s) to trash?`);
            if (!confirmed) return;

            const result = await fetch('/api/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files: [...selectedFiles] })
            });
            const data = await result.json();

            if (data.success) {
                showToast(`Moved ${data.count} item(s) to trash (Cmd+Z to undo)`);
                selectedFiles.clear();
                navigate(currentPath, false);
                checkHistoryStatus();
            } else {
                showToast(`Error: ${data.error}`, true);
            }
        }

        function showToast(message, isError = false) {
            const existing = document.querySelector('.toast');
            if (existing) existing.remove();

            const toast = document.createElement('div');
            toast.className = 'toast' + (isError ? ' error' : '');
            toast.textContent = message;
            document.body.appendChild(toast);

            setTimeout(() => toast.classList.add('show'), 10);
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 2500);
        }

        // Undo/Redo functions
        async function performUndo() {
            try {
                const res = await fetch('/api/undo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: '{}'
                });
                const data = await res.json();
                if (data.success) {
                    showToast(data.message);
                    navigate(currentPath, false);
                    updateHistoryButtons(data.canUndo, data.canRedo);
                } else {
                    showToast(data.error, true);
                }
            } catch (e) {
                showToast('Undo failed', true);
            }
        }

        async function performRedo() {
            try {
                const res = await fetch('/api/redo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: '{}'
                });
                const data = await res.json();
                if (data.success) {
                    showToast(data.message);
                    navigate(currentPath, false);
                    updateHistoryButtons(data.canUndo, data.canRedo);
                } else {
                    showToast(data.error, true);
                }
            } catch (e) {
                showToast('Redo failed', true);
            }
        }

        function updateHistoryButtons(canUndo, canRedo) {
            const undoBtn = document.getElementById('undo-btn');
            const redoBtn = document.getElementById('redo-btn');
            if (undoBtn) undoBtn.disabled = !canUndo;
            if (redoBtn) redoBtn.disabled = !canRedo;
        }

        // Check history status on load and after operations
        async function checkHistoryStatus() {
            try {
                const res = await fetch('/api/history-status', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: '{}'
                });
                const data = await res.json();
                updateHistoryButtons(data.canUndo, data.canRedo);
            } catch (e) {}
        }

        function handleDblClick(idx) {
            const file = filteredFiles[idx];
            if (!file.is_dir) {
                openInApp();
            }
        }

        async function openLightbox(idx) {
            currentLightboxIndex = idx;
            const file = filteredFiles[idx];

            document.getElementById('lightbox-title').textContent = file.name;
            document.getElementById('lightbox').classList.add('active');

            // Update sidebar with file info
            updateLightboxSidebar(file);

            // Reset content transform
            const content = document.getElementById('lightbox-content');
            content.style.transform = 'none';
            const type = file.preview_type;
            const ext = (file.ext || '').toLowerCase();

            if (type === 'image') {
                content.innerHTML = `<img src="/file${file.path}">`;
            }
            else if (type === 'video') {
                content.innerHTML = `<video src="/file${file.path}" controls autoplay></video>`;
            }
            else if (type === 'audio') {
                content.innerHTML = `<audio src="/file${file.path}" controls autoplay></audio>`;
            }
            else if (type === 'pdf') {
                content.innerHTML = `<iframe src="/file${file.path}"></iframe>`;
            }
            else if (['glb', 'gltf'].includes(ext)) {
                content.innerHTML = `
                    <model-viewer src="/file${file.path}"
                                  auto-rotate camera-controls
                                  shadow-intensity="1"
                                  environment-image="neutral"
                                  style="width:80vw;height:70vh;max-width:1000px">
                    </model-viewer>`;
            }
            else if (ext === 'stl') {
                const canvasId = 'stl-lightbox-' + Math.random().toString(36).substr(2, 9);
                content.innerHTML = `<canvas id="${canvasId}" style="width:80vw;height:70vh;max-width:1000px;border-radius:12px"></canvas>`;
                setTimeout(() => initSTLLightbox(canvasId, file.path), 100);
            }
            else if (type === 'code') {
                content.innerHTML = '<div style="color:var(--text-dim)">Loading...</div>';
                try {
                    const res = await fetch(`/api/content?path=${encodeURIComponent(file.path)}`);
                    const data = await res.json();
                    if (file.ext === 'md') {
                        content.innerHTML = `<div class="md-full">${marked.parse(data.content)}</div>`;
                    } else {
                        const lang = LANG_MAP[file.ext] || 'plaintext';
                        const highlighted = hljs.highlight(data.content, {language: lang, ignoreIllegals: true}).value;
                        content.innerHTML = `<div class="code-full"><pre><code>${highlighted}</code></pre></div>`;
                    }
                } catch (e) {
                    content.innerHTML = '<div style="color:var(--text-dim)">Could not load file</div>';
                }
            }
            else {
                content.innerHTML = `<div style="text-align:center">
                    <div style="font-size:5rem;margin-bottom:20px">${icon('file', 'xl')}</div>
                    <div style="color:var(--text-dim)">${file.name}</div>
                    <div style="color:var(--text-dim);margin-top:8px">${file.size_fmt}</div>
                </div>`;
            }
        }

        function closeLightbox() {
            document.getElementById('lightbox').classList.remove('active');
            currentLightboxIndex = -1;
        }

        function navLightbox(delta) {
            // Only navigate between files (not folders)
            const fileIndices = filteredFiles.map((f, i) => f.is_dir ? -1 : i).filter(i => i >= 0);
            const currentPos = fileIndices.indexOf(currentLightboxIndex);
            if (currentPos === -1) return;

            const newPos = (currentPos + delta + fileIndices.length) % fileIndices.length;
            openLightbox(fileIndices[newPos]);
        }

        async function openInApp() {
            const file = filteredFiles[currentLightboxIndex];
            if (file) {
                await fetch(`/api/open?path=${encodeURIComponent(file.path)}`);
            }
        }

        // Zoom state and controls
        let currentZoom = 100;
        const ZOOM_MIN = 25;
        const ZOOM_MAX = 400;
        const ZOOM_STEP = 25;

        function zoomIn() {
            currentZoom = Math.min(ZOOM_MAX, currentZoom + ZOOM_STEP);
            applyZoom();
        }

        function zoomOut() {
            currentZoom = Math.max(ZOOM_MIN, currentZoom - ZOOM_STEP);
            applyZoom();
        }

        function zoomReset() {
            currentZoom = 100;
            applyZoom();
        }

        function applyZoom() {
            document.getElementById('zoom-level').textContent = currentZoom + '%';
            const content = document.getElementById('lightbox-content');
            const transform = currentZoom === 100 ? 'none' : `scale(${currentZoom / 100})`;
            content.style.transform = transform;
            content.style.transformOrigin = 'center center';
        }

        // Lightbox sidebar helpers
        function downloadFile() {
            const file = filteredFiles[currentLightboxIndex];
            if (file) {
                const a = document.createElement('a');
                a.href = '/file' + file.path;
                a.download = file.name;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                showToast('Downloading: ' + file.name);
            }
        }

        function copyFilePath() {
            const file = filteredFiles[currentLightboxIndex];
            if (file) {
                navigator.clipboard.writeText(file.path).then(() => {
                    showToast('Path copied to clipboard');
                }).catch(() => {
                    showToast('Failed to copy path');
                });
            }
        }

        function showFileInfo() {
            const file = filteredFiles[currentLightboxIndex];
            if (file) {
                const info = [
                    `Name: ${file.name}`,
                    `Path: ${file.path}`,
                    `Size: ${file.size_fmt}`,
                    `Modified: ${file.modified || 'Unknown'}`,
                    `Type: ${file.preview_type || 'Unknown'}`
                ].join('\\n');
                alert(info);
            }
        }

        // Format to color mapping (OKLCH-based)
        const FORMAT_COLORS = {
            image: { hue: 30, iconName: 'image', name: 'Image' },
            video: { hue: 280, iconName: 'video', name: 'Video' },
            audio: { hue: 180, iconName: 'audio', name: 'Audio' },
            document: { hue: 220, iconName: 'file', name: 'Document' },
            code: { hue: 140, iconName: 'code', name: 'Code' },
            model3d: { hue: 320, iconName: 'model3d', name: '3D Model' },
            archive: { hue: 60, iconName: 'archive', name: 'Archive' },
            data: { hue: 200, iconName: 'data', name: 'Data' },
            font: { hue: 100, iconName: 'file', name: 'Font' },
            pdf: { hue: 0, iconName: 'pdf', name: 'PDF' },
            unknown: { hue: 0, iconName: 'file', name: 'File' }
        };

        function getFormatInfo(file) {
            const ext = (file.ext || '').toLowerCase();
            const type = file.preview_type || 'unknown';

            // Map extensions to categories
            const extMap = {
                // Images
                jpg: 'image', jpeg: 'image', png: 'image', gif: 'image', webp: 'image',
                svg: 'image', bmp: 'image', ico: 'image', heic: 'image', avif: 'image',
                // Video
                mp4: 'video', webm: 'video', mov: 'video', avi: 'video', mkv: 'video',
                // Audio
                mp3: 'audio', wav: 'audio', flac: 'audio', ogg: 'audio', m4a: 'audio', aac: 'audio',
                // Documents
                doc: 'document', docx: 'document', txt: 'document', rtf: 'document',
                odt: 'document', md: 'document',
                // PDF
                pdf: 'pdf',
                // Code
                js: 'code', ts: 'code', py: 'code', java: 'code', c: 'code', cpp: 'code',
                h: 'code', hpp: 'code', cs: 'code', go: 'code', rs: 'code', rb: 'code',
                php: 'code', html: 'code', css: 'code', scss: 'code', less: 'code',
                json: 'code', yaml: 'code', yml: 'code', xml: 'code', sh: 'code', bash: 'code',
                // 3D
                glb: 'model3d', gltf: 'model3d', obj: 'model3d', stl: 'model3d',
                fbx: 'model3d', usdz: 'model3d',
                // Archives
                zip: 'archive', tar: 'archive', gz: 'archive', rar: 'archive', '7z': 'archive',
                // Data
                csv: 'data', tsv: 'data', parquet: 'data', sqlite: 'data', db: 'data',
                xls: 'data', xlsx: 'data',
                // Fonts
                ttf: 'font', otf: 'font', woff: 'font', woff2: 'font'
            };

            const category = extMap[ext] || type || 'unknown';
            return FORMAT_COLORS[category] || FORMAT_COLORS.unknown;
        }

        // Format-specific tools configuration
        const FORMAT_TOOLS = {
            image: [
                { iconName: 'resize', label: 'Rotate', action: 'rotateImage' },
                { iconName: 'resize', label: 'Crop', action: 'cropImage' },
                { iconName: 'filter', label: 'Filters', action: 'applyFilters' },
                { iconName: 'resize', label: 'Resize', action: 'resizeImage' }
            ],
            video: [
                { iconName: 'resize', label: 'Trim', action: 'trimVideo' },
                { iconName: 'image', label: 'Frame', action: 'extractFrame' },
                { iconName: 'audio', label: 'Audio', action: 'extractAudio' }
            ],
            audio: [
                { iconName: 'resize', label: 'Trim', action: 'trimAudio' },
                { iconName: 'audio', label: 'Volume', action: 'adjustVolume' },
                { iconName: 'info', label: 'Tags', action: 'editTags' }
            ],
            pdf: [
                { iconName: 'extract', label: 'Extract', action: 'extractPages' },
                { iconName: 'file', label: 'Merge', action: 'mergePdfs' },
                { iconName: 'lock', label: 'Protect', action: 'protectPdf' }
            ],
            code: [
                { iconName: 'copy', label: 'Copy All', action: 'copyCode' },
                { iconName: 'code', label: 'Format', action: 'formatCode' },
                { iconName: 'stats', label: 'Stats', action: 'codeStats' }
            ],
            document: [
                { iconName: 'edit', label: 'Edit', action: 'editDoc' },
                { iconName: 'extract', label: 'Export', action: 'exportDoc' }
            ],
            model3d: [
                { iconName: 'model3d', label: 'Convert', action: 'convertModel' },
                { iconName: 'scale', label: 'Scale', action: 'scaleModel' },
                { iconName: 'info', label: 'Info', action: 'modelInfo' }
            ],
            archive: [
                { iconName: 'folderOpen', label: 'Extract', action: 'extractArchive' },
                { iconName: 'copy', label: 'List', action: 'listArchive' }
            ]
        };

        function updateLightboxSidebar(file) {
            const formatInfo = getFormatInfo(file);
            const badge = document.getElementById('format-badge');

            // Update format badge
            badge.innerHTML = `
                <span class="format-icon">${icon(formatInfo.iconName || 'file', 'lg')}</span>
                <span class="format-name">${formatInfo.name}</span>
            `;
            badge.style.background = `oklch(0.25 0.05 ${formatInfo.hue})`;
            badge.style.borderColor = `oklch(0.45 0.12 ${formatInfo.hue})`;

            // Update file info
            document.getElementById('info-size').textContent = file.size_fmt || '-';
            document.getElementById('info-modified').textContent = file.modified || '-';
            document.getElementById('info-type').textContent = (file.ext || 'unknown').toUpperCase();

            // Reset zoom
            currentZoom = 100;
            document.getElementById('zoom-level').textContent = '100%';

            // Update format-specific tools
            const toolsSection = document.getElementById('format-tools-section');
            const toolsContainer = document.getElementById('format-tools');
            const ext = (file.ext || '').toLowerCase();

            // Determine format category
            const extToCategory = {
                jpg: 'image', jpeg: 'image', png: 'image', gif: 'image', webp: 'image', svg: 'image', bmp: 'image', heic: 'image',
                mp4: 'video', webm: 'video', mov: 'video', avi: 'video', mkv: 'video',
                mp3: 'audio', wav: 'audio', flac: 'audio', ogg: 'audio', m4a: 'audio',
                pdf: 'pdf',
                js: 'code', ts: 'code', py: 'code', java: 'code', c: 'code', cpp: 'code', go: 'code', rs: 'code',
                html: 'code', css: 'code', json: 'code', yaml: 'code', xml: 'code', sh: 'code',
                md: 'document', txt: 'document', doc: 'document', docx: 'document',
                glb: 'model3d', gltf: 'model3d', obj: 'model3d', stl: 'model3d', fbx: 'model3d',
                zip: 'archive', tar: 'archive', gz: 'archive', rar: 'archive', '7z': 'archive'
            };

            const category = extToCategory[ext];
            const tools = FORMAT_TOOLS[category];

            if (tools && tools.length > 0) {
                toolsSection.style.display = 'block';
                toolsContainer.innerHTML = tools.map(tool => `
                    <button class="tool-btn" onclick="handleFormatTool('${tool.action}', '${file.path}')" title="${tool.label}">
                        <span class="tool-icon">${icon(tool.iconName || 'file')}</span>
                        <span class="tool-label">${tool.label}</span>
                    </button>
                `).join('');
            } else {
                toolsSection.style.display = 'none';
                toolsContainer.innerHTML = '';
            }
        }

        // Format tool handlers
        function handleFormatTool(action, filePath) {
            switch (action) {
                case 'rotateImage':
                    showToast('Rotate: Coming soon');
                    break;
                case 'cropImage':
                    showToast('Crop: Coming soon');
                    break;
                case 'applyFilters':
                    showToast('Filters: Coming soon');
                    break;
                case 'resizeImage':
                    showToast('Resize: Coming soon');
                    break;
                case 'copyCode':
                    fetch(`/api/content?path=${encodeURIComponent(filePath)}`)
                        .then(r => r.json())
                        .then(data => {
                            navigator.clipboard.writeText(data.content);
                            showToast('Code copied to clipboard');
                        });
                    break;
                case 'extractArchive':
                    fetch('/api/extract-archive', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ path: filePath })
                    }).then(r => r.json()).then(data => {
                        if (data.success) {
                            showToast('Archive extracted');
                            loadFolder(currentPath);
                        } else {
                            showToast('Extract failed: ' + data.error);
                        }
                    });
                    break;
                case 'modelInfo':
                    showToast('Model info: ' + filePath.split('/').pop());
                    break;
                default:
                    showToast(action + ': Coming soon');
            }
        }

        // Event listeners
        document.getElementById('search').oninput = () => applyFilter();

        document.getElementById('tile-size').oninput = (e) => {
            document.querySelector('.grid').style.setProperty('--tile-size', e.target.value + 'px');
            // Re-render to update folder preview grid dimensions
            renderGrid();
        };

        // Selection mode toggle
        document.getElementById('select-mode-toggle').onclick = () => {
            selectionMode = !selectionMode;
            const toggle = document.getElementById('select-mode-toggle');
            toggle.classList.toggle('active', selectionMode);
            document.getElementById('select-mode-checkbox').checked = selectionMode;
            if (selectionMode) {
                showToast('Selection mode: Click anywhere to select');
            }
        };

        // Click-drag selection rectangle and drag-drop state
        let isSelecting = false;
        let isDragging = false;
        let selectionStart = null;
        let selectionRect = null;
        let dragGhost = null;
        let dragStartTile = null;
        let dragThreshold = 5; // pixels before drag starts
        let currentDropTarget = null;

        document.querySelector('.grid-container').addEventListener('mousedown', (e) => {
            if (e.button !== 0) return; // Only left mouse button

            const tile = e.target.closest('.tile');
            selectionStart = { x: e.clientX, y: e.clientY };
            dragStartTile = tile;

            // If clicking on a selected tile, prepare for potential drag
            if (tile && tile.classList.contains('selected')) {
                // Don't start selection, wait to see if it's a drag
                return;
            }

            // If clicking on an unselected tile without shift, select it and prepare for drag
            if (tile && !e.shiftKey) {
                const idx = Array.from(document.querySelectorAll('.tile')).indexOf(tile);
                const file = filteredFiles[idx];
                if (file) {
                    selectedFiles.clear();
                    selectedFiles.add(file.path);
                    tile.classList.add('selected');
                    document.querySelectorAll('.tile').forEach(t => {
                        if (t !== tile) t.classList.remove('selected');
                    });
                }
                return;
            }

            // Start selection rectangle (empty area or shift-click)
            isSelecting = true;
            selectionRect = document.createElement('div');
            selectionRect.className = 'selection-rect';
            selectionRect.style.left = e.clientX + 'px';
            selectionRect.style.top = e.clientY + 'px';
            selectionRect.style.width = '0';
            selectionRect.style.height = '0';
            document.body.appendChild(selectionRect);

            document.querySelector('.grid').classList.add('is-selecting');

            // Clear selection unless shift is held
            if (!e.shiftKey) {
                selectedFiles.clear();
                document.querySelectorAll('.tile.selected').forEach(t => t.classList.remove('selected'));
            }
        });

        document.addEventListener('mousemove', (e) => {
            if (!selectionStart) return;

            const dx = Math.abs(e.clientX - selectionStart.x);
            const dy = Math.abs(e.clientY - selectionStart.y);

            // Check if we should start dragging selected items
            if (dragStartTile && !isSelecting && !isDragging && (dx > dragThreshold || dy > dragThreshold)) {
                if (selectedFiles.size > 0) {
                    startDrag(e);
                    return;
                }
            }

            // Handle dragging
            if (isDragging && dragGhost) {
                dragGhost.style.left = (e.clientX + 10) + 'px';
                dragGhost.style.top = (e.clientY + 10) + 'px';

                // Highlight drop targets
                updateDropTarget(e);
                return;
            }

            // Handle selection rectangle
            if (!isSelecting || !selectionRect) return;

            const x = Math.min(e.clientX, selectionStart.x);
            const y = Math.min(e.clientY, selectionStart.y);
            const width = Math.abs(e.clientX - selectionStart.x);
            const height = Math.abs(e.clientY - selectionStart.y);

            selectionRect.style.left = x + 'px';
            selectionRect.style.top = y + 'px';
            selectionRect.style.width = width + 'px';
            selectionRect.style.height = height + 'px';

            // Select tiles that intersect with rectangle
            const rect = { left: x, top: y, right: x + width, bottom: y + height };
            document.querySelectorAll('.tile').forEach((tile, idx) => {
                const tileRect = tile.getBoundingClientRect();
                const intersects = !(
                    tileRect.right < rect.left ||
                    tileRect.left > rect.right ||
                    tileRect.bottom < rect.top ||
                    tileRect.top > rect.bottom
                );

                const file = filteredFiles[idx];
                if (file) {
                    if (intersects) {
                        selectedFiles.add(file.path);
                        tile.classList.add('selected');
                    } else if (!e.shiftKey) {
                        selectedFiles.delete(file.path);
                        tile.classList.remove('selected');
                    }
                }
            });

            // Update selection count
            const selCount = document.getElementById('sel-count');
            const selBar = document.getElementById('selection-bar');
            if (selectedFiles.size > 0) {
                selBar.classList.add('active');
                selCount.textContent = selectedFiles.size;
            } else {
                selBar.classList.remove('active');
            }
        });

        function startDrag(e) {
            isDragging = true;
            document.body.classList.add('is-dragging');

            // Create drag ghost
            dragGhost = document.createElement('div');
            dragGhost.className = 'drag-ghost';
            const count = selectedFiles.size;
            dragGhost.innerHTML = `
                <div class="drag-icon">${icon('folder', 'lg')}</div>
                <div class="drag-label">${count} item${count > 1 ? 's' : ''}</div>
            `;
            dragGhost.style.left = (e.clientX + 10) + 'px';
            dragGhost.style.top = (e.clientY + 10) + 'px';
            document.body.appendChild(dragGhost);
        }

        function updateDropTarget(e) {
            // Remove previous highlight
            if (currentDropTarget) {
                currentDropTarget.classList.remove('drop-target', 'drop-folder', 'drop-file');
                currentDropTarget = null;
            }

            const tile = document.elementFromPoint(e.clientX, e.clientY)?.closest('.tile');
            if (!tile) return;

            const idx = Array.from(document.querySelectorAll('.tile')).indexOf(tile);
            const file = filteredFiles[idx];
            if (!file) return;

            // Don't drop on itself
            if (selectedFiles.has(file.path)) return;

            currentDropTarget = tile;
            if (file.is_dir) {
                tile.classList.add('drop-target', 'drop-folder');
            } else {
                tile.classList.add('drop-target', 'drop-file');
            }
        }

        async function handleDrop(e) {
            if (!currentDropTarget) return;

            const idx = Array.from(document.querySelectorAll('.tile')).indexOf(currentDropTarget);
            const targetFile = filteredFiles[idx];
            if (!targetFile) return;

            const selectedPaths = Array.from(selectedFiles);

            if (targetFile.is_dir) {
                // Move items into folder
                await moveItemsToFolder(selectedPaths, targetFile.path);
            } else if (targetFile.name.endsWith('.app')) {
                // Open items with app
                showOpenWithAppDialog(selectedPaths, targetFile.path);
            } else {
                // Create new folder with items
                showCreateFolderDialog(selectedPaths, targetFile.path);
            }
        }

        async function moveItemsToFolder(paths, folderPath) {
            try {
                const res = await fetch('/api/move-items', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ paths, destination: folderPath })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`Moved ${paths.length} item${paths.length > 1 ? 's' : ''} to ${folderPath.split('/').pop()}`);
                    selectedFiles.clear();
                    await loadFolder(currentPath);
                } else {
                    showToast('Move failed: ' + (data.error || 'Unknown error'));
                }
            } catch (err) {
                showToast('Move failed: ' + err.message);
            }
        }

        function showOpenWithAppDialog(paths, appPath) {
            const appName = appPath.split('/').pop().replace('.app', '');
            if (confirm(`Open ${paths.length} item${paths.length > 1 ? 's' : ''} with ${appName}?`)) {
                fetch('/api/open-with-app', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ paths, app: appPath })
                }).then(() => {
                    showToast(`Opened with ${appName}`);
                });
            }
        }

        function showCreateFolderDialog(paths, targetPath) {
            const targetName = targetPath.split('/').pop();
            const defaultName = 'New Folder';

            // Create dialog
            const dialog = document.createElement('div');
            dialog.className = 'folder-dialog-overlay';
            dialog.innerHTML = `
                <div class="folder-dialog">
                    <h3>Create Folder</h3>
                    <p>Group ${paths.length + 1} items into a new folder:</p>
                    <input type="text" class="folder-name-input" value="${defaultName}" autofocus>
                    <div class="dialog-buttons">
                        <button class="dialog-cancel">Cancel</button>
                        <button class="dialog-confirm">Create</button>
                    </div>
                </div>
            `;
            document.body.appendChild(dialog);

            const input = dialog.querySelector('.folder-name-input');
            input.select();

            const cleanup = () => dialog.remove();

            dialog.querySelector('.dialog-cancel').onclick = cleanup;
            dialog.querySelector('.folder-dialog-overlay').onclick = (e) => {
                if (e.target === dialog) cleanup();
            };

            dialog.querySelector('.dialog-confirm').onclick = async () => {
                const folderName = input.value.trim();
                if (!folderName) return;

                try {
                    const res = await fetch('/api/create-folder-with-items', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            folderName,
                            parentPath: currentPath,
                            itemPaths: [...paths, targetPath]
                        })
                    });
                    const data = await res.json();
                    if (data.success) {
                        showToast(`Created folder "${folderName}"`);
                        selectedFiles.clear();
                        await loadFolder(currentPath);
                    } else {
                        showToast('Failed: ' + (data.error || 'Unknown error'));
                    }
                } catch (err) {
                    showToast('Failed: ' + err.message);
                }
                cleanup();
            };

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') dialog.querySelector('.dialog-confirm').click();
                if (e.key === 'Escape') cleanup();
            });
        }

        document.addEventListener('mouseup', (e) => {
            // Handle drag end
            if (isDragging) {
                handleDrop(e);
                isDragging = false;
                document.body.classList.remove('is-dragging');
                if (dragGhost) {
                    dragGhost.remove();
                    dragGhost = null;
                }
                if (currentDropTarget) {
                    currentDropTarget.classList.remove('drop-target', 'drop-folder', 'drop-file');
                    currentDropTarget = null;
                }
            }

            // Handle selection end
            if (isSelecting) {
                isSelecting = false;
                if (selectionRect) {
                    selectionRect.remove();
                    selectionRect = null;
                }
                document.querySelector('.grid')?.classList.remove('is-selecting');
                renderGrid(); // Re-render to update checkmarks
            }

            // Reset state
            selectionStart = null;
            dragStartTile = null;
        });

        // =====================
        // EXTERNAL DRAG-IN (Finder/OS)
        // =====================
        const gridContainer = document.querySelector('.grid-container');

        gridContainer.addEventListener('dragover', (e) => {
            // Only handle external drags (from Finder)
            if (e.dataTransfer.types.includes('Files')) {
                e.preventDefault();
                e.stopPropagation();
                e.dataTransfer.dropEffect = 'copy';
                gridContainer.classList.add('external-drop-active');
            }
        });

        gridContainer.addEventListener('dragleave', (e) => {
            // Only remove if leaving the container entirely
            if (!gridContainer.contains(e.relatedTarget)) {
                gridContainer.classList.remove('external-drop-active');
            }
        });

        gridContainer.addEventListener('drop', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            gridContainer.classList.remove('external-drop-active');

            const files = e.dataTransfer.files;
            if (!files || files.length === 0) return;

            showToast(`Uploading ${files.length} file(s)...`);

            const formData = new FormData();
            formData.append('targetPath', currentPath);

            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    showToast(`Uploaded ${result.uploaded} file(s)`, 'success');
                    loadDir(currentPath);
                } else {
                    showToast(`Upload failed: ${result.error}`, 'error');
                }
            } catch (err) {
                console.error('Upload error:', err);
                showToast('Upload failed', 'error');
            }
        });

        document.addEventListener('keydown', (e) => {
            // Cmd+/- for zoom
            if ((e.metaKey || e.ctrlKey) && (e.key === '=' || e.key === '+')) {
                e.preventDefault();
                const slider = document.getElementById('tile-size');
                slider.value = Math.min(450, parseInt(slider.value) + 40);
                slider.dispatchEvent(new Event('input'));
                return;
            }
            if ((e.metaKey || e.ctrlKey) && e.key === '-') {
                e.preventDefault();
                const slider = document.getElementById('tile-size');
                slider.value = Math.max(180, parseInt(slider.value) - 40);
                slider.dispatchEvent(new Event('input'));
                return;
            }

            // Cmd+Z = Undo
            if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey && !e.target.matches('input')) {
                e.preventDefault();
                performUndo();
                return;
            }
            // Cmd+Shift+Z = Redo
            if ((e.metaKey || e.ctrlKey) && e.key === 'z' && e.shiftKey && !e.target.matches('input')) {
                e.preventDefault();
                performRedo();
                return;
            }
            // Cmd+C = Copy
            if ((e.metaKey || e.ctrlKey) && e.key === 'c' && !e.target.matches('input')) {
                e.preventDefault();
                copySelected();
                return;
            }
            // Cmd+X = Cut
            if ((e.metaKey || e.ctrlKey) && e.key === 'x' && !e.target.matches('input')) {
                e.preventDefault();
                cutSelected();
                return;
            }
            // Cmd+V = Paste
            if ((e.metaKey || e.ctrlKey) && e.key === 'v' && !e.target.matches('input')) {
                e.preventDefault();
                pasteToCurrentFolder();
                return;
            }
            // Delete/Backspace with selection = delete files
            if ((e.key === 'Delete' || (e.key === 'Backspace' && e.metaKey)) && selectedFiles.size > 0) {
                e.preventDefault();
                deleteSelected();
                return;
            }
            // Cmd+A = Select all
            if ((e.metaKey || e.ctrlKey) && e.key === 'a' && !e.target.matches('input')) {
                e.preventDefault();
                filteredFiles.forEach(f => selectedFiles.add(f.path));
                renderGrid();
                return;
            }
            // Escape = Clear selection
            if (e.key === 'Escape' && selectedFiles.size > 0 && !document.getElementById('lightbox').classList.contains('active')) {
                selectedFiles.clear();
                renderGrid();
                return;
            }

            if (e.target.matches('input')) return;

            const lightbox = document.getElementById('lightbox');
            if (lightbox.classList.contains('active')) {
                if (e.key === 'Escape') closeLightbox();
                if (e.key === 'ArrowLeft') navLightbox(-1);
                if (e.key === 'ArrowRight') navLightbox(1);
                if (e.key === 'Enter') openInApp();
            } else {
                if (e.key === 'Backspace' && selectedFiles.size === 0) {
                    e.preventDefault();
                    goUp();
                }
            }
        });

        // =====================
        // SETTINGS POPUP
        // =====================
        const settings = {
            showHidden: false,
            showExtensions: true,
            showSidebar: true,
            confirmDelete: true,
            autoRefresh: false,
            sortBy: 'name',
            sortOrder: 'asc',
            foldersFirst: true,
            doubleClick: 'open',
            tileSize: 280,
            gridGap: 17,
            maxItems: 200,
            theme: 'dark'
        };

        // Load settings from localStorage
        function loadSettings() {
            const saved = localStorage.getItem('fileExplorerSettings');
            if (saved) {
                Object.assign(settings, JSON.parse(saved));
            }
            applySettings();
        }

        function saveSettings() {
            localStorage.setItem('fileExplorerSettings', JSON.stringify(settings));
        }

        function applySettings() {
            // Apply tile size
            document.getElementById('tile-size').value = settings.tileSize;
            document.documentElement.style.setProperty('--tile-size', settings.tileSize + 'px');

            // Apply grid gap
            document.querySelector('.grid').style.gap = settings.gridGap + 'px';

            // Apply sidebar visibility
            document.querySelector('.sidebar').style.display = settings.showSidebar ? 'flex' : 'none';

            // Apply max items
            MAX_VISIBLE_ITEMS = settings.maxItems;

            // Update toggles in settings popup
            updateSettingsUI();
        }

        function updateSettingsUI() {
            // Update toggle states
            document.getElementById('toggle-hidden')?.classList.toggle('active', settings.showHidden);
            document.getElementById('toggle-extensions')?.classList.toggle('active', settings.showExtensions);
            document.getElementById('toggle-sidebar')?.classList.toggle('active', settings.showSidebar);
            document.getElementById('toggle-confirm-delete')?.classList.toggle('active', settings.confirmDelete);
            document.getElementById('toggle-auto-refresh')?.classList.toggle('active', settings.autoRefresh);
            document.getElementById('toggle-folders-first')?.classList.toggle('active', settings.foldersFirst);

            // Update sliders
            const tileSizeSlider = document.getElementById('settings-tile-size');
            const gridGapSlider = document.getElementById('settings-grid-gap');
            const depthSlider = document.getElementById('settings-depth-factor');

            if (tileSizeSlider) {
                tileSizeSlider.value = settings.tileSize;
                document.getElementById('tile-size-value').textContent = settings.tileSize + 'px';
            }
            if (gridGapSlider) {
                gridGapSlider.value = settings.gridGap;
                document.getElementById('grid-gap-value').textContent = settings.gridGap + 'px';
            }
            if (depthSlider) {
                depthSlider.value = depthFactor * 100;
                document.getElementById('depth-factor-value').textContent = depthFactor.toFixed(2);
            }

            // Update selects
            const sortBySelect = document.getElementById('settings-sort-by');
            const sortOrderSelect = document.getElementById('settings-sort-order');
            const maxItemsSelect = document.getElementById('settings-max-items');
            const doubleClickSelect = document.getElementById('settings-double-click');

            if (sortBySelect) sortBySelect.value = settings.sortBy;
            if (sortOrderSelect) sortOrderSelect.value = settings.sortOrder;
            if (maxItemsSelect) maxItemsSelect.value = settings.maxItems;
            if (doubleClickSelect) doubleClickSelect.value = settings.doubleClick;
        }

        function openSettings() {
            updateSettingsUI();
            document.getElementById('settings-overlay').classList.add('active');
        }

        function closeSettings() {
            document.getElementById('settings-overlay').classList.remove('active');
            saveSettings();
        }

        function saveAndCloseSettings() {
            saveSettings();
            closeSettings();
        }

        function resetSettings() {
            if (confirm('Reset all settings to defaults?')) {
                localStorage.removeItem('fileExplorerSettings');
                location.reload();
            }
        }

        function toggleSetting(key) {
            settings[key] = !settings[key];
            applySettings();

            if (key === 'showHidden') {
                navigate(currentPath, false);
            }
        }

        function setTheme(theme) {
            settings.theme = theme;
            document.querySelectorAll('.theme-option').forEach(el => {
                el.classList.toggle('active', el.dataset.theme === theme);
            });
            // Theme switching would go here
            saveSettings();
        }

        function updateTileSize(value) {
            settings.tileSize = parseInt(value);
            document.getElementById('tile-size-value').textContent = value + 'px';
            document.getElementById('tile-size').value = value;
            document.documentElement.style.setProperty('--tile-size', value + 'px');
            saveSettings();
        }

        function updateGridGap(value) {
            settings.gridGap = parseInt(value);
            document.getElementById('grid-gap-value').textContent = value + 'px';
            document.querySelector('.grid').style.gap = value + 'px';
            saveSettings();
        }

        function updateMaxItems(value) {
            settings.maxItems = parseInt(value);
            MAX_VISIBLE_ITEMS = settings.maxItems;
            applyFilter();
            saveSettings();
        }

        function updateDepthFactor(value) {
            depthFactor = value / 100;
            document.getElementById('depth-factor-value').textContent = depthFactor.toFixed(2);
            updateCSSColors();
            renderGrid();
            saveSettings();
        }

        function updateSortBy(value) {
            settings.sortBy = value;
            sortFiles();
            saveSettings();
        }

        function updateSortOrder(value) {
            settings.sortOrder = value;
            sortFiles();
            saveSettings();
        }

        function updateDoubleClick(value) {
            settings.doubleClick = value;
            saveSettings();
        }

        function sortFiles() {
            if (!files || files.length === 0) return;

            files.sort((a, b) => {
                // Folders first if enabled
                if (settings.foldersFirst) {
                    if (a.is_dir && !b.is_dir) return -1;
                    if (!a.is_dir && b.is_dir) return 1;
                }

                let cmp = 0;
                switch (settings.sortBy) {
                    case 'name':
                        cmp = a.name.localeCompare(b.name);
                        break;
                    case 'modified':
                        cmp = (a.modified || '').localeCompare(b.modified || '');
                        break;
                    case 'size':
                        cmp = (a.size || 0) - (b.size || 0);
                        break;
                    case 'type':
                        cmp = (a.ext || '').localeCompare(b.ext || '');
                        break;
                }
                return settings.sortOrder === 'desc' ? -cmp : cmp;
            });

            applyFilter();
        }

        // Settings tab navigation
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.settings-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.settings-tab-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
            });
        });

        // Settings panel toggle - now opens popup
        document.getElementById('settings-toggle').onclick = () => {
            openSettings();
        };

        // Close settings on overlay click
        document.getElementById('settings-overlay').addEventListener('click', (e) => {
            if (e.target.id === 'settings-overlay') {
                closeSettings();
            }
        });

        // Close settings on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.getElementById('settings-overlay').classList.contains('active')) {
                closeSettings();
            }
        });

        // Initialize colors
        updateCSSColors();
        renderColorSettings();
        loadSettings();

        // Memory monitoring
        function updateMemoryStats() {
            const memValue = document.getElementById('mem-value');
            if (!memValue) return;

            if (performance.memory) {
                // Chrome/Edge - actual heap size
                const used = performance.memory.usedJSHeapSize / (1024 * 1024);
                const total = performance.memory.jsHeapSizeLimit / (1024 * 1024);
                const pct = (used / total) * 100;

                memValue.textContent = `${used.toFixed(0)}MB`;
                memValue.className = 'mem-value' + (pct > 70 ? ' critical' : pct > 50 ? ' warning' : '');
            } else {
                // Safari/Firefox - estimate from trackers
                const renderers = resourceTracker.threeRenderers.size;
                const pending = resourceTracker.pendingFetches.size;
                memValue.textContent = `${renderers}R/${pending}F`;
            }
        }

        // Update memory stats every 2 seconds
        setInterval(updateMemoryStats, 2000);
        updateMemoryStats();

        // Click to force cleanup
        document.getElementById('memory-stats').addEventListener('click', () => {
            cleanupThreeResources();
            if (window.gc) window.gc(); // Chrome with --js-flags="--expose-gc"
            updateMemoryStats();
        });

        // =====================
        // FILTER FUNCTIONALITY
        // =====================
        let activeFilters = new Set(['folder', 'image', 'vector', 'video', 'audio', 'code', 'doc', 'pdf', 'data', 'config', 'archive', 'model3d', 'font', 'notebook', 'executable', 'database', 'binary']);
        const otherTypes = ['vector', 'font', 'notebook', 'executable', 'database', 'binary'];

        function toggleFilterMenu() {
            const menu = document.getElementById('filter-menu');
            menu.classList.toggle('show');
        }

        function toggleAllFilters(checkbox) {
            const menu = document.getElementById('filter-menu');
            const checkboxes = menu.querySelectorAll('input[type="checkbox"]:not([value="all"])');
            checkboxes.forEach(cb => cb.checked = checkbox.checked);
            updateFilters();
        }

        function updateFilters() {
            const menu = document.getElementById('filter-menu');
            const checkboxes = menu.querySelectorAll('input[type="checkbox"]:not([value="all"])');
            const allCheckbox = menu.querySelector('input[value="all"]');

            activeFilters.clear();
            checkboxes.forEach(cb => {
                if (cb.checked) {
                    if (cb.value === 'other') {
                        otherTypes.forEach(t => activeFilters.add(t));
                    } else {
                        activeFilters.add(cb.value);
                    }
                }
            });

            // Update "All" checkbox state
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            const someChecked = Array.from(checkboxes).some(cb => cb.checked);
            allCheckbox.checked = allChecked;
            allCheckbox.indeterminate = someChecked && !allChecked;

            // Update filter button state
            const filterBtn = document.getElementById('filter-btn');
            const filterCount = document.getElementById('filter-count');
            const uncheckedCount = Array.from(checkboxes).filter(cb => !cb.checked).length;

            if (uncheckedCount > 0) {
                filterBtn.classList.add('active');
                filterCount.style.display = 'inline';
                filterCount.textContent = checkboxes.length - uncheckedCount;
            } else {
                filterBtn.classList.remove('active');
                filterCount.style.display = 'none';
            }

            applyFilter();
        }

        // =====================
        // SORT FUNCTIONALITY
        // =====================
        let currentSort = 'name';
        let sortDirection = 'asc';

        function toggleSortMenu() {
            const menu = document.getElementById('sort-menu');
            menu.classList.toggle('show');
            // Close filter menu if open
            document.getElementById('filter-menu').classList.remove('show');
        }

        function setSort(sortBy) {
            currentSort = sortBy;
            updateSortUI();
            applyFilter();
            document.getElementById('sort-menu').classList.remove('show');
        }

        function setSortDirection(dir) {
            sortDirection = dir;
            updateSortUI();
            applyFilter();
            document.getElementById('sort-menu').classList.remove('show');
        }

        function updateSortUI() {
            // Update sort label
            const labels = { name: 'Name', date: 'Date', size: 'Size', type: 'Type' };
            document.getElementById('sort-label').textContent = labels[currentSort];
            document.getElementById('sort-dir').textContent = sortDirection === 'asc' ? '↑' : '↓';

            // Update checkmarks
            document.querySelectorAll('.sort-option[data-sort]').forEach(opt => {
                opt.classList.toggle('active', opt.dataset.sort === currentSort);
            });
            document.getElementById('sort-asc').classList.toggle('active', sortDirection === 'asc');
            document.getElementById('sort-desc').classList.toggle('active', sortDirection === 'desc');
        }

        function sortFiles(fileList) {
            const sorted = [...fileList];

            // Folders always first
            sorted.sort((a, b) => {
                if (a.is_dir && !b.is_dir) return -1;
                if (!a.is_dir && b.is_dir) return 1;

                let comparison = 0;
                switch (currentSort) {
                    case 'name':
                        comparison = a.name.localeCompare(b.name, undefined, { numeric: true });
                        break;
                    case 'date':
                        comparison = (a.modified || 0) - (b.modified || 0);
                        break;
                    case 'size':
                        comparison = (a.size || 0) - (b.size || 0);
                        break;
                    case 'type':
                        comparison = (a.ext || '').localeCompare(b.ext || '');
                        break;
                }

                return sortDirection === 'asc' ? comparison : -comparison;
            });

            return sorted;
        }

        // Close sort menu when clicking outside
        document.addEventListener('click', (e) => {
            const sortDropdown = document.querySelector('.sort-dropdown');
            if (!sortDropdown.contains(e.target)) {
                document.getElementById('sort-menu').classList.remove('show');
            }
        });

        // Close filter menu when clicking outside
        document.addEventListener('click', (e) => {
            const filterDropdown = document.querySelector('.filter-dropdown');
            if (filterDropdown && !filterDropdown.contains(e.target)) {
                document.getElementById('filter-menu').classList.remove('show');
            }
        });

        // =====================
        // VIEW MODES
        // =====================
        let currentViewMode = 'grid';  // 'grid', 'list', 'column'
        let columnPanes = [];  // For column view navigation

        function setViewMode(mode) {
            if (mode === currentViewMode) return;
            currentViewMode = mode;

            // Update toggle buttons
            document.querySelectorAll('.view-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.view === mode);
            });

            // Re-render grid with new view mode
            applyFilter();
        }

        function renderListView(files, grid) {
            grid.className = 'grid view-list';
            grid.innerHTML = '';

            files.forEach(file => {
                const item = document.createElement('div');
                item.className = 'tile';
                item.dataset.path = file.path;
                item.dataset.name = file.name;
                item.dataset.isDir = file.is_dir ? 'true' : 'false';
                item.draggable = true;

                const previewUrl = file.is_dir
                    ? '/api/folder-icon'
                    : `/api/thumbnail?path=${encodeURIComponent(file.path)}&size=64`;

                const modDate = file.modified
                    ? new Date(file.modified * 1000).toLocaleDateString()
                    : '-';
                const sizeStr = file.is_dir
                    ? '-'
                    : (file.size_fmt || '-');

                item.innerHTML = `
                    <div class="preview">
                        <img src="${previewUrl}" alt="" loading="lazy" onerror="this.style.display='none'">
                    </div>
                    <div class="label">${escapeHtml(file.name)}</div>
                    <div class="file-meta">
                        <span class="file-meta-item">${modDate}</span>
                        <span class="file-meta-item">${sizeStr}</span>
                        <span class="file-meta-item">${file.ext || (file.is_dir ? 'Folder' : '-')}</span>
                    </div>
                `;

                item.addEventListener('click', (e) => {
                    if (e.ctrlKey || e.metaKey) {
                        toggleSelect(file.path);
                    } else {
                        if (file.is_dir) {
                            navigateTo(file.path);
                        } else {
                            openLightbox(file);
                        }
                    }
                });

                item.addEventListener('dblclick', () => {
                    if (!file.is_dir) {
                        openInApp(file.path);
                    }
                });

                grid.appendChild(item);
            });
        }

        function renderColumnView(files, grid) {
            grid.className = 'grid view-column';
            grid.innerHTML = '';

            // First column shows current directory
            const firstPane = document.createElement('div');
            firstPane.className = 'column-pane';

            files.forEach(file => {
                const item = document.createElement('div');
                item.className = 'column-item' + (file.is_dir ? ' folder' : '');
                item.dataset.path = file.path;
                item.dataset.name = file.name;
                item.dataset.isDir = file.is_dir ? 'true' : 'false';

                const previewUrl = file.is_dir
                    ? '/api/folder-icon'
                    : `/api/thumbnail?path=${encodeURIComponent(file.path)}&size=40`;

                item.innerHTML = `
                    <div class="column-item-icon">
                        <img src="${previewUrl}" alt="" loading="lazy" onerror="this.style.display='none'">
                    </div>
                    <span class="column-item-name">${escapeHtml(file.name)}</span>
                `;

                item.addEventListener('click', () => {
                    // Remove selected from siblings
                    firstPane.querySelectorAll('.column-item').forEach(i => i.classList.remove('selected'));
                    item.classList.add('selected');

                    // Remove subsequent panes
                    while (grid.children.length > 1) {
                        grid.removeChild(grid.lastChild);
                    }

                    if (file.is_dir) {
                        // Load folder contents in next pane
                        loadColumnPane(file.path, grid);
                    } else {
                        // Show preview pane
                        showColumnPreview(file, grid);
                    }
                });

                item.addEventListener('dblclick', () => {
                    if (file.is_dir) {
                        navigateTo(file.path);
                    } else {
                        openInApp(file.path);
                    }
                });

                firstPane.appendChild(item);
            });

            grid.appendChild(firstPane);
        }

        async function loadColumnPane(path, grid) {
            try {
                const response = await fetch(`/api/list?path=${encodeURIComponent(path)}`);
                const files = await response.json();

                const pane = document.createElement('div');
                pane.className = 'column-pane';

                const sorted = sortFiles(files);

                sorted.forEach(file => {
                    const item = document.createElement('div');
                    item.className = 'column-item' + (file.is_dir ? ' folder' : '');
                    item.dataset.path = file.path;
                    item.dataset.name = file.name;
                    item.dataset.isDir = file.is_dir ? 'true' : 'false';

                    const previewUrl = file.is_dir
                        ? '/api/folder-icon'
                        : `/api/thumbnail?path=${encodeURIComponent(file.path)}&size=40`;

                    item.innerHTML = `
                        <div class="column-item-icon">
                            <img src="${previewUrl}" alt="" loading="lazy" onerror="this.style.display='none'">
                        </div>
                        <span class="column-item-name">${escapeHtml(file.name)}</span>
                    `;

                    item.addEventListener('click', () => {
                        pane.querySelectorAll('.column-item').forEach(i => i.classList.remove('selected'));
                        item.classList.add('selected');

                        // Remove panes after this one
                        const paneIndex = Array.from(grid.children).indexOf(pane);
                        while (grid.children.length > paneIndex + 1) {
                            grid.removeChild(grid.lastChild);
                        }

                        if (file.is_dir) {
                            loadColumnPane(file.path, grid);
                        } else {
                            showColumnPreview(file, grid);
                        }
                    });

                    item.addEventListener('dblclick', () => {
                        if (file.is_dir) {
                            navigateTo(file.path);
                        } else {
                            openInApp(file.path);
                        }
                    });

                    pane.appendChild(item);
                });

                grid.appendChild(pane);
                pane.scrollIntoView({ behavior: 'smooth', inline: 'end' });
            } catch (err) {
                console.error('Failed to load column pane:', err);
            }
        }

        function showColumnPreview(file, grid) {
            const previewPane = document.createElement('div');
            previewPane.className = 'column-pane';
            previewPane.style.padding = '16px';
            previewPane.style.minWidth = '250px';
            previewPane.style.background = 'rgba(40, 40, 40, 0.9)';

            const previewUrl = `/api/thumbnail?path=${encodeURIComponent(file.path)}&size=200`;

            previewPane.innerHTML = `
                <div style="text-align:center;margin-bottom:16px;">
                    <img src="${previewUrl}" alt="" style="max-width:100%;max-height:180px;border-radius:8px;"
                         onerror="this.style.display='none'">
                </div>
                <div style="font-weight:600;margin-bottom:8px;word-break:break-word;">${escapeHtml(file.name)}</div>
                <div style="color:var(--text-secondary);font-size:11px;">
                    <div>Size: ${file.size_fmt || '-'}</div>
                    <div>Type: ${file.ext || 'Unknown'}</div>
                    ${file.modified ? `<div>Modified: ${new Date(file.modified * 1000).toLocaleString()}</div>` : ''}
                </div>
                <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap;">
                    <button onclick="openInApp('${file.path.replace(/'/g, "\\'")}')"
                        style="flex:1;padding:8px 12px;border:none;border-radius:6px;background:var(--accent);color:white;cursor:pointer;">
                        Open
                    </button>
                    <button onclick="openLightbox(cachedFiles.find(f=>f.path==='${file.path.replace(/'/g, "\\'")}'))"
                        style="flex:1;padding:8px 12px;border:none;border-radius:6px;background:rgba(255,255,255,0.15);color:white;cursor:pointer;">
                        Preview
                    </button>
                </div>
            `;

            grid.appendChild(previewPane);
            previewPane.scrollIntoView({ behavior: 'smooth', inline: 'end' });
        }

        // =====================
        // NEW FOLDER
        // =====================
        async function createNewFolder() {
            const name = prompt('New folder name:', 'New Folder');
            if (!name || !name.trim()) return;

            try {
                const res = await fetch('/api/create-folder', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: currentPath, name: name.trim() })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`Created folder: ${name}`);
                    navigate(currentPath, false);
                    checkHistoryStatus();
                } else {
                    showToast(data.error, true);
                }
            } catch (e) {
                showToast('Failed to create folder', true);
            }
        }

        // =====================
        // CONTEXT MENU
        // =====================
        let contextTarget = null; // { type: 'file'|'folder'|'empty'|'multi', path, idx }

        function showContextMenu(e, target) {
            e.preventDefault();
            contextTarget = target;

            const menu = document.getElementById('context-menu');
            let html = '';

            if (target.type === 'multi') {
                // Multiple selection
                const count = selectedFiles.size;
                html = `
                    <div class="context-menu-item" onclick="openSelectedFiles()"><span class="label">Open All (${count})</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item" onclick="cutSelected(); hideContextMenu();"><span class="label">${icon('resize')} Cut</span><span class="shortcut">⌘X</span></div>
                    <div class="context-menu-item" onclick="copySelected(); hideContextMenu();"><span class="label">${icon('copy')} Copy</span><span class="shortcut">⌘C</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item" onclick="compressSelected()"><span class="label">${icon('archive')} Compress (${count} items)</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item danger" onclick="deleteSelected(); hideContextMenu();"><span class="label">${icon('file')} Move to Trash</span><span class="shortcut">⌘⌫</span></div>
                `;
            } else if (target.type === 'empty') {
                // Empty space
                html = `
                    <div class="context-menu-item" onclick="createNewFolder(); hideContextMenu();"><span class="label">${icon('newFolder')} New Folder</span><span class="shortcut">⇧⌘N</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item ${clipboard.files.length === 0 ? 'disabled' : ''}" onclick="pasteToCurrentFolder(); hideContextMenu();"><span class="label">${icon('extract')} Paste</span><span class="shortcut">⌘V</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item" onclick="selectAllFiles(); hideContextMenu();"><span class="label">Select All</span><span class="shortcut">⌘A</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item" onclick="navigate(currentPath, false); hideContextMenu();"><span class="label">${icon('resize')} Refresh</span><span class="shortcut">⌘R</span></div>
                `;
            } else if (target.type === 'folder') {
                // Folder
                html = `
                    <div class="context-menu-item" onclick="navigate(contextTarget.path); hideContextMenu();"><span class="label">${icon('folderOpen')} Open</span><span class="shortcut">↵</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item" onclick="cutContextItem()"><span class="label">${icon('resize')} Cut</span><span class="shortcut">⌘X</span></div>
                    <div class="context-menu-item" onclick="copyContextItem()"><span class="label">${icon('copy')} Copy</span><span class="shortcut">⌘C</span></div>
                    <div class="context-menu-item" onclick="duplicateContextItem()"><span class="label">${icon('duplicate')} Duplicate</span><span class="shortcut">⌘D</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item" onclick="renameContextItem()"><span class="label">${icon('edit')} Rename</span></div>
                    <div class="context-menu-item" onclick="copyPathToClipboard()"><span class="label">${icon('copy')} Copy Path</span><span class="shortcut">⇧⌘C</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item" onclick="compressContextItem()"><span class="label">${icon('archive')} Compress</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item danger" onclick="deleteContextItem()"><span class="label">${icon('file')} Move to Trash</span><span class="shortcut">⌘⌫</span></div>
                `;
            } else {
                // File
                html = `
                    <div class="context-menu-item" onclick="openLightbox(contextTarget.idx); hideContextMenu();"><span class="label">${icon('eye')} Quick Look</span><span class="shortcut">Space</span></div>
                    <div class="context-menu-item" onclick="openContextItemInApp()"><span class="label">${icon('extract')} Open in App</span><span class="shortcut">⌘↵</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item" onclick="cutContextItem()"><span class="label">${icon('resize')} Cut</span><span class="shortcut">⌘X</span></div>
                    <div class="context-menu-item" onclick="copyContextItem()"><span class="label">${icon('copy')} Copy</span><span class="shortcut">⌘C</span></div>
                    <div class="context-menu-item" onclick="duplicateContextItem()"><span class="label">${icon('duplicate')} Duplicate</span><span class="shortcut">⌘D</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item" onclick="renameContextItem()"><span class="label">${icon('edit')} Rename</span></div>
                    <div class="context-menu-item" onclick="copyPathToClipboard()"><span class="label">${icon('copy')} Copy Path</span><span class="shortcut">⇧⌘C</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item" onclick="compressContextItem()"><span class="label">${icon('archive')} Compress</span></div>
                    <div class="divider"></div>
                    <div class="context-menu-item danger" onclick="deleteContextItem()"><span class="label">${icon('file')} Move to Trash</span><span class="shortcut">⌘⌫</span></div>
                `;
            }

            menu.innerHTML = html;
            menu.classList.add('show');

            // Position menu
            const menuRect = menu.getBoundingClientRect();
            let x = e.clientX;
            let y = e.clientY;

            if (x + menuRect.width > window.innerWidth) {
                x = window.innerWidth - menuRect.width - 10;
            }
            if (y + menuRect.height > window.innerHeight) {
                y = window.innerHeight - menuRect.height - 10;
            }

            menu.style.left = x + 'px';
            menu.style.top = y + 'px';
        }

        function hideContextMenu() {
            document.getElementById('context-menu').classList.remove('show');
            contextTarget = null;
        }

        // Context menu actions
        function cutContextItem() {
            if (!contextTarget) return;
            selectedFiles.clear();
            selectedFiles.add(contextTarget.path);
            cutSelected();
            hideContextMenu();
        }

        function copyContextItem() {
            if (!contextTarget) return;
            selectedFiles.clear();
            selectedFiles.add(contextTarget.path);
            copySelected();
            hideContextMenu();
        }

        async function duplicateContextItem() {
            if (!contextTarget) return;
            hideContextMenu();
            try {
                const res = await fetch('/api/duplicate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: contextTarget.path })
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Duplicated');
                    navigate(currentPath, false);
                    checkHistoryStatus();
                } else {
                    showToast(data.error, true);
                }
            } catch (e) {
                showToast('Duplicate failed', true);
            }
        }

        async function renameContextItem() {
            if (!contextTarget) return;
            hideContextMenu();
            const currentName = contextTarget.path.split('/').pop();
            const newName = prompt('Rename to:', currentName);
            if (!newName || newName === currentName) return;

            try {
                const res = await fetch('/api/rename', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: contextTarget.path, newName: newName.trim() })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`Renamed to ${newName}`);
                    navigate(currentPath, false);
                    checkHistoryStatus();
                } else {
                    showToast(data.error, true);
                }
            } catch (e) {
                showToast('Rename failed', true);
            }
        }

        function copyPathToClipboard() {
            if (!contextTarget) return;
            navigator.clipboard.writeText(contextTarget.path);
            showToast('Path copied');
            hideContextMenu();
        }

        async function compressContextItem() {
            if (!contextTarget) return;
            hideContextMenu();
            showToast('Compressing...');
            try {
                const res = await fetch('/api/compress', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ files: [contextTarget.path] })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`Created ${data.name}`);
                    navigate(currentPath, false);
                } else {
                    showToast(data.error, true);
                }
            } catch (e) {
                showToast('Compress failed', true);
            }
        }

        async function compressSelected() {
            if (selectedFiles.size === 0) return;
            hideContextMenu();
            showToast('Compressing...');
            try {
                const res = await fetch('/api/compress', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ files: [...selectedFiles] })
                });
                const data = await res.json();
                if (data.success) {
                    showToast(`Created ${data.name}`);
                    selectedFiles.clear();
                    navigate(currentPath, false);
                } else {
                    showToast(data.error, true);
                }
            } catch (e) {
                showToast('Compress failed', true);
            }
        }

        function deleteContextItem() {
            if (!contextTarget) return;
            selectedFiles.clear();
            selectedFiles.add(contextTarget.path);
            deleteSelected();
            hideContextMenu();
        }

        function openContextItemInApp() {
            if (!contextTarget) return;
            fetch(`/api/open?path=${encodeURIComponent(contextTarget.path)}`);
            hideContextMenu();
        }

        function openSelectedFiles() {
            selectedFiles.forEach(path => {
                fetch(`/api/open?path=${encodeURIComponent(path)}`);
            });
            hideContextMenu();
        }

        function selectAllFiles() {
            filteredFiles.forEach(f => selectedFiles.add(f.path));
            renderGrid();
        }

        // Right-click event handlers
        document.querySelector('.grid-container').addEventListener('contextmenu', (e) => {
            const tile = e.target.closest('.tile');

            if (tile) {
                const path = tile.dataset.path;
                const idx = Array.from(document.querySelectorAll('.tile')).indexOf(tile);
                const file = filteredFiles[idx];

                // If multiple selected and right-clicking on a selected item
                if (selectedFiles.size > 1 && selectedFiles.has(path)) {
                    showContextMenu(e, { type: 'multi' });
                } else {
                    showContextMenu(e, {
                        type: file.is_dir ? 'folder' : 'file',
                        path: path,
                        idx: idx
                    });
                }
            } else {
                // Empty space
                showContextMenu(e, { type: 'empty' });
            }
        });

        // Hide context menu on click outside or escape
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.context-menu')) {
                hideContextMenu();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                hideContextMenu();
            }
            // Cmd+Shift+N for new folder
            if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'n') {
                e.preventDefault();
                createNewFolder();
            }
            // Cmd+R for refresh
            if ((e.metaKey || e.ctrlKey) && e.key === 'r' && !e.target.matches('input')) {
                e.preventDefault();
                navigate(currentPath, false);
            }
        });

        // =====================
        // INIT
        // =====================
        // Initialize sidebar mode from localStorage
        document.getElementById('mode-grouped').classList.toggle('active', sidebarMode === 'grouped');
        document.getElementById('mode-flat').classList.toggle('active', sidebarMode === 'flat');

        navigate(INITIAL_PATH);
        checkHistoryStatus();
    </script>
</body>
</html>
'''


class FileExplorerHandler(SimpleHTTPRequestHandler):

    def check_auth(self) -> bool:
        """Check if request has valid auth token."""
        global AUTH_TOKEN, AUTH_VERIFIED
        if not AUTH_VERIFIED:
            return False

        # Check cookie for auth token
        cookies = self.headers.get('Cookie', '')
        for cookie in cookies.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                if name == 'fe_auth' and value == AUTH_TOKEN:
                    return True
        return False

    def send_auth_required(self):
        """Send 401 response requiring authentication."""
        self.send_response(401)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        html = '''<!DOCTYPE html>
<html><head><title>Authentication Required</title>
<style>
body { font-family: -apple-system, sans-serif; background: #1e1e1e; color: #fff;
       display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
.box { text-align: center; padding: 40px; background: #2d2d2d; border-radius: 12px; }
h1 { font-size: 1.5rem; margin-bottom: 1rem; }
p { color: #888; margin-bottom: 1.5rem; }
button { padding: 12px 24px; font-size: 1rem; background: #0a84ff; color: white;
         border: none; border-radius: 8px; cursor: pointer; }
button:hover { background: #409cff; }
</style></head>
<body><div class="box">
<h1>File Explorer</h1>
<p>Touch ID or Face ID required to access files</p>
<button onclick="location.href='/auth'">Authenticate</button>
</div></body></html>'''
        self.wfile.write(html.encode())

    def do_GET(self):
        global AUTH_TOKEN, AUTH_VERIFIED
        path = unquote(self.path)

        # Handle authentication endpoint
        if path == '/auth':
            if request_biometric_auth("File Explorer wants to access your files"):
                AUTH_VERIFIED = True
                AUTH_TOKEN = generate_auth_token()
                self.send_response(302)
                self.send_header('Set-Cookie', f'fe_auth={AUTH_TOKEN}; Path=/; HttpOnly; SameSite=Strict')
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''<!DOCTYPE html><html><head><title>Auth Failed</title>
<style>body{font-family:-apple-system,sans-serif;background:#1e1e1e;color:#fff;
display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}
.box{text-align:center;padding:40px;background:#2d2d2d;border-radius:12px;}
h1{color:#ff453a;}</style></head><body><div class="box">
<h1>Authentication Failed</h1><p>Please try again</p>
<button onclick="location.href='/auth'" style="padding:12px 24px;font-size:1rem;
background:#0a84ff;color:white;border:none;border-radius:8px;cursor:pointer;">
Retry</button></div></body></html>''')
            return

        # Check auth for all other endpoints
        if not self.check_auth():
            self.send_auth_required()
            return

        if path == '/' or path == '/index.html':
            # Inject the initial browse root path
            html = HTML_TEMPLATE.replace('{{BROWSE_ROOT}}', str(BROWSE_ROOT))
            self.send_html(html)
        elif path.startswith('/api/list'):
            qs = parse_qs(path.split('?')[1]) if '?' in path else {}
            dir_path = qs.get('path', [''])[0]
            self.send_json(self.list_dir(dir_path))
        elif path.startswith('/api/folder-preview'):
            qs = parse_qs(path.split('?')[1]) if '?' in path else {}
            dir_path = qs.get('path', [''])[0]
            limit = int(qs.get('limit', ['10'])[0])
            depth = int(qs.get('depth', ['1'])[0])
            self.send_json(self.get_folder_preview(dir_path, limit=limit, depth=depth))
        elif path.startswith('/api/preview'):
            qs = parse_qs(path.split('?')[1]) if '?' in path else {}
            file_path = qs.get('path', [''])[0]
            self.send_preview(file_path)
        elif path.startswith('/api/content'):
            qs = parse_qs(path.split('?')[1]) if '?' in path else {}
            file_path = qs.get('path', [''])[0]
            self.send_content(file_path)
        elif path.startswith('/api/open'):
            qs = parse_qs(path.split('?')[1]) if '?' in path else {}
            file_path = qs.get('path', [''])[0]
            self.open_file(file_path)
        elif path.startswith('/file/'):
            self.serve_file(path[5:])
        else:
            self.send_error(404)

    def do_POST(self):
        # Check auth for all POST requests
        if not self.check_auth():
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error": "Authentication required"}')
            return

        path = unquote(self.path)
        content_type = self.headers.get('Content-Type', '')

        # Handle multipart file uploads
        if path == '/api/upload' and 'multipart/form-data' in content_type:
            self.handle_upload()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body) if body else {}

        if path == '/api/paste':
            self.handle_paste(data)
        elif path == '/api/delete':
            self.handle_delete(data)
        elif path == '/api/undo':
            self.handle_undo(data)
        elif path == '/api/redo':
            self.handle_redo(data)
        elif path == '/api/history-status':
            self.handle_history_status(data)
        elif path == '/api/create-folder':
            self.handle_create_folder(data)
        elif path == '/api/rename':
            self.handle_rename(data)
        elif path == '/api/duplicate':
            self.handle_duplicate(data)
        elif path == '/api/compress':
            self.handle_compress(data)
        elif path == '/api/move-items':
            self.handle_move_items(data)
        elif path == '/api/open-with-app':
            self.handle_open_with_app(data)
        elif path == '/api/create-folder-with-items':
            self.handle_create_folder_with_items(data)
        elif path == '/api/extract-archive':
            self.handle_extract_archive(data)
        else:
            self.send_error(404)

    def list_dir(self, path_str):
        # Validate path is within BROWSE_ROOT
        dir_path = validate_path(path_str)
        if dir_path is None:
            return []  # Path outside allowed root

        if not dir_path.exists() or not dir_path.is_dir():
            return []

        items = []
        try:
            for item in dir_path.iterdir():
                if item.is_dir() and item.name in EXCLUDE_DIRS:
                    continue
                if item.name.startswith('.') and item.name not in ('.env', '.gitignore', '.Trash'):
                    continue

                try:
                    stat = item.stat()
                    size = stat.st_size if item.is_file() else 0
                    modified = stat.st_mtime
                except:
                    size = 0
                    modified = 0

                item_count = 0
                if item.is_dir():
                    try:
                        item_count = len([x for x in item.iterdir()
                                         if not x.name.startswith('.')
                                         and x.name not in EXCLUDE_DIRS])
                    except:
                        pass

                ext = item.suffix.lstrip('.').lower() if item.is_file() else ''

                # Use absolute path for free navigation
                items.append({
                    'name': item.name,
                    'path': str(item),
                    'is_dir': item.is_dir(),
                    'ext': ext,
                    'size': size,
                    'size_fmt': format_size(size),
                    'modified': self.format_time(modified),
                    'item_count': item_count,
                    'preview_type': get_preview_type(ext) if item.is_file() else 'folder',
                })
        except PermissionError:
            pass

        return items

    def get_folder_preview(self, path_str, limit=10, depth=1):
        """Get preview items for a folder with optional recursive depth."""
        dir_path = validate_path(path_str)
        if dir_path is None:
            return []  # Path outside allowed root
        if not dir_path.exists() or not dir_path.is_dir():
            return []

        items = []
        try:
            all_items = []
            for item in dir_path.iterdir():
                if item.name.startswith('.'):
                    continue
                if item.is_dir() and item.name in EXCLUDE_DIRS:
                    continue

                ext = item.suffix.lstrip('.').lower() if item.is_file() else ''
                preview_type = get_preview_type(ext) if item.is_file() else 'folder'

                # Priority: images > code > video > folders > others
                priority = 0
                if preview_type == 'image':
                    priority = 4
                elif preview_type == 'code':
                    priority = 3
                elif preview_type == 'video':
                    priority = 2
                elif item.is_dir():
                    priority = 1

                all_items.append((priority, item, ext, preview_type))

            all_items.sort(key=lambda x: (-x[0], x[1].name))

            for priority, item, ext, preview_type in all_items[:limit]:
                entry = {
                    'name': item.name,
                    'path': str(item),  # Use absolute path
                    'is_dir': item.is_dir(),
                    'ext': ext,
                    'preview_type': preview_type,
                }

                # Add code preview
                if preview_type == 'code':
                    try:
                        with open(item, 'r', encoding='utf-8', errors='replace') as f:
                            entry['preview_content'] = f.read(200)
                    except:
                        entry['preview_content'] = ''

                # Recursively get children for folders
                if item.is_dir() and depth > 1:
                    entry['children'] = self.get_folder_preview(str(item), limit=4, depth=depth-1)

                items.append(entry)

        except PermissionError:
            pass

        return items

    def format_time(self, ts):
        if ts == 0:
            return '-'
        from datetime import datetime
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    def send_preview(self, path_str):
        """Send truncated preview for tile."""
        file_path = validate_path(path_str)
        if file_path is None:
            self.send_json({'error': 'Access denied'})
            return
        if not file_path.exists() or not file_path.is_file():
            self.send_json({'error': 'Not found'})
            return

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(2000)  # First 2KB for preview
            self.send_json({'content': content})
        except:
            self.send_json({'error': 'Cannot read'})

    def send_content(self, path_str):
        """Send full file content."""
        file_path = validate_path(path_str)
        if file_path is None:
            self.send_json({'error': 'Access denied'})
            return
        if not file_path.exists() or not file_path.is_file():
            self.send_json({'error': 'Not found'})
            return

        try:
            max_size = MAX_CONTENT_SIZE
            size = file_path.stat().st_size
            if size > max_size:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(max_size)
                content += f"\n\n... [Truncated - file is {format_size(size)}]"
            else:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            self.send_json({'content': content})
        except Exception as e:
            self.send_json({'error': str(e)})

    def open_file(self, path_str):
        file_path = validate_path(path_str)
        if file_path is None:
            self.send_json({'error': 'Access denied'})
            return
        if not file_path.exists():
            self.send_json({'error': 'Not found'})
            return
        try:
            subprocess.run(['open', str(file_path)], check=True)
            self.send_json({'ok': True})
        except subprocess.CalledProcessError as e:
            self.send_json({'error': str(e)})

    def serve_file(self, path_str):
        file_path = validate_path(path_str)
        if file_path is None:
            self.send_error(403, "Access denied")
            return
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404)
            return

        mime = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
        size = file_path.stat().st_size

        # Limit file size for security
        if size > MAX_SERVE_SIZE:
            self.send_error(413, f"File too large (max {MAX_SERVE_SIZE // 1024 // 1024}MB)")
            return

        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(size))
        self.end_headers()

        # Stream file in chunks to avoid memory issues
        chunk_size = 64 * 1024  # 64KB chunks
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                self.wfile.write(chunk)

    def handle_paste(self, data):
        """Handle copy/cut paste operation with undo support."""
        global ACTION_HISTORY, REDO_STACK

        files = data.get('files', [])
        target = data.get('target', '/')
        operation = data.get('operation', 'copy')

        # Validate target path
        target_dir = validate_path(target)
        if target_dir is None:
            self.send_json({'success': False, 'error': 'Access denied'})
            return
        if not target_dir.exists():
            self.send_json({'success': False, 'error': 'Target folder not found'})
            return

        count = 0
        errors = []
        action_items = []  # Track for undo

        for file_path in files:
            src = validate_path(file_path)
            if src is None:
                errors.append(f'{file_path}: access denied')
                continue
            if not src.exists():
                errors.append(f'{src.name}: not found')
                continue

            dst = target_dir / src.name

            # Handle name conflicts
            if dst.exists():
                base = dst.stem
                ext = dst.suffix
                counter = 1
                while dst.exists():
                    dst = target_dir / f"{base} ({counter}){ext}"
                    counter += 1

            try:
                if operation == 'cut':
                    shutil.move(str(src), str(dst))
                    action_items.append({'type': 'move', 'src': str(src), 'dst': str(dst)})
                else:
                    if src.is_dir():
                        shutil.copytree(str(src), str(dst))
                    else:
                        shutil.copy2(str(src), str(dst))
                    # Store source for redo capability
                    action_items.append({'type': 'copy', 'src': str(src), 'dst': str(dst)})
                count += 1
            except Exception as e:
                errors.append(f'{src.name}: {str(e)}')

        # Record action for undo
        if action_items:
            ACTION_HISTORY.append({'action': 'paste', 'operation': operation, 'items': action_items})
            REDO_STACK.clear()  # Clear redo when new action is performed

        self.send_json({
            'success': len(errors) == 0,
            'count': count,
            'errors': errors
        })

    def handle_delete(self, data):
        """Handle file deletion - moves to trash for undo support."""
        global ACTION_HISTORY, REDO_STACK, TRASH_DIR

        # Ensure trash directory exists
        if TRASH_DIR is None or not TRASH_DIR.exists():
            self.send_json({'success': False, 'error': 'Trash directory not available'})
            return

        files = data.get('files', [])
        count = 0
        errors = []
        action_items = []

        for file_path in files:
            path = validate_path(file_path)
            if path is None:
                errors.append(f'{file_path}: access denied')
                continue
            if not path.exists():
                continue

            # Create unique trash path with timestamp
            timestamp = int(time.time() * 1000)
            trash_name = f"{timestamp}_{path.name}"
            trash_path = TRASH_DIR / trash_name

            try:
                shutil.move(str(path), str(trash_path))
                action_items.append({
                    'original': str(path),  # Store absolute path
                    'trash': str(trash_path)  # Store absolute path
                })
                count += 1
            except Exception as e:
                errors.append(f'{path.name}: {str(e)}')

        # Record action for undo
        if action_items:
            ACTION_HISTORY.append({'action': 'delete', 'items': action_items})
            REDO_STACK.clear()

        self.send_json({
            'success': len(errors) == 0,
            'count': count,
            'errors': errors
        })

    def handle_undo(self, _data):
        """Undo the last action."""
        global ACTION_HISTORY, REDO_STACK

        if not ACTION_HISTORY:
            self.send_json({'success': False, 'error': 'Nothing to undo', 'canUndo': False, 'canRedo': len(REDO_STACK) > 0})
            return

        action = ACTION_HISTORY.pop()

        try:
            if action['action'] == 'delete':
                # Restore from trash
                for item in action['items']:
                    trash_path = validate_path(item['trash'])
                    original_path = validate_path(item['original'])
                    if trash_path is None or original_path is None:
                        continue
                    if trash_path.exists():
                        # Ensure parent directory exists
                        original_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(trash_path), str(original_path))

            elif action['action'] == 'paste':
                for item in action['items']:
                    if item['type'] == 'copy':
                        # Delete the copied file
                        dst_path = validate_path(item['dst'])
                        if dst_path is None:
                            continue
                        if dst_path.exists():
                            if dst_path.is_dir():
                                shutil.rmtree(str(dst_path))
                            else:
                                dst_path.unlink()
                    elif item['type'] == 'move':
                        # Move back to original location
                        dst_path = validate_path(item['dst'])
                        src_path = validate_path(item['src'])
                        if dst_path is None or src_path is None:
                            continue
                        if dst_path.exists():
                            src_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(dst_path), str(src_path))

            REDO_STACK.append(action)
            self.send_json({
                'success': True,
                'message': f"Undid {action['action']}",
                'canUndo': len(ACTION_HISTORY) > 0,
                'canRedo': True
            })

        except Exception as e:
            # Put action back if undo failed
            ACTION_HISTORY.append(action)
            self.send_json({'success': False, 'error': str(e), 'canUndo': True, 'canRedo': len(REDO_STACK) > 0})

    def handle_redo(self, _data):
        """Redo the last undone action."""
        global ACTION_HISTORY, REDO_STACK

        if not REDO_STACK:
            self.send_json({'success': False, 'error': 'Nothing to redo', 'canUndo': len(ACTION_HISTORY) > 0, 'canRedo': False})
            return

        action = REDO_STACK.pop()

        try:
            if action['action'] == 'delete':
                # Delete again (move to trash)
                if TRASH_DIR is None:
                    REDO_STACK.append(action)
                    self.send_json({'success': False, 'error': 'Trash not available', 'canUndo': len(ACTION_HISTORY) > 0, 'canRedo': True})
                    return

                new_items = []
                for item in action['items']:
                    orig = item['original']
                    original_path = validate_path(orig)
                    if original_path is None:
                        continue
                    if original_path.exists():
                        timestamp = int(time.time() * 1000)
                        trash_name = f"{timestamp}_{original_path.name}"
                        trash_path = TRASH_DIR / trash_name
                        shutil.move(str(original_path), str(trash_path))
                        new_items.append({
                            'original': item['original'],
                            'trash': str(trash_path)
                        })
                action['items'] = new_items

            elif action['action'] == 'paste':
                for item in action['items']:
                    if item['type'] == 'copy':
                        # Re-copy the file from stored source
                        src_path = validate_path(item.get('src', ''))
                        dst_path = validate_path(item.get('dst', ''))
                        if src_path is None or dst_path is None:
                            continue
                        if src_path.exists() and not dst_path.exists():
                            if src_path.is_dir():
                                shutil.copytree(str(src_path), str(dst_path))
                            else:
                                shutil.copy2(str(src_path), str(dst_path))
                    elif item['type'] == 'move':
                        src_path = validate_path(item['src'])
                        dst_path = validate_path(item['dst'])
                        if src_path is None or dst_path is None:
                            continue
                        if src_path.exists():
                            dst_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(src_path), str(dst_path))

            ACTION_HISTORY.append(action)
            self.send_json({
                'success': True,
                'message': f"Redid {action['action']}",
                'canUndo': True,
                'canRedo': len(REDO_STACK) > 0
            })

        except Exception as e:
            REDO_STACK.append(action)
            self.send_json({'success': False, 'error': str(e), 'canUndo': len(ACTION_HISTORY) > 0, 'canRedo': True})

    def handle_history_status(self, _data):
        """Get current undo/redo status."""
        global ACTION_HISTORY, REDO_STACK
        self.send_json({
            'canUndo': len(ACTION_HISTORY) > 0,
            'canRedo': len(REDO_STACK) > 0,
            'undoCount': len(ACTION_HISTORY),
            'redoCount': len(REDO_STACK)
        })

    def handle_create_folder(self, data):
        """Create a new folder."""
        global ACTION_HISTORY, REDO_STACK

        parent_path = data.get('path', '')
        name = data.get('name', 'New Folder')

        # Sanitize folder name
        name = name.strip()
        if not name or '/' in name or '\\' in name:
            self.send_json({'success': False, 'error': 'Invalid folder name'})
            return

        parent_dir = validate_path(parent_path)
        if parent_dir is None:
            self.send_json({'success': False, 'error': 'Access denied'})
            return
        if not parent_dir.exists() or not parent_dir.is_dir():
            self.send_json({'success': False, 'error': 'Parent folder not found'})
            return

        new_folder = parent_dir / name

        # Handle name conflicts
        if new_folder.exists():
            counter = 1
            while new_folder.exists():
                new_folder = parent_dir / f"{name} ({counter})"
                counter += 1

        try:
            new_folder.mkdir(parents=False, exist_ok=False)
            ACTION_HISTORY.append({
                'action': 'create_folder',
                'path': str(new_folder)
            })
            REDO_STACK.clear()
            self.send_json({
                'success': True,
                'path': str(new_folder),
                'name': new_folder.name
            })
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)})

    def handle_rename(self, data):
        """Rename a file or folder."""
        global ACTION_HISTORY, REDO_STACK

        old_path = data.get('path', '')
        new_name = data.get('newName', data.get('name', '')).strip()

        if not new_name or '/' in new_name or '\\' in new_name:
            self.send_json({'success': False, 'error': 'Invalid name'})
            return

        path = validate_path(old_path)
        if path is None:
            self.send_json({'success': False, 'error': 'Access denied'})
            return
        if not path.exists():
            self.send_json({'success': False, 'error': 'Not found'})
            return

        new_path = path.parent / new_name

        if new_path.exists():
            self.send_json({'success': False, 'error': 'Name already exists'})
            return

        try:
            path.rename(new_path)
            ACTION_HISTORY.append({
                'action': 'rename',
                'old_path': str(path),
                'new_path': str(new_path)
            })
            REDO_STACK.clear()
            self.send_json({
                'success': True,
                'path': str(new_path),
                'name': new_name
            })
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)})

    def handle_duplicate(self, data):
        """Duplicate a file or folder."""
        global ACTION_HISTORY, REDO_STACK

        file_path = data.get('path', '')

        path = validate_path(file_path)
        if path is None:
            self.send_json({'success': False, 'error': 'Access denied'})
            return
        if not path.exists():
            self.send_json({'success': False, 'error': 'Not found'})
            return

        # Generate unique name
        base = path.stem
        ext = path.suffix
        parent = path.parent
        counter = 1
        new_path = parent / f"{base} copy{ext}"
        while new_path.exists():
            new_path = parent / f"{base} copy {counter}{ext}"
            counter += 1

        try:
            if path.is_dir():
                shutil.copytree(str(path), str(new_path))
            else:
                shutil.copy2(str(path), str(new_path))

            ACTION_HISTORY.append({
                'action': 'duplicate',
                'original': str(path),
                'copy': str(new_path)
            })
            REDO_STACK.clear()
            self.send_json({
                'success': True,
                'path': str(new_path),
                'name': new_path.name
            })
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)})

    def handle_compress(self, data):
        """Compress files/folders to a zip archive."""
        global ACTION_HISTORY, REDO_STACK
        import zipfile

        files = data.get('files', [])
        if not files:
            self.send_json({'success': False, 'error': 'No files to compress'})
            return

        # Validate all paths first
        validated = []
        for f in files:
            p = validate_path(f)
            if p is None:
                self.send_json({'success': False, 'error': f'Access denied: {f}'})
                return
            if not p.exists():
                self.send_json({'success': False, 'error': f'Not found: {f}'})
                return
            validated.append(p)

        # Determine archive name and location
        if len(validated) == 1:
            archive_name = f"{validated[0].stem}.zip"
            archive_path = validated[0].parent / archive_name
        else:
            archive_name = "Archive.zip"
            archive_path = validated[0].parent / archive_name

        # Handle name conflicts
        counter = 1
        while archive_path.exists():
            if len(validated) == 1:
                archive_path = validated[0].parent / f"{validated[0].stem} ({counter}).zip"
            else:
                archive_path = validated[0].parent / f"Archive ({counter}).zip"
            counter += 1

        try:
            with zipfile.ZipFile(str(archive_path), 'w', zipfile.ZIP_DEFLATED) as zf:
                for p in validated:
                    if p.is_dir():
                        for root, dirs, filenames in os.walk(str(p)):
                            # Skip hidden directories
                            dirs[:] = [d for d in dirs if not d.startswith('.')]
                            for fname in filenames:
                                if not fname.startswith('.'):
                                    file_path = Path(root) / fname
                                    arcname = p.name + '/' + str(file_path.relative_to(p))
                                    zf.write(str(file_path), arcname)
                    else:
                        zf.write(str(p), p.name)

            ACTION_HISTORY.append({
                'action': 'compress',
                'files': [str(p) for p in validated],
                'archive': str(archive_path)
            })
            REDO_STACK.clear()
            self.send_json({
                'success': True,
                'path': str(archive_path),
                'name': archive_path.name
            })
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)})

    def handle_move_items(self, data):
        """Move multiple items to a destination folder."""
        global ACTION_HISTORY, REDO_STACK

        paths = data.get('paths', [])
        destination = data.get('destination', '')

        if not paths:
            self.send_json({'success': False, 'error': 'No items to move'})
            return

        dest_path = validate_path(destination)
        if dest_path is None:
            self.send_json({'success': False, 'error': 'Invalid destination'})
            return

        if not dest_path.is_dir():
            self.send_json({'success': False, 'error': 'Destination is not a folder'})
            return

        moved = []
        errors = []

        for item_path in paths:
            src = validate_path(item_path)
            if src is None:
                errors.append(f'Access denied: {item_path}')
                continue

            if not src.exists():
                errors.append(f'Not found: {item_path}')
                continue

            new_path = dest_path / src.name
            # Handle name conflicts
            counter = 1
            original_stem = src.stem
            suffix = src.suffix
            while new_path.exists():
                new_path = dest_path / f"{original_stem} ({counter}){suffix}"
                counter += 1

            try:
                shutil.move(str(src), str(new_path))
                moved.append({'from': str(src), 'to': str(new_path)})
            except Exception as e:
                errors.append(f'Move failed for {src.name}: {str(e)}')

        if moved:
            ACTION_HISTORY.append({
                'action': 'move_items',
                'items': moved
            })
            REDO_STACK.clear()

        self.send_json({
            'success': len(errors) == 0,
            'moved': len(moved),
            'errors': errors
        })

    def handle_open_with_app(self, data):
        """Open items with a specified app."""
        import subprocess

        paths = data.get('paths', [])
        app = data.get('app', '')

        if not paths or not app:
            self.send_json({'success': False, 'error': 'Missing paths or app'})
            return

        app_path = validate_path(app)
        if app_path is None or not app_path.exists():
            self.send_json({'success': False, 'error': 'Invalid app'})
            return

        validated_paths = []
        for p in paths:
            validated = validate_path(p)
            if validated and validated.exists():
                validated_paths.append(str(validated))

        if not validated_paths:
            self.send_json({'success': False, 'error': 'No valid files'})
            return

        try:
            subprocess.Popen(['open', '-a', str(app_path)] + validated_paths)
            self.send_json({'success': True})
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)})

    def handle_create_folder_with_items(self, data):
        """Create a new folder and move items into it."""
        global ACTION_HISTORY, REDO_STACK

        folder_name = data.get('folderName', '').strip()
        parent_path = data.get('parentPath', '')
        item_paths = data.get('itemPaths', [])

        if not folder_name:
            self.send_json({'success': False, 'error': 'Folder name required'})
            return

        parent = validate_path(parent_path)
        if parent is None or not parent.is_dir():
            self.send_json({'success': False, 'error': 'Invalid parent path'})
            return

        # Sanitize folder name
        folder_name = folder_name.replace('/', '').replace('\\', '').strip()
        if not folder_name:
            self.send_json({'success': False, 'error': 'Invalid folder name'})
            return

        new_folder = parent / folder_name
        # Handle name conflicts
        counter = 1
        original_name = folder_name
        while new_folder.exists():
            new_folder = parent / f"{original_name} ({counter})"
            counter += 1

        try:
            new_folder.mkdir(parents=False, exist_ok=False)
        except Exception as e:
            self.send_json({'success': False, 'error': f'Cannot create folder: {str(e)}'})
            return

        moved = []
        errors = []

        for item_path in item_paths:
            src = validate_path(item_path)
            if src is None or not src.exists():
                errors.append(f'Invalid: {item_path}')
                continue

            new_path = new_folder / src.name
            # Handle name conflicts within new folder
            c = 1
            orig_stem = src.stem
            suffix = src.suffix
            while new_path.exists():
                new_path = new_folder / f"{orig_stem} ({c}){suffix}"
                c += 1

            try:
                shutil.move(str(src), str(new_path))
                moved.append({'from': str(src), 'to': str(new_path)})
            except Exception as e:
                errors.append(f'Move failed for {src.name}: {str(e)}')

        ACTION_HISTORY.append({
            'action': 'create_folder_with_items',
            'folder': str(new_folder),
            'items': moved
        })
        REDO_STACK.clear()

        self.send_json({
            'success': len(errors) == 0,
            'folder': str(new_folder),
            'moved': len(moved),
            'errors': errors
        })

    def handle_extract_archive(self, data):
        """Extract a compressed archive to a folder."""
        global ACTION_HISTORY, REDO_STACK

        archive_path = data.get('archivePath', '')
        target_dir = data.get('targetDir', '')  # Optional, defaults to same folder

        src = validate_path(archive_path)
        if src is None or not src.is_file():
            self.send_json({'success': False, 'error': 'Invalid archive path'})
            return

        # Determine target directory
        if target_dir:
            dest = validate_path(target_dir)
            if dest is None or not dest.is_dir():
                self.send_json({'success': False, 'error': 'Invalid target directory'})
                return
        else:
            dest = src.parent

        # Create extraction folder (archive name without extension)
        extract_name = src.stem
        extract_folder = dest / extract_name
        counter = 1
        original_name = extract_name
        while extract_folder.exists():
            extract_folder = dest / f"{original_name} ({counter})"
            counter += 1

        suffix = src.suffix.lower()

        try:
            extract_folder.mkdir(parents=False, exist_ok=False)

            if suffix == '.zip':
                with zipfile.ZipFile(str(src), 'r') as zf:
                    zf.extractall(str(extract_folder))
            elif suffix in ('.tar', '.gz', '.tgz', '.bz2', '.xz'):
                # Handle various tar formats
                mode = 'r'
                if suffix == '.gz' or suffix == '.tgz':
                    mode = 'r:gz'
                elif suffix == '.bz2':
                    mode = 'r:bz2'
                elif suffix == '.xz':
                    mode = 'r:xz'
                with tarfile.open(str(src), mode) as tf:
                    tf.extractall(str(extract_folder))
            else:
                # Try using system unzip/tar as fallback
                extract_folder.rmdir()  # Remove empty folder
                self.send_json({'success': False, 'error': f'Unsupported archive format: {suffix}'})
                return

            ACTION_HISTORY.append({
                'action': 'extract_archive',
                'archive': str(src),
                'folder': str(extract_folder)
            })
            REDO_STACK.clear()

            self.send_json({
                'success': True,
                'extractedTo': str(extract_folder)
            })

        except zipfile.BadZipFile:
            if extract_folder.exists():
                shutil.rmtree(str(extract_folder), ignore_errors=True)
            self.send_json({'success': False, 'error': 'Invalid or corrupted ZIP file'})
        except tarfile.TarError as e:
            if extract_folder.exists():
                shutil.rmtree(str(extract_folder), ignore_errors=True)
            self.send_json({'success': False, 'error': f'TAR error: {str(e)}'})
        except Exception as e:
            if extract_folder.exists():
                shutil.rmtree(str(extract_folder), ignore_errors=True)
            self.send_json({'success': False, 'error': f'Extraction failed: {str(e)}'})

    def handle_upload(self):
        """Handle multipart file uploads from external drag-drop."""
        global ACTION_HISTORY, REDO_STACK

        content_type = self.headers.get('Content-Type', '')
        content_length = int(self.headers.get('Content-Length', 0))

        # Extract boundary from content-type
        boundary = None
        for part in content_type.split(';'):
            part = part.strip()
            if part.startswith('boundary='):
                boundary = part[9:].strip('"')
                break

        if not boundary:
            self.send_json({'success': False, 'error': 'No boundary in multipart request'})
            return

        body = self.rfile.read(content_length)
        boundary_bytes = ('--' + boundary).encode()

        # Parse multipart data
        parts = body.split(boundary_bytes)
        target_path = str(BROWSE_ROOT)
        uploaded_files = []
        errors = []

        for part in parts:
            if not part or part == b'--' or part == b'--\r\n':
                continue

            # Split headers from content
            if b'\r\n\r\n' not in part:
                continue

            header_section, content = part.split(b'\r\n\r\n', 1)
            headers_str = header_section.decode('utf-8', errors='ignore')

            # Parse content-disposition
            filename = None
            name = None
            for line in headers_str.split('\r\n'):
                if line.lower().startswith('content-disposition:'):
                    for item in line.split(';'):
                        item = item.strip()
                        if item.startswith('filename="'):
                            filename = item[10:-1]
                        elif item.startswith("filename="):
                            filename = item[9:].strip('"')
                        elif item.startswith('name="'):
                            name = item[6:-1]
                        elif item.startswith("name="):
                            name = item[5:].strip('"')

            # Handle form field for target path
            if name == 'targetPath' and not filename:
                target_path = content.rstrip(b'\r\n--').decode('utf-8', errors='ignore').strip()
                continue

            # Handle file
            if filename:
                # Remove trailing boundary markers from content
                if content.endswith(b'\r\n'):
                    content = content[:-2]

                # Validate target path
                target = validate_path(target_path)
                if target is None or not target.is_dir():
                    errors.append(f'Invalid target directory for {filename}')
                    continue

                # Sanitize filename
                safe_name = filename.replace('/', '').replace('\\', '').strip()
                if not safe_name:
                    errors.append(f'Invalid filename: {filename}')
                    continue

                dest_file = target / safe_name
                # Handle name conflicts
                counter = 1
                original_stem = Path(safe_name).stem
                suffix = Path(safe_name).suffix
                while dest_file.exists():
                    dest_file = target / f"{original_stem} ({counter}){suffix}"
                    counter += 1

                try:
                    with open(dest_file, 'wb') as f:
                        f.write(content)
                    uploaded_files.append(str(dest_file))
                except Exception as e:
                    errors.append(f'Failed to save {filename}: {str(e)}')

        if uploaded_files:
            ACTION_HISTORY.append({
                'action': 'upload',
                'files': uploaded_files
            })
            REDO_STACK.clear()

        self.send_json({
            'success': len(errors) == 0,
            'uploaded': len(uploaded_files),
            'files': uploaded_files,
            'errors': errors
        })

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

    def log_message(self, format: str, *args):  # noqa: A002
        """Suppress HTTP request logging."""
        pass


def main():
    global BROWSE_ROOT, TRASH_DIR

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default=str(PROJECT_ROOT))
    parser.add_argument('--port', type=int, default=DEFAULT_PORT)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()

    BROWSE_ROOT = Path(args.path).resolve()

    if not BROWSE_ROOT.exists():
        print(f"Error: {BROWSE_ROOT} does not exist")
        sys.exit(1)

    # Initialize trash directory for undo support
    TRASH_DIR = BROWSE_ROOT / '.file_explorer_trash'
    TRASH_DIR.mkdir(exist_ok=True)

    print(f"File Explorer (with Touch ID / Face ID)")
    print(f"  Root: {BROWSE_ROOT}")
    print(f"  Trash: {TRASH_DIR}")
    print(f"  URL: http://localhost:{args.port}")
    print(f"  Auth: Touch ID / Face ID required on first access")
    print(f"\nPress Ctrl+C to stop\n")

    if not args.no_browser:
        webbrowser.open(f'http://localhost:{args.port}')

    # Bind to localhost only for security
    server = HTTPServer(('127.0.0.1', args.port), FileExplorerHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == '__main__':
    main()
