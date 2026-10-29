# Resultados brutos — Inevitable Defeat no Vihaan (2026-10-03)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis
estão em `vihaan-goldwaker-mardu/goldfish-log.md` (seção "Inevitable Defeat — avaliação como possível inclusão — 2026-10-03") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**
Pedido do usuário: *"Faça o mesmo para Inevitable Defeat como possível inclusão nos meus dois decks Mardu: Megatron e Vihaan."*

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer uma tabela a partir dos dados | rodar o comando da coluna "comando" do mapa, **de dentro de `orquestracao/`** (os scripts leem os `.json.xz` direto, via `raw_io.py`) |
| abrir os brutos por partida em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## O simulador não foi alterado

> **Nota posterior (2026-10-03, mesma data, depois desta rodada): o simulador vivo mudou.** A frase "o simulador não foi alterado" vale **para esta rodada** (medidas com o commit `6e623d3`).
> Depois dela, `vihaan_goldfish_v1.py` ganhou o roteamento do Treasure animado (todo sacrifício de Treasure depois da animação conta como morte de criatura), o mulligan com escolha das cartas do fundo
> e o terreno tapped em T1/T2 (`../2026-10-03-treasure-animado-e-mulligan/LEIAME.md`). Consequências para esta pasta: (1) **as tabelas continuam reproduzíveis**, porque `--sum` lê só os brutos `.json.xz`;
> (2) `bitident.py` e qualquer rerodada **sem** `--sum` rodam contra o arquivo VIVO e **passam a divergir**: para refazê-los, extraia o simulador antigo com
> `git show 6e623d3:vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` (há uma cópia em `../2026-10-03-treasure-animado-e-mulligan/codigo/vihaan_goldfish_v1_ANTES_6e623d3.py`) ou desligue as 3 chaves
> (`ANIMATED_TREASURE_ROUTING_ENABLED`, `MULLIGAN_SMART_BOTTOM_ENABLED`, `TAPPED_LAND_FIRST_ENABLED`); (3) os números **absolutos** daqui são do simulador antigo, não comparáveis com rodadas feitas depois da correção;
> o "achado lateral" do Treasure animado citado no log desta rodada foi **corrigido** nessa rodada seguinte.


`vihaan-goldwaker-mardu/vihaan_goldfish_v1.py` (último commit `6e623d3`) **não foi editado**: a carta nova e a instrumentação entram por *monkeypatch* em tempo de execução (`orquestracao/*_harness.py`).
A base do harness (sem a carta na lista) foi comparada com o módulo original, carregado como módulo separado e sem nenhum patch: ver `resumos/bitident.txt`.
Código desta pasta: o commit que a adiciona (`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-03-inevitable-defeat`).

## Como os dados foram gerados

