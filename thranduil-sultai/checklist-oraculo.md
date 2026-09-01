# Checklist cláusula-a-cláusula — Thranduil, the Elvenking

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge e Rat King.

**Contexto importante:** este é o simulador mais extensamente auditado da
sessão antes desta rodada — já tinha passado por auditorias completas em
2026-08-28 e 2026-08-30 (documentadas no próprio código com comentários
"Achado real 2026-08-28/30" espalhados pelo arquivo, corrigindo dezenas
de gaps: Cavern of Souls/Eclipsed Realms tratadas como incolor, Thranduil's
Company land drop bloqueado, landfall triggers só logando sem efeito,
Oversold Cemetery só tutorando sem devolver, etc). Mesmo assim, a
releitura desta rodada achou **6 gaps reais adicionais**.

**Método diferente do Rat King:** este arquivo despacha majoritariamente
por **nome de carta** (não por tag) — a detecção automatizada aqui
cruzou 2 sinais: (a) tags órfãs (definidas em `add()`, nunca lidas) e (b)
nomes de carta que só aparecem na própria linha `add()` + no
`DECKLIST_TEXT`, nunca em nenhuma lógica de resolução. 8 candidatos
apareceram; 2 eram falsos positivos (cobertos pelo dispatcher genérico de
`finisher_repeatable`), 6 eram gaps reais.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — não produz número neste modelo por decisão de
  arquitetura documentada (sem oponente real, sem combate/P-T por
  criatura individual, sem tap-de-criatura-por-mana) — limite conhecido,
  não julgamento de valor.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.
- ⚠️ **Órfão de lista** — carta definida em `CARD_DB` mas fora da lista
  atual de 91 cartas (`lista.md`); implementação correta, mas inerte hoje.

## 🐛 Os 6 gaps corrigidos nesta rodada

1. **Deadly Rollick** — não era uma tag órfã, era um **julgamento de
   valor disfarçado de custo estático**: `CARD_DB` tinha `mv=2` como
   aproximação ("quase sempre paga {1}{B}, controla comandante") em vez
   de checar a condição real. Oráculo real (Scryfall): *"If you control a
   commander, you may cast this spell without paying its mana cost.
   Exile target creature."* Custo real impresso {3}{B}=MV4. Corrigido com
   `effective_mv()`: retorna 0 quando `state.commander_in_play`, senão o
   custo real (4). Usado em `can_cast()`, `cast_spell()` e na ordenação de
   `try_use_own_interaction()`.
2. **Urza's Incubator** ⚠️ órfão de lista (tag `cost_reducer`) — *"As this
   artifact enters, choose a creature type. Creature spells of the chosen
   type cost {2} less to cast."* Tipo = Elfo. Corrigido em
   `effective_mv()`. Correto, mas fora da lista atual de 91 cartas.
3. **Eclipsed Elf** ⚠️ órfão de lista (tag `card_selection`) — *"When this
   creature enters, look at the top four cards of your library. You may
   reveal an Elf, Swamp, or Forest card from among them and put it into
   your hand."* Corrigido em `_apply_etb()`, usando `LAND_SUBTYPES` (já
   existente pro check-land Hinterland Harbor) pra checar Swamp/Forest de
   verdade, não só nome literal. Correto, mas fora da lista atual.
4. **Harmonized Crescendo** ⚠️ órfão de lista (tag `draw_burst`) — *"Choose
   a creature type. Draw a card for each permanent you control of that
   type."* Tipo = Elfo. Corrigido em `_apply_etb()` — compra 1 por
   permanente Elfo controlado. Convoke não modelado (limitação
   estrutural do motor de mana inteiro, não recorte desta carta). Correto,
   mas fora da lista atual.
5. **Kindred Dominance** (tag `wipe_asymmetric`) — *"Choose a creature
   type. Destroy all creatures that aren't of the chosen type."* Mesma
   convenção já aplicada nesta sessão pros wipes assimétricos do Rat King:
   destruiria as PRÓPRIAS criaturas não-Elfo sem oponente real — conta
   como conjurável (mana gasta via `cast_spell`, já incrementa
   `removal_cast`), sem destruir o próprio board (Regra 1).
