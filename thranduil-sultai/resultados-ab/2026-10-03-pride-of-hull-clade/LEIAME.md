# Resultados brutos — The Pride of Hull Clade no Thranduil (2026-10-03)

Arquivo de referência **permanente e auditável** de tudo que sustenta as conclusões desta rodada do deck Thranduil, the Elvenking. As conclusões e as tabelas legíveis
estão em `thranduil-sultai/goldfish-log.md` (seção "The Pride of Hull Clade — avaliação como possível inclusão — 2026-10-03") e em `thranduil-sultai/checklist-oraculo.md`. **Esta pasta guarda os dados por trás delas.**
Pedido do usuário: *"Avalie a possível inclusão de The Pride of Hull Clade no Thranduil."*

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

`thranduil-sultai/thranduil_goldfish_v1.py` (último commit `0ee4972`) **não foi editado**: a carta nova e a instrumentação entram por *monkeypatch* em tempo de execução (`orquestracao/*_harness.py`).
A base do harness (sem a carta na lista) foi comparada com o módulo original, carregado como módulo separado e sem nenhum patch: ver `resumos/bitident.txt`.
Código desta pasta: o commit que a adiciona (`git log -1 -- thranduil-sultai/resultados-ab/2026-10-03-pride-of-hull-clade`).

## Como os dados foram gerados

- **Sementes:** `3_000_000 + i`, a mesma semente em todas as variantes de um lote (**pareado**; IC95% = 1,96·dp/√N da diferença). N = 6.000 (A/B; 8 e 10 turnos), 4.000 (ablação; 8 turnos), 6.000 (toughness por turno).
- **Variante:** `(CORTE, MODO)`: a Pride entra **na linha** de `CORTE` na decklist (`swap_text`); `MODO` = `off` (só o corpo 2/15 defender), `trample_line` (linha deliberada: no turno em que a Ezuri já pagou +3/+3 e trample, ativa {2}{U}{U} no Elfo de maior toughness; compra = toughness + 3, dobrada pela Roaming Throne) ou `ceiling` (teto irreal: ativa nela mesma todo turno, sem bloqueio).
- **Toughness:** o simulador original **não rastreia toughness**; o harness acrescenta `total_toughness()` = toughness impresso (cache do Scryfall) + anthem de Elfo + contadores da Marwyn; ficha de Elfo = 1; criatura com `*` = 1 (subestima Jarad). Custo da Pride = `max(1, 11 − toughness total)`.
- **Blank Card:** carta inconjurável (instantâneo, MV 99) da ablação: cortar `X` por ela mede o que o simulador perde sem `X`; carta morta na mão = descarte grátis, ler só relativamente. (A 1ª ablação, com a Blank como artefato, foi substituída antes de ser usada em qualquer conclusão.)
- **Formato dos brutos:** `raw_*.json.xz` = `{"formato":"colunas-v1","variantes":{nome:{"n":N,"campos":{campo:[valor por semente]}}}}` (ver `orquestracao/raw_io.py`; campos em `thr_harness.summarize`). Os A/B foram gravados primeiro como lista de dicts em `.json` (81 MB cada) e convertidos para este formato sem perda (o `--sum` refaz as tabelas byte a byte a partir do convertido).

## Mapa: arquivo → o que é → código → status → tabela

