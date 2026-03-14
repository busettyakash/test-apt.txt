import os

ffmpeg_version = os.getenv("FFMPEG_VERSION_VAR", "not found")
ffmpeg_size = os.getenv("FFMPEG_SIZE_VAR", "unknown")

status = "Installed" if "ffmpeg version" in ffmpeg_version else "Not Installed"

html = f"""
<html>
<head>
<title>Voice Agent Check</title>
</head>

<body>

<h1>Voice Agent Dependency</h1>

<h2>FFmpeg Status</h2>
<p>{status}</p>

<h2>Version</h2>
<pre>{ffmpeg_version}</pre>

<h2>FFmpeg Binary Size</h2>
<pre>{ffmpeg_size}</pre>

</body>
</html>
"""

os.makedirs("docs", exist_ok=True)

with open("docs/index.html", "w") as f:
    f.write(html)

print("Report generated")
