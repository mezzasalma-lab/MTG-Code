# Rodada 5 do Rat King, Verminister (2026-10-28): Kindred Dominance, Swarmyard Massacre e Damnation no próprio campo (Opção B) e o A/B dos limites

Arquivo **permanente e auditável** de tudo que sustenta as conclusões desta rodada. As conclusões e as tabelas legíveis estão em `rat-king-verminister/goldfish-log.md` (seção desta rodada, no topo) e `checklist-oraculo.md`. Esta pasta guarda os dados.

Pedido do usuário (2026-10-28), resposta ao relatório da rodada 4: *"Opção B nos wipes, e meça no A/B"*.

> **STATUS DESTA PASTA:** fechada em 2026-10-28. Verificação de reprodutibilidade: `bash orquestracao/verificar_reproducao.sh --tudo` → **19/19 saídas byte a byte iguais** (tabelas do A/B, resumos derivados dos brutos, smoke, bit-identidade, regressão, testes dirigidos e os 4 brutos re-simulados, comparados com `cmp`; `resumos/verificacao_reproducao.txt`). **A 1ª execução deu 18/19** (`resumos/verificacao_reproducao_1a_execucao_18_de_19.txt`): o `testes_dirigidos.txt` nunca tinha sido gravado, então o `cmp` não tinha com o que comparar; gravei o arquivo e refiz a verificação inteira. **Não conferidos por `cmp`:** `determinismo.txt`, `audit_etb_sem_efeito_DEPOIS.txt`, `indice_dados.md` e `log_driver.txt`; o determinismo e o scanner foram rodados uma vez cada.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (seção mais nova no topo) |
| ver cada cláusula/ruling × código | `../../checklist-oraculo.md` (seção da rodada 5) |
| refazer as tabelas do A/B a partir dos dados | `bash orquestracao/verificar_reproducao.sh` |
| refazer TUDO (re-simula; **não editar o simulador enquanto roda**) | `bash orquestracao/verificar_reproducao.sh --tudo` |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |

## O que mudou no simulador

`ratking_goldfish_v1.py` ganhou **3 chaves de efeito e 2 de política**, todas ligadas no arquivo vivo. Com todas desligadas (`WIPE_EFFECT_* = False`, `WIPE_CAST_MAX_OWN_LOSS = None`, `WIPE_GATE_NET_OF_NEW_TOKENS = False`) ele é **bit-idêntico** ao snapshot `codigo/ratking_goldfish_v1_ANTES_3635578.py` (o arquivo no commit `3635578`, o fim da rodada 4).

| chave | o que faz | antes |
|---|---|---|
| `WIPE_EFFECT_KINDRED` | "Choose a creature type. Destroy all creatures that aren't of the chosen type." no MEU campo; escolhe o tipo que menos mata; o Mercenary de changeling sempre sobrevive | pago e contado como interação, sem efeito |
| `WIPE_EFFECT_SWARMYARD` | 2 Esquilos, depois −1/−1 por criatura minha Insect/Rat/Spider/Squirrel; morre a carta não protegida com tenacidade ≤ N | só criava os 2 Esquilos |
| `WIPE_EFFECT_DAMNATION` | "Destroy all creatures": tudo morre, o comandante inclusive (volta à zona de comando) | pago e contado, sem efeito |
| `WIPE_CAST_MAX_OWN_LOSS = 0` (**política minha**) | só conjura o wipe com efeito ligado se a perda própria ≤ N; `None` = conjura sempre | conjurava sempre que cabia |
| `WIPE_GATE_NET_OF_NEW_TOKENS = True` (**política minha**) | a perda comparada é líquida dos corpos que o wipe cria (os 2 Esquilos do Swarmyard) | — |

As mortes são simultâneas (CR 603.10) e disparam os mesmos payoffs do wipe do oponente do modo de resiliência (Zulaport, Pitiless Plunderer, Syr Konrad, Species Specialist, Ninja Teen). Tipos e tenacidades das 18 criaturas: tabela `CREATURE_TYPES`/`CREATURE_TOUGHNESS` do simulador, conferida contra o oráculo ao vivo arquivado pelo teste WP0.

## Como os dados foram gerados

- **Oráculo e rulings:** lidos do arquivo ao vivo da rodada 3 (`../2026-10-25-rodada3-spellbook-rulings-e-correcoes/dados/scryfall_oraculo_rulings_2026-10-25.json`: Kindred Dominance 3 rulings, Swarmyard Massacre 1, Damnation 0) **antes** de editar o simulador.
- **A/B pareado, bit-identidade, regressão:** `orquestracao/driver.py` + `abgen.py` (cópia da rodada 4, com o indicador `__ate_T2`; lêem `orquestracao/config.json`). Sementes: A/B N=2.000 → `1_000_000+i`; N=10.000 → `3_000_000+i`; regressão e bit-identidade → `5_000_000+i`. 8 turnos; dois modos. `PYTHONHASHSEED=0` fixado pelo driver. Variantes (cada uma lista as 5 chaves; diferem entre si e do `antes`, `resumos/diferem_entre_variantes.txt`): `antes` (snapshot), `depois` (arquivo vivo: limite 0 líquido), `so_kindred`, `so_swarmyard`, `so_damnation` (só aquele wipe com efeito; os outros no comportamento antigo), `limite_0_bruto` (a 1ª versão da política), `limite_1`, `limite_2`, `limite_5` e `sempre_conjura_com_efeito` (Opção C).
- **Testes dirigidos:** `orquestracao/testes_dirigidos.py` (10; chave ligada e desligada; partidas inteiras onde o resultado exige contagem > 0).
- **Determinismo:** `varredura-2026-10-05/scripts/det_check.sh rat-king-verminister ratking_goldfish_v1.py 8 1500` → `resumos/determinismo.txt`.

