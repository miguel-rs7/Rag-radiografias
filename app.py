
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

# Guardar conversación y resultados
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "contexto" not in st.session_state:
    st.session_state.contexto = None

archivo = st.file_uploader("Sube una radiografía", type=["png", "jpg", "jpeg"])

if st.button("Buscar imágenes similares"):
    if archivo is None:
        st.warning("Primero sube una radiografía.")
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
                st.session_state.contexto = None
            else:
                st.session_state.contexto = "\n".join(
                    f"Imagen: {id_}; etiqueta: {diagnostico}; distancia: {distancia}"
                    for id_, diagnostico, distancia in resultados
                )
                st.session_state.mensajes = []

                st.subheader("Imágenes similares")
                for id_, diagnostico, distancia in resultados:
                    st.write(
                        f"**{id_}** — Etiqueta: {diagnostico} "
                        f"— Distancia: {distancia}"
                    )

                st.success("¡Listo! Ya puedes hacer preguntas en el chat.")

        except Exception as e:
            st.error(f"Error durante la búsqueda: {e}")
        finally:
            if ruta and os.path.exists(ruta):
                os.remove(ruta)

# Mostrar conversación anterior
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.write(mensaje["content"])

# Campo para seguir preguntando
if st.session_state.contexto:
    pregunta = st.chat_input("Escribe tu pregunta sobre las imágenes...")

    if pregunta:
        st.session_state.mensajes.append(
            {"role": "user", "content": pregunta}
        )

        with st.chat_message("user"):
            st.write(pregunta)

        historial = "\n".join(
            f"{'Usuario' if m['role'] == 'user' else 'Asistente'}: {m['content']}"
            for m in st.session_state.mensajes
        )

        prompt = f"""
Eres un chatbot educativo especializado en radiografías de tórax
y recuperación de imágenes similares.

Responde en español, de forma clara, natural y conversacional.
Ten en cuenta el historial para responder preguntas de seguimiento.
Utiliza las etiquetas recuperadas como referencias de una base de datos,
no como diagnóstico de la radiografía subida.
Explica los términos técnicos con palabras sencillas.
Una distancia menor indica mayor similitud dentro de este sistema.
No inventes hallazgos médicos ni presentes tus respuestas como diagnóstico.
Si no tienes información suficiente, dilo claramente.
Termina con una invitación breve a continuar la conversación.

Imágenes similares recuperadas:
{st.session_state.contexto}

Historial de la conversación:
{historial}

Responde a la última pregunta del usuario.
"""

        try:
            with st.chat_message("assistant"):
                with st.spinner("Gemini está preparando la respuesta..."):
                    cliente = genai.Client(api_key=api_key)
                    respuesta = cliente.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=prompt
                    )

                    texto = respuesta.text or "No se pudo generar una respuesta."
                    st.write(texto)

            st.session_state.mensajes.append(
                {"role": "assistant", "content": texto}
            )

        except Exception as e:
            st.error(f"Error durante la consulta: {e}")

