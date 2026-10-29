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
    if nome.endswith(".done"):
        print(f"| `{nome}` | sinal de fim do lançador (arquivo vazio de dados) |")
        continue
    try:
        d = json.load(lzma.open(f, "rt")) if f.endswith(".xz") else json.load(open(f))
    except Exception as e:
        print(f"| `{nome}` | (ilegível: {type(e).__name__}) |")
        continue
    if nome == "spellbook_cru.json.xz":
        print(f"| `{nome}` | respostas CRUAS do Commander Spellbook (`find-my-combos`): {', '.join(d.keys())} |")
    elif nome == "spellbook_monument.json":
        print(f"| `{nome}` | resumo do Spellbook: reconhecimento de nomes (`reconhece`), base, Monument por corte (87 cortes), Monument sem cortar, controles ({', '.join(d.keys())}) |")
    elif nome == "spellbook_monument_quase.json":
        print(f"| `{nome}` | os {len(d)} combos 'quase' do Spellbook que contêm o Monument (uma carta fora da lista completa cada um) |")
    elif nome == "riverchurn_scryfall.json":
        print(f"| `{nome}` | oráculo bruto do Scryfall + {len(d['rulings']['data'])} rulings + impressões de {d['card']['name']} (lido ao vivo em 2026-10-07) |")
    elif isinstance(d, dict) and d.get("formato") == "colunas-v1":
        v = d["variantes"]
        campos = sorted({c for x in v.values() for c in x["campos"]})
        ns = sorted({x["n"] for x in v.values()})
        print(f"| `{nome}` | bruto por partida: {len(v)} variantes × N={'/'.join(map(str, ns))} partidas; {len(campos)} campos numéricos. Variantes: " + "; ".join(f"`{k}`" for k in v) + " |")
    else:
        print(f"| `{nome}` | (chaves: {', '.join(list(d.keys())[:8]) if isinstance(d, dict) else type(d).__name__}) |")
