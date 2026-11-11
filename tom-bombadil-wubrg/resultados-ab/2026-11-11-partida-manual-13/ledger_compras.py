"""Ledger de compras da partida manual #13 (Tom Bombadil): ESPERADO (se todo gatilho foi resolvido) x LOG.
Uso: python3 -I ledger_compras.py [dados/partida.json.xz]   (saída em Markdown)
Os eventos esperados por turno são LEITURA MINHA do trace (resumos/trace.md) + oráculo/rulings ao vivo + respostas do usuário (2026-11-11), não prova:
 - Compra natural: 1 por turno (T1: mão inicial de 7, confirmada pela foto, + a compra do turno = 8).
 - The First Iroan Games cap. III ("If you control a creature with power 4 or greater, draw two cards"): o marcador natural do T5 (2→3, ação de turno do início da fase principal 1,
   CR 714.3c) dispara o cap. III ANTES de qualquer magia do turno; o Human Soldier do cap. II (3 marcadores +1/+1 no T4) é 4/4 e já cumpre a condição: +2 no T5 (Goldberry, Fertile Ground,
   na ordem do log, antes do Tom ser conjurado).
Nada na lista compra por outra fonte (Goldberry só compra pela 2ª habilidade, que não foi usada)."""
import json, lzma, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(aqui, "dados", "partida.json.xz")
T = json.load(lzma.open(caminho))
LOG = {i: [r["name"].split(" // ")[0] for r in t if r["fromZone"] == "library" and r["toZone"] == "hand"] for i, t in enumerate(T, 1)}
ESP = {
 1: [("mão inicial 7 + compra do turno", 8, "foto: Mulligan (0)")],
 2: [("compra do turno", 1, "")],
 3: [("compra do turno", 1, "")],
 4: [("compra do turno", 1, "")],
 5: [("compra do turno", 1, ""), ("Iroan Games cap. III (Soldier 4/4 já em campo)", 2, "Goldberry e Fertile Ground; ocorre antes do Tom")],
 6: [("compra do turno", 1, "")],
 7: [("compra do turno", 1, "")],
}
print("| turno | esperado | log | diferença (log − esperado) | fontes esperadas | cartas library→mão no log |")
print("|---|---|---|---|---|---|")
te = tl = 0
for i in range(1, len(T) + 1):
    e = sum(n for _, n, _ in ESP.get(i, [])); l = len(LOG[i]); te += e; tl += l
    fontes = "; ".join(f"{f} ×{n}" for f, n, _ in ESP.get(i, []) if n)
    print(f"| T{i} | {e} | {l} | {l - e:+d} | {fontes} | {', '.join(LOG[i])} |")
print(f"\n**Total esperado {te} × log {tl} (log − esperado = {tl - te:+d}).**")
