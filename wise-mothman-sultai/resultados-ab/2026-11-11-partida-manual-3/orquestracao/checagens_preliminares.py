"""Checagens preliminares da partida manual #3 do Wise Mothman, antes das respostas do usuario (so o que o log e o oraculo provam).
Uso: python3 -I checagens_preliminares.py   (saida em texto). Cada item diz o que o log PROVA e o que depende de leitura minha."""
import json, lzma, os, re
aqui = os.path.dirname(os.path.abspath(__file__))
T = json.load(lzma.open(os.path.join(aqui, "..", "dados", "partida.json.xz")))
C = json.load(open(os.path.join(aqui, "..", "..", "..", "..", "scryfall-cache", "oracle-cache.json")))
tipo = lambda n: C[n]["type_line"] if n in C else "?"
def cores_do_terreno(n):
    t = C[n].get("oracle_text") or ""
    base = {"Forest": "G", "Island": "U", "Swamp": "B", "Mountain": "R", "Plains": "W"}
    s = {base[x] for x in base if x in tipo(n)}
    s |= set(re.findall(r"\{T\}: Add \{([WUBRG])\}", t))
    return s
print("== 1) T4: The Wise Mothman", C["The Wise Mothman"]["mana_cost"], "x fontes viradas no T4")
v4 = [r["name"] for r in T[3] if r["tapped"] and r["zone"] == "battlefield" and "Land" in tipo(r["name"]) and r["toZone"] is None]
cores = set()
for n in v4:
    cores |= cores_do_terreno(n)
print("  terrenos virados no T4:", v4, "| cores possiveis:", sorted(cores), "| B disponivel:", "B" in cores)
print("  Plaza de Heroes estava na mao no T4 (foi descartada pela Dark Deal):", any(r["name"] == "Plaza of Heroes" and r["toZone"] == "graveyard" for r in T[3]))
print("== 2) T4: Dark Deal ->", C["Dark Deal"]["oracle_text"].replace("\n", " / "))
descartes = [r["name"] for r in T[3] if r["fromZone"] == "hand" and r["toZone"] == "graveyard"]
compras = [r["name"] for r in T[3] if r["fromZone"] == "library" and r["toZone"] == "hand"]
idx_dd = [j for j, r in enumerate(T[3]) if r["name"] == "Dark Deal"][0]
depois = [r["name"] for j, r in enumerate(T[3]) if j > idx_dd and r["fromZone"] == "library" and r["toZone"] == "hand"]
print(f"  descartou {len(descartes)} ({', '.join(descartes)}); comprou {len(depois)} depois ({', '.join(depois)}); esperado {len(descartes) - 1}")
print("== 3) T6: cartas do cemiterio que foram para a MAO (Evolution Witness: 'target permanent card')")
for j, r in enumerate(T[5]):
    if r["fromZone"] == "graveyard" and r["toZone"] in ("hand", "battlefield"):
        print(f"  idx {j}: {r['name']} -> {r['toZone']} | tipo: {tipo(r['name'])} | permanente: {'Instant' not in tipo(r['name']) and 'Sorcery' not in tipo(r['name'])}")
print("== 4) jogadas de terreno por turno (objetos distintos, mao->campo e cemiterio->campo)")
for i, t in enumerate(T, 1):
    mao = list(dict.fromkeys(r["name"] + "#" + r["id"][:4] for r in t if r["fromZone"] == "hand" and r["toZone"] == "battlefield" and "Land" in tipo(r["name"])))
    cem = list(dict.fromkeys(r["name"] + "#" + r["id"][:4] for r in t if r["fromZone"] == "graveyard" and r["toZone"] == "battlefield" and "Land" in tipo(r["name"])))
    print(f"  T{i}: da mao {mao or '-'} | do cemiterio {cem or '-'}")
print("== 5) mill proprio (library->graveyard) por turno: o rad exige 1 por contador no inicio da fase principal 1")
for i, t in enumerate(T, 1):
    print(f"  T{i}: {[r['name'] for r in t if r['fromZone'] == 'library' and r['toZone'] == 'graveyard'] or '-'}")
print("== 6) contadores +1/+1 por turno (ultimo valor por criatura)")
ult = {}
for i, t in enumerate(T, 1):
    for r in t:
        if "+1 / +1" in r["counters"]:
            ult.setdefault(r["name"], {})[i] = r["counters"]["+1 / +1"]["count"]
for n, d in ult.items():
    print(f"  {n}: {d}")
