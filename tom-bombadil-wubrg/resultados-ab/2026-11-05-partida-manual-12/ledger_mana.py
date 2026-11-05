"""Ledger de mana da partida manual #12 (Tom Bombadil): mana DISPONÍVEL x CUSTO das magias, por turno.
Uso: python3 -I ledger_mana.py   (saída em Markdown; sai com código 1 se algum turno gasta mais do que tinha, exceto os marcados como aberto)
Tudo aqui é LEITURA MINHA do trace e do bruto (quais terrenos viraram, na ordem do log), mais respostas do usuário (2026-11-05):
 - Fertile Ground estava na Floresta (resposta do usuário): a Floresta rende 2 mana. Prismatic Omen faz todo terreno render qualquer cor (sem mana extra).
 - Bloom Tender (vivid) rende 1 mana por cor entre os meus permanentes; com o Tom em campo são 5 (Tom é W U B R G).
 - Terreno que entra virado não rende no turno. A conta de COR não foi conferida (só o total).
 - Imposto do comandante: Tom custa 5 + 2 por cada vez que já foi lançado da zona de comando (CR 903.8).
"""
import sys

# turno: (fontes de mana [(nome, mana)], gastos [(descrição, custo)], nota)
T = {
 2: ([("Forest", 1), ("Ketria Triome", 1)], [("Fertile Ground", 2)], ""),
 3: ([("Forest + Fertile Ground", 2), ("Ketria Triome", 1)], [("Enchantress's Presence", 3)], "Temple Garden entrou e ficou sem uso"),
 4: ([("Forest + Fertile Ground", 2), ("Ketria Triome", 1), ("Nesting Grounds", 1)], [("Bloom Tender", 2), ("Prismatic Omen", 2)], "Temple Garden sem uso"),
 5: ([("Forest + Fertile Ground", 2), ("Ketria Triome", 1), ("Temple Garden", 1), ("Nesting Grounds", 1), ("Bloom Tender (Tom em campo: 5 cores)", 5)],
     [("Tom Bombadil (1ª vez, sem imposto)", 5), ("In the Darkness Bind Them", 5)], "Godless Shrine entrou virada; Bloom Tender só rende depois do Tom entrar"),
 6: ([("Forest + Fertile Ground", 2), ("Godless Shrine", 1), ("Temple Garden", 1), ("Nesting Grounds", 1), ("Ketria Triome", 1)],
     [("Jugan Defends the Temple", 3), ("The First Iroan Games", 3)], "Stomping Ground entrou virada; Bloom Tender (5 cores) ficou sem uso"),
 7: ([("Plains", 1), ("Nesting Grounds", 1)], [("Resurgent Belief: suspend {1}{W}", 2)], "idx 9-10; a varredura de viragens depois da 2ª Plains (idx 23-31) é desfazer/refazer"),
 8: ([("Plains", 1), ("Godless Shrine", 1), ("Forest + Fertile Ground", 2), ("Ketria Triome", 1), ("Temple Garden", 1), ("Stomping Ground", 1)],
     [("Tom Bombadil (2ª vez: 5 + imposto 2)", 7), ("Nesting Grounds: {1} da ativação (Nesting Grounds vira como custo, não rende mana)", 1)],
     "ABERTO: 7 de mana para 8 de gastos se a ativação do Nesting Grounds foi paga (o usuário diz que pagou 7 pelo Tom e que a ativação foi erro de timing); commandTax ficou 0 no log"),
 9: ([("Ketria Triome", 1), ("Raugrin Triome", 1), ("Karn's Bastion", 1), ("Forest (Fertile Ground já destruída)", 1), ("Plains", 1), ("Nesting Grounds", 1), ("Stomping Ground", 1)],
     [("Kiora Bests the Sea God", 7), ("Resurgent Belief: de graça (sem mana)", 0)], "Temple Garden e Godless Shrine sem uso; Fertile Ground só volta com a Resurgent"),
 10: ([("Ketria Triome", 1), ("Plains", 1), ("Raugrin Triome", 1), ("Forest", 1), ("Godless Shrine", 1), ("Temple Garden", 1), ("Stomping Ground", 1)],
      [("O'aka, Traveling Merchant", 2), ("Song of Eärendil", 5)], "Karn's Bastion sem uso; a Fertile Ground voltou no T9 e o bônus dela não foi usado no log"),
}
ABERTOS = {8}
print("| turno | mana disponível (fontes viradas no log) | custo das magias | saldo | nota |")
print("|---|---|---|---|---|")
ruim = []
for i, (fontes, gastos, nota) in T.items():
    d = sum(m for _, m in fontes); g = sum(c for _, c in gastos)
    if g > d and i not in ABERTOS:
        ruim.append(i)
    print(f"| T{i} | {d} ({', '.join(f'{n} {m}' for n, m in fontes)}) | {g} ({', '.join(f'{n} {c}' for n, c in gastos)}) | {d - g:+d}{' **ABERTO**' if g > d else ''} | {nota} |")
print(f"\nTurnos em que o custo passa do mana (fora os abertos): {ruim or 'nenhum'}")
sys.exit(1 if ruim else 0)
