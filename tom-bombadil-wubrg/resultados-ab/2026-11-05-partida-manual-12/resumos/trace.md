## Trace por turno (mudanças de zona e fichas; `∅` = origem fora de jogo)

**T1**
- Fertile Ground: library → hand
- Jugan Defends the Temple // Remnant of the Rising Star: library → hand
- The First Iroan Games: library → hand
- Prismatic Omen: library → hand
- Enchantress's Presence: library → hand
- Forest: library → hand
- Ketria Triome: library → hand
- In the Darkness Bind Them: library → hand
- Ketria Triome: hand → battlefield · entra virado

**T2**
- Bloom Tender: library → hand
- Forest: hand → battlefield
- Fertile Ground: hand → battlefield

**T3**
- Temple Garden: library → hand
- Temple Garden: hand → battlefield
- Enchantress's Presence: hand → battlefield

**T4**
- Nesting Grounds: library → hand
- Nesting Grounds: hand → battlefield
- Bloom Tender: hand → battlefield
- Prismatic Omen: hand → battlefield
- Ripples of Potential: library → hand
- Walker: ∅ → opponentsCards

**T5**
- Godless Shrine: library → hand
- Godless Shrine: hand → battlefield · entra virado
- Tom Bombadil: commandZone → battlefield
- In the Darkness Bind Them: hand → battlefield (Lore=1)
- Wraith [ficha]: ∅ → battlefield
- Stomping Ground: library → hand
- Fold into Aether: ∅ → opponentsCards

**T6**
- Kiora Bests the Sea God: library → hand
- Stomping Ground: hand → battlefield · entra virado
- Wraith [ficha]: ∅ → battlefield
- Jugan Defends the Temple // Remnant of the Rising Star: hand → battlefield (Lore=1)
- Jugan Defends the Temple // Remnant of the Rising Star: battlefield → graveyard
- Plains: library → hand
- The First Iroan Games: hand → battlefield (Lore=1)
- The Coming of Galactus: library → hand
- Snuff Out: ∅ → opponentsCards
- Bloom Tender: battlefield → graveyard

**T7**
- Resurgent Belief: library → hand
- Plains: hand → battlefield
- Human Soldier [ficha]: ∅ → battlefield
- The Ring // The Ring Tempts You [ficha]: ∅ → battlefield
- Plains: hand → battlefield
- Resurgent Belief: hand → battlefield
- Wraith [ficha]: ∅ → battlefield
- Soul Shatter: ∅ → opponentsCards
- Tom Bombadil: battlefield → commandZone

**T8**
- Raugrin Triome: library → hand
- Raugrin Triome: hand → battlefield
- Tom Bombadil: commandZone → battlefield
- Austere Command: ∅ → opponentsCards
- Enchantress's Presence: battlefield → graveyard
- Prismatic Omen: battlefield → graveyard
- In the Darkness Bind Them: battlefield → graveyard
- The First Iroan Games: battlefield → graveyard

**T9**
- Karn's Bastion: library → hand
- Fertile Ground: battlefield → graveyard
- Karn's Bastion: hand → battlefield
- Kiora Bests the Sea God: hand → battlefield (Lore=1)
- Kraken [ficha]: ∅ → battlefield
- Resurgent Belief: battlefield → graveyard
- Fertile Ground: graveyard → battlefield
- Fertile Ground: graveyard → battlefield
- Enchantress's Presence: graveyard → battlefield
- Prismatic Omen: graveyard → battlefield
- In the Darkness Bind Them: graveyard → battlefield (Lore=1)
- The First Iroan Games: graveyard → battlefield (Lore=1)
- Jugan Defends the Temple // Remnant of the Rising Star: graveyard → battlefield (Lore=1)
- Human Monk [ficha]: ∅ → battlefield
- Wraith [ficha]: ∅ → battlefield
- Human Soldier [ficha]: ∅ → battlefield
- Kiora Bests the Sea God: hand → battlefield (Lore=1)
- Kraken [ficha]: ∅ → battlefield
- Song of Eärendil: library → hand
- Plant Warrior: ∅ → opponentsCards

**T10**
- O'aka, Traveling Merchant: library → hand
- Wraith [ficha]: ∅ → battlefield
- O'aka, Traveling Merchant: hand → battlefield
- Song of Eärendil: hand → battlefield (Lore=1)
- Estrid's Invocation: library → hand
- Elspeth Conquers Death: library → hand
- Verdant Catacombs: library → hand
- Verdant Catacombs: hand → battlefield

## Verificações automáticas

