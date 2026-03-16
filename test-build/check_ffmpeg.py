# Copyright (c) 2025 Revinci AI.
#
# All rights reserved. This software is proprietary to and embodies the
# confidential technology of Revinci AI. Possession,
# use, duplication, or dissemination of the software and media is
# authorized only pursuant to a valid written license from Revinci AI.
#
# Unauthorized use of this software is strictly prohibited.
#
# THIS SOFTWARE IS PROVIDED BY Revinci AI "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Revinci AI BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Voice helpers and voice listing endpoint.

Mounted at /voice on the opportunity agent server.
All endpoints require:
  - Authorization: Bearer <token>
  - Tenant-Id: <realm>
"""

import asyncio
import glob
import os
import platform
import subprocess
import tempfile

import httpx
import requests as _requests
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter(prefix="/voice", tags=["Voice"])

_security = HTTPBearer(
    scheme_name="Bearer Token",
    description="Enter your Bearer token from Keycloak",
)

_ELEVENLABS_URL = "https://api.elevenlabs.io/v1"
_ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_turbo_v2_5")

# ── ffmpeg PATH discovery ──────────────────────────────────────────────────────
def _ensure_ffmpeg_path() -> None:
    """Ensure ffmpeg is on PATH. On Linux, ffmpeg must be installed via Cloud Native Buildpacks.
    Add paketo-buildpacks/apt buildpack and list 'ffmpeg' in apt.yml in the agent directory."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
        return  # already on PATH
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        pass

    if platform.system() != "Windows":
        print("[voice/stt] ffmpeg not found. Add to agent apt.yml for Cloud Native Buildpacks (paketo-buildpacks/apt).")
        return

    search_patterns = [
        # WinGet
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*FFmpeg*\**\bin"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"),
        # Scoop
        os.path.expandvars(r"%USERPROFILE%\scoop\shims"),
        os.path.expandvars(r"%USERPROFILE%\scoop\apps\ffmpeg\current\bin"),
        # Chocolatey / manual installs
        r"C:\ProgramData\chocolatey\bin",
        r"C:\tools\ffmpeg\bin",
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
    ]

    current_path = os.environ.get("PATH", "")
    for pattern in search_patterns:
        for p in glob.glob(pattern, recursive=True):
            if os.path.isdir(p) and p not in current_path:
                if (
                    os.path.exists(os.path.join(p, "ffmpeg.exe"))
                    or os.path.exists(os.path.join(p, "ffmpeg"))
                ):
                    os.environ["PATH"] = p + os.pathsep + current_path
                    current_path = os.environ["PATH"]
                    print(f"[voice/stt] Added ffmpeg to PATH: {p}")
                elif p.endswith("Links") or p.endswith("shims"):
                    os.environ["PATH"] = p + os.pathsep + current_path
                    current_path = os.environ["PATH"]


_ensure_ffmpeg_path()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _el_key() -> str:
    return os.getenv("ELEVENLABS_API_KEY", "")


def _stt_key() -> str:
    return os.getenv("AZURE_SPEECH_KEY", "")


def _stt_region() -> str:
    return os.getenv("AZURE_SPEECH_REGION", "westus")


from shared.voice import FALLBACK_VOICES as _FALLBACK_VOICES


# ── Voices ────────────────────────────────────────────────────────────────────

@router.get("/voices")
async def get_voices(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    tenant_id: str = Header(..., alias="Tenant-Id", description="Tenant identifier"),
):
    """Return available ElevenLabs voices organised by gender."""
    api_key = _el_key()
    if not api_key:
        return _FALLBACK_VOICES

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"{_ELEVENLABS_URL}/voices",
                headers={"xi-api-key": api_key},
            )
            if r.status_code == 200:
                organised: dict[str, list] = {"female": [], "male": [], "other": []}
                for v in r.json().get("voices", []):
                    gender = v.get("labels", {}).get("gender", "").lower()
                    info = {
                        "voice_id":     v["voice_id"],
                        "name":         v["name"],
                        "display_name": v["name"],
                    }
                    organised.get(gender, organised["other"]).append(info)
                return organised
    except Exception as e:
        print(f"[voice/voices] ElevenLabs error: {e}")

    return _FALLBACK_VOICES


