# Resultados brutos — A metade do farm com Dictate conta só os Treasures animados (2026-10-04)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Correção do simulador: a metade do farm com Dictate conta só os Treasures animados") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**

Pedido do usuário (1 frase, corrigindo a rodada anterior), transcrito sem reescrever:
> *"Metade dos tesouros animados, tesouros inanimados não trigam o Dictate!"*

Na rodada anterior (`../2026-10-04-dictate-metade/`) eu li "até metade dos treasures" como metade do **estoque inteiro** (animados + inanimados) e registrei essa leitura como "premissa minha, não confirmada". Estava errada: Treasure inanimado não é criatura, não morre como criatura e não dispara o Dictate; a metade é **dos animados**.

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

Arquivo: `vihaan-goldwaker-mardu/vihaan_goldfish_v1.py`. Código anterior = commit `9e613ea` (guardado em `codigo/vihaan_goldfish_v1_ANTES_9e613ea.py`, idêntico ao `git show 9e613ea:…` por `cmp`); o commit `8e9ab6e` (6ª rodada, o Dictate sacrifica **todos** os animados) fica em `codigo/vihaan_goldfish_v1_ANTES_8e9ab6e.py` como referência. O código novo é o do commit que adiciona esta pasta:
`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-04-dictate-metade-dos-animados`. **Uma chave; com ela desligada o arquivo é bit-idêntico ao `9e613ea`; com as chaves da 7ª e 8ª rodadas desligadas, ao `8e9ab6e`.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **Base da metade = animados** | `TREASURE_FARM_DICTATE_HALF_OF_ANIMATED_ENABLED` | `farm_animated_treasures` | quando **só o Dictate** justifica o sacrifício (sem Mahadi nem Pitiless Plunderer em campo), o teto passa de `state.treasures // 2` (estoque inteiro) para `state.treasures_animated_alive // 2` (só os animados, os únicos que são criatura). Só age com `TREASURE_FARM_DICTATE_HALF_RESERVE_ENABLED` (7ª rodada) ligada. Com Mahadi/Plunderer continua sendo de todos os animados. Nenhum campo novo no `GameState`. |

**O sacrifício em si já era só de animados** (`sacrifice_treasures` manda os animados primeiro; `farm_animated_treasures` limita `n` aos animados vivos): o erro era só a **base do teto**. Conferi por grep que `sacrifice_treasures` e o wipe de oponente são os únicos pontos que baixam `state.treasures`.
**Premissas minhas, não confirmadas pelo usuário:** (1) `animados // 2` arredonda pra baixo (com 1 animado não sacrifica nenhum); (2) o teto não vale com Mahadi/Plunderer em campo.

## Oráculo e rulings lidos antes de escrever o código (Regra #3)

`dados/oraculo_rulings_ao_vivo.json` é **cópia** do arquivo da partida manual (lido ao vivo no Scryfall em 2026-10-03, antes do código desta rodada): oráculo + 70 rulings de 29 cartas. Os que decidem aqui: **Dictate of Erebos** (um gatilho por criatura que morre; o oponente escolhe, ruling 2014-04-26), **Treasure** (a habilidade `{T}, Sacrifice` é de mana e ativável sem nada para gastar) e **Vihaan, Goldwaker** (o conjunto animado é fixado na resolução, CR 611.2c: Treasure criado depois não é criatura). Nenhuma carta foi adicionada ou cortada.

## Como os dados foram gerados

