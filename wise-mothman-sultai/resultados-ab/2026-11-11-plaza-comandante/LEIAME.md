# The Wise Mothman: o terreno que libera o comandante (2026-11-11): A/B, regressão, bit-identidade e determinismo

Arquivo da Regra #8 (`CLAUDE.md`). **Status: validado em 2026-11-11** (números abaixo; o que NÃO foi coberto está em "Não coberto"). Origem: partida manual #3 (`../2026-11-11-partida-manual-3/`): no T4 o usuário conjurou o Mothman (`{1}{B}{G}{U}`) sem `{B}` porque descartou a **Plaza of Heroes**, e o simulador, na conferência da mesma partida, também jogava outro terreno (5 de 6 conferências; a 6ª falhava). Classe (o) da Regra #10, nova (texto em `CLAUDE.md`).

## O erro
`land_play_score` pontuava a Plaza of Heroes como terreno incolor (−4): o oráculo é `{T}: Add {C}` / `{T}: Add one mana of any color. Spend this mana only to cast a legendary spell` / `{T}: Add one mana of any color among legendary permanents you control`, e o Mothman é lendário. A escolha do terreno também não olhava o comandante: nenhum terreno da mão que o deixasse conjurável NESTE turno ganhava prioridade. Medido ANTES da correção (N = 10.000, `../2026-11-11-partida-manual-3/dados/medicao_plaza_ANTES_*`): **6,69%** das partidas do modo padrão e **7,01%** do de resiliência tiveram ao menos uma ocasião perdida (669 e 701 partidas; 1.005 e 1.091 ocasiões, quase todas no T3 e no T4).

## A correção (`wise-mothman-sultai/mothman_goldfish_v1.py`)
`commander_enabling_land(state, cands)`: com o comandante na zona de comando e NÃO conjurável agora, testa cada terreno jogável da mão (não fetch, não MDFC, não entra virado) com um **ensaio a seco** (o terreno entra em campo só para a checagem `can_cast_name` e sai em seguida, `next_uid` restaurado) e, se algum o libera, joga o de maior `land_play_score` entre os que liberam. Chave `PLAZA_ENABLES_COMMANDER` (padrão ligada; desligada = comportamento de `c59226f`, bit a bit). Contador do estado `commander_land_overrides_total` e contador global `COMMANDER_LAND_OVERRIDES_ANYWHERE` (conta a troca em QUALQUER estado, inclusive as cópias do ensaio a seco da guarda do landfall; só serve à bit-identidade).

## Resultado (pareado, mesmas sementes; `resumos/resumo_plaza.md`)
**Efeito pequeno e real no comandante; no resto do jogo está no limite do ruído.**

| N, modo | partidas com troca | comandante até T3 | até T4 | até T5 | primeira eliminação até T6 | `cleared_T8` |
|---|---|---|---|---|---|---|
| 10.000, padrão | 9,84% | +0,84 ±0,18 pts | **+1,01 ±0,20 pts** | +0,25 ±0,10 | +0,80 ±0,24 | +0,28 ±0,24 (no limite) |
| 10.000, resiliência | 10,96% | +0,79 ±0,17 | **+1,08 ±0,21** | +0,35 ±0,13 | +0,54 ±0,24 | +0,58 ±0,29 |
| 2.000 (os dois modos) | 9,1% / 10,3% | +0,85 | +1,45 / +1,40 | | | |

Partidas idênticas entre antes e depois: 90,1% (padrão) e 89,3% (resiliência) em N = 10.000. `cleared_T10`, `self_lost`, cartas moídas e contadores do Mothman: dentro do IC95%.

## Validação (Regras #1 e #10)
- **Smoke** (`resumos/smoke.txt`): 99 cartas, 91 distintas, 0 desconhecidas, 0 duplicadas não-básicas; 200 partidas por modo sem exceção.
- **Regressão 20.000 × 2 modos** (`resumos/regressao_20000.txt`): 0 exceções, 0 carta acima do baralho, 0 campos negativos.
- **Bit-identidade 20.000 × 2 modos** (`resumos/bitident_20000.txt`; `orquestracao/bitident.py`): (1) chave desligada == `c59226f` campo a campo; (2) chave ligada, toda partida em que NENHUMA troca ocorreu em estado nenhum (`COMMANDER_LAND_OVERRIDES_ANYWHERE == 0`) == `c59226f`; só as partidas com troca podem diferir. O script exige > 0 partidas em cada grupo (verificação vácua é falha).
- **Determinismo** (`resumos/determinismo.txt`): 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo no estado final.
- **Teste dirigido na partida real**: com a correção, a conferência da partida #3 passa 6/6 (`../2026-11-11-partida-manual-3/resumos/confere_simulador_DEPOIS_plaza.txt`).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_{2000,10000}{,_resiliencia}.json.xz` | bruto do A/B (variantes `base` e `plaza`, colunas-v1) | usado |
| `resumos/ab_*.txt`, `resumos/compacto_*.txt`, `resumos/resumo_plaza.md` | tabelas (a publicada é função só do bruto) | usado |
| `resumos/{smoke,regressao_20000,bitident_20000,determinismo,status,log_driver}.txt` | saída de cada etapa | usado |
| `codigo/mothman_goldfish_v1_ANTES_c59226f.py` | o simulador como estava | snapshot |
| `orquestracao/{abgen.py,driver_mm.py,config.json,bitident.py,resumo_plaza.py,rodar_tudo.sh,verificar_reproducao.sh}` | harness | usado |
| `SHA256SUMS`, `descomprimir.sh`, `verificar_reproducao.sh` (raiz) | somas e reprodução | ver abaixo |

Reproduz: `bash wise-mothman-sultai/resultados-ab/2026-11-11-plaza-comandante/orquestracao/verificar_reproducao.sh [--tudo]` (sem opção refaz as tabelas dos brutos e compara por `cmp`; `--tudo` re-simula o lote de 2.000, **não** o de 10.000, a regressão, a bit-identidade nem o determinismo).

## Não coberto (Regra #7)
- A política só olha o **comandante**. Terreno que libera uma magia que não é o comandante (Plaza para outra lendária, filtro para uma cor que falta) não tem política própria: o `land_play_score` pontua a Plaza como −4 também nesses casos.
- A escolha **entre terrenos que liberam** é por `land_play_score`, sem ensaio de qual deixa o resto do turno melhor.
- Terreno que entra em campo por magia (Cultivate, Farseek...), blink de terreno e ordem de várias fases principais não foram tocados.
- Os outros 17 simuladores não foram medidos para esta classe (só Tam e Prismatic Bridge; ver `varredura-2026-10-05/resumos/revisao_terrenos_2026-11-11.md`).
- O A/B usa o goldfish de 3 oponentes simulados do Mothman; não há calibração do efeito contra a mesa real do usuário.
