# Rodada 4 do Rat King, Verminister (2026-10-28): as duas faces do Fell the Profane // Fell Mire, Black Market Connections com lifegain e o ensaio do terreno virado que escondia o comandante do T2

Arquivo **permanente e auditável** de tudo que sustenta as conclusões desta rodada. As conclusões e as tabelas legíveis estão em `rat-king-verminister/goldfish-log.md` (seção desta rodada, no topo), `checklist-oraculo.md` e `auditoria.md` §15. Esta pasta guarda os dados.

Pedido do usuário (2026-10-28), em resposta ao relatório da rodada 3: *"Bracket 2"*; *"Modela sim ambas as faces"*; *"Acho que o modo mais importante do Black Market Connections é o 1o, com custo 1 de vida. Os demais só entram em cena se eu tiver algum mecanismo de lifegain rodando: Ayara, ou outro qq"*.

> **STATUS DESTA PASTA:** fechada em 2026-10-28. Verificação de reprodutibilidade: `bash orquestracao/verificar_reproducao.sh --tudo` → **22/22 saídas byte a byte iguais** (tabelas do A/B, resumos derivados dos brutos, smoke, bit-identidade, ghost, regressão, testes dirigidos, prova de não-vacuidade do ghost e os 4 brutos re-simulados, comparados com `cmp`; `resumos/verificacao_reproducao.txt`). **Não conferidos por `cmp`:** `determinismo.txt`, `regra10_*.txt`, `indice_dados.md` e os logs (`log_driver*.txt`); o determinismo e as varreduras foram rodados uma vez cada.

> **Nota de 2026-10-29:** o arquivo vivo `ratking_goldfish_v1.py` mudou nas rodadas 5 e 6 depois desta pasta. `verificar_reproducao.sh --tudo` **desta pasta DIFERE** do vivo (não reexecutei); sem `--tudo` (tabelas derivadas dos brutos) continua valendo. Para reproduzir o `--tudo`, use `codigo/ratking_goldfish_v1_DEPOIS.py` no lugar do vivo, ou o commit `3635578`.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (seção mais nova no topo) |
| ver cada cláusula/ruling × código | `../../checklist-oraculo.md` (seção da rodada 4) |
| refazer as tabelas do A/B a partir dos dados | `bash orquestracao/verificar_reproducao.sh` |
| refazer TUDO (re-simula; **não editar o simulador enquanto roda**) | `bash orquestracao/verificar_reproducao.sh --tudo` |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |

## O que mudou no simulador

`ratking_goldfish_v1.py` ganhou **4 chaves**, todas ligadas no arquivo vivo. Com as 4 desligadas ele é **bit-idêntico** ao snapshot `codigo/ratking_goldfish_v1_ANTES_7639380.py` (o arquivo no commit `7639380`, imediatamente antes desta rodada; `sha256` a86fa266…caebb5).

