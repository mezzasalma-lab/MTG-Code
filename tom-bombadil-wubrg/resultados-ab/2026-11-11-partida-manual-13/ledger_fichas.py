"""Ledger de fichas da partida manual #13 (Tom Bombadil): ESPERADO pelo oráculo x LOG, por turno.
Uso: python3 -I ledger_fichas.py [dados/partida.json.xz]   (saída em Markdown)
Historian's Boon (oráculo no scryfall-cache): "Whenever this enchantment or another nontoken enchantment you control enters, create a 1/1 white Soldier creature token. /
Whenever the final chapter ability of a Saga you control TRIGGERS, create a 4/4 white Angel creature token with flying and vigilance." O Angel depende de o capítulo final DISPARAR,
não de a Saga ser sacrificada (a ruling do Tom de 2023-06-16 distingue "triggers" de "resolves").
Eventos esperados = LEITURA MINHA do trace + oráculo + respostas do usuário (2026-11-11): é isto que o script compara com o log; não é prova do que aconteceu na mesa.
 T3: Iroan Games entra (Boon ainda na mão): cap. I = Human Soldier 1/1 (da Saga, não da Boon). T4: cap. II = 3 marcadores +1/+1 (sem ficha).
 T5: Boon entra (vê a si mesma: Soldier); Satsuki põe o 4º marcador na Iroan (cap. IV dispara: ANGEL da Boon; resolve: Gold); Iroan é sacrificada (CR 714.4); o Tom dispara e traz a
     There and Back Again (encantamento não-ficha entrando: 2º SOLDIER); cap. I: o Anel tenta.
 T6: Fertile Ground (Aura, encantamento não-ficha: Soldier) e Summon: Yojimbo (Saga encantamento-criatura: Soldier).
 T7: cap. III da There and Back Again dispara (ANGEL da Boon) e resolve (Smaug); o Tom dispara e traz Binding the Old Gods (Soldier)."""
import collections, json, lzma, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(aqui, "dados", "partida.json.xz")
T = json.load(lzma.open(caminho))
ESP = {  # turno -> {ficha: quantidade}
 3: {"Human Soldier": 1},
 5: {"Human Soldier": 2, "Angel": 1, "Gold": 1},
 6: {"Human Soldier": 2},
 7: {"Human Soldier": 1, "Angel": 1, "Smaug": 1},
}
RELEVANTES = ("Human Soldier", "Angel", "Gold", "Smaug")
print("| turno | ficha | esperado | log | log − esperado |")
print("|---|---|---|---|---|")
falt = []
for ti, t in enumerate(T, 1):
    c = collections.Counter(r["name"] for r in t if r["token"] and r["fromZone"] is None and r["toZone"] == "battlefield" and r["name"] in RELEVANTES)
    for f in RELEVANTES:
        e = ESP.get(ti, {}).get(f, 0)
        if e or c.get(f, 0):
            d = c.get(f, 0) - e
            print(f"| T{ti} | {f} | {e} | {c.get(f, 0)} | {d:+d} |")
            if d:
                falt.append((ti, f, d))
print("\nDiferenças (turno, ficha, log − esperado):", falt or "nenhuma")
