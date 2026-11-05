"""Lista o que ha' em cada arquivo de dados (brutos por partida colunas-v1 e Spellbook). Uso: python3 indice_dados.py > resumos/indice_dados.md   (rodar de dentro desta pasta)"""
import glob, json, lzma, os
aqui = os.path.dirname(os.path.abspath(__file__))
print("| arquivo | conteúdo |\n|---|---|")
for f in sorted(glob.glob(os.path.join(aqui, "dados", "*"))):
    nome = os.path.basename(f)
    d = json.load(lzma.open(f, "rt")) if f.endswith(".xz") else json.load(open(f))
    if isinstance(d, dict) and d.get("formato") == "colunas-v1":
        v = d["variantes"]; campos = sorted({c for x in v.values() for c in x["campos"]}); ns = sorted({x["n"] for x in v.values()})
        print(f"| `{nome}` | bruto por partida: {len(v)} variantes × N={'/'.join(map(str, ns))}; {len(campos)} campos numéricos. Variantes: " + "; ".join(f"`{k}`" for k in v) + " |")
    elif nome == "spellbook_viva.json":
        print(f"| `{nome}` | Commander Spellbook da lista exata (antes × depois): {len(d['reconhece'])} nomes resolvidos (não reconhecidos: {d['nao_reconhecidos']}), {len(d['combos_antes'])} combos antes, {len(d['combos_viva'])} depois, novos {d['novos']}, perdidos {d['sumiram']}, controle positivo={d['controle_positivo_thassa_consultation']}, controle de corte={d['controle_de_corte_ascension_mindcrank_sumiu']} |")
    else:
        print(f"| `{nome}` | {type(d).__name__} |")
