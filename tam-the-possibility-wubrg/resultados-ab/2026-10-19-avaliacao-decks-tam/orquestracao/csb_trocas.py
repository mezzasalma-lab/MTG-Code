"""Commander Spellbook (Regra #4 + adendo) para o PACOTE de trocas propostas ao Tam: deck ANTES x DEPOIS de cada troca individual e do pacote inteiro (comandante + 99); nomes resolvidos; combos novos / perdidos; "quase" novos; controle positivo e de corte.
Uso: python3 csb_trocas.py <lista.md> <saida.json>"""
import json, os, sys, concurrent.futures as cf
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import csb_base as C
TROCAS = [("Leyline Immersion", "Swords to Plowshares"), ("Staff of Compleation", "Oath of Ajani"), ("Domri, Chaos Bringer", "Doubling Season"), ("Teferi's Talent", "Commodore Guff"), ("Baxter Building", "Karn's Bastion"), ("Liliana's Talent", "Mutational Advantage")]
EXTRAS = [("Teferi's Talent", "Carth the Lion"), ("Teferi's Talent", "Nicol Bolas, Dragon-God"), ("Dack Fayden", "Countersculpt"), ("Dack Fayden", "Jace's Machinations"), ("Dack Fayden", "Loyal Tutor")]
if __name__ == "__main__":
    lista, out = sys.argv[1], sys.argv[2]
    main, side = C.parse(lista); assert len(main) == 99
    nomes = sorted({x for p in TROCAS + EXTRAS for x in p} | set(main) | {C.CMD, "Thassa's Oracle", "Demonic Consultation", "Mind Stone"})
    with cf.ThreadPoolExecutor(3) as ex: reconhece = dict(zip(nomes, ex.map(C.resolve, nomes)))
    nao = [n for n, r in reconhece.items() if r is None]; print("nomes verificados:", len(nomes), "| NAO reconhecidos:", nao, flush=True)
    binc, balm = C.resumo(C.query(main)); print("antes:", len(binc), "combos,", len(balm), "quase", flush=True)
    def aplica(trocas):
        d = list(main)
        for sai, entra in trocas:
            assert sai in d and entra not in d, (sai, entra); d[d.index(sai)] = entra
        assert len(d) == 99; return d
    def roda(rot, trocas):
        inc, alm = C.resumo(C.query(aplica(trocas)))
        r = {"trocas": trocas, "n_combos": len(inc), "novos": {k: v for k, v in inc.items() if k not in binc}, "sumiram": [k for k in binc if k not in inc], "quase_novos": sorted(set(alm) - set(balm)), "quase_que_sumiram": sorted(set(balm) - set(alm))}
        print(f"{rot:62s} | combos {len(inc)} | novos {[(k, v['bracket']) for k, v in r['novos'].items()]} | sumiram {r['sumiram']} | quase +{len(r['quase_novos'])} -{len(r['quase_que_sumiram'])}", flush=True); return rot, r
    res = {}
    jobs = [(f"{a} -> {b}", [(a, b)]) for a, b in TROCAS] + [("PACOTE (as 6 trocas)", TROCAS)] + [(f"[opcao] {a} -> {b}", [(a, b)]) for a, b in EXTRAS]
    with cf.ThreadPoolExecutor(3) as ex:
        for rot, r in ex.map(lambda j: roda(*j), jobs): res[rot] = r
    pos = list(main); pos.remove("Sol Ring"); pos.remove("Arcane Signet"); pos += ["Thassa's Oracle", "Demonic Consultation"]
    pinc, _ = C.resumo(C.query(pos)); achou = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in pinc)
    cor = list(main); cor.remove("Sol Ring"); cor.remove("Arcane Signet"); cor += ["Thassa's Oracle", "Mind Stone"]
    cinc, _ = C.resumo(C.query(cor)); sumiu = not any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in cinc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "antes": {"incluidos": binc, "quase_n": len(balm)}, "trocas": res, "controle_positivo": achou, "controle_de_corte": sumiu}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo:", achou, "| controle de corte:", sumiu)
