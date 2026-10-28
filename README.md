# RAG de radiografías de tórax

Búsqueda de radiografías similares con base vectorial (ChromaDB, distancia coseno)
y base SQL (SQLite), usando embeddings multimodales de Gemini Embedding 2.
Dataset: Chest X-Ray Pneumonia (Kaggle).

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/miguel-rs7/rag-radiografias/blob/main/Github.ipynb)

## Resultados
- 200 radiografías indexadas (100 normales, 100 con neumonía), 768 dimensiones.
- Evaluación con 50 imágenes de test (voto de los 5 vecinos más cercanos): **94 % de acierto**.
- Es una prueba de concepto con muestra pequeña, no una validación clínica.

## Arquitectura
Radiografía → Gemini Embedding 2 → ChromaDB (coseno) → ids similares → SQLite (diagnóstico)

## Cómo ejecutarlo
1. Pulsa el botón "Open in Colab".
2. Guarda tu clave en Secretos de Colab como `GEMINI_API_KEY` y activa el acceso al notebook.
3. Ejecuta las celdas en orden.

## Estructura
- `src/config.py`: parámetros
- `src/db.py`: ChromaDB + SQLite
- `src/embeddings.py`: Gemini Embedding 2
- `src/rag.py`: indexar, buscar, evaluar
- `Github.ipynb`: notebook de ejecución

## Entorno
Google Colab (CPU), bases guardadas en Google Drive, claves en Secretos de Colab.
