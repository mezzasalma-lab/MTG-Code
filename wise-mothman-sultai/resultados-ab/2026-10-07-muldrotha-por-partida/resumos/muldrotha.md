# Muldrotha por partida (lista atual, sem trocas; N = 10.000 por modo, sementes 3.000.000+i, 12 turnos)

`base` = Muldrotha normal; `sem_habilidade` = a mesma carta como corpo 6/6 sem a habilidade do cemitério (mesmo baralho, mesma semente). `*` = excede o IC95% pareado.

## Modo padrao

### Quando ela entra em campo (acumulado, % das partidas)

| até T5 | T6 | T7 | T8 | T10 | T12 |
|---|---|---|---|---|---|
| 1.9% | 6.9% | 13.6% | 21.5% | 28.0% | 29.9% |

### O que ela faz nas 2994 partidas (29.9%) em que entra

| métrica | valor |
|---|---|
| turnos meus com ela em campo (média) | 2.08 |
| jogadas do cemitério por partida (terreno + magias) | 2.65 |
| ... magias recastadas por partida | 1.91 |
| ... terrenos jogados do cemitério por ela | 0.74 |
| ... recasts de creature | 0.94 |
| ... recasts de artifact | 0.59 |
| ... recasts de enchantment | 0.31 |
| ... recasts de planeswalker | 0.07 |
| magias recastadas por turno com ela em campo | 0.92 |
| partidas com 1+ / 3+ / 5+ recasts (entre as que ela entra) | 77% / 31% / 8% |
| peças-chave recompradas por partida (lista no script: Henge, Altars, Mindcrank, Orb, Psychic Corrosion, Memory Erosion, Palantír, Scales, Constrictor, Kami, Ruin Crab, Hollowmurk, Danny, Cauldron, Shredder, Ballista, Boots) | 1.11 (58% dos recasts) |

### O que ela recompra (top 12 de 5731 recasts em 10000 partidas)

| carta | recasts | % |
|---|---|---|
| Walking Ballista | 505 | 8.8% |
| Hardened Scales | 314 | 5.5% |
| The Great Henge | 288 | 5.0% |
| Winding Constrictor | 281 | 4.9% |
| Ruin Crab | 279 | 4.9% |
| Hollowmurk Siege | 266 | 4.6% |
| The Gitrog Monster | 246 | 4.3% |
| Sol Ring | 238 | 4.2% |
| Ashiok, Dream Render | 218 | 3.8% |
| Bramble Familiar // Fetch Quest | 206 | 3.6% |
| Danny Pink | 194 | 3.4% |
| Altar of the Brood | 175 | 3.1% |

### Fontes de recursão no deck (por partida, TODAS as partidas da `base`; o que cada peça devolve ao jogo)

| fonte | por partida |
|---|---|
| Muldrotha: magias recastadas (criatura, artefato, encantamento, planeswalker) | 0.57 |
| Muldrotha: terrenos jogados do cemitério (quando o Icetill não está em campo) | 0.22 |
| Six: retraces (cada um descarta um terreno) | 0.40 |
| Icetill Explorer: terrenos jogados do cemitério | 0.88 |
| `recursion_events_total` (inclui as linhas acima + Evolution Witness, Takenuma, Agadeem, Woodland...) | 1.96 |

### Valor da HABILIDADE (base − sem_habilidade, mesmas sementes; pontos percentuais de partidas, exceto onde indicado)

| amostra | n | mesa limpa T7 | T8 | T10 | 1º oponente fora até T6 | oponentes eliminados (média) | contadores +1/+1 | cartas milladas dos oponentes | eu perco por deck-out |
|---|---|---|---|---|---|---|---|---|---|
| todas as partidas | 10000 | +0.40 ± 0.15 * | +0.58 ± 0.24 * | +0.10 ± 0.21 | +0.08 ± 0.06 * | -0.00 ± 0.00 | +2.91 ± 0.44 * | +1.63 ± 0.35 * | +0.16 ± 0.20 |
| ela entra até T6 | 689 | +5.37 ± 1.91 * | +4.64 ± 2.62 * | -2.03 ± 1.75 * | +1.16 ± 0.80 * | -0.02 ± 0.03 | +19.17 ± 3.82 * | +12.12 ± 3.52 * | +2.03 ± 1.75 * |
| ela entra até T8 | 2154 | +1.86 ± 0.69 * | +2.69 ± 1.13 * | -0.19 ± 0.87 | +0.37 ± 0.26 * | -0.01 ± 0.01 | +11.23 ± 1.77 * | +6.17 ± 1.51 * | +0.79 ± 0.82 |

