import subprocess
import os

print("Testing ffmpeg...")

_STATIC_FFMPEG_DIR = os.path.join(os.path.dirname(__file__), "ffmpeg")
_STATIC_FFMPEG_BIN = os.path.join(_STATIC_FFMPEG_DIR, "ffmpeg")

def _set_ffmpeg_path() -> None:
    """Add static ffmpeg binary directory to PATH."""
    current_path = os.environ.get("PATH", "")
    if _STATIC_FFMPEG_DIR not in current_path:
        os.environ["PATH"] = _STATIC_FFMPEG_DIR + os.pathsep + current_path
        print(f"✅ PATH set: {os.environ['PATH']}")
    else:
        print(f"✅ PATH already set: {current_path}")

def _ensure_ffmpeg_path() -> None:
    """Ensure static ffmpeg binary is available.
    Download: https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
    Place binary at: ffmpeg/ffmpeg"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
        version_line = result.stdout.decode().split("\n")[0]
        print(f"✅ ffmpeg is installed: {version_line}")
        return
    except (FileNotFoundError, subprocess.CalledProcessError, OSError) as e:
        print(f"❌ ffmpeg is NOT installed: {e}")
        print(f"   Expected static binary at: {_STATIC_FFMPEG_BIN}")

def _check_ffmpeg_path() -> None:
    """Check if static ffmpeg binary is correctly set."""
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

    # 4. Static binary exists check
    if os.path.exists(_STATIC_FFMPEG_BIN):
        size_mb = os.path.getsize(_STATIC_FFMPEG_BIN) // (1024 * 1024)
        print(f"✅ static binary found: {_STATIC_FFMPEG_BIN} ({size_mb} MB)")
    else:
        print(f"❌ static binary NOT found: {_STATIC_FFMPEG_BIN}")

    # 5. Executable check
    if os.access(_STATIC_FFMPEG_BIN, os.X_OK):
        print(f"✅ ffmpeg is executable")
    else:
        print(f"❌ ffmpeg is NOT executable — run: chmod +x ffmpeg/ffmpeg")

    print("────────────────────────────────────────────\n")

_set_ffmpeg_path()
_ensure_ffmpeg_path()
_check_ffmpeg_path()
