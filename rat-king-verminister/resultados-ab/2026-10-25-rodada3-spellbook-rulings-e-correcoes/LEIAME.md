# Rodada 3 do Rat King, Verminister (2026-10-25): Spellbook, rulings dos conceitos compartilhados e 21 correções de simulador

Arquivo **permanente e auditável** de tudo que sustenta as conclusões desta rodada. As conclusões e as tabelas legíveis estão em `rat-king-verminister/goldfish-log.md` (seção desta rodada), `checklist-oraculo.md` e `auditoria.md` §15. Esta pasta guarda os dados.

Pedido do usuário (2026-10-25): *"Quero sim"*, em resposta ao meu relatório "O quê falta para terminar o deck do Verminister?" (itens 1 e 3: texto desatualizado; Spellbook e rulings nunca rodados).

> **STATUS DESTA PASTA:** fechada em 2026-10-28. Verificação de reprodutibilidade: `bash orquestracao/verificar_reproducao.sh --tudo` → **18/18 saídas byte a byte iguais** (tabelas do A/B, smoke, bit-identidade, regressão e os 4 brutos re-simulados, comparados com `cmp`; `resumos/verificacao_reproducao.txt`). **Não conferidos por `cmp`:** `spellbook.txt`, `prob_combos.txt`, `enumera_condicoes.txt`, `audit_etb_sem_efeito_*.txt`, `determinismo.txt` e `rulings_vs_codigo.md` (dependem de rede, do arquivo vivo em outro diretório ou foram escritos à mão); o determinismo e o Spellbook foram rodados uma vez cada.

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

## Mapa: arquivo → o que é → código → status → onde aparece

| arquivo | o que é | código | status | tabela do log que o usa |
|---|---|---|---|---|
| `dados/raw_ab_2000.json.xz`, `raw_ab_10000.json.xz` | A/B padrão: `antes` + `depois` + 20 variantes `so_*` (uma correção por vez), N=2.000 / 10.000 | `orquestracao/driver.py ab` com `config.json` | usado (versão CORRIGIDA das variantes) | `resumos/ab_*.txt`; log: tabela principal e "Leitura por correção" |
| `dados/raw_ab_2000_resiliencia.json.xz`, `raw_ab_10000_resiliencia.json.xz` | idem, modo resiliência | idem | usado | `resumos/ab_*_resiliencia.txt` |
| `dados/scryfall_oraculo_rulings_2026-10-25.json` | oráculo + 131 rulings (54 cartas) ao vivo | `orquestracao/scry_rulings.py` | usado | `resumos/rulings_vs_codigo.md` |
| `dados/spellbook_rat_king_2026-10-25.json` | respostas do Spellbook (combos, "quase", `estimate-bracket`, controles) | `orquestracao/csb_ratking.py` | usado | log: "Combos do Spellbook"; `auditoria.md` §15 |
| `resumos/log_driver.txt` | log da 1ª execução `tudo` | `driver.py tudo` | **A PARTE DO A/B DESTE LOG É INVÁLIDA** (variantes `so_*` sem as chaves explícitas: todas iguais a `depois`); smoke, bit-identidade e regressão dessa execução valem e estão em `smoke.txt`, `bitident_20000.txt`, `regressao_20000.txt`. Os brutos dessa execução foram sobrescritos pelos da versão corrigida (não guardados) | log: seção "Primeira versão do A/B estava errada" |
| `resumos/log_driver_ab.txt` | log da execução corrigida (só A/B) | `driver.py ab` | usado | — |
| `resumos/bitident_20000.txt` | 21 chaves desligadas == snapshot `ANTES_da85341`, 20.000 × 2 modos: 0 diferentes | `driver.py bitid` | verificação | log: validação |
| `resumos/regressao_20000.txt` | 20.000 × 2 modos × 2 configurações: 0 exceções, 0 cartas acima do baralho; `mana_spent_this_turn` negativo em 60/49 (desligadas) e 80/74 (ligadas) | `driver.py reg` | verificação | log: validação |
| `resumos/smoke.txt` | biblioteca de 99 cartas, 0 desconhecidas; 200 partidas × 2 modos, vivo e snapshot | `driver.py smoke` | verificação | log: validação |
| `resumos/determinismo.txt` | 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos: 0 divergentes | `varredura-2026-10-05/scripts/det_check.sh rat-king-verminister ratking_goldfish_v1.py 8 1500` | verificação | log: validação |
| `resumos/prob_combos.txt` | probabilidade dos 2 combos por turno (forma fechada + simulador, 20.000 partidas, 12 turnos) | `orquestracao/prob_combos.py` (rodado sobre a cópia fixada de `codigo/…DEPOIS.py`) | usado | log e `auditoria.md` §15 |
| `resumos/resumo_variantes_10000.md`, `resumos/resumo_novos_10000.txt` | tabela por correção; campos novos e probabilidade dos combos no A/B | `resumo_variantes.py`, `resumo_novos.py` | usado (verificados por `cmp`) | log: "Leitura por correção" |
| `resumos/enumera_condicoes.txt` | quem satisfaz cada condição de tipo/cor, incluindo as fichas | `orquestracao/enumera_condicoes.py` | usado | `checklist-oraculo.md` |
| `resumos/carddb_vs_oraculo.txt` | `CARD_DB` × oráculo, 54 cartas, 0 divergências | `orquestracao/carddb_vs_oraculo.py` | usado | `rulings_vs_codigo.md` |
| `resumos/audit_etb_sem_efeito_{ANTES,DEPOIS}.txt` | varredura nova (ETB/feitiço sem efeito; gatilho sem reação) no snapshot e no pinado | `varredura-2026-10-05/scripts/audit_etb_sem_efeito.py` | usado | log |
| `resumos/rulings_vs_codigo.md` | cada ruling × código × situação (escrito à mão) | — | usado | `checklist-oraculo.md` |
| `codigo/ratking_goldfish_v1_ANTES_da85341.py` | o simulador como estava antes (o "antes" de tudo) | — | usado | — |
| `codigo/ratking_goldfish_v1_DEPOIS.py` | o simulador fixado usado pelo A/B e pela verificação (== o arquivo vivo; conferido por `cmp` em `--tudo`) | — | usado | — |
| `orquestracao/testes_dirigidos.py` | 37 testes dirigidos (chave ligada e desligada) | — | verificação (37/37 passam; rodar: `python3 -I orquestracao/testes_dirigidos.py orquestracao/config.json`) | log: validação |

