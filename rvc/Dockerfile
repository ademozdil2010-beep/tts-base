# The base image of a Jarvis speech container: Silero reads the text and RVC turns the voice into Vyacheslav Baranov's.
# torch for the CPU only, rvc-python with its base models (hubert, rmvpe), the Baranov model and Silero are all in the image,
# so a container starts without the internet. The application image adds its server on top (FROM this image, COPY the server,
# CMD). Published by .github/workflows/build.yml as ghcr.io/<owner>/tts-base-rvc:<tag>, where the tag is a hash of this file.
#
# Python 3.10 and pip<24.1 are needed because of rvc-python: it pulls fairseq 0.12.2 and omegaconf 2.0.6, which do not install
# on a newer Python or pip.
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

# gcc in case pyworld / praat-parselmouth have no ready wheel; removed again after the install
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
 && pip install pip==23.3.1 \
 && pip install --index-url https://download.pytorch.org/whl/cpu torch==2.1.2 torchaudio==2.1.2 \
 && pip install rvc-python==0.1.5 num2words==0.5.14 \
 && apt-get purge -y build-essential && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# The RVC base models (rvc-python downloads them on first use, and the container has no internet)
RUN python -c "import os, rvc_python.download_model as d; d.download_rvc_models(os.path.dirname(os.path.abspath(d.__file__)))" \
 && python -c "import os, rvc_python as r; b = os.path.join(os.path.dirname(r.__file__), 'base_model'); \
 [print(f, os.path.getsize(os.path.join(b, f))) for f in ('hubert_base.pt', 'rmvpe.pt')]"

# Vyacheslav Baranov's model (RVC v2, no index): niobures/RVC-Models on Hugging Face, checked by SHA-256.
ARG RVC_URL="https://huggingface.co/niobures/RVC-Models/resolve/main/rvc-big-ru-voice-pack/%D0%90%D0%BA%D1%82%D0%B5%D1%80%D1%8B%20%D0%B4%D1%83%D0%B1%D0%BB%D0%B5%D0%B6%D0%B0/%D0%92%D1%8F%D1%87%D0%B5%D1%81%D0%BB%D0%B0%D0%B2%20%D0%91%D0%B0%D1%80%D0%B0%D0%BD%D0%BE%D0%B2/%D0%92%D1%8F%D1%87%D0%B5%D1%81%D0%BB%D0%B0%D0%B2%20%D0%91%D0%B0%D1%80%D0%B0%D0%BD%D0%BE%D0%B2.pth"
ARG RVC_SHA256=b77f227fffdfab2deb2ef1cdb0cc026a1806be6718489aaf2f0f3db927679523
RUN python -c "import hashlib, sys, urllib.request; urllib.request.urlretrieve('${RVC_URL}', 'baranov.pth'); \
h = hashlib.sha256(open('baranov.pth', 'rb').read()).hexdigest(); \
sys.exit(0 if h == '${RVC_SHA256}' else 'baranov.pth: sha256 ' + h + ' does not match')"

# Silero reads the text, RVC changes its voice into Baranov's. The Silero models are licensed CC BY-NC.
ARG MODEL_URL=https://models.silero.ai/models/tts/ru/v5_6_ru.pt
ARG MODEL_SHA256=04cc9b1d08ce38bcaa9d02c488d80d3e6806d17f7eaa7c95982f36a3cbf50b2e
RUN python -c "import hashlib, sys, urllib.request; urllib.request.urlretrieve('${MODEL_URL}', 'model.pt'); \
h = hashlib.sha256(open('model.pt', 'rb').read()).hexdigest(); \
sys.exit(0 if h == '${MODEL_SHA256}' else 'model.pt: sha256 ' + h + ' does not match')"
