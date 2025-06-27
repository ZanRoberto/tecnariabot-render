# ✅ File: indicizza_pagine_prodotto.py
# Crea corpus_testuale.json leggibile dal bot da prodotti_raw.json

import json
import os
from pathlib import Path

INPUT_RAW = "data/prodotti_raw.json"
OUTPUT_CORPUS = "data/corpus_testuale.json"


def indicizza():
    if not Path(INPUT_RAW).exists():
        print("❌ File prodotti_raw.json non trovato.")
        return

    with open(INPUT_RAW, "r", encoding="utf-8") as f:
        prodotti = json.load(f)

    corpus = []
    for p in prodotti:
        testo = p.get("testo", "")
        if len(testo) >= 100:
            corpus.append({"testo": testo.strip()[:3000]})

    with open(OUTPUT_CORPUS, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    print(f"✅ Corpus indicizzato con {len(corpus)} elementi.")


if __name__ == "__main__":
    indicizza()
