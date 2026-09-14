# Checklist cláusula-a-cláusula — Vihaan, Goldwaker

## Auditoria oráculo-por-oráculo completa — 2026-09-14

Última das 16 decks desta campanha (mesmo tratamento já aplicado a
Edgar Markov, Hei Bai, Kutzil, Maralen, Ms. Bumbleflower, Nekusar,
Prismatic Bridge, Rat King, Thranduil, Toph, Azula, Beorn, Captain Storm,
Ur-Dragon e Ulalek). A rodada de 2026-09-01 (ver seção abaixo) já tinha
corrigido 3 gaps reais e concluído "arquitetura já madura, poucos gaps
restantes" — releitura completa desta rodada, clause-by-clause contra o
oráculo real (Scryfall `/cards/collection` em 2 lotes de 45/46, todas as
91 cartas encontradas de primeira, sem fallback `fuzzy` necessário —
inclusive o MDFC Brightclimb//Grimclimb e o `transform` do Sephiroth),
achou **16 gaps reais adicionais**, a maioria numa classe de bug que a
detecção automatizada de "tag órfã" das rodadas anteriores não conseguia
enxergar: **tag aplicada ao subconjunto ERRADO de cartas** (não uma tag
nunca lida — a tag "outlaw" É lida em vários lugares — mas aplicada
faltando em 7 cartas e sobrando em 2), e **habilidades 100% ausentes sem
nenhuma tag própria pra detecção automatizada encontrar** (Magda's
Scorpion Dragon só tinha um comentário mencionando o nome, nunca uma
implementação real).

### 🐛 Os 16 gaps reais corrigidos nesta rodada

**Grupo 1 — tags `outlaw`/`haste` erradas (afeta Back in Town, Olivia,
Laughing Jasper Flint, e o novo item 3 abaixo):**

1. **Tag `outlaw` faltando em 7 cartas com type real Assassin/Mercenary/
   Pirate/Rogue/Warlock** (verificado via `type_line` do Scryfall, não
   assumido): Captain Lannery Storm (*Human Pirate*), Grim Hireling
   (*Tiefling Rogue*), Lotho, Corrupt Shirriff (*Halfling Rogue*), Mari,
   the Killing Quill (*Vampire Assassin*), Pitiless Plunderer (*Human
   Pirate*), Witch of the Moors (*Human Warlock*), Zulaport Cutthroat
   (*Human Rogue Ally*). `OUTLAW_TYPES` já existia no arquivo mas nunca
   era usado pra checar tipo real — a tag era aplicada manualmente carta
   a carta, e essas 7 ficaram de fora.
2. **Tag `outlaw` sobrando em 2 cartas SEM type outlaw real**: Jan
   Jansen, Chaos Crafter (*Gnome Artificer* — Artificer não é outlaw
   type) e Magda, the Hoardmaster (*Dwarf Berserker* — Berserker não é
   outlaw type).
   Corrigido em `CARD_DB`. Afeta 4 pontos reais de leitura: `Back in
   Town` (alvo em pilha "outlaw creature cards"), o gatilho da Olivia,
   Opulent Outlaw ("um ou mais outlaws causam dano"), o X do Laughing
   Jasper Flint ("número de outlaws que você controla") e o novo item 3.
3. **Vihaan, Goldwaker — 2ª habilidade estática (a "menor" das duas,
   nunca lida) 100% ausente.** Oráculo real: *"Other outlaws you control
   have vigilance and haste."* Só a 1ª habilidade (animar Treasures em
   combate) estava implementada. Vigilance é 📊 (sem bloqueio modelado,
   não muda nada). Haste NUNCA era propagado pra `ready_creatures` —
   toda criatura outlaw sem a keyword impressa (Grenzo, Laughing Jasper
   Flint, Lotho, Mari, Olivia, Orochi Soul-Reaver, Pitiless Plunderer,
   Prosper, Witch of the Moors, Zulaport, Aya) ficava presa com doença de
   invocação no turno em que entrava, mesmo com Vihaan em campo
   concedendo haste de verdade — perdendo o gatilho de ataque daquele
   turno inteiro. Corrigido em `combat_step()`:
   `"haste" in CARD_DB[n].tags or (state.commander_in_play and is_outlaw(n))`.
