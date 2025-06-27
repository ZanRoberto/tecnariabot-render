from flask import Flask, render_template, request, jsonify
import openai
import os
from scraper_tecnaria import cerca_online_tecnaria  # modulo scraping

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Prompt specializzato su TECNARIA Bassano ===
BASE_SYSTEM_PROMPT = (
    "Agisci come assistente esperto della società TECNARIA S.p.A., con sede unica in Viale Pecori Giraldi 55, 36061 Bassano del Grappa (VI), Italia. "
    "Rispondi solo in relazione a questa azienda. "
    "Se l'utente menziona aziende omonime, ignorale. "
    "Puoi fornire qualsiasi informazione utile su prodotti, connettori, strumenti, caratteristiche tecniche e dettagli pratici, "
    "anche se non presente nei cataloghi, purché sia riferita a Tecnaria S.p.A. "
)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message", "").strip()

    # 🧠 Recupera info dal sito Tecnaria (scraping mirato)
    contesto_scraping = cerca_online_tecnaria(user_message, max_url=3)
    print("\n--- CONTENUTO DA SCRAPING ---\n", contesto_scraping[:1000], "\n-----------------------------")

    # 🔒 Protezione se scraping vuoto o fallito
    if not contesto_scraping or "Errore" in contesto_scraping or "Nessuna informazione" in contesto_scraping:
        contesto_scraping = (
            "⚠️ Nessun contenuto trovato nel sito Tecnaria. Rispondi solo in base alle informazioni note su Tecnaria S.p.A."
        )

    # 🔁 Costruzione del prompt completo
    system_prompt = (
        BASE_SYSTEM_PROMPT +
        "\n\nInformazioni raccolte dal sito Tecnaria:\n" +
        contesto_scraping +
        "\n\nRispondi nel limite di queste informazioni. Non dire mai 'visita il sito'."
    )

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
