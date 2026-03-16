import subprocess
import os

print("Testing ffmpeg...")

def _ensure_ffmpeg_path() -> None:
    """Ensure ffmpeg is on PATH. Installed via Cloud Native Buildpacks.
    Add paketo-buildpacks/apt buildpack and list 'ffmpeg' in Aptfile in the agent directory."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
        version_line = result.stdout.decode().split("\n")[0]
        print(f"✅ ffmpeg is installed: {version_line}")
        return
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        print("❌ ffmpeg is NOT installed. Add 'ffmpeg' to Aptfile and include paketo-buildpacks/apt in buildpack config.")

def _check_ffmpeg_path() -> None:
    """Check if ffmpeg PATH is correctly set."""
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

    # 3. which/where check
    which_result = subprocess.run(["which", "ffmpeg"], capture_output=True)
    if which_result.returncode == 0:
        print(f"✅ which ffmpeg: {which_result.stdout.decode().strip()}")
    else:
        print("❌ which ffmpeg: not found")

    print("────────────────────────────────────────────\n")

_ensure_ffmpeg_path()
_check_ffmpeg_path()
