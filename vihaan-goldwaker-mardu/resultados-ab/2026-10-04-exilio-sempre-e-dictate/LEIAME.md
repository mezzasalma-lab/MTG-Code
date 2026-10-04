# Resultados brutos — Exílio sempre primeiro e farm de Treasure animado também com Dictate (2026-10-04)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Correção do simulador: exílio sempre primeiro e farm de Treasure animado também com Dictate") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**
Pedido do usuário (3 frases): *"T7 foi erro meu. Prefiro sempre jogar o spell exilado para criar mais tesouros. O dictate é mais vantagem, eu sacrifico tesouros animados e todos os oponentes sacrificam criaturas."* A 1ª é registro (ver `../2026-10-03-partida-manual-1/LEIAME.md`); a 2ª e a 3ª são **preferências de jogo** que viraram chaves do simulador.

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

Arquivo: `vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` (código anterior = commit `ba594c8`, guardado em `codigo/vihaan_goldfish_v1_ANTES_ba594c8.py`, idêntico ao `git show ba594c8:…` por `cmp`; o código novo é o do commit que adiciona esta pasta:
`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-04-exilio-sempre-e-dictate`). **Uma chave por correção; com as duas desligadas o arquivo é bit-idêntico ao anterior.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **Exílio sempre primeiro** | `IMPULSE_ALL_FIRST_ENABLED` | início e laço de `main_phase`, `play_from_impulse` | **toda** carta do exílio (não só as que expiram neste turno) é conjurada antes das da mão, a mais barata primeiro; inclui as recém-exiladas no meio do main (Inspired Tinkering). O comandante continua primeiro |
| **Farm também com Dictate** | `TREASURE_FARM_WITH_DICTATE_ENABLED` | `farm_animated_treasures` | Dictate of Erebos em campo também aciona o sacrifício dos Treasures animados, mesmo sem Mahadi/Plunderer (custa 1 Treasure por morte sem reposição; `treasure_farm_dictate_total` conta quantos foram só por causa do Dictate) |

## Oráculo e rulings lidos antes de escrever o código (Regra #3)

`dados/oraculo_rulings_ao_vivo.json` é **cópia** do arquivo da partida manual (lido ao vivo no Scryfall em 2026-10-03, antes do código desta rodada): oráculo + 70 rulings de 29 cartas. Os que decidem: **Prosper** (Pact Boon em qualquer carta jogada do exílio, 2021-07-23), **Dictate of Erebos** (um gatilho por criatura que morre; o oponente escolhe qual criatura sacrifica, 2014-04-26), **Vihaan** (os Treasures mantêm as habilidades enquanto são criaturas, 2024-04-12). Inspired Tinkering (*play those cards*, até o fim do próximo turno): oráculo de `scryfall-cache/oracle-cache.json`.

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada): `antes` = commit `ba594c8` · `todo` (exílio sempre primeiro) · `dictate` (farm com Dictate) — cada correção sozinha · `todas` = as duas. As demais chaves do Vihaan ficam como no repositório.
- **Lotes:** `2000` = sementes `1_000_000+i` · `10000` = sementes `3_000_000+i` · cada um em modo padrão e em modo resiliência (`FX_MODO=resiliencia`). 8 turnos. Regressão: sementes `5_000_000+i`. Bit-identidade: sementes `1_000_000+i`, 20.000 partidas.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`). Campos: `win_turn`, `treasures` (criados), `tend` (estoque no fim), `table_dmg`, `drain`, `combat`, `creature_deaths`, `bonus_mana`, `mana_t5/t6`, `imp_spells`, `pact`, `first` (cartas do exílio jogadas antes da mão pela chave "sempre"), `farm`, `farm_dic` (animados sacrificados só por causa do Dictate), `mahadi_n`, `plund_n`, `dictate` (gatilhos do Dictate; ×3 oponentes = criaturas de oponente forçadas a sacrificar, proxy), `pool_expirado`, `fp`.
- **Falha do primeiro resumo (corrigida antes de qualquer conclusão):** a 1ª execução do `fx_ab.py` desta pasta imprimiu só a 1ª tabela de cada lote (erro de formatação do cabeçalho da 2ª, 11 valores para 10 colunas), **depois** de os brutos já estarem salvos. Corrigi a linha e regenerei as quatro tabelas dos mesmos brutos com `--sum`; nenhum dado foi resimulado.
- **Destino do Prosper** (`orquestracao/prosper_destino.py`): para cada carta que o Prosper exila no end step, se foi jogada, conjurada, expirou ou ainda era válida no fim (só as que já tiveram a vez entram nas porcentagens). `FX_SIM=` aponta o simulador (snapshot `ba594c8` para o "antes").

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/vihaan_goldfish_v1_ANTES_ba594c8.py` | simulador antes da correção | — | referência | variante `antes`, `bitident.py`, `prosper_destino_antes_padrao.txt` |
| `dados/raw_ab_2000.json.xz` | 4 variantes × 2.000 partidas, sementes 1.000.000+, padrão | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 4 variantes × 10.000 partidas, sementes 3.000.000+, padrão | `fx_ab.py 10000` | **usado (tabela do log, "padrão")** | `resumos/ab_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, 2.000, resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, 10.000, resiliência | `FX_MODO=resiliencia fx_ab.py 10000` | **usado (tabela do log, entre parênteses)** | `resumos/ab_10000_resiliencia.txt` |
| `dados/oraculo_rulings_ao_vivo.json` | oráculo + 70 rulings de 29 cartas (cópia do arquivo da partida manual) | consulta direta à API | referência | checklist |
| `resumos/prosper_destino_antes_padrao.txt` / `_depois_padrao.txt` | destino de cada carta exilada pelo Prosper (N=10.000, padrão) | `prosper_destino.py` | **usado (tabela do log)** | log: "Destino das cartas que o Prosper exila" |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 16 testes dirigidos | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS com as 2 chaves desligadas × ANTES: 20.000 partidas × 2 modos, 0 diferentes | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 7 configurações/modos (140.000): 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh --tudo` | verificação | — |
| `orquestracao/lote.sh` | roda os 4 lotes do A/B e grava os resumos | — | usado | — |

