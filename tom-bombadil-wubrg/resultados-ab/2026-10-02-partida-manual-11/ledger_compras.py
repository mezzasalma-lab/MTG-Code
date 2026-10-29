"""Ledger de compras e de fichas da partida manual #11 (Tom Bombadil): ESPERADO (se todo gatilho foi resolvido) x LOG.
Uso: python3 ledger_compras.py [dados/partida.json.xz]   (saída em Markdown)
Os eventos esperados por turno foram lidos à mão do trace (resumos/trace.md) + oráculo/rulings ao vivo; são LEITURA MINHA, não prova:
 - [2026-10-03] O usuário não sabia que a Narci compra ("Whenever you sacrifice an enchantment, draw a card" é a 1ª habilidade; a 2ª é o dreno do cap. final): as compras dela estão no ledger e foram esquecidas.
 - Narci (Whenever you sacrifice an enchantment, draw a card): vale enquanto Narci está em campo; sacrifício de Saga por SBA (cap. final) conta;
   Soul Shatter/All Is Dust (sacrificar) contam; Bane of Progress/Lethal Scheme (destruir) NÃO contam.
 - Sythis (cast enchantment spell: ganhe 1, compre 1): vale só enquanto Sythis está em campo e só para MAGIA conjurada (não para devolução/ficha).
 - War of the Last Alliance I/II: tutor de lendária -> mão; Cruelty II: tutor qualquer -> mão; O'aka/Goldberry: compra por ativação; Nexus Mentality: 1 por marcador removido.
 - O 'Anel' (2ª habilidade: Ring-bearer ataca -> compre, descarte) NÃO entra aqui (ver resumo): não há descarte de loot no log.
 - Fenrir III (compre se tiver a criatura de maior poder) fica fora (depende do campo do oponente simulado).
 - Jace's Archivist (T16): o número de compras = maior descarte entre jogadores; aceito o que o log mostra (3)."""
import json, lzma, os, sys
from collections import defaultdict
aqui = os.path.dirname(os.path.abspath(__file__))
caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(aqui, "dados", "partida.json.xz")
T = json.load(lzma.open(caminho))
LOG = {i: [r["name"].split(" // ")[0] for r in t if r["fromZone"] == "library" and r["toZone"] == "hand"] for i, t in enumerate(T, 1)}

# (fonte, quantidade, nota)
ESP = {
 1: [("mão inicial 7 + compra do turno", 8, "foto: 7 cartas; a 8ª (O'aka) é a compra do T1")],
 2: [("compra do turno", 1, "")], 3: [("compra do turno", 1, "")], 4: [("compra do turno", 1, "")], 5: [("compra do turno", 1, "")],
 6: [("compra do turno", 1, ""), ("War cap. I (tutor lendária)", 1, "Narci")],
 7: [("compra do turno", 1, ""), ("War cap. II (tutor lendária)", 1, "log só mostra Goldberry no T8")],
 8: [("compra do turno", 1, "")],
 9: [("compra do turno", 1, "")],
 10: [("compra do turno", 1, "")],
 11: [("compra do turno", 1, ""), ("Narci: Eldest Reborn sacrificada (cap. III)", 1, "Narci entrou antes (idx 11) do SBA (idx 12)")],
 12: [("compra do turno", 1, ""), ("Cruelty cap. II (tutor)", 1, "Power Conduit"), ("War cap. I (tutor lendária)", 1, "Sythis")],
 13: [("compra do turno", 1, ""), ("Narci: Cruelty, ITDBT e Fenrir sacrificadas (cap. final)", 3, "Eldest foi salva (3->2): não conta"),
      ("Sythis: Sanctum Weaver e Historian's Boon conjuradas", 2, "Sythis voltou no idx 10"), ("War cap. II (tutor lendária)", 1, "Barbara"),
      ("Goldberry {U},{T}: move contador e compra", 1, "só se foi a 2ª habilidade (idx 40-42)")],
 14: [("compra do turno", 1, ""), ("Narci: War sacrificada (cap. III)", 1, "Eldest foi salva (3->2) segundo o usuário (2026-10-03): não conta; fonte do marcador: Power Conduit (idx 22), O'aka ficou desvirada")],
 15: [("compra do turno", 1, "")],
 16: [("compra do turno", 1, ""), ("O'aka: tira contador do Odin", 1, "Nexus Mentality"), ("Nexus Mentality (2 modos, comandante em campo): 2 contadores do Tom", 2, "Resurgent Belief + Prismatic Omen"),
      ("Narci: Odin sacrificada pelo Soul Shatter", 1, ""), ("Jace's Archivist (aceito o log)", 3, "Hall, Flux Channeler, Nesting Grounds")],
 17: [("compra do turno", 1, ""), ("O'aka: tira contador do Angel", 1, "Raffine's Tower")],
 18: [("compra do turno", 1, ""), ("Narci: Utopia Sprawl sacrificada pela All Is Dust (simultânea)", 1, "")],  # as 14 compras do log vieram de Sythis lida como 'encantamento ENTRA' (2026-10-03); Sythis só dispara ao CONJURAR: sem base
 19: [("compra do turno", 1, "")],
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
print(f"\n**Total esperado {te} × log {tl} (log − esperado = {tl - te:+d}).** T18: as 14 cartas extras vieram de Sythis lida como 'encantamento entra' (usuário, 2026-10-03); sem base no oráculo. Sem elas o log teria {tl - 14} (log − esperado = {tl - 14 - te:+d}).")

# fichas do Historian's Boon (Soldier 1/1 por encantamento NÃO-ficha que entra com a Boon em campo; Angel 4/4 por cap. final que dispara com a Boon em campo)
ENTR_BOON = {13: ("Historian's Boon (ela própria)", 1), 14: ("Fenrir (Eldest III) e Cruelty (Starfield); a Eldest foi salva, não reentrou", 2),
             18: ("16 encantamentos devolvidos pela Resurgent Belief (inclui a Boon)", 16)}
SOLD = {i: sum(1 for r in t if r["token"] and r["name"] in ("Knight", "Human Soldier") and r["fromZone"] is None and r["toZone"] == "battlefield") for i, t in enumerate(T, 1)}
ANG = {i: sum(1 for r in t if r["token"] and r["name"] == "Angel" and r["fromZone"] is None and r["toZone"] == "battlefield") for i, t in enumerate(T, 1)}
print("\n| turno | Soldier/Knight esperado (Boon) | fichas Knight/Human Soldier no log | Angel esperado (cap. final com a Boon) | Angel no log |")
print("|---|---|---|---|---|")
for i in (13, 14, 18):
    ang = {13: 0, 14: 2, 18: 0}[i]
    print(f"| T{i} | {ENTR_BOON[i][1]} ({ENTR_BOON[i][0]}) | {SOLD[i]} | {ang} | {ANG[i]} |")
