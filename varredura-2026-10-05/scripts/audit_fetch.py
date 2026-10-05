"""Fetchlands: jogar a fetch no T1 (mao [fetch]) deve (1) sacrifica-la (sai do campo; vai pro cemiterio), (2) buscar de verdade um terreno do tipo certo da biblioteca (biblioteca -1, terreno novo em campo),
(3) pagar 1 de vida quando o oraculo manda (se o simulador rastreia `life`). Mede o que o simulador faz; NAO decide sozinho -- lista pra revisao."""
import sys, os, re, json, random, dataclasses
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
R = os.environ.get("ROOT", "/home/user/MTG-Code")
oc = json.load(open("/home/user/MTG-Code/scryfall-cache/oracle-cache.json"))
SIMS = {"azula-grixis":"azula_goldfish_v1.py","edgar-markov-mardu":"edgar_markov_goldfish_v1.py","hei-bai-wurbg":"heibai_goldfish_v1.py","kutzil-selesnya":"kutzil_goldfish_v1.py","megatron-tyrant-mardu":"megatron_goldfish_v1.py","ms-bumbleflower-bant":"bumbleflower_goldfish_v1.py","nekusar-grixis":"nekusar_goldfish_v1.py","prismatic-bridge-wurbg":"prismatic_bridge_goldfish_v1.py","tom-bombadil-wubrg":"tom_goldfish_v1.py","toph-naya":"toph_goldfish_v1.py","ur-dragon-wurbg":"urdragon_goldfish_v1.py"}
SKIP = {"Urza's Saga", "The World Tree", "Inventors' Fair", "Urza's Cave", "Myriad Landscape"}
def estado(M, hand):
    campos = {f.name for f in dataclasses.fields(M.GameState)}
    kw = {}
    if "rng" in campos: kw["rng"] = random.Random(3)
    lib = list(getattr(M, "BASE_LIBRARY", []) or [])
    if not lib and hasattr(M, "parse_decklist"): lib = list(M.parse_decklist(M.DECKLIST_TEXT))
    lib = [c for c in lib if c in M.CARD_DB and c not in hand]
    if "library" in campos: kw["library"] = lib
    s = M.GameState(**kw); s.turn = 1; s.hand = list(hand); return s
def nomes(s, zona):
    out = []
    for p in getattr(s, zona):
        c = getattr(p, "card", p); out.append(c if isinstance(c, str) else getattr(c, "name", str(c)))
    return out
for d, f in SIMS.items():
    M = A.carrega(f"{R}/{d}/{f}", "audf_" + d.replace("-", "_"), f"{R}/{d}")
    eh = (lambda n: n in M.LAND_NAMES) if hasattr(M, "LAND_NAMES") else (lambda n: bool(M.is_land(n)))
    fetches = []
    for line in open(f"{R}/{d}/lista.md"):
        m = re.match(r"\s*(\d+)\s+(.+?)\s*$", line)
        if not m: continue
        n = m.group(1 + 1); e = oc.get(n) or oc.get(n.split(" // ")[0]) or {}
        if "Land" in e.get("type_line", "") and re.search(r"Search your library for", e.get("oracle_text") or "") and re.search(r"Sacrifice", e.get("oracle_text") or "") and n not in SKIP and n in M.CARD_DB:
            fetches.append(n)
    print(f"== {d}: {len(fetches)} fetch-likes")
    for n in fetches:
        s = estado(M, [n]); lib0 = len(s.library); life0 = getattr(s, "life", getattr(s, "life_total", None))
        try:
            try: M.play_land(s, [])
            except TypeError: M.play_land(s)
        except Exception as ex:
            print(f"   {n:26s} ERRO {type(ex).__name__}: {str(ex)[:80]}"); continue
        bf = nomes(s, "battlefield"); gy = nomes(s, "graveyard")
        life1 = getattr(s, "life", getattr(s, "life_total", None))
        print(f"   {n:26s} fetch ainda em campo={n in bf!s:5s} no cemiterio={n in gy!s:5s} biblioteca {lib0}->{len(s.library)} campo={bf} vida {life0}->{life1}")
