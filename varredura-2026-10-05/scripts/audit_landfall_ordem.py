"""Varredura mecanica (Regra #10): o simulador joga o TERRENO antes de conjurar o payoff de landfall?
Achado real em 2026-10-06 (Mothman, partida manual #1): `main_phase` chamava `play_land_phase` antes de `cast_loop`, entao Ruin Crab / Icetill Explorer entravam DEPOIS do terreno do turno e
nunca disparavam com ele (100% das sementes em 4 cenarios dirigidos). O jogador real conjura o payoff primeiro quando o mana de agora o paga.
Para cada simulador (exceto `_original` e `physical`): (1) quais cartas do arquivo tem gatilho de entrada de terreno (oraculo do cache do repositorio, nao memoria);
(2) em cada funcao de turno/fase (nome com main/turn/phase/step) que chama as duas coisas, a ordem das PRIMEIRAS chamadas de jogar terreno e de conjurar; (3) se ja' existe politica de payoff primeiro (`payoff_first`/`landfall_first`).
Saida: so' CANDIDATOS. Ler a mao cada um (Regra #10.1): o script nao prova que a ordem custa algo nem que o deck joga landfall de verdade.
Uso (da raiz do repositorio): python3 varredura-2026-10-05/scripts/audit_landfall_ordem.py"""
import glob, json, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CACHE = json.load(open(os.path.join(ROOT, "scryfall-cache", "oracle-cache.json")))
LF = re.compile(r"(?i)\blandfall\b|whenever (a|one or more|another) lands? (you control )?(enters?|enter)|whenever a land enters")
def texto(c):
    t = c.get("oracle_text") or ""
    return t + " " + " ".join(f.get("oracle_text") or "" for f in c.get("card_faces", []))
PAYOFFS = sorted(n for n, c in CACHE.items() if LF.search(texto(c)) and ("Creature" in (c.get("type_line") or "") or "Enchantment" in (c.get("type_line") or "") or "Artifact" in (c.get("type_line") or "")))
print(f"cartas com gatilho de landfall no cache (permanentes nao-terreno): {len(PAYOFFS)} (> 0)")
assert len(PAYOFFS) > 0
TERRENO = re.compile(r"\b(\w*(?:play_land|put_land|land_drop|land_phase)\w*)\s*\(")
CONJURA = re.compile(r"\b(\w*(?:cast_loop|cast_phase|cast_spells|cast_all|cast_what|castable|main_cast|cast_step|spend_mana)\w*)\s*\(")
FUNCS = re.compile(r"^def (\w*(?:main|turn|phase|step)\w*)\(.*?(?=^def |\Z)", re.S | re.M)
res = []
for f in sorted(glob.glob(os.path.join(ROOT, "*", "*goldfish*v*.py"))):
    b = os.path.basename(f)
    if "_original" in b or "physical" in b:
        continue
    src = open(f, encoding="utf-8").read()
    achados = sorted(n for n in PAYOFFS if re.search(r'["\']' + re.escape(n) + r'["\']', src))
    ordens = []
    for m in FUNCS.finditer(src):
        corpo = m.group(0)
        t = TERRENO.search(corpo); c = CONJURA.search(corpo)
        if t and c:
            ordens.append(f"{m.group(1)}: {'TERRENO(' + t.group(1) + ') ANTES de CONJURAR(' + c.group(1) + ')' if t.start() < c.start() else 'conjurar antes do terreno'}")
    ordem = "; ".join(ordens) if ordens else "nenhuma funcao de turno/fase com as duas chamadas"
    pol = bool(re.search(r"payoff_first|landfall_first|PAYOFF_FIRST", src))
    res.append((b, achados, ordem, pol))
print()
n_cand = 0
for b, ach, ordem, pol in res:
    cand = bool(ach) and "TERRENO(" in ordem and not pol
    n_cand += cand
    print(f"{b}: payoffs de landfall no arquivo = {', '.join(ach) if ach else '-'} | politica payoff-primeiro: {'sim' if pol else 'nao'}\n    ordem: {ordem}{'   <== CANDIDATO' if cand else ''}")
print(f"\n{len(res)} simuladores varridos; {n_cand} candidatos (landfall no arquivo + terreno antes de conjurar + sem politica). Falsos positivos possiveis: carta no arquivo mas fora da lista; payoff que nao importa a ordem.")
assert len(res) > 0
