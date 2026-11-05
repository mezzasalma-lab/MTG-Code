"""Gera, SO' dos arquivos salvos por `csb_todos.py`, (1) `RESUMO.md` central, (2) o `LEIAME.md` e o `SHA256SUMS` de cada `<deck>/resultados-ab/2026-10-28-spellbook/`, (3) o SHA256SUMS central.
Nao consulta a API. Uso: python3 -I gera_resumo.py <raiz do repositorio>"""
import glob, hashlib, json, os, re, sys
RAIZ = os.path.abspath(sys.argv[1]); DATA = "2026-10-28"
CENTRAL = os.path.join(RAIZ, "spellbook-todos-os-decks-2026-10-28")
res = json.load(open(os.path.join(CENTRAL, "dados", "resumo_todos.json"), encoding="utf-8"))
nomes = json.load(open(os.path.join(CENTRAL, "dados", "nomes_resolvidos.json"), encoding="utf-8"))["reconhece"]
TAG = {"R": "Ruthless", "S": "Spicy", "P": "Powerful", "O": "Oddball", "C": "Core", "E": "Exhibition", "B": "Banned"}


def deck_json(d):
    return json.load(open(os.path.join(RAIZ, d, "resultados-ab", f"{DATA}-spellbook", "dados", f"spellbook_{d}_{DATA}.json"), encoding="utf-8"))


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def combos_md(op):
    linhas = []
    for k, v in sorted(op["incluidos"].items(), key=lambda kv: (len(kv[1]["usa"]), kv[0])):
        linhas.append(f"  - `{v['id']}` ({len(v['usa'])} cartas, tag {v['bracketTag']} {TAG.get(v['bracketTag'], '?')}): {k} → {'; '.join(v['produz']) or '(sem feature listada)'}")
    return linhas


def _linhas(nome):
    return {l.split()[0]: l.split(None, 1)[1].strip() for l in open(os.path.join(CENTRAL, "resumos", nome), encoding="utf-8") if re.match(r"^[a-z0-9-]+ +total=", l)}
_a, _b = _linhas("log_csb_todos_execucao1_sem_bruto.txt"), _linhas("log_csb_todos.txt")
_comuns = sorted(set(_a) & set(_b)); _dif = [d for d in _comuns if _a[d] != _b[d]]
CMP_EXEC = (f"- **Duas execuções da etapa por deck** (a 1ª sem gravar o bruto: `resumos/log_csb_todos_execucao1_sem_bruto.txt`; a 2ª, que grava o bruto e é a que vale: `resumos/log_csb_todos.txt`), minutos de diferença: "
            f"{len(_comuns)} decks nas duas, **{len(_dif)} com linha diferente** (combos, tag, controles)" + (f": {', '.join(_dif)}" if _dif else "") + ". A resolução de nomes teve uma tentativa anterior que caiu por erro de rede (o log dessa tentativa não foi guardado); as duas execuções por deck usaram o mesmo cache de nomes resolvidos (`dados/nomes_resolvidos_parcial.json`).")
