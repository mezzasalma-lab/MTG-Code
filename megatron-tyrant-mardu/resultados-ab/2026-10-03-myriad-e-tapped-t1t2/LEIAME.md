# Resultados brutos — correção do Myriad Landscape e do terreno tapped em T1/T2 (Megatron, 2026-10-03)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Megatron, Tyrant. As conclusões e as tabelas legíveis estão em
`megatron-tyrant-mardu/goldfish-log.md` (seção "Correção do simulador: Myriad Landscape e terreno tapped em T1/T2 — 2026-10-03") e em `megatron-tyrant-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**
Pedido do usuário: *"Quero que vc corrija o Myriad Landscape e o terreno tapped em T1 e T2 no simulador do Megatron"*.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` (rápido, só lê os `.json.xz`); `--tudo` re-executa também testes, bit-identidade e regressão |
| abrir os brutos por partida em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## O que foi alterado no simulador

Arquivo: `megatron-tyrant-mardu/megatron_goldfish_v1.py` (código anterior = commit `22d0ed2`, guardado nesta pasta em `codigo/megatron_goldfish_v1_ANTES_22d0ed2.py`; o código novo é o do commit que adiciona esta pasta:
`git log -1 -- megatron-tyrant-mardu/resultados-ab/2026-10-03-myriad-e-tapped-t1t2`).

| mudança | onde | o que faz |
|---|---|---|
| **Myriad Landscape: 3ª habilidade** | `try_myriad_landscape`, chamada em `play_turn` entre a 2ª `main_phase` e o `end_step` | `{2},{T}`, sacrifica: busca até dois básicos do mesmo tipo, para o campo tapped, embaralha |
| **Terreno tapped em T1/T2** | `choose_land_to_play` (+ `land_enters_tapped`, `dry_run_mana_spent`), usada por `play_land` | em T1/T2, com um terreno tapped e um untapped na mão, joga o tapped, **salvo** se o tapped fizer perder uma jogada de desenvolvimento |
| chaves de liga/desliga | `TAPPED_LAND_FIRST_ENABLED`, `TAPPED_LAND_FIRST_MAX_TURN` (=2), `TAPPED_LAND_FIRST_SKIP_IF_LOSES_PLAY`, `MYRIAD_ABILITY_ENABLED` | isolam cada correção no A/B; **com as duas desligadas o arquivo é bit-idêntico ao anterior** |
| contadores | `myriad_activations_total`, `myriad_basics_fetched_total`, `tapped_land_first_plays_total`, `tapped_land_skipped_for_play_total` | métricas novas, impressas por `run_batch` |

Convenções do **piloto** (não do oráculo), documentadas no código: o Myriad só é ativado com mana que **sobraria** (remaining ≥ 3: {2} de custo + o {C} do próprio Myriad, que fica tapado), nunca no lugar de conjurar;
depois da 2ª main phase e **antes** do end step (os básicos entram tapped e desviram no próximo untap: custo de tempo zero; e o "descended" do Brass's Tunnel-Grinder conta o Myriad sacrificado);
o tipo escolhido é o de maior déficit de fonte (W/B/R que o comandante ainda exige, ou o maior número de pips de uma carta da mão), depois o que traz 2 em vez de 1, depois o de menos fontes.

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada):
  `antes` = código do commit `22d0ed2` · `tapped` = só a política de terreno tapped · `blunt` = política **cega** (sempre o tapped em T1/T2, sem o teste de jogada perdida; reproduz o `early_all` do Power Depot) ·
  `myriad` = só a habilidade do Myriad · **`ambas` = as duas (o simulador que fica no repositório)** · `ambas_t4` = sensibilidade, a política de tapped vale até o T4.
