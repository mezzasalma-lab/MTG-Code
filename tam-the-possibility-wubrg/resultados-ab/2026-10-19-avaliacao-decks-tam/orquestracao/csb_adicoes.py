"""Commander Spellbook (Regra #4 + adendo) para as candidatas a ENTRAR no Tam (sem cortar nada): para cada candidata X, o deck exato (comandante + 99) + X; registra (1) se o Spellbook RECONHECE o nome (a API ignora nome desconhecido, sem erro),
(2) combos NOVOS e (3) combos "quase" que viram combo. Mais os controles: positivo (Thassa + Consultation) e de corte (so' o Thassa: o combo some). Uso: python3 csb_adicoes.py <lista.md> <saida.json>"""
import json, os, sys, concurrent.futures as cf
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import csb_base as C
CAND = ["Loyal Tutor", "Nicol Bolas, Dragon-God", "Carth the Lion", "Commodore Guff", "Doubling Season", "The Theorist, Jace Beleren", "Interplanar Beacon", "Chromatic Lantern", "Farseek", "Deepglow Skate", "Swords to Plowshares",
        "Karn's Bastion", "Atraxa, Praetors' Voice", "Jace, Multiverse Architect", "Tekuthal, Inquiry Dominus", "Teferi, Master of Time", "Narset, Parter of Veils", "Ugin, the Spirit Dragon", "Liliana, Dreadhorde General", "Nature's Lore",
        "Lae'zel, Vlaakith's Champion", "Evolution Sage", "Spark Double", "Three Visits", "Oath of Ajani", "Teferi, Time Raveler", "Brokers Ascendancy", "Delighted Halfling", "Path to Exile", "Vorinclex, Monstrous Raider",
        "Mutational Advantage", "Tomik, Orzhov Lawmage", "Gideon's Memorial", "Reflecting Pool", "Godless Shrine", "Chandra, Torch of Defiance", "Chandra, Chill of Compliance"]
if __name__ == "__main__":
    lista, out = sys.argv[1], sys.argv[2]
    main, side = C.parse(lista); assert len(main) == 99
    nomes = sorted(set(main) | set(CAND) | {C.CMD, "Thassa's Oracle", "Demonic Consultation", "Mind Stone"})
    with cf.ThreadPoolExecutor(3) as ex: reconhece = dict(zip(nomes, ex.map(C.resolve, nomes)))
    nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos:", nao, flush=True)
    binc, balm = C.resumo(C.query(main)); print("base:", len(binc), "combos,", len(balm), "quase", flush=True)
    def um(x):
        inc, alm = C.resumo(C.query(main + [x]))
        return x, {"n_combos": len(inc), "novos": {k: v for k, v in inc.items() if k not in binc}, "quase_viraram_combo": [k for k in inc if k not in binc and k in balm],
                   "quase_novos_com_a_peca": sorted(k for k in set(alm) - set(balm) if x in k)}
    res = {}
    with cf.ThreadPoolExecutor(3) as ex:
        for x, r in ex.map(um, CAND):
            res[x] = r; print(f"{x:34s} | combos {r['n_combos']} | novos: {[(k, v['bracket']) for k, v in r['novos'].items()]} | quase novos c/ a peça: {len(r['quase_novos_com_a_peca'])}", flush=True)
    pos = list(main); pos.remove("Sol Ring"); pos.remove("Arcane Signet"); pos += ["Thassa's Oracle", "Demonic Consultation"]
    pinc, _ = C.resumo(C.query(pos)); achou = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in pinc)
    cor = list(main); cor.remove("Sol Ring"); cor.remove("Arcane Signet"); cor += ["Thassa's Oracle", "Mind Stone"]
    cinc, _ = C.resumo(C.query(cor)); sumiu = not any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in cinc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "base": {"incluidos": binc, "quase_n": len(balm)}, "adicoes": res, "controle_positivo": achou, "controle_de_corte": sumiu}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo:", achou, "| controle de corte (sem a Consultation some):", sumiu)
