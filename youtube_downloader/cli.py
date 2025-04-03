import click
from .downloader import YouTubeDownloader
from .helpers import list_available_formats, get_best_quality, clean_downloads

@click.command()
@click.argument('url', required=False)
@click.option('--quality', default='best', help='Video quality (e.g., 1080, 720, best)')
@click.option('--output', '-o', help='Output directory')
@click.option('--format', '-f', 'format_', default='mp4', help='Output format')
@click.option('--audio-only', is_flag=True, help='Download audio only')
@click.option('--list-formats', is_flag=True, help='List available formats')
@click.option('--clean', is_flag=True, help='Clean partial downloads')
def main(url: str, quality: str, output: str, format_: str, 
         audio_only: bool, list_formats: bool, clean: bool):
    """Download YouTube videos with optional quality selection."""
    try:
        if clean:
            clean_downloads(output)
            click.echo("Cleaned partial downloads")
            return 0

        if not url:
            click.echo("URL is required unless using --clean")
            return 1

        if list_formats:
            formats = list_available_formats(url)
            for fmt in formats:
                click.echo(f"Format: {fmt.get('format_id')} - "
                         f"{fmt.get('height', 'audio')}p - {fmt.get('ext')}")
            return 0

        if quality == 'best':
            quality = get_best_quality(url)
            click.echo(f"Selected best quality: {quality}")

        downloader = YouTubeDownloader(output)
        if downloader.download(url, quality, format_, audio_only):
            click.echo("Download completed successfully!")
        else:
            click.echo("Download failed.")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        return 1
    return 0

if __name__ == '__main__':
    main()
