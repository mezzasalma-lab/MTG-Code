# Resultados brutos — Farm com Dictate limitado a até metade dos Treasures (2026-10-04)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Correção do simulador: farm com Dictate limitado a até metade dos Treasures") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**

Pedido do usuário (2 frases), transcrito sem reescrever:
> *"O contador foi erro de clique, era para duplicar o token. Eu sacrificaria até metade dos treasures para eliminar criaturas dos adversários"*

A 1ª é registro (o contador +1/+1 do Treasure 24DnlO5iG em T7 foi clique errado; ver `../2026-10-03-partida-manual-1/LEIAME.md`); a 2ª é o critério de reserva do sacrifício com o Dictate e virou chave do simulador.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` (rápido, só lê os `.json.xz`); `--tudo` re-executa também smoke, testes, bit-identidade, regressão e o destino do Prosper |
| abrir os brutos por partida em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta; o `LEIAME.md` e o próprio `SHA256SUMS` ficam de fora) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## O que foi alterado no simulador

Arquivo: `vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` (código anterior = commit `8e9ab6e`, guardado em `codigo/vihaan_goldfish_v1_ANTES_8e9ab6e.py`, idêntico ao `git show 8e9ab6e:…` por `cmp`; o código novo é o do commit que adiciona esta pasta:
`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-04-dictate-metade`). **Uma chave; com ela desligada o arquivo é bit-idêntico ao anterior.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **Reserva de "até metade"** | `TREASURE_FARM_DICTATE_HALF_RESERVE_ENABLED` | `farm_animated_treasures` | quando **só o Dictate** justifica o sacrifício (sem Mahadi nem Pitiless Plunderer em campo), sacrifica no máximo `estoque // 2` Treasures-criatura (arredonda pra baixo; nunca mais que os animados vivos). Com Mahadi/Plunderer continua sendo de todos os animados (a reposição devolve o Treasure). Nenhum campo novo no `GameState`. |

**Premissas minhas, não confirmadas pelo usuário:** (1) "metade dos treasures" = metade do **estoque inteiro** (animados + não animados), não só dos animados; (2) o teto não vale com Mahadi/Plunderer em campo.

## Oráculo e rulings lidos antes de escrever o código (Regra #3)

`dados/oraculo_rulings_ao_vivo.json` é **cópia** do arquivo da partida manual (lido ao vivo no Scryfall em 2026-10-03, antes do código desta rodada): oráculo + 70 rulings de 29 cartas. Os que decidem aqui: **Dictate of Erebos** (um gatilho por criatura que morre; o oponente escolhe o que sacrifica, ruling 2014-04-26) e **Treasure** (a habilidade `{T}, Sacrifice` é de mana e pode ser ativada sem nada para gastar). Nenhuma carta foi adicionada ou cortada.

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada): `antes` = commit `8e9ab6e` (Dictate sacrifica **todos** os animados) · `metade` = a chave nova ligada (é o que fica no repositório) · `sem` = sensibilidade: farm com Dictate desligado (`TREASURE_FARM_WITH_DICTATE_ENABLED = False`, a regra da 5ª rodada: só Mahadi/Plunderer sacrificam), como referência do custo total. As demais chaves do Vihaan ficam como no repositório.
- **Lotes:** `2000` = sementes `1_000_000+i` · `10000` = sementes `3_000_000+i` · cada um em modo padrão e em modo resiliência (`FX_MODO=resiliencia`). 8 turnos. Regressão: sementes `5_000_000+i`. Bit-identidade: sementes `1_000_000+i`, 20.000 partidas.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`). Campos: `win_turn`, `treasures` (criados), `tend` (estoque no fim), `table_dmg`, `drain`, `combat`, `creature_deaths`, `bonus_mana` e os contadores diretos (`farm`, `farm_dic`, `dictate`, `mahadi`, `first`, …); lista completa em `resumos/indice_dados.md`. `--sum` refaz as tabelas só dos brutos.
- **Leitura das tabelas:** "Treasures criados" superestima o ganho líquido com Mahadi/Plunderer (reposição); use **estoque no fim**. `Dictate (gat.)` × 3 oponentes = proxy de criaturas de oponente forçadas a sacrificar (📊: o simulador não modela o campo do oponente).
- **Destino do Prosper** (`orquestracao/prosper_destino.py`): para cada carta que o Prosper exila no end step, se foi jogada, conjurada, expirou ou ainda era válida no fim. `FX_SIM=` aponta o simulador (snapshot `8e9ab6e` para o "antes"). Resultado: **praticamente inalterado** (mágica jogada 65,2% → 65,2%; terreno 67,8% → 67,8%), como esperado: a reserva não mexe no Prosper.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/vihaan_goldfish_v1_ANTES_8e9ab6e.py` | simulador antes da correção | — | referência | variante `antes`, `bitident.py`, `prosper_destino_antes_padrao.txt` |
| `dados/raw_ab_2000.json.xz` | 3 variantes × 2.000 partidas, sementes 1.000.000+, padrão | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 3 variantes × 10.000 partidas, sementes 3.000.000+, padrão | `fx_ab.py 10000` | **usado (tabela do log, "padrão")** | `resumos/ab_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, 2.000, resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, 10.000, resiliência | `FX_MODO=resiliencia fx_ab.py 10000` | **usado (tabela do log, entre parênteses)** | `resumos/ab_10000_resiliencia.txt` |
| `dados/oraculo_rulings_ao_vivo.json` | oráculo + 70 rulings de 29 cartas (cópia do arquivo da partida manual) | consulta direta à API | referência | checklist |
| `resumos/prosper_destino_antes_padrao.txt` / `_depois_padrao.txt` | destino de cada carta exilada pelo Prosper (N=10.000, padrão) | `prosper_destino.py` | usado (confirma que o Prosper não mudou) | log |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 17 testes dirigidos (H1–H15 + 2 invariantes de 1.500 jogos) | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS com a chave desligada × ANTES: 20.000 partidas × 2 modos, 0 diferentes | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 6 configurações/modos (`metade`/`tudo`/`sem` × padrão/resiliência = 120.000): 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh --tudo` | verificação | — |
| `orquestracao/lote.sh` | roda os 4 lotes do A/B e grava os resumos | — | usado | — |

