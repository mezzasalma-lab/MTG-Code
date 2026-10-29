# Mothman: nossa lista × lista do Stefano (2026-10-07)

> Pedido do usuário: comparar a nossa lista com a do Stefano (sem atualização há mais de um ano); o usuário tem Agent Frank Horrigan e The Master, Transcendent e acha que são boas adições. Dados: `../dados/`, scripts: `../orquestracao/`, código: `../codigo/`. A parte 5 (triagem N = 2.000) fica como história; o resultado FINAL (N = 10.000) está no fim.

## 1. Os dois baralhos em números (por script, nomes REAIS resolvidos por set + nº de colecionador, 93 de 93; nenhum `flavor_name`)

| | nossa lista | lista do Stefano |
|---|---|---|
| cartas / nomes distintos | 100 / 91 | 100 / 93 |
| **em comum** (não básicos) | 23 (o comandante + 14 não-terrenos + 8 terrenos) | |
| só numa das listas (não básicos) | 65 (49 não-terrenos + 16 terrenos) | 67 (49 não-terrenos + 18 terrenos) |
| básicos | 5 Forest, 4 Island, 3 Swamp | 3 Forest, 4 Island, 3 Swamp |
| terrenos (slots) | 36 | 36 |
| custo médio dos não-terrenos (X = 0, com o comandante) | 2,95 | 3,19 |
| criaturas (com o comandante) | 32 | 16 |
| Game Changers (Scryfall, ao vivo) | 1 (Fierce Guardianship) | 0 |
| combos (Commander Spellbook, 157 nomes reconhecidos, controles ok) | 2: Bloodchief Ascension + Mindcrank; Altar of Dementia + The Great Henge (+ Glen Elendra) | **0** (15 "quase", entre eles Bloodchief Ascension + Mindcrank: ele tem o Mindcrank e não tem a Ascension) |

**Em comum (23):** The Wise Mothman, An Offer You Can't Refuse, Arcane Denial, Hardened Scales, Mesmeric Orb, Mindcrank, Mirelurk Queen, Nature's Lore, Negate, Nuclear Fallout, Ruin Crab, Sol Ring, Syr Konrad, Wave Goodbye, Winding Constrictor, Bojuka Bog, Breeding Pool, Command Tower, Overgrown Tomb, Rejuvenating Springs, Undergrowth Stadium, Watery Grave, Zagoth Triome.

## 2. Classes funcionais (contagem por oráculo, cartas lidas uma a uma; `resumos/enumeracao_condicoes.txt` tem a triagem por regex, que errou em algumas classes e foi corrigida à mão aqui)

