import subprocess
import os

print("Testing ffmpeg...")

def _ensure_ffmpeg_path() -> None:
    """Ensure ffmpeg is on PATH. Installed via Cloud Native Buildpacks.
    Aptfile must contain: ffmpeg"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
        version_line = result.stdout.decode().split("\n")[0]
        print(f"✅ ffmpeg is installed: {version_line}")
        return
    except (FileNotFoundError, subprocess.CalledProcessError, OSError) as e:
        print(f"❌ ffmpeg is NOT installed: {e}")
        print("   Aptfile must contain: ffmpeg")

def _check_ffmpeg_path() -> None:
    """Check if ffmpeg is correctly installed."""
    print("\n── PATH Check ──────────────────────────────")

    # 1. Check PATH env
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    print(f"📁 PATH dirs count: {len(path_dirs)}")

    # 2. Find ffmpeg in PATH
    ffmpeg_found = False
    for d in path_dirs:
        ffmpeg_bin = os.path.join(d, "ffmpeg")
        if os.path.exists(ffmpeg_bin):
            print(f"✅ ffmpeg found in PATH: {ffmpeg_bin}")
            ffmpeg_found = True
            break
    if not ffmpeg_found:
        print("❌ ffmpeg binary not found in any PATH directory")

    # 3. which ffmpeg check
    which_result = subprocess.run(["which", "ffmpeg"], capture_output=True)
    if which_result.returncode == 0:
        print(f"✅ which ffmpeg: {which_result.stdout.decode().strip()}")
    else:
        print("❌ which ffmpeg: not found")

    # 4. ffmpeg binary check
    ffmpeg_bin = "/usr/bin/ffmpeg"
    if os.path.exists(ffmpeg_bin):
        print(f"✅ ffmpeg binary found: {ffmpeg_bin}")
    else:
        print(f"❌ ffmpeg binary NOT found — Add 'ffmpeg' to Aptfile")

    print("────────────────────────────────────────────\n")

_ensure_ffmpeg_path()
_check_ffmpeg_path()
```

---

**Also update `Aptfile`:**
```
ffmpeg
