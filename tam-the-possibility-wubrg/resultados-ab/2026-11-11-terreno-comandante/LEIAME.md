# Tam, the Possibility: o terreno que libera o comandante (2026-11-11): A/B, regressão, bit-identidade e determinismo

Arquivo da Regra #8 (`CLAUDE.md`). **Status: validado em 2026-11-11** (números abaixo; o que NÃO foi coberto está em "Não coberto"). Origem: partida manual #3 do Wise Mothman (`../../../wise-mothman-sultai/resultados-ab/2026-11-11-partida-manual-3/`), classe (o) da Regra #10; a mesma correção do Mothman (`../../../wise-mothman-sultai/resultados-ab/2026-11-11-plaza-comandante/`), aplicada ao simulador do Tam, que tem a mesma API (`play_land_phase`, `mk_perm`, `can_cast_name`, `commander_in_cz`).

## O erro (medido ANTES da correção)
A escolha do terreno (`land_play_score`) ignorava que outro terreno da mão, jogado AGORA, deixaria a Tam (`{1}{G}{U}`) conjurável neste turno. Auditoria em runtime (`../../../varredura-2026-10-05/scripts/audit_terreno_comandante.py`, N = 2.000, sementes 1.000.000+i, correção desligada; só LÊ o estado): **32,15% das partidas do modo padrão (643) e 34,15% da resiliência (683)** tiveram ao menos uma ocasião perdida (3.237 e 3.913 ocasiões; 2.285 e 2.382 perdidas). **Quase todas no T2 (1.569) e no T3 (624)**, e os terrenos que liberavam eram, em ordem, Great Hall of the Citadel (322), Plaza of Heroes (264), Boseiju (240), Yavimaya (240) e Baxter Building (215). Ou seja, a classe (o) aqui é dominada pela escolha entre terrenos nos primeiros turnos, com a Plaza só como parte. **Hipótese, não medida:** o ensaio do "terreno virado primeiro" (classe (k) da Regra #10) tem o mesmo ponto cego para o comandante e pode contribuir no T2. Saídas: `../../../varredura-2026-10-05/resumos/audit_terreno_comandante_tam_{padrao,resiliencia}_N2000.json`.

## A correção (`tam-the-possibility-wubrg/tam_goldfish_v1.py`)
`commander_enabling_land(state, cands)`: com a Tam na zona de comando e NÃO conjurável agora, testa cada terreno jogável da mão/impulso/cemitério (não fetch, não entra virado) com um **ensaio a seco** (o terreno entra em campo só para `can_cast_name`, sai em seguida e `next_uid` é restaurado); se algum a libera neste turno, joga o de maior `land_play_score` entre os que liberam. Chave `COMMANDER_ENABLING_LAND` (padrão ligada; desligada = comportamento de `d4a122b`, bit a bit). Contador do estado `m["commander_land_overrides"]` e contador global `COMMANDER_LAND_OVERRIDES_ANYWHERE` (só serve à bit-identidade).

## Resultado (pareado, mesmas sementes; `resumos/ab_*.txt`)
**O efeito real é no comandante até o T3; o resto do jogo mexe pouco.**

| N, modo | partidas idênticas ao antes | comandante até T3 | até T4 | planeswalkers em campo no T4 | mesa limpa no T8 / no T10 |
|---|---|---|---|---|---|
| 10.000, padrão | 86,6% | 81,02% → 90,18%: **+9,16 ±0,57 pontos** | +0,37 ±0,12 | +0,0595 ±0,0057 por partida | **+0,84 ±0,29 / +1,09 ±0,37 pontos** |
| 10.000, resiliência | 83,8% | **+9,16 ±0,57** | +0,39 ±0,12 | +0,0518 ±0,0059 | +0,07 ±0,07 / +0,07 ±0,21 (dentro do ruído) |
| 2.000, padrão | 86,2% | +9,20 ±1,27 | +0,50 ±0,31 | +0,0590 ±0,0138 | +0,60 ±0,65 / +0,90 ±0,78 |
| 2.000, resiliência | 83,7% | +9,20 ±1,27 | +0,50 ±0,31 | +0,0560 ±0,0141 | 0,00 / 0,00 |

Também sobem, no padrão (N = 10.000): planeswalkers no T6 +0,054 ±0,010 e no T8 +0,042 ±0,018; mana no T6 +0,035 ±0,011 e no T8 +0,093 ±0,030; a mão no T4 cai 0,059 ±0,007 (gastou mais cartas). `self_lost` e `m_pw_entered` ficam dentro do IC95%.

## Validação (Regras #1 e #10)
- **Smoke** (`resumos/smoke.txt`): 99 cartas, 99 distintas, 0 desconhecidas, 0 duplicadas não-básicas; 200 partidas por modo, antes e depois, sem exceção.
- **Regressão 20.000 × 2 modos × 2 configurações** (`resumos/regressao_20000.txt`): 0 exceções, 0 carta acima do baralho, 0 campos negativos, com a chave ligada e com a chave desligada.
- **Bit-identidade 20.000 × 2 modos** (`resumos/bitident_20000.txt`, 4 blocos de 5.000 sementes 5.000.000–5.019.999; `orquestracao/bitident_tam.py`): chave desligada == `d4a122b` em **40.000 de 40.000** execuções; chave ligada: **34.192 sem troca em estado nenhum, idênticas ao `d4a122b`, e 5.808 com troca** (as únicas que podem diferir); **0 divergências**. O script exige > 0 partidas em cada grupo (verificação vácua é falha).
- **Determinismo** (`resumos/determinismo.txt`): __DET__

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_{2000,10000}{,_resiliencia}.json.xz` | bruto do A/B (variantes `antes` e `depois`, colunas-v1) | usado |
| `resumos/ab_*.txt` | tabelas (função só do bruto: `driver.py sum`) | usado (`cmp`) |
| `resumos/{smoke,regressao_20000,bitident_20000,determinismo,status,log_driver}.txt`, `resumos/bitident_chunk_*.txt` | saída de cada etapa | usado |
| `codigo/tam_goldfish_v1_ANTES_d4a122b.py`, `codigo/tam_cartas.json` | o simulador como estava e o recorte de oráculo que ele lê | snapshot |
| `orquestracao/{abgen.py,driver.py,config.json,bitident_tam.py,rodar_tudo.sh,verificar_reproducao.sh}` | harness (o `driver.py`/`abgen.py` são os da rodada de 2026-10-22 do Tam) | usado |
| `SHA256SUMS`, `descomprimir.sh` | somas e descompressão | ver abaixo |

Reproduz: `bash tam-the-possibility-wubrg/resultados-ab/2026-11-11-terreno-comandante/orquestracao/verificar_reproducao.sh` (refaz as 4 tabelas dos brutos e compara por `cmp`, testa os `.xz` e confere o `SHA256SUMS`). **Não re-executa** as simulações (A/B, regressão, bit-identidade, determinismo): são as saídas das execuções originais.

## Não coberto (Regra #7)
- A política só olha a **Tam (o comandante)**. Terreno que libera outra magia (Plaza ou Great Hall para um planeswalker lendário que não é o comandante) segue com `land_play_score`.
- A escolha **entre terrenos que liberam** é por `land_play_score`; não há ensaio de qual deixa o resto do turno melhor.
- A auditoria de ocasiões (32%/34%) foi medida em N = 2.000, só ANTES da correção; não reaudito com a chave ligada (é 0 por construção da política).
- O ensaio do "terreno virado primeiro" (classe (k)) não foi tocado e **não foi medido** o comandante até T2 com e sem ele.
- Sem calibração contra a mesa real do usuário (o modo resiliência usa o perfil de oponente do simulador).
- A leitura "T2 domina" vem da distribuição por turno da auditoria; **não separei** quanto do ganho no T3 vem de cada terreno.
