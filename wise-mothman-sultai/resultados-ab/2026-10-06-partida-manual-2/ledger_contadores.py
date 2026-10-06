"""Ledger da partida manual #2 do Mothman: o que o LOG mostra x o que as REGRAS exigem, em 4 frentes. Uso: python3 ledger_contadores.py > resumos/ledger_contadores.md
 (1) contadores +1/+1, evento a evento, com as substituicoes que estavam em campo: Kami of Whispered Hopes (+1 por colocacao, em qualquer permanente seu) e Winding Constrictor (+1 por colocacao
     em artefato/criatura sua); o gatilho de combate do Ouroboroid poe X contadores em CADA criatura (X = poder dele quando resolve, valor fixado), fichas inclusive;
 (2) compras do The Great Henge (nao-ficha entra: +1 contador e compra);
 (3) rad: o Constrictor tambem soma +1 aos rad counters que EU recebo (segunda habilidade dele);
 (4) jogadas de terreno.
Cada evento usa como base o estado que o LOG mostra ANTES dele (assim o erro de um passo nao contamina a conta do seguinte); no fim ha um replay "estrito" so' para mostrar como o erro se compoe.
SUPOSICOES (leitura minha do trace, conferidas por `assert` contra os contadores finais por turno): a ordem dos registros e' a ordem real; o alvo de cada colocacao e' o que o log mostra recebendo o contador;
Gyre Sage evolve so' compara P/T de quem ENTRA (sem os contadores que o Henge poe depois: a condicao 'if' e' checada quando a criatura entra)."""
import json, lzma, os
aqui = os.path.dirname(os.path.abspath(__file__))
T = json.load(lzma.open(os.path.join(aqui, "dados", "partida.json.xz")))
def ctr(e): return sum(v["count"] for k, v in (e.get("counters") or {}).items() if k.startswith("+1"))
est = {}
FIM = {}
for i, t in enumerate(T, 1):
    for e in t:
        est[e["id"]] = e
    FIM[i] = {e["name"]: ctr(e) for e in est.values() if e["zone"] == "battlefield" and not e.get("token")}
# conferencias dos contadores finais usados abaixo
assert FIM[4] == {"Zagoth Triome": 0, "Gyre Sage": 1, "Island": 0, "Swarmyard": 0, "The Wise Mothman": 1, "The Great Henge": 0, "Basking Broodscale": 1}, FIM[4]
assert FIM[5]["Winding Constrictor"] == 1 and FIM[5]["Kami of Whispered Hopes"] == 2 and FIM[5]["The Wise Mothman"] == 4 and FIM[5]["Gyre Sage"] == 3
assert FIM[6]["Ouroboroid"] == 10 and FIM[6]["Basking Broodscale"] == 6 and FIM[6]["Winding Constrictor"] == 7 and FIM[6]["Kami of Whispered Hopes"] == 8 and FIM[6]["Gyre Sage"] == 9 and FIM[6]["The Wise Mothman"] == 10
assert FIM[7]["Ouroboroid"] == 23 and FIM[7]["The Wise Mothman"] == 10
print("# Ledger da partida manual #2 do Mothman (2026-10-06)\n")
print("Leitura minha do trace (`resumos/trace.md`); contadores finais por turno conferidos por `assert`. **Limites:** o log nao registra vida, rad, mana flutuante, nem a ordem da pilha.\n")
print("## 1. Contadores +1/+1, evento a evento (base = o que o log mostrava antes do evento)\n")
print("Colocacao de `n` contadores num permanente seu com Kami e/ou Constrictor em campo = `n + (#Kami) + (#Constrictor)` (todas aditivas, CR 616.1; rulings do Kami e do Hardened Scales/Constrictor).\n")
print("| T | evento | n | Kami/Constr. em campo | esperado | no log | diferenca |")
print("|---|---|---|---|---|---|---|")
EV = [
 (3, "Mothman entra: Gyre Sage evolve (o log so' mostra o contador no T4)", 1, 0, 0, 1),
 (4, "Cankerbloom milado pelo rad (nao-terreno, X=1): gatilho do Mothman, alvo Mothman", 1, 0, 0, 1),
 (4, "Basking Broodscale entra: Henge poe 1 contador (e deveria comprar)", 1, 0, 0, 1),
 (5, "Winding Constrictor entra: Henge poe 1 contador nele (o Constrictor ja' vale para si)", 1, 0, 1, 1),
 (5, "Kami entra: Henge poe 1 contador nele (Kami e Constrictor ja' valem)", 1, 1, 1, 2),
 (5, "Mindcrank milado (X=1): gatilho do Mothman, alvo Mothman", 1, 1, 1, 3),
 (6, "Ouroboroid entra: Henge poe 1 contador nele", 1, 1, 1, 2),
 (6, "Fierce Guardianship milada (X=1): gatilho do Mothman, alvo Ouroboroid", 1, 1, 1, 2),
]
dif_tot = 0
for t, ev, n, k, c, log in EV:
    esp = n + k + c
    dif_tot += log - esp
    print(f"| T{t} | {ev} | {n} | {k}/{c} | {esp} | {log} | {'ok' if log == esp else '**%+d**' % (log - esp)} |")
