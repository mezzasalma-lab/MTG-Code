# Resultados brutos — Exílio do Prosper expirando primeiro e Treasure animado com Mahadi (2026-10-03)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Correção do simulador: exílio do Prosper expirando primeiro e Treasure animado com Mahadi") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**
Pedido do usuário: *"Corrija o efeito do Prosper, a melhor parte dele é jogar terreno do exílio e criar um tesouro! Além disso quando castei o Dictate eu usei tesouros já criaturas para ativar o Machado mais vezes!"* — lido como **Machado = Mahadi** (autocorretor; o contexto é o das mortes que o Mahadi conta). As respostas do usuário à análise da partida estão em `../2026-10-03-partida-manual-1/LEIAME.md`.

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

Arquivo: `vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` (código anterior = commit `7cd3f55`, guardado em `codigo/vihaan_goldfish_v1_ANTES_7cd3f55.py`, idêntico ao `git show 7cd3f55:…` por `cmp`; o código novo é o do commit que adiciona esta pasta:
`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-03-exilio-primeiro-e-mahadi`). **Uma chave por correção; com as duas desligadas o arquivo é bit-idêntico ao anterior.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **Exílio expirando primeiro** | `IMPULSE_EXPIRING_FIRST_ENABLED` | `main_phase`, `play_from_impulse(expiring_only=)` | a carta do exílio com prazo = turno atual é conjurada antes das da mão (mais barata primeiro), pela esteira de cast, com Pact Boon; as que podem esperar continuam depois da mão |
| **Treasure animado como saída própria** | `TREASURE_SELF_OUTLET_FARM_ENABLED` | `farm_animated_treasures`, `play_turn` | com Mahadi ou Pitiless Plunderer em campo, sacrifica no fim da 2ª main todos os Treasures animados que sobraram (mana ability do próprio Treasure), sem exceder os animados |
| (sem chave, só leitura) **proxy do Dictate** | — | `on_creature_dies` | `dictate_triggers_total` conta as criaturas minhas que morrem com o Dictate em campo; o oponente nunca sacrifica nada (📊) |

## Oráculo e rulings lidos antes de escrever o código (Regra #3)

`dados/oraculo_rulings_ao_vivo.json` é **cópia** do arquivo da partida manual, lido ao vivo no Scryfall em 2026-10-03 antes do código desta rodada. Os que decidem: **Prosper** (*play that card*; Pact Boon em qualquer carta jogada do exílio, 2021-07-23), **Vihaan** (os Treasures mantêm as habilidades enquanto são criaturas, 2024-04-12), **Mahadi** (sem rulings; conta criaturas mortas no turno), **Pitiless Plunderer** (dispara para cada outra criatura que morre junto, 2018-01-19), **Captain Lannery Storm** (*"You can activate the mana ability of a Treasure even if you have nothing to spend that mana on"*, 2017-09-29: é o que torna o Treasure uma saída de sacrifício sem nada pra gastar), **Dictate of Erebos** (um gatilho por criatura; o oponente escolhe, 2014-04-26).

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada): `antes` = commit `7cd3f55` · `first` · `farm` — cada correção sozinha · `todas` = as duas (o simulador que fica no repositório). As demais chaves do Vihaan (inclusive as cinco de "fora da mão") ficam como no repositório.
- **Lotes:** `2000` = sementes `1_000_000+i` · `10000` = sementes `3_000_000+i` · cada um em modo padrão e em modo resiliência (`FX_MODO=resiliencia`). 8 turnos. Regressão: sementes `5_000_000+i`. Bit-identidade: sementes `1_000_000+i`, 20.000 partidas.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`). Campos: `win_turn`, `treasures` (criados), `tend` (**estoque** de Treasures no fim), `table_dmg`, `drain`, `combat`, `creature_deaths`, `bonus_mana`, `life_gained`, `recursion`, `mana_t5`, `mana_t6`, `imp_spells`, `pact` (chamadas de Pact Boon), `first`, `farm`, `mahadi` e `mahadi_n` (chamadas e quantidade pedida pelo Mahadi), `plund_n`, `dictate` (-1 no ANTES: não existia), `pool_expirado`, `fp`.
- **"Treasures criados" × "estoque no fim":** com Mahadi/Plunderer o Treasure sacrificado volta como um Treasure novo, então "criados" sobe mais do que o estoque; o ganho líquido é `tend`.
- **Primeira versão do A/B descartada:** a 1ª rodada do A/B não tinha o estoque no fim nem a quantidade por fonte (só chamadas), o que faria "Treasures criados" parecer um ganho líquido. Foi apagada e refeita antes de qualquer conclusão; os `.json.xz` desta pasta são os da 2ª rodada.
- **Destino do Prosper** (`orquestracao/prosper_destino.py`): para cada carta que o Prosper exila no end step, se foi jogada (terreno), conjurada (mágica), expirou sem uso ou ainda era válida no fim; só as que já tiveram a sua vez entram nas porcentagens. `FX_SIM=` aponta o simulador (o do snapshot `7cd3f55` para o "antes").

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/vihaan_goldfish_v1_ANTES_7cd3f55.py` | simulador antes da correção | — | referência | variante `antes`, `bitident.py`, `prosper_destino_antes_padrao.txt` |
| `dados/raw_ab_2000.json.xz` | 4 variantes × 2.000 partidas, sementes 1.000.000+, padrão | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 4 variantes × 10.000 partidas, sementes 3.000.000+, padrão | `fx_ab.py 10000` | **usado (tabela do log, "padrão")** | `resumos/ab_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, 2.000, resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, 10.000, resiliência | `FX_MODO=resiliencia fx_ab.py 10000` | **usado (tabela do log, entre parênteses)** | `resumos/ab_10000_resiliencia.txt` |
| `dados/oraculo_rulings_ao_vivo.json` | oráculo + 70 rulings de 29 cartas (cópia do arquivo da partida manual) | consulta direta à API | referência | checklist |
| `resumos/prosper_destino_antes_padrao.txt` / `_depois_padrao.txt` | destino de cada carta exilada pelo Prosper (N=10.000, padrão), antes e depois | `prosper_destino.py` | **usado (tabela do log)** | log: "Destino das cartas que o Prosper exila" |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 17 testes dirigidos | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS com as 2 chaves desligadas × ANTES: 20.000 partidas × 2 modos, 0 diferentes | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 7 configurações/modos (140.000): 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh --tudo` | verificação | — |
| `orquestracao/lote.sh` | roda os 4 lotes do A/B e grava os resumos | — | usado | — |

