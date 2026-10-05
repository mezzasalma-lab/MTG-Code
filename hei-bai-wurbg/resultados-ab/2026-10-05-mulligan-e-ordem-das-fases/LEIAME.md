# Resultados brutos — Mulligan com escolha do fundo, imposto de comandante e ordem de iteração determinística no Hei-Bai (2026-10-05)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Hei-Bai, Forest Guardian. As conclusões e as tabelas legíveis
estão em `hei-bai-wurbg/goldfish-log.md` (seção "Mulligan com escolha do fundo + imposto de comandante + ordem de set determinística (varredura de 2026-10-05)") e em `hei-bai-wurbg/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**
Pedido do usuário (2026-10-05): *"Com base nos erros encontrados nas ultimas revisões, reanálise todos os outros decks em busca de erros semelhantes, e os corrija"*.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` (só as tabelas do A/B, segundos) ou `--tudo` (re-simula tudo numa pasta temporária e compara byte a byte) |
| abrir os brutos por partida em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## O que mudou no simulador

`heibai_goldfish_v1.py` ganhou 3 chave(s) de correção, todas **ligadas** no arquivo vivo: `MULLIGAN_SMART_BOTTOM_ENABLED`, `COMMANDER_TAX_ENABLED`, `DETERMINISTIC_SET_ORDER_ENABLED`. Com todas desligadas o simulador é **bit-idêntico** ao snapshot `codigo/heibai_goldfish_v1_ANTES_67ac5f4.py` (`resumos/bitident_20000.txt`).

- `MULLIGAN_SMART_BOTTOM_ENABLED` (padrão `True`) + `choose_bottom(hand, n)`: só devolve terreno quando sobram MAIS de 4 na mão (e então o que entra virado primeiro, se o `CARD_DB` marcar `etb_tapped`); fora isso devolve a carta não-terreno de MAIOR custo, poupando `MULLIGAN_PROTECTED` (as cartas que `should_keep` já trata como boa abertura). A regra do mulligan grátis do 1º mulligan (CR 103.5c, multiplayer) já estava modelada e não mudou. Com a chave em `False` o caminho antigo (sorteio) volta bit a bit.
- `COMMANDER_TAX_ENABLED` (padrão `True`) + `GameState.commander_cast_count`: `effective_cost` soma `2 × commander_cast_count` quando a carta é o comandante; `cast_card` incrementa o contador logo após pagar (antes de `try_smart_opponent_counter`, então um cast anulado também conta). O contador é um campo novo do estado (ignorado na comparação de bit-identidade, o snapshot não o tem).
- `DETERMINISTIC_SET_ORDER_ENABLED` (padrão `True`): o laço sobre `set(state.battlefield)` passa a iterar `dict.fromkeys(state.battlefield)` (deduplicado na ordem do campo). Com a chave em `False` o laço antigo volta.

O snapshot `codigo/heibai_goldfish_v1_ANTES_67ac5f4.py` é o simulador **como estava no commit `67ac5f4`**, imediatamente antes desta rodada, e é o que o "antes" do A/B executa.
Código desta pasta: o commit que a adiciona (`git log -1 -- hei-bai-wurbg/resultados-ab/2026-10-05-mulligan-e-ordem-das-fases`).

## Como os dados foram gerados

