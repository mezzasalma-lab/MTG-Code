# Mothman: as seis candidatas do Stefano (2026-10-07)

Arquivo da Regra #8 (`CLAUDE.md`). Pedido do usuário: medir, na ordem, **Fractured Sanity, Screeching Scorchbeast, Inexorable Tide** e os dobradores (**Branching Evolution, Loading Zone, The Earth Crystal**) da lista do Stefano. Raciocínio, tabelas e ressalvas: `../../goldfish-log.md` §15; cláusulas e rulings: `../../checklist-oraculo.md` §14.

## Resposta curta (MEDIDO, N = 10.000, pareado, `no lugar`, sementes 3.000.000+i, 12 turnos; mesa limpa até T8, padrão / resiliência, pontos; `*` = excede o IC95%)
| carta ← Negate | T8 | quando entra até T6 |
|---|---|---|
| Branching Evolution | **+1,88 ± 0,38 \* / +0,93 ± 0,31 \*** | +13,8 \* |
| Loading Zone | +1,25 \* / +0,69 \* | +9,5 \* |
| The Earth Crystal | +1,18 \* / +0,49 \* | +13,3 \* |
| Fractured Sanity | +1,17 \* / +0,59 \* | +5,7 \* (conjurada ou ciclada) |
| Inexorable Tide | +1,12 \* / +0,29 \* | +11,5 \* |
| Screeching Scorchbeast | +0,95 \* / +0,20 (`SCORCH_MIN_X` 1: +1,42 \*; 6: +0,67 \*) | +14,0 \* |
- **Seis juntas** no lugar das seis (4 contramágicas + Deluge + Selkie): **+5,47 ± 0,65** / +2,43 ± 0,56, menos que a soma (+7,55); o valor de interação contra oponente real NÃO está medido.
- **Achado do baseline:** a Glen Elendra voltava do persist como 0/0 vivo com Constrictor ou Loading Zone; corrigido (`PERSIST_ZERO_TOUGHNESS_DIES`), efeito **nulo** (+0,02 ± 0,03; 0,4% das partidas).
- **Spellbook** (`resumos/log_spellbook_cand2.txt`): 96 nomes reconhecidos, controles ok; nenhuma das seis (nem juntas) cria combo.

**NÃO verificado (Regra #7):** prioridades de conjuração; Zumbi Mutant contra oponentes reais; as seis somadas com Horrigan/Monument/Jace; política de esperar um mill maior (Scorchbeast); Warp no turno do oponente; ordem humana de ciclar a Fractured Sanity.

## Como foi gerado
- **Simulador:** `codigo/mothman_goldfish_v1_C2.py` (== `../../mothman_goldfish_v1.py` deste commit) = `codigo/mothman_goldfish_v1_ANTES_HM.py` (Horrigan/Master) + `orquestracao/patch_c2.py`. 194 testes dirigidos (12 novos, `orquestracao/novos_testes_c2.py`).
- **Harness:** `driver_mm.py` + `abgen.py` (cópias das da pasta do Horrigan); `PYTHONHASHSEED=0`. Triagem N = 2.000 (`config_triagem.json`: 6 cartas × 6 cortes + base); final N = 10.000 (`config_final.json`, 15 variantes). Ambos sobre o arquivo CONGELADO de `codigo/`.
- **Spellbook:** `orquestracao/csb_cand2.py` (base, + cada carta, + as seis, controles positivo e de corte).

## Mapa arquivo → o que é → status
| arquivo | o que é | status | usado em |
|---|---|---|---|
| `dados/rulings_candidatas2.json` | oráculo + rulings das seis (Scryfall, 2026-10-07; sem `flavor_name`) | usado | `checklist-oraculo.md` §14 |
| `dados/spellbook_cand2.json` | `find-my-combos`: base, + cada carta, + as seis, controles | usado | `resumos/log_spellbook_cand2.txt` |
| `dados/raw_triagem_2000[_resiliencia].json.xz` | triagem N = 2.000, 37 variantes | usado (escolheu as variantes do final) | `resumos/rank_triagem.txt` |
| `dados/raw_final_10000[_resiliencia].json.xz` | final N = 10.000, 15 variantes | usado | `resumos/tabela_final.md`, `condicional.txt` |
| `resumos/bitident_*.txt`, `log_regressao.txt` / `regressao_validacao_20000.txt`, `determinismo.txt`, `smoke_final.txt` | validação do código | validação | — |
| `orquestracao/` | harness, patch, testes, `bitident_c2.py`, scripts de tabela, `verificar_reproducao.sh` | apoio | — |

## Validação do código
| verificação | resultado |
|---|---|
| testes dirigidos | **194/194** |
| smoke das 15 variantes (200 partidas × 2 modos) | 0 exceções (`resumos/smoke_final.txt`) |
| bit-identidade, `SWAPS=()` == `ANTES_HM` (chave do persist desligada, `SCORCH_MIN_X` nos extremos), 20.000 × 2 modos | **80.000 de 80.000**, 0 divergências; 3.944 partidas sem nenhuma das seis idênticas (36.056 em que alguma aparece) |
| regressão 20.000 × 2 modos × 4 variantes (base; seis no lugar; seis `remove+append` com `SCORCH_MIN_X` 1; base com o persist antigo) | **0 exceções**, 0 carta acima do baralho, 0 campo negativo |
| determinismo (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos; chaves padrão e extremas) | **0 divergências** |
| **reprodutibilidade** (`resumos/verificacao_reproducao.txt`, `bash orquestracao/verificar_reproducao.sh --tudo`, concluída em 2026-10-08) | **5/5 saídas byte a byte iguais**: `rank_triagem.txt`, `tabela_final.md` e `condicional.txt` refeitos só dos brutos arquivados, e os dois brutos da triagem (37 variantes × 2.000 × 2 modos) **re-simulados do zero com o simulador congelado** `codigo/mothman_goldfish_v1_C2.py`, idênticos ao arquivado. A 1ª tentativa (2026-10-07 23:49) e a 2ª (2026-10-08 00:21) foram derrubadas por reinícios do worker; esta é a 3ª e a que fecha. **Não conferido:** os brutos do lote final de 10.000 não foram re-simulados (só as tabelas dele foram refeitas dos brutos, 2/2 iguais); a replicação cruzada deles está em `../2026-10-08-pacote-e-interacao/resumos/replicacao.txt` (base e Branching ← Negate bit-idênticas, 10.000 × 2 modos). |

## Reprodução (comandos)
`bash orquestracao/lanca_triagem.sh`; `bash orquestracao/lanca_final.sh`; `python3 orquestracao/rank_triagem.py 2000 triagem > resumos/rank_triagem.txt`; `python3 orquestracao/rank_final.py > resumos/tabela_final.md`; `python3 orquestracao/condicional.py > resumos/condicional.txt`; `python3 orquestracao/csb_cand2.py ../../lista.md dados/spellbook_cand2.json`; validação `bash orquestracao/lanca_validacao.sh` (≈ 1,5 h; **não edite o simulador enquanto roda**); verificação `bash orquestracao/verificar_reproducao.sh [--tudo]`.
