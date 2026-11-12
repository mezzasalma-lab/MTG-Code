# Maralen, Fae Ascendant: payoff de landfall antes do terreno (`LANDFALL_PAYOFF_FIRST`, 2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Pedido do usuário (2026-10-07): *"Corrige os simuladores com erro no script para automatizar a ordem de jogadas para o landfall"*. Classe achada no Mothman em 2026-10-06 (`wise-mothman-sultai/resultados-ab/2026-10-06-landfall-payoff-primeiro/`): o simulador jogava o terreno ANTES de conjurar o payoff de landfall, então o terreno do turno nunca disparava o landfall que o jogador real teria armado. `varredura-2026-10-05/scripts/audit_landfall_ordem.py` listou este deck; a ordem do turno foi lida à mão (abaixo) e o erro confirmado.
Simulador: `../../maralen_goldfish_v1.py` (commit desta pasta). Código **anterior** fixado em `codigo/maralen_goldfish_v1_ANTES_aaf2c2b.py` (idêntico ao commit `aaf2c2b`).

## Ordem do turno (lida inteira, Regra #6)
`play_turn`: upkeep → compra → `play_land` → `main_phase(is_first_main=True)` (comandante, depois o loop por mana) → combate → `main_phase(False)` → fim (relida inteira, Regra #6).
Gancho novo: `play_turn` chama `cast_landfall_payoffs_first(state)` logo antes de `play_land`; depois de cada cast repete a sequência do loop de `main_phase` (Maralen grátis, Umbral Mantle, dorks).

## O que mudou no código
- Chave `LANDFALL_PAYOFF_FIRST` (padrão **True**; `False` = ordem antiga, **bit-idêntica** ao commit `aaf2c2b`) e `LANDFALL_PAYOFFS` = as cartas com gatilho de landfall que o arquivo trata:

| payoff | cláusula de landfall (oráculo do cache) |
|---|---|
| `Thranduil's Company` | As long as you control another Elf, you may play an additional land on each of your turns; Landfall — dois +1/+1 counters (modelado só em Marwyn: único alvo com efeito numérico) |
| `Thranduil, Sindarin Liege // Silvan Rally` | Landfall — Elfo 1/1 |

- `cast_landfall_payoffs_first`: com um terreno ainda por jogar, conjura antes os payoffs que o mana de **agora** já paga, na ordem do próprio loop de conjuração do deck. **Guarda por ensaio a seco** (`_hoist_loses_a_play`): cópia profunda do estado, roda o resto da fase pré-combate na ordem ANTIGA e na NOVA, e só deixa o payoff passar se nada que a ordem antiga conjuraria/jogaria (comandante, rochas de mana, qualquer jogada de prioridade maior) deixar de acontecer na nova. A 1ª versão usava a fórmula `custo do comandante <= mana de agora + 1` e **estava errada** (não conta cor, mana de landfall já em campo, land drop extra).
- Guarda por ensaio a seco (`_hoist_loses_a_play`); mesma conclusão da Company do Thranduil: o 2º land drop só é usado se a Company entrar antes.
- `can_cast(state, COMMANDER)` deste arquivo ignora o imposto do comandante (o custo cobrado em `main_phase` inclui `2 × commander_cast_count`): comportamento anterior, não alterado aqui.
- Campo novo `payoff_first_casts` (quantas vezes um payoff entrou antes do terreno) e testes dirigidos em `../../test_maralen_goldfish.py`: **6/6** passam.

## Validação (Regra #1 / #10)
| verificação | resultado | arquivo |
|---|---|---|
| smoke: 99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos (vivo e snapshot) | 0 exceções | `resumos/smoke.txt` |
| testes dirigidos | **6/6** | `../../test_maralen_goldfish.py` |
| bit-identidade, 20.000 partidas × 2 modos (chave desligada == snapshot; campo novo ignorado) | **0 divergências** | `resumos/bitident_20000.txt` |
| regressão, 20.000 × 2 modos × 2 configurações (ligada, desligada) | **0 exceções**; ver nota | `resumos/regressao_20000.txt` |
| determinismo entre processos (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo) | **0 divergências** | `resumos/determinismo.txt` |
| A/B pareado 2.000 e 10.000 (padrão e resiliência) | tabela abaixo | `resumos/ab_*.txt` |

Saídas literais:
```
    DEPOIS (arquivo vivo): cartas na biblioteca=99 | distintas=94 | desconhecidas (fora do CARD_DB)=[] | duplicadas nao-basicas=[]
    200 partidas modo padrao: excecoes=0
    200 partidas modo resiliencia: excecoes=0
    ANTES (snapshot): cartas na biblioteca=99 | distintas=94 | desconhecidas (fora do CARD_DB)=[] | duplicadas nao-basicas=[]
    200 partidas modo padrao: excecoes=0
    200 partidas modo resiliencia: excecoes=0
    chaves da correcao no arquivo vivo: LANDFALL_PAYOFF_FIRST=True
    padrao: N=20000 partidas diferentes=0 -> BIT-IDENTICO
    resiliencia: N=20000 partidas diferentes=0 -> BIT-IDENTICO
    depois (repositorio)   padrao       partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    depois (repositorio)   resiliencia  partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    chave_desligada        padrao       partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    chave_desligada        resiliencia  partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    maralen-sultai             padrao       N=1500 sementes divergentes entre 3 hash seeds: 0 [] campos: []
    maralen-sultai             resiliencia  N=1500 sementes divergentes entre 3 hash seeds: 0 [] campos: []
```
O smoke da 1ª rodada saiu com a biblioteca contada pelo `driver.py` do modelo; refeito com o `driver.py` corrigido (99 cartas, 94 distintas, 0 desconhecidas).

## O que o A/B mediu (N = 10.000 pareado, mesmas sementes; `base` = ordem antiga; `*` = a diferença excede o IC95%)
Frequência do conserto: padrao: payoff_first_casts por partida = 0.172 | partidas com >= 1 = 16.1% (N=10000) | resiliencia: payoff_first_casts por partida = 0.122 | partidas com >= 1 = 11.7% (N=10000).

| campo (N=10.000 pareado) | padrao: base -> depois (dif ± IC95%) | resiliencia: base -> depois (dif ± IC95%) |
|---|---|---|
| `lands_played_total` | 6.154 -> 6.169 (+0.016 ± 0.007) * | 5.822 -> 5.834 (+0.012 ± 0.005) * |
| `landfall_elf_tokens_total` | 0.250 -> 0.356 (+0.106 ± 0.009) * | 0.090 -> 0.166 (+0.076 ± 0.007) * |
| `landfall_counters_total` | 0.329 -> 0.450 (+0.121 ± 0.010) * | 0.126 -> 0.212 (+0.086 ± 0.008) * |
| `tokens_created_total` | 1002.887 -> 1030.995 (+28.108 ± 42.218) | 254.725 -> 258.801 (+4.076 ± 17.087) |
| `ramp_pieces_cast_total` | 5.005 -> 5.010 (+0.005 ± 0.017) | 3.725 -> 3.730 (+0.005 ± 0.011) |
| `commander_cast_turn__ate_T3` | - | 0.140 -> 0.140 (-0.000 ± 0.000) |
| `commander_cast_turn__ate_T4` | 0.494 -> 0.494 (+0.000 ± 0.000) | 0.418 -> 0.418 (+0.000 ± 0.001) |
| `commander_cast_turn__ate_T5` | - | 0.758 -> 0.758 (-0.000 ± 0.001) |
| `infinite_combo_turn__nunca` | 0.840 -> 0.840 (+0.000 ± 0.002) | 0.943 -> 0.943 (-0.000 ± 0.002) |
| `infinite_combo_turn__ate_T6` | 0.049 -> 0.049 (+0.000 ± 0.001) | 0.023 -> 0.024 (+0.001 ± 0.001) * |
| `staff_infinite_draws` | 2.112 -> 2.123 (+0.011 ± 0.070) | 0.575 -> 0.596 (+0.022 ± 0.045) |
| partidas com resultado idêntico ao da base | 83.8% | 88.3% |

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_2000*.json.xz`, `raw_ab_10000*.json.xz` | bruto por partida (antes × depois), padrão e resiliência | usado |
| `resumos/ab_*.txt`, `resumos/ab_resumo.md` | tabelas pareadas completas / as linhas desta página | usado (`cmp` conferido) |
| `resumos/smoke.txt`, `bitident_20000.txt`, `regressao_20000.txt`, `determinismo.txt`, `frequencia_hoist.txt` | validação | usado |
| `orquestracao/driver.py`, `abgen.py`, `config.json`, `verificar_reproducao.sh` | harness genérico (`config.json` = variantes e campos de destaque) | apoio |
| `codigo/*_ANTES_aaf2c2b.py` | simulador anterior (para a bit-identidade) | referência |

## Não coberto (Regra #7)
Magia que põe terreno em campo (Cultivate, Farseek, Three Visits...) conjurada antes de um payoff que o mana também pagaria depois do terreno; terreno que volta ao campo (blink, Lander); só a 1ª fase principal; a política de um jogador humano que prefere guardar o terreno por informação. **Classes do motor NÃO varridas aqui:** as demais da Regra #10 (esta rodada só mexeu na ordem terreno × payoff).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh --tudo` em 2026-10-07: **11 de 11 saídas byte a byte iguais** (`cmp`): as 4 tabelas `ab_*` refeitas só dos `.json.xz`; e, **re-simulando** o lote de 2.000 nos dois modos, o smoke, as 2 tabelas e os 2 brutos (descomprimidos) idênticos aos arquivados, a bit-identidade (N = 2.000 × 2 modos, chave desligada == snapshot) e a regressão (N = 2.000 × 4 configurações, 0 exceções). Saída em `resumos/verificacao_reproducao.txt`.
**Não conferido por re-execução:** os lotes de 10.000 (só as tabelas a partir do bruto), a bit-identidade e a regressão de 20.000 (saídas das execuções originais), o determinismo entre processos (`resumos/determinismo.txt`, `varredura-2026-10-05/scripts/det_check.sh`) e a extração de `frequencia_hoist.txt`/`ab_resumo.md` (scripts `varredura-2026-10-05/scripts/hoist_stats.py` e `resume_ab_landfall.py`, refeitos dos brutos). **Nota do harness:** os lotes de bit-identidade/A/B/regressão foram gerados com o `driver.py` antes do suporte a `LOTES` (variável de ambiente que só limita a verificação rápida aos lotes de 2.000); com `LOTES` ausente o comportamento é idêntico.
