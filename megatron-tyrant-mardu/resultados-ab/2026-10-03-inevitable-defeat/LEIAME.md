# Resultados brutos — Inevitable Defeat no Megatron (2026-10-03)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Megatron, Tyrant. As conclusões e as tabelas legíveis
estão em `megatron-tyrant-mardu/goldfish-log.md` (seção "Inevitable Defeat — avaliação como possível inclusão — 2026-10-03") e em `megatron-tyrant-mardu/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**
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

> **Nota posterior (2026-10-03, mesma data, depois desta rodada): o simulador vivo mudou.** A frase "o simulador não foi alterado" vale **para esta rodada** (medidas com o commit `22d0ed2`).
> Depois dela, `megatron_goldfish_v1.py` ganhou a habilidade do Myriad Landscape e o piloto de terreno tapped em T1/T2
> (`../2026-10-03-myriad-e-tapped-t1t2/LEIAME.md`). Consequências para esta pasta: (1) **as tabelas continuam reproduzíveis**, porque `--sum` lê só os brutos `.json.xz`;
> (2) `bitident.py` compara com o arquivo VIVO e **passa a divergir**: para refazê-lo, extraia o simulador antigo com `git show 22d0ed2:megatron-tyrant-mardu/megatron_goldfish_v1.py`
> (há uma cópia em `../2026-10-03-myriad-e-tapped-t1t2/codigo/megatron_goldfish_v1_ANTES_22d0ed2.py`) e aponte o script para ele; (3) os números **absolutos** daqui (por exemplo cmd ≤T4 = 77,8%) são do piloto antigo,
> não comparáveis com rodadas feitas depois da correção; as diferenças pareadas desta rodada continuam valendo para o piloto antigo.
> **Segunda mudança do simulador no mesmo dia:** London Mulligan com escolha das cartas do fundo e fetch lands com a habilidade real (`../2026-10-03-mulligan-e-fetches/LEIAME.md`, código anterior em `../2026-10-03-mulligan-e-fetches/codigo/`). Vale tudo que está dito acima.


`megatron-tyrant-mardu/megatron_goldfish_v1.py` (último commit `22d0ed2`) **não foi editado**: a carta nova e a instrumentação entram por *monkeypatch* em tempo de execução (`orquestracao/*_harness.py`).
A base do harness (sem a carta na lista) foi comparada com o módulo original, carregado como módulo separado e sem nenhum patch: ver `resumos/bitident.txt`.
Código desta pasta: o commit que a adiciona (`git log -1 -- megatron-tyrant-mardu/resultados-ab/2026-10-03-inevitable-defeat`).

## Como os dados foram gerados

- **Sementes:** `3_000_000 + i`, a mesma semente em todas as variantes de um lote (**pareado**: a diferença entre duas variantes é por partida; IC95% = 1,96·dp/√N da diferença). N = 10.000 (A/B), 5.000 (ablação), 20.000 (alimentação do flip), 10.000 (castabilidade de cor). 8 turnos.
- **Variante:** `[(SAI, ENTRA)]` aplicado à `BASE_LIBRARY` (troca **posicional**: a carta nova entra na linha da cortada). `ENTRA` = `Inevitable Defeat` ou `Blank Card`.
- **Blank Card:** carta inconjurável (**instantâneo**, MV 99) usada como controle: cortar `X` por ela mede o que o simulador perde sem `X`. Como a Blank é uma carta morta que fica na mão, o simulador a trata como descarte grátis e **premia não gastar mana** em `X` (+0,9 a +1,8 de dano no A/B): ler só relativamente. Como **artefato** ela era trazida ao campo (Welder/Sneak Attack/Anrakyr/…) e sacrificada como combustível MV 99 (+9 a +11): lote superado, em `superado-blank-artefato/`. `BLANK_TYPE=artifact` reproduz o lote superado.
- **Modelagem da Defeat** (`orquestracao/meg_harness.py`): tag `interaction`; `proxy_drain(3)` + `gain_life(3)` ao resolver; cor via `pips` do próprio simulador; o exílio é 📊 (sem permanente de oponente). Instrumentação só-leitura: `rwb_turn` (1º turno com R+W+B em campo e ≥4 de mana), `defeat_*` (turno, face do Megatron, comandante em campo, flip no mesmo turno).
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`; campos em `meg_harness.summarize`).

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é (variantes) | código | status | tabela do log que o usa |
|---|---|---|---|---|
| `dados/raw_ablacao_megatron.json.xz` | base + 63 cortes (cada carta não-terreno trocada pela Blank), N=5.000 | `meg_ablacao.py` | usado | `resumos/ablacao_megatron.txt` (ranking dos controles; log: "o que a medição não diz") |
| `dados/raw_ab_megatron_10000.json.xz` | base + 15 `Defeat<-X` (13 candidatas + 2 controles) + 4 `Blank<-X`, N=10.000 | `meg_ab.py` | usado | `resumos/ab_megatron_10000.txt` (log: tabela de medição) |
| `dados/raw_defeat_alimenta_megatron.json.xz` | `Defeat<-Chaos Warp` e `Defeat<-Generous Gift`, N=20.000, com `defeat_fed` | `meg_fed.py` | usado | `resumos/defeat_alimenta_megatron.txt` (log: "quanto a Defeat alimenta o flip") |
| `dados/raw_castabilidade_cor_megatron.json.xz` | base, N=10.000, `rwb_turn` e `cmd_turn` | `meg_cor.py` | usado | `resumos/castabilidade_cor_megatron.txt` (log: Cor) |
| `dados/spellbook_megatron_swaps.json` | **resumo** do `find-my-combos` do Commander Spellbook (combos incluídos e "quase" por lista: base, +Defeat, 15 trocas); **não** guarda a resposta crua da API | `csb_generic.py` | usado | `resumos/spellbook_megatron_swaps.txt` (log: Combos) |
| `dados/rulings_Inevitable_Defeat.json` | oráculo bruto do Scryfall + 1 ruling (lidos ao vivo em 2026-10-03) | consulta direta à API | referência | checklist: Inevitable Defeat |
| `superado-blank-artefato/` | 1º lote (Blank como artefato MV 99) | — | **SUPERADO** (as linhas `Defeat<-X` são idênticas; só mudam `Blank<-X` e a ablação absoluta) | nenhuma |
| `resumos/enumeracao.txt` | enumeração por script das 85 entradas distintas de `lista.md` (remoção, perda/ganho de vida, exile) | `meg_enumeracao.py` | usado | log: cobertura de interação |
| `resumos/bitident.txt` | base do harness × simulador original sem patch (300 partidas) | `bitident.py` | verificação | log: escopo verificado |

## Mapa: tabela → comando que a reproduz (de dentro de `orquestracao/`)

| resumo salvo (`resumos/`) | comando |
|---|---|
| `ablacao_megatron.txt` | `python3 meg_ablacao.py --sum` |
| `ab_megatron_10000.txt` | `python3 meg_ab.py 10000 --sum` |
| `defeat_alimenta_megatron.txt` | `python3 meg_fed.py --sum` |
| `castabilidade_cor_megatron.txt` | `python3 meg_cor.py --sum` |
| `enumeracao.txt` | `python3 meg_enumeracao.py` (lê o cache do Scryfall e `lista.md`) |
| `bitident.txt` | `python3 bitident.py 300 8` |
| `spellbook_megatron_swaps.txt` | a partir da raiz do repositório: `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 megatron-tyrant-mardu/resultados-ab/2026-10-03-inevitable-defeat/orquestracao/csb_generic.py megatron-tyrant-mardu "Megatron, Tyrant" saida.json "CARTA1|CARTA2|…" "Inevitable Defeat"` (cortes separados por `|`); depende da API ao vivo, **não** é refeito byte a byte |
| `indice_dados.md` | `python3 ../indice_dados.py` |

Sem `--sum`, os mesmos scripts **rodam** as simulações de novo (e gravam os brutos).

## Verificações feitas ao arquivar (2026-10-03)

- **Reprodutibilidade:** a partir dos `.json.xz`, as 4 tabelas `ablacao_megatron`, `ab_megatron_10000`, `defeat_alimenta_megatron` e `castabilidade_cor_megatron` saíram **byte a byte iguais** às salvas (`cmp` sem diferença); `enumeracao.txt` também (rodado de novo, igual, com 3 valores de `PYTHONHASHSEED`). As tabelas salvas são também **iguais às da rodada anterior** do mesmo código (determinismo entre execuções).
- **Bit-identidade:** `bitident.py 300 8`: 300/300 partidas idênticas em 123 campos do `GameState` (original sem patch × base do harness).
- **Controles:** no A/B, cortar Arcane Signet ou Fellwar Stone custa −3,1pp / −2,6pp de win (doem, como deveriam); no Spellbook, cortar Chandra's Ignition remove o combo com Blightsteel Colossus e cortar Genesis Chamber remove o combo com Cursed Mirror + Daretti.
- **Não conferido byte a byte:** `spellbook_megatron_swaps.*` (depende da API ao vivo; a resposta crua não foi guardada) e `rulings_*.json` (resposta da API).
- **Tudo de uma vez:** `bash orquestracao/verificar_reproducao.sh` refaz todas as tabelas dos `.json.xz` e compara com `cmp`; a saída desta verificação está em `resumos/reproducao_cmp.txt`.
- **Hashes:** `SHA256SUMS` cobre `dados/`, `resumos/`, `orquestracao/`, `superado-blank-artefato/`, `indice_dados.py`, `descomprimir.sh` e `.gitignore`.
