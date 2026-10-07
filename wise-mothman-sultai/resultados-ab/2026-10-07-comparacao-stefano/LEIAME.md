# Mothman: comparação com a lista do Stefano + Agent Frank Horrigan e The Master, Transcendent (2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Pedido do usuário: *"compare nosso deck com esse aqui, feito pelo Stefano (sem atualização há mais de um ano)… Tenho Agent Frank Horrigan e me parece uma boa adição ao deck, assim como The Master, Transcendent!"* O documento da comparação é `resumos/comparacao.md`; as tabelas de decisão estão em `../../goldfish-log.md` §14 e a tabela de cláusulas em `../../checklist-oraculo.md` §13.

## Resposta curta (MEDIDO, N = 10.000 por variante e modo, pareado, `no lugar`, sementes 3.000.000+i, 12 turnos)
1. **Os dois baralhos dividem 22 cartas + o comandante** (resolvidas por set + nº de colecionador, 93 de 93, nenhum `flavor_name`). Ele: rad + proliferate + controle (14 cartas de rad, 10 de proliferate, 3 dobradores, 7 remoções, 8 pedras, 16 criaturas, 0 combos); nós: mill + contadores + recursão + combos (32 criaturas, 2 combos). Os amplificadores "+1" são 3 nossos (Scales, Kami, Constrictor) contra 2 dele; a diferença são os 3 **dobradores**.
2. **Agent Frank Horrigan:** mesa limpa até T8 **+2,37 ± 0,37 \*** (← Offer), +2,25 (← Negate), +2,27 (← Didn't Say Please), +2,07 (← Wave Goodbye), +1,48 (← Selkie); resiliência +0,6 a +1,1. ← Kozilek +0,87, mas deck-out **+1,68 \***. **Sem o proliferate (só o corpo 8/6) o ganho some: +0,15 ± 0,31.** Entrando até T6 (3,3% das partidas): +17 a +26 pontos de T8.
3. **The Master, Transcendent: neutra** (← Negate +0,36 ± 0,33; ← Offer +0,26; ← Tear Asunder −0,25). Piso: a criatura de oponente é um 3/3 genérico sem as habilidades da carta real.
4. **Spellbook** (157 nomes reconhecidos, controles ok): nenhuma das duas cria combo; a lista do Stefano tem 0 combos e 15 "quase".

**NÃO verificado (Regra #7):** o valor real da criatura de oponente que a Master leva (habilidades); Horrigan junto com Monument/Jace (mesmas vagas); prioridades de conjuração (Horrigan 71, Master 67); o Alchemist exilando a criatura milada antes de a Master agir; a mesa de oponentes é passiva; todas as outras cartas dele (as seis mais promissoras estão em `../2026-10-07-candidatas-stefano-2/`).

## Como foi gerado
- **Simulador:** `codigo/mothman_goldfish_v1_HM.py` (idêntico ao `../../mothman_goldfish_v1.py` deste commit): `patch_hm.py`, `patch_hm2.py` e `patch_hm3.py` aplicados ao `codigo/mothman_goldfish_v1_ANTES_1b9a865.py` (Jace incluso). Triagem N = 2.000: `codigo/mothman_goldfish_v1_HM_triagem.py` (antes de renomear `master_act_on_opp_turn` → `master_act_on_opp_phase` e de acrescentar a chave `HORRIGAN_PROLIF_TIMES`; o comportamento padrão é o mesmo). 182 testes dirigidos (16 novos).
- **Harness:** `orquestracao/driver_mm.py` + `abgen.py` (cópias dos da pasta do Jace), `PYTHONHASHSEED=0`; configs em `config_triagem.json` (21 cortes × 2 cartas + base), `config_final.json` (19 variantes), `config_reg.json`. A triagem e o final rodaram sobre o arquivo CONGELADO de `codigo/`; a validação, sobre o arquivo vivo.
- **Lista do Stefano:** `dados/lista_stefano_original.txt` (como recebida), `resolve_stefano.py` → `dados/lista_stefano_resolvida.json`; diff por nome real em `diff_listas.py`.

## Mapa arquivo → o que é → status
| arquivo | o que é | status | usado em |
|---|---|---|---|
| `dados/lista_stefano_original.txt`, `lista_stefano_resolvida.json`, `diff_listas.json`, `game_changers.json` | a lista, a resolução por set+número, o diff e os Game Changers/legalidade | usado | `resumos/comparacao.md` |
| `dados/rulings_candidatas.json` | oráculo + rulings do Horrigan e da Master (Scryfall, 2026-10-07) | usado | `checklist-oraculo.md` §13 |
| `dados/spellbook_stefano_frank_master.json` | `find-my-combos`: nossa lista, a do Stefano, + Horrigan/Master, 174 cortes, controles | usado | `resumos/resumo_spellbook.md` |
| `dados/raw_triagem_2000[_resiliencia].json.xz` | triagem N = 2.000, 43 variantes | usado (escolheu os cortes) | `resumos/rank_triagem.txt` |
| `dados/raw_final_10000[_resiliencia].json.xz` | final N = 10.000, 19 variantes | usado | `resumos/tabela_final.md`, `condicional.txt` |
| `resumos/comparacao*.md` | o documento da comparação (partes 1 a 3) | usado | — |
| `resumos/bitident_*.txt`, `log_regressao.txt` / `regressao_validacao_20000.txt`, `determinismo.txt` | validação do código | validação | — |
| `orquestracao/` | harness, patches, testes novos (`novos_testes.py`), `bitident_hm.py`, scripts de tabela, `verificar_reproducao.sh` | apoio | — |

Formato dos brutos: `colunas-v1`; `python3 indice_dados.py > resumos/indice_dados.md` lista variantes e campos.

## Validação do código
| verificação | resultado | arquivo |
|---|---|---|
| testes dirigidos (`../../testes/testes_dirigidos.py`) | **182/182** | — |
| smoke das 19 variantes (99 cartas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos) | 0 exceções | `resumos/smoke_final.txt` |
| bit-identidade, `SWAPS=()`: simulador novo == `ANTES_1b9a865`, campo a campo (campos `jace_`, `horrigan_`, `master_` ignorados), 20.000 × 2 modos × 2 conjuntos de chaves | **80.000 de 80.000**, 0 divergências | `resumos/bitident_20000.txt` |
| bit-identidade, as duas no baralho: partida em que nenhuma é vista (mão/campo/cemitério/exílio) é idêntica com as chaves nos extremos | **15.146 idênticas**, 0 divergências (24.854 em que alguma aparece) | idem |
| regressão 20.000 × 2 modos × 4 variantes | **0 exceções**, 0 carta acima do baralho, 0 campo negativo | `resumos/regressao_validacao_20000.txt` |
| determinismo (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos; chaves padrão e extremas) | **0 divergências** | `resumos/determinismo.txt` |

## Reprodução (comandos)
- Triagem / final: `bash orquestracao/lanca_triagem.sh`, `bash orquestracao/lanca_final.sh`; tabelas: `python3 orquestracao/rank_triagem.py 2000 triagem > resumos/rank_triagem.txt`, `python3 orquestracao/rank_final.py > resumos/tabela_final.md`, `python3 orquestracao/condicional.py > resumos/condicional.txt`.
- Spellbook: `python3 orquestracao/csb_stefano.py ../../lista.md dados/spellbook_stefano_frank_master.json 3`; `python3 orquestracao/resumo_spellbook.py > resumos/resumo_spellbook.md`.
- Lista: `python3 orquestracao/resolve_stefano.py`, `python3 orquestracao/diff_listas.py`, `python3 orquestracao/enumera_condicoes.py > resumos/enumeracao_condicoes.txt`.
- Validação: `bash orquestracao/lanca_validacao.sh` (≈ 1 h em 4 núcleos; **não edite o simulador enquanto roda**). Verificação: `bash orquestracao/verificar_reproducao.sh [--tudo]`.

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)
`bash orquestracao/verificar_reproducao.sh --tudo` (2026-10-07): **6 de 6 saídas byte a byte iguais** (`cmp`): `rank_triagem.txt`, `tabela_final.md`, `condicional.txt` e `resumo_spellbook.md` refeitos só dos `.json.xz` / do JSON da API e, **re-simulando a triagem inteira** (43 variantes × 2 modos × 2.000 partidas) com o simulador congelado `codigo/mothman_goldfish_v1_HM_triagem.py`, os dois brutos descomprimidos idênticos aos arquivados. **Não conferido:** o lote final de 10.000 (simulador `codigo/mothman_goldfish_v1_HM.py`; só a tabela dele foi refeita dos brutos), a regressão, a bit-identidade e o determinismo (saídas das execuções originais), e `diff_listas.py`/`enumera_condicoes.py` (leem o `lista.md` e o cache vivos).
