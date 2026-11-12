"""Lista o que há em cada arquivo de dados: para os brutos por partida (raw_*.json.xz, formato colunas-v1) as variantes e o N de cada uma;
para os demais (.json) o tipo. Uso: python3 indice_dados.py > resumos/indice_dados.md   (rodar de dentro desta pasta)"""
import glob
import json
import lzma
import os

aqui = os.path.dirname(os.path.abspath(__file__))
print("| arquivo | conteúdo |")
print("|---|---|")
for f in sorted(glob.glob(os.path.join(aqui, "dados", "*"))):
    nome = os.path.basename(f)
    try:
        d = json.load(lzma.open(f, "rt")) if f.endswith(".xz") else json.load(open(f))
    except Exception as e:
        print(f"| `{nome}` | (ilegível: {type(e).__name__}) |")
        continue
    if nome == "partida.json.xz":
        print(f"| `{nome}` | o log da partida manual (Archidekt playtester): lista de {len(d)} turnos, {sum(len(x) for x in d)} registros no total; cada registro = nome, id, tapped, token, counters, fromZone, toZone, zone |")
        continue
    if nome == "oraculo_ao_vivo.json":
        print(f"| `{nome}` | 1a consulta ao Scryfall: oráculo das {len(d)} cartas do log, **sem rulings** (SUPERADO por `oraculo_rulings_ao_vivo.json`; guardado, não apagado) |")
        continue
    if isinstance(d, dict) and d.get("formato") == "colunas-v1":
        v = d["variantes"]
        campos = sorted({c for x in v.values() for c in x["campos"]})
        ns = sorted({x["n"] for x in v.values()})
        print(f"| `{nome}` | bruto por partida: {len(v)} variantes × N={'/'.join(map(str, ns))} partidas; campos: {', '.join(campos)}. Variantes: " + "; ".join(f"`{k}`" for k in v) + " |")
    elif isinstance(d, dict) and d and all(isinstance(v, dict) and "rulings" in v for v in d.values()):
        print(f"| `{nome}` | oráculo bruto do Scryfall + rulings de {len(d)} cartas ({', '.join(d)}; {sum(len(v['rulings']) for v in d.values())} rulings no total), lidos ao vivo em 2026-10-03 antes de escrever o código |")
    elif isinstance(d, dict) and "rulings" in d:
        print(f"| `{nome}` | oráculo bruto do Scryfall + {len(d['rulings'])} ruling(s) de {d['card']} (lido ao vivo em 2026-10-03) |")
    elif isinstance(d, dict) and any(k.startswith("+") or k == "base" for k in d):
        print(f"| `{nome}` | respostas do Commander Spellbook (`find-my-combos`): {', '.join(d.keys())} |")
    elif isinstance(d, dict) and "uses" in d:
        print(f"| `{nome}` | combo \"quase\" do Commander Spellbook (um item fora da lista) |")
    else:
        print(f"| `{nome}` | resumo agregado derivado dos brutos (chaves: {', '.join(list(d.keys())[:8]) if isinstance(d, dict) else type(d).__name__}) |")
