"""Commander Spellbook (Regra #4 + adendo) para os terrenos com proxy (Underground Sea, Bayou, Tropical Island, Prismatic Vista): nomes resolvidos e registrados; lista base (a atual); base + CADA terreno candidato (sem cortar: se a peca entra em combo, aparece); as listas dos 3 ajustes
medidos (Swarmyard e Yavimaya Hollow por Swamp / Forest, por basicos); controle positivo (Thassa + Consultation) e de corte (cortar Mindcrank tira Ascension + Mindcrank). Uso: python3 csb_proxy.py <lista-base.md> <saida.json> [<lista-viva.md>]   (base = lista de 2026-10-08, ANTES da troca de terrenos; a lista viva, se dada, e' conferida contra a variante d1)"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import csb_stefano as C
CANDS = ["Underground Sea", "Bayou", "Tropical Island", "Prismatic Vista"]
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
    c1 = troca(troca(base, "Yavimaya Hollow", "Underground Sea"), "Bojuka Bog", "Bayou"); rodar("c1_hollow_sea_bog_bayou", c1, ["Underground Sea", "Bayou"])
    v1 = troca(base, "Fabled Passage", "Prismatic Vista"); rodar("v1_passage_vista", v1, ["Prismatic Vista"])
    d1 = troca(troca(base, "Yavimaya Hollow", "Bayou"), "Fabled Passage", "Prismatic Vista"); rodar("d1_hollow_bayou_passage_vista", d1, ["Bayou", "Prismatic Vista"])
    d2 = troca(d1, "Bojuka Bog", "Underground Sea"); rodar("d2_d1_mais_bog_sea", d2, ["Bayou", "Prismatic Vista", "Underground Sea"])
    d3 = troca(d2, "Minamo, School at Water's Edge", "Tropical Island"); rodar("d3_d2_mais_minamo_tropical", d3, ["Bayou", "Prismatic Vista", "Underground Sea", "Tropical Island"])
    d4 = troca(d2, "Shifting Woodland", "Tropical Island"); rodar("d4_d2_mais_woodland_tropical", d4, ["Bayou", "Prismatic Vista", "Underground Sea", "Tropical Island"])
    viva_igual_d1 = None
    if len(sys.argv) > 3:
        viva = C.parse(sys.argv[3]); assert len(viva) == 99, len(viva); viva_igual_d1 = sorted(viva) == sorted(d1); print("lista viva == d1 (como multiconjunto de nomes):", viva_igual_d1, flush=True)
    d = list(base)
    for x in ("Swiftfoot Boots", "Heroic Intervention"): d.remove(x)          # duas cartas que EXISTEM na lista atual (o Negate saiu em 2026-10-08)
    d += ["Thassa's Oracle", "Demonic Consultation"]; assert len(d) == 99
    inc, _ = C.resumo(C.query(d)); pos = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in inc)
    d = list(base); d.remove("Mindcrank"); d.append("Fathom Mage")
    inc, _ = C.resumo(C.query(d)); corte = not any("Bloodchief Ascension" in k and "Mindcrank" in k for k in inc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "base": {"incluidos": binc, "quase_n": len(balm)}, "por_variante": res, "controle_positivo_thassa_consultation": pos, "controle_de_corte_ascension_mindcrank_sumiu": corte,
               "lista_viva_igual_d1": viva_igual_d1, "base_tem_ascension_mindcrank": any("Bloodchief Ascension" in k and "Mindcrank" in k for k in binc)}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo:", pos, "| controle de corte:", corte)
