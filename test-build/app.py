import subprocess
import sys
import os

print("Testing ffmpeg...")

result = subprocess.run(
    ["ffmpeg", "-version"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print(result.stdout)
    print("✓ ffmpeg is installed and working")
else:
    print(result.stderr)
    print("✗ ffmpeg not found")
    sys.exit(1)
