import json,sys
T='/root/.claude/projects/-home-user-MTG-Code/6f4db589-169e-5ac7-b0c5-42b29015f83f.jsonl'
dec=json.JSONDecoder()
last=None
with open(T,'r') as f:
    for line in f:
        try: o=json.loads(line)
        except: continue
        m=o.get('message') or {}
        if m.get('role')!='user': continue
        c=m.get('content')
        txt=''
        if isinstance(c,str): txt=c
        elif isinstance(c,list):
            for b in c:
                if isinstance(b,dict) and b.get('type')=='text': txt+=b.get('text','')
        if 'Fiz um goldfish mais longo' in txt and 'Raugrin Triome' in txt:
            last=txt
print(len(last) if last else None, file=sys.stderr)
i=last.index('[\n  [')
data,end=dec.raw_decode(last[i:])
print(len(data),'turnos',file=sys.stderr)
json.dump(data,open(sys.argv[1],'w'),ensure_ascii=False)
