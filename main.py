from flask import Flask, render_template, request, jsonify
import openai
import os
from scraper_tecnaria import cerca_online_tecnaria
from chat_corpus_local import trova_contesto_rilevante  # ✅ nuovo modulo integrato

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

BASE_SYSTEM_PROMPT = (
    "Agisci come assistente esperto della società TECNARIA S.p.A., con sede unica in Viale Pecori Giraldi 55, 36061 Bassano del Grappa (VI), Italia. "
    "Concentrati esclusivamente su questa azienda e sui suoi prodotti e servizi. "
    "Se l'utente menziona altre aziende omonime, ignorale. "
    "Puoi fornire qualsiasi informazione utile su prodotti, usi, caratteristiche tecniche e dettagli pratici, "
    "anche se non presente nei cataloghi, purché rilevante per Tecnaria S.p.A. "
)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "").strip()

    # 1️⃣ Cerca prima nel corpus locale
    contesto_corpus = trova_contesto_rilevante(user_message)
    contesto_locale = contesto_corpus[0] if contesto_corpus else ""

    # 2️⃣ Se il contesto locale è troppo generico, fai scraping
    if not contesto_locale or len(contesto_locale) < 100:
        contesto_locale = cerca_online_tecnaria(user_message)

    # 3️⃣ Unisci prompt e contesto
    prompt = BASE_SYSTEM_PROMPT + "\n\nContesto rilevante:\n" + contesto_locale

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ]
        )
        risposta = response.choices[0].message.content.strip()
    except Exception as e:
        risposta = f"⚠️ Errore nella risposta: {e}\n\nContesto:\n{contesto_locale}"

    return jsonify({"response": risposta})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
