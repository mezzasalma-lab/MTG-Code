# Resultados brutos — Conjurar/jogar de fora da mão no simulador do Vihaan (2026-10-03)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Correção do simulador: conjurar/jogar de fora da mão …") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**
Origem: as quatro primeiras lacunas saíram da análise da partida manual #1 (`../2026-10-03-partida-manual-1/`); a quinta (alvo da Sevinne's) saiu do invariante de validação da correção 2. O usuário tinha respondido *"Quero sim, sempre!"* à oferta de corrigir erros do simulador.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` (rápido, só lê os `.json.xz`); `--tudo` re-executa também smoke, testes, bit-identidade e regressão |
| abrir os brutos por partida em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta; o `LEIAME.md` e o próprio `SHA256SUMS` ficam de fora) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## O que foi alterado no simulador

Arquivo: `vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` (código anterior = commit `c04840d`, guardado em `codigo/vihaan_goldfish_v1_ANTES_c04840d.py`, idêntico ao `git show c04840d:…` por `cmp`; o código novo é o do commit que adiciona esta pasta:
`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-03-fora-da-mao`). **Uma chave por correção; com as cinco desligadas o arquivo é bit-idêntico ao anterior.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **Terreno do exílio** | `IMPULSE_LAND_PLAY_ENABLED` | `pull_impulse(lands_ok=)`, `play_impulse_land`, `play_land`, `play_from_impulse` | fontes *play* (Prosper, Inspired Tinkering, Face-Breaker) mandam o terreno exilado para `impulse_lands`; ele é a jogada de terreno (antes do da mão) + Pact Boon. Grenzo e Laughing Jasper Flint (*cast*) não |
| **Magia do exílio** | `IMPULSE_CAST_PIPELINE_ENABLED` | `play_from_impulse`, `cast_card(from_zone=)` | a magia do pool passa pela esteira de cast da mão: resolve, cemitério, conta, extort, Lotho; Pact Boon no cast. Antes: entrava como permanente parado |
| **Contagem de "spell cast"** | `SPELL_CAST_COUNT_ALL_PATHS_ENABLED` | `_lotho_second_spell`, `_register_nonhand_cast`, `cast_card`, `try_sevinne_flashback`, `do_cascade` | flashback e Cascade contam como magia; Lotho só dispara se já estava em campo no cast |
| **Storm** | `STORM_SACRIFICE_PUMP_ENABLED` | `_storm_pump`, `sacrifice_treasures`, `enter_battlefield`, `_combat_damage_proxy`, bloco do Cleaver | +1/+0 por Treasure sacrificado (os pagos pra conjurá-la não contam) no poder e no "that many" do Cleaver |
| **Alvo da Sevinne's** | `SEVINNE_PERMANENT_TARGET_ENABLED` | `_sevinne_return_one` (cast e flashback) | alvo = permanent card MV ≤3 (terreno sim; instantânea/feitiço e ela mesma não) |

## Oráculo e rulings lidos antes de escrever o código (Regra #3)

`dados/oraculo_rulings_ao_vivo.json` é **cópia** do arquivo da partida manual (`../2026-10-03-partida-manual-1/dados/`), lido ao vivo no Scryfall em 2026-10-03 e **antes** do código desta rodada: oráculo + 70 rulings de 29 cartas. Os que decidem as correções: **Prosper** (*Pact Boon triggers whenever you play any cards from exile*, 2021-07-23), **Lotho** (*spells cast before Lotho count*, 2023-06-16), **Captain Lannery Storm** (o +1/+0 vale para qualquer sacrifício; os Treasures pagos para conjurá-la não, 2017-09-29), **Sevinne's Reclamation** (*a permanent card is an artifact, battle, creature, enchantment, land, or planeswalker card*, 2024-06-07; flashback exila sempre; a cópia não é "cast"), **Monologue Tax** (opponent only). Oráculo de Professional Face-Breaker, Laughing Jasper Flint, Inspired Tinkering, Rain of Riches e Life Insurance lido de `scryfall-cache/oracle-cache.json`.

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada): `antes` = commit `c04840d` · `land` · `cast` · `count` · `storm` · `sevinne` — cada correção sozinha · `todas` = as cinco (o simulador que fica no repositório). As demais chaves do Vihaan ficam como no repositório.
- **Lotes:** `2000` = sementes `1_000_000+i` · `10000` = sementes `3_000_000+i` · cada um em modo padrão e em modo resiliência (`FX_MODO=resiliencia`). 8 turnos. Regressão: sementes `5_000_000+i`. Bit-identidade: sementes `1_000_000+i`, 20.000 partidas.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`). Campos: `win_turn`, `treasures`, `table_dmg`, `drain`, `combat`, `creature_deaths`, `bonus_mana`, `life_gained`, `recursion`, `mana_t5`, `mana_t6`, `imp_lands` (terrenos do exílio jogados), `imp_spells` (magias do exílio conjuradas), `lotho` e `pact` (chamadas de `create_treasures` pela fonte "Lotho (2a magica)" e "Prosper Pact Boon": comparáveis entre ANTES e DEPOIS), `storm_pump` (bônus da Storm somado), `stuck` (instantâneas/feitiços parados no campo no fim), `pool_expirado`, `fp` (impressão digital do estado final).
- **Primeira versão do A/B descartada:** a primeira rodada do A/B tinha as colunas "Lotho gatilhos" e "Sevinne's devolveu não-permanente" lidas de contadores que o código antigo não tem (mostravam 0 no ANTES, enganoso). Foi apagada e refeita com as medidas comparáveis acima antes de qualquer conclusão; os `.json.xz` desta pasta são os da segunda rodada.
- **Colunas das tabelas:** `win<=8 pp` = vitória (proxy) até o T8; `Treasures` = criados; `dano mesa`/`combate`/`drain` = proxies agregados (nunca vida real de oponente); `mortes cria.` = mortes de criatura; `recursoes` = devoluções do cemitério; `mana T5/T6` = mana total após a jogada de terreno.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/vihaan_goldfish_v1_ANTES_c04840d.py` | simulador antes da correção | — | referência | variante `antes`, `bitident.py` |
| `dados/raw_ab_2000.json.xz` | 7 variantes × 2.000 partidas, sementes 1.000.000+, padrão | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 7 variantes × 10.000 partidas, sementes 3.000.000+, padrão | `fx_ab.py 10000` | **usado (tabela do log, "padrão")** | `resumos/ab_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, 2.000, resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, 10.000, resiliência | `FX_MODO=resiliencia fx_ab.py 10000` | **usado (tabela do log, entre parênteses)** | `resumos/ab_10000_resiliencia.txt` |
| `dados/oraculo_rulings_ao_vivo.json` | oráculo + 70 rulings de 29 cartas (cópia do arquivo da partida manual) | consulta direta à API | referência | checklist |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 37 testes dirigidos | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS com as 5 chaves desligadas × ANTES: 20.000 partidas × 2 modos, 0 diferentes | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 9 configurações/modos (180.000): 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh --tudo` | verificação | — |
| `orquestracao/lote.sh` | roda os 4 lotes do A/B e grava os resumos | — | usado | — |

