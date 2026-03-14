import os

ffmpeg_version = os.getenv("FFMPEG_VERSION_VAR", "not found")

status = "Installed" if "ffmpeg version" in version else "Not Installed"

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
<pre>{version}</pre>

</body>
</html>
"""

os.makedirs("docs", exist_ok=True)

with open("docs/index.html","w") as f:
    f.write(html)
