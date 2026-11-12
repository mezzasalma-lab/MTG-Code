# Resultados brutos — Avaliação: algum wipe de sacrifício válido no deck muda os números e a avaliação da Edict? (2026-10-04)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Vihaan, Goldwaker. As conclusões e as tabelas legíveis estão em
`vihaan-goldwaker-mardu/goldfish-log.md` (seção "Avaliação: algum wipe de sacrifício válido no deck muda os números e a avaliação da Edict?") e em `vihaan-goldwaker-mardu/checklist-oraculo.md` (seção do topo, cláusula a cláusula).
**Esta pasta guarda os dados por trás delas.**

Pergunta do usuário, transcrita sem reescrever:
> *"Algum wipe de sacrifício valido no deck muda esses números e avaliação?"*

**Nada foi trocado na lista** (decisão do usuário; `lista.md` intacta) e **o simulador não foi alterado**: `vihaan_goldfish_v1.py` fica no commit `a17049f` (SHA-256 `b7f08615fdc576624924b25db57968b827ae6defda03cd6f9a460ec78cb9a49b`). Todas as cartas candidatas existem só no harness `orquestracao/sac_harness.py`; o Blasphemous Act e o Blood Money, que já estão na lista, são medidos pelo simulador. Esta rodada tem uma parte só: a **avaliação** (busca ampla ao vivo, oráculo/rulings ao vivo, Commander Spellbook antes/depois com controle positivo, enumeração por script, ensaio a seco no simulador, aritmética do lado dos oponentes).

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (a seção mais nova fica no topo) |
| ver a tabela pronta de um resultado | `resumos/` (um `.txt` por tabela; mapa abaixo) |
| refazer as tabelas a partir dos dados | `bash orquestracao/verificar_reproducao.sh` (rápido, só lê os `.json.xz`); `--tudo` re-executa também smoke, testes, enumeração, efeitos unilaterais e os 4 lotes do ensaio a seco (~25 min) |
| abrir os brutos por estado em JSON | `bash descomprimir.sh` (cria `dados_json/`, ignorado pelo git) |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta; o `LEIAME.md` e o próprio `SHA256SUMS` ficam de fora) |
| saber o que há em cada arquivo de dados | `resumos/indice_dados.md` (gerado por `python3 indice_dados.py`) |

## Oráculo, rulings e pesquisas ao vivo (Regra #3: lidos ANTES de modelar)

