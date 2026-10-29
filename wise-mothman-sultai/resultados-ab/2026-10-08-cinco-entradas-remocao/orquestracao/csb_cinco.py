"""Commander Spellbook (Regra #4 + adendo) para as CINCO ENTRADAS (Agent Frank Horrigan, Branching Evolution, Atomize, Casualties of War, Assassin's Trophy) e os 5 cortes candidatos.
1) resolve cada nome e REGISTRA se o Spellbook reconhece (a API ignora nome desconhecido, sem erro); 2) lista base; 3) base + CADA entrada (sem cortar: se a PECA entra em combo, aparece); 4) as cinco juntas, sem cortar;
5) as listas EXATAS dos conjuntos de corte (cada um dos 7 do A/B); 6) controle positivo (Thassa + Consultation) e de corte (cortar Mindcrank tira Ascension + Mindcrank). Uso: python3 csb_cinco.py <lista.md> <saida.json>"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import csb_stefano as C
ENTRAM = ["Agent Frank Horrigan", "Branching Evolution", "Atomize", "Casualties of War", "Assassin's Trophy"]
OFFER, NEG, DSP, ARC, WAVE, DEL, TEAR, VATS = "An Offer You Can't Refuse", "Negate", "Didn't Say Please", "Arcane Denial", "Wave Goodbye", "Toxic Deluge", "Tear Asunder", "V.A.T.S."
CORTES = {"s1_vats_wave_deluge": [VATS, WAVE, DEL], "s2_vats_arcane_dsp": [VATS, ARC, DSP], "s3_vats_wave_arcane": [VATS, WAVE, ARC], "s4_vats_wave_dsp": [VATS, WAVE, DSP],
          "s5_vats_deluge_arcane": [VATS, DEL, ARC], "s6_vats_deluge_dsp": [VATS, DEL, DSP], "s7_tear_wave_deluge": [TEAR, WAVE, DEL]}
if __name__ == "__main__":
    lista, out = sys.argv[1], sys.argv[2]
    base = C.parse(lista); assert len(base) == 99, len(base)
    nomes = sorted(set(c for c in base if c not in C.BASICOS) | set(ENTRAM) | {C.CMD, "Thassa's Oracle", "Demonic Consultation"})
    reconhece = {n: C.resolve(n) for n in nomes}; nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos:", nao, flush=True)
    binc, balm = C.resumo(C.query(base)); print("base:", len(binc), "combos,", len(balm), "quase", flush=True)
    res = {}
    def rodar(nome, deck, extra):
        inc, alm = C.resumo(C.query(deck))
        res[nome] = {"n_combos": len(inc), "novos": {k: v for k, v in inc.items() if k not in binc}, "sumiram": [k for k in binc if k not in inc],
                     "quase_novos_com_a_peca": sorted(k for k in set(alm) - set(balm) if any(p in k for p in extra)), "quase_novos_n": len(set(alm) - set(balm))}
        print(nome, "| combos:", len(inc), "| novos:", list(res[nome]["novos"]), "| sumiram:", res[nome]["sumiram"], "| quase novos com a peca:", len(res[nome]["quase_novos_com_a_peca"]), flush=True)
    for c in ENTRAM: rodar("base+" + c, base + [c], [c])
    rodar("base+as_cinco", base + ENTRAM, ENTRAM)
    for nome, tres in CORTES.items():
        deck = [c for c in base if c not in (OFFER, NEG, *tres)] + ENTRAM
        assert len(deck) == 99, (nome, len(deck))
        rodar("lista_exata_" + nome, deck, ENTRAM)
    d = list(base); [d.remove(x) for x in ("Negate", "Swiftfoot Boots")]; d += ["Thassa's Oracle", "Demonic Consultation"]
    inc, _ = C.resumo(C.query(d)); pos = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in inc)
    d = list(base); d.remove("Mindcrank"); d.append("Fathom Mage")
    inc, _ = C.resumo(C.query(d)); corte = not any("Bloodchief Ascension" in k and "Mindcrank" in k for k in inc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "base": {"incluidos": binc, "quase_n": len(balm)}, "por_variante": res,
               "controle_positivo_thassa_consultation": pos, "controle_de_corte_ascension_mindcrank_sumiu": corte,
               "base_tem_ascension_mindcrank": any("Bloodchief Ascension" in k and "Mindcrank" in k for k in binc)}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo:", pos, "| controle de corte (Ascension+Mindcrank some ao cortar o Mindcrank):", corte)
