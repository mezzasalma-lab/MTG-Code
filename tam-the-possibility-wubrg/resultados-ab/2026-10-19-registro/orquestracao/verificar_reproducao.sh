#!/bin/bash
# Refaz as saidas que dependem so' dos dados arquivados e compara byte a byte (cmp). Uso: bash verificar_reproducao.sh
#  Refeitos offline: resumos/analise_estatica.md e resumos/indice_dados.md; e lista.md (regenerada de dados/resolvido.json.xz) contra a lista do repositorio.
#  NAO refeitos offline (consultam APIs ao vivo; o bruto da resposta esta' em dados/): resolve.py (Scryfall), csb_tam.py (Spellbook), o snapshot do EDHREC.
cd "$(dirname "$0")"
ok=0; total=0; tmp=$(mktemp -d)
cmpf () { total=$((total+1)); if cmp -s "$1" "$2"; then echo "IGUAL  $3"; ok=$((ok+1)); else echo "DIFERE $3"; fi; }
python3 analise_estatica.py > "$tmp/a.md";   cmpf "$tmp/a.md" ../resumos/analise_estatica.md "analise_estatica.md (refeita so' dos dados arquivados)"
python3 indice_dados.py > "$tmp/i.md";       cmpf "$tmp/i.md" ../resumos/indice_dados.md "indice_dados.md (refeito so' dos dados arquivados)"
python3 - <<PY > "$tmp/lista_nomes.txt"
import json, lzma, collections
rows = json.load(lzma.open("../dados/resolvido.json.xz", "rt"))
print("\n".join(sorted(f"{x['cat']}|{x['card']['name']}" for x in rows)))
PY
python3 - <<PY > "$tmp/lista_md_nomes.txt"
import re
sec = None; cat = {"terrenos": "Land", "ramp": "Ramp", "compra / valor": "Draw", "remoção": "Removal", "proliferate": "Proliferate", "fichas": "Tokens", "proteção": "Protection", "blink": "Blink", "tutor": "Tutor"}
out = []
for l in open("../../../lista.md", encoding="utf-8"):
    l = l.rstrip("\n")
    if l.startswith("#"):
        h = re.sub(r"\s*\(\d+\).*|\s*\(rochas.*|\s*—.*", "", l.lstrip("# ").strip()).strip().lower(); sec = "Sideboard" if h.startswith("sideboard") else ("Commander{top}" if h.startswith("comandante") else cat.get(h.split(" (")[0], h)); continue
    m = re.match(r"^1 (.+)$", l)
    if m and sec: out.append(f"{sec}|{m.group(1)}")
print("\n".join(sorted(out)))
PY
cmpf "$tmp/lista_nomes.txt" "$tmp/lista_md_nomes.txt" "lista.md (categoria + nome) == o que o Scryfall devolveu para as 113 linhas"
rm -rf "$tmp"
echo "$ok/$total saidas iguais"
