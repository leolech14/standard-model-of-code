#!/usr/bin/env python3
"""
Minimal File Viewer - Compact popup with grouped sidebar + preview
Click outside or ESC to close
"""

import os
import sys
import json
import mimetypes
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import webbrowser

PORT = 8001
BROWSE_ROOT = os.path.expanduser("~")

if len(sys.argv) > 1:
    BROWSE_ROOT = os.path.abspath(sys.argv[1])

def get_preview_type(ext):
    ext = ext.lower().lstrip('.')
    image_exts = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico', 'heic', 'avif', 'tiff'}
    video_exts = {'mp4', 'webm', 'mov', 'avi', 'mkv', 'm4v', 'ogv'}
    audio_exts = {'mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac', 'wma'}
    code_exts = {'py', 'js', 'ts', 'jsx', 'tsx', 'html', 'css', 'scss', 'json', 'yaml', 'yml',
                 'xml', 'sql', 'sh', 'bash', 'zsh', 'go', 'rs', 'rb', 'php', 'java', 'c', 'cpp',
                 'h', 'hpp', 'swift', 'kt', 'scala', 'r', 'lua', 'pl', 'md', 'txt', 'log', 'toml',
                 'ini', 'cfg', 'conf', 'env', 'gitignore', 'dockerfile', 'makefile'}
    if ext in image_exts: return 'image'
    if ext in video_exts: return 'video'
    if ext in audio_exts: return 'audio'
    if ext == 'pdf': return 'pdf'
    if ext in code_exts: return 'code'
    return 'binary'

class FileViewerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = HTML_TEMPLATE.replace('{{BROWSE_ROOT}}', BROWSE_ROOT)
            self.wfile.write(html.encode())
        elif path == '/api/list':
            self.handle_list(parse_qs(parsed.query))
        elif path == '/api/content':
            self.handle_content(parse_qs(parsed.query))
        elif path.startswith('/file/'):
            self.handle_file(path[6:])
        else:
            self.send_error(404)

    def handle_list(self, params):
        dir_path = params.get('path', [BROWSE_ROOT])[0]
        dir_path = os.path.abspath(unquote(dir_path))

        if not dir_path.startswith(BROWSE_ROOT):
            self.send_json({'error': 'Access denied'}, 403)
            return

        try:
            items = []
            for item in sorted(Path(dir_path).iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if item.name.startswith('.'): continue
                ext = item.suffix.lstrip('.').lower() if item.is_file() else ''
                stat = item.stat()
                items.append({
                    'name': item.name,
                    'path': str(item),
                    'is_dir': item.is_dir(),
                    'ext': ext,
                    'size': stat.st_size if item.is_file() else 0,
                    'size_fmt': self.format_size(stat.st_size) if item.is_file() else '',
                    'preview_type': get_preview_type(ext) if item.is_file() else 'folder',
                    'item_count': len(list(item.iterdir())) if item.is_dir() else 0
                })
            self.send_json({'files': items, 'path': dir_path})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_content(self, params):
        file_path = params.get('path', [''])[0]
        file_path = os.path.abspath(unquote(file_path))

        if not file_path.startswith(BROWSE_ROOT):
            self.send_json({'error': 'Access denied'}, 403)
            return

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(100000)  # Limit to 100KB
            self.send_json({'content': content})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_file(self, file_path):
        file_path = os.path.abspath(unquote('/' + file_path))
        if not file_path.startswith(BROWSE_ROOT):
            self.send_error(403)
            return

        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', mime_type or 'application/octet-stream')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(404)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024: return f"{size:.0f} {unit}" if unit == 'B' else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def log_message(self, format, *args): pass

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Viewer</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --bg: #0d0d0f;
            --panel-bg: #1a1a1f;
            --sidebar-bg: #141418;
            --border: #2a2a30;
            --text: #e4e4e7;
            --text-dim: #71717a;
            --accent: #3b82f6;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
            background: var(--bg);
            color: var(--text);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            -webkit-font-smoothing: antialiased;
        }

        /* Backdrop - click to close */
        .backdrop {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(4px);
            cursor: pointer;
        }

        /* Main popup container */
        .popup {
            position: relative;
            display: flex;
            width: 900px;
            height: 600px;
            max-width: 90vw;
            max-height: 85vh;
            background: var(--panel-bg);
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
            overflow: hidden;
            z-index: 10;
        }

        /* Sidebar */
        .sidebar {
            width: 220px;
            min-width: 220px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .sidebar-header {
            padding: 12px 14px;
            border-bottom: 1px solid var(--border);
            font-size: 11px;
            font-weight: 600;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .sidebar-header .path {
            font-weight: 400;
            text-transform: none;
            letter-spacing: 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .sidebar-content {
            flex: 1;
            overflow-y: auto;
            padding: 6px;
        }

        /* Type Drawers */
        .drawer {
            margin-bottom: 2px;
        }

        .drawer-header {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.15s;
        }

        .drawer-header:hover {
            background: rgba(255,255,255,0.05);
        }

        .drawer.open .drawer-header {
            background: rgba(255,255,255,0.03);
        }

        .drawer-icon {
            width: 16px;
            height: 16px;
            opacity: 0.7;
        }

        .drawer-icon svg {
            width: 100%;
            height: 100%;
            fill: none;
            stroke: currentColor;
            stroke-width: 1.5;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .drawer-label {
            flex: 1;
            font-size: 12px;
            font-weight: 500;
        }

        .drawer-count {
            font-size: 10px;
            color: var(--text-dim);
            background: rgba(255,255,255,0.08);
            padding: 1px 6px;
            border-radius: 8px;
        }

        .drawer-chevron {
            font-size: 10px;
            color: var(--text-dim);
            transition: transform 0.15s;
        }

        .drawer.open .drawer-chevron {
            transform: rotate(90deg);
        }

        .drawer-content {
            display: none;
            padding: 2px 0 4px 0;
        }

        .drawer.open .drawer-content {
            display: block;
        }

        /* File items */
        .file-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px 6px 28px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.1s;
        }

        .file-item:hover {
            background: rgba(255,255,255,0.05);
        }

        .file-item.active {
            background: var(--accent);
        }

        .file-item .file-icon {
            width: 14px;
            height: 14px;
            opacity: 0.6;
        }

        .file-item.active .file-icon {
            opacity: 1;
        }

        .file-item .file-icon svg {
            width: 100%;
            height: 100%;
            fill: none;
            stroke: currentColor;
            stroke-width: 1.5;
        }

        .file-item .file-name {
            flex: 1;
            font-size: 12px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .file-item .file-size {
            font-size: 10px;
            color: var(--text-dim);
        }

        .file-item.active .file-size {
            color: rgba(255,255,255,0.7);
        }

        /* Preview area */
        .preview {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .preview-header {
            padding: 10px 16px;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .preview-header .file-meta {
            font-size: 11px;
            color: var(--text-dim);
        }

        .preview-content {
            flex: 1;
            overflow: auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .preview-content img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }

        .preview-content video,
        .preview-content audio {
            max-width: 100%;
            max-height: 100%;
        }

        .preview-content iframe {
            width: 100%;
            height: 100%;
            border: none;
        }

        .preview-content pre {
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 16px;
            overflow: auto;
            font-size: 12px;
            line-height: 1.5;
            background: transparent;
        }

        .preview-content code {
            font-family: 'SF Mono', 'Fira Code', monospace;
        }

        .preview-content .markdown {
            padding: 20px;
            width: 100%;
            height: 100%;
            overflow: auto;
            font-size: 14px;
            line-height: 1.6;
        }

        .preview-content .markdown h1, .preview-content .markdown h2 {
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
            margin-bottom: 16px;
        }

        .preview-content .markdown pre {
            background: rgba(0,0,0,0.3);
            border-radius: 6px;
            padding: 12px;
        }

        .preview-empty {
            text-align: center;
            color: var(--text-dim);
        }

        .preview-empty .icon {
            font-size: 48px;
            margin-bottom: 12px;
            opacity: 0.3;
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
    </style>
</head>
<body>
    <div class="backdrop" onclick="closePopup()"></div>
    <div class="popup">
        <div class="sidebar">
            <div class="sidebar-header">
                <span class="path" id="current-path"></span>
            </div>
            <div class="sidebar-content" id="sidebar"></div>
        </div>
        <div class="preview">
            <div class="preview-header">
                <span id="preview-title">Select a file</span>
                <span class="file-meta" id="preview-meta"></span>
            </div>
            <div class="preview-content" id="preview">
                <div class="preview-empty">
                    <div class="icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/>
                            <polyline points="14 2 14 8 20 8"/>
                        </svg>
                    </div>
                    <div>Select a file to preview</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const BROWSE_ROOT = '{{BROWSE_ROOT}}';
        let currentPath = BROWSE_ROOT;
        let files = [];
        let activeFile = null;

        // Icons
        const ICONS = {
            folder: '<svg viewBox="0 0 24 24"><path d="M3 7v10c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V9c0-1.1-.9-2-2-2h-6l-2-2H5c-1.1 0-2 .9-2 2z"/></svg>',
            file: '<svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/><polyline points="14 2 14 8 20 8"/></svg>',
            image: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
            video: '<svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><polygon points="10 9 15 12 10 15"/></svg>',
            audio: '<svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
            code: '<svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
            pdf: '<svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6z"/><path d="M9 13h2v4H9zM13 11h2v6h-2z"/></svg>',
            data: '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
            archive: '<svg viewBox="0 0 24 24"><path d="M21 8v13H3V8"/><path d="M1 3h22v5H1z"/><path d="M10 12h4"/></svg>',
        };

        const TYPE_GROUPS = {
            folder: { label: 'Folders', icon: 'folder', order: 0 },
            image: { label: 'Images', icon: 'image', order: 1 },
            video: { label: 'Videos', icon: 'video', order: 2 },
            audio: { label: 'Audio', icon: 'audio', order: 3 },
            code: { label: 'Code', icon: 'code', order: 4 },
            pdf: { label: 'PDFs', icon: 'pdf', order: 5 },
            binary: { label: 'Other', icon: 'file', order: 6 }
        };

        function getFileGroup(f) {
            if (f.is_dir) return 'folder';
            return f.preview_type || 'binary';
        }

        function closePopup() {
            window.close();
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closePopup();
        });

        async function loadDirectory(path) {
            currentPath = path;
            document.getElementById('current-path').textContent = path.split('/').pop() || 'Root';

            try {
                const res = await fetch(`/api/list?path=${encodeURIComponent(path)}`);
                const data = await res.json();
                files = data.files || [];
                renderSidebar();
            } catch (e) {
                console.error('Failed to load:', e);
            }
        }

        function renderSidebar() {
            const sidebar = document.getElementById('sidebar');

            // Group files by type
            const groups = {};
            files.forEach(f => {
                const type = getFileGroup(f);
                if (!groups[type]) groups[type] = [];
                groups[type].push(f);
            });

            // Sort and render
            const sortedTypes = Object.keys(groups).sort((a, b) =>
                (TYPE_GROUPS[a]?.order || 99) - (TYPE_GROUPS[b]?.order || 99)
            );

            const drawerStates = JSON.parse(localStorage.getItem('viewerDrawers') || '{}');

            sidebar.innerHTML = sortedTypes.map(type => {
                const group = TYPE_GROUPS[type] || TYPE_GROUPS.binary;
                const items = groups[type];
                const isOpen = drawerStates[type] !== undefined ? drawerStates[type] : (type === 'folder');

                const fileItems = items.map(f => `
                    <div class="file-item ${activeFile?.path === f.path ? 'active' : ''}"
                         onclick="${f.is_dir ? `loadDirectory('${f.path}')` : `selectFile('${f.path}')`}">
                        <span class="file-icon">${ICONS[f.is_dir ? 'folder' : (group.icon || 'file')]}</span>
                        <span class="file-name">${f.name}</span>
                        <span class="file-size">${f.is_dir ? f.item_count : f.size_fmt}</span>
                    </div>
                `).join('');

                return `
                    <div class="drawer ${isOpen ? 'open' : ''}" data-type="${type}">
                        <div class="drawer-header" onclick="toggleDrawer('${type}')">
                            <span class="drawer-icon">${ICONS[group.icon]}</span>
                            <span class="drawer-label">${group.label}</span>
                            <span class="drawer-count">${items.length}</span>
                            <span class="drawer-chevron">›</span>
                        </div>
                        <div class="drawer-content">${fileItems}</div>
                    </div>
                `;
            }).join('');
        }

        function toggleDrawer(type) {
            const drawer = document.querySelector(`.drawer[data-type="${type}"]`);
            if (drawer) {
                const isOpen = drawer.classList.toggle('open');
                const states = JSON.parse(localStorage.getItem('viewerDrawers') || '{}');
                states[type] = isOpen;
                localStorage.setItem('viewerDrawers', JSON.stringify(states));
            }
        }

        async function selectFile(path) {
            const file = files.find(f => f.path === path);
            if (!file) return;

            activeFile = file;
            renderSidebar(); // Update active state

            document.getElementById('preview-title').textContent = file.name;
            document.getElementById('preview-meta').textContent = file.size_fmt;

            const preview = document.getElementById('preview');
            const type = file.preview_type;
            const ext = file.ext?.toLowerCase();

            if (type === 'image') {
                preview.innerHTML = `<img src="/file${file.path}">`;
            }
            else if (type === 'video') {
                preview.innerHTML = `<video src="/file${file.path}" controls autoplay></video>`;
            }
            else if (type === 'audio') {
                preview.innerHTML = `<audio src="/file${file.path}" controls autoplay></audio>`;
            }
            else if (type === 'pdf') {
                preview.innerHTML = `<iframe src="/file${file.path}"></iframe>`;
            }
            else if (type === 'code') {
                try {
                    const res = await fetch(`/api/content?path=${encodeURIComponent(file.path)}`);
                    const data = await res.json();

                    if (ext === 'md') {
                        preview.innerHTML = `<div class="markdown">${marked.parse(data.content)}</div>`;
                    } else {
                        const lang = ext || 'plaintext';
                        const highlighted = hljs.highlight(data.content, {language: lang, ignoreIllegals: true}).value;
                        preview.innerHTML = `<pre><code>${highlighted}</code></pre>`;
                    }
                } catch (e) {
                    preview.innerHTML = '<div class="preview-empty">Failed to load file</div>';
                }
            }
            else {
                preview.innerHTML = `
                    <div class="preview-empty">
                        <div class="icon">${ICONS.file}</div>
                        <div>${file.name}</div>
                        <div style="margin-top:8px;font-size:12px">${file.size_fmt}</div>
                    </div>
                `;
            }
        }

        // Init
        loadDirectory(BROWSE_ROOT);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print(f"Starting File Viewer on http://localhost:{PORT}")
    print(f"Browsing: {BROWSE_ROOT}")
    webbrowser.open(f"http://localhost:{PORT}")
    HTTPServer(('127.0.0.1', PORT), FileViewerHandler).serve_forever()
