"""Testes diretos das 4 lacunas do simulador achadas ao auditar a partida manual #1, contra o simulador do commit c04840d (snapshot em
../codigo/). Cada teste monta um GameState a mao e chama a funcao real. Uso: python3 lacunas_simulador_c04840d.py"""
import importlib.util, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
os.chdir(os.path.join(DECK, "resultados-ab", "_lista_legada"))   # 12a rodada: o snapshot le a lista de a17049f (com Blood Money)
spec = importlib.util.spec_from_file_location("v", os.path.join(AQUI, "..", "codigo", "vihaan_goldfish_v1_c04840d.py"))
V = importlib.util.module_from_spec(spec); sys.modules["v"] = V; spec.loader.exec_module(V)


def novo(bf, pool=(), lands=12, hand=()):
    s = V.GameState(hand=list(hand), battlefield=list(bf) + ["Mountain"] * lands, library=["Swamp"] * 20)
    s.turn = 7
    s.impulse_pool = [(c, 8) for c in pool]
    return s

print("1) terreno exilado pelo Prosper: pull_impulse poe no pool e play_from_impulse o ignora")
s = novo(["Prosper, Tome-Bound"], ["Desolate Mire"]); s.hand = []
ok = V.play_from_impulse(s)
print("   play_from_impulse devolveu %s | Desolate Mire no campo: %s | Treasures criados: %d (esperado pelo oraculo: jogar o terreno e +1 Treasure)" % (ok, "Desolate Mire" in s.battlefield, s.treasures_created_total))

print("2) Blood Money do exilio")
s = novo(["Prosper, Tome-Bound", "Zulaport Cutthroat"], ["Blood Money"])
ok = V.play_from_impulse(s)
print("   jogou=%s | Blood Money no CAMPO=%s | no cemiterio=%s | Zulaport ainda em campo=%s | mortes de criatura=%d | spells_cast=%d (esperado: wipe, cemiterio, 1 magica conjurada)" % (
    ok, "Blood Money" in s.battlefield, "Blood Money" in s.graveyard, "Zulaport Cutthroat" in s.battlefield, s.creature_deaths_total, s.spells_cast_this_turn))
s = novo(["Prosper, Tome-Bound"], ["Sevinne's Reclamation"]); s.graveyard = ["Mahadi, Emporium Master"]
V.play_from_impulse(s)
print("   Sevinne's do exilio com Mahadi no cemiterio: Mahadi voltou=%s (esperado: voltou, como no T6 da partida)" % ("Mahadi, Emporium Master" in s.battlefield))

print("3) contagem de 'spell cast' e Lotho")
s = novo(["Prosper, Tome-Bound"], ["Lotho, Corrupt Shirriff"]); s.hand = ["Monologue Tax"]
V.play_from_impulse(s); t0 = s.treasures_created_total
V.cast_card(s, "Monologue Tax")
print("   Lotho do exilio + Tax da mao: spells_cast=%d, Treasures do Lotho na Tax=%d (esperado 2 e 1)" % (s.spells_cast_this_turn, s.treasures_created_total - t0))
s = novo(["Lotho, Corrupt Shirriff"]); s.graveyard = ["Sevinne's Reclamation", "Zulaport Cutthroat"]; s.hand = ["Dictate of Erebos"]
V.try_sevinne_flashback(s); n1 = s.spells_cast_this_turn; t0 = s.treasures_created_total
V.cast_card(s, "Dictate of Erebos")
print("   flashback Sevinne's (1a) depois Dictate (2a): spells_cast apos o flashback=%d (esperado 1); Treasures do Lotho no Dictate=%d (esperado 1)" % (n1, s.treasures_created_total - t0))
s = novo([]); s.hand = ["Sol Ring", "Lotho, Corrupt Shirriff"]; t0 = s.treasures_created_total
V.cast_card(s, "Sol Ring"); V.cast_card(s, "Lotho, Corrupt Shirriff")
print("   Sol Ring depois Lotho (2a magica): Treasures=%d, vida=%d (esperado 0 e 40: o Lotho estava na pilha)" % (s.treasures_created_total - t0, s.life))

print("4) Storm: +1/+0 por Treasure sacrificado")
print("   'Lannery' aparece no .py nas linhas: %s (so' o gatilho de ataque; nenhuma menciona o +1/+0)" % [i + 1 for i, l in enumerate(open(os.path.join(AQUI, "..", "codigo", "vihaan_goldfish_v1_c04840d.py"))) if "Lannery" in l])
