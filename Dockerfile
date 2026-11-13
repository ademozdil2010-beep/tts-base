# The base image of a speech container: the Opus and MP3 encoders, Vosk TTS with a prepared Russian model, Piper with two English
# voices. The application image adds its server on top (FROM this image, COPY the server, CMD).
# Published by .github/workflows/build.yml as ghcr.io/ademozdil2010-beep/tts-base:<tag>, where the tag is a hash of
# this file and prepare_vosk.py.

# The Vosk model is made smaller and faster to load here; the tools for that stay out of the final image.
FROM python:3.12-slim AS vosk
RUN pip install --no-cache-dir onnxruntime==1.31.1 onnx==1.23.2
COPY prepare_vosk.py .
RUN python prepare_vosk.py /vosk

FROM python:3.12-slim

# The encoders for the two formats the server answers in. ffmpeg would do both, but it brings 450 MB of libraries.
RUN apt-get update \
 && apt-get install -y --no-install-recommends opus-tools lame \
 && rm -rf /var/lib/apt/lists/*

# onnxruntime is the version the Vosk model was prepared with.
RUN pip install --no-cache-dir piper-tts==1.8.0 vosk-tts==0.3.61 num2words==0.5.14 onnxruntime==1.31.1

# Voices are part of the image, so a cold start downloads nothing.
WORKDIR /app/voices
RUN python - <<'PY'
import urllib.request
BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"
VOICES = ["en/en_US/amy/medium/en_US-amy-medium", "en/en_US/ryan/medium/en_US-ryan-medium"]
for path in VOICES:
    for ext in (".onnx", ".onnx.json"):
        urllib.request.urlretrieve(f"{BASE}/{path}{ext}", path.rsplit("/", 1)[1] + ext)
PY

WORKDIR /app
COPY --from=vosk /vosk vosk
