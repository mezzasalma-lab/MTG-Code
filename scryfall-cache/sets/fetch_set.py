"""
Baixa uma colecao inteira do Scryfall, grava todas as cartas no
`scryfall-cache/oracle-cache.json` e gera a lista legivel do set
(`<slug>.md` + `<slug>.json`) nesta pasta.

Uso (a partir da raiz do repositorio):
    python3 scryfall-cache/sets/fetch_set.py fra frc --slug fra-reality-fracture

Regras do cache (references/user-standing-rules.md, Regras 14 e 15):
- entrada nova -> grava;
- entrada existente com `oracle_text` vazio -> preenche;
- entrada existente cujo `set` e' um dos sets baixados agora -> atualiza
  (spoiler de colecao nao lancada ainda pode mudar de texto);
- entrada existente de outro set (reimpressao) com oraculo -> mantem.

Colecao ainda nao lancada: rodar de novo antes de qualquer analise com
cartas dela, a lista cresce enquanto o spoiler anda.
"""
import argparse
import datetime
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, "scryfall-cache", "oracle-cache.json")
OUT_DIR = os.path.join(ROOT, "scryfall-cache", "sets")
H = {"User-Agent": "mtg-code-cache/1.0", "Accept": "application/json"}
FIELDS = ["cmc", "collector_number", "color_identity", "colors", "keywords", "legalities", "loyalty", "mana_cost", "name",
          "oracle_text", "power", "prices", "released_at", "scryfall_uri", "set", "toughness", "type_line"]

# Notas escritas a mao por set (mecanicas novas), lidas do oraculo real.
NOTES = {
    "fra": """\
- **Empower Jace N** (35 cartas entre FRA/FRC): poe N marcadores de lealdade num
  token de Jace que voce controla; se nao controla nenhum, primeiro cria um
  token planeswalker azul "Jace" com `[-1]: Surveil 1` e `[-3]: Draw a card`.
  Todo "empower" do set e' de Jace. O ciclo **Way of the ...** (10 encantamentos
  lendarios) da' empower Jace no ETB + um estatico que conversa com
  habilidades de lealdade.
- **Prepared** (cartas de 2 faces criatura // magica): a criatura "enters
  prepared"; enquanto preparada voce pode conjurar uma COPIA da magica da
  outra face (isso a despreparada).
- **Behold um Jace** (ex.: Theorist's Sanctum): escolher um Jace que voce
  controla ou revelar um card de Jace da mao.
- **Ciclo de terrenos Commons / Annex** (10 duais, 1 por par de cores):
  "enters tapped unless you control a planeswalker".
""",
}


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H)))


def search(q, unique):
    url = "https://api.scryfall.com/cards/search?" + urllib.parse.urlencode(
        {"q": q, "unique": unique, "order": "set", "include_extras": "false"})
    out = []
    while url:
        d = get(url)
        out += d["data"]
        url = d.get("next_page")
        time.sleep(0.12)
    return out


def entry(c):
    e = {k: c.get(k) for k in FIELDS}
    faces = c.get("card_faces")
    if faces and not (c.get("oracle_text") or "").strip():
        e["oracle_text"] = "\n // \n".join(f"{f['name']} ({f.get('mana_cost', '')}): {f.get('oracle_text', '')}" for f in faces)
        if not e["mana_cost"]:
            e["mana_cost"] = " // ".join(f.get("mana_cost", "") for f in faces)
        for k in ("power", "toughness", "loyalty", "type_line"):
            if e[k] is None:
                e[k] = faces[0].get(k)
    if faces:
        e["card_faces"] = [{"name": f["name"], "mana_cost": f.get("mana_cost", ""), "type_line": f.get("type_line"),
                            "oracle_text": f.get("oracle_text", ""), "power": f.get("power"), "toughness": f.get("toughness"),
                            **({"loyalty": f["loyalty"]} if f.get("loyalty") else {})} for f in faces]
    return e


def pw_related(e):
    if "Planeswalker" in (e["type_line"] or ""):
        return False
    t = (e["oracle_text"] or "").lower()
    return "planeswalker" in t or "loyalty" in t


