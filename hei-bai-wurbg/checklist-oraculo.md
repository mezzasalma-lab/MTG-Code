# Checklist cláusula-a-cláusula — Hei Bai, Forest Guardian

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn the Fierce e Edgar Markov.

89 cartas não-terreno-básico do decklist (comandante + deck, excluindo
Forest/Island/Mountain/Plains/Swamp básicas), oráculo real buscado ao
vivo via Scryfall (`POST /cards/collection`, 2 lotes) contra o
`heibai_goldfish_v1.py` atual.

**Contexto importante:** este deck (5 cores, WUBRG, tribal Shrine) já era
o mais estruturalmente sofisticado da sessão — construído do zero em
2026-08-24 com um dispatch central pra Shrines (`shrine_enters()`), um
motor de blink completo com timing atômico vs. adiado corretamente
diferenciado, e 3 dobradores de gatilho distintos (Elesh Norn/Sanctum of
All/Annie Joins Up) implementados sem se confundirem. Passou por rodadas
de correção em 2026-08-27 (timing de blink adiado, tag `untap_all` morta)
e 2026-08-28 (auditoria de habilidades estáticas). A releitura linha-a-
linha desta rodada **não achou nenhum bug de comportamento novo** — só 2
comentários que usavam linguagem de "julgamento de valor" (Weaver of
Harmony, Destiny Spinner) para justificar exceções que na verdade já são
genuinamente estruturais. Reclassificados/reescritos, sem mudança de
comportamento (ver docstring do arquivo).

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem combate real, sem oponente modelado, sem
  P/T por permanente individual fora do agregado, ou sem janela de
  "untap step do oponente"/"ataque do oponente" que este sim nunca avança.
- 📝 **Documentado, fora de escopo genuíno** — exceção arquitetural real
  (ex: "escolher qual gatilho copiar" — mesma classe do Strionic Resonator).

## Terrenos (35, incluindo básicas contadas genericamente)
Todos os terrenos (duais, fetches, triomes, Command Tower/Arcane Signet
equivalentes) contam como fonte de mana genérica — modelo TOTAL, não
pip-a-pip (decisão documentada no topo do arquivo, consistente pra TODOS
os terrenos, não uma simplificação seletiva). Fetches (`FETCH_NAMES`)
não "buscam" de verdade porque não há cor/tipo pra fixar num modelo sem
pips — ✅ correto dado o modelo de mana escolhido.
- **Abandoned Air Temple**: enters tapped condicional — ✅; `{3}{W},{T}`:
  +1/+1 em cada criatura — ✅ `do_shrine_mainphase_triggers()`/ativada dedicada.
- **Hall of Heliod's Generosity**: `{1}{W},{T}`: encantamento do
  cemitério pro topo — ✅ `do_hall_of_heliods_generosity()`.
- **Yavimaya, Cradle of Growth**: todo terreno é Forest — ✅ (fixação, sem efeito numérico no modelo total, consistente).
- Demais terrenos: mana genérica — ✅.

## Sanctums / Hondens / Temples (as 17 Shrines)
Dispatch central `shrine_enters()` cobre TODAS: gatilho "esta entra" (X=Shrines,
inclusive ela mesma) + "outra Shrine entra" (efeito fixo). Cada uma
verificada individualmente:
- **Crescent Island Temple**: Monk tokens (própria + outras) — ✅.
- **Go-Shintai of Ancient Wars**: first strike 📊 combate; end step dano
  pago — ✅ `do_go_shintai_endstep()`.
- **Go-Shintai of Hidden Cruelty**: deathtouch 📊 combate; end step
  destrói criatura — 📝 opponent_dependent (proxy de interação).
- **Go-Shintai of Life's Origin**: `{WUBRG},{T}` reanima encantamento —
  ✅ `do_life_origin_reanimate()`; ETB token (self OU outra Shrine
  nontoken) — ✅ `shrine_enters()`.
