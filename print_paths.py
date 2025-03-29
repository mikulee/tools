import os
import sys
import site
import shutil
import subprocess

print("=== Python Path Information ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

print("\n=== System Path (sys.path) ===")
for i, path in enumerate(sys.path):
    print(f"{i+1}. {path}")

print("\n=== Environment PATH Variable ===")
path_var = os.environ.get('PATH', '')
path_items = path_var.split(os.pathsep)
for i, path in enumerate(path_items):
    print(f"{i+1}. {path}")

print("\n=== Site Packages Directories ===")
print(f"User site-packages: {site.getusersitepackages()}")
print("Global site-packages:")
for path in site.getsitepackages():
    print(f"  {path}")

print("\n=== Python Module Search Path ===")
import importlib.util
def find_module_path(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return f"Module '{module_name}' not found"
    return spec.origin

print(f"moviepy path: {find_module_path('moviepy')}")
try:
    print(f"moviepy.editor path: {find_module_path('moviepy.editor')}")
except ImportError:
    print("moviepy.editor cannot be found")

print("\n=== FFmpeg Information ===")
# Check if ffmpeg is in PATH
ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    print(f"FFmpeg found in PATH: {ffmpeg_path}")
    try:
        # Get FFmpeg version
        result = subprocess.run(["ffmpeg", "-version"], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        version_line = result.stdout.split('\n')[0]
        print(f"FFmpeg version: {version_line}")
    except subprocess.SubprocessError as e:
        print(f"Error getting FFmpeg version: {e}")
else:
    print("FFmpeg not found in PATH")
    
    # Search for ffmpeg in common installation locations
    common_locations = [
        "C:\\Program Files\\ffmpeg\\bin",
        "C:\\Program Files (x86)\\ffmpeg\\bin",
        "C:\\ffmpeg\\bin",
        os.path.expanduser("~\\ffmpeg\\bin"),
        # Add Chocolatey default location
        "C:\\ProgramData\\chocolatey\\bin"
    ]
    
    print("\nSearching for FFmpeg in common locations:")
    for location in common_locations:
        potential_path = os.path.join(location, "ffmpeg.exe")
        if os.path.exists(potential_path):
            print(f"FFmpeg found at: {potential_path}")
        else:
            print(f"Not found at: {location}")
            
    # Check if it might be in the PATH but with different casing or extension
    for path_item in path_items:
        if os.path.exists(path_item):
            try:
                files = os.listdir(path_item)
                for file in files:
                    if file.lower().startswith("ffmpeg"):
                        print(f"Possible FFmpeg found: {os.path.join(path_item, file)}")
            except (PermissionError, OSError):
                # Skip directories we don't have permission to read
                pass