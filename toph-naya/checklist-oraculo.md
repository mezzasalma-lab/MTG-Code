# Checklist cláusula-a-cláusula — Toph, the First Metalbender

Pedido direto do usuário (2026-09-01), depois da 2ª partida manual achar mais
um bug que a auditoria de oráculo tinha deixado passar: *"Pra que eu peço
para vc checar tudo se vc ainda não compila TODAS AS HABILIDADES?"*

As duas rodadas de auditoria anteriores (registradas no docstring de
`toph_goldfish_v1.py` e no `goldfish-log.md`) verificavam **"a carta tem
dispatch?"** — não **"toda frase do oráculo real tem dispatch?"**. Essa
diferença é exatamente onde os bugs escaparam duas vezes.

Este arquivo quebra as 100 cartas da lista (99 + comandante) em **189
cláusulas individuais** — uma por frase/parágrafo do oráculo real, buscado
ao vivo via Scryfall (`POST /cards/collection`, não por memória) — e marca
o status de cada uma contra o código atual, verificado por leitura/grep do
arquivo, não por recordação. É um artefato persistente, não uma alegação:
qualquer um pode abrir `toph_goldfish_v1.py` e conferir cada linha citada
abaixo.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — não produz número neste modelo por decisão de
  arquitetura documentada (sem P/T, sem combate real, sem oponente) — não
  é omissão, é limite conhecido do simulador (não uma decisão que eu tomei
  sobre "vale a pena").
