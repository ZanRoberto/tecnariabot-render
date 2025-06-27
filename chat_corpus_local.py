import json
import os
import numpy as np
from openai import OpenAI
from pathlib import Path

client = OpenAI()
CORPUS_PATH = "data/corpus_testuale.json"
SIMILARITY_THRESHOLD = 0.80  # puoi alzarla se vuoi essere più restrittivo


def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def trova_contesto_rilevante(domanda, top_k=1):
    if not Path(CORPUS_PATH).exists():
        return []

    # Carica corpus locale
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    # Embedding della domanda
    embedding_utente = client.embeddings.create(
        model="text-embedding-3-small",
        input=domanda
    ).data[0].embedding

    # Calcola similarità
    scored = []
    for doc in corpus:
        testo = doc.get("testo", "")
        if testo:
            embedding_doc = client.embeddings.create(
                model="text-embedding-3-small",
                input=testo
            ).data[0].embedding

            score = cosine_similarity(embedding_utente, embedding_doc)
            scored.append((score, testo))

    # Ordina per rilevanza
    scored.sort(reverse=True, key=lambda x: x[0])
    return [x[1] for x in scored[:top_k] if x[0] >= SIMILARITY_THRESHOLD]
