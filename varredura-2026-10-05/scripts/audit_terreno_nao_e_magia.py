"""Jogar terreno NAO e' conjurar magia (CR 305.1/601): nenhum contador de magia conjurada/storm pode mudar quando `play_land` joga um terreno comum (nem basico nem nao-basico sem efeito de conjuracao)."""
import sys, os, re, json, random, dataclasses
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
R = os.environ.get("ROOT", "/home/user/MTG-Code")
SIMS = {"azula-grixis":"azula_goldfish_v1.py","beorn-fierce":"beorn_goldfish_v1.py","captain-storm-izzet":"captainstorm_goldfish_v1.py","edgar-markov-mardu":"edgar_markov_goldfish_v1.py","hei-bai-wurbg":"heibai_goldfish_v1.py","kutzil-selesnya":"kutzil_goldfish_v1.py","maralen-sultai":"maralen_goldfish_v1.py","megatron-tyrant-mardu":"megatron_goldfish_v1.py","ms-bumbleflower-bant":"bumbleflower_goldfish_v1.py","nekusar-grixis":"nekusar_goldfish_v1.py","prismatic-bridge-wurbg":"prismatic_bridge_goldfish_v1.py","rat-king-verminister":"ratking_goldfish_v1.py","thranduil-sultai":"thranduil_goldfish_v1.py","tom-bombadil-wubrg":"tom_goldfish_v1.py","toph-naya":"toph_goldfish_v1.py","ulalek-wurbg":"ulalek_goldfish_v1.py","ur-dragon-wurbg":"urdragon_goldfish_v1.py","vihaan-goldwaker-mardu":"vihaan_goldfish_v1.py"}
PAT = re.compile(r"spell|cast|storm", re.I)
def estado(M):
    campos = {f.name for f in dataclasses.fields(M.GameState)}
    kw = {}
    if "rng" in campos: kw["rng"] = random.Random(3)
    lib = list(getattr(M, "BASE_LIBRARY", []) or [])
    if not lib and hasattr(M, "parse_decklist"): lib = list(M.parse_decklist(M.DECKLIST_TEXT))
    if "library" in campos: kw["library"] = [c for c in lib if c in M.CARD_DB][:70]
    s = M.GameState(**kw); s.turn = 1; return s
for d, f in SIMS.items():
    M = A.carrega(f"{R}/{d}/{f}", "aud3_" + d.replace("-", "_"), f"{R}/{d}")
    eh = (lambda n: n in M.LAND_NAMES) if hasattr(M, "LAND_NAMES") else (lambda n: bool(M.is_land(n)))
    candidatos = [n for n in ("Forest", "Island", "Swamp", "Mountain", "Plains", "Command Tower") if n in M.CARD_DB and eh(n)]
    if not candidatos:
        candidatos = [n for n in M.CARD_DB if eh(n) and "//" not in n][:1]
    mudou = {}
    for n in candidatos[:2]:
        s = estado(M); s.hand = [n]
        antes = {k: v for k, v in vars(s).items() if PAT.search(k) and isinstance(v, (int, float)) and not isinstance(v, bool)}
        try: M.play_land(s, [])
        except TypeError: M.play_land(s)
        for k, v in antes.items():
            nv = getattr(s, k)
            if nv != v: mudou[k] = (n, v, nv)
    print(f"{d:26s} contadores de magia/storm alterados por jogar um terreno comum: {mudou or 'nenhum'}")
