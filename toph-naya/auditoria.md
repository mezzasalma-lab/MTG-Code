# Auditoria — Toph, the First Metalbender (Naya — R/G/W)

Fontes usadas nesta auditoria: Scryfall REST API (`cards/collection` para as 97 cartas únicas da lista, `cards/search?q=is:gamechanger`, campos `legalities.commander`, `color_identity`, `oracle_text`, `type_line`, `produced_mana`, `cmc`), consultada em 2026-08-22. EDHREC (`json.edhrec.com/pages/commanders/toph-the-first-metalbender.json`), consultado em 2026-08-22. Definições de Bracket: `references/commander-rules.md#brackets` do skill mtg-commander (fonte primária: anúncios oficiais da Wizards).
Data da auditoria: 2026-08-22

---

## 0. Achado crítico — carta banida em Commander

**Primeval Titan está BANIDA em Commander.** Confirmado ao vivo via Scryfall (`legalities.commander: "banned"`). É uma das cartas que **entraram** na lista nesta sessão de mudanças (seção "ENTRA" do `lista.md`).

```
Primeval Titan — {4}{G}{G} — Creature — Giant
Trample
Whenever this creature enters or attacks, you may search your library
for up to two land cards, put them onto the battlefield tapped, then shuffle.
legalities.commander: banned
```

Todas as outras 96 cartas não-terreno da lista foram checadas: **nenhuma outra tem `legalities.commander` diferente de `legal`.** Este é o único problema de legalidade do deck, mas é impeditivo — o deck **não pode ser jogado como está** em mesa que respeite o banlist oficial. Precisa ser substituída antes de qualquer outra consideração.

Como referência de troca (não uma recomendação definitiva, só contexto pra decisão do usuário): o próprio EDHREC lista **Bumi, Unleashed** e **Toph, Hardheaded Teacher** como cartas de sinergia alta (0.592 e 0.578) que ainda não estão na lista — ver seção 11.

---

## 1. Validação formal

| Check | Resultado | Fonte |
|---|---|---|
| Total de cartas | **99** (1 comandante + 98 no corpo da lista) — **falta 1 carta pra fechar 100/100**, apesar do cabeçalho do `lista.md` dizer "100/100" | contagem de linhas com quantidade em `lista.md` |
| Singleton | Sem duplicatas fora de terrenos básicos | checagem de nomes únicos |
| Identidade de cor (R/G/W) | Sem violação — todas as 97 cartas únicas têm `color_identity` ⊆ {R,G,W} | `color_identity` de cada carta |
| Legalidade em Commander | **1 problema: Primeval Titan banida** (ver seção 0) | `legalities.commander` |

**Comandante:** Toph, the First Metalbender — `{1}{R}{G}{W}` — Legendary Creature — Human Warrior Ally.
```
Nontoken artifacts you control are lands in addition to their other types.
(They don't gain the ability to {T} for mana.)
At the beginning of your end step, earthbend 2. (Target land you control
becomes a 0/0 creature with haste that's still a land. Put two +1/+1
counters on it. When it dies or is exiled, return it to the battlefield
tapped.)
```

O cabeçalho do `lista.md` diz "100/100" e "GC 3/3" — a contagem de Game Changers está correta (seção 8), mas a contagem de cartas está **1 abaixo do declarado**. Não vou inventar qual carta falta — é uma checagem que só o usuário resolve (ou colando a lista completa de novo, ou confirmando que uma carta específica foi esquecida na hora de copiar/colar).

---

## 2. Terrenos e curva

- Terrenos: **32** (contando as 3 cópias de Forest; varredura de `type_line` em qualquer face, incluindo os MDFCs Bala Ged Sanctuary, Tanglespan Bridgeworks e Ondu Skyruins).
- Não-terrenos (sem comandante): **66** — CMC médio: **3.05**.
- Fontes de mana adicionais fora de terrenos: Arcane Signet, Sol Ring, Mox Opal, Lotus Cobra, Tireless Provisioner (Treasure), Talon Gates of Madara (ability paga), Great Divide Guide e Wrenn and Realmbreaker (ambos convertem **todos os terrenos** em fontes de qualquer cor via habilidade estática).

