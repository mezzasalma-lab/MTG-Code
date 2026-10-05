# Resultados brutos — Terreno virado primeiro em T1/T2 e ordem determinística dos payoffs no Edgar Markov (2026-10-05)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Edgar Markov. As conclusões e as tabelas legíveis
estão em `edgar-markov-mardu/goldfish-log.md` (seção "Terreno virado primeiro em T1/T2 + ordem dos payoffs determinística (varredura de 2026-10-05)") e em `edgar-markov-mardu/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**
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

`edgar_markov_goldfish_v1.py` ganhou 2 chave(s) de correção, todas **ligadas** no arquivo vivo: `TAPPED_LAND_FIRST_ENABLED`, `DETERMINISTIC_SET_ORDER_ENABLED`. Com todas desligadas o simulador é **bit-idêntico** ao snapshot `codigo/edgar_markov_goldfish_v1_ANTES_0c92480.py` (`resumos/bitident_20000.txt`).

- `TAPPED_LAND_FIRST_ENABLED` (padrão `True`), `TAPPED_LAND_FIRST_MAX_TURN = 2`: em T1..T2, havendo terreno virado E desvirado na mão, `tapped_first_pick` joga o virado, **salvo se isso custar desenvolvimento**: o teste é um ENSAIO a seco da própria fase de conjuração pré-combate do deck (cópia profunda do estado; `CARD_DB` compartilhado; RNG do estado copiado; `random` global restaurado), comparando o MV total das cartas que saem da mão com cada candidato. Empate → o virado. Dentro de cada grupo vale a ordem própria do deck (cor mais escassa etc.). Contadores novos no estado: `tapped_land_first_plays_total` (jogou o virado) e `tapped_land_skipped_for_play_total` (o ensaio mostrou que custaria uma jogada e jogou o desvirado). `TAPPED_LAND_FIRST_GHOST` só existe pra validação (roda o ensaio e ignora o resultado). Com a chave em `False` o caminho antigo volta bit a bit.
- `DETERMINISTIC_SET_ORDER_ENABLED` (padrão `True`): `for payoff in DEATH_PAYOFF_FORMULAS` (dict, ordem de declaração) no lugar de iterar `DEATH_PAYOFFS` (set). Com a chave em `False` o laço antigo (ordem do hash) volta.

O snapshot `codigo/edgar_markov_goldfish_v1_ANTES_0c92480.py` é o simulador **como estava no commit `0c92480`**, imediatamente antes desta rodada, e é o que o "antes" do A/B executa.
Código desta pasta: o commit que a adiciona (`git log -1 -- edgar-markov-mardu/resultados-ab/2026-10-05-terreno-virado-primeiro`).

## Como os dados foram gerados

- **Simulador / driver:** `orquestracao/driver.py` (genérico, lê `orquestracao/config.json`) + `orquestracao/abgen.py` (A/B pareado, impressão digital, regressão). `edgar_markov_goldfish_v1.py` lê `lista.md` do diretório do deck no `import`; o driver faz `chdir` pro deck.
- **Pareamento:** a MESMA semente em todas as variantes de um lote; IC95% = 1,96·dp(diferença pareada)/√N. As métricas são **todos** os campos numéricos do resultado (listas/conjuntos/dicts viram o tamanho; campos `*_turn` viram indicadores "nunca"/"até T3..T6"), então a tabela mostra tudo que a correção moveu, sem escolher o que olhar. Na tabela aparecem os campos de destaque do `config.json` e os 14 mais movidos (`*` = |dif| > IC95%).
- **Sementes:** A/B N=2.000 → `1_000_000+i`; A/B N=10.000 → `3_000_000+i`; regressão e bit-identidade → `5_000_000+i`. 8 turnos. Dois modos: `padrao` (`simulate_one`) e `resiliencia` (`simulate_one_with_interaction`).
- **`PYTHONHASHSEED=0`:** `driver.py` se reexecuta com o hash fixo (o `set` de `str` itera em ordem de hash, que muda a cada processo). Com isso até um snapshot antigo (que ainda dependa da ordem do hash) reproduz byte a byte em outro processo; os workers do `multiprocessing` herdam.
- **Variantes:** `antes` (snapshot), `depois` (arquivo vivo, todas as chaves ligadas) e as de sensibilidade (uma correção por vez): `so_terreno` (define DETERMINISTIC_SET_ORDER_ENABLED=False; o resto do arquivo vivo fica como está), `so_ordem_set` (define TAPPED_LAND_FIRST_ENABLED=False; o resto do arquivo vivo fica como está).
- **Bit-identidade:** impressão digital (sha1 do resultado inteiro, campo a campo, conjuntos ordenados) do arquivo vivo com as chaves DESLIGADAS × snapshot; N=20.000 por modo. Campos novos ignorados (o snapshot não os tem): ['tapped_land_first_plays_total', 'tapped_land_skipped_for_play_total'].
- **Ghost (validação do ensaio a seco):** a correção roda um ENSAIO da própria fase de conjuração numa cópia profunda do estado. Para provar que o ensaio não tem efeito colateral, o arquivo vivo com a chave ligada + `TAPPED_LAND_FIRST_GHOST=True` (roda o ensaio e ignora o resultado) é comparado ao arquivo vivo com tudo desligado: N=20.000 por modo, impressão digital do resultado inteiro.
- **Regressão:** 20.000 partidas × 2 modos × 2 configurações (`depois` e `chave_desligada`): exceções + invariantes genéricas (carta acima do número no baralho em alguma zona; contadores negativos).
- **Testes dirigidos:** `orquestracao/testes_dirigidos.py` (8/8 passaram; saída em `resumos/testes_dirigidos.txt`).
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
| `resumos/ghost_20000.txt` | chave ligada + modo GHOST (o ensaio roda, o resultado é ignorado) == tudo desligado, 20.000 × 2 modos | `driver.py ghost` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 × 2 modos × 2 configurações, 0 exceções | `driver.py reg` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | testes dirigidos da correção | `orquestracao/testes_dirigidos.py` | verificação | log: validação |
| `resumos/determinismo.txt` | mesma semente, 3 `PYTHONHASHSEED` (11, 22, 33), 1.500 sementes × 2 modos: controle (chave desligada) × correção, estado final campo a campo | `varredura-2026-10-05/scripts/det_check.sh` | verificação | log: determinismo |
| `resumos/log_driver.txt` | saída completa do `driver.py tudo` | `driver.py tudo` | registro | — |
| `resumos/indice_dados.md` | índice dos brutos (variantes, N, campos) | `indice_dados.py` | índice | — |
| `resumos/verificacao_reproducao.txt` | saída do `verificar_reproducao.sh --tudo` | `orquestracao/verificar_reproducao.sh` | verificação | abaixo |
| `codigo/edgar_markov_goldfish_v1_ANTES_0c92480.py` | o simulador ANTES da correção (o "antes" do A/B) | — | referência | — |

## Mapa: tabela → comando que a reproduz

| resumo salvo (`resumos/`) | comando (de dentro de `orquestracao/`) |
|---|---|
| `ab_2000.txt`, `ab_10000.txt`, `ab_2000_resiliencia.txt`, `ab_10000_resiliencia.txt` | `DRIVER_OUT=/tmp/x python3 driver.py config.json sum` (só dos brutos arquivados) |
| `smoke.txt`, `bitident_20000.txt`, `regressao_20000.txt` | `DRIVER_OUT=/tmp/x python3 driver.py config.json smoke` / `bitid` / `reg` |
| `ghost_20000.txt` | `DRIVER_OUT=/tmp/x python3 driver.py config.json ghost` |
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
IGUAL  ghost_20000.txt
IGUAL  regressao_20000.txt
IGUAL  ab_2000.txt (re-execucao)
IGUAL  raw_ab_2000.json.xz (bruto re-simulado identico)
IGUAL  ab_10000.txt (re-execucao)
IGUAL  raw_ab_10000.json.xz (bruto re-simulado identico)
IGUAL  ab_2000_resiliencia.txt (re-execucao)
IGUAL  raw_ab_2000_resiliencia.json.xz (bruto re-simulado identico)
IGUAL  ab_10000_resiliencia.txt (re-execucao)
IGUAL  raw_ab_10000_resiliencia.json.xz (bruto re-simulado identico)
16/16 saidas byte a byte iguais
```

