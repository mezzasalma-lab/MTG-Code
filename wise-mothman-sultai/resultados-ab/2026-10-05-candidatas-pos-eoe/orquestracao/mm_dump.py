import json, sys
def tl(c): return c.get('type_line') or " // ".join(f['type_line'] for f in c.get('card_faces', []))
def mc(c): return c.get('mana_cost') or " // ".join(f.get('mana_cost', '') for f in c.get('card_faces', []))
def txt(c):
    if c.get('card_faces') and not c.get('oracle_text'):
        return "\n  // ".join(f"[{f['name']} {f.get('mana_cost','')} | {f['type_line']}{' '+f['power']+'/'+f['toughness'] if f.get('power') else ''}] {f.get('oracle_text','')}" for f in c['card_faces'])
    return c.get('oracle_text', '')
def dump(c):
    pt = f" {c['power']}/{c['toughness']}" if c.get('power') else ""
    return f"## {c['name']} {mc(c)} | {tl(c)}{pt}\n  " + txt(c).replace("\n", "\n  ")
if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    for o in sorted(d, key=lambda o: ((o['carta'].get('cmc', 0) or 0), o['carta']['name'])):
        c = o['carta']
        if 'Basic Land' in tl(c): continue
        print(dump(c))
