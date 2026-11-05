"""Lista o que ha' em cada arquivo de dados. Uso: python3 indice_dados.py > resumos/indice_dados.md   (rodar de dentro da pasta do registro)"""
import glob, json, lzma, os
aqui = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
print("| arquivo | conteúdo |\n|---|---|")
for f in sorted(glob.glob(os.path.join(aqui, "dados", "*"))):
    nome = os.path.basename(f)
    if nome.endswith(".txt"):
        n = len(open(f, encoding="utf-8").read().splitlines()); print(f"| `{nome}` | a lista do usuário, literal (export do Archidekt): {n} linhas |"); continue
    d = json.load(lzma.open(f, "rt")) if f.endswith(".xz") else json.load(open(f))
    if nome == "resolvido.json.xz":
        print(f"| `{nome}` | resposta bruta do Scryfall (`POST /cards/collection` por set + nº de colecionador) das {len(d)} linhas da lista; {sum(1 for x in d if 'card' in x)} resolvidas; {sum(1 for x in d if x.get('resolvido_por_nome'))} por fallback de nome |")
    elif nome == "edhrec_tam.json.xz":
        print(f"| `{nome}` | `json.edhrec.com/pages/commanders/tam-the-possibility.json` de 2026-10-19: {len(d['container']['json_dict']['cardlists'])} listas de cartas, média de tipos, curva, temas e brackets |")
    elif nome == "spellbook_tam.json":
        print(f"| `{nome}` | Commander Spellbook do deck exato: {len(d['reconhece'])} nomes resolvidos (não reconhecidos: {d['nao_reconhecidos']}), {len(d['deck']['incluidos'])} combos, {len(d['deck']['quase'])} \"quase\", controle positivo={d['controle_positivo_thassa_consultation']}, controle de corte={d['controle_de_corte_combo_sumiu_sem_a_consultation']} |")
    elif nome == "spellbook_combos_detalhe.json":
        print(f"| `{nome}` | variantes completas (passo-a-passo, pré-requisitos) dos {len(d)} combos achados: {', '.join(d)} |")
    else:
        print(f"| `{nome}` | {type(d).__name__} |")
