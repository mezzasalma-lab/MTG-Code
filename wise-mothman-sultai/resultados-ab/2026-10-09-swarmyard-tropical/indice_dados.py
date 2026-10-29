"""Lista o que ha' em cada arquivo de dados: brutos por partida (colunas-v1: variantes e N) e Spellbook.
Uso: python3 indice_dados.py > resumos/indice_dados.md   (rodar de dentro desta pasta)"""
import glob, json, lzma, os
aqui = os.path.dirname(os.path.abspath(__file__))
print("| arquivo | conteúdo |\n|---|---|")
for f in sorted(glob.glob(os.path.join(aqui, "dados", "*"))):
    nome = os.path.basename(f)
    try:
        d = json.load(lzma.open(f, "rt")) if f.endswith(".xz") else json.load(open(f))
    except Exception as e:
        print(f"| `{nome}` | (ilegível: {type(e).__name__}) |"); continue
    if isinstance(d, dict) and d.get("formato") == "colunas-v1":
        v = d["variantes"]; campos = sorted({c for x in v.values() for c in x["campos"]}); ns = sorted({x["n"] for x in v.values()})
        print(f"| `{nome}` | bruto por partida: {len(v)} variantes × N={'/'.join(map(str, ns))}; {len(campos)} campos numéricos. Variantes: " + "; ".join(f"`{k}`" for k in v) + " |")
    elif nome == "spellbook_swtrop.json":
        print(f"| `{nome}` | Commander Spellbook: {len(d['reconhece'])} nomes resolvidos (não reconhecidos: {d['nao_reconhecidos']}), {len(d['base']['incluidos'])} combos da base, {len(d['por_variante'])} variantes, controle positivo={d['controle_positivo_thassa_consultation']}, controle de corte={d['controle_de_corte_ascension_mindcrank_sumiu']}, lista viva == e1: {d.get('lista_viva_igual_e1')} |")
    else:
        print(f"| `{nome}` | {type(d).__name__} |")
