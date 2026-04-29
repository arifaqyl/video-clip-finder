import subprocess
import sys

# Test if ffmpeg is installed
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
    print("✓ ffmpeg is installed")
    print(result.stdout.split('\n')[0])
except FileNotFoundError:
    print("✗ ffmpeg not found")
    sys.exit(1)