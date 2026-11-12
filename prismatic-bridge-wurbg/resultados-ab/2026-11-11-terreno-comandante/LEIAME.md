# Prismatic Bridge: o terreno que libera o comandante (2026-11-11): A/B, regressão, bit-identidade e determinismo

Arquivo da Regra #8 (`CLAUDE.md`). **Status: validado em 2026-11-11** (números abaixo; o que NÃO foi coberto está em "Não coberto"). Origem: partida manual #3 do Wise Mothman (`../../../wise-mothman-sultai/resultados-ab/2026-11-11-partida-manual-3/`), classe (o) da Regra #10; mesma correção do Mothman e do Tam, adaptada a este simulador (campo e mão são listas de NOMES, não `Permanent`).

## O erro (medido ANTES da correção)
A escolha do terreno (`play_land`) preferia "o terreno que cobre cor que falta" pela lista `produces`, e a **Plaza of Heroes** tem `produces={"C"}` (a cor para magia lendária é tratada à parte em `color_sources`): nunca era preferida, mesmo quando era o único terreno que deixava a Prismatic Bridge (lendária, 5 cores) conjurável no turno. Auditoria em runtime (`../../../varredura-2026-10-05/scripts/audit_terreno_comandante_pb.py`, N = 2.000, sementes 1.000.000+i, correção desligada; só LÊ o estado): **4,15% das partidas do modo padrão (83) e 4,10% da resiliência (82)** tiveram ao menos uma ocasião perdida (2.323 e 1.739 ocasiões; 97 e 96 perdidas), em T4 e T5 sobretudo (padrão: T2 9, T3 19, T4 28, T5 30). Terrenos que liberavam, em ordem: **Plaza of Heroes (35 e 37)**, City of Brass (10 e 10), Mana Confluence (10 e 9). Saídas: `../../../varredura-2026-10-05/resumos/audit_terreno_comandante_pb_{padrao,resiliencia}_N2000.json`.

## A correção (`prismatic-bridge-wurbg/prismatic_bridge_goldfish_v1.py`)
`commander_enabling_land(state, ordered)`: com a Bridge fora de campo e NÃO conjurável, testa cada terreno da mão (não fetch, não Fabled Passage, não entra virado; shockland só se a própria política pagaria os 2 de vida) com um **ensaio a seco** (o terreno entra em campo só para `can_cast`, sai em seguida) e, se algum a libera neste turno, joga o primeiro deles na ordem do deck. Não se aplica dentro do ensaio do terreno virado (`_TL_FORCED`). Chave `COMMANDER_ENABLING_LAND` (padrão ligada; desligada = comportamento de `1b7dd73`, bit a bit). Contador do estado `commander_land_overrides_total` e contador global `COMMANDER_LAND_OVERRIDES_ANYWHERE` (só serve à bit-identidade).

## Resultado (pareado, mesmas sementes; `resumos/ab_*.txt`)
**Efeito pequeno e consistente com a taxa de ~4% de partidas afetadas; todos os deltas ficam abaixo de 1 ponto.**

| N, modo | partidas idênticas ao antes | Bridge conjurada até T3 | até T4 | até T5 | primeiro PW atingido até T4 / T6 |
|---|---|---|---|---|---|
| 10.000, padrão | 98,0% | **+0,56 ±0,15 pontos** | +0,28 ±0,10 | +0,46 ±0,13 | +0,27 ±0,10 / +0,32 ±0,12 |
| 10.000, resiliência | 96,8% | **+0,57 ±0,15** | +0,28 ±0,11 | +0,45 ±0,13 | +0,39 ±0,12 / +0,34 ±0,13 |
| 2.000, padrão | 97,7% | +0,90 ±0,41 | +0,35 ±0,26 | +0,50 ±0,31 | +0,40 ±0,28 / +0,05 ±0,17 (ruído) |
| 2.000, resiliência | 96,0% | +0,85 ±0,40 | +0,30 ±0,28 | +0,55 ±0,35 | +0,75 ±0,38 / +0,35 ±0,29 |

Nunca conjurar a Bridge: −0,01 ±0,02 pontos no padrão (10.000), −0,06 ±0,05 na resiliência. Os demais campos de contagem (ativações, compras e ultimates de planeswalker) movem na 2ª casa decimal e estão nas tabelas completas.

## Validação (Regras #1 e #10)
- **Smoke** (`resumos/smoke.txt`): 99 cartas, 99 distintas, 0 desconhecidas, 0 duplicadas não-básicas; 200 partidas por modo, antes e depois, sem exceção.
- **Regressão 20.000 × 2 modos × 2 configurações** (`resumos/regressao_20000.txt`): 0 exceções, 0 carta acima do baralho, 0 campos negativos, com a chave ligada e desligada.
- **Bit-identidade 20.000 × 2 modos** (`resumos/bitident_20000.txt`, 4 blocos de 5.000 sementes 5.000.000–5.019.999; `orquestracao/bitident_pb.py`): chave desligada == `1b7dd73` em **40.000 de 40.000** execuções; chave ligada: **38.673 sem troca em estado nenhum, idênticas ao `1b7dd73`, e 1.327 com troca** (as únicas que podem diferir); **0 divergências**. O script exige > 0 partidas em cada grupo (verificação vácua é falha).
- **Determinismo** (`resumos/determinismo.txt`): 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos, campo a campo no estado final: **0 sementes divergentes** nos dois modos.

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_{2000,10000}{,_resiliencia}.json.xz` | bruto do A/B (variantes `antes` e `depois`, colunas-v1) | usado |
| `resumos/ab_*.txt` | tabelas (função só do bruto: `driver.py sum`) | usado (`cmp`) |
| `resumos/{smoke,regressao_20000,bitident_20000,determinismo,status,log_driver}.txt`, `resumos/bitident_chunk_*.txt` | saída de cada etapa | usado |
| `codigo/prismatic_bridge_goldfish_v1_ANTES_1b7dd73.py` | o simulador como estava | snapshot |
| `orquestracao/{abgen.py,driver.py,config.json,bitident_pb.py,rodar_tudo.sh,verificar_reproducao.sh}` | harness (o `driver.py`/`abgen.py` são os da rodada de 2026-10-07 do Prismatic Bridge) | usado |
| `SHA256SUMS`, `descomprimir.sh` | somas e descompressão | ver abaixo |

Reproduz: `bash prismatic-bridge-wurbg/resultados-ab/2026-11-11-terreno-comandante/orquestracao/verificar_reproducao.sh` (refaz as 4 tabelas dos brutos e compara por `cmp`, testa os `.xz` e confere o `SHA256SUMS`). **Não re-executa** as simulações (A/B, regressão, bit-identidade, determinismo): são as saídas das execuções originais.

## Não coberto (Regra #7)
- A política só olha a **Prismatic Bridge (o comandante)**. Terreno que libera outra magia (Plaza para um planeswalker lendário, Interplanar Beacon para um planeswalker) segue sem política própria.
- A escolha **entre terrenos que liberam** é a primeira na ordem do deck, sem ensaio de qual deixa o resto do turno melhor.
- A auditoria de ocasiões (4,15%/4,10%) foi medida em N = 2.000, só ANTES da correção; não reaudito com a chave ligada (é 0 por construção da política).
- O ensaio do "terreno virado primeiro" (T1–T2) não foi tocado; `_hoist_loses_a_play` (ordem do landfall) roda `play_land` em cópias e a política vale nelas também (a bit-identidade conta as trocas em qualquer estado).
- Sem calibração contra a mesa real do usuário (o modo resiliência usa o perfil de oponente do simulador).
