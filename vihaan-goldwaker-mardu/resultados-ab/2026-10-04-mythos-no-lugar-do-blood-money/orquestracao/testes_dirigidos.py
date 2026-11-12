"""Testes dirigidos da 12a rodada (Mythos of Snapdax no lugar do Blood Money) alem dos 8 testes novos de `test_vihaan_goldfish.py` (resumos/testes_repo.txt). Aqui, sobre ESTADOS NATURAIS
(o estado final de partidas reais, nos turnos 4..8, nos dois modos), nao so' sobre estados montados a mao:
  (A) consistencia de copia: a selecao+sacrificio da Mythos do simulador (`_mythos_selection` + `_mass_sacrifice`) deixa o MESMO estado que `r_manter_um` do harness da rodada dos wipes de
      sacrificio (`2026-10-04-wipes-de-sacrificio/orquestracao/sac_harness.py`), que foi escrito antes e a parte. ATENCAO: os dois sao do mesmo autor e seguem a mesma politica de escolha; isto
      pega divergencia acidental de copia, NAO e' um oraculo independente. O oraculo independente das regras sao os testes montados a mao (rulings 2020-04-17 lidos ao vivo).
  (B) resolucao forcada da Mythos em cada estado natural: os sobreviventes da selecao (antes - sacrificadas, medidos ao redor de `_mass_sacrifice`, sem o ruido dos gatilhos de morte que criam
      Treasure/Clue/Food) formam uma ESCOLHA LEGAL (`fx_common.escolha_legal`: cada sobrevivente num slot distinto artefato/criatura/encantamento do tipo dele), nenhuma magia em voo e'
      sacrificada, o motor guardado (Vihaan > Mahadi > Mayhem Devil) sobrevive, e o contador `mythos_perm_lost_total` e o retorno batem com antes - sobreviventes.
Uso: python3 testes_dirigidos.py [sementes_por_modo]"""
import collections, copy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_common as F
sys.path.insert(0, os.path.join(F.DECK, "resultados-ab", "2026-10-04-wipes-de-sacrificio", "orquestracao"))
import sac_harness as H

N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
V = F.carrega(F.DEPOIS, "vih_td")
MYTHOS, ENGINES = V.MYTHOS, ("Vihaan, Goldwaker", "Mahadi, Emporium Master", "Mayhem Devil")


def estado(s):
    return (sorted(s.battlefield), sorted(s.graveyard), s.constructs, s.other_tokens, s.dragons, s.treasures, s.treasures_animated_alive, s.treasures_tapped, s.clues, s.foods,
            s.drain_damage_total, s.table_damage_total, s.creature_deaths_total, s.treasures_created_total, s.commander_in_play, s.own_wipe_commander_destroyed_total)


def tipos(s):
    nom = [n for n in s.battlefield if n not in V.LAND_NAMES and V.CARD_DB[n].ctype not in ("instant", "sorcery")]
    cre = sum(1 for n in nom if V.is_creature_card(n)) + s.constructs + s.other_tokens + s.dragons + min(s.treasures_animated_alive, s.treasures)
    return nom, cre, sum(1 for n in nom if V.is_artifact_card(n)), sum(1 for n in nom if V.is_enchantment_card(n))


tot = diverge = viol = materia = com_motor = 0
perm_tot = 0
falhas = []
for modo in ("padrao", "resiliencia"):
    fn = V.simulate_one if modo == "padrao" else V.simulate_one_with_interaction
    for i in range(N):
        for turnos in (4, 6, 8):
            s0 = fn(7_000_000 + i, turnos)
            nome = [n for n in s0.battlefield if n not in V.LAND_NAMES]
            tot += 1
            if not nome and not (s0.constructs or s0.other_tokens or s0.dragons or s0.treasures or s0.clues or s0.foods):
                continue
            materia += 1
            # (A) simulador x harness
            a, b = copy.deepcopy(s0), copy.deepcopy(s0)
            na = V._mass_sacrifice(a, V._mythos_selection(a))
            nb = H.r_manter_um(V, b)
            if na != nb or estado(a) != estado(b):
                diverge += 1
                if len(falhas) < 5:
                    falhas.append(("A", modo, i, turnos, na, nb))
            # (B) resolucao forcada pelo caminho real (resolve_instant_sorcery), medida ao redor de _mass_sacrifice
            c = copy.deepcopy(s0)
            pre_nom = [n for n in c.battlefield if n not in V.LAND_NAMES and V.CARD_DB[n].ctype not in ("instant", "sorcery")]
            anim0 = min(c.treasures_animated_alive, c.treasures)
            pre_tok = {"con": c.constructs, "oth": c.other_tokens, "dra": c.dragons, "anim": anim0, "inan": c.treasures - anim0, "clues": c.clues, "foods": c.foods}
            pre_n = len(pre_nom) + sum(pre_tok.values())
            motor = next((e for e in ENGINES if e in pre_nom), None)
            cap = {}
            orig_ms = V._mass_sacrifice
            def ms(state, sel):
                r = orig_ms(state, sel)
                cap["sel"], cap["r"] = sel, r
                return r
            V._mass_sacrifice = ms
            try:
                V.resolve_instant_sorcery(c, MYTHOS)
            finally:
                V._mass_sacrifice = orig_ms
            sel = cap["sel"]
            sac = collections.Counter(sel["cre"] + sel["outros"])
            vivos = list((collections.Counter(pre_nom) - sac).elements())
            tok = {k: pre_tok[k] - sel[k] for k in pre_tok}
            resto = len(vivos) + sum(tok.values())
            ok = F.escolha_legal(V, vivos, tok) and (motor is None or motor in vivos)
            ok = ok and cap["r"] == pre_n - resto and c.mythos_perm_lost_total == cap["r"] and c.mythos_cast_total == 1
            if motor is not None:
                com_motor += 1
            perm_tot += cap["r"]
            if not ok:
                viol += 1
                if len(falhas) < 5:
                    falhas.append(("B", modo, i, turnos, vivos, tok, motor))
print(f"estados naturais: {tot} (turnos 4/6/8 x {N} sementes x 2 modos) | com algum permanente nao-terreno: {materia} | com motor (Vihaan/Mahadi/Mayhem Devil) em campo: {com_motor}")
print(f"(A) divergencias simulador x harness: {diverge}")
print(f"(B) violacoes da resolucao forcada: {viol} | permanentes minhas sacrificadas no total: {perm_tot}")
for f in falhas:
    print("   falha", f)
raise SystemExit(1 if diverge or viol else 0)
