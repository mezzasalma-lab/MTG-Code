"""Lista o que há em cada arquivo de dados (variantes e N dos brutos `colunas-v1`). Uso: python3 indice_dados.py > resumos/indice_dados.md   (rodar de dentro desta pasta)"""
import glob, json, lzma, os
aqui = os.path.dirname(os.path.abspath(__file__))
print("| arquivo | conteúdo |\n|---|---|")
for f in sorted(glob.glob(os.path.join(aqui, "dados", "*"))):
    nome = os.path.basename(f)
    if nome.endswith(".done"):
        print(f"| `{nome}` | sinal de fim do lançador |"); continue
    d = json.load(lzma.open(f, "rt")) if f.endswith(".xz") else json.load(open(f))
    if isinstance(d, dict) and d.get("formato") == "colunas-v1":
        v = d["variantes"]; campos = sorted({c for x in v.values() for c in x["campos"]})
        print(f"| `{nome}` | bruto por partida: {len(v)} variantes ({', '.join('`'+k+'`' for k in v)}) × N={'/'.join(sorted({str(x['n']) for x in v.values()}))}; {len(campos)} campos numéricos (todos os do estado final, incl. `jace_*`) |")
    else:
        print(f"| `{nome}` | resposta bruta de API (Scryfall / Commander Spellbook); chaves: {', '.join(list(d.keys())[:8])} |")
