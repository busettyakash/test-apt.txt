import subprocess
import os

def test_ffmpeg():
    print("── ffmpeg Test ──────────────────────────────")
    
    # 1. Check PATH
    print(f"PATH: {os.environ.get('PATH', '')}")
    
    # 2. Check ffmpeg version
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if result.returncode == 0:
        version_line = result.stdout.decode().split("\n")[0]
        print(f"✅ ffmpeg found: {version_line}")
    else:
        print(f"❌ ffmpeg NOT found")

    # 3. Check exact path
    which = subprocess.run(["which", "ffmpeg"], capture_output=True)
    if which.returncode == 0:
        print(f"✅ ffmpeg path: {which.stdout.decode().strip()}")
        # Expected: /layers/paketo-buildpacks_apt/apt/usr/bin/ffmpeg
    else:
        print("❌ which ffmpeg: not found")

    print("────────────────────────────────────────────")

test_ffmpeg()
