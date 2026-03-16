import subprocess
import os

print("Testing ffmpeg...")

LIB_PATH = "/layers/paketo-buildpacks_apt/apt/usr/lib/x86_64-linux-gnu"

def _set_lib_path() -> None:
    """Set LD_LIBRARY_PATH for ffmpeg shared libraries (libgobject-2.0.so.0 etc.)"""
    current_ld = os.environ.get("LD_LIBRARY_PATH", "")
    if LIB_PATH not in current_ld:
        os.environ["LD_LIBRARY_PATH"] = LIB_PATH + os.pathsep + current_ld
        print(f"✅ LD_LIBRARY_PATH set: {os.environ['LD_LIBRARY_PATH']}")
    else:
        print(f"✅ LD_LIBRARY_PATH already set: {current_ld}")

def _ensure_ffmpeg_path() -> None:
    """Ensure ffmpeg is on PATH. Installed via Cloud Native Buildpacks.
    Add paketo-buildpacks/apt buildpack and list 'ffmpeg' + 'libglib2.0-0' in Aptfile."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
        version_line = result.stdout.decode().split("\n")[0]
        print(f"✅ ffmpeg is installed: {version_line}")
        return
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        print("❌ ffmpeg is NOT installed. Add 'ffmpeg' and 'libglib2.0-0' to Aptfile and include paketo-buildpacks/apt in buildpack config.")

def _check_ffmpeg_path() -> None:
    """Check if ffmpeg PATH and library path are correctly set."""
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

    # 4. LD_LIBRARY_PATH check
    ld = os.environ.get("LD_LIBRARY_PATH", "")
    if LIB_PATH in ld:
        print(f"✅ LD_LIBRARY_PATH: {ld}")
    else:
        print(f"❌ LD_LIBRARY_PATH missing: {LIB_PATH}")

    # 5. Shared lib check
    lib_file = os.path.join(LIB_PATH, "libglib-2.0.so.0")
    if os.path.exists(lib_file):
        print(f"✅ libglib-2.0.so.0 found: {lib_file}")
    else:
        print(f"❌ libglib-2.0.so.0 NOT found — Add 'libglib2.0-0' to Aptfile")

    print("────────────────────────────────────────────\n")

_set_lib_path()
_ensure_ffmpeg_path()
_check_ffmpeg_path()
