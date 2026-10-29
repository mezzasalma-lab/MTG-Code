"""Utilitarios comuns: carrega o simulador do Vihaan ANTES (commit a17049f, lista com Blood Money) e DEPOIS (arquivo vivo, lista com Mythos of Snapdax) como modulos separados e gera a
impressao digital do estado final. O simulador le 'lista.md' DA PASTA ATUAL no import: o carregador faz chdir pro deck (DEPOIS) ou pra `resultados-ab/_lista_legada` (ANTES, que nao conhece a
Mythos e precisa da lista de a17049f)."""
import hashlib, importlib.util, os, sys

DECK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEGADO = os.path.join(DECK, "resultados-ab", "_lista_legada")
ANTES = os.path.join(HERE, "codigo", "vihaan_goldfish_v1_ANTES_a17049f.py")    # 11a rodada: lista com Blood Money
DEPOIS = os.path.join(DECK, "vihaan_goldfish_v1.py")
NOVOS = {"interaction_rng", "super_nova_emblems", "seph_batch_active", "seph_batch_front_up", "seph_batch_emblems", "seph_batch_leaves",
         "sephiroth_extra_triggers_total", "impulse_lands", "impulse_lands_played_total", "impulse_spells_cast_total", "lotho_triggers_total",
         "treasures_sacrificed_this_turn", "storm_sac_baseline", "storm_pump_total", "sevinne_nonpermanent_returns_total",
         "dictate_triggers_total", "treasure_farm_total", "impulse_expiring_first_total", "impulse_all_first_total",
         "treasure_farm_dictate_total", "treasures_tapped", "own_wipes_cast_total", "blood_money_cast_total", "own_wipe_commander_destroyed_total",
         "own_wipe_tapped_treasures_total", "own_wipe_held_total", "own_wipe_held_this_turn",
         "own_wipe_mitigated_casts_total", "own_wipe_animated_paid_total", "own_wipe_pay_drain_total",
         "mythos_cast_total", "mythos_br_spent_total", "mythos_br_pending", "mythos_perm_lost_total"}


def carrega(caminho, nome):
    os.chdir(LEGADO if caminho == ANTES else DECK)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def flags(m, mythos=True, cor=True, hold=True, cascata=None):
    """A correcao da 12a rodada: `mythos` = a lista tem Mythos of Snapdax no lugar do Blood Money (desligada, a biblioteca volta a ter o Blood Money na posicao antiga: bit-identico a
    a17049f); `cor` = a Mythos so' e' conjuravel com `{W}{W}` nas fontes em campo; `hold` = a retencao de TODO wipe proprio (10a rodada: ligada, como no repositorio; `hold=False`
    liga a variante "sem retencao", so' pra medir o efeito de conjurar); `cascata` = o cascade recusa o wipe proprio segurado (padrao: o mesmo valor de `mythos`, ou seja,
    `mythos=False` volta a ser TUDO de a17049f, inclusive o cascade que conjurava wipe a forca). As chaves anteriores ficam como no repositorio. Cada chave so' e' definida se existir no modulo (o snapshot
    antigo nao tem as da 12a)."""
    if hasattr(m, "MYTHOS_REPLACES_BLOOD_MONEY_ENABLED"):
        m.MYTHOS_REPLACES_BLOOD_MONEY_ENABLED = mythos
        m.BASE_LIBRARY = m.build_library()   # a biblioteca e' montada no import: refaz com a chave nova
    if hasattr(m, "MYTHOS_COLOR_CHECK_ENABLED"):
        m.MYTHOS_COLOR_CHECK_ENABLED = cor
    if hasattr(m, "CASCADE_DECLINE_HELD_WIPES_ENABLED"):
        m.CASCADE_DECLINE_HELD_WIPES_ENABLED = mythos if cascata is None else cascata
    if not hold:
        for nome in ("OWN_WIPE_HOLD_ALWAYS_ENABLED", "OWN_WIPE_HOLD_ENGINE_ENABLED"):
            if hasattr(m, nome):
                setattr(m, nome, False)
    return m


def impressao(state, norm=False):
    """`norm=True`: o nome "Mythos of Snapdax" vira "Blood Money" antes do hash, pra comparar partidas COM e SEM a troca (a biblioteca/mao/cemiterio carregam o nome da carta, entao sem isto
    nenhuma partida de uma variante com troca seria 'igual' a de ANTES, mesmo que a carta nunca tenha sido comprada)."""
    partes = []
    for k in sorted(vars(state)):
        if k in NOVOS:
            continue
        v = getattr(state, k)
        if isinstance(v, set):
            v = sorted(v)
        partes.append(f"{k}={v!r}")
    texto = "|".join(partes)
    if norm:
        texto = texto.replace("Mythos of Snapdax", "Blood Money")
    return hashlib.sha1(texto.encode()).hexdigest()


def escolha_legal(V, vivos, tok):
    """A Mythos of Snapdax deixa em campo, por jogador, "an artifact, a creature, an enchantment, and a planeswalker" ESCOLHIDOS (um objeto por tipo; o mesmo objeto pode ser escolhido pra
    varios tipos, ruling 2020-04-17). Um conjunto de sobreviventes e' LEGAL se da' pra atribuir cada sobrevivente a um SLOT DISTINTO (artefato / criatura / encantamento; nao ha' planeswalker
    na lista) cujo tipo ele tem. Um objeto escolhido como "o artefato" pode ser tambem criatura (Academy Manufactor, Treasure animado, Construct) e continua em campo: por isso "no maximo 1
    criatura" NAO e' o invariante certo (a 1a versao dele dava falso positivo). `vivos` = nomes nomeados que sobraram; `tok` = fichas que sobraram (con, oth, dra, anim, inan, clues, foods)."""
    objs = []
    for n in vivos:
        objs.append({t for t, ok in (("A", V.is_artifact_card(n)), ("C", V.is_creature_card(n)), ("E", V.is_enchantment_card(n))) if ok})
    for k, tipos in (("con", "AC"), ("oth", "C"), ("dra", "C"), ("anim", "AC"), ("inan", "A"), ("clues", "A"), ("foods", "A")):
        objs += [set(tipos)] * max(0, tok[k])
    if any(v < 0 for v in tok.values()) or len(objs) > 3 or any(not o for o in objs):
        return False

    def casa(i, usados):
        if i == len(objs):
            return True
        return any(t not in usados and casa(i + 1, usados | {t}) for t in objs[i])
    return casa(0, frozenset())
