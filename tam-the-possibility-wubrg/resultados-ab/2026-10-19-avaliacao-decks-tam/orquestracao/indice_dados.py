"""Lista o que ha' em cada arquivo de dados. Uso: python3 indice_dados.py > ../resumos/indice_dados.md"""
import collections, glob, json, lzma, os
aqui = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
def carrega(f):
    if f.endswith(".jsonl.xz"): return [json.loads(l) for l in lzma.open(f, "rt", encoding="utf-8")]
    return json.load(lzma.open(f, "rt", encoding="utf-8")) if f.endswith(".xz") else json.load(open(f, encoding="utf-8"))
print("| arquivo | conteúdo |\n|---|---|")
for f in sorted(glob.glob(os.path.join(aqui, "dados", "*"))):
    nome = os.path.basename(f); d = carrega(f)
    if nome == "decks_edhrec.jsonl.xz":
        src = collections.Counter(r["url"].split("/")[2] for r in d); brk = collections.Counter(r["bracket"] for r in d)
        print(f"| `{nome}` | {len(d)} decks do Tam baixados do EDHREC (`edhrec.com/api/deckpreview/<urlhash>`, campos úteis): por site de origem {dict(sorted(src.items()))}; por bracket {dict(sorted(brk.items(), key=lambda kv: str(kv[0])))} |")
    elif nome == "oraculos_referencia.json.xz":
        print(f"| `{nome}` | oráculo (Scryfall `POST /cards/collection` por nome) de {len(d)} cartas distintas dos decks de referência e das candidatas; {sum(1 for v in d.values() if v.get('game_changer'))} com `game_changer` |")
    elif nome == "rulings_candidatas.json":
        print(f"| `{nome}` | oráculo, `game_changer` e rulings (Scryfall, ao vivo) de {len(d)} cartas (candidatas e cartas do deck que elas tocam); {sum(len(v.get('rulings', [])) for v in d.values())} rulings no total |")
    elif nome == "spellbook_adicoes.json":
        print(f"| `{nome}` | Commander Spellbook, deck exato + uma candidata por vez: {len(d['reconhece'])} nomes resolvidos (não reconhecidos: {d['nao_reconhecidos']}), {len(d['adicoes'])} candidatas, controle positivo={d['controle_positivo']}, controle de corte={d['controle_de_corte']} |")
    elif nome == "spellbook_trocas.json":
        print(f"| `{nome}` | Commander Spellbook, cada troca do pacote, o pacote inteiro e 5 opções: {len(d['reconhece'])} nomes resolvidos (não reconhecidos: {d['nao_reconhecidos']}), {len(d['trocas'])} cenários, controle positivo={d['controle_positivo']}, controle de corte={d['controle_de_corte']} |")
    elif nome == "spellbook_carth_variante.json":
        print(f"| `{nome}` | variante completa (passo-a-passo e pré-requisitos) do combo que o Carth cria: {', '.join(x['combo'] + ' [' + x['id'] + ']' for x in d)} |")
    else:
        print(f"| `{nome}` | {type(d).__name__} |")
