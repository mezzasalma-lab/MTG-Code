# Ulalek: Eldrazi Temple e Shrine of the Forsaken Gods contavam 1 mana (2026-11-11): A/B, regressão, bit-identidade e determinismo

Arquivo da Regra #8 (`CLAUDE.md`). **Status: validado em 2026-11-11** (números abaixo; o que NÃO foi coberto está em "Não coberto"). Origem: pedido do usuário *"Vc vai precisar revisar e corrigir o Plaza e demais terrenos em todos os simuladores"* (`../../../varredura-2026-10-05/resumos/revisao_terrenos_2026-11-11.md`). Classe (q) da Regra #10 (mana restrita achatada para 1 genérica "por convenção"); achada pela leitura do docstring do arquivo, que dizia que Eldrazi Temple, Cascading Cataracts e Shrine eram "tratadas como terreno genérico de 1 mana".

## O erro
Oráculo (Scryfall, `scryfall-cache`): Eldrazi Temple `{T}: Add {C}.` / `{T}: Add {C}{C}. Spend this mana only to cast colorless Eldrazi spells or activate abilities of colorless Eldrazi.`; Shrine of the Forsaken Gods `{T}: Add {C}.` / `{T}: Add {C}{C}. Spend this mana only to cast colorless spells. Activate only if you control seven or more lands.` Cada um rende **1 `{C}` a mais, só para a magia elegível**. O modelo de mana do arquivo é agregado (sem pips), mas a magia conjurada, o tipo e a cor estão no cache: **não é impossibilidade estrutural** (Regra #7, item 2); foi "convenção".

## A correção (`ulalek-wurbg/ulalek_goldfish_v1.py`)
`restricted_land_discount(state, name, cost, commit)` dentro de `effective_cost`: desconto = `min(Temples/Shrines ainda não usados no turno, custo // 2)`, onde conta Eldrazi Temple se a magia é Eldrazi incolor e Shrine se a magia é incolor e há 7+ terrenos (um `{C}{C}` paga 2 do custo com 1 virada; sobra de custo ímpar não rende). O uso é registrado no pagamento (`resolve_cast` normal, warp e evoke; lançamento do comandante) em `restricted_bonus_used_this_turn` (zerado por turno) e `restricted_land_bonus_total`. Chave `RESTRICTED_LAND_BONUS` (padrão ligada; desligada = comportamento de `f9b8905`, bit a bit). Teste dirigido (estado mínimo): Anticausal Vestige (Eldrazi incolor, custo 4 por warp) com 0 / 1 / 3 / 5 Temples = 4 / 3 / 2 / 2; artefato incolor com 1 Temple = 4 (não Eldrazi); com Shrine, 6 terrenos = 4, 7 terrenos = 3; 2 magias com 1 Temple: a 2ª não ganha de novo (3 e 4).

## Resultado (pareado, mesmas sementes; `resumos/ab_*.txt`)
**A correção ADICIONA mana que o simulador omitia, então o comandante e os finishers entram mais cedo.**

| N, modo | partidas idênticas ao antes | comandante até T3 | até T4 | até T5 | até T6 |
|---|---|---|---|---|---|
| 10.000, padrão | 74,6% | 20,25% → 22,94%: **+2,69 ±0,32 pontos** | +3,31 ±0,35 | +0,51 ±0,14 | +0,26 ±0,11 |
| 10.000, resiliência | 75,9% | 19,20% → 21,80%: **+2,60 ±0,31** | +3,47 ±0,37 | +0,86 ±0,22 | +0,55 ±0,18 |
| 2.000, padrão | 73,8% | +3,55 ±0,81 | +3,20 ±0,77 | +0,55 ±0,32 | +0,30 ±0,24 |
| 2.000, resiliência | 75,5% | +3,15 ±0,77 | +3,10 ±0,85 | +1,10 ±0,52 | +0,75 ±0,40 |

Outros efeitos (N = 10.000, padrão / resiliência): cópias de Ulalek +0,089 ±0,008 / +0,078 ±0,008 por partida; finishers resolvidos +0,053 ±0,006 (0,4415 → 0,4943) / +0,038 ±0,005; nunca resolver um finisher: **−2,20 ±0,30 / −1,76 ±0,29 pontos** (76,8% → 74,6% / 85,1% → 83,4%); finisher até T6 +0,62 ±0,16 / +0,48 ±0,15.

## Validação (Regras #1 e #10)
- **Smoke** (`resumos/smoke.txt`): 99 cartas, 99 distintas, 0 desconhecidas, 0 duplicadas não-básicas; 200 partidas por modo, antes e depois, sem exceção.
- **Regressão 20.000 × 2 modos × 2 configurações** (`resumos/regressao_20000.txt`): **0 exceções** e 0 campos negativos. **O invariante "carta acima do baralho" dispara em 14.606 (padrão) e 11.267 (resiliência) das 20.000 partidas com a chave ligada e em 14.165 e 10.781 com ela desligada**, e dispara no mesmo nível na rodada de 2026-10-05 (14.072 e 10.726, chave desligada; `../2026-10-05-mulligan-e-ordem-das-fases/resumos/regressao_*.txt`): **não é causado por esta correção, é um limite do invariante genérico neste simulador**. Amostra de 300 partidas (padrão): 230 têm algum nome acima da contagem da lista, e os mais frequentes são Writhing Chrysalis, Roaming Throne, Sowing Mycospawn, Chittering Dispatcher (todos 1 na lista); **leitura minha, não confirmada**: as cópias de feitiço do Ulalek ("ulalek_copies", "spell_token_copies") entram em campo com o mesmo nome da carta. Por isso este lote **não** prova que nenhuma carta passa do baralho; prova só 0 exceções e que o invariante não piorou de forma relevante.
- **Bit-identidade 20.000 × 2 modos** (`resumos/bitident_20000.txt`, 4 blocos de 5.000 sementes 5.000.000–5.019.999; `orquestracao/bitident_ul.py`): chave desligada == `f9b8905` em **40.000 de 40.000** execuções; chave ligada: **29.515 partidas em que `restricted_land_discount` nunca devolveu desconto, idênticas ao `f9b8905`, e 10.485 com desconto**; **0 divergências**. O script exige > 0 partidas em cada grupo.
- **Determinismo** (`resumos/determinismo.txt`): 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos, campo a campo no estado final: **0 sementes divergentes** nos dois modos.

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_{2000,10000}{,_resiliencia}.json.xz` | bruto do A/B (variantes `antes` e `depois`; colunas-v1) | usado |
| `resumos/ab_*.txt` | tabelas (função só do bruto: `driver.py sum`) | usado (`cmp`) |
| `resumos/{smoke,regressao_20000,bitident_20000,determinismo,status,log_driver}.txt`, `resumos/bitident_chunk_*.txt` | saída de cada etapa | usado |
| `codigo/ulalek_goldfish_v1_ANTES_f9b8905.py` | o simulador como estava | snapshot |
| `orquestracao/{abgen.py,driver.py,config.json,bitident_ul.py,rodar_tudo.sh,verificar_reproducao.sh}` | harness (o `driver.py`/`abgen.py` são os da rodada de 2026-10-05 do Ulalek) | usado |
| `SHA256SUMS`, `descomprimir.sh` | somas e descompressão | ver abaixo |

Reproduz: `bash ulalek-wurbg/resultados-ab/2026-11-11-terrenos-restritos/orquestracao/verificar_reproducao.sh` (refaz as 4 tabelas dos brutos e compara por `cmp`, testa os `.xz` e confere o `SHA256SUMS`). **Não re-executa** as simulações (A/B, regressão, bit-identidade, determinismo): são as saídas das execuções originais.

## Não coberto (Regra #7)
- **Habilidades ativadas de Eldrazi incolor pagas com o `{C}{C}` do Eldrazi Temple** (o oráculo permite): o gasto das ativadas é `spend_mana` direto e **não** recebe o desconto.
- **Cascading Cataracts** (`{5}, {T}: Add five mana in any combination of colors`): filtro de líquido 0 no modelo agregado (sem pips); **não alterado**.
- **Corrupted Crossroads** (`{T}, Pay 1 life: Add one mana of any color. Spend this mana only to cast a spell with devoid`) e as dores/vida dos painlands, City of Brass e Mana Confluence: o docstring do arquivo diz que a vida de manabase não é rastreada; **não alterado**.
- O desconto é uma aproximação em um modelo agregado: em custo ímpar a sobra de 1 `{C}` não rende, e a atribuição de qual terreno paga qual magia no turno não é modelada.
- Sem calibração contra a mesa real do usuário.
