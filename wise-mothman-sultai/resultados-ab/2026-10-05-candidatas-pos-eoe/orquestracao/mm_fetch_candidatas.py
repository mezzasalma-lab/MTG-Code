"""Baixa TODAS as impressoes legais em Commander, dentro da identidade Sultai (id<=bug), de colecoes com data >= 2025-08-01 (Edge of Eternities em diante).
Grava o bruto (todas as impressoes) e um indice por oracle_id. Uso: python3 mm_fetch_candidatas.py <saida_dir>"""
import json, sys, time, os, urllib.parse
sys.path.insert(0, "/home/user/MTG-Code/scryfall-cache/sets")
import fetch_set as F
saida = sys.argv[1]
os.makedirs(saida, exist_ok=True)
Q = "f:commander id<=bug date>=2025-08-01"
url = "https://api.scryfall.com/cards/search?" + urllib.parse.urlencode({"q": Q, "unique": "prints", "order": "set", "include_extras": "false"})
prints, n = [], 0
while url:
    d = F.get(url)
    prints += d["data"]
    n += 1
    url = d.get("next_page")
    time.sleep(0.12)
print("query:", Q, "| paginas:", n, "| impressoes:", len(prints), "| total_cards reportado:", d.get("total_cards"))
json.dump({"query": Q, "impressoes": prints}, open(os.path.join(saida, "candidatas_impressoes_bruto.json"), "w", encoding="utf-8"), ensure_ascii=False)