| chave (e constantes) | cláusula do oráculo / ruling | o que o código fazia antes |
|---|---|---|
| `FELL_MIRE_LAND_ENABLED`, `FELL_MIRE_MAX_LANDS_IN_PLAY = 6`, `FELL_MIRE_LIFE_FLOOR = 10`, `FELL_MIRE_GHOST` (só validação) | Fell Mire: "As this land enters, you may pay 3 life. If you don't, it enters tapped. {T}: Add {B}."; ruling 2024-06-07 (a MDFC se joga como terreno; fora do campo vale só a face da frente) | só a face de feitiço existia ("remoção é o gap real": julgamento de valor, vedado pela Regra #1) |
| `FELL_MIRE_COUNTS_FOR_KEEP` | a MDFC é jogável como terreno | `should_keep` não a contava |
| `BMC_MODES_NEED_LIFEGAIN`, `LIFEGAIN_ENGINES` | Black Market Connections: "At the beginning of your first main phase, choose one or more — Sell Contraband (Treasure, You lose 1 life) · Buy Information (draw, 2) · Hire a Mercenary (Mercenary 3/2 changeling, 3)" (0 rulings); pedido do usuário | sempre os 3 modos, a vida podia passar de 0 |
| `TAPPED_FIRST_COUNTS_MANA` | (conceito compartilhado, Regra #3) o comandante sai da zona de comando, não da mão | o ensaio do "terreno virado primeiro" (2026-10-05) media só o MV que sai da mão e ignorava o comandante: com empate em 0 jogava o terreno virado e perdia o T2 |

**Políticas minhas, não do oráculo (o usuário não as definiu):** 6 terrenos como limite para a MDFC virar terreno; piso de vida 10 para pagar os 3; nunca escolher modo do BMC que leve a vida a 0 ou menos. Sensibilidade no A/B: limite 4 e 99; nunca pagar vida; piso 4.

## Como os dados foram gerados

- **Oráculo e rulings:** lidos do arquivo ao vivo da rodada 3 (`../2026-10-25-rodada3-spellbook-rulings-e-correcoes/dados/scryfall_oraculo_rulings_2026-10-25.json`: Fell the Profane // Fell Mire com 6 rulings, Black Market Connections com 0) **antes** de editar o simulador.
- **A/B pareado, bit-identidade, ghost, regressão:** `orquestracao/driver.py` + `abgen.py` (lêem `orquestracao/config.json`). Sementes: A/B N=2.000 → `1_000_000+i`; N=10.000 → `3_000_000+i`; regressão, bit-identidade e ghost → `5_000_000+i`. 8 turnos; dois modos (`padrao` = `simulate_one`; `resiliencia` = `simulate_one_with_interaction`). `PYTHONHASHSEED=0` fixado pelo driver. Variantes (cada uma lista **as chaves todas**; confirmado em `resumos/diferem_entre_variantes.txt` que diferem entre si): `antes` (snapshot), `depois` (arquivo vivo, tudo ligado), `so_fell_terreno`, `so_fell_terreno_e_keep`, `so_bmc`, `so_tapped_first_mana`, `fell_max_terrenos_4`, `fell_max_terrenos_99`, `fell_nunca_paga_vida`, `fell_piso_vida_4` e `ref_sem_terreno_virado_primeiro` (referência: a política de 2026-10-05 desligada). IC95% = 1,96·dp(diferença pareada)/√N.
- **Mudança no harness desta pasta:** `abgen.py` agora gera o indicador `__ate_T2` (antes T3 a T6); `driver.py` aceita `ghost_base` no config (a referência do ghost pode ser outra configuração ligada).
- **Ghost:** com `FELL_MIRE_GHOST` o ensaio a seco roda e o resultado é ignorado (nunca paga); a referência tem `FELL_MIRE_LIFE_FLOOR = 99`, em que o ensaio nem roda. Idênticos ⇒ o ensaio não tem efeito colateral. **A 1ª versão desse teste era vácua** (as duas pontas tinham piso 99): `resumos/ghost_20000_INVALIDO_vacuo.txt`, guardado e marcado. `resumos/ghost_vacuidade.txt` prova a não-vacuidade da versão que vale: 642 ensaios executados em 3.000 partidas, contra 0 na referência.
- **Testes dirigidos:** `orquestracao/testes_dirigidos.py` (21; chave ligada e desligada; partidas inteiras onde o resultado exige contagem > 0).
- **Determinismo:** `varredura-2026-10-05/scripts/det_check.sh rat-king-verminister ratking_goldfish_v1.py 8 1500` → `resumos/determinismo.txt`.
- **Varreduras da Regra #10** (`varredura-2026-10-05/scripts/`, rodadas sobre o arquivo vivo, saída inteira guardada em `resumos/regra10_*.txt`).

## Mapa: arquivo → o que é → código → status → onde aparece

| arquivo | o que é | código | status | tabela do log que a usa |
|---|---|---|---|---|
| `dados/raw_ab_2000.json.xz`, `raw_ab_10000.json.xz` | A/B padrão: `antes` + `depois` + 9 variantes, N=2.000 / 10.000 | `orquestracao/driver.py ab` com `config.json` | usado | `resumos/ab_*.txt`; log: tabela principal |
| `dados/raw_ab_2000_resiliencia.json.xz`, `raw_ab_10000_resiliencia.json.xz` | idem, modo resiliência | idem | usado | `resumos/ab_*_resiliencia.txt` |
| `resumos/ab_2000.txt`, `ab_10000.txt`, `*_resiliencia.txt` | tabelas pareadas (diferença ± IC95%, fração de partidas idênticas) | `driver.py sum` (só dos brutos) | usado | log |
| `resumos/resumo_variantes_10000.md` | uma linha por variante, métricas escolhidas, e os contadores novos | `orquestracao/resumo_variantes.py` | usado | log: tabela por chave |
| `resumos/diferem_entre_variantes.txt` | fração de partidas idênticas entre pares de variantes (controle de vacuidade) | `orquestracao/diferem_entre_variantes.py` | usado | log: sensibilidade |
| `resumos/combos_antes_depois.txt` | combos do Spellbook executados até T4–T6, antes × depois | `orquestracao/combos_antes_depois.py` | usado | `auditoria.md` §15 (decisão do Bracket 2) |
| `resumos/bitident_20000.txt` | 4 chaves desligadas == snapshot, 20.000 × 2 modos: 0 diferentes | `driver.py bitid` | verificação | log: validação |
| `resumos/ghost_20000.txt` | ensaio rodando e ignorado == ensaio nem rodando: 0 diferentes | `driver.py ghost` | verificação | log: validação |
| `resumos/ghost_20000_INVALIDO_vacuo.txt` | 1ª versão do ghost (piso 99 nas duas pontas: o ensaio nunca rodou) | `driver.py ghost` com o config antigo | **INVÁLIDO** (guardado, marcado) | log |
| `resumos/ghost_vacuidade.txt` | quantas vezes o ensaio executou (642 × 0) | `orquestracao/ghost_vacuidade.py` | verificação | log |
| `resumos/regressao_20000.txt` | 20.000 × 2 modos × 2 configurações: 0 exceções, 0 cartas acima do baralho; `mana_spent_this_turn` negativo em 76/80 (ligadas) e 80/74 (desligadas) | `driver.py reg` | verificação | log |
| `resumos/smoke.txt` | biblioteca de 99 cartas, 0 desconhecidas; 200 partidas × 2 modos, vivo e snapshot | `driver.py smoke` | verificação | log |
| `resumos/testes_dirigidos.txt` | 21/21 testes | `orquestracao/testes_dirigidos.py` | verificação | log |
| `resumos/determinismo.txt` | 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos: 0 divergentes | `det_check.sh` | verificação (1 execução, não coberta por `cmp`) | log |
| `resumos/regra10_*.txt` | saída inteira de `audit_entrada`, `audit_entrada2`, `audit_fetch`, `audit_terreno_nao_e_magia`, `colisao_nome` (padrão e resiliência, 400 partidas), `audit_compra_t1`, `audit_landfall_ordem`, `audit_etb_sem_efeito` (idêntico ao DEPOIS da rodada 3) | `varredura-2026-10-05/scripts/` | verificação (1 execução, não coberta por `cmp`) | log |
| `resumos/indice_dados.md` | o que há em cada arquivo de `dados/` | `indice_dados.py` | índice | — |
| `resumos/log_driver.txt` | log da 1ª bateria `smoke bitid ghost reg ab`. **A parte do ghost é a versão INVÁLIDA** (a que vale foi rodada depois e está em `ghost_20000.txt`) e **a parte do A/B é de uma execução superada** (sem o indicador T2 e sem a variante de referência; os brutos dela foram sobrescritos). Smoke, bit-identidade e regressão dessa bateria valem | `driver.py` | **parcialmente superado** (marcado) | — |
| `resumos/log_driver_ab.txt` | log da última execução do `ab` (a que gerou os brutos arquivados: T2 e variante de referência) | `driver.py ab` | usado | — |
| `resumos/verificacao_reproducao.txt` | saída de `verificar_reproducao.sh --tudo` | `orquestracao/verificar_reproducao.sh` | verificação | — |
| `codigo/ratking_goldfish_v1_ANTES_7639380.py` | o simulador antes desta rodada | — | usado | — |
| `codigo/ratking_goldfish_v1_DEPOIS.py` | o simulador fixado usado pelo A/B e pela verificação (== o arquivo vivo; conferido por `cmp` em `--tudo`) | — | usado | — |
| `orquestracao/*` | harness, config, testes, resumos, verificação | — | usado | — |

## Escopo (Regra #7): o que esta rodada NÃO fez

- **Não decidi** (esperam o usuário): os 3 wipes (Kindred Dominance, Swarmyard Massacre, Damnation), que seguem sem efeito no próprio campo.
- **Não medi** os outros 13 simuladores com a mesma função `_tl_dry_run_mv` (Azula, Bumbleflower, Captain Storm, Edgar, Hei Bai, Kutzil, Maralen, Nekusar, Prismatic Bridge, Thranduil, Toph, Ulalek, Ur-Dragon), nem li os 4 com a chave `TAPPED_LAND_FIRST_ENABLED` e outra função (Megatron, Mothman, Tam, Vihaan). O erro do comandante pode estar neles.
- **Cobertura das varreduras:** `audit_entrada.py` e `audit_entrada2.py` só varrem os 11 terrenos da lista (a MDFC não está na biblioteca); a regra "paga 3 ou entra virado" é coberta só pelos testes dirigidos FM4–FM6. `audit_landfall.py` não rodou (o deck não tem payoff de landfall).
- **Políticas e simplificações:** `choose_bottom` do mulligan trata a MDFC como feitiço; `try_takenuma_channel` não a conta como "outro terreno na mão"; o "lifegain rodando" do BMC olha só a presença do permanente no começo da fase principal, não se o gatilho dispara no turno (Crypt Ghast sem magia para pagar extort, Rotcaller sem atacar); Gray Merchant (só ETB) não conta como lifegain.
- **O piso de vida 10 nunca decide** nas 10.000 partidas (a variante com piso 4 é idêntica em 10.000 de 10.000): ele só existe como proteção.
- **O modo de resiliência** não foi lido cláusula a cláusula; só passou pelos mesmos testes e tabelas.
- **Provas de uma execução só:** determinismo (3 hash seeds), varreduras da Regra #10.
- O invariante genérico "contador negativo" de `mana_spent_this_turn` (76/80 ligadas, 80/74 desligadas) é o mesmo da rodada 3 (mana líquida de rituais somada como gasto negativo); não o investiguei de novo.
