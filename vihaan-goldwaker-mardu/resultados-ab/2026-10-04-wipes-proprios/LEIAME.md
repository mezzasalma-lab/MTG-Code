# Resultados brutos — Wipes próprios (Blood Money / Blasphemous Act) e imposto do comandante (2026-10-04)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Respostas do T8 (Sevinne's, Blood Money, Lotho + Tax) e correção do simulador: wipes próprios e imposto do comandante") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**

Respostas do usuário (3 frases), transcritas sem reescrever:
> *"A cópia da Sevinne trouxe o Zulaport de volta*
> *Blood money ficou exilada permanentemente, mesmo que ela gerasse muitos tesouros, sem Vihaan e Mahadi em campo acho que seria pior!*
> *Lotho e Tax eu considerei que 1 dos 3 oponentes jogou 2 mágicas no mesmo turno e por isso perdi 1 de vida e criei 2 tesouros!"*

A 1ª e a 3ª são registro (ver `../2026-10-03-partida-manual-1/LEIAME.md`): a cópia da Sevinne's já estava modelada; a conta de Lotho + Tax bate com o oráculo e continua 📊 no simulador. A 2ª é a linha de jogo do usuário (**segurar** a Blood Money quando ela destruiria Vihaan e Mahadi) e, ao auditar a carta cláusula a cláusula, apareceram erros reais no wipe próprio e no imposto do comandante, corrigidos aqui.

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

Arquivo: `vihaan-goldwaker-mardu/vihaan_goldfish_v1.py`. Código anterior = commit `bf8a6f6` (guardado em `codigo/vihaan_goldfish_v1_ANTES_bf8a6f6.py`, idêntico ao `git show bf8a6f6:…` por `cmp`); o código novo é o do commit que adiciona esta pasta:
`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-04-wipes-proprios`. **5 chaves, todas ligadas por padrão; com as 5 desligadas o arquivo é bit-idêntico ao `bf8a6f6`.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **Destruição de verdade** | `OWN_WIPE_DESTROY_ORACLE_ENABLED` | `_own_wipe_destroy_all`, ramos `Blood Money` / `Blasphemous Act` de `resolve_instant_sorcery`, `on_creature_dies` | "Destroy all creatures": inclui o **comandante** (zona de comando, CR 903.9a), os **Treasures animados** vivos e as fichas; é destruição, **não sacrifício** (Mayhem Devil não reage); morte **simultânea** (os gatilhos olham pra trás: todos os eventos são disparados com o campo cheio e só depois as peças saem; o Plunderer nunca dispara pela própria morte) |
| **Treasure virado** | `BLOOD_MONEY_TAPPED_TREASURE_ENABLED` | `create_treasures(tapped=)`, `total_mana`, `sacrifice_treasures`, `farm_animated_treasures`, `combat_step`, `play_turn` | "create a **tapped** Treasure": campo novo `treasures_tapped` (contador agregado); não paga mana nem entra no farm no turno; sacrifício fora da mana leva os virados primeiro; desvira no meu próximo turno; animado virado não ataca; o wipe do oponente zera o contador |
| **Custo da Blasphemous Act** | `BLASPHEMOUS_ACT_COST_REDUCTION_ENABLED` | `spell_cost`, `creatures_on_battlefield`, `can_cast`, `cast_card` | "costs {1} less for each creature on the battlefield", piso {R}; só as **minhas** criaturas (as do oponente são 📊) |
| **Retenção (linha do usuário)** | `OWN_WIPE_HOLD_ENGINE_ENABLED` | `wipe_held`, `main_phase`, `play_from_impulse` | não conjura Blood Money nem Blasphemous Act se `commander_in_play` **ou** Mahadi em campo (inclui a carta exilada pelo Prosper, que expira) |
| **Imposto do comandante** | `COMMANDER_TAX_ENABLED` | `spell_cost`, `cast_card`, `enter_battlefield` | CR 903.8: o imposto ({2} por cast anterior) entra no `can_cast`; o cast anulado também conta |

