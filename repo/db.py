import os, sqlite3, chromadb
from .config import BASE, COLECCION

def conectar():
    os.makedirs(BASE, exist_ok=True)
    chroma = chromadb.PersistentClient(path=f"{BASE}/chroma")
    col = chroma.get_or_create_collection(COLECCION, metadata={"hnsw:space": "cosine"})
    db = sqlite3.connect(f"{BASE}/radiologia.db")
    db.execute("""CREATE TABLE IF NOT EXISTS estudios (
        id TEXT PRIMARY KEY, ruta TEXT NOT NULL,
        diagnostico TEXT NOT NULL, split TEXT)""")
    return col, db
