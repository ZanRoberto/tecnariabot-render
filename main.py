from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
import json
import numpy as np
from difflib import SequenceMatcher
from pathlib import Path
import fitz  # PyMuPDF per lettura PDF

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Costanti ===
FAQ_JSON_PATH = "data/faq_tecnaria.json"
EMBEDDINGS_PATH = "data/faq_embeddings.json"
SIMILARITY_THRESHOLD = 0.80
PDF_PATHS = [
    "data/cataloghi/CT_C_CATALOGO_IT.pdf",
    "data/cataloghi/CT_L_CATALOGO_IT.pdf",
    "data/cataloghi/CT_F_CATALOGO_IT.pdf",
    "data/cataloghi/CT_LISTINI_IT.pdf"
]

# === Caricamento FAQ ===
with open(FAQ_JSON_PATH, "r", encoding="utf-8") as f:
    faq_data = json.load(f)

# === Mappa immagini ===
mappa_immagini = {
    "acciaio": "Connettori-acciaio-510x510.jpg",
    "legno base": "3.1.3_001_connettori_solai_legno_base-510x510.jpg"
}

def cerca_immagine(messaggio):
    msg = messaggio.lower()
    for chiave, file_img in mappa_immagini.items():
        if chiave in msg:
            return f"<br><img src='/static/img/{file_img}' alt='{chiave}' style='max-width:100%; margin-top:10px;'>"
    return ""

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

# === Cerca nei cataloghi PDF ===
def cerca_nei_cataloghi(domanda):
    risultati = []
    for percorso in PDF_PATHS:
        nome = percorso.split("/")[-1]
        try:
            with fitz.open(percorso) as pdf:
                for pagina in pdf:
                    testo = pagina.get_text()
                    if domanda.lower() in testo.lower():
                        risultati.append({
                            "file": nome,
                            "pagina": pagina.number + 1,
                            "estratto": testo.strip()[:500]
                        })
        except Exception as e:
            risultati.append({"file": nome, "pagina": 0, "estratto": f"Errore: {e}"})
    return risultati

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "")

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
        immagine = cerca_immagine(user_message)
        return jsonify({"response": f"📚 Risposta dalle FAQ Tecnaria:<br>{migliore['risposta']}{immagine}"})

    # Cerca anche nei PDF
    risultati_pdf = cerca_nei_cataloghi(user_message)
    if risultati_pdf:
        r = risultati_pdf[0]
        immagine = cerca_immagine(user_message)
        return jsonify({"response": f"📄 Trovato in <b>{r['file']}</b> (pagina {r['pagina']}):<br><br>{r['estratto']}{immagine}"})

    # Altrimenti passa a GPT
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Rispondi esclusivamente su contenuti relativi all’azienda TECNARIA. Se una domanda riguarda altri marchi o prodotti non correlati, rifiuta gentilmente e invita a riformulare."},
            {"role": "user", "content": user_message}
        ]
    )
    risposta = response.choices[0].message.content
    immagine = cerca_immagine(user_message)
    return jsonify({"response": f"{risposta}{immagine}"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
