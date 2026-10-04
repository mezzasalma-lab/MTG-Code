# Resultados brutos — Treasure animado, mulligan e terreno tapped no simulador do Vihaan (2026-10-03)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Correção do simulador: Treasure animado, mulligan e terreno tapped — 2026-10-03") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**
Pedido do usuário: *"Quer que eu corrija agora o roteamento do Treasure animado para todos os gatilhos de criatura? Isso move os números de base do Vihaan, então eu rodaria antes e depois." — "Quero sim, corrija todos os erros do simulador!"*

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` (rápido, só lê os `.json.xz`); `--tudo` re-executa também smoke, testes, bit-identidade e regressão |
| abrir os brutos por partida em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## O que foi alterado no simulador

Arquivo: `vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` (código anterior = último commit que o tocou, `6e623d3`, guardado em `codigo/vihaan_goldfish_v1_ANTES_6e623d3.py`; o código novo é o do commit que adiciona esta pasta:
`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-03-treasure-animado-e-mulligan`). **Uma chave por correção; com as três desligadas o arquivo é bit-idêntico ao anterior.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **Treasure animado = criatura em TODO sacrifício** | `ANIMATED_TREASURE_ROUTING_ENABLED` | `sacrifice_treasures`, `aggressive_treasure_destruction`, `combat_step`, `end_step`, `play_turn` | o Vihaan anima os Treasures no início do combate; a partir daí e até o fim do turno (inclusive a 2ª main phase) sacrificar um deles conta como morte de criatura + artefato + ficha, por **qualquer** caminho (mana, Deadly Dispute, Magda, Jan Jansen, Face-Breaker, Lich-Knights' Conquest, Krark-Clan Ironworks, Ashnod's Altar). Só os que existiam no início do combate (CR 611.2c) |
| **Mulligan com escolha** | `MULLIGAN_SMART_BOTTOM_ENABLED` | `choose_bottom`, `mulligan` | o London Mulligan sorteava as cartas do fundo; agora o jogador escolhe |
| **Terreno tapped em T1/T2** | `TAPPED_LAND_FIRST_ENABLED` (`_MAX_TURN`=2, `_SKIP_IF_LOSES_PLAY`) | `land_enters_tapped`, `dry_run_mana_spent`, `choose_land_to_play`, `play_land` | antes jogava o primeiro terreno da mão; agora, em T1/T2, joga o que entra tapped, **salvo** se isso custar uma jogada de desenvolvimento (mesma regra do Megatron) |

Detalhes que mudam o comportamento (todos documentados no código):
- `Ashnod's Altar` ("Sacrifice a **creature**") só aceita os Treasures **animados ainda vivos**; o código antigo sacrificava todos os Treasures a ele, inclusive os criados depois da animação (que não são criatura). `Krark-Clan Ironworks` ("Sacrifice an **artifact**") aceita todos, e um Treasure animado sacrificado a ele **também** é criatura (o código antigo dizia "não é criatura fora do combate", o que o oráculo do Vihaan nega: vale até o fim do turno).
- Sacrifica os animados primeiro (mais gatilhos pelo mesmo Treasure; escolha do controlador).
- Mulligan: só devolve terreno quando sobram mais de 4 (primeiro o que entra tapped); fora isso devolve a carta não-terreno de **maior custo**, protegendo `GOOD_KEEP` (Sol Ring, Arcane Signet, Smothering Tithe, Big Score).

## Oráculo e rulings lidos antes de escrever o código (Regra #3)

