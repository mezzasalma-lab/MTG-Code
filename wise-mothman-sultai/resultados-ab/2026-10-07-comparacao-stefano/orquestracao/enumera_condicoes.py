"""Enumeracao POR SCRIPT (oraculo vivo do cache, nunca de memoria) das condicoes de Agent Frank Horrigan e The Master, Transcendent contra a NOSSA lista (Regra #4 item 4),
e classes funcionais das duas listas para a comparacao com a do Stefano. Triagem por regex; cada linha foi lida a mao depois. Uso: python3 enumera_condicoes.py > ../resumos/enumeracao_condicoes.txt"""
import json, os, re, collections
AQUI = os.path.dirname(os.path.abspath(__file__)); DADOS = os.path.join(AQUI, "..", "dados")
cache = json.load(open(os.path.join(AQUI, "..", "..", "..", "..", "scryfall-cache", "oracle-cache.json"), encoding="utf-8"))
d = json.load(open(os.path.join(DADOS, "diff_listas.json"), encoding="utf-8"))
def card(n): return cache.get(n) or cache.get(n.replace(" / ", " // ")) or {}
BAS = {"Forest", "Island", "Swamp"}
nossa = sorted(n for n in d["nossa"] if n not in BAS); dele = sorted(n for n in d["dele"] if n not in BAS)
def txt(n): return (card(n).get("oracle_text") or "")
def tl(n): return card(n).get("type_line") or ""
def lista(titulo, nomes, f):
    r = [n for n in nomes if f(n)]
    print(f"\n## {titulo} [{len(r)}]"); [print("  -", n, "|", tl(n)) for n in r]
    return r
print("# NOSSA lista (91 nomes, 88 nao-basicos) -- condicoes de Horrigan e Master")
lista("CRIATURA (tipo no cemiterio vira alvo da habilidade do Master; Artifact Creature conta; Vehicle NAO e criatura no cemiterio)", nossa,
      lambda n: "Creature" in tl(n).split("—")[0])
