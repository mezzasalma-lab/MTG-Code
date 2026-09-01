# Checklist cláusula-a-cláusula — Beorn the Fierce

Pedido direto do usuário (2026-09-01), o mesmo trabalho já feito pro Toph
agora exigido pra **todos os decks**: *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA COMO EU
MANDEI DESDE O COMEÇO"* — seguido de: *"cada carta tem que ser lida
linha a linha e isso tudo incorporado aos modelos que já fizemos até
agora"*.

Este arquivo quebra as 69 cartas não-terreno-básico da lista (comandante +
deck, excluindo as 31 Forest) em cláusulas individuais — uma por
frase/parágrafo do oráculo real, buscado ao vivo via Scryfall
(`POST /cards/collection` + `/cards/named?fuzzy=` pros 2 MDFC/Adventure) —
e marca o status de cada uma contra o `beorn_goldfish_v1.py` atual,
verificado por leitura/grep do arquivo, não por recordação.

**Contexto importante:** diferente do Toph (que partiu de um estado
pouco auditado), este deck já tinha passado por **duas rodadas de
auditoria anteriores** (2026-08-30 e 2026-08-31, documentadas no próprio
docstring do arquivo e em `goldfish-log.md`) que corrigiram vários gaps
reais (Eternal Witness, Natural Order, Lumra, Nykthos, War Room, Chameleon
Colossus, Beorn's Hospitality, etc — ver comentários "achado real
2026-08-30/31" espalhados pelo código). Mesmo assim, a releitura
linha-a-linha desta rodada achou **7 gaps reais adicionais** que as
rodadas anteriores tinham deixado passar — provando que "já foi auditado
antes" não é garantia de completude, exatamente o padrão que motivou o
pedido do usuário.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — não produz número neste modelo por decisão de
  arquitetura documentada (sem P/T por criatura individual, sem combate
  real, sem oponente) — limite conhecido do simulador, não julgamento de
  valor.
- 📝 **Documentado, fora de escopo** — decisão explícita por motivo
  genuinamente estrutural.
- 🐛 **Corrigido nesta rodada (2026-09-01)** — gap real que as auditorias
  anteriores (2026-08-30/31) tinham deixado passar.

## 🐛 Os 7 gaps corrigidos nesta rodada

1. **Selvala, Heart of the Wilds** — mana ability real é `{G}, {T}: Add X
   mana in any combination of colors, where X is the greatest power among
   creatures you control`. Estava caindo no tratamento genérico de "dork
   de 1 mana" (mesma categoria de Llanowar Elves) — subestimava
   MUITO o valor real (X escala com counters/anthems, facilmente 4-12+
   nesse deck). Corrigido em `total_mana()`: `max(0, greatest_power_in_play(state) - 1)`.
2. **Return of the Wildspeaker** — fórmula errada: estava conflada com a
   de Shamanic Revelation ("draw por criatura"), mas o oráculo real é
   "draw cards equal to the **greatest power** among **non-Human**
   creatures you control" — filtro de tipo E fórmula diferentes. Corrigido
   em `cast_spell()` com novo helper `is_human()`.
3. **Obscuring Haze** — "If you control a commander, you may cast this
   spell **without paying its mana cost**." Alt-cost grátis nunca
   modelado — o sim cobrava sempre o custo impresso. Corrigido em
   `effective_cost()`/`can_cast()`.
4. **Lightning Greaves** — Equip {0} nunca era ativado em lugar nenhum;
   o haste que ela concede de graça nunca beneficiava nenhuma criatura.
   Corrigido: `try_lightning_greaves_equip()`, novo campo
   `lightning_greaves_equipped_to`, `can_attack()` atualizado.
5. **Allosaurus Shepherd** — `{4}{G}{G}: each Elf creature... 5/5
   Dinosaur` 100% ausente (só as estáticas "can't be countered" estavam
   modeladas). Corrigido: `try_allosaurus_shepherd_pump()` (mesmo
   tratamento do Chameleon Colossus: métrica de ativação, buff temporário
   não propagado pra BASE_POWER).
6. **Chronicle of Victory / Patchwork Banner** — os anthems reais
   ("+2/+2 tipo escolhido" e "+1/+1 tipo escolhido") nunca tinham efeito
   de poder modelado — só o anthem da própria Beorn era somado, e só
   localmente dentro de `on_creature_enters` (nunca propagado pro resto
   do arquivo). Corrigido: novo helper `effective_power()`, usado
   consistentemente em `on_creature_enters`, `total_power_in_play()`,
   `greatest_power_in_play()` e no desconto de custo do Goreclaw.
7. **Roaming Throne** só dobrava o gatilho de combate da Beorn — mas
   Ayula, Queen Among Bears é ela mesma um Bear, e seu próprio gatilho de
   ETB ("whenever another Bear enters") também deveria dobrar sob Roaming
   Throne. Corrigido em `on_creature_enters()`.

Validado com 7 testes unitários isolados (1 por gap) + regressão de
20.000 partidas (0 erros) + `run_batch` n=3000 antes/depois (ver
`goldfish-log.md` pros números completos).

---

## Allosaurus Shepherd {G}
1. This spell can't be countered — 📊 opponent_dependent (sem counterspell de oponente modelado).
2. Green spells you control can't be countered — 📊 idem.
3. `{4}{G}{G}`: cada Elfo vira 5/5 Dinossauro até o fim do turno — 🐛 `try_allosaurus_shepherd_pump()`, ativa com 2+ Elfos em campo.

## Ambush Viper {1}{G}
1. Flash — 📊 sem instant-speed real modelado (só conjura na main phase).
2. Deathtouch — 📊 combate.

## Archdruid's Charm {G}{G}{G}
1. Modo tutor (criatura/terreno pra mão/campo) — ✅ `cast_spell()`, único modo sem alvo de oponente.
2. Modo +1/+1 counter + fight — 📝 opponent_dependent (fight exige criatura do oponente).
3. Modo exile artefato/encantamento — 📝 opponent_dependent.

## Ayula's Influence {G}{G}{G}
1. Discard terreno: cria Bear 2/2 — ✅ `try_ayula_influence()`.

## Ayula, Queen Among Bears {1}{G}
1. Outro Bear entra: 2 contadores OU fight — ✅ `on_creature_enters()` (modo contadores, fight é opponent_dependent 📝). 🐛 Roaming Throne agora dobra esse gatilho corretamente (Ayula é ela mesma um Bear).

## Bala Ged Recovery // Bala Ged Sanctuary
1. Face sorcery: retorna carta do cemitério — ✅ `try_bala_ged_recovery()`.
2. Face terreno: enters tapped, `{T}`: Add G — ✅ `play_land()` + genérico.

## Beast Whisperer {2}{G}{G}
1. Cast creature spell: draw — ✅ `on_spell_cast_effects()`.

## Beast Within {2}{G}
1. Destroy target permanent — ✅ tag "removal", `try_use_own_interaction()`.
2. Controlador cria Beast 3/3 — 📊 é o OPONENTE que recebe o token (efeito do oponente, não nosso).

## Beorn the Fierce (comandante) {3}{G}{G}
1. Trample — 📊 combate.
2. Other Bears +2/+2 — ✅ `effective_power()` (🐛 corrigido: antes só local em on_creature_enters, não propagado pro resto do arquivo).
3. Início de combate: trample counter + vira Bear + 3+ Bears→draw 2 — ✅ `combat_step()`.

## Beorn's Hospitality {1}{G}
1. Landfall: +1/+1 counter em criatura alvo — ✅ `on_land_enters()`.
2. `{5}{G}{G}`: vira criatura Bear P/T=terrenos — ✅ `try_beorns_hospitality_animate()`.

## Beorn, Reluctant Host // Till and Tend
1. Trample (face criatura) — 📊 combate.
2. Till and Tend: land drop extra — ✅ `try_till_and_tend()`.
3. Cast da criatura do exílio depois — ✅ `try_cast_beorn_host_from_exile()`.

## Birds of Paradise {G}
1. Flying — 📊 combate.
2. `{T}`: Add any color — ✅ genérico (ramp/green_source_any).

## Boseiju, Who Endures
1. `{T}`: Add G — ✅ genérico.
2. Channel: destrói artefato/encantamento/terreno não-básico do oponente — 📝 opponent_dependent.

## Chameleon Colossus {2}{G}{G}
1. Changeling — ✅ `is_bear()` conta via tag "changeling".
2. Protection from black — 📊 combate/oponente.
3. `{2}{G}{G}`: +X/+X (X=próprio poder) até o fim do turno — ✅ `try_chameleon_colossus_pump()` (métrica de ativação, buff temporário não propagado).

## Chronicle of Victory {6}
1. Tipo escolhido (Bear, convenção do arquivo) — ✅ `is_bear()`.
2. Criaturas do tipo escolhido +2/+2, first strike, trample — 🐛 `effective_power()` (first strike/trample são 📊 combate, +2/+2 agora real).
3. Cast spell do tipo escolhido: draw — ✅ `on_spell_cast_effects()`.

## Craterhoof Behemoth {5}{G}{G}{G}
1. Haste — 📊 combate.
2. ETB: trample + X/+X pro time (X=criaturas) — 📊 buff temporário até o fim do turno, mesma família de efeitos de combate não rastreados por criatura individual (documentado, contado como finisher via tag).

## Cultivate {2}{G}
1. Busca 2 básicas, 1 campo tapped + 1 mão — ✅ `cast_spell()`.

## Dancing from Dark to Dawn {3}{G}{G}
1. Cast creature spell: X contadores (X=mv) — ✅ `on_spell_cast_effects()`.
2. Landfall: cria Bear 2/2 — ✅ `on_land_enters()`.

## Defiler of Vigor {3}{G}{G}
1. Trample — 📊 combate.
2. Custo alternativo (pagar 2 vida, spells verdes custam {G} menos) — ✅ `effective_cost()` (vida não rastreada, sempre assume que paga — documentado).
3. Cast green permanent spell: +1/+1 em cada criatura — ✅ `on_spell_cast_effects()`.

## Emerald Medallion {2}
1. Spells verdes custam {1} menos — ✅ `effective_cost()`.

## Eternal Witness {1}{G}{G}
1. ETB: retorna carta do cemitério pra mão — ✅ `cast_spell()`.

## Ezuri's Predation {5}{G}{G}{G}
1. Cria token 4/4 por criatura do oponente + fight — 📝 opponent_dependent (tag "mass_removal", excluída de `try_use_own_interaction`).

## Firdoch Core {3}
1. Changeling — ✅ `is_bear()`.
2. `{T}`: Add any color — ✅ genérico (ramp/green_source_any).
3. `{4}`: vira 4/4 artefato-criatura até o fim do turno — 📝 buff temporário, sem P/T por criatura individual (documentado desde 2026-08-30).

## Forgotten Ancient {3}{G}
1. Player casts spell: pode por +1/+1 counter — ✅ `on_spell_cast_effects()` (próprios casts) + `play_turn()` (aproximação de 2 casts de oponentes/turno).
2. Upkeep: move contadores entre criaturas — 📊 sem efeito no modelo agregado (counters_on_board é um total, mover entre criaturas não muda a soma).

## Garruk's Uprising {2}{G}
1. ETB: se poder>=4 em campo, draw — ✅ `cast_spell()`.
2. Criaturas têm trample — 📊 combate.
3. Criatura poder>=4 entra: draw — ✅ `on_creature_enters()`.

## Genji Glove {5}
1. Equipped: double strike — 📊 combate.
2. Ataca (1º combate): untap + combate extra — ✅ `combat_step()` + equip em `main_phase()`.
3. Equip {3} — ✅ `main_phase()`.

## Germination Practicum {3}{G}{G}
1. 2 contadores em cada criatura — ✅ `cast_spell()`.
2. Paradigm (recast grátis do exílio) — ✅ `main_phase()`.

## Ghalta, Primal Hunger {10}{G}{G}
1. Custo reduzido por poder total em campo — ✅ `effective_cost()`.
2. Trample — 📊 combate.

## Gigantic Big Bear {5}{G}{G}
1. Can't be countered — 📊 opponent_dependent.
2. Hexproof, haste — 📊 combate/oponente (haste não precisa de dispatch, é vanilla stats).

## Goreclaw, Terror of Qal Sisma {3}{G}
1. Creature spells poder>=4 custam {2} menos — ✅ `effective_cost()` (🐛 agora usa `effective_power()`, considerando anthems).
2. Ataca: criaturas poder>=4 +1/+1 e trample até o fim do turno — 📝 buff temporário de combate, mesma família de Craterhoof/Unnatural Growth (documentado nesta rodada — antes não tinha nenhum comentário explicando a ausência).

## Haywire Mite {1}
1. Morre: ganha 2 vida — 📊 vida não rastreada neste modelo (mono-verde, documentado no header do arquivo).
2. `{G}`, Sac: exile artefato/encantamento não-criatura — 📝 sem restrição de "do oponente" no oráculo, mas sem alvo próprio valioso (Regra 1) nem alvo de oponente modelado — excluída explicitamente de `try_use_own_interaction` (comentário na linha ~1506).

## Heroic Intervention {1}{G}
1. Permanentes ganham hexproof/indestructible até o fim do turno — 📊 proteção reativa, sem remoção de oponente modelada pra proteger contra.

## Last March of the Ents {6}{G}{G}
1. Can't be countered — 📊 opponent_dependent.
2. Draw = maior toughness + coloca criaturas da mão em campo — ✅ `cast_spell()`.

## Lightning Greaves {2}
1. Haste + shroud — 🐛 `try_lightning_greaves_equip()` + `can_attack()` (shroud continua 📊, sem remoção de oponente modelada).
2. Equip {0} — ✅ idem (reativa todo turno, sem {T} no custo).

## Little Bear {2}{G}
1. Flash — 📊 sem instant-speed modelado.
2. ETB: untap outra criatura + se for Bear, +1/+1 counter — ✅ `cast_spell()` (untap sem efeito modelável, documentado; contador real).

## Llanowar Elves {G}
1. `{T}`: Add G — ✅ genérico.

## Lotus Cobra {1}{G}
1. Landfall: Add any color — ✅ `on_land_enters()`.

## Lumra, Bellow of the Woods {4}{G}{G}
1. Reach, vigilance — 📊 combate.
2. P/T = terrenos controlados — 📊 sem P/T por criatura rastreado (não afeta os thresholds deste deck, que usam BASE_POWER fixo).
3. ETB: mill 4, retorna terrenos do cemitério pro campo tapped — ✅ `cast_spell()`.

## Managorger Hydra {2}{G}
1. Trample — 📊 combate.
2. Player casts spell: +1/+1 counter — ✅ `cast_spell()` (próprios) + `play_turn()` (aproximação de oponentes + premissa de "morre" por remoção depois de ~4 turnos).

## Maskwood Nexus {4}
1. Suas criaturas são todo tipo de criatura — ✅ `is_bear()`, `is_human()`.
2. `{3}, {T}`: cria Shapeshifter 2/2 changeling — ✅ `try_maskwood_nexus()`.

## Natural Order {2}{G}{G}
1. Custo adicional: sacrifica criatura verde — ✅ `can_cast()` (gate) + `cast_spell()` (sacrifício real).
2. Busca criatura verde pro campo — ✅ `cast_spell()`.

## Necklace of Girion {2}{G}
1. Cast spell verde OU Forest entra: +1/+1 counter em criatura alvo — ✅ `on_spell_cast_effects()` + `on_land_enters()`.
2. `{T}`: Add G — ✅ genérico (green_source).

## Nykthos, Shrine to Nyx
1. `{T}`: Add C — ✅ genérico.
2. `{2}, {T}`: Add mana = devoção à cor escolhida — ✅ `try_nykthos()`.

## Obscuring Haze {2}{G}
1. Se controla comandante, pode conjurar de graça — 🐛 `effective_cost()`/`can_cast()`.
2. Previne todo dano de criaturas do oponente — 📊 sem combate/dano de oponente modelado.

## Ohran Frostfang {3}{G}{G}
1. Criaturas atacantes têm deathtouch — 📊 combate.
2. Criatura causa dano de combate a jogador: draw — ✅ `combat_step()`.

## Patchwork Banner {3}
1. Tipo escolhido (Bear, mesma convenção de Chronicle/Roaming Throne) — ✅ `is_bear()`.
2. Criaturas do tipo +1/+1 — 🐛 `effective_power()` (antes: zero efeito de poder modelado).
3. `{T}`: Add any color — ✅ genérico (ramp/green_source_any).

## Radagast of Rhosgobel {2}{G}{G}
1. 1º creature spell do turno custa {2} menos — ✅ `effective_cost()`.
2. ...e pode ser conjurado com flash — 📝 sem instant-speed/janela de turno adversário modelada (documentado).

## Ram Through {1}{G}
1. Criatura sua causa dano = seu poder numa criatura do oponente (excesso c/ trample vai na cara) — ✅ tag "removal", `try_use_own_interaction()` (efeito numérico exato do combate é 📊, mas a conjuração conta como interação real).

## Reliquary Tower
1. Sem tamanho máximo de mão — ✅ `cleanup_hand_size()`.
2. `{T}`: Add C — ✅ genérico.

## Return of the Wildspeaker {4}{G}
1. Draw = maior poder entre criaturas não-Humanas — 🐛 `cast_spell()` (fórmula corrigida, era conflada com Shamanic Revelation).
2. Modo alternativo: +3/+3 não-Humanas até o fim do turno — 📝 buff temporário de combate (mesma família de Craterhoof).

## Roaming Throne {4}
1. Ward {2} — 📊 opponent_dependent.
2. Tipo escolhido (Bear) — ✅ `roaming_throne_active()`.
3. Gatilho de OUTRA criatura do tipo escolhido dispara 2x — ✅ `combat_step()` (Beorn) + `on_creature_enters()` (Ayula, 🐛 corrigido nesta rodada — antes só a Beorn dobrava).

## Scavenger Grounds
1. `{T}`: Add C — ✅ genérico.
2. `{2}, {T}, Sac Desert`: exile todos os cemitérios — 📝 opponent_dependent (exilar o PRÓPRIO cemitério é estritamente ruim pra esse deck sem alvo de oponente que valha, Regra 1).

## Selvala, Heart of the Wilds {1}{G}{G}
1. Outra criatura entra com poder maior que todas as outras: draw — ✅ `on_creature_enters()` (`max_power_seen`).
2. `{G}, {T}`: Add X mana (X=maior poder em campo) — 🐛 `total_mana()` (era tratada como dork genérico de 1 mana, agora usa `greatest_power_in_play()`).

## Shamanic Revelation {3}{G}{G}
1. Draw = número de criaturas controladas — ✅ `cast_spell()`.
2. Ferocious: ganha 4 vida por criatura poder>=4 — 📊 vida não rastreada neste modelo.

## Sol Ring {1}
1. `{T}`: Add CC — ✅ genérico (caso especial em `total_mana()`).

## Solemn Simulacrum {4}
1. ETB: busca básica pro campo tapped — ✅ `cast_spell()`.
2. Morre: pode draw — 📝 sem morte/remoção modelada pra esse corpo especificamente (nunca "morre" nesse sim, só fica em campo — consistente com o resto do arquivo, que não modela remoção de oponente).

## Song of the Dryads {2}{G}
1. Encantada vira Forest incolor — ✅ tag "removal", `try_use_own_interaction()`.

## Springleaf Parade {X}{G}{G}
1. ETB: cria X tokens Shapeshifter 1/1 changeling — ✅ `cast_spell()` (X=1, convenção do arquivo pra custo {X}).
2. Tokens-criatura têm `{T}: Add any color` — ✅ `total_mana()`/`green_sources()` (vale pra qualquer token-criatura, não só o próprio).

## The Great Henge {7}{G}{G}
1. Custo reduzido pelo maior poder em campo — ✅ `effective_cost()`.
2. `{T}`: Add GG, ganha 2 vida — ✅ `total_mana()` (vida 📊 não rastreada).
3. Criatura não-token entra: +1/+1 counter + draw — ✅ `on_creature_enters()`.

## Thought Vessel {2}
1. Sem tamanho máximo de mão — ✅ `cleanup_hand_size()`.
2. `{T}`: Add C — ✅ genérico.

## Three Visits {1}{G}
1. Busca Forest pro campo — ✅ `cast_spell()`.

## Tireless Provisioner {2}{G}
1. Landfall: Food ou Treasure — ✅ `on_land_enters()` (sempre Treasure, cracka na hora).

## Tireless Tracker {2}{G}
1. Landfall: investigate (Clue) — ✅ `on_land_enters()`.
2. Sacrifica Clue: +1/+1 counter — ✅ `try_crack_clues()`.

## Titania's Command {4}{G}{G}
1. Exile cemitério de um jogador + ganha vida — 📝 opponent_dependent, não escolhido pela heurística (vida 📊).
2. Busca até 2 terrenos tapped — ✅ `cast_spell()` (modo escolhido).
3. Cria 2 Bears 2/2 — ✅ `cast_spell()` (modo escolhido).
4. 2 contadores em cada criatura — 📝 modo não escolhido pela heurística (só busca terreno + Bears).

## Toski, Bearer of Secrets {3}{G}
1. Can't be countered — 📊 opponent_dependent.
2. Indestructible — 📊 combate/oponente.
3. Ataca todo combate se puder — 📊 já assumido implicitamente (toda criatura apta ataca).
4. Criatura causa dano de combate a jogador: draw — ✅ `combat_step()`.

## Tribute to the World Tree {G}{G}{G}
1. Criatura entra: draw se poder>=3, senão 2 contadores — ✅ `on_creature_enters()`.

## Unnatural Growth {1}{G}{G}{G}{G}
1. Início de cada combate: dobra poder/toughness até o fim do turno — 📝 buff temporário de combate, mesma família de Craterhoof/Goreclaw (contado como finisher via tag, sem número exato).

## War Room
1. `{T}`: Add C — ✅ genérico.
2. `{3}, {T}, pague vida=cores da identidade`: draw — ✅ `try_war_room()` (vida 📊 não rastreada, custo de mana real).

## Yavimaya, Cradle of Growth
1. Todo terreno é Forest adicionalmente — ✅ `is_forest_for_landfall()`, `green_sources()`.

---

## Resumo numérico

- **69 cartas** (comandante + 68 do deck, excluindo as 31 Forest básicas).
- **~120 linhas de cláusula** cobertas nesta tabela.
- **✅ Implementado:** ~85 linhas.
- **📊 N/A estrutural:** ~24 linhas (combate, vida não rastreada, oponente).
- **📝 Documentado, fora de escopo:** ~11 linhas (buffs temporários de
  combate não rastreados por criatura, modos de spell não escolhidos pela
  heurística, opponent_dependent sem alvo modelável).
- **🐛 Corrigido nesta rodada (2026-09-01):** Selvala (mana real),
  Return of the Wildspeaker (fórmula), Obscuring Haze (custo alternativo
  grátis), Lightning Greaves (nunca equipada), Allosaurus Shepherd (pump
  100% ausente), Chronicle of Victory/Patchwork Banner (anthems sem
  efeito de poder), Roaming Throne (só dobrava a Beorn, não a Ayula).

Nenhuma cláusula ficou sem uma linha nesta tabela. Se algo aqui estiver
errado, o local citado (`nome_da_funcao()`) é onde conferir.
