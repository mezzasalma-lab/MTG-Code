"""Verificacao cruzada: a politica 'cega' (variante blunt) deste simulador corrigido deve reproduzir, PARTIDA A PARTIDA, o `early_all`
do harness do Power Depot (resultados-ab/2026-10-03-power-depot), que implementava o mesmo 'tapped primeiro em T1/T2' por monkeypatch,
de forma independente. Compara os campos por partida que existem nos dois brutos (sementes 3_000_000+i, N=10000), variante base
('__base__') do lote early_all do Power Depot contra 'blunt' (Myriad desligado nos dois: o harness antigo nao tinha a habilidade)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
from raw_io import carregar_raw
antigo = carregar_raw(os.path.join(F.DECK, "resultados-ab", "2026-10-03-power-depot", "dados", "raw_ab_powerdepot_10000_early_all"))["__base__"]
novo = carregar_raw(os.path.join(F.HERE, "dados", "raw_ab_10000"))
CAMPOS = ["cmd_turn", "proxy_dmg", "mana_convert", "conversions", "weld", "recursion", "cards_extra", "poison_win", "cmd_dmg_win", "lands_end", "hand", "ramp"]
# 'blunt' liga o Myriad? NAO: blunt = tapped sem skip, Myriad desligado (ver fx_ab.modulo)
b = novo["blunt"]
assert len(antigo) == len(b)
dif = {c: sum(1 for x, y in zip(antigo, b) if x[c] != y[c]) for c in CAMPOS}
iguais = sum(1 for x, y in zip(antigo, b) if all(x[c] == y[c] for c in CAMPOS))
print("N=%d partidas; campos comparados: %s" % (len(b), ", ".join(CAMPOS)))
print("partidas com TODOS os campos iguais: %d/%d" % (iguais, len(b)))
print("partidas diferentes por campo:", dif)