- **Variantes** (`orquestracao/fx_ab.py`; mesma semente em todas = **pareado**; IC95% = 1,96·dp/√N da diferença pareada; as diferenças da tabela são sempre contra `antes`): `antes` = commit `9e613ea` (metade do **estoque**) · `animados` = a chave nova ligada (é o que fica no repositório) · `tudo` = commit `8e9ab6e` (o Dictate sacrifica todos os animados), referência · `sem` = sensibilidade: farm com Dictate desligado (`TREASURE_FARM_WITH_DICTATE_ENABLED = False`, regra da 5ª rodada). As demais chaves do Vihaan ficam como no repositório.
- **Lotes:** `2000` = sementes `1_000_000+i` · `10000` = sementes `3_000_000+i` · cada um em modo padrão e em modo resiliência (`FX_MODO=resiliencia`). 8 turnos. Regressão: sementes `5_000_000+i`, 4 configurações (`animados`, `estoque`, `tudo`, `sem`) × 2 modos. Bit-identidade: sementes `1_000_000+i`, 20.000 partidas, 2 bases (`9e613ea` e `8e9ab6e`) × 2 modos.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`). Campos: `win_turn`, `treasures` (criados), `tend` (estoque no fim), `table_dmg`, `drain`, `combat`, `creature_deaths`, `bonus_mana` e os contadores diretos (`farm`, `farm_dic`, `dictate`, `mahadi`, `first`, …); lista completa em `resumos/indice_dados.md`. `--sum` refaz as tabelas só dos brutos.
- **Pares extras** (`orquestracao/comparar_pares.py`, só lê os brutos de 10.000): `animados − tudo` e `animados − sem` (a tabela do `fx_ab.py` só compara com `antes`).
- **Leitura das tabelas:** "Treasures criados" superestima o ganho líquido com Mahadi/Plunderer (reposição); use **estoque no fim**. `Dictate (gat.)` × 3 oponentes = proxy de criaturas de oponente forçadas a sacrificar (📊: o simulador não modela o campo do oponente).
- **Consistência com a rodada anterior:** na regressão, as contagens de `estoque`, `tudo` e `sem` são **idênticas** às de `../2026-10-04-dictate-metade/resumos/regressao_20000.txt` (padrão: 14.880 / 15.521 / 13.397 Treasures-criatura sacrificados; gatilhos do Dictate 6.884 / 7.454 / 5.535); `animados` dá 14.372 e 6.459.
- **Destino do Prosper** (`orquestracao/prosper_destino.py`): resultado **idêntico antes e depois** (mágica jogada 65,2%, terreno 67,8%, 4.633 exílios), como esperado: o teto do farm não mexe no Prosper.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/vihaan_goldfish_v1_ANTES_9e613ea.py` | simulador antes da correção (metade do estoque) | — | referência | variante `antes`, `bitident.py` (a), `prosper_destino_antes_padrao.txt` |
| `codigo/vihaan_goldfish_v1_ANTES_8e9ab6e.py` | simulador da 6ª rodada (todos os animados) | — | referência | variante `tudo`, `bitident.py` (b) |
| `dados/raw_ab_2000.json.xz` | 4 variantes × 2.000 partidas, sementes 1.000.000+, padrão | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 4 variantes × 10.000 partidas, sementes 3.000.000+, padrão | `fx_ab.py 10000` | **usado (tabela do log, "padrão")** | `resumos/ab_10000.txt`, `resumos/pares_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, 2.000, resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, 10.000, resiliência | `FX_MODO=resiliencia fx_ab.py 10000` | **usado (tabela do log, entre parênteses)** | `resumos/ab_10000_resiliencia.txt`, `resumos/pares_10000.txt` |
| `dados/oraculo_rulings_ao_vivo.json` | oráculo + 70 rulings de 29 cartas (cópia do arquivo da partida manual) | consulta direta à API | referência | checklist |
| `resumos/pares_10000.txt` | diferenças pareadas `animados − tudo` e `animados − sem` (10.000, 2 modos) | `comparar_pares.py` | **usado (log: "Pares que a tabela não mostra")** | log |
| `resumos/prosper_destino_antes_padrao.txt` / `_depois_padrao.txt` | destino de cada carta exilada pelo Prosper (N=10.000, padrão) | `prosper_destino.py` | usado (confirma que o Prosper não mudou) | log |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 19 testes dirigidos (A1–A17 + 2 invariantes de 1.500 jogos) | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS com a chave desligada × `9e613ea`, e com as 2 chaves desligadas × `8e9ab6e`: 20.000 partidas × 2 modos cada, 0 diferentes | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 8 configurações/modos (160.000): 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh --tudo` | verificação | — |
| `orquestracao/lote.sh` | roda os 4 lotes do A/B e grava os resumos | — | usado | — |

Nenhum lote superado ou inválido nesta pasta.

**Comandos que reproduzem cada tabela** (de dentro de `orquestracao/`): `python3 fx_ab.py 2000 --sum` → `ab_2000.txt` · `python3 fx_ab.py 10000 --sum` → `ab_10000.txt` · `FX_MODO=resiliencia python3 fx_ab.py {2000,10000} --sum` → `ab_*_resiliencia.txt` · `python3 comparar_pares.py` → `pares_10000.txt` · `python3 smoke.py` · `python3 testes_dirigidos.py` · `python3 bitident.py 20000 1000000` · `python3 fx_regressao.py 20000` · `FX_SIM=../codigo/vihaan_goldfish_v1_ANTES_9e613ea.py python3 prosper_destino.py 10000 3000000` (antes) e sem `FX_SIM` (depois).

