import os, glob
from .embeddings import embed

def id_de(ruta):
    return f"{os.path.basename(os.path.dirname(ruta))}_{os.path.splitext(os.path.basename(ruta))[0]}"

def muestra(path, split, n):
    rutas = []
    for clase in ["NORMAL", "PNEUMONIA"]:
        rutas += sorted(glob.glob(f"{path}/**/{split}/{clase}/*.jpeg", recursive=True))[:n]
    return rutas

def indexar(col, db, rutas, split):
    ya = set(col.get(ids=[id_de(p) for p in rutas])["ids"])
    pendientes = [p for p in rutas if id_de(p) not in ya]
    print(f"{len(ya)} ya indexadas, {len(pendientes)} pendientes")

    for i, ruta in enumerate(pendientes, 1):
        vec = embed(ruta)
        if vec is None:
            print("Falló, se detiene:", ruta)
            return
        id_, clase = id_de(ruta), os.path.basename(os.path.dirname(ruta))
        db.execute("INSERT OR REPLACE INTO estudios (id, ruta, diagnostico, split) VALUES (?,?,?,?)",
                   (id_, ruta, clase, split))
        col.add(ids=[id_], embeddings=[vec], metadatas=[{"clase": clase}])
        db.commit()
        if i % 10 == 0:
            print(f"  {i}/{len(pendientes)}")

def buscar(col, db, ruta_imagen, k=5):
    r = col.query(query_embeddings=[embed(ruta_imagen)], n_results=k)
    resultados = []
    for id_, dist in zip(r["ids"][0], r["distances"][0]):
        diag = db.execute("SELECT diagnostico FROM estudios WHERE id=?", (id_,)).fetchone()[0]
        resultados.append((id_, diag, round(dist, 3)))
    return resultados

def evaluar(col, db, rutas_test, k=5):
    aciertos = 0
    for p in rutas_test:
        real = os.path.basename(os.path.dirname(p))
        votos = [diag for _, diag, _ in buscar(col, db, p, k)]
        aciertos += max(set(votos), key=votos.count) == real
    return aciertos / len(rutas_test)