**Premissas minhas, não confirmadas pelo usuário:** (a) a retenção vale também para a Blasphemous Act; (b) "segurar" com Vihaan **ou** Mahadi em campo (não só os dois juntos); (c) Treasures virados como contador agregado (não rastreia quais são animados).

## Oráculo e rulings lidos antes de escrever o código (Regra #3)

`dados/oraculo_rulings_ao_vivo_9a_rodada.json`: oráculo, tipo, custo e **rulings** de 9 cartas, lidos ao vivo no Scryfall em 2026-10-04, **antes** do código: Blood Money, Sevinne's Reclamation, Lotho, Monologue Tax, Mayhem Devil, Blasphemous Act, Vihaan, Mahadi, Pitiless Plunderer. Os que decidem: **Blood Money** (destrói todas as criaturas; 1 Treasure **virado** por não-ficha destruída; ruling 2022-06-10), **Mayhem Devil** (só **sacrifício**), **Pitiless Plunderer** (dispara pelas outras que morrem junto, ruling 2018-01-19), **Blasphemous Act** (piso {R}, MV 9, ruling 2020-11-10), **Sevinne's** (a cópia não é conjurada, 2019-08-23), **Lotho** (2ª mágica de **qualquer** jogador) e **Monologue Tax** (só de oponente, 1 vez por oponente por turno), **Vihaan** (Legendary Creature; animados são artefato-criatura até o fim do turno). Nenhuma carta foi adicionada ou cortada.

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada; as diferenças da tabela são sempre contra `antes`; chaves não citadas ficam desligadas): `antes` = commit `bf8a6f6` · `imposto` · `oraculo` (destruição + virado) · `custo` · `hold` (só a retenção, sobre o código antigo do wipe) · `sem_hold` (tudo menos a retenção) · `todas` (as 5, o que fica no repositório).
- **Lotes:** `2000` = sementes `1_000_000+i` · `10000` = sementes `3_000_000+i` · cada um em modo padrão e em modo resiliência (`FX_MODO=resiliencia`). 8 turnos. Regressão: sementes `5_000_000+i`, 3 configurações (`todas`, `sem_hold`, `antes`) × 2 modos. Bit-identidade: sementes `1_000_000+i`, 20.000 partidas × 2 modos.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`); lista completa de campos em `resumos/indice_dados.md`. `--sum` refaz as tabelas só dos brutos.
- **Contagem comparável entre `antes` e as demais:** o snapshot antigo não tem os contadores novos (`own_wipes_cast_total` etc.), então as colunas "Blood Money", "Blasphemous Act", "wipe com Vihaan|Mahadi" e "Vihaan destruído" vêm de um **espião em `resolve_instant_sorcery`** aplicado igualmente a todas as variantes (lição da rodada do Dictate: colunas lidas de contadores ausentes no código antigo dão 0 enganoso). "Retenções" e "Treasures virados" só existem nas variantes novas (`n/a` no `antes`).
- **Pares extras** (`orquestracao/comparar_pares.py`, só lê os brutos de 10.000): `todas − sem_hold` (efeito da retenção) e `sem_hold − oraculo` (efeito do custo da Act + imposto, dada a destruição).
- **Destino do Prosper** (`orquestracao/prosper_destino.py`): para cada carta que o Prosper exila no end step, se foi jogada, expirou ou ainda era válida no fim; nesta rodada também por carta (wipes próprios exilados: 88 → 89, **conjurados 27 → 0**, expiraram 22 → 49). `FX_SIM=` aponta o simulador (snapshot `bf8a6f6` para o "antes").
- **Limite (Regra #5):** o simulador não tem criaturas de oponente: nele o wipe só destrói o campo **do jogador**, então o ganho da retenção é verdadeiro por construção e **não mede** o benefício real do wipe contra os campos dos oponentes (📊).

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/vihaan_goldfish_v1_ANTES_bf8a6f6.py` | simulador antes da correção | — | referência | variante `antes`, `bitident.py`, `prosper_destino_antes_padrao.txt` |
| `dados/raw_ab_2000.json.xz` | 7 variantes × 2.000 partidas, sementes 1.000.000+, padrão | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 7 variantes × 10.000 partidas, sementes 3.000.000+, padrão | `fx_ab.py 10000` | **usado (tabela do log, "padrão")** | `resumos/ab_10000.txt`, `resumos/pares_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, 2.000, resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, 10.000, resiliência | `FX_MODO=resiliencia fx_ab.py 10000` | **usado (tabela do log, entre parênteses)** | `resumos/ab_10000_resiliencia.txt`, `resumos/pares_10000.txt` |
| `dados/oraculo_rulings_ao_vivo_9a_rodada.json` | oráculo + rulings de 9 cartas, ao vivo | consulta direta à API | referência | checklist |
| `resumos/pares_10000.txt` | diferenças pareadas `todas − sem_hold` e `sem_hold − oraculo` (10.000, 2 modos) | `comparar_pares.py` | **usado (log: "Pares que a tabela não mostra")** | log |
| `resumos/prosper_destino_antes_padrao.txt` / `_depois_padrao.txt` | destino de cada carta exilada pelo Prosper (N=10.000, padrão), com quebra por carta | `prosper_destino.py` | **usado (log: "Destino das cartas que o Prosper exila")** | log |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 34 testes dirigidos (W1–W9, H1–H6, X1–X2 + 4 invariantes de 2.000 jogos) | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS com as 5 chaves desligadas × `bf8a6f6`: 20.000 partidas × 2 modos, 0 diferentes | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 6 configurações/modos (120.000): 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh --tudo` | verificação | — |
| `orquestracao/lote.sh` | roda os 4 lotes do A/B e grava os resumos | — | usado | — |

