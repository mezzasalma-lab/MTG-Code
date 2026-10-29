# Mothman: o simulador jogava o terreno ANTES do Ruin Crab / Icetill Explorer (correção `LANDFALL_PAYOFF_FIRST`, 2026-10-06)

> **Superado em magnitude (2026-10-07):** os lotes desta pasta usam a **guarda aritmética** do comandante, que era cega a cor e superestimou o efeito (Ruin Crab +21% → +13%; mesa limpa até T8 +0,9 → +0,6 ponto com o ensaio a seco, o padrão atual do simulador). Mesma direção, conclusões qualitativas iguais. Ver `../2026-10-07-guarda-ensaio-a-seco/LEIAME.md`. Para reproduzir estes brutos, `config.json` e `bitident.py` fixam `LANDFALL_GUARD_DRYRUN = false`.


Arquivo da Regra #8 (`CLAUDE.md`). Achado no ensaio da partida manual #1 (`../2026-10-06-partida-manual-1/`): o usuário conjurou Ruin Crab, Mothman e Icetill **e só depois** jogou o terreno (Urza's Saga do cemitério); o simulador chamava `play_land_phase` **antes** de `cast_loop` em todo `main_phase`, então o payoff de landfall nunca estava em campo quando o terreno do turno entrava (**100% das sementes em 4 cenários dirigidos**). É uma convenção de ordem do motor, não um limite da carta (Regra #5): virou correção.
Simulador: `../../mothman_goldfish_v1.py` (commit desta pasta). Código **anterior** fixado em `codigo/mothman_goldfish_v1_ANTES_91b1a3d.py` (idêntico ao commit `91b1a3d`).

## O que mudou no código
- Chave `LANDFALL_PAYOFF_FIRST` (padrão **True**; `False` = ordem antiga, bit-idêntica a `91b1a3d`) e `LANDFALL_PAYOFFS = {Ruin Crab, Icetill Explorer, Evolution Sage}`.
- `main_phase` chama antes `cast_landfall_payoffs_first`: com um terreno ainda por jogar (da mão, ou do cemitério via Icetill), conjura o payoff **se o mana de agora já o paga** (`landfall_payoff_options`: mão ou retrace da Six/Muldrotha). Regras para não mudar o que o jogador conjuraria: o **comandante tem prioridade** (não é deslocado se seria conjurado no turno e o payoff o impediria); o **retrace** só antecipa se sobra outro terreno na mão (o descarte não pode tirar a jogada de terreno).
- Refatorações mecânicas (sem mudar comportamento): `land_play_candidates` (extraído de `play_land_phase`) e `execute_cast` (extraído de `cast_loop`). `landfall_payoff_options` não chama `castable_candidates` porque este incrementa um contador de estatística (`self_mill_blocked_total`); a 1ª versão chamava e a bit-identidade acusou 1 divergência só nesse contador (corrigido).
- Campo novo `payoff_first_casts` (quantas vezes um payoff entrou antes do terreno) e **5 testes dirigidos** novos (`testes/testes_dirigidos.py`, 139/139 passam).

## Validação (Regra #1)
| verificação | resultado | arquivo |
|---|---|---|
| smoke: 99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas por modo (11 variantes) | 0 exceções | `resumos/smoke.txt` |
| testes dirigidos | **139/139** (134 anteriores + 5 novos) | `../../testes/testes_dirigidos.py` |
| bit-identidade, 20.000 partidas × 2 modos | **chave desligada == `91b1a3d` em 40.000 de 40.000**; chave ligada: 28.717 partidas sem disparo, **idênticas**; 11.283 com disparo (as únicas que podem diferir); **0 divergências** | `resumos/bitident_20000.txt` |
| regressão, 20.000 × 4 configurações × 2 modos (`payoff_primeiro`, `pacote5+master+payoff_primeiro`, `guarda_desligada+…`, `orb_sem_limite+…`) | **0 exceções**, 0 carta acima do baralho, 0 campos negativos | `resumos/regressao_20000.txt` |
| determinismo entre processos (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo) | **0 divergências** | `resumos/determinismo.txt` |
| varreduras mecânicas da Regra #10 (entrada de terreno, fetch, terreno não é magia, **landfall em todo ponto de entrada: 7.329 entradas = 7.329 chamadas**, estado por nome) | OK | `resumos/varredura_mecanica.txt` |
| A/B pareado 2.000 (11 variantes) e 10.000 (6 variantes), padrão e resiliência | tabelas abaixo | `resumos/ab_*.txt`, `compacto_*.txt` |

## O que o A/B mediu (N = 10.000 pareado, mesmas sementes; `base` = ordem antiga; * = a diferença excede o IC95%)
| métrica (ligada − desligada) | padrão | resiliência |
|---|---|---|
| partidas em que um payoff entrou antes do terreno (`payoff_first_casts` por partida) | 0,372 | 0,287 |
| gatilhos do **Ruin Crab** por partida (base 1,51 / 1,01) | **+0,319 ± 0,031 *** | +0,221 ± 0,025 * |
| entradas de terreno do cemitério pelo Icetill (base 0,85 / 0,71) | +0,170 ± 0,017 * | +0,122 ± 0,017 * |
| cartas milladas dos oponentes (base 84,18 / 69,44) | **+1,59 ± 0,44 *** | +0,80 ± 0,40 * |
| ... das quais não-terrenos | +1,03 ± 0,27 * | +0,52 ± 0,24 * |
| contadores +1/+1 postos | +0,94 ± 0,57 * | +0,16 ± 0,43 |
| cartas milladas minhas (auto-mill do Icetill) | +0,27 ± 0,09 * | +0,20 ± 0,08 * |
| mesa limpa até T7 / T8 / T10 (pontos) | +0,5 ± 0,3 * / **+0,9 ± 0,4 *** / −0,0 ± 0,3 | +0,4 ± 0,2 * / +0,8 ± 0,3 * / +0,1 ± 0,3 |
| 1º oponente eliminado até T6 (pontos) | +0,5 ± 0,2 * | +0,4 ± 0,2 * |
| **eu perco por deck-out** (`self_lost`, pontos) | **+0,02 ± 0,29** (sem efeito) | +0,02 ± 0,19 (sem efeito) |

