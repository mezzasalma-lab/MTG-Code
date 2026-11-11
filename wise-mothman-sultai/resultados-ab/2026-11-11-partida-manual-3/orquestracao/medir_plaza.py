"""Mede, no simulador do Mothman (MM_SIM; padrao = a copia ANTES da correcao arquivada em ../codigo/) (sem alterar o comportamento: so' envolve `play_land_phase` com uma checagem de leitura), quantas vezes o simulador
joga OUTRO terreno quando jogar a Plaza of Heroes deixaria o comandante conjuravel NESTE turno (a linha que o usuario errou no T4 da partida manual #3).
Uso: python3 -I medir_plaza.py <N> <semente_inicial> [modo]    modo: padrao (simulate_one) | resiliencia (simulate_one_with_interaction)
Cada partida: 12 turnos. Saida: JSON com contagens. O envoltorio so' LE o estado (ensaio a seco com a Plaza e remocao imediata, sem efeito colateral: `next_uid` restaurado)."""
import importlib.util, json, os, sys
aqui = os.path.dirname(os.path.abspath(__file__))
SIM = os.environ.get("MM_SIM") or os.path.join(aqui, "..", "codigo", "mothman_goldfish_v1_ANTES_plaza_c59226f.py")   # padrao: copia arquivada ANTES da correcao
spec = importlib.util.spec_from_file_location("mm", SIM); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
N, S0 = int(sys.argv[1]), int(sys.argv[2])
modo = sys.argv[3] if len(sys.argv) > 3 else "padrao"
orig = m.play_land_phase
cont = {"jogos": 0, "oportunidades": 0, "perdidas": 0, "perdidas_por_turno": {}, "oportunidades_por_turno": {}, "plaza_jogada_na_oportunidade": 0, "jogos_com_perdida": 0}
atual = {"perdeu": False}
def comandante_conjuravel_com_plaza(st):
    if not st.commander_in_cz or "Plaza of Heroes" not in st.hand:
        return None
    if m.can_cast_name(st, m.COMMANDER, 0):
        return None                                   # ja conjuravel sem a Plaza: nao e' oportunidade
    uid0 = st.next_uid
    tmp = m.mk_perm(st, "Plaza of Heroes"); tmp.entered_turn = st.turn - 1
    st.battlefield.append(tmp)
    try:
        ok = m.can_cast_name(st, m.COMMANDER, 0)
    finally:
        st.battlefield.remove(tmp); st.next_uid = uid0
    return ok
def envolve(st):
    op = comandante_conjuravel_com_plaza(st)
    orig(st)
    if op:
        t = st.turn
        cont["oportunidades"] += 1
        cont["oportunidades_por_turno"][t] = cont["oportunidades_por_turno"].get(t, 0) + 1
        plaza_em_campo = any(p.card.name == "Plaza of Heroes" for p in st.battlefield)
        if plaza_em_campo:
            cont["plaza_jogada_na_oportunidade"] += 1
        else:
            cont["perdidas"] += 1
            cont["perdidas_por_turno"][t] = cont["perdidas_por_turno"].get(t, 0) + 1
            atual["perdeu"] = True
m.play_land_phase = envolve
fn = m.simulate_one if modo == "padrao" else m.simulate_one_with_interaction
for i in range(N):
    atual["perdeu"] = False
    fn(S0 + i, 12)
    cont["jogos"] += 1
    cont["jogos_com_perdida"] += 1 if atual["perdeu"] else 0
print(json.dumps(cont, sort_keys=True))
