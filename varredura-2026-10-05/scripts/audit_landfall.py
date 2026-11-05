"""Auditoria mecanica de LANDFALL: todo terreno que entra em campo (por qualquer caminho) dispara o gatilho de landfall do deck?
Para cada simulador com funcao de landfall: embrulha a funcao (conta chamadas) e a lista `battlefield` (registra cada terreno que entra e a funcao CHAMADORA do append);
um terreno e' 'coberto' se a funcao de landfall roda depois do append e antes do proximo append de terreno. Relatorio por chamador: entradas, cobertas, descobertas.
Uso: python3 audit_landfall.py <N> [modo]"""
import sys, os, json, traceback, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
modo = sys.argv[2] if len(sys.argv) > 2 else "padrao"
R = "/home/user/MTG-Code"
ALVOS = [  # deck, sim, nome da funcao de landfall
    ("beorn-fierce", "beorn_goldfish_v1.py", "on_land_enters"),
    ("prismatic-bridge-wurbg", "prismatic_bridge_goldfish_v1.py", "on_land_enters"),
    ("maralen-sultai", "maralen_goldfish_v1.py", "landfall_trigger"),
    ("toph-naya", "toph_goldfish_v1.py", "landfall"),
]
def nome_de(x):
    return getattr(x, "name", None) or getattr(getattr(x, "card", None), "name", None) or (x if isinstance(x, str) else None)
for deck, sim, fn in ALVOS:
    cfgp = f"{R}/{deck}/resultados-ab/2026-10-05-terreno-virado-primeiro/orquestracao/config.json"
    cfg = json.load(open(cfgp)) if os.path.exists(cfgp) else {}
    extra = tuple(cfg["extra"]) if cfg.get("extra") is not None else None
    turns = cfg.get("turns", 8)
    m = A.carrega(f"{R}/{deck}/{sim}", "lf_" + deck, f"{R}/{deck}")
    eh_terreno = (lambda n: n in m.LAND_NAMES) if hasattr(m, "LAND_NAMES") else (lambda n: bool(m.is_land(n)) if hasattr(m, "is_land") else False)
    estat = collections.defaultdict(lambda: [0, 0])   # chamador -> [entradas, cobertas]
    pend = {"v": None}
    chamadas = {"n": 0}
    orig_fn = getattr(m, fn)
    def wrap(*a, _o=orig_fn, **k):
        chamadas["n"] += 1
        if pend["v"] is not None:
            estat[pend["v"]][1] += 1; pend["v"] = None
        return _o(*a, **k)
    setattr(m, fn, wrap)
    class L(list):
        def append(self, x):
            n = nome_de(x)
            if n is not None and isinstance(n, str) and eh_terreno(n):
                frame = sys._getframe(1)
                ch = frame.f_code.co_name
                if ch != "_reconstruct":   # copia profunda do ensaio a seco do terreno virado (nao e' evento de jogo)
                    estat[ch][0] += 1; pend["v"] = ch
            super().append(x)
    orig = m.GameState.__setattr__
    def sa(self, k, v):
        if k == "battlefield" and not isinstance(v, L):
            v = L(v)
        orig(self, k, v)
    m.GameState.__setattr__ = sa
    for sd in range(5_000_000, 5_000_000 + N):
        pend["v"] = None
        try:
            A.chama(m, modo, sd, turns, extra)
        except Exception as e:
            print("  excecao", sd, type(e).__name__, str(e)[:80]); break
    tot = sum(e for e, c in estat.values())
    print(f"== {deck} ({fn}) {modo} N={N}: entradas de terreno={tot} | chamadas da funcao de landfall={chamadas['n']}")
    for ch, (e, c) in sorted(estat.items(), key=lambda kv: -kv[1][0]):
        print(f"   chamador={ch:32s} entradas={e:5d} (a 1a chamada de landfall depois da entrada cobre so' 1: em laco 'entra tudo, depois dispara' o numero 'cobertas' subestima; compare o TOTAL)")