- **Simulador / driver:** `orquestracao/driver.py` (genérico, lê `orquestracao/config.json`) + `orquestracao/abgen.py` (A/B pareado, impressão digital, regressão). `heibai_goldfish_v1.py` lê `lista.md` do diretório do deck no `import`; o driver faz `chdir` pro deck.
- **Pareamento:** a MESMA semente em todas as variantes de um lote; IC95% = 1,96·dp(diferença pareada)/√N. As métricas são **todos** os campos numéricos do resultado (listas/conjuntos/dicts viram o tamanho; campos `*_turn` viram indicadores "nunca"/"até T3..T6"), então a tabela mostra tudo que a correção moveu, sem escolher o que olhar. Na tabela aparecem os campos de destaque do `config.json` e os 14 mais movidos (`*` = |dif| > IC95%).
- **Sementes:** A/B N=2.000 → `1_000_000+i`; A/B N=10.000 → `3_000_000+i`; regressão e bit-identidade → `5_000_000+i`. 8 turnos. Dois modos: `padrao` (`simulate_one`) e `resiliencia` (`simulate_one_with_interaction`).
- **Variantes:** `antes` (snapshot), `depois` (arquivo vivo, todas as chaves ligadas) e as de sensibilidade (uma correção por vez): `so_mulligan` (define COMMANDER_TAX_ENABLED=False, DETERMINISTIC_SET_ORDER_ENABLED=False; o resto do arquivo vivo fica como está), `so_imposto` (define MULLIGAN_SMART_BOTTOM_ENABLED=False, DETERMINISTIC_SET_ORDER_ENABLED=False; o resto do arquivo vivo fica como está), `so_ordem_set` (define MULLIGAN_SMART_BOTTOM_ENABLED=False, COMMANDER_TAX_ENABLED=False; o resto do arquivo vivo fica como está).
- **Bit-identidade:** impressão digital (sha1 do resultado inteiro, campo a campo, conjuntos ordenados) do arquivo vivo com as chaves DESLIGADAS × snapshot; N=20.000 por modo. Campos novos ignorados (o snapshot não os tem): ['commander_cast_count'].
- **Regressão:** 20.000 partidas × 2 modos × 2 configurações (`depois` e `chave_desligada`): exceções + invariantes genéricas (carta acima do número no baralho em alguma zona; contadores negativos).
- **Testes dirigidos:** `orquestracao/testes_dirigidos.py` (13/13 passaram; saída em `resumos/testes_dirigidos.txt`).
- **Formato dos brutos:** `dados/raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"fp":[impressão por partida],"campos":{campo:[valor por semente]}}}}` (`xz -9`; `abgen.carregar_raw` lê).

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela do log que o usa |
|---|---|---|---|---|
| `dados/raw_ab_2000.json.xz` | variantes antes/depois/sensibilidade, N=2.000, modo padrão | `orquestracao/driver.py ab` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | idem, N=10.000, modo padrão | `driver.py ab` | usado | `resumos/ab_10000.txt` (log: tabela principal) |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, N=2.000, modo resiliência | `driver.py ab` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, N=10.000, modo resiliência | `driver.py ab` | usado | `resumos/ab_10000_resiliencia.txt` (log: tabela da resiliência) |
| `resumos/smoke.txt` | biblioteca (99 cartas, 0 desconhecidas/duplicadas) + 200 partidas × 2 modos, vivo e snapshot | `driver.py smoke` | verificação | log: validação |
| `resumos/bitident_20000.txt` | chaves desligadas == snapshot, 20.000 × 2 modos | `driver.py bitid` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 × 2 modos × 2 configurações, 0 exceções | `driver.py reg` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | testes dirigidos da correção | `orquestracao/testes_dirigidos.py` | verificação | log: validação |
| `resumos/determinismo.txt` | mesma semente, 3 `PYTHONHASHSEED` (11, 22, 33), 1.500 sementes × 2 modos: controle (chave desligada) × correção, estado final campo a campo | `varredura-2026-10-05/scripts/det_check.sh` | verificação | log: determinismo |
| `resumos/log_driver.txt` | saída completa do `driver.py tudo` | `driver.py tudo` | registro | — |
| `resumos/indice_dados.md` | índice dos brutos (variantes, N, campos) | `indice_dados.py` | índice | — |
| `resumos/verificacao_reproducao.txt` | saída do `verificar_reproducao.sh --tudo` | `orquestracao/verificar_reproducao.sh` | verificação | abaixo |
| `codigo/heibai_goldfish_v1_ANTES_67ac5f4.py` | o simulador ANTES da correção (o "antes" do A/B) | — | referência | — |

## Mapa: tabela → comando que a reproduz

| resumo salvo (`resumos/`) | comando (de dentro de `orquestracao/`) |
|---|---|
| `ab_2000.txt`, `ab_10000.txt`, `ab_2000_resiliencia.txt`, `ab_10000_resiliencia.txt` | `DRIVER_OUT=/tmp/x python3 driver.py config.json sum` (só dos brutos arquivados) |
| `smoke.txt`, `bitident_20000.txt`, `regressao_20000.txt` | `DRIVER_OUT=/tmp/x python3 driver.py config.json smoke` / `bitid` / `reg` |
| os 4 lotes do A/B re-simulados | `DRIVER_OUT=/tmp/x python3 driver.py config.json ab` |
| `testes_dirigidos.txt` | `python3 testes_dirigidos.py` |

## Reprodutibilidade (verificada ANTES de declarar arquivado)

```
IGUAL  ab_2000.txt
IGUAL  ab_10000.txt
IGUAL  ab_2000_resiliencia.txt
IGUAL  ab_10000_resiliencia.txt
IGUAL  smoke.txt
IGUAL  bitident_20000.txt
IGUAL  regressao_20000.txt
IGUAL  ab_2000.txt (re-execucao)
IGUAL  raw_ab_2000.json.xz (bruto re-simulado identico)
IGUAL  ab_10000.txt (re-execucao)
IGUAL  raw_ab_10000.json.xz (bruto re-simulado identico)
IGUAL  ab_2000_resiliencia.txt (re-execucao)
IGUAL  raw_ab_2000_resiliencia.json.xz (bruto re-simulado identico)
IGUAL  ab_10000_resiliencia.txt (re-execucao)
IGUAL  raw_ab_10000_resiliencia.json.xz (bruto re-simulado identico)
15/15 saidas byte a byte iguais
```

## Escopo desta rodada

**Verificado (com método):**
- **Mulligan:** leitura de `mulligan` e `should_keep`; teste dirigido (M1–M8: escolha do fundo, conservação das cartas, caminho antigo com a chave desligada); A/B pareado 2.000 e 10.000 nos dois modos.
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.
- **Imposto:** testes dirigidos T1–T5 (1º cast sem taxa; 2º cast com +{2}; cast anulado conta; ordem de contagem; chave desligada = custo antigo).
- **Determinismo:** 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, controle (chave desligada) × correção (`resumos/determinismo.txt`); varredura estática (AST) de laços/compreensões sobre `set` nos 18 simuladores (`varredura-2026-10-05/`).

**NÃO verificado nesta rodada (ver o log do deck):**
- **Jogada de terreno virado em T1/T2 ("tapped-first")** e **condições de entrada dos terrenos** (checkland/fastland/slow/reveal): não são tratadas nesta seção; quando houver correção, ela tem seção própria.
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.

**Observação sobre a regressão:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.
