"""Regra 12 (varredura mecanica): no T1, com campo vazio e mao [terreno], o simulador joga o terreno E o terreno entra virado quando o oraculo manda.
Detecta via delta de `total_mana` (mana disponivel no proprio turno). Esperado (campo vazio, mesa de 4): 'enters tapped.' incondicional -> virado; 'unless you control...' / reveal -> virado;
'unless you have two or more opponents' -> desvirado; choque 'may pay 2 life' -> desvirado (convencao)."""
import sys, os, re, json, random, dataclasses, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
R = os.environ.get("ROOT", "/home/user/MTG-Code")   # ROOT: arvore a auditar (ex.: git archive HEAD = estado ANTES)
oc = json.load(open("/home/user/MTG-Code/scryfall-cache/oracle-cache.json"))
SIMS = {"azula-grixis":"azula_goldfish_v1.py","beorn-fierce":"beorn_goldfish_v1.py","captain-storm-izzet":"captainstorm_goldfish_v1.py","edgar-markov-mardu":"edgar_markov_goldfish_v1.py","hei-bai-wurbg":"heibai_goldfish_v1.py","kutzil-selesnya":"kutzil_goldfish_v1.py","maralen-sultai":"maralen_goldfish_v1.py","megatron-tyrant-mardu":"megatron_goldfish_v1.py","ms-bumbleflower-bant":"bumbleflower_goldfish_v1.py","nekusar-grixis":"nekusar_goldfish_v1.py","prismatic-bridge-wurbg":"prismatic_bridge_goldfish_v1.py","rat-king-verminister":"ratking_goldfish_v1.py","thranduil-sultai":"thranduil_goldfish_v1.py","tom-bombadil-wubrg":"tom_goldfish_v1.py","toph-naya":"toph_goldfish_v1.py","ulalek-wurbg":"ulalek_goldfish_v1.py","ur-dragon-wurbg":"urdragon_goldfish_v1.py","vihaan-goldwaker-mardu":"vihaan_goldfish_v1.py"}

def esperado(txt):
    t = txt.replace("\n", " ")
    if re.search(r"unless you have two or more opponents", t, re.I): return "desvirado"
    if re.search(r"you may pay (\d+) life\. If you don't, it enters tapped", t, re.I): return "desvirado"
    if re.search(r"enters( the battlefield)? tapped", t, re.I) or re.search(r"enter tapped", t, re.I): return "virado"
    return "desvirado"

def estado(M, hand, turn=1):
    campos = {f.name for f in dataclasses.fields(M.GameState)}
    kw = {}
    if "rng" in campos: kw["rng"] = random.Random(3)
    lib = list(getattr(M, "BASE_LIBRARY", []) or [])
    if not lib and hasattr(M, "parse_decklist"): lib = list(M.parse_decklist(M.DECKLIST_TEXT))
    if "library" in campos: kw["library"] = [c for c in lib if c in M.CARD_DB][:70]
    s = M.GameState(**kw); s.turn = turn; s.hand = list(hand); return s

def eh_terreno(M, n):
    return (n in M.LAND_NAMES) if hasattr(M, "LAND_NAMES") else bool(M.is_land(n))

res = {}
for d, f in SIMS.items():
    M = A.carrega(f"{R}/{d}/{f}", "aud_" + d.replace("-", "_"), f"{R}/{d}")
    if not hasattr(M, "total_mana"):
        res[d] = "sem total_mana"; continue
    lands = []
    for line in open(f"{R}/{d}/lista.md"):
        m = re.match(r"\s*(\d+)\s+(.+?)\s*$", line)
        if m: lands.append(m.group(2))
    bad = []; checked = 0; erros = 0
    for n in lands:
        if n not in M.CARD_DB or not eh_terreno(M, n) or "//" in n: continue
        e = oc.get(n) or {}
        txt = e.get("oracle_text") or ""
        if not txt and "Land" not in e.get("type_line", ""): continue
        exp = esperado(txt)
        try:
            s = estado(M, [n])
            m0 = M.total_mana(s)
            try: M.play_land(s, [])
            except TypeError: M.play_land(s)
            m1 = M.total_mana(s)
        except Exception as ex:
            erros += 1; continue
        # terreno sem fonte de mana propria (ex.: so' habilidade) nao entra na comparacao
        produces = getattr(M.CARD_DB[n], "produces", None)
        if produces is not None and len(produces) == 0: continue
        checked += 1
        obs = "virado" if (m1 - m0) <= 0 else "desvirado"
        if obs != exp: bad.append((n, exp, obs))
    res[d] = (checked, erros, bad)
for d, r in res.items():
    if isinstance(r, str): print(f"{d:26s} {r}"); continue
    checked, erros, bad = r
    print(f"{d:26s} terrenos checados={checked} erros={erros} divergencias oraculo x simulador={len(bad)}")
    for n, e, o in bad: print(f"     {n:42s} oraculo(campo vazio)={e:9s} simulador={o}")
