import json,lzma,sys
T=json.load(lzma.open('tom-bombadil-wubrg/resultados-ab/2026-10-02-partida-manual-11/dados/partida.json.xz'))
st={}
def cnt(r):
    return ','.join(f"{k}={v['count']}" for k,v in r['counters'].items())
for i,t in enumerate(T,1):
    seq=[]
    for r in t:
        st[r['id']]=r
    print(f"\n=== FIM T{i}")
    for z in ['battlefield','hand','graveyard','commandZone','opponentsCards']:
        items=[r for r in st.values() if r['zone']==z]
        if z=='hand' or z=='opponentsCards': 
            print(z,':',', '.join(r['name'] for r in items))
            continue
        out=[]
        for r in items:
            s=r['name'].split(' // ')[0]
            if r['token']: s='['+s+']'
            if r['tapped']: s+='(T)'
            if r['flipped']: s+='(flip)'
            c=cnt(r)
            if c: s+='{'+c+'}'
            if r['commandTax']: s+=f"tax{r['commandTax']}"
            out.append(s)
        print(z,f'({len(items)})',':',', '.join(out))