- **Lotes:** `2000` = sementes `1_000_000+i` (as de `run_batch`, exigência da Regra #1) · `10000` = sementes `3_000_000+i` (**as mesmas do Power Depot**, comparáveis com os números dele) ·
  `2000` em modo resiliência (`FX_MODO=resiliencia`, `simulate_one_with_interaction`). 8 turnos. Regressão: sementes `5_000_000+i`.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`). Campos: os de sempre (`cmd_turn`, `proxy_dmg`,
  `mana_convert`, `weld`, …), `mana_t1..t6` (mana total disponível logo depois de jogar o terreno, antes de conjurar), os 4 contadores novos e `fp` (impressão digital de 12 hex do estado final inteiro, usada para contar "jogos iguais").
- **Colunas das tabelas:** `cmd<=T` = comandante conjurado até o turno T; `nunca` = nunca conjurado em 8 turnos; `win` = vitória por veneno ou dano de comandante; `dano` e `mana conv` = dano proxy e mana de flip;
  `mana T2..T5` = `mana_t*` acima; `terrenos` = terrenos em campo no fim; `jogos iguais` = % de partidas com o mesmo estado final que `antes`.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/megatron_goldfish_v1_ANTES_22d0ed2.py` | simulador antes da correção (`git show 22d0ed2:…`) | — | referência | variante `antes`, `bitident.py` |
| `dados/raw_ab_2000.json.xz` | 6 variantes × 2.000 partidas, sementes 1.000.000+ | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 6 variantes × 10.000 partidas, sementes 3.000.000+ | `fx_ab.py 10000` | **usado (tabela principal do log)** | `resumos/ab_10000.txt`, `resumos/verificacao_cruzada_blunt_vs_early_all.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, modo resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/rulings_Myriad_Landscape.json` | oráculo bruto do Scryfall + 1 ruling (lidos ao vivo em 2026-10-03, **antes** de escrever o código) | consulta direta à API | referência | checklist: Myriad Landscape |
| `resumos/smoke.txt` | contagem de cartas (99), 0 desconhecidas, 0 duplicadas não básicas, 34 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 49 testes dirigidos (PASS/FAIL por teste) | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | simulador novo com as duas correções desligadas × antigo: 20.000 partidas × 2 modos | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × (7 configurações/modos): 0 exceções + conservação de cartas | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/verificacao_cruzada_blunt_vs_early_all.txt` | a política cega daqui × o `early_all` do harness do Power Depot, partida a partida (10.000) | `fx_cruzada.py` | verificação | log: validação |
| `resumos/mulligan_topo.txt` | achado lateral: cartas devolvidas no mulligan vão pro topo da biblioteca (demonstração em runtime + frequência de 2+ mulligans) | `mulligan_topo.py` | achado (não corrigido) | checklist: achados laterais |
| `resumos/indice_dados.md` | o que há em cada arquivo de dados | `indice_dados.py` | índice | — |

## Mapa: tabela → comando que a reproduz (de dentro de `orquestracao/`)

| resumo salvo (`resumos/`) | comando |
|---|---|
| `ab_2000.txt` / `ab_10000.txt` | `python3 fx_ab.py 2000 --sum` / `python3 fx_ab.py 10000 --sum` |
| `ab_2000_resiliencia.txt` | `FX_MODO=resiliencia python3 fx_ab.py 2000 --sum` |
| `verificacao_cruzada_blunt_vs_early_all.txt` | `python3 fx_cruzada.py` (lê também `../../2026-10-03-power-depot/dados/raw_ab_powerdepot_10000_early_all.json.xz`) |
| `mulligan_topo.txt` | `python3 mulligan_topo.py` |
| `smoke.txt` | `python3 smoke.py` |
| `testes_dirigidos.txt` | `python3 testes_dirigidos.py` |
| `bitident_flags_off_20000.txt` | `python3 bitident.py 20000 1000000` |
| `regressao_20000.txt` | `python3 fx_regressao.py 20000` |
| `indice_dados.md` | `python3 ../indice_dados.py` |

Sem `--sum`, `fx_ab.py` **roda** as simulações de novo (e regrava os brutos).

## Resultado em uma tabela (N=10.000, sementes 3.000.000+i, pareado; `resumos/ab_10000.txt`)

Base (`antes`): comandante ≤T3 31,3% · ≤T4 77,8% · ≤T5 88,8% · nunca (T8) 4,1% · win 83,8% · dano 83,40 · mana de flip 70,25 · mana no main phase: T2 1,943, T3 3,300, T4 4,273, T5 4,927.
Diferenças pareadas (variante − antes), IC95%:

| variante | cmd ≤T3 (pp) | cmd ≤T4 (pp) | cmd ≤T5 (pp) | nunca (pp) | win (pp) | dano | mana T2 / T3 / T4 | terrenos no fim |
|---|---|---|---|---|---|---|---|---|
| `tapped` (T1/T2, com teste de jogada perdida) | +4,25 ±0,45 | +3,31 ±0,38 | +0,02 ±0,07 | +0,00 ±0,04 | +0,72 ±0,22 | +2,73 ±0,45 | +0,09 / +0,10 / +0,04 | +0,01 |
| `blunt` (T1/T2, sempre o tapped) | +1,36 ±0,51 | +4,75 ±0,43 | +0,02 ±0,07 | +0,00 ±0,04 | +0,75 ±0,24 | +1,70 ±0,38 | **−0,13** / +0,12 / +0,10 | +0,01 |
| `myriad` (só a habilidade) | +0,00 | +0,04 ±0,04 | +0,15 ±0,08 | −0,34 ±0,12 | +0,31 ±0,16 | +0,56 ±0,20 | 0 / 0 / 0 | **+0,15 ±0,01** |
| **`ambas` (o que fica)** | **+4,26 ±0,45** | **+3,53 ±0,39** | +0,35 ±0,13 | −0,32 ±0,13 | **+1,25 ±0,28** | **+3,32 ±0,49** | +0,09 / +0,10 / +0,04 | +0,16 |
| `ambas_t4` (sensibilidade, tapped até T4) | +6,94 ±0,55 | +5,36 ±0,48 | +0,32 ±0,14 | −0,33 ±0,13 | +1,41 ±0,30 | +4,27 ±0,60 | +0,09 / +0,10 / +0,01 | +0,16 |

O Myriad foi ativado em 15,4% das partidas (`myriad`) e rende +0,31 terreno por partida buscado: +1 terreno líquido × 15,4% = **+0,15 terreno**, igual ao medido.

## Verificações feitas ao arquivar (2026-10-03)

- **Bit-identidade com as duas correções desligadas:** 20.000/20.000 partidas idênticas no modo padrão e 20.000/20.000 no modo resiliência (impressão digital de todo o estado final): `resumos/bitident_flags_off_20000.txt`.
- **Verificação cruzada independente:** a política cega (`blunt`) reproduz o `early_all` do harness do Power Depot (outro código, por monkeypatch) em **10.000/10.000 partidas, 12 campos por partida**: `resumos/verificacao_cruzada_blunt_vs_early_all.txt`.
- **Regressão:** 20.000 partidas × (padrão e resiliência com `ambas`; padrão com `so_tapped`, `so_myriad`, `blunt`, `ambas_t4`; resiliência com `ambas_t4`) = 140.000 partidas, **0 exceções**, **0 violações de conservação** (Plains/Swamp/Mountain/Myriad sempre somam 6/6/6/1 entre mão, campo, cemitério, biblioteca e exílio).
- **Testes dirigidos:** 49/49 (`resumos/testes_dirigidos.txt`), incluindo dois em `play_turn` completo (Regra #6): o Myriad sacrificado conta como "descended" do Tunnel-Grinder (só vale porque a chamada fica antes do `end_step`), e os básicos buscados rendem mana no turno seguinte.
- **Reprodutibilidade:** `bash orquestracao/verificar_reproducao.sh --tudo` → **9/9 saídas byte a byte iguais** (`cmp`) aos resumos salvos: as 3 tabelas de A/B refeitas a partir dos `.json.xz`, a verificação cruzada, o achado do mulligan, o smoke, e a **re-execução** dos 49 testes dirigidos, da bit-identidade de 20.000 partidas × 2 modos e da regressão de 140.000 partidas (`resumos/reproducao_cmp.txt`, ~1m45s).

## O que NÃO foi verificado (Regra #7)

- Só foram varridas, neste arquivo, as classes: terreno (entra tapped, mana, básicos), mana/cor (`total_mana`, `color_sources`), biblioteca/embaralhar, ordem de fases (`play_turn`) e o conceito compartilhado "carta no cemitério = permanente" (`count_permanent_cards`, usado pelo Tunnel-Grinder). **Não** foi feita auditoria carta a carta do `.py` inteiro.
- As fetches (Evolving Wilds, Terramorphic Expanse, Rocky Tar Pit) **continuam simplificadas** como fonte fixa já em campo (a habilidade de sacrifício delas é modelável com o mesmo mecanismo e **não** foi feita: fora do pedido).
- A política do Myriad (só com mana que sobraria; depois da 2ª main phase) é convenção do piloto; ativar antes de conjurar para acelerar o turno seguinte, ou no fim do turno do oponente, **não** foi modelado nem medido.
- `TAPPED_LAND_FIRST_MAX_TURN` ficou em 2 como pedido; a sensibilidade até o T4 está na tabela, mas a política "tapped sempre que não custar jogada" em todos os turnos não foi medida além do T4.
- Achado lateral não corrigido: o London Mulligan do `mulligan()` põe as cartas devolvidas no TOPO da biblioteca (`library.insert(0, worst)`; `draw_cards` tira do índice 0). Afeta as partidas com 2+ mulligans (21,4% em 20.000 sorteios de mão). Ver checklist.
- Nenhuma carta foi cortada ou adicionada à lista; o Commander Spellbook não foi consultado porque nada na lista mudou.
