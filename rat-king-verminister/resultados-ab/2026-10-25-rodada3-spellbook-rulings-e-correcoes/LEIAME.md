# Rodada 3 do Rat King, Verminister (2026-10-25): Spellbook, rulings dos conceitos compartilhados e 21 correções de simulador

Arquivo **permanente e auditável** de tudo que sustenta as conclusões desta rodada. As conclusões e as tabelas legíveis estão em `rat-king-verminister/goldfish-log.md` (seção desta rodada), `checklist-oraculo.md` e `auditoria.md` §15. Esta pasta guarda os dados.

Pedido do usuário (2026-10-25): *"Quero sim"*, em resposta ao meu relatório "O quê falta para terminar o deck do Verminister?" (itens 1 e 3: texto desatualizado; Spellbook e rulings nunca rodados).

> **STATUS DESTA PASTA:** em construção. Ao fim da rodada este LEIAME ganha a tabela de resultados, o mapa arquivo → comando e a verificação de reprodutibilidade. O que ainda NÃO foi feito está listado em "Escopo" no fim.

## Em 1 minuto

| Quero… | Faça |
|---|---|
| ver o que foi concluído | `../../goldfish-log.md` (seção mais nova no topo) e `../../auditoria.md` §15 |
| ver os combos que o Spellbook acha no deck | `resumos/spellbook.txt`, `resumos/prob_combos.txt` |
| ver cada ruling × código | `resumos/rulings_vs_codigo.md` |
| refazer as tabelas do A/B a partir dos dados | `bash orquestracao/verificar_reproducao.sh` |
| conferir que nada foi alterado | `sha256sum -c SHA256SUMS` (nesta pasta) |

## O que mudou no simulador

`ratking_goldfish_v1.py` ganhou **21 chaves de correção**, todas ligadas no arquivo vivo. Com todas desligadas ele é **bit-idêntico** ao snapshot `codigo/ratking_goldfish_v1_ANTES_da85341.py` (commit `da85341`, imediatamente antes desta rodada). Cada chave cita a cláusula do oráculo no próprio arquivo.

| chave | cláusula do oráculo / ruling | o que o código fazia antes |
|---|---|---|
| `TREASURE_MANA_ENABLED` | Treasure: "{T}, Sacrifice: Add one mana of any color"; Rat King/Disappear: "a permanent left the battlefield" | a Treasure nunca era gasta como mana |
| `THORNBITE_STAFF_ENABLED` | Equip {4}; "{2},{T}: 1 damage to any target"; "whenever a creature dies, untap"; "Whenever a Shaman creature enters, you may attach"; **combo Marrow-Gnawer + Staff (Spellbook 2178-3126)** | carta inerte; a nota dizia "nenhuma criatura Shaman na lista", mas o Mercenary de Black Market Connections (changeling) é Shaman |
| `ROTCALLER_EXACT_X` | Valley Rotcaller: X = outros Squirrels, Bats, Lizards e Rats que controlo | `Rats prontos + fichas − 1` (tirava um Rat de verdade; ignorava Esquilos e Rats doentes) |
| `MARROW_X_AFTER_SACRIFICE` | ruling 2004-12-01 | X contava o Rat sacrificado |
| `BIG_APPLE_PER_OPPONENT` | "for each opponent you have" | 1 ficha |
| `AYARA_TOKEN_TRIGGER` | "Ayara or another black creature you control enters" (a ficha de Rat é preta) | código morto: `... if False else None` |
| `AYARA_SACRIFICE_TOKENS` | "Sacrifice another black creature" | sacrificava carta nomeada havendo ficha |
| `PLAGUE_PAYS_WITH_AYARA` | **combo Ayara + Plague of Vermin (Spellbook 884-5035)** | pagava no máx. 10 e só a vida acima de 20 |
| `JET_MEDALLION_BLACK_SPELLS` | "Black spells you cast cost {1} less" | `pips_b=0` nas magias: nenhuma magia preta recebia o desconto |
| `COST_REDUCTION_COLORED_FLOOR` | rulings Jet Medallion (2023-07-28) e Bontu's (2017-04-18): só reduz o genérico | Rat Colony {1}{B} custava 0 com os dois em campo |
| `GRAY_MERCHANT_ETB` | "each opponent loses X life ... you gain life equal to the life lost" | o ETB não existia |
| `NINJA_TEEN_LEVELS_AND_DRAIN` | a Classe entra no nível 1; nível 1: "creature you control leaves the battlefield → each opponent loses 1" | cobrava {1}{B} fantasma; dreno inexistente |
| `NINJA_TEEN_SNEAK_RULING` | CR 702.190a/b e rulings de 2026-01-27 | sneak na main phase, sem devolver atacante, entrava desvirada |
| `RAT_KING_REANIMATE_COST` | "Sacrifice three Rats" (o comandante nunca é sacrificado) | o comandante entrava na conta e pagava 2 |
| `SOUL_STONE_SHARED_TAP` | Harness: {6}{B}, **{T}** | o {B} da pedra contava no mesmo turno |
| `PRIEST_EXACT` | "any number of target players"; "two other creatures" | perdia 2 de vida própria; podia sacrificar a si mesmo |
| `EMERITUS_ENTERS_PREPARED` | "This creature enters prepared" | só o end step ligava o estado |
| `EXTORT_ENABLED` | Crypt Ghast: extort | tag órfã |
| `ZULAPORT_SELF_DEATH` | "this creature or another creature you control dies" | a própria morte não contava |
| `SACRIFICE_COST_NEEDS_FODDER` | Deadly Dispute / Culling the Weak: custo adicional "sacrifice" | conjuradas sem nada a sacrificar |
| `BONTU_TRIGGER_ONCE` | "Whenever you cast a creature spell" | disparava 2× por criatura conjurada da mão |

