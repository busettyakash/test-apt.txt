import subprocess

print("Testing ffmpeg...")

try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
    version_line = result.stdout.decode().split("\n")[0]
    print(f"✅ ffmpeg is installed: {version_line}")
except FileNotFoundError:
    print("❌ ffmpeg NOT found — Add 'ffmpeg' to Aptfile and include paketo-buildpacks/apt")
except subprocess.CalledProcessError:
    print("❌ ffmpeg found but failed to run")
except subprocess.TimeoutExpired:
    print("❌ ffmpeg check timed out")
