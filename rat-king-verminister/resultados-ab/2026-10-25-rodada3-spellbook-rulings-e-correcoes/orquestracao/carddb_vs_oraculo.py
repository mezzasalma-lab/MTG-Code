"""Compara os DADOS FIXOS do CARD_DB do simulador (mv, ctype, pips_b, base_power, tag 'rat') com o oraculo AO VIVO (dados/scryfall_oraculo_rulings_*.json).
Classe: dado de carta digitado errado / divergente do oraculo (devocao, custo, tipo, poder). Sai com codigo 1 se achar divergencia; imprime quantas cartas checou (>0).
Uso: python3 -I carddb_vs_oraculo.py <deck_dir> <scryfall_oraculo_rulings.json>"""
import json, os, re, sys, importlib.util
deck_dir, jpath = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.chdir(deck_dir); sys.path.insert(0, deck_dir)
spec = importlib.util.spec_from_file_location("sim", os.path.join(deck_dir, "ratking_goldfish_v1.py")); sim = importlib.util.module_from_spec(spec); spec.loader.exec_module(sim)
live = json.load(open(jpath))
def cmc(mc):
    if not mc: return 0
    mc = mc.split(" // ")[0]; t = 0
    for s in re.findall(r"\{([^}]+)\}", mc):
        t += int(s) if s.isdigit() else (0 if s == "X" else 1)
    return t
ctmap = {"Creature": "creature", "Land": "land", "Sorcery": "sorcery", "Instant": "instant", "Artifact": "artifact", "Enchantment": "enchantment"}
def ctype_of(tl):
    front = tl.split(" // ")[0]
    for k in ("Creature", "Land", "Instant", "Sorcery", "Artifact", "Enchantment"):
        if re.search(rf"\b{k}\b", front.split("—")[0]): return ctmap[k]
    return "?"
erros = []; n = 0
for nome, v in live.items():
    if nome == sim.COMMANDER: pass
    key = nome if nome in sim.CARD_DB else None
    if key is None:
        key = next((k for k in sim.CARD_DB if k.split(" // ")[0] == nome.split(" // ")[0]), None)
    if key is None:
        if nome != "Swamp": erros.append((nome, "ausente do CARD_DB"))
        continue
    c = sim.CARD_DB[key]; n += 1
    mc = v["mana_cost"] or ""
    if c.ctype != "land" and c.mv != cmc(mc): erros.append((nome, f"mv sim={c.mv} oraculo={cmc(mc)} ({mc})"))
    ct = ctype_of(v["type_line"])
    if ct != c.ctype: erros.append((nome, f"ctype sim={c.ctype} oraculo={ct} ({v['type_line']})"))
    pb = mc.split(" // ")[0].count("{B}")
    # pips_b so' e' lido pela devocao (Gray Merchant/Nykthos), que soma PERMANENTES: instant/sorcery nunca estao em `battlefield` (falso positivo verificado a mao)
    if c.ctype in ("creature", "artifact", "enchantment", "land") and getattr(c, "pips_b", 0) != pb: erros.append((nome, f"pips_b sim={getattr(c,'pips_b',0)} oraculo={pb} ({mc})"))
    if c.ctype == "creature":
        pw = v["faces"][0].get("power")
        if pw is not None and pw.isdigit() and getattr(c, "base_power", None) != int(pw): erros.append((nome, f"base_power sim={getattr(c,'base_power',None)} oraculo={pw}"))
    is_rat_type = bool(re.search(r"\bRat\b", v["type_line"].split(" // ")[0].split("—")[-1])) and ctype_of(v["type_line"]) == "creature"
    if ("rat" in c.tags) != is_rat_type: erros.append((nome, f"tag 'rat' sim={'rat' in c.tags} oraculo(type_line Rat)={is_rat_type}"))
print(f"cartas checadas contra o oraculo ao vivo: {n} (>0) | divergencias: {len(erros)}")
for e in erros: print("  DIVERGE:", e[0], "->", e[1])
sys.exit(1 if erros else 0)
