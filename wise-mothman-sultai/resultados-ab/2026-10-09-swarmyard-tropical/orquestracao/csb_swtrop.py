"""Commander Spellbook (Regra #4 + adendo) para a troca Swarmyard -> Tropical Island: nomes resolvidos e registrados; lista base (a de ANTES da troca, `lista-anterior-2026-10-09.md`); a lista com a troca (e1) e com a troca
mais Bojuka Bog -> Underground Sea (e2, nao aplicada); a lista VIVA conferida contra e1; controle positivo (Thassa + Consultation) e de corte (cortar Mindcrank tira Ascension + Mindcrank). Uso: python3 csb_swtrop.py <lista-base.md> <saida.json> <lista-viva.md>"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import csb_stefano as C
if __name__ == "__main__":
    lista, out, vivaf = sys.argv[1], sys.argv[2], sys.argv[3]
    base = C.parse(lista); assert len(base) == 99, len(base)
    nomes = sorted(set(c for c in base if c not in C.BASICOS) | {"Tropical Island", "Underground Sea", C.CMD, "Thassa's Oracle", "Demonic Consultation"})
    reconhece = {n: C.resolve(n) for n in nomes}; nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos:", nao, flush=True)
    binc, balm = C.resumo(C.query(base)); print("base:", len(binc), "combos,", len(balm), "quase", flush=True)
    res = {}
    def troca(d, a, b):
        d = list(d); d[d.index(a)] = b; return d
    def rodar(nome, deck, extra):
        inc, alm = C.resumo(C.query(deck))
        res[nome] = {"n_combos": len(inc), "novos": {k: v for k, v in inc.items() if k not in binc}, "sumiram": [k for k in binc if k not in inc], "quase_novos_com_a_peca": sorted(k for k in set(alm) - set(balm) if any(p in k for p in extra)), "quase_que_sumiram": sorted(set(balm) - set(alm))[:5]}
        print(nome, "| combos:", len(inc), "| novos:", list(res[nome]["novos"]), "| sumiram:", res[nome]["sumiram"], "| quase novos com a peca:", len(res[nome]["quase_novos_com_a_peca"]), "| quase que sumiram:", len(set(balm) - set(alm)), flush=True)
    e1 = troca(base, "Swarmyard", "Tropical Island"); rodar("e1_swarmyard_tropical", e1, ["Tropical Island"])
    e2 = troca(e1, "Bojuka Bog", "Underground Sea"); rodar("e2_e1_mais_bog_sea", e2, ["Tropical Island", "Underground Sea"])
    viva = C.parse(vivaf); assert len(viva) == 99, len(viva); viva_igual_e1 = sorted(viva) == sorted(e1); print("lista viva == e1 (multiconjunto de nomes):", viva_igual_e1, flush=True)
    d = list(base)
    for x in ("Swiftfoot Boots", "Heroic Intervention"): d.remove(x)
    d += ["Thassa's Oracle", "Demonic Consultation"]; assert len(d) == 99
    inc, _ = C.resumo(C.query(d)); pos = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in inc)
    d = list(base); d.remove("Mindcrank"); d.append("Fathom Mage")
    inc, _ = C.resumo(C.query(d)); corte = not any("Bloodchief Ascension" in k and "Mindcrank" in k for k in inc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "base": {"incluidos": binc, "quase_n": len(balm)}, "por_variante": res, "controle_positivo_thassa_consultation": pos, "controle_de_corte_ascension_mindcrank_sumiu": corte,
               "lista_viva_igual_e1": viva_igual_e1, "base_tem_ascension_mindcrank": any("Bloodchief Ascension" in k and "Mindcrank" in k for k in binc)}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo:", pos, "| controle de corte:", corte)