Constantes novas (não são chaves): `MARROW_STAFF_LOOP_RAT_TARGET = 40`, `MARROW_STAFF_LOOP_MAX_ITERS = 12` (o loop real é infinito; o simulador precisa de um teto), `PLAGUE_COMBO_CAP = 60`.

## Como os dados foram gerados

- **Oráculo e rulings:** `orquestracao/scry_rulings.py` → `dados/scryfall_oraculo_rulings_2026-10-25.json` (ao vivo; 54 cartas únicas; resolução por nome exato, depois fuzzy, depois `flavor_name` (Regra #2); nenhuma precisou dos dois últimos).
- **Spellbook:** `orquestracao/csb_ratking.py` → `dados/spellbook_rat_king_2026-10-25.json`. Resolve cada nome antes (57 nomes, **0 não reconhecidos**), roda `find-my-combos` e `estimate-bracket`, com **controle positivo** (Basalt Monolith + Rings of Brighthearth aparece; Necropotence é marcada Game Changer) e **controle de corte** (sem o Rings o combo some).
- **Enumeração por script** dos satisfazedores de cada condição de tipo/cor (`orquestracao/enumera_condicoes.py` → `resumos/enumera_condicoes.txt`) e dos dados fixos do `CARD_DB` contra o oráculo (`orquestracao/carddb_vs_oraculo.py` → `resumos/carddb_vs_oraculo.txt`).
- **A/B pareado, bit-identidade, regressão:** `orquestracao/driver.py` + `abgen.py` (genéricos, lêem `orquestracao/config.json`). Sementes: A/B N=2.000 → `1_000_000+i`; N=10.000 → `3_000_000+i`; regressão e bit-identidade → `5_000_000+i`. 8 turnos; dois modos (`padrao` = `simulate_one`; `resiliencia` = `simulate_one_with_interaction`). `PYTHONHASHSEED=0` fixado pelo driver. Variantes: `antes` (snapshot), `depois` (arquivo vivo, tudo ligado) e **uma por correção** (`so_*`: só aquela chave ligada). IC95% = 1,96·dp(diferença pareada)/√N.
- **Testes dirigidos:** `orquestracao/testes_dirigidos.py` (cada teste confere o comportamento prometido com a chave ligada e com ela desligada).
- **Probabilidade dos combos:** `orquestracao/prob_combos.py` (forma fechada + simulador) → `resumos/prob_combos.txt`.
- **Varredura sistêmica nova:** `../../../varredura-2026-10-05/scripts/audit_etb_sem_efeito.py` (ETB/feitiço sem efeito e gatilho sem reação) → `resumos/audit_etb_sem_efeito_ANTES.txt` e `_DEPOIS.txt`.
