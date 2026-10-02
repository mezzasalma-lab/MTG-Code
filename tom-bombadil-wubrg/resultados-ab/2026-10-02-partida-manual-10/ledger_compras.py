"""Conta das compras por turno da partida #10: ESPERADO pelo oráculo (motores de compra de encantamento) x LOG (library→mão).
Os eventos de cada turno foram lidos à mão do `resumos/trace.md` (suposições abaixo); o lado "log" sai do JSON.
Motores: Enchantress's Presence (T4+, ao CONJURAR encantamento), Femeref (T5+, encantamento vai ao cemitério vindo do campo),
Eidolon of Blossoms (T7+, ao ENTRAR encantamento, inclusive ele mesmo), Sythis (T10+, ao CONJURAR encantamento), Setessan Champion (T12+, ao ENTRAR encantamento).
Suposições: entradas duplicadas do mesmo id no mesmo turno são desfazer/refazer (1 jogada real); Femeref e Eidolon vivos desde que entraram."""
import json
import lzma
import os
aqui = os.path.dirname(os.path.abspath(__file__))
T = json.load(lzma.open(os.path.join(aqui, "dados", "partida.json.xz")))
obs = [sum(1 for e in t if e["fromZone"] == "library" and e["toZone"] == "hand") for t in T]
# (descrição, quantidade) por turno
ESP = {
    1: [("compra do turno (a mão da foto + 1)", 1)],
    2: [("compra do turno", 1)], 3: [("compra do turno", 1)], 4: [("compra do turno (a Presence entra sem compra)", 1)],
    5: [("compra do turno", 1), ("Presence: Fertile Ground conjurada", 1)],
    6: [("compra do turno", 1)],
    7: [("compra do turno", 1), ("Presence: Eidolon conjurado", 1), ("Eidolon: ele mesmo entra", 1)],
    8: [("compra do turno", 1)],
    9: [("compra do turno", 1), ("Presence: Starfield conjurada", 1), ("Eidolon: Starfield entra", 1)],
    10: [("compra do turno", 1), ("Eidolon: Bath Song volta pela Starfield", 1), ("Bath Song I (compre 2)", 2),
         ("Presence + Eidolon: Resourceful Defense", 2), ("Presence + Eidolon: Sythis (ela mesma não compra)", 2),
         ("Presence + Sythis + Eidolon: Sanctum Weaver", 3)],
    11: [("compra do turno", 1), ("Eidolon: Summon: Knights volta pela Starfield", 1), ("Bath Song II (compre 2)", 2),
         ("Presence + Sythis + Eidolon: The Kami War", 3), ("Femeref: Casualties of War manda Knights, Fertile Ground e Utopia Sprawl ao cemitério", 3)],
    12: [("compra do turno", 1), ("Femeref: Bath Song sacrificada depois do cap. III", 1), ("Eidolon: Knights volta pela Starfield", 1),
         ("Eidolon: The First Iroan Games entra pelo Tom", 1), ("Presence + Sythis + Eidolon: Prismatic Omen", 3),
         ("Presence + Sythis + Eidolon: Estrid's Invocation", 3)],
    13: [("compra do turno", 1), ("Eidolon + Champion: ITDBT volta (Starfield)", 2), ("Eidolon + Champion: Primal Odin volta (cópia da Starfield pela Estrid)", 2),
         ("Eidolon + Champion: Estrid volta no upkeep", 2), ("Presence + Sythis + Eidolon + Champion: Summon: Bahamut", 4),
         ("Presence + Sythis + Eidolon + Champion: Jugan Defends the Temple", 4)],
}
print("| turno | esperado | log (library→mão) | diferença | composição do esperado |")
print("|---|---|---|---|---|")
tot_e = tot_o = 0
for i in range(1, 14):
    e = sum(q for _, q in ESP[i])
    o = obs[i - 1] - (1 if i == 1 else 0) + (1 if i == 1 else 0)
    if i == 1:
        e, o = 8, obs[0]     # mão da foto (7) + compra do turno
    tot_e += e
    tot_o += o
    comp = "; ".join(f"{d} ({q})" for d, q in ESP[i]) if i > 1 else "7 da foto + 1 compra"
    print(f"| T{i} | {e} | {o} | {'**' if o != e else ''}{o - e:+d}{'**' if o != e else ''} | {comp} |")
print(f"\nTotal: esperado {tot_e}, log {tot_o}, diferença {tot_o - tot_e:+d}")
