# Resultados brutos — London Mulligan e fetch lands no simulador do Megatron (2026-10-03, 2ª rodada)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Megatron, Tyrant. As conclusões e as tabelas legíveis estão em
`megatron-tyrant-mardu/goldfish-log.md` (seção "Correção do simulador: London Mulligan e fetch lands — 2026-10-03") e em `megatron-tyrant-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**
Pedido do usuário: *"Quer que eu corrija o mulligan ou modele as fetches? Os dois mudam a base de novo" — "Quero sim, sempre! Termine as tarefas que pararam pelo limite"*.

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

Arquivo: `megatron-tyrant-mardu/megatron_goldfish_v1.py` (código anterior = commit `3dae6ba`, guardado em `codigo/megatron_goldfish_v1_ANTES_3dae6ba.py`; o código novo é o do commit que adiciona esta pasta:
`git log -1 -- megatron-tyrant-mardu/resultados-ab/2026-10-03-mulligan-e-fetches`). **Com `MULLIGAN_BOTTOM_MODE="legacy"` e `FETCHLANDS_ENABLED=False` o arquivo é bit-idêntico ao anterior.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **London Mulligan** | `MULLIGAN_BOTTOM_MODE` (`legacy` / `bottom_only` / `smart`) | `choose_bottom`, `mulligan` | as cartas devolvidas iam para o **topo** da biblioteca (`library.insert(0, …)`, e a compra tira do índice 0) e eram as de **menor** custo (terrenos primeiro). Agora o jogador escolhe e elas vão para o **fundo** |
| **Fetch lands** | `FETCHLANDS_ENABLED` | `crack_fetchland`, `pick_fetch_target`, `try_crack_rocky_tar_pit`, `play_land`, `total_mana`, `color_sources` | Evolving Wilds, Terramorphic Expanse e Rocky Tar Pit com a habilidade real (antes: "terreno tapped que vira fonte de W/B/R") |
| **Terreno tapped por efeito, por instância** | (mesma chave) | `extra_tapped_lands_this_turn`, `color_sources`, `total_mana` | o campo antigo `tapped_land_this_turn` guarda UM **nome** e excluiria todas as cópias de um básico; agora cada instância tapped por efeito (básico buscado, Myriad Landscape) é descontada uma vez |

**Mulligan, como a escolha funciona** (a mesma do Edgar Markov, com Sol Ring, Arcane Signet, Fellwar Stone e Mind Stone protegidos): só devolve terreno quando sobram **mais de 4** (o de menos cores; empate: o que entra tapped); fora isso devolve a carta não-terreno de **maior custo**.

**Fetch lands, o que o oráculo diz** (lido ao vivo, `dados/oraculo_e_rulings.json`):
- *Evolving Wilds / Terramorphic Expanse*: **entram untapped**. "{T}, Sacrifice this land: Search your library for a basic land card, put it onto the battlefield **tapped**, then shuffle." O piloto sacrifica na hora, o básico entra tapped (0 de mana no turno).
- *Rocky Tar Pit*: "This land **enters tapped**. {T}, Sacrifice this land: Search your library for a **Swamp or Mountain card**, put it onto the battlefield, then shuffle." O alvo é qualquer **carta com o tipo** Swamp ou Mountain, não só básico: na lista, Swamp, Mountain, **Badlands, Scrubland, Plateau, Smoldering Marsh e Sunlit Marsh** (conferido por script contra o `type_line` do cache). Entra untapped, salvo se o próprio alvo entra tapped. Só pode ser sacrificado a partir do turno seguinte (entrou tapped): o piloto sacrifica **antes** da main phase, para o terreno buscado já render mana. Ruling 2004-10-04: a busca pode falhar; o piloto não sacrifica sem alvo.
- Nenhuma das três tem habilidade de mana: em campo não rendem mana nem cor.
- Alvo escolhido: o que cobre mais cores em déficit (cor que o comandante ainda exige ou maior pip de uma carta da mão), depois maior demanda da mão, depois o que entra untapped, depois o de mais cores. O sacrifício passa pelo `sacrifice()` central (permanente no cemitério: conta como "descended" do Brass's Tunnel-Grinder) e embaralha de verdade.

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada): `antes` = código do commit `3dae6ba` · `mull_posicao` = só a posição corrigida (menor MV, mas no fundo) · `mull_smart` = mulligan com escolha (fetches desligadas) · `fetch` = só as fetches (mulligan antigo) · **`ambas` = as duas (o simulador que fica)**.
- **Lotes:** `2000` = sementes `1_000_000+i` · `10000` = sementes `3_000_000+i` (as mesmas do Power Depot e do Myriad) · `2000` em modo resiliência (`FX_MODO=resiliencia`). 8 turnos. Regressão: sementes `5_000_000+i`.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`). `mana_t1..t6` = mana disponível **no 1º main phase** do turno (depois de jogar o terreno e de sacrificar o Rocky Tar Pit); `fp` = impressão digital de 12 hex do estado final.
- **Colunas das tabelas:** as mesmas das rodadas anteriores do Megatron: `cmd<=T` = comandante conjurado até o turno T; `nunca` = nunca conjurado em 8 turnos; `win` = vitória por veneno ou dano de comandante; `dano`/`mana conv` = dano proxy e mana de flip.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/megatron_goldfish_v1_ANTES_3dae6ba.py` | simulador antes desta rodada (`git show 3dae6ba:…`) | — | referência | variante `antes`, `bitident.py` |
| `dados/raw_ab_2000.json.xz` | 5 variantes × 2.000 partidas | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 5 variantes × 10.000 partidas | `fx_ab.py 10000` | **usado (tabela principal do log)** | `resumos/ab_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, modo resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/oraculo_e_rulings.json` | oráculo + rulings de Evolving Wilds, Terramorphic Expanse e Rocky Tar Pit | consulta direta à API | referência | checklist: fetch lands |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 34 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 33 testes dirigidos | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS (mulligan `legacy`, fetch desligado) × ANTES: 20.000 partidas × 2 modos | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 7 configurações/modos: 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
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

Base (`antes`, simulador com Myriad e tapped T1/T2): comandante ≤T3 35,5% · ≤T4 81,3% · ≤T5 89,1% · nunca (T8) 3,8% · win 85,1% · dano 86,72 · mana de flip 73,01 · mana no 1º main phase T2/T3/T4 = 2,032 / 3,401 / 4,316.
Diferenças pareadas (variante − antes), IC95%:

| variante | cmd ≤T3 (pp) | cmd ≤T4 (pp) | cmd ≤T5 (pp) | nunca (pp) | win (pp) | dano | mana T2 / T3 / T4 | terrenos no fim |
|---|---|---|---|---|---|---|---|---|
| `mull_posicao` (só a posição) | −1,46 ±0,35 | **−3,74 ±0,44** | −3,98 ±0,42 | +2,47 ±0,33 | −3,47 ±0,43 | −2,58 ±0,43 | −0,05 / −0,11 / −0,13 | −0,19 |
| `mull_smart` (mulligan com escolha) | +1,80 ±0,29 | **+2,65 ±0,33** | +1,83 ±0,27 | −0,93 ±0,19 | +1,93 ±0,33 | +0,80 ±0,38 | +0,03 / +0,05 / +0,07 | +0,10 |
| `fetch` (só as fetches) | −0,65 ±0,35 | **−1,35 ±0,44** | −1,29 ±0,35 | +0,33 ±0,23 | −1,33 ±0,46 | −0,48 ±0,77 | −0,01 / 0,00 / 0,00 | −0,04 |
| **`ambas` (o que fica)** | **+1,22 ±0,43** | **+1,51 ±0,52** | +0,74 ±0,42 | −0,68 ±0,28 | +0,72 ±0,53 | +0,71 ±0,84 | +0,02 / +0,05 / +0,07 | +0,06 |

**Leitura (medido):** (a) corrigir só a posição **piora** (−3,74pp no T4): o bug do topo escondia a escolha ruim (a carta de menor custo, quase sempre terreno, voltava na compra seguinte); sem escolher bem, mandar para o fundo deixa a mão sem terrenos (média de terrenos numa mão de 6 cartas com 2 mulligans: **1,44** no legado, **2,35** com a escolha). A correção só vale as duas juntas. (b) As fetches **pioram** os números (−1,35pp no T4), sem mudar a mana (T2–T4 ≈ 0): a perda é de **cor**. O modelo antigo contava **cada** Evolving Wilds/Terramorphic Expanse como fonte de W, B **e** R ao mesmo tempo (e o Rocky Tar Pit como B+R); a carta real busca **um** básico. **Raciocínio (não medido separadamente):** é isso que explica a queda, já que a mana não mudou.

## Verificações feitas ao arquivar (2026-10-03)

- **Bit-identidade com as duas correções desligadas:** 20.000/20.000 partidas idênticas no modo padrão e 20.000/20.000 no modo resiliência. **O teste achou um erro meu da rodada anterior:** na 1ª versão, 1 partida em 20.000 divergia; os 2 básicos que o Myriad Landscape busca (que entram **tapped**) contavam como mana do próprio turno para efeitos do end step (a mana "fantasma" pagava uma cópia a mais da Ultron). Agora o Myriad registra os básicos como tapped (sob `FETCHLANDS_ENABLED`, para a chave desligada continuar bit-idêntica).
- **Regressão:** 140.000 partidas (7 configurações/modos × 20.000), **0 exceções**, 0 violações de conservação dos 13 terrenos nomeados (Plains/Swamp/Mountain/Myriad Landscape/3 fetches/5 duais/Command Tower, sempre o número certo entre mão, campo, cemitério, biblioteca e exílio), 0 fetch sobrando em campo ao fim do turno quando havia alvo, 0 `total_mana` negativo: `resumos/regressao_20000.txt`.
- **Testes dirigidos:** 33/33, incluindo: tipos de terreno do simulador **iguais** aos do `type_line` do Scryfall (cache) e o conjunto de alvos do Rocky Tar Pit; fetch sacrifica, busca, embaralha, básico tapped; escolha pela cor que falta; instâncias tapped (duas Plains, uma tapped: `color_sources`=1); sem alvo não sacrifica; Rocky só no turno seguinte, escolhe Badlands/Scrubland/Plateau pelo déficit, Sunlit Marsh/Smoldering Marsh entram tapped conforme a regra; `play_turn` completo (o Rocky é sacrificado **antes** do 1º main phase do T2 e o terreno buscado já rende mana: Regra #6); 2.000 partidas reais com as invariantes.
- **Rodadas anteriores continuam reproduzíveis:** `../2026-10-03-myriad-e-tapped-t1t2/orquestracao/verificar_reproducao.sh --tudo` → 9/9 depois desta mudança (o `fx_common.flags` de lá agora desliga o mulligan novo e as fetches).
- **Reprodutibilidade desta pasta:** `bash orquestracao/verificar_reproducao.sh --tudo` → **7/7 saídas byte a byte iguais** (`cmp`): as 3 tabelas de A/B refeitas dos `.json.xz` e a **re-execução** do smoke, dos 33 testes, da bit-identidade de 20.000 partidas × 2 modos e da regressão de 140.000 partidas (`resumos/reproducao_cmp.txt`, ~1 min).

## O que NÃO foi verificado (Regra #7)

- Só foram varridas, neste arquivo, as classes: terreno (entra tapped, mana, cor, fetch), biblioteca/embaralhar/busca com restrição de tipo real, mulligan, ordem de fases (`play_turn`) e "carta no cemitério = permanente". **Não** foi feita auditoria carta a carta do `.py` inteiro.
- **Escolha de quando sacrificar a fetch:** o piloto sacrifica na hora (Evolving/Terramorphic) ou no início do turno seguinte (Rocky). Sacrificar no fim do turno do oponente, ou guardar a fetch para afinar a biblioteca mais tarde, **não** foi modelado nem medido; em mana é equivalente.
- **Regra de escolha do fundo do mulligan:** é convenção do piloto (a mesma do Edgar Markov), não do oráculo; só a variante "posição" foi medida como alternativa.
- **Nomes de carta com `flavor_name` (Regra #2):** esta rodada não compara listas; nenhuma carta foi cortada ou adicionada; o Commander Spellbook não foi consultado porque nada na lista mudou.
- Os outros 7 decks com sorteio das cartas do fundo no mulligan **não** foram alterados (ver o log do Vihaan para a lista).
