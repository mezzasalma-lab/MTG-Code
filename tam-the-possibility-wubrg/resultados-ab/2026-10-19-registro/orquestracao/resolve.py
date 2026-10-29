import re, json, urllib.request, time, sys
pat=re.compile(r"^(\d+)x (.+?) \((\w+)\) (\S+)( \*F\*)? \[(.+?)\]$")
rows=[]
for l in open("lista_original.txt").read().splitlines():
    m=pat.match(l); q,nome,s,cn,f,cat=m.groups(); rows.append({"linha":l,"qtd":int(q),"nome_lista":nome,"set":s,"cn":cn,"foil":bool(f),"cat":cat})
def post(ids):
    req=urllib.request.Request("https://api.scryfall.com/cards/collection",data=json.dumps({"identifiers":ids}).encode(),headers={"Content-Type":"application/json","User-Agent":"mtg-code/1.0","Accept":"application/json"})
    return json.load(urllib.request.urlopen(req))
res={}; nf=[]
for i in range(0,len(rows),50):
    ch=rows[i:i+50]; r=post([{"set":x["set"],"collector_number":x["cn"]} for x in ch])
    got={ (c["set"],c["collector_number"].lower()):c for c in r["data"]}
    for x in ch:
        c=got.get((x["set"],x["cn"].lower()))
        if c: x["card"]=c
        else: nf.append(x)
    time.sleep(0.2)
print("resolvidas por set+numero:",sum(1 for x in rows if "card" in x),"de",len(rows)); print("nao resolvidas:",[(x["nome_lista"],x["set"],x["cn"]) for x in nf])
# fallback por nome
for x in nf:
    r=post([{"name":x["nome_lista"]}])
    if r["data"]: x["card"]=r["data"][0]; x["resolvido_por_nome"]=True
    else: print("NAO ACHADA:",x["nome_lista"])
json.dump(rows,open("resolvido.json","w"),ensure_ascii=False,indent=0)
dif=[(x["nome_lista"],x["card"]["name"],x["card"].get("flavor_name")) for x in rows if "card" in x and x["card"]["name"]!=x["nome_lista"]]
print("nome da lista != nome real do Scryfall:",dif)
