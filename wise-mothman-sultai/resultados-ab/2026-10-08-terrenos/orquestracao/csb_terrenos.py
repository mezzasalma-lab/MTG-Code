"""Commander Spellbook (Regra #4 + adendo) para os terrenos candidatos: nomes resolvidos e registrados; lista base (a atual); base + CADA terreno candidato (sem cortar: se a peca entra em combo, aparece); as listas dos 3 ajustes
medidos (Swarmyard e Yavimaya Hollow por Swamp / Forest, por basicos); controle positivo (Thassa + Consultation) e de corte (cortar Mindcrank tira Ascension + Mindcrank). Uso: python3 csb_terrenos.py <lista.md> <saida.json>"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import csb_stefano as C
CANDS = ["Woodland Cemetery", "Drowned Catacomb", "Hinterland Harbor", "Llanowar Wastes", "Underground River", "Yavimaya Coast", "Opulent Palace", "Underground Mortuary", "Undercity Sewers", "Blooming Marsh", "Darkslick Shores", "Botanical Sanctum",
         "Darkbore Pathway // Slitherbore Pathway", "Jungle Hollow", "Dismal Backwater", "Yavimaya, Cradle of Growth"]
if __name__ == "__main__":
    lista, out = sys.argv[1], sys.argv[2]
    base = C.parse(lista); assert len(base) == 99, len(base)
    nomes = sorted(set(c for c in base if c not in C.BASICOS) | set(CANDS) | {C.CMD, "Thassa's Oracle", "Demonic Consultation"})
    reconhece = {n: C.resolve(n) for n in nomes}; nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos:", nao, flush=True)
    binc, balm = C.resumo(C.query(base)); print("base:", len(binc), "combos,", len(balm), "quase", flush=True)
    res = {}
    def rodar(nome, deck, extra):
        inc, alm = C.resumo(C.query(deck))
        res[nome] = {"n_combos": len(inc), "novos": {k: v for k, v in inc.items() if k not in binc}, "sumiram": [k for k in binc if k not in inc], "quase_novos_com_a_peca": sorted(k for k in set(alm) - set(balm) if any(p in k for p in extra))}
        print(nome, "| combos:", len(inc), "| novos:", list(res[nome]["novos"]), "| sumiram:", res[nome]["sumiram"], "| quase novos com a peca:", len(res[nome]["quase_novos_com_a_peca"]), flush=True)
    for c in CANDS: rodar("base+" + c, base + [c], [c])
    def troca(d, a, b):
        d = list(d); d[d.index(a)] = b; return d
    t3 = troca(troca(base, "Swarmyard", "Swamp"), "Yavimaya Hollow", "Forest"); rodar("t3_swarmyard_swamp_hollow_forest", t3, [])
    d = list(base)
    for x in ("Swiftfoot Boots", "Heroic Intervention"): d.remove(x)          # duas cartas que EXISTEM na lista atual (o Negate saiu em 2026-10-08)
    d += ["Thassa's Oracle", "Demonic Consultation"]; assert len(d) == 99
    inc, _ = C.resumo(C.query(d)); pos = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in inc)
    d = list(base); d.remove("Mindcrank"); d.append("Fathom Mage")
    inc, _ = C.resumo(C.query(d)); corte = not any("Bloodchief Ascension" in k and "Mindcrank" in k for k in inc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "base": {"incluidos": binc, "quase_n": len(balm)}, "por_variante": res, "controle_positivo_thassa_consultation": pos, "controle_de_corte_ascension_mindcrank_sumiu": corte,
               "base_tem_ascension_mindcrank": any("Bloodchief Ascension" in k and "Mindcrank" in k for k in binc)}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo:", pos, "| controle de corte:", corte)
