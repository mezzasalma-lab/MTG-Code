# Esika, God of the Tree // The Prismatic Bridge: payoff de landfall antes do terreno (`LANDFALL_PAYOFF_FIRST`, 2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Pedido do usuário (2026-10-07): *"Corrige os simuladores com erro no script para automatizar a ordem de jogadas para o landfall"*. Classe achada no Mothman em 2026-10-06 (`wise-mothman-sultai/resultados-ab/2026-10-06-landfall-payoff-primeiro/`): o simulador jogava o terreno ANTES de conjurar o payoff de landfall, então o terreno do turno nunca disparava o landfall que o jogador real teria armado. `varredura-2026-10-05/scripts/audit_landfall_ordem.py` listou este deck; a ordem do turno foi lida à mão (abaixo) e o erro confirmado.
Simulador: `../../prismatic_bridge_goldfish_v1.py` (commit desta pasta). Código **anterior** fixado em `codigo/prismatic_bridge_goldfish_v1_ANTES_4df825f.py` (idêntico ao commit `4df825f`).

## Ordem do turno (lida inteira, Regra #6)
`play_turn`: janelas de flash/remoção do fim da rodada → upkeep da Bridge → compra → `play_land` → `main_phase` (passada de lealdade, protetores, Bridge, reserva de flash/resposta, loop por custo crescente) → combate → fim (relida inteira, Regra #6).
Gancho novo: `play_turn` chama `cast_landfall_payoffs_first(state, log)` logo antes de `play_land`.

## O que mudou no código
- Chave `LANDFALL_PAYOFF_FIRST` (padrão **True**; `False` = ordem antiga, **bit-idêntica** ao commit `4df825f`) e `LANDFALL_PAYOFFS` = as cartas com gatilho de landfall que o arquivo trata:

| payoff | cláusula de landfall (oráculo do cache) |
|---|---|
| `Evolution Sage` | Landfall — proliferate (+1 de lealdade em cada planeswalker, +1 em contadores de criatura) |

- `cast_landfall_payoffs_first`: com um terreno ainda por jogar, conjura antes os payoffs que o mana de **agora** já paga, na ordem do próprio loop de conjuração do deck. **Guarda por ensaio a seco** (`_hoist_loses_a_play`): cópia profunda do estado, roda o resto da fase pré-combate na ordem ANTIGA e na NOVA, e só deixa o payoff passar se nada que a ordem antiga conjuraria/jogaria (comandante, rochas de mana, qualquer jogada de prioridade maior) deixar de acontecer na nova. A 1ª versão usava a fórmula `custo do comandante <= mana de agora + 1` e **estava errada** (não conta cor, mana de landfall já em campo, land drop extra).
- **Refatoração sem mudar nada** (necessária para usar o MESMO caminho de cast): o corpo do loop genérico de `main_phase` virou `_cast_hand_spell(state, choice, log)` e o cálculo da reserva de mana virou `_main_phase_reserved(state)`. Prova: bit-identidade 20.000 × 2 modos com a chave desligada.
- A Evolution Sage respeita as mesmas travas do loop (`can_cast`, orçamento = mana − reserva, remoção segurada, resposta segurada); a Bridge (comandante) é protegida por ensaio a seco (`_hoist_loses_a_play`).
- **Efeito pequeno por construção:** a Evolution Sage é 1 carta de 99 e só tem alvo (lealdade) se já houver planeswalker em campo.
- Campo novo `payoff_first_casts` (quantas vezes um payoff entrou antes do terreno) e testes dirigidos em `../../test_prismatic_bridge_goldfish.py`: **142/142 (137 anteriores + 5 novos)** passam.

## Validação (Regra #1 / #10)
| verificação | resultado | arquivo |
|---|---|---|
| smoke: 99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos (vivo e snapshot) | 0 exceções | `resumos/smoke.txt` |
| testes dirigidos | **142/142 (137 anteriores + 5 novos)** | `../../test_prismatic_bridge_goldfish.py` |
| bit-identidade, 20.000 partidas × 2 modos (chave desligada == snapshot; campo novo ignorado) | **0 divergências** | `resumos/bitident_20000.txt` |
| regressão, 20.000 × 2 modos × 2 configurações (ligada, desligada) | **0 exceções**; ver nota | `resumos/regressao_20000.txt` |
| determinismo entre processos (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo) | **0 divergências** | `resumos/determinismo.txt` |
| A/B pareado 2.000 e 10.000 (padrão e resiliência) | tabela abaixo | `resumos/ab_*.txt` |

Saídas literais:
```
    DEPOIS (arquivo vivo): cartas na biblioteca=99 | distintas=99 | desconhecidas (fora do CARD_DB)=[] | duplicadas nao-basicas=[]
    200 partidas modo padrao: excecoes=0
    200 partidas modo resiliencia: excecoes=0
    ANTES (snapshot): cartas na biblioteca=99 | distintas=99 | desconhecidas (fora do CARD_DB)=[] | duplicadas nao-basicas=[]
    200 partidas modo padrao: excecoes=0
    200 partidas modo resiliencia: excecoes=0
    chaves da correcao no arquivo vivo: LANDFALL_PAYOFF_FIRST=True
    padrao: N=20000 partidas diferentes=0 -> BIT-IDENTICO
    resiliencia: N=20000 partidas diferentes=0 -> BIT-IDENTICO
    depois (repositorio)   padrao       partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    depois (repositorio)   resiliencia  partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    chave_desligada        padrao       partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    chave_desligada        resiliencia  partidas ok=20000 | excecoes=0  | carta acima do baralho=0 | campos negativos={}
    prismatic-bridge-wurbg     padrao       N=1500 sementes divergentes entre 3 hash seeds: 0 [] campos: []
    prismatic-bridge-wurbg     resiliencia  N=1500 sementes divergentes entre 3 hash seeds: 0 [] campos: []
```
O 1º lote falhou com `OverflowError: int too large to convert to float` (o `abgen.py` do modelo não limitava inteiros astronômicos como `all_will_be_one_face_damage_total`); a pasta passou a usar o `driver.py`/`abgen.py` corrigidos da pasta `2026-10-05-terreno-virado-primeiro` do mesmo deck e o lote foi refeito do zero.

## O que o A/B mediu (N = 10.000 pareado, mesmas sementes; `base` = ordem antiga; `*` = a diferença excede o IC95%)
Frequência do conserto: padrao: payoff_first_casts por partida = 0.070 | partidas com >= 1 = 7.0% (N=10000) | resiliencia: payoff_first_casts por partida = 0.068 | partidas com >= 1 = 6.8% (N=10000).

| campo (N=10.000 pareado) | padrao: base -> depois (dif ± IC95%) | resiliencia: base -> depois (dif ± IC95%) |
|---|---|---|
| `evolution_sage_proliferates` | 1.155 -> 1.245 (+0.090 ± 0.018) * | 0.738 -> 0.833 (+0.095 ± 0.019) * |
| `lands_played_total` | 6.240 -> 6.240 (+0.001 ± 0.002) | 6.145 -> 6.147 (+0.002 ± 0.002) |
| `pw_activations_total` | 10.770 -> 10.877 (+0.108 ± 0.056) * | 9.240 -> 9.409 (+0.169 ± 0.060) * |
| `pw_ultimates_used_total` | 2.382 -> 2.403 (+0.021 ± 0.024) | 1.549 -> 1.609 (+0.060 ± 0.026) * |
| `pw_draws_total` | 7.320 -> 7.373 (+0.052 ± 0.064) | 5.880 -> 6.033 (+0.153 ± 0.070) * |
| `first_ult_turn__nunca` | 0.631 -> 0.629 (-0.002 ± 0.001) * | 0.764 -> 0.761 (-0.003 ± 0.002) * |
| `first_ult_turn__ate_T6` | 0.056 -> 0.060 (+0.004 ± 0.001) * | 0.036 -> 0.037 (+0.002 ± 0.001) * |
| `bridge_first_cast_turn__ate_T4` | 0.351 -> 0.351 (+0.000 ± 0.000) | 0.337 -> 0.337 (+0.000 ± 0.000) |
| `bridge_first_cast_turn__ate_T5` | 0.691 -> 0.690 (-0.001 ± 0.001) * | 0.650 -> 0.650 (+0.000 ± 0.001) |
| `bridge_first_cast_turn__nunca` | 0.109 -> 0.110 (+0.000 ± 0.000) | 0.147 -> 0.146 (-0.000 ± 0.001) |
| partidas com resultado idêntico ao da base | 93.0% | 93.2% |

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_2000*.json.xz`, `raw_ab_10000*.json.xz` | bruto por partida (antes × depois), padrão e resiliência | usado |
| `resumos/ab_*.txt`, `resumos/ab_resumo.md` | tabelas pareadas completas / as linhas desta página | usado (`cmp` conferido) |
| `resumos/smoke.txt`, `bitident_20000.txt`, `regressao_20000.txt`, `determinismo.txt`, `frequencia_hoist.txt` | validação | usado |
| `orquestracao/driver.py`, `abgen.py`, `config.json`, `verificar_reproducao.sh` | harness genérico (`config.json` = variantes e campos de destaque) | apoio |
| `codigo/*_ANTES_4df825f.py` | simulador anterior (para a bit-identidade) | referência |

## Não coberto (Regra #7)
Magia que põe terreno em campo (Cultivate, Farseek, Three Visits...) conjurada antes de um payoff que o mana também pagaria depois do terreno; terreno que volta ao campo (blink, Lander); só a 1ª fase principal; a política de um jogador humano que prefere guardar o terreno por informação. **Classes do motor NÃO varridas aqui:** as demais da Regra #10 (esta rodada só mexeu na ordem terreno × payoff).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh --tudo` em 2026-10-07: **11 de 11 saídas byte a byte iguais** (`cmp`): as 4 tabelas `ab_*` refeitas só dos `.json.xz`; e, **re-simulando** o lote de 2.000 nos dois modos, o smoke, as 2 tabelas e os 2 brutos (descomprimidos) idênticos aos arquivados, a bit-identidade (N = 2.000 × 2 modos, chave desligada == snapshot) e a regressão (N = 2.000 × 4 configurações, 0 exceções). Saída em `resumos/verificacao_reproducao.txt`.
**Não conferido por re-execução:** os lotes de 10.000 (só as tabelas a partir do bruto), a bit-identidade e a regressão de 20.000 (saídas das execuções originais), o determinismo entre processos (`resumos/determinismo.txt`, `varredura-2026-10-05/scripts/det_check.sh`) e a extração de `frequencia_hoist.txt`/`ab_resumo.md` (scripts `varredura-2026-10-05/scripts/hoist_stats.py` e `resume_ab_landfall.py`, refeitos dos brutos). **Nota do harness:** os lotes de bit-identidade/A/B/regressão foram gerados com o `driver.py` antes do suporte a `LOTES` (variável de ambiente que só limita a verificação rápida aos lotes de 2.000); com `LOTES` ausente o comportamento é idêntico.
