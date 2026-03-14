import os

ffmpeg_path = os.environ.get('FFMPEG_PATH_VAR', 'Not found')
missing = os.environ.get('MISSING_VAR', '')
ffmpeg_version = os.environ.get('FFMPEG_VERSION_VAR', '')
aptfile = os.environ.get('APTFILE_VAR', '')
build_date = os.environ.get('BUILD_DATE_VAR', '')
status = os.environ.get('STATUS_VAR', 'fail')

missing_html = '✓ No missing libraries' if not missing.strip() else missing.strip()
badge = '<span class="badge-pass">✓ PASS</span>' if status == 'pass' else '<span class="badge-fail">✗ FAIL - Missing libraries</span>'

html = f"""<!DOCTYPE html>
<html>
<head>
  <title>FFmpeg Build Test Report</title>
  <style>
    body {{ font-family: monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4; }}
    h1 {{ color: #569cd6; }}
    h2 {{ color: #9cdcfe; }}
    .box {{ background: #2d2d2d; padding: 15px; border-radius: 5px; margin: 10px 0; white-space: pre-wrap; word-break: break-all; }}
    .badge-pass {{ background: #4ec9b0; color: black; padding: 4px 10px; border-radius: 4px; font-weight: bold; }}
    .badge-fail {{ background: #f44747; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>🐳 FFmpeg Buildpack Test Report</h1>
  <p>Built: {build_date}</p>
  <p>Builder: paketobuildpacks/builder-jammy-base</p>

  <h2>Aptfile</h2>
  <div class="box">{aptfile}</div>

  <h2>ffmpeg Path</h2>
  <div class="box">{ffmpeg_path}</div>

  <h2>Missing Libraries</h2>
  <div class="box">{missing_html}</div>

  <h2>ffmpeg Version Output</h2>
  <div class="box">{ffmpeg_version}</div>

  <h2>Result</h2>
  {badge}
</body>
</html>"""

os.makedirs('docs', exist_ok=True)

with open('docs/index.html', 'w') as f:
    f.write(html)

print('✓ Report generated at docs/index.html')
