import subprocess
import sys
import os

print("Testing ffmpeg...")

# Set PATH and LD_LIBRARY_PATH for paketo apt layer
os.environ["PATH"] = "/layers/paketo-buildpacks_apt/apt/usr/bin:" + os.environ.get("PATH", "")
os.environ["LD_LIBRARY_PATH"] = "/layers/paketo-buildpacks_apt/apt/usr/lib/x86_64-linux-gnu:" + os.environ.get("LD_LIBRARY_PATH", "")

result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)

if result.returncode == 0:
    print(result.stdout)
    print("✓ ffmpeg is installed and working")
else:
    print(result.stderr)
    print("✗ ffmpeg not found")
    sys.exit(1)