`dados/oraculo_e_rulings.json` (resposta bruta do Scryfall, 2026-10-03). **Vihaan, Goldwaker:** *Other outlaws you control have vigilance and haste. At the beginning of combat on your turn, you may have Treasures you control become 3/3 Construct Assassin artifact creatures in addition to their other types until end of turn.*
Rulings (2024-04-12): os Treasures **mantêm as habilidades** enquanto são criaturas; Assassin é outlaw. **CR 611.2c** (`rules-cache/comprehensive-rules.txt`, linha 2915): o conjunto de objetos afetado por um efeito contínuo que modifica características é fixado quando ele começa (Treasure criado depois não vira criatura).
Também lidos: Zulaport Cutthroat, Pitiless Plunderer, Mahadi, Emporium Master, Ashnod's Altar, Krark-Clan Ironworks, Sephiroth (10 rulings, nenhuma muda a leitura).

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada): `antes` = código do commit `6e623d3` · `treasure` · `bottom` (mulligan) · `tapped` (terreno) — cada correção sozinha · `blunt` = terreno tapped **cego** (sempre o tapped, sem o teste de jogada perdida; só sensibilidade) · **`todas` = as três (o simulador que fica)** · `todas_t4` = sensibilidade, a política de tapped vale até o T4.
- **Lotes:** `2000` = sementes `1_000_000+i` · `10000` = sementes `3_000_000+i` (**as mesmas do Kingpin**) · `2000` em modo resiliência (`FX_MODO=resiliencia`). 8 turnos. Regressão: sementes `5_000_000+i`.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`). Campos: `win_turn`, `revel_turn`, `cmd_turn`, `treasures`, `drain`, `table_dmg`, `combat`, `creature_deaths`, `bonus_mana`, `animated_any` (animados sacrificados como criatura, qualquer caminho), `animated_altar`, `mana_t1..t6` (mana disponível logo depois de jogar o terreno), contadores do piloto e `fp` (impressão digital de 12 hex do estado final).
- **Colunas das tabelas:** `win<=8` = vitória (proxy de dano letal ou Revel in Riches) até o T8; `cmd<=T` = comandante conjurado até o T; `Treasures` = criados; `dano mesa`/`combate`/`drain` = proxies agregados (nunca vida real de oponente); `mortes cria.` = mortes de criatura; `mana bonus` = mana de Altar/KCI; `mana T2..T4` = mana disponível.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/vihaan_goldfish_v1_ANTES_6e623d3.py` | simulador antes da correção (`git show 6e623d3:…`) | — | referência | variante `antes`, `bitident.py` |
| `dados/raw_ab_2000.json.xz` | 7 variantes × 2.000 partidas, sementes 1.000.000+ | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 7 variantes × 10.000 partidas, sementes 3.000.000+ | `fx_ab.py 10000` | **usado (tabela principal do log)** | `resumos/ab_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, modo resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/oraculo_e_rulings.json` | oráculo + rulings de 7 cartas | consulta direta à API | referência | checklist: Treasure animado |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 42 testes dirigidos | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS com as 3 chaves desligadas × ANTES: 20.000 partidas × 2 modos | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 8 configurações/modos: 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/indice_dados.md` | o que há em cada arquivo de dados | `indice_dados.py` | índice | — |

## Mapa: tabela → comando que a reproduz (de dentro de `orquestracao/`)

| resumo salvo (`resumos/`) | comando |
|---|---|
| `ab_2000.txt` / `ab_10000.txt` | `python3 fx_ab.py 2000 --sum` / `python3 fx_ab.py 10000 --sum` |
| `ab_2000_resiliencia.txt` | `FX_MODO=resiliencia python3 fx_ab.py 2000 --sum` |
| `smoke.txt` / `testes_dirigidos.txt` | `python3 smoke.py` / `python3 testes_dirigidos.py` |
| `bitident_flags_off_20000.txt` | `python3 bitident.py 20000 1000000` |
| `regressao_20000.txt` | `python3 fx_regressao.py 20000` |
| `indice_dados.md` | `python3 ../indice_dados.py` |

Sem `--sum`, `fx_ab.py` **roda** as simulações de novo (e regrava os brutos).

## Resultado em uma tabela (N=10.000, sementes 3.000.000+i, pareado; `resumos/ab_10000.txt`)

Base (`antes`): win ≤T8 8,8% · revel ≤T8 0,46% · comandante ≤T3 85,0% · ≤T4 95,3% · Treasures criados 9,71 · dano mesa 13,85 · combate 47,43 · drain 6,23 · mortes de criatura 2,13 · mana bonus 2,28 · mana T2/T3/T4 = 1,968 / 3,074 / 3,924.
Diferenças pareadas (variante − antes), IC95%:

| variante | win ≤8 (pp) | revel ≤8 (pp) | cmd ≤3 (pp) | cmd ≤4 (pp) | Treasures | dano mesa | combate | drain | mortes cria. | mana bonus | mana T2/T3/T4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `treasure` (só o roteamento) | +0,81 ±0,24 | +0,15 ±0,08 | 0 | 0 | +0,42 ±0,17 | +0,93 ±0,17 | +0,71 ±0,22 | +0,42 ±0,08 | **+0,91 ±0,06** | −0,34 ±0,09 | 0 / 0 / 0 |
| `bottom` (só o mulligan) | +0,25 ±0,19 | +0,07 ±0,06 | +1,40 ±0,31 | +1,00 ±0,20 | +0,10 ±0,05 | +0,08 ±0,12 | +0,64 ±0,19 | +0,05 ±0,05 | +0,04 ±0,02 | +0,04 ±0,04 | +0,01 / +0,03 / +0,04 |
| `tapped` (só o terreno T1/T2) | +0,72 ±0,20 | +0,07 ±0,06 | **+6,39 ±0,52** | +0,03 ±0,05 | +0,23 ±0,05 | +0,64 ±0,23 | +1,50 ±0,21 | +0,28 ±0,09 | +0,07 ±0,02 | +0,11 ±0,04 | +0,05 / +0,08 / +0,05 |
| `blunt` (tapped cego, sensibilidade) | +0,53 ±0,22 | +0,06 ±0,08 | +7,67 ±0,52 | +0,03 ±0,05 | +0,19 ±0,06 | +0,48 ±0,21 | +1,11 ±0,21 | +0,22 ±0,08 | +0,06 ±0,03 | +0,08 ±0,04 | **−0,02** / +0,09 / +0,04 |
| **`todas` (o que fica)** | **+1,83 ±0,36** | **+0,33 ±0,13** | **+7,77 ±0,57** | **+1,05 ±0,21** | **+0,77 ±0,18** | **+1,76 ±0,30** | **+3,01 ±0,36** | **+0,78 ±0,13** | **+1,05 ±0,07** | −0,21 ±0,10 | +0,06 / +0,11 / +0,10 |
| `todas_t4` (sensibilidade) | +2,08 ±0,38 | +0,34 ±0,13 | +8,76 ±0,57 | +1,05 ±0,21 | +0,83 ±0,18 | +1,78 ±0,28 | +3,34 ±0,38 | +0,81 ±0,12 | +1,07 ±0,07 | −0,17 ±0,10 | +0,06 / +0,11 / +0,05 |

Treasures animados sacrificados **como criatura** por partida: **0,56** (só Altar, antes) → **1,46** (qualquer caminho, só `treasure`) → **1,53** (`todas`). O mana bonus **cai** (−0,34) porque o Altar deixou de aceitar Treasure que não é criatura (o código antigo contava mana que o oráculo não permite).

## Verificações feitas ao arquivar (2026-10-03)

- **Bit-identidade com as três correções desligadas:** 20.000/20.000 partidas idênticas no modo padrão e 20.000/20.000 no modo resiliência (impressão digital de todo o estado final): `resumos/bitident_flags_off_20000.txt`.
- **Regressão:** 160.000 partidas (8 configurações/modos × 20.000), **0 exceções**, 0 cartas duplicadas, 0 partidas com "Treasures animados vivos" ≠ 0 ao fim do turno, 0 com Treasures < 0: `resumos/regressao_20000.txt`.
- **Testes dirigidos:** 42/42 (`resumos/testes_dirigidos.txt`), incluindo 2.000 partidas reais com a invariante "criaturas sacrificadas = mín(n, animados vivos) em toda chamada", `play_turn` completo com Vihaan + KCI + Zulaport + Mahadi (os animados morrem como criatura e o Mahadi cria Treasure no end step: a ordem de fases está certa) e animação no combate / zera no fim do turno.
- **Reprodutibilidade:** `bash orquestracao/verificar_reproducao.sh --tudo` → **7/7 saídas byte a byte iguais** (`cmp`): as 3 tabelas de A/B refeitas dos `.json.xz` e a **re-execução** do smoke, dos 42 testes, da bit-identidade de 20.000 partidas × 2 modos e da regressão de 160.000 partidas (`resumos/reproducao_cmp.txt`, ~1 min).

## O que NÃO foi verificado (Regra #7)

- Só foram varridas, neste arquivo, as classes: sacrifício/morte de Treasure e o conceito compartilhado "criatura que morre" (`on_permanent_sacrificed`, `sacrifice_*`), ordem de fases (animação no combate, 2ª main, end step), mulligan e jogada de terreno. **Não** foi feita auditoria carta a carta do `.py` inteiro.
- **Sephiroth** ("sacrifique qualquer número de outras criaturas ao atacar, compre essa quantia"): os Treasures animados também são criaturas nesse momento e poderiam ser combustível; o simulador só oferece fichas e Constructs (política, não oráculo). **Não** modelado nem medido.
- Pitiless Plunderer/Xorn: o simulador cria os Treasures em **lote** por evento (`create_treasures(n)`), e o Xorn soma +1 por lote, não por criatura que morre. Pré-existente; **não** alterado.
- O Treasure só tapa por mana se estiver desvirado; o Vihaan dá vigilância aos outlaws (os animados), então atacar não os tapa. Se o Vihaan morresse no meio do turno, os animados perderiam vigilância e haste. **Não** modelado.
- Os outros 7 decks com sorteio das cartas do fundo no mulligan (Hei Bai, Maralen, Nekusar, Rat King, Toph, Ulalek, Ur-Dragon) **não** foram alterados.
- Nenhuma carta foi cortada ou adicionada à lista; o Commander Spellbook não foi consultado porque nada na lista mudou.

## Nota posterior (2026-10-03, rodada do Sephiroth): o que mudou NESTA pasta depois do commit original

O simulador vivo ganhou depois três chaves novas (`SEPHIROTH_*`, ver `../2026-10-03-sephiroth/LEIAME.md`), **ligadas por padrão**. Para esta pasta continuar reproduzindo o simulador como era no commit dela, `orquestracao/fx_common.py` foi ajustado em duas linhas lógicas: (1) `flags()` agora também **desliga** as 3 chaves do Sephiroth; (2) o conjunto `NOVOS` (campos de `GameState` ignorados na impressão digital) ganhou os 6 campos novos (`super_nova_emblems`, `seph_batch_*`, `sephiroth_extra_triggers_total`). Nenhum dado bruto, resumo ou tabela mudou. Reverificado: `bash orquestracao/verificar_reproducao.sh --tudo` → 7/7 byte a byte iguais (a bit-identidade tinha passado a divergir sem o ajuste; com ele volta a 20.000/20.000 nos dois modos). `SHA256SUMS` regenerado (só o `fx_common.py` mudou).

Segunda nota (rodada "fora da mão", 2026-10-03): o simulador vivo ganhou cinco chaves novas ligadas por padrão (`../2026-10-03-fora-da-mao/LEIAME.md`). `orquestracao/fx_common.py` agora também desliga essas 5 chaves e ignora os 8 campos novos do `GameState`; `orquestracao/smoke.py` passou a carregar o simulador por `F.flags(...)`. Reverificado: `bash orquestracao/verificar_reproducao.sh --tudo` → 7/7 byte a byte iguais. `SHA256SUMS` regenerado.

Terceira nota (rodada "Prosper e Mahadi", 2026-10-03): o simulador vivo ganhou mais duas chaves ligadas por padrão (`IMPULSE_EXPIRING_FIRST_ENABLED`, `TREASURE_SELF_OUTLET_FARM_ENABLED`; ver `../2026-10-03-exilio-primeiro-e-mahadi/LEIAME.md`). `orquestracao/fx_common.py` agora também as desliga e ignora os 3 campos novos do `GameState`. Reverificado: `bash orquestracao/verificar_reproducao.sh --tudo` → 7/7 byte a byte iguais. `SHA256SUMS` regenerado.

Nota (rodada "exílio sempre e Dictate", 2026-10-04): o simulador vivo ganhou mais duas chaves ligadas por padrão (`IMPULSE_ALL_FIRST_ENABLED`, `TREASURE_FARM_WITH_DICTATE_ENABLED`; ver `../2026-10-04-exilio-sempre-e-dictate/LEIAME.md`). `orquestracao/fx_common.py` agora também as desliga e ignora os 2 campos novos do `GameState`. Reverificado: `bash orquestracao/verificar_reproducao.sh --tudo` → 7/7 byte a byte iguais. `SHA256SUMS` regenerado.

## Nota de 2026-10-04 (9ª rodada: `../2026-10-04-wipes-proprios/`)

- **As 5 chaves novas** (wipes próprios: destruição fiel, Treasure virado, custo da Blasphemous Act, retenção; imposto do comandante) vêm **ligadas** no simulador vivo. O `orquestracao/fx_common.py` desta pasta as **desliga** (e inclui os 7 campos novos do `GameState` em `NOVOS`) pra continuar reproduzindo o simulador do commit dela.
- `verificar_reproducao.sh --tudo` depois da 9ª rodada: 7/7. `SHA256SUMS` regenerado.

## Nota de 2026-10-04 (10ª rodada: `../2026-10-04-wipes-segurados/`)

- **As 3 chaves novas** (todo wipe próprio segurado; custo do wipe pago primeiro com Treasures animados; exceção mitigada com Mayhem Devil) vêm **ligadas** no simulador vivo. O `orquestracao/fx_common.py` desta pasta as **desliga** (e inclui os 3 campos novos do `GameState` em `NOVOS`) pra continuar reproduzindo o simulador do commit dela.
- `verificar_reproducao.sh --tudo` depois da 10ª rodada: 7/7. `SHA256SUMS` regenerado.

## Nota de 2026-10-04 (11ª rodada: `../2026-10-04-blasphemous-edict/`)

- **A chave nova** (`MIRKWOOD_BATS_SACRIFICE_ONLY_ENABLED`: o Mirkwood Bats só dispara em sacrifício de ficha, não em ficha destruída) vem **ligada** no simulador vivo. O `orquestracao/fx_common.py` desta pasta a **desliga** (bloco anexado ao fim do `flags()`; nenhum campo novo do `GameState`) pra continuar reproduzindo o simulador do commit dela.
- `verificar_reproducao.sh --tudo` depois da 11ª rodada: 7/7. `SHA256SUMS` regenerado.
