import yt_dlp
from typing import Dict, List, Optional
from pathlib import Path

def get_video_info(url: str) -> Dict:
    """Get video metadata without downloading."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def list_available_formats(url: str) -> List[Dict]:
    """List all available formats for a video."""
    info = get_video_info(url)
    return info.get('formats', [])

def get_best_quality(url: str) -> str:
    """Get the best available quality for a video."""
    formats = list_available_formats(url)
    max_height = 0
    for fmt in formats:
        height = fmt.get('height', 0)
        if height > max_height:
            max_height = height
    return str(max_height) + 'p'

def clean_downloads(directory: Optional[str] = None, pattern: str = "*.part") -> None:
    """Clean up partial downloads from the directory."""
    dir_path = Path(directory or './downloads')
    for partial in dir_path.glob(pattern):
        partial.unlink()
