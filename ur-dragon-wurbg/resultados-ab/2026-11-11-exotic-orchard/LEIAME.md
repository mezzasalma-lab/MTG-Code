# Ur-Dragon: proxy da Exotic Orchard (2026-11-11): A/B, regressão, bit-identidade e determinismo

Arquivo da Regra #8 (`CLAUDE.md`). **Status: validado em 2026-11-11** (números abaixo, lidos dos resumos arquivados por `orquestracao/gera_leiame.py`; o que NÃO foi coberto está em "Não coberto"). Origem: pedido do usuário *"Vc vai precisar revisar e corrigir o Plaza e demais terrenos em todos os simuladores"* e a decisão dele sobre a Exotic Orchard (2026-11-11): *"Kutzil, Megatron, Prismatic Bridge e Edgar como proxy"* (a Exotic Orchard gera mana de alguma cor; na mesa real, com 3 oponentes, quase sempre há terreno deles de alguma cor).

## O erro
Oráculo (Scryfall): Exotic Orchard `{T}: Add one mana of any color that a land an opponent controls could produce.` Goldfish solo não tem terrenos de oponente. Antes: o simulador deixava a Exotic Orchard sem cor (LAND_PRODUCES set(): contava 1 mana de terreno, mas nenhuma fonte de cor)

## A correção (`ur-dragon-wurbg/urdragon_goldfish_v1.py`)
Chave `EXOTIC_ORCHARD_PROXY` (padrão ligada; desligada = comportamento de `5be8579`, bit a bit): a Exotic Orchard conta como fonte das cores da **identidade do comandante** (W, U, B, R, G) em todo ponto que lê o que um terreno produz (`land_prod(name, default)`); o total de mana não muda (o terreno já contava 1). Teste dirigido (estado mínimo, só a Exotic Orchard em campo): chave desligada = nenhuma fonte de cor; chave ligada = 1 fonte de cada cor da identidade.

## Resultado (pareado, mesmas sementes; `resumos/ab_*.txt`)
| N, modo | partidas idênticas ao antes | comandante até T3 | até T4 | até T5 | até T6 | nunca conjurar |
|---|---|---|---|---|---|---|
| 10.000, padrão | 89,6% | 0,00 (idêntico: 0,11%) | +0,08 ±0,08 | +0,20 ±0,15 | +0,37 ±0,19 | -0,24 ±0,17 |
| 10.000, resiliência | 89,5% | 0,00 (idêntico: 0,10%) | +0,08 ±0,07 | +0,13 ±0,14 | +0,39 ±0,21 | -0,46 ±0,23 |
| 2.000, padrão | 90,8% | 0,00 (idêntico: 0,00%) | +0,20 ±0,20 | +0,40 ±0,34 | +0,50 ±0,44 | -0,20 ±0,31 |
| 2.000, resiliência | 90,8% | 0,00 (idêntico: 0,00%) | +0,10 ±0,14 | +0,15 ±0,35 | +0,50 ±0,42 | -0,45 ±0,45 |

