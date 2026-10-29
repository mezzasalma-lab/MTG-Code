"""Prova de LEGALIDADE DE MANA turno a turno: para cada turno, as fontes viradas no log (lidas do trace) e as magias pagas (leitura minha) -> existe alguma escolha de cores
que paga tudo? Uso: python3 mana_por_turno.py > resumos/mana_por_turno.md
Fontes: Strip Mine {C}; Triome {B/G/U}; Watery Grave {U/B}; Island {U}; Swamp {B}; Forest {G}; Overgrown Tomb {B/G}; Sol Ring {C}{C}; Kami: X mana de UMA cor, X = poder (1 base + contadores do log).
Limites: so' prova a viabilidade da conta (total e cores); NAO prova a ordem em que as fontes foram viradas nem o que foi pago com o que. Vida de shock/Waterlogged nao e' contada."""
import itertools, json, lzma, os, re
aqui = os.path.dirname(os.path.abspath(__file__))
KAMI_BASE = int(json.load(open(os.path.join(aqui, "..", "..", "..", "scryfall-cache", "oracle-cache.json")))["Kami of Whispered Hopes"]["power"])
FONTE = {"Strip Mine": ["C"], "Zagoth Triome": ["B", "G", "U"], "Watery Grave": ["U", "B"], "Island": ["U"], "Swamp": ["B"], "Forest": ["G"], "Overgrown Tomb": ["B", "G"], "Sol Ring": ["CC"],
         "Urza's Saga": ["C"]}
def pips(custo):
    cores = re.findall(r"\{([WUBRGC])\}", custo)
    gen = sum(int(x) for x in re.findall(r"\{(\d+)\}", custo))
    return cores, gen
# turno: (fontes viradas por mana, kami_contadores (None = nao usado), [(magia, custo)])
T = {
 2: (["Strip Mine", "Zagoth Triome", "Sol Ring"], None, [("Sol Ring", "{1}"), ("Six", "{2}{G}")]),
 3: (["Zagoth Triome", "Sol Ring"], None, [("Kami of Whispered Hopes", "{2}{G}")]),
 4: (["Zagoth Triome", "Watery Grave", "Island", "Strip Mine"], None, [("The Wise Mothman", "{1}{B}{G}{U}")]),
 5: (["Forest", "Zagoth Triome", "Sol Ring", "Swamp", "Strip Mine"], 1, [("Icetill Explorer (retrace, descartando Swamp)", "{2}{G}{G}"), ("Hedge Shredder", "{2}{G}{G}")]),
 6: (["Island", "Watery Grave", "Zagoth Triome", "Sol Ring"], None, [("Ruin Crab (retrace, descartando Urza's Saga)", "{U}"), ("Memory Erosion", "{1}{U}{U}")]),
 7: (["Forest", "Sol Ring", "Watery Grave", "Island", "Strip Mine", "Swamp", "Zagoth Triome"], None,
     [("Generous Patron", "{2}{G}"), ("Wave Goodbye", "{2}{U}{U}"), ("Hardened Scales (retrace, descartando Takenuma)", "{G}")]),
 8: (["Island", "Zagoth Triome", "Watery Grave", "Swamp", "Forest", "Strip Mine", "Overgrown Tomb", "Forest", "Sol Ring"], None,
     [("Ruin Crab", "{U}"), ("The Wise Mothman", "{1}{B}{G}{U}"), ("Icetill Explorer", "{2}{G}{G}")]),
 9: (["Forest", "Sol Ring", "Forest", "Overgrown Tomb", "Swamp"], None, [("Six", "{2}{G}"), ("Kami of Whispered Hopes", "{2}{G}")]),
}
print("# Legalidade de mana por turno (partida manual do Mothman)\n")
print("| T | mana produzido | custo pago | sobra | viavel? | exemplo de pagamento |")
print("|---|---|---|---|---|---|")
ok_all = True
for t, (fontes, kami, magias) in sorted(T.items()):
    cores, gen = [], 0
    for _, c in magias:
        a, b = pips(c); cores += a; gen += b
    custo = len(cores) + gen
    opcoes = []
    for f in fontes:
        o = FONTE[f]
        opcoes.append([[x] for x in o] if o != ["CC"] else [["C", "C"]])
    if kami is not None:
        x = KAMI_BASE + kami
        opcoes.append([[c] * x for c in "WUBRG"])
    prod = sum(len(max(o, key=len)) for o in opcoes)
    viavel = None
    for esc in itertools.product(*opcoes):
        unidades = [u for e in esc for u in e]
        if len(unidades) < custo:
            continue
        cont = {c: unidades.count(c) for c in set(unidades)}
        if all(cont.get(c, 0) >= cores.count(c) for c in set(cores)):
            viavel = esc
            break
    ok_all &= viavel is not None
    ex = "-" if viavel is None else " + ".join("".join(e) for e in viavel)
    print(f"| T{t} | {prod} | {custo} ({', '.join(m for m, _ in magias)}) | {prod - custo} | {'sim' if viavel else '**NAO**'} | {ex} |")
assert ok_all and len(T) == 8
print(f"\nPoder base do Kami lido do cache: {KAMI_BASE}. No T5 o Kami tinha 1 contador no log (poder {KAMI_BASE + 1}); se a substituicao do Kami tivesse sido aplicada (2 contadores) ele daria 1 mana a mais.")
print("**Todos os 8 turnos com magias (T2-T9) sao pagaveis** com as fontes que o log mostra viradas (T1 so' tem a Misty).")
