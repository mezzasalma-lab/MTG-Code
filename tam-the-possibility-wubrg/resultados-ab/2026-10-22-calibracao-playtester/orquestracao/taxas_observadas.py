"""Taxas de interacao do OPONENTE do playtester do Archidekt, observadas nos 5 goldfish manuais do usuario (Tam). SO' dos brutos (`goldfish_manual_N_bruto.json`, zona `opponentsCards`) + oraculo do cache do Scryfall.
Cada carta da zona `opponentsCards` e' um evento. Categoria (minha, pelo oraculo; o jogador nao classificou): criatura/ficha, remocao pontual, contramagia, efeito em massa (wipe/sacrificio/devolve atacantes), aura, outro.
Saida: tabela por turno, taxas por rodada (1 turno meu + 3 turnos de oponente) e IC95% de Poisson (Garwood), em markdown. Nao interpreta."""
import json, os, math, collections
AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.abspath(os.path.join(AQUI, "..", ".."))
LOGS = [("#1", "2026-10-19-goldfish-manual-1", "goldfish_manual_1_bruto.json"), ("#2", "2026-10-20-goldfish-manual-2", "goldfish_manual_2_bruto.json"),
        ("#3", "2026-10-21-goldfish-manual-3", "goldfish_manual_3_bruto.json"), ("#4", "2026-10-21-goldfish-manual-4", "goldfish_manual_4_bruto.json"),
        ("#5", "2026-10-21-goldfish-manual-5", "goldfish_manual_5_bruto.json")]
# categoria por NOME (pelo oraculo/Scryfall; fichas = criaturas do playtester sem oraculo no cache)
CAT = {
    "Nature's Claim": "remocao_pontual", "Assassin's Trophy": "remocao_pontual", "Disenchant": "remocao_pontual", "Murderous Rider // Swift End": "remocao_pontual", "Loran of the Third Path": "remocao_pontual",
    "Vex": "contramagia", "Ertai's Scorn": "contramagia",
    "Split Up": "efeito_em_massa", "Cleansing Nova": "efeito_em_massa", "Damning Verdict": "efeito_em_massa", "Promise of Loyalty": "efeito_em_massa", "Aetherize": "efeito_em_massa",
    "Witness Protection": "aura",
    "Golem": "criatura", "Doombot": "criatura", "Zombie": "criatura", "Carnivore": "criatura", "Warrior": "criatura", "Metallic Sliver": "criatura", "Graveborn": "criatura", "Spider": "criatura",
    "Goblin Wizard": "criatura", "Eldrazi Angel": "criatura", "Junji, the Midnight Sky": "criatura",
}
CATS = ["criatura", "remocao_pontual", "contramagia", "efeito_em_massa", "aura"]


def ic_poisson(k, expo):
    """IC95% exato (Garwood) da taxa k/expo."""
    from math import gamma
    def chi2_ppf(p, df):   # busca binaria na CDF do qui-quadrado via serie da gama incompleta
        def cdf(x):
            a = df / 2.0; s = 0.0; term = 1.0 / a; s = term; n = 0
            while abs(term) > 1e-12 and n < 2000:
                n += 1; term *= (x / 2.0) / (a + n); s += term
            return (x / 2.0) ** a * math.exp(-x / 2.0) * s / gamma(a)
        lo, hi = 0.0, 200.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if cdf(mid) < p: lo = mid
            else: hi = mid
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else chi2_ppf(0.025, 2 * k) / 2
    hi = chi2_ppf(0.975, 2 * (k + 1)) / 2
    return lo / expo, hi / expo


ev = []        # (log, turno, nome, categoria)
turnos = {}    # log -> n de turnos
for rot, pasta, arq in LOGS:
    d = json.load(open(os.path.join(ARQ, pasta, "dados", arq)))
    turnos[rot] = len(d)
    for t, blk in enumerate(d, 1):
        for e in blk:
            if e.get("toZone") == "opponentsCards":
                ev.append((rot, t, e["name"], CAT[e["name"]]))
print("# Taxas de interacao do oponente do playtester (5 goldfish manuais do Tam)\n")
print("Cada carta que aparece na zona `opponentsCards` do log e' um evento. **Turno** = o bloco do log (o turno do usuario + os turnos de oponente que vem depois dele, ate' o proximo untap dele).\n")
print("| log | turnos | eventos | por turno |\n|---|---|---|---|")
for rot in turnos:
    n = sum(1 for e in ev if e[0] == rot)
    print(f"| {rot} | {turnos[rot]} | {n} | {n / turnos[rot]:.2f} |")
tot_t = sum(turnos.values())
print(f"| **total** | **{tot_t}** | **{len(ev)}** | **{len(ev) / tot_t:.2f}** |\n")
print("## Por turno (todos os logs juntos)\n\n| turno | logs com esse turno | eventos | por log | cartas |\n|---|---|---|---|---|")
for t in range(1, max(turnos.values()) + 1):
    nlog = sum(1 for r in turnos if turnos[r] >= t)
    es = [e for e in ev if e[1] == t]
    print(f"| T{t} | {nlog} | {len(es)} | {len(es) / nlog:.2f} | {', '.join(f'{e[2]} ({e[0]})' for e in es) or '—'} |")
print("\n## Por categoria, de T4 em diante (nenhum evento antes do T4 nos 5 logs)\n")
expo = sum(max(0, turnos[r] - 3) for r in turnos)
print(f"Exposicao: {expo} turnos (T4 ate' o fim de cada log). Taxa = eventos por turno do usuario (a mesa inteira, 3 oponentes); IC95% de Poisson (Garwood).\n")
print("| categoria | eventos | por turno | IC95% | por partida de 12 turnos (T4-T12 = 9 turnos) |\n|---|---|---|---|---|")
for c in CATS + ["total"]:
    k = sum(1 for e in ev if e[3] == c or c == "total")
    lo, hi = ic_poisson(k, expo)
    print(f"| {c} | {k} | {k / expo:.3f} | {lo:.3f}–{hi:.3f} | {9 * k / expo:.2f} ({9 * lo:.2f}–{9 * hi:.2f}) |")
print("\nAntes do T4: 0 eventos em %d turnos (T1-T3 dos 5 logs)." % sum(min(3, turnos[r]) for r in turnos))
