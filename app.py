import os
import tempfile
import streamlit as st
from google import genai
from src import embeddings
from src.db import conectar
from src.rag import buscar

st.set_page_config(page_title="Chatbot de radiografías", page_icon="🩻")
st.title("Chatbot educativo de radiografías de tórax")
st.warning("Proyecto educativo; no sustituye la evaluación de un profesional médico.")

api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not api_key:
    st.error("Configura GEMINI_API_KEY en Streamlit Cloud → Settings → Secrets.")
    st.stop()

@st.cache_resource
def iniciar():
    embeddings.iniciar(api_key)
    return conectar()

try:
    col, db = iniciar()
except Exception as e:
    st.error(f"No se pudo abrir la base RAG: {e}")
    st.stop()

archivo = st.file_uploader("Sube una radiografía", type=["png", "jpg", "jpeg"])
pregunta = st.text_input("¿Qué quieres saber sobre las imágenes similares?")

if st.button("Buscar y preguntar"):
    if archivo is None:
        st.warning("Primero sube una radiografía.")
    elif not pregunta.strip():
        st.warning("Escribe una pregunta.")
    else:
        ruta = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                f.write(archivo.getvalue())
                ruta = f.name

            with st.spinner("Buscando imágenes similares..."):
                resultados = buscar(col, db, ruta, k=5)

            if not resultados:
                st.info("No se encontraron resultados.")
            else:
                st.subheader("Imágenes similares")
                contexto = []

                for id_, diagnostico, distancia in resultados:
                    st.write(f"**{id_}** — Etiqueta: {diagnostico} — Distancia: {distancia}")
                    contexto.append(
                        f"Imagen: {id_}; etiqueta: {diagnostico}; distancia: {distancia}"
                    )

prompt = f"""
Eres un chatbot educativo especializado en explicar información
sobre radiografías de tórax y recuperación de imágenes similares.

Tu función es responder las preguntas del usuario de forma
clara, natural y conversacional.

Utiliza las etiquetas recuperadas como referencias de una base
de datos. No afirmes que esas etiquetas describen necesariamente
la radiografía que acaba de subir el usuario.

Reglas:
- Responde directamente a la pregunta del usuario.
- Explica los términos técnicos con palabras sencillas.
- Si aparecen etiquetas NORMAL y PNEUMONIA, explica que la
  base recuperó imágenes con ambas etiquetas.
- Explica que una distancia menor indica mayor similitud
  dentro de este sistema de búsqueda.
- No inventes características visuales ni resultados médicos.
- No presentes la búsqueda como un diagnóstico.
- Si los resultados no permiten responder, dilo claramente.
- Si el usuario hace una pregunta general relacionada con
  las etiquetas, puedes explicar su significado educativo.

Imágenes similares recuperadas:
{chr(10).join(contexto)}

Pregunta del usuario:
{pregunta}

Redacta una respuesta completa, clara y útil. No te limites
a enumerar las etiquetas.
"""
                with st.spinner("Gemini está preparando la respuesta..."):
                    cliente = genai.Client(api_key=api_key)
                    respuesta = cliente.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt
                    )

                st.subheader("Respuesta")
                st.write(respuesta.text)

        except Exception as e:
            st.error(f"Error durante la consulta: {e}")
        finally:
            if ruta and os.path.exists(ruta):
                os.remove(ruta)
