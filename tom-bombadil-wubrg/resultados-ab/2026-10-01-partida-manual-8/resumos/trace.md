## Trace por turno (mudanças de zona e fichas; `∅` = origem fora de jogo)

**T1**
- Narci, Fable Singer: library → hand
- O'aka, Traveling Merchant: library → hand
- Forest: library → hand
- Jugan Defends the Temple // Remnant of the Rising Star: library → hand
- Sol Ring: library → hand
- Flooded Strand: library → hand
- Estrid's Invocation: library → hand
- Resourceful Defense: library → hand
- Forest: hand → battlefield
- Sol Ring: hand → battlefield

**T2**
- Bloom Tender: library → hand
- Flooded Strand: hand → battlefield
- Flooded Strand: battlefield → graveyard
- Raffine's Tower: library → battlefield · entra virado
- Jugan Defends the Temple // Remnant of the Rising Star: hand → battlefield (Lore=1)
- Human Monk [ficha]: ∅ → battlefield

**T3**
- Satsuki, the Living Lore: library → hand
- O'aka, Traveling Merchant: hand → battlefield
- Bloom Tender: hand → battlefield

**T4**
- Fable of the Mirror-Breaker // Reflection of Kiki-Jiki: library → hand
- Elspeth Conquers Death: library → hand
- Resourceful Defense: hand → battlefield
- Resourceful Defense: hand → battlefield
- Satsuki, the Living Lore: hand → battlefield

**T5**
- The Creation of Avacyn: library → hand
- Serra's Sanctum: library → hand
- Serra's Sanctum: hand → battlefield
- Elspeth Conquers Death: hand → battlefield (Lore=1)

**T6**
- Summon: Fenrir: library → hand
- Raugrin Triome: library → hand
- Raugrin Triome: hand → battlefield · entra virado
- Summon: Fenrir: hand → battlefield (Lore=1)
- Swamp: library → battlefield · entra virado
- Estrid's Invocation: hand → battlefield
- Mountain: library → battlefield · entra virado
- Human Citizen: ∅ → opponentsCards

**T7**
- Binding the Old Gods: library → hand
- Elspeth Conquers Death: battlefield → graveyard
- Tom Bombadil: commandZone → battlefield
- Summon: Fenrir: battlefield → graveyard
- Urza's Saga: library → hand
- Birth of the Imperium: library → battlefield (Lore=1)
- Astartes Warrior [ficha]: ∅ → battlefield
- Astartes Warrior [ficha]: ∅ → battlefield
- Astartes Warrior [ficha]: ∅ → battlefield
- Urza's Saga: hand → battlefield (Lore=1)
- Ugin, Eye of the Storms: ∅ → opponentsCards
- Birth of the Imperium: battlefield → exile

**T8**
- Farseek: library → hand
- Estrid's Invocation: battlefield → exile
- Estrid's Invocation: exile → battlefield
- Human Monk [ficha]: ∅ → battlefield
- Summon: Bahamut: library → hand

## Verificações automáticas

| turno | terrenos jogados da mão | saiu por fetch | veredito |
|---|---|---|---|
| T1 | Forest | — | ok |
| T2 | Flooded Strand | Raffine's Tower | ok |
| T3 | — | — | ok |
| T4 | — | — | ok |
| T5 | Serra's Sanctum | — | ok |
| T6 | Raugrin Triome | Swamp, Mountain | ok |
| T7 | Urza's Saga | — | ok |
| T8 | — | — | ok |

- T2: Flooded Strand jogado → cemitério: sim · terreno buscado: sim

| turno | fontes viradas no fim do turno | magias entrando em campo (MV) | magia/descarte mão→cemitério (MV) |
|---|---|---|---|
| T1 | Forest | Sol Ring (1) | — |
| T2 | Forest, Sol Ring | Jugan Defends the Temple (3) | — |
| T3 | Sol Ring, Raffine's Tower, Forest | O'aka, Traveling Merchant (2), Bloom Tender (2) | — |
| T4 | Sol Ring, Raffine's Tower, O'aka, Traveling Merchant (criatura), Bloom Tender (criatura) | Resourceful Defense (3), Resourceful Defense (3), Satsuki, the Living Lore (2) | — |
| T5 | O'aka, Traveling Merchant (criatura), Sol Ring, Serra's Sanctum, Forest | Elspeth Conquers Death (5) | — |
| T6 | O'aka, Traveling Merchant (criatura), Sol Ring, Forest, Bloom Tender (criatura) | Summon: Fenrir (3), Estrid's Invocation (3) | — |
| T7 | Swamp, Mountain, Raugrin Triome, Forest, O'aka, Traveling Merchant (criatura), Raffine's Tower, Satsuki, the Living Lore (criatura) | Tom Bombadil (5) | — |
| T8 | O'aka, Traveling Merchant (criatura) | — | — |

| turno | library→mão no log | cartas |
|---|---|---|
| T1 | 8 | Narci, Fable Singer, O'aka, Traveling Merchant, Forest, Jugan Defends the Temple, Sol Ring, Flooded Strand, Estrid's Invocation, Resourceful Defense |
| T2 | 1 | Bloom Tender |
| T3 | 1 | Satsuki, the Living Lore |
| T4 | 2 | Fable of the Mirror-Breaker, Elspeth Conquers Death |
| T5 | 2 | The Creation of Avacyn, Serra's Sanctum |
| T6 | 2 | Summon: Fenrir, Raugrin Triome |
| T7 | 2 | Binding the Old Gods, Urza's Saga |
| T8 | 2 | Farseek, Summon: Bahamut |

| Saga (objeto) | valores de saber em ordem do log (T: valores) | anomalias |
|---|---|---|
| Jugan Defends the Temple `UXAXAXT1Dfx` | T2: entra 1; T3: 2; T4: 3→3→1→2; T5: 1→2; T6: 1→2; T7: 1→2; T8: 1→2 | T4: incremento extra 1→2 no mesmo turno (entrou no T2; só +1 na fase principal 1 é automático) |
| Fable of the Mirror-Breaker `LjC_tcLQMGQ` |  | — |
| Elspeth Conquers Death `DADZmPotLRT` | T5: entra 1; T6: 1→2; T7: 3→cemitério | — |
| The Creation of Avacyn `c7-2oBebblp` |  | — |
| Summon: Fenrir `k-KzmN76hDM` | T6: entra 1; T7: 2→3→cemitério | T7: incremento extra 2→3 no mesmo turno (entrou no T6; só +1 na fase principal 1 é automático) |
| Binding the Old Gods `bZm6RiKxQri` |  | — |
| Urza's Saga `KBgRp7TwNiV` | T7: entra 1 | — |
| Birth of the Imperium `fs7VDSN9Kvk` | T7: entra 1→exílio | T7: saiu para o exílio |
| Summon: Bahamut `pTF6UPxsDRy` |  | — |

Saída de campo: Elspeth Conquers Death → cemitério (T7); Summon: Fenrir → cemitério (T7); Birth of the Imperium → exílio (T7)

- T7: Saga da biblioteca direto para o campo: Birth of the Imperium (1; limite 1 por turno do Tom: ok)

**Violações provadas pelo log: 0**
**Anomalias sem fonte no log: 2 — Jugan Defends the Temple T4: incremento extra 1→2 no mesmo turno (entrou no T2; só +1 na fase principal 1 é automático); Summon: Fenrir T7: incremento extra 2→3 no mesmo turno (entrou no T6; só +1 na fase principal 1 é automático)** (estado que nenhuma carta da lista explica; típico de ajuste manual/desfazer do playtester, não prova erro de jogo)
