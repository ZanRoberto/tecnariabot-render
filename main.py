from flask import Flask, render_template, request, jsonify
import openai
import os
import json
import numpy as np
from pathlib import Path

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = (
    "Rispondi esclusivamente in qualità di rappresentante esperto della società TECNARIA S.p.A., "
    "con sede unica in Viale Pecori Giraldi 55, 36061 Bassano del Grappa (VI), Italia. "
    "Fornisci solo informazioni relative a questa azienda, ai suoi prodotti, servizi e cataloghi ufficiali. "
    "Ignora qualsiasi altra azienda omonima o simile. "
    "Se una domanda non riguarda direttamente TECNARIA, rispondi gentilmente che l'informazione non è disponibile. "
    "Per indirizzo, recapiti e posizione geografica, fai riferimento alla sede di Bassano del Grappa."
)

# === LISTA DEI FILE JSON E EMBEDDING ===
FILE_SET = [
    {
        "faq_json": "data/FAQ_Tecnaria_JSON_Esteso_Completo.json",
        "embedding_json": "data/FAQ_Tecnaria_JSON_Esteso_Completo_EMBEDDING.json"
    },
    {
        "faq_json": "data/Solaio_Laterocemento_Completo_QA.json",
        "embedding_json": "data/Solaio_Laterocemento_Completo_QA_EMBEDDING.json"
    }
]

SIMILARITY_THRESHOLD = 0.80

# === Caricamento di tutte le FAQ e embedding ===
faq_data = []
faq_embeddings = []

for files in FILE_SET:
    with open(files["faq_json"], "r", encoding="utf-8") as f_json:
        faq_data.extend(json.load(f_json))
    with open(files["embedding_json"], "r", encoding="utf-8") as f_embed:
        faq_embeddings.extend(json.load(f_embed))

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "").strip()

    try:
        # 1. Calcola embedding della domanda utente
        embedding_utente = openai.embeddings.create(
            model="text-embedding-3-small",
            input=user_message
        ).data[0].embedding

        # 2. Cerca la risposta migliore tra tutte le FAQ caricate
        migliore = None
        miglior_score = 0
        for voce in faq_embeddings:
            score = cosine_similarity(embedding_utente, voce["embedding"])
            if score > miglior_score:
                miglior_score = score
                migliore = voce

        if miglior_score >= SIMILARITY_THRESHOLD:
            return jsonify({"response": migliore["risposta"]})

        # 3. Se nessuna FAQ è abbastanza simile, passa a GPT-4o con contesto specializzato
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        risposta = response.choices[0].message.content

    except Exception as e:
        risposta = f"⚠️ Errore nella risposta: {e}"

    return jsonify({"response": risposta})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
