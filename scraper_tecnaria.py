import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def cerca_online_tecnaria(domanda, max_url=1):
    query = f"site:tecnaria.com {domanda}"
    url = f"https://www.google.com/search?q={quote_plus(query)}"

    try:
        # Richiesta a Google Search
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        # Trova i link risultati
        risultati = []
        for a in soup.select("a"):
            href = a.get("href")
            if href and "/url?q=" in href and "tecnaria.com" in href:
                link = href.split("/url?q=")[1].split("&sa=")[0]
                if link not in risultati:
                    risultati.append(link)
            if len(risultati) >= max_url:
                break

        # Recupera contenuto dal primo risultato
        if risultati:
            testo = estrai_testo_da_url(risultati[0])
            return testo
        else:
            return "(Nessuna informazione trovata sul sito tecnaria.com)"

    except Exception as e:
        return f"(Errore nello scraping: {e})"

def estrai_testo_da_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Rimuove script e stile
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # Raccoglie il testo visibile
        testo = " ".join(chunk.strip() for chunk in soup.stripped_strings)

        # Pulizia base
        testo = re.sub(r"\s+", " ", testo)
        return testo[:3000]  # massimo 3000 caratteri per contesto

    except Exception as e:
        return f"(Errore nel recupero contenuto: {e})"

# Esempio uso manuale
if __name__ == "__main__":
    domanda = "Che chiodatrici vende Tecnaria?"
    print(cerca_online_tecnaria(domanda))
