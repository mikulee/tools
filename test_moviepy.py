# test_moviepy.py
print("Starting test...")
try:
    import moviepy
    print(f"MoviePy base package imported successfully. Version: {moviepy.__version__}")
    
    print("Attempting to import VideoFileClip...")
    from moviepy.editor import VideoFileClip
    print("VideoFileClip imported successfully!")
except Exception as e:
    print(f"Error: {e}")
    
    import sys
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Show installed packages
    import pkg_resources
    print("\nInstalled packages:")
    for pkg in pkg_resources.working_set:
        if 'movie' in pkg.key:
            print(f"  {pkg.key}=={pkg.version}")