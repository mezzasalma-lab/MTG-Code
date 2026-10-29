# Mothman: guarda do payoff-primeiro, aritmética × ensaio a seco (2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Origem: ao corrigir a ordem terreno × payoff de landfall nos outros 5 simuladores (`<deck>/resultados-ab/2026-10-07-landfall-payoff-primeiro/`) a **guarda aritmética** do comandante (`custo do comandante <= mana de agora + 1`, a que o Mothman arquivou em `../2026-10-06-landfall-payoff-primeiro/`) falhou no Beorn (comandante atrasado em 38 de 2.000 partidas) e foi trocada por um **ensaio a seco** do resto da fase. Pergunta aqui: a mesma falha existe no Mothman e quanto ela mexe nos números que eu já tinha publicado?

## Resposta curta (medida)
1. **A guarda aritmética do Mothman também estava errada**, por outro motivo: é cega a COR. Cena dirigida (`testes/testes_dirigidos.py`, `payoff_primeiro_guarda_por_ensaio_a_seco_nao_desloca_o_comandante`): Ruin Crab custa `{U}` (1) e o comandante `{1}{B}{G}{U}` (4); `1 + 4 = 5 = mana de agora (4) + 1`, a fórmula deixa o Crab passar, mas ele gasta o ÚNICO Island e o comandante fica sem `{U}`: **não é conjurado**. O ensaio a seco vê isso.
2. **Os números publicados em 2026-10-06 estavam superestimados** (guarda aritmética × ensaio a seco, N = 10.000 pareado, padrão): Ruin Crab **+0,319 → +0,201 gatilhos por partida (+21% → +13%)**; Icetill replays +0,170 → +0,024; mesa limpa até T8 **+0,9 → +0,6 ponto**; payoff antes do terreno 0,37 → 0,21 vezes por partida. Mesma direção, magnitude cerca de um terço menor (Crab −37%, mesa limpa até T8 −33%; os IC95% da tabela se sobrepõem no T8).
3. **A conclusão do pacote de 5 trocas + Master se mantém nas duas guardas** (N = 2.000, pacote − guarda): mesa limpa até T8 **+6,6 pontos (aritmética) × +5,6 (ensaio)** no padrão, +4,1 × +4,0 na resiliência.
4. **Decisão:** o padrão do simulador passou a `LANDFALL_GUARD_DRYRUN = True` (ensaio a seco), igual aos outros 5 simuladores. A pasta `../2026-10-06-landfall-payoff-primeiro/` fica como estava (lotes da guarda aritmética, **superados em magnitude**, marcados), com `LANDFALL_GUARD_DRYRUN = false` fixado nos configs e no `bitident.py` para reproduzir os brutos.
**Não verificado:** o critério do ensaio a seco (nenhuma jogada NÃO-terreno que a ordem antiga faria pode deixar de acontecer) é conservador: no Mothman ele recusa cerca de metade dos payoffs que a guarda aritmética deixava passar e uma parte dessas recusas pode ser efeito colateral benigno do próprio landfall (mais mill/terreno do cemitério muda a mão). Por isso o número do ensaio é um **limite inferior** do efeito do payoff-primeiro; o da guarda aritmética, um limite superior.

## O que mudou no código (`../../mothman_goldfish_v1.py`)
- Chave nova `LANDFALL_GUARD_DRYRUN` (padrão **True**; `False` = guarda aritmética arquivada em 2026-10-06) e `_hoist_loses_a_play(state, t, phase)`: copia o estado, roda o resto da fase (`play_land_phase` e o loop de conjuração) na ordem antiga e na nova, e recusa o payoff se algo que a antiga tiraria da mão (terrenos não contam: o Icetill troca terreno da mão pelo do cemitério) deixa de sair, ou se o comandante deixa de ser conjurado.
- Com `LANDFALL_PAYOFF_FIRST = False` nada muda (bit-identidade com `91b1a3d` refeita com o código final: `resumos/bitident_20000.txt`). Snapshot do código anterior a esta rodada: `codigo/mothman_goldfish_v1_ANTES_7ff46e0.py` (a guarda aritmética era a única).
- Testes dirigidos: `testes/testes_dirigidos.py` **141/141** (139 + 2 novos; o do Icetill passou a contar só os mills do estado real, porque o ensaio roda cópias que também passam pela função de mill).
- Referência exata do experimento que revelou o problema (monkeypatch, sem editar o arquivo vivo): em 800 sementes, 292 payoffs antes do terreno; o ensaio a seco recusaria 152 (52%) pelo critério de jogada não-terreno perdida, e em 42 deles o payoff nem era conjurado na ordem antiga.

