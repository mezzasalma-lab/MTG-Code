"""Testes dirigidos da partida manual #12 (Tom Bombadil): cada afirmação do goldfish-log/LEIAME que depende do log bruto
é conferida contra `dados/partida.json.xz`; as que dependem de oráculo/ruling/regra, contra os arquivos arquivados em
`resumos/` (rulings ao vivo do Scryfall e trechos das Comprehensive Rules de 2026-09-25, extraídos de rules-cache/comprehensive-rules.txt) e contra o cache do repositório.
Cada teste tem um CONTROLE DE CORTE (a afirmação tem de FALHAR no dado alterado), para o teste não passar no vazio.
Uso: python3 -I testes_manual12.py   (uma linha por teste; sai com 1 se algum falhar)
O que estes testes NÃO provam: a intenção do usuário (ver as respostas de 2026-11-05 no LEIAME), a cor da mana, o que o log não registra (fichas que somem)."""
import copy, json, lzma, os, subprocess, sys
aqui = os.path.dirname(os.path.abspath(__file__))
T = json.load(lzma.open(os.path.join(aqui, "dados", "partida.json.xz")))
RUL = json.load(open(os.path.join(aqui, "resumos", "rulings_scryfall.json")))
CR = open(os.path.join(aqui, "resumos", "cr_2026-09-25_trechos.txt"), encoding="utf-8").read()
ORC = json.load(open(os.path.join(aqui, "..", "..", "..", "scryfall-cache", "oracle-cache.json")))
B = lambda ti: T[ti - 1]
res = []


def teste(nome, fn, controle=None):
    try:
        ok = bool(fn(T))
    except Exception as e:      # noqa
        ok, nome = False, f"{nome} (erro: {e!r})"
    ctrl = "sem controle"
    if controle is not None:
        try:
            falha = not bool(controle())
        except Exception:
            falha = True
        ctrl = "controle de corte falha como deve" if falha else "CONTROLE NÃO FALHOU (teste vácuo)"
        ok = ok and falha
    res.append(ok)
    print(f"{'PASSA' if ok else 'FALHA'} | {nome} | {ctrl}")


def idx(ti, pred, d=None):
    return [j for j, r in enumerate((d or T)[ti - 1]) if pred(r)]


def sem_evento(d, ti, a, b):
    d = copy.deepcopy(d)
    d[ti - 1] = [r for j, r in enumerate(d[ti - 1]) if not (a <= j <= b)]
    return d


# 1. T7: a Plains do 2º hand→battlefield é o MESMO objeto (desfazer): 1 terreno por turno em todos os 10 turnos
def t1(d):
    for ti, t in enumerate(d, 1):
        ev = [r for r in t if r["fromZone"] == "hand" and r["toZone"] == "battlefield" and "Land" in (ORC.get(r["name"], {}).get("type_line") or "")]
        if len({r["id"] for r in ev}) > 1:
            return False
    return len([r for r in B(7) if r["name"] == "Plains" and r["fromZone"] == "hand" and r["toZone"] == "battlefield"]) == 2
def c1():
    d = copy.deepcopy(T)
    for r in d[6]:
        if r["name"] == "Plains" and r["fromZone"] == "hand" and r["toZone"] == "battlefield":
            r["id"] = r["id"] + "x"; r["_a"] = 1          # se fossem 2 objetos, haveria 2 terrenos no turno
    p = [r for r in d[6] if r.get("_a")]
    p[0]["id"] = p[0]["id"] + "y"
    return t1(d)
teste("T7: Plains jogada 2× é o mesmo objeto; 1 terreno por turno em T1–T10", t1, c1)

# 2. compras por turno = esperado (leitura minha, ver ledger_compras.py)
ESP = [8, 1, 1, 2, 2, 3, 1, 1, 2, 4]
def t2(d):
    return [sum(1 for r in t if r["fromZone"] == "library" and r["toZone"] == "hand") for t in d] == ESP
teste("compras library→mão por turno = [8,1,1,2,2,3,1,1,2,4] (25 = 25)", t2, lambda: t2(sem_evento(T, 10, 26, 28)))

# 3. imposto do Tom: 2 lançamentos do comando (T5 e T8) e o campo commandTax do log fica 0 (o usuário pagou 7 sem registrar)
def t3(d):
    casts = [ti for ti, t in enumerate(d, 1) for r in t if r["name"] == "Tom Bombadil" and r["fromZone"] == "commandZone" and r["toZone"] == "battlefield"]
    return casts == [5, 8] and all(r["commandTax"] == 0 for t in d for r in t if r["name"] == "Tom Bombadil")
def c3():
    d = copy.deepcopy(T)
    for r in d[7]:
        if r["name"] == "Tom Bombadil" and r["fromZone"] == "commandZone":
            r["commandTax"] = 1
    return t3(d)