## Mapa: arquivo → o que é → código → status → onde aparece

| arquivo | o que é | código | status | tabela do log que a usa |
|---|---|---|---|---|
| `dados/raw_ab_2000.json.xz`, `raw_ab_10000.json.xz` | A/B padrão: `antes` + `depois` + 8 variantes, N=2.000 / 10.000 | `orquestracao/driver.py ab` | usado (2ª execução, com o limite líquido) | `resumos/ab_*.txt`; log: tabela do limite |
| `dados/raw_ab_2000_resiliencia.json.xz`, `raw_ab_10000_resiliencia.json.xz` | idem, modo resiliência | idem | usado | `resumos/ab_*_resiliencia.txt` |
| `superado-1a-execucao/` | brutos, tabelas, logs, config, bit-identidade e regressão da 1ª execução (SEM `WIPE_GATE_NET_OF_NEW_TOKENS`: o limite comparava só as mortes; era o que hoje é a variante `limite_0_bruto`) | `driver.py` com o simulador da 1ª versão (não pinado: o `depois` dela == a variante `limite_0_bruto` do lote atual) | **SUPERADO** (guardado, marcado) | log: "A 1ª versão do limite estava errada" |
| `resumos/ab_2000.txt`, `ab_10000.txt`, `*_resiliencia.txt` | tabelas pareadas (diferença ± IC95%, fração idêntica) | `driver.py sum` (só dos brutos) | usado | log |
| `resumos/resumo_variantes_10000.md` | uma linha por variante, métricas escolhidas e os contadores de wipe | `orquestracao/resumo_variantes.py` | usado | log: tabela do limite |
| `resumos/diferem_entre_variantes.txt` | fração de partidas idênticas entre pares de variantes | `orquestracao/diferem_entre_variantes.py` | usado (controle de vacuidade) | log |
| `resumos/bitident_20000.txt` | 5 chaves desligadas == snapshot, 20.000 × 2 modos: 0 diferentes | `driver.py bitid` | verificação | log |
| `resumos/regressao_20000.txt` | 20.000 × 2 modos × 2 configurações: 0 exceções, 0 cartas acima do baralho; `mana_spent_this_turn` negativo em 80/86 (ligadas) e 76/80 (desligadas) | `driver.py reg` | verificação | log |
| `resumos/smoke.txt` | biblioteca de 99 cartas, 0 desconhecidas; 200 partidas × 2 modos, vivo e snapshot | `driver.py smoke` | verificação | log |
| `resumos/testes_dirigidos.txt` | 10/10 testes | `orquestracao/testes_dirigidos.py` | verificação | log |
| `resumos/determinismo.txt` | 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos: 0 divergentes | `det_check.sh` | verificação (1 execução, não coberta por `cmp`) | log |
| `resumos/audit_etb_sem_efeito_DEPOIS.txt` | scanner de ETB sem efeito: saída idêntica à da rodada 4 | `varredura-2026-10-05/scripts/audit_etb_sem_efeito.py` | verificação (1 execução, não coberta por `cmp`) | log |
| `resumos/log_driver.txt` | log da bateria `smoke bitid reg ab` da 2ª execução | `driver.py` | log | — |
| `resumos/indice_dados.md` | o que há em cada arquivo de `dados/` | `indice_dados.py` | índice | — |
| `resumos/verificacao_reproducao.txt` | saída de `verificar_reproducao.sh --tudo` | `orquestracao/verificar_reproducao.sh` | verificação | — |
| `codigo/ratking_goldfish_v1_ANTES_3635578.py` | o simulador antes desta rodada | — | usado | — |
| `codigo/ratking_goldfish_v1_DEPOIS.py` | o simulador fixado usado pelo A/B e pela verificação (== o arquivo vivo; `cmp` em `--tudo`) | — | usado | — |
| `orquestracao/*` | harness, config, testes, resumos, verificação | — | usado | — |

## Escopo (Regra #7): o que esta rodada NÃO fez

- **Oponente real:** o lado do oponente dos 3 wipes segue N/A estrutural; o limite de perda própria é **política minha** e não há número correto sem um tabuleiro de oponente. O A/B mostra o preço de cada limite; a escolha é do usuário.
- **Simplificações:** bônus de tenacidade (Skullclamp equipado) não entram no −1/−1 do Swarmyard; fichas contam como 1/1 sem bônus; a escolha do tipo do Kindred olha só os tipos das minhas criaturas; o gatilho de Species Specialist usa o tipo Rat por convenção do deck.
- **Não varrido:** as classes da Regra #10 que a mudança não toca (entrada de terreno, compra do T1, landfall, ordem de fases); o modo de resiliência cláusula a cláusula.
- **Provas de uma execução só:** determinismo (3 hash seeds) e o scanner.
- O invariante genérico "contador negativo" de `mana_spent_this_turn` (80/86 ligadas, 76/80 desligadas) é o mesmo das rodadas 3 e 4 (mana líquida de rituais somada como gasto negativo); a diferença de ligadas para desligadas (+4/+6) não foi investigada.
