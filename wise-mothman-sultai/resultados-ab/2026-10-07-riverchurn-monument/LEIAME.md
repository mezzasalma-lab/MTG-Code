# Mothman: Riverchurn Monument (2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Pergunta do usuário: *"Avalie a inclusão de Riverchurn Monument no deck do Mothman, e elenque 5 possíveis trocas em ordem de prioridade (do menos importante para o gameplan para o mais importante)"*.

## Resposta curta (o que foi MEDIDO)
1. **Oráculo ao vivo** (Scryfall, `flavor_name` checado: nenhum, as 5 impressões se chamam `Riverchurn Monument`): `{1}{U}` artefato. `{1},{T}`: *any number of target players each mill two cards*. **Exhaust** `{2}{U}{U},{T}`: *any number of target players each mill cards equal to the number of cards in their graveyard* (uma vez por objeto). Rulings (2025-02-07): exhaust a qualquer momento em que se pode ativar habilidade; sair e voltar = objeto novo (Exhaust de novo); gatilho de "ativar exhaust" resolve antes (a lista não tem nenhum: `resumos/confere_gatilho_de_ativar.txt`).
2. **Spellbook** (`resumos/resumo_spellbook.md`): 91 nomes reconhecidos, controle positivo e de corte passaram. O Monument **não cria combo novo** (base: Ascension + Mindcrank, Altar of Dementia + Great Henge); 8 combos de 2 peças "quase" (Maddening Cacophony, Jidoor, Traumatize, Singularity Rupture, Cut Your Losses, Terisian Mindbreaker, Fleet Swallower, Kitsune's Technique: **nenhuma na lista**). Só as 5 peças desses 2 combos, quando cortadas, derrubam combo (não são candidatas).
3. **Efeito (A/B pareado, N = 10.000, `no lugar`, Monument ← Negate):** mesa inteira limpa até T8 **+1,03 ± 0,28 ponto** no padrão (51,4% → 52,4%) e **+0,36 ± 0,24** na resiliência (24,0% → 24,4%). **Todo o ganho vem das ativadas**: com a chave `RIVERCHURN_ACTIVATE = False` (só o corpo de artefato) o ganho é +0,02 ± 0,21. A carta aparece em campo em **18,7%** das partidas (12 turnos); ativa o tap 1,73× e o Exhaust 0,17× por partida em que entra. **Quando entra até T4 (5,4% das partidas): +10,5 ± 3,3 pontos de mesa limpa até T8** (`resumos/condicional.txt`).
4. **Cortes (medido, N = 10.000):** nos 20 finalistas, o Monument nunca é pior que a carta cortada além do ruído; os 5 mais baratos pelo simulador e pelo papel real estão em `resumos/rank_final.txt` e na resposta do `goldfish-log.md` §11. Em 84 cortes testados (`resumos/rank_triagem_no_lugar.txt`), os piores são peças de motor (Altar of the Brood −3,5 pontos, Kami −3,4, Command Tower, Breeding Pool, Ruin Crab −2,4…).

**NÃO verificado (Regra #7):** criaturas de oponente (Generous Patron + Mothman mirando criatura de oponente; Cauldron exilando criaturas do cemitério dele), decks de oponente que recorrem ao próprio cemitério, prioridade de conjuração do Monument (fixa em 57), a ordem humana real das ativações além de 3 políticas, o pacote de 5 trocas aplicado **junto** (medido só com o Monument por cima, `resumos/rank_pacote.txt`), a pergunta aberta do Zellix (gatilho por jogador × por evento, sem ruling achada), e o Saga/Urza (lista de artefatos buscáveis é a convenção já auditada).

## Como foi gerado
- **Simulador:** `../../mothman_goldfish_v1.py`, com o Monument implementado (`act_riverchurn_tap`, `act_riverchurn_exhaust`, `riverchurn_opp_end_step`, chaves `RIVERCHURN_*`, `SWAP_IN_PLACE`; testes dirigidos **157/157**, 16 novos). Só entra na biblioteca por `SWAPS`.
- **`SWAP_IN_PLACE` (novo, padrão `False`):** a carta que entra ocupa o **lugar** da que sai antes do embaralhamento. Com `remove+append` (convenção de todos os A/B anteriores) **0 de 300** partidas ficam idênticas entre a variante e a base; no lugar, **236 de 300 (79%)** têm as métricas-chave idênticas e o IC95% cai cerca de 5× (±0,030 → ±0,006 em T8 com N = 2.000). A triagem 1 (`remove+append`) fica **SUPERADA** e marcada; a 2 (no lugar) é a usada.
- **Harness:** `orquestracao/driver_mm.py` + `abgen.py` (cópias dos de `../2026-10-07-guarda-ensaio-a-seco/`, `TAG` novo para vários lotes na mesma pasta); `PYTHONHASHSEED=0` fixado; sementes `1.000.000+i` (N = 2.000) e `3.000.000+i` (N = 10.000); 12 turnos; modos padrão e resiliência. `gera_config.py` / `gera_config_final.py` geram os configs (`config_*.json`), `lanca_*.sh` são os lançadores.
- **Estado do código por lote:** triagem 1 = `codigo/mothman_goldfish_v1_TRIAGEM_sem_commit.py` (Monument, sem `SWAP_IN_PLACE`); triagem 2 = o mesmo + `SWAP_IN_PLACE` e os contadores novos (**sem** a janela `RIVERCHURN_OPP_END_STEP`, sem snapshot próprio: o arquivo vivo com chaves padrão reproduz byte a byte, ver `--tudo` abaixo); final, pacote, regressão, bit-identidade e determinismo = arquivo vivo no commit desta pasta. Código anterior: `codigo/mothman_goldfish_v1_ANTES_cd5d453.py`.

## Mapa arquivo → o que é → status
| arquivo(s) em `dados/` | o que é | status | tabela que o usa |
|---|---|---|---|
| `riverchurn_scryfall.json` | oráculo bruto + rulings + impressões do Monument (lido ao vivo em 2026-10-07) | usado | — |
| `spellbook_cru.json.xz`, `spellbook_monument.json`, `spellbook_monument_quase.json` | respostas CRUAS do `find-my-combos` (base, base+Monument, controle positivo, controle de corte) e resumos por corte (87 cortes) | usado | `resumos/resumo_spellbook.md` |
| `raw_triagem_{1..6}_2000[_resiliencia].json.xz` | 84 cortes `Monument ← X`, N = 2.000, **`remove+append`** (6 lotes de 14 + base) | **SUPERADO** (pareamento fraco, IC ±0,03) | `resumos/rank_triagem_remove_append_SUPERADA.txt` |
| `raw_triagemip_{1..6}_2000[_resiliencia].json.xz` | os mesmos 84 cortes, **no lugar** | usado (escolheu os 20 finalistas) | `resumos/rank_triagem_no_lugar.txt` |
| `raw_final_{1..4}_10000[_resiliencia].json.xz` | 20 finalistas + 8 sensibilidades do Monument (plataforma: ← Negate), N = 10.000, no lugar | usado | `resumos/rank_final.txt`, `condicional.txt` |
| `raw_pacote_10000[_resiliencia].json.xz` | Monument ← X **sobre** o pacote de 5 trocas + Master ← Negate (pendente), N = 10.000 | usado | `resumos/rank_pacote.txt` |
| `*.done` | sinais de fim dos lançadores | apoio | — |

Formato dos brutos: `colunas-v1` (`{variante: {n, fp, campos: {campo: [valor por partida]}}}`), TODOS os campos numéricos do estado final; `python3 indice_dados.py > resumos/indice_dados.md` lista variantes e campos de cada arquivo.

## Validação
| verificação | resultado | arquivo |
|---|---|---|
| testes dirigidos (`../../testes/testes_dirigidos.py`) | **157/157** (cada um confere que o número esperado é > 0) | — |
| smoke das 29 variantes finais (99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos) | 0 exceções | `resumos/smoke_final.txt` |
| regressão 20.000 × 2 modos × 3 variantes (`Monument ← Negate` no lugar com chaves padrão; com TODAS as chaves ligadas; `remove+append` com `← Yavimaya Hollow`) | 0 exceções, 0 carta acima do baralho, 0 campo negativo | `resumos/regressao_validacao_20000.txt` |
| bit-identidade, `SWAPS=()`: simulador novo == `ANTES_cd5d453`, campo a campo, 20.000 sementes × 2 modos × 2 conjuntos de chaves | **80.000 de 80.000 idênticas**, 0 divergências | `resumos/bitident_20000.txt` |
| bit-identidade, Monument no baralho: partida em que ele NUNCA entra em campo é idêntica com `RIVERCHURN_ACTIVATE` ligado/desligado | 32.444 partidas idênticas, 0 divergências (7.556 em que ele entra, podem diferir) | idem |
| determinismo entre processos (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, Monument no baralho, chaves padrão e todas ligadas) | **0 divergências** | `resumos/determinismo.txt` |
| tabelas refeitas só dos `.json.xz` e `cmp` | **77 de 77** saídas byte a byte iguais | `resumos/verificacao_reproducao.txt` |

## Reprodução (comandos)
- Triagem 2: `LOTES=2000 TAG=triagemip_K python3 orquestracao/driver_mm.py orquestracao/config_triagem_ip_K.json ab` (K = 1..6, ou `bash orquestracao/lanca_triagem_ip.sh`); ranking: `python3 orquestracao/rank_triagem.py 2000 triagemip`.
- Final: `bash orquestracao/lanca_final.sh`; `python3 orquestracao/rank_final.py`; `python3 orquestracao/condicional.py`.
- Pacote: `bash orquestracao/lanca_pacote.sh`; `python3 orquestracao/rank_pacote.py`.
- Spellbook: `python3 orquestracao/csb_monument.py ../../lista.md dados/spellbook_monument.json 3`; `python3 orquestracao/resumo_spellbook.py`.
- Motores/condições por script: `python3 orquestracao/enumera_condicoes.py`, `orquestracao/motores_com_monument.py`.
- Bit-identidade: `bash orquestracao/lanca_bitident.sh` (4 fatias de 5.000); validação: `bash orquestracao/lanca_validacao.sh`.
- Verificação: `bash orquestracao/verificar_reproducao.sh [--tudo]` (**não edite o simulador enquanto roda**).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
- **`bash orquestracao/verificar_reproducao.sh` (2026-10-07): 77 de 77 saídas byte a byte iguais (`cmp`)**: as tabelas A/B e compactas de todos os lotes (triagem 1 e 2: 6 lotes × 2 modos cada; final: 4 × 2; pacote), os rankings (`rank_triagem_*`, `rank_final`, `rank_pacote`), `condicional`, `tabela_final.md`, `resumo_spellbook.md`, `motores_por_script.txt` e `confere_gatilho_de_ativar.txt`, refeitos só dos `.json.xz`.
- **`--tudo` (1ª rodada, `resumos/verificacao_reproducao_tudo_1a_rodada.txt`): 79 de 80**; a única divergência foi um defeito do próprio script de verificação (`motores_com_monument.py` gravava direto em `resumos/` em vez de na pasta temporária, então o `cmp` comparava com arquivo inexistente); corrigido e refeito (a linha passou a IGUAL na 2ª rodada). Nessa 1ª rodada, **re-simulando** o lote 1 da triagem `no lugar` (N = 2.000, 15 variantes × 2 modos) com o arquivo VIVO: as 2 tabelas e os 2 brutos descomprimidos saíram **idênticos** aos arquivados (e esse lote foi gerado antes de eu acrescentar a janela `RIVERCHURN_OPP_END_STEP`: confirma que o código final com as chaves padrão não mudou nada).
- **NÃO re-executados na verificação:** a triagem 1 e 2–6, o lote final de 10.000, o pacote, a regressão de 20.000, a bit-identidade de 20.000 e o determinismo (saídas das execuções originais; a bit-identidade foi feita em 4 fatias paralelas de 5.000 sementes).
