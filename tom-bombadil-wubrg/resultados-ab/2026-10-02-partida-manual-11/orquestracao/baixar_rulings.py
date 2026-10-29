import json,sys,urllib.request,urllib.parse,time,ssl
names=["Narci, Fable Singer","Tom Bombadil","Starfield of Nyx","Historian's Boon","Goldberry, River-Daughter","Resurgent Belief","Nexus Mentality","Teferi's Protection","Soul Shatter","Martial Coup","All Is Dust","Bane of Progress","Power Conduit","Summon: Fenrir","Summon: Primal Odin","War of the Last Alliance","The Cruelty of Gix","There and Back Again","The Eldest Reborn","Jugan Defends the Temple","Satsuki, the Living Lore","Sanctum Weaver","Barbara Wright","Blasphemous Edict","Faeburrow Elder","O'aka, Traveling Merchant","In the Darkness Bind Them","Binding the Old Gods","Jace's Archivist","Lethal Scheme","Casualties of War","Prismatic Omen","Utopia Sprawl","Fertile Ground","Scholar of New Horizons","Flux Channeler"]
out={}
for n in names:
    u="https://api.scryfall.com/cards/named?"+urllib.parse.urlencode({"exact":n})
    try:
        H={"User-Agent":"MTG-Code-audit/1.0","Accept":"application/json"}
        c=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H)))
        r=json.load(urllib.request.urlopen(urllib.request.Request(c["rulings_uri"],headers=H)))
        out[n]={"oracle_id":c.get("oracle_id"),"rulings":[(x["published_at"],x["comment"]) for x in r["data"]]}
    except Exception as e:
        out[n]={"erro":str(e)}
    time.sleep(0.12)
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
print(len(out),'cartas')
