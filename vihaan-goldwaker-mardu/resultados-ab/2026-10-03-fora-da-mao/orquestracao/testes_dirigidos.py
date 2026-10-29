"""Testes dirigidos das 4 correcoes de 'fora da mao' (terreno do exilio, magia do exilio, contagem de spell cast/Lotho, +1/+0 da Storm). Cada
teste monta um GameState a mao e chama a funcao real; os cenarios T5..T8 reproduzem a partida manual #1. Uso: python3 testes_dirigidos.py"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

V = F.flags(F.carrega(F.DEPOIS, "vih_fm_testes"))
res = []


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def novo(bf=(), hand=(), lands=12, library=None, turn=7):
    s = V.GameState(hand=list(hand), battlefield=list(bf) + ["Mountain"] * lands, library=list(library) if library is not None else ["Swamp"] * 30)
    s.turn = turn
    return s


def modo(land=True, cast=True, count=True, storm=True, sevinne=True):
    F.flags(V, land=land, cast=cast, count=count, storm=storm, sevinne=sevinne)


PROSPER = "Prosper, Tome-Bound"
# ------------------------------------------------------------------ item 1: terreno do exilio
s = novo([PROSPER], library=["Desolate Mire", "Swamp"], turn=4)
V.end_step(s)
teste("L1 Prosper no end step exila um TERRENO: vai pra impulse_lands (fonte 'play'), nao pro pool de cast",
      s.impulse_lands == [("Desolate Mire", 5)] and not s.impulse_pool, str((s.impulse_lands, s.impulse_pool)))
s = novo([PROSPER], hand=["Mountain"], turn=5); s.impulse_lands = [("Desolate Mire", 5)]
n0 = len(s.hand)
V.play_land(s)
teste("L2 proximo turno: joga o terreno do EXILIO como a jogada de terreno (a da mao fica), Pact Boon cria 1 Treasure (T5 da partida)",
      "Desolate Mire" in s.battlefield and s.hand == ["Mountain"] and s.lands_played_this_turn == 1 and s.treasures_created_total == 1 and s.impulse_lands_played_total == 1,
      str((s.battlefield[-1], s.hand, s.treasures_created_total)))
s = novo([], hand=[], turn=5); s.impulse_lands = [("Desolate Mire", 5)]
V.play_land(s)
teste("L3 sem Prosper em campo: joga o terreno (ainda dentro do prazo) mas SEM Treasure", "Desolate Mire" in s.battlefield and s.treasures_created_total == 0)
s = novo([PROSPER], turn=5); s.lands_played_this_turn = 1; s.impulse_lands = [("Desolate Mire", 5)]
V.play_land(s); V.play_from_impulse(s)
teste("L4 jogada de terreno ja' usada: o terreno do exilio NAO e' jogado", "Desolate Mire" not in s.battlefield and s.impulse_lands == [("Desolate Mire", 5)])
s = novo([PROSPER], turn=7); s.impulse_lands = [("Desolate Mire", 5)]
V.play_land(s)
teste("L4b prazo vencido (deadline 5 < turno 7): nao joga", "Desolate Mire" not in s.battlefield)
s = novo([PROSPER], turn=5); s.impulse_lands = [("Path of Ancestry", 5), ("Mountain", 5)]
V.play_land(s)
teste("L5 entre dois terrenos do exilio joga o que entra UNTAPPED primeiro (Path of Ancestry entra tapped)", "Mountain" in s.battlefield and "Path of Ancestry" not in s.battlefield and "Mountain" not in s.tapped_lands_this_turn)
s = novo([PROSPER], turn=5); s.impulse_lands = [("Path of Ancestry", 5)]
V.play_land(s)
teste("L5b terreno que entra tapped e' registrado como tapped no turno", "Path of Ancestry" in s.tapped_lands_this_turn)
s = novo([PROSPER], library=["Mountain"] * 5, turn=5)
V.pull_impulse(s, 1, deadline_turns=0)  # fonte "cast" (Grenzo / Laughing Jasper Flint): lands_ok=False
V.play_land(s); V.play_from_impulse(s)
teste("L6 fonte de 'cast' (Grenzo, Laughing Jasper Flint, sem lands_ok): terreno exilado NAO e' jogavel", s.impulse_lands == [] and len(s.impulse_pool) == 1 and s.lands_played_this_turn == 0 and s.treasures_created_total == 0)
s = novo(["Professional Face-Breaker", PROSPER], library=["Swamp"] * 5, turn=6); s.treasures = 1
V.try_face_breaker_impulse(s)
V.play_from_impulse(s)
teste("L7 Face-Breaker ('you may play that card this turn') exila um terreno com a jogada livre: joga na mesma fase + Pact Boon", s.lands_played_this_turn == 1 and s.treasures_created_total == 1 and s.impulse_lands_played_total == 1,
      str((s.lands_played_this_turn, s.treasures_created_total)))
modo(land=False)
s = novo([PROSPER], library=["Desolate Mire", "Swamp"], turn=4)
V.end_step(s)
teste("L8 chave desligada = comportamento antigo: o terreno vai pro pool e nunca e' jogado", s.impulse_lands == [] and s.impulse_pool == [("Desolate Mire", 5)] and not V.play_from_impulse(s))
modo()

# ------------------------------------------------------------------ item 2: magia do exilio
s = novo([PROSPER, "Zulaport Cutthroat"]); s.impulse_pool = [("Blood Money", 8)]
V.play_from_impulse(s)
teste("C1 Blood Money do exilio RESOLVE: vai pro cemiterio (nao pro campo), destroi as criaturas, conta como 1 magia; Pact Boon (1) + 'nontoken destroyed' (Prosper e Zulaport = 2)",
      "Blood Money" in s.graveyard and "Blood Money" not in s.battlefield and "Zulaport Cutthroat" not in s.battlefield and s.spells_cast_this_turn == 1 and s.treasures_created_total == 3 and s.impulse_spells_cast_total == 1,
      str(("Blood Money" in s.graveyard, s.spells_cast_this_turn, s.treasures_created_total)))
s = novo([PROSPER]); s.impulse_pool = [("Sevinne's Reclamation", 8)]; s.graveyard = ["Mahadi, Emporium Master"]
V.play_from_impulse(s)
teste("C2 Sevinne's do exilio devolve o Mahadi do cemiterio (T6 da partida), vai pro cemiterio, Pact Boon cria 1 Treasure",
      "Mahadi, Emporium Master" in s.battlefield and "Sevinne's Reclamation" in s.graveyard and "Sevinne's Reclamation" not in s.battlefield and s.treasures_created_total == 1)
s = novo([PROSPER]); s.impulse_pool = [("Lotho, Corrupt Shirriff", 8)]
V.play_from_impulse(s)
teste("C3 criatura do exilio (Lotho): entra em campo, conta como magia, Pact Boon cria 1 Treasure", "Lotho, Corrupt Shirriff" in s.battlefield and s.spells_cast_this_turn == 1 and s.treasures_created_total == 1)
modo(cast=False)
s = novo([PROSPER, "Zulaport Cutthroat"]); s.impulse_pool = [("Blood Money", 8)]
V.play_from_impulse(s)
teste("C4 chave desligada = comportamento antigo: Blood Money vira permanente e nada resolve", "Blood Money" in s.battlefield and "Zulaport Cutthroat" in s.battlefield and s.spells_cast_this_turn == 0)
modo()

# ------------------------------------------------------------------ item 3: contagem de spell cast / Lotho
s = novo([PROSPER], hand=["Monologue Tax"]); s.impulse_pool = [("Lotho, Corrupt Shirriff", 8)]
V.play_from_impulse(s)
n_pact = s.treasures_created_total
V.cast_card(s, "Monologue Tax")
teste("S1 T7 da partida: Lotho do exilio (1a magica, Pact Boon +1) e Tax da mao (2a): o Lotho dispara na Tax: +1 Treasure e -1 de vida",
      s.spells_cast_this_turn == 2 and n_pact == 1 and s.treasures_created_total == 2 and s.life == 39 and s.lotho_triggers_total == 1,
      str((s.spells_cast_this_turn, n_pact, s.treasures_created_total, s.life)))
s = novo(["Lotho, Corrupt Shirriff"], hand=["Dictate of Erebos"]); s.graveyard = ["Sevinne's Reclamation", "Zulaport Cutthroat"]
V.try_sevinne_flashback(s); n1 = s.spells_cast_this_turn; t1 = s.treasures_created_total
V.cast_card(s, "Dictate of Erebos")
teste("S2 T8 da partida: flashback da Sevinne's conta como 1a magia (sem Pact Boon: veio do cemiterio); o Dictate (2a) dispara o Lotho: +1 Treasure e -1 de vida",
      n1 == 1 and t1 == 0 and s.spells_cast_this_turn == 2 and s.treasures_created_total == 1 and s.life == 39 and "Zulaport Cutthroat" in s.battlefield,
      str((n1, t1, s.spells_cast_this_turn, s.treasures_created_total, s.life)))
s = novo([], hand=["Sol Ring", "Lotho, Corrupt Shirriff"])
V.cast_card(s, "Sol Ring"); V.cast_card(s, "Lotho, Corrupt Shirriff")
teste("S3 Lotho conjurado como 2a magica NAO dispara contra si mesmo (estava na pilha)", s.treasures_created_total == 0 and s.life == 40)
s = novo(["Lotho, Corrupt Shirriff"], hand=["Sol Ring", "Arcane Signet", "Monologue Tax"])
V.cast_card(s, "Sol Ring"); V.cast_card(s, "Arcane Signet"); V.cast_card(s, "Monologue Tax")
teste("S4 Lotho em campo: dispara na 2a magica e so' nela (a 3a nao)", s.treasures_created_total == 1 and s.life == 39)
s = novo(["Lotho, Corrupt Shirriff"]); s.spells_cast_this_turn = 1
s.library = ["Sol Ring"] + ["Swamp"] * 10
V.do_cascade(s, 5)
teste("S5 a magia do Cascade e' conjurada: conta, e com Lotho em campo e 1 magia antes ela e' a 2a (+1 Treasure)", s.spells_cast_this_turn == 2 and s.treasures_created_total == 1 and "Sol Ring" in s.battlefield, str((s.spells_cast_this_turn, s.treasures_created_total)))
s = novo(["Life Insurance"]); s.graveyard = ["Sevinne's Reclamation", "Zulaport Cutthroat"]
V.try_sevinne_flashback(s)
teste("S6 extort da Life Insurance dispara no flashback ('whenever you cast a spell')", s.extort_paid_total == 1)
modo(count=False)
s = novo([], hand=["Sol Ring", "Lotho, Corrupt Shirriff"])
V.cast_card(s, "Sol Ring"); V.cast_card(s, "Lotho, Corrupt Shirriff")
teste("S7 chave desligada = comportamento antigo: o Lotho dispara contra si mesmo", s.treasures_created_total == 1 and s.life == 39)
s = novo(["Lotho, Corrupt Shirriff"], hand=["Dictate of Erebos"]); s.graveyard = ["Sevinne's Reclamation", "Zulaport Cutthroat"]
V.try_sevinne_flashback(s)
teste("S8 chave desligada: flashback nao conta", s.spells_cast_this_turn == 0)
modo()

# ------------------------------------------------------------------ item 4: Storm
def combate_storm(pump_sacrificios, flag=True, baseline=0):
    modo(storm=flag)
    s = novo(["Captain Lannery Storm", "The Reaver Cleaver"], lands=0)
    s.reaver_cleaver_host = "Captain Lannery Storm"; s.reaver_cleaver_equipped = True
    s.treasures_sacrificed_this_turn = pump_sacrificios; s.storm_sac_baseline = baseline
    s.creature_cast_turn["Captain Lannery Storm"] = 1
    V.combat_step(s)
    modo()
    return s
s = combate_storm(2)
teste("W1 Storm equipada com o Cleaver, 2 Treasures sacrificados antes do dano: ataque (+1) + Cleaver (2 + 1 + 2 = 5) = 6 Treasures", s.treasures_created_total == 6 and s.storm_pump_total == 2, str((s.treasures_created_total, s.storm_pump_total)))
s = combate_storm(2, flag=False)
teste("W2 chave desligada: sem o +1/+0 (1 + 3 = 4 Treasures)", s.treasures_created_total == 4 and s.storm_pump_total == 0)
s = combate_storm(3, baseline=3)
teste("W3 os Treasures sacrificados pra CONJURAR a Storm nao contam (ruling 2017-09-29): 1 + 3 = 4", s.treasures_created_total == 4)
modo()
s = novo([], hand=["Captain Lannery Storm"], lands=0); s.treasures = 5
V.cast_card(s, "Captain Lannery Storm")
base = s.treasures_sacrificed_this_turn
teste("W4 Storm paga com Treasures: base dos sacrificios = os feitos pra paga-la; bonus = 0", base == 3 and s.storm_sac_baseline == 3 and V._storm_pump(s) == 0, str((base, s.storm_sac_baseline)))
V.sacrifice_treasures(s, 1, for_mana=True)
teste("W5 um sacrificio depois da conjuracao da Storm = +1/+0", V._storm_pump(s) == 1)
s = combate_storm(2)
s2 = novo(["Captain Lannery Storm"], lands=0); s2.creature_cast_turn["Captain Lannery Storm"] = 1; s2.treasures_sacrificed_this_turn = 2
V.combat_step(s2)
teste("W6 o dano de combate proxy da propria Storm cresce com o bonus (poder 2 + 2)", s2.combat_damage_proxy_total == 4, str(s2.combat_damage_proxy_total))

# ------------------------------------------------------------------ item 5: alvo da Sevinne's = permanent card
s = novo(); s.graveyard = ["Sevinne's Reclamation", "Mahadi, Emporium Master"]
V.resolve_instant_sorcery(s, "Sevinne's Reclamation")
teste("V1 cemiterio [Sevinne's (ela mesma), Mahadi]: devolve o MAHADI (criatura MV3), nao a propria Sevinne's",
      "Mahadi, Emporium Master" in s.battlefield and "Sevinne's Reclamation" not in s.battlefield and "Sevinne's Reclamation" in s.graveyard)
s = novo(); s.graveyard = ["Boros Charm", "Back in Town", "Sevinne's Reclamation"]
V.resolve_instant_sorcery(s, "Sevinne's Reclamation")
teste("V2 so' instantanea/feitico no cemiterio (nenhuma 'permanent card'): nao devolve nada", [c for c in s.battlefield if c != "Mountain"] == [] and len(s.graveyard) == 3)
s = novo(); s.graveyard = ["Path of Ancestry", "Sevinne's Reclamation"]
V.resolve_instant_sorcery(s, "Sevinne's Reclamation")
teste("V3 terreno E' 'permanent card' (ruling 2024-06-07): sem outro alvo, devolve o terreno, que entra TAPPED se a regra dele manda", "Path of Ancestry" in s.battlefield and "Path of Ancestry" in s.tapped_lands_this_turn and s.lands_played_this_turn == 0)
s = novo(); s.graveyard = ["Path of Ancestry", "Captain Lannery Storm", "Sevinne's Reclamation"]
V.resolve_instant_sorcery(s, "Sevinne's Reclamation")
teste("V4 com criatura MV3 e terreno: prefere a criatura (maior MV)", "Captain Lannery Storm" in s.battlefield and "Path of Ancestry" not in s.battlefield)
s = novo(["Lotho, Corrupt Shirriff"]); s.graveyard = ["Sevinne's Reclamation", "Captain Lannery Storm", "Zulaport Cutthroat", "Boros Charm"]
V.try_sevinne_flashback(s)
teste("V5 flashback: original + copia devolvem DOIS alvos diferentes (Storm MV3 e Zulaport MV2), nunca a instantanea nem a Sevinne's", "Captain Lannery Storm" in s.battlefield and "Zulaport Cutthroat" in s.battlefield and "Boros Charm" in s.graveyard and "Sevinne's Reclamation" not in s.battlefield and s.recursion_events_total == 2)
modo(sevinne=False)
s = novo(); s.graveyard = ["Sevinne's Reclamation", "Mahadi, Emporium Master"]
V.resolve_instant_sorcery(s, "Sevinne's Reclamation")
teste("V6 chave desligada = comportamento antigo: devolve a PROPRIA Sevinne's (parada no campo) em vez do Mahadi", "Sevinne's Reclamation" in s.battlefield and "Mahadi, Emporium Master" not in s.battlefield and s.sevinne_nonpermanent_returns_total == 1)
modo()

# ------------------------------------------------------------------ invariantes em partidas reais
import collections
def jogos(n, seed0, modo_jogo):
    fn = V.simulate_one if modo_jogo == "padrao" else V.simulate_one_with_interaction
    base = collections.Counter(V.BASE_LIBRARY)
    magia_no_campo = dup = 0
    for i in range(n):
        s = fn(seed0 + i)
        if any(V.CARD_DB[c].ctype in ("instant", "sorcery") for c in s.battlefield):
            magia_no_campo += 1
        zonas = collections.Counter(s.hand + s.battlefield + s.graveyard + s.library + [c for c, _ in s.impulse_pool] + [c for c, _ in s.impulse_lands])
        if any(zonas[k] > v for k, v in base.items()):
            dup += 1
    return magia_no_campo, dup
a, b = jogos(1500, 1_000_000, "padrao")
teste("I1 (1.500 jogos, padrao, chaves ligadas) nenhuma instantanea/feitico no campo e nenhuma carta duplicada", a == 0 and b == 0, str((a, b)))
a, b = jogos(1500, 1_000_000, "resiliencia")
teste("I2 (1.500 jogos, resiliencia) idem", a == 0 and b == 0, str((a, b)))
modo(cast=False, sevinne=False)
a_old, _ = jogos(1500, 1_000_000, "padrao")
modo()
print(f"   info I3: com as chaves da esteira e da Sevinne's DESLIGADAS (codigo antigo), jogos de 1.500 com instantanea/feitico parado no campo: {a_old}")
teste("I3 o codigo antigo realmente deixava magia no campo (a lacuna existia no mundo simulado)", a_old > 0, str(a_old))

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)
