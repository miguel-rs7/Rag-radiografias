# RAG de radiografías de tórax

Base vectorial (ChromaDB, coseno) + SQL (SQLite) con embeddings de Gemini Embedding 2.
Dataset: Chest X-Ray Pneumonia (Kaggle).

## Uso en Google Colab
1. Guarda tu clave en Secretos de Colab como `GEMINI_API_KEY` (con acceso al notebook activado).
2. Abre `notebook.ipynb` en Colab y ejecuta las celdas en orden.

## Estructura
- `src/config.py`: parámetros
- `src/db.py`: ChromaDB + SQLite
- `src/embeddings.py`: Gemini Embedding 2
- `src/rag.py`: indexar, buscar, evaluar