| classe | nossa | Stefano |
|---|---|---|
| **rad counters** (cartas que dão ou citam) | 3: Mothman, Mirelurk Queen, Nuclear Fallout | **14**: + Bloatfly Swarm, Contaminated Drink, Feral Ghoul, Glowing One, Infesting Radroach, Mariposa Military Base, Screeching Scorchbeast, Struggle for Project Purity, Tato Farmer, The Master, Vexing Radgull |
| **proliferate** | 1 (Cankerbloom, sacrifício) | **10**: Agent Frank Horrigan, Atomize, Experimental Augury, Inexorable Tide, Karn's Bastion, Mutational Advantage, Radstorm, Ripples of Potential, Tezzeret's Gambit, Vexing Radgull |
| **amplificador/dobrador de contador +1/+1** | 3 "+1" (Scales, Kami, Constrictor), **0 dobradores** | 2 "+1" (Scales, Constrictor) + **3 dobradores** (Branching Evolution, Loading Zone, The Earth Crystal) |
| **pedras de mana / rampa não-terreno** | Sol Ring + Nature's Lore, Three Visits, Gyre Sage, Kami, Bramble, Broodscale, Freestrider Lookout, Kodama | 8 pedras (Arcane Signet, Chromatic Lantern, Fellwar Stone, Sol Ring, 3 Talismans, Strength Bobblehead) + Nature's Lore, Cultivate, Kodama's Reach, Rampant Growth |
| **remoção pontual** | 2 + Ballista (V.A.T.S., Tear Asunder com kicker) | **7**: Assassin's Trophy, Beast Within, Putrefy, Deadly Rollick, Drown in the Loch, Atomize, Casualties of War |
| varredores | 3 (Toxic Deluge, Nuclear Fallout, Wave Goodbye) | 4 (Nuclear Fallout, Wave Goodbye, Find // Finality, Singularity Rupture) |
| contramágicas | 6 (Offer, Negate, Arcane Denial, Fierce Guardianship, Didn't Say Please, Glen Elendra) | 5 (Offer, Negate, Arcane Denial, Counterspell, Drown in the Loch) |
| **mill do oponente** (motor) | 14 fontes + payoffs de "milled" (Zellix, Alchemist, Konrad, Ascension, Mothman, Queen) | Mindcrank, Mesmeric Orb, Ruin Crab, Konrad, Fractured Sanity (14 de uma vez), Singularity Rupture, Nephalia Drownyard, Raul, Screeching Scorchbeast (tokens por mill) |
| **recursão / reanimação** | Muldrotha, Six, Icetill, Cauldron, Evolution Witness, Agadeem, Takenuma, Hedge Shredder | Reanimate, Rise of the Dark Realms, Find // Finality, Fire Nation Salvagers, Crucible of Worlds, Tato Farmer, The Master |
| proteção do comandante | Heroic Intervention, Smuggler's Surprise, Swiftfoot Boots, Plaza of Heroes, Glen Elendra | Mutational Advantage, Inspiring Call (só quem tem contador) |

**Leitura (raciocinada, a partir dos números acima):** o Stefano montou o Mothman como **deck de rad + proliferate + controle**: 14 cartas de rad, 10 de proliferate, 3 dobradores, 7 remoções pontuais e 8 pedras de mana, com só 16 criaturas e 0 combos. A nossa lista é **deck de mill + contadores + motores de terreno e recursão**: 32 criaturas (corpos para o Mothman pôr contadores em "até X alvos"), 14 fontes de mill no oponente, recursão forte (Muldrotha, Six, Icetill), 2 combos de infinito. As duas listas compartilham o núcleo do comandante (Ruin Crab, Mesmeric Orb, Mindcrank, Konrad, Mirelurk Queen, Scales + Constrictor, Sol Ring, Fallout).


## 3. O que a lista dele tem que a nossa não (relevância pelos MOTORES da nossa lista; raciocinado a partir do oráculo, NÃO medido, exceto Horrigan e Master)

| carta dele | o que faz (oráculo) | onde encaixa nos nossos motores |
|---|---|---|
| **Agent Frank Horrigan** (7) | 8/6 trample; entra ou ataca: **proliferate duas vezes**; indestrutível se atacou neste turno | rad nos oponentes (+2 por gatilho em cada um que já tem), contadores em todas as criaturas (com Scales: +2 por passada), quest counters da Ascension, The Great Henge custa `{G}{G}`. **Medido, ver §4** |
| **The Master, Transcendent** (4) | ao entrar: 2 rad num jogador; `{T}`: leva criatura milada neste turno, de QUALQUER cemitério, como Mutant 3/3 | é a nossa Mirelurk Queen (2 rad) + reanimação de mill. **Medida, ver §4** |
| **Fractured Sanity** (UUU) | cada oponente **mila 14**; ciclar `{1}{U}`: mila 4 | 42 cartas milladas de uma vez: Mothman (X ≈ 27, limitado pelos corpos), Konrad (≈ 0,28 × 42 ≈ 12 pings em cada oponente), Zellix, Alchemist, Ascension armada, Mirelurk Queen |
| **Screeching Scorchbeast** (6) | 5/5 voa menace; ataca: **cada jogador 2 rad**; mill de não-terreno: cria **tantos Zumbis Mutant 2/2 quantas cartas** (1×/turno) | corpos para o "até X alvos" do Mothman; os Zumbis combinam com o **Undead Alchemist** (dano de Zumbi vira mill) |
| **Inexorable Tide** (3UU) | toda magia que você conjura: proliferate | rad nos oponentes e contadores a cada magia (a lista tem 29 não-terrenos de custo ≤ 2) |
| **Branching Evolution / Loading Zone / The Earth Crystal** | dobram os contadores +1/+1 nas suas criaturas | a lista tem 3 "+1" e **0 dobradores** (auditoria §5). O medidor **não valoriza crescer contadores** (candidatas §0b: cortar o Hardened Scales não mexe a velocidade) |
| Atomize, Experimental Augury, Tezzeret's Gambit, Radstorm, Ripples of Potential, Mutational Advantage, Karn's Bastion | proliferate "de graça" em magia/terreno | só 1 proliferate hoje (Cankerbloom). O pacote antigo já tinha Evolution Sage + Karn's Bastion (`candidatas-pos-eoe.md`) |
| **Assassin's Trophy, Putrefy, Beast Within, Deadly Rollick, Casualties of War, Drown in the Loch** | remoção pontual, a maioria instantânea | a **lacuna estrutural da nossa lista** (auditoria §4: 2 remoções pontuais + Ballista). Estrutural para o simulador: ele não modela o tabuleiro do oponente |
| **Arcane Signet, 3 Talismans, Chromatic Lantern, Fellwar Stone** | pedras de mana/fixação | a nossa lista só tem Sol Ring de pedra; os Talismans de B/G, U/B e G/U fixam as cores apertadas (G e U) |
| Reanimate, Rise of the Dark Realms, Find // Finality, Fire Nation Salvagers, Crucible of Worlds | reanimação / terreno do cemitério | os cemitérios dos oponentes ficam cheios pelo nosso mill; a recursão nossa (Muldrotha, Six, Icetill) já é forte |
| Glowing One, Infesting Radroach, Feral Ghoul, Bloatfly Swarm, Vexing Radgull, Struggle for Project Purity, Tato Farmer, Contaminated Drink, Mariposa | mais fontes de rad | só 3 fontes de rad na nossa lista; mas **rad também mila VOCÊ** (cada jogador recebe) |

## 4. O que a nossa lista tem que a dele não

- **2 combos** (Ascension + Mindcrank, Altar of Dementia + Great Henge + Glen Elendra) e 1 Game Changer; ele tem 0 e 0.
- **Recursão forte** (Muldrotha, Six, Icetill, Agatha's Soul Cauldron, Evolution Witness, Takenuma, Agadeem) e **motores de terreno** (3 fetches, Fabled Passage, Hedge Shredder, Gitrog, Kodama, Urza's Saga, Strip Mine).
- **32 criaturas contra 16**: o Mothman põe 1 contador por criatura-alvo (até X alvos), então corpos importam; com 16 criaturas o X sobra.
- **Payoffs de "milled" e de contador** que ele não tem: Zellix, Undead Alchemist, Psychic Corrosion, Memory Erosion, Altar of the Brood, Danny Pink, Fathom Mage, Gyre Sage, Herd Baloth, Hollowmurk Siege, Basking Broodscale, Ouroboroid, Kami.
- **Proteção de verdade**: Heroic Intervention, Smuggler's Surprise, Swiftfoot Boots, Plaza of Heroes.


## 5. Agent Frank Horrigan e The Master, Transcendent no nosso deck (oráculo + rulings lidos ANTES do código; `dados/rulings_candidatas.json`)

**Spellbook** (`resumos/resumo_spellbook.md`; 157 nomes reconhecidos, controle positivo e de corte passaram): nenhuma das duas cria combo novo nem "quase" novo; só as 5 peças dos dois combos da lista (Altar of Dementia, Bloodchief Ascension, The Great Henge, Mindcrank, Glen Elendra Archmage) derrubam combo se cortadas.

**Implementação (todas as cláusulas):** Horrigan: 7 de mana 8/6 trample; entrar OU atacar: `proliferate` ×2 (duas escolhas independentes; política: tudo que ajuda, nunca rad nem lore da Urza's Saga próprios); indestrutível só no turno em que atacou (ruling: vale desde declarado atacante, não vale se entrou atacando); The Great Henge fica em `{G}{G}`. Master: `{1}{B}{G}{U}` 2/4 artefato-criatura; entrar: 2 rad num oponente; `{T}`: criatura **milada neste turno** (só "mill", não descarte; qualquer cemitério) volta ao campo sob meu controle como Mutant verde com **base 3/3** (sobrepõe a CDA; contadores continuam valendo; perde os outros tipos, `Zombie`/`Insect` incluídos), com doença de invocação (Swiftfoot Boots dá haste) e também no turno do oponente depois do rad dele. **Conceitos compartilhados auditados (Regra #3):** `power()`/`toughness()` (2 pontos), checagens de subtipo (3 pontos: Alchemist ×2, Swarmyard), Wave Goodbye (a criatura de oponente volta à mão DELE), `remove_permanent` (volta ao cemitério DELE), lista de alvos da remoção de oponente na resiliência. 182 testes dirigidos passam (16 novos).

**Amplificadores de contador (Hardened Scales, Kami of Whispered Hopes e Winding Constrictor, os três "+1" da lista) somam com o proliferate do Horrigan:** num gatilho (2 passadas), um contador vira 3 sem amplificador, 5 com qualquer um dos três e **9 com os três juntos** (+4 por passada; medido em `codigo/mothman_goldfish_v1_HM.py`, conta direta). A diferença para a lista do Stefano não é ter ou não amplificadores (nós 3 "+1", ele 2), é que ele tem 3 dobradores e nós 0.

**Estrutural (📊):** a criatura de OPONENTE que a Master leva é, no simulador, um corpo genérico 3/3 sem habilidades (as cartas do oponente são só "terreno / criatura / outra"): "It's a green Mutant with base power and toughness 3/3" mantém as **habilidades** da carta, que não são modeladas. O valor medido da Master é, portanto, **piso**.

### Triagem (N = 2.000 pareado, `no lugar`, 21 cortes; padrão / resiliência; pontos percentuais de mesa limpa; `*` = excede o IC95%)


### Resultado FINAL (N = 10.000 pareado, `no lugar`, sementes 3.000.000+i, 12 turnos; mesa limpa até T8 em pontos percentuais, `*` = excede o IC95%; tabelas completas em `tabela_final.md`)

**Agent Frank Horrigan** (padrão / resiliência): ← Offer **+2,37 ± 0,37 \* / +0,98 ± 0,30 \***; ← Didn't Say Please +2,27 / +0,93; ← Negate +2,25 / +1,03; ← Wave Goodbye +2,07 / +0,94; ← Toxic Deluge +1,74 / +1,04; ← Tear Asunder +1,76 / +1,07; ← Arcane Denial +1,66 / +0,65; ← Cold-Eyed Selkie +1,48 / +0,71; **← Kozilek +0,87 ± 0,39 / +0,58, mas T10 −1,19 ± 0,39 \* e deck-out +1,68 ± 0,38 \* (padrão)**. Todos os outros cortes também **reduzem** o deck-out (−0,5 ponto).
- **O valor é o proliferate, não o corpo:** sem o proliferate (`HORRIGAN_PROLIF_TIMES = 0`, só o 8/6 trample) ← Negate dá **+0,15 ± 0,31** (padrão) e −0,06 ± 0,25 (resiliência), contra +2,25 e +1,03 com ele. Rad nos oponentes: +0,79 de rad médio por partida.
- **Quando entra até T6** (≈ 320–365 partidas de 10.000, 3,3%): **+17 a +26 pontos** de mesa limpa até T8 no padrão (ex.: ← Offer +22,9 ± 4,8; ← Didn't Say Please +25,9 ± 4,9) e +15 a +23 na resiliência. Ele só é conjurado em **22%** das partidas (19% na resiliência), ataca 0,15 vez por partida e cada ataque causa ≈ 14 de dano (o 8 base + contadores).
- **Não cresce junto com o Monument/Jace?** NÃO medido junto (as vagas são as mesmas: Offer, Negate, Didn't Say Please, Wave Goodbye, Deluge).

**The Master, Transcendent** (padrão / resiliência): ← Negate **+0,36 ± 0,33 \* / +0,05 ± 0,27**; ← Offer +0,26 / +0,09; ← Tear Asunder −0,25 / −0,14; ← Wave Goodbye +0,02 / −0,26 \*. **Neutra** na velocidade. Ativa 0,20 vez por partida (0,14 em criatura minha, 0,05 em criatura de oponente) e põe +0,45 de rad médio por partida (os 2 rad ao entrar).
- Tirar a criatura de oponente (`MASTER_TAKE_OPP = False`) ou ativar só no meu turno quase não muda nada (+0,42 / +0,36 contra +0,36). **Quando entra até T6** (≈ 600–800 partidas): ← Negate +3,7 ± 3,3, ← Offer +4,0 ± 3,0 (padrão), ~ +2 na resiliência (no limite do IC).
- **Juntos** (Offer → Horrigan e Negate → Master): +2,65 ± 0,48 (padrão) / +0,98 ± 0,39 (resiliência), contra +2,37 / +0,98 do Horrigan sozinho: a Master acrescenta ≈ +0,3 (no ruído).
- **Piso, não teto:** a criatura de oponente que a Master leva é um 3/3 genérico sem as habilidades da carta real. O valor real (levar um bomba milado do cemitério do oponente) NÃO está medido.

**Leitura (raciocinada):** o Horrigan entra bem porque a lista JÁ tem os três amplificadores e a mesa cai por rad + perda de vida: cada gatilho dele põe +2 rad em cada oponente que já tenha e +4 contadores por criatura (com Scales, Kami e Constrictor). Por isso o melhor corte é o que menos mexe nesses motores (Offer, Didn't Say Please, Negate, Wave Goodbye). O Kozilek não é corte (o seguro contra decking vale mais que os +0,87). A Master é boa mas não muda a velocidade; ela serve mais como **recursão de mill** (levar a criatura milada) do que como motor de rad (2 rad = o que a Mirelurk Queen já dá).