Nenhum lote superado ou inválido nesta pasta.

**Comandos que reproduzem cada tabela** (de dentro de `orquestracao/`): `python3 fx_ab.py 2000 --sum` → `ab_2000.txt` · `python3 fx_ab.py 10000 --sum` → `ab_10000.txt` · `FX_MODO=resiliencia python3 fx_ab.py {2000,10000} --sum` → `ab_*_resiliencia.txt` · `python3 smoke.py` · `python3 testes_dirigidos.py` · `python3 bitident.py 20000 1000000` · `python3 fx_regressao.py 20000` · `FX_SIM=../codigo/vihaan_goldfish_v1_ANTES_8e9ab6e.py python3 prosper_destino.py 10000 3000000` (antes) e sem `FX_SIM` (depois).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` → **10/10 saídas byte a byte iguais** (`cmp`; `resumos/verificacao_reproducao.txt`): as 4 tabelas do A/B refeitas dos `.json.xz` e a **re-execução** do smoke, dos 17 testes, da bit-identidade de 20.000 partidas × 2 modos, da regressão (120.000 partidas) e do destino do Prosper (antes e depois).
**Os 8 arquivos anteriores do Vihaan foram reverificados com `--tudo` contra o simulador vivo (com a chave nova ligada por padrão) depois desta correção:** `exilio-primeiro-e-mahadi` 10/10, `fora-da-mao` 8/8, `sephiroth` 11/11, `treasure-animado-e-mulligan` 7/7, `kingpin` 11/11, `inevitable-defeat` 6/6, `partida-manual-1` 7/7 (esses 7 não precisaram de ajuste: ou desligam o farm com Dictate ou não o exercitam, e a chave nova só age quando ele está ligado) e `exilio-sempre-e-dictate` **9/10 na 1ª execução**: o `prosper_destino_depois_padrao.txt` diferia em 3 contagens de 4.634 exílios (jogada 1.108 → 1.109 de terreno, 1.955 → 1.954 de mágica, 991 → 990 válida no fim), porque o `prosper_destino.py` dessa pasta carregava o simulador vivo **sem passar por `F.flags`**, isto é, com a chave nova ligada. Corrigi o script (`V = F.flags(F.carrega(...))`, o `fx_common.py` dela já desliga a chave nova) e os dois resumos do Prosper dessa pasta, antes e depois, voltaram a bater por `cmp`; as outras 9 saídas já tinham dado IGUAL na mesma execução (não repeti o `--tudo` inteiro depois do ajuste, só os dois `cmp` do Prosper). Os `SHA256SUMS` de `exilio-sempre-e-dictate` foram regenerados (2 arquivos ajustados: `orquestracao/fx_common.py` e `orquestracao/prosper_destino.py`) e o `LEIAME.md` dela ganhou uma nota.
**Não conferido byte a byte:** a leitura do oráculo no Scryfall (guardada em `dados/oraculo_rulings_ao_vivo.json`, não refeita por `cmp`).

## O que NÃO foi verificado (Regra #7)

- Só foi varrido, neste arquivo, `farm_animated_treasures` (a regra do teto e a posição da chamada em `play_turn`). **Não** foi auditoria carta a carta.
- O **valor** dos sacrifícios do Dictate no oponente é 📊 (só se conta o uso: `dictate_triggers_total` × 3 oponentes). O simulador sacrifica **exatamente o teto** (`estoque // 2`) quando há animados suficientes; uma jogada real sacrifica o que o campo do oponente pede.
- As duas premissas acima ("metade" do estoque inteiro; teto não vale com Mahadi/Plunderer) não foram confirmadas pelo usuário.
- Lotho/Monologue Tax em 2ª mágica de **oponente** continuam 📊. Sem resposta: a cópia da Sevinne's no T8 e a Blood Money que expirou no T8.
- Nenhuma carta foi cortada ou adicionada à lista; o Commander Spellbook não foi consultado porque nada na lista mudou.