teste("Tom lançado do comando no T5 e no T8; commandTax = 0 no log inteiro", t3, c3)

# 4. T8: ordem do log = Nesting+Plains viram, ITDBT 4→3, Soldier ganha Lore=1, Ring 4, só depois o Tom volta; ITDBT sai só na Austere
def t4(d):
    t = d[7]
    nest = idx(8, lambda r: r["name"] == "Nesting Grounds" and r["tapped"], d)[0]
    l4 = idx(8, lambda r: r["name"] == "In the Darkness Bind Them" and (r["counters"].get("Lore") or {}).get("count") == 4, d)[0]
    l3 = idx(8, lambda r: r["name"] == "In the Darkness Bind Them" and (r["counters"].get("Lore") or {}).get("count") == 3, d)[0]
    sol = idx(8, lambda r: r["name"] == "Human Soldier" and (r["counters"].get("Lore") or {}).get("count") == 1, d)[0]
    ring = idx(8, lambda r: r["name"].startswith("The Ring") and (r["counters"].get("Generic") or {}).get("count") == 4, d)[0]
    tom = idx(8, lambda r: r["name"] == "Tom Bombadil" and r["fromZone"] == "commandZone", d)[0]
    aus = idx(8, lambda r: r["name"] == "Austere Command", d)[0]
    gy = idx(8, lambda r: r["name"] == "In the Darkness Bind Them" and r["toZone"] == "graveyard", d)[0]
    return nest < l4 < l3 < sol < ring < tom < aus < gy
def c4():
    d = copy.deepcopy(T)
    d[7][6], d[7][7] = d[7][7], d[7][6]          # inverte 4 e 3
    return t4(d)
teste("T8: Nesting Grounds → ITDBT 4→3 → Lore no Soldier → Anel 4 → Tom volta → Austere → ITDBT ao cemitério", t4, c4)

# 5. T9: Resurgent Belief chega a Time=0 DEPOIS da 1ª entrada da Kiora (mesmo id 2×); a compra da Song vem depois da volta da Presence e da 2ª Kiora
def t5(d):
    k = idx(9, lambda r: r["name"] == "Kiora Bests the Sea God" and r["fromZone"] == "hand" and r["toZone"] == "battlefield", d)
    t0 = idx(9, lambda r: r["name"] == "Resurgent Belief" and (r["counters"].get("Time") or {}).get("count") == 0, d)[0]
    pres = idx(9, lambda r: r["name"] == "Enchantress's Presence" and r["fromZone"] == "graveyard" and r["toZone"] == "battlefield", d)[0]
    song = idx(9, lambda r: r["name"] == "Song of Eärendil" and r["fromZone"] == "library", d)[0]
    ids = {d[8][j]["id"] for j in k}
    return len(k) == 2 and len(ids) == 1 and k[0] < t0 < pres < k[1] < song
def c5():
    d = copy.deepcopy(T)
    d[8] = [r for j, r in enumerate(d[8]) if j != 42]   # sem a 2ª Kiora
    return t5(d)
teste("T9: Kiora (mesmo id) 1ª vez < Resurgent Time=0 < Presence volta < 2ª Kiora < compra da Song", t5, c5)

# 6. T9: 2 tokens Kraken com ids distintos no log (a 1ª sumiu sem registro; o usuário diz que ficou 1) e 1 única compra de Presence no T9 (a Song)
def t6(d):
    kr = [r["id"] for r in d[8] if r["token"] and r["name"] == "Kraken" and r["fromZone"] is None and r["toZone"] == "battlefield"]
    lib = [r["name"] for r in d[8] if r["fromZone"] == "library" and r["toZone"] == "hand"]
    return len(kr) == 2 and len(set(kr)) == 2 and lib == ["Karn's Bastion", "Song of Eärendil"]
teste("T9: 2 Krakens com ids distintos no log (1 real, segundo o usuário) e só 2 compras", t6, lambda: t6(sem_evento(T, 9, 43, 43)))

# 7. T10: nenhuma Saga ganha marcador no T10 (Jugan, Iroan, ITDBT, Kiora ficam em 1), mas Tom termina com 4 e o Kraken (o do idx 43) com 1, e há 1 Wraith novo
def t7(d):
    sagas = {"Jugan Defends the Temple // Remnant of the Rising Star", "The First Iroan Games", "In the Darkness Bind Them", "Kiora Bests the Sea God"}
    sem_lore = not any(r["name"] in sagas for r in d[9])
    tom = [r for r in d[9] if r["name"] == "Tom Bombadil"][-1]["counters"].get("+1 / +1", {}).get("count")
    kr = [r for r in d[9] if r["name"] == "Kraken"][-1]["counters"].get("+1 / +1", {}).get("count")
    wr = [r for r in d[9] if r["token"] and r["name"] == "Wraith" and r["toZone"] == "battlefield"]
    return sem_lore and tom == 4 and kr == 1 and len(wr) == 1
