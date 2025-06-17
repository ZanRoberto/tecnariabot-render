from flask import Flask, render_template, request, jsonify
import openai
import os
import json

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

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

    # Cerca risposta nelle FAQ
    risposta_faq = cerca_faq(user_message)
    if risposta_faq:
        return jsonify({"response": risposta_faq})

    # Se non trovata nelle FAQ, chiama OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Rispondi solo su argomenti riguardanti Tecnaria. Rifiuta gentilmente domande esterne."},
            {"role": "user", "content": user_message}
        ]
    )
    return jsonify({"response": response["choices"][0]["message"]["content"]})

def is_rilevante(msg):
    keywords = ["tecnaria", "connettore", "solaio", "omega", "flap", "maxi", "ctf", "ordini", "forniture", "software"]
    msg = msg.lower()
    return any(word in msg for word in keywords)

def cerca_faq(messaggio):
    messaggio = messaggio.lower().strip()
    for voce in faq_data:
        domanda = voce["domanda"].lower().strip()
        if domanda in messaggio or messaggio in domanda:
            return voce["risposta"]
    return None

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
