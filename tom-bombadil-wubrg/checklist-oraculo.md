# Tom Bombadil — checklist oráculo × código (2026-09-22)

Construção do simulador `tom_goldfish_v1.py` do zero, junto com a lista.
Método (CLAUDE.md, Regra #1): oráculo das 100 cartas buscado **ao vivo** no
Scryfall (`/cards/collection` + `/cards/named?fuzzy=` para as de duas
faces; cache em `scryfall_oracle.json`), rulings das peças-chave lidas
(Tom, Estrid's Invocation, Urza's Saga, Satsuki, Nesting Grounds,
Goldberry, Strionic, Clockspinning, Hex Parasite, Ripples, Flux Channeler,
Starfield, Prismatic Omen, Kami War), regras de Saga (CR 714) lidas no
`rules-cache`, comparação cláusula por cláusula, varredura de
tags/nomes órfãos e 57 testes dirigidos (`test_tom_goldfish.py`, todos passando).

Legenda: ✅ implementado (função) · 🐛 bug achado e corrigido **nesta
rodada** (antes do 1º commit) · 📊 estrutural (depende de estado real de
oponente — cláusula do oráculo citada; conta como métrica proxy quando dá).

## Regras centrais (valem para as 25 Sagas)

- ✅ 714.2b: capítulo N dispara quando o lore "was less than N and became
  at least N". **Toda** colocação de lore passa por `add_counters()`, que
  empilha todos os capítulos atravessados (teste
  `test_crossing_multiple_chapters_triggers_all`).
- ✅ 714.3b: o lore do turno entra no início da fase principal pré-combate
  (`precombat_lore_step`, chamado em `run_turn` **depois** do draw e
  **antes** de qualquer ação da fase principal; Regra #6 conferida).
- ✅ 714.4: sacrifício por SBA só quando nenhum capítulo dela está na pilha
  (`check_sba` roda entre **cada** resolução de `resolve_stack`). Remover
  lore em resposta ao capítulo final mantém a Saga (`try_save_final`).
- 🐛 **Read ahead (702.155)**: 1ª versão somava N marcadores de uma vez e
  disparava I..N. A regra diz "Skipped chapters don't trigger". Corrigido
  em `saga_enter_lore` (só o capítulo escolhido dispara). Achado no teste
  `test_barbara_read_ahead_final_with_tom`.
- 🐛 **Resposta dentro da pilha** (Regra #6, orquestração): Clockspinning
  salvando capítulo final e Enlightened Tutor em resposta ao Tom chamavam
  `resolve_stack` por dentro. Com Flux Channeler em campo, o capítulo final
  resolvia **antes** do marcador sair, e a Saga era sacrificada em vez de
  salva. Corrigido com `cast_instant(..., in_response=True)`: os gatilhos
  ficam empilhados por cima, a pilha não é resolvida por dentro, e o
  original é reinserido embaixo das respostas em `resolve_item`. Tem teste
  de regressão (`test_clockspinning_save_with_flux_channeler_in_play`).
- 🐛 **Mágica em resposta resolvia na hora** (2ª parte do mesmo achado):
  a 1ª correção aplicava o efeito do Clockspinning na hora e já o
  devolvia pra mão pelo buyback, com o gatilho do Flux Channeler ainda na
  pilha. A mesma cópia salvava várias Sagas numa cascata só (a varredura
  de robustez pegou partidas de ~490 capítulos em 10 turnos). Agora toda
  instantânea é um item real da pilha (`kind: "spell"` →
  `resolve_spell`), empilhado **antes** dos gatilhos de conjuração dela.
  Alvo que sumiu = não resolve (608.2b), sem efeito e sem buyback.
- ✅ **Combo infinito real** (There and Back Again + Clockspinning/Flux +
  Hex Parasite, com Smaug em campo): cada III cria um Smaug novo, o antigo
  morre pela regra da lenda e gera 14 Treasures, por ~6 de custo. Teste
  `test_infinite_smaug_loop_is_real_and_detected`. Detectado e encerrado
  como vitória por combo (`infinite_combo_turn`), ver `goldfish-log.md`.
- 🐛 **Proliferate** escolhia inclusive a Saga que acabou de ser salva
  (capítulo ainda na pilha), redisparando o final e sacrificando-a.
  "Choose any number" → agora pula Sagas com capítulo pendente.

## Comandante

### Tom Bombadil
> As long as there are four or more lore counters among Sagas you control, Tom Bombadil has hexproof and indestructible. / Whenever the final chapter ability of a Saga you control resolves, reveal cards from the top of your library until you reveal a Saga card. Put that card onto the battlefield and the rest on the bottom of your library in a random order. This ability triggers only once each turn.
- ✅ 4+ lore → indestrutível (`tom_protected`, `is_indestructible`; wipe de criatura do modo de resiliência não o mata). Hexproof: 📊 no goldfish (sem alvo de oponente); a remoção pontual do modo de resiliência já exclui o comandante por convenção.
- ✅ Gatilho depois do capítulo final **resolver** (`on_final_chapter_resolved`), 1×/turno (`tom_triggered_this_turn`), revela até "Saga card" (face da frente em DFC; Urza's Saga conta), resto no fundo em ordem aleatória **pelo RNG com seed** (`resolve_tom_trigger`).
- ✅ CR 903.8 (taxa), 903.9a (morre → zona de comando), 903.10a (dano de comandante por uid).

## Sagas (24 mágicas + Urza's Saga)

### The Kami War // O-Kagachi Made Manifest
- 📊 I "Exile target nonland permanent an opponent controls" → `interaction_plays`.
- 📊 II "Return up to one other target nonland permanent to its owner's hand. Then each opponent discards a card" → `interaction_plays`.
- ✅ III exila e volta transformada (`transform_saga`; sair com 3 lore dispara Resourceful Defense).
- ✅ O-Kagachi "is all colors" (conta 5 cores pra Bloom Tender/Faeburrow); ✅ ataque: "defending player chooses a nonland card in your graveyard" → o oponente escolhe a de **menor** MV (pior pra mim), volta pra mão, +X/+0. Flying/trample 📊 (sem bloqueio modelado).

### Binding the Old Gods
- 📊 I destroy nonland permanent de oponente. ✅ II "Forest card, tapped" (`search_land_to_battlefield` com tipo impresso). 📊 III deathtouch (sem bloqueio).

### There and Back Again
- 📊 I "Up to one target creature can't block" + ✅ "The Ring tempts you" (`ring_tempts`). ✅ II "Mountain card" **desvirada** (oráculo não diz tapped; shock buscada paga 2). ✅ III Smaug 6/6 flying haste lendário; ✅ "When Smaug dies, create fourteen Treasure tokens" (inclusive pela regra da lenda ao repetir o III).

### Kiora Bests the Sea God
- ✅ I Kraken 8/8 hexproof. 📊 II "Tap all nonland permanents target opponent controls". 📊 III "Gain control of target permanent an opponent controls".

### Summon: Bahamut
- 📊 I, II "Destroy up to one target nonland permanent". ✅ III compra 2. ✅ IV Mega Flare = soma do MV dos **outros** permanentes × cada oponente (`mega_flare_total`). ✅ 9/9 flying ataca.

### Battle at the Helvault
- 📊 I, II exila permanente não-Saga de cada jogador ("For each player… up to one" — do meu lado escolho nenhum). ✅ III Avacyn 8/8 flying/vigilance/indestrutível lendária (regra da lenda: repetir o III não soma).

### War of the Last Alliance
- ✅ I, II tutor de criatura lendária → mão (prioridade: motor que falta). ✅ III double strike até o fim do turno (dispara no 714.3b, vale no combate do mesmo turno — Regra #6) + Ring tempts.

### Song of Eärendil
- ✅ I scry 2 + compra 2. ✅ II Treasure + Bird 2/2 flying. ✅ III marcador de flying em cada criatura sem flying (marcador real: Resourceful/Goldberry podem movê-lo).

### The Creation of Avacyn
- ✅ I tutor → exilado ligado à Saga (`exiled_card`). ✅ II perde vida = MV se for criatura. ✅ III criatura → campo (linha real: Summon: Bahamut de graça), senão mão. Se a Saga sai antes do III, a carta fica exilada.

### Awaken the Honored Dead
- 📊 I destroy nonland permanent. ✅ II mill 3. ✅ III descarta pior carta → devolve criatura/terreno do cemitério.

### The Coming of Galactus
- 📊 I destroy. ✅ II, III cada oponente perde 2. ✅ IV Galactus 16/16 flying trample lendário; 📊 "Whenever Galactus attacks, destroy target land" (terreno de oponente) → `interaction_plays`.

### Jugan Defends the Temple // Remnant of the Rising Star
- ✅ I Monk 1/1 com "{T}: Add {G}" (dork real). ✅ II +1/+1 em até 2 criaturas. ✅ III transforma.
- ✅ Remnant: "Whenever another creature you control enters, you may pay {X}" (paga X=1 se sobra mana — `on_creature_enters`); ✅ 5+ criaturas modificadas → +5/+5. Flying/trample 📊.

### Elspeth Conquers Death
- 📊 I exile MV≥3 de oponente; 📊 II taxa de oponente. ✅ III volta criatura do **meu** cemitério + marcador +1/+1.

### The Eldest Reborn
- 📊 I edict; 📊 II discard. ✅ III "from a graveyard" — só o meu é modelado (cemitério de oponente 📊).

### The Bath Song
- ✅ I, II compra 2 descarta 1. ✅ III embaralha cartas do cemitério no grimório (mantém encantamentos se há recursão de encantamento em jogo) + {U}{U} que **some** ao fim da fase (`burn_unspent_bonus`).

### The Cruelty of Gix
- ✅ Read ahead nativo. 📊 I (mão de oponente). ✅ II tutor + perde 3. ✅ III reanima criatura de cemitério (o meu).

### Birth of the Imperium
- ✅ I um Astartes 2/2 vigilance **por oponente** (3). 📊 II edict. 📊 III "Draw two cards for each opponent who controls fewer creatures than you" — compara com board de oponente, não fabrico (`structural_unmeasured`).

### In the Darkness Bind Them
- ✅ I, II, III Wraith 3/3 menace + Ring tempts. 📊 IV rouba criaturas de oponente + ✅ Ring tempts.

### Summon: Knights of Round
- ✅ I–IV três Knights 2/2 cada. ✅ V +2/+2 até o fim do turno + marcador indestrutível nas outras. ✅ Indestructible (estático — sobrevive a wipe no modo de resiliência).

### Summon: Primal Odin
- 📊 I destroy creature de oponente. ✅ II Zantetsuken → `odin_eliminations` (sem bloqueio modelado; nunca vitória automática). ✅ III compra 2 + cada jogador perde 2 (eu também).

### Summon: Fenrir
- ✅ I terreno **básico** → campo virado. ✅ II próxima criatura conjurada neste turno +1/+1. 📊 III "if you control the creature with the greatest power" (precisa do board de oponente).

### Fable of the Mirror-Breaker // Reflection of Kiki-Jiki
- ✅ I Goblin Shaman 2/2 ("Whenever this token attacks, create a Treasure"). ✅ II descarta até 2 e compra o mesmo número. ✅ III transforma → ✅ Reflection: "{1},{T}: copy another nonlegendary creature… haste. Sacrifice it at the beginning of the next end step" (cópia de Summon entra no capítulo I).

### The First Iroan Games
- ✅ I Soldier 1/1. ✅ II três +1/+1. ✅ III compra 2 se tenho poder 4+. ✅ IV Gold token (vira mana de qualquer cor).

### Summon: Yojimbo
- 📊 I exile de oponente; 📊 II, III "creatures can't attack you unless…" (Propaganda); 📊 IV "X = opponents who control a creature with power 4 or greater". ✅ Vigilance (ataca sem virar).

### Urza's Saga (terreno)
- ✅ I ganha "{T}: Add {C}". ✅ II ganha "{2},{T}: Construct 0/0 +1/+1 por artefato" (conta Treasure/Gold). ✅ III busca artefato de custo **exato** {0}/{1} (Sol Ring, Hex Parasite — ruling). ✅ É Saga pro Tom, pro limiar de 4 lore, pro Serra's Sanctum.
- ✅ Interação real: com Starfield of Nyx ativo vira criatura 0/0 e morre por SBA (`check_sba`).

## Motor de marcadores

### Resourceful Defense
- ✅ "Whenever a permanent you control leaves the battlefield, if it had counters on it, put those counters on target permanent you control" (em `leave_battlefield`, vale pra Saga sacrificada, transformada, legend rule, wipe; alvo = Saga que mais ganha — cadeia medida em `resourceful_chain_max`).
- ✅ "{4}{W}: Move any number of counters…" (`try_resourceful_move`, pra fechar uma Saga no final e disparar o Tom).

### Goldberry, River-Daughter
- ✅ "{T}: Move a counter of each kind not on Goldberry from another target permanent…" (puxa; também é removedor em resposta ao capítulo final).
- ✅ "{U}, {T}: Move one or more counters from Goldberry onto another target permanent. If you do, draw a card." Mesmo {T} → uma das duas por turno; doença de invocação respeitada.

### Nexus Mentality
- ✅ Modo 1 move todos os marcadores de A→B; ✅ modo 2 remove todos de C e compra 1 por marcador; ✅ os dois se controlo comandante.
- 🐛 A 1ª versão só conjurava na busca pelo gatilho do Tom (0,6% das partidas na tabela de uso). O modo 2 sozinho é uma linha real de valor: zerar uma Saga no meio a faz recomeçar do capítulo I (ex.: Knights of Round no IV → compra 4 e mais 12 Knights). Agora também é usada no fim do turno (`try_nexus_value`, teste `test_nexus_mentality_value_reset_draws`).

### Power Conduit
- ✅ "{T}, Remove a counter from a permanent you control" → +1/+1 em criatura. Modo "charge counter on target artifact": nenhum artefato da lista usa marcador de carga (✅ escolha consciente do modo útil, não omissão).

### Scholar of New Horizons
- ✅ Entra com +1/+1. ✅ "{T}, Remove a counter…: Search for a Plains card" (tipo impresso, tríomes/shocks contam). 📊 "If an opponent controls more lands than you, you may put it onto the battlefield tapped" — sempre vai pra mão.

### O'aka, Traveling Merchant
- ✅ "{T}, Remove a counter from a nonland permanent you control: Draw a card."

### Hex Parasite
- ✅ "{X}{B/P}: Remove up to X counters from target permanent" (sem {T}, repetível; {B/P} pago com 2 de vida se vida > 20). ✅ +1/+0 por marcador removido.

### Clockspinning
- ✅ Buyback {3}. ✅ Remove **ou** adiciona marcador em permanente. ✅ Em "suspended card" (Resurgent Belief; tirar o último marcador conjura na hora — ruling).

### Satsuki, the Living Lore
- ✅ "{T}: Put a lore counter on each Saga you control. Activate only as a sorcery." (ruling: Saga já no final não redispara.)
- ✅ Morte: devolve Saga do cemitério pra mão.

### Barbara Wright
- ✅ "Sagas you control have read ahead" (`choose_saga_start`: pula direto pro final só com o Tom ainda podendo disparar e final forte).
- 📊 "Doctor's companion" — regra de construção de deck (segundo comandante Doctor); o Tom não é Time Lord Doctor.

### Flux Channeler
- ✅ "Whenever you cast a noncreature spell, proliferate" (resolve antes da mágica — ruling).

### Ripples of Potential
- ✅ Proliferate. Phase out de quem ganhou marcador: no goldfish escolho nenhum (fasar tiraria Saga/criatura sem ganho); 📊 o uso como proteção reativa exigiria segurar mana no turno de oponente — no modo de resiliência a proteção reativa modelada é o Teferi's Protection.

### Weaver of Harmony
- ✅ "Other enchantment creatures you control get +1/+1" (inclui Summons, Sythis, Eidolon, animadas pelo Starfield).
- ✅ "{G}, {T}: Copy target activated or triggered ability you control from an enchantment source" (capítulos e Resourceful Defense).

### Strionic Resonator
- ✅ "{2}, {T}: Copy target triggered ability you control" — prioridade no gatilho do Tom (2 Sagas); senão capítulo de valor alto. Cópia de capítulo final não conta como "final chapter resolves" pro Tom/Narci (conservador).

### Estrid's Invocation
- ✅ Entra como cópia de encantamento que controlo (prefere Saga; nunca lendário). ✅ "At the beginning of your upkeep, you may exile… return" → objeto novo, escolhe de novo (capítulo I a cada turno). ✅ Ruling: copiando Saga que transforma, o III a exila e ela fica no exílio.

## Retorno por Saga terminada

### Narci, Fable Singer
- ✅ Lifelink (combate). ✅ "Whenever you sacrifice an enchantment, draw a card" (SBA do 714.4 é sacrifício). ✅ Capítulo final resolve → cada oponente perde X, eu ganho X (X = MV da Saga, via LKI no item da pilha).

### Historian's Boon
- ✅ Este ou outro encantamento **não-token** entra → Soldier 1/1. ✅ Capítulo final **dispara** → Anjo 4/4 flying vigilance.

### Femeref Enchantress
- ✅ Encantamento vai do campo pro cemitério → compra (Saga sacrificada, wipe, Aura órfã).

## Enchantress

- ✅ **Sythis**: conjura encantamento → ganha 1 e compra.
- ✅ **Enchantress's Presence**: conjura encantamento → compra.
- ✅ **Setessan Champion**: encantamento entra → +1/+1 nela e compra.
- ✅ **Eidolon of Blossoms**: ela ou outro encantamento entra → compra.

## Rampa

- ✅ **Sol Ring** {C}{C}. ✅ **Arcane Signet** cor da identidade (WUBRG).
- ✅ **Utopia Sprawl** "Enchant Forest" (tipo em campo; Prismatic Omen conta), escolhe a cor mais escassa, +1 dessa cor.
- ✅ **Fertile Ground** +1 de qualquer cor.
- ✅ **Sanctum Weaver** X = encantamentos que controlo.
- ✅ **Bloom Tender** / ✅ **Faeburrow Elder** 1 mana de cada cor entre permanentes (Tom = 5); Faeburrow +1/+1 por cor, vigilance.
- ✅ **Enduring Vitality**: vigilance; "Creatures you control have {T}: Add one mana of any color" (estática, vale mesmo depois de voltar como não-criatura; convenção: criaturas de poder ≤1 sem outro {T} viram mana e não atacam); ✅ morre → volta como encantamento não-criatura.
- ✅ **Farseek** "Plains, Island, Swamp, or Mountain card" (não Forest; tríomes/shocks contam), virado.
- ✅ **Prismatic Omen**: terrenos com todos os tipos básicos (mana de qualquer cor, Utopia em qualquer terreno, domínio 5 pro Leyline Binding).

## Recursão

- ✅ **Replenish** / ✅ **Resurgent Belief** (suspend 2—{1}{W}, sem custo de mana; lança de graça quando sai o último marcador de tempo): tudo volta junto; Aura sem alvo fica; Estrid's Invocation só copia o que **já estava** no campo (ruling).
- ✅ **Starfield of Nyx**: upkeep devolve encantamento do cemitério; 5+ encantamentos → não-Aura viram criatura com P/T base = MV (doença de invocação respeitada — ruling).

## Interação / tutor

- 📊 **Swords to Plowshares** (criatura de oponente) → `interaction_plays`.
- ✅ **Leyline Binding** domínio (custo real `1 + max(0, 5 - tipos)`), entra como encantamento (dispara enchantress); 📊 exile de oponente; 📊 flash (só importa no turno de oponente).
- ✅ **Teferi's Protection**: 📊 no goldfish; ✅ no modo de resiliência é usada de verdade, reativa, se {2}{W} ficou aberto no fim do meu turno (anula wipe/remoção/ataque até meu próximo turno, é exilada).
- ✅ **Enlightened Tutor**: em resposta ao gatilho do Tom põe a melhor Saga no topo (o Tom revela exatamente ela); senão no fim do turno busca a peça de motor que falta.

## Terrenos

- ✅ **Nesting Grounds** {C} + "{1},{T}: Move a counter… Activate only as a sorcery" (virar o próprio terreno conta como custo de mana — `land_ability_affordable`).
- ✅ **Karn's Bastion** {C} + "{4},{T}: Proliferate".
- ✅ **Serra's Sanctum** {W} por encantamento. ✅ **Hall of Heliod's Generosity** {C} + "{1}{W},{T}: enchantment card do cemitério pro topo" (em resposta ao Tom ou no fim do turno).
- ✅ **The World Tree** entra virado, {G}, com 6+ terrenos todos produzem qualquer cor. Busca de "God cards": nenhuma carta God nas 99 (o Tom mora na zona de comando) — habilidade modelada como sem alvo, não omitida.
- ✅ **Command Tower** (WUBRG). 📊 **Exotic Orchard** (cores de terreno de oponente — 1 mana sem cor, convenção do Bumbleflower). ✅ **City of Brass** / **Mana Confluence** (1 de vida quando o gasto do turno obriga a usá-las). ✅ **Reflecting Pool** (cores dos meus terrenos).
- ✅ 9 tríomes/SNC: entram virados, 3 cores, **cycling {3}** (`try_cycling`). ✅ 6 shocks (paga 2, também quando buscada desvirada). ✅ 5 fetches (1 de vida, busca o tipo impresso, desvirado). ✅ 5 básicos.

## Varredura de tags/nomes órfãos

- 1ª passada: 57 tags só descritivas (o despacho deste arquivo é por **nome** de carta) e 4 cartas sem nome no código (City of Brass, Mana Confluence, Exotic Orchard, Command Tower — tratadas genericamente pela tag `pain_any` e pelo campo `produces`). As tags descritivas foram **removidas**, para não virarem "tags fantasma" numa auditoria futura. As palavras-chave sem efeito num goldfish (trample, menace, hexproof, flash) ficaram declaradas em `KEYWORDS_NO_EFFECT_IN_GOLDFISH`, com o motivo 📊.
- 2ª passada: 0 tags órfãs.

## Bugs de política achados rodando (não de oráculo)

- 🐛 Pareamento de cor **guloso** falhava em casos resolvíveis (GU, BGR, R, GW, UW pagam WUBRG) e deixava o Tom na zona de comando → pareamento bipartido exato (`pips_payable`).
- 🐛 O Tom só era tentado 1× no início da fase → agora é tentado antes de cada mágica do loop (rampa do mesmo turno libera a cor).
- 🐛 Hex Parasite gastava a mana do Tom salvando capítulo final no 714.3b → removedor pago não toca na mana do Tom enquanto ele pode ser conjurado.
- 🐛 Escolha de terreno por "conserta cor" jogava fetch→tríome virada no T2 e travava o Sythis → escolhe o terreno que libera mais mana gastável no turno (empate: o que entra virado).
- 🐛 Peça de motor de marcador entrava antes de qualquer Saga (sem Saga, não faz nada) → prioridade de Saga × motor depende de haver Saga em campo.

## Checklist por categoria de mecânica (`references/goldfish-sim-card-rules.md`)

| # | Categoria | Cartas da lista | Situação |
|---|---|---|---|
| 1 | Landfall | 0 cartas | N/A (checado: nenhum "Landfall —" no oráculo das 99) |
| 2 | Mana dorks | Bloom Tender, Faeburrow Elder, Sanctum Weaver, Enduring Vitality (+ criaturas via Vitality), token Monk (Jugan I) | ✅ doença de invocação respeitada em todos (`sick`); dork não ataca |
| 3 | Mana rocks | Sol Ring, Arcane Signet (+ Treasure/Gold) | ✅ sem doença de invocação |
| 4 | Fixing / mudar tipo de terreno | Prismatic Omen, The World Tree, Reflecting Pool, Command Tower, City of Brass, Mana Confluence, Exotic Orchard (📊), tríomes, shocks, fetches | ✅ cores pareadas exatamente (`pips_payable`); tipos impressos × tipos em campo separados |
| 5 | Motores de compra | Sythis, Enchantress's Presence, Setessan, Eidolon, Femeref, Narci, O'aka, Goldberry, Nexus Mentality, Bath Song, Song of Eärendil, Bahamut III, Odin III, First Iroan III, Ring nível 2 | ✅ todos disparando (tabela de uso no `goldfish-log.md`) |
| 6 | Motores de rampa | Farseek, Binding II, There and Back II, Fenrir I, Scholar, auras, fetches | ✅ restrição de tipo real de cada busca |
| 7 | Ativadas repetíveis | Nesting Grounds, Karn's Bastion, Hall of Heliod, Goldberry, O'aka, Scholar, Power Conduit, Hex Parasite, Satsuki, Weaver, Strionic, Resourceful Defense {4}{W}, Urza's Saga II, Reflection of Kiki-Jiki, Clockspinning (buyback) | ✅ custo real deduzido; {T} de criatura com doença de invocação; mesmo {T} da Goldberry = 1 por turno; terreno virado pra habilidade abre mão da mana |
| 8 | Combos entre peças da lista | Resourceful Defense em cadeia; "salvar capítulo final" (714.4) + Tom todo turno; Creation of Avacyn → Summon: Bahamut; Enlightened Tutor/Hall → topo → Tom; Strionic → 2 gatilhos do Tom; Barbara → final no turno em que entra; Estrid's Invocation re-copiando; Nexus zerando Saga; Smaug + regra da lenda → 14 Treasures | ✅ cada um com teste dirigido |
| 9 | Estáticas | Tom (4+ lore), Weaver (+1/+1), Starfield (animação P/T=MV), Prismatic Omen, World Tree, Enduring Vitality, Barbara (read ahead), Remnant (+5/+5), Knights (indestrutível), Faeburrow (P/T), Sanctum Weaver | ✅ aplicadas em toda leitura (`is_creature`, `creature_power`, `mana_units`, `land_types_in_play`, `is_indestructible`) |
| 10 | Métricas básicas | rampa (mana por turno), compra extra, interação 📊, recursão, letalidade (turno com dano ≥ 120) | ✅ todas no `run_batch` |
| 11 | Face múltipla | Kami War, Jugan, Fable — `layout: transform` no Scryfall (conferido) | ✅ só a frente é conjurável; o verso só pelo capítulo III |
| 12 | Planeswalkers | 0 cartas | N/A |
| 13 | Níveis (Classes/Sagas) | 0 Classes; 25 Sagas | ✅ todos os capítulos de todas as Sagas (seção acima); o capítulo II do Urza's Saga compete pelo mesmo {T} da mana (`activate_land`) |
