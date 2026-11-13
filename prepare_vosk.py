"""Prepares the Vosk speech model for the image: python prepare_vosk.py <output directory>.

The model as published takes about a minute to load and 1.8 GB of memory. What is written here loads in a second
and takes about 550 MB:
- dictionary.db: the pronunciation dictionary (two million words) as an SQLite table that is read from disk, in
  place of a text file that vosk-tts loads into memory whole;
- model.onnx: the synthesis model with its constants folded, about half the nodes;
- bert.onnx: ruBert, which the model takes the intonation from, with 8-bit weights: a quarter of the size.
"""
import hashlib
import io
import shutil
import sqlite3
import sys
import urllib.request
import zipfile
from pathlib import Path

import onnxruntime
from onnxruntime.quantization import QuantType, quantize_dynamic

NAME = "vosk-model-tts-ru-0.9-multi"
URL = f"https://alphacephei.com/vosk/models/{NAME}.zip"
SHA256 = "0aa332451ce46bfdbd620e74765fc16a4087988067c299969121ed0f8ed5bdf2"


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    work = out / "source"
    archive = urllib.request.urlopen(URL).read()
    if hashlib.sha256(archive).hexdigest() != SHA256:
        raise SystemExit("The Vosk model archive is not the one this image was made for")
    zipfile.ZipFile(io.BytesIO(archive)).extractall(work)
    del archive
    source = work / NAME

    # A word listed more than once keeps its most probable pronunciation, as vosk-tts chooses it.
    best = {}
    with open(source / "dictionary", encoding="utf-8") as lines:
        for line in lines:
            word, probability, phonemes = line.split(maxsplit=2)
            if best.get(word, (0,))[0] < float(probability):
                best[word] = (float(probability), phonemes.strip())
    db = sqlite3.connect(out / "dictionary.db")
    db.execute("CREATE TABLE words (word TEXT PRIMARY KEY, phonemes TEXT NOT NULL) WITHOUT ROWID")
    db.executemany("INSERT INTO words VALUES (?, ?)", ((word, best[word][1]) for word in sorted(best)))
    db.commit()
    db.close()
    del best

    # Not the highest level: its changes depend on the processor the image is built on.
    options = onnxruntime.SessionOptions()
    options.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
    options.optimized_model_filepath = str(out / "model.onnx")
    onnxruntime.InferenceSession(str(source / "model.onnx"), sess_options=options, providers=["CPUExecutionProvider"])

    quantize_dynamic(source / "bert" / "model.onnx", out / "bert.onnx", weight_type=QuantType.QInt8)

    shutil.copy(source / "config.json", out / "config.json")
    shutil.copy(source / "bert" / "vocab.txt", out / "vocab.txt")
    shutil.rmtree(work)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
