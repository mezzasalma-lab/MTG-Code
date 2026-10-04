"""Testes dirigidos da 10a rodada (wipes proprios segurados), depois do principio do usuario: "Todo boardwipe deve ser segurado para causar mais perdas aos
oponentes do que a mim. Claro que quando utilizados, eu perco tudo que for criatura em campo, mas dependendo das circunstancias isso pode ser mitigado:
por exemplo: com Mayhem Devil em campo, sacrificar tesouros animados para pagar o custo do wipe ainda causa dano nos oponentes alem do efeito do wipe em si".
Oraculo e rulings (lidos ao vivo em 2026-10-04, `dados/oraculo_rulings_ao_vivo.json`): Blood Money = {5}{B}{B}, destroy all creatures; Blasphemous Act = {8}{R},
{1} a menos por criatura; Mayhem Devil = "whenever a player sacrifices a permanent, deals 1 damage to any target" (ruling 2019-05-03: se o sacrificio paga um
custo, o gatilho resolve ANTES da magia); Treasure = "{T}, Sacrifice this token: add one mana of any color". Cada teste monta um GameState a mao e chama a
funcao real. Uso: python3 testes_dirigidos.py"""
import collections, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

V = F.flags(F.carrega(F.DEPOIS, "vih_10a_testes"))
res = []
BM, ACT = "Blood Money", "Blasphemous Act"
ZUL, LOTHO, PLUND, MAHADI, MAYHEM = "Zulaport Cutthroat", "Lotho, Corrupt Shirriff", "Pitiless Plunderer", "Mahadi, Emporium Master", "Mayhem Devil"
OUTRO = "Olivia, Opulent Outlaw"


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def modo(hold_always=True, pay=True, release=True, engine=True):
    F.flags(V, hold_always=hold_always, pay=pay, release=release, engine=engine)


def novo(bf=(), hand=(), lands=0, turn=8, commander=True, animados=0, treasures=0):
    bf = [n for n in bf if n != V.COMMANDER]
    s = V.GameState(hand=list(hand), battlefield=list(bf) + ["Mountain"] * lands, library=["Swamp"] * 30)
    s.turn = turn
    s.commander_cast_count = 10  # imposto enorme: o comandante nunca e' recastado nestas cenas (so' quando commander=True ele ja' esta em campo)
    if commander:
        s.commander_in_play = True
        s.battlefield.append(V.COMMANDER)
    s.treasures = treasures if treasures else animados
    s.treasures_animated_alive = animados
    return s


# ---------------------------------------------------------------- pagar o wipe com os Treasures animados (OWN_WIPE_PAY_WITH_ANIMATED_ENABLED)
modo()
s = novo([MAYHEM, LOTHO], hand=[BM], lands=7, animados=7)
V.cast_card(s, BM)
teste("P1 Blood Money paga com 7 animados (custo 7): mana dos terrenos intacta, 7 sacrificados, 7 de dano do Mayhem Devil ANTES do wipe",
      s.mana_spent_this_turn == 0 and s.own_wipe_animated_paid_total == 7 and s.own_wipe_pay_drain_total == 7 and s.treasures_sacrificed_total == 7,
      str((s.mana_spent_this_turn, s.own_wipe_animated_paid_total, s.own_wipe_pay_drain_total, s.treasures_sacrificed_total)))
teste("P1b e o wipe segue valendo: o Vihaan, o Mahadi/Lotho e o proprio Mayhem Devil morrem (destruicao, sem dano extra do Mayhem), e os 7 animados ja' tinham morrido como custo (mortes = 7 + 3)",
      not s.commander_in_play and MAYHEM in s.graveyard and LOTHO in s.graveyard and s.creature_deaths_total == 10 and s.drain_damage_total == 7,
      str((s.commander_in_play, s.creature_deaths_total, s.drain_damage_total)))
