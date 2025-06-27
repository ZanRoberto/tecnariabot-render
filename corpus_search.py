# ✅ File: corpus_search.py
# Cerca dentro corpus_testuale.json il contenuto più rilevante per una domanda

import json
import os
import numpy as np
from difflib import SequenceMatcher

CORPUS_PATH = "data/corpus_testuale.json"

# === Similarità semplice tra due stringhe (fallback semantico)
def string_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def carica_corpus():
    if not os.path.exists(CORPUS_PATH):
        return []
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def trova_contesto_rilevante(domanda, max_risultati=1):
    corpus = carica_corpus()
    risultati = []

    for voce in corpus:
        testo = voce.get("testo", "")
        sim = string_similarity(domanda, testo)
        risultati.append((sim, testo))

    risultati.sort(reverse=True)
    return [t for _, t in risultati[:max_risultati]]

# Esempio uso
if __name__ == "__main__":
    domanda = "Che chiodatrici vende Tecnaria?"
    contesto = trova_contesto_rilevante(domanda)
    print("Contesto trovato:\n", contesto[0])
