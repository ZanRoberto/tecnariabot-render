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
    risposta_faq, domanda_matchata, punteggio = cerca_faq(user_message)
    if risposta_faq:
        print(f"➡️ Match FAQ: '{domanda_matchata}' (score: {punteggio:.2f})")
        return jsonify({"response": f"📚 Risposta dalle FAQ Tecnaria:\n{risposta_faq}"})

    # Se non trovata nelle FAQ, chiama OpenAI
    print("⏩ Nessun match sufficiente, passo a GPT")
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
    domanda_matchata = None
    punteggio_massimo = 0.6  # soglia più permissiva
    for voce in faq_data:
        domanda = voce["domanda"].lower().strip()
        score = similar(messaggio, domanda)
        if score > punteggio_massimo:
            punteggio_massimo = score
            migliore = voce["risposta"]
            domanda_matchata = domanda
    return migliore, domanda_matchata, punteggio_massimo

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