**Contagem de fontes de cor nos terrenos (sem contar rocks/criaturas), direto do `produced_mana` da Scryfall** (fetchlands recebem override manual — Scryfall não popula `produced_mana` pra fetches, então usei a cor real que cada uma busca):

| Cor | Fontes (terrenos) |
|---|---|
| G | **21** |
| W | **12** |
| R | **11** |

Verde é claramente a cor primária (bate com o tema landfall/earthbend), branco secundário, vermelho é o mais raro — consistente com a curva do deck (a maior parte dos payoffs de landfall e earthbend é `{G}` ou `{X}{G}`, enquanto R aparece sobretudo em cartas híbridas Naya como Tannuk, Toph Greatest Earthbender, Jetmir's Garden).

**Pacote de fixing "qualquer cor" (não contado na tabela acima, mas relevante — reduz muito o risco real de tela de cor apesar do R ser raro em fontes dedicadas):**
- Command Tower, Arcane Signet, Mox Opal, Jetmir's Garden, Talon Gates of Madara — fontes de qualquer cor da identidade do comandante, individuais.
- **Great Divide Guide** (`Each land and Ally you control has "{T}: Add one mana of any color."`) e **Wrenn and Realmbreaker** (`Lands you control have "{T}: Add one mana of any color."`) — cada um sozinho, uma vez em campo, converte **todos os 32 terrenos** em fontes de qualquer cor simultaneamente. É a rede de segurança real contra tela de cor deste deck, não os terrenos duais isolados.
- Lotus Cobra, Tireless Provisioner, Nissa, Resurgent Animist — mana de qualquer cor via landfall (Lotus Cobra e Nissa direto; Tireless Provisioner via token Treasure).
- Yavimaya, Cradle of Growth e Prismatic Omen/Dryad of the Ilysian Grove — fazem todo terreno virar Floresta (e todos os tipos básicos, nos dois últimos casos) — reforça fontes de G especificamente, e viabiliza fetches buscarem qualquer terreno.

---

## 3. Sinergia central — landfall + earthbend + "artefato é terreno"

Esse deck tem uma interação estrutural que amplifica tudo: **a própria Toph, the First Metalbender torna todo artefato não-token seu também um terreno** (`Nontoken artifacts you control are lands in addition to their other types`). Isso significa que **toda vez que um artefato entra em campo, ele conta como um terreno entrando** — disparando landfall de Lotus Cobra, Tireless Provisioner, Nissa, Bristly Bill, Felidar Retreat, Mossborn Hydra, Tannuk, Scute Swarm, Sapling Nursery, Springheart Nantuko, Earthbender Ascension e o próprio contador de experiência de Toph, Earthbending Master — mesmo que o artefato não seja fisicamente um terreno.

**Pacote de earthbend (converte terreno em criatura 0/0 com counters e haste) — 10 fontes reais na lista:**

| Carta | Earthbend |
|---|---|
| Toph, the First Metalbender (comandante) | earthbend 2, todo end step |
| Avatar Kyoshi, Earthbender | earthbend 8, todo combate |
| Toph, Earthbending Master | earthbend X = contadores de experiência, ao atacar |
| Toph, Greatest Earthbender | earthbend X = mana gasto ao conjurá-la (ETB único) |
| Ba Sing Se | earthbend 2 (ativada, `{2}{G},{T}`) |
| Badgermole Cub | earthbend 1 (ETB) |
| Bumi, Eclectic Earthbender | earthbend 1 (ETB) |
| Earth Kingdom General | earthbend 2 (ETB) |
| Earthbender Ascension | earthbend 2 (ETB) |
| Earthbending Student | earthbend 2 (ETB) |
| Earthshape | earthbend 3 (instant, com hexproof/indestructible bônus) |

**Payoffs de landfall — 11 fontes reais** (Lotus Cobra, Tireless Provisioner, Nissa Resurgent Animist, Bristly Bill Spine Sower, Felidar Retreat, Mossborn Hydra, Tannuk Memorial Ensign, Scute Swarm, Sapling Nursery, Springheart Nantuko, Earthbender Ascension, Toph Earthbending Master) — a maioria dobra de valor em cada terreno extra que entra (fetches, Dryad/Horizon Explorer permitindo terreno extra por turno, e sobretudo os artefatos-terreno da própria Toph).

**Pacote de contadores (+1/+1 e sinergia com o volume gerado pelo earthbend):** The Ozolith, Iron Spider Stark Upgrade, Bristly Bill (dobra contadores em `{3}{G}{G}`), Germination Practicum, Caretaker's Talent (nível 3 dá +2/+2 a tokens), Earth Kingdom General (converte contadores em vida).

Essa é a identidade real do deck: um motor de landfall Naya reforçado por artefatos-como-terreno + uma sub-tema de "terrenos viram criaturas grandes" via earthbend. Não é um deck de combo — é um deck de **valor incremental que escala rápido com quantidade de permanentes que entram**, o que também explica por que a lista tem tantos tutores de terreno (Erode, Primeval Titan — banida, Elvish Reclaimer, Earthbender Ascension, Planar Engineering, Horizon Explorer) em vez de tutores de carta: eles alimentam o próprio motor.

---

## 4. Motores identificados — 15 interações estruturais reais

Levantamento conjunto (9 identificados pelo usuário + 6 achados nesta revisão adicional do oráculo completo), cada um conferido contra o texto real da Scryfall antes de entrar aqui.

**Os 9 do usuário (revalidados):**

1. **Earthbend trava land-creature independente da Toph continuar em campo** — o texto de reminder do earthbend (`Put X +1/+1 counters on it. When it dies or is exiled, return it to the battlefield tapped`) não tem duração ("until end of turn"), então o efeito é permanente por padrão — a terra continua criatura mesmo se a fonte que a earthbendou sair de campo.
2. **Artefato não-token entrando com Toph em campo = landfall garantido**, via `Nontoken artifacts you control are lands in addition to their other types` (seção 3).
3. **Pacote de mana universal:** Prismatic Omen, Dryad of the Ilysian Grove, Wrenn and Realmbreaker, Ashaya (só verde), Overlord of the Hauntwoods (token "Everywhere", todo tipo básico) e Enduring Vitality (`Creatures you control have "{T}: Add one mana of any color."` — conferido ao vivo, ainda não incluída fisicamente).
4. **Field of the Dead conta nomes de artefato-terreno** — cada artefato virado terreno pela Toph é mais um nome distinto na contagem de "7+ terrenos com nomes diferentes".
5. **Krang dá flying/trample/indestructible/haste a todo artefato earthbent** — só se aplica quando o terreno earthbent também é um artefato (via Toph transformando um artefato seu em terreno primeiro); land creatures "puras" (não-artefato) não recebem o buff.
6. **Mycosynth Lattice + Toph = todo permanente seu vira terreno** — Lattice torna tudo artefato, Toph torna todo artefato não-token em terreno.
7. **Ondu Inversion / Oblivion Stone = wraths quase assimétricos** — `destroy all nonland permanents` (Ondu Inversion) e `destroy each nonland permanent without a fate counter` (Oblivion Stone) preservam terrenos por definição, incluindo os artefatos-terreno da Toph.
8. **Earthbender Ascension:** confirmando o texto exato — cada landfall poe 1 quest counter; a partir do 4º quest counter acumulado, **cada landfall subsequente também** dá +1/+1 permanente + trample **até o final do turno** (o trample não é permanente, só o counter — pequena correção em relação à formulação original).
9. **Awaken the Woods + Felidar Retreat + Mossborn Hydra:** Awaken the Woods com X alto cria X tokens de terreno-criatura que entram *simultaneamente*, cada um disparando landfall — com Mossborn Hydra em campo isso é X dobras seguidas dos contadores dela (crescimento geométrico, não aditivo) e X escolhas de Felidar Retreat.

**+6 achados nesta revisão (varredura do oráculo completo das 97 cartas):**

10. **Land creatures ganham double strike + vigilance de graça, empilhando com o buff de artefato do Krang:**
    - Toph, Greatest Earthbender: `Land creatures you control have double strike.`
    - Earthbending Student: `Land creatures you control have vigilance.`
    - Vale pra **todo** terreno earthbent do deck (não só os que viraram artefato primeiro, ao contrário do Krang).
11. **Ashaya, Soul of the Wild é um segundo motor "permanente vira terreno" — paralelo ao da Toph, e maior em volume.** Texto real: `Nontoken creatures you control are Forest lands in addition to their other types.` A Toph cobre artefatos; a Ashaya cobre **toda criatura não-token**. As duas juntas em campo tornam quase todo spell relevante que você resolve em um trigger de landfall, e reforçam ainda mais o Field of the Dead (item 4).
12. **The Ozolith recicla os counters de land creatures que morrem** — earthbend devolve a terra "tapped" sem counters quando ela morre/é exilada; o Ozolith intercepta esses counters antes de se perderem (`Whenever a creature you control leaves the battlefield, if it had counters on it, put those counters on The Ozolith`) e permite realocá-los depois. É a proteção real do investimento de earthbend contra remoção/combate.
13. **A ativada do Bristly Bill (`{3}{G}{G}: Double the number of +1/+1 counters on each creature you control`) dobra o board inteiro, não só a Mossborn Hydra** — é repetível (limitado só por mana), então serve como um segundo modo de crescimento explosivo fora do combo específico do item 9.
14. **Kodama of the East Tree — cheat-into-play em cadeia a partir de qualquer permanente que entra:** `Whenever another permanent you control enters, if it wasn't put onto the battlefield with this ability, you may put a permanent card with equal or lesser mana value from your hand onto the battlefield.` Dado o volume de entradas de permanente que o deck já gera (landfall, tokens, artefatos), cada uma pode puxar de graça outro permanente mais barato da mão — inclusive encadeando, já que o permanente puxado também conta como "outro permanente que entra" pro próximo gatilho.
15. **Strionic Resonator — dobrador universal e flexível de gatilho, escolhido a cada ativação:** `{2},{T}: Copy target triggered ability you control.` Ao contrário de um dobrador fixo numa única carta, esse permite escolher qual gatilho copiar a cada turno — o earthbend do comandante, um landfall específico, o dano do Tannuk, etc.

---

## 5. Ramp — 9 peças

Arcane Signet, Sol Ring, Mox Opal (condicional, Metalcraft), Dryad of the Ilysian Grove (terreno extra por turno), Horizon Explorer (Lander token = fetch de terreno básico, terrenos entram destapados), Lotus Cobra, Nissa Resurgent Animist, Tireless Provisioner, Planar Engineering (sacrifica 2 terrenos, busca 4 básicas — ramp líquido de +2 terrenos).

Primeval Titan (banida, ver seção 0) também seria ramp — **não conto ela aqui já que precisa sair da lista.**

---

## 6. Card draw — 12 fontes

Sylvan Library, Esper Sentinel, Skullclamp, Ichor Wellspring, Mishra's Bauble, Iron Spider Stark Upgrade (remove contadores: puxa carta), Caretaker's Talent (token entra: puxa carta), The Great Henge (criatura não-token entra: contador + puxa carta), Tannuk Memorial Ensign (2º landfall do turno: puxa), Nissa Resurgent Animist (2º landfall do turno: dig até achar Elfo/Elemental), Spelunking (ETB: puxa), Fountainport (sacrifica token: puxa).

---

## 7. Remoção e interação — 4 peças + 2 wipes (fraqueza real, já identificada pelo usuário)

**Remoção pontual:**
- Erode — destroy target creature or planeswalker (dá terreno básico ao dono, downside real).
- Bridgeworks Battle (face sorcery do MDFC) — fight, exige criatura própria em campo.
- Haywire Mite — exile artefato/encantamento não-criatura, exige sacrificar a própria Haywire Mite.
- Talon Gates of Madara — phase out (temporário, não remove de fato) no ETB do próprio terreno.

**Wipes:**
- Ondu Inversion (face sorcery do MDFC) — destroy all nonland permanents (simétrico).
- Oblivion Stone — wipe assimétrico via fate counters (`{4}` marca, depois `{5}`+sacrifício destrói tudo sem contador).

**Isso é pouco.** Zero remoção instantânea barata e dedicada a criatura (nem Swords to Plowshares nem Path to Exile estão na lista — e são justamente os dois "Top Cards" mais jogados com este comandante no EDHREC, com `num_decks` de 17800/31002 e 15541/31002 respectivamente, apesar de terem sinergia ~0 — ou seja, staples genéricos que a maioria das listas roda por eficiência pura, não por sinergia). Confere com o que o próprio `lista.md` já registrou na seção "Opções salvas": **Weapons Manufacturing** foi cogitada especificamente para "endereçar a fraqueza de interação do deck" — a auditoria concorda com esse diagnóstico com números reais: 4 remoções pontuais (uma delas condicional a ter criatura própria, outra a sacrificar a própria carta) num deck de 98 cartas é abaixo da faixa típica de 8-10 recomendada pra Bracket 3.

---

## 8. Win conditions

Não há um "combo de vitória" dedicado — o plano de jogo é batalha via corpos grandes:
- **Earthbend em escala:** Avatar Kyoshi (earthbend 8 todo combate) e Toph, Earthbending Master (earthbend X = contadores de experiência acumulados, que só crescem) transformam terrenos em ameaças de combate recorrentes, sem depender de conjurar novas criaturas.
- **Wide + counters:** Scute Swarm (se copia com 6+ terrenos), Sapling Nursery (Treefolk 3/4 a cada terreno), Felidar Retreat, Mossborn Hydra (dobra contadores a cada landfall) — geram um board largo que se authoriza a atacar em conjunto.
- **Krang, Utrom Warlord** (`{9}`) — dá flying/trample/indestructible/haste a todas as criaturas-artefato; combina com Toph transformando artefatos em terrenos-criatura via earthbend, e com Iron Spider (contador em toda artefato-criatura/Vehicle).
- **The Great Henge** — engine de draw+counter que também reduz seu próprio custo pelo maior poder em campo, plausível de ser jogado cedo com Toph em campo (poder alto vem rápido com earthbend).

Nenhuma dessas é um "combo" no sentido do critério de Bracket — são todas ameaças incrementais que dependem de continuar resolvendo permanentes, sem loop fechado.

---

## 9. Game Changers — contagem oficial (3/3, confirma o cabeçalho da lista)

Cruzamento ao vivo contra `https://api.scryfall.com/cards/search?q=is:gamechanger` (53 cartas, consultado 2026-08-22):

**3 Game Changers: Enlightened Tutor, Field of the Dead, Teferi's Protection.**

Confere exatamente com o que o cabeçalho do `lista.md` já declarava ("GC 3/3") — sem discrepância. Isso coloca o deck no teto exato do Bracket 3.

---

## 10. Varredura de combo e estruturas restritas por Bracket

- **Combo de 2 peças:** varredura manual do texto oracle completo das 97 cartas (não é combo detectável por regex simples nesse deck — a categoria de risco aqui seria "mana infinito via sacrifício de artefato", então li Krark-Clan Ironworks, Mycosynth Lattice, Liquimetal Coating/Torque, Ultron, Oswald Fiddlebender e Urza's Saga com atenção). **Não encontrei um loop fechado de 2 peças.** Krark-Clan Ironworks (`Sacrifice an artifact: Add {C}{C}`) combinado com Crucible of Worlds (recompra terreno-artefato do cemitério) gera valor real, mas está limitado a 1 land drop por turno (a menos que Dryad of the Ilysian Grove/Horizon Explorer estejam em campo também — nesse caso vira 3 peças, e ainda assim finito por turno, não um loop infinito).
- **Negação de terras em massa:** nenhuma encontrada — Strip Mine é destruição de terreno único (não é "mass land denial" pelo critério oficial, que fala de efeitos repetíveis/assimétricos de negar terreno a todos os oponentes).
- **Turnos extras:** nenhum efeito de turno extra no texto de nenhuma carta.
- **Combate adicional/turnos extras encadeados:** nenhum encontrado.
- **Densidade de tutores:** Enlightened Tutor é o único tutor de carta não-terreno da lista (busca artefato/encantamento pro topo). Os demais "tutores" da lista (Erode, Elvish Reclaimer, Earthbender Ascension, Planar Engineering, Horizon Explorer via Lander) buscam exclusivamente terreno básico — não tutoram peças de combo nem ameaças específicas, e terreno básico redundante não é o tipo de tutor que o critério de Bracket 3 restringe.

**Nenhuma das quatro restrições estruturais de Bracket 3 é violada.**

---

## 11. Cruzamento com dados reais do EDHREC (sinergia com o comandante)

Consultado `json.edhrec.com/pages/commanders/toph-the-first-metalbender.json` (2026-08-22). Cartas de **maior sinergia real** com Toph, the First Metalbender segundo o próprio EDHREC (`synergy` = o quanto uma carta aparece mais que a média em decks desse comandante especificamente, não popularidade genérica):

| Carta | Synergy | Está na lista? |
|---|---|---|
| Ba Sing Se | +0.594 | ✅ |
| Bumi, Unleashed | +0.592 | ❌ (Bumi, **Eclectic** Earthbender está — carta diferente) |
| Toph, Hardheaded Teacher | +0.578 | ❌ |
| Earthbender Ascension | +0.520 | ✅ |
| Ichor Wellspring | +0.520 | ✅ |
| Toph, the Blind Bandit | +0.510 | ❌ |
| Tannuk, Memorial Ensign | +0.497 | ✅ |
| Toph, Earthbending Master | +0.458 | ✅ |
| Toph, Greatest Earthbender | +0.451 | ✅ |
| Great Divide Guide | +0.446 | ✅ |
| Badgermole Cub | +0.444 | ✅ |
| Zuran Orb | +0.439 | ✅ |
| Lotus Cobra | +0.426 | ✅ |
| Avatar Kyoshi, Earthbender | +0.397 | ✅ |
| The Stasis Coffin | +0.416 | ✅ |
| Tireless Provisioner | +0.370 | ✅ |

**11 de 16 cartas de alta sinergia listadas pelo EDHREC já estão na lista** — forte alinhamento com o build padrão da comunidade pra esse comandante, não é uma lista fora da curva. As 3 ausências relevantes (Bumi, Unleashed / Toph, Hardheaded Teacher / Toph, the Blind Bandit) são só dados — não é uma recomendação de troca, e nenhuma delas resolve o problema de legalidade da seção 0.

Só como contexto (não é recomendação): os dois cards mais jogados junto com este comandante no EDHREC geral são Swords to Plowshares e Path to Exile (`num_decks` 17800/31002 e 15541/31002) — nenhum dos dois está na lista, reforçando o achado da seção 6 sobre a remoção estar abaixo do típico.

---

## 12. Classificação de Bracket

**Bracket 3 (Upgraded), no teto de Game Changers (3 de 3) — condicionado à remoção da Primeval Titan banida (seção 0).**

Base: 3 Game Changers (teto exato), sem negação de terras em massa, sem turnos extras, sem combo de 2 peças identificado na varredura de texto, densidade de tutores baixa e majoritariamente restrita a terreno básico. A classificação de poder não muda com a remoção da Primeval Titan (ela não era Game Changer nem combo piece, só ramp) — mas o deck **precisa** dessa troca antes de ir pra mesa, independente do bracket.

---

## Links

- EDHREC: https://edhrec.com/commanders/toph-the-first-metalbender
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
- Scryfall (comandante): https://scryfall.com/search?q=%21%22Toph%2C+the+First+Metalbender%22
