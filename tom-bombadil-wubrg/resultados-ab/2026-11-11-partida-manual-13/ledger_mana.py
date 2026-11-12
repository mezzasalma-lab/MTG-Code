"""Ledger de mana da partida manual #13 (Tom Bombadil): mana DISPONÍVEL x CUSTO das magias, por turno.
Uso: python3 -I ledger_mana.py   (saída em Markdown; sai com código 1 se algum turno gasta mais do que tinha)
Tudo aqui é LEITURA MINHA do trace e do bruto (quais fontes viraram, na ordem do log), mais o oráculo (scryfall-cache):
 - Os custos (MV) são lidos do cache e conferidos contra o que está escrito abaixo (assert), para o ledger não passar no vazio.
 - Serra's Sanctum: {T}: Add {W} para cada encantamento que você controla, contado NO MOMENTO de virar (a ordem do log decide).
 - Bloom Tender (vivid): 1 mana por cor entre os meus permanentes; com o Tom em campo são 5 (W U B R G).
 - Fertile Ground: +1 mana de qualquer cor quando o terreno encantado vira. O log NÃO registra em qual terreno ela ficou: suposto num terreno que vira depois (T6).
 - Terreno que entra virado não rende no turno (Ketria Triome no T6; Ziatora's Proving Ground no T1). A conta de COR não foi conferida (só o total), exceto o T5 (Tom precisa de WUBRG)."""
import json, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
ORC = json.load(open(os.path.join(aqui, "..", "..", "..", "scryfall-cache", "oracle-cache.json")))
MV = {"Satsuki, the Living Lore": 2, "The First Iroan Games": 3, "Bloom Tender": 2, "Tom Bombadil": 5, "Historian's Boon": 4, "Fertile Ground": 2, "Summon: Yojimbo": 4, "Goldberry, River-Daughter": 2}
for n, m in MV.items():
    assert int(ORC[n]["cmc"]) == m, (n, ORC[n]["cmc"], m)
# turno: (fontes [(nome, mana)], gastos [(descrição, custo)], nota)
T = {
 2: ([("Ziatora's Proving Ground", 1), ("Command Tower", 1)], [("Satsuki, the Living Lore", 2)], "Ziatora entrou virada no T1"),
 3: ([("Godless Shrine", 1), ("Command Tower", 1), ("Ziatora's Proving Ground", 1)], [("The First Iroan Games", 3)], "Godless Shrine entrou desvirada (2 de vida)"),
 4: ([("Temple Garden", 1), ("Command Tower", 1)], [("Bloom Tender", 2)], "só 2 fontes viradas no log; Godless Shrine e Ziatora ficaram sem uso"),
 5: ([("Serra's Sanctum (1 encantamento: Iroan)", 1), ("Temple Garden", 1), ("Godless Shrine", 1), ("Command Tower", 1), ("Ziatora's Proving Ground", 1), ("Bloom Tender (Tom em campo: 5 cores)", 5)],
     [("Tom Bombadil (sem imposto: 1ª vez)", 5), ("Historian's Boon", 4)], "WUBRG do Tom: Sanctum W, Command Tower U, Godless Shrine B, Ziatora R, Temple Garden G; Bloom Tender só rende depois do Tom"),
 6: ([("Godless Shrine", 1), ("Temple Garden", 1), ("Command Tower", 1), ("Ziatora's Proving Ground", 1), ("Serra's Sanctum (3 encantamentos: There and Back Again, Boon, Fertile Ground)", 3), ("Fertile Ground (+1)", 1)],
     [("Fertile Ground", 2), ("Summon: Yojimbo", 4), ("Goldberry, River-Daughter", 2)], "zero de folga: Bloom Tender (5 de mana potencial) ficou sem uso; Ketria Triome entrou virada (cap. II da There and Back Again)"),
 7: ([("Command Tower", 1), ("Ketria Triome", 1), ("Godless Shrine", 1), ("Temple Garden", 1), ("Ziatora's Proving Ground", 1), ("Serra's Sanctum", 4)], [], "(potencial: nada foi virado) o usuário não jogou nada no T7 (resposta de 2026-11-11: 'Não joguei mais, não usei o gold')"),
}
print("| turno | mana disponível (fontes viradas no log) | custo das magias | saldo | nota |")
print("|---|---|---|---|---|")
ruim = []
for i, (fontes, gastos, nota) in T.items():
    d = sum(m for _, m in fontes); g = sum(c for _, c in gastos)
    if g > d:
        ruim.append(i)
    print(f"| T{i} | {d} ({', '.join(f'{n} {m}' for n, m in fontes)}) | {g} ({', '.join(f'{n} {c}' for n, c in gastos) or '—'}) | {d - g:+d} | {nota} |")
print(f"\nTurnos em que o custo passa do mana: {ruim or 'nenhum'}")
sys.exit(1 if ruim else 0)