Nenhum lote superado ou inválido nesta pasta (a 1ª versão descartada acima não foi arquivada).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` → ver `resumos/verificacao_reproducao.txt`: as 4 tabelas de A/B refeitas dos `.json.xz` e a **re-execução** do smoke, dos 37 testes, da bit-identidade de 20.000 partidas × 2 modos e da regressão de 180.000 partidas, tudo comparado com `cmp`. `sha256sum -c SHA256SUMS` passa.
Os arquivos dos lotes anteriores do Vihaan (`2026-10-03-sephiroth`, `2026-10-03-treasure-animado-e-mulligan`) foram ajustados em `orquestracao/fx_common.py`/`smoke.py` para **desligar as 5 chaves novas** e ignorar os campos novos do `GameState`, e reverificados contra o simulador vivo (resultado no `LEIAME.md` de cada um). A pasta `2026-10-03-partida-manual-1` usa um snapshot do código (`c04840d`) e não é afetada.
**Não conferido byte a byte:** a leitura do oráculo no Scryfall (guardada em `dados/oraculo_rulings_ao_vivo.json`, não refeita por `cmp`).

## O que NÃO foi verificado (Regra #7)

- Só foram varridos, neste arquivo, os 5 caminhos que movem carta de fora da mão (`cast_card`, `play_from_impulse`, `play_land`/`play_impulse_land`, `try_sevinne_flashback`, `do_cascade`), o filtro "permanent card" nos 2 pontos da Sevinne's e a Storm/Cleaver no combate. **Não** foi auditoria carta a carta.
- **Política de jogada não alterada:** a carta do exílio é jogada **depois** de tudo que dá para jogar da mão, embora expire; medido: 1,5 cartas não-terreno por jogo entram no pool e expiram sem ser jogadas (padrão, até o T8; ~1,0 na resiliência). É ordem de jogo, não regra.
- Lotho/Monologue Tax em 2ª mágica de **oponente** continuam 📊 (estado de oponente); a escolha do alvo da Sevinne's continua "maior MV" (heurística); wipes próprios por sacrifício, Sephiroth só conta mortes minhas, Xorn/Plunderer em lote: achados abertos das rodadas anteriores, não alterados.
- Nenhuma carta foi cortada ou adicionada à lista; o Commander Spellbook não foi consultado porque nada na lista mudou.

Terceira nota (rodada "Prosper e Mahadi", 2026-10-03): o simulador vivo ganhou mais duas chaves ligadas por padrão (`IMPULSE_EXPIRING_FIRST_ENABLED`, `TREASURE_SELF_OUTLET_FARM_ENABLED`; ver `../2026-10-03-exilio-primeiro-e-mahadi/LEIAME.md`). `orquestracao/fx_common.py` agora também as desliga e ignora os 3 campos novos do `GameState`. Reverificado: `bash orquestracao/verificar_reproducao.sh --tudo` → 8/8 byte a byte iguais. `SHA256SUMS` regenerado.

Nota (rodada "exílio sempre e Dictate", 2026-10-04): o simulador vivo ganhou mais duas chaves ligadas por padrão (`IMPULSE_ALL_FIRST_ENABLED`, `TREASURE_FARM_WITH_DICTATE_ENABLED`; ver `../2026-10-04-exilio-sempre-e-dictate/LEIAME.md`). `orquestracao/fx_common.py` agora também as desliga e ignora os 2 campos novos do `GameState`. Reverificado: `bash orquestracao/verificar_reproducao.sh --tudo` → 8/8 byte a byte iguais. `SHA256SUMS` regenerado.

## Nota de 2026-10-04 (9ª rodada: `../2026-10-04-wipes-proprios/`)

- **As 5 chaves novas** (wipes próprios: destruição fiel, Treasure virado, custo da Blasphemous Act, retenção; imposto do comandante) vêm **ligadas** no simulador vivo. O `orquestracao/fx_common.py` desta pasta as **desliga** (e inclui os 7 campos novos do `GameState` em `NOVOS`) pra continuar reproduzindo o simulador do commit dela.
- `verificar_reproducao.sh --tudo` depois da 9ª rodada: 8/8. `SHA256SUMS` regenerado.
