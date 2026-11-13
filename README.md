# tts-base

The base image of a speech container: ffmpeg, [Vosk TTS](https://github.com/alphacep/vosk-tts) with the Russian
model `vosk-model-tts-ru-0.9-multi` (Apache 2.0) prepared to load in about a second and take about 550 MB of
memory, and [Piper](https://github.com/OHF-Voice/piper1-gpl) with the English voices `amy` and `ryan`.

`prepare_vosk.py` does the preparation when the image is built: the pronunciation dictionary becomes an SQLite
table read from disk, the synthesis model gets its constants folded, and ruBert gets 8-bit weights.

Every push to `main` that changes `Dockerfile` or `prepare_vosk.py` publishes
`ghcr.io/ademozdil2010-beep/tts-base:<tag>`; the tag is the first 12 characters of the SHA-256 of those two files
(`cat Dockerfile prepare_vosk.py | sha256sum`). An application builds on it:

```dockerfile
FROM ghcr.io/ademozdil2010-beep/tts-base:<tag>
COPY server.py .
CMD ["python", "server.py"]
```