tags = sorted({t for r in res for t in r["bracket_estimado"]})
tot_combos = sum(max(r["n_combos"]) for r in res)
linhas = [f"# Commander Spellbook em TODOS os decks do repositório — {DATA}", "",
          "Pedido do usuário (2026-10-28): *\"Quero todos os Spellbooks sim, e salvos no repositório\"*. Esta pasta guarda o resumo; os dados de cada deck ficam em `<deck>/resultados-ab/2026-10-28-spellbook/` (resposta CRUA da API em `.json.xz`, JSON derivado, `LEIAME.md`, `SHA256SUMS`).", "",
          "## O que foi feito (e com que método)", "",
          f"- **{len(res)} decks** (todo `<deck>/lista.md` do repositório, exceto o `rat-king-verminister`, que tem a rodada própria de 2026-10-25 em `rat-king-verminister/resultados-ab/2026-10-25-rodada3-spellbook-rulings-e-correcoes/`).",
          f"- **Nomes resolvidos ANTES** (a API ignora, sem erro, nome que não reconhece; achado de 2026-10-05): {len(nomes)} nomes únicos, via `GET /cards/?q=<nome>` (face da frente conta para cartas de 2 faces); **{sum(1 for v in nomes.values() if v is None)} não reconhecidos**.",
          "- Para cada deck: `POST /find-my-combos` (comandante + lista) e `POST /estimate-bracket`. **Precons de 2 ou mais comandantes** rodam uma opção por comandante, com os outros comandantes entrando na lista.",
          "- **Controle positivo** (lista + Basalt Monolith + Rings of Brighthearth: o combo dos dois TEM de aparecer) e **controle de corte** (lista + Basalt Monolith + Mind Stone: o combo NÃO pode aparecer): "
          f"passaram em **{sum(1 for r in res if r['controles'] == [True, True])} de {len(res)}** decks.",
          "- Seções ignoradas na leitura da lista: as de notas, mudanças, sugestões, trocas, sideboard, fora do deck, cortadas/removidas e links; só se lê depois do primeiro `## Comandante`. Total de cartas lidas por deck na tabela (100, ou 99 no Captain Storm, cuja lista tem 99).", "",
          "**Legenda da coluna \"tag\"** (`bracketTag` da API, rótulos do Spellbook): " + ", ".join(f"`{k}` {v}" for k, v in TAG.items()) +
          ". **Não são os Brackets oficiais 1–4**: não verifiquei a correspondência com o texto oficial.", "",
          "## Tabela por deck", "",
          "| deck | comandante(s) | cartas | combos | de 2 cartas | \"quase\" | tag Spellbook | Game Changers | \"Bracket N\" citado em `lista.md`/`auditoria.md` (grep) |", "|---|---|---|---|---|---|---|---|---|"]
for r in res:
    linhas.append(f"| `{r['deck']}` | {' / '.join(r['comandantes'])} | {r['total']} | {'/'.join(map(str, r['n_combos']))} | {len(r['combos_2_cartas'])} | {'/'.join(map(str, r['n_quase']))} | {'/'.join(r['bracket_estimado'])} | {len(r['game_changers'])} | {', '.join(r['bracket_mencionado']) or '—'} |")
linhas += ["", "A coluna \"Bracket N citado\" é um `grep` cru de \"Bracket <dígito>\" nos dois arquivos: pode listar vários números (o deck discute 3 e 4, por exemplo) e **não é uma decisão registrada**. \"Quase\" = combos a uma carta de distância (informativo; não são sugestões de troca).", "",
           "## Combos achados, por deck (só decks com pelo menos um)", ""]
for r in res:
    if max(r["n_combos"]) == 0:
        continue
    dj = deck_json(r["deck"])
    linhas.append(f"### `{r['deck']}` — {max(r['n_combos'])} combo(s), tag {'/'.join(r['bracket_estimado'])}" + (f"; Game Changers: {', '.join(r['game_changers'])}" if r["game_changers"] else ""))
    for i, op in enumerate(dj["opcoes_de_comandante"]):
        if len(dj["opcoes_de_comandante"]) > 1:
            linhas.append(f"- opção {op['comandante']}:")
        linhas += combos_md(op)
    linhas.append("")
