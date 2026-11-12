# Taxas de interacao do oponente do playtester (5 goldfish manuais do Tam)

Cada carta que aparece na zona `opponentsCards` do log e' um evento. **Turno** = o bloco do log (o turno do usuario + os turnos de oponente que vem depois dele, ate' o proximo untap dele).

| log | turnos | eventos | por turno |
|---|---|---|---|
| #1 | 10 | 6 | 0.60 |
| #2 | 8 | 3 | 0.38 |
| #3 | 7 | 3 | 0.43 |
| #4 | 10 | 6 | 0.60 |
| #5 | 11 | 6 | 0.55 |
| **total** | **46** | **24** | **0.52** |

## Por turno (todos os logs juntos)

| turno | logs com esse turno | eventos | por log | cartas |
|---|---|---|---|---|
| T1 | 5 | 0 | 0.00 | — |
| T2 | 5 | 0 | 0.00 | — |
| T3 | 5 | 0 | 0.00 | — |
| T4 | 5 | 3 | 0.60 | Nature's Claim (#1), Zombie (#2), Warrior (#3) |
| T5 | 5 | 5 | 1.00 | Assassin's Trophy (#1), Metallic Sliver (#3), Graveborn (#4), Vex (#4), Goblin Wizard (#5) |
| T6 | 5 | 6 | 1.20 | Golem (#1), Carnivore (#2), Disenchant (#3), Junji, the Midnight Sky (#4), Ertai's Scorn (#5), Promise of Loyalty (#5) |
| T7 | 5 | 2 | 0.40 | Murderous Rider // Swift End (#2), Split Up (#4) |
| T8 | 4 | 4 | 1.00 | Witness Protection (#1), Doombot (#1), Spider (#4), Loran of the Third Path (#5) |
| T9 | 3 | 3 | 1.00 | Aetherize (#1), Cleansing Nova (#4), Damning Verdict (#5) |
| T10 | 3 | 1 | 0.33 | Eldrazi Angel (#5) |
| T11 | 1 | 0 | 0.00 | — |

## Por categoria, de T4 em diante (nenhum evento antes do T4 nos 5 logs)

Exposicao: 31 turnos (T4 ate' o fim de cada log). Taxa = eventos por turno do usuario (a mesa inteira, 3 oponentes); IC95% de Poisson (Garwood).

| categoria | eventos | por turno | IC95% | por partida de 12 turnos (T4-T12 = 9 turnos) |
|---|---|---|---|---|
| criatura | 11 | 0.355 | 0.177–0.635 | 3.19 (1.59–5.71) |
| remocao_pontual | 5 | 0.161 | 0.052–0.376 | 1.45 (0.47–3.39) |
| contramagia | 2 | 0.065 | 0.008–0.233 | 0.58 (0.07–2.10) |
| efeito_em_massa | 5 | 0.161 | 0.052–0.376 | 1.45 (0.47–3.39) |
| aura | 1 | 0.032 | 0.001–0.180 | 0.29 (0.01–1.62) |
| total | 24 | 0.774 | 0.496–1.152 | 6.97 (4.46–10.37) |

Antes do T4: 0 eventos em 15 turnos (T1-T3 dos 5 logs).
