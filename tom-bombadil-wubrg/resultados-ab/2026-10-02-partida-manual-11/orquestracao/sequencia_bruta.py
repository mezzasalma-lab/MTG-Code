import json,lzma,sys
T=json.load(lzma.open('tom-bombadil-wubrg/resultados-ab/2026-10-02-partida-manual-11/dados/partida.json.xz'))
a,b=int(sys.argv[1]),int(sys.argv[2])
for i in range(a,b+1):
    print(f"\n--- T{i}")
    for j,r in enumerate(T[i-1]):
        s=r['name'].split(' // ')[0]
        if r['token']: s='['+s+']'
        mv=f"{r['fromZone']}->{r['toZone']}" if r['toZone'] else ''
        c=','.join(f"{k}={v['count']}" for k,v in r['counters'].items())
        print(f"{j:2d} {s:32s} {r['zone']:11s} {mv:26s} {'T' if r['tapped'] else '-'}{'F' if r['flipped'] else ' '} {c} {('tax'+str(r['commandTax'])) if r['commandTax'] else ''}")
