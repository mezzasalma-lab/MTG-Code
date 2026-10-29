"""Trace e verificações automáticas de uma partida manual do Archidekt playtester (Tom Bombadil).
Uso: python3 analisa_partida.py [dados/partida.json.xz]   (saída em Markdown no stdout)
Cada elemento do JSON é um turno (rodada: meu turno + o do oponente); cada registro é o estado de um objeto
quando ele mudou (zona, virada, marcadores). `opponentsCards` = interação que o usuário põe contra si (simulação).
As verificações automáticas cobrem só o que o log permite provar (terrenos, fetch, marcadores de saber, gatilho do Tom);
custo de mana e ordem da pilha NÃO são verificáveis só pelo log (ver o LEIAME e o goldfish-log).
Saída final separa VIOLAÇÃO PROVADA (o log contradiz a regra) de ANOMALIA SEM FONTE (o log mostra um estado que nenhuma carta
da lista explica, típico de ajuste manual/desfazer do playtester: não prova erro de jogo)."""
import json
import lzma
import os
import re
import sys
from collections import defaultdict

aqui = os.path.dirname(os.path.abspath(__file__))
caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(aqui, "dados", "partida.json.xz")
T = json.load(lzma.open(caminho) if caminho.endswith(".xz") else open(caminho))
CACHE = os.path.join(aqui, "..", "..", "..", "scryfall-cache", "oracle-cache.json")
try:
    ORC = json.load(open(CACHE))
except Exception:
    ORC = {}
ROM = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6}


def oraculo(n):
    e = ORC.get(n) or ORC.get(n.split(" // ")[0]) or {}
    if e.get("card_faces"):
        return e["card_faces"][0].get("oracle_text") or ""
    return e.get("oracle_text") or ""


def capitulo_final(n):
    """maior número romano que abre uma linha de capítulo no oráculo (ex.: 'I, II — ...' -> 2); 0 se não for Saga."""
    e = ORC.get(n) or ORC.get(n.split(" // ")[0]) or {}
    tl = (e.get("type_line") or "") + " ".join(f.get("type_line") or "" for f in e.get("card_faces", [])[:1])
    if "Saga" not in tl:
        return 0
    mx = 0
    for ln in oraculo(n).split("\n"):
        m = re.match(r"^((?:[IVX]+)(?:, [IVX]+)*) [—-]", ln)
        if m:
            mx = max([mx] + [ROM[x] for x in m.group(1).split(", ") if x in ROM])
    return mx


NOMES = sorted({e["name"] for t in T for e in t})
FINAL = {n: capitulo_final(n) for n in NOMES if capitulo_final(n)}   # capítulo final lido do oráculo ao vivo (cache)
FETCH = {n for n in NOMES if "Land" in ((ORC.get(n) or {}).get("type_line") or "") and "Saga" not in ((ORC.get(n) or {}).get("type_line") or "")
         and "Search your library" in oraculo(n) and "Sacrifice this land" in oraculo(n)}


def is_land(n):
    e = ORC.get(n) or ORC.get(n.split(" // ")[0]) or {}
    return "Land" in (e.get("type_line") or "")


def lore(e):
    return (e["counters"].get("Lore") or {}).get("count", 0)


print("## Trace por turno (mudanças de zona e fichas; `∅` = origem fora de jogo)\n")
for i, t in enumerate(T, 1):
    print(f"**T{i}**")
    for e in t:
        fz, tz = e["fromZone"], e["toZone"]
        if not (fz or tz):
            continue
        tag = " [ficha]" if e["token"] else (" [cópia]" if e["tokenCopy"] else "")
        cn = ", ".join(f"{k}={v['count']}" for k, v in e["counters"].items())
        print(f"- {e['name']}{tag}: {fz or '∅'} → {tz}" + (f" ({cn})" if cn else "") + (" · entra virado" if e["tapped"] and tz == "battlefield" and fz else ""))
    print()

print("## Verificações automáticas\n")
viol = []          # o log contradiz a regra (prova)
anom = []          # estado do log que nenhuma carta da lista explica (não prova erro de jogo)
# 1) terrenos jogados da mão por turno
print("| turno | terrenos jogados da mão | saiu por fetch | veredito |")
print("|---|---|---|---|")
for i, t in enumerate(T, 1):
    drops = [e["name"] for e in t if e["fromZone"] == "hand" and e["toZone"] == "battlefield" and is_land(e["name"])]
    fetched = [e["name"] for e in t if e["fromZone"] == "library" and e["toZone"] == "battlefield" and is_land(e["name"])]
    bad = len(drops) > 1
    if bad:
        viol.append(f"T{i}: {len(drops)} terrenos jogados da mão")
    print(f"| T{i} | {', '.join(drops) or '—'} | {', '.join(fetched) or '—'} | {'**VIOLA (mais de 1)**' if bad else 'ok'} |")
