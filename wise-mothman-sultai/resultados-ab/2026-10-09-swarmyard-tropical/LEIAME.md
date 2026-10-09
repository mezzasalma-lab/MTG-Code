# 2026-10-09 — Mothman: Swarmyard → Tropical Island

Pedido do usuário (2026-10-09), depois do levantamento de Insetos da lista (só The Wise Mothman e Icetill Explorer): *"Troca o Swarmyard pela Tropical"*. **Lista APLICADA** em `lista.md` e no `DECKLIST_TEXT` do simulador (trocada NO LUGAR): sai **Swarmyard**, entra **Tropical Island**. A lista anterior está em `../../lista-anterior-2026-10-09.md`. Esta troca **revoga** a decisão da rodada anterior (*"a Swarmyard fica: regenera o comandante"*, `../2026-10-09-terrenos-proxy/`): a decisão é do usuário; abaixo está o que ela custa e o que sobra.

## Conclusão (medido × raciocinado)

N = 10.000 por variante e modo, pareado, trocas `no lugar` (`SWAP_IN_PLACE`: a permutação do baralho não muda), sementes 3.000.000+i, 12 turnos; `*` = excede o IC95%. Base = a lista de antes desta troca (com a Swarmyard).

1. **A troca (e1)** (`resumos/tabela_w.md`; padrão / resiliência): comandante conjurado até T4 **+1,91 ± 0,30 \* / +1,69 ± 0,30 \***; mesa limpa até T8 **+1,42 ± 0,41 \* / +0,84 ± 0,36 \***, T10 +0,93 / +1,04; 1º oponente fora até T6 +1,35 / +0,82; deck-out +0,12 ± 0,21 / +0,04 (sem efeito). O ganho vem de quantidade e cor de mana: a Swarmyard produzia só `{C}`, a Tropical Island produz `{G}` ou `{U}` desvirada, sem custo, e conta como Forest para a Shifting Woodland, a Nature's Lore, a Three Visits e as 3 fetches.
2. **O que se perde: toda a regeneração da lista.** A Yavimaya Hollow já tinha saído na rodada anterior; com a Swarmyard fora, **não sobra nenhuma fonte de regeneração**. Quanto a Swarmyard fazia no simulador (`resumos/base_nova.md`, resiliência, único modo com remoção): regeneração usada em **0,44% das partidas** (0,0044 por partida) com a remoção pontual nunca mirando o comandante e em **0,62%** quando 50% das remoções pontuais miram o comandante (lote V); no modo padrão não há remoção, logo 0. Mesmo com 50% de remoção no comandante a troca continua ganhando: T8 resiliência **+0,51 ± 0,36 \***, comandante até T4 +1,69 \*, T10 +0,90 \*. Os dois únicos Insetos que ela cobria eram o comandante e o Icetill Explorer (`../2026-10-09-terrenos-proxy/resumos/insetos_da_lista.txt`). **Premissa do simulador, não medida de mesa real:** toda remoção do oponente é "destroy" (a Swarmyard só regenera contra isso) e o 0,5 de comandante-alvo é palpite meu; mesa real costuma mirar mais o comandante, e contra exílio / −X/−X / "can't be regenerated" a Swarmyard nunca valeu.
3. **O que protege o comandante e o Icetill sem regeneração** (raciocinado, a partir das proteções que o simulador modela e da lista): (oráculo lido no cache do Scryfall) Heroic Intervention (hexproof e indestrutível para todos os seus permanentes), Smuggler's Surprise (modo `{1}`: criaturas de poder ≥ 4 ganham hexproof e indestrutível), Plaza of Heroes (`{3}`, `{T}`, exila: uma criatura LENDÁRIA ganha hexproof e indestrutível: protege o Mothman, não o Icetill), Swiftfoot Boots (hexproof, mas só se já estiver equipada: equipar é velocidade de feitiço), e as respostas na pilha: Fierce Guardianship e Glen Elendra Archmage (só magia que não é criatura), Arcane Denial (qualquer magia), Repulsive Mutation ("a menos que pague"). Contra "destroy" sem uma delas na mão, o comandante agora morre.
4. **Nova linha de base** (`resumos/base_nova.md`; padrão / resiliência): comandante até T4 **65,4% / 60,1%**, até T5 78,3% / 72,6%; mesa limpa até T7 19,2% / 7,5%, **T8 59,6% / 28,0%**, T10 88,9% / 62,5%; 1º oponente fora até T6 45,3% / 27,4%; deck-out 2,66% / 1,52%. (Antes da troca: T4 63,5% / 58,4%, T8 58,1% / 27,1%.) O simulador vivo com `SWAPS=()` é a lista aplicada (bit-idêntico ao ANTES + e1 `no lugar`: 40.000/40.000, `resumos/bitident_lista_20000.txt`). O campo de contadores de `base_nova.md` (`mothman_counters_placed_total`) **não** é o dos §17–§19 do `goldfish-log.md` (133/91): não comparar.
5. **Proposto e NÃO aplicado (precisa de um "sim" do usuário):** Bojuka Bog → Underground Sea por cima da troca (**e2**): contra a base, T8 **+2,61 ± 0,51 \* / +1,47 ± 0,44 \*** (≈ +1,2 / +0,6 sobre e1), comandante até T4 +3,19 / +2,94; com comandante-alvo 0,5, +1,07 ± 0,43 \* no T8 da resiliência (≈ +0,56 sobre e1). Custo: o Bojuka Bog é o tira-cemitério da lista (contra oponente real, estado que o simulador não modela; parte coberta pelo Soul-Guide Lantern, raciocinado).
6. **Spellbook** (`dados/spellbook_swtrop.json`, `resumos/log_spellbook_swtrop.txt`): 92 nomes resolvidos (não reconhecidos: nenhum), 2 combos na base; **e1 e e2: 0 combos novos, 0 perdidos, 0 "quase" combos criados ou derrubados**; a lista viva == e1 (conjunto de nomes). Controle positivo (Thassa's Oracle + Demonic Consultation aparece) e de corte (sem o Mindcrank some Bloodchief Ascension + Mindcrank) ok. A Tropical Island não é Game Changer (campo `game_changer` = false no Scryfall, conferido ao vivo em 2026-10-09); o Bracket não muda.

## O que mudou no simulador

**Nenhuma regra nova.** Só a lista: `DECKLIST_TEXT` (a linha `1 Swarmyard` virou `1 Tropical Island`, mesma posição) e `lista.md`. A Tropical Island (`add("Tropical Island", …, produces={"G","U"}, land_types={"Forest","Island"})`, rulings 2008-10-01 em `../2026-10-09-terrenos-proxy/dados/rulings_terrenos.json`) e a Swarmyard (`{T}: Add {C}` e `{T}: Regenerate target Insect, Rat, Spider, or Squirrel`) continuam no `CARD_DB`; a regeneração dela segue implementada e volta por `SWAPS=(("Tropical Island","Swarmyard"),)`.
Testes (`../../testes/testes_dirigidos.py`, **206/206**): o teste de `SWAPS` e o de partidas completas deixavam de achar a Swarmyard na lista e foram adaptados (usam o Bojuka Bog); teste novo `lista_viva_troca_swarmyard_por_tropical_e_os_insetos_continuam_dois` (a lista viva tem a Tropical Island e não a Swarmyard, tem Bayou e Vista e não Hollow e Passage, os Insetos são exatamente The Wise Mothman e Icetill Explorer, a Tropical produz G/U desvirada com os tipos certos, a Swarmyard volta por `SWAPS`).

## Escopo verificado e NÃO verificado (Regra #7)

**Varrido:** (a) o conceito "Inseto / Rato / Aranha / Esquilo / Changeling" na lista, por script no Scryfall ao vivo (`../2026-10-09-terrenos-proxy/orquestracao/insetos.py`); (b) todo ponto do código que lê a etiqueta `swarmyard` ou o nome (grep: `regenerate_sources`, `_try_protect_from_destroy`, `add(...)`; nenhum outro); (c) o conceito "Forest / Island" (Tropical conta pelos tipos, já testado na rodada anterior).
**NÃO verificado:** valor real de a lista ficar sem regeneração contra oponente humano (remoção que mira o comandante; o 0,5 é premissa minha); o simulador não separa a regeneração do comandante da do Icetill Explorer (`regenerations_used` soma as duas); remoção de terreno não básico do oponente (Wasteland, Blood Moon) contra a Tropical Island; uma só família de sementes; pedras e rampa.

## Validação

| o quê | resultado | arquivo |
|---|---|---|
| testes dirigidos | **206/206** | `../../testes/testes_dirigidos.py` |
| smoke (99 cartas, 90 distintas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos sem exceção) | ok nas 3 listas | `resumos/smoke_swtrop.txt` |
| bit-identidade: vivo `SWAPS=()` == ANTES congelado + e1 `no lugar` | 40.000/40.000 (4 fatias × 5.000 sementes × 2 modos, sementes 9.400.000+) | `resumos/bitident_lista_20000.txt` |
| regressão 20.000 × 2 modos, sementes 5.000.000+i (e1) | 0 exceções, 0 carta acima do baralho, 0 contador negativo | `resumos/regressao_swtrop_20000.txt` |
| determinismo: 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo (vivo; vivo com `COMMANDER_REMOVAL_SHARE=0.5`) | 0 divergências nos 2 casos | `resumos/determinismo.txt` |
| replicação cruzada: `base` do lote W == `d1` do lote Z de `../2026-10-09-terrenos-proxy`; `base` do V == `d1` do z50 | **3/3 séries**, 10.000 partidas cada, 0 divergências | `resumos/replicacao.txt` |
| reprodutibilidade (`orquestracao/verificar_reproducao.sh --tudo`) | **6/6** saídas iguais com `cmp` (as 2 tabelas, a base nova, a replicação, o índice, e a re-simulação de base e e1: 1.000 sementes × 2 modos + resiliência com 0,5 = 6/6 séries 1000/1000) | `resumos/verificacao_reproducao.txt` |

(Regra #10, item 4: nenhuma verificação é vazia: as séries comparadas têm 10.000 partidas, o A/B tem diferenças com IC e o Spellbook tem 2 combos na base e os dois controles.)

## Mapa arquivo → o que é → status → tabela que o usa

| arquivo (`dados/`) | o que é | status | usado em |
|---|---|---|---|
| `raw_swtrop_10000[_resiliencia].json.xz` | lote **W**: base, e1 (Swarmyard → Tropical), e2 (e1 + Bojuka Bog → Underground Sea) × 2 modos, `COMMANDER_REMOVAL_SHARE=0` | usado | `resumos/tabela_w.md`, `base_nova.md` |
| `raw_swtrop50_10000_resiliencia.json.xz` | lote **V**: as mesmas 3 variantes, só resiliência, comandante-alvo 0,5 | usado | `resumos/tabela_v.md`, `base_nova.md` |
| `spellbook_swtrop.json` | Commander Spellbook (92 nomes, e1, e2, lista viva, 2 controles) | usado | acima |

Nenhum lote foi superado nem invalidado. Os `*_parcial.json.xz` e `*.done` do driver retomável foram apagados depois de os lotes fecharem. O `COMMANDER_REMOVAL_SHARE` do lote V é o único parâmetro que não é do jogo.

## Como refazer

```
bash descomprimir.sh                                                  # .json.xz -> dados_json/ (fora do git)
cd orquestracao
python3 rank_proxy.py swtrop | cmp - ../resumos/tabela_w.md          # idem: swtrop50 -> tabela_v.md
python3 base_nova.py | cmp - ../resumos/base_nova.md
python3 confere_replicacao.py | cmp - ../resumos/replicacao.txt
(cd .. && python3 indice_dados.py | cmp - resumos/indice_dados.md)
bash verificar_reproducao.sh --tudo                                    # tudo acima + re-simulação (PYTHONHASHSEED=0; NÃO editar o simulador congelado enquanto roda)
sha256sum -c ../SHA256SUMS
```

Gerado por `orquestracao/`: `lanca_tudo.sh` (lotes W e V e regressão), `driver_mm.py` (retomável por variante; `LOTES`, `TAG`, `MODOS`), `abgen.py` (harness, formato `colunas-v1`), `gera_config.py` (`config_w.json`, `config_v.json`), `csb_swtrop.py` + `csb_stefano.py` (Spellbook), `bitident_lista.py` (bit-identidade), `confere_replicacao.py`, `base_nova.py`, `resimula_amostra.py`. Sintaxe das variantes: `{"SWAPS": [["saiu","entrou"], …], "SWAP_IN_PLACE": true, "COMMANDER_REMOVAL_SHARE": 0.5}`. Simulador congelado: `codigo/mothman_goldfish_v1_ANTES.py` (= o vivo de antes da troca, `cmp` igual no momento da cópia).

## Incidentes

- A bateria de bit-identidade rodou em paralelo com o A/B (nice 19) sem afetar os resultados: o A/B usa só `codigo/…_ANTES.py` (congelado); o vivo é lido apenas pela bit-identidade e pelos testes.
- Os 92 nomes do Spellbook foram todos resolvidos antes das consultas (0 não reconhecidos), então nenhum foi ignorado em silêncio.
