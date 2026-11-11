## Trace por turno (mudanças de zona e fichas; `∅` = origem fora de jogo)

**T1**
- Satsuki, the Living Lore: library → hand
- Historian's Boon: library → hand
- Godless Shrine: library → hand
- The First Iroan Games: library → hand
- Command Tower: library → hand
- Wooded Foothills: library → hand
- The Cruelty of Gix: library → hand
- Serra's Sanctum: library → hand
- Wooded Foothills: hand → battlefield
- Wooded Foothills: battlefield → graveyard
- Ziatora's Proving Ground: library → battlefield · entra virado

**T2**
- Summon: Yojimbo: library → hand
- Command Tower: hand → battlefield
- Satsuki, the Living Lore: hand → battlefield

**T3**
- Temple Garden: library → hand
- Godless Shrine: hand → battlefield
- The First Iroan Games: hand → battlefield (Lore=1)
- Human Soldier [ficha]: ∅ → battlefield

**T4**
- Bloom Tender: library → hand
- Temple Garden: hand → battlefield
- Bloom Tender: hand → battlefield

**T5**
- The Kami War // O-Kagachi Made Manifest: library → hand
- Serra's Sanctum: hand → battlefield
- Goldberry, River-Daughter: library → hand
- Fertile Ground: library → hand
- Tom Bombadil: commandZone → battlefield
- Historian's Boon: hand → battlefield
- Human Soldier [ficha]: ∅ → battlefield
- Gold [ficha]: ∅ → battlefield
- The First Iroan Games: battlefield → graveyard
- There and Back Again: library → battlefield (Lore=1)
- The Ring // The Ring Tempts You [ficha]: ∅ → battlefield
- Angel [ficha]: ∅ → battlefield
- Song of the Dryads: ∅ → opponentsCards

**T6**
- Clockspinning: library → hand
- Ketria Triome: library → battlefield · entra virado
- Fertile Ground: hand → battlefield
- Human Soldier [ficha]: ∅ → battlefield
- Summon: Yojimbo: hand → battlefield (Lore=1)
- Human Soldier [ficha]: ∅ → battlefield
- Goldberry, River-Daughter: hand → battlefield

**T7**
- Barbara Wright: library → hand
- Smaug [ficha]: ∅ → battlefield
- Binding the Old Gods: library → battlefield (Lore=1)
- Human Soldier [ficha]: ∅ → battlefield

## Verificações automáticas

| turno | terrenos jogados da mão | saiu por fetch | veredito |
|---|---|---|---|
| T1 | Wooded Foothills | Ziatora's Proving Ground | ok |
| T2 | Command Tower | — | ok |
| T3 | Godless Shrine | — | ok |
| T4 | Temple Garden | — | ok |
| T5 | Serra's Sanctum | — | ok |
| T6 | — | Ketria Triome | ok |
| T7 | — | — | ok |

- T1: Wooded Foothills jogado → cemitério: sim · terreno buscado: sim

| turno | fontes viradas no fim do turno | magias entrando em campo (MV) | magia/descarte mão→cemitério (MV) |
|---|---|---|---|
| T1 | — | — | — |
| T2 | Ziatora's Proving Ground, Command Tower | Satsuki, the Living Lore (2) | — |
| T3 | Command Tower, Ziatora's Proving Ground, Godless Shrine | The First Iroan Games (3) | — |
| T4 | Command Tower, Temple Garden | Bloom Tender (2) | — |
| T5 | Temple Garden, Command Tower, Serra's Sanctum, Godless Shrine, Ziatora's Proving Ground, Bloom Tender (criatura), Satsuki, the Living Lore (criatura) | Tom Bombadil (5), Historian's Boon (4) | — |
| T6 | Godless Shrine, Serra's Sanctum, Command Tower, Temple Garden, Ziatora's Proving Ground | Fertile Ground (2), Summon: Yojimbo (4), Goldberry, River-Daughter (2) | — |
| T7 | Goldberry, River-Daughter (criatura) | — | — |

| turno | library→mão no log | cartas |
|---|---|---|
| T1 | 8 | Satsuki, the Living Lore, Historian's Boon, Godless Shrine, The First Iroan Games, Command Tower, Wooded Foothills, The Cruelty of Gix, Serra's Sanctum |
| T2 | 1 | Summon: Yojimbo |
| T3 | 1 | Temple Garden |
| T4 | 1 | Bloom Tender |
| T5 | 3 | The Kami War, Goldberry, River-Daughter, Fertile Ground |
| T6 | 1 | Clockspinning |
| T7 | 1 | Barbara Wright |

| Saga (objeto) | valores de saber em ordem do log (T: valores) | anomalias |
|---|---|---|
| The First Iroan Games `5Grpg1bmV1X` | T3: entra 1; T4: 2; T5: 3→4→cemitério | T5: incremento extra 3→4 no mesmo turno (entrou no T3; só +1 na fase principal 1 é automático) |
| The Cruelty of Gix `p5Po5DKRJhk` |  | — |
| Summon: Yojimbo `I9rh_ajaHOb` | T6: entra 1; T7: 2 | — |
| The Kami War `B_VZQIyLO7i` |  | — |
| There and Back Again `Og4Rf_LclJx` | T5: entra 1; T7: 2→3→2 | T7: incremento extra 2→3 no mesmo turno (entrou no T5; só +1 na fase principal 1 é automático) |
| Binding the Old Gods `fFoYYBacJWv` | T7: entra 1 | — |

Saída de campo: The First Iroan Games → cemitério (T5)

- T5: Saga da biblioteca direto para o campo: There and Back Again (1; limite 1 por turno do Tom: ok)
- T7: Saga da biblioteca direto para o campo: Binding the Old Gods (1; limite 1 por turno do Tom: ok)

**Violações provadas pelo log: 0**
**Anomalias sem fonte no log: 2 — The First Iroan Games T5: incremento extra 3→4 no mesmo turno (entrou no T3; só +1 na fase principal 1 é automático); There and Back Again T7: incremento extra 2→3 no mesmo turno (entrou no T5; só +1 na fase principal 1 é automático)** (estado que nenhuma carta da lista explica; típico de ajuste manual/desfazer do playtester, não prova erro de jogo)