Comandos que refazem as tabelas: `bash orquestracao/verificar_reproducao.sh` (rápido, só dos brutos) e `bash orquestracao/verificar_reproducao.sh --tudo` (re-simula tudo numa pasta temporária; **não editar o simulador enquanto roda**).

## Escopo (Regra #7): o que esta rodada NÃO fez

- **Não decidi** (esperam o usuário): wipes sem efeito no próprio campo (Kindred Dominance, Swarmyard Massacre, Damnation), a face de terreno de Fell the Profane // Fell Mire, e o Bracket declarado (2) diante do combo Marrow-Gnawer + Thornbite Staff.
- **Políticas minhas, não do oráculo:** Equip {4} só no Marrow-Gnawer; ping do Staff com o mana que sobra na 2ª fase principal; o teto do loop do combo (40 Rats / 12 voltas) e o do Plague com Ayara (60 fichas); o extort paga se isso não tira outra conjuração que a mão já tem; o sneak devolve primeiro uma ficha de Rat de turnos anteriores e só depois uma carta pronta.
- **Não varrido:** o modo de resiliência cláusula a cláusula (só o wipe do oponente foi lido); a política de Black Market Connections (escolhe sempre os 3 modos e a vida pode passar de 0 sem perder); mulligan/keep; `proxy_damage_total` conta "each opponent loses X" como X por gatilho, não X × oponentes (convenção do arquivo; a vida ganha sim usa `NUM_OPPONENTS` onde o oráculo diz "that much");
  o scanner `audit_etb_sem_efeito.py` só exercita 6 eventos-padrão e só roda neste simulador; Spellbook nos outros 38 decks sem registro; ETB fantasma nos outros 19 simuladores.
- **Provas que são apenas de uma execução:** Spellbook (1×), determinismo (1×, 3 hash seeds), scanner (1×).
- O invariante genérico "contador negativo" de `mana_spent_this_turn` sobe de 60/49 para 80/74 partidas de 20.000 com as chaves ligadas; é a mana líquida de rituais somada como gasto negativo, mas **não investiguei qual chave a faz subir**.
