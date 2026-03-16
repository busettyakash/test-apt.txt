import subprocess

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

_ensure_ffmpeg_path()
