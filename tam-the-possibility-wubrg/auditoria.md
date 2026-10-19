# Tam, the Possibility (WUBRG): auditoria estática — 2026-10-19

> Auditoria feita ao registrar o deck (Regra 2 de `user-standing-rules.md`: "sempre que eu adicionar um deck aqui RODE A AUDITORIA COMPLETA"). **Simulador: NÃO feito, a pedido do usuário** ("Registra ele e não faça o simulador ainda"). Tudo abaixo vem de consulta ao vivo (Scryfall, Commander Spellbook, EDHREC) e de contas sobre esses dados; nada foi simulado.
> Tabelas completas e a lista de cartas por varredura: `resultados-ab/2026-10-19-registro/resumos/analise_estatica.md`. Dados brutos, scripts e como refazer: `resultados-ab/2026-10-19-registro/LEIAME.md`.

## 1. Resumo

- **Registrado e legal:** 1 comandante + 99 cartas + 13 de sideboard, 113/113 linhas resolvidas no Scryfall por set + nº de colecionador; **0 carta fora da identidade de cor** (WUBRG), **0 ilegal em Commander**, 0 duplicada, **0 Game Changer** (campo `game_changer` do Scryfall, deck e sideboard). Nenhum nome de capa diferente do real (`nomes-de-capa.md`).
- **O deck:** superfriends WUBRG em volta de **Tam, the Possibility** ({1}{G}{U}, criatura lendária, Reality Fracture, lançada em 2026-10-02): "Planeswalker spells you cast cost {1} less" e `{W}{U}{B}{R}{G}, {T}`: proliferate X vezes, X = número de **tipos de planeswalker** entre os que você controla. **25 planeswalkers** (EDHREC: média de 21) com **21 tipos distintos** + a ficha de **Jace** que as 10 cartas "empower Jace" de Reality Fracture criam.
- **Combos no Commander Spellbook: 2**, mas só um é executável como listado e **nenhum é provável cedo** (≤ 3,6% até o T12 com todas as peças já vistas; item 5). **Bracket:** sem Game Changers, sem destruição em massa de terrenos, 1 carta de turno extra, 3 cartas de busca; EDHREC: 567 dos 932 decks do Tam com bracket declarado estão no 3 (item 7).

## 2. Checklist de `commander-rules.md#analise`