- `dados/busca_ampla_cru.json.xz`: resposta **crua** do Scryfall (`/cards/search`, todas as páginas) de **10 formulações** de busca de sacrifício em massa (`f:commander id<=rwb`), `orquestracao/busca_ampla.py`. `dados/busca_ampla_classificada.json`: a união (348 cartas, por `oracle_id`) classificada **por script** (quem sacrifica, o quê, quanto): 141 "em massa", 164 "edict de 1", 20 só de terreno, 23 outras; `resumos/busca_ampla.txt` é a saída legível.
- `dados/oraculo_candidatas_rulings.json`: oráculo completo (todas as faces), tipo, custo, cor, poder, legalidade, Game Changer e **rulings** (248) de **63 cartas** (as candidatas, as unilaterais, as excluídas e as do deck que decidem: Mayhem Devil, Dictate, Teferi's Protection, Boros Charm...), lidos ao vivo em 2026-10-04 (`orquestracao/oraculo_candidatas.py`); `resumos/oraculo_candidatas.txt` é a saída legível. Das 17 candidatas, **todas legais em Commander e nenhuma Game Changer** (o único Game Changer entre as 63 é o Teferi's Protection, que já está na lista).
- `dados/oraculo_lista_ao_vivo.json.xz`: oráculo **cru** das 94 cartas distintas da lista + comandante (cópia do arquivo da rodada `2026-10-04-blasphemous-edict`, lido ao vivo no mesmo dia, Regra #2: `flavor_name` checado lá). Usado pelo harness (tipos de criatura, poder, cores, mana produzida) e pela enumeração.
- `dados/spellbook_cru.json.xz` (resposta **crua**, 39 consultas) e `dados/spellbook_resumo.json`: Commander Spellbook `find-my-combos` para a lista atual, `−Act`, 3 controles positivos e, para cada uma das **17 candidatas**, `+X (sem cortar)` e `−Act +X (a troca)` (`orquestracao/csb_wipes.py`).

## Como os dados foram gerados

- **Harness** (`orquestracao/sac_harness.py`): um executor de **sacrifício simultâneo** (`sacrificar`: Mayhem Devil dispara por cada permanente sacrificada, de qualquer tipo; mortes com look-back; Mirkwood Bats só em sacrifício de ficha; comandante vai à zona de comando) e **um resolvedor por carta**. Convenções: o jogador sacrifica primeiro os Treasures animados, depois Constructs, fichas, Dragões e só então as criaturas nomeadas de menor MV, guardando por último Vihaan, Mahadi e Mayhem Devil (ordem estável do campo nos empates); o custo é pago primeiro com Treasures animados (política da 10ª rodada), **exceto Winnowing** (convoke: as criaturas pagam sem morrer). Variantes: Edict; By Invitation Only com 3 políticas de N (`13`, `motores`, `fodder`); Barter in Blood; Tergrid's Shadow; Rankle's Prank (modos *perder 4* + *sacrificar 2*); Taste of Death; Necrotic Hex; Liliana (−4 + compra); Zodiark; Meathook Massacre II (X máximo); Mythos of Snapdax e Tragic Arrogance (guardo 1 criatura, 1 artefato, 1 encantamento); Winnowing (2 políticas: guardo o Vihaan, ou guardo os animados); Slaughter the Strong; Living Death; Scrap Mastery; All Is Dust. **Referências** (já na lista, simulador puro): Blasphemous Act e Blood Money.
- **Ensaio a seco** (`orquestracao/sac_dry_run.py`): a cada fase principal (turno ≥ 3) de partidas naturais, copia o `GameState` (deepcopy) e conjura cada variante em cópias separadas pelo `cast_card` real (custo, pagamento, gatilhos), **sem a retenção** (só para medir). Registra o que cada uma causa **no meu lado**, a castabilidade por mana e por **cor** (`fontes`/`pips_ok`: as fontes em campo cobrem os símbolos de cor? otimista: ignora o mana já gasto no turno) e invariantes de estado. Dois modos: padrão e resiliência (estados sob pressão de interação de oponente). Lote principal: 10.000 partidas, sementes `3_000_000+i`; regressão: 20.000 partidas, sementes `5_000_000+i`, por modo. IC95% = 1,96·dp/√n **ingênuo** (estados da mesma partida não são independentes).
- **Aritmética do lado dos oponentes** (`orquestracao/paridade_oponente.py`, a partir do bruto): com `c` criaturas por oponente, `3·min(N, c)` criaturas dele saem por conjuração; **nunca medido** (o simulador não modela campo de oponente).
- **Efeitos unilaterais** (`orquestracao/efeitos_unilaterais.py`, 5.000 partidas): castabilidade (mana + cor) de Vona's Hunger, Crackling Doom, Rush of Dread, Make an Example, Syphon Flesh e Perilous Predicament, e a condição do *ascend* do Vona's Hunger (10+ permanentes) por turno.
- **Enumeração por script** (`orquestracao/enumeracao_sac.py`): reage a sacrifício x morte x destroy, grupos de tipo de criatura, incolores x coloridos, artefatos/encantamentos, fontes de cor, cartas de proteção, lendo o oráculo cru das 94 cartas.
- **Formato dos brutos:** `raw_dry_run_*.json.xz` = `{"formato":"amostras-colunas-v1", "modo", "N", "S0", "variantes", "campos_amostra", "campos_r", "amostras":{campo:[valor por estado]}, "resultados":{variante:{campo:[valor por estado]}}, "violacoes", "excecoes", "n_excecoes"}`; `--sum` refaz as tabelas só dele.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela / uso |
|---|---|---|---|---|
| `dados/busca_ampla_cru.json.xz`, `dados/busca_ampla_classificada.json` | busca ampla do Scryfall (crua e classificada) | `busca_ampla.py` | **usado (log: "Como foi a busca")** | `resumos/busca_ampla.txt` |
| `dados/oraculo_candidatas_rulings.json` | oráculo + rulings de 63 cartas, ao vivo | `oraculo_candidatas.py` | **usado (checklist)** | `resumos/oraculo_candidatas.txt` |
| `dados/oraculo_lista_ao_vivo.json.xz` | oráculo cru das 94 cartas da lista + comandante (copiado de `2026-10-04-blasphemous-edict`) | — | usado (harness, enumeração) | `resumos/enumeracao.txt` |
| `dados/spellbook_cru.json.xz`, `dados/spellbook_resumo.json` | Commander Spellbook antes/depois + controles | `csb_wipes.py` | **usado (log: "Documentação do deck e Commander Spellbook")** | `resumos/spellbook.txt` |
| `dados/raw_dry_run_padrao_10000.json.xz` | 119.958 estados × 22 variantes, modo padrão | `sac_dry_run.py 10000 3000000 --bruto …` | **usado (tabelas do log)** | `resumos/dry_run_padrao_10000.txt`, `resumos/paridade_oponente_padrao.txt` |
| `dados/raw_dry_run_resiliencia_10000.json.xz` | idem, modo resiliência | `FX_MODO=resiliencia sac_dry_run.py 10000 3000000 --bruto …` | usado (log: parágrafo da resiliência) | `resumos/dry_run_resiliencia_10000.txt`, `resumos/paridade_oponente_resiliencia.txt` |
| `resumos/regressao_dry_run_padrao_20000.txt`, `resumos/regressao_dry_run_resiliencia_20000.txt` | regressão do harness: 20.000 partidas por modo, sementes `5_000_000+i`, 0 exceções e 0 violações | `sac_dry_run.py 20000 5000000` (com e sem `FX_MODO`) | verificação | log: validação |
| `resumos/efeitos_unilaterais.txt` | castabilidade dos unilaterais e do ascend | `efeitos_unilaterais.py 5000 3000000` | usado | log |
| `resumos/enumeracao.txt` | varredura por script (sacrifício, morte, tipos, cores...) | `enumeracao_sac.py` | usado | log / checklist |
| `resumos/smoke.txt` | 99 cartas, 0 desconhecidas/duplicadas, 35 terrenos + 200 partidas | `smoke.py` | verificação | log: validação |
| `resumos/testes_dirigidos.txt` | 38 testes dirigidos do harness (incluindo equivalência com o executor da rodada anterior) | `testes_dirigidos.py` | verificação | log: validação |
| `resumos/indice_dados.md`, `resumos/verificacao_reproducao.txt` | índice dos dados; saída da verificação | `indice_dados.py`, `verificar_reproducao.sh` | verificação | — |
| `orquestracao/edict_harness.py` | o executor da rodada anterior (só para o teste S1) | — | usado (teste S1) | `resumos/testes_dirigidos.txt` |
| `resumos/espiao_fichas_doentes_padrao.txt`, `resumos/espiao_fichas_doentes_resiliencia.txt` | achado lateral: sacrifício de fichas "doentes" antes do combate (12 de 3.000 partidas no padrão, 9 na resiliência) | `espiao_fichas_doentes.py padrao 3000` / `resiliencia 3000` | usado (log: achado aberto) | log |
| `resumos/winnowing_escolha.txt` | que criatura o Winnowing (política Vihaan) escolhe em 2.461 estados naturais: o Vihaan em 96%; sobrevivem 28% das minhas criaturas | `winnowing_escolha.py` | verificação do harness | log |

Nenhum lote superado ou inválido nesta pasta (os dois primeiros lançamentos dos lotes principais foram **interrompidos antes de terminar** — caminho relativo no `--bruto` e, depois, métricas e variantes acrescentadas — e refeitos do zero: nada foi apagado de dados publicados).

**Comandos que reproduzem cada tabela** (de dentro de `orquestracao/`): `python3 sac_dry_run.py --sum --bruto ../dados/raw_dry_run_padrao_10000.json.xz` → `dry_run_padrao_10000.txt` · idem `…resiliencia…` → `dry_run_resiliencia_10000.txt` · `python3 paridade_oponente.py ../dados/raw_dry_run_{padrao,resiliencia}_10000.json.xz` → `paridade_oponente_{padrao,resiliencia}.txt` · `python3 enumeracao_sac.py` → `enumeracao.txt` · `python3 smoke.py` · `python3 testes_dirigidos.py` · `python3 efeitos_unilaterais.py 5000 3000000` · `python3 espiao_fichas_doentes.py {padrao,resiliencia} 3000` · `python3 winnowing_escolha.py` (esses dois foram reproduzidos numa 2ª execução com os mesmos números, mas **não** estão no `verificar_reproducao.sh`) · `python3 sac_dry_run.py 10000 3000000` e `FX_MODO=resiliencia python3 sac_dry_run.py 10000 3000000` (re-executam os lotes) · `python3 sac_dry_run.py 20000 5000000` e `FX_MODO=resiliencia python3 sac_dry_run.py 20000 5000000` (regressões).

## Verificação de reprodutibilidade (feita ANTES de declarar arquivado)

`bash orquestracao/verificar_reproducao.sh --tudo` → **12/12 saídas byte a byte iguais** (`cmp`; `resumos/verificacao_reproducao.txt`):
1. as 2 tabelas do ensaio a seco (padrão e resiliência, 10.000 partidas) **refeitas só dos `.json.xz`** (`--sum`);
2. as 2 tabelas da aritmética do lado dos oponentes (`paridade_oponente.py`), também só dos brutos;
3. a enumeração por script (`enumeracao_sac.py`, sobre o oráculo cru arquivado);
4. a **re-execução** do smoke, dos 38 testes dirigidos e dos efeitos unilaterais (5.000 partidas);
5. a **re-execução dos 4 lotes** do ensaio a seco (10.000 × 2 modos e a regressão de 20.000 × 2 modos), 4 processos em paralelo, ~35 min.
O simulador e os arquivos das rodadas anteriores **não foram tocados** (nenhuma chave nova), então os 13 arquivos anteriores do Vihaan não foram reverificados nesta rodada.
**Não conferido byte a byte:** tudo que vem de API ao vivo (`busca_ampla_*`, `oraculo_candidatas_rulings.json`, `spellbook_*`, `resumos/busca_ampla.txt`, `resumos/oraculo_candidatas.txt`, `resumos/spellbook.txt`): as respostas **cruas estão guardadas**, mas uma nova consulta pode devolver dados diferentes (cartas, rulings e combos mudam). Também não entram no `verificar_reproducao.sh` o espião de fichas doentes e a conferência do Winnowing (reproduzidos numa 2ª execução, mesmos números).

## O que NÃO foi verificado (Regra #7)

- O efeito de cada candidata **no campo dos oponentes** (📊: o simulador não modela criatura de oponente); o ensaio a seco é só o **meu** lado e é piso. A convenção "o Act só conta as minhas criaturas" torna o Act mais caro que na mesa real: a castabilidade do Act contra a das candidatas **não é comparável**.
- A frequência real, **nas mesas do usuário**, de campos grandes, de tipos de criatura iguais (que anulam o Winnowing), de indestrutível e de Mayhem Devil.
- O corte (Act × Blood Money × outra carta) e a comparação carta a carta com o que sai: o Blood Money só aparece como **referência medida**.
- As cartas excluídas (motores de morte, alvo único, MV ≥ 8, mistas de vida/mão) só têm a **cláusula do oráculo citada** (`checklist-oraculo.md`); não rodaram. As unilaterais só foram medidas em castabilidade.
- O convoke do Winnowing (1ª main: todas as criaturas; 2ª main: animados + outlaws com vigilance do Vihaan) e as escolhas do que guardar (Vihaan, Sol Ring, Dictate...) são **aproximações minhas**; a castabilidade por cor é otimista (ignora o mana já gasto no turno; trata filter lands e Pathway pela união das cores).
- As cartas **não** foram adicionadas ao `vihaan_goldfish_v1.py`; nenhuma carta foi cortada ou adicionada à lista.
- Não houve auditoria carta a carta do `.py`; só os caminhos de sacrifício/morte lidos (`sacrifice_*`, `on_permanent_sacrificed`, `on_creature_dies`, `on_token_leaves`, `begin/end_mass_death`, `_own_wipe_destroy_all`, `cast_card`, `spell_cost`).

## Nota de 2026-10-04 (12ª rodada: Mythos of Snapdax no lugar do Blood Money)

A lista viva do Vihaan (`../../lista.md`) passou a ter `Mythos of Snapdax` no lugar de `Blood Money` e o simulador vivo ganhou duas chaves novas (`MYTHOS_REPLACES_BLOOD_MONEY_ENABLED`, `CASCADE_DECLINE_HELD_WIPES_ENABLED`; ver `../2026-10-04-mythos-no-lugar-do-blood-money/LEIAME.md`). Para esta pasta **continuar reproduzindo o que publicou**, os scripts abaixo passaram a ler a lista antiga (`../_lista_legada/lista.md`, cópia exata da lista de `a17049f`) e/ou a **desligar as duas chaves novas** no simulador vivo (a lista volta a ter o Blood Money na posição antiga; bit-idêntico a `a17049f`) e, nos `fx_common.py`, a ignorar os 4 campos novos do `GameState` na impressão digital. **Nenhum dado bruto nem resumo desta pasta foi tocado.** Scripts alterados: `orquestracao/csb_wipes.py`, `orquestracao/enumeracao_sac.py`, `orquestracao/fx_common.py`. Depois do ajuste, `bash orquestracao/verificar_reproducao.sh --tudo`: **12/12** saídas iguais byte a byte, **0 `DIFERE`**. `SHA256SUMS` regenerado (o `LEIAME.md` e o próprio `SHA256SUMS` ficam de fora).