## Validação (Regras #1 e #10)
- **Smoke** (`resumos/smoke.txt`): 99 cartas, 99 distintas, 0 desconhecidas, 0 duplicadas não-básicas; 200 partidas por modo, antes e depois, sem exceção.
- **Regressão 20.000 × 2 modos × 2 configurações** (`resumos/regressao_20000.txt`): 0 exceções, 0 carta acima do baralho, 0 campos negativos, com a chave ligada e desligada.
- **Bit-identidade 20.000 × 2 modos** (`resumos/bitident_20000.txt`, 4 blocos de 5.000 sementes 5.000.000–5.019.999; `orquestracao/bitident_orchard.py`): chave desligada == `5be8579` em **40.000 de 40.000** execuções; chave ligada: **32.514 partidas em que a Exotic Orchard nunca foi consultada (`land_prod`, em campo ou na mão), idênticas ao `5be8579`, e 7.486 com ela** (as únicas que podem diferir); **0 divergências**. O script vigia `land_prod` e exige > 0 partidas em cada grupo.
- **Determinismo** (`resumos/determinismo.txt`): 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos, campo a campo no estado final: **0 e 0 sementes divergentes** (padrão e resiliência).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_{2000,10000}{,_resiliencia}.json.xz` | bruto do A/B (variantes `antes` e `depois`; colunas-v1) | usado |
| `resumos/ab_*.txt` | tabelas (função só do bruto: `driver.py sum`) | usado (`cmp`) |
| `resumos/{smoke,regressao_20000,bitident_20000,determinismo,status,log_driver}.txt`, `resumos/bitident_chunk_*.txt` | saída de cada etapa | usado |
| `codigo/*_ANTES_5be8579.py` | o simulador como estava | snapshot |
| `orquestracao/{abgen.py,driver.py,config.json,bitident_orchard.py,rodar_tudo.sh,verificar_reproducao.sh,gera_leiame.py}` | harness (o `driver.py`/`abgen.py` são os genéricos de 2026-10-05) | usado |
| `orquestracao/rodar_retomada.sh`, `orquestracao/anexa_cor.py` | relança só a bit-identidade e o determinismo depois do reinício do contêiner; anexa a leitura de cor lendo `resumos/ab_10000*.txt` | usado |
| `SHA256SUMS`, `descomprimir.sh` | somas (sem `__pycache__`) e descompressão | ver abaixo |

Reproduz: `bash ur-dragon-wurbg/resultados-ab/2026-11-11-exotic-orchard/orquestracao/verificar_reproducao.sh` (refaz as 4 tabelas dos brutos e compara por `cmp`, testa os `.xz` e confere o `SHA256SUMS`). **Não re-executa** as simulações (A/B, regressão, bit-identidade, determinismo): são as saídas das execuções originais.

## Onde o efeito aparece neste deck: a cor, não o comandante
O comandante (MV 9) quase nunca sai até o T4 (2,3% das partidas), então a coluna do comandante é pequena por construção. O que o proxy mexe é a **falta de cor** (N = 10.000, pareado, `resumos/ab_10000*.txt`):
- padrão: `color_screw_turns` 0,9342 → 0,7857 (**-0,1485 ±0,0179 turnos com falta de cor por partida**); partidas que NUNCA tiveram falta de cor 74,71% → 77,99% (**3,28 ±0,35 pontos**); falta de cor até o T4 -2,66 ±0,32 pontos.
- resiliência: `color_screw_turns` 1,0217 → 0,8600 (**-0,1617 ±0,0187 turnos com falta de cor por partida**); partidas que NUNCA tiveram falta de cor 72,94% → 76,34% (**3,40 ±0,36 pontos**); falta de cor até o T4 -2,67 ±0,32 pontos.
Leitura: a Exotic Orchard em campo deixa de ser terreno sem cor num deck de 5 cores. Em partidas sem ela o resultado é idêntico (bit-identidade).

## Não coberto (Regra #7)
- É um **proxy de decisão do usuário**, não a regra: o oráculo depende dos terrenos dos oponentes. Em jogo real a Orchard pode não produzir (oponentes sem terreno ou só de cor fora do necessário).
- A Orchard produz TODAS as cores da identidade ao mesmo tempo no modelo de cor (1 fonte de cada); a mana total não muda, mas uma magia que peça 2 cores diferentes e só tenha a Orchard + 1 fonte pode contar a cor de forma otimista.
- Os números anteriores do deck foram medidos com a Orchard sem cor: subestimam o deck quando ela estava em campo (19% das partidas dos lotes de bit-identidade); a linha de base inteira não foi refeita.
- Sem calibração contra a mesa real do usuário.

## Proveniência e verificação
- **Execução interrompida e retomada.** `orquestracao/rodar_tudo.sh` fechou smoke, A/B e regressão (`resumos/status.txt`: "regressao fim" às 23:48:33 UTC de 2026-11-11) e foi morta por um reinício do contêiner durante a bit-identidade (os 4 `bitident_chunk_*.txt` ficaram com 0 byte, nada a aproveitar). A bit-identidade e o determinismo foram **refeitos do zero** em 2026-11-12 por `orquestracao/rodar_retomada.sh` (mesmos comandos, mesmas sementes 5.000.000–5.019.999; "bitident fim" 15:56:06, "determinismo fim" 15:57:16 UTC). O simulador vivo não foi editado entre as duas execuções.
- **Determinismo não é vácuo:** conferi os JSONs de cada execução: 6 execuções (3 `PYTHONHASHSEED` × 2 modos) com 1.500 partidas, 130–132 campos por partida, 1.500 estados distintos por execução e `stderr` vazio; o mesmo script achou 682/262 divergências (`_mana_cache`) no Tom, então ele sabe divergir.
- **`verificar_reproducao.sh` (2026-11-12): 9 conferências, 0 falhas** (4 `.xz` íntegros; as 4 tabelas do A/B refeitas só a partir dos brutos e iguais por `cmp`; `SHA256SUMS` confere).
- **NÃO conferidos por `cmp`:** `smoke.txt`, `regressao_20000.txt`, `bitident_*.txt` e `determinismo.txt` (saídas das execuções originais; o script não re-simula); o A/B 10.000 e 2.000 não foi re-simulado (`--tudo` não existe nesta pasta). A coluna "até T3" e o texto do `goldfish-log.md` vêm de `orquestracao/gera_leiame.py` **na versão corrigida em 2026-11-12** (nome do deck "Ur-Dragon" em vez de "Ur"; célula do T3 conferida no bruto em vez de `n/d`; destaque lista T3 a T6); os LEIAMEs de Azula, Bumbleflower e Tom foram gerados pela versão anterior, que dá o mesmo resultado nesses decks (todas as células deles têm linha na tabela).
