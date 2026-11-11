"""Testes dirigidos da partida manual #13 (Tom Bombadil): cada afirmação do goldfish-log/LEIAME que depende do log bruto é conferida contra `dados/partida.json.xz`;
as que dependem de oráculo/ruling/regra, contra o cache do repositório, `resumos/rulings_scryfall.json` (Scryfall ao vivo, 2026-11-11) e `resumos/cr_2026-09-25_trechos.txt`.
Cada teste tem um CONTROLE DE CORTE (a afirmação tem de FALHAR no dado alterado), para o teste não passar no vazio.
Uso: python3 -I testes_manual13.py   (uma linha por teste; sai com 1 se algum falhar)
O que estes testes NÃO provam: a intenção do usuário (ver as respostas de 2026-11-11 no LEIAME), a cor da mana, o que o log não registra (fichas que somem, mill/interação de oponente)."""
import copy, json, lzma, os, subprocess, sys
aqui = os.path.dirname(os.path.abspath(__file__))
T = json.load(lzma.open(os.path.join(aqui, "dados", "partida.json.xz")))
RUL = json.load(open(os.path.join(aqui, "resumos", "rulings_scryfall.json")))
CR = open(os.path.join(aqui, "resumos", "cr_2026-09-25_trechos.txt"), encoding="utf-8").read()
ORC = json.load(open(os.path.join(aqui, "..", "..", "..", "scryfall-cache", "oracle-cache.json")))
res = []
lore = lambda r: (r["counters"].get("Lore") or {}).get("count")


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


def sem_evento(d, ti, j):
    d = copy.deepcopy(d)
    d[ti - 1] = [r for k, r in enumerate(d[ti - 1]) if k != j]
    return d


def troca(d, ti, a, b):
    d = copy.deepcopy(d)
    d[ti - 1][a], d[ti - 1][b] = d[ti - 1][b], d[ti - 1][a]
    return d


# 1. 1 terreno jogado da mão por turno (objetos distintos), T1–T7: Foothills, Tower, Shrine, Garden, Sanctum, —, —
def t1(d):
    esp = {1: "Wooded Foothills", 2: "Command Tower", 3: "Godless Shrine", 4: "Temple Garden", 5: "Serra's Sanctum"}
    for ti, t in enumerate(d, 1):
        ev = {r["id"]: r["name"] for r in t if r["fromZone"] == "hand" and r["toZone"] == "battlefield" and "Land" in (ORC.get(r["name"], {}).get("type_line") or "")}
        if list(ev.values()) != ([esp[ti]] if ti in esp else []):
            return False
    return True
def c1():
    d = copy.deepcopy(T)
    extra = copy.deepcopy(next(r for r in d[4] if r["name"] == "Serra's Sanctum" and r["fromZone"] == "hand")); extra["id"] += "x"; extra["name"] = "Temple Garden"
    d[4].append(extra)
    return t1(d)
teste("1 terreno da mão por turno em T1–T7 (Foothills, Tower, Shrine, Garden, Sanctum, —, —)", t1, c1)

# 2. T1: Wooded Foothills jogada, sacrificada e busca da Ziatora's Proving Ground (tipos Mountain e Forest: alvo legal da Foothills)
def t2(d):
    fo = [r for r in d[0] if r["name"] == "Wooded Foothills"]
    ok_fo = [r["toZone"] for r in fo if r["toZone"]] == ["hand", "battlefield", "graveyard"]
    zi = [r for r in d[0] if r["name"] == "Ziatora's Proving Ground" and r["fromZone"] == "library" and r["toZone"] == "battlefield"]
    tl = ORC["Ziatora's Proving Ground"]["type_line"]
    return ok_fo and len(zi) == 1 and zi[0]["tapped"] and "Mountain" in tl and "Forest" in tl and "Mountain or Forest" in ORC["Wooded Foothills"]["oracle_text"]
def c2():
    d = copy.deepcopy(T)
    for r in d[0]:
        if r["name"] == "Wooded Foothills" and r["toZone"] == "graveyard":
            r["toZone"] = "battlefield"
    return t2(d)
teste("T1: Wooded Foothills → cemitério e busca a Ziatora's Proving Ground (Mountain Forest) entrando virada", t2, c2)

# 3. compras library→mão por turno = esperado (16 = 16)
ESP = [8, 1, 1, 1, 3, 1, 1]
def t3(d):
    return [sum(1 for r in t if r["fromZone"] == "library" and r["toZone"] == "hand") for t in d] == ESP
