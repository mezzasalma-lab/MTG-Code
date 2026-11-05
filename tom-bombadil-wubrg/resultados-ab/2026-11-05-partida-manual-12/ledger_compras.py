"""Ledger de compras da partida manual #12 (Tom Bombadil): ESPERADO (se todo gatilho foi resolvido) x LOG.
Uso: python3 -I ledger_compras.py [dados/partida.json.xz]   (saída em Markdown)
Os eventos esperados por turno são LEITURA MINHA do trace (resumos/trace.md) + oráculo/rulings ao vivo + respostas do usuário (2026-11-05), não prova:
 - Compra natural: 1 por turno (T1: mão inicial de 7 + a compra do turno = 8; o usuário disse que a mão inicial são as cartas "antes da primeira compra", sem foto).
 - Enchantress's Presence ("Whenever you cast an enchantment spell, draw a card."): vale só enquanto está em campo e só para MAGIA de encantamento conjurada.
   Ruling 2021-06-18: o gatilho é independente da magia, então a Jugan ANULADA no T6 (Fold into Aether, resposta do usuário) comprou do mesmo jeito.
   Resurgent Belief é feitiço com suspend (e suspender não é conjurar); Tom e O'aka não são encantamentos.
 - Song of Eärendil cap. I: "Scry 2, then draw two cards" (+2 no T10).
 - Fica FORA da conta (e listado à parte como "linha legal"): The First Iroan Games cap. III (compre 2 se controla criatura de poder >= 4), que na linha legal do Resurgent
   no upkeep do T9 (esquecida pelo usuário) cairia no T10; o loot do Anel (compre, descarte quando o Ring-bearer ataca), esquecido pelo usuário.
"""
import json, lzma, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(aqui, "dados", "partida.json.xz")
T = json.load(lzma.open(caminho))
LOG = {i: [r["name"].split(" // ")[0] for r in t if r["fromZone"] == "library" and r["toZone"] == "hand"] for i, t in enumerate(T, 1)}

# (fonte, quantidade, nota)
ESP = {
 1: [("mão inicial 7 + compra do turno", 8, "sem foto; o usuário disse que a mão inicial são as cartas antes da 1ª compra")],
 2: [("compra do turno", 1, "")],
 3: [("compra do turno", 1, "a própria Presence não vê a sua conjuração")],
 4: [("compra do turno", 1, ""), ("Presence: Prismatic Omen conjurada", 1, "Bloom Tender não é encantamento")],
 5: [("compra do turno", 1, ""), ("Presence: In the Darkness Bind Them conjurada", 1, "Tom não é encantamento")],
 6: [("compra do turno", 1, ""), ("Presence: Jugan conjurada (ANULADA pela Fold into Aether: compra mesmo assim)", 1, "ruling 2021-06-18"),
     ("Presence: The First Iroan Games conjurada", 1, "")],
 7: [("compra do turno", 1, "Resurgent Belief suspensa: não é conjurar")],
 8: [("compra do turno", 1, "Tom recomprado do comando: não é encantamento")],
 9: [("compra do turno", 1, ""), ("Presence (devolvida pela Resurgent): Kiora conjurada (2ª vez, depois de desfazer a 1ª)", 1, "1 conjuração válida; resposta do usuário")],
 10: [("compra do turno", 1, ""), ("Presence: Song of Eärendil conjurada", 1, ""), ("Song of Eärendil cap. I: compre 2", 2, "Estrid's Invocation, Elspeth Conquers Death, Verdant Catacombs na ordem do log")],
}
print("| turno | esperado | log | diferença (log − esperado) | fontes esperadas | cartas library→mão no log |")
print("|---|---|---|---|---|---|")
te = tl = 0
for i in range(1, len(T) + 1):
    e = sum(n for _, n, _ in ESP.get(i, []))
    l = len(LOG[i])
    te += e; tl += l
    fontes = "; ".join(f"{f} ×{n}" for f, n, _ in ESP.get(i, []) if n)
    print(f"| T{i} | {e} | {l} | {l - e:+d} | {fontes} | {', '.join(LOG[i])} |")
print(f"\n**Total esperado {te} × log {tl} (log − esperado = {tl - te:+d}).**")

print("\n### Linha legal que o usuário não jogou (NÃO entra na conta acima)\n")
print("| turno | o que a regra pedia | o que o log mostra | efeito |")
print("|---|---|---|---|")
print("| T8 | cap. IV da In the Darkness Bind Them resolve com o Tom no comando (sem gatilho do Tom); a Saga é sacrificada ao sair a habilidade da pilha (CR 714.4). Nesting Grounds só ativa como feitiço (CR 602.5d, 307.5): não há janela para tirar o marcador | Lore 4 → 3 e marcador movido para um Human Soldier; ITDBT fica em campo e a Austere a destrói | nenhum: a ITDBT vai ao cemitério do mesmo jeito (sacrificada ou destruída) antes da Resurgent Belief |")
print("| T9 | Resurgent Belief resolve no UPKEEP (suspend: o gatilho remove o último contador e você pode conjurar ali; se não conjurar, fica exilada): 6 encantamentos voltam antes da compra; ITDBT, Iroan e Jugan ganham o 2º marcador no mesmo turno (cap. II no T9) | contador removido na fase principal, depois da Kiora (idx 21-24); cap. II só no T10 | os efeitos do cap. II vêm 1 turno depois (contra o jogador) |")
print("| T10 | com a linha legal, cap. III: Iroan (compre 2: Tom tem poder 4 ou mais), ITDBT (Wraith + Anel) e Jugan (vira Remnant of the Rising Star) | cap. II aplicado sem clicar o marcador de saber (usuário: esqueceu) | Iroan III (+2 cartas) não aconteceria neste log nem na linha jogada |")
print("| T7 | Ring-bearer com o Anel em 2 ou mais: compre e descarte ao atacar. O Human Soldier criado no T7 NÃO pode atacar (enjoo de invocação); só valeria se o Ring-bearer escolhido fosse outra criatura que ataque (o Tom, por exemplo) | Soldier virado no T7; sem loot | o usuário confirmou que errou o enjoo e esqueceu o loot |")
