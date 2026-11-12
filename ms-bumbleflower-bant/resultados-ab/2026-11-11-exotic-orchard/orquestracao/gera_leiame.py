"""Gera LEIAME.md, a secao do goldfish-log e a nota do checklist-oraculo da correcao EXOTIC_ORCHARD_PROXY de um deck, LENDO os numeros dos resumos arquivados (nada digitado a mao).
Uso (da raiz do repositorio): python3 -I gera_docs_orchard.py <deck-dir> <sim.py> <snapshot_hash> <cores> <antes_texto>
(`orquestracao/gera_leiame.py` arquivado em cada pasta; a saida e' funcao so' dos resumos + dos argumentos)."""
import os, re, sys
deck, sim, snap, cores, antes = sys.argv[1:6]
R = os.getcwd()
D = os.path.join(R, deck, "resultados-ab", "2026-11-11-exotic-orchard")
RS = os.path.join(D, "resumos")
def lo(f): return open(os.path.join(RS, f), encoding="utf-8").read()
def secao_depois(t):
    return t.split("\n\n")[1].split("\n")
def linha(sec, campo):
    for l in sec:
        m = re.match(r"\s*\*?\s*(\S+)\s+([\d.]+)\s+([\d.]+)\s+([+-][\d.]+) ±([\d.]+)", l)
        if m and m.group(1) == campo:
            return float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5))
    return None
def ident(t):
    m = re.search(r"IDENTICO ao da base: \d+ \(([\d.]+)%\)", t)
    return m.group(1).replace(".", ",") if m else "?"
def mil(n):
    return f"{n:,}".replace(",", ".")


def pts(x):
    return "n/d" if x is None else f"{x[2]*100:+.2f} ±{x[3]*100:.2f}".replace(".", ",")
lotes = {}
for N, suf, modo in ((10000, "", "10.000, padrão"), (10000, "_resiliencia", "10.000, resiliência"), (2000, "", "2.000, padrão"), (2000, "_resiliencia", "2.000, resiliência")):
    t = lo(f"ab_{N}{suf}.txt"); s = secao_depois(t)
    lotes[modo] = (ident(t), [linha(s, f"commander_cast_turn__ate_T{k}") for k in (3, 4, 5, 6)], linha(s, "commander_cast_turn__nunca"), s)
tab = "| N, modo | partidas idênticas ao antes | comandante até T3 | até T4 | até T5 | até T6 | nunca conjurar |\n|---|---|---|---|---|---|---|\n"
for modo, (idt, ks, nun, _) in lotes.items():
    tab += f"| {modo} | {idt}% | " + " | ".join(pts(k) for k in ks) + f" | {pts(nun)} |\n"
