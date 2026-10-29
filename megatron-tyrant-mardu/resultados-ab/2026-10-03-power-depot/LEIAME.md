# Resultados brutos — Power Depot no Megatron (2026-10-03)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Megatron, Tyrant. As conclusões e as tabelas legíveis estão em
`megatron-tyrant-mardu/goldfish-log.md` (seção "Power Depot — avaliação como possível inclusão — 2026-10-03") e em `megatron-tyrant-mardu/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**
Pedido do usuário: *"E a inclusão de Power Depot no Megatron?"*

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

> **Nota posterior (2026-10-03, mesma data, depois desta rodada): o simulador vivo mudou.** A frase "o simulador não foi alterado" vale **para esta rodada** (medidas com o commit `22d0ed2`).
> Depois dela, `megatron_goldfish_v1.py` ganhou a habilidade do Myriad Landscape e o piloto de terreno tapped em T1/T2
> (`../2026-10-03-myriad-e-tapped-t1t2/LEIAME.md`). Consequências para esta pasta: (1) **as tabelas continuam reproduzíveis**, porque `--sum` lê só os brutos `.json.xz`;
> (2) `bitident.py` compara com o arquivo VIVO e **passa a divergir**: para refazê-lo, extraia o simulador antigo com `git show 22d0ed2:megatron-tyrant-mardu/megatron_goldfish_v1.py`
> (há uma cópia em `../2026-10-03-myriad-e-tapped-t1t2/codigo/megatron_goldfish_v1_ANTES_22d0ed2.py`) e aponte o script para ele; (3) os números **absolutos** daqui (por exemplo cmd ≤T4 = 77,8%) são do piloto antigo,
> não comparáveis com rodadas feitas depois da correção; as diferenças pareadas desta rodada continuam valendo para o piloto antigo.
> **Segunda mudança do simulador no mesmo dia:** London Mulligan com escolha das cartas do fundo e fetch lands com a habilidade real (`../2026-10-03-mulligan-e-fetches/LEIAME.md`, código anterior em `../2026-10-03-mulligan-e-fetches/codigo/`). Vale tudo que está dito acima.


`megatron-tyrant-mardu/megatron_goldfish_v1.py` (último commit `22d0ed2`) **não foi editado**: o Power Depot e a instrumentação entram por *monkeypatch* em tempo de execução (`orquestracao/pd_harness.py`).
A base do harness (sem o Depot na lista) foi comparada com o módulo original, carregado como módulo separado e sem nenhum patch: ver `resumos/bitident.txt`.
Código desta pasta: o commit que a adiciona (`git log -1 -- megatron-tyrant-mardu/resultados-ab/2026-10-03-power-depot`).

## Como os dados foram gerados

- **Sementes:** `3_000_000 + i`, a mesma semente em todas as variantes de um lote (**pareado**; IC95% = 1,96·dp/√N da diferença). N = 10.000 por variante, 8 turnos. 22 variantes por lote: a base, 19 `Depot<-TERRENO` (todos os terrenos distintos da lista) e 2 `Depot<-ROCK` (Arcane Signet, Fellwar Stone) como comparação terreno-vs-rock.
- **Variante:** `[(SAI, "Power Depot")]` aplicado à `BASE_LIBRARY` (troca **posicional**).
- **Modelagem** (`orquestracao/pd_harness.py`, detalhes na docstring e no `checklist-oraculo.md`): terreno que entra tapped, rende {C}; **fixação condicional**: para magia-artefato (o próprio Megatron é artefato nas duas faces), cada Depot untapped cobre UM pip faltante; Demonic Junker (Affinity) conta o Depot. Por política NÃO entra nas piscinas de artefato do simulador.
- **Políticas de jogada (`PD_POLICY`):** `core` = piloto original do simulador (terrenos por cor faltante, empate pela ordem da mão) · `early` = só o Depot é jogado no T1/T2 · **`early_all`** = QUALQUER terreno que entra tapped é jogado primeiro no T1/T2, **na base e nas variantes** (comparação justa; a base muda: é o piloto deliberado) · `fodder7` = `early` + Depot sobrando (≥7 terrenos) vira o combustível mais barato de Welder/Scrap Welder/Engineer/Trash · `early_all_fodder7` = `early_all` + combustível.
- **Cor (`PD_COLOR`):** `sim` = checagem do simulador (conta fontes por cor, sem casar fontes: um tri-land ou a Command Tower valem R, W e B ao mesmo tempo) · `strict` = casamento exato fonte→pip (cada fonte paga 1 pip); muda a base: serve de sensibilidade.
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`; campos em `pd_harness.summarize`).
- **Colunas das tabelas:** `cmd<=T` = comandante conjurado até o turno T; `nunca T8` = nunca conjurado em 8 turnos; `win` = vitória por veneno (Blightsteel) ou dano de comandante; `dano`/`mana conv.` = dano proxy e mana de flip; `Depot` = % das partidas com o Depot em campo; `fixa` = % em que o Depot foi o que tornou o comandante castável pela 1ª vez; `decis.` = % em que isso aconteceu no mesmo turno em que o comandante foi de fato conjurado.

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é | código | status | tabela do log que o usa |
|---|---|---|---|---|
| `dados/raw_ab_powerdepot_10000_core.json.xz` | 22 variantes, piloto original, cor `sim` | `pd_ab.py` com `PD_POLICY=core` | usado | `resumos/ab_powerdepot_10000_core.txt` (sensibilidade) |
| `dados/raw_ab_powerdepot_10000_early.json.xz` | idem, só o Depot jogado cedo | `PD_POLICY=early` | usado (sensibilidade; **favorece o Depot** frente a terrenos tapped que o piloto joga em ordem arbitrária) | `resumos/ab_powerdepot_10000_early.txt` |
| `dados/raw_ab_powerdepot_10000_early_all.json.xz` | idem, todo terreno tapped jogado cedo (base e variantes) | `PD_POLICY=early_all` | **usado (tabela principal do log)** | `resumos/ab_powerdepot_10000_early_all.txt` |
| `dados/raw_ab_powerdepot_10000_fodder7.json.xz` | `early` + Depot como combustível | `PD_POLICY=fodder7` | usado (sensibilidade) | `resumos/ab_powerdepot_10000_fodder7.txt` |
| `dados/raw_ab_powerdepot_10000_early_all_fodder7.json.xz` | `early_all` + Depot como combustível | `PD_POLICY=early_all_fodder7` | usado (sensibilidade) | `resumos/ab_powerdepot_10000_early_all_fodder7.txt` |
| `dados/raw_ab_powerdepot_10000_core_strict.json.xz` | cor estrita, piloto original | `PD_COLOR=strict PD_POLICY=core` | usado (sensibilidade de cor) | `resumos/ab_powerdepot_10000_core_strict.txt` |
| `dados/raw_ab_powerdepot_10000_early_all_strict.json.xz` | cor estrita, `early_all` | `PD_COLOR=strict PD_POLICY=early_all` | usado (sensibilidade de cor) | `resumos/ab_powerdepot_10000_early_all_strict.txt` |
| `dados/spellbook_megatron_powerdepot_swaps.json` | **resumo** do `find-my-combos` do Commander Spellbook (combos incluídos e "quase" por lista: base, +Depot, 19 trocas de terreno + 2 controles positivos); **não** guarda a resposta crua | `csb_generic.py` | usado | `resumos/spellbook_megatron_powerdepot_swaps.txt` |
| `dados/rulings_Power_Depot.json` | oráculo bruto do Scryfall + 4 rulings (lidos ao vivo em 2026-10-03) | consulta direta à API | referência | checklist: Power Depot |
| `dados/rulings_contexto_megatron_ultron_pia.json` | rulings de Megatron (18), Ultron (0), Pia's Revolution (5), Demonic Junker (0), Warstorm Surge (2), Scrap Trawler (4), Goblin Welder (1) | consulta direta à API | referência | checklist: Power Depot |
| `resumos/enumeracao.txt` | enumeração por script das 85 entradas distintas de `lista.md` (artefatos com pip colorido, cartas que leem "artifact", artefatos-criatura, terrenos, habilidades de artefato com mana colorido) | `pd_enumeracao.py` | usado | log: motores |
| `resumos/bitident.txt` | base do harness × simulador original sem patch (300 partidas, políticas `core`/`early`/`fodder7`) | `bitident.py` | verificação | log: escopo verificado |

