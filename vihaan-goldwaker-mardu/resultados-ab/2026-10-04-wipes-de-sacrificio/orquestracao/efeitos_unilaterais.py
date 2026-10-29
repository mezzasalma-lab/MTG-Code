"""Castabilidade (mana + cor) dos efeitos de sacrificio UNILATERAIS (so' os oponentes sacrificam; custo zero no MEU campo) e da condicao do Vona's Hunger ('ascend': 10 ou mais permanentes
-> cada oponente sacrifica METADE das criaturas, arredondada pra cima, em vez de uma) sobre estados naturais do goldfish. O que esses efeitos fazem NOS OPONENTES e' 📊 (o simulador nao modela
campo de oponente); aqui so' se mede quando daria pra conjurar e quando o Vona's Hunger estaria no modo 'metade'. Mayhem Devil dispara por cada criatura que o OPONENTE sacrifica (1 de dano
cada, de qualquer jogador): isso tambem e' 📊. Uso: python3 efeitos_unilaterais.py [N] [semente0]"""
import os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
import sac_harness as H

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 3_000_000
V = F.flags(F.carrega(F.DEPOIS, "vih_unilaterais"))
H.instala(V)
V.OWN_WIPE_HOLD_ALWAYS_ENABLED = False
V.OWN_WIPE_HOLD_ENGINE_ENABLED = False
EFEITOS = {  # nome: (custo em mana, pips de cor)
    "Vona's Hunger (instantanea; 'metade' com 10+ permanentes)": (3, ["B"]),
    "Crackling Doom (instantanea; 2 de dano a cada oponente + o de maior poder)": (3, ["R", "W", "B"]),
    "Rush of Dread (so' 1 oponente alvo; metade das criaturas, modo +{1})": (4, ["B", "B"]),
    "Make an Example (eu escolho a pilha de cada oponente)": (4, ["B"]),
    "Syphon Flesh (cada outro jogador sacrifica 1; eu ganho um Zumbi por criatura)": (5, ["B"]),
    "Perilous Predicament (instantanea; 1 artefato-criatura + 1 nao-artefato por oponente)": (5, ["B"]),
    "Blasphemous Act (referencia: custo REDUZIDO pelas criaturas MINHAS)": (None, ["R"]),
}
amostras = []
contador = {}
orig_main = V.main_phase


def permanentes(s):
    return sum(1 for n in s.battlefield) + s.treasures + s.constructs + s.other_tokens + s.dragons + s.clues + s.foods


def espia(s):
    if s.turn >= 3:
        mana = V.remaining_mana(s)
        f = H.fontes(V, s)
        r = {}
        for nome, (c, pips) in EFEITOS.items():
            custo = V.spell_cost(s, "Blasphemous Act") if c is None else c
            r[nome] = (mana >= custo, H.pips_ok(f, pips))
        amostras.append({"turno": s.turn, "perm": permanentes(s), "r": r, "criaturas": H.total_criaturas(H.inventario(V, s))})
    return orig_main(s)


V.main_phase = espia
for i in range(N):
    V.simulate_one(S0 + i)
tot = len(amostras)
print(f"N={N} partidas (padrao, sementes {S0}..{S0 + N - 1}); {tot} estados (turno >= 3, 1a e 2a main).")
print("\n%-86s %8s %10s" % ("efeito unilateral", "%mana", "%mana+cor"))
for nome in EFEITOS:
    pm = sum(1 for a in amostras if a["r"][nome][0])
    pc = sum(1 for a in amostras if a["r"][nome][0] and a["r"][nome][1])
    print("%-86s %7.1f%% %9.1f%%" % (nome, 100.0 * pm / tot, 100.0 * pc / tot))
print("\nCondicao 'ascend' do Vona's Hunger (10 ou mais permanentes meus, contando terrenos, fichas, Treasures, Clues e Foods), por turno:")
print("%-8s %10s %14s %20s" % ("turno", "estados", "%>=10 perm", "permanentes (media)"))
for t in range(3, 9):
    sel = [a for a in amostras if a["turno"] == t]
    if sel:
        print("%-8d %10d %13.1f%% %20.2f" % (t, len(sel), 100.0 * sum(1 for a in sel if a["perm"] >= 10) / len(sel), st.mean(a["perm"] for a in sel)))
print("\nVona's Hunger no modo METADE (10+ permanentes) E conjuravel por mana+cor, %% de todos os estados: %.1f%%" % (
    100.0 * sum(1 for a in amostras if a["perm"] >= 10 and a["r"]["Vona's Hunger (instantanea; 'metade' com 10+ permanentes)"][0] and a["r"]["Vona's Hunger (instantanea; 'metade' com 10+ permanentes)"][1]) / tot))
