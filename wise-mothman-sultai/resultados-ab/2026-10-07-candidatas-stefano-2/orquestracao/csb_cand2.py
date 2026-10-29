"""Commander Spellbook para as 6 candidatas (Fractured Sanity, Screeching Scorchbeast, Inexorable Tide, Branching Evolution, Loading Zone, The Earth Crystal) no Mothman (Regra #4 + adendo).
1) resolve cada nome via GET /cards/?q= e REGISTRA se o Spellbook reconhece; 2) lista base; 3) lista + CADA carta (100 no main, sem cortar: se a PECA entra em combo, ele aparece, seja qual for o corte)
e + as 6 juntas; 4) controle positivo (Thassa + Consultation tem de aparecer) e de corte (cortar Mindcrank tira Ascension + Mindcrank). Cortar uma carta so' pode DERRUBAR combo se ela for peca dele
(Altar of Dementia, Bloodchief Ascension, The Great Henge, Mindcrank, Glen Elendra Archmage: ver o Spellbook da rodada do Horrigan). Uso: python3 csb_cand2.py <lista.md> <saida.json>"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(AQUI, "..", "..", "2026-10-07-comparacao-stefano", "orquestracao"))
import csb_stefano as C
CARTAS = ["Fractured Sanity", "Screeching Scorchbeast", "Inexorable Tide", "Branching Evolution", "Loading Zone", "The Earth Crystal"]
if __name__ == "__main__":
    lista, out = sys.argv[1], sys.argv[2]
    base = C.parse(lista)
    nomes = sorted(set(c for c in base if c not in C.BASICOS) | set(CARTAS) | {C.CMD, "Thassa's Oracle", "Demonic Consultation"})
    reconhece = {n: C.resolve(n) for n in nomes}
    nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos:", nao, flush=True)
    binc, balm = C.resumo(C.query(base))
    print("base:", len(binc), "combos,", len(balm), "quase", flush=True)
    res = {}
    for nome, extra in [(c, [c]) for c in CARTAS] + [("as_seis_juntas", CARTAS)]:
        inc, alm = C.resumo(C.query(base + extra))
        res[nome] = {"novos": {k: v for k, v in inc.items() if k not in binc}, "sumiram": [k for k in binc if k not in inc],
                     "quase_novos_com_a_peca": sorted(k for k in set(alm) - set(balm) if any(p in k for p in extra)), "quase_novos_n": len(set(alm) - set(balm))}
        print(nome, "novos:", list(res[nome]["novos"]), "| quase novos com a peca:", len(res[nome]["quase_novos_com_a_peca"]), flush=True)
    d = list(base); [d.remove(x) for x in ("Negate", "Swiftfoot Boots")]; d += ["Thassa's Oracle", "Demonic Consultation"]
    inc, _ = C.resumo(C.query(d)); pos = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in inc)
    d = list(base); d.remove("Mindcrank"); d.append("Fathom Mage")
    inc, _ = C.resumo(C.query(d)); corte = not any("Bloodchief Ascension" in k and "Mindcrank" in k for k in inc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "base": {"incluidos": binc, "quase_n": len(balm)}, "por_carta": res,
               "controle_positivo_thassa_consultation": pos, "controle_de_corte_ascension_mindcrank_sumiu": corte,
               "base_tem_ascension_mindcrank": any("Bloodchief Ascension" in k and "Mindcrank" in k for k in binc)}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo:", pos, "| controle de corte (Ascension+Mindcrank some ao cortar o Mindcrank):", corte)
