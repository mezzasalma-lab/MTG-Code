# Tom: proxy da Exotic Orchard (2026-11-11): A/B, regressão, bit-identidade e determinismo

Arquivo da Regra #8 (`CLAUDE.md`). **Status: validado em 2026-11-11** (números abaixo, lidos dos resumos arquivados por `orquestracao/gera_leiame.py`; o que NÃO foi coberto está em "Não coberto"). Origem: pedido do usuário *"Vc vai precisar revisar e corrigir o Plaza e demais terrenos em todos os simuladores"* e a decisão dele sobre a Exotic Orchard (2026-11-11): *"Kutzil, Megatron, Prismatic Bridge e Edgar como proxy"* (a Exotic Orchard gera mana de alguma cor; na mesa real, com 3 oponentes, quase sempre há terreno deles de alguma cor).

## O erro
Oráculo (Scryfall): Exotic Orchard `{T}: Add one mana of any color that a land an opponent controls could produce.` Goldfish solo não tem terrenos de oponente. Antes: o simulador tratava a Exotic Orchard como terreno SEM cor nenhuma (`produces=set()`: "produz 1 mana sem cor definida", mesma convenção do Bumbleflower).

## A correção (`tom-bombadil-wubrg/tom_goldfish_v1.py`)
Chave `EXOTIC_ORCHARD_PROXY` (padrão ligada; desligada = comportamento de `8ca861c`, bit a bit): a Exotic Orchard conta como fonte das cores da **identidade do comandante** (W, U, B, R, G) em todo ponto que lê o que um terreno produz (`land_prod(name, default)`); o total de mana não muda (o terreno já contava 1). Teste dirigido (estado mínimo, só a Exotic Orchard em campo): chave desligada = nenhuma fonte de cor; chave ligada = 1 fonte de cada cor da identidade.

## Resultado (pareado, mesmas sementes; `resumos/ab_*.txt`)
| N, modo | partidas idênticas ao antes | comandante até T3 | até T4 | até T5 | até T6 | nunca conjurar |
|---|---|---|---|---|---|---|
| 10.000, padrão | 80,9% | +0,09 ±0,09 | +1,90 ±0,30 | +3,31 ±0,38 | +2,80 ±0,34 | -0,76 ±0,18 |
| 10.000, resiliência | 83,1% | +0,09 ±0,09 | +1,71 ±0,28 | +3,21 ±0,38 | +3,07 ±0,37 | -1,09 ±0,23 |
| 2.000, padrão | 82,1% | +0,10 ±0,14 | +2,10 ±0,69 | +3,00 ±0,84 | +2,90 ±0,80 | -0,85 ±0,40 |
| 2.000, resiliência | 84,0% | +0,10 ±0,14 | +1,85 ±0,64 | +2,75 ±0,83 | +2,90 ±0,87 | -1,25 ±0,53 |