4. **Tags `haste` faltando em 3 cartas com "Haste" real no oráculo**
   (Scryfall): Goldspan Dragon (*"Flying, haste"*), Jan Jansen, Chaos
   Crafter (*"Haste"*), Sentinel Sarah Lyons (*"Haste"*). Sem a tag,
   `ready_creatures` as tratava como tendo doença de invocação no turno
   em que entravam — Goldspan Dragon nunca disparava seu próprio
   "attacks: create Treasure" no turno de entrada; Sentinel Sarah Lyons
   nunca disparava seu Battalion (já implementado desde 2026-09-01) no
   turno de entrada.

**Grupo 2 — timing errado (mesma classe de bug documentada desde a
criação do arquivo pro Mahadi, replicada aqui em 2 cartas novas):**

5. **Laughing Jasper Flint — gatilho inteiro na fase ERRADA, 0% de valor
   gerado desde sempre.** Oráculo real: *"At the beginning of your
   upkeep, exile the top X cards of target opponent's library... Until
   end of turn, you may cast spells from among those cards..."* — estava
   implementado dentro de `end_step()` (fase que só roda DEPOIS das 2
   main phases do turno). Como `play_from_impulse()` só é chamado de
   dentro de `main_phase()`, as cartas exiladas no end_step nunca tinham
   janela nenhuma pra serem jogadas — a habilidade inteira produzia zero
   valor, só acumulava lixo em `impulse_pool`. Corrigido: movida pra
   `play_turn()`, na mesma posição de upkeep real já usada pelo Smaug the
   Magnificent (logo após o reset de flags do turno). `deadline_turns=0`
   continua correto nessa posição nova (a fase de upkeep é o INÍCIO do
   turno, então "until end of turn" cobre as 2 main phases inteiras
   deste mesmo turno).
6. **Urabrask's Forge — token criado DEPOIS do snapshot de atacantes do
   combate, nunca contava como atacante no próprio combate em que
   nascia, apesar de ter haste real impressa.** Oráculo real: *"At the
   beginning of combat on your turn, put an oil counter..., then create
   an X/1 red Phyrexian Horror creature token with trample and HASTE...
   Sacrifice that token at the beginning of the next end step."* O
   código antigo criava o token no FINAL de `combat_step()`, depois de
   `ready_other`/`total_attackers` já calculados — o token literalmente
   não podia contribuir pra nenhum gatilho de "criatura ataca" deste
   mesmo combate (Aya/Grenzo/Face-Breaker/Orochi/Olivia), e era
   sacrificado no `end_step()` sem nunca ter feito nada. Corrigido: movida
   pro TOPO de `combat_step()` (mesma posição de "beginning of combat" já
   usada pra animação de Treasures do Vihaan), com novo parâmetro
   `haste=True` em `create_other_tokens()` (não marca como
   summoning-sick). Bônus real da mesma correção: `state.forge_oil`
   nunca era lido em lugar nenhum além do próprio incremento — o X/1 real
   continua 📊 (P/T por criatura não é rastreado neste arquivo, mesma
   limitação estrutural de sempre), mas o token agora ao menos CONTA como
   1 atacante genérico pros gatilhos de combate, que é o mínimo que a
   contagem baseada em presença (não P/T) deste simulador consegue
   refletir. Também corrigido: se Anointed Procession dobra a criação
   (2 tokens em vez de 1), o `end_step()` antigo só sacrificava 1 sempre
   — novo campo `state.forge_tokens_this_turn` sacrifica a quantidade
   exata criada.

**Grupo 3 — gatilho "one or more" (lote) confundido com gatilho "a
creature"/"a historic creature" (por instância — 2 cartas onde o oráculo
NÃO usa a fórmula em lote que suas cartas-irmãs no mesmo deck usam):**