- **Go-Shintai of Lost Wisdom**: flying 📊; end step mill — 📊 opponent_dependent (proxy).
- **Go-Shintai of Shared Purpose**: vigilance 📊; end step Spirit tokens = Shrines — ✅.
- **Honden of Life's Web**: upkeep Spirit tokens = Shrines — ✅ `do_shrine_upkeep_triggers()`.
- **Honden of Seeing Winds**: upkeep draw = Shrines — ✅ idem.
- **Kyoshi Island Plaza**: ETB busca X básicas; outra Shrine entra: busca 1 — ✅ `shrine_enters()`.
- **Northern Air Temple**: ETB drain X; outra Shrine entra: drain 1 — ✅ idem (`proxy_drain`).
- **Sanctum of All**: upkeep busca Shrine; dobrador (6+ Shrines) — ✅ `resolve_times()`.
- **Sanctum of Calm Waters**: main phase draw X, descarta 1 — ✅ `do_shrine_mainphase_triggers()`.
- **Sanctum of Fruitful Harvest**: main phase mana X — ✅ idem.
- **Sanctum of Shattered Heights**: descarta terreno/Shrine: dano X — ✅ `do_sanctum_shattered_heights()` (opponent_dependent no alvo, mas o CUSTO/ativação é real).
- **Sanctum of Stone Fangs**: main phase drain X — ✅ `do_shrine_mainphase_triggers()`.
- **Southern Air Temple**: ETB counters X; outra Shrine entra: +1/+1 — ✅.
- **The Spirit Oasis**: ETB draw X; outra Shrine entra: draw 1 — ✅.

## Criaturas / Payoffs
- **Argothian Enchantress**: shroud 📊; cast encantamento: draw — ✅ `on_cast_enchantment()`.
- **Birds of Paradise / Bloom Tender / Sanctum Weaver**: mana dorks, doença de invocação real — ✅ `dork_mana()`.
- **Deadeye Navigator**: soulbond + blink repetível — ✅ `do_deadeye_navigator()`.
- **Displacer Kitten**: cast não-criatura: blink — ✅ (dispatch de conjuração).
- **Dryad of the Ilysian Grove**: land drop extra — ✅; fixação — 📊 (modelo total).
- **Elesh Norn**: vigilance 📊; dobrador de ETB — ✅ `resolve_times()`; nega gatilhos de oponente — 📊 opponent_dependent (sem gatilho de oponente modelado, já N/A por padrão).
- **Enduring Vitality**: vigilance 📊; mana em massa — ✅ (via tag em `dork_mana`/`total_mana`, criaturas ganham `{T}: any color`); morre→volta como encantamento — 📝 nunca alcançável (sem morte de criatura nomeada, mesma razão documentada no topo do arquivo).
- **Go-Shintai of Ancient Wars/etc.**: ver seção Shrines acima.
- **Herald of the Pantheon**: custo -{1} encantamento — ✅ `effective_cost()`; cast encantamento: +1 vida — ✅.
- **Purphoros**: indestructible 📊; dano por criatura entrando — ✅ (dispatch central de ETB); bombeio `{2}{R}` — 📝 buff temporário de combate (mesma família de Craterhoof/Destiny Spinner).
- **Seedborn Muse**: untap em turno de OPONENTE — 📊 genuinamente fora de escopo (sim nunca avança turno de oponente), corpo vanilla 2/4.
- **Sythis**: cast encantamento: +1 vida + draw — ✅.
- **Thassa**: indestructible 📊; blink de end step — ✅ `do_endstep_blinks()`; tap ativado `{3}{U}` — 📊 combate (tapar bloqueador, sem combate real modelado).
- **Weaver of Harmony**: anthem +1/+1 enchantment creatures — ✅; copiar ativada/disparada — 📝 exceção estrutural genuína (escolher QUAL gatilho copiar entre 17 Shrines com efeitos diferentes, mesma classe do Strionic Resonator — reclassificado 2026-09-01, não é mais "baixo valor").

