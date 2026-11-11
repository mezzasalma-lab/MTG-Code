"""Classe de erro do MOTOR (Regra #10, achada na partida manual #3 do Mothman em 2026-11-11): a ESCOLHA do terreno ignora que outro terreno da mao deixaria o COMANDANTE conjuravel NESTE turno
(Plaza of Heroes da' qualquer cor so' para magia lendaria; o simulador a pontuava como terreno incolor, o usuario cometeu o mesmo erro no T4).
Mede, sem alterar o comportamento (so' LE o estado: ensaio a seco com o terreno em campo e remocao imediata, `next_uid` restaurado), em quantas partidas existiu uma OCASIAO PERDIDA:
o comandante esta no comando, nao e' conjuravel agora, algum terreno da mao (nao fetch, nao entra virado) o deixaria conjuravel neste turno, e o simulador jogou OUTRO terreno.
Serve a simuladores com `play_land_phase`, `mk_perm`, `can_cast_name`, `commander_in_cz` (Mothman, Tam). Uso: python3 -I audit_terreno_comandante.py <mothman|tam> <N> <semente0> [padrao|resiliencia]
A chave de correcao (`PLAZA_ENABLES_COMMANDER` no Mothman) tem de estar DESLIGADA para medir o erro (a ocasiao perdida e' 0 com ela ligada)."""
import importlib.util, json, os, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CFG = {
    "mothman": ("wise-mothman-sultai", "mothman_goldfish_v1.py", lambda m: (m.COMMANDER, (m.COMMANDER, 0)), {"PLAZA_ENABLES_COMMANDER": False}),
    "tam": ("tam-the-possibility-wubrg", "tam_goldfish_v1.py", lambda m: ("Tam, the Possibility", ("Tam, the Possibility", "cz")), {}),
}
deck, N, S0 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
modo = sys.argv[4] if len(sys.argv) > 4 else "padrao"
pasta, arq, cmd, flags = CFG[deck]
os.chdir(os.path.join(R, pasta))
spec = importlib.util.spec_from_file_location("sim", os.path.join(R, pasta, arq)); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for k, v in flags.items():
    setattr(m, k, v)
nome, args = cmd(m)
orig = m.play_land_phase
cont = {"deck": deck, "modo": modo, "jogos": 0, "jogos_com_ocasiao_perdida": 0, "ocasioes": 0, "perdidas": 0, "perdidas_por_turno": {}, "terreno_que_liberava": {}}
atual = {"perdeu": False}
def libera(st):
    """lista de terrenos da mao que deixariam o comandante conjuravel agora (vazia se ja' e' conjuravel ou se nao esta no comando)"""
    if not st.commander_in_cz or m.can_cast_name(st, *args):
        return []
    out = []
    for c in dict.fromkeys(st.hand):
        cc = m.CARD_DB[c]
        if "land" not in cc.types or "mdfc" in getattr(cc, "tags", set()) or "fetch" in getattr(cc, "tags", set()):
            continue
        if m.land_enters_tapped(st, c):
            continue
        uid0 = st.next_uid
        tmp = m.mk_perm(st, c)
        st.battlefield.append(tmp)
        try:
            ok = m.can_cast_name(st, *args)
        finally:
            st.battlefield.remove(tmp); st.next_uid = uid0
        if ok:
            out.append(c)
    return out
def envolve(st):
    antes = set(p.card.name for p in st.battlefield)
    lib = libera(st)
    orig(st)
    if lib:
        cont["ocasioes"] += 1
        novos = [p.card.name for p in st.battlefield if "land" in p.card.types and p.card.name not in antes or (p.card.name in lib and sum(1 for q in st.battlefield if q.card.name == p.card.name) > 0)]
        jogou_um_que_libera = any(n in lib for n in [p.card.name for p in st.battlefield if "land" in p.card.types]) and any(
            st.battlefield.count(None) == 0 for _ in [0])
        # o terreno JOGADO neste turno e' o que entrou agora: o que existe em campo e nao existia antes (por nome; basicos repetidos: contagem)
        from collections import Counter
        antes_c = Counter(antes_lista)
        depois_c = Counter(p.card.name for p in st.battlefield)
        jogados = [n for n in depois_c if depois_c[n] > antes_c.get(n, 0) and "land" in m.CARD_DB[n].types]
        if any(n in lib for n in jogados):
            return
        cont["perdidas"] += 1
        cont["perdidas_por_turno"][st.turn] = cont["perdidas_por_turno"].get(st.turn, 0) + 1
        for n in lib:
            cont["terreno_que_liberava"][n] = cont["terreno_que_liberava"].get(n, 0) + 1
        atual["perdeu"] = True
antes_lista = []
def envolve2(st):
    global antes_lista
    antes_lista = [p.card.name for p in st.battlefield]
    envolve(st)
m.play_land_phase = envolve2
fn = m.simulate_one if modo == "padrao" else m.simulate_one_with_interaction
for i in range(N):
    atual["perdeu"] = False
    fn(S0 + i, 12)
    cont["jogos"] += 1
    cont["jogos_com_ocasiao_perdida"] += 1 if atual["perdeu"] else 0
cont["pct_jogos_com_ocasiao_perdida"] = round(100 * cont["jogos_com_ocasiao_perdida"] / max(1, cont["jogos"]), 2)
print(json.dumps(cont, sort_keys=True))
