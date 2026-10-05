"""Regra 12, 2o cenario: terrenos com condicao 'unless you control ...' / reveal: com a condicao SATISFEITA entram desvirados; com ela VIOLADA (a 1 passo do limite) entram virados.
Mede por delta de total_mana; so' decks com total_mana. Padroes cobertos: 'unless you control a/an X or Y' (tipos de terreno basico), 'unless you control two or more other lands',
'unless you control two or fewer other lands', 'unless you control two or more basic lands', 'unless you control a basic land', 'you may reveal a/an X or Y card from your hand'."""
import sys, os, re, json, random, dataclasses
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
R = os.environ.get("ROOT", "/home/user/MTG-Code")   # ROOT: arvore a auditar (ex.: git archive HEAD = estado ANTES)
oc = json.load(open("/home/user/MTG-Code/scryfall-cache/oracle-cache.json"))
SIMS = {"azula-grixis":"azula_goldfish_v1.py","beorn-fierce":"beorn_goldfish_v1.py","captain-storm-izzet":"captainstorm_goldfish_v1.py","edgar-markov-mardu":"edgar_markov_goldfish_v1.py","hei-bai-wurbg":"heibai_goldfish_v1.py","kutzil-selesnya":"kutzil_goldfish_v1.py","maralen-sultai":"maralen_goldfish_v1.py","megatron-tyrant-mardu":"megatron_goldfish_v1.py","ms-bumbleflower-bant":"bumbleflower_goldfish_v1.py","nekusar-grixis":"nekusar_goldfish_v1.py","prismatic-bridge-wurbg":"prismatic_bridge_goldfish_v1.py","rat-king-verminister":"ratking_goldfish_v1.py","thranduil-sultai":"thranduil_goldfish_v1.py","tom-bombadil-wubrg":"tom_goldfish_v1.py","toph-naya":"toph_goldfish_v1.py","ulalek-wurbg":"ulalek_goldfish_v1.py","ur-dragon-wurbg":"urdragon_goldfish_v1.py","vihaan-goldwaker-mardu":"vihaan_goldfish_v1.py"}
BASIC = {"Plains": "Plains", "Island": "Island", "Swamp": "Swamp", "Mountain": "Mountain", "Forest": "Forest"}

def estado(M, hand, bf, turn=3):
    campos = {f.name for f in dataclasses.fields(M.GameState)}
    kw = {}
    if "rng" in campos: kw["rng"] = random.Random(3)
    lib = list(getattr(M, "BASE_LIBRARY", []) or [])
    if not lib and hasattr(M, "parse_decklist"): lib = list(M.parse_decklist(M.DECKLIST_TEXT))
    if "library" in campos: kw["library"] = [c for c in lib if c in M.CARD_DB][:70]
    s = M.GameState(**kw); s.turn = turn; s.hand = list(hand)
    for n in bf:
        poe(M, s, n)
    return s

def poe(M, s, n):
    """poe um terreno em campo (desvirado) usando o formato do deck"""
    if hasattr(M, "mk_perm"):
        try:
            p = M.mk_perm(s, n)
        except TypeError:
            p = M.mk_perm(n)
        if hasattr(p, "tapped"): p.tapped = False
        s.battlefield.append(p)
    elif hasattr(M, "Permanent"):
        s.battlefield.append(M.Permanent(card=n, uid=len(s.battlefield) + 100, entered_turn=0))
    else:
        s.battlefield.append(n)

def delta(M, n, hand_extra, bf):
    s = estado(M, [n] + list(hand_extra), bf)
    m0 = M.total_mana(s)
    try: M.play_land(s, [])
    except TypeError: M.play_land(s)
    return M.total_mana(s) - m0

def basics_in(M, k):
    out = [b for b in BASIC if b in M.CARD_DB]
    return out

for d, f in SIMS.items():
    M = A.carrega(f"{R}/{d}/{f}", "aud2_" + d.replace("-", "_"), f"{R}/{d}")
    if not hasattr(M, "total_mana"): print(f"{d}: sem total_mana"); continue
    nomes = []
    for line in open(f"{R}/{d}/lista.md"):
        m = re.match(r"\s*(\d+)\s+(.+?)\s*$", line)
        if m: nomes.append(m.group(2))
    falhas = []; ok = 0; pulados = 0
    eh = (lambda n: n in M.LAND_NAMES) if hasattr(M, "LAND_NAMES") else (lambda n: bool(M.is_land(n)))
    for n in nomes:
        if n not in M.CARD_DB or not eh(n) or "//" in n: continue
        t = ((oc.get(n) or {}).get("oracle_text") or "").replace("\n", " ")
        casos = []   # (descricao, mao_extra, campo, esperado)
        mt = re.search(r"enters tapped unless you control an? ([A-Z][a-z]+)(?: or an? ([A-Z][a-z]+))?(?: or an? ([A-Z][a-z]+))?\.", t)
        if mt and all(x in BASIC for x in mt.groups() if x):
            tipos = [x for x in mt.groups() if x]
            casos.append((f"sem {'/'.join(tipos)} em campo", [], [], "virado"))
            for x in tipos:
                if x in M.CARD_DB: casos.append((f"com {x} em campo", [], [x], "desvirado"))
        mt = re.search(r"enters tapped unless you control two or more other lands", t)
        if mt:
            casos.append(("1 outro terreno", [], ["Island"], "virado")); casos.append(("2 outros terrenos", [], ["Island", "Island"], "desvirado"))
        mt = re.search(r"enters tapped unless you control two or fewer other lands", t)
        if mt:
            casos.append(("2 outros terrenos", [], ["Island", "Island"], "desvirado")); casos.append(("3 outros terrenos", [], ["Island", "Island", "Island"], "virado"))
        mt = re.search(r"enters tapped unless you control two or more basic lands", t)
        if mt:
            casos.append(("1 basico", [], ["Island"], "virado")); casos.append(("2 basicos", [], ["Island", "Island"], "desvirado"))
        mt = re.search(r"enters tapped unless you control a basic land", t)
        if mt:
            casos.append(("sem basico", [], [], "virado")); casos.append(("1 basico", [], ["Island"], "desvirado"))
        mt = re.search(r"you may reveal an? ([A-Z][a-z]+)(?: or an? ([A-Z][a-z]+))? card from your hand\. If you don't, this land enters tapped", t)
        if mt:
            tipos = [x for x in mt.groups() if x]
            casos.append(("sem revelar (mao so' o terreno)", [], [], "virado"))
            for x in tipos:
                if x in M.CARD_DB: casos.append((f"revela {x}", [x], [], "desvirado"))
        for desc, hx, bf, exp in casos:
            if any(b not in M.CARD_DB for b in bf + hx): pulados += 1; continue
            try:
                dm = delta(M, n, hx, bf)
            except Exception as ex:
                falhas.append((n, desc, exp, f"ERRO {type(ex).__name__}")); continue
            obs = "virado" if dm <= 0 else "desvirado"
            if obs == exp: ok += 1
            else: falhas.append((n, desc, exp, obs))
    print(f"{d:26s} cenarios ok={ok} pulados={pulados} FALHAS={len(falhas)}")
    for n, desc, exp, obs in falhas: print(f"     {n:34s} [{desc}] oraculo={exp} simulador={obs}")
