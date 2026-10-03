"""Ledger dos Treasures do log, por id de ficha: em cada turno, o que o log registra (criada, virada, desvirada) e quando o id
SOME (ficha que o log nao registra ao sair: sacrificada por mana, morta, etc.). Premissa a conferir com o usuario: 'virada' = atacou
animada pelo Vihaan; ficha que some depois de virada = sacrificada/morta. Uso: python3 ledger_treasures.py ../dados/partida.json.xz"""
import json, lzma, sys
from collections import OrderedDict, defaultdict
d = json.load(lzma.open(sys.argv[1], 'rt'))
tok = OrderedDict()
for n, t in enumerate(d, 1):
    for r in t:
        if r['token']:
            ev = ('CRIADA' if r['fromZone'] is None and r['toZone'] == 'battlefield' else ('tap' if r['tapped'] else 'untap')) + ('+ctr' if r['counters'] else '')
            tok.setdefault(r['id'], []).append((n, ev))
print("Treasures (ids do log): turno -> eventos")
vivos_fim = {}
for i, ev in tok.items():
    por = defaultdict(list)
    for n, e in ev:
        por[n].append(e)
    ultimo = max(por)
    print(f"  {i:12} " + " | ".join(f"T{n}:{','.join(por[n])}" for n in sorted(por)) + f"   ultima aparicao: T{ultimo}")
print()
print("Criadas por turno:", {n: sum(1 for i, ev in tok.items() for m, e in ev if m == n and e == 'CRIADA') for n in range(1, len(d) + 1)})
# Destino de cada ficha. O log so' gera linha quando o ESTADO muda; ficha que o log nao registra ao sair nao deixa rastro direto:
# - termina o turno TAPPED e nao tem linha de untap no turno seguinte -> SUMIU (sacrificada por mana, morta ou apagada);
# - termina o turno UNTAPPED -> sem linha seguinte nao prova nada (continua em campo, ou foi apagada sem tocar: INDETERMINADO, tratada como viva).
for i, ev in tok.items():
    ns = sorted({n for n, e in ev})
    ult = ns[-1]
    ult_ev = [e for n, e in ev if n == ult][-1]
    if ult == len(d):
        print(f"  {i}: ainda aparece no ultimo turno T{ult} ({ult_ev}); ultimo turno, sem turno seguinte pra decidir")
    elif ult_ev.startswith("tap"):
        print(f"  {i}: terminou T{ult} TAPPED e nao desvirou em T{ult + 1} -> SUMIU (sacrificada, morta ou apagada)")
    else:
        print(f"  {i}: terminou T{ult} destapada ({ult_ev}) e sem linha depois -> INDETERMINADO (tratada como viva)")
