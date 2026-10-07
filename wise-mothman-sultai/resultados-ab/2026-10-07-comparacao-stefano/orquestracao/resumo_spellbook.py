"""Resume dados/spellbook_stefano_frank_master.json em resumos/resumo_spellbook.md (so' le o JSON). Uso: python3 resumo_spellbook.py > ../resumos/resumo_spellbook.md"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
s = json.load(open(os.path.join(AQUI, "..", "dados", "spellbook_stefano_frank_master.json"), encoding="utf-8"))
print("# Commander Spellbook: nossa lista, lista do Stefano, Agent Frank Horrigan e The Master, Transcendent\n")
print(f"- Nomes verificados: {len(s['reconhece'])}; **não reconhecidos: {s['nao_reconhecidos']}** (a API ignora nome desconhecido sem erro).")
cp, cc = s["controle_positivo"], s["controle_corte"]
print(f"- Controle positivo (Thassa's Oracle + Demonic Consultation aparece): **{cp['achou_thassa_consultation']}**. Controle de corte (a base tem Ascension + Mindcrank: {cc['base_tem_ascension_mindcrank']}; some ao cortar o Mindcrank: {cc['combo_ascension_mindcrank_sumiu']}).")
print(f"- **Nossa lista:** {len(s['base']['incluidos'])} combos incluídos: " + "; ".join(f"{k} ({v['bracket']})" for k, v in s["base"]["incluidos"].items()) + f"; {s['base']['quase_n']} \"quase\".")
print(f"- **Lista do Stefano:** {len(s['stefano']['incluidos'])} combos incluídos; {s['stefano']['quase_n']} \"quase\": " + "; ".join(s["stefano"]["quase"]) + ".\n")
print("## Frank / Master sem cortar nada (a peça entra em algum combo?)\n")
for k, v in s["sem_cortar"].items():
    print(f"- **{k}** (main {v['n_main']}): combos novos {list(v['novos']) or 'nenhum'}; \"quase\" novos com a peça: {v['quase_novos_com_peca'] or 'nenhum'}; combos que somem: {v['sumiram'] or 'nenhum'}.")
print("\n## Por corte (X → peça): o que muda\n")
for peca, d in s["por_corte"].items():
    print(f"### {peca}\n")
    novos = {x: c["novos"] for x, c in d.items() if c["novos"]}
    sumiram = {x: c["sumiram"] for x, c in d.items() if c["sumiram"]}
    quase = sorted({k for c in d.values() for k in c["quase_novos_com_peca"]})
    qs = {x: c["quase_sumiram"] for x, c in d.items() if c["quase_sumiram"]}
    print(f"- {len(d)} cortes testados. Combos NOVOS em algum corte: {novos or 'nenhum'}.")
    print(f"- Combos que SOMEM (cortar a peça de um combo da base): {sumiram or 'nenhum'}.")
    print(f"- \"Quase\" novos com a peça (a outra peça NÃO está na lista, {len(quase)}): {', '.join(quase) or 'nenhum'}.")
    print(f"- \"Quase\" (combo de 2-3 peças com UMA peça faltando, fora da lista) da base que somem com o corte, por corte: " + (", ".join(f"{x} ({len(v)})" for x, v in qs.items()) or "nenhum") + ". Não são combos da lista; contam só como \"armadilha de Bracket\" evitada.\n")