## Validação (Regras #1 e #10)
- **Smoke** (`resumos/smoke.txt`): 99 cartas, 99 distintas, 0 desconhecidas, 0 duplicadas não-básicas; 200 partidas por modo, antes e depois, sem exceção.
- **Regressão 20.000 × 2 modos × 2 configurações** (`resumos/regressao_20000.txt`): 0 exceções, o invariante genérico "carta acima do baralho" dispara em 3 (padrão) e 0 (resiliência) das 20.000 partidas com a chave ligada e em 4 e 0 com a chave DESLIGADA: **aparece também sem a correção e não aumenta com ela** (causa não investigada neste deck), 0 campos negativos, com a chave ligada e desligada.
- **Bit-identidade 20.000 × 2 modos** (`resumos/bitident_20000.txt`, 4 blocos de 5.000 sementes 5.000.000–5.019.999; `orquestracao/bitident_orchard.py`): chave desligada == `8ca861c` em **40.000 de 40.000** execuções; chave ligada: **29.229 partidas em que a Exotic Orchard nunca foi consultada (`land_prod`, em campo ou na mão), idênticas ao `8ca861c`, e 10.771 com ela** (as únicas que podem diferir); **0 divergências**. O script vigia `land_prod` e exige > 0 partidas em cada grupo.
- **Determinismo** (`resumos/determinismo.txt`): 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos, campo a campo no estado final: **682 (padrão) e 262 (resiliência) sementes divergentes, e SÓ no campo `_mana_cache`** (cache de memoização do Tom, que depende da ordem de iteração de `set` e já é excluído da impressão digital do resultado em `abgen`); **nenhum outro campo do estado final diverge**. Controle com a chave DESLIGADA (`resumos/determinismo_controle_chave_desligada.txt`): 670 e 262 sementes, também só `_mana_cache`: **o fenômeno já existia sem a correção** (a chave ligada mexeu em 12 sementes a mais do cache no padrão e 0 na resiliência; o cache não é lido como resultado). Causa do cache não investigada além disso.

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_{2000,10000}{,_resiliencia}.json.xz` | bruto do A/B (variantes `antes` e `depois`; colunas-v1) | usado |
| `resumos/ab_*.txt` | tabelas (função só do bruto: `driver.py sum`) | usado (`cmp`) |
| `resumos/{smoke,regressao_20000,bitident_20000,determinismo,status,log_driver}.txt`, `resumos/bitident_chunk_*.txt` | saída de cada etapa | usado |
| `codigo/*_ANTES_8ca861c.py` | o simulador como estava | snapshot |
| `orquestracao/{abgen.py,driver.py,config.json,bitident_orchard.py,rodar_tudo.sh,rodar_rodada2.sh,verificar_reproducao.sh,gera_leiame.py}` | harness (o `driver.py`/`abgen.py` são os genéricos de 2026-10-05) | usado |
| `SHA256SUMS`, `descomprimir.sh` | somas e descompressão | ver abaixo |

Reproduz: `bash tom-bombadil-wubrg/resultados-ab/2026-11-11-exotic-orchard/orquestracao/verificar_reproducao.sh` (refaz as 4 tabelas dos brutos e compara por `cmp`, testa os `.xz` e confere o `SHA256SUMS`). **Não re-executa** as simulações (A/B, regressão, bit-identidade, determinismo): são as saídas das execuções originais.

## Rodada 1 da bit-identidade e do determinismo (SUPERADA, guardada e marcada)
- **Bit-identidade da rodada 1** (`resumos/bitident_20000_RODADA1_criterio_color_sources_SUPERADA.txt` e `bitident_chunk_*_RODADA1_SUPERADA.txt`): o grupo "chave ligada sem Orchard em campo" foi definido por `color_sources` e deu **331 divergências** (79 + 88 + 93 + 71) em 40.000. **Diagnóstico** (8 sementes divergentes do bloco 0, padrão): em todas, `land_prod("Exotic Orchard", ...)` foi chamado com a Orchard **só na mão**, na pontuação de qual terreno jogar (`fix` e desempate em `land_option_score`), e nunca em campo durante `color_sources`. **A divergência é a correção agindo, não um erro de código**: o critério do grupo "idêntico" estava estreito. Rodada 2 com o critério `land_prod` (campo OU mão): **0 divergências**.
- **Determinismo da rodada 1** (`resumos/determinismo_RODADA1_com_mana_cache.txt`): 682/262 sementes, só em `_mana_cache`; a rodada 2 repete o resultado e traz o controle com a chave desligada (acima).
- Um deslize de orquestração: o `cat bitident_chunk_*.txt` da rodada 2 pegou também os blocos SUPERADA (glob amplo) e contaminou o 1º `bitident_20000.txt`; refeito só com `bitident_chunk_[0-3].txt`, e o `orquestracao/rodar_rodada2.sh` ficou com o glob corrigido.
- **Azula e Bumbleflower** usaram o critério de `color_sources`; nesses dois simuladores `land_prod` só é chamada dentro de `color_sources` para o que está em campo, então os critérios são equivalentes (0 divergências nos dois). O **Ur-Dragon** usa `land_prod` também na pontuação de terreno da mão, então segue o critério do Tom.

## Não coberto (Regra #7)
- É um **proxy de decisão do usuário**, não a regra: o oráculo depende dos terrenos dos oponentes. Em jogo real a Orchard pode não produzir (oponentes sem terreno ou só de cor fora do necessário).
- A Orchard produz TODAS as cores da identidade ao mesmo tempo no modelo de cor (1 fonte de cada); a mana total não muda, mas uma magia que peça 2 cores diferentes e só tenha a Orchard + 1 fonte pode contar a cor de forma otimista.
- Os números anteriores do deck foram medidos com a Orchard sem cor: subestimam o deck quando ela estava em campo (27% das partidas dos lotes de bit-identidade); a linha de base inteira não foi refeita.
- Sem calibração contra a mesa real do usuário.
