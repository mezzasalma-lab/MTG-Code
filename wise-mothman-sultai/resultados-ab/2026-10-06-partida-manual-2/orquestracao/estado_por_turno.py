"""Estado (mao / campo / cemiterio / zona do oponente simulado) ao fim de cada turno, pelo ultimo registro de cada objeto (id). Uso: python3 estado_por_turno.py [dados/partida.json.xz]
Limite: o log registra so' o que mudou; objetos que nunca aparecem estao na biblioteca. Copias de mesmo nome tem ids proprios, EXCETO os basicos (um id por nome neste log)."""
import json, lzma, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(aqui, "..", "dados", "partida.json.xz")
T = json.load(lzma.open(caminho))
est = {}
def ctr(e): return ",".join(f"{k}x{v['count']}" for k, v in sorted((e.get("counters") or {}).items()))
for i, t in enumerate(T, 1):
    for e in t:
        est[e["id"]] = e
    z = {}
    for e in est.values():
        z.setdefault(e["zone"], []).append(e["name"] + ("*" if e["tapped"] else "") + (f"[{ctr(e)}]" if ctr(e) else ""))
    print(f"== fim do T{i} (* = virado)")
    for k in ("battlefield", "hand", "graveyard", "opponentsCards"):
        print(f"  {k:15s} ({len(z.get(k, []))}): " + ", ".join(sorted(z.get(k, []))))
