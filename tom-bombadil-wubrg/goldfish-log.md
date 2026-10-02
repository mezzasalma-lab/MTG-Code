# Tom Bombadil — goldfish log

Regra #5: o simulador é **evidência de apoio**. A análise do deck
(`construcao.md`) vem do oráculo, das regras e dos motores reais. O
goldfish tem convenções fixas: ataca com tudo, não modela bloqueio, não
tem oponente real, e interação com oponente conta como 📊 (proxy).

**Dados brutos arquivados (Regra #8):** partidas manuais #6 e #7 (2026-09-30), #8 (2026-10-01), #9, #10 e #11 (2026-10-02) em
`tom-bombadil-wubrg/resultados-ab/2026-09-30-partida-manual-6/`, `.../2026-09-30-partida-manual-7/`, `.../2026-10-01-partida-manual-8/`, `.../2026-10-02-partida-manual-9/`, `.../2026-10-02-partida-manual-10/` e `.../2026-10-02-partida-manual-11/`
(`LEIAME.md` em cada uma: origem, mapa de arquivos, comandos, `cmp`; a #7 inclui a sensibilidade do Exotic Orchard).

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

### Combo infinito real achado na lista (mantido por decisão do usuário, 2026-09-22)

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

## Teste descartado — 10 duals originais (2026-09-22, decisão do usuário)

Foi testado trocar os 6 shocks e as 4 tri-lands de Nova Capenna pelas 10
duals originais (commit `432d469`, revertido). Resultado nas mesmas 3.000
seeds (8 turnos):

| Métrica | Lista atual (shocks + SNC) | 10 duals | Duals + SNC, −4 básicos |
|---|---|---|---|
| Tom conjurado em 8 turnos | 91,6% | 89,6% | 91,9% |
| Tom até o T5 | 56,8% | 57,2% | 58,1% |
| Mana na fase 1, T2 / T3 | 1,9 / 3,1 | 2,0 / 3,3 | 1,9 / 3,1 |
| Vida final | 53,2 | 56,3 | 56,6 |

As duals dão 2 cores contra 3 das tri-lands. Com elas, subiram as partidas
com 5+ manas mas sem alguma cor para o Tom (139 → 177). O usuário decidiu
**voltar à lista anterior**, sem as duals.

## Partidas manuais reais (Archidekt playtester)

Registradas aqui pra comparar com os números do simulador (Regra #5: o
goldfish é evidência de apoio — a partida manual real é sinal mais forte
ainda, é a regra real sendo jogada por uma pessoa). Auditoria feita
cláusula por cláusula contra o oráculo ao vivo do Scryfall (Regra #1);
duas cartas tinham texto que eu tinha de cabeça desatualizado (Archon of
Cruelty, sem mais cláusula de sacrificar terreno; Summon: Knights of Round,
capítulos I–IV criam 3 tokens cada, não só o I) — corrigido antes de fechar
a auditoria, nunca assumido de memória.

### Partida manual #1 (2026-09-23) — 0 erros de regra encontrados

Mão inicial mantida (keep): Summon: Knights of Round, Farseek, Jetmir's
Garden, Ketria Triome, Utopia Sprawl, Indatha Triome, Sol Ring.

| Turno | Evento principal |
|---|---|
| T1 | Land drop Jetmir's Garden (Triome, entra virado) |
| T2 | Sol Ring (1 mana de Jetmir's Garden) · land drop Ketria Triome |
| T3 | Farseek busca Zagoth Triome (válido — tem tipo Swamp/Forest/Island, Farseek só exclui a Forest básica) · Utopia Sprawl encanta um Forest-type · land drop Swamp |
| T4 | **Tom Bombadil conjurado** (WUBRG exato: Swamp→B, Jetmir's Garden→W, Ketria Triome→R, Zagoth Triome→U, Indatha Triome→G; taxa 0, 1ª conjuração) · land drop Indatha Triome |
| T5 | Summon: Knights of Round conjurada (8 mana) → capítulo I, 3 Knights 2/2 · land drop Mountain |
| T6 | Vários disparos de capítulo em Knights of Round via os motores de mover/somar marcador do deck (capítulos I–IV, 3 tokens cada vez) · Faeburrow Elder conjurada · **Archon of Cruelty** (interação simulada do oponente): descarta Serra's Sanctum da mão + sacrifica 1 Knight token |
| T7-T8 | There and Back Again, Leyline Binding, Summon: Bahamut em campo · **All Is Dust** (interação simulada) sacrifica todo permanente colorido — Tom (WUBRG) vai pra zona de comando pela 903.9a; só o Bahamut (incolor) sobrevive |
| T9 | **Replenish** devolve todos os encantamentos do cemitério pro campo de uma vez (Knights of Round, Yojimbo, There and Back Again, Leyline Binding, Fertile Ground, Utopia Sprawl) — cada Saga volta com 1 marcador (ETB), capítulo I dispara de novo em todas · Tom reconjurado da zona de comando (taxa 2) |

**Conferido e correto**: sequência de mana do Tom (T4, sem erro), alvo do
Farseek, alvo do Utopia Sprawl, capítulos da Knights of Round batendo com
o oráculo real, Archon of Cruelty e All Is Dust como interação simulada
contra o jogador, replacement 903.9a mandando o Tom pra zona de comando
em vez do cemitério, e a recursão total via Replenish reiniciando o
capítulo I de toda Saga que voltou.

**Não confirmado com certeza** (log bruto do Archidekt tem undo/redo
misturado, mas não muda a legalidade de nada acima): a sequência exata de
qual carta moveu/somou cada marcador de saber na Knights of Round no T6
(Nesting Grounds/Goldberry/Resourceful Defense/Hex Parasite/Clockspinning
são as candidatas reais do deck pra isso).

### Partida manual #2 (2026-09-23) — travada em 2 terrenos, 0 erros de regra

Mão inicial de 7 sem nenhum terreno (Prismatic Omen, Scholar of New
Horizons, Jugan Defends the Temple, Leyline Binding, Swords to Plowshares,
Kiora Bests the Sea God, Enduring Vitality) — mulligan correto. Mulligan
gratuito (regra da casa do Archidekt/mesa), mantida a segunda mão de 7 com
1 terreno (Spara's Headquarters): Prismatic Omen, Awaken the Honored Dead,
Femeref Enchantress, Spara's Headquarters, The Kami War, War of the Last
Alliance, Narci, Fable Singer.

| Turno | Evento |
|---|---|
| T1 | Draw Karn's Bastion · land drop Spara's Headquarters (entra virado) |
| T2 | Draw Ripples of Potential · land drop Karn's Bastion · **Prismatic Omen** conjurada (`{1}{G}`, 2 mana — bati o custo real no Scryfall, não é `{2}{G}` como eu tinha de cabeça) |
| T3 | Draw Elspeth Conquers Death · **Femeref Enchantress** conjurada (`{G}{W}`) — só legal por causa da Omen: ela dá a **todo terreno seu todos os 5 tipos básicos**, e terreno com tipo básico tem a habilidade de mana daquela cor mesmo sem texto impresso (CR 305.6-adjacente) — assim o Karn's Bastion (só fazia `{C}`) e o Spara's Headquarters passam a produzir qualquer uma das 5 cores |
| T4 | Draw Summon: Yojimbo — sem land drop |
| T5 | Draw Summon: Primal Odin — sem land drop. **Travado em 2 terrenos**, usuário reinicia a partida com a mesma mão pra testar de novo |

**Conferido e correto**: land drops, custo real da Prismatic Omen, e a
legalidade da Femeref Enchantress via o fixing de cor da Omen. O travamento
em 2 terrenos é variância real (mão de 7 com 1 terreno + 4 compras seguidas
sem nenhum terreno), não bug — a Omen resolve cor, nunca quantidade.

### Partida manual #3 (2026-09-23) — replay da mesma mão da #2, 0 erros de regra

Mesma mão mantida da partida #2, mas puxou terrenos diferentes desta vez
(o embaralhamento do restart é outro). Auditoria confirmada com trace
programático (não de memória — importava pro ponto do Tom abaixo).

| Turno | Evento |
|---|---|
| T1-T4 | Land drops Spara's Headquarters, Karn's Bastion, Exotic Orchard · Arcane Signet (`{2}`) · **Prismatic Omen** conjurada (`{1}{G}`, Arcane Signet fazendo G da identidade do comandante + Karn's Bastion genérico) |
| T5 | Fable of the Mirror-Breaker conjurada (`{2}{R}`, já com fixing da Omen) → capítulo I cria Goblin Shaman |
| T6 | Capítulo II da Fable dispara: **"discard up to two, draw that many"** — descarta Kami War + War of the Last Alliance, compra Reflecting Pool + Swamp (bati com o oráculo real). Land drop Swamp. **Tom Bombadil conjurado** (taxa 0) |
| T7 | Capítulo III da Fable resolve → **transforma** (não sacrifica) em Reflection of Kiki-Jiki — é capítulo final mesmo assim, **dispara o Tom** → Battle at the Helvault de graça. Land drop Reflecting Pool. Summon: Fenrir conjurada, capítulo I dispara na entrada e busca Mountain básico (bati com o oráculo real do Fenrir) |
| T8 | Island (land drop), Femeref Enchantress, Narci, Flux Channeler conjuradas |
| T9 | **Fenrir e Battle at the Helvault resolvem capítulo final no mesmo turno** (ambas sacrificadas, Avacyn criada) — só **1** Saga de graça entra (The Eldest Reborn), confirmando que o "once each turn" do Tom não foi violado mesmo com 2 finais simultâneos. Reflection of Kiki-Jiki copia o Flux Channeler real (`{1}`, T, alvo não-lendário). Jugan Defends the Temple conjurada, capítulo I cria Human Monk |

**Conferido e correto**: sequência de mana em toda mágica, capítulos II e
III da Fable batendo com o oráculo real, capítulo I do Fenrir buscando
terreno na entrada, e o ponto crítico — **2 capítulos finais resolvendo no
mesmo turno só geram 1 gatilho do Tom**, exatamente como a regra exige.

**Não confirmado com certeza** (ruído de undo/redo do Archidekt, mesmo
padrão da Utopia Sprawl na partida #1 — não muda legalidade): Femeref
Enchantress e Jugan Defends the Temple aparecem "recastadas" no log sem
nunca terem morrido. Também não persegui a fonte exata de cada +1/+1 do
Narci (o capítulo II do Jugan ainda não tinha disparado nesse ponto).

### Partida manual #4 (2026-09-23) — Strionic Resonator dobrando capítulos, 0 erros de regra

O usuário perguntou se a jogada estava certa; trace programático do JSON
confirmou que sim, com uma correção de entendimento (registrada aqui).

| Turno | Evento |
|---|---|
| T6 | Birth of the Imperium conjurada (Lore=1, ETB). Capítulo I dispara
("Create... Astartes Warrior... for each opponent"). **Strionic Resonator**
usado (tapado neste turno) pra copiar esse gatilho — 6 tokens em vez de 3 |
| T7 | Draw step leva o marcador de 1→2, cruzando o limiar do **capítulo II**
("Each opponent sacrifices a creature of their choice") — é aqui que o
sacrifício de verdade aconteceu. Tom Bombadil conjurado |
| T8 | Draw step leva o marcador de 2→3 (capítulo III final, "Sacrifice
after III", draw 2 per opponent with fewer creatures). Em resposta,
**Clockspinning com Buyback** tira 1 marcador (Lore 3→2, confirmado no
log) — pela 714.4 ela sobrevive. Como III é o capítulo final, dispara o
Tom; **Strionic Resonator usado de novo** (destapado no T7, tapado de
novo aqui) pra copiar o **gatilho do Tom** (não o da Birth) — 2 Sagas de
graça (Coming of Galactus + Summon: Bahamut). Summon: Knights of Round
volta do cemitério via **Starfield of Nyx** (upkeep, "return target
enchantment card from your graveyard") — ela tinha sido descartada no T7 |

**Correção de entendimento**: o usuário achou que salvar a Birth em 2
continuava disparando o **sacrifício** (capítulo II). Na verdade o
sacrifício só disparou 1 vez (T7, ao cruzar 1→2) — segurar o marcador EM 2
não recruza esse limiar. O que se repete ao segurá-la ali é o **capítulo
III (compra)**, não o II. Pra repetir o sacrifício seria preciso derrubar
o marcador abaixo de 2 (pra 0 ou 1) e deixar cruzar 2 de novo.

### Partida manual #5 (2026-09-23) — Goldberry salvando a Kiora, 0 erros de regra confirmados

| Turno | Evento |
|---|---|
| T1-T2 | Land drop The World Tree (entra virado). Barbara Wright conjurada
(`{1}{W}`) — dá "read ahead" a todas as Sagas do jogador. Breeding Pool
aparece hand→battlefield e depois Hallowed Fountain também — **confirmado
pelo usuário**: jogou a Breeding Pool errado (sem W), desfez, e jogou a
Hallowed Fountain no lugar pra ter acesso a branco. 1 land drop real, não 2 |
| T3-T4 | Scholar of New Horizons, Goldberry River-Daughter, Flux Channeler
conjuradas. Savai Triome buscada por fetch (Windswept Heath) |
| T5 | Summon: Fenrir buscada pelo **Enlightened Tutor**
(`"...reveal it, then shuffle and put that card on top"` — confirmei o
texto exato) e posta no topo da library. Log mostra ela indo pra
battlefield→library duas vezes: **confirmado pelo usuário** — depois de
achar o Fenrir no topo, ele cracou a Windswept Heath (`...then shuffle`),
embaralhando a library de novo e perdendo a posição garantida no topo.
Sem erro de regra — risco real de tutor "topdeck" com fetchland no
próprio deck |
| T6 | Tom Bombadil conjurado |
| T7 | Kiora Bests the Sea God conjurada (Lore=1, capítulo I cria Kraken 8/8) |
| T8 | The Cruelty of Gix conjurada |
| T9 | Kiora e The Cruelty of Gix ambas avançam. Kiora cruza pro **capítulo
III** (Lore=3, "Gain control of target permanent an opponent controls") —
📊 estrutural (sem oponente real). Em resposta, **Goldberry, River-Daughter**
usa a 1ª habilidade (`{T}: Move a counter... from another target permanent
onto Goldberry`) puxando 1 marcador de saber da Kiora pra si — Kiora volta
pra Lore=2 e sobrevive (714.4), mesmo padrão de "salvar a Saga" das
partidas #1 e #4, mas com Goldberry em vez de Clockspinning/Hex Parasite.
Battle at the Helvault também cruza pro capítulo final (Lore=3) no mesmo
turno — só **1** Saga de graça entra via Tom (Summon: Yojimbo), confirmando
de novo o "once each turn" com 2 finais simultâneos |

**Conferido e correto**: read ahead da Barbara Wright, capítulo I do Fenrir,
capítulos da Kiora, e o salvamento da Kiora via Goldberry batendo com o
oráculo real dela (movimenta 1 marcador de cada tipo que ela não tem, de
outra permanente pra ela). "Once each turn" do Tom confirmado de novo com
Kiora + Helvault simultâneos. As 2 anomalias do T2 e T5 foram confirmadas
pelo usuário como desfazer de jogada e embaralho por fetchland — nenhuma
é bug, 0 erros de regra na partida inteira.

Também confirmado (Scholar of New Horizons, custo real conferido):
`{T}, Remove a counter from a permanent you control: Search your library
for a Plains card...` — o custo é remover 1 marcador de **qualquer
permanente sua**, incondicional (não depende de achar ou de colocar a
planície em campo). Explica a flutuação de marcadores da própria Scholar
vista no T5/T8.

### Partida manual #6 (2026-09-30) — 0 violações de regra provadas pelo log; 6 erros de operação e 1 blefe deliberado, todos confirmados pelo usuário

Dados brutos, script e verificação byte a byte em
`tom-bombadil-wubrg/resultados-ab/2026-09-30-partida-manual-6/` (Regra #8).
Oráculo de cada carta conferido ao vivo no Scryfall; `Femeref Enchantress` tem só o gatilho de
"encantamento vai pro cemitério" (não tem o de entrar), `Serra's Sanctum` rende W por encantamento
**seu** (Fertile Ground, Fable, ECD e Enduring Vitality contam; a Femeref é só criatura).

| Turno | Evento principal |
|---|---|
| T1 | Temple Garden (shock, entra virado). Mão de 8: Enduring Vitality, Femeref, Serra's Sanctum, Temple Garden, Bloom Tender, Wooded Foothills, Barbara Wright, Elspeth Conquers Death |
| T2 | Wooded Foothills → cracada, busca **Raugrin Triome** (tem o tipo Mountain; virado). Sem jogada no turno (só o Temple Garden destapado) |
| T3 | Serra's Sanctum · Fertile Ground (só fecha no Sanctum: aura dá +1 mana) · Arcane Signet |
| T4 | Flooded Strand → **Savai Triome** (tem Plains) · **Tom Bombadil** (WUBRG exato: Sanctum 2 = W do encantamento + 1 da aura, Signet, Temple Garden, Raugrin) |
| T5 | Raffine's Tower (virado) · Enduring Vitality + Bloom Tender (5 mana, com 6 fontes de sobra sem o Tom; o Tom aparece virado: ataque ou mana via Vitality) |
| T6 | Fable (Goblin Shaman) + Elspeth Conquers Death + Femeref = 10 mana de gasto; o usuário reconheceu erro de mana neste turno (ver "confirmado" abaixo). Snail do oponente (interação simulada) |
| T7 | Fable cap. II: descarta Barbara, compra Windswept Heath → cracada, busca **Zagoth Triome** (tem Forest). ECD cap. II. Goblin Shaman ataca → Treasure |
| T8 | ECD cap. III (devolve Barbara com +1/+1) **e** Fable cap. III (vira Reflection of Kiki-Jiki) no mesmo turno → o Tom dispara **1 vez** (The Coming of Galactus de graça). Culling Ritual (oponente simulado) destrói MV ≤ 2 |
| T9–T10 | Reflection copia Enduring Vitality (cópia-ficha); Galactus cap. II e III |
| T11 | Galactus cap. IV (ficha 16/16) → o Tom busca **In the Darkness Bind Them** (Wraith + o Anel tenta). Leyline Binding ({W}: 5 tipos básicos) + Weaver of Harmony |
| T12 | ITDBT cap. II (Wraith). Anguished Unmaking (oponente simulado) exila o token Galactus 16/16. O log mostra a ITDBT no exílio, voltando com Lore 1 e subindo até 3 no mesmo turno, com 2 Wraiths e 2 tempts a mais: erro de operação, o correto era só somar 1 marcador (ver "confirmado"). O'aka + Utopia Sprawl |
| T13 | só compra |

**Conferido e correto** (script + conta à mão; escopo no `LEIAME.md` da pasta):
- **Terrenos**: 1 jogado da mão por turno, nos 13 turnos. Os 3 fetches foram ao cemitério e buscaram terreno do tipo certo
  (Wooded Foothills→Mountain, Flooded Strand→Plains, Windswept Heath→Forest; as Triomes têm esses tipos).
- **Saber**: ECD T6→T8 (1→2→3, sacrificada), Fable T6→T8, Galactus T8→T11 (1→4, sacrificada), ITDBT T11. Só +1 por turno na fase
  principal 1 (CR 714.3c), sacrifício depois do capítulo final (714.4). A única exceção, a ITDBT no T12, foi erro de operação do usuário (ver abaixo).
- **Tom**: no máximo 1 Saga de graça por turno. No T8 houve 2 capítulos finais resolvendo (ECD III e Fable III) e entrou só 1
  Saga — o "once each turn" funcionando de verdade (mesma confirmação da partida #5).
- **Mana**: T3 (Raugrin + Temple Garden pagam a Fertile Ground; o Sanctum só rende depois dela, X = 1 + 1 da aura = 2, e paga o Signet: exato),
  T4 (Sanctum 2 + Signet + Temple Garden + Raugrin = 5 = WUBRG exato) e T5 (6 fontes para 5) fecham. **T6 não fecha com certeza**: gastos 10 (Fable 3 + ECD 5 + Femeref 2; a Femeref
  é criatura, não encantamento) contra 7 fontes de 1 (contando Tom e Enduring Vitality) + Sanctum (já havia Fertile Ground + Enduring Vitality, X = 2 → 3 mana; X = 3 após a Fable → 4) = 10 a 11.
  Se as viradas do Tom e da Vitality no T6 eram ataque simulado (o usuário confirmou esse hábito para a Vitality nos T7/T8), sobram só 5 fontes de 1 + Sanctum 4 = **9 para 10 gastos**.
  T7–T12: no máximo 3 mana gastos por turno com ≥ 4 fontes viradas (folga grande; não conferi cor por cor).
- **Compra/descarte**: Fable II no T7 (descarta 1, compra 1 ✓). Barbara voltando com o contador da ECD III ✓.
  Femeref: no T8 saem 2 compras extras (Forest, Hallowed Fountain) e o oráculo dá 2 gatilhos (ECD vai pro cemitério; Fertile Ground morre
  junto com a própria Femeref no Culling Ritual e ela "vê" — CR 603.10a). A contagem bate; a 2ª compra foi feita antes da hora (confirmado pelo usuário, ver abaixo).
- **The Ring** no T12: o 2º tempt (o do cap. II) dá "atacar → compra e descarta": o descarte da Hallowed Fountain bate. Os tempts 3–4 do log foram erro (ver abaixo).

**Confirmado pelo usuário (2026-09-30): erros de operação dele, não regra do deck nem bug do simulador**
- **ITDBT no T12**: o correto era só somar o marcador de saber (Lore 2 → cap. II: 1 Wraith + 1 tempt). O exílio, a volta com Lore 1, os 2 marcadores extras, os 2 Wraiths extras e os
  tempts 3–4 do Anel foram erro. **O alvo da Anguished Unmaking (oponente simulado, mesmo turno) foi o token Galactus 16/16** ("destrói um terreno por ataque"), não a Saga: o log mostra a ITDBT, e não o
  Galactus, indo para o exílio. Ficha que sai de jogo não aparece no log do playtester (mesmo motivo do Goblin Shaman e dos Treasures), então o Galactus exilado não está registrado.
- **Fichas do Culling Ritual (T8)**: Goblin Shaman e os Treasures deveriam ter sido removidos (MV 0). Ficaram em jogo por esquecimento.
- **Fertile Ground**: anexada no Serra's Sanctum (era a minha dedução; o T3 só fecha assim).
- **Enduring Vitality virada nos T7/T8**: era ataque simulado, erro dele. A Vitality tem vigilance (oráculo), então atacar não a vira.
- **Femeref, 2ª compra extra do T8**: feita antes da hora (a contagem de 2 compras estava certa; a ordem não).
- **Mana do T6**: o usuário reconhece erro, sem dizer qual. Pela minha conta, é compatível com Tom e Vitality terem sido virados como ataque: aí faltaria 1 mana para os 10 gastos.
  Se a Femeref (2) não tivesse sido conjurada no T6, as 2 compras do T8 também não teriam acontecido. Não medi.

- **Fable com duas entradas idênticas no T6**: misclick.
- **Bloom Tender sem virar nos T6–T7: deliberado**, para o oponente achar que havia interação pronta (blefe, não erro). Correção minha: o log mostra o Bloom Tender virado uma vez, no T8, logo antes de
  morrer no Culling Ritual (antes eu escrevi "nunca virado"). Pela minha conta, o Bloom Tender (vivid) com o Tom em campo (WUBRG) rende 5 mana a partir do T6; o blefe deixou esses 5 mana de fora (o T6 não era
  impossível; a falta apontada em "Mana do T6" vem da contagem sem o Bloom Tender).

Resíduo da #6: nenhum item sem resposta.

**Leitura do deck** (oráculo + regras; o simulador só apoia):
- O T2 real ficou sem jogada com 4 magias de 2 mana na mão (Femeref, Bloom Tender, Barbara, depois Fertile Ground): fetch no T1 (1 vida; busca um shock que entra
  virado de graça) e um shock destapado no T2 (2 vidas) dariam 2 fontes destapadas no T2. Não medi no simulador.
- T8, escolha de read ahead: com Barbara em campo, uma Saga pode entrar no capítulo final, mas o Tom só dispara 1 vez por turno — com o T8 já
  ocupado por ECD III + Fable III, entrar com a Galactus no cap. IV teria gastado o gatilho do turno; entrar no cap. I escalonou o final pro T11
  (2º gatilho do Tom). Trade-off de calendário, não erro.
- Reflection of Kiki-Jiki + Enduring Vitality: a cópia-ficha tem haste, toca pra mana ("criaturas têm {T}: mana") e conta como encantamento pro Sanctum;
  com Femeref viva, a cópia sacrificada no fim do turno compraria 1 (encantamento indo pro cemitério). Sem Femeref no T9–T10, o ganho foi só mana.
- **Sim × real**: Tom no T4 acontece em 27,3% das 3.000 partidas do simulador (≤ T5: 56,8%). Primeiro gatilho do Tom no T8, igual à #7.

### Partida manual #7 (2026-09-30) — 1 violação de regra provada pelo log (2º terreno no T8) e 6 outros erros/suposições do usuário, todos confirmados; 0 pontos residuais

Dados brutos, script, rulings, varredura da lista e a sensibilidade do Exotic Orchard em
`tom-bombadil-wubrg/resultados-ab/2026-09-30-partida-manual-7/` (Regra #8; `cmp` byte a byte feito).
Oráculos ao vivo; rulings lidas antes de concluir (15 cartas, `resumos/rulings_scryfall.json`). Duas cartas faltavam no cache e entraram:
Golgari Charm e Torment of Hailfire.

| Turno | Evento principal |
|---|---|
| T1 | Mão de 8: Awaken the Honored Dead, Savai Triome, Barbara Wright, Exotic Orchard, Zagoth Triome, Forest, Sanctum Weaver, Ketria Triome (5 terrenos). Savai Triome (virado) |
| T2 | compra Flux Channeler · Forest · **Sanctum Weaver** ({1}{G}; Savai + Forest) |
| T3 | compra Setessan Champion · Exotic Orchard · **Setessan Champion** ({2}{G}; Forest + Savai + Orchard) |
| T4 | compra Summon: Knights of Round · Ketria Triome (virado) · **Barbara Wright** ({1}{W}; Savai→W + Orchard). Torment of Hailfire (oponente simulado) → descarta Awaken the Honored Dead e Zagoth Triome |
| T5 | compra Faeburrow Elder · sem terreno na mão · **Tom Bombadil** ({W}{U}{B}{R}{G} com 5 fontes: Savai, Ketria, Forest, Orchard, Weaver X=1) |
| T6 | compra The Bath Song · **Bath Song** ({3}{U}, 4 terrenos) com read ahead da Barbara escolhendo o capítulo I (Lore 1): compra Teferi's Protection + Fable, descarta Faeburrow Elder · Champion +1 (1) e ataca. Golgari Charm (oponente simulado) e Barbara vai pro cemitério |
| T7 | compra Arcane Signet · Bath Song lore 2 → cap. II: compra Farseek + Jugan Defends the Temple, descarta Farseek · Signet (2) + **Fable** ({2}{R}) = 5 mana de 5 (4 terrenos + o próprio Signet) · Fable entra com Lore 1 (Barbara morta → sem read ahead) → Goblin Shaman · Champion +1 (2) |
| T8 | compra City of Brass · City of Brass (terreno) · Fable lore 2 → cap. II: descarta Flux Channeler + Jugan, compra Sythis + Urza's Saga · Bath Song lore 3 → cap. III: 5 cartas do cemitério voltam pra biblioteca, +{U}{U}; Saga sacrificada → **1º gatilho do Tom: In the Darkness Bind Them** (Lore 1 → Wraith 3/3 menace + o Anel tenta) · Sythis ({G}{W}) · **Urza's Saga jogada como 2º terreno do turno** · **Summon: Knights of Round** (8 mana) → cap. I: 3 Knights 2/2 · Champion 4 marcadores |

**Conferido e correto** (script + conta à mão):
- **Mana, T2–T8**: T2 (2 fontes = Weaver 2), T3 (3 fontes = Champion 3), T4 (2 = Barbara 2), T6 (4 terrenos = Bath Song 4, U da Ketria),
  T7 (4 terrenos + Signet = Signet 2 + Fable 3, exato), T8 (≥ 11 disponíveis para 10 gastos: 6–7 fontes fixas + {U}{U} da Bath Song + Weaver X ≥ 3
  [Weaver, Fable, ITDBT]; o W do Knights vem do Savai, Signet, City ou Weaver). T5: ver o Orchard abaixo.
- **Saber**: Bath Song 1→2→3 (T6–T8) e sacrificada depois do cap. III; Fable 1→2; Urza's Saga e Summon: Knights entram com 1. Só +1 por turno. O Tom só
  disparou no T8 (nenhum capítulo final antes) e 1 vez.
- **Read ahead da Barbara**: T6 escolheu o capítulo I (permitido 1–3, não usa a pilha); T7 sem read ahead porque a Barbara já tinha morrido.
- **Compra/descarte dos capítulos**: Bath Song I e II ("compre 2, descarte 1": T6 e T7 ✓ 1 descarte cada), Fable II no T8 (descarta 2, compra 2 ✓),
  Bath Song III (5 cartas do cemitério pra biblioteca; o ruling permite cap. III sem alvo só pra somar {U}{U}).
- ITDBT cap. I: 1 Wraith + 1 tempt (emblema com 1 marcador "Charge"); Summon: Knights cap. I: 3 Knights; Tom com 5 marcadores de saber no fim do T8
  (ITDBT 1, Fable 2, Urza's Saga 1, Summon 1) → hexproof + indestructible ✓.

**Violação provada pelo log**
- **T8, 2 jogadas de terreno**: City of Brass e **Urza's Saga** (a ruling de 2021-06-18 diz "é um terreno, só pode ser jogada como terreno"). CR 305.2 dá 1 por
  turno e nenhuma das 100 cartas da `lista.md` dá jogada extra (varredura por script: 0). O erro não muda o que foi conjurado (sem a Saga ainda sobram ≥ 10 mana para os 10 gastos).
  **Confirmado pelo usuário: esqueceu que já tinha jogado a City of Brass.**

**Confirmado pelo usuário (2026-09-30): erros de operação ou suposições dele, não regra do deck nem bug do simulador**
- **As 6 cópias-ficha de The Bath Song no T8**: erro dele. Sem efeito no jogo (nenhuma carta da lista copia Saga; se fossem reais teriam disparado o cap. I ×6 e a constelação ×6).
- **A Barbara Wright morrer com a Golgari Charm no T6**: erro dele. O oráculo dá −1/−1 e a Barbara é 1/3, então ela sobrevive (0/2 até o fim do turno). Consequência real: com ela viva,
  a Fable do T7 poderia ter entrado com read ahead (escolhendo o capítulo). Não medi essa linha.
- **Setessan Champion e Sythis (corrigido em 2026-10-01)**: o usuário disse que o Champion só ganha marcador e que quem compra e dá 1 de vida é a Sythis. **A Sythis está certa; o Champion, não.**
  Oráculo ao vivo (Scryfall, igual ao cache): *Setessan Champion — "Constellation — Whenever an enchantment you control enters, put a +1/+1 counter on this creature **and draw a card**."*
  *Sythis — "Whenever you cast an enchantment spell, you gain 1 life and draw a card."* O Champion dispara com QUALQUER encantamento entrando (ruling 2020-01-24: inclui criatura-encantamento, e o que o Tom
  põe em campo); a Sythis só com encantamento **conjurado**. O jogador esqueceu os marcadores (T8: +2 no log, +4 pelo oráculo) **e não comprou com o Champion** (leitura errada da carta).
  Conta por turno (compras library→mão: o log está em `resumos/trace.md`; o esperado vem do oráculo):
  | turno | esperado | log | o que faltou |
  |---|---|---|---|
  | T6 | 4 (passo + Bath Song I ×2 + Champion pela Bath Song) | 3 | 1 do Champion |
  | T7 | 4 (passo + Bath Song II ×2 + Champion pela Fable) | 3 | 1 do Champion |
  | T8 | 8 (passo + Fable II ×2 + Champion ×4 [ITDBT, Sythis, Urza's Saga, Summon] + Sythis na Summon) | 3 | 4 do Champion e 1 da Sythis (+1 de vida) |
  Total: 7 cartas e 1 de vida não obtidas, só em prejuízo do jogador. Com 4 terrenos até o T8 e nenhum terreno na mão do T5 ao T7, as 2 compras extras dos T6/T7 viriam antes do T8; não medi o efeito.
  O simulador já compra com o Champion (`on_enchantment_enters`: contador + compra) e com a Sythis só na conjuração; nada a mudar no código.
- **Farseek no T7**: devia ter sido descartado pelo cap. II da Bath Song, e não entrado em campo (arrasto errado; nenhum terreno foi buscado).
- **Exotic Orchard no T5**: o usuário **presumiu** que o Orchard gerava a cor que faltava entre as 4 das outras fontes. Não é regra: o log não tem terreno de oponente, e o oráculo/ruling
  (2009-02-01) só dá cor de terreno de oponente (nunca incolor). Sem a suposição, o Tom no T5 não fecha (4 fontes reais para 5 cores); nos T3, T4, T6 e T7 o Weaver (que não foi virado) cobriria a falta.
  A conjuração do Tom no T5 fica como "legal só sob a suposição de que os oponentes têm terreno com a cor que faltava".

- **Bath Song indo ao cemitério duas vezes no T8**: foi só uma vez; o outro registro foi erro dele.

Resíduo da #7: nenhum item sem resposta.

**Leitura do deck** (oráculo + regras; o simulador só apoia):
- T5–T7 sem terreno na mão (Zagoth Triome descartado no T4 pro Torment): 4 terrenos até o T8 (e com 7 cartas a menos vistas por causa das compras esquecidas, ver acima). O Flux Channeler ficou na mão do T2 ao T8 (nunca conjurado, descartado
  na Fable II): em nenhum turno sobraram 3 mana livres (T4 sobrou 2, T6 sobrou 1). No T4 havia a alternativa de descartar a Summon (8 MV) em vez da Zagoth; não medi.
- **Linha que não foi jogada no T6**: Tom em campo (T5) e Barbara viva na hora de conjurar a Bath Song → entrar com Lore 3 (cap. III, sem alvo) resolveria o final no T6:
  gatilho do Tom (1 Saga de graça, 2 turnos antes) + {U}{U} + 1 fonte sobrando = 3 mana, o Flux Channeler ({2}{U}) no mesmo turno. Custo: perde os caps. I e II (2 × "compre 2, descarte 1" = +2 cartas líquidas).
  O simulador valoriza o cap. III da Bath Song em 2 contra 4 e 4 dos caps. I e II (`CHAPTER_VALUE`) e não a põe em `READ_AHEAD_FINAL_OK`: decisão de projeto do simulador, não bug; **a linha não foi medida**.
- Tom no T4 (#6) e no T5 (#7), 1º gatilho no T8 nas duas: dentro do que o simulador dá como comum (Tom ≤ T5 em 56,8% das partidas). Duas partidas não provam a distribuição.

**Sensibilidade medida: convenção do Exotic Orchard no simulador** (achado desta partida; simulador NÃO alterado)
O simulador dá ao Orchard 1 mana incolor (`add_land("Exotic Orchard", (), set(), produces=set())`). As duas pontas estão erradas pela ruling: o Orchard nunca faz incolor, e faz cor só se um terreno de oponente a produzir. A variante "qualquer cor" é portanto um **teto** (assume oponentes com as cores que faltam; é a mesma suposição que o usuário fez no T5).
Pareado, N = 3.000, mesmas sementes, 10 turnos (controle: a variante `base` reproduz `tom_v1_runs.jsonl` em 3000/3000 partidas):

| métrica | Orchard incolor (atual) | Orchard qualquer cor | Δ pareado |
|---|---|---|---|
| Tom lançado até o T4 | 27,3% | 29,4% | **+2,0 pp ±0,5** |
| Tom lançado até o T5 | 56,8% | 60,1% | **+3,3 pp ±0,7** |
| Tom lançado até o T6 | 76,2% | 79,1% | **+2,9 pp ±0,7** |
| ≥ 1 gatilho do Tom até o T10 | 90,2% | 91,5% | **+1,3 pp ±0,5** |
| só nas 684 partidas (22,8%) com Orchard em campo: Tom até o T5 | 53,7% | 68,0% | **+14,3 pp ±3,0** |

Tradução (teto): na média o simulador subestima o Tom em até cerca de 3 partidas a mais em 100 por T5; em quem tem o Orchard, até 14 a mais em 100. O valor real fica entre a convenção atual e o teto, conforme os terrenos dos oponentes. O turno de lançamento do Tom mudou em 232 de 3.000 partidas (7,7%).
Não mudei o padrão: todas as tabelas arquivadas (A/B, regressões) usam a convenção antiga e mudá-la quebraria a comparação. A variante fica pronta em `orchard_sens.py`; a terceira convenção
(Orchard sem mana quando não há terreno de oponente, a leitura estrita do goldfish) não foi medida.

### Partida manual #8 (2026-10-01) — 1 violação de regra confirmada (Satsuki) e 2 omissões

Dados brutos, script, rulings e trace em `tom-bombadil-wubrg/resultados-ab/2026-10-01-partida-manual-8/` (Regra #8). Oráculos ao vivo; rulings lidas antes de concluir
(Estrid's Invocation, Satsuki, O'aka, Resourceful Defense, Jugan, Summon: Fenrir, Birth of the Imperium, Ugin, ECD, Tom; `resumos/rulings_scryfall.json`).
Mão inicial (foto, "Keep this", Interaction simulator ligado): Narci, O'aka, Forest, Jugan Defends the Temple, Sol Ring, Flooded Strand, Estrid's Invocation (2 terrenos + Sol Ring);
a 8ª carta do T1 (Resourceful Defense) é a compra do turno. O playtester compra sozinho ao mudar de turno (informado pelo usuário); marcador de saber é manual.

| Turno | Evento principal |
|---|---|
| T1 | Forest · Sol Ring (pago com a Forest) |
| T2 | compra Bloom Tender · Flooded Strand → cracada, busca **Raffine's Tower** (Plains Island Swamp, virada) · **Jugan** ({2}{G} = Forest + Sol Ring, exato) → cap. I: Human Monk |
| T3 | sem terreno na mão · Jugan lore 2 → cap. II: +1/+1 no Monk · **O'aka** + **Bloom Tender** (4 de 5 mana: Raffine's, Forest, Sol Ring 2, Monk) |
| T4 | O'aka remove 1 marcador de saber da Jugan antes do passo natural (2→1), compra a ECD; o passo natural a leva a 2 → cap. II de novo: +1/+1 em Bloom Tender e O'aka · **Resourceful Defense** ({2}{W}) + **Satsuki** ({G}{W}) |
| T5 | mesmo ciclo (Jugan 2→1→2, cap. II: Satsuki e Bloom Tender), O'aka compra o Serra's Sanctum · Sanctum jogado · **ECD** ({3}{W}{W} = Sanctum WW [Jugan + Resourceful Defense] + Sol Ring 2 + Forest, exato) |
| T6 | Jugan cap. II (Satsuki e Monk) · ECD lore 2 · Raugrin Triome (virada) · **Summon: Fenrir** (cap. I busca Swamp) · **Estrid's Invocation** como cópia da Fenrir (cap. I busca **Mountain**; Raugrin e Mountain são o 1º vermelho do jogo e entram virados) · simulador de interação: 3 fichas Human Citizen 1/1 atacam (confirmado pelo usuário) |
| T7 | Jugan cap. II (O'aka e Bloom Tender) · ECD lore 3 (cap. III sem alvo) e sacrificada → Resourceful Defense move os 3 marcadores de saber para a Sol Ring · Fenrir lore 2 e a cópia da Estrid lore 2 (2× cap. II "próximo spell de criatura entra com +1/+1") · **Tom Bombadil** (5 terrenos = WUBRG exato) entra com 2 marcadores · Satsuki acelera só a Fenrir (3) → cap. III, sacrificada → **1º gatilho do Tom: Birth of the Imperium** → 3 Astartes Warrior; Fenrir morre e os 3 marcadores vão para o Bloom Tender · Urza's Saga (terreno) · Ugin, Eye of the Storms (oponente simulado) exila a Birth |
| T8 | Jugan 2→1→2, cap. II (Tom e O'aka) · Estrid sai e volta no upkeep como cópia da Jugan → cap. I: outro Human Monk · nenhuma magia (parou o goldfish de propósito) |

**Conferido e correto** (script + conta à mão; escopo no `LEIAME.md` da pasta):
- **Terrenos**: 1 jogado da mão por turno (T3, T4 e T8 sem terreno na mão). Flooded Strand → Raffine's Tower (tem Plains/Island); Fenrir e Estrid buscam básicos, virados.
- **Mana**: T1–T7 fecham (T2, T5 e T7 exatos). T7: Raugrin (W/U) + Raffine's (W/U/B) + Swamp + Mountain + Forest = WUBRG. Sobraram Sol Ring e Sanctum.
- **Loop O'aka + Jugan** legal: remover marcador de saber de uma Saga e recolocar faz o mesmo capítulo disparar de novo (ruling "removing lore counters... will trigger again", Summon: Fenrir/ECD). Rendeu +1/+1 em 2 criaturas por turno (T3: 1; T4–T8: 2) e 1 compra do O'aka por turno a partir do T4. Os marcadores finais batem (Bloom Tender 3, Tom 3, O'aka 3, Satsuki 2, Monk 2).
- **Estrid**: copia o que está em campo ao entrar (ruling 2018-07-13), entra como Saga com 1 marcador (cap. I buscou o Mountain) e, ao voltar no upkeep, é objeto novo e copia o que estiver em campo (a Jugan); contadores somem.
- **Tom**: 1 gatilho (Fenrir III) e 1 só por turno. A ECD III resolveu ANTES de o Tom entrar (o Tom é de velocidade de feitiço: o marcador natural da ECD no início da fase principal dispara o capítulo III antes de qualquer conjuração), então não gerou gatilho. Quando a Ugin foi conjurada (antes de a Birth sair): Jugan 2 + Birth 1 + Urza's Saga 1 = 4 marcadores de saber em Sagas → Tom com hexproof/indestructible.
- Marcador de saber em não-Saga (Sol Ring, Bloom Tender, via Resourceful Defense) é legal ("put those counters on target permanent") e não conta para o Tom.
- Compras (library→mão, `resumos/trace.md`): T4–T6 e T8 = 2 (compra do turno + O'aka). T7 = 2 (esperado 3, ver abaixo).

**Confirmado pelo usuário (2026-10-01)**
- **T4, Jugan**: usou o O'aka antes do passo natural de 2 para 3, voltando a Jugan para 1; o passo natural a leva a 2 e o cap. II dispara de novo. O log mostra "Lore 3" antes do registro do O'aka, com um ajuste de +4/+4 na Jugan (o Remnant é 2/2); o usuário não comentou o +4/+4 e a ordem do log. Aceito o relato dele (ruído de interface).
- **Human Citizen (T6)**: 3 fichas 1/1 que o simulador de interação mandou atacar.
- **Estrid no T8**: aconteceu no upkeep (o simulador compra sozinho na troca de turno).
- **Encerramento**: parou no T8 para fechar o goldfish mais cedo (com Narci, Fable, Creation of Avacyn, Binding the Old Gods, Farseek e Summon: Bahamut na mão e mana de sobra).
- **T7, Fenrir III**: assumiu que não controlava a criatura de maior poder, por isso sem compra (ver omissão 3).
- **Resourceful Defense e a Birth (T7)**: esqueceu de mover o 1 marcador de saber da Birth exilada (gatilho obrigatório).

**Violação de regra (confirmada pelo usuário)**
- **T7, Satsuki**: "Put a lore counter on each Saga you control". O usuário disse que só acelerou a Fenrir ("para ativar o gatilho do Tom e trazer mais uma saga"). Pelo oráculo, a Jugan (2→3) e a cópia da Estrid (2→3) também receberiam o marcador:
  - Jugan cap. III: exila e volta transformada (Remnant of the Rising Star 2/2 voador). Acaba o loop O'aka + Jugan, porque deixa de ser Saga.
  - Cópia da Estrid cap. III: compra 1 carta (condição provavelmente verdadeira: Tom 6/6 contra as fichas 1/1, se ainda estavam em campo) e é sacrificada → Resourceful Defense move os marcadores dela.
  - O Tom continuaria com 1 gatilho (só dispara 1 vez por turno).
  - **Linha legal que mantinha o loop E o gatilho do Tom** (achada depois, corrige a lista de escolhas que dei antes): com o Tom já em campo, pagar a habilidade da **Resourceful Defense**
    ({4}{W}: "Move any number of counters from target permanent you control onto a second target permanent you control") para tirar 1 marcador de saber da Jugan (2→1) e só então ativar a Satsuki: a Jugan
    volta a 2 e o cap. II dispara DE NOVO (+1/+1 em mais 2 criaturas), a Fenrir vai a 3 (Tom) e a cópia da Estrid a 3. Era pagável sem mexer nos 5 terrenos do Tom: no fim do T7 o Serra's Sanctum
    (1 W por encantamento seu: Jugan, Resourceful Defense, Fenrir e Estrid = 4), a Sol Ring (2), o Bloom Tender (5 cores com o Tom em campo) e o Human Monk terminam desvirados no log.
  - Ou seja: ativar a Satsuki era boa ideia; o erro foi não pagar o ajuste da Jugan. Alternativas sem a Resourceful Defense: não ativar (o gatilho do Tom ficaria para o T8, quando a Fenrir chega a 3 sozinha) ou ativar
    e aceitar a Jugan transformada. Nenhuma das linhas foi medida.

**Omissões / sem registro**
1. **T7, marcador da Birth**: a Birth foi exilada com 1 marcador e nenhum foi movido (confirmado: esquecimento).
2. **T8, cópia da Estrid como Jugan**: entrou com 1 marcador no upkeep. No início da fase principal ela deveria ganhar o marcador natural (2) e disparar o cap. II (+1/+1 em até 2 criaturas). O log mostra só os 2 contadores da Jugan de verdade. O usuário confirmou o timing no upkeep, mas não comentou o marcador: provável omissão (perdeu 2 contadores +1/+1).
3. **T7, compras (resolvido)**: o log tem 2 (compra do turno + O'aka). A Fenrir III não comprou porque o usuário **assumiu que não tinha a criatura de maior poder** (resposta de 2026-10-01). O estado
   registrado/simulado só tinha as 3 fichas 1/1 do T6 contra o Tom 6/6, então pelo log a condição seria verdadeira; a premissa de uma criatura de oponente maior não está no log. Fica como suposição declarada, não erro de regra.

**Regra de futuro (não ocorreu)**: se a cópia da Estrid como Jugan chegar ao cap. III, ela será exilada e NÃO volta (não é carta de dupla face; ruling análogo da Azusa em `Jugan Defends the Temple`). O gatilho do Tom ainda dispara.

**Leitura do deck** (oráculo + regras; o simulador só apoia):
- **O Tom só entrou no T7 por falta de vermelho, não de mana**: o primeiro vermelho veio no T6 (Raugrin e Mountain, os dois virados). No T5 havia mana de sobra (Sanctum 2–3 + Sol Ring 2 + Forest + Raffine's + Bloom Tender 3 + Monk) mas nenhuma fonte de R, e o Bloom Tender só dá cor de permanente em campo. O Farseek (busca Mountain) ficou na biblioteca até o T8.
- **Sim × real**: o simulador lança o Tom até o T7 em 86,2% das partidas (até o T5: 56,8%). T7 é típico, nem rápido nem lento. Um gatilho no T7.
- O loop O'aka + Jugan é linha real do deck. O simulador faz o equivalente (O'aka tira marcador no fim do turno de Saga cujo capítulo vale repetir, `try_value_removers`, e o passo natural a devolve). A Satsuki do simulador (`try_satsuki`) já põe marcador em TODA Saga com saber abaixo do final, como o oráculo manda. Nada a mudar no código.

### Partida manual #9 (2026-10-02) — 2 erros de regra confirmados (2º terreno no T6 e Binding II) e 1 omissão (Anel ×2); sem resíduo

Dados brutos, script, rulings e trace em `tom-bombadil-wubrg/resultados-ab/2026-10-02-partida-manual-9/` (Regra #8). Oráculos ao vivo; rulings lidas antes de concluir (Binding the Old Gods, Power Conduit,
Replenish, Battle at the Helvault, Amazing Acrobatics, The Eldest Reborn, Rankle, Fenrir, In the Darkness Bind Them, Urza's Saga; `resumos/rulings_scryfall.json`). Mão inicial (foto, "Keep this"):
Power Conduit, Overgrown Tomb, Birth of the Imperium, Battle at the Helvault, Binding the Old Gods, Command Tower, Serra's Sanctum; a 8ª carta do T1 (City of Brass) é a compra do turno.
O simulador de interação estava **Off** na foto e foi ligado depois (confirmado); o usuário o configurou para "até três interações por rodada".

| Turno | Evento principal |
|---|---|
| T1 | Overgrown Tomb (virado, sem pagar 2 vidas) |
| T2 | Command Tower · **Power Conduit** ({2}: Tower + Tomb) |
| T3 | Ziatora's Proving Ground (virado), sem magia (2 fontes, nada de 2 na mão) |
| T4 | City of Brass · **Binding the Old Gods** ({2}{B}{G}, 4 terrenos, exato) |
| T5 | Binding lore 2 → cap. II busca **Zagoth Triome** (tem Forest, virado) · Serra's Sanctum · **Tom Bombadil** (WUBRG exato: Sanctum W [só o Binding é encantamento], Tower U, Tomb B, City R, Proving Ground G) · interação: o "Shapeshifter" (ficha genérica 3/2) ataca e o Tom o bloqueia; o Rankle conecta e escolhe só o modo "cada jogador descarta" (a Birth of the Imperium vai da mão ao cemitério) |
| T6 | Binding lore 3 → Power Conduit tira 1 marcador (3→2) em resposta ao cap. III e põe +1/+1 no Tom; o cap. III resolve → **1º gatilho do Tom: Summon: Fenrir** (cap. I busca **Plains**, virado) · Jetmir's Garden (virado) · **The Eldest Reborn** ({4}{B}) · interação: Amazing Acrobatics |
| T7 | Fenrir lore 2 · Eldest lore 2 · Binding lore 3 → Conduit (3→2, +1/+1 no Tom, que fica com 2) → **2º gatilho do Tom: In the Darkness Bind Them** (Wraith) · **Indatha Triome** buscada pelo cap. II do Binding (ver erro) · Urza's Saga (terreno) · **Battle at the Helvault** ({4}{W}{W} = Sanctum 5 W + Plains) **contrada pela Amazing Acrobatics** (vai ao cemitério) · interação: Archfiend of Ifnir |
| T8 | compra a Replenish · Binding lore 3 e Fenrir lore 3 e Eldest lore 3: os três vão ao cemitério de propósito (capítulos III) · **3º gatilho do Tom: Fable of the Mirror-Breaker** (Goblin Shaman) · Fenrir III compra o Mountain (Tom 6/6 contra o Archfiend 5/4: tem o maior poder) · Urza's Saga cap. II + {2},{T}: Construct · Mountain · **Replenish** ({3}{W}) devolve Eldest Reborn, Binding, Fenrir, Battle e Birth (todos com 1 marcador). Parou aí (confirmado: não resolveu nenhum capítulo I) |

**Conferido e correto** (script + conta à mão; escopo no `LEIAME.md` da pasta):
- **Mana**: T2–T8 fecham. T4, T5 e T7 exatos (T7: Sanctum com Binding, Fenrir, Eldest, ITDBT e Urza's Saga = 5 W + Plains = os 6 da Battle). T8: Replenish com 4 terrenos; Construct com 2 do Sanctum.
- **Gatilho do Tom**: 1 por turno nos T6, T7 e T8 (no T8 resolveram 3 capítulos finais e entrou só 1 Saga). Os três vêm do capítulo III do Binding, que o Power Conduit salvou no T6 e no T7
  (tirar o marcador com o capítulo na pilha: lore 2 < final, a Saga não é sacrificada; ruling 2021-02-05).
- **Compras** (library→mão, `resumos/trace.md`): T2–T7 = 1 (compra do turno); T8 = 2 (compra do turno + Fenrir III). T1 = 8 (a mão da foto + a compra do turno).
- **Fetch por efeito**: Zagoth (Binding II, T5) e Plains (Fenrir I, T6) corretos (Forest / básico). **Terrenos da mão**: 1 por turno, exceto T6 (ver residual).
- **Battle at the Helvault no T7**: entra e vai ao cemitério porque foi **contrada** (o playtester põe o spell no campo e, se é contrado, move ao cemitério; a Amazing Acrobatics é "counter target spell"). Foi só depois devolvida pela Replenish.
- **Construct com 2 marcadores +1/+1 (T8)**: o usuário os pôs para representar o 2/2 (0/0 com +1/+1 por artefato: Power Conduit + ele mesmo). O P/T bate; o efeito real é estático, então não acompanha mudança no número de artefatos, e os marcadores poderiam ser removidos pelo Conduit.

**Erro de regra (confirmado pelo usuário)**
- **T7, Indatha Triome**: o usuário achou que tirar o marcador do Binding (3→2) fazia o capítulo II disparar de novo. Não faz: "Removing lore counters won't cause a previous chapter ability to trigger" (ruling 2021-02-05); o capítulo II só dispara de novo
  quando um marcador é *posto* e o saber passa de 1 para 2. A busca (Forest, virado) não era devida. Efeito: 1 terreno a mais em campo (virado no T7, sem uso no T8: a Replenish foi paga com outros 4). A forma legal de repetir o capítulo II
  é remover ANTES do passo natural (2→1) e deixar o passo natural levá-lo a 2, mas então o Binding não chega ao III e o Tom não dispara (o usuário escolheu o III).

**Omissão (confirmada)**: **The Ring Tempts You** (In the Darkness Bind Them I no T7 e II no T8) esquecido: nenhum emblema nem portador do Anel (o emblema apareceu no log da #6).

**Erro de regra (confirmado pelo usuário, 2026-10-02)**
- **T6, dois terrenos**: o usuário jogou a Urza's Saga e o Jetmir's Garden; "era para ter jogado o Garden". A Urza's Saga voltou à mão (aparece "mão→campo" de novo no T7; devolução à mão não fica no log, mesmo padrão da #5) e foi jogada no T7 como único terreno do turno.
  Efeito: com a Saga em campo o Sanctum rendeu 3 W (Binding, Fenrir, Urza's Saga) e pagou a Eldest Reborn ({4}{B}) com Zagoth + Proving Ground; sem a 2ª terra o Sanctum renderia 2 W, mas City, Tower e Tomb terminaram desvirados,
  então o spell era pagável legalmente do mesmo jeito. Sem efeito no que foi conjurado.

**Interações (confirmado pelo usuário)**
- **Shapeshifter**: era uma **ficha genérica 3/2** (não a carta real, em que poder + resistência = 7). Atacou e o **Tom 4/4 bloqueou**: pela conta de combate o Tom leva 3 e sobrevive, e a ficha (resistência 2) morre (ficha que sai de jogo não aparece no log).
- **Rankle**: só o modo "each player discards a card" (a Birth do T5). Os modos de comprar/perder vida e de sacrificar não foram escolhidos; o de sacrifício teria matado o Tom.
- **Archfiend of Ifnir**: "Whenever you cycle or discard another card, put a -1/-1 counter on each creature your opponents control." Não faz nada ao entrar (o usuário confirmou); nenhum ciclo/descarte do oponente depois dele, então sem efeito.
- **Amazing Acrobatics**: controu a Battle at the Helvault (T7).
- O Tom ficar virado nos T6/T7 não foi explicado (provavelmente ataque); sem efeito nas conclusões.

Resíduo da #9: nenhum.

**Leitura do deck** (oráculo + regras; o simulador só apoia):
- **Linha Binding III + Power Conduit** rende 1 gatilho do Tom por turno (T6, T7 e T8) com 1 só Saga: o Conduit a salva toda vez, e o gatilho traz uma Saga nova. No T8 o usuário parou de salvá-la e sacrificou 3 Sagas para a Replenish devolver 5.
- **Replenish**: devolve 5 Sagas com 1 marcador; os capítulos I valem: Fenrir (básico), Birth (3 Astartes Warrior, um por oponente) e Binding/Eldest/Battle (dependem de alvo de oponente, 📊). O log termina antes de resolvê-los.
- **Sim × real**: 3 gatilhos do Tom até o T8 acontece em 21,1% das partidas simuladas (8 turnos); Tom até o T5 em 56,8%; os dois juntos em 18,8% (cerca de 1 em 5): nesses dois critérios a partida está entre as ~20% melhores do simulador. O simulador joga Replenish (`replenish_effect`) e guarda encantamentos no cemitério quando há Replenish na mão (`bath_song_iii`). Nada a mudar no código.

### Partida manual #10 (2026-10-02) — 13 turnos; 0 erros de regra a favor do jogador, 13 compras esquecidas e 6 erros de registro

Dados brutos, script, ledger de compras, rulings e trace em `tom-bombadil-wubrg/resultados-ab/2026-10-02-partida-manual-10/` (Regra #8). Oráculos ao vivo; rulings lidas antes de concluir (Kami War, Hex Parasite, Starfield of Nyx,
Eidolon of Blossoms, Enchantress's Presence, Femeref, Deafening Silence, Casualties of War, Torment of Hailfire, Syphon Mind, Estrid, Sythis, The First Iroan Games, Setessan Champion; `resumos/rulings_scryfall.json`).
Mão inicial (foto, **1 mulligan grátis**, simulador de interação On): Enchantress's Presence, Summon: Primal Odin, Leyline Binding, Utopia Sprawl, Femeref Enchantress, Hallowed Fountain, Misty Rainforest; a 8ª carta do T1 (Starfield of Nyx) é a compra do turno.

| Turno | Evento principal |
|---|---|
| T1 | Misty Rainforest → busca **Ziatora's Proving Ground** (tem Forest, virado) |
| T2 | **Ketria Triome** (virado; a Hallowed Fountain do log foi desfeita) |
| T3 | **Utopia Sprawl** num terreno Forest (Proving Ground paga o {G}) |
| T4 | Hallowed Fountain (o log a repete em T3 e T4) · **Enchantress's Presence** ({2}{G}) |
| T5 | **Fertile Ground** (a Presence compra a Bath Song) · **Femeref Enchantress** |
| T6 | **Tom Bombadil** (5 mana) e logo morre por interação do oponente (volta ao comando, taxa 1) · Torment of Hailfire: descarta de propósito Primal Odin, Leyline Binding e The Bath Song (enchantments → cemitério para a Starfield) |
| T7 | **Eidolon of Blossoms** |
| T8 | **Tom** de novo (taxa 1 = 7 mana: 5 terrenos + Utopia Sprawl + Fertile Ground) · Witness Protection (oponente) |
| T9 | **Starfield of Nyx** · Sol Ring · Deafening Silence (oponente) |
| T10 | Starfield devolve a Bath Song (cap. I: compre 2, descarte 1) · Resourceful Defense, **Sythis**, Hex Parasite, Sanctum Weaver · Syphon Mind ×2: descarta Summon: Knights e In the Darkness Bind Them (voltam depois) |
| T11 | Starfield devolve Summon: Knights (3 Knights) · Bath Song II · **The Kami War** (cap. I exila a Witness Protection) · Scholar · Casualties of War destrói Sol Ring, Summon: Knights, Fertile Ground e a Hallowed Fountain (e a Utopia Sprawl junto) |
| T12 | **Kami War**: Hex Parasite tira o marcador (1→0) no upkeep, o passo natural a leva a 1 e o cap. I exila a **Deafening Silence** · Bath Song III → **gatilho do Tom: The First Iroan Games** · Starfield devolve Knights (+3 Knights) · Prismatic Omen, **Estrid's Invocation** (cópia da Knights: +3), Setessan Champion, Satsuki · Savai Triome |
| T13 | Starfield devolve **In the Darkness Bind Them** e a cópia da Starfield (Estrid) devolve **Summon: Primal Odin** · Kami War 1→0→1 de novo · Arcane Signet, Power Conduit, **Summon: Bahamut**, **Jugan** · Plains · O Anel (carga 2) |

**Conferido e correto** (script + conta à mão; escopo no `LEIAME.md` da pasta):
- **Terrenos**: 1 por turno. As repetições da mesma carta (Fountain nos T2–T4, Mountain ×3 no T10) são desfazer; no T2 foi a Ketria Triome e no T12 a Savai Triome (confirmado), a Overgrown Tomb do T12 e a Fountain do T2 foram desfeitas.
- **Mana** T3–T10 fecha (T4 = 3 com Ketria + Fountain + bônus da Sprawl; T5 = 4; T8 = 7; T10 gasta 8 de 10). T11–T13 não conferi cor por cor.
- **Starfield**: devoluções legais no upkeep: Bath Song (T10), Knights (T11 e T12, 3 fichas cada), ITDBT e Primal Odin (T13: a Starfield e a cópia dela pela Estrid, 2 gatilhos).
- **Deafening Silence** ("uma magia não-criatura por turno", conta o turno inteiro: ruling 2019-10-04): T10 só a Resourceful Defense, T11 só a Kami War; no T12 e no T13 ela já tinha saído (exilada pelo cap. I da Kami War, ver abaixo).
- **Loop Kami War + Hex Parasite**: legal. O Hex Parasite tira o marcador de saber no upkeep (`{X}{B/P}`: X = 1) e o passo natural o devolve: o capítulo I dispara de novo (ruling: remover marcador deixa o capítulo disparar de novo quando um marcador é *posto*). Cada volta exila um permanente não-terreno do oponente: T11 Witness Protection, T12 Deafening Silence, T13 alvo não informado.
- **Descartes de propósito** (Torment de 3): Primal Odin, Leyline Binding e Bath Song já no cemitério para a Starfield (Bath Song voltou no T10, Odin no T13).
- **Tom**: lançado no T6 (taxa 0), morreu e voltou no T8 (taxa 1); 1 gatilho em 13 turnos (T12: Bath Song III → The First Iroan Games).

**Confirmado pelo usuário (2026-10-02)**
- **Compras**: esqueceu "quase todas" as do Femeref e algumas das demais. Ledger (`resumos/ledger_compras.md`): esperado 67, log 54 (−13): T7 −1, T10 −1, T11 −4 (Eidolon pelo Knights que voltou e Femeref ×3 do Casualties), T12 −5 (Femeref da Bath Song e Estrid ×3, mais 1), T13 −2. Só prejudica o jogador.
- **Marcadores**: Kami War com saber 2 no T12 foi erro de registro (o certo era 1→0→1); Summon: Knights 1→2 no T13 sem fonte foi erro; a Iroan Games II deu só 2 marcadores ao Tom em vez de 3 (erro); os marcadores do Setessan Champion foram esquecidos.
- **T10**: a Fable "mão→campo" foi erro de registro (foi descartada); eram para ser 2 descartes (os 2 Syphon Mind) e o log tem 3, então um descarte indevido (o usuário não disse qual; a Fable é o último do log); a Resourceful Defense em 3 registros foi erro (1 conjuração).
- **T6, Tom morto**: o usuário diz que foi o Casualties of War. O log mostra o Torment of Hailfire no T6 e o Casualties de fato só no T11 (alvo de criatura: Summon: Knights; o Tom ficou). Divergência entre o relato e o log, sem efeito: o Tom volta ao comando e é recastado no T8 com taxa 1.
- **Terrenos**: Ketria Triome no T2 e Savai Triome no T12.

**Leitura do deck** (oráculo + regras; o simulador só apoia):
- **O prejuízo principal desta partida é contabilidade, não regra**: 13 compras a menos de 67 (~19%). O Femeref é o motor mais esquecido (4 compras).
- **Kami War + Hex Parasite** é um removedor repetível por turno, o mesmo padrão do O'aka + Jugan (#8). O simulador usa o Hex Parasite para salvar capítulo final e no combo infinito, mas `try_value_removers` só tem O'aka, Scholar e Power Conduit: **candidato a ajuste no simulador** (Regra #5: convenção, não limite da carta). Não alterei.
- **Sim × real**: Tom lançado no T6 (simulador: até o T6 em 76,2%), mas 0 gatilhos do Tom até o T8, e o 1º só no T12. No simulador, 0 gatilhos até o T8 acontece em 28,5% das partidas de 8 turnos. O Tom morrer e recastar no T8 (taxa 1) pesou.

### Partida manual #11 (2026-10-02) — 19 turnos; a mais longa e a que mais sofreu interação · AGUARDANDO as respostas do usuário

Dados brutos, scripts, ledger e rulings em `tom-bombadil-wubrg/resultados-ab/2026-10-02-partida-manual-11/` (Regra #8; `LEIAME.md` tem o escopo). O usuário jogou "para testar a resiliência" (mulligan 0, simulador de interação On; 16 interações simuladas).
Mão (foto): Raugrin Triome, Windswept Heath, The Eldest Reborn, In the Darkness Bind Them, Jugan Defends the Temple, Fertile Ground, Ketria Triome; a 8ª carta (O'aka) é a compra do T1.
Oráculos ao vivo; rulings lidas antes de concluir (36 cartas; `resumos/rulings_scryfall.json`).

| Turno | Evento principal |
|---|---|
| T1–T4 | Ketria Triome · Windswept Heath busca Overgrown Tomb + Fertile Ground · Raugrin Triome, O'aka · Savai Triome, Faeburrow Elder |
| T5 | Karn's Bastion · **Tom Bombadil** (5) e, com o Tom em campo, o Faeburrow Elder dá 5 cores → **In the Darkness Bind Them** (5) · cap. I: Wraith + O Anel (O'aka é o Ring-bearer) |
| T6 | Breeding Pool · ITDBT II · **War of the Last Alliance** (cap. I busca a Narci) · **Narci** · **Jugan** (cap. I: Human Monk) · **Blasphemous Edict** (menos de 13 criaturas: sacrifica todas): Tom volta ao comando (taxa 1) |
| T7 | ITDBT III · Jugan II · War II · **Tom** (7 = 5 + taxa 2) |
| T8 | **Starfield of Nyx** · ITDBT IV, Jugan III (vira Dragão) e War III: **gatilho do Tom → Binding the Old Gods** · **Martial Coup** (X≥5): Tom, o Dragão da Jugan e as fichas morrem (Tom volta, taxa 2) |
| T9 | Starfield devolve a ITDBT · Binding II (busca a Ziatora's Proving Ground) · **The Eldest Reborn** · Temple Garden · Amazing Acrobatics |
| T10 | The World Tree · Starfield devolve a Jugan · Binding III (sem Tom em campo: sem gatilho) · **Tom** (9) |
| T11 | Eldest III: Narci volta e **gatilho do Tom → The Cruelty of Gix** · **Summon: Fenrir** (cap. I: Plains) · **Goldberry** · Eldest Reborn aparece de novo em campo (ver dúvida 1) |
| T12 | Cruelty II (busca Power Conduit) · War (devolvida) I busca **Sythis** · Sythis (+1/+1 do Fenrir II), Power Conduit, **Satsuki** · ITDBT IV salva pela Goldberry (4→3) · Lethal Scheme destrói a Sythis |
| T13 | Cruelty III: Sythis volta · Jugan III vira Dragão · ITDBT IV · Eldest III devolve O'aka (salva pelo Power Conduit, 3→2) · **gatilho do Tom → There and Back Again** · Fenrir III · Sanctum Weaver, **Historian's Boon** · War II busca Barbara · Soul Shatter: Tom volta ao comando (taxa 3) |
| T14 | War III e Eldest III (devolve a Fenrir) + **2 Angels** da Boon · Cruelty volta · **Tom** (11) · **Bane of Progress** destrói 11 encantamentos/artefatos (Starfield, Power Conduit, Boon, Jugan, Sythis, Weaver...) |
| T15 | Barbara Wright, **Summon: Primal Odin**, Utopia Sprawl, City of Brass · No Mercy (oponente) |
| T16 | O'aka + **Nexus Mentality** (2 modos): Odin 2→1→0 e o contador vai para um Angel; os 2 marcadores do Tom saem e compram 2 · **Resurgent Belief suspensa** (2) · Jace's Archivist · Soul Shatter sacrifica o Odin |
| T17 | Sol Ring, Flux Channeler, Nesting Grounds · Resurgent Belief (1) · Steel Hellkite + **All Is Dust** (oponente) |
| T18 | All Is Dust varre as permanentes coloridas (Tom, Narci, Goldberry, Satsuki, O'aka, Barbara, Flux, Utopia Sprawl...) · **Resurgent Belief resolve no upkeep: 16 encantamentos voltam** · 14 Human Soldier (Boon) · **Tom** (13 = 5 + taxa 8) · Teferi's Protection contra Vandalblast + Casualties of War |
| T19 | Strionic Resonator comprada; Teferi's Protection sai · fim |

**Conferido e correto** (script + conta à mão; escopo no `LEIAME.md`):
- **Terrenos**: 1 por turno de T1 a T17 (Windswept Heath → Overgrown Tomb no T2; Binding II → Ziatora e Fenrir I → Plains/Island/Swamp são efeitos, não jogada). T8 e T12 sem jogada de terreno com terreno na mão (escolha, não regra).
  O T14 "Catacombs sem busca" do script é falso positivo: o terreno ficou em campo e a The World Tree dá "qualquer cor" a todo terreno com 6+ terrenos.
- **Mana (total)** fecha de T2 a T17: T5 = 10 (4 terrenos + Fertile + Elder 5 com o Tom em campo = Tom 5 + ITDBT 5), T6 = 11, T7 = 7, T8 = 5, T9 = 5, T10 = 9, T11 = 5, T12 = 6, T13 = 7 (inclui o {U} da Goldberry), T15 = 9, T17 = 4. Cor não conferida.
- **Tom**: lançado 5 vezes (T5, T7, T10, T14, T18) com taxa 0, 1, 2, 3, 4 = custo 5, 7, 9, 11, 13; o log fecha. Gatilhos (1 por turno): T8 Binding, T11 Cruelty, T13 There and Back Again. T10 sem gatilho está certo (o Tom entrou depois do cap. III do Binding).
  No T18 o Tom entra com 9 marcadores de saber nas Sagas (≥ 4): hexproof e indestrutível contra Vandalblast/Casualties.
- **Interações simuladas**: Blasphemous Edict (T6) sacrifica todas as criaturas (ruling 2024-11-08); Bane of Progress (T14) destrói exatamente os 11 encantamentos/artefatos que estavam em campo (o log tem os 11); All Is Dust (T18) sacrifica as 9 permanentes coloridas e os terrenos ficam (ruling 2018-12-07);
  Soul Shatter (T16) sobre o Odin é forçado (MV 6 > Tom).
- **Saves de Saga com o capítulo final na pilha**: ITDBT 4→3 pela Goldberry (T12) e Eldest 3→2 pelo Power Conduit (T13) são legais (ruling: o capítulo já disparado não é afetado; a Saga só é sacrificada se ainda tiver ≥ final).
- **Resurgent Belief**: suspensa no T16 (2), 1 no T17, resolve de graça no upkeep do T18 (suspend); "todos os encantamentos do cemitério voltam" (ruling 2021-06-18): são 16 cartas e o log tem as 16.
- **Nexus Mentality (T16)** com o Tom em campo: os 2 modos juntos (mover os contadores do Odin e remover os do Tom comprando 2) são legais (ruling 2026-03-20).
- **Narci** volta no T11 pelo Eldest III e vê a resolução do capítulo final (ruling do Tom, 2023-06-16: "triggers when another ability resolves... will see"); Fenrir II (T12) põe o +1/+1 na Sythis (a próxima magia de criatura).
- **Compras por tutor**: War I → Narci (T6) e Sythis (T12), War II → Barbara (T13), Cruelty II → Power Conduit (T12).
- **Mão do T18**: 14 cartas descartadas a 7 = limite de mão no fim do turno; Teferi's Protection conjurada na vez do oponente com a Serra's Sanctum.

**Perguntas ao usuário (pendentes, 2026-10-02)**
1. **Eldest Reborn voltou depois de sacrificada** (T11 e T14): a Starfield só age no upkeep, quando a Eldest ainda estava em campo. Quem a devolveu? No T14 ela ainda ganhou um 2º marcador (1→2).
2. **Starfield × marcador natural**: ITDBT (T9), Jugan (T10), War (T12) e Cruelty (T14) voltam com 1 marcador e terminam o turno com 1. Pela regra (714.3b) a devolução é no upkeep e o marcador natural vem depois, então terminariam com 2 (cap. II no mesmo turno). Foi a ordem manual (marcador antes da Starfield)? Além disso a Jugan ficou com 2 do T11 ao T12 (nenhum registro no T12).
3. **T12, gatilho do Tom**: a ITDBT chegou ao cap. IV (final) e você a salvou com a Goldberry; o Tom (1×/turno) devia ter buscado uma Saga da biblioteca e não há nenhuma library→campo no T12.
4. **Compras** (`resumos/ledger_compras.md`): esperado 49, log 55; por turno T7 −1 (War II só aparece no T8), T11 −1 (Narci), T13 −4, T14 −1 (esperado: compra + Narci ×2 pelas Sagas sacrificadas; o log tem só 2 cartas), T16 −1 (Narci pelo Odin sacrificado); T18 +13.
5. **T18, 14 cartas library→mão** sem fonte no log (Narci e Sythis estavam mortos pela All Is Dust): de onde vieram?
6. **Fichas da Boon**: T14 devia dar 3 Soldier (Fenrir, Eldest, Cruelty entraram com a Boon) e há 1 "Knight"; T18 devia dar 16 (16 encantamentos entraram juntos com a Boon) e há 14. Os 2 Angels do T14 (War III e Eldest III) estão certos.
7. **T18, 2 terrenos da mão**: Hall of Heliod's Generosity e Serra's Sanctum.
8. **O Anel**: o Ring-bearer fica virado de T10 a T17 e o Anel já tinha o "compre e descarte ao atacar" desde o T6: não há nenhum loot no log.
9. **There and Back Again II (T14)**: Lore=2 e nenhum Mountain entrou (a lista tem Mountain, Stomping Ground e Jetmir's Garden na biblioteca; a Island do T14 foi do Fenrir I).

**Leitura do deck** (oráculo + regras; o simulador só apoia):
- **Resiliência**: o Tom morreu 4 vezes (Edict T6, Martial Coup T8, Soul Shatter T13, All Is Dust T18) e voltou pelo comando com taxa até 4 (5 lançamentos no total); o Bane of Progress não o atinge (não é artefato nem encantamento) e, com ≥ 4 marcadores nas Sagas, ele fica hexproof e indestrutível. A Resurgent Belief reconstruiu 16 encantamentos de uma vez (a Boon deu 14 fichas) e a Teferi's Protection passou por Vandalblast + Casualties.
- **Sim × real**: Tom no T5 (simulador ≤T5 em 56,8%), 1 gatilho até o T8 (simulador: ≥1 em 71,5%, ≥2 em 47,3%). O simulador só mede 8 turnos; o `upkeep_step` já faz a Starfield antes do marcador natural (714.3b), então a ordem do log manual é do jogador, não do simulador. Nada a mudar no código.