# 2) cada fetchland jogado foi pro cemitério e buscou um terreno no mesmo turno
print()
for i, t in enumerate(T, 1):
    for f in sorted(FETCH):
        jog = any(e["name"] == f and e["fromZone"] == "hand" and e["toZone"] == "battlefield" for e in t)
        if jog:
            gy = any(e["name"] == f and e["toZone"] == "graveyard" for e in t)
            busca = any(e["fromZone"] == "library" and e["toZone"] == "battlefield" and is_land(e["name"]) for e in t)
            if not (gy and busca):
                viol.append(f"T{i}: {f} sem cemitério/busca")
            print(f"- T{i}: {f} jogado → cemitério: {'sim' if gy else 'NÃO'} · terreno buscado: {'sim' if busca else 'NÃO'}")
if not FETCH & {e["name"] for t in T for e in t}:
    print("- (nenhum fetchland nesta partida)")
# 2b) fontes viradas no fim do turno (último registro do objeto no turno; entrada já virada não conta) x magias lançadas.
#     Só prova limite superior de ativações; o mana de Weaver (X), Faeburrow Elder (cores), Urza's Saga, City of Brass etc. é conferido à mão no goldfish-log.
def tipos(n):
    e = ORC.get(n) or ORC.get(n.split(" // ")[0]) or {}
    return e.get("type_line") or ""


def mv(n):
    e = ORC.get(n) or ORC.get(n.split(" // ")[0]) or {}
    return int(e.get("cmc") or 0)


print("\n| turno | fontes viradas no fim do turno | magias entrando em campo (MV) | magia/descarte mão→cemitério (MV) |")
print("|---|---|---|---|")
for i, t in enumerate(T, 1):
    ult = {}
    for e in t:
        ult[e["id"]] = e
    vir = []
    for e in ult.values():
        if e["zone"] == "battlefield" and e["tapped"] and not (e["fromZone"] and e["toZone"] == "battlefield") and not e["token"]:
            tp = tipos(e["name"])
            vir.append(e["name"] + (" (criatura)" if "Creature" in tp and "Land" not in tp else ""))
    cast = [f"{e['name'].split(' // ')[0]} ({mv(e['name'])})" for e in t if e["fromZone"] in ("hand", "commandZone") and e["toZone"] == "battlefield" and "Land" not in tipos(e["name"])]
    gy = [f"{e['name'].split(' // ')[0]} ({mv(e['name'])})" for e in t if e["fromZone"] == "hand" and e["toZone"] == "graveyard"]
    print(f"| T{i} | {', '.join(vir) or '—'} | {', '.join(cast) or '—'} | {', '.join(gy) or '—'} |")
# 2c) cartas que entram na mão vindas da biblioteca, por turno (compra do passo + capítulos "compre" + constelação/Sythis etc.).
#     É o lado "log" da conta; o esperado pelo oráculo (passo de compra + cada habilidade) está no goldfish-log.
print("\n| turno | library→mão no log | cartas |")
print("|---|---|---|")
for i, t in enumerate(T, 1):
    cs = [e["name"].split(" // ")[0] for e in t if e["fromZone"] == "library" and e["toZone"] == "hand"]
    print(f"| T{i} | {len(cs)} | {', '.join(cs) or '—'} |")