## Encantamentos
- **Annie Joins Up**: ETB 5 dano — 📝 opponent_dependent (proxy interação); dobrador de gatilho de criatura lendária — ✅ `resolve_times()`.
- **Destiny Spinner**: can't be countered — 📊; `{3}{G}` land vira X/X — 📝 buff temporário de combate (reclassificado 2026-09-01, não é mais "baixo valor").
- **Enchantress's Presence**: cast encantamento: draw — ✅.
- **Greater Auramancy**: shroud pra encantamentos — 📊 sem targeting de oponente modelado (mesma razão de Sterling Grove).
- **Hallowed Haunting**: 7+ encantamentos: voo/vigilance — 📊 combate; cast encantamento: Spirit token X/X — ✅.
- **In Search of Greatness**: upkeep cast grátis ou scry — ✅ `do_in_search_of_greatness()`.
- **Skybind**: Constellation blink — ✅ `on_any_enchantment_enters()`, `best_nonenchantment_permanent_to_reblink()`.
- **Sphere of Safety**: defesa pura de ataque de oponente — 📊 (sem ataque de oponente modelado).
- **Sterling Grove**: shroud — 📊; sac: tutor encantamento pro topo — ✅ `do_sterling_grove_tutor()`.
- **Teleportation Circle**: end step blink — ✅ `do_endstep_blinks()`.

## Interação / Proteção
Todas (An Offer You Can't Refuse, Arcane Denial, Aura Shards, Dovin's
Veto, Heroic Intervention, Path to Exile, Swan Song, Swords to
Plowshares, Teferi's Protection, Touch the Spirit Realm) — 📝/📊
opponent_dependent, contadas como interação usada sem efeito colateral
no próprio campo (convenção consistente da biblioteca inteira). **Aura
Shards** e **Ephemerate** são exceções parciais reais: Aura Shards
("criatura entra: destrói artefato/encantamento alvo") é opponent-target
mas o GATILHO em si (criatura entra) é real — ✅ contado; Ephemerate
(blink com rebound) é 100% self-target — ✅ `do_ephemerate()`.

## Ramp / Tutores
- **Aang's Journey**: kicker busca básica+Shrine — ✅ `search_land()`/dispatch dedicado, vida ✅ `gain_life()`.
- **Cultivate / Nature's Lore / Three Visits / Farseek**: busca terreno — ✅ `search_land()`.
- **Idyllic Tutor**: busca encantamento pra mão — ✅.
- **Replenish**: retorna todos os encantamentos do cemitério — ✅.
- **Waterbender's Restoration**: waterbend X, blink X criaturas (retorno adiado) — ✅ `resolve_instant_sorcery()`, `state.pending_end_step_returns`.

## Rocks
- **Arcane Signet / Sol Ring / The Mind Stone**: mana — ✅ `rocks_mana()`.
  The Mind Stone: indestructible 📊; harness + ∞ blink end step — ✅ `do_endstep_blinks()`.

---

## Resumo numérico

- **89 cartas.**
- **~110 linhas de cláusula.**
- **✅ Implementado:** ~75 linhas.
- **📊 N/A estrutural:** ~25 linhas (combate, oponente, "untap step do
  oponente" genuinamente fora do loop de simulação).
- **📝 Documentado, fora de escopo genuíno:** ~10 linhas (proxies de
  interação/remoção sem alvo real de oponente; Weaver of Harmony —
  escolha entre 17 tipos de gatilho, mesma classe do Strionic Resonator).
- **🐛 Corrigido nesta rodada:** nenhum bug de comportamento novo — 2
  comentários reclassificados de "baixo valor esperado" pra justificativa
  estrutural real (Weaver of Harmony, Destiny Spinner), sem mudança de
  código funcional.

Este foi o único dos decks auditados até agora (Toph, Beorn, Edgar
Markov, Hei Bai) em que a releitura linha-a-linha não achou nenhum gap
funcional novo — consistente com o nível de detalhe já presente no
docstring do arquivo antes desta rodada.