sem = [r["deck"] for r in res if max(r["n_combos"]) == 0]
linhas += [f"Decks com **0 combos** achados ({len(sem)}): " + ", ".join(f"`{d}`" for d in sem) + ".", "",
           "## O que NÃO foi feito (Regra #7)", "",
           "- **Não conferi se o simulador de cada deck EXECUTA os combos achados** (Regra #4, adendo, item 3). O Rat King tinha 2 combos e um simulador que não executava nenhum (rodada de 2026-10-25); a mesma classe de erro pode estar nos decks com simulador e combos (Toph, Prismatic Bridge, Maralen, Ulalek, Thranduil, Azula, Edgar, Vihaan, Mothman, Tam, Ur-Dragon, Megatron, Bumbleflower, Nekusar, Tom). **Não varrido.**",
           "- **Não calculei a probabilidade por turno** de cada combo (regra 7 de `references/user-standing-rules.md`).",
           "- **Não comparei** com os registros antigos de Spellbook dos 8 decks que já tinham (Beorn, Megatron, Prismatic Bridge, Tam, Thranduil, Ur-Dragon, Vihaan, Mothman): esta rodada é independente, com a lista de hoje; as rodadas antigas não foram reauditadas e algumas passaram nomes sem a checagem de resolução.",
           "- **Não verifiquei o texto oficial atual do critério de Brackets**; as tags acima são do Spellbook.",
           "- Decks sem `goldfish-log.md` (27) não ganharam o link no topo do log; o link está só neste arquivo e no `LEIAME.md` da pasta de cada deck. `lista.md` não foi tocado.",
           CMP_EXEC, "",
           "## Como refazer", "",
           "```", "python3 -I spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py <raiz do repositório> [deck ...]   # consulta a API (rede); REFAZER=1 refaz decks já gravados",
           "python3 -I spellbook-todos-os-decks-2026-10-28/orquestracao/gera_resumo.py <raiz do repositório>                  # só dos arquivos salvos (sem rede): este RESUMO.md, os LEIAME e os SHA256SUMS", "```", ""]
open(os.path.join(CENTRAL, "RESUMO.md"), "w", encoding="utf-8").write("\n".join(linhas))

for r in res:
    d = r["deck"]; pasta = os.path.join(RAIZ, d, "resultados-ab", f"{DATA}-spellbook"); dj = deck_json(d)
    L = [f"# Commander Spellbook — `{d}` ({DATA})", "",
         f"Pedido do usuário (2026-10-28): *\"Quero todos os Spellbooks sim, e salvos no repositório\"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).", "",
         "## Resultado", "",
         f"- Comandante(s): {' / '.join(r['comandantes'])}; cartas lidas de `lista.md`: {r['total']}; nomes não reconhecidos pelo Spellbook: **{len(r['nao_reconhecidos'])}**.",
         f"- Combos achados: **{'/'.join(map(str, r['n_combos']))}** (de 2 cartas: {len(r['combos_2_cartas'])}); \"quase\": {'/'.join(map(str, r['n_quase']))}; tag do Spellbook: **{'/'.join(r['bracket_estimado'])}**; Game Changers: {', '.join(r['game_changers']) or 'nenhum'}.",
         f"- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **{r['controles'][0]}**; de corte (com Mind Stone o combo some) = **{r['controles'][1]}**."]
    for op in dj["opcoes_de_comandante"]:
        if op["incluidos"]:
            L += ["", f"### Combos" + (f" ({op['comandante']})" if len(dj['opcoes_de_comandante']) > 1 else "")] + combos_md(op)
    L += ["", "## Arquivos", "", "| arquivo | o que é |", "|---|---|",
          f"| `dados/spellbook_raw_{d}_{DATA}.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |",
          f"| `dados/spellbook_{d}_{DATA}.json` | JSON derivado das respostas (combos, \"quase\", `estimate-bracket`, controles) |", "| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |", "",
          "Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).", "",
          "## Não feito (Regra #7)", "",
          "Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.", ""]
    open(os.path.join(pasta, "LEIAME.md"), "w", encoding="utf-8").write("\n".join(L))
    arqs = sorted(glob.glob(os.path.join(pasta, "dados", "*")))
    open(os.path.join(pasta, "SHA256SUMS"), "w").write("".join(f"{sha(a)}  dados/{os.path.basename(a)}\n" for a in arqs) + f"{sha(os.path.join(pasta, 'LEIAME.md'))}  LEIAME.md\n")

central = [os.path.join(CENTRAL, "RESUMO.md")] + sorted(glob.glob(os.path.join(CENTRAL, "dados", "*"))) + sorted(glob.glob(os.path.join(CENTRAL, "orquestracao", "*.py"))) + sorted(glob.glob(os.path.join(CENTRAL, "resumos", "*")))
open(os.path.join(CENTRAL, "SHA256SUMS"), "w").write("".join(f"{sha(a)}  {os.path.relpath(a, CENTRAL)}\n" for a in central))
print("ok", len(res), "decks; central:", len(central), "arquivos")
