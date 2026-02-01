"""File preview service."""

from pathlib import Path
from typing import Optional, Tuple

# Language detection by extension
LANG_MAP = {
    'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'tsx': 'tsx',
    'jsx': 'jsx', 'json': 'json', 'yaml': 'yaml', 'yml': 'yaml',
    'md': 'markdown', 'html': 'html', 'css': 'css', 'scss': 'scss',
    'sql': 'sql', 'sh': 'bash', 'bash': 'bash', 'zsh': 'zsh',
    'rs': 'rust', 'go': 'go', 'java': 'java', 'kt': 'kotlin',
    'swift': 'swift', 'c': 'c', 'cpp': 'cpp', 'h': 'cpp',
    'rb': 'ruby', 'php': 'php', 'lua': 'lua', 'r': 'r',
    'toml': 'toml', 'ini': 'ini', 'xml': 'xml', 'svg': 'svg',
    'dockerfile': 'dockerfile', 'makefile': 'makefile',
}

# Text file extensions
TEXT_EXTENSIONS = {
    'txt', 'log', 'csv', 'tsv', 'diff', 'patch', 'rst',
    'gitignore', 'gitattributes', 'editorconfig', 'env',
    'npmrc', 'nvmrc', 'babelrc', 'eslintrc', 'prettierrc',
}

# Binary preview types
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'ico', 'tiff', 'svg'}
VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi', 'mkv', 'm4v'}
AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac'}


class PreviewService:
    """Service for generating file previews."""

    MAX_PREVIEW_LINES = 100
    MAX_PREVIEW_SIZE = 1024 * 100  # 100KB

    @staticmethod
    def get_preview(path: Path) -> dict:
        """Get preview for a file.

        Returns dict with:
            - path: file path
            - type: preview type (code, text, image, video, audio, binary)
            - preview: content preview (for text/code)
            - language: detected language (for code)
            - line_count: total lines (for text/code)
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.is_dir():
            return {
                'path': str(path),
                'type': 'directory',
                'preview': None,
                'item_count': len(list(path.iterdir()))
            }

        ext = path.suffix.lower().lstrip('.')
        preview_type = PreviewService._get_preview_type(ext)

        result = {
            'path': str(path),
            'type': preview_type,
            'preview': None,
            'language': None,
            'line_count': None
        }

        if preview_type in ('code', 'text'):
            content, line_count = PreviewService._read_text_preview(path)
            result['preview'] = content
            result['line_count'] = line_count
            if preview_type == 'code':
                result['language'] = LANG_MAP.get(ext, 'plaintext')

        elif preview_type == 'image':
            # For images, just return the path - frontend will display
            result['mime_type'] = f'image/{ext}'

        elif preview_type in ('video', 'audio'):
            result['mime_type'] = PreviewService._get_media_type(ext)

        return result

    @staticmethod
    def _get_preview_type(ext: str) -> str:
        """Determine preview type from extension."""
        if ext in LANG_MAP:
            return 'code'
        if ext in TEXT_EXTENSIONS:
            return 'text'
        if ext in IMAGE_EXTENSIONS:
            return 'image'
        if ext in VIDEO_EXTENSIONS:
            return 'video'
        if ext in AUDIO_EXTENSIONS:
            return 'audio'
        if ext == 'pdf':
            return 'pdf'
        return 'binary'

    @staticmethod
    def _read_text_preview(path: Path) -> Tuple[str, int]:
        """Read text preview from file.

        Returns:
            Tuple of (preview_content, total_line_count)
        """
        try:
            # Check file size first
            if path.stat().st_size > PreviewService.MAX_PREVIEW_SIZE:
                # Read only first N bytes
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(PreviewService.MAX_PREVIEW_SIZE)
                lines = content.split('\n')
                preview = '\n'.join(lines[:PreviewService.MAX_PREVIEW_LINES])
                return preview + '\n... (truncated)', -1  # Unknown total

            # Read entire file
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            total_lines = len(lines)
            preview_lines = lines[:PreviewService.MAX_PREVIEW_LINES]
            preview = ''.join(preview_lines)

            if total_lines > PreviewService.MAX_PREVIEW_LINES:
                preview += f'\n... ({total_lines - PreviewService.MAX_PREVIEW_LINES} more lines)'

            return preview, total_lines

        except Exception as e:
            return f"Error reading file: {str(e)}", 0

    @staticmethod
    def _get_media_type(ext: str) -> str:
        """Get MIME type for media files."""
        if ext in VIDEO_EXTENSIONS:
            return f'video/{ext}'
        if ext in AUDIO_EXTENSIONS:
            return f'audio/{ext}'
        return 'application/octet-stream'

    @staticmethod
    def get_full_content(path: Path) -> str:
        """Get full file content (for editing)."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.is_dir():
            raise IsADirectoryError(f"Cannot read directory: {path}")

        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error reading file: {str(e)}")