# combate T6: X do Ouroboroid com o que o log mostrava (4 contadores: 2 + 2)
oc = 4
X = 1 + oc
esp = X + 1 + 1
print(f"| T6 | combate: Ouroboroid (poder {X} = 1 + {oc} contadores) poe X em CADA criatura | {X} | 1/1 | {esp} por criatura | +6 (Ouroboroid, Mothman, Gyre Sage, Constrictor, Kami) e +5 (Broodscale) | **-1** (-2 na Broodscale) |")
print("| T6 | o mesmo gatilho nas fichas Eldrazi Spawn (0/1, criatura): ja' havia 1 em campo | | | " + f"{esp} na ficha | 0 | **-{esp}** |")
X7 = 1 + 10
print(f"| T7 | combate: Ouroboroid (poder {X7}) poe X em cada criatura (so' o Ouroboroid foi registrado) | {X7} | 1/1 | {X7 + 2} | +13 (10 -> 23) | ok |")
assert FIM[7]["Ouroboroid"] - FIM[6]["Ouroboroid"] == X7 + 2
assert (FIM[6]["The Wise Mothman"] - FIM[5]["The Wise Mothman"], FIM[6]["Basking Broodscale"] - FIM[5]["Basking Broodscale"]) == (6, 5)
print(f"\nNo T7 o log mostra **as duas substituicoes** (11 + 1 + 1 = 13); no T6 mostra so' **uma** (5 + 1 = 6) e nenhuma ficha recebeu contador. Colocacoes com a conta errada (so' as que o log permite provar): "
      f"T5 Constrictor (-1), T5 Kami (-1), T6 Ouroboroid entrando (-1), T6 gatilho do Mothman (-1) e T6 combate (-1 em 5 criaturas, -2 na Broodscale, -{esp} na ficha). "
      "O gatilho do Mothman do T5 (+3 no Mothman) esta CERTO.")
print("**Sem fonte pelas regras:** Gyre Sage ganhou +2 no T5 (1 -> 3): a evolve nao dispara com o Constrictor (2/3) nem com o Kami (1/1) entrando (a condicao 'if' e' checada na entrada, antes dos contadores do Henge), e so' houve 1 gatilho do Mothman, no Mothman.")
# replay estrito (a partir do inicio de T5 do log, com as ESCOLHAS de alvo do usuario)
print("\n### Como o erro se compoe (replay estrito, mesmas escolhas de alvo do usuario, base = fim do T4 do log)\n")
M, G, B, C, K, O = 1, 1, 1, 0, 0, 0
R = 0
C = 1 + 1; R = 1                       # T5 Constrictor
K = 1 + 2; R = 2                       # T5 Kami
M += 1 + R                             # T5 Mindcrank -> Mothman
O = 1 + R                              # T6 Ouroboroid entra
O += 1 + R                             # T6 Fierce Guardianship -> Ouroboroid
x6 = 1 + O
M += x6 + R; G += x6 + R; B += x6 + R; C += x6 + R; K += x6 + R; O += x6 + R; ficha6 = x6 + R
x7 = 1 + O
print(f"- fim do T6 pelas regras: Mothman {M}, Gyre Sage {G} (sem o +2 sem fonte), Broodscale {B}, Constrictor {C}, Kami {K}, Ouroboroid {O}, ficha Spawn {ficha6}; no log: Mothman 10, Gyre Sage 9, Broodscale 6, Constrictor 7, Kami 8, Ouroboroid 10, ficha 0.")
print(f"- gatilho do T7 pelas regras: X = poder do Ouroboroid = 1 + {O} = {x7}, cada criatura +{x7 + R} (o log: X = 11, +13).")
assert O > 10 and x7 > 11
# ---------- 2. compras do Henge ----------
print("\n## 2. Compras do The Great Henge (\"whenever a nontoken creature you control enters, put a +1/+1 counter on it and draw a card\")\n")
print("| T | criaturas nao-ficha que entraram com o Henge em campo | compras esperadas (alem da compra do turno) | compras no log (library -> mao fora do passo de compra) |")
print("|---|---|---|---|")
HENGE = {4: (["Basking Broodscale"], 0), 5: (["Winding Constrictor", "Kami of Whispered Hopes"], 2), 6: (["Ouroboroid"], 1)}
for t, (cs, log) in HENGE.items():
    desse = [e["name"] for e in T[t - 1] if e.get("fromZone") == "library" and e.get("toZone") == "hand"]
    extra = len(desse) - 1
    assert extra == log, (t, desse)
    print(f"| T{t} | {', '.join(cs)} | {len(cs)} | {extra} | {'ok' if extra == len(cs) else '**faltou %d**' % (len(cs) - extra)} |")
