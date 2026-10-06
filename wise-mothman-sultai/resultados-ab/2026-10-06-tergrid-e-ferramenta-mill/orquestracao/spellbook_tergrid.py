"""Commander Spellbook antes/depois para a Tergrid (Regra #4, adendo 2): lista atual do Mothman x lista com Tergrid no lugar de cada candidata a corte, com
(1) resolucao do nome via GET /cards/?q= (a API IGNORA em silencio nome que nao reconhece), (2) controle positivo (Thassa's Oracle + Demonic Consultation tem que aparecer) e
(3) controles de corte (cortar Mindcrank / Glen Elendra tem que fazer o combo respectivo sumir).
Uso: python3 spellbook_tergrid.py <lista.md> <saida.json>"""
import json, os, sys, time, urllib.request, urllib.parse
sys.path.insert(0, "/home/user/MTG-Code/wise-mothman-sultai/resultados-ab/2026-10-05-candidatas-pos-eoe/orquestracao")
import mm_csb as C
lista, out = sys.argv[1], sys.argv[2]
base = C.parse(lista)
def g(url):
    for t in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "MTG-Code-audit/1.0"}), timeout=90))
        except Exception:
            time.sleep(2 * (t + 1))
    raise RuntimeError(url)
def resolve(n):
    d = g("https://backend.commanderspellbook.com/cards/?" + urllib.parse.urlencode({"q": n, "limit": 10}))
    nomes = [x["name"] for x in d["results"]]
    for x in nomes:
        if x.lower() == n.lower(): return x
    for x in nomes:
        if x.split(" // ")[0].lower() == n.split(" // ")[0].lower(): return x
    return None
TG = "Tergrid, God of Fright // Tergrid's Lantern"
reconhece = {n: resolve(n) for n in (TG, "Thassa's Oracle", "Demonic Consultation", "Mindcrank", "Glen Elendra Archmage")}
print("nomes resolvidos no Spellbook:", reconhece, flush=True)
assert all(reconhece.values()), "nome nao reconhecido: resultado seria vacuo"
tg = reconhece[TG]
cen = {"base": ([], []),
       "tergrid_por_negate": (["Negate"], [tg]), "tergrid_por_strip_mine": (["Strip Mine"], [tg]), "tergrid_por_yavimaya_hollow": (["Yavimaya Hollow"], [tg]),
       "tergrid_por_cold_eyed_selkie": (["Cold-Eyed Selkie"], [tg]),
       "controle_positivo_Thassa+Consultation": (["Negate", "Swiftfoot Boots"], [reconhece["Thassa's Oracle"], reconhece["Demonic Consultation"]]),
       "controle_corte_sem_Mindcrank": (["Mindcrank"], []), "controle_corte_sem_Glen_Elendra": (["Glen Elendra Archmage"], [])}
res = {}
binc = None
for nome, (sai, entra) in cen.items():
    deck = list(base)
    for x in sai:
        deck.remove(x)
    deck += entra
    r = C.query(deck)
    inc, alm = C.resumo(r)
    if nome == "base":
        binc, balm = inc, alm
    res[nome] = {"n_main": len(deck), "sai": sai, "entra": entra, "n_incluidos": len(inc), "incluidos": inc, "quase": alm,
                 "novos_vs_base": sorted(set(inc) - set(binc)), "sumiram_vs_base": sorted(set(binc) - set(inc)),
                 "quase_novos_com_tergrid": [k for k in sorted(set(alm) - set(balm)) if tg in k], "identidade": r.get("identity"),
                 "bracket_tags": sorted({str(v.get("bracket")) for v in inc.values()})}
    print(f"{nome:40s} incluidos={len(inc)} novos={res[nome]['novos_vs_base']} sumiram={res[nome]['sumiram_vs_base']} quase_novos_com_Tergrid={len(res[nome]['quase_novos_com_tergrid'])}", flush=True)
json.dump({"nomes_resolvidos": reconhece, "cenarios": res}, open(out, "w"), ensure_ascii=False, indent=1)
