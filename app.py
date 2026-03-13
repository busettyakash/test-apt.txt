import subprocess

print("Testing ffmpeg...")

result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)

print(result.stdout)