Nenhum lote superado ou inválido nesta pasta (a 1ª versão descartada acima não foi arquivada).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` → **10/10 saídas byte a byte iguais** (`cmp`; `resumos/verificacao_reproducao.txt`): as 4 tabelas do A/B refeitas dos `.json.xz` e a **re-execução** do smoke, dos 17 testes, da bit-identidade de 20.000 partidas × 2 modos, da regressão de 140.000 partidas e do destino do Prosper antes e depois. `sha256sum -c SHA256SUMS` passa.
Os arquivos dos lotes anteriores do Vihaan (`2026-10-03-fora-da-mao`, `2026-10-03-sephiroth`, `2026-10-03-treasure-animado-e-mulligan`) tiveram o `orquestracao/fx_common.py` ajustado para **desligar as 2 chaves novas** e ignorar os 3 campos novos do `GameState` (e `smoke.py` do `fora-da-mao` passou a carregar por `F.flags`), e foram reverificados contra o simulador vivo: 8/8, 11/11 e 7/7. `2026-10-03-kingpin` (11/11), `2026-10-03-inevitable-defeat` (6/6) e `2026-10-03-partida-manual-1` (7/7, usa snapshot de código) reverificados sem ajuste.
**Não conferido byte a byte:** a leitura do oráculo no Scryfall (guardada em `dados/oraculo_rulings_ao_vivo.json`, não refeita por `cmp`).

## O que NÃO foi verificado (Regra #7)

- Só foram varridos, neste arquivo, o início de `main_phase` (ordem exílio × mão), `play_from_impulse`, o fim da 2ª main (`farm_animated_treasures`) e `on_creature_dies` (proxy do Dictate). **Não** foi auditoria carta a carta.
- **Farm sem Mahadi/Plunderer** não é feito (custaria 1 Treasure por morte: decisão de valor). O farm assume que o Mahadi/Plunderer continuam em campo até o end step (o simulador não tem remoção em resposta ali) e desperdiça a mana desses Treasures (esvazia).
- **Dictate** segue 📊: o oponente nunca sacrifica nada; só se conta o uso. Lotho/Monologue Tax em 2ª mágica de **oponente** continuam 📊.
- **A leitura de "Machado" como Mahadi** é minha; se o usuário quis dizer o Reaver Cleaver, esta correção do farm não é a que ele pediu.
- Nenhuma carta foi cortada ou adicionada à lista; o Commander Spellbook não foi consultado porque nada na lista mudou.
