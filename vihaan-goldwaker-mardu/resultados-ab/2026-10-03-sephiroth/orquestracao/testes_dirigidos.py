"""Testes dirigidos do Sephiroth (3a rodada): emblema acumulavel, mortes simultaneas em wipe, contador por turno. Cada teste monta
um GameState a mao e chama a funcao real do simulador. Uso: python3 testes_dirigidos.py"""
import random, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fx_common as F

V = F.flags(F.carrega(F.DEPOIS, "vih_seph_testes"))
S = V.SEPHIROTH
res = []


def teste(nome, cond, detalhe=""):
    res.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", nome, ("| " + detalhe) if detalhe and not cond else "")


def novo(bf=(S,), emblemas=0, transformado=False, contador=0):
    s = V.GameState(hand=[], battlefield=list(bf), library=["Swamp"] * 20)
    s.super_nova_emblems = emblemas
    s.has_super_nova_emblem = emblemas > 0
    s.sephiroth_transformed = transformado
    s.sephiroth_deaths_this_turn = contador
    return s


def modo(emb, sim, fro):
    V.SEPHIROTH_EMBLEM_STACKING_ENABLED, V.SEPHIROTH_SIMULTANEOUS_DEATH_ENABLED, V.SEPHIROTH_TURN_BOUNDARY_ENABLED = emb, sim, fro


def mortes(s, n, um_a_um=False):
    d0 = s.drain_damage_total
    if um_a_um:
        for _ in range(n):
            V.on_creature_dies(s, 1, False)
    else:
        V.on_creature_dies(s, n, False)
    return s.drain_damage_total - d0


SEM_GATILHO = ["Prosper, Tome-Bound", "Mahadi, Emporium Master", "Lotho, Corrupt Shirriff", "Magda, the Hoardmaster", "Aya of Alexandria"]

# ----------------------------------------------------------- comportamento que ja' estava certo (regressao)
s = novo(); d = mortes(s, 3)
teste("B1 3 mortes: 3 drains, nao vira", d == 3 and not s.sephiroth_transformed and s.super_nova_emblems == 0)
s = novo(); d = mortes(s, 4)
teste("B2 4 mortes juntas: vira, 1 emblema, 4 drains", d == 4 and s.sephiroth_transformed and s.super_nova_emblems == 1 and s.has_super_nova_emblem)
s = novo(); d = mortes(s, 4, um_a_um=True)
teste("B3 4 mortes uma a uma: o mesmo", d == 4 and s.sephiroth_transformed and s.super_nova_emblems == 1)
s = novo(); d = mortes(s, 6)
teste("B4 6 mortes juntas: 6 drains, 1 emblema (a 5a e a 6a ja' estavam na pilha)", d == 6 and s.super_nova_emblems == 1)
s = novo(bf=[], emblemas=1, transformado=True); d = mortes(s, 2)
teste("B5 emblema sem Sephiroth em campo: 1 drain por morte (permanente)", d == 2)

# ----------------------------------------------------------- item 2: emblema + Sephiroth de frente
s = novo(emblemas=1); d = mortes(s, 3, um_a_um=True)
teste("E1 emblema + Sephiroth de frente: DOIS gatilhos por morte (3 mortes = 6 drains)", d == 6 and s.sephiroth_deaths_this_turn == 3 and not s.sephiroth_transformed, f"d={d} cont={s.sephiroth_deaths_this_turn}")
s = novo(emblemas=1); d = mortes(s, 4, um_a_um=True)
teste("E2 a 4a resolucao da frente vira de novo: 2o emblema (acumula)", d == 8 and s.sephiroth_transformed and s.super_nova_emblems == 2, f"d={d} emb={s.super_nova_emblems}")
d5 = mortes(s, 1)
teste("E2 depois da 2a virada, cada morte dispara os 2 emblemas", d5 == 2, str(d5))
s = novo(bf=[], emblemas=2, transformado=True); d = mortes(s, 3)
teste("E3 2 emblemas e Sephiroth fora: 3 mortes = 6 drains", d == 6)
modo(False, False, False)
s = novo(emblemas=1); d = mortes(s, 3, um_a_um=True)
teste("E4 chaves desligadas (codigo antigo): emblema + frente = 1 gatilho por morte (o erro documentado)", d == 3)
modo(True, True, True)
s = novo(emblemas=1); mortes(s, 4, um_a_um=True)
teste("E5 gain_life acompanha o drain (1 por gatilho)", s.life_gained_total == 8, str(s.life_gained_total))

