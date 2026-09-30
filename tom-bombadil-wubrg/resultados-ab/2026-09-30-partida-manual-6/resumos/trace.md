## Trace por turno (mudanças de zona e fichas; `∅` = origem fora de jogo)

**T1**
- Enduring Vitality: library → hand
- Femeref Enchantress: library → hand
- Serra's Sanctum: library → hand
- Temple Garden: library → hand
- Bloom Tender: library → hand
- Wooded Foothills: library → hand
- Barbara Wright: library → hand
- Elspeth Conquers Death: library → hand
- Temple Garden: hand → battlefield · entra virado

**T2**
- Fertile Ground: library → hand
- Wooded Foothills: hand → battlefield
- Wooded Foothills: battlefield → graveyard
- Raugrin Triome: library → battlefield · entra virado

**T3**
- Arcane Signet: library → hand
- Serra's Sanctum: hand → battlefield
- Fertile Ground: hand → battlefield
- Arcane Signet: hand → battlefield

**T4**
- Flooded Strand: library → hand
- Flooded Strand: hand → battlefield
- Flooded Strand: battlefield → graveyard
- Savai Triome: library → battlefield · entra virado
- Tom Bombadil: commandZone → battlefield

**T5**
- Raffine's Tower: library → hand
- Raffine's Tower: hand → battlefield · entra virado
- Enduring Vitality: hand → battlefield
- Bloom Tender: hand → battlefield

**T6**
- Fable of the Mirror-Breaker // Reflection of Kiki-Jiki: library → hand
- Fable of the Mirror-Breaker // Reflection of Kiki-Jiki: hand → battlefield (Lore=1)
- Fable of the Mirror-Breaker // Reflection of Kiki-Jiki: hand → battlefield (Lore=1)
- Goblin Shaman [ficha]: ∅ → battlefield
- Elspeth Conquers Death: hand → battlefield (Lore=1)
- Femeref Enchantress: hand → battlefield
- Snail: ∅ → opponentsCards

**T7**
- Leyline Binding: library → hand
- Barbara Wright: hand → graveyard
- Windswept Heath: library → hand
- Windswept Heath: hand → battlefield
- Windswept Heath: battlefield → graveyard
- Zagoth Triome: library → battlefield · entra virado
- Treasure [ficha]: ∅ → battlefield

**T8**
- Stomping Ground: library → hand
- Barbara Wright: graveyard → battlefield
- Elspeth Conquers Death: battlefield → graveyard
- The Coming of Galactus: library → battlefield (Lore=1)
- Forest: library → hand
- Hallowed Fountain: library → hand
- Forest: hand → battlefield
- Treasure [ficha]: ∅ → battlefield
- Culling Ritual: ∅ → opponentsCards
- Barbara Wright: battlefield → graveyard
- Bloom Tender: battlefield → graveyard
- Femeref Enchantress: battlefield → graveyard
- Arcane Signet: battlefield → graveyard
- Fertile Ground: battlefield → graveyard

**T9**
- Godless Shrine: library → hand
- Stomping Ground: hand → battlefield · entra virado
- Enduring Vitality [cópia]: ∅ → battlefield
- Wan Shi Tong, Librarian: ∅ → opponentsCards

**T10**
- Ketria Triome: library → hand
- Ketria Triome: hand → battlefield · entra virado
- Enduring Vitality [cópia]: ∅ → battlefield
- Jin-Gitaxias, Core Augur: ∅ → opponentsCards

**T11**
- Weaver of Harmony: library → hand
- Leyline Binding: hand → battlefield
- Weaver of Harmony: hand → battlefield
- Galactus [ficha]: ∅ → battlefield
- The Coming of Galactus: battlefield → graveyard
- In the Darkness Bind Them: library → battlefield (Lore=1)
- Wraith [ficha]: ∅ → battlefield
- The Ring // The Ring Tempts You [ficha]: ∅ → battlefield
- Vandalblast: ∅ → opponentsCards

**T12**
- O'aka, Traveling Merchant: library → hand
- Wraith [ficha]: ∅ → battlefield
- O'aka, Traveling Merchant: hand → battlefield
- Hallowed Fountain: hand → graveyard
- Utopia Sprawl: library → hand
- Utopia Sprawl: hand → battlefield
- Anguished Unmaking: ∅ → opponentsCards
- In the Darkness Bind Them: battlefield → exile
- In the Darkness Bind Them: exile → battlefield (Lore=1)
- Wraith [ficha]: ∅ → battlefield
- Wraith [ficha]: ∅ → battlefield

**T13**
- Indatha Triome: library → hand

## Verificações automáticas

