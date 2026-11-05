## Trace por turno (mudanças de zona e fichas; `∅` = origem fora de jogo)

**T1**
- Power Conduit: library → hand
- Overgrown Tomb: library → hand
- Birth of the Imperium: library → hand
- Battle at the Helvault: library → hand
- Binding the Old Gods: library → hand
- Command Tower: library → hand
- Serra's Sanctum: library → hand
- City of Brass: library → hand
- Overgrown Tomb: hand → battlefield · entra virado

**T2**
- Jetmir's Garden: library → hand
- Command Tower: hand → battlefield
- Power Conduit: hand → battlefield

**T3**
- Ziatora's Proving Ground: library → hand
- Ziatora's Proving Ground: hand → battlefield · entra virado

**T4**
- The Eldest Reborn: library → hand
- City of Brass: hand → battlefield
- Binding the Old Gods: hand → battlefield (Lore=1)

**T5**
- Verdant Catacombs: library → hand
- Zagoth Triome: library → battlefield · entra virado
- Serra's Sanctum: hand → battlefield
- Tom Bombadil: commandZone → battlefield
- Shapeshifter: ∅ → opponentsCards
- Rankle, Master of Pranks: ∅ → opponentsCards
- Birth of the Imperium: hand → graveyard

**T6**
- Urza's Saga: library → hand
- Summon: Fenrir: library → battlefield (Lore=1)
- Plains: library → battlefield · entra virado
- Urza's Saga: hand → battlefield (Lore=1)
- Jetmir's Garden: hand → battlefield · entra virado
- The Eldest Reborn: hand → battlefield (Lore=1)
- Amazing Acrobatics: ∅ → opponentsCards

**T7**
- Exotic Orchard: library → hand
- Indatha Triome: library → battlefield · entra virado
- In the Darkness Bind Them: library → battlefield (Lore=1)
- Wraith [ficha]: ∅ → battlefield
- Urza's Saga: hand → battlefield (Lore=1)
- Battle at the Helvault: hand → battlefield (Lore=1)
- Battle at the Helvault: battlefield → graveyard
- Archfiend of Ifnir: ∅ → opponentsCards

**T8**
- Replenish: library → hand
- Wraith [ficha]: ∅ → battlefield
- Summon: Fenrir: battlefield → graveyard
- Mountain: library → hand
- Binding the Old Gods: battlefield → graveyard
- The Eldest Reborn: battlefield → graveyard
- Fable of the Mirror-Breaker // Reflection of Kiki-Jiki: library → battlefield (Lore=1)
- Goblin Shaman [ficha]: ∅ → battlefield
- Construct [ficha]: ∅ → battlefield
- Mountain: hand → battlefield
- Replenish: hand → battlefield
- Replenish: battlefield → graveyard
- The Eldest Reborn: graveyard → battlefield (Lore=1)
- Binding the Old Gods: graveyard → battlefield (Lore=1)
- Summon: Fenrir: graveyard → battlefield (Lore=1)
- Battle at the Helvault: graveyard → battlefield (Lore=1)
- Birth of the Imperium: graveyard → battlefield (Lore=1)

## Verificações automáticas

| turno | terrenos jogados da mão | saiu por fetch | veredito |
|---|---|---|---|
| T1 | Overgrown Tomb | — | ok |
| T2 | Command Tower | — | ok |
| T3 | Ziatora's Proving Ground | — | ok |
| T4 | City of Brass | — | ok |
| T5 | Serra's Sanctum | Zagoth Triome | ok |
| T6 | Urza's Saga, Jetmir's Garden | Plains | **VIOLA (mais de 1)** |
| T7 | Urza's Saga | Indatha Triome | ok |
| T8 | Mountain | — | ok |


| turno | fontes viradas no fim do turno | magias entrando em campo (MV) | magia/descarte mão→cemitério (MV) |
|---|---|---|---|
| T1 | — | — | — |
| T2 | Overgrown Tomb, Command Tower | Power Conduit (2) | — |
| T3 | — | — | — |
| T4 | Ziatora's Proving Ground, City of Brass, Command Tower, Overgrown Tomb | Binding the Old Gods (4) | — |
| T5 | City of Brass, Ziatora's Proving Ground, Command Tower, Overgrown Tomb, Serra's Sanctum | Tom Bombadil (5) | Birth of the Imperium (5) |
| T6 | Serra's Sanctum, Zagoth Triome, Ziatora's Proving Ground, Power Conduit, Tom Bombadil (criatura) | The Eldest Reborn (5) | — |
| T7 | Plains, Tom Bombadil (criatura), Serra's Sanctum, Power Conduit | Battle at the Helvault (6) | — |
| T8 | Plains, Serra's Sanctum, Urza's Saga, Jetmir's Garden, Ziatora's Proving Ground, Zagoth Triome | Replenish (4) | — |

| turno | library→mão no log | cartas |
|---|---|---|
| T1 | 8 | Power Conduit, Overgrown Tomb, Birth of the Imperium, Battle at the Helvault, Binding the Old Gods, Command Tower, Serra's Sanctum, City of Brass |
| T2 | 1 | Jetmir's Garden |
| T3 | 1 | Ziatora's Proving Ground |
| T4 | 1 | The Eldest Reborn |
| T5 | 1 | Verdant Catacombs |
| T6 | 1 | Urza's Saga |
| T7 | 1 | Exotic Orchard |
| T8 | 2 | Replenish, Mountain |

| Saga (objeto) | valores de saber em ordem do log (T: valores) | anomalias |
|---|---|---|
| Birth of the Imperium `kYt4rSXNabM` |  | — |
| Battle at the Helvault `nnW2kMNBmoQ` | T7: entra 1→cemitério; T8: 1 | — |
| Binding the Old Gods `kNmBX52Gntb` | T4: entra 1; T5: 2; T6: 3→2; T7: 3→2; T8: 3→cemitério→1 | — |
| The Eldest Reborn `h8bUKY-37cS` | T6: entra 1; T7: 1→1→2; T8: 3→cemitério→1 | — |
| Urza's Saga `fRdOn71suMD` | T6: entra 1; T7: entra 1; T8: 2→2 | — |
| Summon: Fenrir `bAfPI0CBToR` | T6: entra 1; T7: 2; T8: 3→cemitério→1 | — |
| In the Darkness Bind Them `acsji8HDPmA` | T7: entra 1; T8: 2 | — |
| Fable of the Mirror-Breaker `Hp06q9SNIS_` | T8: entra 1 | — |

Saída de campo: Battle at the Helvault → cemitério (T7); Summon: Fenrir → cemitério (T8); Binding the Old Gods → cemitério (T8); The Eldest Reborn → cemitério (T8)

- T6: Saga da biblioteca direto para o campo: Summon: Fenrir (1; limite 1 por turno do Tom: ok)
- T7: Saga da biblioteca direto para o campo: In the Darkness Bind Them (1; limite 1 por turno do Tom: ok)
- T8: Saga da biblioteca direto para o campo: Fable of the Mirror-Breaker // Reflection of Kiki-Jiki (1; limite 1 por turno do Tom: ok)

**Violações provadas pelo log: 1 — T6: 2 terrenos jogados da mão**
**Anomalias sem fonte no log: 0** (estado que nenhuma carta da lista explica; típico de ajuste manual/desfazer do playtester, não prova erro de jogo)
