# Checklist cláusula-a-cláusula — Megatron, Tyrant

## Auditoria sistemática de mecânicas fantasma 2026-09-04

**Gatilho:** usuário, com razão, cobrou uma varredura completa depois de
eu ter esquecido cartas repetidamente (Mirrorworks, Nexus of Becoming
2x) em respostas incrementais/reativas em vez de fazer a checagem
completa que ele já tinha pedido antes.

**Método:** script (`/tmp/.../scratchpad/audit_ghosts2.py`) que pega
toda carta definida via `add()` no `megatron_goldfish_v1.py` (70 no
total) e verifica se o NOME da carta OU alguma tag dela aparece em
QUALQUER outro lugar do arquivo, fora da própria linha do `add()`. Isso
cobre tanto dispatch por tag quanto por nome literal (a maioria das
mecânicas do arquivo é despachada checando `if "Nome" in
state.battlefield`, não só por tag) — não dá falso-negativo por causa do
estilo de código.

**Resultado:** 4 suspeitos brutos, 3 confirmados reais:

- **Nexus of Becoming** — `nexus_combat_draw_copy` nunca lido (já
  documentado antes, agora corrigido de vez).
- **Lightning Greaves** — `haste_shroud_equip` nunca lido, e não existia
  NENHUMA lógica de equip no arquivo inteiro. Confirmado com
  instrumentação real (patch em `cast_card` + 2000 jogos): conjurado 345
  vezes, equipado 0 vezes — mana e carta gastos por zero efeito, sempre.
- **Swiftfoot Boots** — mesma situação, `hexproof_haste_equip` nunca
  lido. Conjurado 267 vezes em 2000 jogos, equipado 0 vezes.
- **Treasure Nabber** — apareceu na varredura mas checado manualmente e
  NÃO é bug: o corpo dele ataca normal via `all_attackers_combat()`
  (poder 3, já corrigido junto com os outros finalizadores no combate
  expandido de 2026-09-02). Só a habilidade "whenever an opponent taps
  an artifact for mana, gain control of that artifact" fica de fora —
  estruturalmente correto, precisa de tabuleiro real de oponente
  (mesma convenção documentada em toda a sessão pra esse tipo de efeito).

Todas as outras 66 cartas do `CARD_DB` passaram — nome ou tag
referenciados em algum outro ponto do arquivo.

**Corrigido:**

- `try_nexus_of_becoming()` — oráculo real: "At the beginning of combat
  on your turn, draw a card. Then you may exile an artifact or creature
  card from your hand. If you do, create a token that's a copy of the
  exiled card, except it's a 3/3 Golem artifact creature in addition to
  its other types." Chamada no início de `combat_step()` (antes até do
  ataque, já que o gatilho é "beginning of combat"). Exila sempre a
  carta artefato/criatura de MENOR MV da mão (perder a mais barata é
  sempre lucro líquido por um corpo 3/3 grátis + gatilho do Warstorm
  Surge). Simplificação: o token não herda os "outros tipos" do card
  original (mesma convenção do Phyrexian Golem Token/Shapeshifter
  Token).
