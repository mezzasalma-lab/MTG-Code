"""Passo-a-passo (Commander Spellbook) do combo que a troca Teferi's Talent -> Carth the Lion cria com Teferi, Temporal Archmage + The Chain Veil: o laco exige recastar o Teferi da zona de comando, ou nao? (o combo de 2 cartas ja' no deck exige: auditoria.md item 5).
Grava a variante completa em dados/spellbook_carth_variante.json. Uso: python3 csb_carth_detalhe.py <lista.md> <saida.json>   (consulta API ao vivo; o bruto fica arquivado)"""
import json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import csb_base as C
if __name__ == "__main__":
    lista, out = sys.argv[1], sys.argv[2]
    main, side = C.parse(lista); assert len(main) == 99
    d = list(main); assert "Teferi's Talent" in d and "Carth the Lion" not in d; d[d.index("Teferi's Talent")] = "Carth the Lion"
    r = C.query(d)
    achados = [c for c in r["included"] if "Carth the Lion" in C.key(c)]
    assert achados, "o combo do Carth nao apareceu"
    res = []
    for c in achados:
        v = C.http("https://backend.commanderspellbook.com/variants/%s/" % c["id"])
        res.append({"id": c["id"], "combo": C.key(c), "bracketTag": c.get("bracketTag"), "description": v.get("description"), "easyPrerequisites": v.get("easyPrerequisites"), "notablePrerequisites": v.get("notablePrerequisites"),
                    "produces": [p.get("feature", {}).get("name") for p in v.get("produces", [])]})
        print(C.key(c), c["id"], c.get("bracketTag")); print(v.get("description")); print("PRE:", v.get("notablePrerequisites"), v.get("easyPrerequisites"))
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
