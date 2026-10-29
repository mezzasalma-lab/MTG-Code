"""Commander Spellbook (Regra #4 + adendo) para cada troca 'terreno X -> Underground Sea' do lote U: nomes resolvidos e registrados; lista base (a atual, `lista.md`); UMA consulta por candidato (a lista com o terreno trocado);
controle positivo (Thassa + Consultation) e de corte (cortar Mindcrank tira Ascension + Mindcrank). Uso: python3 csb_under.py <lista.md> <saida.json>"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import csb_stefano as C
CANDS = ["Bojuka Bog", "Watery Grave", "Morphic Pool", "Swamp", "Island", "Minamo, School at Water's Edge", "Shifting Woodland", "Zagoth Triome", "Strip Mine", "Takenuma, Abandoned Mire", "Boseiju, Who Endures", "Urza's Saga"]
if __name__ == "__main__":
    lista, out = sys.argv[1], sys.argv[2]
    base = C.parse(lista); assert len(base) == 99, len(base)
    nomes = sorted(set(c for c in base if c not in C.BASICOS) | set(CANDS) | {"Underground Sea", C.CMD, "Thassa's Oracle", "Demonic Consultation"})
    reconhece = {n: C.resolve(n) for n in nomes}; nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos:", nao, flush=True)
    binc, balm = C.resumo(C.query(base)); print("base:", len(binc), "combos,", len(balm), "quase", flush=True)
    res = {}
    for sai in CANDS:
        d = list(base)
        if sai in C.BASICOS or sai not in d:
            # basicos nao estao em `base` como nomes distintos? C.parse expande as copias; garantir a troca de UMA copia
            pass
        assert sai in d, sai
        d[d.index(sai)] = "Underground Sea"
        inc, alm = C.resumo(C.query(d))
        res[sai] = {"n_combos": len(inc), "novos": {k: v for k, v in inc.items() if k not in binc}, "sumiram": [k for k in binc if k not in inc], "quase_novos_com_a_peca": sorted(k for k in set(alm) - set(balm) if "Underground Sea" in k), "quase_que_sumiram": sorted(set(balm) - set(alm))[:8]}
        print(f"{sai:34s} -> Underground Sea | combos: {len(inc)} | novos: {list(res[sai]['novos'])} | sumiram: {res[sai]['sumiram']} | quase novos com a peca: {len(res[sai]['quase_novos_com_a_peca'])} | quase que sumiram: {len(set(balm) - set(alm))}", flush=True)
    d = list(base)
    for x in ("Swiftfoot Boots", "Heroic Intervention"): d.remove(x)
    d += ["Thassa's Oracle", "Demonic Consultation"]; assert len(d) == 99
    inc, _ = C.resumo(C.query(d)); pos = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in inc)
    d = list(base); d.remove("Mindcrank"); d.append("Fathom Mage")
    inc, _ = C.resumo(C.query(d)); corte = not any("Bloodchief Ascension" in k and "Mindcrank" in k for k in inc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "base": {"incluidos": binc, "quase_n": len(balm)}, "por_troca": res, "controle_positivo_thassa_consultation": pos, "controle_de_corte_ascension_mindcrank_sumiu": corte,
               "base_tem_ascension_mindcrank": any("Bloodchief Ascension" in k and "Mindcrank" in k for k in binc)}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo:", pos, "| controle de corte:", corte)
