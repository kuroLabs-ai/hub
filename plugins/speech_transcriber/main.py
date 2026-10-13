"""
community_hub/plugins/speech_transcriber/main.py
Convert audio recordings into text using configurable speech-recognition APIs or local Whisper models.
Includes audio metadata detection and clean JSON response structures with timestamp segments.
"""

import os
import struct
import urllib.request
import json
from typing import Dict, Any, List, Optional


def get_audio_info(file_path: str) -> Dict[str, Any]:
    """
    Inspect basic audio file format, size, and header properties.
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"Audio file '{file_path}' does not exist"}

    size_bytes = os.path.getsize(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    info: Dict[str, Any] = {
        "success": True,
        "file_path": file_path,
        "size_bytes": size_bytes,
        "extension": ext,
        "duration_estimate_sec": None,
        "channels": None,
        "sample_rate": None
    }

    # Inspect WAV RIFF header if file is a WAV
    if ext == ".wav" and size_bytes > 44:
        try:
            with open(file_path, "rb") as f:
                header = f.read(44)
            if header.startswith(b"RIFF") and header[8:12] == b"WAVE":
                channels = struct.unpack("<H", header[22:24])[0]
                sample_rate = struct.unpack("<I", header[24:28])[0]
                byte_rate = struct.unpack("<I", header[28:32])[0]
                info["channels"] = channels
                info["sample_rate"] = sample_rate
                if byte_rate > 0:
                    info["duration_estimate_sec"] = round(size_bytes / byte_rate, 2)
        except Exception:
            pass

    return info


def transcribe_audio_api(
    audio_path: str,
    api_endpoint: str = "https://api.openai.com/v1/audio/transcriptions",
    api_key: Optional[str] = None,
    model: str = "whisper-1",
    language: Optional[str] = None,
    response_format: str = "verbose_json"
) -> Dict[str, Any]:
    """
    Send an audio recording to a transcription API (OpenAI Whisper compatible).
    """
    if not os.path.exists(audio_path):
        return {"success": False, "error": f"Audio file '{audio_path}' not found."}

    token = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("SPEECH_API_KEY")
    if not token:
        return {
            "success": False,
            "error": "Missing API key. Set OPENAI_API_KEY / SPEECH_API_KEY or pass api_key parameter."
        }

    try:
        # Prepare multipart/form-data payload
        boundary = "----WebKitFormBoundaryKuroCodeSpeech" + os.urandom(8).hex()
        body = bytearray()

        def add_field(name: str, value: str):
            nonlocal body
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
            body.extend(f"{value}\r\n".encode("utf-8"))

        add_field("model", model)
        add_field("response_format", response_format)
        if language:
            add_field("language", language)

        # Append file data
        fname = os.path.basename(audio_path)
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'.encode("utf-8"))
        body.extend(b"Content-Type: audio/octet-stream\r\n\r\n")

        with open(audio_path, "rb") as f:
            body.extend(f.read())
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode("utf-8"))

        req = urllib.request.Request(
            api_endpoint,
            data=bytes(body),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": f"multipart/form-data; boundary={boundary}"
            }
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            raw_response = resp.read().decode("utf-8")
            data = json.loads(raw_response)

        segments = []
        if isinstance(data, dict) and "segments" in data:
            for s in data["segments"]:
                segments.append({
                    "start": s.get("start"),
                    "end": s.get("end"),
                    "text": s.get("text", "").strip()
                })

        return {
            "success": True,
            "audio_file": audio_path,
            "model": model,
            "text": data.get("text", "") if isinstance(data, dict) else str(data),
            "segments_count": len(segments),
            "segments": segments
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def transcribe_local_whisper(audio_path: str, model_size: str = "base") -> Dict[str, Any]:
    """
    Transcribe audio locally using installed whisper Python module (if present).
    """
    if not os.path.exists(audio_path):
        return {"success": False, "error": f"Audio file '{audio_path}' not found."}

    try:
        import whisper
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path)
        
        segments = []
        for s in result.get("segments", []):
            segments.append({
                "start": round(s.get("start", 0), 2),
                "end": round(s.get("end", 0), 2),
                "text": s.get("text", "").strip()
            })

        return {
            "success": True,
            "engine": "local_whisper",
            "model_size": model_size,
            "text": result.get("text", "").strip(),
            "language": result.get("language"),
            "segments": segments
        }
    except ImportError:
        return {
            "success": False,
            "error": "Local transcription requires 'whisper'. Install via `pip install openai-whisper` or use transcribe_audio_api()."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