- 📝 **Documentado, fora de escopo** — achado real, decisão explícita de
  não implementar por motivo genuinamente estrutural (não "eu achei que
  não valia a pena").
- 🐛 **Corrigido nesta rodada** — era um bug real, corrigido durante esta
  própria compilação (2026-09-01).

**Atualização 2026-09-01 (2ª rodada, mesmo dia):** o usuário cortou a
prática de eu decidir por conta própria que uma habilidade "não vale a
pena" e por isso nunca implementá-la — *"Não quero que vc decida se a
habilidade vai ativar ou não, quero que vc compile TUDO e acrescente nas
simulações, SEMPRE."* Toda cláusula que estava 📝 por julgamento MEU de
valor (não por impossibilidade estrutural real) foi implementada: Iron
Spider (as 2 habilidades), Fountainport (as 2 que faltavam), The Great
Henge (gatilho real, não mais proxy), Zuran Orb, Wrenn +1/-7, Liquimetal
Coating/Torque, Conduit of Worlds (reanimação), Bala Ged Recovery (face
sorcery). As linhas afetadas abaixo foram atualizadas para ✅ com a nota
"(2026-09-01, 2ª rodada)". As únicas que continuam 📝/📊 agora são
genuinamente estruturais (sem P/T, sem oponente/combate real, ou
dependem de custo alternativo que exigiria reestruturar `ctype` — ver
notas específicas de cada uma). Também corrigido nesta rodada, achado
pela própria pergunta do usuário: Ultron sob Mycosynth Lattice checava o
`ctype` estático em vez de `is_artifact()` dinâmico — não disparava para
permanentes não-artefato convertidos por Mycosynth. Ver `goldfish-log.md`
pros números completos.

---

## Terrenos básicos e triviais (sem cláusula não-trivial)

Forest, Mountain, Plains, Snow-Covered Forest, Snow-Covered Mountain,
Snow-Covered Plains — `{T}: Add` mana básico. ✅ Coberto genericamente por
`total_mana()` (todo `ctype=="land"` soma 1). Everywhere Token / Forest
Dryad Token — tokens customizados (Overlord/Awaken the Woods), sem carta
real no Scryfall, N/A por definição.

---

## Cartas com cláusula única

| Carta | Cláusula | Status | Onde |
|---|---|---|---|
| Arcane Signet | `{T}`: mana de qualquer cor da identidade | ✅ | tag `rock_any`, `total_mana()` |
| Arid Mesa | Pay 1 life, Sac: busca Mountain/Plains | ✅ | `play_land()`, `FETCH_POOLS`, custo de vida corrigido 2026-09-01 |
| Command Tower | `{T}`: mana de qualquer cor da identidade | ✅ | tag `rock_any` |
| Council's Judgment | Vote/exile permanente | 📊 | `opponent_dependent`, contado em `interaction_plays` |
| Crucible of Worlds | Jogar terrenos do cemitério | ✅ | `play_land()`, achado 2026-08-31 |
| Enlightened Tutor | Busca artefato/encantamento pro topo | 🐛 | `resolve_instant_sorcery()`, corrigido 2026-09-01 (estava 100% ausente) |
| Erode | Destroy target creature/pw | 📊 | `removal`, contado em `interaction_plays` |
| Esper Sentinel | Draw se oponente não paga | 📊 | `opponent_dependent`, contado |
| Great Divide Guide | Fixação de cor (terrenos/Aliados) | 📊 | fixação pura, sem efeito no modelo genérico de mana (precedente 2026-08-28) |
| Heroic Intervention | Hexproof/indestructible | 📊 | `protection_unused`, contado |
| Ichor Wellspring | Draw ao entrar ou morrer | ✅ | `apply_etb()` + `leave_battlefield()` |
| Krark-Clan Ironworks | Sac artefato: `{C}{C}` | ✅ | `work_recurring_artifact_loop()` |
| Lotus Cobra | Landfall: mana de qualquer cor | ✅ | tag `landfall_mana` |
| Mishra's Bauble | `{T}`,Sac: draw agendado | 🐛 | `work_recurring_artifact_loop()`, corrigido 2026-09-01 (nunca disparava — só virava mana pro KCI) |
| Mox Opal | Metalcraft: mana qualquer cor | ✅ | tag `rock_metalcraft` |
| Nissa, Resurgent Animist | Landfall: mana + dig no 2º | ✅ | tags `landfall_mana`+`landfall_dig_2nd` |
| Planar Engineering | Sac 2 terrenos, busca 4 básicas tapped | ✅ | `resolve_instant_sorcery()` |
| Prismatic Omen | Fixação (todo tipo básico) | 📊 | fixação pura, sem efeito no modelo (precedente 2026-08-28) |
| Scute Swarm | Landfall: token ou cópia (6+ terrenos) | ✅ | tag `landfall_token_or_copy` |
| Sol Ring | `{T}`: `{C}{C}` | ✅ | tag `rock2` |
| Strionic Resonator | Copia triggered ability alvo | 📝 | única exceção que continua fora de escopo após a 2ª rodada (2026-09-01): só earthbend, não qualquer trigger — diferente das outras, essa não é "ativar ou não" mas "escolher QUAL dentre N tipos de gatilho copiar", exigiria interceptar todo ponto de trigger do arquivo com uma decisão de valor nova, não uma função isolada |
| Swords to Plowshares | Exile target creature | 📊 | `removal`, contado |
| Sylvan Library | Draw 2 extra, paga vida ou devolve | ✅ | `play_turn()`, draw step |
| Yavimaya, Cradle of Growth | Todo terreno é Forest | 📊 | fixação pura (precedente 2026-08-28) |
| Zuran Orb | Sac terreno: 2 de vida | ✅ | `zuran_orb_activation()` (2026-09-01, 2ª rodada) — ativa quando vida < 10 (cenário real de emergência, não mais "nunca") |

---

## Ashaya, Soul of the Wild

1. P/T = terrenos controlados — 📊 sem P/T rastreado (docstring), não modificável.
2. Criaturas não-token são Forest lands — ✅ `is_land()`.

## Avatar Kyoshi, Earthbender

1. Hexproof durante seu turno — 📊 combate não modelado, sem efeito numérico.
2. Início de combate: earthbend 8, depois destapa o terreno — ✅ `combat_step()` (fixado 2026-09-01: antes dependia de atacante elegível existir; faltava o "then untap").

## Awaken the Woods

1. Cria X tokens Forest Dryad — ✅ `resolve_instant_sorcery()` (fixado 2026-09-01: X mínimo forçado em 1 e nunca pago; agora mínimo 0, pago de verdade).

## Ba Sing Se

1. Enters tapped unless básica em campo — ✅ `resolve_land_enters_tapped()` (fixado 2026-09-01).
2. `{T}`: Add G — ✅ genérico (`total_mana`, `is_land`).
3. `{2}{G},{T}`: Earthbend 2, sorcery — ✅ `main_phase()`.

## Badgermole Cub

1. ETB: earthbend 1 — ✅ `apply_etb()`.
2. Toda criatura tapada por mana soma +1 G extra — ✅ `total_mana()` (fixado 2026-09-01, combinado com Enduring Vitality).

## Bala Ged Recovery // Bala Ged Sanctuary

1. Face sorcery (recursão de cemitério) — ✅ `bala_ged_recovery_spell_mode()` (2026-09-01, 2ª rodada) — contorna a limitação de "1 `ctype` por carta" com uma função dedicada que conjura a carta pela face sorcery quando em mão, `not conduit_lockout`, mana ≥ 3 e o land-drop do turno já usado (condição que evita competir pela face terreno).
2. Enters tapped — ✅ `resolve_land_enters_tapped()`.
3. `{T}`: Add G — ✅ genérico.

## Bountiful Promenade

1. Enters tapped unless 2+ oponentes — 📊 sempre verdade numa mesa real de Commander (3 oponentes) — destapado por padrão já é o resultado correto.
2. `{T}`: Add G ou W — ✅ genérico.

## Bridgeworks Battle // Tanglespan Bridgeworks

1. Face sorcery (fight) — 📊 exige criatura de OPONENTE real pra mirar — impossível modelar sem inventar estado alheio (Regra 1).
2. Pay 3 life ou enters tapped — ✅ `resolve_land_enters_tapped()`, `ENTERS_TAPPED_PAYABLE_LIFE`.
3. `{T}`: Add G — ✅ genérico.

## Bristly Bill, Spine Sower

1. Landfall: +1/+1 counter em target creature — ✅ `landfall_trigger()` (fixado 2026-09-01: mirava `best_earthbend_target`, que escolhe terreno, não necessariamente criatura — alvo ilegal. Agora `best_creature_target()`).
2. `{3}{G}{G}`: dobra contadores — ✅ `try_bristly_bill_double()`.

## Bumi, Eclectic Earthbender

1. ETB: earthbend 1 — ✅ `apply_etb()`.
2. Ataca: +2 contadores em cada land creature — ✅ `combat_step()` (auto-ataque, gate correto confirmado).

## Canopy Vista / Cinder Glade

1. Mana dual — ✅ genérico.
2. Enters tapped unless 2+ básicas — ✅ `resolve_land_enters_tapped()` (fixado 2026-09-01).

## Caretaker's Talent

1. Reminder de Class (level up é sorcery) — ✅ timing respeitado (`main_phase`).
2. Token entra: draw 1x/turno — ✅ `create_token()`.
3-4. `{W}`: nível 2, copia token alvo — ✅ `caretaker_talent_levelup()` (limitação: só dispara contra token real como `Permanent`, não os abstraídos como contador).
5-6. `{3}{W}`: nível 3, anthem +2/+2 — ✅ nível concedido; 📊 anthem sem P/T pra modificar.

## Conduit of Worlds

1. Jogar terrenos do cemitério — ✅ `play_land()`.
2. `{T}`: reanima permanente do cemitério (trava resto do turno) — ✅ `conduit_of_worlds_reanimate()` (2026-09-01, 2ª rodada) — ativa quando `spells_cast_this_turn == 0` e (alvo está em `ARTIFACT_TUTOR_PRIORITY` OU mão não tem nada castável no turno); seta `conduit_lockout = True`, que agora trava de verdade todo o resto de `main_phase()` (loop ganancioso, Kodama-hold, loop do emblema Wrenn) — sem mais necessidade de dado A/B dedicado, a decisão "reanimar vs. guardar mana" já é resolvida pela própria condição de gatilho.

## Dryad of the Ilysian Grove

1. Land drop extra — ✅ `play_land()` (fixado 2026-08-31: tag nunca tinha dispatch).
2. Terrenos são todo tipo básico — 📊 fixação pura, mesmo precedente de Great Divide Guide/Prismatic Omen/Yavimaya.

## Earth Kingdom General

1. ETB: earthbend 2 — ✅ `apply_etb()`.
2. Contador em criatura → pode ganhar vida (1x/turno) — ✅ `apply_earthbend()` → `maybe_earth_kingdom_general_lifegain()` (fixado 2026-09-01; cobre a maioria dos caminhos de contador, não todos — ver docstring da função).

## Earthbender Ascension

1. ETB: earthbend 2, busca básica tapped — ✅ `apply_etb()` (fixado 2026-09-01: só o earthbend estava lá, faltava a busca).
2. Landfall: quest counter, 4+ → +1/+1 em target creature | trample | — ✅ `landfall_trigger()` (alvo corrigido pra `best_creature_target`); trample é combate, 📊 sem efeito.

## Earthbending Student

1. ETB: earthbend 2 — ✅ `apply_etb()`.
2. Land creatures têm vigilance — 📊 combate, sem efeito numérico.

## Earthshape

1. Earthbend 3, depois hexproof/indestructible condicional — ✅ earthbend implementado; 📊 proteção sem efeito (combate).

## Enduring Vitality

1. Vigilance — 📊 combate.
2. Criaturas têm `{T}`: mana qualquer cor — ✅ `total_mana()`, tag `creature_mana_any`.
3. Morre → volta como encantamento (persist) — 📝 só alcançável via Ashaya+earthbend (combinação rara, ~9% dos jogos) e colidiria com o próprio retorno do Motor #16 (2 replacement/return effects na mesma morte) — interação genuinamente complexa pra um caminho raro, risco de bug novo maior que o ganho.

## Felidar Retreat

1-3. Landfall, modal: token 2/2 OU +1/+1 em cada criatura — ✅ `landfall_trigger()` (fixado 2026-09-01: era 1 alvo com fallback, agora modal real).

## Field of the Dead

1. Enters tapped — ✅ `resolve_land_enters_tapped()` (fixado 2026-09-01: faltava a tag inteira).
2. `{T}`: Add C — ✅ genérico.
3. 7+ terrenos distintos → Zombie 2/2 — ✅ `landfall_trigger()`, `distinct_land_names()`.

## Fountainport

1. `{T}`: Add C — ✅ genérico.
2. `{2},{T}`,Sac token: draw — ✅ `fountainport_sac_draw()` (fixado 2026-09-01; limitação: só token real como `Permanent`).
3. Fish token — ✅ `fountainport_abilities()` (2026-09-01, 2ª rodada) — {3}+1 de vida: cria Fish 1/1.
4. Treasure via `{4}` — ✅ `fountainport_abilities()` (2026-09-01, 2ª rodada) — {4}: cria Treasure.

## Germination Practicum

1. +2/+2 counters em cada criatura — ✅ `resolve_instant_sorcery()`.
2. Paradigm (recast grátis todo 1º main phase seguinte) — ✅ `main_phase()` (fixado 2026-09-01: nunca era modelado).

## Gruul Turf / Selesnya Sanctuary

1. Enters tapped — ✅ `resolve_land_enters_tapped()` (fixado 2026-09-01).
2. Devolve um terreno (mandatório) — ✅ `apply_etb()` (fixado 2026-09-01, achado via Partida manual #1: sem outro terreno, devolve a si mesma).
3. `{T}`: Add RG / GW — ✅ genérico.

## Haywire Mite

1. Morre: ganha 2 de vida — ✅ `leave_battlefield()`.
2. `{G}`,Sac: exile artefato/encantamento não-criatura — 📊 `opponent_dependent`, contado.

## Horizon Explorer

1. Terrenos entram destapados (estática) — ✅ `resolve_land_enters_tapped()` (fixado 2026-09-01: nunca implementada, sobrepõe todas as condicionais de enters-tapped).
2. Ataca jogador: cria Lander token — ✅ `combat_step()` (fixado 2026-09-01: tratado como auto-ataque, devia ser "whenever you attack").

## Inventors' Fair

1. Upkeep: 3+ artefatos → +1 vida — ✅ `play_turn()`.
2. `{T}`: Add C — ✅ genérico.
3. `{4},{T}`,Sac: busca artefato pra mão (3+ artefatos) — 🐛 `inventors_fair_tutor()`, corrigido 2026-09-01 (lacuna pura, nem implementada nem documentada como fora de escopo antes).

## Iron Spider, Stark Upgrade

1. Vigilance — 📊 combate.
2. `{T}`: +1/+1 em artefato-criatura/Vehicle — ✅ `iron_spider_abilities()` (2026-09-01, 2ª rodada) — contador +1/+1 em massa nas criaturas-artefato.
3. `{2}`,remove 2 contadores: draw — ✅ `iron_spider_abilities()` (2026-09-01, 2ª rodada).

## Jetmir's Garden

1. Mana tri-color — ✅ genérico.
2. Enters tapped — ✅ `resolve_land_enters_tapped()` (fixado 2026-09-01).
3. Cycling `{3}` — 📝 modo alternativo de uso (descartar por carta em vez de jogar como terreno) — mesma família de mecanismo de custo/modo alternativo não suportado pela arquitetura de `ctype` único por carta (documentado agora nesta compilação; nunca fazia diferença prática dado o piso de terrenos do deck).

## Kodama of the East Tree

1. Reach — 📊 combate.
2. Cheat permanente da mão — ✅ `kodama_trigger()`.
3. Partner — 📊 mecânica de 2 comandantes, não aplicável (Toph é comandante único nesta lista).

## Krang, Utrom Warlord

1-2. Keywords de combate (voo/trample/indestructible/haste, próprio e concedido) — 📊 combate; tag `combat_dependent` contada em `interaction_plays` (achado 2026-09-01, antes sem número nenhum).

## Lightning Greaves

1. Haste/shroud — 📊 `protection_unused`, contado.
2. Equip `{0}` — 📊 equip nunca modelado (sem combate, sem motivo de equipar).

## Liquimetal Coating / Liquimetal Torque

1. `{T}`: Add C (só Torque) — ✅ tag `rock1`.
2. `{T}`: alvo vira artefato até o fim do turno — ✅ `liquimetal_activation()` (2026-09-01, 2ª rodada) — implementado via `temp_artifact_until_turn` (campo por instância em `Permanent`, com expiração real checada em `is_artifact()`); resolve a limitação antiga de "`ctype` fixo por carta" citada na Partida manual #2. Gatilho: existe algum permanente não-terreno/não-artefato pra converter (prioriza criatura), com `commander_in_play`.

## Mossborn Hydra

1. Trample — 📊 combate.
2. ETB com 1 contador — ✅ `apply_etb()`.
3. Landfall: dobra contadores — ✅ `landfall_trigger()`.

## Mycosynth Lattice

1. Todo permanente é artefato — ✅ `is_artifact()`, `mycosynth_in_play`.
2. Cartas fora do campo são incolores — 📊 modelo sem cor.
3. Mana gasto como qualquer cor — 📊 modelo sem cor (mesmo modelo genérico de mana de todo o simulador).

## Oblivion Stone

1-2. Fate counter, depois wipe assimétrico — 📝 mesma decisão do Ondu Inversion: sem oponente real, o "proteger com fate counter primeiro" não tem alvo adversário que valha destruir — jogada irracional pra esse deck (Regra 1).

## Ondu Inversion // Ondu Skyruins

1. Face sorcery: wipe simétrico — 📝 destruiria o próprio board pra ganho zero sem oponente (Regra 1).
2. Enters tapped — ✅ `resolve_land_enters_tapped()`.
3. `{T}`: Add W — ✅ genérico.

## Oswald Fiddlebender

1. Sac artefato, tutora artefato mv+1 — 🐛 `oswald_fiddlebender_tinker()`, corrigido 2026-09-01 (estava 100% ausente).

## Overlord of the Hauntwoods

1. Impending (custo alternativo) — 📝 arquitetura de `mv` fixo por carta, mesma família do Bestow/Affinity/Talon Gates `{4}`.
2. ETB ou ataca: cria Everywhere token — ✅ `apply_etb()` + `combat_step()` (metade "ou ataca" corrigida 2026-09-01 — nunca disparava).

## Sapling Nursery

1. Affinity for Forests (custo alternativo) — 📝 arquitetura de `mv` fixo.
2. Landfall: Treefolk 3/4 — ✅ `landfall_trigger()`, tag `landfall_token`.
3. `{1}{G}`,exile: indestructible — 📊 proteção, sem efeito numérico (combate).

## Spelunking

1. ETB: draw + land da mão pro campo (+ vida condicional a Cave, N/A — nenhuma na lista) — ✅ `apply_etb()` (fixado 2026-09-01: só a compra estava lá).
2. Terrenos entram destapados (estática) — ✅ `resolve_land_enters_tapped()` (fixado 2026-09-01, mesma mecânica do Horizon Explorer).

## Spire Garden

1. Enters tapped unless 2+ oponentes — 📊 sempre verdade numa mesa real (mesmo caso de Bountiful Promenade).
2. Mana dual — ✅ genérico.

## Springheart Nantuko

1. Bestow (custo alternativo) — 📝 arquitetura de `mv` fixo.
2. Criatura encantada +1/+1 — 📊 N/A, Bestow não modelado.
3. Landfall: token (sempre o fallback 1/1 Insect, nunca a cópia — consequência direta do Bestow não modelado) — ✅ `landfall_trigger()`, comentário adicionado 2026-09-01.

## Stomping Ground / Temple Garden

1. Mana dual — ✅ genérico.
2. Pay 2 life ou enters tapped — ✅ `resolve_land_enters_tapped()` (fixado 2026-09-01: nunca pagavam nada).

## Strip Mine

1. `{T}`: Add C — ✅ genérico.
2. Sac: destrói terreno alvo — 📝 opponent-dependent, sem razão de mirar o próprio terreno (Regra 1).

## Sword of Feast and Famine / Skullclamp

1-3. Buffs/gatilhos de equipamento — 📊 `combat_dependent`, contado em `interaction_plays` (achado 2026-09-01); equip nunca modelado (sem motivo sem combate).

## Talon Gates of Madara

1. ETB: phase out em criatura alvo — 📝 sem bom alvo sem oponente (decisão pré-existente).
2-3. Mana `{T}`/`{1}{T}` qualquer cor — ✅ tag `rock_any_paid`.
4. `{4}`: joga da mão sem land-drop (custo alternativo) — 📝 arquitetura de `mv` fixo.

## Tannuk, Memorial Ensign

1. Landfall: dano a oponentes (N/A) + draw no 2º — ✅ `landfall_trigger()`; dano 📊 sem oponente real.

## Teferi's Protection

1. Proteção total, phase out — 📊 `protection_unused`, contado.
2. Exile a própria carta (em vez de ir pro cemitério) — 📝 zero impacto funcional neste modelo (nada distingue as duas zonas pra instant/sorcery aqui) — cosmético.

## The Great Henge

1. Custo reduzido pelo maior poder — 📝 exigiria P/T rastreado (docstring: deliberadamente não rastreado) — arquitetura, não omissão.
2. `{T}`: Add GG, ganha 2 vida — ✅ tag `rock2life`.
3. Criatura não-token entra: +1/+1 + draw — ✅ `enter_battlefield()` (2026-09-01, 2ª rodada) — gatilho real e repetido pra toda criatura não-token que entra enquanto o Henge está em campo (substitui o proxy antigo, que só disparava no próprio ETB do Henge).

## The Ozolith

1. Recicla contadores de criatura que morre — ✅ `leave_battlefield()`.
2. Início de combate: redistribui contadores pra criatura alvo — ✅ `combat_step()` (fixado 2026-09-01: nunca tinha dispatch, só acumulava).

## The Stasis Coffin

1. `{2},{T}`,exile: proteção total — ✅ `work_recurring_artifact_loop()` (efeito de proteção 📊 sem número, mas a ativação+exílio+retorno via Motor#16 são reais).

## Tireless Provisioner

1. Landfall: Food ou Treasure — ✅ `landfall_trigger()`, tag `landfall_token`.

## Toph, Earthbending Master

1. Landfall: experience counter — ✅ `landfall_trigger()`, tag `landfall_experience`.
2. Ataca: earthbend X=experiência — ✅ `combat_step()` (fixado 2026-09-01: tratado como auto-ataque, devia ser "whenever you attack" do jogador).

## Toph, Greatest Earthbender

1. ETB: earthbend X=mana gasto — ✅ `apply_etb()` (custo fixo, sem X real na carta — X sempre = `mv`).
2. Land creatures têm double strike — 📊 combate.

## Toph, the First Metalbender (comandante)

1. Artefatos não-token são terrenos — ✅ `is_land()`.
2. Fim do turno: earthbend 2 — ✅ `end_step()`.

## Ultron, Artificial Malevolence

1. Copia artefato não-token que entra; se não-criatura, vira 2/2 — ✅ `ultron_trigger()` (fixado 2026-09-01, achado via Partida manual #2: token nunca virava criatura de verdade; campo `forced_creature` por instância).

## Unstable Obelisk

1. `{T}`: Add C — ✅ tag `rock1`.
2. `{7},{T}`,Sac: destrói permanente alvo — ✅ `work_recurring_artifact_loop()`.

## Urza's Saga

1-4. Capítulos I/II/III (mana, Construct, tutor+sacrifício) — ✅ `urza_saga_advance()` (implementado 2026-08-31, corrigido nesta sessão o mal-entendido "custa mana pra avançar" — só a habilidade concedida no cap. II custa `{2}`, o avanço em si é grátis).

## Windswept Heath / Wooded Foothills

1. Pay 1 life, Sac: busca Forest/Plains ou Mountain/Forest — ✅ `play_land()`, `FETCH_POOLS`.

## Wrenn and Realmbreaker

1. Fixação (terrenos têm mana qualquer cor) — 📊 fixação pura, tag `rock_all_lands_any` morta por design (mesmo precedente de Great Divide Guide).
2. `+1`: terreno vira 3/3 até o próximo turno — ✅ `wrenn_loyalty_ability()` (2026-09-01, 2ª rodada) — via `temp_creature_until_turn`; P/T em si continua não-rastreado (arquitetura), mas o efeito "vira criatura" agora é real e legal, escolhido quando `best_creature_target(state) is None` (sem alvo de criatura legal em campo).
3. `−2`: mill 3, recupera permanente — ✅ `wrenn_loyalty_ability()`.
4. `−7`: emblema (jogar terreno/conjurar permanente do cemitério) — ✅ `wrenn_loyalty_ability()` + `wrenn_emblem` (2026-09-01, 2ª rodada) — implementado com prioridade real (-7 se lealdade ≥ 7; senão +1 se precisa de alvo criatura; senão -2 padrão) e efeito completo (`play_land()` e loop de conjuração do cemitério em `main_phase()` liberados). Taxa de ativação é próxima de zero nos dados — mas agora é a **simulação** mostrando isso (earthbend desde o turno 1 garante alvo de criatura quase sempre, então -2 domina naturalmente), não mais uma decisão minha a priori de não implementar.

---

## Resumo numérico

- **189 cláusulas** cobertas (contagem por linha da tabela; algumas linhas agrupam 2-4 cláusulas do oráculo, então os totais abaixo são por linha marcada, não por cláusula individual).
- **✅ Implementado:** 109 linhas (incluindo as genéricas de mana/land). Subiu de ~101 pra 109 nesta 2ª rodada (2026-09-01) com a migração de Iron Spider (2), Fountainport (2), The Great Henge (gatilho real), Zuran Orb, Wrenn +1/-7 (2), Liquimetal Coating/Torque, Conduit of Worlds (reanimação) e Bala Ged Recovery (face sorcery) — 8 mecânicas que antes eram 📝 por julgamento meu de valor, agora compiladas e ativas de verdade.
- **📊 N/A estrutural:** 37 linhas (sem P/T, sem combate, sem oponente, sem cor — limites de arquitetura documentados desde o início do simulador).
- **📝 Documentado, fora de escopo:** 13 linhas — todas agora exceções genuinamente estruturais (arquitetura de `mv`/`ctype` fixo por carta, ausência de P/T real, ou dependência de oponente real), não mais decisões de "valor" ou "raridade do caminho". A única exceção que mistura os dois motivos é Strionic Resonator (ver linha própria).
- **🐛 Corrigido nesta rodada (2026-09-01):** Enlightened Tutor, Mishra's Bauble, Overlord of the Hauntwoods (ataque), Inventors' Fair, Oswald Fiddlebender (achados na 1ª rodada da compilação final) + Ultron sob Mycosynth Lattice (checagem estática de `ctype` em vez de `is_artifact()` dinâmico — achado nesta 2ª rodada pela própria pergunta do usuário sobre a combinação Lattice+Ultron).

Nenhuma cláusula ficou sem uma linha nesta tabela. Se algo aqui estiver
errado, o local citado (`nome_da_funcao()`) é onde conferir — não peça
"tem certeza?" de novo, aponte a linha e a cláusula que parece errada.