teste("compras library→mão por turno = [8,1,1,1,3,1,1] (16 = 16)", t3, lambda: t3(sem_evento(T, 5, idx(5, lambda r: r["name"] == "Fertile Ground" and r["fromZone"] == "library")[0])))

# 4. T5: o cap. III da Iroan (marcador natural 2→3) vem ANTES das 2 compras e do Tom; o Soldier do T4 tem 3 marcadores +1/+1 (4/4): a condição de poder 4 já valia
def t4(d):
    soldier = [r["counters"].get("+1 / +1", {}).get("count") for r in d[3] if r["name"] == "Human Soldier"]
    l3 = idx(5, lambda r: r["name"] == "The First Iroan Games" and lore(r) == 3, d)[0]
    g = idx(5, lambda r: r["name"] == "Goldberry, River-Daughter" and r["fromZone"] == "library", d)[0]
    f = idx(5, lambda r: r["name"] == "Fertile Ground" and r["fromZone"] == "library", d)[0]
    tom = idx(5, lambda r: r["name"] == "Tom Bombadil" and r["fromZone"] == "commandZone", d)[0]
    return soldier[-1] == 3 and l3 < g < f < tom
teste("T5: Iroan Lore=3 < compra de Goldberry e Fertile Ground < Tom lançado; Soldier do T4 com 3 marcadores (4/4)", t4, lambda: t4(troca(T, 5, 4, 12)))

# 5. T5: Boon entra; Satsuki → Iroan 3→4 (cap. IV) → Gold → Iroan sacrificada → There and Back Again vem da biblioteca (Tom) → Anel → Angel
def t5(d):
    b = idx(5, lambda r: r["name"] == "Historian's Boon" and r["fromZone"] == "hand", d)[0]
    s = idx(5, lambda r: r["name"] == "Satsuki, the Living Lore" and r["tapped"], d)[0]
    l4 = idx(5, lambda r: r["name"] == "The First Iroan Games" and lore(r) == 4, d)[0]
    gold = idx(5, lambda r: r["name"] == "Gold" and r["token"], d)[0]
    gy = idx(5, lambda r: r["name"] == "The First Iroan Games" and r["toZone"] == "graveyard", d)[0]
    tba = idx(5, lambda r: r["name"] == "There and Back Again" and r["fromZone"] == "library", d)[0]
    ring = idx(5, lambda r: r["name"].startswith("The Ring") and r["token"], d)[0]
    ang = idx(5, lambda r: r["name"] == "Angel" and r["token"], d)[0]
    return b < s < l4 < gold < gy < tba < ring < ang
teste("T5: Boon → Satsuki → Iroan 4 → Gold → Iroan ao cemitério → There and Back Again (Tom) → Anel → Angel", t5, lambda: t5(troca(T, 5, 18, 19)))

# 6. fichas: o log tem 1 Soldier no T5 e 0 Angel no T7; o oráculo pede 2 e 1 (respostas do usuário: "Esqueci" e "Esqueci de criar o boon")
def fichas(d, nome, ti):
    return sum(1 for r in d[ti - 1] if r["token"] and r["name"] == nome and r["fromZone"] is None and r["toZone"] == "battlefield")
def t6(d):
    esp_boon = "nontoken enchantment you control enters" in ORC["Historian's Boon"]["oracle_text"] and "final chapter ability of a Saga you control triggers" in ORC["Historian's Boon"]["oracle_text"]
    return esp_boon and fichas(d, "Human Soldier", 5) == 1 and fichas(d, "Angel", 7) == 0 and fichas(d, "Angel", 5) == 1 and fichas(d, "Human Soldier", 6) == 2 and fichas(d, "Human Soldier", 7) == 1
def c6():
    d = copy.deepcopy(T)
    extra = copy.deepcopy(next(r for r in d[6] if r["name"] == "Smaug")); extra["name"] = "Angel"; extra["id"] += "a"
    d[6].append(extra)      # se o log tivesse o Angel do T7, o teste cai
    return t6(d)
teste("fichas: T5 1 Soldier (esperado 2), T7 0 Angel (esperado 1); T5 Angel 1, T6 Soldier 2, T7 Soldier 1", t6, c6)

