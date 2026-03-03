#!/usr/bin/env python3
"""
collider-live: Hot-reloading server for Collider HTML visualizations.

Watches a directory for .html files produced by `collider viz` and serves
the latest one with automatic browser refresh via SSE.

Usage:
    python server.py [WATCH_DIR] [--port PORT]

    WATCH_DIR defaults to .collider/ or /tmp/collider-self-analysis/
    PORT defaults to 4242
"""

import argparse
import asyncio
import hashlib
import mimetypes
import signal
import sys
import time
from pathlib import Path
from string import Template

# ---------------------------------------------------------------------------
# Minimal async HTTP server -- zero external dependencies
# ---------------------------------------------------------------------------

SSE_INJECT = b"""
<!-- collider-live reload -->
<script>
(function() {
  const es = new EventSource('/__live');
  es.onmessage = function(e) {
    if (e.data === 'reload') location.reload();
  };
  es.onerror = function() {
    setTimeout(() => location.reload(), 2000);
  };
})();
</script>
</head>
"""

INDEX_TEMPLATE = Template("""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>collider-live</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#0a0a0f; color:#e0e0e0; font-family:system-ui,-apple-system,sans-serif;
         display:flex; flex-direction:column; min-height:100vh; }
  h1 { padding:24px 32px 8px; font-size:1.4rem; color:#7dd3fc; }
  .subtitle { padding:0 32px 24px; color:#888; font-size:0.85rem; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr));
          gap:16px; padding:0 32px 32px; }
  a.card { display:block; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
           border-radius:12px; padding:20px; text-decoration:none; color:inherit;
           transition:all 0.2s; }
  a.card:hover { background:rgba(125,211,252,0.08); border-color:rgba(125,211,252,0.3);
                 transform:translateY(-2px); }
  .card .name { font-size:1.05rem; color:#7dd3fc; margin-bottom:6px; }
  .card .meta { font-size:0.8rem; color:#888; }
  .card .size { float:right; color:#666; }
  .empty { padding:32px; text-align:center; color:#666; }
  .badge { display:inline-block; background:rgba(125,211,252,0.15); color:#7dd3fc;
           padding:2px 8px; border-radius:4px; font-size:0.75rem; margin-left:8px; }
</style>
</head><body>
<h1>collider-live</h1>
<p class="subtitle">Watching: $watch_dir &middot; $count visualization(s)</p>
<div class="grid">$cards</div>
$empty
<!-- collider-live reload -->
<script>
(function() {
  const es = new EventSource('/__live');
  es.onmessage = function(e) { if (e.data === 'reload') location.reload(); };
  es.onerror = function() { setTimeout(() => location.reload(), 2000); };
})();
</script>
</body></html>
""")


