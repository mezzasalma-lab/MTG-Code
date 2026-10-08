"""Commander Spellbook (Regra #4 + adendo): pacote (Horrigan + Branching Evolution, cortando Offer + Negate) e as remocoes/hibridas candidatas (Drown in the Loch, Assassin's Trophy, Putrefy,
Beast Within, Deadly Rollick, Atomize, Casualties of War). 1) resolve cada nome e REGISTRA se o Spellbook reconhece (a API ignora nome desconhecido, sem erro); 2) lista base; 3) pacote EXATO
(base - Offer - Negate + Horrigan + Branching); 4) base + cada candidata (sem cortar: se a PECA entra em combo, aparece); 5) pacote + Drown; 6) controle positivo (Thassa + Consultation) e de corte
(cortar Mindcrank tira Ascension + Mindcrank). Uso: python3 csb_pacote.py <lista.md> <saida.json>"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import csb_stefano as C
PACOTE_IN = ["Agent Frank Horrigan", "Branching Evolution"]; PACOTE_OUT = ["An Offer You Can't Refuse", "Negate"]
CANDS = ["Drown in the Loch", "Assassin's Trophy", "Putrefy", "Beast Within", "Deadly Rollick", "Atomize", "Casualties of War"]
if __name__ == "__main__":
    lista, out = sys.argv[1], sys.argv[2]
    base = C.parse(lista)
    assert len(base) == 99, len(base)
    nomes = sorted(set(c for c in base if c not in C.BASICOS) | set(PACOTE_IN) | set(CANDS) | {C.CMD, "Thassa's Oracle", "Demonic Consultation"})
    reconhece = {n: C.resolve(n) for n in nomes}
    nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos:", nao, flush=True)
    binc, balm = C.resumo(C.query(base))
    print("base:", len(binc), "combos,", len(balm), "quase", flush=True)
    pac = [c for c in base if c not in PACOTE_OUT] + PACOTE_IN
    assert len(pac) == 99
    res = {}
    def rodar(nome, deck, extra):
        inc, alm = C.resumo(C.query(deck))
        res[nome] = {"novos": {k: v for k, v in inc.items() if k not in binc}, "sumiram": [k for k in binc if k not in inc],
                     "quase_novos_com_a_peca": sorted(k for k in set(alm) - set(balm) if any(p in k for p in extra)), "quase_novos_n": len(set(alm) - set(balm)), "n_combos": len(inc)}
        print(nome, "novos:", list(res[nome]["novos"]), "| sumiram:", res[nome]["sumiram"], "| quase novos com a peca:", len(res[nome]["quase_novos_com_a_peca"]), flush=True)
    rodar("pacote_exato(-Offer -Negate +Horrigan +Branching)", pac, PACOTE_IN)
    for c in CANDS: rodar("base+" + c, base + [c], [c])
    rodar("pacote+Drown", pac + ["Drown in the Loch"], PACOTE_IN + ["Drown in the Loch"])
    d = list(base); [d.remove(x) for x in ("Negate", "Swiftfoot Boots")]; d += ["Thassa's Oracle", "Demonic Consultation"]
    inc, _ = C.resumo(C.query(d)); pos = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in inc)
    d = list(base); d.remove("Mindcrank"); d.append("Fathom Mage")
    inc, _ = C.resumo(C.query(d)); corte = not any("Bloodchief Ascension" in k and "Mindcrank" in k for k in inc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "base": {"incluidos": binc, "quase_n": len(balm)}, "por_variante": res,
               "controle_positivo_thassa_consultation": pos, "controle_de_corte_ascension_mindcrank_sumiu": corte,
               "base_tem_ascension_mindcrank": any("Bloodchief Ascension" in k and "Mindcrank" in k for k in binc)}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo:", pos, "| controle de corte (Ascension+Mindcrank some ao cortar o Mindcrank):", corte)