# 7. T7: Goldberry vira e o marcador da There and Back Again vai de 3 para 2 ANTES de o Smaug existir (cap. III ainda na pilha) → a Saga não é sacrificada (CR 714.4)
def t7(d):
    l3 = idx(7, lambda r: r["name"] == "There and Back Again" and lore(r) == 3, d)[0]
    tap = idx(7, lambda r: r["name"] == "Goldberry, River-Daughter" and r["tapped"], d)[0]
    l2 = idx(7, lambda r: r["name"] == "There and Back Again" and lore(r) == 2, d)
    smaug = idx(7, lambda r: r["name"] == "Smaug", d)[0]
    gl = idx(7, lambda r: r["name"] == "Goldberry, River-Daughter" and lore(r) == 1, d)[0]
    bind = idx(7, lambda r: r["name"] == "Binding the Old Gods" and r["fromZone"] == "library", d)[0]
    return l3 < tap < l2[-1] < smaug < gl < bind and "that has triggered but not yet left the stack" in CR
def c7():
    d = copy.deepcopy(T)
    d[6][11], d[6][12] = d[6][12], d[6][11]       # Smaug antes da remoção do marcador: a Saga já teria sido sacrificada
    return t7(d)
teste("T7: Lore 3 → Goldberry vira → Lore 2 → Smaug → Goldberry Lore=1 → Binding (Tom): remoção com o cap. III na pilha", t7, c7)

# 8. a There and Back Again continua em campo no fim do T7 (nenhum registro para o cemitério); a Iroan foi ao cemitério no T5
def t8(d):
    tba_gy = [ti for ti, t in enumerate(d, 1) for r in t if r["name"] == "There and Back Again" and r["toZone"] == "graveyard"]
    ir_gy = [ti for ti, t in enumerate(d, 1) for r in t if r["name"] == "The First Iroan Games" and r["toZone"] == "graveyard"]
    return tba_gy == [] and ir_gy == [5]
def c8():
    d = copy.deepcopy(T)
    r = copy.deepcopy(next(x for x in d[6] if x["name"] == "There and Back Again")); r["toZone"] = "graveyard"
    d[6].append(r)
    return t8(d)
teste("There and Back Again não vai ao cemitério até o T7; Iroan vai no T5", t8, c8)

# 9. o gatilho do Tom é 1 por turno: Sagas library→campo = 1 no T5 (There and Back Again) e 1 no T7 (Binding the Old Gods), 0 nos outros
def t9(d):
    sagas = {"There and Back Again", "Binding the Old Gods", "The Kami War // O-Kagachi Made Manifest", "The Cruelty of Gix"}
    return [sum(1 for r in t if r["fromZone"] == "library" and r["toZone"] == "battlefield" and r["name"] in sagas) for t in d] == [0, 0, 0, 0, 1, 0, 1]
def c9():
    d = copy.deepcopy(T)
    r = copy.deepcopy(next(x for x in d[4] if x["name"] == "There and Back Again" and x["fromZone"] == "library")); r["name"] = "Binding the Old Gods"; r["id"] += "b"
    d[4].append(r)
    return t9(d)
teste("Tom: 1 Saga da biblioteca por turno (T5 There and Back Again, T7 Binding the Old Gods)", t9, c9)

# 10. T6: o cap. II da There and Back Again (Mountain) foi aplicado (Ketria Triome, Forest Island Mountain, entra virada, da biblioteca) mas o marcador NÃO foi clicado no T6; no T7 há 2 cliques (2 e 3) para 1 só de Yojimbo (2)
def t10(d):
    k = [r for r in d[5] if r["name"] == "Ketria Triome" and r["fromZone"] == "library" and r["toZone"] == "battlefield" and r["tapped"]]
    sem_clique = not any(r["name"] == "There and Back Again" for r in d[5])
    tba7 = [lore(r) for r in d[6] if r["name"] == "There and Back Again" and lore(r) is not None]
    yo7 = [lore(r) for r in d[6] if r["name"] == "Summon: Yojimbo" and lore(r) is not None]
    return len(k) == 1 and "Mountain" in ORC["Ketria Triome"]["type_line"] and sem_clique and tba7 == [2, 3, 2] and yo7 == [2]
def c10():
    d = copy.deepcopy(T)
    r = copy.deepcopy(next(x for x in d[6] if x["name"] == "There and Back Again")); d[5].append(r)
    return t10(d)
teste("T6: Ketria Triome (Mountain) buscada e nenhum clique de saber na There and Back Again; T7: cliques 2→3→2", t10, c10)

