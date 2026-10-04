# Resultados brutos — Avaliação: Blasphemous Act × Blasphemous Edict, e Mirkwood Bats só em sacrifício (2026-10-04)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Avaliação: trocar Blasphemous Act por Blasphemous Edict") e em `vihaan-goldwaker-mardu/checklist-oraculo.md`.
**Esta pasta guarda os dados por trás delas.**

Pergunta do usuário, transcrita sem reescrever:
> *"Pensando nisso agora, não seria melhor trocar o Blasphemous Act por um wipe que sacrifica as criaturas, como por exemplo: Blasphemous Edict?"*

**Nada foi trocado na lista** (decisão do usuário; `lista.md` intacta). Esta rodada tem duas partes: (1) a **avaliação da troca** (oráculo/rulings ao vivo, Commander Spellbook antes/depois com controle positivo, enumeração por script, ensaio a seco no simulador); (2) um **achado lateral corrigido no simulador** ao comparar "destruir" com "sacrificar": o Mirkwood Bats disparava em ficha destruída.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` (rápido, só lê os `.json.xz`); `--tudo` re-executa também smoke, testes, bit-identidade, regressão e o ensaio a seco |
| abrir os brutos por partida em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta; o `LEIAME.md` e o próprio `SHA256SUMS` ficam de fora) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## O que foi alterado no simulador (1 chave)

Arquivo: `vihaan-goldwaker-mardu/vihaan_goldfish_v1.py`. Código anterior = commit `b30ef1f` (guardado em `codigo/vihaan_goldfish_v1_ANTES_b30ef1f.py`, idêntico ao `git show b30ef1f:…` por `cmp`); o código novo é o do commit que adiciona esta pasta:
`git log -1 -- vihaan-goldwaker-mardu/resultados-ab/2026-10-04-blasphemous-edict`. **Com a chave desligada o arquivo é bit-idêntico ao `b30ef1f`.**

| correção | chave | onde | o que faz |
|---|---|---|---|
| **Mirkwood Bats só em sacrifício** | `MIRKWOOD_BATS_SACRIFICE_ONLY_ENABLED` | `on_token_leaves(…, sacrificed=)`, `on_permanent_destroyed`, `_own_wipe_destroy_all` | oráculo ao vivo: *"Whenever you create or **sacrifice** a token, each opponent loses 1 life"*: ficha **destruída** (wipe próprio, remoção/wipe do oponente) não o dispara; Nadier's Nightblade (*"leaves the battlefield"*) dispara nas duas. Nenhum campo novo no `GameState` |

**A Blasphemous Edict NÃO foi adicionada ao `vihaan_goldfish_v1.py`**: ela só existe no harness `orquestracao/edict_harness.py` (`instala(V)` registra a carta, o custo 5/{B}, a resolução por sacrifício e a inclui em `OWN_WIPES`), usado pelos testes e pelo ensaio a seco.

## Oráculo, rulings e pesquisas ao vivo (Regra #3)

- `dados/oraculo_rulings_ao_vivo.json`: oráculo, tipo, custo e **rulings** de 19 cartas lidos ao vivo no Scryfall em 2026-10-04 (`orquestracao/scryfall_ao_vivo.py`): Blasphemous Edict, Blasphemous Act, Mayhem Devil, Mirkwood Bats, Nadier's Nightblade, Zulaport, Plunderer, Mahadi, Dictate, Rain of Riches, Blood Money, Marionette Master, Agent of the Iron Throne, Life Insurance, Captain Lannery Storm, Sephiroth, Vihaan, Anointed Procession, Kambal.
- `dados/oraculo_lista_ao_vivo.json.xz`: oráculo **cru** das 94 cartas distintas da lista + a Edict (`/cards/collection`, com fallback por `flavor_name`, Regra #2: as 94 resolveram; 2 por nome de face dupla) usado pela enumeração (`orquestracao/enumeracao.py`).
- `dados/scryfall_buscas.json`: busca de Game Changer (a Edict **não** é) e lista de outras magias de sacrifício em R/W/B legais em Commander (**só listadas**, não avaliadas).
- `dados/spellbook_cru.json.xz` (resposta **crua**) e `dados/spellbook_resumo.json`: Commander Spellbook `find-my-combos` para a lista atual, `+Edict`, `−Act`, `−Act +Edict` e 3 controles positivos (`orquestracao/csb_edict.py`, derivado do `csb_generic.py` do arquivo do Kingpin).

## Como os dados foram gerados

- **Ensaio a seco** (`orquestracao/edict_dry_run.py`, padrão, sementes `3_000_000+i`, N=10.000, 119.958 estados com turno ≥ 3): a cada fase principal copia o `GameState` (deepcopy) e conjura cada wipe em cópias separadas pelo `cast_card` real (custo da Act reduzido, custo 5 da Edict, pagamento primeiro com animados, gatilhos), **sem a retenção** (só pra medir); registra o que cada um causa **no meu lado**; estratos: com/sem Mayhem Devil, 1ª main × 2ª main, 4+ animados. **Não mede o campo do oponente (📊).**
- **A/B pareado da chave do Bats** (`orquestracao/fx_ab.py`; mesma semente = pareado; IC95% = 1,96·dp/√N): variantes `antes` (`b30ef1f`) e `bats`; lotes `2000` (sementes `1_000_000+i`) e `10000` (`3_000_000+i`), modos padrão e resiliência (`FX_MODO=resiliencia`), 8 turnos. A coluna "dreno atribuível ao Bats" vem de um espião em `on_token_leaves` aplicado igualmente às duas variantes (o snapshot antigo não tem o argumento `sacrificed`).
- **Regressão** (`fx_regressao.py`): sementes `5_000_000+i`, 2 configurações (`bats`, `antes`) × 2 modos × 20.000. **Bit-identidade** (`bitident.py`): sementes `1_000_000+i`, 20.000 × 2 modos.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`); campos em `resumos/indice_dados.md`. `--sum` refaz as tabelas só dos brutos.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `codigo/vihaan_goldfish_v1_ANTES_b30ef1f.py` | simulador antes da correção do Bats | — | referência | variante `antes`, `bitident.py` |
| `dados/oraculo_rulings_ao_vivo.json` | oráculo + rulings de 19 cartas, ao vivo | `scryfall_ao_vivo.py` | **usado (log: "Oráculo")** | checklist |
| `dados/oraculo_lista_ao_vivo.json.xz` | oráculo cru das 94 cartas da lista + Edict | `enumeracao.py` | **usado** | `resumos/enumeracao.txt` |
| `dados/scryfall_buscas.json` | Game Changer + outras magias de sacrifício | `scryfall_buscas.py` | usado | `resumos/scryfall_buscas.txt` |
| `dados/spellbook_cru.json.xz`, `dados/spellbook_resumo.json` | Commander Spellbook antes/depois + controles | `csb_edict.py` | **usado (log: "Documentação do deck e Commander Spellbook")** | `resumos/spellbook.txt` |
| `dados/raw_ab_2000.json.xz` | 2 variantes × 2.000 partidas, padrão | `fx_ab.py 2000` | usado | `resumos/ab_2000.txt` |
| `dados/raw_ab_10000.json.xz` | 2 variantes × 10.000, padrão | `fx_ab.py 10000` | **usado (log: achado lateral)** | `resumos/ab_10000.txt` |
| `dados/raw_ab_2000_resiliencia.json.xz` | idem, 2.000, resiliência | `FX_MODO=resiliencia fx_ab.py 2000` | usado | `resumos/ab_2000_resiliencia.txt` |
| `dados/raw_ab_10000_resiliencia.json.xz` | idem, 10.000, resiliência | `FX_MODO=resiliencia fx_ab.py 10000` | **usado (log: achado lateral)** | `resumos/ab_10000_resiliencia.txt` |
| `resumos/edict_dry_run_10000.txt` | ensaio a seco Act × Edict (10.000 partidas) | `edict_dry_run.py 10000 3000000` | **usado (tabela do log)** | log: "Medido no simulador" |
| `resumos/enumeracao.txt` | varredura por script (sacrifício, morte, destroy, indestrutível, fichas…) | `enumeracao.py` | **usado** | log / checklist |
| `resumos/spellbook.txt` | saída do Spellbook (combos que somem/surgem, "quase") | `csb_edict.py` | **usado** | log |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 15 testes dirigidos (Bats e semântica da Edict) | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/bitident_flags_off_20000.txt` | DEPOIS com a chave desligada × `b30ef1f`: 20.000 × 2 modos, 0 diferentes | `bitident.py 20000 1000000` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 partidas × 4 configurações/modos (80.000): 0 exceções + invariantes | `fx_regressao.py 20000` | verificação | log: validação |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh --tudo` | verificação | — |
| `orquestracao/edict_harness.py` | a Edict como harness (não está no simulador) | — | usado | testes, ensaio a seco |

