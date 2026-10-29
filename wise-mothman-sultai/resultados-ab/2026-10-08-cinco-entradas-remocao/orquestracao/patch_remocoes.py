"""Patch do simulador do Mothman (2026-10-08, pedido do usuario): Atomize, Casualties of War e Assassin's Trophy como candidatas (entram via SWAPS; com SWAPS=() o comportamento e' bit-identico ao snapshot ANTES).
Oraculo e rulings lidos ANTES (dados/rulings_remocoes.json + dados/rulings_casualties.json do dia). Uso: python3 patch_remocoes.py <caminho do mothman_goldfish_v1.py>"""
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()

def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)

# 1) cartas
sub('add("The Earth Crystal", "{2}{G}{G}", {"artifact"}, {"earth_crystal"}, legendary=True)\n',
    'add("The Earth Crystal", "{2}{G}{G}", {"artifact"}, {"earth_crystal"}, legendary=True)\n'
    'add("Atomize", "{2}{B}{G}", {"instant"}, {"atomize"})      # candidatas de 2026-10-08 (pedido do usuario): resultados-ab/2026-10-08-cinco-entradas-remocao\n'
    'add("Casualties of War", "{2}{B}{B}{G}{G}", {"sorcery"}, {"casualties"})\n'
    'add("Assassin\'s Trophy", "{B}{G}", {"instant"}, {"trophy"})\n')

# 2) contadores de atividade (campos novos; nao mudam nenhum campo existente)
sub("    interaction_plays: int = 0\n",
    "    interaction_plays: int = 0\n"
    "    atomize_casts: int = 0\n    casualties_casts: int = 0\n    trophy_casts: int = 0\n    trophy_lands_given: int = 0\n")

# 3) resolucao
sub('    if "tear_asunder" in tags or "vats" in tags:\n        state.interaction_plays += 1\n        commit_crime(state, "removal")\n        return\n',
    '    if "tear_asunder" in tags or "vats" in tags:\n        state.interaction_plays += 1\n        commit_crime(state, "removal")\n        return\n'
    '    if "atomize" in tags:\n'
    '        # "Destroy target nonland permanent. Proliferate.": o destroy mira permanente de OPONENTE (estrutural: crime + metrica proxy); o proliferate e\' REAL (o crime vem antes: o gatilho do Deepmuck resolve antes da magia)\n'
    '        state.atomize_casts += 1\n        state.interaction_plays += 1\n        commit_crime(state, "removal")\n        proliferate(state, "atomize")\n        return\n'
    '    if "casualties" in tags:\n'
    '        # "Choose one or more": artefato / criatura / encantamento / terreno / planeswalker, alvos de OPONENTE (estrutural); uma magia que mira = UM crime; sem inventar quantos modos haveria\n'
    '        state.casualties_casts += 1\n        state.interaction_plays += 1\n        commit_crime(state, "removal")\n        return\n'
    '    if "trophy" in tags:\n'
    '        # "Destroy target permanent an opponent controls. Its controller may search their library for a basic land card, put it onto the battlefield, then shuffle."\n'
    '        # destroy: estrutural (crime + metrica proxy). A busca e\' REAL no que o simulador rastreia: o oponente alvo (o 1o vivo) tira 1 terreno da biblioteca (-1 carta) e ganha 1 terreno em campo (`Opp.lands`);\n'
    '        # o embaralhar nao tem efeito observavel (a biblioteca ja\' e\' uma permutacao aleatoria e nada aqui depende de ordem conhecida).\n'
    '        state.trophy_casts += 1\n        state.interaction_plays += 1\n        commit_crime(state, "removal")\n'
    '        al = alive_opps(state)\n'
    '        if al and "L" in al[0].library:\n'
    '            al[0].library.remove("L")\n            al[0].lands += 1\n            state.trophy_lands_given += 1\n'
    '        return\n')

# 4) fora da conjuracao automatica da mao (tratadas em act_removal_proxy)
sub('        if tags & {"wipe", "tear_asunder", "vats", "repulsive_mutation", "smugglers_surprise", "agadeem"}:',
    '        if tags & {"wipe", "tear_asunder", "vats", "repulsive_mutation", "smugglers_surprise", "agadeem", "atomize", "casualties", "trophy"}:')

# 5) politica: as cinco remocoes entram no proxy de remocao (1 por turno, so' com mana sobrando e alvo disponivel); ordem = a mais cara/multi-modo primeiro
sub('    for name in ("Tear Asunder", "V.A.T.S."):\n        if name not in state.hand:\n            continue\n        g, pips = effective_cost(state, name, 0)\n        if name == "Tear Asunder":',
    '    for name in ("Casualties of War", "Atomize", "Assassin\'s Trophy", "Tear Asunder", "V.A.T.S."):\n        if name not in state.hand:\n            continue\n        g, pips = effective_cost(state, name, 0)\n        if name == "Tear Asunder":')
sub('    """Tear Asunder / V.A.T.S.: precisam de alvo',
    '    """Tear Asunder / V.A.T.S. (+ candidatas Atomize / Casualties of War / Assassin\'s Trophy): precisam de alvo')
open(p, "w", encoding="utf-8").write(s)
print("patch ok")
