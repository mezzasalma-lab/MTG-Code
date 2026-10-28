"""Lista o que há em cada arquivo de dados: para os brutos por partida (raw_*.json.xz, formato colunas-v1) as variantes e o N de cada uma;
para os demais (.json) o tipo. Uso: python3 indice_dados.py > resumos/indice_dados.md   (rodar de dentro desta pasta)"""
import glob
import json
import lzma
import os
import re

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
    if nome == "spellbook_cru.json.xz":
        print(f"| `{nome}` | respostas CRUAS do Commander Spellbook (`find-my-combos`) para a lista antes (`_lista_legada`), a lista depois e 2 controles positivos: {', '.join(d.keys())} |")
        continue
    if nome == "spellbook_resumo.json":
        print(f"| `{nome}` | resumo (combos incluídos e 'quase') extraído das respostas cruas acima: {', '.join(d.keys())} |")
        continue
    if isinstance(d, dict) and d.get("formato") == "colunas-v1":
        v = d["variantes"]
        campos = sorted({c for x in v.values() for c in x["campos"]})
        ns = sorted({x["n"] for x in v.values()})
        print(f"| `{nome}` | bruto por partida: {len(v)} variantes × N={'/'.join(map(str, ns))} partidas; campos: {', '.join(campos)}. Variantes: " + "; ".join(f"`{k}`" for k in v) + " |")
    elif isinstance(d, dict) and d and all(isinstance(v, dict) and "rulings" in v for v in d.values()):
        data_arq = re.search(r"\d{4}-\d{2}-\d{2}", nome)
        data_arq = data_arq.group(0) if data_arq else "data não registrada no nome"
        print(f"| `{nome}` | oráculo bruto do Scryfall + rulings de {len(d)} cartas únicas ({sum(len(v['rulings']) for v in d.values())} rulings no total, {sum(1 for v in d.values() if v['rulings'])} cartas com ruling), lidos ao vivo em {data_arq} antes de escrever o código |")
    elif isinstance(d, dict) and "incluidos" in d and "estimate_bracket" in d:
        print(f"| `{nome}` | Commander Spellbook para a lista: {len(d['incluidos'])} combos incluídos, {len(d['quase'])} 'quase', `estimate-bracket` (tag {d['estimate_bracket']['bracketTag']}), nomes reconhecidos {sum(1 for v in d['reconhece'].values() if v)}/{len(d['reconhece'])}, controle positivo {d['controle_positivo_basalt_rings']}, controle de corte {d['controle_de_corte_combo_sumiu_sem_o_rings']} |")
    elif isinstance(d, dict) and "rulings" in d:
        print(f"| `{nome}` | oráculo bruto do Scryfall + {len(d['rulings'])} ruling(s) de {d['card']} (lido ao vivo em 2026-10-03) |")
    elif isinstance(d, dict) and any(k.startswith("+") or k == "base" for k in d):
        print(f"| `{nome}` | respostas do Commander Spellbook (`find-my-combos`): {', '.join(d.keys())} |")
    elif isinstance(d, dict) and "uses" in d:
        print(f"| `{nome}` | combo \"quase\" do Commander Spellbook (um item fora da lista) |")
    else:
        print(f"| `{nome}` | resumo agregado derivado dos brutos (chaves: {', '.join(list(d.keys())[:8]) if isinstance(d, dict) else type(d).__name__}) |")