# ── TTS ───────────────────────────────────────────────────────────────────────

async def _do_tts(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
    """Call ElevenLabs streaming API and return raw MP3 bytes. Raises HTTPException on failure."""
    api_key = _el_key()
    if not api_key:
        raise HTTPException(500, "ELEVENLABS_API_KEY not configured")

    url = (
        f"{_ELEVENLABS_URL}/text-to-speech/{voice_id}/stream"
        "?optimize_streaming_latency=4&output_format=mp3_22050_32"
    )
    headers = {
        "Accept":       "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key":   api_key,
    }
    payload = {
        "text":     text,
        "model_id": _ELEVENLABS_MODEL,
        "voice_settings": {
            "stability":         0.5,
            "similarity_boost":  0.75,
            "style":             0.0,
            "use_speaker_boost": False,
        },
    }

    def _call():
        resp = _requests.post(url, headers=headers, json=payload, timeout=60, stream=True)
        if resp.status_code != 200:
            err = resp.text
            try:
                detail = resp.json().get("detail", {})
                err = detail.get("message", err) if isinstance(detail, dict) else str(detail)
            except Exception:
                pass
            raise HTTPException(resp.status_code, f"ElevenLabs: {err}")
        return b"".join(resp.iter_content(chunk_size=4096))

    print(f"[voice/tts] {len(text)} chars, voice={voice_id}")
    return await asyncio.to_thread(_call)


# ── STT ───────────────────────────────────────────────────────────────────────

async def _do_stt(audio_bytes: bytes) -> str:
    """Transcribe WebM audio bytes via Azure Speech. Returns transcribed text. Raises HTTPException on failure."""
    api_key = _stt_key()
    region  = _stt_region()
    if not api_key:
        raise HTTPException(500, "AZURE_SPEECH_KEY not configured")

    webm_path = wav_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
            f.write(audio_bytes)
            webm_path = f.name

        wav_path = webm_path.replace(".webm", ".wav")

        def _run_ffmpeg():
            try:
                return subprocess.run(
                    ["ffmpeg", "-y", "-i", webm_path, "-ar", "16000", "-ac", "1", wav_path],
                    check=True,
                    capture_output=True,
                )
            except FileNotFoundError:
                raise RuntimeError(
                    "ffmpeg not found. "
                    "Windows: winget install Gyan.FFmpeg | "
                    "Linux: apt-get install -y ffmpeg (add to Dockerfile)"
                )

        await asyncio.to_thread(_run_ffmpeg)

        stt_url = (
            f"https://{region}.stt.speech.microsoft.com"
            "/speech/recognition/conversation/cognitiveservices/v1"
        )
        with open(wav_path, "rb") as wf:
            wav_bytes = wf.read()

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                stt_url,
                content=wav_bytes,
                headers={
                    "Ocp-Apim-Subscription-Key": api_key,
                    "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
                },
                params={"language": "en-US", "format": "simple"},
            )

        print(f"[voice/stt] Azure status: {r.status_code}")
        if r.status_code != 200:
            raise HTTPException(r.status_code, f"Azure STT error: {r.text}")

        result = r.json()
        status = result.get("RecognitionStatus", "")
        text   = result.get("DisplayText", "").strip()

        if status != "Success" or not text:
            raise HTTPException(422, f"Recognition failed: {status}")

        return text

    except HTTPException:
        raise
    except subprocess.CalledProcessError as e:
        err = e.stderr.decode(errors="replace") if e.stderr else str(e)
        raise HTTPException(500, f"ffmpeg conversion failed: {err}")
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    except Exception as e:
        import traceback
        print(f"[voice/stt] Unexpected error: {traceback.format_exc()}")
        raise HTTPException(500, str(e))
    finally:
        for p in [webm_path, wav_path]:
            if p and os.path.exists(p):
                os.unlink(p)