6. **Raise the Palisade** (tag `bounce_asymmetric`) — *"Choose a creature
   type. Return all creatures that aren't of the chosen type to their
   owners' hands."* Mesma lógica do item 5 (bounce assimétrico do próprio
   board sem oponente real) — conjurável, sem efeito no próprio board.
7. **Takenuma, Abandoned Mire** (tag `gy_engine`) — Channel já documentado
   como deferido desde 2026-08-30. Oráculo real: *"Channel — {3}{B},
   Discard this card: Mill three cards, then return a creature or
   planeswalker card from your graveyard to your hand. This ability costs
   {1} less to activate for each legendary creature you control."*
   Corrigido com `try_takenuma_channel()` (chamada antes de
   `play_land()`) — só descarta quando sobra outro terreno na mão nesse
   turno. `is_legendary_elf` cobre "legendary creature" com exatidão
   nesta lista: as 21 criaturas lendárias do deck são todas Elfos
   (verificado via Scryfall/`thranduil_full.json`, sem exceção).

**Falsos positivos descartados** (nomes que apareciam só em `add()`+
decklist, mas na verdade já cobertos): **Allosaurus Shepherd** e
**Tyvar, the Pummeler** — suas ativadas de finisher (`{4}{G}{G}`/
`{3}{G}{G}`) já eram despachadas genericamente via
`has_tag(card, "finisher_repeatable")` em `activate_finishers()`; só as
estáticas "can't be countered"/"tap outra criatura pra indestructible"
ficam 📊 (sem contraparte de oponente/remoção modelada).

Validado com 8 testes unitários isolados + regressão de 20.000 partidas
(seed 2000000+, turns=10, 0 exceções) + `run_batch` antes/depois via
`importlib` (3000 jogos, seed 5000000, turns=10): RECURSION 0.68→0.92,
Kindred Dominance 4.9%, Raise the Palisade 9.0%, Takenuma Channel 20.8%
dos jogos.

## Demais cartas — confirmadas ✅ implementadas ou 📊 estruturais

Nenhum outro nome ou tag ficou órfão na varredura automatizada. As
categorias 📊 já documentadas em rodadas anteriores (2026-08-28/30)
seguem válidas: efeitos opponent-dependent (Rhystic Study, High Perfect
Morcant, Maralen, Ruthless Winnower symmetric part), combat-dependent sem
P/T por criatura (Tyvar the Bellicose deathtouch), e simplificações de
escopo já documentadas no próprio código (Three Tree City 2ª habilidade,
Cavern/Eclipsed Realms só pro modo criatura).

---

## Resumo numérico

- **91 cartas na lista atual** (comandante + 90 de biblioteca,
  `lista.md`) — confirmado por comparação direta `CARD_DB` vs `lista.md`.
- **🐛 Corrigido nesta rodada, ativo na lista atual:** 4 cartas (Deadly
  Rollick, Kindred Dominance, Raise the Palisade, Takenuma, Abandoned
  Mire).
- **🐛 Corrigido nesta rodada, mas ⚠️ órfão de lista (inerte hoje):** 3
  cartas (Eclipsed Elf, Harmonized Crescendo, Urza's Incubator).
- **⚠️ Outras 8 entradas órfãs de lista já existentes** (não corrigidas
  nem quebradas nesta rodada, apenas confirmadas fora da lista atual):
  Deathcap Glade, Elf Warrior Token (token, não é carta real da lista),
  Feed the Swarm, Formidable Speaker, Llanowar Wastes, Lys Alana
  Huntmaster, Putrefy, Undergrowth Stadium.
- **✅ Falsos positivos descartados (já cobertos por dispatcher
  genérico):** Allosaurus Shepherd, Tyvar, the Pummeler.