modo(pay=False)
s = novo([MAYHEM, LOTHO], hand=[BM], lands=7, animados=7)
V.cast_card(s, BM)
teste("P1c chave desligada = codigo anterior: paga com os 7 terrenos (mana gasta 7), os 7 animados morrem no wipe como fichas e o Mayhem Devil NAO causa dano (destruicao)",
      s.mana_spent_this_turn == 7 and s.own_wipe_animated_paid_total == 0 and s.drain_damage_total == 0, str((s.mana_spent_this_turn, s.drain_damage_total)))
modo()
s = novo([LOTHO], hand=[BM], lands=7, animados=7)
V.cast_card(s, BM)
teste("P2 sem Mayhem Devil o pagamento com animados e' o mesmo (os animados morreriam no wipe de qualquer jeito), mas sem dano: 0 de dreno", s.mana_spent_this_turn == 0 and s.own_wipe_animated_paid_total == 7 and s.own_wipe_pay_drain_total == 0)
s = novo([MAYHEM], hand=[BM], lands=7, animados=3, treasures=3)
V.cast_card(s, BM)
teste("P3 cobertura parcial: 3 animados pagam 3 e os terrenos pagam os 4 restantes (mana gasta 4), 3 de dano", s.own_wipe_animated_paid_total == 3 and s.mana_spent_this_turn == 4 and s.own_wipe_pay_drain_total == 3, str((s.own_wipe_animated_paid_total, s.mana_spent_this_turn)))
s = novo([MAYHEM], hand=[BM], lands=7, animados=7, treasures=9)
s.treasures_tapped = 5
V.cast_card(s, BM)
teste("P4 Treasure virado nao paga (so' o desvirado entra no custo): 9 Treasures, 7 animados, 5 virados -> so' 4 desvirados; 4 pagam, terrenos pagam 3", s.own_wipe_animated_paid_total == 4 and s.mana_spent_this_turn == 3, str((s.own_wipe_animated_paid_total, s.mana_spent_this_turn)))
s = novo([MAYHEM], hand=[BM], lands=7, animados=7)
s.battlefield.append("Goldspan Dragon")
V.cast_card(s, BM)
teste("P5 com Goldspan Dragon (Treasure vale 2) 4 animados pagam os 7 (8 de mana; o excesso de 1 se perde) e nada sai dos terrenos", s.own_wipe_animated_paid_total == 4 and s.mana_spent_this_turn == 0, str((s.own_wipe_animated_paid_total, s.mana_spent_this_turn)))
s = novo([MAYHEM, ZUL], hand=[ACT], lands=3, animados=6)
V.cast_card(s, ACT)
teste("P6 Blasphemous Act: o custo ja' cai pelas criaturas (Vihaan, Mayhem, Zulaport + 6 animados = 9 -> piso 1) e 1 animado paga; Zulaport drena pelo pagamento",
      s.own_wipe_animated_paid_total == 1 and s.mana_spent_this_turn == 0 and s.own_wipe_pay_drain_total >= 2, str((s.own_wipe_animated_paid_total, s.mana_spent_this_turn, s.own_wipe_pay_drain_total)))
modo()
s = novo([MAYHEM], hand=["Sol Ring"], lands=7, animados=7)
V.cast_card(s, "Sol Ring")
teste("P7 so' o wipe paga com animados: uma magia comum continua pagando com terrenos primeiro (Sol Ring custa 1: 0 animados sacrificados)", s.own_wipe_animated_paid_total == 0 and s.treasures == 7)

# ---------------------------------------------------------------- retencao universal e a excecao mitigada
modo()
def cena_sem_motores(cartas=(BM,), lands=8, extra=()):
    s = novo(list(extra) + [LOTHO], hand=list(cartas), lands=lands, commander=False)
    return s
