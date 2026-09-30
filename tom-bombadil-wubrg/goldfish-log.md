# Tom Bombadil — goldfish log

Regra #5: o simulador é **evidência de apoio**. A análise do deck
(`construcao.md`) vem do oráculo, das regras e dos motores reais. O
goldfish tem convenções fixas: ataca com tudo, não modela bloqueio, não
tem oponente real, e interação com oponente conta como 📊 (proxy).

**Dados brutos arquivados (Regra #8):** partidas manuais #6 e #7 (2026-09-30) em
`tom-bombadil-wubrg/resultados-ab/2026-09-30-partida-manual-6/` e `.../2026-09-30-partida-manual-7/`
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

### Partida manual #6 (2026-09-30) — 0 violações de regra provadas pelo log; 6 erros de operação confirmados pelo usuário

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
| T12 | ITDBT cap. II (Wraith). Anguished Unmaking (oponente simulado). O log mostra a ITDBT no exílio, voltando com Lore 1 e subindo até 3 no mesmo turno, com 2 Wraiths e 2 tempts a mais: erro de operação, o correto era só somar 1 marcador (ver "confirmado"). O'aka + Utopia Sprawl |
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
  tempts 3–4 do Anel foram erro. O alvo da Anguished Unmaking (oponente simulado, no mesmo turno) não foi informado.
- **Fichas do Culling Ritual (T8)**: Goblin Shaman e os Treasures deveriam ter sido removidos (MV 0). Ficaram em jogo por esquecimento.
- **Fertile Ground**: anexada no Serra's Sanctum (era a minha dedução; o T3 só fecha assim).
- **Enduring Vitality virada nos T7/T8**: era ataque simulado, erro dele. A Vitality tem vigilance (oráculo), então atacar não a vira.
- **Femeref, 2ª compra extra do T8**: feita antes da hora (a contagem de 2 compras estava certa; a ordem não).
- **Mana do T6**: o usuário reconhece erro, sem dizer qual. Pela minha conta, é compatível com Tom e Vitality terem sido virados como ataque: aí faltaria 1 mana para os 10 gastos.
  Se a Femeref (2) não tivesse sido conjurada no T6, as 2 compras do T8 também não teriam acontecido. Não medi.

**Sem resposta do usuário** (não perguntei ou não respondeu): a Fable com duas entradas idênticas no T6 (provável desfazer/refazer) e o Bloom Tender nunca virado (morreu no Ritual).

**Leitura do deck** (oráculo + regras; o simulador só apoia):
- O T2 real ficou sem jogada com 4 magias de 2 mana na mão (Femeref, Bloom Tender, Barbara, depois Fertile Ground): fetch no T1 (1 vida; busca um shock que entra
  virado de graça) e um shock destapado no T2 (2 vidas) dariam 2 fontes destapadas no T2. Não medi no simulador.
- T8, escolha de read ahead: com Barbara em campo, uma Saga pode entrar no capítulo final, mas o Tom só dispara 1 vez por turno — com o T8 já
  ocupado por ECD III + Fable III, entrar com a Galactus no cap. IV teria gastado o gatilho do turno; entrar no cap. I escalonou o final pro T11
  (2º gatilho do Tom). Trade-off de calendário, não erro.
- Reflection of Kiki-Jiki + Enduring Vitality: a cópia-ficha tem haste, toca pra mana ("criaturas têm {T}: mana") e conta como encantamento pro Sanctum;
  com Femeref viva, a cópia sacrificada no fim do turno compraria 1 (encantamento indo pro cemitério). Sem Femeref no T9–T10, o ganho foi só mana.
- **Sim × real**: Tom no T4 acontece em 27,3% das 3.000 partidas do simulador (≤ T5: 56,8%). Primeiro gatilho do Tom no T8, igual à #7.

### Partida manual #7 (2026-09-30) — 1 violação de regra provada pelo log (2º terreno no T8) e 5 outros erros/suposições do usuário, todos confirmados; 2 pontos residuais

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
- **Marcadores +1/+1 do Setessan Champion**: esqueceu de pôr os de quando encantamentos entraram (no T8 o oráculo pedia +4 e o log tem +2). Sobre a Sythis, o usuário lembrou que o gatilho só
  compra 1 carta e dá 1 de vida; o log não tem essa compra no T8.
- **Farseek no T7**: devia ter sido descartado pelo cap. II da Bath Song, e não entrado em campo (arrasto errado; nenhum terreno foi buscado).
- **Exotic Orchard no T5**: o usuário **presumiu** que o Orchard gerava a cor que faltava entre as 4 das outras fontes. Não é regra: o log não tem terreno de oponente, e o oráculo/ruling
  (2009-02-01) só dá cor de terreno de oponente (nunca incolor). Sem a suposição, o Tom no T5 não fecha (4 fontes reais para 5 cores); nos T3, T4, T6 e T7 o Weaver (que não foi virado) cobriria a falta.
  A conjuração do Tom no T5 fica como "legal só sob a suposição de que os oponentes têm terreno com a cor que faltava".

**Residual (sem resposta do usuário)**
1. **Compras da constelação do Champion nos T6 e T7 e a da Sythis no T8**: o log tem 1 compra a menos em cada um dos T6/T7 (passo + constelação + capítulo: 4 esperadas, 3 no log). O usuário só confirmou ter
   esquecido os marcadores. Suposição declarada: as compras também foram esquecidas (mesmo padrão). Só prejudica o jogador.
2. Bath Song mão→cemitério duas vezes no T8 (registro duplicado, provável desfazer/refazer).

**Leitura do deck** (oráculo + regras; o simulador só apoia):
- T5–T7 sem terreno na mão (Zagoth Triome descartado no T4 pro Torment): 4 terrenos até o T8. O Flux Channeler ficou na mão do T2 ao T8 (nunca conjurado, descartado
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
