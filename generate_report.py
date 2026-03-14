import os

version = os.getenv("FFMPEG_VERSION_VAR", "not found")
size = os.getenv("FFMPEG_SIZE_VAR", "unknown")
date = os.getenv("BUILD_DATE_VAR", "")

status = "Installed" if "ffmpeg version" in version else "Not Installed"

html = f"""
<html>
<body>

<h1>Voice Agent Dependency</h1>

<p><b>Build Date:</b> {date}</p>

<h2>FFmpeg Status</h2>
<p>{status}</p>

<h2>Version</h2>
<pre>{version}</pre>

<h2>Binary Size</h2>
<pre>{size}</pre>

</body>
</html>
"""

os.makedirs("docs", exist_ok=True)

with open("docs/index.html","w") as f:
    f.write(html)
