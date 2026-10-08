"""Lista o que ha' em cada arquivo de dados: brutos por partida (colunas-v1: variantes e N), castabilidade das remocoes novas (cast-v1), Spellbook e rulings.
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
    elif False:
        print(f"| `{nome}` | cemitério de cada oponente no fim de cada turno meu: N={d['n']} partidas, modo {d['modo']}, sementes {d['sementes']}, {sum(len(j) for j in d['jogos'])} (partida, turno) registrados |")
    elif isinstance(d, dict) and str(d.get("formato", "")).startswith("cast-v1"):
        print(f"| `{nome}` | por partida e turno: terrenos, terrenos B, terrenos G, se Atomize / Casualties / Trophy foram vistas e conjuradas; N={d['n']}, modo {d['modo']}, {d['variante']} |")
    elif nome == "spellbook_cinco.json":
        print(f"| `{nome}` | Commander Spellbook: {len(d['reconhece'])} nomes resolvidos (não reconhecidos: {d['nao_reconhecidos']}), combos da base, {len(d['por_variante'])} variantes, controle positivo={d['controle_positivo_thassa_consultation']}, controle de corte={d['controle_de_corte_ascension_mindcrank_sumiu']} |")
    elif nome in ("rulings_remocoes.json", "rulings_casualties.json"):
        print(f"| `{nome}` | oráculo + rulings ao vivo (Scryfall) de {len(d)} cartas ({', '.join(d)}; {sum(len(v['rulings']) for v in d.values())} rulings), lidos em 2026-10-08 antes de escrever o código |")
    else:
        print(f"| `{nome}` | {type(d).__name__} |")
