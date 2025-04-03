import shutil
import os
from pathlib import Path
import tempfile

def package_youtube_downloader():
    """Package YouTube downloader into a zip file."""
    # Setup paths
    base_dir = Path(__file__).parent
    temp_dir = Path(tempfile.mkdtemp())
    package_dir = temp_dir / "youtube_downloader"
    
    try:
        # Create package directory
        package_dir.mkdir(parents=True)
        
        # Files to copy
        files_to_copy = [
            "youtube_downloader/__init__.py",
            "youtube_downloader/__main__.py",
            "youtube_downloader/cli.py",
            "youtube_downloader/downloader.py",
            "youtube_downloader/helpers.py",
            "youtube_downloader/utils.py",
            "PRD.md",
            "README.md",
        ]
        
        # Copy files
        for file in files_to_copy:
            src = base_dir / file
            dst = temp_dir / file
            if src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        
        # Create minimal requirements.txt
        reqs = [
            "yt-dlp>=2023.0",
            "ffmpeg-python>=0.2.0",
            "click>=8.0.0",
            "tqdm>=4.0.0",
        ]
        with open(temp_dir / "requirements.txt", "w") as f:
            f.write("\n".join(reqs))
        
        # Create zip file
        output_file = base_dir / "youtube_downloader.zip"
        shutil.make_archive(output_file.with_suffix(''), 'zip', temp_dir)
        
        print(f"Package created successfully: {output_file}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    package_youtube_downloader()
