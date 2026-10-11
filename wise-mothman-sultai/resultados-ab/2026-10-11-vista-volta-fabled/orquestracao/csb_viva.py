"""Commander Spellbook (Regra #4 + adendo) para a troca aplicada (Prismatic Vista -> Fabled Passage): nomes resolvidos; lista de ANTES (`lista-anterior-2026-10-11.md`) x lista VIVA (`lista.md`); a viva tem de ser a de antes com a troca (multiconjunto);
controle positivo (Thassa + Consultation) e de corte (cortar Mindcrank tira Ascension + Mindcrank). Uso: python3 csb_viva.py <lista-anterior.md> <lista-viva.md> <saida.json>"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import csb_stefano as C
if __name__ == "__main__":
    ant, viva, out = sys.argv[1:4]
    base = C.parse(ant); v = C.parse(viva); assert len(base) == len(v) == 99
    esperado = list(base); esperado[esperado.index("Prismatic Vista")] = "Fabled Passage"; igual = sorted(v) == sorted(esperado)
    nomes = sorted(set(c for c in base + v if c not in C.BASICOS) | {C.CMD, "Thassa's Oracle", "Demonic Consultation"})
    reconhece = {n: C.resolve(n) for n in nomes}; nao = [n for n, r in reconhece.items() if r is None]
    print("nomes verificados:", len(nomes), "| NAO reconhecidos:", nao, "| viva == anterior com a troca:", igual, flush=True)
    binc, balm = C.resumo(C.query(base)); vinc, valm = C.resumo(C.query(v))
    novos = [k for k in vinc if k not in binc]; sumiram = [k for k in binc if k not in vinc]
    print("antes:", len(binc), "combos,", len(balm), "quase | viva:", len(vinc), "combos,", len(valm), "quase | novos:", novos, "| sumiram:", sumiram, "| quase novos:", len(set(valm) - set(balm)), "| quase que sumiram:", len(set(balm) - set(valm)), flush=True)
    d = list(base)
    for x in ("Swiftfoot Boots", "Heroic Intervention"): d.remove(x)
    d += ["Thassa's Oracle", "Demonic Consultation"]; assert len(d) == 99
    inc, _ = C.resumo(C.query(d)); pos = any("Thassa's Oracle" in k and "Demonic Consultation" in k for k in inc)
    d = list(base); d.remove("Mindcrank"); d.append("Fathom Mage")
    inc, _ = C.resumo(C.query(d)); corte = not any("Bloodchief Ascension" in k and "Mindcrank" in k for k in inc)
    json.dump({"reconhece": reconhece, "nao_reconhecidos": nao, "viva_igual_anterior_com_a_troca": igual, "combos_antes": binc, "combos_viva": vinc, "novos": novos, "sumiram": sumiram, "quase_novos": sorted(set(valm) - set(balm)), "quase_que_sumiram": sorted(set(balm) - set(valm)),
               "controle_positivo_thassa_consultation": pos, "controle_de_corte_ascension_mindcrank_sumiu": corte}, open(out, "w"), ensure_ascii=False, indent=1)
    print("controle positivo:", pos, "| controle de corte:", corte)