# ----------------------------------------------------------- item 3: wipe com mortes simultaneas
def wipe_proprio(ordem_seph, simultaneas=True):
    modo(True, simultaneas, True)
    others = SEM_GATILHO[:4]
    bf = ([S] + others) if ordem_seph == "primeiro" else (others + [S])
    s = V.GameState(hand=[], battlefield=list(bf), library=["Swamp"] * 20)
    d0 = s.drain_damage_total
    V.resolve_instant_sorcery(s, "Blasphemous Act")
    modo(True, True, True)
    return s, s.drain_damage_total - d0

s, d = wipe_proprio("primeiro")
teste("W1 Blasphemous Act, Sephiroth de frente listado PRIMEIRO, 4 outras morrem junto: 4 gatilhos, nao vira (ruling 2025-06-06)", d == 4 and not s.sephiroth_transformed and s.super_nova_emblems == 0, f"d={d} transf={s.sephiroth_transformed}")
s, d = wipe_proprio("ultimo")
teste("W2 idem com o Sephiroth listado ULTIMO: o mesmo resultado (a ordem de remocao nao importa)", d == 4 and not s.sephiroth_transformed and s.super_nova_emblems == 0, f"d={d} transf={s.sephiroth_transformed}")
s, d = wipe_proprio("primeiro", simultaneas=False)
t1 = (d == 0)
s2, d2 = wipe_proprio("ultimo", simultaneas=False)
teste("W3 codigo antigo (chave desligada): Sephiroth primeiro = 0 gatilhos; ultimo = 5 (4 da frente + o emblema recem-criado na propria morte) E vira (apesar de morrer junto): o erro documentado",
      t1 and d2 == 5 and s2.sephiroth_transformed, f"primeiro={d} ultimo={d2} transf={s2.sephiroth_transformed}")
# lote em que o Sephiroth sobrevive: 5 mortes (ex.: fichas), vira na 4a, 5 gatilhos (o 5o ja' estava na pilha), emblema novo nao dispara pro lote
s = novo()
V.begin_mass_death(s, [])
d0 = s.drain_damage_total
V.on_permanent_destroyed(s, 5, is_artifact=True, is_creature=True, is_token=True)
V.end_mass_death(s)
teste("W4 5 fichas morrem juntas, Sephiroth sobrevive: 5 gatilhos, vira na 4a, 1 emblema", s.drain_damage_total - d0 == 5 and s.sephiroth_transformed and s.super_nova_emblems == 1,
      f"d={s.drain_damage_total - d0} emb={s.super_nova_emblems}")
# Sephiroth virado + 1 emblema morre junto com 3 outras: o emblema dispara 4x (inclui a morte dele mesmo)
modo(True, True, True)
s = V.GameState(hand=[], battlefield=[S] + SEM_GATILHO[:3], library=["Swamp"] * 20)
s.sephiroth_transformed, s.super_nova_emblems, s.has_super_nova_emblem = True, 1, True
d0 = s.drain_damage_total
V.resolve_instant_sorcery(s, "Blasphemous Act")
teste("W5 Sephiroth virado + emblema morre com 3 outras: 4 gatilhos do emblema (a propria morte conta)", s.drain_damage_total - d0 == 4, str(s.drain_damage_total - d0))
# emblema + frente no mesmo wipe: a frente dispara so' pras OUTRAS (nao pra si), o emblema dispara pra todas, inclusive o Sephiroth
modo(True, True, True)
s = V.GameState(hand=[], battlefield=[S] + SEM_GATILHO[:3], library=["Swamp"] * 20)
s.super_nova_emblems, s.has_super_nova_emblem = 1, True
d0 = s.drain_damage_total
V.resolve_instant_sorcery(s, "Blasphemous Act")
teste("W8 emblema + Sephiroth de frente morrem com 3 outras: emblema 4 (inclui a morte dele) + frente 3 (so' as outras) = 7, nao vira",
      s.drain_damage_total - d0 == 7 and not s.sephiroth_transformed and s.super_nova_emblems == 1, f"d={s.drain_damage_total - d0} emb={s.super_nova_emblems}")
