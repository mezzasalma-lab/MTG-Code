"""Classe SISTEMICA (Rat King, 2026-10-25): carta cujo oraculo tem um efeito de ENTRADA/de feitico, mas que o simulador deixa passar SEM MUDAR NADA no estado ("ETB fantasma").
Achados reais que esta varredura teria pego: Gray Merchant (o ETB de dreno por devocao nao existia: so' o Nykthos lia a devocao) e Emeritus of Woe ("enters prepared" nunca ligava o flag).
Nenhuma auditoria carta-a-carta pegou: a carta TINHA entrada no CARD_DB e um comentario dizendo que era "real e rastreada".

Metodo: monta um estado neutro (T5, 8 terrenos, comandante, 2 fichas, cemiterio com criaturas, biblioteca real), conjura/poe em campo CADA carta nao-terreno (`resolve_cast(..., free=True)`)
e compara todos os campos do estado antes x depois (numericos, tamanhos de listas/conjuntos), IGNORANDO a propria presenca da carta no campo. Carta sem NENHUMA mudanca e' candidata a ETB fantasma.
Triagem: imprime o oraculo ao vivo (dados/scryfall_oraculo_rulings_*.json) das candidatas; a leitura contra o oraculo e' a mao. Um falso positivo comum: permanente so' com estatico/ativada
(Rat Colony, Cabal Coffers...), que nao muda nada ao entrar de verdade; por isso marca "ORACULO TEM ENTRADA/FEITICO" quando o texto tem "enters"/e' instant/sorcery.
Controle positivo: rodar no snapshot ANTES da rodada (tem de listar Gray Merchant e Emeritus) e no arquivo DEPOIS (nao listam mais).
PARTE 2 (gatilhos "Whenever/At the beginning"): pra cada permanente, aplica eventos-padrao (conjurar criatura, entrar uma ficha de Rat, morrer uma criatura, combate, upkeep, fim de turno) num estado COM a carta e
num estado SEM ela; se a diferenca de estado causada pelo evento e' IGUAL nos dois pra TODOS os eventos, a carta nao reage a nenhum deles no simulador. Candidata quando o oraculo tem gatilho. Pegaria: Crypt Ghast (extort),
Ninja Teen (criatura sai do campo: dreno), Ayara (ficha de Rat entra), Zulaport... Limite: so' os 6 eventos acima; gatilho de outro evento (ataque de uma criatura especifica, descarte...) nao e' exercitado.
Uso: python3 -I audit_etb_sem_efeito.py <sim.py> <scryfall_oraculo_rulings.json>      (so' simuladores com GameState{battlefield,hand,library,graveyard}, resolve_cast, create_rat_token, sacrifice_any_creature, combat_step,
upkeep_step, end_step; hoje so' o Rat King)"""
import copy, dataclasses, importlib.util, json, os, random, re, sys
simp, jsonp = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.chdir(os.path.dirname(simp)); sys.path.insert(0, os.path.dirname(simp))
spec = importlib.util.spec_from_file_location("sim_etb", simp); M = importlib.util.module_from_spec(spec); sys.modules["sim_etb"] = M; spec.loader.exec_module(M)
live = json.load(open(jsonp))
IGN = {"battlefield", "creature_cast_turn", "commander_in_play", "commander_cast_count", "commander_cast_turn", "ramp_pieces_cast_total", "interaction_spells_cast_total", "mana_spent_this_turn",
       "tapped_lands_this_turn", "interaction_rng", "treasures_spent_this_turn"}
def foto(s):
    d = {}
    for f in dataclasses.fields(s):
        if f.name in IGN: continue
        v = getattr(s, f.name)
        if isinstance(v, (list, set, dict, tuple)): d["len_" + f.name] = len(v)
        elif isinstance(v, (bool, int, float)) or v is None: d[f.name] = v
    return d
