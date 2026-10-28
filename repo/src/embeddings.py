import io, time
from PIL import Image
from google import genai
from google.genai import types
from .config import MODELO, DIM

client = None

def iniciar(api_key):
    global client
    client = genai.Client(api_key=api_key)

def embed(ruta):
    img = Image.open(ruta).convert("RGB")
    img.thumbnail((768, 768))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    parte = types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg")

    for intento in range(3):
        try:
            r = client.models.embed_content(
                model=MODELO, contents=[parte],
                config=types.EmbedContentConfig(output_dimensionality=DIM))
            return r.embeddings[0].values
        except Exception as e:
            print("Error:", str(e)[:150])
            time.sleep(5 * (intento + 1))
    return None
