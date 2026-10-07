# Toph, the First Metalbender: payoff de landfall antes do terreno (`LANDFALL_PAYOFF_FIRST`, 2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Pedido do usuário (2026-10-07): *"Corrige os simuladores com erro no script para automatizar a ordem de jogadas para o landfall"*. Classe achada no Mothman em 2026-10-06 (`wise-mothman-sultai/resultados-ab/2026-10-06-landfall-payoff-primeiro/`): o simulador jogava o terreno ANTES de conjurar o payoff de landfall, então o terreno do turno nunca disparava o landfall que o jogador real teria armado. `varredura-2026-10-05/scripts/audit_landfall_ordem.py` listou este deck; a ordem do turno foi lida à mão (abaixo) e o erro confirmado.
Simulador: `../../toph_goldfish_v1.py` (commit desta pasta). Código **anterior** fixado em `codigo/toph_goldfish_v1_ANTES_0030b8b.py` (idêntico ao commit `0030b8b`).

## Ordem do turno (lida inteira, Regra #6)
`main_phase(first=True)`: `play_land` → `conduit_of_worlds_reanimate` → `cast_loop` (comandante primeiro, depois o mais barato primeiro); `play_turn`: untap → upkeep/draw → `main_phase(first=True)` → combate → `main_phase(first=False)` → fim (relida inteira, Regra #6).
Gancho novo: `main_phase` chama `cast_landfall_payoffs_first(state, log)` logo antes de `play_land` (só na 1ª fase principal).

## O que mudou no código
- Chave `LANDFALL_PAYOFF_FIRST` (padrão **True**; `False` = ordem antiga, **bit-idêntica** ao commit `0030b8b`) e `LANDFALL_PAYOFFS` = as cartas com gatilho de landfall que o arquivo trata:

| payoff | cláusula de landfall (oráculo do cache) |
|---|---|
| `Lotus Cobra` | Landfall — add one mana of any color |
| `Nissa, Resurgent Animist` | Landfall — add one mana of any color; 2ª resolução do turno: revela até um Elfo/Elemental |
| `Tireless Provisioner` | Landfall — Food ou Treasure |
| `Bristly Bill, Spine Sower` | Landfall — +1/+1 counter em criatura |
| `Mossborn Hydra` | Landfall — dobra os +1/+1 counters |
| `Tannuk, Memorial Ensign` | Landfall — 1 de dano a cada oponente; 2ª resolução: compra |
| `Toph, Earthbending Master` | Landfall — experience counter |
| `Earthbender Ascension` | Landfall — quest counter; com 4, +1/+1 counter e trample |
| `Scute Swarm` | Landfall — token 1/1 (cópia dele com 6+ terrenos) |
| `Sapling Nursery` | Landfall — Treefolk 3/4 com reach |
| `Springheart Nantuko` | Landfall — paga {1}{G} e copia a criatura encantada, senão Inseto 1/1 |
| `Felidar Retreat` | Landfall — Cat Beast 2/2 ou +1/+1 em todas as criaturas |

- `cast_landfall_payoffs_first`: com um terreno ainda por jogar, conjura antes os payoffs que o mana de **agora** já paga, na ordem do próprio loop de conjuração do deck. **Guarda por ensaio a seco** (`_hoist_loses_a_play`): cópia profunda do estado, roda o resto da fase pré-combate na ordem ANTIGA e na NOVA, e só deixa o payoff passar se nada que a ordem antiga conjuraria/jogaria (comandante, rochas de mana, qualquer jogada de prioridade maior) deixar de acontecer na nova. A 1ª versão usava a fórmula `custo do comandante <= mana de agora + 1` e **estava errada** (não conta cor, mana de landfall já em campo, land drop extra).
- `_hoist_loses_a_play` roda o `main_phase` inteiro numa cópia (`_copia_do_estado`, com `CARD_DB` compartilhado e `memo` NOVO a cada cópia: a 1ª versão reaproveitava o `memo` e a 2ª cópia aliasava a 1ª, `ValueError: list.remove(x)` nos testes). Dentro do ensaio a chave fica desligada (sem recursão).
- Custo: a partida com a chave ligada leva ~2,7× o tempo (53 ms contra 20 ms): o ensaio copia o estado 2 vezes por decisão.
- Springheart Nantuko com bestow usa o mesmo caminho do `cast_loop` (`_cast_payoff`).
- Campo novo `payoff_first_casts` (quantas vezes um payoff entrou antes do terreno) e testes dirigidos em `../../test_toph_goldfish.py`: **67/67 (61 anteriores + 6 novos)** passam.

## Validação (Regra #1 / #10)
| verificação | resultado | arquivo |
|---|---|---|
| smoke: 99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos (vivo e snapshot) | 0 exceções | `resumos/smoke.txt` |
| testes dirigidos | **67/67 (61 anteriores + 6 novos)** | `../../test_toph_goldfish.py` |
| bit-identidade, 20.000 partidas × 2 modos (chave desligada == snapshot; campo novo ignorado) | **0 divergências** | `resumos/bitident_20000.txt` |
| regressão, 20.000 × 2 modos × 2 configurações (ligada, desligada) | **0 exceções**; ver nota | `resumos/regressao_20000.txt` |
| determinismo entre processos (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo) | **0 divergências** | `resumos/determinismo.txt` |
| A/B pareado 2.000 e 10.000 (padrão e resiliência) | tabela abaixo | `resumos/ab_*.txt` |

Saídas literais:
```
    DEPOIS (arquivo vivo): cartas na biblioteca=99 | distintas=97 | desconhecidas (fora do CARD_DB)=[] | duplicadas nao-basicas=[]
    200 partidas modo padrao: excecoes=0
    200 partidas modo resiliencia: excecoes=0
    ANTES (snapshot): cartas na biblioteca=99 | distintas=97 | desconhecidas (fora do CARD_DB)=[] | duplicadas nao-basicas=[]
    200 partidas modo padrao: excecoes=0
    200 partidas modo resiliencia: excecoes=0
    chaves da correcao no arquivo vivo: LANDFALL_PAYOFF_FIRST=True
    padrao: N=20000 partidas diferentes=0 -> BIT-IDENTICO
    resiliencia: N=20000 partidas diferentes=0 -> BIT-IDENTICO
    depois (repositorio)   padrao       partidas ok=20000 | excecoes=0  | carta acima do baralho=6099 | campos negativos={}
    depois (repositorio)   resiliencia  partidas ok=20000 | excecoes=0  | carta acima do baralho=3064 | campos negativos={}
    chave_desligada        padrao       partidas ok=20000 | excecoes=0  | carta acima do baralho=5941 | campos negativos={}
    chave_desligada        resiliencia  partidas ok=20000 | excecoes=0  | carta acima do baralho=3017 | campos negativos={}
    toph-naya                  padrao       N=1500 sementes divergentes entre 3 hash seeds: 0 [] campos: []
    toph-naya                  resiliencia  N=1500 sementes divergentes entre 3 hash seeds: 0 [] campos: []
```
`carta acima do baralho` na regressão (6.099 / 3.064 ligada contra 5.941 / 3.017 desligada) **não é regressão**: é a invariante genérica do harness tropeçando nas fichas e cópias de nome de carta do Toph (Scute Swarm, Springheart), igual na pasta de 2026-10-05 (5.941 / 3.017 com a chave desligada).

## O que o A/B mediu (N = 10.000 pareado, mesmas sementes; `base` = ordem antiga; `*` = a diferença excede o IC95%)
Frequência do conserto: padrao: payoff_first_casts por partida = 0.867 | partidas com >= 1 = 56.9% (N=10000) | resiliencia: payoff_first_casts por partida = 0.729 | partidas com >= 1 = 51.7% (N=10000).

| campo (N=10.000 pareado) | padrao: base -> depois (dif ± IC95%) | resiliencia: base -> depois (dif ± IC95%) |
|---|---|---|
| `landfall_triggers_fired` | 15.255 -> 15.518 (+0.262 ± 0.087) * | 12.922 -> 13.142 (+0.220 ± 0.064) * |
| `spells_cast_total` | 11.378 -> 11.612 (+0.234 ± 0.043) * | 9.945 -> 10.120 (+0.175 ± 0.033) * |
| `lethal_turn__nunca` | 0.740 -> 0.706 (-0.034 ± 0.004) * | 0.880 -> 0.851 (-0.028 ± 0.004) * |
| `lethal_turn__ate_T6` | 0.008 -> 0.013 (+0.005 ± 0.002) * | 0.005 -> 0.008 (+0.003 ± 0.001) * |
| `commander_cast_turn__ate_T3` | 0.144 -> 0.144 (+0.000 ± 0.001) | 0.134 -> 0.134 (+0.000 ± 0.001) |
| `commander_cast_turn__ate_T4` | 0.539 -> 0.543 (+0.004 ± 0.002) * | 0.483 -> 0.489 (+0.005 ± 0.002) * |
| `commander_cast_turn__ate_T5` | - | 0.684 -> 0.695 (+0.011 ± 0.003) * |
| partidas com resultado idêntico ao da base | 43.1% | 48.4% |

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_2000*.json.xz`, `raw_ab_10000*.json.xz` | bruto por partida (antes × depois), padrão e resiliência | usado |
| `resumos/ab_*.txt`, `resumos/ab_resumo.md` | tabelas pareadas completas / as linhas desta página | usado (`cmp` conferido) |
| `resumos/smoke.txt`, `bitident_20000.txt`, `regressao_20000.txt`, `determinismo.txt`, `frequencia_hoist.txt` | validação | usado |
| `orquestracao/driver.py`, `abgen.py`, `config.json`, `verificar_reproducao.sh` | harness genérico (`config.json` = variantes e campos de destaque) | apoio |
| `codigo/*_ANTES_0030b8b.py` | simulador anterior (para a bit-identidade) | referência |

## Não coberto (Regra #7)
Magia que põe terreno em campo (Cultivate, Farseek, Three Visits...) conjurada antes de um payoff que o mana também pagaria depois do terreno; terreno que volta ao campo (blink, Lander); só a 1ª fase principal; a política de um jogador humano que prefere guardar o terreno por informação. **Classes do motor NÃO varridas aqui:** as demais da Regra #10 (esta rodada só mexeu na ordem terreno × payoff).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh --tudo` em 2026-10-07: **11 de 11 saídas byte a byte iguais** (`cmp`): as 4 tabelas `ab_*` refeitas só dos `.json.xz`; e, **re-simulando** o lote de 2.000 nos dois modos, o smoke, as 2 tabelas e os 2 brutos (descomprimidos) idênticos aos arquivados, a bit-identidade (N = 2.000 × 2 modos, chave desligada == snapshot) e a regressão (N = 2.000 × 4 configurações, 0 exceções). Saída em `resumos/verificacao_reproducao.txt`.
**Não conferido por re-execução:** os lotes de 10.000 (só as tabelas a partir do bruto), a bit-identidade e a regressão de 20.000 (saídas das execuções originais), o determinismo entre processos (`resumos/determinismo.txt`, `varredura-2026-10-05/scripts/det_check.sh`) e a extração de `frequencia_hoist.txt`/`ab_resumo.md` (scripts `varredura-2026-10-05/scripts/hoist_stats.py` e `resume_ab_landfall.py`, refeitos dos brutos). **Nota do harness:** os lotes de bit-identidade/A/B/regressão foram gerados com o `driver.py` antes do suporte a `LOTES` (variável de ambiente que só limita a verificação rápida aos lotes de 2.000); com `LOTES` ausente o comportamento é idêntico.
