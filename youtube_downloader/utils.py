import re
from pathlib import Path
from typing import Optional

def validate_youtube_url(url: str) -> bool:
    """Validate if the given URL is a valid YouTube URL."""
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    return bool(re.match(youtube_regex, url))

def ensure_output_dir(directory: Optional[str] = None) -> Path:
    """Ensure output directory exists, create if it doesn't."""
    output_dir = Path(directory or './downloads')
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)