## Como os dados foram gerados
`orquestracao/driver_mm.py` + `abgen.py` (cópias dos de `../2026-10-06-landfall-payoff-primeiro/orquestracao/`), `config.json`: variantes `base` (ordem antiga), `aritmetica`, `ensaio`, `pacote5+master+aritmetica`, `pacote5+master+ensaio` (N = 2.000, sementes 1.000.000+i) e `base`/`aritmetica`/`ensaio` (N = 10.000, sementes 3.000.000+i); 12 turnos; modos padrão e resiliência; regressão 20.000 × 2 modos da variante `ensaio`. `PYTHONHASHSEED=0` fixado pelo driver. `resumos/resumo_guarda.md` é a tabela desta página (`orquestracao/resumo_guarda.py`, só lê os brutos).

## Tabelas (de `resumos/resumo_guarda.md`)
### N=10.000, modo padrao (12 turnos; diferenca pareada, `*` = excede o IC95%)

| campo | media da base | aritmetica - base | ensaio - base | ensaio - aritmetica |
|---|---|---|---|---|
| `payoff_first_casts` | 0.0000 | +0.372 ± 0.012 * | +0.211 ± 0.009 * | -0.161 ± 0.008 * |
| `ruin_crab_mills` | 1.5147 | +0.319 ± 0.031 * | +0.201 ± 0.022 * | -0.118 ± 0.025 * |
| `icetill_replays` | 0.8544 | +0.170 ± 0.017 * | +0.024 ± 0.010 * | -0.146 ± 0.015 * |
| `mothman_counters_placed_total` | 75.1248 | +0.943 ± 0.575 * | +0.695 ± 0.384 * | -0.248 ± 0.459 |
| `cards_milled_opp_total` | 84.1843 | +1.586 ± 0.442 * | +1.218 ± 0.289 * | -0.368 ± 0.358 * |
| `cleared_T7` | 0.1477 | +0.005 ± 0.003 * | +0.004 ± 0.002 * | -0.002 ± 0.002 |
| `cleared_T8` | 0.5073 | +0.009 ± 0.004 * | +0.006 ± 0.002 * | -0.002 ± 0.003 |
| `cleared_T10` | 0.8497 | -0.000 ± 0.003 | +0.001 ± 0.002 | +0.001 ± 0.002 |
| `first_elim_T6` | 0.3875 | +0.005 ± 0.002 * | +0.003 ± 0.002 * | -0.002 ± 0.002 * |
| `self_lost` | 0.0329 | +0.000 ± 0.003 | -0.000 ± 0.002 | -0.001 ± 0.002 |

### N=2.000, modo padrao: efeito do pacote de 5 trocas + Master DENTRO de cada guarda (pacote+guarda - guarda)

| campo | pacote - aritmetica | pacote - ensaio |
|---|---|---|
| `cleared_T7` | +0.042 ± 0.024 * | +0.041 ± 0.024 * |
| `cleared_T8` | +0.066 ± 0.031 * | +0.056 ± 0.031 * |
| `cleared_T10` | +0.033 ± 0.020 * | +0.024 ± 0.020 * |
| `self_lost` | -0.010 ± 0.009 * | +0.000 ± 0.009 |

### N=10.000, modo resiliencia (12 turnos; diferenca pareada, `*` = excede o IC95%)

