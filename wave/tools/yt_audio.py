#!/usr/bin/env python3
"""
YouTube Audio Downloader

Downloads audio from YouTube videos and saves to ~/Downloads.
Adapted from PROJECT_ytpipe's DownloadService.

Usage:
    python yt_audio.py URL [--format wav] [--quality 320]
    python yt_audio.py URL1 URL2 URL3  # batch mode
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

DOWNLOADS = Path.home() / "Downloads"


def download_audio(url: str, fmt: str = "mp3", quality: str = "192") -> Path:
    """Download audio from a YouTube URL to ~/Downloads."""
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", fmt,
        "--audio-quality", f"{quality}K" if fmt == "mp3" else "0",
        "--no-playlist",
        "--no-update",
        "-o", str(DOWNLOADS / "%(title)s.%(ext)s"),
        url,
    ]

    print(f"Downloading: {url}")
    print(f"Format: {fmt.upper()}, Quality: {quality}kbps")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # Filter out the version warning noise
        errors = [
            line for line in result.stderr.splitlines()
            if not line.startswith("WARNING: Your yt-dlp version")
            and "strongly recommended" not in line
            and "suppress this warning" not in line
            and "installed yt-dlp" not in line
        ]
        if errors:
            print(f"Error: {chr(10).join(errors)}", file=sys.stderr)
            return None

    # Find the output file from yt-dlp output
    for line in (result.stdout + result.stderr).splitlines():
        if "Destination:" in line and DOWNLOADS.as_posix() in line:
            path = line.split("Destination: ", 1)[-1].strip()
            # yt-dlp may show intermediate format, find the final file
            pass

    # Scan Downloads for recently created file matching the format
    candidates = sorted(DOWNLOADS.glob(f"*.{fmt}"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        out = candidates[0]
        size_mb = out.stat().st_size / (1024 * 1024)
        print(f"Saved: {out.name} ({size_mb:.1f} MB)")
        return out

    print("Warning: download may have completed but file not found", file=sys.stderr)
    return None


def main():
    parser = argparse.ArgumentParser(description="Download YouTube audio to ~/Downloads")
    parser.add_argument("urls", nargs="+", help="YouTube URL(s)")
    parser.add_argument("--format", "-f", default="mp3", choices=["mp3", "wav", "flac", "m4a", "opus"],
                        help="Audio format (default: mp3)")
    parser.add_argument("--quality", "-q", default="192",
                        help="Audio quality/bitrate in kbps (default: 192)")
    args = parser.parse_args()

    results = []
    for url in args.urls:
        path = download_audio(url, fmt=args.format, quality=args.quality)
        if path:
            results.append(path)

    print(f"\n{len(results)}/{len(args.urls)} downloaded to {DOWNLOADS}")


if __name__ == "__main__":
    main()