# 11. Song of the Dryads (oponente) no T5 e o marcador `Forest` no Tom no fim do T5; no T6 o Tom aparece sem o marcador (o usuário exilou a Song com o cap. I da Yojimbo)
def t11(d):
    song5 = [r for r in d[4] if r["name"] == "Song of the Dryads" and r["toZone"] == "opponentsCards"]
    tom5 = [r for r in d[4] if r["name"] == "Tom Bombadil"][-1]
    tom6 = [r for r in d[5] if r["name"] == "Tom Bombadil"][-1]
    yo = idx(6, lambda r: r["name"] == "Summon: Yojimbo" and r["toZone"] == "battlefield", d)[0]
    tomj = idx(6, lambda r: r["name"] == "Tom Bombadil", d)[0]
    return len(song5) == 1 and tom5["counters"].get("Forest", {}).get("count") == 1 and "Forest" not in tom6["counters"] and yo < tomj
def c11():
    d = copy.deepcopy(T)
    [r for r in d[5] if r["name"] == "Tom Bombadil"][-1]["counters"]["Forest"] = {"count": 1}
    return t11(d)
teste("Song of the Dryads no Tom (T5) e Tom sem o marcador Forest no T6, depois da Yojimbo cap. I", t11, c11)

# 12. Goldberry: lançada no T6, virada no T7 (sem enjoo de invocação: CR 302.6); o oráculo move 1 marcador de cada tipo que ela não tem
def t12(d):
    cast = [ti for ti, t in enumerate(d, 1) for r in t if r["name"] == "Goldberry, River-Daughter" and r["fromZone"] == "hand" and r["toZone"] == "battlefield"]
    tap = sorted({ti for ti, t in enumerate(d, 1) for r in t if r["name"] == "Goldberry, River-Daughter" and r["tapped"]})
    return cast == [6] and tap == [7] and "Move a counter of each kind not on Goldberry from another target permanent you control onto Goldberry" in ORC["Goldberry, River-Daughter"]["oracle_text"]
def c12():
    d = copy.deepcopy(T)
    for r in d[5]:
        if r["name"] == "Goldberry, River-Daughter":
            r["tapped"] = True
    return t12(d)
teste("Goldberry lançada no T6 e virada só no T7; oráculo da 1ª habilidade", t12, c12)

# 13. oráculo e rulings: Boon dispara no "triggers" (não no sacrifício), Tom no "resolves"; ruling de 2023-06-16 do Tom; Saga: remover marcador não redispara, mas o próximo marcador redispara; Song tira todas as outras habilidades
def t13(_):
    boon = ORC["Historian's Boon"]["oracle_text"]; tom = ORC["Tom Bombadil"]["oracle_text"]
    tomr = " ".join(c for _, c in RUL["Tom Bombadil"]["rulings"]); bind = " ".join(c for _, c in RUL["Binding the Old Gods"]["rulings"]); song = " ".join(c for _, c in RUL["Song of the Dryads"]["rulings"])
    return ("ability triggers" in boon or "triggers, create a 4/4" in boon) and "resolves, reveal cards" in tom and "triggers when all of its instructions" in tomr \
        and "If lore counters are removed from a Saga, the appropriate chapter abilities will trigger again" in bind and "loses all other abilities" in song
def c13():
    return "triggers when all of its instructions" in " ".join(c for _, c in RUL["Goldberry, River-Daughter"]["rulings"])
teste("oráculo/rulings: Boon 'triggers', Tom 'resolves', capítulo redispara após remover marcador, Song tira habilidades", t13, c13)

# 14. CR de 2026-09-25 arquivada: 714.2b, 714.2e, 714.3c, 714.4 (sacrifício só com o cap. fora da pilha), 704.3, 117.5, 603.2
def t14(_):
    return all(k in CR for k in ("714.2b", "714.2e", "714.3c", "714.4. If the number of lore counters", "704.3.", "117.5.", "603.2.")) and "NAO ACHADO" not in CR and "effective as of September 25, 2026" in CR
teste("CR 2026-09-25: 714.2b, 714.2e, 714.3c, 714.4, 704.3, 117.5, 603.2 (texto arquivado)", t14, lambda: "714.9z" in CR)

# 15. o analisador: 0 violações provadas e 2 anomalias de marcador (explicadas pela Satsuki no T5 e pelos cliques de saber do T7)
def t15(_):
    out = subprocess.run([sys.executable, "-I", os.path.join(aqui, "analisa_partida.py"), os.path.join(aqui, "dados", "partida.json.xz")], capture_output=True, text=True, check=True).stdout
    return "**Violações provadas pelo log: 0**" in out and "**Anomalias sem fonte no log: 2" in out
teste("analisa_partida.py: 0 violações provadas, 2 anomalias de marcador", t15, lambda: "**Violações provadas pelo log: 0**" in "**Violações provadas pelo log: 1**")

print(f"\n{sum(res)}/{len(res)} testes passam")
sys.exit(0 if all(res) else 1)