# Sephiroth sacrificado sozinho (fora de lote): nao dispara a propria frente
s = novo(); d0 = s.drain_damage_total
V.sacrifice_named_creature(s, S)
teste("W9 Sephiroth sacrificado sozinho: 0 gatilhos (a frente diz 'another')", s.drain_damage_total - d0 == 0, str(s.drain_damage_total - d0))
s = V.GameState(hand=[], battlefield=[S] + SEM_GATILHO[:3], library=["Swamp"] * 20)
s.sephiroth_transformed, s.super_nova_emblems, s.has_super_nova_emblem = True, 1, True
# o lote nao vaza: depois do wipe o estado de lote esta inativo
teste("W6 begin/end_mass_death: o lote termina inativo", not s.seph_batch_active and not s.seph_batch_leaves)
# wipe de OPONENTE: usa o mesmo caminho (try_smart_opponent_wipe), com Sephiroth de frente + criaturas nomeadas
def wipe_oponente(ligado):
    modo(True, ligado, True)
    st = V.GameState(hand=[], battlefield=[S] + SEM_GATILHO[:4], library=["Swamp"] * 20, interaction_rng=random.Random(5))
    st.turn = 5
    # forca o wipe de criatura: restringe o sorteio ao tipo 'creature'
    orig = V.WIPE_TYPE_WEIGHTS.copy()
    V.WIPE_TYPE_WEIGHTS.update({"creature": 1.0, "artifact": 0.0, "enchantment": 0.0})
    orig_ch = V.interaction_chance
    V.interaction_chance = lambda state: 1.0
    d0 = st.drain_damage_total
    try:
        V.try_smart_opponent_wipe(st)
    finally:
        V.WIPE_TYPE_WEIGHTS.clear(); V.WIPE_TYPE_WEIGHTS.update(orig); V.interaction_chance = orig_ch
    modo(True, True, True)
    return st, st.drain_damage_total - d0
st, d = wipe_oponente(True)
teste("W7 wipe de OPONENTE (try_smart_opponent_wipe): Sephiroth de frente + 4 outras criaturas morrem junto: 4 gatilhos, nao vira", d == 4 and not st.sephiroth_transformed, f"d={d}")
st, d_off = wipe_oponente(False)
teste("W7 (codigo antigo) o mesmo wipe: 0 gatilhos, porque o Sephiroth saia do campo primeiro (e e' o 1o da lista)", d_off == 0, str(d_off))

# ----------------------------------------------------------- contador por turno
def inicio_turno_oponente(ligado, contador=3):
    modo(True, True, ligado)
    st = V.GameState(hand=[], battlefield=[S], library=["Swamp"] * 20, interaction_rng=random.Random(1))
    st.turn = 1  # turno de setup: nenhuma interacao rola, so' o reset
    st.sephiroth_deaths_this_turn = contador
    V.try_smart_opponent_turn(st)
    modo(True, True, True)
    return st.sephiroth_deaths_this_turn
teste("T1 cada turno de oponente zera o contador do Sephiroth", inicio_turno_oponente(True) == 0)
teste("T1 (codigo antigo) o contador vazava do meu turno pro do oponente", inicio_turno_oponente(False) == 3)
# 3 mortes no meu turno + 1 no do oponente: nao vira (turnos diferentes)
s = novo(); mortes(s, 3); s.sephiroth_deaths_this_turn = 0  # reset do turno do oponente
mortes(s, 1)
teste("T2 3 mortes no meu turno + 1 no turno do oponente: NAO vira (eram 2 turnos)", not s.sephiroth_transformed)
# reentrada: objeto novo
def reentrada(ligado):
    modo(ligado, True, True)
    st = V.GameState(hand=[], battlefield=[], library=["Swamp"] * 20)
    st.sephiroth_deaths_this_turn = 3
    V.enter_battlefield(st, S, from_hand=False)
    modo(True, True, True)
    return st.sephiroth_deaths_this_turn
teste("T3 Sephiroth volta ao campo no mesmo turno: objeto novo, contador recomeca em 0", reentrada(True) == 0)
teste("T3 (codigo antigo) o contador era herdado do objeto anterior", reentrada(False) == 3)

# ----------------------------------------------------------- invariantes em partidas reais (resiliencia: onde os wipes acontecem)
orig_et = V.end_step
viol_lote = viol_sync = 0
def et(state):
    global viol_lote
    if state.seph_batch_active:
        viol_lote += 1
    orig_et(state)
V.end_step = et
extra = 0
for i in range(2000):
    st = V.simulate_one_with_interaction(1_000_000 + i)
    if st.has_super_nova_emblem != (st.super_nova_emblems > 0):
        viol_sync += 1
    extra += st.sephiroth_extra_triggers_total
V.end_step = orig_et
teste("I1 (2.000 jogos, resiliencia) has_super_nova_emblem == (emblemas > 0), sempre", viol_sync == 0, str(viol_sync))
teste("I1 (2.000 jogos, resiliencia) nenhum lote de mortes ficou ativo ao fim do turno", viol_lote == 0, str(viol_lote))
print(f"   info I1: gatilhos extras que o codigo antigo perdia em 2.000 jogos de resiliencia: {extra}")

print(f"\n{sum(res)}/{len(res)} testes passaram")
sys.exit(0 if all(res) else 1)
