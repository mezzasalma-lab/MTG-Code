# Beorn the Fierce: payoff de landfall antes do terreno (`LANDFALL_PAYOFF_FIRST`, 2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Pedido do usuário (2026-10-07): *"Corrige os simuladores com erro no script para automatizar a ordem de jogadas para o landfall"*. Classe achada no Mothman em 2026-10-06 (`wise-mothman-sultai/resultados-ab/2026-10-06-landfall-payoff-primeiro/`): o simulador jogava o terreno ANTES de conjurar o payoff de landfall, então o terreno do turno nunca disparava o landfall que o jogador real teria armado. `varredura-2026-10-05/scripts/audit_landfall_ordem.py` listou este deck; a ordem do turno foi lida à mão (abaixo) e o erro confirmado.
Simulador: `../../beorn_goldfish_v1.py` (commit desta pasta). Código **anterior** fixado em `codigo/beorn_goldfish_v1_ANTES_0ee4972.py` (idêntico ao commit `0ee4972`).

## Ordem do turno (lida inteira, Regra #6)
`play_turn`: compra → `try_bala_ged_recovery` → `play_land` → `try_use_own_interaction` → `main_phase` (comandante a partir do T3, depois o loop guloso por `priority`) → combate (relida inteira, Regra #6).
Gancho novo: `play_turn` chama `cast_landfall_payoffs_first(state, log)` entre `try_bala_ged_recovery` e `play_land`.

## O que mudou no código
- Chave `LANDFALL_PAYOFF_FIRST` (padrão **True**; `False` = ordem antiga, **bit-idêntica** ao commit `0ee4972`) e `LANDFALL_PAYOFFS` = as cartas com gatilho de landfall que o arquivo trata:

| payoff | cláusula de landfall (oráculo do cache) |
|---|---|
| `Lotus Cobra` | Landfall — add one mana of any color |
| `Tireless Provisioner` | Landfall — Food ou Treasure (modelado como mana avulsa) |
| `Tireless Tracker` | Landfall — investigate |
| `Beorn's Hospitality` | Landfall — +1/+1 counter em criatura |
| `Dancing from Dark to Dawn` | Landfall — Urso 2/2 |
| `Necklace of Girion` | Whenever a Forest you control enters — +1/+1 counter |

- `cast_landfall_payoffs_first`: com um terreno ainda por jogar, conjura antes os payoffs que o mana de **agora** já paga, na ordem do próprio loop de conjuração do deck. **Guarda por ensaio a seco** (`_hoist_loses_a_play`): cópia profunda do estado, roda o resto da fase pré-combate na ordem ANTIGA e na NOVA, e só deixa o payoff passar se nada que a ordem antiga conjuraria/jogaria (comandante, rochas de mana, qualquer jogada de prioridade maior) deixar de acontecer na nova. A 1ª versão usava a fórmula `custo do comandante <= mana de agora + 1` e **estava errada** (não conta cor, mana de landfall já em campo, land drop extra).
- **Achado do A/B (a 1ª guarda estava errada):** a 1ª versão protegia o comandante com a fórmula `custo do comandante <= mana de agora + 1`. Ela não conta o mana de landfall que já está em campo (Lotus Cobra, Provisioner): em 38 de 2.000 partidas pareadas o comandante saiu do T3 para o T4 (Provisioner (3) antes do terreno com 2 terrenos + Cobra em campo (3 de mana agora) deixava 0 + 1 (terreno) + 1 (landfall do Cobra) + 1 (do Provisioner) = 3 para a Beorn (5), enquanto a ordem antiga fazia terreno + landfall do Cobra = 5 e conjurava a Beorn no T3) e, em outras, a Hospitality antes do terreno tirou a rocha de mana (Firdoch Core) que a ordem antiga conjurava. Trocada por **ensaio a seco** (`_hoist_loses_a_play`): roda o resto da fase na ordem antiga e na nova, em cópias, e só deixa o payoff passar se nada que a antiga conjuraria/jogaria deixar de acontecer. Depois: 0 atrasos do comandante em 2.000 pareadas (3 adiantados).
- 2 testes dirigidos novos provam a diferença: com a guarda aritmética antiga o teste do Cobra em campo e o da rocha de mana FALHAM (`PASSOU` seria sinal de teste que não discrimina).
- Campo novo `payoff_first_casts` (quantas vezes um payoff entrou antes do terreno) e testes dirigidos em `../../test_beorn_goldfish.py`: **8/8** passam.

## Validação (Regra #1 / #10)
| verificação | resultado | arquivo |
|---|---|---|
| smoke: 99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos (vivo e snapshot) | 0 exceções | `resumos/smoke.txt` |
| testes dirigidos | **8/8** | `../../test_beorn_goldfish.py` |
| bit-identidade, 20.000 partidas × 2 modos (chave desligada == snapshot; campo novo ignorado) | **0 divergências** | `resumos/bitident_20000.txt` |
| regressão, 20.000 × 2 modos × 2 configurações (ligada, desligada) | **0 exceções**; ver nota | `resumos/regressao_20000.txt` |
| determinismo entre processos (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo) | **0 divergências** | `resumos/determinismo.txt` |
| A/B pareado 2.000 e 10.000 (padrão e resiliência) | tabela abaixo | `resumos/ab_*.txt` |

Saídas literais:
```
    DEPOIS (arquivo vivo): cartas na biblioteca=99 | distintas=69 | desconhecidas (fora do CARD_DB)=[] | duplicadas nao-basicas=[]
    200 partidas modo padrao: excecoes=0
    200 partidas modo resiliencia: excecoes=0
    ANTES (snapshot): cartas na biblioteca=99 | distintas=69 | desconhecidas (fora do CARD_DB)=[] | duplicadas nao-basicas=[]
    200 partidas modo padrao: excecoes=0
    200 partidas modo resiliencia: excecoes=0
    chaves da correcao no arquivo vivo: LANDFALL_PAYOFF_FIRST=True
    padrao: N=20000 partidas diferentes=0 -> BIT-IDENTICO
    resiliencia: N=20000 partidas diferentes=0 -> BIT-IDENTICO
    depois (repositorio)   padrao       partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    depois (repositorio)   resiliencia  partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    chave_desligada        padrao       partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    chave_desligada        resiliencia  partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    beorn-fierce               padrao       N=1500 sementes divergentes entre 3 hash seeds: 0 [] campos: []
    beorn-fierce               resiliencia  N=1500 sementes divergentes entre 3 hash seeds: 0 [] campos: []
```
O smoke da 1ª rodada deu `cartas na biblioteca=0` (o `driver.py` do modelo não contava a biblioteca de simuladores baseados em dict: verificação vácua, Regra #10 item 4); refeito com o `driver.py` corrigido (99 cartas, 0 desconhecidas).

## O que o A/B mediu (N = 10.000 pareado, mesmas sementes; `base` = ordem antiga; `*` = a diferença excede o IC95%)
Frequência do conserto: padrao: payoff_first_casts por partida = 0.865 | partidas com >= 1 = 57.4% (N=10000) | resiliencia: payoff_first_casts por partida = 0.622 | partidas com >= 1 = 45.9% (N=10000).

| campo (N=10.000 pareado) | padrao: base -> depois (dif ± IC95%) | resiliencia: base -> depois (dif ± IC95%) |
|---|---|---|
| `lands_played_total` | 6.963 -> 6.982 (+0.019 ± 0.004) * | 6.572 -> 6.593 (+0.021 ± 0.004) * |
| `spells_cast` | 13.144 -> 13.401 (+0.257 ± 0.019) * | 11.065 -> 11.213 (+0.148 ± 0.017) * |
| `bear_count_final` | 8.430 -> 8.816 (+0.387 ± 0.045) * | - |
| `counters_on_board_final` | 16.567 -> 18.854 (+2.288 ± 0.326) * | - |
| `counters_on_board` | - | 8.097 -> 9.144 (+1.048 ± 0.171) * |
| `extra_draws` | 20.429 -> 21.142 (+0.713 ± 0.095) * | 10.698 -> 11.052 (+0.354 ± 0.076) * |
| `battlefield_count` | 21.493 -> 22.055 (+0.562 ± 0.056) * | - |
| `finishers_resolved` | 0.572 -> 0.595 (+0.024 ± 0.005) * | - |
| `commander_cast_turn__ate_T3` | 0.174 -> 0.174 (+0.000 ± 0.000) | 0.085 -> 0.084 (-0.001 ± 0.001) * |
| `commander_cast_turn__ate_T4` | 0.619 -> 0.620 (+0.001 ± 0.001) * | 0.337 -> 0.336 (-0.001 ± 0.002) |
| `commander_cast_turn__ate_T5` | 0.896 -> 0.896 (+0.000 ± 0.000) | 0.557 -> 0.557 (-0.000 ± 0.003) |
| `finisher_turn__ate_T6` | 0.175 -> 0.181 (+0.005 ± 0.002) * | 0.134 -> 0.136 (+0.003 ± 0.002) * |
| `finisher_turn__nunca` | 0.566 -> 0.554 (-0.012 ± 0.004) * | 0.667 -> 0.662 (-0.005 ± 0.003) * |
| `clues` | - | 0.108 -> 0.166 (+0.058 ± 0.007) * |
| partidas com resultado idêntico ao da base | 54.0% | 56.9% |

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_2000*.json.xz`, `raw_ab_10000*.json.xz` | bruto por partida (antes × depois), padrão e resiliência | usado |
| `resumos/ab_*.txt`, `resumos/ab_resumo.md` | tabelas pareadas completas / as linhas desta página | usado (`cmp` conferido) |
| `resumos/smoke.txt`, `bitident_20000.txt`, `regressao_20000.txt`, `determinismo.txt`, `frequencia_hoist.txt` | validação | usado |
| `orquestracao/driver.py`, `abgen.py`, `config.json`, `verificar_reproducao.sh` | harness genérico (`config.json` = variantes e campos de destaque) | apoio |
| `codigo/*_ANTES_0ee4972.py` | simulador anterior (para a bit-identidade) | referência |

## Não coberto (Regra #7)
Magia que põe terreno em campo (Cultivate, Farseek, Three Visits...) conjurada antes de um payoff que o mana também pagaria depois do terreno; terreno que volta ao campo (blink, Lander); só a 1ª fase principal; a política de um jogador humano que prefere guardar o terreno por informação. **Classes do motor NÃO varridas aqui:** as demais da Regra #10 (esta rodada só mexeu na ordem terreno × payoff).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh --tudo` em 2026-10-07: **11 de 11 saídas byte a byte iguais** (`cmp`): as 4 tabelas `ab_*` refeitas só dos `.json.xz`; e, **re-simulando** o lote de 2.000 nos dois modos, o smoke, as 2 tabelas e os 2 brutos (descomprimidos) idênticos aos arquivados, a bit-identidade (N = 2.000 × 2 modos, chave desligada == snapshot) e a regressão (N = 2.000 × 4 configurações, 0 exceções). Saída em `resumos/verificacao_reproducao.txt`.
**Não conferido por re-execução:** os lotes de 10.000 (só as tabelas a partir do bruto), a bit-identidade e a regressão de 20.000 (saídas das execuções originais), o determinismo entre processos (`resumos/determinismo.txt`, `varredura-2026-10-05/scripts/det_check.sh`) e a extração de `frequencia_hoist.txt`/`ab_resumo.md` (scripts `varredura-2026-10-05/scripts/hoist_stats.py` e `resume_ab_landfall.py`, refeitos dos brutos). **Nota do harness:** os lotes de bit-identidade/A/B/regressão foram gerados com o `driver.py` antes do suporte a `LOTES` (variável de ambiente que só limita a verificação rápida aos lotes de 2.000); com `LOTES` ausente o comportamento é idêntico.
