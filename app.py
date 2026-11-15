import streamlit as st

st.set_page_config(
    page_title="Chatbot de radiografías",
    page_icon="🩻",
    layout="wide"
)

st.title("Chatbot educativo de radiografías de tórax")
st.write(
    "Busca radiografías similares y consulta sus etiquetas mediante Gemini. "
    "No sustituye una evaluación médica."
)

st.info(
    "Esta interfaz necesita conectarse a la base vectorial y a Gemini "
    "mediante las funciones y credenciales configuradas en el proyecto."
)

archivo = st.file_uploader(
    "Sube una radiografía de tórax",
    type=["png", "jpg", "jpeg"]
)

pregunta = st.text_input(
    "¿Qué quieres saber sobre los resultados?"
)

if st.button("Buscar y consultar"):
    if archivo is None:
        st.warning("Primero debes subir una radiografía.")
    elif not pregunta.strip():
        st.warning("Escribe una pregunta.")
    else:
        st.warning(
            "Falta conectar aquí la función buscar(), la base vectorial "
            "y la llamada a Gemini para ejecutar el flujo completo."
        )
