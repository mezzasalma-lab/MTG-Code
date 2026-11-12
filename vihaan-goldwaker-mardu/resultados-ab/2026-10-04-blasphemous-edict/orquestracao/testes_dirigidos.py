"""Testes dirigidos da 11a rodada: (A) Mirkwood Bats so' dispara em SACRIFICIO de ficha (oraculo ao vivo: "Whenever you create or sacrifice a token, each opponent loses 1
life"; o simulador o disparava tambem em ficha DESTRUIDA, achado ao comparar Blasphemous Act (destroi) com Blasphemous Edict (sacrifica)); (B) a semantica da Blasphemous Edict
no harness (`edict_harness.py`), carta que NAO esta na lista. Cada teste monta um GameState a mao e chama a funcao real. Uso: python3 testes_dirigidos.py"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F
import edict_harness as H

V = F.flags(F.carrega(F.DEPOIS, "vih_11a_testes"))
H.instala(V)
res = []
BM, ACT, EDICT = "Blood Money", "Blasphemous Act", H.EDICT
ZUL, LOTHO, PLUND, MAHADI, MAYHEM, BATS, NADIER = "Zulaport Cutthroat", "Lotho, Corrupt Shirriff", "Pitiless Plunderer", "Mahadi, Emporium Master", "Mayhem Devil", "Mirkwood Bats", "Nadier's Nightblade"
OLIVIA = "Olivia, Opulent Outlaw"


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def novo(bf=(), hand=(), lands=0, turn=8, commander=True, animados=0, tokens=0, constructs=0):
    bf = [n for n in bf if n != V.COMMANDER]
    s = V.GameState(hand=list(hand), battlefield=list(bf) + ["Mountain"] * lands, library=["Swamp"] * 30)
    s.turn = turn
    s.commander_cast_count = 10
    if commander:
        s.commander_in_play = True
        s.battlefield.append(V.COMMANDER)
    s.treasures = animados
    s.treasures_animated_alive = animados
    s.other_tokens = tokens
    s.constructs = constructs
    return s


# ---------------------------------------------------------------- (A) Mirkwood Bats so' em sacrificio
F.flags(V, bats=True)
s = novo([BATS], commander=False, tokens=3)
V._own_wipe_destroy_all(s)
a_on = s.drain_damage_total
s = novo([BATS], commander=False, tokens=3)
V.sacrifice_other_tokens(s, 3)
b_on = s.drain_damage_total
F.flags(V, bats=False)
s = novo([BATS], commander=False, tokens=3)
V._own_wipe_destroy_all(s)
a_off = s.drain_damage_total
F.flags(V, bats=True)
teste("B1 ficha DESTRUIDA (Blood Money/Blasphemous Act) nao dispara o Mirkwood Bats (0 de dreno com 3 fichas); chave desligada = codigo antigo (3)", a_on == 0 and a_off == 3, str((a_on, a_off)))
teste("B2 ficha SACRIFICADA dispara o Mirkwood Bats (3 de dreno com 3 fichas), com a chave ligada", b_on == 3, str(b_on))
s = novo([NADIER], commander=False, tokens=3)
V._own_wipe_destroy_all(s)
teste("B3 Nadier's Nightblade ('leaves the battlefield') continua disparando em ficha destruida: 3 de dreno e 3 de vida", s.drain_damage_total == 3 and s.life_gained_total == 3, str((s.drain_damage_total, s.life_gained_total)))
s = novo([BATS], commander=False)
V.on_permanent_destroyed(s, 2, is_artifact=False, is_creature=True, is_token=True)
teste("B4 o caminho de destruicao do OPONENTE (`on_permanent_destroyed`) tambem nao dispara o Bats", s.drain_damage_total == 0, str(s.drain_damage_total))
s = novo([BATS], commander=False, animados=4)
V.sacrifice_treasures(s, 4, for_mana=True)
teste("B5 Treasure animado SACRIFICADO por mana (ficha + criatura + artefato) dispara o Bats: 4 de dreno", s.drain_damage_total == 4, str(s.drain_damage_total))

# ---------------------------------------------------------------- (B) Blasphemous Edict (harness)
s = novo([MAYHEM, LOTHO, OLIVIA])
n = H.edict_sacrificar(V, s)
teste("E1 menos de 13 criaturas: sacrifica TODAS (Vihaan, Mayhem, Lotho, Olivia = 4), o Vihaan vai a zona de comando, e o Mayhem Devil dispara por cada sacrificio, inclusive o proprio (4 de dano)",
      n == 4 and not s.commander_in_play and s.creature_deaths_total == 4 and s.drain_damage_total == 4 and not any(V.is_creature_card(x) for x in s.battlefield), str((n, s.drain_damage_total, s.creature_deaths_total)))
s = novo([ZUL, LOTHO, OLIVIA])
H.edict_sacrificar(V, s)
teste("E2 mortes simultaneas: o Zulaport dispara pela propria morte e pelas outras (4 mortes = 4 de vida e 4 de dreno); sem Mayhem Devil nao ha' dano de sacrificio", s.life_gained_total == 4 and s.drain_damage_total == 4, str((s.life_gained_total, s.drain_damage_total)))
s = novo([BATS, MAYHEM], commander=False, tokens=3, animados=4)
H.edict_sacrificar(V, s)
teste("E3 fichas sacrificadas: Mirkwood Bats dispara por cada ficha (7) e o Mayhem Devil por cada permanente (Bats + Mayhem + 7 fichas = 9): 16 de dreno/dano no proxy", s.drain_damage_total == 16 and s.constructs == 0 and s.other_tokens == 0 and s.treasures_animated_alive == 0, str(s.drain_damage_total))
s = novo([MAHADI, MAYHEM, LOTHO], tokens=12, animados=1)
n = H.edict_sacrificar(V, s)
teste("E4 com MAIS de 13 criaturas o jogador escolhe (ruling 2024-11-08: sacrifica 13): 17 criaturas -> 13 sacrificadas, as 13 sao as fichas (12 + 1 animado) e Vihaan, Mahadi, Mayhem e Lotho SOBREVIVEM",
      n == 13 and s.commander_in_play and MAHADI in s.battlefield and MAYHEM in s.battlefield and LOTHO in s.battlefield and s.other_tokens == 0 and s.treasures_animated_alive == 0, str((n, s.battlefield)))
s = novo([MAHADI, MAYHEM, LOTHO, ZUL, OLIVIA, PLUND], tokens=9, animados=1)
n = H.edict_sacrificar(V, s)
teste("E4b 17 criaturas com so' 10 fichas: as 10 fichas + 3 nomeadas de menor valor (os motores Vihaan/Mahadi/Mayhem ficam); sacrifica exatamente 13", n == 13 and s.commander_in_play and MAHADI in s.battlefield and MAYHEM in s.battlefield, str((n, s.battlefield)))
s = novo([LOTHO], hand=[EDICT], lands=5)
c5 = V.spell_cost(s, EDICT)
s2 = novo([LOTHO] * 3, hand=[EDICT], lands=5, tokens=11)
c1 = V.spell_cost(s2, EDICT)
teste("E5 custo: {3}{B}{B} = 5; com 13 ou mais criaturas no campo (aqui so' as minhas: 3 + Vihaan + 11 fichas = 15) paga {B} = 1", (c5, c1) == (5, 1), str((c5, c1)))
a = novo([MAYHEM, LOTHO, OLIVIA], hand=[ACT], lands=5)
V.cast_card(a, ACT)
e = novo([MAYHEM, LOTHO, OLIVIA], hand=[EDICT], lands=5)
V.cast_card(e, EDICT)
teste("E6 mesma mesa (Vihaan, Mayhem, Lotho, Olivia; 5 terrenos): a Blasphemous Act destroi tudo SEM dano do Mayhem Devil; a Edict sacrifica tudo e o Mayhem Devil causa 4 de dano (so' o meu lado)",
      a.drain_damage_total == 0 and e.drain_damage_total == 4 and not e.commander_in_play and not a.commander_in_play, str((a.drain_damage_total, e.drain_damage_total)))
s = novo([MAYHEM, LOTHO], hand=[EDICT], lands=0, animados=5)
V.cast_card(s, EDICT)
teste("E7 custo da Edict (5) pago primeiro com os 5 animados: 5 sacrificios (5 de dano do Mayhem Devil, antes da magia) + o efeito sacrifica Vihaan, Mayhem, Lotho (3 de dano): 8 no total",
      s.own_wipe_animated_paid_total == 5 and s.own_wipe_pay_drain_total == 5 and s.drain_damage_total == 8 and s.mana_spent_this_turn == 0, str((s.own_wipe_animated_paid_total, s.own_wipe_pay_drain_total, s.drain_damage_total, s.mana_spent_this_turn)))
s = novo([LOTHO], hand=[EDICT], lands=8)
V.main_phase(s)
teste("E8 a Edict tambem e' segurada pela retencao universal da 10a rodada (nenhum wipe proprio sai sem a circunstancia mitigada)", EDICT in s.hand and s.own_wipes_cast_total == 0)
s = novo([MAYHEM, LOTHO, OLIVIA], hand=[EDICT], lands=0, animados=5)
V.main_phase(s)
teste("E9 a circunstancia mitigada libera a Edict como libera a Act/Blood Money (Mayhem + 5 animados pagam o custo 5; dano do pagamento 5 > 4 criaturas minhas perdidas)", s.own_wipes_cast_total == 1 and EDICT in s.graveyard, str((s.own_wipes_cast_total,)))

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)
