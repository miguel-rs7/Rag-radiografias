import os

MODELO = "gemini-embedding-2"
DIM = 768
BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "radiologia"
)
COLECCION = "rx_gemini"
