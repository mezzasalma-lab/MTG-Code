# Tom Bombadil — goldfish log

Regra #5: o simulador é **evidência de apoio**. A análise do deck
(`construcao.md`) vem do oráculo, das regras e dos motores reais. O
goldfish tem convenções fixas: ataca com tudo, não modela bloqueio, não
tem oponente real, e interação com oponente conta como 📊 (proxy).

## v1 — construção inicial (2026-09-22) — RASCUNHO, aguardando revisão da lista pelo usuário

### Validação

| Checagem | Resultado |
|---|---|
| Smoke test da lista | 99 + comandante, 99 nomes únicos, 0 cartas fora do `CARD_DB` (asserts no import) |
| Testes dirigidos (`test_tom_goldfish.py`) | **57/57** passando (1+ por habilidade de cada carta, regras de Saga, resiliência) |
| Determinismo | mesmo hash com `PYTHONHASHSEED` 1/2/3 (300 seeds, padrão + resiliência) |
| Cache de mana (`mana_units`) | bit-idêntico ao cálculo sem cache (200 seeds × 10 turnos, mesmo md5); 8× mais rápido |
| Varredura de robustez (timeout 2 s/partida) | modo resiliência: 10.000 partidas, 0 exceções, 0 travamentos · modo padrão: **não concluída** (sessão interrompida) |
| Regressão 20.000 partidas × 10 turnos (padrão) | **não concluída** (sessão interrompida antes do fim; rodar de novo antes de usar os números) |
| Regressão 20.000 partidas × 10 turnos (resiliência) | **não concluída** com o código final (a rodada anterior, antes da correção de timing do Clockspinning, deu 0 exceções em 20.000) |

### Bugs achados antes do 1º commit (detalhes no `checklist-oraculo.md`)

