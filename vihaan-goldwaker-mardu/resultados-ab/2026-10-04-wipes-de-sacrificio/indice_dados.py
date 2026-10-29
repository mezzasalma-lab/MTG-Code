"""Lista o que ha' em cada arquivo de dados desta pasta: busca ampla do Scryfall (crua e classificada), oraculo+rulings (candidatas e lista), Commander Spellbook (cru e resumo) e os brutos por estado
do ensaio a seco (formato amostras-colunas-v1). Uso: python3 indice_dados.py > resumos/indice_dados.md   (rodar de dentro desta pasta)"""
import glob, json, lzma, os
aqui = os.path.dirname(os.path.abspath(__file__))
print("| arquivo | conteudo |")
print("|---|---|")
for f in sorted(glob.glob(os.path.join(aqui, "dados", "*"))):
    nome = os.path.basename(f)
    try:
        d = json.load(lzma.open(f, "rt")) if f.endswith(".xz") else json.load(open(f))
    except Exception as e:
        print(f"| `{nome}` | (ilegivel: {type(e).__name__}) |")
        continue
    if isinstance(d, dict) and d.get("formato") == "amostras-colunas-v1":
        print(f"| `{nome}` | bruto por ESTADO do ensaio a seco (modo {d['modo']}, N={d['N']} partidas, sementes {d['S0']}..{d['S0'] + d['N'] - 1}): {len(d['amostras']['turno'])} estados; por estado: {', '.join(d['campos_amostra'])}; por variante e estado: {', '.join(d['campos_r'])}. Variantes: " + "; ".join(f"`{v}`" for v in d["variantes"]) + f". Violacoes de invariante: {len(d['violacoes'])}; excecoes: {d['n_excecoes']} |")
    elif nome == "busca_ampla_cru.json.xz":
        print(f"| `{nome}` | resposta CRUA do Scryfall (`/cards/search`) de {len(d)} formulacoes de busca (R/W/B, legal em Commander): " + ", ".join(f"{k}={len(v['cartas'])}" for k, v in d.items()) + " cartas |")
    elif nome == "busca_ampla_classificada.json":
        from collections import Counter
        c = Counter(x["tipo"] for x in d)
        print(f"| `{nome}` | uniao deduplicada por oracle_id: {len(d)} cartas, classificadas por script (`tipo`): {dict(c)}; por carta: oraculo, quem sacrifica, o que, quanto, em que buscas apareceu |")
    elif isinstance(d, dict) and d and all(isinstance(v, dict) and ("rulings" in v or "erro" in v) for v in d.values()):
        print(f"| `{nome}` | oraculo completo (todas as faces) + {sum(len(v.get('rulings', [])) for v in d.values())} rulings de {len(d)} cartas, lidos ao vivo em 2026-10-04 antes de modelar |")
    elif isinstance(d, dict) and len(d) > 50 and all(isinstance(v, dict) and "oracle_text" in v or isinstance(v, dict) and "card_faces" in v for v in d.values()):
        print(f"| `{nome}` | oraculo cru do Scryfall das {len(d)} cartas da lista (94 distintas + comandante), usado pela enumeracao e pelo harness (tipos, cores, poder, mana produzida) |")
    elif isinstance(d, dict) and any(k.startswith("+") or k == "base" or k.startswith("base") for k in d):
        print(f"| `{nome}` | Commander Spellbook (`find-my-combos`): {len(d)} consultas ({'resposta crua' if nome.endswith('.xz') else 'resumo: combos incluidos e quase'}) |")
    else:
        print(f"| `{nome}` | (outro) |")
