from setuptools import setup, find_packages

setup(
    name="tools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yt-dlp>=2023.0",
        "ffmpeg-python>=0.2.0",
        "click>=8.0.0",
        "tqdm>=4.0.0",
    ],
    entry_points={
        'console_scripts': [
            'yt-download=tools.youtube_downloader.cli:main',
        ],
    },
)
