from flask import Flask, render_template, request, jsonify
import openai
import os
from scraper_tecnaria import cerca_online_tecnaria  # ✅ IMPORTA modulo scraping

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

BASE_SYSTEM_PROMPT = (
    "Agisci come assistente ufficiale della società TECNARIA S.p.A., con sede unica in Viale Pecori Giraldi 55, 36061 Bassano del Grappa (VI), Italia. "
    "Rispondi solo su prodotti, servizi e contenuti reali riconducibili a questa azienda. "
    "Ignora qualsiasi riferimento ad aziende con nome simile o contenuti non verificabili su tecnaria.com. "
    "Mantieni un tono tecnico, chiaro e professionale. "
)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "").strip()

    # 🔍 Scraping mirato su tecnaria.com
    contesto_scraping = cerca_online_tecnaria(user_message)
    print("\n📎 CONTENUTO SCRAPING TECNARIA:\n", contesto_scraping[:1000], "\n---")  # Debug console (max 1000 char)

    # 🔧 Integrazione nel prompt
    system_prompt = BASE_SYSTEM_PROMPT + "\n\n--- CONTENUTO TECNARIA.COM ---\n" + contesto_scraping + "\n---"

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        risposta = response.choices[0].message.content.strip()
    except Exception as e:
        risposta = f"⚠️ Errore nella risposta: {e}\n\nContesto trovato:\n{contesto_scraping}"

    return jsonify({"response": risposta})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
