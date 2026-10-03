"""A/B pareado das tres correcoes do Sephiroth no simulador do Vihaan (emblema acumulavel, mortes simultaneas em wipe, contador por turno).
Variantes (mesma semente em todas = pareado; ANTES = commit ba74496, ja' com Treasure animado/mulligan/tapped corrigidos):
  antes         simulador ANTES (codigo/vihaan_goldfish_v1_ANTES_ba74496.py)
  emblema       DEPOIS, so' o emblema acumulavel (emblema + frente = 2 gatilhos; 2a virada = 2o emblema)
  simultaneas   DEPOIS, so' as mortes simultaneas em wipe (lote: o Sephiroth enxerga todas, em qualquer ordem; nao vira)
  fronteira     DEPOIS, so' o contador 'este turno' zerado nos turnos de oponente e na reentrada
  todas         DEPOIS, as tres correcoes (e' o simulador que fica no repositorio)
Uso: [FX_MODO=resiliencia] python3 fx_ab.py LOTE [--sum]   LOTE = 2000 (sementes 1_000_000+i) | 10000 (sementes 3_000_000+i)"""
import math, os, statistics as st, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
from raw_io import salvar_raw, carregar_raw

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
LOTE = int(ARGS[0]) if ARGS else 2000
SEED0 = {2000: 1_000_000, 10000: 3_000_000}.get(LOTE, 3_000_000)
SEEDS = list(range(SEED0, SEED0 + LOTE))
MODO = os.environ.get("FX_MODO", "padrao")
RAW = os.path.join(F.HERE, "dados", "raw_ab_%d%s" % (LOTE, "" if MODO == "padrao" else "_" + MODO))
VARIANTES = ["antes", "emblema", "simultaneas", "fronteira", "todas"]
TURNS = 8


def modulo(nome):
    pid = os.getpid()
    if nome == "antes":
        return F.carrega(F.ANTES, "vih_antes_%d" % pid)
    m = F.carrega(F.DEPOIS, "vih_depois_%d_%s" % (pid, nome))
    return F.flags(m, emblema=nome in ("emblema", "todas"), simultaneas=nome in ("simultaneas", "todas"), fronteira=nome in ("fronteira", "todas"))


def run_variant(nome):
    V = modulo(nome)
    fn = V.simulate_one if MODO == "padrao" else V.simulate_one_with_interaction
    out = []
    for sd in SEEDS:
        s = fn(sd, TURNS)
        out.append({"win_turn": s.win_turn, "drain": s.drain_damage_total, "table_dmg": s.table_damage_total, "combat": s.combat_damage_proxy_total,
                    "creature_deaths": s.creature_deaths_total, "life_gained": s.life_gained_total, "treasures": s.treasures_created_total,
                    "flipped": 1 if s.has_super_nova_emblem else 0, "emblems": getattr(s, "super_nova_emblems", 1 if s.has_super_nova_emblem else 0),
                    "extra": getattr(s, "sephiroth_extra_triggers_total", 0), "fp": F.impressao(s)[:12]})
    return nome, out


def vec(rs):
    return {"win8": [1.0 if (r["win_turn"] and r["win_turn"] <= TURNS) else 0.0 for r in rs],
            "table": [float(r["table_dmg"]) for r in rs], "drain": [float(r["drain"]) for r in rs], "life": [float(r["life_gained"]) for r in rs],
            "deaths": [float(r["creature_deaths"]) for r in rs], "treas": [float(r["treasures"]) for r in rs],
            "flip": [float(r["flipped"]) for r in rs], "emb": [float(r["emblems"]) for r in rs], "extra": [float(r["extra"]) for r in rs]}


def ci(a, b):
    d = [y - x for x, y in zip(a, b)]
    return st.mean(d), 1.96 * st.stdev(d) / math.sqrt(len(d)) if len(set(d)) > 1 else 0.0


def tabela(bruto):
    res = {k: vec(v) for k, v in bruto.items()}
    base = res["antes"]
    n = len(bruto["antes"])
    print("LOTE N=%d sementes %d..%d, %d turnos, %s" % (n, SEED0, SEED0 + n - 1, TURNS,
          "modo padrao (goldfish)" if MODO == "padrao" else "modo resiliencia (oponente esperto, simulate_one_with_interaction)"))
    print("ANTES: win<=T8 %.1f%% | Sephiroth virou (emblema) em %.2f%% dos jogos | emblemas/jogo %.4f | dano mesa %.2f drain %.2f vida ganha %.2f mortes de criatura %.2f Treasures %.2f" % (
        100 * st.mean(base["win8"]), 100 * st.mean(base["flip"]), st.mean(base["emb"]), st.mean(base["table"]), st.mean(base["drain"]),
        st.mean(base["life"]), st.mean(base["deaths"]), st.mean(base["treas"])))
    cols = ("win8", "flip", "emb", "table", "drain", "life", "deaths", "treas")
    cab = ("win<=8 pp", "virou pp", "emblemas", "dano mesa", "drain", "vida ganha", "mortes cria.", "Treasures")
    print("%-12s " % "variante" + " ".join("%-14s" % c for c in cab))
    for nome in VARIANTES[1:]:
        r = res[nome]
        linha = []
        for c in cols:
            m, h = ci(base[c], r[c])
            f = 100 if c in ("win8", "flip") else 1
            linha.append("%+7.3f±%-6.3f" % (f * m, f * h))
        print("%-12s " % nome + " ".join("%-14s" % x for x in linha))
    print()
    print("%-12s %-13s %-30s %-24s" % ("variante", "jogos iguais", "jogos com gatilho extra do emblema", "gatilhos extras/jogo"))
    for nome in VARIANTES[1:]:
        rs, ra = bruto[nome], bruto["antes"]
        iguais = sum(1 for x, y in zip(ra, rs) if x["fp"] == y["fp"])
        print("%-12s %5.2f%%        %-30d %-24.5f" % (nome, 100 * iguais / n, sum(1 for r in rs if r["extra"]), st.mean([r["extra"] for r in rs])))


if __name__ == "__main__":
    if "--sum" in sys.argv:
        bruto = carregar_raw(RAW)
    else:
        with Pool(4) as p:
            bruto = dict(p.map(run_variant, VARIANTES))
        salvar_raw(RAW, bruto)
    tabela(bruto)