def find_html_files(watch_dir: Path) -> list[Path]:
    """Find all .html files, sorted newest first."""
    files = sorted(watch_dir.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def human_size(nbytes: int) -> str:
    for unit in ("B", "KB", "MB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} GB"


def build_index(watch_dir: Path) -> bytes:
    files = find_html_files(watch_dir)
    cards = []
    for f in files:
        stat = f.stat()
        mod = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
        sz = human_size(stat.st_size)
        label = ""
        if f == files[0]:
            label = '<span class="badge">latest</span>'
        cards.append(
            f'<a class="card" href="/view/{f.name}">'
            f'<div class="name">{f.stem}{label}</div>'
            f'<div class="meta">{mod}<span class="size">{sz}</span></div>'
            f"</a>"
        )
    empty = (
        f'<div class="empty">No .html files found. Run: collider viz &lt;analysis.json&gt; --output {watch_dir}/viz.html</div>'
        if not files else ""
    )
    html = INDEX_TEMPLATE.safe_substitute(
        watch_dir=watch_dir,
        count=len(files),
        cards="\n".join(cards),
        empty=empty,
    )
    return html.encode()


def inject_reload(html_bytes: bytes) -> bytes:
    """Inject the SSE live-reload script before </head>."""
    if b"/__live" in html_bytes:
        return html_bytes  # already injected
    if b"</head>" in html_bytes:
        return html_bytes.replace(b"</head>", SSE_INJECT, 1)
    # fallback: prepend
    return SSE_INJECT + html_bytes


class FileWatcher:
    """Polls for file changes (no external deps needed)."""

    def __init__(self, watch_dir: Path, interval: float = 0.5):
        self.watch_dir = watch_dir
        self.interval = interval
        self._fingerprint = self._snapshot()
        self._subscribers: list[asyncio.Queue] = []

    def _snapshot(self) -> str:
        entries = []
        for p in sorted(self.watch_dir.glob("*.html")):
            try:
                s = p.stat()
                entries.append(f"{p.name}:{s.st_size}:{s.st_mtime_ns}")
            except OSError:
                pass
        return hashlib.md5("|".join(entries).encode()).hexdigest()

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        self._subscribers.discard(q) if hasattr(self._subscribers, 'discard') else (
            self._subscribers.remove(q) if q in self._subscribers else None
        )

    async def run(self):
        while True:
            await asyncio.sleep(self.interval)
            fp = self._snapshot()
            if fp != self._fingerprint:
                self._fingerprint = fp
                for q in list(self._subscribers):
                    await q.put("reload")


async def handle_request(reader, writer, watch_dir: Path, watcher: FileWatcher):
    try:
        request_line = await asyncio.wait_for(reader.readline(), timeout=5)
        if not request_line:
            writer.close()
            return

        line = request_line.decode("utf-8", errors="replace").strip()
        parts = line.split()
        if len(parts) < 2:
            writer.close()
            return

        method, path = parts[0], parts[1]

        # consume headers
        while True:
            header = await asyncio.wait_for(reader.readline(), timeout=5)
            if header in (b"\r\n", b"\n", b""):
                break

        if path == "/" or path == "/index.html":
            body = build_index(watch_dir)
            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Content-Type: text/html; charset=utf-8\r\n")
            writer.write(f"Content-Length: {len(body)}\r\n".encode())
            writer.write(b"Cache-Control: no-cache\r\n")
            writer.write(b"\r\n")
            writer.write(body)

        elif path.startswith("/view/"):
            filename = path[6:]  # strip /view/
            filepath = watch_dir / filename
            if filepath.exists() and filepath.suffix == ".html":
                raw = filepath.read_bytes()
                body = inject_reload(raw)
                writer.write(b"HTTP/1.1 200 OK\r\n")
                writer.write(b"Content-Type: text/html; charset=utf-8\r\n")
                writer.write(f"Content-Length: {len(body)}\r\n".encode())
                writer.write(b"Cache-Control: no-cache\r\n")
                writer.write(b"\r\n")
                writer.write(body)
            else:
                writer.write(b"HTTP/1.1 404 Not Found\r\n\r\nNot found")

        elif path == "/__live":
            # SSE endpoint
            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Content-Type: text/event-stream\r\n")
            writer.write(b"Cache-Control: no-cache\r\n")
            writer.write(b"Connection: keep-alive\r\n")
            writer.write(b"\r\n")
            await writer.drain()

            q = watcher.subscribe()
            try:
                while True:
                    msg = await q.get()
                    writer.write(f"data: {msg}\n\n".encode())
                    await writer.drain()
            except (ConnectionError, asyncio.CancelledError):
                pass
            finally:
                watcher.unsubscribe(q)
            return

        elif path == "/favicon.ico":
            writer.write(b"HTTP/1.1 204 No Content\r\n\r\n")

        else:
            # try serving static files from watch_dir
            filepath = watch_dir / path.lstrip("/")
            if filepath.exists() and filepath.is_file():
                body = filepath.read_bytes()
                ct = mimetypes.guess_type(str(filepath))[0] or "application/octet-stream"
                writer.write(b"HTTP/1.1 200 OK\r\n")
                writer.write(f"Content-Type: {ct}\r\n".encode())
                writer.write(f"Content-Length: {len(body)}\r\n".encode())
                writer.write(b"\r\n")
                writer.write(body)
            else:
                writer.write(b"HTTP/1.1 404 Not Found\r\n\r\nNot found")

        await writer.drain()
        writer.close()
    except (asyncio.TimeoutError, ConnectionError, BrokenPipeError):
        try:
            writer.close()
        except Exception:
            pass


async def main():
    parser = argparse.ArgumentParser(description="collider-live: hot-reload server for Collider viz")
    parser.add_argument("watch_dir", nargs="?", default=None, help="Directory to watch for .html files")
    parser.add_argument("--port", "-p", type=int, default=4242, help="Port (default: 4242)")
    args = parser.parse_args()

    # resolve watch dir
    if args.watch_dir:
        watch_dir = Path(args.watch_dir).resolve()
    else:
        # try .collider/ first, then /tmp/collider-self-analysis/
        candidates = [Path(".collider"), Path("/tmp/collider-self-analysis")]
        watch_dir = next((c for c in candidates if c.exists()), candidates[0])
        watch_dir = watch_dir.resolve()

    watch_dir.mkdir(parents=True, exist_ok=True)
    html_count = len(find_html_files(watch_dir))

    watcher = FileWatcher(watch_dir)
    asyncio.create_task(watcher.run())

    server = await asyncio.start_server(
        lambda r, w: handle_request(r, w, watch_dir, watcher),
        host="0.0.0.0",
        port=args.port,
    )

    print(f"\033[36m")
    print(f"  collider-live")
    print(f"  {'─' * 40}")
    print(f"  Watching:  {watch_dir}")
    print(f"  Files:     {html_count} HTML visualization(s)")
    print(f"  Server:    http://localhost:{args.port}")
    print(f"  {'─' * 40}")
    print(f"  Generate new viz:")
    print(f"    collider viz <analysis.json> -o {watch_dir}/viz.html")
    print(f"\033[0m")

    # graceful shutdown
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown(server)))

    async with server:
        await server.serve_forever()


async def _shutdown(server):
    print("\nShutting down...")
    server.close()
    await server.wait_closed()
    asyncio.get_event_loop().stop()


if __name__ == "__main__":
    asyncio.run(main())