s = cena_sem_motores()
V.main_phase(s)
teste("R1 todo wipe e' segurado: sem Vihaan nem Mahadi em campo, com 8 de mana, a Blood Money continua na mao (a regra da 9a rodada a conjuraria)", BM in s.hand and s.blood_money_cast_total == 0 and s.own_wipe_held_total == 1, str((s.hand, s.own_wipe_held_total)))
s = cena_sem_motores(cartas=(ACT,))
V.main_phase(s)
teste("R1b idem a Blasphemous Act", ACT in s.hand and s.own_wipes_cast_total == 0)
modo(hold_always=False)
s = cena_sem_motores()
V.main_phase(s)
teste("R1c chave desligada = retencao da 9a rodada: sem Vihaan/Mahadi conjura", BM in s.graveyard and s.blood_money_cast_total == 1)
modo()
s = novo([MAYHEM, LOTHO], hand=[BM], lands=0, animados=7)
V.main_phase(s)
teste("R2 excecao mitigada: Mayhem Devil em campo e 7 animados pagam os 7 do custo -> a Blood Money e' conjurada, paga so' com animados, e o Vihaan morre no wipe (a perda e' aceita)",
      s.blood_money_cast_total == 1 and s.own_wipe_mitigated_casts_total == 1 and s.own_wipe_animated_paid_total == 7 and s.own_wipe_pay_drain_total == 7 and not s.commander_in_play,
      str((s.blood_money_cast_total, s.own_wipe_mitigated_casts_total, s.own_wipe_animated_paid_total, s.own_wipe_pay_drain_total)))
s = novo([LOTHO], hand=[BM], lands=0, animados=7)
V.main_phase(s)
teste("R2b sem Mayhem Devil: a mesma cena NAO libera (fica na mao)", BM in s.hand and s.blood_money_cast_total == 0)
s = novo([MAYHEM, LOTHO], hand=[BM], lands=4, animados=3, treasures=3)
V.main_phase(s)
teste("R2c com Mayhem Devil mas animados que NAO pagam o custo inteiro (3 de 7): segura (a excecao exige o custo inteiro nos doomed)", BM in s.hand and s.blood_money_cast_total == 0, str((s.hand,)))
s = novo([MAYHEM, LOTHO], hand=[BM], lands=0, animados=7, treasures=7)
s.treasures_tapped = 4
V.main_phase(s)
teste("R2d animados virados nao contam pra liberar (7 animados, 4 virados): segura", BM in s.hand and s.blood_money_cast_total == 0)
modo(release=False)
s = novo([MAYHEM, LOTHO], hand=[BM], lands=0, animados=7)
V.main_phase(s)
teste("R2e chave da excecao desligada: nem a circunstancia mitigada libera (segura sempre)", BM in s.hand and s.blood_money_cast_total == 0)
modo()
s = novo([MAYHEM, LOTHO], hand=[ACT], lands=0, animados=7)
V.main_phase(s)
teste("R2f a Blasphemous Act com tabuleiro cheio NAO libera: o custo cai pelo piso (1), o pagamento causa 1 de dano contra 3 criaturas minhas perdidas (dano 1 <= 3)", ACT in s.hand and s.own_wipes_cast_total == 0, str((s.hand,)))
s = novo([MAYHEM], hand=[ACT], lands=0, commander=False, animados=5)
V.main_phase(s)
teste("R2g mas libera num tabuleiro magro: so' o Mayhem Devil + 5 animados (custo 9 - 6 = 3): 3 de dano > 1 criatura minha perdida -> conjura", s.own_wipes_cast_total == 1 and s.own_wipe_animated_paid_total == 3 and s.own_wipe_pay_drain_total == 3, str((s.own_wipes_cast_total, s.own_wipe_animated_paid_total, s.own_wipe_pay_drain_total)))
s = novo([MAYHEM, LOTHO, ZUL, PLUND, OUTRO, "Prosper, Tome-Bound", "Magda, the Hoardmaster", "Kambal, Profiteering Mayor"], hand=[BM], lands=0, animados=7)
V.main_phase(s)
teste("R2h Blood Money com 7 animados pagando (7 de dano) mas 9 criaturas minhas perdidas (Vihaan + 8): 7 <= 9 -> segura (o principio: mais perdas pro oponente do que pra mim)", BM in s.hand and s.blood_money_cast_total == 0, str((s.hand,)))
s = novo([MAYHEM, LOTHO, ZUL, PLUND, OUTRO], hand=[BM], lands=0, animados=7)
V.main_phase(s)
teste("R2i e com 6 criaturas minhas (Vihaan + 5): 7 de dano > 6 -> conjura", s.blood_money_cast_total == 1 and s.own_wipe_mitigated_casts_total == 1, str((s.blood_money_cast_total,)))
s = novo([MAYHEM, LOTHO], lands=0, animados=7)
s.impulse_pool.append((BM, s.turn))
ok1 = V.play_from_impulse(s)
s2 = novo([LOTHO], lands=8, commander=False)
s2.impulse_pool.append((BM, s2.turn))
ok2 = V.play_from_impulse(s2)
teste("R3 carta exilada pelo Prosper: com Mayhem + animados pagando, e' conjurada; sem a circunstancia fica no pool ate' expirar (o T8 do usuario)", ok1 and s.blood_money_cast_total == 1 and (not ok2) and (BM, s2.turn) in s2.impulse_pool, str((ok1, ok2)))