- **Sementes:** `3_000_000 + i`, a mesma semente em todas as variantes de um lote (**pareado**; IC95% = 1,96·dp/√N da diferença). N = 10.000 (A/B e castabilidade), 5.000 (ablação). 8 turnos (o simulador encerra a partida quando a condição do Revel in Riches é cumprida).
- **Variante:** `swap=[(SAI, ENTRA)]` do próprio `simulate_one` (troca **posicional**). `ENTRA` = `Inevitable Defeat` ou `Blank Card`.
- **Blank Card:** carta inconjurável (instantâneo, MV 99). No Vihaan o tipo (artefato ou instantâneo) **não muda** nenhum número (conferido: tabelas idênticas); ver `superado-blank-artefato/LEIA-ME-PRIMEIRO.md`. Como é carta morta, o simulador **premia não gastar mana** em `X`: ler só relativamente.
- **Modelagem da Defeat** (`orquestracao/vih_harness.py`): tag `removal`; `commits_crime_this_turn = True` (alvo é permanente de oponente: comete crime, lido pela Magda no fim do turno); `drain(3, each_opp=False)` + `gain_life(3)` ao resolver; o exílio é 📊. **O simulador não modela cor**, então a restrição R+W+B é uma **porta de cor do harness**, escolhida por `VIH_COLOR`: `off` (sem porta, como a 1ª rodada), `sim` (pessimista: só terrenos já jogados pelo simulador, que joga `lands_in_hand[0]` sem sequenciar por cor; Exotic Orchard sem cor; Pathway/filtros como 1 fonte de 2 cores) e `best` (otimista: melhor subconjunto campo+mão, Orchard de qualquer cor). Em ambos, Arcane Signet e cada Treasure contam como fonte de qualquer cor; precisa de 3 fontes distintas.
- **Instrumentação só-leitura:** `rwb_turn_sim`/`rwb_turn_best` (1º turno com R+W+B e ≥4 de mana), `defeat_magda`/`defeat_witch` (Magda/Witch em campo quando a Defeat resolve), `recursion`.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`; campos em `vih_harness.summarize`).

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é (variantes) | código | status | tabela do log que o usa |
|---|---|---|---|---|
| `dados/raw_ablacao_vihaan.json.xz` | base + 64 cortes (cada carta não-terreno pela Blank), N=5.000 | `vih_ablacao.py` | usado | `resumos/ablacao_vihaan.txt` (ranking dos controles) |
| `dados/raw_ab_vihaan_10000_cor-sim.json.xz` | base + 21 `Defeat<-X` (19 candidatas + 2 controles) + 3 `Blank<-X`, N=10.000, porta de cor **pessimista** | `vih_ab.py` com `VIH_COLOR=sim` | **usado (tabela do log)** | `resumos/ab_vihaan_10000_cor-sim.txt` |
| `dados/raw_ab_vihaan_10000_cor-best.json.xz` | idem, porta de cor otimista | `VIH_COLOR=best` | usado (sensibilidade; difere ≤0,2pp de conjuração e ≤0,01 nos efeitos) | `resumos/ab_vihaan_10000_cor-best.txt` |
| `dados/raw_ab_vihaan_10000_cor-off.json.xz` | idem, sem porta de cor | `VIH_COLOR=off` | usado (sensibilidade) | `resumos/ab_vihaan_10000_cor-off.txt` |
| `dados/raw_castabilidade_cor_vihaan.json.xz` | base, N=10.000, `rwb_turn_sim`/`rwb_turn_best` e `cmd_turn` | `vih_cor.py` | usado | `resumos/castabilidade_cor_vihaan.txt` (log: Cor) |
| `dados/spellbook_vihaan_swaps.json` | **resumo** do `find-my-combos` (combos incluídos e "quase" por lista: base, +Defeat, 15 trocas); **não** guarda a resposta crua | `csb_generic.py` | usado | `resumos/spellbook_vihaan_swaps.txt` (log: Combos) |
| `dados/rulings_Inevitable_Defeat.json` | oráculo bruto do Scryfall + 1 ruling (lidos ao vivo em 2026-10-03) | consulta direta à API | referência | checklist: Inevitable Defeat |
| `superado-blank-artefato/` | 1º lote (Blank como artefato), só tabelas agregadas | — | marcado: **tabelas idênticas** às atuais (ver o README da pasta) | nenhuma |
| `resumos/enumeracao.txt` | enumeração por script das 95 entradas distintas de `lista.md` (crime, alvo de oponente, ganho/perda de vida, exile, gatilho de spell) | `vih_enumeracao.py` | usado | log: motores |
| `resumos/bitident.txt` | base do harness × simulador original sem patch, nos 3 modos de cor (300 partidas cada) | `bitident.py` | verificação | log: escopo verificado |

## Mapa: tabela → comando que a reproduz (de dentro de `orquestracao/`)

| resumo salvo (`resumos/`) | comando |
|---|---|
| `ablacao_vihaan.txt` | `python3 vih_ablacao.py --sum` |
| `ab_vihaan_10000_cor-sim.txt` | `VIH_COLOR=sim python3 vih_ab.py 10000 --sum` |
| `ab_vihaan_10000_cor-best.txt` | `VIH_COLOR=best python3 vih_ab.py 10000 --sum` |
| `ab_vihaan_10000_cor-off.txt` | `VIH_COLOR=off python3 vih_ab.py 10000 --sum` |
| `castabilidade_cor_vihaan.txt` | `python3 vih_cor.py --sum` |
| `enumeracao.txt` | `python3 vih_enumeracao.py` (lê o cache do Scryfall e `lista.md`) |
| `bitident.txt` | `for m in off sim best; do VIH_COLOR=$m python3 bitident.py 300 8; done` |
| `spellbook_vihaan_swaps.txt` | a partir da raiz do repositório: `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 vihaan-goldwaker-mardu/resultados-ab/2026-10-03-inevitable-defeat/orquestracao/csb_generic.py vihaan-goldwaker-mardu "Vihaan, Goldwaker" saida.json "CARTA1|CARTA2|…" "Inevitable Defeat"`; depende da API ao vivo, **não** é refeito byte a byte |
| `indice_dados.md` | `python3 ../indice_dados.py` |

Sem `--sum`, os mesmos scripts **rodam** as simulações de novo (e gravam os brutos).

## Verificações feitas ao arquivar (2026-10-03)

- **Reprodutibilidade:** a partir dos `.json.xz`, as 6 tabelas `ablacao_vihaan`, `ab_vihaan_10000_cor-{off,sim,best}` e `castabilidade_cor_vihaan` saíram **byte a byte iguais** às salvas (`cmp` sem diferença); `enumeracao.txt` também (rodado de novo, igual, com 3 valores de `PYTHONHASHSEED`). Também são **iguais às da rodada anterior** do mesmo código (determinismo).
- **Bit-identidade:** `bitident.py 300 8` nos 3 modos de cor: 300/300 partidas idênticas em 101 campos do `GameState` (original sem patch × base do harness).
- **Controles:** no A/B, cortar Sol Ring custa −3,1pp de win ≤T8 e cortar Arcane Signet atrasa o comandante (−0,7pp ≤T3); no Spellbook, cortar Smothering Tithe ou Gleaming Splendor remove 3 combos.
- **Não conferido byte a byte:** `spellbook_vihaan_swaps.*` (API ao vivo; resposta crua não guardada) e `rulings_*.json`.
- **Limitação declarada:** a porta de cor é uma leitura do estado do simulador (que não tem cores), não um modelo de mana completo; Treasures contam como fonte curinga.
- **Tudo de uma vez:** `bash orquestracao/verificar_reproducao.sh` refaz todas as tabelas dos `.json.xz` e compara com `cmp`; a saída desta verificação está em `resumos/reproducao_cmp.txt`.
- **Hashes:** `SHA256SUMS` cobre `dados/`, `resumos/`, `orquestracao/`, `superado-blank-artefato/`, `indice_dados.py`, `descomprimir.sh` e `.gitignore`.

## Nota de 2026-10-04 (12ª rodada: Mythos of Snapdax no lugar do Blood Money)

A lista viva do Vihaan (`../../lista.md`) passou a ter `Mythos of Snapdax` no lugar de `Blood Money` e o simulador vivo ganhou duas chaves novas (`MYTHOS_REPLACES_BLOOD_MONEY_ENABLED`, `CASCADE_DECLINE_HELD_WIPES_ENABLED`; ver `../2026-10-04-mythos-no-lugar-do-blood-money/LEIAME.md`). Para esta pasta **continuar reproduzindo o que publicou**, os scripts abaixo passaram a ler a lista antiga (`../_lista_legada/lista.md`, cópia exata da lista de `a17049f`) e/ou a **desligar as duas chaves novas** no simulador vivo (a lista volta a ter o Blood Money na posição antiga; bit-idêntico a `a17049f`) e, nos `fx_common.py`, a ignorar os 4 campos novos do `GameState` na impressão digital. **Nenhum dado bruto nem resumo desta pasta foi tocado.** Scripts alterados: `orquestracao/bitident.py`, `orquestracao/vih_enumeracao.py`, `orquestracao/vih_harness.py`. Depois do ajuste, `bash orquestracao/verificar_reproducao.sh` (esta pasta não tem `--tudo`; o roteiro refaz tudo o que tem): **6/6** saídas iguais byte a byte, **0 `DIFERE`**. `SHA256SUMS` regenerado (o `LEIAME.md` e o próprio `SHA256SUMS` ficam de fora).