Nenhum lote superado ou inválido nesta pasta.

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` → **10/10 saídas byte a byte iguais** (`cmp`; `resumos/verificacao_reproducao.txt`): as 4 tabelas do A/B refeitas dos `.json.xz` e a **re-execução** do smoke, dos 16 testes, da bit-identidade de 20.000 partidas × 2 modos, da regressão de 140.000 partidas e do destino do Prosper antes e depois. `sha256sum -c SHA256SUMS` passa.
Os arquivos dos lotes anteriores do Vihaan (`2026-10-03-exilio-primeiro-e-mahadi`, `2026-10-03-fora-da-mao`, `2026-10-03-sephiroth`, `2026-10-03-treasure-animado-e-mulligan`) tiveram o `orquestracao/fx_common.py` ajustado para **desligar as 2 chaves novas** e ignorar os 2 campos novos do `GameState` (e o `prosper_destino.py`/`smoke.py` de `exilio-primeiro-e-mahadi` passaram a carregar por `F.flags`), e foram reverificados contra o simulador vivo: 10/10, 8/8, 11/11 e 7/7. `2026-10-03-kingpin` (11/11), `2026-10-03-inevitable-defeat` (6/6) e `2026-10-03-partida-manual-1` (7/7, usa snapshot de código) reverificados sem ajuste.
**Não conferido byte a byte:** a leitura do oráculo no Scryfall (guardada em `dados/oraculo_rulings_ao_vivo.json`, não refeita por `cmp`).

## O que NÃO foi verificado (Regra #7)

- Só foram varridos, neste arquivo, o início e o laço de `main_phase` (ordem exílio × mão), `play_from_impulse` e `farm_animated_treasures`. **Não** foi auditoria carta a carta.
- O **valor** dos sacrifícios do Dictate no oponente é 📊 (só se conta o uso: `dictate_triggers_total`). O simulador sacrifica **todos** os animados que sobram quando há Dictate; a sua T8 sacrificou 7 dos até 12 disponíveis, e o critério da reserva não dá pra inferir do log.
- Lotho/Monologue Tax em 2ª mágica de **oponente** continuam 📊. Sem resposta: o contador +1/+1 do Treasure no T7 e a cópia da Sevinne's no T8.
- Nenhuma carta foi cortada ou adicionada à lista; o Commander Spellbook não foi consultado porque nada na lista mudou.

## Nota de 2026-10-04 (7ª rodada: `../2026-10-04-dictate-metade/`)

- **Respondido pelo usuário:** o contador +1/+1 do Treasure no T7 foi **clique errado** (a intenção era duplicar o token); e o critério de reserva do Dictate é *"até metade dos treasures"* (virou a chave `TREASURE_FARM_DICTATE_HALF_RESERVE_ENABLED`, ligada por padrão no simulador vivo). As frases "Sem resposta: o contador +1/+1 do Treasure no T7" e "sacrifica todos os animados que sobram" acima descrevem o estado **daquela** rodada.
- **Esta pasta continua reproduzindo o simulador do commit dela**: `orquestracao/fx_common.py` desliga a chave nova e `orquestracao/prosper_destino.py` agora passa por `F.flags` (antes carregava o simulador vivo sem desligá-la e 3 contagens do `prosper_destino_depois_padrao.txt` diferiam). `verificar_reproducao.sh --tudo`: 9/10 na 1ª execução depois da 7ª rodada; os dois resumos do Prosper (antes e depois) conferidos por `cmp` depois do ajuste. `SHA256SUMS` regenerado.

## Nota de 2026-10-04 (9ª rodada: `../2026-10-04-wipes-proprios/`)

- **As 5 chaves novas** (wipes próprios: destruição fiel, Treasure virado, custo da Blasphemous Act, retenção; imposto do comandante) vêm **ligadas** no simulador vivo. O `orquestracao/fx_common.py` desta pasta as **desliga** (e inclui os 7 campos novos do `GameState` em `NOVOS`) pra continuar reproduzindo o simulador do commit dela.
- O `orquestracao/smoke.py` desta pasta carregava o simulador vivo **sem passar por `F.flags`** (as 200 partidas rodavam com as chaves novas ligadas e o `smoke.txt` deu `DIFERE` na 1ª execução); passou a usar `F.flags(F.carrega(...))` e o `cmp` voltou a bater.
- `verificar_reproducao.sh --tudo` depois da 9ª rodada: 10/10 depois de corrigir o smoke. `SHA256SUMS` regenerado.
