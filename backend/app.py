#!/usr/bin/env python3
"""
TEKNARIA V3 - Backend FastAPI
Integration of:
- OVERTOP V15 (Teknaria Engine)
- COVOLO (Operational structure)
- SINAPSI GOLD (LLM + KB routing)
- HERMENEUTICA (Financial analysis narrative)
"""

import os
import json
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
BACKEND_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
DB_PATH = BASE_DIR / "teknaria.db"
UPLOAD_DIR = BASE_DIR / "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

MASTER_PASSWORD = os.getenv("MASTER_PASSWORD", "ZANNA1959")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

class LoginRequest(BaseModel):
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: str

app = FastAPI(title="Teknaria V3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS cassetti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT UNIQUE NOT NULL,
            descrizione TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS bilanci (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cassetto_id INTEGER NOT NULL,
            anno INTEGER NOT NULL,
            file_path TEXT,
            dati_estratti TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(cassetto_id) REFERENCES cassetti(id)
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS analisi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bilancio_id INTEGER NOT NULL,
            capsule TEXT,
            narrativa TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(bilancio_id) REFERENCES bilanci(id)
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE,
            expires_at TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

def verify_token(token: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM sessions WHERE token = ?", (token,))
    result = c.fetchone()
    conn.close()
    return result is not None

@app.post("/api/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    if req.password != MASTER_PASSWORD:
        raise HTTPException(status_code=401, detail="Password scorretta")
    
    token = os.urandom(16).hex()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (token) VALUES (?)", (token,))
    conn.commit()
    conn.close()
    
    return LoginResponse(success=True, token=token)

@app.get("/api/cassetti")
async def get_cassetti(token: str):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Token non valido")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nome_cliente, descrizione FROM cassetti")
    cassetti = [{"id": row[0], "nome": row[1], "descrizione": row[2]} for row in c.fetchall()]
    conn.close()
    
    return cassetti

@app.post("/api/cassetti")
async def create_cassetto(nome_cliente: str, token: str):
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Token non valido")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO cassetti (nome_cliente, descrizione) VALUES (?, ?)",
                  (nome_cliente, ""))
        conn.commit()
        cassetto_id = c.lastrowid
        conn.close()
        return {"success": True, "cassetto_id": cassetto_id}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Cassetto già esiste")

@app.get("/api/status")
async def status():
    return {
        "status": "Teknaria V3 online",
        "db": "SQLite",
        "openai": "disponibile" if OPENAI_API_KEY else "non configurato"
    }

@app.get("/")
async def root():
    index = BASE_DIR / "frontend" / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Teknaria V3 - Backend running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
