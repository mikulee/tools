from moviepy.editor import VideoFileClip
from tqdm import tqdm
import os

def extract_audio(video_path, output_audio_path):
    # Add data folder prefix to input path
    input_path = video_path
    
    print(f"Loading video: {input_path}")
    
    try:
        # Load the video file with specific ffmpeg parameters to handle MKV files better
        video = VideoFileClip(input_path, audio_fps=44100, audio_buffersize=20000, audio_nbytes=4)
        
        # Check if audio exists
        if video.audio is None:
            print(f"Error: No audio track found in {input_path}")
            return False
        
        # Extract the audio
        audio = video.audio
        
        # Get duration for progress bar
        duration = video.duration
        
        # Create a callback function for the progress bar
        def progress_callback(current_time):
            # Update the progress bar
            progress_bar.update(current_time - progress_bar.n)
        
        print(f"Extracting audio to: {output_audio_path}")
        # Initialize progress bar
        with tqdm(total=duration, unit="sec", desc="Extracting Audio") as progress_bar:
            # Save the audio to a file with progress callback
            audio.write_audiofile(output_audio_path, 
                                  codec='libmp3lame',  # Specify codec explicitly
                                  logger=None,  # Disable moviepy's own progress output
                                  progress_callback=progress_callback)
        
        print("Extraction complete!")
        # Close the clips to free resources
        audio.close()
        video.close()
        return True
        
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        # If there was an error, try using ffmpeg directly as a fallback
        if os.path.exists(input_path):
            try_ffmpeg_direct(input_path, output_audio_path)
        return False

def try_ffmpeg_direct(input_path, output_audio_path):
    """Try to use ffmpeg directly if MoviePy fails"""
    import subprocess
    try:
        print("Attempting direct FFmpeg extraction...")
        cmd = f'ffmpeg -i "{input_path}" -vn -acodec libmp3lame -y "{output_audio_path}"'
        subprocess.call(cmd, shell=True)
        if os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 0:
            print(f"FFmpeg direct extraction complete: {output_audio_path}")
            return True
        else:
            print("FFmpeg direct extraction failed")
            return False
    except Exception as e:
        print(f"FFmpeg direct extraction error: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    import sys
    print(sys.path)  # Add this to your script temporarily to debug
    
    if len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        print(f"Processing {input_file} to {output_file}")
        extract_audio(input_file, output_file)
    else:
        print("Usage: python audio_extract.py input_file.mkv output_file.mp3")