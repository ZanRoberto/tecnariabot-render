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
    if not is_rilevante(user_message):
        return jsonify({"response": "Questo assistente risponde solo su contenuti relativi a Tecnaria."})

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
