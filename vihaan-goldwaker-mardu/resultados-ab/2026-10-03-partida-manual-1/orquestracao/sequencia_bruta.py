"""Lista, por turno, os registros do log na ordem em que aparecem, com a leitura de cada um (draw, terreno, conjuracao, tap, ficha criada,
morte, acao do oponente). Uso: python3 sequencia_bruta.py ../dados/partida.json.xz   (saida = ../resumos/sequencia_bruta.txt)"""
import json, lzma, sys
d = json.load(lzma.open(sys.argv[1], 'rt'))
LANDS = {"Mountain", "Swamp", "Plains", "Dragonskull Summit", "Tainted Peak", "Path of Ancestry", "Battlefield Forge", "Desolate Mire"}
for n, t in enumerate(d, 1):
    print(f"\n=== T{n} ({len(t)} registros)")
    for r in t:
        nm, fz, tz, z = r['name'], r['fromZone'], r['toZone'], r['zone']
        tag = ("[ficha] " if r['token'] else "") + nm
        ctr = " +ctr" + str({k: v['count'] for k, v in r['counters'].items()}) if r['counters'] else ""
        if fz == 'library' and tz == 'hand':
            ev = "compra"
        elif fz == 'library' and tz == 'exile':
            ev = "exilio do topo (Prosper/Blood Money/Lotho...)"
        elif fz == 'hand' and tz == 'battlefield':
            ev = "joga terreno" if nm in LANDS else "conjura"
        elif fz == 'commandZone':
            ev = "conjura o comandante"
        elif fz == 'exile' and tz == 'battlefield':
            ev = "joga/conjura do exilio"
        elif fz == 'graveyard' and tz == 'battlefield':
            ev = "volta do cemiterio"
        elif fz == 'battlefield' and tz == 'graveyard':
            ev = "MORRE/vai ao cemiterio"
        elif fz == 'battlefield' and tz == 'exile':
            ev = "vai ao exilio"
        elif fz == 'hand' and tz == 'graveyard':
            ev = "descartada"
        elif tz == 'opponentsCards':
            ev = "ACAO DO OPONENTE (marcador)"
        elif r['token'] and fz is None and tz == 'battlefield':
            ev = "FICHA CRIADA"
        elif fz is None and tz is None:
            ev = "virada (tap)" if r['tapped'] else "desvirada (untap) / sem mudanca de zona"
        else:
            ev = f"{fz}->{tz}"
        print(f"  {tag:34} tapped={int(r['tapped'])} {ev}{ctr}   (zona={z})")