## Notas do harness (correções feitas durante a rodada)

- **`abgen.py` (`tabela_pareada`):** os campos da tabela passaram a ser a UNIÃO dos campos de todas as partidas (antes: só os da partida 0). Um campo `Optional` que é `None` na partida 0 mas não nas outras ficava de fora da tabela calculada em memória, e aparecia na tabela refeita dos brutos (`sum`), porque `salvar_raw` grava a união. Achado na verificação de reprodutibilidade do Captain Storm (12/16 → refeito). A correção foi aplicada ao `abgen.py` desta pasta **depois** da bateria; a verificação final (`--tudo`) usa a versão corrigida e confirma que as tabelas salvas saem idênticas dos brutos.
- **`driver.py` (`smoke`):** simuladores baseados em dict (Edgar, Thranduil, Prismatic Bridge, Beorn) não têm `BASE_LIBRARY`; a contagem de cartas saía `0` (vácua). Agora cai em `parse_decklist(DECKLIST_TEXT)`. `smoke.txt` foi refeito com a versão corrigida (cartas=99, desconhecidas=[]).

## Escopo desta rodada

**Verificado (com método):**
- **Terreno virado primeiro:** leitura de `play_land` (+ predicado de entrada virada do deck); testes dirigidos TL1–TL8 (escolha com/sem jogada em T1, chave desligada, T3, só um tipo na mão, ensaio sem efeito no estado/RNG/`random`, modo GHOST, integração em `play_land`); A/B pareado 2.000 e 10.000 nos dois modos.
- **Ensaio sem efeito colateral:** com a chave ligada + modo GHOST (roda o ensaio e ignora o resultado) o resultado é idêntico a tudo desligado, 20.000 × 2 modos (`resumos/ghost_20000.txt`).
- **Bit-identidade** com as chaves desligadas × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro.
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.
- **Determinismo:** 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, controle × correção (`resumos/determinismo.txt`).
- **Invariante genérica "campos negativos" (regressão):** `mana_spent_this_turn` termina negativo em ~1,9% das partidas de resiliência (374/20.000 com a correção, 370/20.000 com ela desligada; 0 no modo padrão). Não é regressão nem bug de custo: o contador é a mana LÍQUIDA gasta e fica negativo por desenho quando sobra mana bônus no fim do turno (`try_cabal_coffers`: `-= sc-2`; Treasure criado e estalado: `-= count`; Ashnod's/Phyrexian Altar e Phyrexian Tower no `sac_loop`). Conferido em 1.200 partidas de resiliência: 22 terminaram negativas, 17 delas sem altar em campo; li o campo final de 2 delas (uma com Phyrexian Tower, outra com Cabal Coffers); as outras 20 não foram inspecionadas uma a uma.

**NÃO verificado nesta rodada (ver o log do deck):**
- **Condições de entrada dos terrenos** além do que a varredura mecânica cobriu (`varredura-2026-10-05/`: cenário de campo vazio + cenário condição satisfeita × violada para os padrões "unless you control …"/reveal; terrenos que o `CARD_DB` do deck não tem como básico foram pulados e estão listados lá).
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão e "whenever you cast", sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual das funções, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada. "Sem achado" aí significa "o `grep` não achou", não "não existe".
- **Oponente real:** o goldfish não modela (convenção do repositório); nada aqui mede interação além do proxy já existente.

**Observação sobre a regressão:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.
