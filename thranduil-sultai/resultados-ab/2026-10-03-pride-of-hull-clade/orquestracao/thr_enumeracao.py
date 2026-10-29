"""Enumeração POR SCRIPT (type_line + oracle_text ao vivo do oracle-cache) das condições da Pride no Thranduil.
Roda a varredura por texto e uma 2ª por efeito/alvo (protocolo de avaliação, passo 5)."""
import json, re, sys
REPO = "/home/user/MTG-Code"
C = json.load(open(f"{REPO}/scryfall-cache/oracle-cache.json"))
sec = None; cards = []
for l in open(f"{REPO}/thranduil-sultai/lista.md"):
    l = l.rstrip("\n")
    if l.startswith("#"): sec = l.lstrip("# ").lower(); continue
    m = re.match(r"^(\d+)\s+(.+)$", l)
    if m and sec and not sec.startswith("comandante"): cards += [m.group(2)] * int(m.group(1))
cmd = "Thranduil, the Elvenking"
def faces(n):
    e = C.get(n) or C.get(n.split(" // ")[0])
    if e.get("card_faces"): return e["card_faces"]
    return [e]
def tl(n): return " // ".join((f.get("type_line") or "") for f in faces(n))
def ot(n): return " // ".join((f.get("oracle_text") or "") for f in faces(n))
creat = [n for n in sorted(set(cards) | {cmd}) if "Creature" in tl(n).split(" // ")[0] or re.search(r"Creature", tl(n))]
elf = [n for n in creat if "Elf" in tl(n) or "Changeling" in ot(n)]
nonelf = [n for n in creat if n not in elf]
print(f"Criaturas (inclui comandante): {len(creat)} | Elfos: {len(elf)} | não-Elfos: {len(nonelf)}")
print("Não-Elfos:", sorted(nonelf))
print("Elfos lendários:", len([n for n in elf if "Legendary" in tl(n)]))
land = [n for n in cards if "Land" in tl(n)]
print("Terrenos na lista:", len(land), "| não-terrenos:", len(cards) - len(land))
def tough(n):
    f = faces(n)[0]; t = f.get("toughness")
    try: return int(t)
    except (TypeError, ValueError): return None
ts = [(n, tough(n)) for n in creat]
vals = [t for _, t in ts if t is not None]
print("Toughness impresso das criaturas: média %.2f, mediana %s, >=5: %s" % (sum(vals)/len(vals), sorted(vals)[len(vals)//2], [n for n, t in ts if t and t >= 5]))
print("-- Cartas que se importam com toughness/defender no texto (varredura 1):", [n for n in sorted(set(cards) | {cmd}) if re.search(r"toughness|defender", ot(n), re.I)])
print("-- Anthems/pumps de +X/+X (varredura 2, efeito):")
for n in sorted(set(cards) | {cmd}):
    t = ot(n)
    if re.search(r"get \+\d/\+\d|gets \+\d/\+\d|\+X/\+X|\+1/\+1 counter", t) and "Land" not in tl(n):
        print("   ", n, "|", re.sub(r"\s+", " ", t)[:150])
print("-- Fontes de compra (draw):")
for n in sorted(set(cards) | {cmd}):
    if re.search(r"draw (a card|two cards|cards|X cards)|draws a card|you may draw", ot(n), re.I) and "Land" not in tl(n):
        print("   ", n, "|", re.sub(r"\s+", " ", ot(n))[:130])
print("-- Efeitos que SACRIFICAM/DESTROEM criatura não-Elfo ou todas as não-do-tipo (anti-sinergia com um Pride não-Elfo):")
for n in sorted(set(cards) | {cmd}):
    t = ot(n)
    if re.search(r"non-Elf|aren't of the chosen type|sacrifices a non", t, re.I): print("   ", n, "|", re.sub(r"\s+", " ", t)[:160])
print("-- Fontes de U (terrenos):", sum(1 for n in land if re.search(r"\{U\}|Island|any color", ot(n)) or "Island" in tl(n)))
print("-- Tutores/revelações de criatura (candidatos: pelo oráculo só Fauna Shaman busca QUALQUER criatura; Vannifar exige sacrificar MV 10; Kindred Summons só traz o tipo escolhido):", sorted(n for n in set(cards) if re.search(r"search your library for a (creature|Elf)|reveal cards from the top of your library until you reveal", ot(n), re.I)))
