from flask import Flask, render_template, request, jsonify
import openai
import os
from scraper_tecnaria import cerca_online_tecnaria  # ✅ IMPORTA modulo scraping

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Prompt specializzato su TECNARIA Bassano ===
SYSTEM_PROMPT = (
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

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        risposta = response.choices[0].message.content.strip()
    except Exception as e:
        risposta = f"⚠️ Errore: {e}\nCerco online…"
        # 🔁 In caso di errore, prova con scraping
        risposta = cerca_online_tecnaria(user_message)

    # Se risposta vuota o troppo generica, fallback anche a scraping
    if not risposta or "non sono sicuro" in risposta.lower() or "non posso" in risposta.lower():
        risposta = cerca_online_tecnaria(user_message)

    return jsonify({"response": risposta})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
