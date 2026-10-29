# 2026-10-09 — Mothman: terrenos com proxy (Underground Sea, Bayou, Tropical Island, Prismatic Vista) e a Swarmyard que fica

> **Atualização (mesmo dia): a Swarmyard saiu por Tropical Island a pedido do usuário** (`../2026-10-09-swarmyard-tropical/LEIAME.md`). Tudo abaixo continua válido como o que foi medido e aplicado ATÉ essa troca; "a Swarmyard fica" foi revogado.

Pedidos do usuário (2026-10-09): *"Farei proxies, o que vc sugere"* e, depois da minha sugestão: *"Quero sim, a Swarmyard é para regenerar o comandante, que é mutant e insect"*. **Lista APLICADA** em `lista.md` e no `DECKLIST_TEXT` do simulador: **Yavimaya Hollow → Bayou** e **Fabled Passage → Prismatic Vista**; **a Swarmyard fica** (decisão do usuário: regenera o The Wise Mothman, que é Inseto Mutante). A lista anterior está em `../../lista-anterior-2026-10-08.md`. **Não aplicado (precisa de um "sim" do usuário):** Bojuka Bog → Underground Sea e, opcionalmente, Minamo ou Shifting Woodland → Tropical Island.

## Conclusão (medido × raciocinado)

N = 10.000 por variante e modo, pareado, trocas `no lugar` (`SWAP_IN_PLACE`: a permutação do baralho não muda), sementes 3.000.000+i, 12 turnos; `*` = excede o IC95%. Base = lista de 2026-10-08 (as cinco entradas já aplicadas).

