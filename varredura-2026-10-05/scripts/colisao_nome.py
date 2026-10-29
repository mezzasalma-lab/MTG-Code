"""Mede, por deck, quantas vezes um terreno e' marcado 'entrou virado neste turno' POR NOME enquanto OUTRA copia do mesmo nome esta' em campo
(o conjunto `tapped_lands_this_turn` guarda nomes: a marca vale pra TODAS as copias, que somem do total de mana no turno). Uso: python3 colisao_nome.py <deck> <sim.py> <N> [modo]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abgen as A
deck, sim, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
modo = sys.argv[4] if len(sys.argv) > 4 else "padrao"
R = "/home/user/MTG-Code"
m = A.carrega(f"{R}/{deck}/{sim}", "col_" + deck, f"{R}/{deck}")
cfgp = f"{R}/{deck}/resultados-ab/2026-10-05-terreno-virado-primeiro/orquestracao/config.json"
cfg = json.load(open(cfgp)) if os.path.exists(cfgp) else {}
extra = tuple(cfg["extra"]) if cfg.get("extra") is not None else None
turns = cfg.get("turns", 8)
cont = {"adds": 0, "colisoes": 0, "jogos_com_colisao": 0}
nomes_col = {}
def nomes(s):
    return [getattr(c, "name", None) or getattr(getattr(c, "card", None), "name", None) or c for c in s.battlefield]
class CS(set):
    def __init__(self, dono):
        super().__init__(); self.dono = dono
    def add(self, x):
        cont["adds"] += 1
        if not (x in self) and nomes(self.dono).count(x) > 1:
            cont["colisoes"] += 1; nomes_col[x] = nomes_col.get(x, 0) + 1; self.dono._col = True
        super().add(x)
orig = m.GameState.__setattr__
def sa(self, k, v):
    if k == "tapped_lands_this_turn" and isinstance(v, set) and not isinstance(v, CS):
        c = CS(self); c.update(v); v = c
    orig(self, k, v)
m.GameState.__setattr__ = sa
n_col = 0
for sd in range(5_000_000, 5_000_000 + N):
    r = A.chama(m, modo, sd, turns, extra)
    st = r[0] if isinstance(r, tuple) else r
    if getattr(st, "_col", False):
        n_col += 1
print(f"{deck} {modo} N={N}: marcacoes={cont['adds']} colisoes_por_nome={cont['colisoes']} partidas_com_colisao={n_col} nomes={dict(sorted(nomes_col.items(), key=lambda kv: -kv[1])[:6])}")