| campo | media da base | aritmetica - base | ensaio - base | ensaio - aritmetica |
|---|---|---|---|---|
| `payoff_first_casts` | 0.0000 | +0.287 ± 0.010 * | +0.176 ± 0.008 * | -0.111 ± 0.007 * |
| `ruin_crab_mills` | 1.0053 | +0.221 ± 0.025 * | +0.143 ± 0.018 * | -0.078 ± 0.020 * |
| `icetill_replays` | 0.7103 | +0.122 ± 0.017 * | +0.026 ± 0.010 * | -0.096 ± 0.014 * |
| `mothman_counters_placed_total` | 54.0751 | +0.160 ± 0.435 | +0.260 ± 0.298 | +0.099 ± 0.362 |
| `cards_milled_opp_total` | 69.4422 | +0.803 ± 0.399 * | +0.741 ± 0.274 * | -0.062 ± 0.324 |
| `cleared_T7` | 0.0595 | +0.004 ± 0.002 * | +0.001 ± 0.001 | -0.003 ± 0.001 * |
| `cleared_T8` | 0.2352 | +0.008 ± 0.003 * | +0.005 ± 0.002 * | -0.003 ± 0.002 * |
| `cleared_T10` | 0.5813 | +0.001 ± 0.003 | -0.000 ± 0.002 | -0.001 ± 0.002 |
| `first_elim_T6` | 0.2327 | +0.004 ± 0.002 * | +0.002 ± 0.001 * | -0.002 ± 0.002 * |
| `self_lost` | 0.0153 | +0.000 ± 0.002 | +0.000 ± 0.001 | +0.000 ± 0.002 |

### N=2.000, modo resiliencia: efeito do pacote de 5 trocas + Master DENTRO de cada guarda (pacote+guarda - guarda)

| campo | pacote - aritmetica | pacote - ensaio |
|---|---|---|
| `cleared_T7` | +0.019 ± 0.016 * | +0.016 ± 0.016 * |
| `cleared_T8` | +0.041 ± 0.027 * | +0.040 ± 0.026 * |
| `cleared_T10` | +0.048 ± 0.028 * | +0.045 ± 0.028 * |
| `self_lost` | -0.005 ± 0.007 | -0.007 ± 0.007 * |

## Validação
| verificação | resultado | arquivo |
|---|---|---|
| testes dirigidos (`../../testes/testes_dirigidos.py`) | **141/141** | — |
| smoke das 5 variantes (99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos) | 0 exceções | `resumos/smoke.txt` |
| regressão, variante `ensaio`, 20.000 × 2 modos | 0 exceções, 0 carta acima do baralho, 0 campo negativo | `resumos/regressao_20000.txt` |
| bit-identidade, chave `LANDFALL_PAYOFF_FIRST` desligada == `91b1a3d`, 20.000 × 2 modos (4 fatias de 5.000), código final | **0 divergências**: 40.000 de 40.000 idênticas com a chave desligada; ligada: 32.859 sem disparo e idênticas, 7.141 com disparo | `resumos/bitident_20000.txt` |
| determinismo entre processos (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, 12 turnos) | **0 divergências** | `resumos/determinismo.txt` |

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_2000*.json.xz`, `raw_ab_10000*.json.xz` | bruto por partida (5 variantes × 2.000; 3 × 10.000), padrão e resiliência | usado |
| `resumos/ab_*.txt`, `compacto_*.txt`, `resumo_guarda.md` | tabelas pareadas | usado (`cmp` conferido) |
| `resumos/smoke.txt`, `regressao_20000.txt`, `bitident_20000.txt`, `determinismo.txt`, `log_driver.txt` | validação | usado |
| `orquestracao/*` | harness, `config.json`, `resumo_guarda.py`, `verificar_reproducao.sh` | apoio |
| `codigo/mothman_goldfish_v1_ANTES_7ff46e0.py` | simulador anterior (só a guarda aritmética) | referência |

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh --tudo` em 2026-10-07: **13 de 13 saídas byte a byte iguais** (`cmp`): as 8 tabelas (`ab_*` e `compacto_*`) e `resumo_guarda.md` refeitos só dos `.json.xz`; e, **re-simulando** o lote de 2.000 nos dois modos (5 variantes), as 2 tabelas e os 2 brutos (descomprimidos) idênticos aos arquivados. Saída em `resumos/verificacao_reproducao.txt`. A pasta irmã `../2026-10-06-landfall-payoff-primeiro/` também foi reverificada com o novo padrão do simulador (13 de 13, `resumos/verificacao_reproducao.txt` dela).
**Não conferido por re-execução:** o lote de 10.000 (só as tabelas a partir do bruto), a regressão e a bit-identidade de 20.000 (saídas das execuções originais; a bit-identidade foi feita em 4 fatias paralelas de 5.000 sementes) e o determinismo.