1. **A troca aplicada (d1 = Hollow → Bayou + Passage → Vista)** (`resumos/tabela_z.md`): comandante conjurado até T4 **+2,32 ± 0,38 \* (padrão) / +2,25 ± 0,39 \* (resiliência)**; mesa limpa até T8 **+2,17 ± 0,52 \* / +1,14 ± 0,46 \***, T10 +1,37 / +1,67; 1º oponente fora até T6 +2,37 / +1,65; deck-out −0,32 ± 0,28 \* (padrão) / +0,02 (resiliência). Em separado (`tabela_x.md`): Hollow → Bayou T8 +1,77 / +1,09, Hollow → Underground Sea +1,22 / +0,76; Passage → Vista T8 +0,50 / +0,04 (o ganho da Vista é comandante até T3, +0,52, e vida mínima −0,36: ela custa 1 de vida e a Fabled Passage não).
2. **Swarmyard → Underground Sea** (`a3_swarmyard_sea`): T8 +1,23 ± 0,39 \* / +0,70 ± 0,34 \* e comandante até T4 +1,93 / +1,74. **O que a regeneração dela vale no simulador** (`resumos/base_aplicada.md`, modo resiliência, único com remoção): com a Swarmyard em campo a regeneração é usada em 1,18% das partidas e **sem ela em 0,66%** (a Hollow e o resto regeneram igual): a Swarmyard responde por **≈ 0,5 ponto de partidas**; com 50% das remoções pontuais mirando o comandante (premissa do lote Y), 1,48% contra 0,79%: **≈ 0,7 ponto**. É a premissa do simulador, não uma medida do jogo real: o motor anterior **nunca** mirava o comandante com remoção pontual (só o anulava na pilha e o incluía nos wipes), e toda remoção do oponente é tratada como "destroy" (a Swarmyard só regenera contra destroy, não contra exílio, −X/−X nem "can't be regenerated"). **Mantida por decisão do usuário**; o custo medido é o do item acima.
3. **Proposto e NÃO aplicado (d2, d3, d4, sobre d1):** Bojuka Bog → Underground Sea (**d2**: T8 +3,19 ± 0,59 \* / +1,82 ± 0,52 \* contra a base, ou seja ≈ +1,0 / +0,7 sobre d1; comandante até T4 +3,71 / +3,59); d2 + Minamo → Tropical Island (**d3**: +3,96 / +1,96); d2 + Shifting Woodland → Tropical Island (**d4**: +4,00 / +2,28). Com 50% das remoções mirando o comandante (resiliência, lote z50) d2 mantém o ganho: T8 +1,66 \* contra +1,17 de d1. O Bojuka Bog serve de tira-cemitério contra oponente real, que este simulador não modela: parte desse papel o Soul-Guide Lantern cobre (raciocinado). **Triagem com básicos** (`tabela_x.md`): Waterlogged Grove → Island **piora** (T8 −1,07 \* / −0,67 \*: fica); Minamo → Island 0; Shifting Woodland → Forest +0,20 / +0,11 (dentro do IC); Bojuka Bog → Swamp +0,96 \* / +0,54 \*; Plaza of Heroes → Swamp já piorava em 2026-10-08 (fica).
4. **Nova linha de base (lista aplicada, `resumos/base_aplicada.md`):** padrão / resiliência — comandante até T4 **63,5% / 58,4%**, até T5 76,6% / 70,9%; mesa limpa até T7 18,6% / 7,3%, **T8 58,1% / 27,1%**, T10 87,9% / 61,4%; 1º oponente fora até T6 44,0% / 26,6%; deck-out 2,54% / 1,48%; contadores +1/+1 133,3 / 91,2; gatilhos do Mothman 26,3 / 23,3. O simulador vivo com `SWAPS=()` é a lista aplicada (bit-idêntico ao ANTES + d1 `no lugar`: 40.000/40.000, `resumos/bitident_lista_20000.txt`).
5. **Spellbook** (`dados/spellbook_proxy.json`, `resumos/log_spellbook_proxy.txt`): 94 nomes resolvidos (não reconhecidos: nenhum), 2 combos na base, **d1, d2, d3, d4, c1, v1 e as quatro entradas isoladas: 0 combos novos, 0 perdidos**; a lista viva == d1 (como conjunto de nomes). Controle positivo (Thassa's Oracle + Demonic Consultation aparece) e controle de corte (cortar o Mindcrank derruba Bloodchief Ascension + Mindcrank) ok. Nenhuma das quatro (nem a Swarmyard) é Game Changer: campo `game_changer` = false no Scryfall, conferido ao vivo em 2026-10-09; o Bracket não muda.

## O que mudou no simulador (código congelado: `codigo/`)

`orquestracao/patch_terrenos.py` aplicado sobre `codigo/mothman_goldfish_v1_ANTES.py` produz `codigo/mothman_goldfish_v1_DEPOIS.py` (todo o A/B rodou nele). O simulador vivo = DEPOIS + as duas trocas na lista. **Oráculo e rulings lidos ANTES do código** (`dados/rulings_terrenos.json`, Scryfall ao vivo em 2026-10-09):

- **Underground Sea / Bayou / Tropical Island:** `({T}: Add {X} or {Y}.)`, tipos `Island Swamp` / `Swamp Forest` / `Forest Island`. Rulings (2008-10-01): tem as duas habilidades de mana dos tipos básicos; **não é terreno básico mas tem os tipos básicos**: "things that affect basic lands don't affect it; things that affect basic land types do". No código: entram desvirados, sem custo e sem dano, produzem as duas cores, `land_types` com os dois tipos (por isso Nature's Lore, Three Visits, Shifting Woodland e as fetches os enxergam; Prismatic Vista **não** os acha, porque pede "basic land card").
- **Prismatic Vista:** `{T}, Pay 1 life, Sacrifice this land: Search your library for a basic land card, put it onto the battlefield, then shuffle.` Sem rulings. `crack_fetch` com a etiqueta `vista`: 1 de vida, sacrifica, busca **qualquer** básico (não só os dois tipos de um fetch comum), embaralha, o terreno entra **desvirado** (diferente da Fabled Passage, que entra desvirado só com 4+ terrenos e não paga vida).
- **Swarmyard:** `{T}: Add {C}.` e `{T}: Regenerate target Insect, Rat, Spider, or Squirrel.` Já estava no simulador (só alvos desses 4 tipos; o Mothman é Inseto Mutante). **Não foi alterado.**
- **Chave nova `COMMANDER_REMOVAL_SHARE`** (padrão 0,0 = comportamento anterior, bit-idêntico): com valor > 0 e o comandante em campo, essa fração das remoções pontuais do oponente (modo resiliência) mira o comandante. Existe para medir a Swarmyard; **0,5 é premissa minha, não dado**; mesas reais costumam mirar mais.

**Insetos da lista (2026-10-09, `resumos/insetos_da_lista.txt`, script `orquestracao/insetos.py`, Scryfall ao vivo, 91 de 91 nomes resolvidos):** só **dois** Insetos: **The Wise Mothman** (Legendary Creature — Insect Mutant) e **Icetill Explorer** (Creature — Insect Scout, 2/4). **Nenhum** Rato, Aranha ou Esquilo (os outros alvos da Swarmyard), nenhum Changeling / Kindred / "every creature type" e nenhuma carta que crie ficha desses tipos ou mude tipo; a própria Swarmyard é o único texto que lê "Insect". O simulador já trata os dois como Inseto (`subtypes={"Insect", ...}`).

## Escopo verificado e NÃO verificado (Regra #7)

**Varrido, com método:** (a) os tipos de terreno, por grep + enumeração de oráculo no cache (cartas da lista com texto que lê tipo de terreno ou "basic land": Nature's Lore e Three Visits (Forest), Shifting Woodland (Forest), Misty Rainforest, Polluted Delta e Verdant Catacombs (pares de tipos), Prismatic Vista (basic), Assassin's Trophy (busca de básico do oponente), Cold-Eyed Selkie (Islandwalk, opõe-se a Island do OPONENTE) e Boseiju (nonbasic land do oponente): nenhuma lê um terreno meu de modo que os duais mudem o resultado além dos listados); (b) teste dirigido dos três duais, das três fetches contra eles e da Vista (205/205); (c) bit-identidade, regressão, determinismo, reprodutibilidade (abaixo).
**NÃO verificado:** valor dos duais contra remoção de terreno do oponente (Wasteland, Blood Moon, Back to Basics: estado de oponente, estrutural: "nonbasic" é a cláusula real, e é uma desvantagem real dos duais originais num pod com isso); custo de vida da Vista e das fetches (a vida só importa onde algo a lê: deck-out e vida mínima); a premissa 0,5 do comandante-alvo; uma só família de sementes; Tropical Island / Bog / Minamo / Woodland só medidos, não aplicados; pedras e rampa; para quem a Swarmyard regenera, a lista tem só **dois** Insetos (enumerados por script no Scryfall ao vivo em 2026-10-09: The Wise Mothman e Icetill Explorer; nenhum Rato, Aranha, Esquilo nem Changeling, nenhuma ficha desses tipos), e o simulador já protege os dois (a Swarmyard só aceita alvo com subtipo Insect; o Icetill está em `INTERACTION_ENGINE_PRIORITY`), mas `regenerations_used` não separa o alvo: não sei quanto das regenerações foi do comandante e quanto do Icetill; quantas vezes a regeneração do comandante realmente o salvaria numa mesa real.

## Validação

| o quê | resultado | arquivo |
|---|---|---|
| testes dirigidos | **205/205** (5 novos: duais entram desvirados e produzem as duas cores com os dois tipos; as 3 fetches acham os 3 duais pelos tipos certos com controle negativo; Vista paga 1 de vida e acha qualquer básico desvirado; chave desligada não mira o comandante, ligada mira e a Swarmyard regenera só Inseto; partidas completas) | `../../testes/testes_dirigidos.py` |
| smoke (99 cartas, 89 ou 90 distintas, 0 desconhecidas, 0 duplicadas não básicas, 200 partidas × 2 modos sem exceção) | ok nas 18 listas (13 do lote X + 5 do Z) | `resumos/smoke_terrenos3.txt`, `smoke_terrenos4.txt` |
| bit-identidade com a chave desligada: vivo/DEPOIS com `SWAPS=()` == ANTES | 40.000/40.000 (4 fatias × 5.000 × 2 modos) | `resumos/bitident_20000.txt` |
| bit-identidade da lista: vivo `SWAPS=()` == DEPOIS + d1 `no lugar` | 40.000/40.000 | `resumos/bitident_lista_20000.txt` |
| regressão 20.000 × 2 modos, sementes 5.000.000+i: c1, v1 (lote X), d3 (lote Z), d1 = lista aplicada | 0 exceções, 0 carta acima do baralho, 0 contador negativo (d2 e d4 só têm o smoke de 200 partidas × 2 modos; d3 contém as trocas de d2) | `resumos/regressao_terrenos3_20000.txt`, `regressao_terrenos4_20000.txt`, `regressao_aplicada_20000.txt` |
| determinismo: 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos, campo a campo (vivo; vivo com `COMMANDER_REMOVAL_SHARE=0.5`; d3 com 0,5) | 0 divergências nos 3 casos | `resumos/determinismo.txt` |
| replicação cruzada: `base` de terrenos3 == `s4_vats_wave_dsp` de `../2026-10-08-cinco-entradas-remocao`; terrenos3 == terrenos4; cmd50 == z50 | **5/5 séries**, 10.000 partidas cada, 0 divergências | `resumos/replicacao.txt` |
| reprodutibilidade (`orquestracao/verificar_reproducao.sh --tudo`) | **8/8** saídas iguais com `cmp` (as 4 tabelas, a base aplicada, a replicação, o índice, e a re-simulação de base e d1: 1.000 sementes × 2 modos + resiliência com 0,5 = 6/6 séries 1000/1000) | `resumos/verificacao_reproducao.txt` |

(Regra #10, item 4: nenhum número acima é de verificação vazia: as séries comparadas têm 10.000 partidas, o A/B tem diferenças com IC, e o Spellbook tem 2 combos na base e os dois controles.)

## Mapa arquivo → o que é → status → tabela que o usa

| arquivo (`dados/`) | o que é | status | usado em |
|---|---|---|---|
| `raw_terrenos3_10000[_resiliencia].json.xz` | lote **X**: 13 variantes (base; a1–a3 Hollow/Swarmyard → Sea/Bayou; s1–s4 básicos no lugar de Bog / Woodland / Grove / Minamo; v1 Passage → Vista; c1–c4 pares) × 2 modos, `COMMANDER_REMOVAL_SHARE=0` | usado | `resumos/tabela_x.md` |
| `raw_cmd50_10000_resiliencia.json.xz` | lote **Y**: 6 variantes, só resiliência, comandante-alvo 0,5 | usado | `resumos/tabela_y.md` |
| `raw_terrenos4_10000[_resiliencia].json.xz` | lote **Z**: base, d1 (aplicada), d2, d3, d4 × 2 modos | usado (d1 = nova linha de base) | `resumos/tabela_z.md`, `base_aplicada.md` |
| `raw_z50_10000_resiliencia.json.xz` | lote **Z50**: base, d1, d2, comandante-alvo 0,5 | usado | `resumos/tabela_z50.md` |
| `rulings_terrenos.json` | oráculo + rulings (Scryfall, 2026-10-09) de Vista, Sea, Bayou, Tropical, Swarmyard | usado | acima |
| `spellbook_proxy.json` | Commander Spellbook (94 nomes, 10 variantes, 2 controles) | usado | acima |
| `scryfall_lista_2026-10-09.json.xz` | resposta bruta do Scryfall (ao vivo) das 91 cartas distintas da lista aplicada | usado | `resumos/insetos_da_lista.txt` (pergunta do usuário: *"Quais outros insetos temos no deck?"*; não é refeita offline pelo `verificar_reproducao.sh`: o script consulta a API, o bruto fica aqui) |

Nenhum lote foi superado nem invalidado. Os `*_parcial.json.xz` e `*.done` do driver retomável foram apagados depois de os lotes fecharem. O `COMMANDER_REMOVAL_SHARE` do lote Y e Z50 é o único parâmetro que não é do jogo.

## Como refazer

```
bash descomprimir.sh                                                  # .json.xz -> dados_json/ (fora do git)
cd orquestracao
python3 rank_proxy.py terrenos3 | cmp - ../resumos/tabela_x.md       # idem: cmd50 -> tabela_y.md, terrenos4 -> tabela_z.md, z50 -> tabela_z50.md
python3 base_aplicada.py | cmp - ../resumos/base_aplicada.md
python3 confere_replicacao.py | cmp - ../resumos/replicacao.txt
(cd .. && python3 indice_dados.py | cmp - resumos/indice_dados.md)
bash verificar_reproducao.sh --tudo                                    # tudo acima + re-simulação (PYTHONHASHSEED=0; NÃO editar o simulador enquanto roda)
sha256sum -c ../SHA256SUMS
```

Gerado por `orquestracao/`: `lanca_tudo.sh` (lotes X, Y e regressão), `lanca_z.sh` (Z, Z50 e regressão), `driver_mm.py` (retomável por variante; variáveis `LOTES`, `TAG`, `MODOS`), `abgen.py` (harness, formato `colunas-v1`), `gera_config.py` (os 4 `config_*.json`; `config_reg_d1.json` é a regressão da lista aplicada), `csb_proxy.py` + `csb_stefano.py` (Spellbook), `bitident_terrenos.py` e `bitident_lista.py` (bit-identidade), `patch_terrenos.py`. Sintaxe das variantes: `{"SWAPS": [["saiu","entrou"], …], "SWAP_IN_PLACE": true, "COMMANDER_REMOVAL_SHARE": 0.5}`.

## Incidentes

- Reinício do contêiner derrubou lotes em andamento nas rodadas anteriores: o `driver_mm.py` é retomável por variante (`*_parcial`), os lotes X, Y, Z, Z50 fecharam sem perda.
- O simulador vivo foi editado (lista aplicada, chave, testes) **depois** de o A/B terminar e **antes** da verificação final; por isso o A/B roda no congelado (`codigo/…_DEPOIS.py`) e a ponte é a bit-identidade vivo × DEPOIS + d1 (40.000/40.000).
