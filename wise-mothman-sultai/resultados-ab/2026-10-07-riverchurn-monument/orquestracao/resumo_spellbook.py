#!/usr/bin/env python3
"""Resumo legivel do Spellbook (le so' dados/spellbook_monument.json e spellbook_monument_quase.json). Uso: python3 resumo_spellbook.py > ../resumos/resumo_spellbook.md"""
import json, os
A = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(A, "..", "dados")
d = json.load(open(os.path.join(D, "spellbook_monument.json"))); q = json.load(open(os.path.join(D, "spellbook_monument_quase.json")))
print("# Commander Spellbook: Riverchurn Monument no Mothman (2026-10-07)\n")
print(f"- Nomes verificados em `GET /cards/?q=`: **{len(d['reconhece'])}**; NAO reconhecidos: **{d['nao_reconhecidos'] or 'nenhum'}** (incluindo `Riverchurn Monument`, `The Wise Mothman` e as duas cartas do controle positivo).")
print("- Combos INCLUIDOS na lista atual (99 + comandante):")
for k, v in d["base"]["incluidos"].items(): print(f"  - **{k}** — {', '.join(v['produz'][:2])} (bracketTag `{v['bracket']}`)")
print(f"  - 'quase incluidos' na base: {d['base']['quase_n']}")
so = d["monument_sem_cortar"]
print(f"- **Com o Monument (sem cortar nada):** combos novos incluidos = **{len(so['novos'])}**; `quase` com o Monument = **{len(so['quase_com_monument'])}** (cada um precisa de UMA carta que NAO esta na lista):")
for o in q: print(f"  - Monument + **{[c for c in o['cartas'] if c != 'Riverchurn Monument'][0]}** → {', '.join(o['produz'][:1])} (tag `{o['bracket']}`, popularidade {o['popularidade']})")
print("\n## Corte por corte (`Monument <- X`): o que SOME e o que APARECE\n")
sumiu = {k: v["sumiram"] for k, v in d["monument_por_corte"].items() if v["sumiram"]}
novo = {k: list(v["novos"]) for k, v in d["monument_por_corte"].items() if v["novos"]}
print(f"- {len(d['monument_por_corte'])} cortes consultados (toda carta nao-basica da lista, menos o comandante). Cortes que **derrubam um combo incluido**: {len(sumiu)}")
for k, v in sorted(sumiu.items()): print(f"  - cortar **{k}** derruba: {', '.join(v)}")
print(f"- Cortes que **adicionam** combo incluido: **{len(novo)}** ({novo or 'nenhum'}).")
cp, cc = d["controle_positivo"], d["controle_corte"]
print("\n## Controles (a API ignora, sem erro, nome nao reconhecido: resultado vazio sem controle e' vacuo)\n")
print(f"- **Controle positivo** (Negate+Swiftfoot Boots → Thassa's Oracle+Demonic Consultation): combo apareceu = **{cp['achou_thassa_consultation']}**.")
print(f"- **Controle de corte** (Mindcrank → Evolution Sage): a base tem Ascension+Mindcrank = **{cc['base_tem_ascension_mindcrank']}**; sumiu ao cortar = **{cc['combo_ascension_mindcrank_sumiu']}**.")