1. Read ahead disparava os capítulos pulados (a regra diz que não disparam).
2. Resposta dentro da pilha (Clockspinning/Enlightened Tutor) resolvia a
   pilha por dentro. Com Flux Channeler, a Saga "salva" era sacrificada
   (Regra #6, orquestração).
3. Proliferate escolhia a Saga que acabou de ser salva.
4. Pareamento de cor guloso deixava o Tom na zona de comando com WUBRG
   disponível.
5. Tom tentado só 1× por fase; rampa do mesmo turno não liberava.
6. Hex Parasite comia a mana do Tom no 714.3b.
7. Escolha de terreno por "conserta cor" travava o 2-drop.
8. Motor de marcador conjurado antes de existir Saga.
9. Nexus Mentality sem o uso de valor real (modo 2 zerando Saga).
10. **Mágica em resposta aplicava o efeito na hora** e voltava pra mão
    (buyback do Clockspinning) com o gatilho do Flux ainda na pilha. A
    mesma cópia salvava várias Sagas numa cascata só, e a varredura de
    robustez pegou partidas com ~490 capítulos. Agora toda instantânea é
    um item real da pilha, embaixo dos gatilhos de conjuração dela.
11. Checagem "comandante preso" do modo de resiliência não contava o Tom
    fora de fase (Teferi's Protection): eram 345 falsos "stuck".

### Resultado de referência — 3.000 partidas, 8 turnos, seed_base 1.000.000

(`python3 tom_goldfish_v1.py` → `tom_v1_runs.jsonl`)

| Métrica | Valor |
|---|---|
| Tom conjurado | 91,6% · turno médio 5,30 · até o T5: 56,8% |
| **Gatilhos do Tom** (Saga de graça) | **1,50** por partida (valor de mana somado 7,2) |
| Turnos com Tom hexproof/indestrutível (4+ lore) | 0,98 |
| Sagas conjuradas / capítulos resolvidos / **capítulos finais** | 3,09 / 15,0 / **3,74** |
| Marcadores de saber adicionados / removidos | +21,0 / −1,7 |
| **Marcadores movidos** (Nesting, Goldberry, Resourceful, Power Conduit, Nexus) | **8,41** |
| Capítulos finais salvos (714.4) | 0,89 |
| Resourceful Defense: gatilhos / maior cadeia | 1,24 / 1,04 |
| **Rampa**: mana disponível na fase principal 1 | T2 1,9 · T3 3,1 · T4 4,5 · T5 6,0 · T6 7,6 · T8 12,3 |
| **Compra** extra | 9,2 cartas |
| **Interação** 📊 (miraria oponente) | 4,5 |
| **Recursão** (cemitério → mão/campo/topo) | 0,45 |
| **Letalidade**: dano proxy ≥ 120 (3 oponentes × 40, sem bloqueio) | 19,6% das partidas · turno médio 7,72 |
| **Combo infinito** (Smaug, ver abaixo) caído por acaso | 0,6% das partidas · turno médio 7,94 |
| Dano proxy médio (mediana) | 104,1 (49,0) · Narci 17,9 · Mega Flare 30,5 |
| Tokens / Treasures | 7,4 / 1,5 |
| 📊 não medível (Birth III, Fenrir III, Yojimbo IV) | 0,40 |
| Eliminações do Primal Odin II (sem bloqueio modelado) | 0,09 |
| Vida final / mulligans | 53,2 / 0,27 |
| Biblioteca esgotada (turno de combo real: cadeia de Resourceful + Narci + Femeref) | 18/3000 |

### Uso por habilidade (3.000 partidas, 8 turnos)

Média por partida e % de partidas em que disparou ao menos 1×. Tudo que
existe no código disparou em jogo real ao menos em parte das partidas.

| Habilidade | média | % partidas |
|---|---|---|
| cast | 0.92 | 83.3% |
| saga_sacrificed | 2.47 | 73.4% |
| tom_trigger | 1.37 | 71.5% |
| fetch | 0.96 | 65.2% |
| saved | 0.89 | 53.4% |
| read_ahead_choice | 1.52 | 44.6% |
| ring_tempts | 0.93 | 39.4% |
| transform | 0.38 | 37.7% |
| read_ahead_skip | 0.32 | 27.1% |
| proliferate | 0.77 | 27.0% |
| narci_drain | 1.15 | 26.8% |
| sythis_draw | 1.25 | 26.3% |
| resourceful_resolve | 1.26 | 24.7% |
| narci_draw | 0.88 | 24.4% |
| war_tutor | 0.48 | 22.4% |
| cruelty_tutor | 0.27 | 20.9% |
| historians_boon_soldier | 1.25 | 20.7% |
| creation_exile | 0.23 | 20.3% |
| setessan_draw | 1.32 | 20.2% |
| eidolon_draw | 1.47 | 19.6% |
| power_conduit | 0.44 | 19.4% |
| presence_draw | 0.92 | 19.0% |
| urza_tutor | 0.23 | 19.0% |
| estrid_cast_copy | 0.18 | 18.2% |
| satsuki_activate | 0.36 | 16.2% |
| goldberry_pull | 0.21 | 15.3% |
| weaver_copy | 0.31 | 15.2% |
| femeref_draw | 0.48 | 14.0% |
| mega_flare | 0.26 | 13.8% |
| creation_put | 0.15 | 13.6% |
| historians_boon_angel | 0.57 | 13.5% |
| resurgent_suspend | 0.13 | 13.0% |
| remnant_pay_x | 0.98 | 12.5% |
| bath_song_shuffle | 0.44 | 11.6% |
| hex_parasite | 0.34 | 11.3% |
| estrid_blink | 0.20 | 11.2% |
| legend_rule | 0.16 | 11.0% |
| oaka_draw | 0.16 | 9.9% |
| scholar_plains | 0.15 | 9.7% |
| strionic_copy_tom | 0.14 | 8.9% |
| awaken_return | 0.09 | 8.8% |
| replenish_returned | 0.14 | 8.7% |
| goldberry_push | 0.10 | 8.5% |
| kiki_copy | 0.14 | 7.8% |
| resurgent_cast | 0.07 | 7.0% |
| clockspinning_buyback | 0.12 | 6.4% |
| nesting_grounds | 0.10 | 6.4% |
| urza_construct | 0.08 | 6.1% |
| cruelty_reanimate | 0.06 | 5.1% |
| strionic_copy | 0.05 | 4.3% |
| smaug_treasures | 0.06 | 3.8% |
| cycling | 0.04 | 3.6% |
| okagachi_return | 0.05 | 3.6% |
| ecd_reanimate | 0.04 | 3.5% |
| hall_of_heliod_tom | 0.04 | 3.3% |
| eldest_reanimate | 0.04 | 3.1% |
| hall_of_heliod_end | 0.04 | 3.1% |
| starfield_return | 0.04 | 2.5% |
| resourceful_activated | 0.02 | 1.7% |
| nexus_draw | 0.08 | 1.3% |
| urza_starfield_0_0 | 0.01 | 1.3% |
| clockspinning_suspend | 0.01 | 1.1% |
| nexus_move | 0.01 | 1.0% |
| infinite_combo_smaug | 0.01 | 0.6% |
| estrid_copy_exiled_by_transform | 0.00 | 0.5% |
| clockspinning_fizzle | 0.00 | 0.3% |
| estrid_cast_nocopy | 0.00 | 0.1% |

Sagas que o Tom mais colocou em campo (3.000 partidas): Knights of Round
284 · Cruelty of Gix 242 · Coming of Galactus 203 · Eldest Reborn 197 ·
Kiora 195 · Primal Odin 193 · Helvault 192 · Birth 179 · Yojimbo 176 ·
War of the Last Alliance 175. O viés para as de maior valor vem do Enlightened
Tutor e do Hall of Heliod respondendo ao gatilho do Tom.

### Combo infinito real achado na lista (decisão do usuário)

**There and Back Again + Clockspinning + Hex Parasite** (com um Smaug já
em campo; o Flux Channeler também serve no lugar do Clockspinning para pôr
o marcador):

1. There and Back Again no capítulo II. O Clockspinning (modo "put another
   of those counters", com buyback = 4 manas) põe 1 lore e dispara o III.
2. Em resposta ao III, o Hex Parasite (`{1}{B/P}`, sem {T}, repetível)
   tira 1 lore. Pela 714.4, a Saga fica.
3. O III resolve e cria um Smaug novo. Pela regra da lenda o antigo vai pro
   cemitério ("dies") e dispara "create fourteen Treasure tokens".
4. A Saga continua no II. Cada volta custa cerca de 6 e rende 14: **mana
   infinita**. Com isso vêm Mega Flare do Bahamut repetido (Clockspinning
   + Hex Parasite nele) e dreno da Narci a cada III (5 × 3 oponentes).

São 3 cartas (mais o Smaug), então é **legal no Bracket 3**, que só proíbe
combo infinito de 2 cartas no começo do jogo. Mesmo assim, avisar na
mesa. O simulador **não busca** o combo de propósito: ele só aparece
quando as peças se juntam pela política normal (0,6% das partidas). Ao
detectar (III da There and Back Again resolvendo 3× no mesmo turno), a
partida é encerrada como vitória por combo (`infinite_combo_turn`).

### Leitura (Regra #5)

- O motor do comandante funciona do jeito que a lista foi desenhada: 3,8
  capítulos finais e 1,5 Saga de graça por partida em 8 turnos, com 8,7
  marcadores movidos. O eixo "mover marcadores" do pedido aparece de
  verdade no jogo, não só na lista.
- O ponto fraco medido é a **velocidade do Tom** (só 56,8% até o T5). É um
  custo real de WUBRG com 36 terrenos e 10 rampas. O goldfish também é
  conservador: o Exotic Orchard não produz cor, e as criaturas pequenas
  ficam reservadas para mana pela Enduring Vitality.
- Os 📊 (remoção por capítulo, Birth III, Kiora III etc.) são valor real
  que o goldfish não converte em número. Eles não diminuem a carta.