# 3) marcadores de saber por objeto-Saga (chave = id do objeto; cópia-ficha é outro objeto), em ORDEM DO LOG:
#    entrada = 1 marcador (ou o de read ahead); depois só +1 no início da fase principal 1 de cada turno (CR 714.3c).
#    Qualquer outro incremento precisa de fonte (proliferate, Satsuki, mover marcador...). Cópia-ficha sem marcador = log incompleto.
print("\n| Saga (objeto) | valores de saber em ordem do log (T: valores) | anomalias |")
print("|---|---|---|")
estado = {}          # id -> {"nome","entrou","ultimo","incs","turno_inc","copia"}
linha = defaultdict(lambda: defaultdict(list))
notas = defaultdict(list)
ordem = []
saidas = []
for i, t in enumerate(T, 1):
    for e in t:
        n, oid = e["name"], e["id"]
        if n not in FINAL or e["flipped"]:
            continue
        rot = n.split(" // ")[0] + (" (cópia-ficha)" if e["tokenCopy"] else "")
        chave = oid
        if chave not in ordem:
            ordem.append(chave)
        nome_linha = rot
        if e["toZone"] in ("graveyard", "exile") and e["fromZone"] == "battlefield":
            saidas.append(f"{rot} → {'cemitério' if e['toZone'] == 'graveyard' else 'exílio'} (T{i})")
            if e["toZone"] == "exile":
                estado.pop(chave, None)
                linha[chave][i].append("exílio")
                notas[chave].append(f"T{i}: saiu para o exílio")
            else:
                linha[chave][i].append("cemitério")
            continue
        l = lore(e)
        entra = e["toZone"] == "battlefield" and (e["fromZone"] in ("library", "hand", "exile") or (e["fromZone"] is None and e["tokenCopy"]))
        if entra:
            estado[chave] = {"nome": rot, "entrou": i, "ultimo": l, "incs": 0, "turno_inc": None}
            linha[chave][i].append(f"entra {l}")
            if e["fromZone"] == "exile":
                notas[chave].append(f"T{i}: voltou do exílio com {l} (objeto novo)")
                anom.append(f"{rot} T{i}: voltou do exílio sem carta da lista que a devolva")
            if e["tokenCopy"]:
                notas[chave].append(f"T{i}: cópia-ficha de Saga sem fonte de cópia na lista" + (" e sem marcador de saber (CR 714.3a: deveria entrar com 1)" if l == 0 else ""))
                anom.append(f"{rot} T{i}: cópia-ficha sem fonte de cópia na lista")
            continue
        if chave in estado and (l or e["counters"].get("Lore")):
            s = estado[chave]
            if l > s["ultimo"]:
                if s["turno_inc"] != i:
                    s["incs"] = 0
                    s["turno_inc"] = i
                s["incs"] += 1
                permitido = 0 if s["entrou"] == i else 1
                if s["incs"] > permitido:
                    msg = f"incremento extra {s['ultimo']}→{l} no mesmo turno (entrou no T{s['entrou']}; só +1 na fase principal 1 é automático)"
                    notas[chave].append(f"T{i}: {msg}")
                    anom.append(f"{rot} T{i}: {msg}")
            s["ultimo"] = l
            linha[chave][i].append(str(l))
        elif chave in estado and l == 0 and e["fromZone"] is None and estado[chave]["ultimo"]:
            notas[chave].append(f"T{i}: registro sem marcador depois de ter {estado[chave]['ultimo']} (marcadores removidos?)")
for chave in ordem:
    nome = (estado.get(chave) or {}).get("nome")
    if nome is None:
        for t in T:
            for e in t:
                if e["id"] == chave:
                    nome = e["name"].split(" // ")[0] + (" (cópia-ficha)" if e["tokenCopy"] else "")
    ln = "; ".join(f"T{t}: {'→'.join(v)}" for t, v in sorted(linha[chave].items()))
    print(f"| {nome} `{chave}` | {ln} | {' · '.join(notas[chave]) or '—'} |")
print("\nSaída de campo: " + ("; ".join(saidas) or "nenhuma"))
# 4) gatilho do Tom: Saga library→battlefield por turno ≤ 1
print()
for i, t in enumerate(T, 1):
    livres = [e["name"] for e in t if e["fromZone"] == "library" and e["toZone"] == "battlefield" and e["name"] in FINAL]
    if livres:
        if len(livres) > 1:
            viol.append(f"T{i}: {len(livres)} Sagas de graça no mesmo turno")
        print(f"- T{i}: Saga da biblioteca direto para o campo: {', '.join(livres)} ({len(livres)}; limite 1 por turno do Tom: {'ok' if len(livres) <= 1 else 'VIOLA'})")
print(f"\n**Violações provadas pelo log: {len(viol)}" + (" — " + "; ".join(viol) if viol else "") + "**")
print(f"**Anomalias sem fonte no log: {len(anom)}" + (" — " + "; ".join(anom) if anom else "") + "** (estado que nenhuma carta da lista explica; típico de ajuste manual/desfazer do playtester, não prova erro de jogo)")