**Erro de processo, registrado:** a 1ª execução de `verificar_reproducao.sh --tudo` deu `DIFERE testes_dirigidos.txt` porque eu tinha rodado os testes só no terminal e **não tinha salvo** `resumos/testes_dirigidos.txt` (e depois reescrevi a descrição de um teste). Salvei o arquivo da versão final e refiz a verificação inteira antes de arquivar; a contagem abaixo é a da execução limpa.

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` → **11/11 saídas byte a byte iguais** (`cmp`; `resumos/verificacao_reproducao.txt`): as 4 tabelas do A/B e o `pares_10000.txt` refeitos dos `.json.xz` e a **re-execução** do smoke, dos 19 testes, da bit-identidade (20.000 partidas × 2 modos × 2 bases), da regressão (160.000 partidas) e do destino do Prosper (antes e depois). A 1ª execução tinha dado 10/11 por um erro meu de processo (resumo dos testes não salvo; ver acima); refeita inteira depois de salvá-lo.
**Os 9 arquivos anteriores do Vihaan foram reverificados com `--tudo` contra o simulador vivo (com a chave nova ligada por padrão):** `dictate-metade` 10/10, `exilio-sempre-e-dictate` 10/10, `exilio-primeiro-e-mahadi` 10/10, `fora-da-mao` 8/8, `sephiroth` 11/11, `treasure-animado-e-mulligan` 7/7, `kingpin` 11/11, `inevitable-defeat` 6/6, `partida-manual-1` 7/7. Só o `dictate-metade` precisou de ajuste: seu `orquestracao/fx_common.py` agora desliga a chave nova (pra reproduzir o simulador do commit dela, metade do estoque) e seu `prosper_destino.py` passa por `F.flags` (o mesmo erro de carregar o simulador vivo sem desligar chaves que já tinha acontecido na rodada anterior; desta vez corrigido antes de a verificação falhar). Os `SHA256SUMS` dele foram regenerados e o `LEIAME.md` dele ganhou uma nota.
**Não conferido byte a byte:** a leitura do oráculo no Scryfall (guardada em `dados/oraculo_rulings_ao_vivo.json`, não refeita por `cmp`).

## O que NÃO foi verificado (Regra #7)

- Só foram varridos, neste arquivo, `farm_animated_treasures` (a base do teto), `sacrifice_treasures` e os 2 pontos que baixam `state.treasures` (grep). **Não** foi auditoria carta a carta.
- O **valor** dos sacrifícios do Dictate no oponente é 📊 (só se conta o uso: `dictate_triggers_total` × 3 oponentes). O simulador sacrifica **exatamente o teto** (`animados // 2`) quando há animados; uma jogada real sacrifica o que o campo do oponente pede.
- As duas premissas acima (arredondar pra baixo; teto não vale com Mahadi/Plunderer) não foram confirmadas pelo usuário.
- Lotho/Monologue Tax em 2ª mágica de **oponente** continuam 📊. Sem resposta: a cópia da Sevinne's no T8 e a Blood Money que expirou no T8.
- Nenhuma carta foi cortada ou adicionada à lista; o Commander Spellbook não foi consultado porque nada na lista mudou.

## Nota de 2026-10-04 (9ª rodada: `../2026-10-04-wipes-proprios/`)

- **As 5 chaves novas** (wipes próprios: destruição fiel, Treasure virado, custo da Blasphemous Act, retenção; imposto do comandante) vêm **ligadas** no simulador vivo. O `orquestracao/fx_common.py` desta pasta as **desliga** (e inclui os 7 campos novos do `GameState` em `NOVOS`) pra continuar reproduzindo o simulador do commit dela.
- O `orquestracao/smoke.py` desta pasta carregava o simulador vivo **sem passar por `F.flags`** (as 200 partidas rodavam com as chaves novas ligadas e o `smoke.txt` deu `DIFERE` na 1ª execução); passou a usar `F.flags(F.carrega(...))` e o `cmp` voltou a bater.
- `verificar_reproducao.sh --tudo` depois da 9ª rodada: 11/11 depois de corrigir o smoke. `SHA256SUMS` regenerado.
