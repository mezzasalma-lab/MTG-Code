import json, re, sys
idx=json.load(open(sys.argv[1]+"/candidatas_indice.json"))
cat=sys.argv[2]
RX={
 "contra": r"counter target (spell|noncreature|creature|activated|triggered)|counter (that|target) spell",
 "draw": r"draw (two|three|a|that many|X) cards?|you draw a card",
 "wipe": r"destroy all creatures|all creatures get -|each creature gets -|exile all creatures|return all creatures|each creature you don't control|destroy each creature",
 "removal": r"destroy target creature|exile target creature|target creature gets -|-\d/-\d until|deals? \d+ damage to target creature|destroy target (nonland )?permanent|exile target (nonland )?permanent|return target (nonland )?permanent",
 "ramp": r"search your library for a (basic )?land|search your library for a (Forest|basic Forest)|add (\{[WUBRGC]\}|one mana|X mana|an amount)|Treasure token|put (a|up to two|up to three) land cards? .* onto the battlefield|additional land",
 "protecao": r"hexproof|indestructible|phase out|ward|can't be countered|regenerate",
 "recursion": r"return (target|up to .*) (creature|permanent|land) cards? from your graveyard|from your graveyard to the battlefield|may cast .* from your graveyard|put .* from (a|your) graveyard onto the battlefield",
}
rx=re.compile(RX[cat],re.I)
maxcmc=float(sys.argv[3]) if len(sys.argv)>3 else 99
only_ined="--ined" in sys.argv
rows=[]
for o,v in idx.items():
    if re.search(r"\bLand\b", v['tipo'].split("//")[0]): continue
    if (v['cmc'] or 0)>maxcmc: continue
    if only_ined and not v['inedita']: continue
    if rx.search(v['oraculo']): rows.append(v)
rows.sort(key=lambda v:(v['cmc'] or 0, v['nome']))
print(f"## {cat} (cmc<={maxcmc}): {len(rows)}")
for v in rows:
    sets=",".join(sorted({s for _,s in v['sets']}))
    pt=f" {v['pt'][0]}/{v['pt'][1]}" if v['pt'][0] is not None else ""
    print(f"- {v['nome']} {v['custo']} | {v['tipo']}{pt} | {v['ci'] or 'C'} | [{sets}]{' INED' if v['inedita'] else ''}{' GC' if v['game_changer'] else ''}{' NL' if v['nao_lancada'] else ''} ${v['usd_min']} :: "+v['oraculo'].replace("\n"," / ")[:200])