| item | resultado |
|---|---|
| Identidade de cor | WUBRG; 100/100 dentro (deck e sideboard) |
| Terrenos | **36** (EDHREC: média 35), **nenhum básico** (EDHREC: 9); 14 sempre desvirados, 7 choques (2 de vida ou virado), 6 sempre virados (5 triomes + The World Tree), 4 lentos (desviram com 2+ oponentes: sempre numa mesa de 4), 4 fetches, 1 que vira a partir do 4º turno (Starting Town) |
| Curva | não-terrenos **MV médio 3,81** (mediana 4): MV1 5, MV2 8, MV3 17, MV4 11, MV5 13, MV6 6, MV7 2, MV9 1. Planeswalkers: média 4,52, **3,56 com a Tam em campo** ("`{1}` a menos" só reduz o genérico) |
| Ramp | 16 na categoria do usuário: 10 rochas e criaturas de mana (Sol Ring, Arcane Signet, Fellwar Stone, Chromatic Orrery, Birds of Paradise, Noble Hierarch, Ignoble Hierarch, Bloom Tender, Faeburrow Elder, Leyline Immersion, esta é uma aura que só vai em criatura lendária), 4 planeswalkers (Garruk Wildspeaker, Domri Chaos Bringer, Chandra Legacy of Fire, Wrenn and Realmbreaker) e 2 encantamentos (Way of the Paradox, Way of the Pyromancer) |
| Compra | 11 na categoria "Draw" (Dack, Dihada, Garruk Curse Breaker, Minsc & Boo, Narset, Oath of Nissa, Dellian Fel, Tamiyo, os dois Teferi, Way of the Mind Sculptor), mais Aminatou (`+1`), Staff of Compleation e Vraska (`0`) |
| Remoção | 9 na categoria; **6 efeitos em massa** (Blasphemous Act, Overwrite the Multiverse, Elspeth Sun's Champion −3, Ajani Unrelenting −3, The Eternal Wanderer −4, Garruk Veiled Butcher −2); remoção pontual só em planeswalker (Dellian Fel −3, Oko, Nissa −1, Garruk −2/+2...). **Só 1 instantâneo (Ripples of Potential) e 0 contramágicas** (varredura de `counter target`) |
| Proteção | 5 (Liliana's Talent, Onakke Oathkeeper, Ripples of Potential, Sanctum Lurker, Vronos) |
| Vitória | sem um combo montado: vias que o oráculo dá (não testadas): **All Will Be One** (dano a cada vez que você põe contador, e cada ativação de lealdade põe), **Chandra, Legacy of Fire** (X de dano a cada oponente no fim do turno, X = planeswalkers), **Sanctum Lurker** (todo planeswalker ganha `+2`: 1 de dano a cada oponente), emblemas e ultimates, fichas (Elspeth, Ajani, Garruk, Beasts, Cadets) e o **turno extra** do Ichormoon Gauntlet (`−12`) |
| Sinergia interna | a Tam e as cartas "empower Jace" empurram o X da proliferate; Ichormoon Gauntlet, Flux Channeler, Staff of Compleation, Dreamtide Whale, Patrolling Peacemaker, Ripples of Potential e Vraska proliferam; Chain Veil / Oath of Teferi / Teferi Temporal Archmage ativam planeswalkers de novo |
| Preço | não calculado (o usuário joga com proxies; não pedido) |
| Bracket | item 7 |

## 3. Base de mana (Regra 6: fixers flexíveis contam)

Fontes por cor (terrenos + 4 fetches + Arcane Signet, Birds, Noble Hierarch, Ignoble Hierarch; **sem** os condicionais): **W 17, U 20, B 16, R 17, G 33** (`analise_estatica.md` §4). A **B é a cor mais curta** (16) e **G a mais folgada** (33, ajudada pela Yavimaya, que faz todo terreno ser Forest). Probabilidade de ≥ 1 fonte da cor entre as cartas vistas até o T4: W 86,3%, U 90,8%, B 84,4%, R 86,3%, G 98,6% (uma cor por vez; **não** é a conjunta das cinco, que a ativação da Tam pede). Condicionais fora da conta: Plaza of Heroes e Great Hall (qualquer cor só para magia lendária, e todo planeswalker e as 8 "Way of…" são lendários), Exotic Orchard e Fellwar Stone (cores de terrenos de **oponente**), Bloom Tender e Faeburrow Elder, Chromatic Orrery, Wrenn and Realmbreaker, The World Tree.
As fetches **só acham terreno com tipo** (não há básico): Misty Rainforest 12 alvos, Verdant Catacombs, Windswept Heath e Wooded Foothills 10 cada; com a **Yavimaya, Cradle of Growth** em campo, qualquer terreno. Pagamento de vida em terrenos: 7 choques (2), 4 fetches (1), Starting Town (1), City of Brass (1 de dano por virada).

## 4. Tam e os tipos de planeswalker

X da Tam = tipos de planeswalker entre os planeswalkers que você controla: **21 tipos** no deck (Ajani, Aminatou, Chandra, Dack, Dellian, Dihada, Domri, Elspeth, Garruk, Kasmina, Minsc, Narset, Nissa, Oko, Saheeli, Tamiyo, Teferi, Tezzeret, Vraska, Vronos, Wrenn), 22 com a ficha de **Jace**. **The Eternal Wanderer não tem subtipo e não conta**; Garruk (3 cartas) e Teferi (2) contam um tipo cada. O X real é o que estiver em campo: com 4 planeswalkers de tipos diferentes em jogo a Tam faz 4 proliferates por ativação.

## 5. Combos (Commander Spellbook, com a probabilidade real, Regra 7)

116 nomes resolvidos (**0 não reconhecidos**, incluindo o comandante de 2026-10-02), controle positivo e de corte ok (`resumos/log_spellbook_tam.txt`). Achados:
1. **Teferi, Temporal Archmage + The Chain Veil:** o passo-a-passo do próprio Spellbook inclui **recastar o Teferi da zona de comando**; aqui o comandante é a Tam e o Teferi está nos 99, então o laço infinito **não fecha como listado** (sem o recast ele gasta 1 de lealdade por volta e termina em 0). O deck tem fontes de lealdade (proliferate da Tam, Gauntlet, Teferi's Talent...) que **podem** repor isso: **não verificado**.
2. **Chromatic Orrery + Tezzeret the Seeker + The Chain Veil:** infinito de mana e ativações (Orrery `{C}`×5 − `{4}` do Veil, `+1` do Tezzeret desvira os dois); sem requisito de zona de comando.
**Probabilidade de ter todas as peças já vistas** (7 + 1 por turno a partir do T2, sem mulligan e sem tutor): T6 **1,49%** (qualquer dos dois), T8 **2,08%**, T10 **2,78%**, T12 **3,59%**; o de 3 cartas sozinho 0,14% / 0,23% / 0,36% / 0,52%. Mana das peças: Orrery 7 + Veil 4 + Tezzeret 5 (4 com a Tam). **Tutores que mudam a conta, que o Spellbook não conta:** Tezzeret the Seeker (`−4` busca o Veil) e Entrust the Spark (sacrifica um planeswalker e busca outro). Nenhum é um combo cedo e provável; **não muda o Bracket pelo critério do jogo de turno/probabilidade**.
**"Quase" (a uma carta): 92.** Um deles tem a peça no **sideboard**: **Vorinclex, Monstrous Raider + Vraska, Betrayal's Sting → "target opponent loses the game"** (Spellbook, bracket S). Se o Vorinclex entrar no deck, vira um combo de **2 cartas** (Vraska já está nos 99).

## 6. Pontos de atenção (fatos; **nenhuma troca sugerida**, o usuário não pediu)

- **Interação a velocidade de instantâneo é quase nula:** 1 instantâneo e 0 contramágicas contra 7 instantâneos de média no EDHREC; a remoção é de planeswalker e de feitiço, lenta.
- **Pouco corpo:** 12 criaturas (média EDHREC 14) para proteger 25 planeswalkers; as 6 remoções em massa do próprio deck também varrem o seu campo (Overwrite exila todas as criaturas e dá lealdade à ficha de Jace).
- **Vida como recurso:** os terrenos acima + Staff of Compleation (1 a 4 de vida por ativação), The Chain Veil (perde 2 se não ativou lealdade no turno), Vraska 0 e Dellian Fel 0 (perdem 1), Nissa e Vraska (mana Phyrexian, 2 de vida por `{G/P}`/`{B/P}` pago assim, e entram com 2 de lealdade a menos).
- **Mana de cinco cores sem básicos:** a B é a mais curta (16 fontes); a ativação da Tam pede as cinco cores no mesmo turno.
- **EDHREC** (6.931 decks do Tam em 2026-10-19; `analise_estatica.md` §5): cartas de inclusão ≥ 30% que **não estão** nem no deck nem no sideboard (fora os básicos): ver a lista lá (Loyal Tutor 65%, Commodore Guff 64%, Nicol Bolas Dragon-God 64%, Carth the Lion 62%, The Theorist Jace Beleren 62%, Chromatic Lantern 57%, Doubling Season 53%...). **Isto é informação, não recomendação:** a Regra #4 de `CLAUDE.md` exige comparar com os motores do deck antes de qualquer troca. As 19 cartas do deck que o EDHREC não lista incluem Displacer Kitten, Garruk Wildspeaker, Nissa Ascended Animist, Staff of Compleation e vários terrenos.

## 7. Bracket (estimativa; o texto oficial dos Brackets NÃO foi consultado nesta rodada)

Fatos medidos: **0 Game Changers** (Scryfall, deck e sideboard); 0 destruição em massa de terrenos; 1 carta de turno extra (Ichormoon Gauntlet, via `−12` de um planeswalker); 3 cartas de busca não-terreno (Entrust the Spark, Kasmina, Tezzeret); sem contramágica; **sem combo infinito cedo e provável** (item 5); 6 efeitos de remoção em massa. EDHREC: 932 decks com bracket declarado, **B3 567 (61%)**, B2 187, B4 152, B1 16, B5 10. Estimativa de trabalho: **Bracket 3**; confirmar com o texto oficial antes de levar a uma mesa.

## 8. O que NÃO foi feito / verificado (Regra #7)

- **Sem simulador** (pedido do usuário): nada de velocidade, linhas de jogo, mulligan, resiliência ou interação foi medido. Quando o simulador for feito valem as Regras #1 a #10 de `CLAUDE.md`, em especial: clausula-a-cláusula das 100 cartas com **rulings lidas antes** (há várias cartas de Reality Fracture novas, "empower Jace", "Compleated", "Vivid", "Warp"-like, e Phyrexian mana em Nissa e Vraska) e o conceito compartilhado "tipos de planeswalker" (o X da Tam).
- Preço, o texto oficial dos Brackets e a probabilidade **conjunta** das cinco cores não foram calculados. As varreduras de oráculo da §7 de `analise_estatica.md` são heurísticas (regex), não listas exaustivas.
- O snapshot do EDHREC é de 2026-10-19 (comandante com 2,5 semanas); os números mudam.
