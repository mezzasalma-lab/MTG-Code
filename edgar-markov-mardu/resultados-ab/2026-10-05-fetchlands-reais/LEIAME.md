# Resultados brutos — Fetchlands reais no Edgar Markov (2026-10-05)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Edgar Markov. As conclusões e as tabelas legíveis
estão em `edgar-markov-mardu/goldfish-log.md` (seção "Fetchlands reais (varredura de 2026-10-05)") e em `edgar-markov-mardu/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**
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

`edgar_markov_goldfish_v1.py` ganhou 1 chave(s) de correção, todas **ligadas** no arquivo vivo: `FETCH_LANDS_ENABLED`. Com todas desligadas o simulador é **bit-idêntico** ao snapshot `codigo/edgar_markov_goldfish_v1_ANTES_fd34e07.py` (`resumos/bitident_20000.txt`).

- `FETCH_LANDS_ENABLED` (padrão `True`): ao jogar a fetch, `crack_fetch` a manda pro cemitério, paga 1 de vida e busca na biblioteca um terreno com subtipo compatível com o texto da fetch (básico OU dual tipada, por SUBTIPO do `type_line` do oráculo, não por nome); o terreno buscado entra em campo pelas regras de entrada do deck. Escolha: o terreno que cobre a cor ausente (W/B/R) e, por último, o que entra virado (Savai Triome). Sem alvo na biblioteca a fetch fica em campo como antes (contado em `fetch_no_target_total`). Contadores novos: `fetches_cracked_total`, `fetch_no_target_total`. Com a chave em `False` o caminho antigo volta bit a bit.
- **Sevinne's Reclamation devolve fetch:** a fetch que volta do cemitério pro campo (permanente de MV ≤ 3) também busca (oráculo: pode ser ativada assim que volta). Achado pelo próprio teste de integração (FT8): sem isso a fetch devolvida ficava em campo como dual.

O snapshot `codigo/edgar_markov_goldfish_v1_ANTES_fd34e07.py` é o simulador **como estava no commit `fd34e07`**, imediatamente antes desta rodada, e é o que o "antes" do A/B executa.
Código desta pasta: o commit que a adiciona (`git log -1 -- edgar-markov-mardu/resultados-ab/2026-10-05-fetchlands-reais`).

## Como os dados foram gerados

- **Simulador / driver:** `orquestracao/driver.py` (genérico, lê `orquestracao/config.json`) + `orquestracao/abgen.py` (A/B pareado, impressão digital, regressão). `edgar_markov_goldfish_v1.py` lê `lista.md` do diretório do deck no `import`; o driver faz `chdir` pro deck.
- **Pareamento:** a MESMA semente em todas as variantes de um lote; IC95% = 1,96·dp(diferença pareada)/√N. As métricas são **todos** os campos numéricos do resultado (listas/conjuntos/dicts viram o tamanho; campos `*_turn` viram indicadores "nunca"/"até T3..T6"), então a tabela mostra tudo que a correção moveu, sem escolher o que olhar. Na tabela aparecem os campos de destaque do `config.json` e os 14 mais movidos (`*` = |dif| > IC95%).
- **Sementes:** A/B N=2.000 → `1_000_000+i`; A/B N=10.000 → `3_000_000+i`; regressão e bit-identidade → `5_000_000+i`. 8 turnos. Dois modos: `padrao` (`simulate_one`) e `resiliencia` (`simulate_one_with_interaction`).
- **`PYTHONHASHSEED=0`:** `driver.py` se reexecuta com o hash fixo (o `set` de `str` itera em ordem de hash, que muda a cada processo). Com isso até um snapshot antigo (que ainda dependa da ordem do hash) reproduz byte a byte em outro processo; os workers do `multiprocessing` herdam.
- **Variantes:** `antes` (snapshot), `depois` (arquivo vivo, todas as chaves ligadas) e as de sensibilidade (uma correção por vez): (nenhuma).
- **Bit-identidade:** impressão digital (sha1 do resultado inteiro, campo a campo, conjuntos ordenados) do arquivo vivo com as chaves DESLIGADAS × snapshot; N=20.000 por modo. Campos novos ignorados (o snapshot não os tem): ['fetches_cracked_total', 'fetch_no_target_total'].
- **Regressão:** 20.000 partidas × 2 modos × 2 configurações (`depois` e `chave_desligada`): exceções + invariantes genéricas (carta acima do número no baralho em alguma zona; contadores negativos).
- **Testes dirigidos:** `orquestracao/testes_dirigidos.py` (9/9 passaram; saída em `resumos/testes_dirigidos.txt`).
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
| `codigo/edgar_markov_goldfish_v1_ANTES_fd34e07.py` | o simulador ANTES da correção (o "antes" do A/B) | — | referência | — |

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
- **`driver.py` (`smoke`):** simuladores baseados em dict (Edgar, Thranduil, Prismatic Bridge, Beorn) não têm `BASE_LIBRARY`; a contagem de cartas saía `0` (vácua). Agora cai em `parse_decklist(DECKLIST_TEXT)`. `smoke.txt` foi refeito com a versão corrigida (cartas=99, desconhecidas=[]).

## Escopo desta rodada

**Verificado (com método):**
- **Fetch real:** leitura de `play_land` (e do caminho de entrada de terreno) + testes dirigidos FT1–FT8 (a fetch vai pro cemitério, a biblioteca perde exatamente 1 carta, o buscado tem subtipo compatível — varre TODAS as fetches do deck —, custo de 1 de vida, sem alvo → fica em campo, escolhe o que entra desvirado, thinning, chave desligada = caminho antigo, 300 partidas completas por modo); A/B pareado 2.000 e 10.000 nos dois modos.
- **Bit-identidade** com a chave desligada × snapshot: 20.000 partidas × 2 modos, impressão digital do resultado inteiro (contadores novos ignorados).
- **Regressão** 20.000 × 2 modos × 2 configurações: 0 exceções.
- **Sevinne's Reclamation × fetch no cemitério:** teste dirigido FT9 e o efeito medido na tabela (`sevinnes_reclamation_returns` sobe porque o cemitério agora tem alvo MV 0).

**NÃO verificado nesta rodada (ver o log do deck):**
- **O "then shuffle" do oráculo NÃO é modelado:** o estado deste simulador não tem RNG próprio na biblioteca (a biblioteca já é uma permutação aleatória). Embaralhar de novo só mudaria algo se um tutor ou scry tivesse posto uma carta específica no topo entre a compra e a jogada de terreno; a ordem do turno impede isso nas linhas modeladas.
- **Landfall:** varri o `oracle_text` das cartas da lista procurando gatilhos de "whenever a land enters"/Landfall: neste deck nenhuma carta além dos terrenos tem esse gatilho, então o terreno buscado não deixa gatilho sem disparar.
- **Resto da taxonomia da Regra #1 neste arquivo** (caminhos de conjuração fora da mão, sacrifício × destroy, cascade, contadores `_sick` agregados, fórmulas dinâmicas achatadas): varrido na triagem de 2026-10-05 por `grep` e leitura pontual, **sem** leitura integral do arquivo e **sem** instrumentação em runtime nesta rodada.
- **Oponente real:** o goldfish não modela (convenção do repositório).

**Observação sobre a regressão:** 0 exceções em 20.000 × 2 modos × 2 configurações; os invariantes genéricos (carta acima do número no baralho; contadores negativos) deram 0 violações.
