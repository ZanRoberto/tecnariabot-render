from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "")

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Agisci come esperto ufficiale della Tecnaria S.p.A. "
                    "e rispondi solo su prodotti, soluzioni tecniche, certificazioni, chiodatrici, schede tecniche, contatti, "
                    "e servizi offerti da Tecnaria. Se una domanda non riguarda direttamente Tecnaria, invita l'utente a riformularla."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    risposta = response.choices[0].message.content
    return jsonify({"response": risposta})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
