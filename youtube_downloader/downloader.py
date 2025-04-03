import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any
from .utils import validate_youtube_url, ensure_output_dir, sanitize_filename

class YouTubeDownloader:
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = ensure_output_dir(output_dir)

    def _get_ydl_opts(self, quality: str = 'best', format_: str = 'mp4',
                      audio_only: bool = False) -> Dict[str, Any]:
        format_selection = 'bestaudio' if audio_only else f'bestvideo[height<={quality}]+bestaudio'
        if quality == 'best':
            format_selection = 'bestaudio' if audio_only else 'bestvideo+bestaudio'

        return {
            'format': format_selection,
            'merge_output_format': format_,
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'quiet': False,
            'no_warnings': True,
        }

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        if d['status'] == 'downloading':
            print(f"\rDownloading... {d.get('_percent_str', '0%')}", end='')
        elif d['status'] == 'finished':
            print("\nDownload complete! Converting...")

    def download(self, url: str, quality: str = 'best',
                format_: str = 'mp4', audio_only: bool = False) -> bool:
        """Download video from YouTube URL."""
        if not validate_youtube_url(url):
            raise ValueError("Invalid YouTube URL")

        try:
            with yt_dlp.YoutubeDL(self._get_ydl_opts(quality, format_, audio_only)) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return False