**Leitura (medida):** o efeito é **pequeno e na direção esperada**: o Ruin Crab dispara ~21% mais (padrão), o mill de oponente sobe 1,9%, a mesa limpa até T8 ganha ~0,9 ponto, e o risco de deck-out **não se move** (o mill extra do Icetill é compensado pela guarda de biblioteca). As conclusões anteriores **continuam valendo**: pacote de 5 trocas T8 +4,6 → +6,1 e pacote + Master +6,9 → +8,2 (cada um com a chave ligada, ambos contra a base antiga; `compacto_10000.txt`). Com o pacote o ganho da correção é maior (+1,5 ponto em T8, contra +0,9 sem ele) porque a Evolution Sage, que o pacote traz, também é payoff de landfall.
**O que isto NÃO mede:** a política do jogador humano (o humano que lê o Crab na mão faz o mesmo); só 3 payoffs (Ruin Crab, Icetill, Evolution Sage); o Altar of the Brood também dispara com terreno, mas não foi incluído (efeito de 1 mill por terreno).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/raw_ab_2000*.json.xz`, `raw_ab_10000*.json.xz` | bruto por partida (11 variantes × 2.000; 6 × 10.000), padrão e resiliência | usado |
| `resumos/ab_*.txt`, `compacto_*.txt` | tabelas pareadas (todas as métricas; as 15 centrais) | usado (`cmp` conferido) |
| `resumos/smoke.txt`, `regressao_20000.txt`, `bitident_20000.txt`, `determinismo.txt`, `varredura_mecanica.txt` | validação | usado |
| `resumos/audit_landfall_ordem.txt` | varredura da **classe** nos 19 simuladores do repositório (`varredura-2026-10-05/scripts/audit_landfall_ordem.py`) | usado |
| `resumos/ensaio_partida_manual_1_com_fix.txt` | o ensaio dos estados T6-T9 da partida #1 com a chave ligada: **idêntico** ao anterior (nenhum dos 4 estados tem payoff na mão antes do terreno) | apoio |
| `orquestracao/driver_mm.py`, `abgen.py`, `config.json`, `bitident.py`, `verificar_reproducao.sh` | código | apoio |
| `codigo/mothman_goldfish_v1_ANTES_91b1a3d.py` | simulador anterior (para a bit-identidade) | referência |

## A classe, nos outros simuladores (Regra #10; NÃO corrigida aqui; **corrigida em 2026-10-07**, ver `<deck>/resultados-ab/2026-10-07-landfall-payoff-primeiro/`)
`resumos/audit_landfall_ordem.txt`: **1 candidato claro, o Toph** (`main_phase`: `play_land` antes de `cast_loop`, com 16 cartas de landfall no arquivo: Lotus Cobra, Tireless Provisioner, Springheart Nantuko, Felidar Retreat, Scute Swarm, Nissa, Resurgent Animist e outras). O script **não consegue ler** a ordem de Beorn, Maralen, Thranduil e Prismatic Bridge (estrutura de turno diferente; têm payoffs de landfall no arquivo): precisam de leitura à mão. Os demais simuladores não têm payoff de landfall no arquivo. **Falsos positivos possíveis:** carta no arquivo que não está na lista; payoff para o qual a ordem não importa. Nada disso foi corrigido nesta rodada.

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh --tudo` em 2026-10-06: **13 de 13 saídas byte a byte iguais** (`cmp`): as 4 tabelas `ab_*` e as 4 `compacto_*` refeitas só dos `.json.xz`; a bit-identidade rápida (N = 300 × 2 modos); e, **re-simulando** o lote de 2.000 nos dois modos, as 2 tabelas e os 2 brutos (descomprimidos) idênticos aos arquivados.
**Não conferido:** os lotes de 10.000 (só as tabelas a partir do bruto; ~10 min cada para re-simular); a regressão de 20.000 e a bit-identidade de 20.000 (saídas das execuções originais); `log_*` ficam fora do git.

## Efeito nos arquivos anteriores
Os números de `../../goldfish-log.md` §1-§5, `../../candidatas-pos-eoe.md` §0b e das pastas `2026-10-05-*` e `2026-10-06-tergrid-e-ferramenta-mill` foram gerados com a **ordem antiga** (`LANDFALL_PAYOFF_FIRST = False`, bit-idêntico a `91b1a3d`). Os scripts que re-simulam essas pastas (`frequencia_annihilator.py`, `crime_deepmuck.py`, `mill_oponentes.py --fixa LANDFALL_PAYOFF_FIRST=false`) **fixam a chave desligada** para reproduzir os brutos arquivados; o `driver_mm.py` das pastas `2026-10-05-*` carrega o simulador vivo e, por isso, **não reproduz mais os brutos re-simulados** sem `LANDFALL_PAYOFF_FIRST = False` (o `sum` das tabelas, que lê só os brutos, continua igual).
