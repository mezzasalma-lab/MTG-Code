"""Classe (o) da Regra #10 para o Prismatic Bridge (achada na partida manual #3 do Mothman em 2026-11-11): a ESCOLHA do terreno ignora que outro terreno da mao deixaria o COMANDANTE conjuravel NESTE turno
(Plaza of Heroes da' qualquer cor so' para magia lendaria; a Prismatic Bridge e' lendaria e de 5 cores). Este simulador guarda o campo como lista de NOMES (nao `Permanent`), entao nao serve o
`audit_terreno_comandante.py` (Mothman/Tam); o ensaio a seco e' o mesmo: o terreno entra em campo so' para a checagem `can_cast(state, COMMANDER)` e sai em seguida. SO' LE o estado: nao altera o jogo.
OCASIAO PERDIDA: a Bridge nao esta em campo, nao e' conjuravel agora, algum terreno da mao (nao fetch, nao entra virado; shockland so' se a propria politica pagaria os 2 de vida) a deixaria conjuravel
neste turno, e o simulador jogou OUTRO terreno. Uso: python3 -I audit_terreno_comandante_pb.py <N> <semente0> [padrao|resiliencia]  (a chave de correcao, se existir, tem de estar desligada)"""
import collections, importlib.util, json, os, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PASTA = os.path.join(R, "prismatic-bridge-wurbg")
N, S0 = int(sys.argv[1]), int(sys.argv[2]); modo = sys.argv[3] if len(sys.argv) > 3 else "padrao"
os.chdir(PASTA)
spec = importlib.util.spec_from_file_location("sim", os.path.join(PASTA, "prismatic_bridge_goldfish_v1.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
if hasattr(m, "COMMANDER_ENABLING_LAND"):
    m.COMMANDER_ENABLING_LAND = False
orig = m.play_land
cont = {"deck": "prismatic-bridge", "modo": modo, "jogos": 0, "jogos_com_ocasiao_perdida": 0, "ocasioes": 0, "perdidas": 0, "perdidas_por_turno": {}, "terreno_que_liberava": {}}
atual = {"perdeu": False}
def libera(st):
    if st.land_played or st.bridge_in_play or m.can_cast(st, m.COMMANDER):
        return []
    out = []
    for c in dict.fromkeys(x for x in st.hand if m.is_land(x)):
        if m.has_tag(c, "fabled_passage") or "fetch" in m.C(c).tags or m._tl_is_tapped(st, c):
            continue
        st.battlefield.append(c)
        try:
            if c in m.SHOCKLANDS and not m._shock_pays_life(st, c):
                continue
            ok = m.can_cast(st, m.COMMANDER)
        finally:
            st.battlefield.remove(c)
        if ok:
            out.append(c)
    return out
def envolve(st, log):
    antes = collections.Counter(st.battlefield)
    lib = libera(st)
    orig(st, log)
    if not lib:
        return
    cont["ocasioes"] += 1
    depois = collections.Counter(st.battlefield)
    jogados = [n for n in depois if depois[n] > antes.get(n, 0) and m.is_land(n)]
    if any(n in lib for n in jogados):
        return
    cont["perdidas"] += 1
    cont["perdidas_por_turno"][st.turn] = cont["perdidas_por_turno"].get(st.turn, 0) + 1
    for n in lib:
        cont["terreno_que_liberava"][n] = cont["terreno_que_liberava"].get(n, 0) + 1
    atual["perdeu"] = True
m.play_land = envolve
fn = m.simulate_one if modo == "padrao" else m.simulate_one_with_interaction
for i in range(N):
    atual["perdeu"] = False
    fn(S0 + i, 12, False)
    cont["jogos"] += 1
    cont["jogos_com_ocasiao_perdida"] += 1 if atual["perdeu"] else 0
cont["pct_jogos_com_ocasiao_perdida"] = round(100 * cont["jogos_com_ocasiao_perdida"] / max(1, cont["jogos"]), 2)
print(json.dumps(cont, sort_keys=True))