# ---------------------------------------------------------------- invariantes em partidas reais
def jogos(n, seed0, modo_jogo):
    F.flags(V)
    fn = V.simulate_one if modo_jogo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    dup = viol_hold = viol_tap = viol_pay = casts = mitig = 0
    orig_res, orig_et = V.resolve_instant_sorcery, V.end_step
    orig_cast = V.cast_card
    def cast_espia(state, name, from_zone="hand"):
        nonlocal viol_hold, casts, mitig, viol_pay
        if name in V.OWN_WIPES:
            casts += 1
            m = V.wipe_mitigated(state, name)
            if m:
                mitig += 1
            else:
                viol_hold += 1  # wipe proprio conjurado fora da circunstancia mitigada (a retencao universal nao deixa)
            antes_pag, antes_ani = state.own_wipe_animated_paid_total, state.treasures_animated_alive
            r = orig_cast(state, name, from_zone)
            pagos = state.own_wipe_animated_paid_total - antes_pag
            if pagos > antes_ani or (m and pagos == 0):
                viol_pay += 1
            return r
        return orig_cast(state, name, from_zone)
    def et(state):
        nonlocal viol_tap
        if not (0 <= state.treasures_tapped <= state.treasures):
            viol_tap += 1
        orig_et(state)
    V.cast_card, V.end_step = cast_espia, et
    try:
        for i in range(n):
            s = fn(seed0 + i)
            zonas = collections.Counter(s.hand + s.battlefield + s.graveyard + s.library + [c for c, _ in s.impulse_pool] + [c for c, _ in s.impulse_lands])
            if any(zonas[k] > v for k, v in base.items()):
                dup += 1
            if not (0 <= s.treasures_tapped <= s.treasures) or s.treasures < 0:
                viol_tap += 1
    finally:
        V.cast_card, V.end_step = orig_cast, orig_et
    return dup, viol_hold, viol_tap, viol_pay, casts, mitig
for modo_jogo in ("padrao", "resiliencia"):
    dup, vh, vt, vp, casts, mit = jogos(3000, 1_000_000, modo_jogo)
    teste(f"I1 ({modo_jogo}, 3.000 jogos) nenhuma carta duplicada, tapped valido, todo wipe proprio conjurado esta na circunstancia mitigada, e o pagamento com animados nunca passa dos animados vivos (e e' > 0 quando mitigado)", dup == 0 and vt == 0 and vh == 0 and vp == 0, str((dup, vh, vt, vp)))
    print(f"   info I1 {modo_jogo}: wipes proprios conjurados em 3.000 jogos: {casts} (na circunstancia mitigada: {mit})")
F.flags(V)

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)
