# Thranduil, the Elvenking: payoff de landfall antes do terreno (`LANDFALL_PAYOFF_FIRST`, 2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Pedido do usuário (2026-10-07): *"Corrige os simuladores com erro no script para automatizar a ordem de jogadas para o landfall"*. Classe achada no Mothman em 2026-10-06 (`wise-mothman-sultai/resultados-ab/2026-10-06-landfall-payoff-primeiro/`): o simulador jogava o terreno ANTES de conjurar o payoff de landfall, então o terreno do turno nunca disparava o landfall que o jogador real teria armado. `varredura-2026-10-05/scripts/audit_landfall_ordem.py` listou este deck; a ordem do turno foi lida à mão (abaixo) e o erro confirmado.
Simulador: `../../thranduil_goldfish_v1.py` (commit desta pasta). Código **anterior** fixado em `codigo/thranduil_goldfish_v1_ANTES_4d76ae0.py` (idêntico ao commit `4d76ae0`).

## Ordem do turno (lida inteira, Regra #6)
`play_turn`: compra → `try_takenuma_channel` → `play_land` → `play_land` (2ª chamada: só vale com a Company) → `try_use_own_interaction` → `main_phase` (comandante a partir do T3, depois o loop por `priority`) → combate (relida inteira, Regra #6).
Gancho novo: `play_turn` chama `cast_landfall_payoffs_first(state, log)` entre `try_takenuma_channel` e o 1º `play_land`.

## O que mudou no código
- Chave `LANDFALL_PAYOFF_FIRST` (padrão **True**; `False` = ordem antiga, **bit-idêntica** ao commit `4d76ae0`) e `LANDFALL_PAYOFFS` = as cartas com gatilho de landfall que o arquivo trata:

| payoff | cláusula de landfall (oráculo do cache) |
|---|---|
| `Thranduil's Company` | As long as you control another Elf, you may play an additional land on each of your turns; Landfall — dois +1/+1 counters |
| `Thranduil, Sindarin Liege // Silvan Rally` | Landfall — Elfo 1/1 (e Elfos +1/+1) |

- `cast_landfall_payoffs_first`: com um terreno ainda por jogar, conjura antes os payoffs que o mana de **agora** já paga, na ordem do próprio loop de conjuração do deck. **Guarda por ensaio a seco** (`_hoist_loses_a_play`): cópia profunda do estado, roda o resto da fase pré-combate na ordem ANTIGA e na NOVA, e só deixa o payoff passar se nada que a ordem antiga conjuraria/jogaria (comandante, rochas de mana, qualquer jogada de prioridade maior) deixar de acontecer na nova. A 1ª versão usava a fórmula `custo do comandante <= mana de agora + 1` e **estava errada** (não conta cor, mana de landfall já em campo, land drop extra).
- **A Company só libera o 2º land drop se entrar ANTES dos terrenos.** Com a ordem antiga o segundo `play_land` nunca era usado no turno em que ela entra (`lands_played_this_turn` 1 contra 2 no teste dirigido).
- Guarda por ensaio a seco (`_hoist_loses_a_play`, como no Beorn): a fórmula aritmética não conta o 2º land drop da Company já em campo; o teste do comandante com imposto falha com a fórmula antiga.
- Campo novo `payoff_first_casts` (quantas vezes um payoff entrou antes do terreno) e testes dirigidos em `../../test_thranduil_goldfish.py`: **7/7** passam.

## Validação (Regra #1 / #10)
| verificação | resultado | arquivo |
|---|---|---|
| smoke: 99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos (vivo e snapshot) | 0 exceções | `resumos/smoke.txt` |
| testes dirigidos | **7/7** | `../../test_thranduil_goldfish.py` |
| bit-identidade, 20.000 partidas × 2 modos (chave desligada == snapshot; campo novo ignorado) | **0 divergências** | `resumos/bitident_20000.txt` |
| regressão, 20.000 × 2 modos × 2 configurações (ligada, desligada) | **0 exceções**; ver nota | `resumos/regressao_20000.txt` |
| determinismo entre processos (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo) | **0 divergências** | `resumos/determinismo.txt` |
| A/B pareado 2.000 e 10.000 (padrão e resiliência) | tabela abaixo | `resumos/ab_*.txt` |

Saídas literais:
```
    DEPOIS (arquivo vivo): cartas na biblioteca=99 | distintas=90 | desconhecidas (fora do CARD_DB)=[] | duplicadas nao-basicas=[]
    200 partidas modo padrao: excecoes=0
    200 partidas modo resiliencia: excecoes=0
    ANTES (snapshot): cartas na biblioteca=99 | distintas=90 | desconhecidas (fora do CARD_DB)=[] | duplicadas nao-basicas=[]
    200 partidas modo padrao: excecoes=0
    200 partidas modo resiliencia: excecoes=0
    chaves da correcao no arquivo vivo: LANDFALL_PAYOFF_FIRST=True
    padrao: N=20000 partidas diferentes=0 -> BIT-IDENTICO
    resiliencia: N=20000 partidas diferentes=0 -> BIT-IDENTICO
    depois (repositorio)   padrao       partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    depois (repositorio)   resiliencia  partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={'mana_spent_this_turn': 1}
    chave_desligada        padrao       partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    chave_desligada        resiliencia  partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={'mana_spent_this_turn': 1}
    thranduil-sultai           padrao       N=1500 sementes divergentes entre 3 hash seeds: 0 [] campos: []
    thranduil-sultai           resiliencia  N=1500 sementes divergentes entre 3 hash seeds: 0 [] campos: []
```
`campos negativos={'mana_spent_this_turn': 1}` na regressão do modo resiliência (1 em 20.000) aparece **igual com a chave desligada**: é anterior a esta correção (não investigado aqui).

## O que o A/B mediu (N = 10.000 pareado, mesmas sementes; `base` = ordem antiga; `*` = a diferença excede o IC95%)
Frequência do conserto: padrao: payoff_first_casts por partida = 0.204 | partidas com >= 1 = 19.3% (N=10000) | resiliencia: payoff_first_casts por partida = 0.146 | partidas com >= 1 = 14.0% (N=10000).

| campo (N=10.000 pareado) | padrao: base -> depois (dif ± IC95%) | resiliencia: base -> depois (dif ± IC95%) |
|---|---|---|
| `lands_played_total` | 6.987 -> 7.037 (+0.050 ± 0.006) * | 6.519 -> 6.546 (+0.027 ± 0.005) * |
| `landfall_elf_tokens` | 0.291 -> 0.431 (+0.140 ± 0.010) * | 0.141 -> 0.231 (+0.090 ± 0.008) * |
| `thranduils_company_counters` | 0.710 -> 1.061 (+0.350 ± 0.025) * | 0.315 -> 0.548 (+0.232 ± 0.019) * |
| `spells_cast` | 11.837 -> 11.854 (+0.017 ± 0.013) * | 10.031 -> 10.030 (-0.001 ± 0.009) |
| `extra_draws` | 12.316 -> 12.336 (+0.021 ± 0.048) | 6.730 -> 6.725 (-0.005 ± 0.030) |
| `commander_cast_turn__ate_T3` | - | 0.057 -> 0.058 (+0.000 ± 0.001) |
| `commander_cast_turn__ate_T4` | - | 0.288 -> 0.289 (+0.000 ± 0.002) |
| `commander_cast_turn__ate_T5` | - | 0.516 -> 0.516 (+0.000 ± 0.002) |
| `finisher_turn__ate_T6` | 0.213 -> 0.215 (+0.002 ± 0.002) * | 0.117 -> 0.117 (+0.001 ± 0.001) |
| `finisher_turn__nunca` | 0.391 -> 0.391 (-0.000 ± 0.002) | 0.658 -> 0.658 (-0.000 ± 0.002) |
| `finishers_activated` | 1.862 -> 1.871 (+0.009 ± 0.007) * | - |
| partidas com resultado idêntico ao da base | 80.7% | 86.0% |

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_2000*.json.xz`, `raw_ab_10000*.json.xz` | bruto por partida (antes × depois), padrão e resiliência | usado |
| `resumos/ab_*.txt`, `resumos/ab_resumo.md` | tabelas pareadas completas / as linhas desta página | usado (`cmp` conferido) |
| `resumos/smoke.txt`, `bitident_20000.txt`, `regressao_20000.txt`, `determinismo.txt`, `frequencia_hoist.txt` | validação | usado |
| `orquestracao/driver.py`, `abgen.py`, `config.json`, `verificar_reproducao.sh` | harness genérico (`config.json` = variantes e campos de destaque) | apoio |
| `codigo/*_ANTES_4d76ae0.py` | simulador anterior (para a bit-identidade) | referência |

## Não coberto (Regra #7)
Magia que põe terreno em campo (Cultivate, Farseek, Three Visits...) conjurada antes de um payoff que o mana também pagaria depois do terreno; terreno que volta ao campo (blink, Lander); só a 1ª fase principal; a política de um jogador humano que prefere guardar o terreno por informação. **Classes do motor NÃO varridas aqui:** as demais da Regra #10 (esta rodada só mexeu na ordem terreno × payoff).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh --tudo` em 2026-10-07: **11 de 11 saídas byte a byte iguais** (`cmp`): as 4 tabelas `ab_*` refeitas só dos `.json.xz`; e, **re-simulando** o lote de 2.000 nos dois modos, o smoke, as 2 tabelas e os 2 brutos (descomprimidos) idênticos aos arquivados, a bit-identidade (N = 2.000 × 2 modos, chave desligada == snapshot) e a regressão (N = 2.000 × 4 configurações, 0 exceções). Saída em `resumos/verificacao_reproducao.txt`.
**Não conferido por re-execução:** os lotes de 10.000 (só as tabelas a partir do bruto), a bit-identidade e a regressão de 20.000 (saídas das execuções originais), o determinismo entre processos (`resumos/determinismo.txt`, `varredura-2026-10-05/scripts/det_check.sh`) e a extração de `frequencia_hoist.txt`/`ab_resumo.md` (scripts `varredura-2026-10-05/scripts/hoist_stats.py` e `resume_ab_landfall.py`, refeitos dos brutos). **Nota do harness:** os lotes de bit-identidade/A/B/regressão foram gerados com o `driver.py` antes do suporte a `LOTES` (variável de ambiente que só limita a verificação rápida aos lotes de 2.000); com `LOTES` ausente o comportamento é idêntico.
