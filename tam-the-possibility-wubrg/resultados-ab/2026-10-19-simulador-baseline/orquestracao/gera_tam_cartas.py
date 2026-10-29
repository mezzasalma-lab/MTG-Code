"""Gera `tam-the-possibility-wubrg/tam_cartas.json`: custo de mana, tipo, P/T, lealdade e oraculo das 100 cartas do Tam (comandante + 99 de `lista.md`), lidos de `scryfall-cache/oracle-cache.json`
(Regra 14: o cache e' a fonte; o simulador le este recorte e NAO escreve custo/tipo de memoria). Uso: python3 gera_tam_cartas.py  (a partir de qualquer pasta)"""
import json, os, re
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
cache = json.load(open(os.path.join(R, "scryfall-cache", "oracle-cache.json"), encoding="utf-8"))
idx = {}
for k, v in cache.items():
    idx[k] = v
    idx.setdefault(k.split(" // ")[0], v)
txt = open(os.path.join(R, "tam-the-possibility-wubrg", "lista.md"), encoding="utf-8").read()
nomes = ["Tam, the Possibility"] + [m.group(1).strip() for m in re.finditer(r"^1 (.+)$", txt.split("## Deck (99)")[1].split("## Sideboard")[0], re.M)]
assert len(nomes) == 100 and len(set(nomes)) == 100
out = {}
for n in nomes:
    v = idx[n]
    assert v.get("oracle_text") is not None, n
    out[n] = {k: v.get(k) for k in ("mana_cost", "cmc", "type_line", "power", "toughness", "loyalty", "oracle_text", "colors", "color_identity")}
json.dump(out, open(os.path.join(R, "tam-the-possibility-wubrg", "tam_cartas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
print(len(out), "cartas gravadas")
