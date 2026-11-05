"""E/S dos resultados brutos por partida: {variante: [dict por semente]} <-> arquivo .json.xz em formato de colunas
({"variantes": {nome: {"n": N, "campos": {campo: [valor por semente]}}}}), que comprime ~20x melhor que lista de dicts."""
import json
import lzma


def salvar_raw(caminho_sem_ext, mapa):
    out = {"formato": "colunas-v1", "variantes": {}}
    for nome, rs in mapa.items():
        campos = {}
        for k in (rs[0].keys() if rs else []):
            campos[k] = [r[k] for r in rs]
        out["variantes"][str(nome)] = {"n": len(rs), "campos": campos}
    with lzma.open(caminho_sem_ext + ".json.xz", "wt", preset=9) as f:
        f.write(json.dumps(out, separators=(",", ":")))


def carregar_raw(caminho_sem_ext):
    with lzma.open(caminho_sem_ext + ".json.xz", "rt") as f:
        d = json.load(f)
    mapa = {}
    for nome, v in d["variantes"].items():
        ks = list(v["campos"].keys())
        mapa[nome] = [{k: v["campos"][k][i] for k in ks} for i in range(v["n"])]
    return mapa
