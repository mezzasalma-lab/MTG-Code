## Trace por turno (mudanças de zona e fichas; `∅` = origem fora de jogo)

**T1**
- Awaken the Honored Dead: library → hand
- Savai Triome: library → hand
- Barbara Wright: library → hand
- Exotic Orchard: library → hand
- Zagoth Triome: library → hand
- Forest: library → hand
- Sanctum Weaver: library → hand
- Ketria Triome: library → hand
- Savai Triome: hand → battlefield · entra virado

**T2**
- Flux Channeler: library → hand
- Forest: hand → battlefield
- Sanctum Weaver: hand → battlefield

**T3**
- Setessan Champion: library → hand
- Exotic Orchard: hand → battlefield
- Setessan Champion: hand → battlefield

**T4**
- Summon: Knights of Round: library → hand
- Ketria Triome: hand → battlefield · entra virado
- Barbara Wright: hand → battlefield
- Torment of Hailfire: ∅ → opponentsCards
- Awaken the Honored Dead: hand → graveyard
- Zagoth Triome: hand → graveyard

**T5**
- Faeburrow Elder: library → hand
- Tom Bombadil: commandZone → battlefield

**T6**
- The Bath Song: library → hand
- The Bath Song: hand → battlefield (Lore=1)
- Teferi's Protection: library → hand
- Fable of the Mirror-Breaker // Reflection of Kiki-Jiki: library → hand
- Faeburrow Elder: hand → graveyard
- Golgari Charm: ∅ → opponentsCards
- Barbara Wright: battlefield → graveyard

**T7**
- Arcane Signet: library → hand
- Arcane Signet: hand → battlefield
- Fable of the Mirror-Breaker // Reflection of Kiki-Jiki: hand → battlefield (Lore=1)
- Farseek: library → hand
- Jugan Defends the Temple // Remnant of the Rising Star: library → hand
- Farseek: hand → battlefield
- Farseek: hand → graveyard
- Goblin Shaman [ficha]: ∅ → battlefield

**T8**
- City of Brass: library → hand
- City of Brass: hand → battlefield
- The Bath Song [cópia]: ∅ → battlefield
- The Bath Song [cópia]: ∅ → battlefield
- The Bath Song [cópia]: ∅ → battlefield
- The Bath Song [cópia]: ∅ → battlefield
- The Bath Song [cópia]: ∅ → battlefield
- The Bath Song [cópia]: ∅ → battlefield
- Farseek: graveyard → library
- Barbara Wright: graveyard → library
- Faeburrow Elder: graveyard → library
- Zagoth Triome: graveyard → library
- Awaken the Honored Dead: graveyard → library
- The Bath Song: battlefield → graveyard
- The Bath Song: battlefield → graveyard
- In the Darkness Bind Them: library → battlefield (Lore=1)
- The Ring // The Ring Tempts You [ficha]: ∅ → battlefield
- Wraith [ficha]: ∅ → battlefield
- Flux Channeler: hand → graveyard
- Jugan Defends the Temple // Remnant of the Rising Star: hand → graveyard
- Sythis, Harvest's Hand: library → hand
- Urza's Saga: library → hand
- Sythis, Harvest's Hand: hand → battlefield
- Urza's Saga: hand → battlefield (Lore=1)
- Summon: Knights of Round: hand → battlefield (Lore=1)
- Knight [ficha]: ∅ → battlefield
- Knight [ficha]: ∅ → battlefield
- Knight [ficha]: ∅ → battlefield

## Verificações automáticas

| turno | terrenos jogados da mão | saiu por fetch | veredito |
|---|---|---|---|
| T1 | Savai Triome | — | ok |
| T2 | Forest | — | ok |
| T3 | Exotic Orchard | — | ok |
| T4 | Ketria Triome | — | ok |
| T5 | — | — | ok |
| T6 | — | — | ok |
| T7 | — | — | ok |
| T8 | City of Brass, Urza's Saga | — | **VIOLA (mais de 1)** |

- (nenhum fetchland nesta partida)

