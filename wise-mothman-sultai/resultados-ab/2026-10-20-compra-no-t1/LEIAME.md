# 2026-10-20 — Mothman: compra no 1º turno (o único dos 20 simuladores que pulava)

Pedido do usuário (2026-10-20): *"Corrija todos os simuladores por conta da compra no turno 1"*, depois de confirmar no goldfish manual #1 da Tam que *"no commander sempre há compra no 1o turno (mais de 2 jogadores)"*. A regra de pular a compra do 1º turno vale no 1x1 (CR 103.8a, citada nos comentários de Maralen, Kutzil, Hei Bai, Megatron, Nekusar, Rat King, Ulalek, Ur-Dragon e Vihaan desde 2026-09-18); Commander com 3+ jogadores não pula.

## Conclusão (medido)

**Só o Mothman pulava.** Verificação por EXECUÇÃO nos 20 `*_goldfish_v1.py` do repositório (`varredura-2026-10-05/scripts/audit_compra_t1.py`; 80 sementes; queda da biblioteca entre `turns=0` e `turns=1`): antes da correção, Mothman `{queda 0: 71 partidas, queda 1: 9}` (pula; nas 9 com queda 1 `draws_by_source` está vazio, isto é, nenhuma compra: a carta saiu da biblioteca por outra via, como busca ou mill) e os outros 19 `COMPRA` com queda mínima ≥ 1 (`varredura-2026-10-05/resumos/audit_compra_t1_ANTES.txt`); depois, 20 de 20 `COMPRA` (`audit_compra_t1_DEPOIS.txt`). Nenhum outro simulador foi alterado (o do Tam já estava corrigido em 2026-10-19, `FIRST_TURN_SKIPS_DRAW = False`).

**A correção:** `draw_step` do Mothman retornava no T1 (`if state.turn == 1 and state.on_play: return`, com `on_play = True` sempre). Agora `if FIRST_TURN_SKIPS_DRAW and state.turn == 1 and state.on_play: return`, com a chave nova `FIRST_TURN_SKIPS_DRAW = False` (padrão: compra). `True` = comportamento até o commit `4d85fbc`, bit a bit.

**Efeito medido** (N = 10.000 pareado, sementes 3.000.000+i, 12 turnos; nova / anterior / diferença ± IC95%; `*` = excede o IC; `resumos/base_nova.md`):

| | modo padrão | modo resiliência |
|---|---|---|
| comandante conjurado até T3 | 19,28 / 15,29 / **+3,99 ± 0,52 \*** | 17,95 / 14,24 / **+3,71 ± 0,50 \*** |
| comandante conjurado até T4 | 75,05 / 65,96 / **+9,09 ± 0,76 \*** | 69,07 / 60,61 / **+8,46 ± 0,78 \*** |
| comandante conjurado até T5 | 84,68 / 78,83 / +5,85 ± 0,65 \* | 79,42 / 72,98 / +6,44 ± 0,73 \* |
| mesa limpa até T7 | 26,77 / 18,74 / +8,03 ± 0,89 \* | 10,88 / 7,31 / +3,57 ± 0,63 \* |
| **mesa limpa até T8** | 69,55 / 59,95 / **+9,60 ± 0,98 \*** | 35,04 / 28,12 / **+6,92 ± 0,98 \*** |
| mesa limpa até T10 | 91,87 / 89,08 / +2,79 ± 0,62 \* | 68,42 / 62,70 / +5,72 ± 1,03 \* |
| 1º oponente fora até T6 | 54,82 / 45,42 / +9,40 ± 0,92 \* | 33,47 / 27,55 / +5,92 ± 0,85 \* |
| deck-out (eu perco) | 3,20 / 2,69 / +0,51 ± 0,44 \* | 1,71 / 1,38 / +0,33 ± 0,33 \* |
| biblioteca mínima (média) | 50,15 / 51,72 / −1,57 ± 0,45 \* | 53,24 / 55,34 / −2,09 ± 0,45 \* |
| vida mínima (média) | 32,95 / 32,96 / −0,01 (ruído) | 30,65 / 30,73 / −0,08 (ruído) |

1. **A coluna "anterior" reproduz a linha de base do `goldfish-log.md` §23** (T8 60,0% / 28,1%; comandante até T4 66,0% / 60,6%; deck-out 2,69% / 1,38%): o snapshot `4d85fbc` é o simulador daquele número, então a diferença é só a compra.
2. **O tamanho do efeito (+9 pontos de comandante até T4, +9,6 de mesa limpa até T8) é a carta a mais em TODA partida**, num deck cujo plano depende de achar terreno e do comandante cedo. A **nova linha de base do Mothman** passa a ser a coluna "nova" (T8: **69,6% / 35,0%**). Todas as seções anteriores do `goldfish-log.md` (§1 a §23) foram medidas **sem** a compra do T1 e ficam marcadas como superadas em magnitude (ver nota no topo do log); **não foram refeitas**.
3. **Custo:** a biblioteca mínima cai ~1,6 a 2,1 cartas e o deck-out sobe +0,5 / +0,3 ponto (as partidas acabam antes, mas quem enche o próprio cemitério compra uma carta a mais).

Lote de 2.000 (sementes 1.000.000+i): mesmo sentido, `cleared_T8` +8,1 ± 2,2 \* (padrão) e +7,3 ± 2,2 \* (resiliência) (`resumos/ab_2000*.txt`).

## O que mudou no código