7. **Aya of Alexandria — achatado pra "1 token fixo se pelo menos 1
   criatura histórica atacar" em vez de 1 por criatura histórica.**
   Oráculo real: *"Whenever A HISTORIC creature you control deals combat
   damage to a player, create a...token"* — SEM "one or more" (ao
   contrário de Olivia/Professional Face-Breaker/Grim Hireling/Orochi
   Soul-Reaver, todas com "one or more...", corretamente já modeladas
   como 1 gatilho em lote). `any(is_historic(n) for n in
   ready_creatures)` virou `sum(...)` + Constructs + Treasures animados
   pelo Vihaan (ambos artefatos, ambos históricos).
8. **Grenzo, Havoc Raiser — mesma classe de bug.** Oráculo real:
   *"Whenever A creature you control deals combat damage to a
   player..."* — singular, sem "one or more". `pull_impulse(state, 1,
   ...)` virou `pull_impulse(state, total_attackers, ...)` (a contagem
   real já calculada no topo de `combat_step()`).

**Grupo 4 — habilidades reais 100% ausentes:**

9. **Magda, the Hoardmaster — 2ª habilidade real inteira ausente, só
   citada num comentário enganoso.** Oráculo real: *"Sacrifice three
   Treasures: Create a 4/4 red Scorpion Dragon creature token with flying
   and haste. Activate only as a sorcery."* — a linha 307 do arquivo
   (`other_tokens: int ... # criaturas token genericas (changeling,
   manifest, Scorpion Dragon...)`) sugeria que já estava coberta pelo
   contador genérico, mas nenhum código em lugar nenhum de fato
   sacrificava Treasures e criava o token. Só a 1ª habilidade ("whenever
   you commit a crime") estava implementada. Corrigido com um loop em
   `main_phase()` (sem {T} no custo real — repetível livremente enquanto
   sobrar Treasure, ao contrário de Jan Jansen que tem {T} e é capado a
   1x/turno corretamente).
10. **Professional Face-Breaker — 2ª habilidade real inteira ausente**
    (tag `impulse_treasure_sac` nunca lida). Oráculo real: *"Sacrifice a
    Treasure: Exile the top card of your library. You may play that card
    this turn."* Corrigido com `try_face_breaker_impulse()`, heurística
    conservadora de 1x/turno (mesmo padrão do Jan Jansen) pra não brigar
    demais pelo combustível de Treasure que Vihaan anima em combate.
11. **Agent of the Iron Throne — metade real da habilidade concedida
    ausente.** Oráculo real (Background): *"Commander creatures you own
    have 'Whenever an ARTIFACT OR CREATURE you control is put into a
    graveyard from the battlefield, each opponent loses 1 life.'"* — só
    a metade artefato (`on_artifact_dies`) estava coberta; a metade
    CRIATURA (provavelmente a mais comum das duas neste deck aristocrata
    cheio de sac outlets) nunca disparava. Corrigido em
    `on_creature_dies()`. Também corrigido, pra bater com "commander
    creatures you own": a habilidade só existe enquanto Vihaan
    (`state.commander_in_play`) estiver de fato em campo — faltava esse
    gate em AMBAS as metades (impacto prático baixo, já que Vihaan é
    sempre a 1ª coisa que `main_phase()` tenta conjurar, mas corrige o
    texto pro caso raro de mana nunca ter dado pro comandante).
12. **Extort (Life Insurance) — habilidade real 100% ausente**, tag
    presente no `CARD_DB` (`extort`), nunca lida. Oráculo real: *"Extort
    (Whenever you cast a spell, you may pay {W/B}. If you do, each
    opponent loses 1 life and you gain that much life.)"* Mesma
    convenção já usada em TODO drain/vida deste arquivo (Zulaport/Mayhem
    Devil/Nadier's Nightblade/etc): é um drain disparado pela SUA PRÓPRIA
    ação (conjurar uma mágica), não por um evento do oponente que
    precisaria ser simulado — modelável de verdade via `drain()`+
    `gain_life()`, diferente de efeitos genuinamente `opponent_dependent`
    que exigem um alvo/evento do oponente pra sequer acontecer. Corrigido
    em `cast_card()`, com snapshot do estado ANTES do próprio ETB (a
    própria Life Insurance não "paga extort" na sua própria conjuração —
    a habilidade só existe uma vez em campo). Não expandido pro caminho
    de `do_cascade()` (cascade via Rain of Riches não incrementa
    `spells_cast_this_turn`/não passa por `cast_card()` — limitação
    pré-existente, não introduzida nem agravada por esta correção,
    documentada como fora de escopo desta rodada por afetar também o
    Lotho e não ser o foco do achado).
13. **Sevinne's Reclamation — custo alternativo Flashback {4}{W}
    inteiramente ausente** (categoria (k) da campanha). Só o cast normal
    da mão estava implementado. Oráculo real completo: *"Return target
    permanent card with mana value 3 or less from your graveyard to the
    battlefield. If this spell was cast from a graveyard, you may copy
    this spell and may choose a new target for the copy. Flashback
    {4}{W}."* — uma ativação via flashback resolve DUAS vezes (original +
    cópia). Corrigido com `try_sevinne_flashback()`, mesma heurística de
    alvo (maior MV≤3, não-terreno) do cast normal; exila depois (não
    volta pro cemitério).
14. **The Reaver Cleaver — custo real Equip {3} nunca pago.** O bônus de
    combate (*"Whenever this creature deals combat damage..., create
    that many Treasure tokens"*, já modelado como proxy de +1 Treasure/
    combate — "that many" exigiria P/T por criatura, que este arquivo não
    rastreia, mesma limitação 📊 de sempre) disparava de graça em
    qualquer ataque, sem nunca ter sido equipado em ninguém. Corrigido
    com `try_equip_reaver_cleaver()` — paga Equip {3} uma vez (fica
    equipado o resto da partida — este simulador nunca reequipa),
    condicionado a ter pelo menos 1 criatura real em campo; o gatilho de
    combate agora exige `state.reaver_cleaver_equipped`.

**Grupo 5 — custo/escala real substituída por valor fixo/arbitrário:**

15. **Back in Town — MV real errado no `CARD_DB` (6 em vez de 3) + custo
    X nunca pago + cap arbitrário de X≤2.** Oráculo real (Scryfall):
    `{X}{2}{B}`, cmc=3 (X conta 0 pra CMC, regra padrão) — o custo fixo
    real é `{2}{B}`=3, não 6. `CARD_DB.mv` corrigido pra 3. O código
    antigo pagava só o (errado) custo fixo de 6 e nunca cobrava X mana
    nenhuma, capando arbitrariamente `X = min(2, remaining_mana)`.
    Corrigido: `X = min(outlaws reais no cemitério, mana que sobrou
    depois do custo fixo real)`, com `spend_mana(state, x)` de verdade —
    sem cap artificial.
16. **Lich-Knights' Conquest — fodder incompleto.** Oráculo real:
    *"Sacrifice any number of ARTIFACTS, ENCHANTMENTS, and/or TOKENS."*
    O código só contava Constructs+Food+Clue como fodder, ignorando
    Treasures e `other_tokens` — AMBOS são tokens de verdade (Treasure
    também é artefato), e Treasures são de longe o maior reservatório do
    deck inteiro (motor central, `TREASURE_MAXIMIZE_POLICY`). Corrigido:
    `fodder = treasures + constructs + other_tokens + foods + clues`,
    sacrificando na mesma ordem de prioridade já usada em Deadly Dispute
    (Treasure > Construct > other_tokens > Food/Clue), reusando
    `on_permanent_sacrificed()` pra Food/Clue (que não tinham função de
    sacrifício própria antes) — hub central continua sendo o único ponto
    de disparo de gatilhos de morte, nenhuma lógica duplicada.

### Verificações que confirmaram implementação correta (não eram gaps)

- **Requisition Raid (Spree)** — modelado como remoção genérica de custo
  base sem escolher modo, mesma convenção já usada pra Council's
  Judgment/outros removals multi-modo neste arquivo; o modo 3 ("+1/+1 em
  cada criatura que um jogador alvo controla", que PODERIA mirar o
  próprio jogador) exigiria P/T por criatura pra ter efeito numérico —
  estrutural, não um gap.
- **Exotic Orchard** — cor por fonte nunca é rastreada em NENHUM terreno
  deste arquivo (convenção já documentada pro Brightclimb Pathway); tratar
  como terreno genérico de 1 mana é consistente com o resto, não uma
  exceção.
- **Jan Jansen — as 2 habilidades de {T}** já estavam corretamente
  mapeadas (Treasure sacrificado = artefato NÃO-criatura → 2 Constructs;
  Construct sacrificado = artefato-criatura → 2 Treasures) e corretamente
  capadas a 1 ativação/turno (as 2 habilidades compartilham o mesmo {T}).
  Só faltavam as tags `haste`/`outlaw` corrigidas (grupo 1).
- **Sephiroth, Fabled SOLDIER // One-Winged Angel** — releitura completa
  do oráculo (front+back via Scryfall `card_faces`) confirmou que a
  implementação de 2026-08-31 já bate 100% clause-by-clause (emblem Super
  Nova independente da carta, sem cap de 4x/turno pós-transform, escala
  de sacrifício "any number" no ataque pós-transform).
- **Blasphemous Act / Blood Money** — excluem o próprio Vihaan do wipe
  (convenção implícita já consistente entre as duas cartas — sacrificar o
  próprio comandante junto com o resto do board num wipe autoinfligido
  não é uma jogada racional que nenhum piloto faria).

### Gaps considerados e deliberadamente NÃO alterados

- **Extort × `do_cascade()`** — cascade (Rain of Riches) não passa por
  `cast_card()`, então spells conjuradas via cascade não disparam Extort
  nem incrementam `spells_cast_this_turn` (afeta também o gatilho "2ª
  mágica do turno" do Lotho). Pré-existente, não introduzido nem agravado
  por esta rodada; documentado aqui pra rodadas futuras, fora de escopo
  desta (cascade só dispara em ≤1 mágica/turno, via `cascade_used_this_
  turn`, impacto baixo).
- **Food/Clue tokens sem habilidade própria ativável** (`{2}, Sac: gain 3
  life` / `{2}, Sac: draw a card`, texto de lembrete padrão desses tipos
  de token) — únicos criados via Academy Manufactor, nunca tinham
  nenhuma função de sacrifício antes desta rodada; agora só são
  sacrificáveis como fodder do Lich-Knights' Conquest (item 16). Dar a
  eles um sink genérico próprio (vida/draw) seria expandir escopo além
  de cartas realmente listadas na lista — mantido fora, mesmo padrão de
  "não inventar mecânica nova não pedida por uma carta real" já usado
  noutras rodadas desta campanha.

### Validação

- **Smoke test:** `CARD_DB` 94 entradas, `BASE_LIBRARY` 99 cartas (100%
  batendo com `lista.md`), 0 cartas desconhecidas, 0 duplicatas,
  comandante presente.
- **38 testes unitários isolados** (script dedicado), cobrindo cada uma
  das 16 correções individualmente — todos passando (outlaw/haste tags,
  anthem de haste do Vihaan propagado, timing do Laughing Jasper Flint e
  do Urabrask's Forge incl. duplicação via Anointed Procession, deadline
  off-by-one do Prosper/Inspired Tinkering, escala por-atacante da
  Aya/Grenzo, Magda/Face-Breaker/Extort/Sevinne flashback gerando valor,
  gate do Agent of the Iron Throne, MV+X real do Back in Town, fodder
  completo do Lich-Knights' Conquest, gate de Equip do Reaver Cleaver).
- **Antes/depois via `git stash`/`git stash pop`** (2.000 jogos, mesma
  seed 7500000, turns=8):

| Métrica | Antes | Depois |
|---|---|---|
| Avg Treasures em campo no fim | 2,60 | 2,06 |
| Avg Treasures sacrificados (total) | 4,83 | 5,37 |
| Avg outros tokens criados | 0,83 | 1,61 |
| Avg mortes de artefato | 5,05 | 5,57 |
| Avg drain/dano agregado (proxy) | 3,34 | 3,93 |
| Avg vida ganha | 1,09 | 1,33 |
| Avg combates com ≥1 atacante | 4,04 | 4,31 |
| Sephiroth transformado — % jogos | 0,6% | 0,7% |
| RECURSION avg/jogo | 0,13 | 0,14 |
| FINISHER Revel in Riches — % jogos | 0,1% | 0,2% |
| Avg Scorpion Dragons da Magda (novo) | — | 0,09 |
| Avg impulsos Face-Breaker (novo) | — | 0,37 |
| Avg Extort pago (novo) | — | 0,17 |
| Avg flashbacks Sevinne's (novo) | — | 0,01 |

  Todas as métricas se moveram na direção esperada (mais atacantes
  hasty/outlaw contando combates, mais sinks reais de Treasure/token
  drenando o pool mais rápido — daí Treasures em campo no fim caindo
  mesmo com mais sinks ativos —, mais drain/vida via Extort+Agent of the
  Iron Throne+escala real da Aya/Grenzo), nenhuma métrica explodiu, e as
  4 métricas novas confirmam que cada habilidade recém-implementada
  realmente dispara em jogos reais.
- **Regressão de 20.000 partidas** (seed 9500000+, turns=10): **0
  exceções**.

---

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge, Rat King, Thranduil, Ulalek e Ur-Dragon.

**Contexto importante:** este simulador já foi construído do zero
(2026-08-22) especificamente pra corrigir 5 problemas reais de um script
anterior de terceiros (mana nunca gasta de verdade, um combo fictício,
combate contra oponentes fictícios, sorteios de probabilidade em vez de
texto real, timing errado do Mahadi) — já nasceu com um padrão de rigor
alto. Mesmo assim, a releitura linha-a-linha desta rodada achou **3 gaps
reais**.

**Método:** detecção automatizada de 37 tags órfãs + nomes de carta com
poucas ocorrências. A esmagadora maioria eram falsos positivos — este
arquivo tem uma arquitetura de aristocratas MUITO centralizada
(`on_permanent_sacrificed()` → `on_creature_dies()`/`on_artifact_dies()`/
`on_token_leaves()`, chamada por toda via real de sacrifício), então
cartas com efeitos de morte/sacrifício raramente precisam de dispatch
próprio — aparecem "órfãs" na varredura textual mas estão corretamente
cobertas pelo hub central.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real, sem combate/P-T por criatura
  individual — limite conhecido, não julgamento de valor.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.

## 🐛 Os 3 gaps corrigidos nesta rodada

1. **High Market** (tag `sac_outlet_life`) — *"{T}, Sacrifice a creature:
   You gain 1 life."* 100% ausente — nem sequer citada fora do próprio
   `add()`.
2. **Phyrexian Tower** (tag `sac_outlet_bb`) — *"{T}, Sacrifice a
   creature: Add {B}{B}."* Mesma situação.
   Ambas corrigidas com `try_sac_land_outlets()`, chamada no início do
   `end_step()` (depois do combate, quando tokens do turno já atacaram e
   Constructs/other_tokens sobrando não têm mais uso pendente). Só
   sacrifica tokens descartáveis, nunca uma criatura nomeada real — dar
   um corpo de verdade por 1 vida ou 1 mana extra é claramente mau
   negócio, nenhum piloto racional faria isso. Reusa
   `sacrifice_constructs()`/`sacrifice_other_tokens()`, que já disparam
   TODOS os gatilhos reais de morte centralizados
   (`on_permanent_sacrificed()`) — Zulaport Cutthroat, Pitiless
   Plunderer, Mahadi (via `deaths_this_turn`), Sephiroth, Mayhem Devil —
   sem duplicar nenhuma lógica. Síntese bônus real: como isso roda ANTES
   do check da Witch of the Moors no mesmo `end_step()`, a vida ganha via
   High Market agora também satisfaz a condição "if you gained life this
   turn" dela em turnos que, de outra forma, não teriam ganho de vida.
3. **Sentinel Sarah Lyons** (tag `anthem_artifact`) — oráculo real tem 2
   habilidades: *"As long as an artifact entered the battlefield under
   your control this turn, creatures you control get +2/+2"* (estático
   numérico — 📊 genuíno, este arquivo não rastreia P/T por criatura em
   NENHUM outro lugar, consistente) e *"Battalion — Whenever Sentinel
   Sarah Lyons and at least two other creatures attack, she deals damage
   equal to the number of artifacts you control to target player"* (gatilho
   real e quantificável, mesma convenção de proxy de dano já usada pro
   Smaug the Magnificent — nunca implementado). Corrigido em
   `combat_step()`, com novo helper `artifacts_in_play()` (soma
   permanentes artifact/artifact_creature nomeados + Treasures +
   Constructs).

Validado com 9 testes unitários isolados + regressão de 20.000 partidas
(seed 8000000+, turns=10, 0 exceções) + `run_batch` antes/depois via
`importlib` (3000 jogos, seed 9000000, turns=10): drain/dano proxy
9.91→11.74, vida ganha 2.78→3.32, mana bônus via sac outlets 5.71→6.10.

## Achado verificado, não um gap (decisão de design já documentada)

O próprio docstring do cabeçalho já documentava, de forma transparente
(não uma omissão disfarçada), que **Grenzo, Havoc Raiser** e **Laughing
Jasper Flint** têm habilidades reais que exilam da biblioteca do
OPONENTE, mas usam a PRÓPRIA biblioteca como fonte substituta aproximada
(diferente da convenção "sem efeito numérico" usada pra Mari/Smothering
Tithe/Monologue Tax/Revel in Riches/Kellogg, todas no mesmo bloco de
"simplificações documentadas"). Essa inconsistência interna já estava
sinalizada no próprio texto do arquivo — não é uma descoberta desta
rodada, e como é uma decisão de design deliberada (não uma omissão
silenciosa) já revisada anteriormente, **não foi alterada** aqui pra
evitar uma regressão de comportamento não solicitada nesta passada.

## Demais cartas — confirmadas ✅ implementadas via dispatch centralizado

Verificação sistemática de todas as ~35 tags/nomes suspeitos restantes
confirmou dispatch real: `checkland_br/rw/wb` (genérico via
`CHECKLAND_TYPES`), `creature_death_drain`/`artifact_death_drain`/
`token_leave_drain`/`token_etb_drain`/`token_create_or_sac_drain`
(centralizados em `on_creature_dies()`/`on_artifact_dies()`/
`on_token_leaves()`), `death_drain_transform` (Sephiroth, lógica extensa
de emblem/transformação), `fabricate3`/`recursion_repeat`/`recursion_sac`/
`recursion_x`/`historic_combat_token`/`combat_impulse`/`upkeep_impulse`/
`impulse_end_step`/`lifegain_recursion`/`sac_damage`/`treasure_attack_damage`/
`forge_token`/`token_draw`/`alt_win` — todas com dispatch por nome
confirmado por leitura direta do código, não por contagem ingênua de
string. `gy_hate` (Bojuka Bog) e as 5 tags já auto-rotuladas `_unused`
(Kellogg, Dictate of Erebos, Boros Charm, Teferi's Protection, Grim
Hireling) confirmadas 📊 genuinamente estruturais via oráculo real
buscado no Scryfall (todas opponent-dependent ou combat-dependent sem
modelo).

---

## Resumo numérico

- **~95 cartas na lista** (`lista.md`).
- **🐛 Corrigido nesta rodada:** 3 cartas (High Market, Phyrexian Tower,
  Sentinel Sarah Lyons).
- **✅ Falsos positivos descartados:** ~34 tags/cartas, confirmadas
  corretamente implementadas via dispatch centralizado.
- **📊 Estrutural confirmado (verificado via Scryfall, não assumido):**
  Kellogg (roubo de criatura), Dictate of Erebos (edict), Boros Charm/
  Teferi's Protection (proteção sem ameaça real), Grim Hireling (-X/-X
  sem alvo), Bojuka Bog (graveyard hate sem oponente), anthem estático da
  Sentinel Sarah Lyons.
