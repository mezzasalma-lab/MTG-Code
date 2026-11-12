# Resultados brutos — Landfall no terreno devolvido ao campo no Prismatic Bridge (2026-10-05)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck The Prismatic Bridge. As conclusões e as tabelas legíveis
estão em `prismatic-bridge-wurbg/goldfish-log.md` (seção "Landfall no terreno devolvido ao campo (varredura de 2026-10-05)") e em `prismatic-bridge-wurbg/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**
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

`prismatic_bridge_goldfish_v1.py` ganhou 1 chave(s) de correção, todas **ligadas** no arquivo vivo: `LAND_ENTER_TRIGGERS_ALL_ENABLED`. Com todas desligadas o simulador é **bit-idêntico** ao snapshot `codigo/prismatic_bridge_goldfish_v1_ANTES_2c2da70.py` (`resumos/bitident_20000.txt`).

- `LAND_ENTER_TRIGGERS_ALL_ENABLED` (padrão `True`): em `_return_to_battlefield`, terreno devolvido chama `on_land_enters` (Evolution Sage → `proliferate_loyalty`). Contadores novos na saída: `returned_land_landfall_total` e `evolution_sage_proliferates` (este já existia no estado, agora também no resultado). Com a chave em `False` o comportamento antigo volta bit a bit.

O snapshot `codigo/prismatic_bridge_goldfish_v1_ANTES_2c2da70.py` é o simulador **como estava no commit `2c2da70`**, imediatamente antes desta rodada, e é o que o "antes" do A/B executa.
Código desta pasta: o commit que a adiciona (`git log -1 -- prismatic-bridge-wurbg/resultados-ab/2026-10-05-landfall-terreno-devolvido`).

## Como os dados foram gerados

- **Simulador / driver:** `orquestracao/driver.py` (genérico, lê `orquestracao/config.json`) + `orquestracao/abgen.py` (A/B pareado, impressão digital, regressão). `prismatic_bridge_goldfish_v1.py` lê `lista.md` do diretório do deck no `import`; o driver faz `chdir` pro deck.
- **Pareamento:** a MESMA semente em todas as variantes de um lote; IC95% = 1,96·dp(diferença pareada)/√N. As métricas são **todos** os campos numéricos do resultado (listas/conjuntos/dicts viram o tamanho; campos `*_turn` viram indicadores "nunca"/"até T3..T6"), então a tabela mostra tudo que a correção moveu, sem escolher o que olhar. Na tabela aparecem os campos de destaque do `config.json` e os 14 mais movidos (`*` = |dif| > IC95%).
- **Sementes:** A/B N=2.000 → `1_000_000+i`; A/B N=10.000 → `3_000_000+i`; regressão e bit-identidade → `5_000_000+i`. 8 turnos. Dois modos: `padrao` (`simulate_one`) e `resiliencia` (`simulate_one_with_interaction`).
- **`PYTHONHASHSEED=0`:** `driver.py` se reexecuta com o hash fixo (o `set` de `str` itera em ordem de hash, que muda a cada processo). Com isso até um snapshot antigo (que ainda dependa da ordem do hash) reproduz byte a byte em outro processo; os workers do `multiprocessing` herdam.
- **Variantes:** `antes` (snapshot), `depois` (arquivo vivo, todas as chaves ligadas) e as de sensibilidade (uma correção por vez): (nenhuma).
- **Bit-identidade:** impressão digital (sha1 do resultado inteiro, campo a campo, conjuntos ordenados) do arquivo vivo com as chaves DESLIGADAS × snapshot; N=20.000 por modo. Campos novos ignorados (o snapshot não os tem): ['returned_land_landfall_total', 'evolution_sage_proliferates'].
- **Regressão:** 20.000 partidas × 2 modos × 2 configurações (`depois` e `chave_desligada`): exceções + invariantes genéricas (carta acima do número no baralho em alguma zona; contadores negativos).
- **Testes dirigidos:** `orquestracao/testes_dirigidos.py` (5/5 passaram; saída em `resumos/testes_dirigidos.txt`).
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
| `resumos/log_driver.txt` | saída completa do `driver.py tudo` | `driver.py tudo` | registro | — |
| `resumos/indice_dados.md` | índice dos brutos (variantes, N, campos) | `indice_dados.py` | índice | — |
| `resumos/verificacao_reproducao.txt` | saída do `verificar_reproducao.sh --tudo` | `orquestracao/verificar_reproducao.sh` | verificação | abaixo |
| `codigo/prismatic_bridge_goldfish_v1_ANTES_2c2da70.py` | o simulador ANTES da correção (o "antes" do A/B) | — | referência | — |

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

## Notas do harness (correções feitas durante a rodada)

- **`abgen.py` (`tabela_pareada`):** os campos da tabela passaram a ser a UNIÃO dos campos de todas as partidas (antes: só os da partida 0). Um campo `Optional` que é `None` na partida 0 mas não nas outras ficava de fora da tabela calculada em memória, e aparecia na tabela refeita dos brutos (`sum`), porque `salvar_raw` grava a união. Achado na verificação de reprodutibilidade do Captain Storm (12/16 → refeito). A correção foi aplicada ao `abgen.py` desta pasta **depois** da bateria; a verificação final (`--tudo`) usa a versão corrigida e confirma que as tabelas salvas saem idênticas dos brutos.
- **`abgen.py` (`numericos`):** inteiros astronômicos estouravam a conversão pra `float` (`OverflowError`) e derrubaram a 1ª bateria do Prismatic Bridge: `all_will_be_one_face_damage_total` chega a 10^17–10^212 em partidas com dobradores em loop (pré-existente, também no snapshot ANTES). Agora os inteiros são limitados a ±1e15 SÓ na hora de tirar a média da tabela; a impressão digital (bit-identidade) usa o valor exato. Esse campo, portanto, não é confiável na tabela do A/B.
- **`driver.py` (`smoke`):** simuladores baseados em dict (Edgar, Thranduil, Prismatic Bridge, Beorn) não têm `BASE_LIBRARY`; a contagem de cartas saía `0` (vácua). Agora cai em `parse_decklist(DECKLIST_TEXT)`. `smoke.txt` foi refeito com a versão corrigida (cartas=99, desconhecidas=[]).

## Escopo desta rodada

**Verificado (com método):**
- **Landfall:** varredura mecânica de entradas de terreno × chamadas da função de landfall em Beorn, PB, Maralen e Toph (300 partidas cada); testes dirigidos PF1–PF5 (proliferate com Evolution Sage, chave desligada, sem Evolution Sage, criatura devolvida não conta, 300 partidas por modo).
- **Bit-identidade** com a chave desligada × snapshot: 20.000 partidas × 2 modos (contadores novos ignorados).
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.

**NÃO verificado nesta rodada (ver o log do deck):**
- **Outros gatilhos de "a land enters"** além do landfall da Evolution Sage neste deck (a varredura de oráculo da lista só achou landfall em Evolution Sage e The World Tree, que não é gatilho de entrada).
- **Resto da taxonomia da Regra #1 neste arquivo:** `grep` e leitura pontual, sem leitura integral nem instrumentação em runtime nesta rodada.
- **Oponente real:** o goldfish não modela.

**Observação sobre a regressão:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos deram 0 violações.
