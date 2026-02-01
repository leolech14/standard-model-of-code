"""File operations service."""

import os
import shutil
import time
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

from middleware.path_validator import validate_path, validate_paths


class FileService:
    """Service for file system operations."""

    @staticmethod
    def list_directory(path: Path) -> List[dict]:
        """List contents of a directory."""
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")

        items = []
        try:
            for entry in path.iterdir():
                try:
                    stat = entry.stat()
                    items.append({
                        'path': str(entry),
                        'name': entry.name,
                        'size': stat.st_size if entry.is_file() else 0,
                        'type': FileService._get_file_type(entry),
                        'modified': stat.st_mtime,
                        'is_directory': entry.is_dir()
                    })
                except (PermissionError, OSError):
                    # Skip files we can't access
                    continue
        except PermissionError:
            raise PermissionError(f"Permission denied: {path}")

        # Sort: directories first, then alphabetically
        items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
        return items

    @staticmethod
    def _get_file_type(path: Path) -> str:
        """Get file type from extension."""
        if path.is_dir():
            return 'directory'
        ext = path.suffix.lower().lstrip('.')
        return ext if ext else 'file'

    @staticmethod
    def create_folder(parent: Path, name: str) -> Path:
        """Create a new folder."""
        new_folder = parent / name

        if new_folder.exists():
            raise FileExistsError(f"Folder already exists: {new_folder}")

        new_folder.mkdir(parents=False)
        return new_folder

    @staticmethod
    def rename(path: Path, new_name: str) -> Path:
        """Rename a file or folder."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        new_path = path.parent / new_name

        if new_path.exists():
            raise FileExistsError(f"File already exists: {new_path}")

        path.rename(new_path)
        return new_path

    @staticmethod
    def delete(paths: List[Path], to_trash: bool = True) -> List[str]:
        """Delete files or folders.

        Args:
            paths: List of paths to delete
            to_trash: If True, move to trash instead of permanent delete

        Returns:
            List of deleted paths
        """
        deleted = []

        for path in paths:
            if not path.exists():
                continue

            if to_trash:
                # Move to system trash (macOS)
                try:
                    import subprocess
                    subprocess.run(
                        ['osascript', '-e', f'tell app "Finder" to delete POSIX file "{path}"'],
                        check=True,
                        capture_output=True
                    )
                    deleted.append(str(path))
                except subprocess.CalledProcessError:
                    # Fallback to permanent delete
                    FileService._permanent_delete(path)
                    deleted.append(str(path))
            else:
                FileService._permanent_delete(path)
                deleted.append(str(path))

        return deleted

    @staticmethod
    def _permanent_delete(path: Path) -> None:
        """Permanently delete a file or folder."""
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    @staticmethod
    def copy(sources: List[Path], destination: Path) -> List[str]:
        """Copy files/folders to destination."""
        if not destination.is_dir():
            raise NotADirectoryError(f"Destination must be a directory: {destination}")

        copied = []
        for source in sources:
            if not source.exists():
                continue

            dest_path = destination / source.name

            # Handle name conflicts
            if dest_path.exists():
                dest_path = FileService._unique_name(dest_path)

            if source.is_dir():
                shutil.copytree(source, dest_path)
            else:
                shutil.copy2(source, dest_path)

            copied.append(str(dest_path))

        return copied

    @staticmethod
    def move(sources: List[Path], destination: Path) -> List[str]:
        """Move files/folders to destination."""
        if not destination.is_dir():
            raise NotADirectoryError(f"Destination must be a directory: {destination}")

        moved = []
        for source in sources:
            if not source.exists():
                continue

            dest_path = destination / source.name

            # Handle name conflicts
            if dest_path.exists():
                dest_path = FileService._unique_name(dest_path)

            shutil.move(str(source), str(dest_path))
            moved.append(str(dest_path))

        return moved

    @staticmethod
    def _unique_name(path: Path) -> Path:
        """Generate a unique name for a file/folder."""
        base = path.stem
        ext = path.suffix
        parent = path.parent
        counter = 1

        while True:
            new_name = f"{base} ({counter}){ext}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    @staticmethod
    def get_metadata(path: Path) -> dict:
        """Get detailed metadata for a file."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        stat = path.stat()

        return {
            'path': str(path),
            'name': path.name,
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'is_directory': path.is_dir(),
            'permissions': oct(stat.st_mode)[-3:],
            'owner': str(stat.st_uid),
            'mime_type': FileService._get_mime_type(path)
        }

    @staticmethod
    def _get_mime_type(path: Path) -> str:
        """Get MIME type for a file."""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(path))
        return mime_type or 'application/octet-stream'
