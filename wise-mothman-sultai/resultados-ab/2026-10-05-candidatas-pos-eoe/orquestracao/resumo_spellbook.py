"""Resume (a partir SO' dos .json brutos) as respostas do Commander Spellbook. Uso: python3 resumo_spellbook.py <dados_dir>"""
import json, os, sys
d = sys.argv[1]
def J(n): return json.load(open(os.path.join(d, n)))
bc = J("spellbook_base_e_controle.json")
print("# Commander Spellbook — The Wise Mothman (resumo gerado dos JSON brutos)\n")
print("## 1. Lista do usuario (base) e controle positivo\n")
for k, v in bc.items():
    print(f"- **{k}** (main={v['n_cartas_main']}): {len(v['incluidos'])} combo(s) incluido(s), {len(v['quase_incluidos'])} 'quase' (falta 1 carta); identidade {v['identidade']}")
    for c, x in sorted(v["incluidos"].items()):
        print(f"    - {c} -> {', '.join(x['produz'])} | bracketTag {x['bracket']} | popularidade {x['popularidade']} | id {x['id']}")
print("\nControle positivo: a lista com Thassa's Oracle + Demonic Consultation devolve o combo deles (`Demonic Consultation + Thassa's Oracle`) -> o endpoint, o formato de nomes e a leitura funcionam.\n")
cand = J("spellbook_candidatas.json")
print("## 2. Cada candidata ADICIONADA a lista (sem cortar nada): combos novos / que somem\n")
print("| candidata | grupo | combos novos | sumiram | 'quase' novos |\n|---|---|---|---|---|")
for n, v in sorted(cand["candidatas"].items(), key=lambda kv: (kv[1]["grupo"], kv[0])):
    if not v.get("spellbook_reconhece"):
        print(f"| {n} | {v['grupo']} | NAO RECONHECIDA | | |"); continue
    novos = "; ".join(sorted(v["incluidos_novos"])) or "-"
    sum_ = "; ".join(v["incluidos_sumiram"]) or "-"
    print(f"| {n} | {v['grupo']} | {novos} | {sum_} | {v['n_quase_novos']} |")
print(f"\nNomes nao reconhecidos pelo Spellbook: {[n for n, v in cand['candidatas'].items() if not v.get('spellbook_reconhece')] or 'nenhum'}")
print("\n## 3. Trocas (sai/entra), com controles de corte de peca de combo\n")
sw = J("spellbook_swaps.json")
b = set(sw["base"]["incluidos"])
print("| cenario | main | incluidos | NOVOS | SUMIRAM | 'quase' |\n|---|---|---|---|---|---|")
for k, v in sw.items():
    inc = set(v["incluidos"])
    print(f"| {k} | {v['n_cartas_main']} | {len(inc)} | {'; '.join(sorted(inc - b)) or '-'} | {'; '.join(sorted(b - inc)) or '-'} | {len(v['quase_incluidos'])} |")
pf = J("spellbook_pacote_final.json")
print("\n## 4. Pacote final de 6 trocas (SUPERADO: tirava o Kozilek) e variante com Mutational Advantage <- Negate\n")
for k, v in pf.items():
    if k == "base": continue
    inc = set(v["incluidos"])
    print(f"- **{k}**: sai {v['sai']}; entra {v['entra']}; NOVOS: {sorted(inc - b) or '-'}; SUMIRAM: {sorted(b - inc) or '-'}; 'quase' {len(v['quase_incluidos'])} (base {len(pf['base']['quase_incluidos'])})")
p5 = J("spellbook_pacote_5trocas.json")
print("\n## 4b. Pacote de 5 trocas (Kozilek MANTIDO) — vigente; o de 6 trocas acima esta SUPERADO\n")
for k, v in p5.items():
    if k == "base": continue
    inc = set(v["incluidos"])
    print(f"- **{k}**: sai {v['sai']}; entra {v['entra']}; NOVOS: {sorted(inc - b) or '-'}; SUMIRAM: {sorted(b - inc) or '-'}; 'quase' {len(v['quase_incluidos'])} (base {len(p5['base']['quase_incluidos'])})")
print("\n## 5. Combos 'quase' da lista base cuja ULTIMA carta existe no pool pos-EOE (uma carta completaria)\n")
q = J("spellbook_quase_pool.json")
print("| carta que falta | demais pecas (ja' na lista) | templates | produz | bracketTag | popularidade |\n|---|---|---|---|---|---|")
for vid, x in sorted(q.items(), key=lambda kv: (kv[1]["falta"], kv[1]["usos"])):
    resto = [u for u in x["usos"] if u != x["falta"]]
    print(f"| {x['falta']} | {', '.join(resto)} | {', '.join(x['requer_templates']) or '-'} | {', '.join(x['produz'][:4])} | {x['bracket']} | {x['popularidade']} |")
