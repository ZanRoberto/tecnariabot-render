from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
import json
import numpy as np
from difflib import SequenceMatcher
from pathlib import Path

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Costanti ===
FAQ_JSON_PATH = "data/faq_tecnaria.json"
EMBEDDINGS_PATH = "data/faq_embeddings.json"
SIMILARITY_THRESHOLD = 0.80

# === Caricamento FAQ ===
with open(FAQ_JSON_PATH, "r", encoding="utf-8") as f:
    faq_data = json.load(f)

# === Funzioni di supporto ===
def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def genera_embeddings():
    embeddings = []
    for voce in faq_data:
        domanda = voce["domanda"]
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=domanda
        ).data[0].embedding
        embeddings.append({
            "domanda": domanda,
            "risposta": voce["risposta"],
            "embedding": embedding
        })
    with open(EMBEDDINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(embeddings, f, ensure_ascii=False)
    return embeddings

# === Caricamento embeddings ===
if not Path(EMBEDDINGS_PATH).exists():
    faq_embeddings = genera_embeddings()
else:
    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        faq_embeddings = json.load(f)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "")
    if not is_rilevante(user_message):
        return jsonify({"response": "Questo assistente risponde solo su contenuti relativi a Tecnaria."})

    # Genera embedding della domanda
    embedding_utente = client.embeddings.create(
        model="text-embedding-3-small",
        input=user_message
    ).data[0].embedding

    # Confronta con le FAQ semantiche
    migliore = None
    miglior_score = 0
    for voce in faq_embeddings:
        score = cosine_similarity(embedding_utente, voce["embedding"])
        if score > miglior_score:
            miglior_score = score
            migliore = voce

    if miglior_score >= SIMILARITY_THRESHOLD:
        return jsonify({"response": f"📚 Risposta dalle FAQ Tecnaria:\n{migliore['risposta']}"})

    # Altrimenti passa a GPT
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Rispondi solo su argomenti riguardanti Tecnaria. Rifiuta gentilmente domande esterne."},
            {"role": "user", "content": user_message}
        ]
    )
    risposta = response.choices[0].message.content
    return jsonify({"response": f"🤖 Risposta generata da GPT:\n{risposta}"})

def is_rilevante(msg):
    keywords = ["tecnaria", "connettore", "solaio", "omega", "flap", "maxi", "ctf", "ordini", "forniture", "software"]
    msg = msg.lower()
    return any(word in msg for word in keywords)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