| arquivo | o que é (variantes) | código | status | tabela do log que o usa |
|---|---|---|---|---|
| `dados/raw_ab_8t.json.xz` | base + 10 cortes × 3 modos (31 variantes), N=6.000, 8 turnos | `thr_ab.py 6000 8` | usado | `resumos/ab_8t.txt` (log: tabela de medição) |
| `dados/raw_ab_10t.json.xz` | idem, 10 turnos | `thr_ab.py 6000 10` | usado | `resumos/ab_10t.txt`; base do condicional |
| `resumos/condicional_10t.txt` | só as partidas em que a Pride foi conjurada (4 cortes × 3 modos) | `thr_condicional.py` (lê `raw_ab_10t`) | usado | log: Condicional |
| `dados/raw_ablacao_thranduil.json.xz` | base + cada carta não-terreno trocada pela Blank, N=4.000 | `thr_ablacao.py` | usado (só ranking dos controles) | `resumos/ablacao_thranduil.txt` |
| `resumos/toughness_por_turno.txt` | toughness total, fontes de U e mana por turno nas partidas-base | `thr_toughness.py` (roda N=6.000) | usado | log: toughness por turno |
| `dados/spellbook_thranduil_swaps.json` | **resumo** do `find-my-combos` (combos incluídos e "quase" por lista: base, +Pride, 10 trocas); **não** guarda a resposta crua | `csb_generic.py` | usado | `resumos/spellbook_thranduil_swaps.txt` (log: Combos) |
| `dados/spellbook_quase_pride_body_of_research.json` | combo "quase" Pride + Body of Research (resposta crua do item) | consulta direta à API | referência | log: Combos |
| `dados/rulings_The_Pride_of_Hull_Clade.json` | oráculo bruto do Scryfall + 6 rulings (lidos ao vivo em 2026-10-03) | consulta direta à API | referência | checklist: Pride |
| `resumos/enumeracao.txt` | enumeração por script das 99 cartas + comandante (tipos, Elfo/não-Elfo, toughness, anthems, compra, efeitos anti não-Elfo, fontes de U, tutores) | `thr_enumeracao.py` | usado | log: motores |
| `resumos/bitident.txt` | base do harness × simulador original sem patch (300 partidas) | `bitident.py` | verificação | log: escopo verificado |

## Mapa: tabela → comando que a reproduz (de dentro de `orquestracao/`)

| resumo salvo (`resumos/`) | comando |
|---|---|
| `ab_8t.txt` | `python3 thr_ab.py 6000 8 --sum` |
| `ab_10t.txt` | `python3 thr_ab.py 6000 10 --sum` |
| `condicional_10t.txt` | `python3 thr_condicional.py` |
| `ablacao_thranduil.txt` | `python3 thr_ablacao.py --sum` |
| `toughness_por_turno.txt` | `python3 thr_toughness.py` (roda as simulações; determinístico) |
| `enumeracao.txt` | `python3 thr_enumeracao.py` (lê o cache do Scryfall e `lista.md`) |
| `bitident.txt` | `python3 bitident.py 300 8` |
| `spellbook_thranduil_swaps.txt` | a partir da raiz do repositório: `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 thranduil-sultai/resultados-ab/2026-10-03-pride-of-hull-clade/orquestracao/csb_generic.py thranduil-sultai "Thranduil, the Elvenking" saida.json "CARTA1|CARTA2|…" "The Pride of Hull Clade"`; depende da API ao vivo, **não** é refeito byte a byte |
| `indice_dados.md` | `python3 ../indice_dados.py` |

Sem `--sum`, os mesmos scripts **rodam** as simulações de novo (e gravam os brutos).

## Verificações feitas ao arquivar (2026-10-03)

- **Reprodutibilidade:** a partir dos `.json.xz`, as 4 tabelas `ab_8t`, `ab_10t`, `condicional_10t` e `ablacao_thranduil` saíram **byte a byte iguais** às salvas (`cmp` sem diferença); `toughness_por_turno.txt` e `enumeracao.txt` foram refeitos por execução e saíram iguais (a enumeração, com 3 valores de `PYTHONHASHSEED`, depois de ordenar duas listas que saíam em ordem de hash).
- **Bit-identidade:** `bitident.py 300 8`: 300/300 partidas idênticas no dict completo de `simulate_one` (original sem patch × remendado) e 300/300 em 12 campos de `sim_state` (cópia de `simulate_one` do harness que devolve o estado) × original.
- **Controles:** no A/B, cortar Priest of Titania custa −6,6pp de finalizador ≤T8 e Elvish Mystic −1,7pp (doem, como deveriam); no Spellbook, cortar Devoted Druid remove os 4 combos e cortar Immaculate Magistrate remove 2.
- **Não conferido byte a byte:** `spellbook_*.json` (API ao vivo; só o "quase" foi guardado cru) e `rulings_*.json`.
- **Tudo de uma vez:** `bash orquestracao/verificar_reproducao.sh` refaz todas as tabelas dos `.json.xz` e compara com `cmp`; a saída desta verificação está em `resumos/reproducao_cmp.txt`.
- **Hashes:** `SHA256SUMS` cobre `dados/`, `resumos/`, `orquestracao/`, `indice_dados.py`, `descomprimir.sh` e `.gitignore`.
