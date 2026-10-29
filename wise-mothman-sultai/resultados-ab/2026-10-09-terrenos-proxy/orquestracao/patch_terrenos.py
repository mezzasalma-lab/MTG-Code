"""Patch do simulador do Mothman (2026-10-09, pedido do usuario: terrenos com proxy): (1) Underground Sea, Bayou e Tropical Island (duais originais: sem condicao, sem dano, com os 2 tipos de terreno basico);
(2) Prismatic Vista (fetch de qualquer basico, 1 de vida, o terreno buscado entra DESVIRADO); (3) chave `COMMANDER_REMOVAL_SHARE` (padrao 0.0 = comportamento anterior, bit-identico): com valor > 0, quando o comandante esta em
campo, essa fracao das remocoes pontuais do oponente mira o COMANDANTE (o simulador anterior nunca mirava o comandante com remocao pontual, so' o anulava na pilha e o incluia nos wipes); serve para medir o valor das regeneracoes
(Swarmyard e' Inseto/Rato/Aranha/Esquilo: regenera o Mothman, que e' Inseto Mutante). Uso: python3 patch_terrenos.py <caminho do mothman_goldfish_v1.py>"""
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90]); s = s.replace(old, new)
# 1) cartas
sub('add("Zagoth Triome", "", {"land"}, {"etb_tapped", "triome", "cycling3"}, produces={"B", "G", "U"}, land_types={"Swamp", "Forest", "Island"})\n',
    'add("Zagoth Triome", "", {"land"}, {"etb_tapped", "triome", "cycling3"}, produces={"B", "G", "U"}, land_types={"Swamp", "Forest", "Island"})\n'
    'add("Underground Sea", "", {"land"}, set(), produces={"U", "B"}, land_types={"Island", "Swamp"})      # candidatas de 2026-10-09 (terrenos com proxy): resultados-ab/2026-10-09-terrenos-proxy\n'
    'add("Bayou", "", {"land"}, set(), produces={"B", "G"}, land_types={"Swamp", "Forest"})\n'
    'add("Tropical Island", "", {"land"}, set(), produces={"G", "U"}, land_types={"Forest", "Island"})\n'
    'add("Prismatic Vista", "", {"land"}, {"fetch", "vista"})\n')
# 2) Prismatic Vista no crack_fetch
sub('    fabled = "fabled_passage" in perm.card.tags\n    if fabled:\n        pred = lambda c: "basic" in CARD_DB[c].tags\n',
    '    fabled = "fabled_passage" in perm.card.tags\n    vista = "vista" in perm.card.tags       # Prismatic Vista: qualquer basico, 1 de vida, o terreno buscado entra DESVIRADO\n    if fabled or vista:\n        pred = lambda c: "basic" in CARD_DB[c].tags\n')
sub('        put_land_onto_battlefield(state, target, source="fetch")\n    return True\n',
    '        put_land_onto_battlefield(state, target, source="vista" if vista else "fetch")\n    return True\n')
# 3) chave: remocao pontual do oponente mira o comandante
sub('INTERACTION_SETUP_TURNS = 2\n',
    'INTERACTION_SETUP_TURNS = 2\nCOMMANDER_REMOVAL_SHARE = 0.0           # [2026-10-09] fracao das remocoes pontuais do oponente que mira o COMANDANTE quando ele esta em campo (0.0 = comportamento anterior, bit-identico)\n')
sub('    perm = next(p for p in state.battlefield if eff_name(p) == target_name)\n    # Swiftfoot Boots',
    '    if COMMANDER_REMOVAL_SHARE > 0 and state.interaction_rng.random() < COMMANDER_REMOVAL_SHARE:\n'
    '        cmd_perm = next((p for p in state.battlefield if eff_name(p) == COMMANDER), None)\n'
    '        if cmd_perm is not None:\n            target_name = COMMANDER\n'
    '    perm = next(p for p in state.battlefield if eff_name(p) == target_name)\n    # Swiftfoot Boots')
sub('''    target_name = next((n for n in INTERACTION_ENGINE_PRIORITY if any(eff_name(p) == n for p in state.battlefield)), None)
    if target_name is None:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    if COMMANDER_REMOVAL_SHARE > 0 and state.interaction_rng.random() < COMMANDER_REMOVAL_SHARE:
        cmd_perm = next((p for p in state.battlefield if eff_name(p) == COMMANDER), None)
        if cmd_perm is not None:
            target_name = COMMANDER
    perm = next''', '''    target_name = next((n for n in INTERACTION_ENGINE_PRIORITY if any(eff_name(p) == n for p in state.battlefield)), None)
    cmd_em_jogo = COMMANDER_REMOVAL_SHARE > 0 and any(eff_name(p) == COMMANDER for p in state.battlefield)       # [2026-10-09] chave desligada (0.0): nenhum sorteio novo, bit-identico
    if target_name is None and not cmd_em_jogo:
        return None
    if state.interaction_rng.random() >= interaction_chance(state):
        return None
    if cmd_em_jogo and state.interaction_rng.random() < COMMANDER_REMOVAL_SHARE:
        target_name = COMMANDER
    if target_name is None:
        return None
    perm = next''')
open(p, "w", encoding="utf-8").write(s); print("patch ok")