lista("Tem o subtipo Mutant (Master torna o alvo um Mutant verde 3/3; cartas da lista que se importam com 'Mutant' no oraculo: ver a classe abaixo)", nossa, lambda n: "Mutant" in tl(n))
lista("Oraculo cita 'Mutant' (alguem se importa com o tipo?)", nossa, lambda n: re.search(r"\bMutants?\b", txt(n)) is not None)
lista("Gatilho de ENTRAR em campo (valor ao ser reanimado pelo Master ou quando o Horrigan/Henge entra): 'enters'", nossa, lambda n: re.search(r"\benters\b", txt(n)) is not None and "Creature" in tl(n).split("—")[0])
lista("CONTADOR +1/+1 em criatura/artefato (proliferate x2 do Horrigan dobra o ganho; Scales/Kami/Constrictor somam)", nossa, lambda n: "+1/+1 counter" in txt(n))
lista("RAD counter (proliferate do Horrigan em jogadores)", nossa, lambda n: "rad counter" in txt(n))
lista("Outros contadores proliferaveis (quest, loyalty, lore, charge, ...)", nossa, lambda n: re.search(r"(quest|lore|charge|loyalty|-1/-1|time|age|stun|brick|shield|oil|spore|finality) counter", txt(n)) is not None or "Planeswalker" in tl(n) or "Saga" in tl(n))
lista("AMPLIFICADOR de contador (replacement 'would be put')", nossa, lambda n: "would be put" in txt(n) or ("would get" in txt(n) and "counter" in txt(n)))
lista("Gatilho de PODER / 'greatest power' / poder >= (Horrigan 8/6 e Master 2/4 alimentam)", nossa, lambda n: re.search(r"greatest power|power (\d|X|is)|power or greater|equal to its power|its power|toughness or greater|power 4 or greater|power greater", txt(n)) is not None)
lista("TRAMPLE no texto (dar/ter trample)", nossa, lambda n: "trample" in txt(n).lower())
lista("INDESTRUCTIBLE no texto", nossa, lambda n: "indestructible" in txt(n).lower())
lista("MILL no OPONENTE (alimenta o 'milled this turn' do Master nos cemiterios dele)", nossa, lambda n: re.search(r"(target (player|opponent)|each (player|opponent)|that player|any number of target players) mills?|each opponent mills|opponent.{0,20}mill|mill cards equal|rad counter", txt(n)) is not None)
lista("AUTO-MILL (alimenta o 'milled this turn' no MEU cemiterio)", nossa, lambda n: re.search(r"\byou mill\b|mill(s)? (two|three|seven|X|\d+) cards?|mills? cards equal|put the top .* into your graveyard|surveil|Sacrifice a creature: Target player mills", txt(n)) is not None)
lista("REANIMA / devolve do cemiterio ao campo (concorrem com o Master ou formam combo)", nossa, lambda n: re.search(r"from (your|a) graveyard (to|onto) the battlefield|from your graveyard.*battlefield|return.*graveyard.*battlefield|retrace|cast .* from your graveyard|play lands from your graveyard", txt(n)) is not None)
lista("COMPRA quando criatura ENTRA (Henge) -- reanimar com o Master dispara", nossa, lambda n: re.search(r"creature you control enters", txt(n)) is not None)
lista("Custo >= 6 (concorrentes de slot de topo do Horrigan {5}{B}{G}=7)", nossa, lambda n: card(n).get("cmc", 0) >= 6)
lista("RAMP/Fontes de mana nao-terreno (ramparia o Horrigan)", nossa, lambda n: "Land" not in tl(n) and re.search(r"add \{|Add \{|search your library for .* (basic )?(land|Forest)|put .* land.* onto the battlefield", txt(n)) is not None)
print("\n# CLASSES FUNCIONAIS (nossa x Stefano; triagem por regex, so' nao-basicos)")
classes = [
 ("terreno", lambda n: "Land" in tl(n) and "Creature" not in tl(n)),
 ("rampa/pedra de mana", lambda n: "Land" not in tl(n) and re.search(r"\{T\}: Add|Add \{|search your library for (a|up to).{0,40}(basic )?(land|Forest|Plains)", txt(n)) is not None and "Creature" not in tl(n).split("—")[0]),
 ("contramagica", lambda n: re.search(r"counter target (spell|noncreature spell)|Counter target", txt(n)) is not None),
 ("remocao pontual", lambda n: re.search(r"(destroy|exile) target|target creature gets -|target .{0,20}(player|creature) sacrifices|Destroy target|-X/-X", txt(n)) is not None and "Instant" in tl(n) or re.search(r"Destroy target (nonland )?permanent|Destroy target", txt(n)) is not None),
 ("varredor", lambda n: re.search(r"each creature gets|destroy all|-X/-X|all creatures|each player sacrifices|Each creature gets", txt(n)) is not None),
 ("compra", lambda n: re.search(r"[Dd]raw (a|two|three|four|X|\d+|that many) cards?|[Dd]raw a card", txt(n)) is not None),
 ("mill (qualquer)", lambda n: re.search(r"\bmills?\b", txt(n)) is not None),
 ("rad counters", lambda n: "rad counter" in txt(n)),
 ("proliferate", lambda n: "roliferate" in txt(n)),
 ("amplificador/dobrador de contador", lambda n: "would be put" in txt(n) or ("would get" in txt(n) and "counter" in txt(n))),
 ("+1/+1 counter", lambda n: "+1/+1 counter" in txt(n)),
 ("reanimacao/recursao", lambda n: re.search(r"from (your|a|their) graveyard|graveyard.{0,40}(onto|to) the battlefield|Return .* from .*graveyard", txt(n)) is not None),
 ("criatura", lambda n: "Creature" in tl(n).split("—")[0]),
]
print("| classe | nossa | Stefano |\n|---|---|---|")
for nome, f in classes:
    a = [n for n in nossa if f(n)]; b = [n for n in dele if f(n)]
    print(f"| {nome} | {len(a)} | {len(b)} |")
print()
for nome, f in classes[1:]:
    a = sorted(n for n in nossa if f(n)); b = sorted(n for n in dele if f(n))
    print(f"### {nome}\n- nossa: {', '.join(a)}\n- Stefano: {', '.join(b)}")
print("\n# Cmc medio dos nao-terrenos (X=0)")
for rot, nomes, cnt in (("nossa", nossa, d["nossa"]), ("Stefano", dele, d["dele"])):
    nt = [(card(n).get("cmc") or 0, cnt[n]) for n in nomes if "Land" not in tl(n)]
    print(rot, "nao-terrenos:", sum(q for _, q in nt), "cmc medio:", round(sum(c * q for c, q in nt) / sum(q for _, q in nt), 2), "| terrenos (slots, incl. basicos):", sum(cnt[n] for n in cnt if "Land" in tl(n) or n in BAS))