Partidas com todas as métricas acima idênticas entre `base` e `sem_habilidade`: 7980 de 10000 (80%).

## Modo resiliencia

### Quando ela entra em campo (acumulado, % das partidas)

| até T5 | T6 | T7 | T8 | T10 | T12 |
|---|---|---|---|---|---|
| 1.3% | 4.3% | 8.7% | 13.6% | 20.8% | 24.8% |

### O que ela faz nas 2477 partidas (24.8%) em que entra

| métrica | valor |
|---|---|
| turnos meus com ela em campo (média) | 2.01 |
| jogadas do cemitério por partida (terreno + magias) | 2.94 |
| ... magias recastadas por partida | 2.17 |
| ... terrenos jogados do cemitério por ela | 0.78 |
| ... recasts de creature | 1.04 |
| ... recasts de artifact | 0.65 |
| ... recasts de enchantment | 0.40 |
| ... recasts de planeswalker | 0.07 |
| magias recastadas por turno com ela em campo | 1.08 |
| partidas com 1+ / 3+ / 5+ recasts (entre as que ela entra) | 79% / 37% / 12% |
| peças-chave recompradas por partida (lista no script: Henge, Altars, Mindcrank, Orb, Psychic Corrosion, Memory Erosion, Palantír, Scales, Constrictor, Kami, Ruin Crab, Hollowmurk, Danny, Cauldron, Shredder, Ballista, Boots) | 1.33 (61% dos recasts) |

### O que ela recompra (top 12 de 5411 recasts em 10000 partidas)

| carta | recasts | % |
|---|---|---|
| Walking Ballista | 478 | 8.8% |
| Hardened Scales | 389 | 7.2% |
| Winding Constrictor | 314 | 5.8% |
| Hollowmurk Siege | 299 | 5.5% |
| Ruin Crab | 288 | 5.3% |
| The Great Henge | 254 | 4.7% |
| Sol Ring | 233 | 4.3% |
| The Gitrog Monster | 218 | 4.0% |
| Danny Pink | 217 | 4.0% |
| Bramble Familiar // Fetch Quest | 183 | 3.4% |
| Ashiok, Dream Render | 178 | 3.3% |
| Palantír of Orthanc | 172 | 3.2% |

### Fontes de recursão no deck (por partida, TODAS as partidas da `base`; o que cada peça devolve ao jogo)

| fonte | por partida |
|---|---|
| Muldrotha: magias recastadas (criatura, artefato, encantamento, planeswalker) | 0.54 |
| Muldrotha: terrenos jogados do cemitério (quando o Icetill não está em campo) | 0.19 |
| Six: retraces (cada um descarta um terreno) | 0.30 |
| Icetill Explorer: terrenos jogados do cemitério | 0.74 |
| `recursion_events_total` (inclui as linhas acima + Evolution Witness, Takenuma, Agadeem, Woodland...) | 1.73 |

### Valor da HABILIDADE (base − sem_habilidade, mesmas sementes; pontos percentuais de partidas, exceto onde indicado)

| amostra | n | mesa limpa T7 | T8 | T10 | 1º oponente fora até T6 | oponentes eliminados (média) | contadores +1/+1 | cartas milladas dos oponentes | eu perco por deck-out |
|---|---|---|---|---|---|---|---|---|---|
| todas as partidas | 10000 | +0.08 ± 0.10 | +0.57 ± 0.19 * | +0.60 ± 0.25 * | +0.11 ± 0.06 * | +0.01 ± 0.00 * | +2.83 ± 0.37 * | +1.96 ± 0.32 * | +0.09 ± 0.15 |
| ela entra até T6 | 432 | +1.39 ± 2.13 | +10.88 ± 3.52 * | +5.09 ± 3.24 * | +2.55 ± 1.49 * | +0.03 ± 0.04 | +16.91 ± 3.90 * | +12.01 ± 3.91 * | +0.93 ± 1.70 |
| ela entra até T8 | 1360 | +0.59 ± 0.71 | +4.12 ± 1.38 * | +3.38 ± 1.63 * | +0.81 ± 0.48 * | +0.03 ± 0.02 * | +13.28 ± 2.01 * | +10.28 ± 1.93 * | +0.96 ± 0.88 * |

Partidas com todas as métricas acima idênticas entre `base` e `sem_habilidade`: 8242 de 10000 (82%).