def c7():
    d = copy.deepcopy(T)
    d[9].append(copy.deepcopy([r for r in d[8] if r["name"] == "In the Darkness Bind Them" and r["toZone"] == "battlefield"][0]))
    return t7(d)
teste("T10: nenhum marcador de saber novo; efeitos do cap. II aplicados (Tom +4, Kraken +1, 1 Wraith)", t7, c7)

# 8. T7: Human Soldier criado só no T7 (depois do Lore=2 da Iroan; cap. I atrasado) e virado no mesmo turno (enjoo); nenhuma ficha Human Soldier no T6
def t8(d):
    criou7 = idx(7, lambda r: r["token"] and r["name"] == "Human Soldier" and r["toZone"] == "battlefield", d)
    ir2 = idx(7, lambda r: r["name"] == "The First Iroan Games" and (r["counters"].get("Lore") or {}).get("count") == 2, d)
    virado = idx(7, lambda r: r["token"] and r["name"] == "Human Soldier" and r["tapped"], d)
    no6 = idx(6, lambda r: r["token"] and r["name"] == "Human Soldier", d)
    return len(criou7) == 1 and ir2 and criou7[0] > ir2[0] and virado and virado[0] > criou7[0] and not no6
teste("T7: Soldier criado depois do Lore=2 da Iroan e virado no mesmo turno; nenhum Soldier no T6", t8, lambda: t8(sem_evento(T, 7, 12, 12)))

# 9. T6: Jugan entra e vai ao cemitério; a compra da Presence (Plains) vem depois mesmo assim; Fold into Aether já estava na zona do oponente desde o T5
def t9(d):
    j = idx(6, lambda r: r["name"].startswith("Jugan") and r["toZone"] == "battlefield", d)[0]
    g = idx(6, lambda r: r["name"].startswith("Jugan") and r["toZone"] == "graveyard", d)[0]
    pl = idx(6, lambda r: r["name"] == "Plains" and r["fromZone"] == "library", d)[0]
    fold5 = idx(5, lambda r: r["name"] == "Fold into Aether" and r["zone"] == "opponentsCards", d)
    mon = [r for t in d for r in t if r["token"] and r["name"] == "Human Monk"]
    return j < g < pl and fold5 and len(mon) == 1 and mon[0] is not None and d[8].index(mon[0]) >= 0
def c9():
    d = copy.deepcopy(T)
    d[5] = [r for r in d[5] if not (r["name"].startswith("Jugan") and r["toZone"] == "graveyard")]
    return t9(d)
teste("T6: Jugan → cemitério antes da compra da Plains (Presence vê a conjuração anulada); Fold into Aether no T5; Monk só no T9", t9, c9)

# 10. T8→T9: Austere manda 4 encantamentos ao cemitério no T8; a Fertile Ground só vai no T9, antes da Karn's Bastion entrar
def t10(d):
    t8 = {r["name"] for r in d[7] if r["toZone"] == "graveyard"}
    fg = idx(9, lambda r: r["name"] == "Fertile Ground" and r["toZone"] == "graveyard", d)
    kb = idx(9, lambda r: r["name"] == "Karn's Bastion" and r["toZone"] == "battlefield", d)
    return t8 >= {"Enchantress's Presence", "Prismatic Omen", "In the Darkness Bind Them", "The First Iroan Games"} and "Fertile Ground" not in t8 and fg and kb and fg[0] < kb[0]
teste("T8: Austere leva 4 encantamentos; Fertile Ground só no T9, antes da Karn's Bastion", t10, lambda: t10(sem_evento(T, 9, 10, 10)))

# 11. Anel: o emblema nasce no T7 já com 3 incrementos seguidos (T5 e T6 registrados atrasados), vai a 4 no T8 e nunca a 5
def t11(d):
    ring = lambda r: r["name"].startswith("The Ring")
    ger = [(ti, (r["counters"].get("Generic") or {}).get("count")) for ti, t in enumerate(d, 1) for r in t if ring(r) and r["counters"].get("Generic")]
    return [g for ti, g in ger if ti == 7] == [1, 2, 3] and [g for ti, g in ger if ti == 8] == [4] and max(g for _, g in ger) == 4
teste("Anel: Generic 1,2,3 no T7 (de uma vez), 4 no T8, nunca 5", t11, lambda: t11(sem_evento(T, 7, 18, 18)))