Nenhum lote superado ou inválido nesta pasta, **exceto** a 1ª tentativa de `lote.sh`, que falhou com `TypeError: ct() got an unexpected keyword argument 'tapped'` (o espião de `create_treasures` do `fx_ab.py` não aceitava o argumento novo `tapped=`): não gerou nenhum bruto nem tabela (os 4 `.txt` ficaram vazios e foram sobrescritos); corrigi o espião (`**kw`) e refiz os 4 lotes. A bit-identidade e a regressão já tinham rodado e não dependem do `fx_ab.py`.

**Comandos que reproduzem cada tabela** (de dentro de `orquestracao/`): `python3 fx_ab.py 2000 --sum` → `ab_2000.txt` · `python3 fx_ab.py 10000 --sum` → `ab_10000.txt` · `FX_MODO=resiliencia python3 fx_ab.py {2000,10000} --sum` → `ab_*_resiliencia.txt` · `python3 comparar_pares.py` → `pares_10000.txt` · `python3 smoke.py` · `python3 testes_dirigidos.py` · `python3 bitident.py 20000 1000000` · `python3 fx_regressao.py 20000` · `FX_SIM=../codigo/vihaan_goldfish_v1_ANTES_bf8a6f6.py python3 prosper_destino.py 10000 3000000` (antes) e sem `FX_SIM` (depois).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` → **11/11 saídas byte a byte iguais** (`cmp`; `resumos/verificacao_reproducao.txt`): as 4 tabelas do A/B e o `pares_10000.txt` refeitos dos `.json.xz` e a **re-execução** do smoke, dos 34 testes, da bit-identidade (20.000 partidas × 2 modos), da regressão (120.000 partidas) e do destino do Prosper (antes e depois).
**Os 10 arquivos anteriores do Vihaan foram reverificados com `--tudo` contra o simulador vivo (com as 5 chaves novas ligadas por padrão):** `exilio-primeiro-e-mahadi` 10/10, `fora-da-mao` 8/8, `sephiroth` 11/11, `treasure-animado-e-mulligan` 7/7, `kingpin` 11/11, `inevitable-defeat` 6/6, `partida-manual-1` 7/7 (esses 7 só precisaram, quando precisaram, que o `fx_common.py` desligasse as chaves novas e ignorasse os campos novos do `GameState`); e **3 deram `DIFERE smoke.txt` na 1ª execução** (`exilio-sempre-e-dictate` 9/10, `dictate-metade` 9/10, `dictate-metade-dos-animados` 10/11): o `smoke.py` deles carregava o simulador vivo **sem passar por `F.flags`**, então as 200 partidas do teste rodavam com as chaves novas ligadas (mudou a contagem de partidas com animados sacrificados). Corrigi os 3 scripts (`V = F.flags(F.carrega(...))`) e o `smoke.txt` de cada um voltou a bater por `cmp`; as outras saídas já tinham dado IGUAL na mesma execução (não repeti o `--tudo` inteiro depois do ajuste, só o `cmp` do smoke). Os `SHA256SUMS` das 7 pastas com `fx_common.py` ajustado (`sephiroth`, `fora-da-mao`, `exilio-primeiro-e-mahadi`, `treasure-animado-e-mulligan`, `exilio-sempre-e-dictate`, `dictate-metade`, `dictate-metade-dos-animados`) foram regenerados e o `LEIAME.md` de cada uma ganhou uma nota.
**Não conferido byte a byte:** a leitura do oráculo e das rulings no Scryfall (guardada em `dados/oraculo_rulings_ao_vivo_9a_rodada.json`, não refeita por `cmp`).

## O que NÃO foi verificado (Regra #7)

- Só foram varridos, neste arquivo, a resolução da Blood Money e da Blasphemous Act, o custo da Blasphemous Act, o imposto do comandante, a mana/farm/combate com Treasure virado, `on_creature_dies` (morte própria do Plunderer) e os pontos que baixam `state.treasures` (grep). **Não** foi auditoria carta a carta.
- O **benefício** do wipe contra os campos dos oponentes e os Treasures por criaturas não-ficha deles é 📊 (o simulador não modela criatura de oponente).
- As 3 premissas acima (retenção também na Blasphemous Act; "Vihaan ou Mahadi"; contador agregado de virados) não foram confirmadas pelo usuário.
- Lotho/Monologue Tax em 2ª mágica de **oponente** continuam 📊 (convenção do usuário: 1 dos 3 oponentes, 2 mágicas).
- Nenhuma carta foi cortada ou adicionada à lista; o Commander Spellbook não foi consultado porque nada na lista mudou.

## Nota de 2026-10-04 (10ª rodada: `../2026-10-04-wipes-segurados/`)

- **As 3 chaves novas** (todo wipe próprio segurado; custo do wipe pago primeiro com Treasures animados; exceção mitigada com Mayhem Devil) vêm **ligadas** no simulador vivo. O `orquestracao/fx_common.py` desta pasta as **desliga** (e inclui os 3 campos novos do `GameState` em `NOVOS`) pra continuar reproduzindo o simulador do commit dela.
- O `orquestracao/smoke.py` desta pasta carregava o simulador vivo **sem passar por `F.flags`**; passou a usar `F.flags(F.carrega(...))` (o `cmp` do smoke foi conferido isolado antes da verificação completa).
- **Princípio mais geral do usuário (mesmo dia):** a retenção desta pasta (só com Vihaan/Mahadi em campo; Blasphemous Act por palpite meu) foi generalizada para **todo wipe segurado**, com exceção mitigada: ver `../2026-10-04-wipes-segurados/`. Os números desta pasta descrevem a regra do commit `47ec126`.
- `verificar_reproducao.sh --tudo` depois da 10ª rodada: 11/11. `SHA256SUMS` regenerado.

## Nota de 2026-10-04 (11ª rodada: `../2026-10-04-blasphemous-edict/`)

- **A chave nova** (`MIRKWOOD_BATS_SACRIFICE_ONLY_ENABLED`: o Mirkwood Bats só dispara em sacrifício de ficha, não em ficha destruída) vem **ligada** no simulador vivo. O `orquestracao/fx_common.py` desta pasta a **desliga** (bloco anexado ao fim do `flags()`; nenhum campo novo do `GameState`) pra continuar reproduzindo o simulador do commit dela.
- `verificar_reproducao.sh --tudo` depois da 11ª rodada: 11/11. `SHA256SUMS` regenerado.