def base():
    s = M.GameState(); s.turn = 5
    s.battlefield = ["Swamp"] * 8 + [M.COMMANDER]
    s.commander_in_play = True
    s.rat_tokens = 2
    s.graveyard = ["Syr Konrad, the Grim", "Rat Colony", "Gray Merchant of Asphodel"]
    s.library = list(M.BASE_LIBRARY[:40]); s.hand = ["Swamp", "Swamp"]
    for n in s.battlefield:
        if M.is_creature_card(n): s.creature_cast_turn[n] = 1
    return s
cand = []; n_checadas = 0
for nome, c in sorted(M.CARD_DB.items()):
    if c.ctype == "land" or nome == M.COMMANDER: continue
    s = base(); a = foto(s)
    try:
        M.resolve_cast(s, nome, free=True)
    except Exception as e:
        print(f"ERRO ao conjurar {nome}: {type(e).__name__}: {e}"); continue
    n_checadas += 1
    b = foto(s)
    mudou = sorted(k for k in a if a[k] != b.get(k))
    if mudou: continue
    v = live.get(nome) or next((x for k, x in live.items() if k.split(" // ")[0] == nome.split(" // ")[0]), None)
    txt = " / ".join((f.get("oracle_text") or "") for f in v["faces"]).replace("\n", " ") if v else "(sem oraculo no arquivo)"
    tem = c.ctype in ("instant", "sorcery") or bool(re.search(r"\benters?\b|\bWhen\b", txt))
    cand.append((nome, c.ctype, tem, txt))
print(f"cartas nao-terreno conjuradas no estado neutro: {n_checadas} (>0) | SEM NENHUMA mudanca de estado: {len(cand)}")
for nome, t, tem, txt in cand:
    print(f"  {'[ORACULO TEM ENTRADA/FEITICO] ' if tem else '[so estatico/ativada]            '}{nome} ({t}): {txt[:230]}")


# ------------------------------------------------------------------------------------------------ PARTE 2: gatilhos
def eventos():
    return {
        "conjurar criatura": lambda st: M.resolve_cast(st, "Rat Colony", free=True),
        "ficha de Rat entra": lambda st: M.create_rat_token(st),
        "criatura morre (sacrificio)": lambda st: M.sacrifice_any_creature(st, 1),
        "combate": lambda st: M.combat_step(st),
        "upkeep": lambda st: M.upkeep_step(st),
        "fim de turno": lambda st: M.end_step(st),
    }
def estado(com=None):
    s = base()
    if com:
        s.battlefield.append(com)
        if M.is_creature_card(com): s.creature_cast_turn[com] = 1
    return s
def delta(s, ev):
    a = foto(s); ev(s); b = foto(s)
    return {k: b[k] - a[k] if isinstance(a[k], (int, float)) and isinstance(b.get(k), (int, float)) and not isinstance(a[k], bool) else (a[k], b.get(k)) for k in a if a[k] != b.get(k)}
ref = {nm: delta(estado(), ev) for nm, ev in eventos().items()}
cand2 = []; n2 = 0
for nome, c in sorted(M.CARD_DB.items()):
    if c.ctype not in ("creature", "artifact", "enchantment") or nome == M.COMMANDER: continue
    n2 += 1
    reage = []
    for nm, ev in eventos().items():
        try:
            d = delta(estado(nome), ev)
        except Exception as e:
            reage.append(f"{nm}: ERRO {type(e).__name__}"); continue
        if d != ref[nm]: reage.append(nm)
    if reage: continue
    v = live.get(nome) or next((x for k, x in live.items() if k.split(" // ")[0] == nome.split(" // ")[0]), None)
    txt = " / ".join((f.get("oracle_text") or "") for f in v["faces"]).replace("\n", " ") if v else "(sem oraculo no arquivo)"
    if re.search(r"\bWhenever\b|\bAt the beginning\b|\bWhen\b", txt):
        cand2.append((nome, c.ctype, txt))
print(f"\nPARTE 2: permanentes testados contra {len(ref)} eventos-padrao: {n2} (>0) | NAO reagem a nenhum evento E o oraculo tem gatilho: {len(cand2)}")
for nome, t, txt in cand2:
    print(f"  {nome} ({t}): {txt[:230]}")
