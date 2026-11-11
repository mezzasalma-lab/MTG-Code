# Azula: proxy da Exotic Orchard (2026-11-11): A/B, regressão, bit-identidade e determinismo

Arquivo da Regra #8 (`CLAUDE.md`). **Status: validado em 2026-11-11** (números abaixo, lidos dos resumos arquivados por `orquestracao/gera_leiame.py`; o que NÃO foi coberto está em "Não coberto"). Origem: pedido do usuário *"Vc vai precisar revisar e corrigir o Plaza e demais terrenos em todos os simuladores"* e a decisão dele sobre a Exotic Orchard (2026-11-11): *"Kutzil, Megatron, Prismatic Bridge e Edgar como proxy"* (a Exotic Orchard gera mana de alguma cor; na mesa real, com 3 oponentes, quase sempre há terreno deles de alguma cor).

## O erro
Oráculo (Scryfall): Exotic Orchard `{T}: Add one mana of any color that a land an opponent controls could produce.` Goldfish solo não tem terrenos de oponente. Antes: o simulador tratava a Exotic Orchard como terreno SEM cor nenhuma (`produces=set()`, leitura literal do oráculo com 0 terrenos de oponente).

## A correção (`azula-grixis/azula_goldfish_v1.py`)
Chave `EXOTIC_ORCHARD_PROXY` (padrão ligada; desligada = comportamento de `99fde54`, bit a bit): a Exotic Orchard conta como fonte das cores da **identidade do comandante** (U, B, R) em todo ponto que lê o que um terreno produz (`land_prod(name, default)`); o total de mana não muda (o terreno já contava 1). Teste dirigido (estado mínimo, só a Exotic Orchard em campo): chave desligada = nenhuma fonte de cor; chave ligada = 1 fonte de cada cor da identidade.

## Resultado (pareado, mesmas sementes; `resumos/ab_*.txt`)
| N, modo | partidas idênticas ao antes | comandante até T3 | até T4 | até T5 | até T6 | nunca conjurar |
|---|---|---|---|---|---|---|
| 10.000, padrão | 91,2% | +0,63 ±0,16 | +2,46 ±0,32 | +1,92 ±0,28 | +1,63 ±0,25 | -0,62 ±0,15 |
| 10.000, resiliência | 91,6% | +0,59 ±0,16 | +2,26 ±0,32 | +1,92 ±0,29 | +1,69 ±0,26 | -0,68 ±0,16 |
| 2.000, padrão | 91,8% | +0,50 ±0,31 | +2,30 ±0,67 | +1,90 ±0,63 | +1,65 ±0,56 | -0,55 ±0,32 |
| 2.000, resiliência | 92,3% | +0,50 ±0,31 | +2,10 ±0,66 | +1,80 ±0,65 | +1,65 ±0,58 | -0,60 ±0,34 |

## Validação (Regras #1 e #10)
- **Smoke** (`resumos/smoke.txt`): 99 cartas, 86 distintas, 0 desconhecidas, 0 duplicadas não-básicas; 200 partidas por modo, antes e depois, sem exceção.
- **Regressão 20.000 × 2 modos × 2 configurações** (`resumos/regressao_20000.txt`): 0 exceções, 0 carta acima do baralho, 0 campos negativos, com a chave ligada e desligada.
- **Bit-identidade 20.000 × 2 modos** (`resumos/bitident_20000.txt`, 4 blocos de 5.000 sementes 5.000.000–5.019.999; `orquestracao/bitident_orchard.py`): chave desligada == `99fde54` em **40.000 de 40.000** execuções; chave ligada: **32.098 partidas em que a Exotic Orchard nunca esteve em campo durante um cálculo de cor, idênticas ao `99fde54`, e 7.902 com ela em campo** (as únicas que podem diferir); **0 divergências**. O script vigia `color_sources` e exige > 0 partidas em cada grupo.
- **Determinismo** (`resumos/determinismo.txt`): 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos, campo a campo no estado final: **0 e 0 sementes divergentes** (padrão e resiliência).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_{2000,10000}{,_resiliencia}.json.xz` | bruto do A/B (variantes `antes` e `depois`; colunas-v1) | usado |
| `resumos/ab_*.txt` | tabelas (função só do bruto: `driver.py sum`) | usado (`cmp`) |
| `resumos/{smoke,regressao_20000,bitident_20000,determinismo,status,log_driver}.txt`, `resumos/bitident_chunk_*.txt` | saída de cada etapa | usado |
| `codigo/*_ANTES_99fde54.py` | o simulador como estava | snapshot |
| `orquestracao/{abgen.py,driver.py,config.json,bitident_orchard.py,rodar_tudo.sh,verificar_reproducao.sh,gera_leiame.py}` | harness (o `driver.py`/`abgen.py` são os genéricos de 2026-10-05) | usado |
| `SHA256SUMS`, `descomprimir.sh` | somas e descompressão | ver abaixo |

Reproduz: `bash azula-grixis/resultados-ab/2026-11-11-exotic-orchard/orquestracao/verificar_reproducao.sh` (refaz as 4 tabelas dos brutos e compara por `cmp`, testa os `.xz` e confere o `SHA256SUMS`). **Não re-executa** as simulações (A/B, regressão, bit-identidade, determinismo): são as saídas das execuções originais.

## Não coberto (Regra #7)
- É um **proxy de decisão do usuário**, não a regra: o oráculo depende dos terrenos dos oponentes. Em jogo real a Orchard pode não produzir (oponentes sem terreno ou só de cor fora do necessário).
- A Orchard produz TODAS as cores da identidade ao mesmo tempo no modelo de cor (1 fonte de cada); a mana total não muda, mas uma magia que peça 2 cores diferentes e só tenha a Orchard + 1 fonte pode contar a cor de forma otimista.
- Os números anteriores do deck foram medidos com a Orchard sem cor: subestimam o deck quando ela estava em campo (20% das partidas dos lotes de bit-identidade); a linha de base inteira não foi refeita.
- Sem calibração contra a mesa real do usuário.
