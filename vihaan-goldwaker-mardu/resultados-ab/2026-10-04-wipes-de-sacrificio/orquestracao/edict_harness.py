"""Harness da Blasphemous Edict no simulador do Vihaan, SEM alterar vihaan_goldfish_v1.py (a carta NAO esta na lista: avaliacao de troca pedida pelo usuario).
Oraculo ao vivo (2026-10-04): {3}{B}{B} Sorcery: "You may pay {B} rather than pay this spell's mana cost if there are thirteen or more creatures on the battlefield.
Each player sacrifices thirteen creatures of their choice." Rulings (2024-11-08): com menos de 13 criaturas o jogador sacrifica todas; na ordem de turno cada um escolhe
o que sacrificar e entao tudo e' sacrificado AO MESMO TEMPO. Mayhem Devil: "whenever a player sacrifices a permanent" (de QUALQUER jogador; o proprio Mayhem Devil
tambem dispara; se o sacrificio ocorre durante a resolucao, a magia termina antes do gatilho entrar na pilha). Mirkwood Bats: "whenever you create or sacrifice a token".
So' o MEU lado e' modelado: as criaturas do oponente que a Edict faria sacrificar (e o dano do Mayhem Devil / o Treasure do Revel in Riches por elas) sao 📊.
Uso: import edict_harness as H; H.instala(V) com V = modulo do simulador ja' carregado."""
EDICT = "Blasphemous Edict"
LIMITE = 13


def edict_sacrificar(V, state, limite=LIMITE):
    named = [n for n in state.battlefield if V.is_creature_card(n)]
    n_con, n_oth, n_dra = state.constructs, state.other_tokens, state.dragons
    n_anim = min(state.treasures_animated_alive, state.treasures)
    total = len(named) + n_con + n_oth + n_dra + n_anim
    restante = min(total, limite)  # "sacrifices thirteen creatures": com menos, sacrifica todas
    sac_anim = min(n_anim, restante); restante -= sac_anim
    sac_con = min(n_con, restante); restante -= sac_con
    sac_oth = min(n_oth, restante); restante -= sac_oth
    sac_dra = min(n_dra, restante); restante -= sac_dra
    motores = {V.COMMANDER, "Mahadi, Emporium Master", "Mayhem Devil"}
    ordem = sorted(named, key=lambda n: (n in motores, V.CARD_DB[n].mv))  # com mais de 13, o jogador escolhe: fichas primeiro, depois as nomeadas de menor valor, guardando os motores
    sac_named = ordem[:restante]
    total_sac = len(sac_named) + sac_con + sac_oth + sac_dra + sac_anim
    V.begin_mass_death(state, sac_named)
    if "Mayhem Devil" in state.battlefield:
        V.drain(state, total_sac)  # 1 de dano por permanente sacrificada (todas simultaneas: o Mayhem Devil ve todas, inclusive a propria)
    for c in sac_named:
        V.on_creature_dies(state, 1, is_token=False, dying=c)
        if V.is_artifact_card(c):
            V.on_artifact_dies(state, 1)
    if sac_con:
        V.on_creature_dies(state, sac_con, is_token=True); V.on_artifact_dies(state, sac_con); V.on_token_leaves(state, sac_con, sacrificed=True)
    if sac_oth:
        V.on_creature_dies(state, sac_oth, is_token=True); V.on_token_leaves(state, sac_oth, sacrificed=True)
    if sac_dra:
        V.on_creature_dies(state, sac_dra, is_token=True); V.on_token_leaves(state, sac_dra, sacrificed=True)
    if sac_anim:
        V.on_creature_dies(state, sac_anim, is_token=True); V.on_artifact_dies(state, sac_anim); V.on_token_leaves(state, sac_anim, sacrificed=True)
    V.end_mass_death(state)
    for c in sac_named:
        state.battlefield.remove(c)
        state.creature_cast_turn.pop(c, None)
        if c == V.COMMANDER:
            state.commander_in_play = False
            state.own_wipe_commander_destroyed_total += 1
        else:
            state.graveyard.append(c)
    state.constructs -= sac_con; state.constructs_sick = min(state.constructs_sick, state.constructs)
    state.other_tokens -= sac_oth; state.other_tokens_sick = min(state.other_tokens_sick, state.other_tokens)
    state.dragons -= sac_dra; state.dragons_sick = min(state.dragons_sick, state.dragons)
    if sac_anim:
        state.treasures -= sac_anim
        state.treasures_animated_alive = max(0, state.treasures_animated_alive - sac_anim)
        state.treasures_tapped = min(state.treasures_tapped, state.treasures)
        state.treasures_sacrificed_total += sac_anim  # Captain Lannery Storm: "whenever you sacrifice a Treasure"
        state.treasures_sacrificed_this_turn += sac_anim
    return total_sac


def instala(V):
    V.add(EDICT, 5, "sorcery", {"wipe"})
    if EDICT not in V.OWN_WIPES:
        V.OWN_WIPES = tuple(V.OWN_WIPES) + (EDICT,)
    orig_cost, orig_res = V.spell_cost, V.resolve_instant_sorcery

    def spell_cost(state, name):
        if name == EDICT:  # {B} no lugar de {3}{B}{B} se ha' 13 ou mais criaturas NO CAMPO (aqui so' as minhas: piso; as do oponente sao 📊)
            return 1 if V.creatures_on_battlefield(state) >= LIMITE else 5
        return orig_cost(state, name)

    def resolve(state, name):
        if name == EDICT:
            state.own_wipes_cast_total += 1
            edict_sacrificar(V, state)
            return
        return orig_res(state, name)
    V.spell_cost, V.resolve_instant_sorcery = spell_cost, resolve
    return V