`wise-mothman-sultai/mothman_goldfish_v1.py`: a chave `FIRST_TURN_SKIPS_DRAW` (junto de `LANDFALL_PAYOFFS`) e a condição no `draw_step`. Nada mais. Os turnos dos oponentes já compravam sempre (`opponent_turn`: "compra (nao pula...)": lido no código, não instrumentado).
Teste dirigido novo `compra_no_turno_1_commander_multijogador` em `testes/testes_dirigidos.py` (a biblioteca cai ≥ 1 no T1 em 5 sementes; `draws_by_source["normal"] == 1`; com a chave ligada `== 0`; o T2 compra nos dois casos): **209/209** (208 anteriores + 1).

## Validação

| o quê | resultado | arquivo |
|---|---|---|
| testes dirigidos | **209/209** | `../../testes/testes_dirigidos.py` |
| smoke (99 cartas, 91 distintas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos × 2 versões) | 0 exceções | `resumos/smoke.txt` |
| **bit-identidade:** vivo com `FIRST_TURN_SKIPS_DRAW=True` == snapshot `4d85fbc` (impressão digital do resultado inteiro, sementes 5.000.000+i) | **20.000 / 20.000 por modo, 0 diferenças** | `resumos/bitident_20000.txt` |
| regressão 20.000 × 2 modos, `depois` e `chave_desligada` (sementes 5.000.000+i) | 0 exceções, 0 carta acima do baralho, 0 campo negativo (4 configurações) | `resumos/regressao_20000.txt` |
| determinismo: 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos, campo a campo, padrão e chave ligada | 0 sementes divergentes nos 4 casos | `resumos/determinismo.txt` |
| varredura em runtime dos 20 simuladores (positivo: o ANTES acusa PULA no Mothman; negativo: o DEPOIS dá 20 COMPRA) | ver acima | `varredura-2026-10-05/resumos/audit_compra_t1_*.txt` |
| A/B pareado `antes` × `depois`, N = 2.000 e 10.000 × 2 modos | tabela acima | `resumos/ab_*.txt`, `base_nova.md` |
| reprodutibilidade (`orquestracao/verificar_reproducao.sh --tudo`) | ver `resumos/verificacao_reproducao.txt` | idem |

## Mapa arquivo → o que é → status

| arquivo | o que é | status |
|---|---|---|
| `codigo/mothman_goldfish_v1_ANTES_4d85fbc.py` | o simulador antes da correção (commit `4d85fbc`, com a Fabled Passage) | usado como variante `antes` |
| `dados/raw_ab_2000[_resiliencia].json.xz`, `raw_ab_10000[_resiliencia].json.xz` | bruto por partida (colunas-v1, uma lista por campo, `fp` = impressão digital): variantes `antes` e `depois` | usado em `ab_*.txt` e `base_nova.md` |
| `resumos/ab_2000*.txt`, `ab_10000*.txt` | tabelas pareadas com IC95% (`driver.py sum`) | usado |
| `resumos/base_nova.md` | a tabela desta conclusão | usado |
| `resumos/bitident_20000.txt`, `regressao_20000.txt`, `smoke.txt`, `determinismo.txt` | validação | usado |
| `resumos/cadeia_horarios.txt`, `log_driver.txt` | horários e log do driver (0 `Traceback`) | usado |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos brutos; saída da re-execução completa | usado |
| `orquestracao/` | `driver.py` e `abgen.py` genéricos, `config.json` (`flags_off = {FIRST_TURN_SKIPS_DRAW: true}`, `turns = 12`), `cadeia.sh` (bit-identidade → regressão → A/B), `base_nova.py`, `verificar_reproducao.sh` | usado |

Nenhum lote foi superado nem invalidado.

## Como refazer

```
bash descomprimir.sh                                   # .json.xz -> dados_json/ (fora do git)
cd orquestracao
python3 base_nova.py | cmp - ../resumos/base_nova.md   # a tabela desta conclusão, só dos brutos
bash verificar_reproducao.sh                           # tabelas do A/B, base_nova e índice: cmp byte a byte (6)
bash verificar_reproducao.sh --tudo                    # re-simula smoke, bit-identidade, regressão e os 4 lotes (~30 min; não edite o simulador enquanto roda)
python3 ../../../../varredura-2026-10-05/scripts/audit_compra_t1.py   # a varredura dos 20 simuladores
sha256sum -c ../SHA256SUMS                             # integridade (rodar na pasta do arquivo)
```

## Escopo (Regra #7)

**Verificado, com método e número:** a queda da biblioteca entre `turns=0` e `turns=1` em 80 sementes de cada um dos 20 simuladores, por execução (não por grep); bit-identidade 20.000 × 2 modos da chave ligada contra o snapshot; regressão e determinismo acima; a coluna "anterior" do A/B reproduz a linha de base documentada.
**NÃO verificado / limites:** (1) a varredura mede só o comportamento padrão (sem variar flags) e 80 sementes por deck; um simulador que pulasse só com certa configuração não apareceria; (2) a regra foi dada pelo usuário e já estava nos comentários do repositório; **não busquei o texto da CR ao vivo nesta rodada**; (3) os turnos de oponente do Mothman foram lidos no código, não instrumentados; (4) as seções §1 a §23 do `goldfish-log.md` e os A/B de lista antigos (Fabled, Underground Sea, Tropical, candidatas, pacotes) **não foram refeitos** com a compra: o sentido das diferenças pareadas deve se manter, a magnitude pode mudar; (5) logs de partidas MANUAIS antigos com "sem compra no T1" (Edgar `goldfish-log.md` ~linha 325, Prismatic Bridge ~1773, ambos de 2026-08-20) são registros históricos do método daquele dia e **não foram alterados**; (6) uma só família de sementes por lote.