# 12. interações simuladas: uma por rodada de T4 a T9, nenhuma no T10
def t12(d):
    got = [[r["name"] for r in t if r["zone"] == "opponentsCards"] for t in d]
    return got == [[], [], [], ["Walker"], ["Fold into Aether"], ["Snuff Out"], ["Soul Shatter"], ["Austere Command"], ["Plant Warrior"], []]
teste("Simulador de interação: Walker T4, Fold T5, Snuff Out T6, Soul Shatter T7, Austere T8, Plant Warrior T9", t12, lambda: t12(sem_evento(T, 6, 24, 24)))

# 13. anomalia sem fonte: Iroan Lore 2→3 no T7 DEPOIS de o Tom ir ao comando (idx 40 > idx 39); no T8 ela não ganha marcador antes de morrer
def t13(d):
    tom = idx(7, lambda r: r["name"] == "Tom Bombadil" and r["toZone"] == "commandZone", d)[0]
    l3 = idx(7, lambda r: r["name"] == "The First Iroan Games" and (r["counters"].get("Lore") or {}).get("count") == 3, d)[0]
    sem8 = not idx(8, lambda r: r["name"] == "The First Iroan Games" and r["counters"].get("Lore"), d)
    return l3 > tom and sem8
teste("T7: Iroan Lore=3 só depois de o Tom sair; sem marcador da Iroan no T8", t13, lambda: t13(sem_evento(T, 7, 40, 40)))

# 14. oráculos no cache do repositório
def t14(_):
    rb = ORC["Resurgent Belief"]["oracle_text"]; ng = ORC["Nesting Grounds"]["oracle_text"]; it = ORC["In the Darkness Bind Them"]["oracle_text"]
    return "Suspend 2" in rb and "Activate only as a sorcery" in ng and "Sacrifice after IV" in it and ORC["Tom Bombadil"]["power"] == "4"
teste("oráculo (cache): Resurgent Belief Suspend 2; Nesting Grounds só como feitiço; ITDBT sacrifica após IV; Tom 4/4", t14, lambda: "Activate only as a sorcery" in ORC["Prismatic Omen"]["oracle_text"])

# 15. rulings arquivadas (Scryfall ao vivo, 2026-11-05)
def t15(rul):
    k = " ".join(c for _, c in rul["Kiora Bests the Sea God"]["rulings"])
    pr = " ".join(c for _, c in rul["Enchantress's Presence"]["rulings"])
    rb = " ".join(c for _, c in rul["Resurgent Belief"]["rulings"])
    return ("sacrifices it as soon as its chapter ability has left the stack" in k and "puts them on the stack in any order" in k
            and "you'll still draw a card" in pr and "beginning of each of your upkeeps" in rb and "remains exiled with no time counters" in rb)
def c15():
    r = copy.deepcopy(RUL)
    r["Kiora Bests the Sea God"]["rulings"] = []          # sem as rulings da Kiora a afirmação sobre a Saga tem de cair
    return t15(r)
teste("rulings arquivadas: Saga sacrificada ao sair a habilidade da pilha; ordem livre; Presence compra com a magia anulada; suspend",
      lambda _: t15(RUL), c15)

# 16. regras (CR de 2026-09-25) arquivadas
def t16(cr):
    return ("714.4." in cr and "that has triggered but not yet left the stack" in cr and "714.3c" in cr and "precombat main phase begins" in cr
            and "602.5d" in cr and "Activate only as a sorcery" in cr and "307.5" in cr and "the stack must be empty" in cr
            and "603.3b" in cr and "in any order they choose" in cr and "702.62a" in cr and "it remains exiled" in cr
            and "701.54c" in cr and "has tempted that player two or more times" in cr and "302.6" in cr)
def c16():
    cortado = "\n".join(l for l in CR.split("\n") if not l.startswith("714.4."))     # sem a 714.4 a afirmação tem de cair
    return t16(cortado)
teste("CR 2026-09-25: 714.4, 714.3c, 602.5d/307.5, 603.3b, 702.62a, 701.54c, 302.6 (texto arquivado)", lambda _: t16(CR), c16)

# 17. o analisador: 0 violações provadas e 1 anomalia (a Iroan do T7); fetch parada no fim não é violação
def t17(_):
    out = subprocess.run([sys.executable, "-I", os.path.join(aqui, "analisa_partida.py"), os.path.join(aqui, "dados", "partida.json.xz")],
                         capture_output=True, text=True, check=True).stdout
    return "**Violações provadas pelo log: 0**" in out and "**Anomalias sem fonte no log: 1" in out and "não é violação" in out
teste("analisa_partida.py: 0 violações provadas, 1 anomalia, Catacombs parada não é violação", t17, lambda: "**Violações provadas pelo log: 0**" in "**Violações provadas pelo log: 2**")

print(f"\n{sum(res)}/{len(res)} testes passam")
sys.exit(0 if all(res) else 1)
