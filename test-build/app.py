import subprocess
import sys
import os

print("Testing ffmpeg...")

# Set PATH and LD_LIBRARY_PATH for paketo apt layer
os.environ["PATH"] = "/layers/paketo-buildpacks_apt/apt/usr/bin:" + os.environ.get("PATH", "")

# Dynamically find all lib directories in apt layer
import glob
lib_dirs = glob.glob("/layers/paketo-buildpacks_apt/apt/**/lib*", recursive=True)
lib_dirs = [d for d in lib_dirs if os.path.isdir(d)]
lib_path = ":".join(lib_dirs) + ":" + os.environ.get("LD_LIBRARY_PATH", "")
os.environ["LD_LIBRARY_PATH"] = lib_path

result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)

if result.returncode == 0:
    print(result.stdout)
    print("✓ ffmpeg is installed and working")
else:
    print(result.stderr)
    print("✗ ffmpeg not found")
    sys.exit(1)