print("\nO T5 (2 compras) e o T6 (1) batem; **no T4 a Broodscale entrou com o Henge em campo e nao ha compra no log** (1 compra a menos).")
# ---------- 3. rad ----------
print("\n## 3. Rad (CR 728.1) e o Winding Constrictor (\"if you would get one or more counters, you get that many plus one\")\n")
print("| T | mills meus no log | rad esperado no inicio da fase principal 1 (minimo) | cartas milladas no log | diferenca |")
print("|---|---|---|---|---|")
MILL = {i: [e["name"] for e in t if e.get("fromZone") == "library" and e.get("toZone") == "graveyard"] for i, t in enumerate(T, 1)}
ROWS = [(4, "1 (ETB do Mothman no T3)", 1), (5, "1 (ataque do T4: +1; o rad do T4 foi consumido por um nao-terreno)", 1),
        (6, "2 ou mais (ataque do T5 com o Constrictor em campo: +1 +1 extra = +2)", 2), (7, "2 ou mais (ataque do T6 com o Constrictor: +2)", 2)]
for t, expl, esp in ROWS:
    n = len(MILL[t])
    print(f"| T{t} | {', '.join(MILL[t]) or '-'} | {expl} | {n} | {'ok' if n >= esp else '**faltam >= %d**' % (esp - n)}{' (sobra %d sem fonte)' % (n - esp) if n > esp else ''} |")
assert len(MILL[6]) == 1 and len(MILL[7]) == 1 and len(MILL[5]) == 2
print("\nO Constrictor so' entrou no T5, mas o Mothman atacou depois dele no T5 e no T6: cada ataque deu **2** rad counters a voce, nao 1. Os mills do T6 e do T7 ficam **pelo menos 1 abaixo** do exigido (limite inferior firme); "
      "o T5 tem 1 mill a mais do que a fonte conhecida (Overgrown Tomb e Mindcrank; so' havia 1 rad).")
# ---------- 4. terrenos ----------
print("\n## 4. Jogadas de terreno (1 por turno; a Takenuma estava na mao desde a abertura)\n")
print("| T | terreno jogado | outros terrenos na mao na hora |")
print("|---|---|---|")
TERR = [(1, "Zagoth Triome (virada)", "Island, Takenuma"), (2, "Island", "Takenuma"), (3, "Swarmyard", "Takenuma"), (4, "**nenhum**", "Takenuma"), (5, "Strip Mine", "Takenuma"),
        (6, "Undergrowth Stadium", "Takenuma, Overgrown Tomb, Watery Grave"), (7, "Forest", "Takenuma, Overgrown Tomb, Watery Grave")]
for t, a, b in TERR:
    print(f"| T{t} | {a} | {b} |")
print("\nO T4 e' a unica rodada sem jogada de terreno, com a Takenuma na mao: era o que faltava para o Henge (T4) caber no mana (5 = 4 fontes + 1 terreno).")
