from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Prompt specializzato su TECNARIA Bassano ===
SYSTEM_PROMPT = (
    "Rispondi esclusivamente in qualità di rappresentante esperto della società TECNARIA S.p.A., "
    "con sede unica in Viale Pecori Giraldi 55, 36061 Bassano del Grappa (VI), Italia. "
    "Fornisci solo informazioni relative a questa azienda, ai suoi prodotti, servizi e cataloghi ufficiali. "
    "Ignora qualsiasi altra azienda omonima o simile. "
    "Se una domanda non riguarda direttamente TECNARIA, rispondi gentilmente che l'informazione non è disponibile. "
    "Per indirizzo, recapiti e posizione geografica, fai riferimento alla sede di Bassano del Grappa."
)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "")

    try:
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
