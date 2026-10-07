# Mothman: Jace, Wielder of Mysteries no lugar do Kozilek (2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Pergunta do usuário: *"Vale incluir no Mothman, no lugar do Kozilek? Ou é melhor ter a garantia contra decking out, até pq o Kozilek funciona ao ser millado?"* O raciocínio e as tabelas que vão ao usuário estão em `../../goldfish-log.md` §13; a tabela de cláusulas e rulings em `../../checklist-oraculo.md` §12; este arquivo guarda de onde cada número veio.

## Resposta curta (MEDIDO, N = 10.000 por variante e modo, pareado, `no lugar`, sementes 3.000.000+i, 12 turnos)
1. **Kozilek → Jace é neutro na velocidade e piora o deck-out:** mesa limpa até T8 −0,12 ± 0,37 (padrão) / −0,20 ± 0,29 (resiliência); T10 −0,31 ± 0,36 / −0,15 ± 0,38; **eu perco por deck-out +0,55 ± 0,35 \* / +0,47 ± 0,27 \*** (base 3,25% / 1,56%). **Controle** Kozilek → Forest: deck-out **+2,54 ± 0,40 \*** / +1,66 ± 0,33 \*. O Jace devolve a maior parte do seguro (o estático "comprar com biblioteca vazia = vitória") **só com ele em campo** (raciocinado).
2. **O que o Jace faz aqui (padrão):** `+1` em 19,4% das partidas (1,92 vezes quando usado), `+1` em mim em 0,7%, `−8` em 0,00%; vence em **4,08%** das partidas (1,67% até T8) com a política de afrouxar a reserva de biblioteca, 1,77% sem ela. Em 74 das 325 partidas que a base perdia por deck-out ele vence; em 186 partidas que a base não perdia, sem o Kozilek passa-se a perder.
3. **Jace no lugar de outra carta (Kozilek fica):** no lugar de Offer / Negate **+1,32 ± 0,33 \* / +1,25 ± 0,33 \*** de mesa limpa até T8 (padrão), +0,35 ± 0,25 \* na resiliência, deck-out −1,2 a −1,3 ponto; Deluge +0,77 \*, Arcane Denial +0,78 \*, Selkie +0,13 (n.s.). Com o Jace saindo 33% das rodadas ainda +0,97 \* (Negate).
4. **Spellbook** (`resumos/log_spellbook_jace.txt`): 91 nomes reconhecidos; controle positivo (Thassa + Consultation) e de corte (Ascension + Mindcrank some ao cortar o Mindcrank) passaram; o Jace **não cria combo novo** (12 "quase" de 2 peças, todas com a outra peça fora da lista).