| turno | terrenos jogados da mão | saiu por fetch | veredito |
|---|---|---|---|
| T1 | Ketria Triome | — | ok |
| T2 | Forest | — | ok |
| T3 | Temple Garden | — | ok |
| T4 | Nesting Grounds | — | ok |
| T5 | Godless Shrine | — | ok |
| T6 | Stomping Ground | — | ok |
| T7 | Plains (mesmo objeto jogado 2×: desfazer/refazer) | — | ok |
| T8 | Raugrin Triome | — | ok |
| T9 | Karn's Bastion | — | ok |
| T10 | Verdant Catacombs | — | ok |

- T10: Verdant Catacombs jogado → cemitério: NÃO · terreno buscado: NÃO · **fim do log: fetch parada em campo, não acionada (não é violação)**

| turno | fontes viradas no fim do turno | magias entrando em campo (MV) | magia/descarte mão→cemitério (MV) |
|---|---|---|---|
| T1 | — | — | — |
| T2 | Ketria Triome, Forest | Fertile Ground (2) | — |
| T3 | Forest, Ketria Triome | Enchantress's Presence (3) | — |
| T4 | Forest, Ketria Triome, Nesting Grounds | Bloom Tender (2), Prismatic Omen (2) | — |
| T5 | Nesting Grounds, Forest, Ketria Triome, Fertile Ground, Temple Garden, Bloom Tender (criatura) | Tom Bombadil (5), In the Darkness Bind Them (5) | — |
| T6 | Godless Shrine, Nesting Grounds, Forest, Temple Garden, Ketria Triome, Tom Bombadil (criatura) | Jugan Defends the Temple (3), The First Iroan Games (3) | — |
| T7 | Ketria Triome, Stomping Ground, Temple Garden, Godless Shrine, Forest, Nesting Grounds, Plains | Resurgent Belief (0) | — |
| T8 | Plains, Godless Shrine, Raugrin Triome, Nesting Grounds, Fertile Ground, Ketria Triome, Temple Garden, Stomping Ground, Forest | Tom Bombadil (5) | — |
| T9 | Raugrin Triome, Plains, Nesting Grounds, Temple Garden, Stomping Ground, Forest, Ketria Triome, Karn's Bastion, Tom Bombadil (criatura) | Kiora Bests the Sea God (7), Kiora Bests the Sea God (7) | — |
| T10 | Plains, Tom Bombadil (criatura), Raugrin Triome, Forest, Temple Garden, Stomping Ground, Ketria Triome, Godless Shrine | O'aka, Traveling Merchant (2), Song of Eärendil (5) | — |

| turno | library→mão no log | cartas |
|---|---|---|
| T1 | 8 | Fertile Ground, Jugan Defends the Temple, The First Iroan Games, Prismatic Omen, Enchantress's Presence, Forest, Ketria Triome, In the Darkness Bind Them |
| T2 | 1 | Bloom Tender |
| T3 | 1 | Temple Garden |
| T4 | 2 | Nesting Grounds, Ripples of Potential |
| T5 | 2 | Godless Shrine, Stomping Ground |
| T6 | 3 | Kiora Bests the Sea God, Plains, The Coming of Galactus |
| T7 | 1 | Resurgent Belief |
| T8 | 1 | Raugrin Triome |
| T9 | 2 | Karn's Bastion, Song of Eärendil |
| T10 | 4 | O'aka, Traveling Merchant, Estrid's Invocation, Elspeth Conquers Death, Verdant Catacombs |

| Saga (objeto) | valores de saber em ordem do log (T: valores) | anomalias |
|---|---|---|
| Jugan Defends the Temple `Kz8oX8bhRFj` | T6: entra 1→cemitério; T9: 1 | — |
| The First Iroan Games `mNXAzCLKx1b` | T6: entra 1; T7: 2→3; T8: cemitério; T9: 1 | T7: incremento extra 2→3 no mesmo turno (entrou no T6; só +1 na fase principal 1 é automático) |
| In the Darkness Bind Them `hfeE11TqF5g` | T5: entra 1; T6: 2; T7: 3; T8: 4→3→cemitério; T9: 1 | — |
| Kiora Bests the Sea God `fImxALV_Y9y` | T9: entra 1→entra 1 | — |
| The Coming of Galactus `VrsC0cF1CAl` |  | — |
| Song of Eärendil `uqRtgo8GDZa` | T10: entra 1 | — |
| Elspeth Conquers Death `AlJhyaNgQi7` |  | — |

Saída de campo: Jugan Defends the Temple → cemitério (T6); In the Darkness Bind Them → cemitério (T8); The First Iroan Games → cemitério (T8)


**Violações provadas pelo log: 0**
**Anomalias sem fonte no log: 1 — The First Iroan Games T7: incremento extra 2→3 no mesmo turno (entrou no T6; só +1 na fase principal 1 é automático)** (estado que nenhuma carta da lista explica; típico de ajuste manual/desfazer do playtester, não prova erro de jogo)
