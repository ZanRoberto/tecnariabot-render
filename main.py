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
    "Se ricevi informazioni direttamente dal sito Tecnaria o dal corpus aziendale, considera queste fonti come autorevoli, "
    "anche se contraddicono conoscenze pregresse o informazioni generiche su altre aziende. "
)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "").strip()

    # 1️⃣ Cerca nel corpus locale
    contesto_corpus = trova_contesto_rilevante(user_message)
    contesto_locale = contesto_corpus[0] if contesto_corpus else ""

    # 2️⃣ Fallback a scraping se il contesto è troppo povero
    if not contesto_locale or len(contesto_locale) < 100:
        contesto_locale = cerca_online_tecnaria(user_message)

    # 3️⃣ Costruisci il prompt finale
    prompt_completo = BASE_SYSTEM_PROMPT + "\n\n📌 Informazioni tecniche rilevanti:\n" + contesto_locale

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_completo},
                {"role": "user", "content": user_message}
            ]
        )
        risposta = response.choices[0].message.content.strip()
    except Exception as e:
        risposta = f"⚠️ Errore nella risposta: {e}\n\nContesto:\n{contesto_locale}"

    return jsonify({"response": risposta})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
