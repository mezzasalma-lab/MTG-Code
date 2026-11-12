"""Ledger de gatilhos do The Wise Mothman na partida manual #3: TETO de gatilhos legitimos por bloco de turno x contadores que o log mostra.
Uso: python3 -I ledger_contadores.py [dados/partida.json.xz]   (saida em Markdown; sai com 1 se algum total do log passar do teto cumulativo)
REGRAS (rulings do Scryfall de 2024-03-08, resumos/rulings_scryfall.json): "The cards are milled all at once, so abilities that trigger 'whenever one or more nonland cards are milled' will trigger exactly
once as long as at least one nonland card was milled" e "If more than one player is instructed to mill at the same time ... The Wise Mothman's last ability will trigger just once".
Logo cada resolucao do Altar of the Brood ("each opponent mills a card": os 3 oponentes milam JUNTOS) vale UM gatilho do Mothman, nao 3; e o gatilho poe UM contador em CADA alvo
(ate X alvos): para um contador a mais na MESMA criatura e' preciso OUTRO gatilho.
O teto abaixo e' o numero maximo de gatilhos, SUPONDO que todo mill teve pelo menos 1 carta nao-terreno (o log nao mostra mill de oponente: limite declarado pelo usuario desde a #1).
FONTES (leitura minha do trace + respostas do usuario de 2026-11-05):
 - rad dos oponentes: cada um tem 1 rad por ETB/ataque do Mothman e mila no inicio da fase principal 1 DELE: 1 gatilho por oponente por rodada (3 oponentes: 'a mesa de 4' das partidas #1 e #2).
 - Altar of the Brood: 1 gatilho por permanente MEU que entra (outro que o Altar), resolvido com o Mothman em campo.
 - meu rad: 1 gatilho por mill meu que tenha carta nao-terreno (aparece no log como library->graveyard).
"""
import json, lzma, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(aqui, "dados", "partida.json.xz")
T = json.load(lzma.open(caminho))
N_OPP = 3
def contadores(nome, t):
    """quantos eventos de +1/+1 (cliques de +1 isolados ou saltos) o log tem para `nome` no bloco t, e o valor final"""
    vals = [r["counters"].get("+1 / +1", {}).get("count", 0) for r in T[t - 1] if r["name"] == nome and "+1 / +1" in r["counters"]]
    return vals
def ult(nome, t):
    v = contadores(nome, t)
    return v[-1] if v else None
MM, SIX, WIT = "The Wise Mothman", "Six", "Evolution Witness"
# (bloco, fonte, teto minimo certo, teto maximo, nota)
FONTES = {
 4: [("Altar: a entrada do Mothman (o Forest do T4 entrou ANTES dele, sem Mothman em campo)", 1, 1, ""),
     (f"rad dos {N_OPP} oponentes (1 rad cada, do ETB)", N_OPP, N_OPP, "mill no turno deles, fora do log")],
 5: [("meu rad: Gyre Sage milada (aparece no log)", 1, 1, "unico mill visivel"),
     ("Altar: Forest (T5)", 1, 1, ""), ("Altar: Six", 1, 1, "Six ja pode ser alvo"),
     (f"rad dos {N_OPP} oponentes", N_OPP, N_OPP, "turnos deles, apos o ataque do T5")],
 6: [("meu rad: ESQUECIDO pelo usuario (nenhum mill meu no T6)", 0, 0, "teria 1 gatilho se milasse nao-terreno"),
     ("Altar: Overgrown Tomb", 1, 1, "entrou antes da Witness"), ("Altar: Evolution Witness", 1, 1, ""), ("Altar: Zagoth Triome (Nature's Lore)", 1, 1, "Nature's Lore e' feitico: nao entra"),
     ("Altar: Gyre Sage (cemiterio -> campo no log; arrastada, voltou para a mao)", 0, 1, "so' conta se de fato entrou"),
     ("Altar: Rejuvenating Springs (misclick, terminou em campo)", 0, 1, "terminou em campo"),
     (f"rad dos {N_OPP} oponentes", N_OPP, N_OPP, "turnos deles, apos o ataque do T6")],
}
print("| bloco | fontes | teto certo | teto maximo | contadores no log (eventos / valor final) |")
print("|---|---|---|---|---|")
cum = {"min": 0, "max": 0}
for t in (4, 5, 6):
    mn = sum(f[1] for f in FONTES[t]); mx = sum(f[2] for f in FONTES[t]); cum["min"] += mn; cum["max"] += mx
    log = []
    for n, rot in ((MM, "Mothman"), (SIX, "Six"), (WIT, "Witness")):
        v = contadores(n, t)
        if v:
            log.append(f"{rot}: {len(v)} registros, final {v[-1]}")
    print(f"| T{t} | " + "; ".join(f[0] for f in FONTES[t]) + f" | {mn} | {mx} | {'; '.join(log) or 'nenhum'} |")
print()
mm_cum = ult(MM, 5) or 0
print(f"**Mothman**: {mm_cum} contadores ao fim do T5 (T4 = 0). Teto de gatilhos T4+T5 = {sum(f[2] for t in (4, 5) for f in FONTES[t])}: cada gatilho da ao Mothman no maximo +1.")
print(f"**Metodo do usuario (resposta de 2026-11-05)**: 1 (meu rad) + 6 (3 oponentes x 2 permanentes: Forest e Six) = 7 dos 8 contadores. Pela ruling, o Altar vale **1 gatilho por permanente**: 2, nao 6. O 8o contador nao foi explicado.")
witn = ult(WIT, 6) or 0; six = ult(SIX, 6) or 0
print(f"**T6**: Six {six} e Witness {witn} contadores, Mothman fica em {ult(MM, 6) or 0}; a Witness precisa de >= {witn} gatilhos (um por evento de contador), o teto do T6 e' {sum(f[2] for f in FONTES[6])} (certo: {sum(f[1] for f in FONTES[6])}).")
# devolucoes do cemiterio no T6 x eventos de contador da Witness
ret = [r["name"] for r in T[5] if r["fromZone"] == "graveyard" and r["toZone"] in ("hand", "battlefield")]
unicas = list(dict.fromkeys(ret))
print(f"**Devolucoes do cemiterio no T6**: {len(unicas)} cartas ({', '.join(unicas)}) para {witn} eventos de contador na Witness (um evento = um gatilho 'target permanent card'): **{len(unicas) - witn:+d}**.")
ok = mm_cum <= sum(f[2] for t in (4, 5) for f in FONTES[t]) and witn <= sum(f[2] for f in FONTES[6])
print(f"\nTotais do log dentro do teto cumulativo (T4+T5 para o Mothman, T6 para a Witness): {'sim' if ok else 'NAO'}")
sys.exit(0 if ok else 1)
