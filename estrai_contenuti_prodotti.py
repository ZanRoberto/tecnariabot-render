# ✅ File: estrai_contenuti_prodotti.py
# Scarica le pagine di prodotto Tecnaria e ne estrae il testo principale

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

BASE_URL = "https://tecnaria.com"
START_URL = "https://tecnaria.com/prodotti/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Filtra i link validi

def estrai_link_prodotti():
    response = requests.get(START_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/prodotto/" in href:
            link = urljoin(BASE_URL, href)
            links.add(link.split("?")[0])
    return list(links)


def pulisci_testo(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    testo = " ".join(s.strip() for s in soup.stripped_strings)
    testo = re.sub(r"\s+", " ", testo)
    return testo


def estrai_contenuti():
    prodotti = []
    links = estrai_link_prodotti()
    for link in links:
        try:
            res = requests.get(link, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                testo = pulisci_testo(res.text)
                prodotti.append({"url": link, "testo": testo})
        except Exception as e:
            print(f"Errore su {link}: {e}")
    with open("data/prodotti_raw.json", "w", encoding="utf-8") as f:
        json.dump(prodotti, f, ensure_ascii=False, indent=2)
    print(f"✅ Salvati {len(prodotti)} prodotti in prodotti_raw.json")


if __name__ == "__main__":
    estrai_contenuti()


# ✅ File: indicizza_pagine_prodotto.py
# Crea corpus_testuale.json leggibile dal bot da prodotti_raw.json

import json
import os
from pathlib import Path

INPUT_RAW = "data/prodotti_raw.json"
OUTPUT_CORPUS = "data/corpus_testuale.json"


def indicizza():
    if not Path(INPUT_RAW).exists():
        print("❌ File prodotti_raw.json non trovato.")
        return

    with open(INPUT_RAW, "r", encoding="utf-8") as f:
        prodotti = json.load(f)

    corpus = []
    for p in prodotti:
        testo = p.get("testo", "")
        if len(testo) >= 100:
            corpus.append({"testo": testo.strip()[:3000]})

    with open(OUTPUT_CORPUS, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    print(f"✅ Corpus indicizzato con {len(corpus)} elementi.")


if __name__ == "__main__":
    indicizza()