| turno | terrenos jogados da mão | saiu por fetch | veredito |
|---|---|---|---|
| T1 | Temple Garden | — | ok |
| T2 | Wooded Foothills | Raugrin Triome | ok |
| T3 | Serra's Sanctum | — | ok |
| T4 | Flooded Strand | Savai Triome | ok |
| T5 | Raffine's Tower | — | ok |
| T6 | — | — | ok |
| T7 | Windswept Heath | Zagoth Triome | ok |
| T8 | Forest | — | ok |
| T9 | Stomping Ground | — | ok |
| T10 | Ketria Triome | — | ok |
| T11 | — | — | ok |
| T12 | — | — | ok |
| T13 | — | — | ok |

- T2: Wooded Foothills jogado → cemitério: sim · terreno buscado: sim
- T4: Flooded Strand jogado → cemitério: sim · terreno buscado: sim
- T7: Windswept Heath jogado → cemitério: sim · terreno buscado: sim

| turno | fontes viradas no fim do turno | magias entrando em campo (MV) | magia/descarte mão→cemitério (MV) |
|---|---|---|---|
| T1 | — | — | — |
| T2 | — | — | — |
| T3 | Raugrin Triome, Temple Garden, Serra's Sanctum | Fertile Ground (2), Arcane Signet (2) | — |
| T4 | Serra's Sanctum, Raugrin Triome, Temple Garden, Arcane Signet | Tom Bombadil (5) | — |
| T5 | Arcane Signet, Savai Triome, Serra's Sanctum, Raugrin Triome, Temple Garden, Tom Bombadil (criatura) | Enduring Vitality (3), Bloom Tender (2) | — |
| T6 | Raffine's Tower, Tom Bombadil (criatura), Arcane Signet, Savai Triome, Serra's Sanctum, Raugrin Triome, Temple Garden, Enduring Vitality (criatura) | Fable of the Mirror-Breaker (3), Fable of the Mirror-Breaker (3), Elspeth Conquers Death (5), Femeref Enchantress (2) | — |
| T7 | Enduring Vitality (criatura) | — | Barbara Wright (2) |
| T8 | Enduring Vitality (criatura) | — | — |
| T9 | Fable of the Mirror-Breaker // Reflection of Kiki-Jiki (criatura), Temple Garden, Enduring Vitality (criatura) | — | — |
| T10 | Fable of the Mirror-Breaker // Reflection of Kiki-Jiki (criatura), Temple Garden, Enduring Vitality (criatura) | — | — |
| T11 | Temple Garden, Forest, Zagoth Triome, Raugrin Triome | Leyline Binding (6), Weaver of Harmony (2) | — |
| T12 | Zagoth Triome, Raugrin Triome, Temple Garden, Savai Triome, Weaver of Harmony (criatura) | O'aka, Traveling Merchant (2), Utopia Sprawl (1) | Hallowed Fountain (0) |
| T13 | — | — | — |

| Saga (objeto) | valores de saber em ordem do log (T: valores) | anomalias |
|---|---|---|
| Elspeth Conquers Death `hwse5NBqt9S` | T6: entra 1; T7: 2; T8: 3→cemitério | — |
| Fable of the Mirror-Breaker `Hdqqde1owJO` | T6: entra 1→entra 1; T7: 2; T8: 3 | — |
| The Coming of Galactus `cPVoE-w9PDU` | T8: entra 1; T9: 2; T10: 3; T11: 4→cemitério | — |
| In the Darkness Bind Them `myf_UXcBRiJ` | T11: entra 1; T12: 2→exílio→entra 1→2→3 | T12: saiu para o exílio · T12: voltou do exílio com 1 (objeto novo) · T12: incremento extra 1→2 no mesmo turno (entrou no T12; só +1 na fase principal 1 é automático) · T12: incremento extra 2→3 no mesmo turno (entrou no T12; só +1 na fase principal 1 é automático) |

Saída de campo: Elspeth Conquers Death → cemitério (T8); The Coming of Galactus → cemitério (T11); In the Darkness Bind Them → exílio (T12)

- T8: Saga da biblioteca direto para o campo: The Coming of Galactus (1; limite 1 por turno do Tom: ok)
- T11: Saga da biblioteca direto para o campo: In the Darkness Bind Them (1; limite 1 por turno do Tom: ok)

**Violações provadas pelo log: 0**
**Anomalias sem fonte no log: 3 — In the Darkness Bind Them T12: voltou do exílio sem carta da lista que a devolva; In the Darkness Bind Them T12: incremento extra 1→2 no mesmo turno (entrou no T12; só +1 na fase principal 1 é automático); In the Darkness Bind Them T12: incremento extra 2→3 no mesmo turno (entrou no T12; só +1 na fase principal 1 é automático)** (estado que nenhuma carta da lista explica; típico de ajuste manual/desfazer do playtester, não prova erro de jogo)