| turno | fontes viradas no fim do turno | magias entrando em campo (MV) | magia/descarte mão→cemitério (MV) |
|---|---|---|---|
| T1 | — | — | — |
| T2 | Savai Triome, Forest | Sanctum Weaver (2) | — |
| T3 | Forest, Savai Triome, Exotic Orchard | Setessan Champion (3) | — |
| T4 | Exotic Orchard, Savai Triome | Barbara Wright (2) | Awaken the Honored Dead (3), Zagoth Triome (0) |
| T5 | Ketria Triome, Exotic Orchard, Savai Triome, Sanctum Weaver (criatura), Forest | Tom Bombadil (5) | — |
| T6 | Ketria Triome, Exotic Orchard, Forest, Savai Triome, Setessan Champion (criatura) | The Bath Song (4) | Faeburrow Elder (3) |
| T7 | Ketria Triome, Exotic Orchard, Forest, Savai Triome, Arcane Signet | Arcane Signet (2), Fable of the Mirror-Breaker (3), Farseek (2) | Farseek (2) |
| T8 | Arcane Signet, Savai Triome, Exotic Orchard, Ketria Triome, Forest, City of Brass, Urza's Saga, Sanctum Weaver (criatura) | Sythis, Harvest's Hand (2), Summon: Knights of Round (8) | Flux Channeler (3), Jugan Defends the Temple (3) |

| Saga (objeto) | valores de saber em ordem do log (T: valores) | anomalias |
|---|---|---|
| Awaken the Honored Dead `8Pfrai0B3de` |  | — |
| Summon: Knights of Round `IpXh9LlQ7OG` | T8: entra 1 | — |
| The Bath Song `fiBhcM4xWyW` | T6: entra 1; T7: 2; T8: 3→cemitério→cemitério | — |
| Fable of the Mirror-Breaker `Hdqqde1owJO` | T7: entra 1; T8: 2 | — |
| Jugan Defends the Temple `a0v_gofRVcf` |  | — |
| The Bath Song (cópia-ficha) `F6WmXQj9V` | T8: entra 0 | T8: cópia-ficha de Saga sem fonte de cópia na lista e sem marcador de saber (CR 714.3a: deveria entrar com 1) |
| The Bath Song (cópia-ficha) `EE9BMld_1c` | T8: entra 0 | T8: cópia-ficha de Saga sem fonte de cópia na lista e sem marcador de saber (CR 714.3a: deveria entrar com 1) |
| The Bath Song (cópia-ficha) `-0IQO-rWIa` | T8: entra 0 | T8: cópia-ficha de Saga sem fonte de cópia na lista e sem marcador de saber (CR 714.3a: deveria entrar com 1) |
| The Bath Song (cópia-ficha) `0X4d8Wm4JJ` | T8: entra 0 | T8: cópia-ficha de Saga sem fonte de cópia na lista e sem marcador de saber (CR 714.3a: deveria entrar com 1) |
| The Bath Song (cópia-ficha) `Gcj913ix2s` | T8: entra 0 | T8: cópia-ficha de Saga sem fonte de cópia na lista e sem marcador de saber (CR 714.3a: deveria entrar com 1) |
| The Bath Song (cópia-ficha) `8WSfYX2aB4` | T8: entra 0 | T8: cópia-ficha de Saga sem fonte de cópia na lista e sem marcador de saber (CR 714.3a: deveria entrar com 1) |
| In the Darkness Bind Them `myf_UXcBRiJ` | T8: entra 1 | — |
| Urza's Saga `bOmaM6YVLvl` | T8: entra 1→1 | — |

Saída de campo: The Bath Song → cemitério (T8); The Bath Song → cemitério (T8)

- T8: Saga da biblioteca direto para o campo: In the Darkness Bind Them (1; limite 1 por turno do Tom: ok)

**Violações provadas pelo log: 1 — T8: 2 terrenos jogados da mão**
**Anomalias sem fonte no log: 6 — The Bath Song (cópia-ficha) T8: cópia-ficha sem fonte de cópia na lista; The Bath Song (cópia-ficha) T8: cópia-ficha sem fonte de cópia na lista; The Bath Song (cópia-ficha) T8: cópia-ficha sem fonte de cópia na lista; The Bath Song (cópia-ficha) T8: cópia-ficha sem fonte de cópia na lista; The Bath Song (cópia-ficha) T8: cópia-ficha sem fonte de cópia na lista; The Bath Song (cópia-ficha) T8: cópia-ficha sem fonte de cópia na lista** (estado que nenhuma carta da lista explica; típico de ajuste manual/desfazer do playtester, não prova erro de jogo)