Nenhum lote superado ou inválido nesta pasta.

**Comandos que reproduzem cada tabela** (de dentro de `orquestracao/`): `python3 fx_ab.py 2000 --sum` → `ab_2000.txt` · `python3 fx_ab.py 10000 --sum` → `ab_10000.txt` · `FX_MODO=resiliencia python3 fx_ab.py {2000,10000} --sum` → `ab_*_resiliencia.txt` · `python3 edict_dry_run.py 10000 3000000` → `edict_dry_run_10000.txt` · `python3 smoke.py` · `python3 testes_dirigidos.py` · `python3 bitident.py 20000 1000000` · `python3 fx_regressao.py 20000`. **Pesquisas à API** (a partir da raiz do repositório, `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt`): `python3 vihaan-goldwaker-mardu/resultados-ab/2026-10-04-blasphemous-edict/orquestracao/{scryfall_ao_vivo,enumeracao,scryfall_buscas,csb_edict}.py`.

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` → **9/9 saídas byte a byte iguais** (`cmp`; `resumos/verificacao_reproducao.txt`): as 4 tabelas do A/B refeitas dos `.json.xz` e a **re-execução** do smoke, dos 15 testes, da bit-identidade (20.000 partidas × 2 modos), da regressão (80.000 partidas) e do ensaio a seco Act × Edict (10.000 partidas).
**Os 12 arquivos anteriores do Vihaan foram reverificados com `--tudo` contra o simulador vivo (com a chave nova ligada por padrão), todos iguais, sem `DIFERE`:** `wipes-segurados` 11/11, `wipes-proprios` 11/11, `dictate-metade-dos-animados` 11/11, `dictate-metade` 10/10, `exilio-sempre-e-dictate` 10/10, `exilio-primeiro-e-mahadi` 10/10, `fora-da-mao` 8/8, `sephiroth` 11/11, `treasure-animado-e-mulligan` 7/7, `kingpin` 11/11, `inevitable-defeat` 6/6, `partida-manual-1` 7/7. Para isso, o `orquestracao/fx_common.py` de 9 deles (`sephiroth`, `fora-da-mao`, `exilio-primeiro-e-mahadi`, `treasure-animado-e-mulligan`, `exilio-sempre-e-dictate`, `dictate-metade`, `dictate-metade-dos-animados`, `wipes-proprios`, `wipes-segurados`) passou a **desligar a chave nova** (o bloco foi anexado ao fim do `flags()` de cada um; nenhum campo novo do `GameState`, então `NOVOS` não mudou). Os `SHA256SUMS` dessas 9 pastas foram regenerados e o `LEIAME.md` de cada uma ganhou uma nota.
**Não conferido byte a byte:** tudo que vem da API ao vivo (`oraculo_rulings_ao_vivo.json`, `oraculo_lista_ao_vivo.json.xz`, `scryfall_buscas.json`, `spellbook_*`, `resumos/enumeracao.txt`, `resumos/spellbook.txt`, `resumos/scryfall_buscas.txt`): as respostas **cruas estão guardadas**, mas uma nova consulta pode devolver dados diferentes (cartas, rulings e combos mudam), então não entram no `cmp`.

## O que NÃO foi verificado (Regra #7)

- O efeito da Edict e do Act **no campo dos oponentes** (📊: o simulador não modela criatura de oponente); o ensaio a seco é só o **meu** lado e é piso da Edict. A convenção "o Act só conta as minhas criaturas" favorece a Edict em castabilidade.
- A frequência real, **nas mesas do usuário**, de indestrutível/proteção, de 14+ criaturas e do Mayhem Devil.
- O corte Blood Money × Edict e as outras magias de sacrifício listadas (By Invitation Only, Tragic Arrogance, Tergrid's Shadow, Barter in Blood, Taste of Death, Necrotic Hex): **só listadas**.
- A Edict **não está** no `vihaan_goldfish_v1.py`; o harness não passa por hold/hold-always além do que `cast_card` já faz.
- Só foram varridos, no simulador, `on_token_leaves`, `on_permanent_destroyed` e `_own_wipe_destroy_all` (grep): **não** foi auditoria carta a carta.
- Nenhuma carta foi cortada ou adicionada à lista.