`early_all*` e `strict` alteram a BASE de propósito (piloto deliberado; casamento exato de cor), então **não** passam por bit-identidade com o simulador original; a base delas é, por construção, a mesma deck com outro piloto/regra de cor.

## Mapa: tabela → comando que a reproduz (de dentro de `orquestracao/`)

| resumo salvo (`resumos/`) | comando |
|---|---|
| `ab_powerdepot_10000_<politica>.txt` | `PD_POLICY=<politica> python3 pd_ab.py 10000 --sum` (política ∈ core, early, early_all, fodder7, early_all_fodder7) |
| `ab_powerdepot_10000_<politica>_strict.txt` | `PD_COLOR=strict PD_POLICY=<politica> python3 pd_ab.py 10000 --sum` (política ∈ core, early_all) |
| `enumeracao.txt` | `python3 pd_enumeracao.py` (lê o cache do Scryfall e `lista.md`) |
| `bitident.txt` | `python3 bitident.py 300 8` |
| `spellbook_megatron_powerdepot_swaps.txt` | a partir da raiz do repositório: `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 megatron-tyrant-mardu/resultados-ab/2026-10-03-power-depot/orquestracao/csb_generic.py megatron-tyrant-mardu "Megatron, Tyrant" saida.json "TERRENO1|TERRENO2|…" "Power Depot"`; depende da API ao vivo, **não** é refeito byte a byte |
| `indice_dados.md` | `python3 ../indice_dados.py` |

Sem `--sum`, o mesmo script **roda** as simulações de novo (e grava os brutos).
`bash orquestracao/verificar_reproducao.sh` refaz todas as tabelas de uma vez e compara com `cmp`.

## Verificações feitas ao arquivar (2026-10-03)

- **Reprodutibilidade:** ver `resumos/reproducao_cmp.txt` (saída de `verificar_reproducao.sh`).
- **Bit-identidade:** `bitident.py 300 8`: 300/300 partidas idênticas em 123 campos do `GameState` nas políticas `core`, `early` e `fodder7` (original sem patch × base do harness).
- **Controles:** no A/B, trocar Arcane Signet ou Fellwar Stone pelo Depot custa −3,7 a −5,3pp de comandante conjurado até T3 (rocks pesam mais que um terreno tapped); no Spellbook, cortar Chandra's Ignition remove o combo com Blightsteel Colossus e cortar Genesis Chamber remove o combo com Cursed Mirror + Daretti.
- **Não conferido byte a byte:** `spellbook_*.json` (API ao vivo; resposta crua não guardada) e `rulings_*.json`.
- **Hashes:** `SHA256SUMS` cobre `dados/`, `resumos/`, `orquestracao/`, `indice_dados.py`, `descomprimir.sh` e `.gitignore`.