def md_escape(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def oracle_block(e):
    lines = [f"**{e['name']}** {e['mana_cost'] or ''} — {e['type_line']}"
             + (f" — lealdade {e['loyalty']}" if e.get("loyalty") else "")
             + (f" — {e['power']}/{e['toughness']}" if e.get("power") is not None else "")]
    lines += ["> " + ln for ln in (e["oracle_text"] or "").split("\n")]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sets", nargs="+")
    ap.add_argument("--slug", required=True)
    a = ap.parse_args()
    codes = [s.lower() for s in a.sets]

    cache = json.load(open(CACHE, encoding="utf-8"))
    added = filled = updated = kept = 0
    data = {}
    for code in codes:
        meta = get(f"https://api.scryfall.com/sets/{code}")
        cards = search(f"e:{code}", "cards")
        prints = search(f"e:{code}", "prints")
        rows = []
        for c in cards:
            e = entry(c)
            old = cache.get(c["name"])
            if old is None:
                cache[c["name"]] = e
                added += 1
            elif not (old.get("oracle_text") or "").strip():
                if old != e:
                    filled += 1
                cache[c["name"]] = e
            elif old.get("set") in codes:
                if old != e:
                    updated += 1
                cache[c["name"]] = e
            else:
                kept += 1
            rows.append({"collector_number": c["collector_number"], "name": c["name"], "mana_cost": e["mana_cost"],
                         "type_line": e["type_line"], "rarity": c.get("rarity"), "reprint": c.get("reprint", False),
                         "loyalty": e.get("loyalty"), "planeswalker": "Planeswalker" in (e["type_line"] or ""),
                         "pw_related": pw_related(e)})
        data[code] = {"name": meta["name"], "released_at": meta.get("released_at"), "set_type": meta.get("set_type"),
                      "printings": len(prints), "cards": rows}
        print(f"{code}: {meta['name']} | {len(cards)} cartas unicas | {len(prints)} impressoes")

    with open(CACHE, "w", encoding="utf-8") as f:
        f.write(json.dumps(cache, indent=2, ensure_ascii=False) + "\n")
    print(f"cache: +{added} novas | {filled} preenchidas | {updated} atualizadas (texto mudou) | "
          f"{kept} reimpressoes mantidas | total {len(cache)}")

    today = datetime.date.today().isoformat()
    with open(os.path.join(OUT_DIR, a.slug + ".json"), "w", encoding="utf-8") as f:
        json.dump({"fetched_at": today, **data}, f, indent=1, ensure_ascii=False)
        f.write("\n")

    out = [f"# {' + '.join(d['name'] for d in data.values())}\n",
           f"Gerado por `scryfall-cache/sets/fetch_set.py {' '.join(codes)} --slug {a.slug}` em {today}, "
           "direto da API do Scryfall. Todas as cartas abaixo estao no `scryfall-cache/oracle-cache.json`.\n"]
    for code, d in data.items():
        if d["released_at"] and d["released_at"] > today:
            out.append(f"> **{code.upper()} ainda nao lancou** (lancamento {d['released_at']}): lista de spoiler, pode crescer "
                       "e o texto pode mudar. Rodar o script de novo antes de analisar cartas deste set.\n")
            break
    out.append("| Set | Nome | Tipo | Lancamento | Cartas unicas | Impressoes | Reimpressoes | Planeswalkers | Outras que citam planeswalker/lealdade |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for code, d in data.items():
        rows = d["cards"]
        out.append(f"| {code.upper()} | {d['name']} | {d['set_type']} | {d['released_at']} | {len(rows)} | {d['printings']} | "
                   f"{sum(r['reprint'] for r in rows)} | {sum(r['planeswalker'] for r in rows)} | {sum(r['pw_related'] for r in rows)} |")
    out.append("")
    for code in codes:
        if code in NOTES:
            out += [f"## Mecanicas novas ({code.upper()})\n", NOTES[code]]
    for code, d in data.items():
        rows = d["cards"]
        out.append(f"## {code.upper()} — {d['name']}\n")
        out.append("### Planeswalkers\n")
        for r in rows:
            if r["planeswalker"]:
                out.append(oracle_block(cache[r["name"]]) + ("*(reimpressao)*\n" if r["reprint"] else ""))
        rel = [r for r in rows if r["pw_related"]]
        if rel:
            out.append("### Outras cartas que citam planeswalker/lealdade\n")
            for r in rel:
                out.append(oracle_block(cache[r["name"]]) + ("*(reimpressao)*\n" if r["reprint"] else ""))
        out.append("### Lista completa\n")
        out.append("| # | Carta | Custo | Tipo | Raridade | Reimpressao |")
        out.append("|---|---|---|---|---|---|")
        key = lambda r: (int(re.sub(r"\D", "", r["collector_number"]) or 0), r["collector_number"])
        for r in sorted(rows, key=key):
            out.append(f"| {r['collector_number']} | {md_escape(r['name'])} | {md_escape(r['mana_cost'])} | "
                       f"{md_escape(r['type_line'])} | {r['rarity']} | {'sim' if r['reprint'] else ''} |")
        out.append("")
    with open(os.path.join(OUT_DIR, a.slug + ".md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("escrito:", a.slug + ".md", "+", a.slug + ".json")


if __name__ == "__main__":
    main()
