# tts-base

The base image of a speech container: the `opusenc` and `lame` encoders, [Vosk TTS](https://github.com/alphacep/vosk-tts) with the Russian
model `vosk-model-tts-ru-0.9-multi` (Apache 2.0) prepared to load in about a second and take about 550 MB of
memory, and [Piper](https://github.com/OHF-Voice/piper1-gpl) with the English voices `amy` and `ryan`.

`prepare_vosk.py` does the preparation when the image is built: the pronunciation dictionary becomes an SQLite
table read from disk, the synthesis model gets its constants folded, and ruBert gets 8-bit weights.

Every push to `main` that changes `Dockerfile` or `prepare_vosk.py` publishes
`ghcr.io/<owner of this repository>/tts-base:<tag>`; the tag is the first 12 characters of the SHA-256 of those two files
(`cat Dockerfile prepare_vosk.py | sha256sum`). An application builds on it:

```dockerfile
FROM ghcr.io/pcelobav/tts-base:<tag>
COPY server.py .
CMD ["python", "server.py"]
```

## tts-base-rvc

The second image in this repository is the base of the Jarvis speech container: Python 3.10 with torch for the CPU and
[rvc-python](https://pypi.org/project/rvc-python/) (its base models `hubert` and `rmvpe` included), the Silero v5 Russian
model that reads the text (CC BY-NC) and the RVC voice model `baranov.pth` that changes the voice. The container starts
without the internet, and an application only adds its server:

```dockerfile
FROM ghcr.io/pcelobav/tts-base-rvc:<tag>
COPY server.py .
EXPOSE 8080
CMD ["python", "server.py"]
```

`rvc/Dockerfile` is its whole description; the tag is the first 12 characters of its SHA-256
(`cat rvc/Dockerfile | sha256sum`). A tag that is already published is never built again.
