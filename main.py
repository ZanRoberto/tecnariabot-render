from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
import json
from difflib import SequenceMatcher

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Carica il file JSON delle FAQ
with open("data/faq_tecnaria.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "")
    if not is_rilevante(user_message):
        return jsonify({"response": "Questo assistente risponde solo su contenuti relativi a Tecnaria."})

    # Cerca risposta nelle FAQ con similarità
    risposta_faq = cerca_faq(user_message)
    if risposta_faq:
        return jsonify({"response": f"📚 Risposta dalle FAQ Tecnaria:\n{risposta_faq}"})

    # Se non trovata nelle FAQ, chiama OpenAI
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

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def cerca_faq(messaggio):
    messaggio = messaggio.lower().strip()
    migliore = None
    punteggio_massimo = 0.7  # soglia di similarità
    for voce in faq_data:
        domanda = voce["domanda"].lower().strip()
        score = similar(messaggio, domanda)
        if score > punteggio_massimo:
            punteggio_massimo = score
            migliore = voce["risposta"]
    return migliore

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
