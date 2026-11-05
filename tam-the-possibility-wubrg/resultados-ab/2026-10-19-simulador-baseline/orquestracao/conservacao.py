"""Invariante de CONSERVACAO de cartas (mais forte que a 'carta acima do baralho' do abgen): no fim de cada partida, cada carta nao-ficha da lista aparece EXATAMENTE a quantidade que tem em BASE_LIBRARY
somando mao + biblioteca + cemiterio + exilio + exilio de impulso (Chandra) + devolucao pendente + campo (nao-ficha). Excecoes declaradas: partida que acabou com magia no ar (game_over: a magia que
disparou o fim nunca resolve) e partida em que a Aminatou -6 entregou permanentes a um oponente (saem do jogo de verdade). 'A mais' = duplicacao de zona; 'a menos' = carta que sumiu.
Uso: python3 conservacao.py [N] [seed0]   (2 modos, 4 processos)"""
import os, sys, collections
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import abgen as A
from multiprocessing import Pool
DECK = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SIM = os.path.join(DECK, "tam_goldfish_v1.py")


def job(args):
    modo, seeds, k = args
    m = A.carrega(SIM, f"cons_{modo}_{k}", DECK)
    base = collections.Counter(m.BASE_LIBRARY)
    mais, menos, exc, ex = collections.Counter(), collections.Counter(), collections.Counter(), {}
    for sd in seeds:
        try:
            s = A.chama(m, modo, sd, 12)
        except Exception as e:
            exc[type(e).__name__ + ": " + str(e)[:60]] += 1; ex.setdefault(type(e).__name__, sd)
            continue
        z = collections.Counter()
        for zona in ("hand", "library", "graveyard", "exile", "impulse"):
            for c in getattr(s, zona):
                z[c] += 1
        for it in s.delayed_return:
            if isinstance(it, str):
                z[it] += 1
        for p in s.battlefield:
            if not p.is_token:
                z[p.card.name] += 1
        for nm, c in z.items():
            if nm != "Tam, the Possibility" and c > base.get(nm, 0):
                mais[nm] += 1; ex.setdefault("mais:" + nm, sd)
        if not s.game_over and not s.m["aminatou_permanents_given"]:
            for nm, c in base.items():
                if z[nm] < c:
                    menos[nm] += 1; ex.setdefault("menos:" + nm, sd)
    return mais, menos, exc, ex


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    seed0 = int(sys.argv[2]) if len(sys.argv) > 2 else 5_000_000
    for modo in ("padrao", "resiliencia"):
        seeds = list(range(seed0, seed0 + N))
        blocos = [(modo, seeds[i::16], i) for i in range(16)]
        with Pool(4) as p:
            partes = p.map(job, blocos)
        mais, menos, exc, ex = collections.Counter(), collections.Counter(), collections.Counter(), {}
        for a, b, c, d in partes:
            mais.update(a); menos.update(b); exc.update(c)
            for k, v in d.items():
                ex.setdefault(k, v)
        print(f"{modo:12s} N={N}: partidas com carta A MAIS = {sum(mais.values())} {dict(mais)} | A MENOS = {sum(menos.values())} {dict(menos)} | excecoes = {sum(exc.values())} {dict(exc)} | exemplos {dict(list(ex.items())[:4])}", flush=True)