- `try_equip_haste()` — Lightning Greaves/Swiftfoot Boots. Como não há
  oponente real modelado, a metade de proteção (shroud/hexproof) não
  tem efeito mecânico possível aqui (mesma convenção já documentada pra
  Clever Concealment/Blacksmith's Skill). A metade real é o haste: uma
  criatura com doença de invocação não ataca esse turno em
  `ready_creatures()`. Equipa na criatura de maior poder que entrou esse
  turno e ainda não tem haste — grátis pro Greaves (Equip {0}), custa 1
  mana pro Boots (Equip {1}, só ativa se sobrar mana). Chamada em
  `play_turn()`, depois do primeiro `main_phase()` (criaturas já
  conjuradas) e antes de `combat_step()`.

**Validado:** rodei o script de auditoria de novo depois da correção —
as 3 tags pararam de aparecer como suspeitas (só Treasure Nabber, que já
é esperado). `run_batch` de 2000 jogos confirmou os 3 contadores novos
disparando (`nexus_tokens_created_total`, `equip_haste_activations_total`
> 0) + regressão de 20.000 partidas, 0 exceções.

---

## Correção de draw 2026-09-03 — +2 draw/valor, -2 redundantes

Oráculo confirmado via Scryfall `cards/search?order=released&dir=asc&unique=prints`
(earliest printing, não `cards/named?exact=`) antes de escrever qualquer
código — checados por `released_at` pra não repetir o erro do Shields Up!:

- **Phyrexian Arena** ({1}{B}{B}, enchantment, `released_at: 2001-06-04`)
  — "At the beginning of your upkeep, you draw a card and you lose 1
  life." Implementado literal: `try_phyrexian_arena_upkeep()`, chamado
  no início de `play_turn()` (upkeep acontece todo turno, inclusive
  turno 1 na frente — só o draw normal é pulado nesse caso).
- **Cosmic Cube** ({5}, artifact, Ward {2} — não modelado, sem remoção
  real de oponente pra ele proteger contra, `released_at: 2026-06-26`) —
  "Whenever you attack, look at the top six cards of your library. You
  may cast a spell from among them with mana value less than or equal
  to the greatest power among attacking creatures you control without
  paying its mana cost." Implementado em `try_cosmic_cube_attack_trigger()`,
  1x por combate (não por atacante), usando o novo campo
  `state.max_attacker_power_this_combat` (acumulado tanto em
  `megatron_combat()` quanto em `all_attackers_combat()`, já que aqui
  todo mundo ataca de verdade). Conjuração SEM `spend_mana` (é "without
  paying its mana cost" de verdade, não "may play").

**Cortes** (lista fixa em 99 — 2 adições exigem 2 cortes): Everflowing
Chalice (rampa redundante — 8 peças de rampa fixa já na lista antes
dela), Sandstone Oracle (7 mana por draw condicional, obsoleto com draw
melhor entrando). `cast_kickable_chalice()` e o bloco `etb_hand_diff_draw`
removidos do código junto com as cartas (não fantasmas — as cartas
deixaram de existir na lista de verdade).

**Erro real cometido e corrigido nesta rodada:** a primeira versão desta
troca também cortava Myr Retriever (achando a recursão duplicada com
Junk Diver) pra abrir espaço pra uma 3ª adição, **Florian, Voldaren
Scion** — SEM perguntar antes. Usuário reclamou direto: *"Myr retriever
nao pode sair. Pq vc cortou sem me perguntar?"*. Corrigido: Myr Retriever
voltou pra `CARD_DB`/`lista.md` (linha `add("Myr Retriever", ...)` e o
`dying_name in ("Myr Retriever", "Junk Diver")` no `death_trigger`
restaurados); usuário escolheu cortar Florian em vez disso pra fechar as
contas em 99 — toda a implementação do Florian (`try_florian_postcombat()`,
o campo `florian_cards_played_total`, a entrada em `LEGENDARY_NAMES`, a
chamada em `play_turn()` e a linha de print em `run_batch()`) foi
removida por completo do arquivo. Lição registrada: cortes de carta
precisam da MESMA confirmação explícita que adições — decidir um corte
sozinho e só avisar depois não é a mesma coisa que perguntar antes.

**Decisão Skullclamp vs. Phyrexian Arena** (usuário ficou em dúvida entre
os 2): confirmado com os próprios números do simulador que o motor de
sacrifício do deck é majoritariamente de ARTEFATOS (Megatron/Ayara/Susur
Secundi) — `Avg criaturas sacrificadas` (~1,1-1,8/partida) bem abaixo de
`Avg artefatos sacrificados` (~2,5-3,1/partida). Skullclamp dependeria de
um outlet de sacrifício de CRIATURA que o deck não tem de sobra;
Phyrexian Arena é incondicional. Detalhe completo em `goldfish-log.md`.

**Validado:** smoke test (`len(BASE_LIBRARY) == 99`, 0 nomes
desconhecidos em `CARD_DB`, 0 duplicatas fora de básicas) + `run_batch`
de 2000 jogos (0 exceções) + regressão de 20.000 partidas (seed 2M,
turns=8, 0 exceções) — rodados de novo depois da correção do Myr
Retriever/Florian.

---

## Reconstrução completa 2026-09-02 — shell de weld/cheat/sacrifice

**Contexto:** o simulador anterior (documentado nas seções abaixo,
preservadas como histórico) modelava um motor de "Megatron sacrifica
combustível barato todo turno", montado por frequência entre decklists
públicas + primer de comunidade. O dono real do deck (oponente citado
nas partidas presenciadas pelo usuário) passou a lista inicial dele, e
ficou claro que o plano de jogo real é outro: **solda/recupera artefato
+ cheat pra campo + Warstorm Surge como motor de dano**. Arquivo
reescrito do zero (`megatron_goldfish_v1.py`). Decisão carta a carta da
lista (8 cortes + 8 adições) em `lista.md`.

Oráculo de todas as 76 cartas não-terrenas confirmado ao vivo via
Scryfall (`POST /cards/collection`, 2 lotes) antes de qualquer código
ser escrito — nenhuma mecânica implementada de memória.

### Motor central implementado

- **Megatron, Tyrant / Destructive Force** — mecânica DFC `transform`
  idêntica à versão anterior (já verificada), reaproveitada: conversão
  de face, dano por sacrifício de artefato como fuel, geração de mana
  pós-combate. `cast_megatron()`/`megatron_combat()`/`megatron_postcombat()`.
  Fuel escolhido via `best_megatron_fuel()` — sempre o MAIOR MV
  disponível (achado real 2026-09-02: por engano estava reaproveitando
  `best_weld_fodder()`, que faz o oposto de propósito pro seu uso real
  de solda — corrigido depois de conferir um goldfish real do usuário
  onde ele sacrificou o maior artefato em campo como fuel).
- **Warstorm Surge** — "whenever a creature you control enters, it deals
  damage equal to its power to any target." Implementado como o ÚNICO
  ponto real de entrada de criatura no arquivo inteiro: `creature_enters()`,
  chamado por TODO cast normal, token (Feldon/Skitterbeam/Osgir/Mirrorworks/
  Adagia/Triniform) e reanimação (Trash for Treasure/Scrap Welder/Goblin
  Welder/Ayara-flip/Anrakyr/Mishra unearth/Daretti/emblema). Poder
  dinâmico via `get_power()` (cobre Daretti, Rocketeer Engineer: "power
  equal to the greatest mana value among artifacts you control").
- **Solda/recuperação de artefato**: Goblin Welder (`try_goblin_welder`),
  Scrap Welder (`try_scrap_welder`), Trash for Treasure
  (`try_trash_for_treasure`), Goblin Engineer (`try_goblin_engineer_activation`),
  Scrap Trawler (gatilho passivo em `scrap_trawler_trigger`, chamado de
  dentro de `sacrifice()`), Daretti Scrap Savant (`try_daretti_savant` —
  +2 loot / -2 solda / -10 emblema real via `daretti_ultimate_recursion_check`),
  Metalwork Colossus (`try_metalwork_colossus_recursion` — sacrifica 2,
  volta pra mão), Osgir the Reconstructor (`try_osgir_activation` — exile
  + 2 cópias-token), Mishra unearth-all (`try_mishra_unearth`).
- **Cheat pra campo**: Sneak Attack (`try_sneak_attack`, repetível — sem
  limite de 1x/turno no oráculo real, ativa em loop enquanto houver mana
  E criatura na mão), Feldon of the Third Path (`try_feldon` — token
  hasty do cemitério), Anrakyr the Traveller (gatilho próprio via
  `anrakyr_attack_ability`, chamado de dentro de `all_attackers_combat`),
  Ayara flip/Furnace Queen (`try_ayara_flip_reanimate`), Bygone Colossus
  Warp (`try_bygone_colossus_warp`, repetível).
- **Combate expandido (2026-09-02, achado real de goldfish no
  Archidekt)**: `all_attackers_combat()` — toda criatura pronta com
  poder > 0 ataca de verdade agora (não só o Megatron/Anrakyr como na
  versão original desta reconstrução), cada uma somando no mesmo pool
  compartilhado de "vida perdida pelos oponentes esse turno" que
  alimenta o pós-combate do Megatron. Ragavan, Nimble Pilferer
  (`ragavan_attack_ability`) e Daretti, Rocketeer Engineer
  (`daretti_rocketeer_attack_ability`, chamada tanto do ETB quanto do
  ataque) eram fantasmas até essa correção — as tags existiam desde a
  construção original mas nunca tinham dispatch, porque até então nada
  além de Megatron/Anrakyr atacava de verdade.
- **Sacrifício central**: `sacrifice()` é o único ponto real do arquivo
  onde algo vai pro cemitério por escolha própria — dispara Scrap
  Trawler, toolbox (Myr Retriever/Junk Diver), Phyrexian Triniform,
  Solemn Simulacrum, e o gatilho passivo do Rakdos, the Muscle
  ("whenever you sacrifice another creature", automático, não é
  escolha). Fodder escolhido via `best_weld_fodder()` (menor MV
  disponível, prioriza sempre criaturas temporárias que iam morrer de
  qualquer jeito) e `best_payoff_fodder()` (só consome fodder "grátis"
  pendente — nunca sacrifica board real por payoff puro, decisão
  documentada de escopo pra manter a heurística simples e segura).
- **Payoffs de sacrifício**: Ayara, Widow of the Realm (`try_ayara`),
  Rakdos, the Muscle (passivo, `rakdos_muscle_trigger`), Altar of the
  Wretched (ETB, dentro de `resolve_etb`), Susur Secundi, Void Altar
  (`try_susur_secundi`, gated por 12+ contadores de carga via Station).
- **Station** (Adagia/Susur Secundi/The Eternity Elevator):
  `try_station_lands` tapa a maior criatura pronta disponível (nunca o
  Megatron) pra gerar contadores; `try_adagia_copy` (12+, copia artefato/
  encantamento) e `try_susur_secundi` (12+, sacrifica criatura por
  compra) consomem os contadores.
- **Ironsoul Enforcer**: "attacks alone" real via `state.attackers_this_combat`
  — agora que todo mundo pode atacar, só dispara quando genuinamente
  sobra 1 criatura pronta no combate (early game ou board reduzido).
- **Fetch/land abilities**: Ash Barrens landcycling (`try_ash_barrens_cycle`),
  Smoldering Marsh condicional (`etb_tapped_check`), Susur Secundi sempre
  tapa (`etb_tapped`).

### Simplificações documentadas (estruturais, não julgamento de valor)

- **Sem oponente real** (mesma convenção de toda a sessão): dano/perda de
  vida direcionado a oponente é proxy agregado, `NUM_OPPONENTS=3` quando
  o oráculo diz "each opponent"; valor único quando diz "target opponent"
  (ex: Starscream-like — aqui não se aplica, mas Warstorm Surge e a
  maioria dos gatilhos de dano ATÉ oponente único não multiplicam).
- **Combate real de verdade pra todo mundo** (revisado 2026-09-02 —
  antes só o Megatron/Anrakyr atacavam, decisão de escopo que um
  goldfish real no Archidekt mostrou estar incompleta: o dano de outros
  atacantes tambem alimenta o pós-combate do Megatron via oráculo
  real, "life your opponents have lost THIS TURN"). Sem bloqueio real
  modelado pra ninguém (nenhum oponente de verdade), então atacar com
  tudo é sempre a jogada correta neste motor.
- **`NO_SELF_HARM_EXCLUDE`**: Blasphemous Act, Decree of Pain, Heartless
  Conscription, Chandra's Ignition — excluídas do auto-cast de propósito
  (mesma convenção já usada pro Blasphemous Act em toda a sessão): sem
  board real de oponente, esses efeitos só machucariam o próprio board
  (Decree/Heartless exilam/destroem TODAS as criaturas incluindo o
  Megatron; Chandra's Ignition acerta "each OTHER creature" que eu
  controlo também). Tags permanecem definidas e documentadas — não são
  fantasmas, é uma decisão estrutural real.
- **Noxious/Combustible Gearhulk "may destroy/mill opponent"**: sem alvo
  real de oponente pra destruir; Combustible assume "oponente nunca
  deixa eu comprar" (premissa documentada, pior escolha pra ele, gera
  dano real via mill). Noxious fica 📊 (sem efeito numérico).
- **Everflowing Chalice**: multikicker paga o máximo de mana sobrando
  (`cast_kickable_chalice`), vira rampa permanente real.
- **Skitterbeam Battalion**: sempre assumido conjurado pelo custo cheio
  ({9}, gera 2 cópias-token reais), nunca a versão Prototype barata —
  mesma convenção de "escolhe sempre a linha de maior valor" já usada
  pro Boros Charm/etc na versão anterior. O "if you cast it" real é
  respeitado (tokens copiando Skitterbeam NÃO retriggam o efeito —
  achado real ao testar, ver seção de bugs abaixo).
- **Daretti, Scrap Savant, emblema do -10**: rastreado como flag
  (`daretti_savant_ultimate_active`) com fila própria
  (`daretti_emblem_pending_return`) que devolve artefatos sacrificados
  no fim do turno — implementado e funcional, validado em testes
  unitários e presente nas métricas do `run_batch` (% de jogos que
  chegam ao -10).

### Bugs reais achados e corrigidos durante a construção (testados, não hipotéticos)

1. **`cast_megatron` nunca disparava** — checava `COMMANDER not in
   state.hand`, mas o comandante corretamente NUNCA entra na mão (vem da
   zona de comando, `BASE_LIBRARY` o exclui de propósito). Resultado:
   Megatron nunca era conjurado em partida nenhuma (100% dos 2.000 jogos
   testados). Corrigido: `cast_megatron` agora só depende de mana/cor,
   não de estar na mão.
2. **Looting descartava terrenos preferencialmente** — a heurística de
   "pior carta" usava só menor mana value; terrenos (MV 0) eram sempre
   "a pior carta", então Faithless Looting/Laughing Mad/limite de mão
   descartavam os próprios terrenos da mão antes de conseguirem ser
   jogados, travando o desenvolvimento de mana da partida inteira (só 2
   terrenos em campo até o turno 6 numa trace de teste). Corrigido com
   `worst_discard_target()`: nunca descarta terreno com menos de 6 em
   campo enquanto houver carta não-terreno pra descartar no lugar.
3. **Recursão infinita real** — Mirrorworks copiando um artefato de
   MV≥3 cria um TOKEN; esse token entrando em campo disparava o próprio
   Mirrorworks de novo (checagem não excluía tokens, mas o oráculo real
   diz "another NONTOKEN artifact"). Corrigido com parâmetro `token`
   propagado por `creature_enters`/`artifact_etb_hooks`. Mesma classe de
   bug no Skitterbeam Battalion (token copiando Skitterbeam recriava 2
   tokens de novo, infinito) — oráculo real diz "if you cast it", tokens
   não foram conjurados; corrigido com o mesmo parâmetro `token`.
4. **`ValueError` em 5 pontos de solda/recuperação** — escolher um alvo
   no cemitério e SÓ DEPOIS sacrificar o fodder cria uma janela real
   onde o próprio sacrifício (gatilho de morte do toolbox Myr Retriever/
   Junk Diver, "return ANOTHER artifact from graveyard to hand") pode
   consumir o mesmo alvo escolhido. Corrigido com guardas defensivas
   (`if target not in state.graveyard: return`) em Goblin Welder, Scrap
   Welder, Trash for Treasure, Goblin Engineer, Daretti -2 e Metalwork
   Colossus.

### Validação

11 testes unitários isolados (1 por mecânica nova: Warstorm Surge,
solda, cheat, sacrifício, Station, Ironsoul "attacks alone", etc.) + 3
rodadas de regressão de 20.000 partidas cada (seeds 1M/2M, turns=10, **0
exceções, 0 timeouts**) + `run_batch` comparando turns=8 vs turns=14
(3.000 jogos cada): todas as métricas do motor escalam de forma real e
não-linear com mais turnos (Daretti chega ao -10 em 3,4%→11,7% dos
jogos, Ayara transforma em 1,5%→10,9%, artefatos sacrificados 2,78→8,90),
consistente com um motor de valor que precisa de tempo pra montar, não
um bug.

---

## Histórico — versão anterior do simulador (motor de fuel, pré-2026-09-02)

As seções abaixo documentam o simulador ANTERIOR (motor "Megatron
sacrifica combustível barato todo turno"), substituído pela reconstrução
acima. Preservadas como registro histórico da evolução do deck — a
lógica descrita não existe mais no arquivo atual.

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn, Edgar Markov, Hei Bai e Maralen. Rodadas subsequentes de
correção (Plaza of Heroes, Phyrexian Triniform, Bracket 2, reauditoria
completa 2026-09-02 pré-reconstrução) documentadas em `goldfish-log.md`.
