"""Ensaio a seco (dry-run) Blasphemous Act x Blasphemous Edict sobre estados NATURAIS do goldfish. A cada fase principal (turno >= 3) de partidas do modo padrao, copia o estado
(deepcopy) e, em copias separadas, conjura cada wipe (sem a retencao, so' pra medir) pelo caminho real do simulador (`cast_card`: custo reduzido da Act, custo 5 da Edict, pagamento
primeiro com os Treasures animados, gatilhos), registrando o que cada um causa so' no MEU lado. Estratos: com/sem Mayhem Devil em campo; 1a main (sem animados) x 2a main (apos o
combate). NAO mede o efeito nas criaturas do oponente (📊: o simulador nao modela campo de oponente): e' o piso da Edict, nao o valor dela.
Uso: python3 edict_dry_run.py [N] [semente0]"""
import copy, math, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
import edict_harness as H

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 3_000_000
V = F.flags(F.carrega(F.DEPOIS, "vih_dryrun"))
H.instala(V)
V.OWN_WIPE_HOLD_ALWAYS_ENABLED = False   # so' pra medir: a retencao da 10a rodada impediria o cast
V.OWN_WIPE_HOLD_ENGINE_ENABLED = False
ACT, EDICT = "Blasphemous Act", H.EDICT
amostras = []
contador = {}


def metricas(s):
    named = [n for n in s.battlefield if V.is_creature_card(n)]
    return {"dreno": s.drain_damage_total, "mesa": s.table_damage_total, "vida": s.life_gained_total, "mortes": s.creature_deaths_total,
            "nomeadas": len(named), "fichas": s.constructs + s.other_tokens + s.dragons + s.treasures_animated_alive,
            "vihaan": 1 if s.commander_in_play else 0, "mahadi": 1 if "Mahadi, Emporium Master" in s.battlefield else 0,
            "estoque": s.treasures, "pagos": s.own_wipe_animated_paid_total, "dreno_pag": s.own_wipe_pay_drain_total,
            "mana_resta": V.remaining_mana(s), "treasures_criados": s.treasures_created_total}


def ensaio(state, carta):
    c = copy.deepcopy(state)
    c.hand.append(carta)
    if not V.can_cast(c, carta):
        return None
    antes = metricas(c)
    V.cast_card(c, carta)
    depois = metricas(c)
    d = {k: depois[k] - antes[k] for k in antes}
    d["custo"] = V.spell_cost(state, carta)
    return d


orig_main = V.main_phase


def main_espia(state):
    if state.turn >= 3:
        k = contador.get(id(state), (None, 0))
        n = k[1] + 1 if k[0] == state.turn else 1
        contador[id(state)] = (state.turn, n)
        a, e = ensaio(state, ACT), ensaio(state, EDICT)
        amostras.append({"fase": "2a main (pos-combate)" if n >= 2 else "1a main", "mayhem": "Mayhem Devil" in state.battlefield, "bats": "Mirkwood Bats" in state.battlefield, "vihaan": state.commander_in_play,
                         "criaturas": len([x for x in state.battlefield if V.is_creature_card(x)]) + state.constructs + state.other_tokens + state.dragons + state.treasures_animated_alive,
                         "animados": state.treasures_animated_alive, "act": a, "edict": e})
    return orig_main(state)


V.main_phase = main_espia
for i in range(N):
    contador.clear()
    V.simulate_one(S0 + i)


def media(xs):
    return (st.mean(xs), 1.96 * st.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 and len(set(xs)) > 1 else 0.0)


def tabela(rotulo, sel):
    ambos = [a for a in amostras if sel(a) and a["act"] and a["edict"]]
    so_edict = [a for a in amostras if sel(a) and a["edict"] and not a["act"]]
    so_act = [a for a in amostras if sel(a) and a["act"] and not a["edict"]]
    print(f"\n### {rotulo}: {len([a for a in amostras if sel(a)])} estados | conjuraveis os DOIS: {len(ambos)} | so' a Edict: {len(so_edict)} | so' a Act: {len(so_act)}")
    if not ambos:
        return
    print("%-44s %-22s %-22s %-24s" % ("(media por estado, so' meu lado; ±IC95%)", "Blasphemous Act", "Blasphemous Edict", "Edict - Act (pareado)"))
    for k, nome in (("custo", "custo pago (mana)"), ("dreno", "dano/dreno causado (proxy)"), ("mesa", "dano de mesa (proxy, x3 oponentes onde 'each opp')"), ("vida", "vida ganha"),
                    ("mortes", "mortes de criatura"), ("nomeadas", "criaturas nomeadas PERDIDAS (delta no campo)"), ("fichas", "fichas/animados perdidos"),
                    ("vihaan", "Vihaan em campo (delta; -1 = morreu)"), ("mahadi", "Mahadi em campo (delta; -1 = morreu)"), ("pagos", "animados que pagaram o custo")):
        va, ve = [a["act"][k] for a in ambos], [a["edict"][k] for a in ambos]
        dif = [y - x for x, y in zip(va, ve)]
        ma, mb, md = media(va), media(ve), media(dif)
        print("%-44s %+8.3f ±%-8.3f   %+8.3f ±%-8.3f   %+8.3f ±%-8.3f" % (nome, ma[0], ma[1], mb[0], mb[1], md[0], md[1]))


print(f"N={N} partidas (modo padrao, sementes {S0}..{S0 + N - 1}); {len(amostras)} estados amostrados (turno >= 3, 1a e 2a main).")
tabela("TODOS os estados", lambda a: True)
tabela("com Mayhem Devil em campo", lambda a: a["mayhem"])
tabela("sem Mayhem Devil em campo", lambda a: not a["mayhem"])
tabela("com Mayhem Devil, 2a main (apos o combate, com animados)", lambda a: a["mayhem"] and a["fase"].startswith("2a"))
tabela("com Mayhem Devil, 2a main, 4 ou mais animados", lambda a: a["mayhem"] and a["fase"].startswith("2a") and a["animados"] >= 4)

print("\n### Distribuicao dos estados amostrados (turno >= 3, 1a e 2a main): o quanto as condicoes que fazem a Edict valer mais aparecem no goldfish")
tot = len(amostras)
def pct(x):
    return "%.1f%% (%d de %d)" % (100.0 * x / tot, x, tot)
print("  Mayhem Devil em campo:", pct(sum(1 for a in amostras if a["mayhem"])))
print("  Mirkwood Bats em campo:", pct(sum(1 for a in amostras if a["bats"])))
print("  Mayhem Devil OU Mirkwood Bats em campo:", pct(sum(1 for a in amostras if a["mayhem"] or a["bats"])))
for lim in (4, 8, 13, 14):
    print(f"  minhas criaturas (nomeadas + fichas + animados) >= {lim}:", pct(sum(1 for a in amostras if a["criaturas"] >= lim)))
print("  Edict conjuravel (mana >= custo):", pct(sum(1 for a in amostras if a["edict"])), "| Act conjuravel:", pct(sum(1 for a in amostras if a["act"])))
print("  Edict conjuravel E Mayhem Devil em campo:", pct(sum(1 for a in amostras if a["edict"] and a["mayhem"])))