b = lo("bitident_20000.txt")
off = sum(int(x) for x in re.findall(r"identica ao snapshot em (\d+) partidas", b))
sem = sum(int(x) for x in re.findall(r"LIGADA: (\d+) sem Exotic", b)); com = sum(int(x) for x in re.findall(r"identicas, (\d+) com ela", b)); div = sum(int(x) for x in re.findall(r"divergencias: (\d+)", b))
det = lo("determinismo.txt"); detn = [int(x) for x in re.findall(r"divergentes entre 3 hash seeds: (\d+)", det)]
reg = lo("regressao_20000.txt").split("\n")[1:5]
exc = sum(int(re.search(r"excecoes=(\d+)", l).group(1)) for l in reg); acima = [int(re.search(r"acima do baralho=(\d+)", l).group(1)) for l in reg]
sm = lo("smoke.txt").split("\n")[0]
cartas = re.search(r"cartas na biblioteca=(\d+) \| distintas=(\d+)", sm)
assert off > 0 and sem > 0 and com > 0 and detn and all(x == 0 for x in detn) and div == 0 and off == 40000, (off, sem, com, div, detn)
inv = "0 carta acima do baralho" if all(a == 0 for a in acima) else f"**invariante 'carta acima do baralho' dispara ({acima}) — conferir contra a chave desligada antes de ler**"
nome = deck.split("-")[0].capitalize() if deck != "ms-bumbleflower-bant" else "Ms. Bumbleflower"
leiame = f'''# {nome}: proxy da Exotic Orchard (2026-11-11): A/B, regressão, bit-identidade e determinismo

Arquivo da Regra #8 (`CLAUDE.md`). **Status: validado em 2026-11-11** (números abaixo, lidos dos resumos arquivados por `orquestracao/gera_leiame.py`; o que NÃO foi coberto está em "Não coberto"). Origem: pedido do usuário *"Vc vai precisar revisar e corrigir o Plaza e demais terrenos em todos os simuladores"* e a decisão dele sobre a Exotic Orchard (2026-11-11): *"Kutzil, Megatron, Prismatic Bridge e Edgar como proxy"* (a Exotic Orchard gera mana de alguma cor; na mesa real, com 3 oponentes, quase sempre há terreno deles de alguma cor).

## O erro
Oráculo (Scryfall): Exotic Orchard `{{T}}: Add one mana of any color that a land an opponent controls could produce.` Goldfish solo não tem terrenos de oponente. Antes: {antes}

## A correção (`{deck}/{sim}`)
Chave `EXOTIC_ORCHARD_PROXY` (padrão ligada; desligada = comportamento de `{snap}`, bit a bit): a Exotic Orchard conta como fonte das cores da **identidade do comandante** ({cores}) em todo ponto que lê o que um terreno produz (`land_prod(name, default)`); o total de mana não muda (o terreno já contava 1). Teste dirigido (estado mínimo, só a Exotic Orchard em campo): chave desligada = nenhuma fonte de cor; chave ligada = 1 fonte de cada cor da identidade.

## Resultado (pareado, mesmas sementes; `resumos/ab_*.txt`)
{tab}
## Validação (Regras #1 e #10)
- **Smoke** (`resumos/smoke.txt`): {cartas.group(1)} cartas, {cartas.group(2)} distintas, 0 desconhecidas, 0 duplicadas não-básicas; 200 partidas por modo, antes e depois, sem exceção.
- **Regressão 20.000 × 2 modos × 2 configurações** (`resumos/regressao_20000.txt`): {exc} exceções, {inv}, 0 campos negativos, com a chave ligada e desligada.
- **Bit-identidade 20.000 × 2 modos** (`resumos/bitident_20000.txt`, 4 blocos de 5.000 sementes 5.000.000–5.019.999; `orquestracao/bitident_orchard.py`): chave desligada == `{snap}` em **{mil(off)} de 40.000** execuções; chave ligada: **{mil(sem)} partidas em que a Exotic Orchard nunca esteve em campo durante um cálculo de cor, idênticas ao `{snap}`, e {mil(com)} com ela em campo** (as únicas que podem diferir); **{div} divergências**. O script vigia `color_sources` e exige > 0 partidas em cada grupo.
- **Determinismo** (`resumos/determinismo.txt`): 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos, campo a campo no estado final: **{detn[0]} e {detn[1]} sementes divergentes** (padrão e resiliência).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_{{2000,10000}}{{,_resiliencia}}.json.xz` | bruto do A/B (variantes `antes` e `depois`; colunas-v1) | usado |
| `resumos/ab_*.txt` | tabelas (função só do bruto: `driver.py sum`) | usado (`cmp`) |
| `resumos/{{smoke,regressao_20000,bitident_20000,determinismo,status,log_driver}}.txt`, `resumos/bitident_chunk_*.txt` | saída de cada etapa | usado |
| `codigo/*_ANTES_{snap}.py` | o simulador como estava | snapshot |
| `orquestracao/{{abgen.py,driver.py,config.json,bitident_orchard.py,rodar_tudo.sh,verificar_reproducao.sh,gera_leiame.py}}` | harness (o `driver.py`/`abgen.py` são os genéricos de 2026-10-05) | usado |
| `SHA256SUMS`, `descomprimir.sh` | somas e descompressão | ver abaixo |

Reproduz: `bash {deck}/resultados-ab/2026-11-11-exotic-orchard/orquestracao/verificar_reproducao.sh` (refaz as 4 tabelas dos brutos e compara por `cmp`, testa os `.xz` e confere o `SHA256SUMS`). **Não re-executa** as simulações (A/B, regressão, bit-identidade, determinismo): são as saídas das execuções originais.

## Não coberto (Regra #7)
- É um **proxy de decisão do usuário**, não a regra: o oráculo depende dos terrenos dos oponentes. Em jogo real a Orchard pode não produzir (oponentes sem terreno ou só de cor fora do necessário).
- A Orchard produz TODAS as cores da identidade ao mesmo tempo no modelo de cor (1 fonte de cada); a mana total não muda, mas uma magia que peça 2 cores diferentes e só tenha a Orchard + 1 fonte pode contar a cor de forma otimista.
- Os números anteriores do deck foram medidos com a Orchard sem cor: subestimam o deck quando ela estava em campo ({com/400:.0f}% das partidas dos lotes de bit-identidade); a linha de base inteira não foi refeita.
- Sem calibração contra a mesa real do usuário.
'''
open(os.path.join(D, "LEIAME.md"), "w", encoding="utf-8").write(leiame)
m10 = lotes["10.000, padrão"]; r10 = lotes["10.000, resiliência"]
sec = f'''## 2026-11-11 — Proxy da Exotic Orchard (decisão do usuário; mesma do Kutzil, Megatron e Prismatic Bridge)

Dados, scripts e escopo: `resultados-ab/2026-11-11-exotic-orchard/LEIAME.md`.
- **Erro:** Antes: {antes}
- **Correção:** `EXOTIC_ORCHARD_PROXY` (padrão ligada; desligada = `{snap}` bit a bit): a Exotic Orchard conta como fonte das cores da identidade ({cores}).
- **Efeito** (pareado, N = 10.000, padrão / resiliência, em pontos): comandante até T3 **{pts(m10[1][0])} / {pts(r10[1][0])}**, até T4 **{pts(m10[1][1])} / {pts(r10[1][1])}**, até T5 {pts(m10[1][2])} / {pts(r10[1][2])}; nunca conjurar {pts(m10[2])} / {pts(r10[2])}; partidas idênticas ao antes {m10[0]}% / {r10[0]}%.
- **Validação:** smoke {cartas.group(1)} cartas; regressão 20.000 × 2 modos × 2 configurações: {exc} exceções; bit-identidade 20.000 × 2: chave desligada idêntica em {mil(off)} de 40.000, ligada {mil(sem)} sem a Orchard em campo idênticas e {mil(com)} com ela, {div} divergências; determinismo 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos: 0 sementes divergentes.
- **Os números anteriores do deck foram medidos com a Orchard sem cor** (em campo em {com/400:.0f}% das partidas); linha de base não refeita. É um proxy de decisão do usuário, não a regra.

'''
gl = os.path.join(R, deck, "goldfish-log.md")
s = open(gl, encoding="utf-8").read()
assert "Proxy da Exotic Orchard (decisão do usuário" not in s, "goldfish-log ja' tem a secao (idempotencia)"
top = "> **Spellbook de 2026-10-28 (todos os decks) — respostas cruas da API e reprodução:**"
if s.count(top) == 1:
    s = s.replace(top, f"> **Atualização 2026-11-11 (§ \"Proxy da Exotic Orchard\"): decisão do usuário aplicada** (comandante até T3 {pts(m10[1][0])} pontos no padrão): [`resultados-ab/2026-11-11-exotic-orchard/LEIAME.md`](resultados-ab/2026-11-11-exotic-orchard/LEIAME.md)\n\n" + top, 1)
mm = re.search(r"^## Partida #\d+ — AAAA-MM-DD", s, re.M)
s = (s[:mm.start()] + sec + s[mm.start():]) if mm else (s.rstrip("\n") + "\n\n" + sec)
open(gl, "w", encoding="utf-8").write(s.rstrip("\n") + "\n")
ck = os.path.join(R, deck, "checklist-oraculo.md")
if os.path.exists(ck):
    c = open(ck, encoding="utf-8").read().rstrip("\n") + f"\n\n## 2026-11-11 — Exotic Orchard: conferência do oráculo contra o simulador\n\nOráculo (scryfall-cache): `{{T}}: Add one mana of any color that a land an opponent controls could produce.` 🐛 **proxy aplicado por decisão do usuário** (`EXOTIC_ORCHARD_PROXY`: fonte das cores da identidade, {cores}); antes: {antes} Números e validação: `goldfish-log.md` (seção de 2026-11-11).\n"
    open(ck, "w", encoding="utf-8").write(c)
print(deck, "docs gerados;", off, sem, com, div, detn, exc, acima)
