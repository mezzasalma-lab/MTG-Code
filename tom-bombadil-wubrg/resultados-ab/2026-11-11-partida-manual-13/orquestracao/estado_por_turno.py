import json,lzma,os,sys
aqui=os.path.dirname(os.path.abspath(__file__))
T=json.load(lzma.open(sys.argv[1] if len(sys.argv)>1 else os.path.join(aqui,'..','dados','partida.json.xz')))
# ATENÇÃO: o log NAO registra ficha que some (#11 e #12): fichas destruidas continuam 'vivas' neste dump (ex.: 2 Kraken; Wraith/Soldier mortos pela Austere T8)
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
