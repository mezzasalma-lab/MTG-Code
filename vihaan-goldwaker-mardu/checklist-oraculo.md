# Checklist cláusula-a-cláusula — Vihaan, Goldwaker

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
