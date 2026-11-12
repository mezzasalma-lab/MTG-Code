"""CR 611.2c: so' os Treasures que existem quando a habilidade do Vihaan resolve viram criatura. Checa, por id, se algum Treasure VIRADO
(atacante marcado) foi criado DEPOIS do primeiro toque de Treasure do turno. Uso: python3 atacantes_vs_criacao.py ../dados/partida.json.xz"""
import json, lzma, sys
d = json.load(lzma.open(sys.argv[1], "rt"))
for n, t in enumerate(d, 1):
    primeiro_tap = next((i for i, r in enumerate(t) if r["token"] and r["tapped"] and r["fromZone"] is None and r["toZone"] is None), None)
    criadas = {r["id"]: i for i, r in enumerate(t) if r["token"] and r["fromZone"] is None and r["toZone"] == "battlefield"}
    viradas = {r["id"] for r in t if r["token"] and r["tapped"] and r["fromZone"] is None and r["toZone"] is None}
    viol = [i for i, idx in criadas.items() if i in viradas and primeiro_tap is not None and idx > primeiro_tap]
    print("T%d: viradas=%d criadas no turno=%d | virada que foi criada DEPOIS do primeiro toque de ficha: %s" % (n, len(viradas), len(criadas), viol))
