# Ledger da partida manual do Mothman (2026-10-06)

Leitura minha do trace (`resumos/trace.md`); cada atribuicao de contadores por evento foi conferida por `assert` contra os contadores do log por turno. **Limites:** o log nao registra vida, marcadores de rad, mana flutuante nem a ordem da pilha.

## 1. Mill meu: fontes que as regras exigem x cartas milladas no log

| T | no log (cartas milladas) | fontes esperadas | esperado (min) | diferenca |
|---|---|---|---|---|
| T1 | 0 | nenhuma | 0 | ok |
| T2 | 0 | nenhuma | 0 | ok |
| T3 | 3 (Kodama of the West Tree, Island, Toxic Deluge) | Six ataca (3) | 3 | ok |
| T4 | 3 (Bramble Familiar // Fetch Quest, Icetill Explorer, Forest) | Six ataca (3) | 3 | ok |
| T5 | 2 (Waterlogged Grove, Ashiok, Dream Render) | rad (>= 1: Mothman entrou no T4) + landfall do Icetill (Swamp do cemiterio) (1) | >= 2 | ok |
| T6 | 3 (Ruin Crab, Hardened Scales, Smuggler's Surprise) | rad (>= 1: ataque do Mothman no T5 deu +1) + landfall do Icetill (Overgrown Tomb) + Hedge Shredder ataca (2) | >= 4 | **faltam >= 1** |
| T7 | 3 (Agatha's Soul Cauldron, Hollowmurk Siege, Forest) | landfall do Icetill (Forest posta pelo Shredder) + Hedge Shredder ataca (2) + rad (0 a 2, depende dos mills do T6) | 3 | ok |
| T8 | 1 (Palantír of Orthanc) | landfall do Icetill (Urza's Saga) + rad (>= 1: o ataque do Mothman no T7 deu +1 e a Evacuation nao tira marcador de rad) | >= 2 | **faltam >= 1** |
| T9 | 1 (Polluted Delta) | rad (>= 1: o ETB do Mothman no T8 deu +1; nenhum terreno entrou) | >= 1 | ok |

Total T3-T9: **16 no log x >= 18 esperadas**. T5 bate (o usuario contou rad E landfall: 2 cartas). **T6 e T8 ficam abaixo, e e' limite inferior firme** (T6: o ataque do Mothman no T5 garante rad >= 1; T8: o ataque do T7 garante rad >= 1): falta pelo menos 1 mill meu em cada um, rad ou landfall do Icetill (a posicao das cartas no log nao permite dizer qual). T7 bate so' se o rad estava em 0 (depende de quais cartas o mill do rad do T6 tirou).

## 2. Contadores +1/+1: regras x log (com Kami e Hardened Scales)

Regra: cada gatilho do Mothman poe um contador em ate X criaturas-alvo (X = nao-terrenos milados); o Kami (e o Scales, quando em campo) somam +1 a CADA colocacao, inclusive no proprio Kami.
`esperado` = min(X, alvos) x (1 + Kami + Scales). Para mill de oponente, X vem de Monte Carlo (200.000 amostras, 62 nao-terrenos em 99).

| T | evento | X (nao-terrenos) | alvos | Kami / Scales | contadores esperados | no log | observacao |
|---|---|---|---|---|---|---|---|
| T4 | Six ataca (mill 3) | 2 | 3 | 1 / 0 | 4.0 | 0 | Mothman ja' em campo (conjurado antes do ataque); alvos: Mothman, Six, Kami |
| T5 | mill de 1 carta com nao-terreno (Ashiok); a outra (Waterlogged Grove) e' terreno | 1 | 4 | 1 / 0 | 2.0 | 1 | Kami recebeu o contador; alvos: Mothman, Six, Kami, Icetill |
| T6 | landfall do Icetill (Overgrown Tomb): Ruin Crab milado | 1 | 4 | 1 / 0 | 2.0 | 1 | Mothman recebeu o contador; alvos: Mothman, Six, Kami, Icetill |
| T6 | Hedge Shredder ataca (mill 2) | 2 | 6 | 1 / 0 | 4.0 | 2 | Kami e Mothman receberam 1 cada; alvos: Mothman, Six, Kami, Icetill, Ruin Crab, Shredder (tripulado) |
| T6 | Memory Erosion: o oponente simulado conjura Aven Mindcensor (milla 2) | 1.25 medio (P(X=0) = 14.0%) | 6 | 1 / 0 | 2.5 | 0 | nao esta no log |
| T7 | Generous Patron: support 2 (nao e' gatilho do Mothman) | 2 (support) | 5 | 1 / 0 | 4.0 | 2 | Icetill e Ruin Crab receberam 1 cada |
| T7 | Agatha's Soul Cauldron milado (fonte nao identificada: rad?) | 1 | 6 | 1 / 0 | 2.0 | 1 | Six recebeu o contador |
| T7 | Hedge Shredder ataca (mill 2: Hollowmurk Siege + Forest) | 1 | 7 | 1 / 0 | 2.0 | 0 | NENHUM contador no log depois deste mill |
| T7 | Ruin Crab: Forest entra (Shredder) e cada oponente milla 3 | 5.64 medio (P(X=0) = 0.0%) | 7 | 1 / 0 | 11.1 | 0 | nao esta no log |
| T7 | Memory Erosion: o oponente simulado conjura Evacuation (milla 2); resolve ANTES da Evacuation | 1.25 medio (P(X=0) = 14.0%) | 5 | 1 / 1 | 3.8 | 0 | Scales ja' em campo (retrace); contadores iriam para criaturas que a Evacuation devolve em seguida |
| T8 | landfall do Icetill (Urza's Saga do cemiterio): Palantir milado | 1 | 3 | 0 / 1 | 2.0 | 0 | Kami esta na mao (devolvido pela Evacuation); NENHUM contador no log |
| T8 | Ruin Crab: Urza's Saga entra e cada oponente milla 3 | 5.64 medio (P(X=0) = 0.0%) | 3 | 0 / 1 | 6.0 | 0 | nao esta no log |

**Total: 7 contadores no log x 45.3 esperados pelas regras.** Desta diferenca, 23.3 vem dos eventos de mill de OPONENTE (que o log nao registra: o usuario ja' avisou); o resto (15.0) sao colocacoes que o log mostra **sem** a substituicao do Kami / sem o gatilho.

### O que o log PROVA sozinho (so' mill meu e Patron; zero dependencia do mill de oponente)

- 8 eventos; contadores exigidos pelas regras: **22**; postos no log: **7**.
- Colocacoes feitas com o Kami em campo: **7** (T5: 1, T6: 3, T7: 3); em todas o log mostra +1 onde a regra manda +2 (Kami). Diferenca so' do Kami: 7 contadores.
- Gatilhos do Mothman por mill MEU **sem nenhum contador no log**: T4 (X = 2), T7 (Hollowmurk Siege, X = 1) e T8 (Palantir, X = 1).

## 3. Mill de oponente reconstruido (o log nao o contem)

| T | fonte | cartas milladas (todos os oponentes) | nao-terrenos esperados |
|---|---|---|---|
| T6 | Memory Erosion: o oponente simulado conjura Aven Mindcensor (milla 2) | 2 | 1.3 |
| T7 | Ruin Crab: Forest entra (Shredder) e cada oponente milla 3 | 9 | 5.6 |
| T7 | Memory Erosion: o oponente simulado conjura Evacuation (milla 2); resolve ANTES da Evacuation | 2 | 1.3 |
| T8 | Ruin Crab: Urza's Saga entra e cada oponente milla 3 | 9 | 5.6 |
| | **total** | **22** | **13.8** |

O log nao mostra essas cartas nem os 4 gatilhos extras do Mothman. Cada gatilho do Ruin Crab milla 3 de CADA oponente (3 oponentes) e dispara o Mothman uma vez.

## 4. Jogadas de terreno (Icetill Explorer: +1 jogada e terrenos do cemiterio) x Ruin Crab em campo

| T | jogadas disponiveis | usadas (mao / cemiterio) | Ruin Crab em campo na hora | terrenos disponiveis nao jogados | gatilhos do Crab perdidos |
|---|---|---|---|---|---|
| T1 | 1 | 1 (Misty) | nao | (todas usadas) | 0 |
| T2 | 1 | 1 (Strip Mine) | nao | (todas usadas) | 0 |
| T3 | 1 | 1 (Watery Grave) | nao | (todas usadas) | 0 |
| T4 | 1 | 1 (Island) | nao | (todas usadas) | 0 |
| T5 | 2 | 2 (Forest da mao; Swamp do cemiterio) | nao | (todas usadas) | 0 |
| T6 | 2 | 1 (Overgrown Tomb) | so' depois (retrace do Crab) | Takenuma (mao); Misty, Waterlogged Grove, Urza's Saga (cemiterio) | 1 |
| T7 | 2 | 0 (a Forest veio do Shredder: nao e' jogada) | sim | Takenuma (mao); Misty, Waterlogged Grove, Urza's Saga (cemiterio) | 2 |
| T8 | 2 | 1 (Urza's Saga do cemiterio) | sim (recem-conjurado) | Agadeem (MDFC, mao); Misty, Waterlogged Grove, Takenuma (cemiterio) | 1 |
| T9 | 2 | 0 ate o fim do log (o log termina apos o ataque) | sim | Agadeem (mao); Misty, Waterlogged Grove, Takenuma, Polluted Delta (cemiterio) | 2 |

Gatilhos do Ruin Crab que **ocorreram** na partida (reconstruidos): 2 (T7, T8). Perdidos por jogada de terreno nao usada com o Crab em campo: **6** (T6-T9; no T9 o log para antes da fase principal 2). Cada um valeria 9 cartas milladas e 1 gatilho do Mothman, alem de 1 mill meu do Icetill; jogar a Misty do cemiterio e quebra-la ainda somaria 1 landfall extra (a Misty entra, depois o terreno buscado entra).

## 5. Six em campo e desvirada que nao atacou

- T5: desvirou no inicio; so' o Mothman virou (ataque).
- T6: desvirada o turno inteiro (Hedge Shredder atacou, tripulado pelo Icetill).
- T7: com 1 contador; so' Mothman e Shredder atacaram.

Cada ataque da Six = 1 evento de mill meu de 3 cartas (gatilho do Mothman com X = nao-terrenos), mais 1 terreno para a mao; com o Hedge Shredder em campo, terreno milado ainda entra em campo (landfall do Crab/Icetill). Foram 3 turnos (T5-T7) sem esse ataque. **Nao e' erro de regra** (atacar e' escolha); fica como pergunta ao usuario.