**NÃO verificado (Regra #7):** ataque/remoção de oponente contra o planeswalker (só o proxy `JACE_REMOVAL_PROB`), oponente real jogando contra a linha de decking, prioridade de conjuração do Jace (66), o −8 (nunca disparou), o alvo ilegal do `+1` (R3; sem teste dirigido), o Jace junto com o Monument (mesmas cinco vagas), a parte do ganho que vem da política de afrouxar a reserva (só isolada contra o Kozilek).

## Como foi gerado
- **Simulador:** `../../mothman_goldfish_v1.py` no commit desta pasta (Jace implementado: `act_jace`, `jace_win`, `jace_line`, `jace_removal_roll`; chaves `JACE_STATIC_ENABLED`, `JACE_WIN_LINE`, `JACE_REMOVAL_PROB`; testes dirigidos **166/166**, 9 novos). Código anterior: `codigo/mothman_goldfish_v1_ANTES_1c18475.py` (bit-idêntico com o Jace fora do baralho).
- **Harness:** `orquestracao/driver_mm.py` + `abgen.py` (cópias dos de `../2026-10-07-riverchurn-monument/`), `PYTHONHASHSEED=0` fixado. Variantes em `orquestracao/config_final_1.json` (lote 1: Kozilek → Jace, sem a política, remoção 20% e 50%, Kozilek → Forest) e `config_final_2.json` (lote 2: Jace no lugar de Offer, Negate, Selkie, Deluge, Arcane Denial, Negate com remoção 33%). `base` é igual nos dois lotes (conferido em `rank_final.py`).
- **Pareamento:** `SWAP_IN_PLACE` (a carta que entra ocupa o lugar da que sai antes do embaralhamento): 96,5% das partidas têm a mesa limpa até T8 idêntica à base.
- **Dados brutos:** `colunas-v1` (`{variante: {n, fp, campos: {campo: [valor por partida]}}}`), todos os 245 campos numéricos do estado final, inclusive `jace_*`.

## Mapa arquivo → o que é → status
| arquivo | o que é | status | tabela que o usa |
|---|---|---|---|
| `dados/raw_final_1_10000[_resiliencia].json.xz` | lote 1 (base + 5 variantes), padrão e resiliência | usado | `resumos/tabela_final.md`, `goldfish-log.md` §13 |
| `dados/raw_final_2_10000[_resiliencia].json.xz` | lote 2 (base + 6 variantes), padrão e resiliência | usado | idem |
| `dados/jace_scryfall.json` | oráculo bruto + 5 rulings (Scryfall ao vivo, 2026-10-07; sem `flavor_name`) | usado | `checklist-oraculo.md` §12 |
| `dados/spellbook_jace.json` | respostas do `find-my-combos` (base, 87 cortes, controles) | usado | `resumos/log_spellbook_jace.txt` |
| `resumos/tabela_final.md` | todas as tabelas (`orquestracao/rank_final.py`, só lê os brutos) | usado | `goldfish-log.md` §13 |
| `resumos/final_*.txt`, `compacto_*.txt` | saída do driver por lote (tabelas pareadas completas) | apoio | — |
| `resumos/enumeracao_condicoes.txt` | cartas da lista por condição do Jace (compra, mill, devolve à biblioteca, fontes de `{U}`) | usado | `checklist-oraculo.md` §12 |
| `resumos/smoke_final_*.txt` | 99 cartas, 0 desconhecidas, 0 duplicadas, 200 partidas × 2 modos por variante | validação | — |
| `resumos/bitident_*.txt` | bit-identidade (`orquestracao/bitident_jace.py`, 4 fatias de 5.000) | validação | — |
| `resumos/regressao_validacao_20000.txt` | regressão 20.000 × 2 modos × 4 variantes | validação | — |
| `resumos/determinismo.txt` | 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos | validação | — |
| `resumos/verificacao_reproducao.txt`, `indice_dados.md` | verificação por `cmp`, índice dos brutos | apoio | — |
| `orquestracao/` | harness, configs, lançadores, `csb_jace.py`, `enumera_condicoes_jace.py`, `bitident_jace.py`, `verificar_reproducao.sh` | apoio | — |

## Validação do código
| verificação | resultado | arquivo |
|---|---|---|
| testes dirigidos (`../../testes/testes_dirigidos.py`) | **166/166** | — |
| smoke das 6 + 7 variantes finais | 0 exceções, 99 cartas, 0 desconhecidas, 0 duplicadas não básicas | `resumos/smoke_final_*.txt` |
| bit-identidade, `SWAPS=()`: simulador novo == `ANTES_1c18475`, campo a campo (campos `jace_*` ignorados), 20.000 sementes × 2 modos × 2 conjuntos de chaves | **80.000 de 80.000 idênticas**, 0 divergências | `resumos/bitident_20000.txt` |
| bit-identidade, Jace no baralho: partida em que ele NUNCA aparece (mão/campo/cemitério) é idêntica com as chaves nos dois extremos | **21.295 partidas idênticas**, 0 divergências (18.705 em que ele aparece, podem diferir) | idem |
| regressão 20.000 × 2 modos × 4 variantes (base; Kozilek → Jace no lugar; Negate → Jace com todas as chaves; Yavimaya Hollow → Jace `remove+append` sem a linha) | **0 exceções, 0 carta acima do baralho, 0 campo negativo** | `resumos/regressao_validacao_20000.txt` |
| determinismo entre processos (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos; chaves padrão e extremas) | **0 divergências** | `resumos/determinismo.txt` |

## Reprodução (comandos)
- A/B: `bash orquestracao/lanca_final.sh`; tabelas: `python3 orquestracao/rank_final.py > resumos/tabela_final.md`.
- Spellbook: `python3 orquestracao/csb_jace.py ../../lista.md dados/spellbook_jace.json 3`; condições: `python3 orquestracao/enumera_condicoes_jace.py`.
- Validação: `bash orquestracao/lanca_validacao.sh` (≈ 45 min em 4 núcleos; **não edite o simulador enquanto roda**).
- Dados brutos: `bash descomprimir.sh`; índice: `python3 indice_dados.py > resumos/indice_dados.md`.
- Verificação: `bash orquestracao/verificar_reproducao.sh [--tudo]` (**não edite o simulador enquanto roda**).
