# Tools Collection

A comprehensive collection of productivity and development tools.

## Table of Contents

- [Installation](#installation)
- [YouTube Video Downloader](#youtube-video-downloader)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tools.git
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install FFmpeg if not already installed:
   - Windows: `choco install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

## YouTube Video Downloader

The `youtube_downloader` module provides a command-line utility for downloading YouTube videos with automatic audio/video stream handling.

### Features

- Download YouTube videos using URLs
- Automatic merging of separate audio/video streams
- Quality selection options
- Progress tracking
- FFmpeg integration for media processing

### Usage

```bash
# Basic usage (recommended)
python -m tools.youtube_downloader "https://youtube.com/watch?v=example"

# Download with quality selection
python -m tools.youtube_downloader "https://youtube.com/watch?v=example" --quality 1080p

# Download to specific directory
python -m tools.youtube_downloader "https://youtube.com/watch?v=example" --output ./my_videos

# Download audio only
python -m tools.youtube_downloader "https://youtube.com/watch?v=example" --audio-only
```

### Advanced Features

```bash
# List available formats
python -m tools.youtube_downloader "https://youtube.com/watch?v=example" --list-formats

# Clean partial downloads
python -m tools.youtube_downloader --clean

# Download with automatic best quality selection
python -m tools.youtube_downloader "https://youtube.com/watch?v=example" --quality best
```

### Packaging

To create a distributable package:

```bash
python package_yt_downloader.py
```

This will create `youtube_downloader.zip` containing all necessary files.

To use the packaged version:
1. Extract the zip file
2. Install requirements: `pip install -r requirements.txt`
3. Run the downloader: `python -m youtube_downloader <URL>`

## Project Structure

```
tools/
├── youtube_downloader/
│   ├── __init__.py      # Package initialization
│   ├── __main__.py      # Entry point for direct execution
│   ├── cli.py           # Command-line interface
│   ├── downloader.py    # Core downloading logic
│   ├── helpers.py       # Helper functions
│   └── utils.py         # Utility functions
├── README.md
├── PRD.md              # Product requirements document
└── requirements.txt    # Project dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
