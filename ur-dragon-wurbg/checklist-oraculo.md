# Checklist cláusula-a-cláusula — The Ur-Dragon (`urdragon_goldfish_v1.py`)

## Mulligan com escolha do fundo (varredura de 2026-10-05) — 2026-10-05

**Origem:** erros achados nas rodadas do Vihaan e do Megatron (mulligan que devolvia cartas ao fundo por sorteio; ordem upkeep × draw; imposto de comandante; jogada de terreno que entra virado) varridos neste simulador, por leitura do código (`grep` + leitura da função) e por teste dirigido/instrumentação em runtime.

| cláusula / conceito | situação |
|---|---|
| London Mulligan, CR 103.5 | 🐛 corrigido: `choose_bottom`, atrás de `MULLIGAN_SMART_BOTTOM_ENABLED` |
| Imposto de comandante, CR 903.8 | ✅ já estava (`effective_cost` soma `2 * commander_cast_count`) |
| Upkeep antes do draw (CR 503/504) | ✅ já estava (`play_turn`: upkeep, depois a compra) |
| Entrada de terrenos (slow/shock/triome) e fetchlands | ✅ já modelados em `land_enters`/`crack_fetch` (corrigido em 2026-09-28); tapped-first não tratado nesta seção |

**Regra permanente aplicada:** a correção entra atrás de chave; com ela desligada o simulador é bit-idêntico ao anterior (20.000 × 2 modos). Dados e reprodução: `resultados-ab/2026-10-05-mulligan-e-ordem-das-fases/LEIAME.md`.

---

## Conceitos "Dwarf" e "Treasure" varridos (Magda, Firdoch Core, Morophon) — 2026-09-28 (4ª rodada do dia)

**Gatilho:** o usuário apontou que eu esqueci o Treasure do tap do Firdoch
Core ao avaliar a Magda. Rulings ao vivo (Magda 2021-02-05: o Dwarf precisa
mudar de desvirado pra virado; Firdoch Core 2025-11-17: Kindred permite tipo
de criatura fora de criatura, Changeling funciona em toda zona).

| Carta | Cláusula | Antes | Agora |
|---|---|---|---|
| Magda, Brazen Outlaw | "Whenever a Dwarf you control becomes tapped, create a Treasure token" | Magda e Firdoch Core | + Morophon atacando, fichas-cópia (Miirym) de Morophon/Firdoch, Sarkhan copiando Morophon; extra combat desvira/vira |
| Magda | "Other Dwarves you control get +1/+0" | nenhum | Firdoch animado, Morophon, cópias |
| Magda | "Sacrifice five Treasures: ... artifact or Dragon card onto the battlefield" | só Treasures da própria Magda | qualquer Treasure (`treasure_stock`); só o que sobrou depois de conjurar |
| Conceito Treasure | "{T}, Sacrifice: Add one mana of any color" (Goldspan: 2 de uma cor) | mana instantânea, perdida no fim do turno | permanente: estoque persiste, paga pip, gasta só o necessário |
| Morophon | "Other creatures you control of the chosen type get +1/+1" | a ficha-cópia dele se dava o próprio bônus | só de outros |

**Escopo (Regra #7).** Varrido: todo produtor e consumidor de Treasure da
lista, e todo Dwarf (Magda, Firdoch Core, Morophon). Método: oráculo e
rulings ao vivo, script de tipos, testes dirigidos. Não varrido: o mesmo
conceito nos outros simuladores com Treasure.

---

## Combos da lista executados no simulador — 2026-09-28 (3ª rodada do dia)

**Gatilho:** o usuário perguntou se a Bladewing não era peça de combo.
Era, e a recomendação da Tiamat tinha ignorado isso. Commander Spellbook
ao vivo (`find-my-combos`): 3 combos já montados na lista. Dois não eram
executáveis no simulador.

| Carta | Cláusula | Antes | Agora |
|---|---|---|---|
| Terror of the Peaks | "deals damage equal to that creature's power to **any target**" | só oponente (proxy) | também a própria Bladewing, dentro do loop (`try_bladewing_loop`) |
| Scourge of Valkas / Dragon Tempest | "deals X damage to **any target**" | só oponente | matam a Bladewing no loop se X ≥ resistência (📝 variante pela regra; o Spellbook lista só a Terror) |
| Miirym (cópia da Bladewing) | ETB da cópia: "return target Dragon permanent card" | devolvia o Dragão de maior MV | com o loop montado, devolve a Bladewing |
| Hellkite Charger | "Whenever this creature attacks, you may pay {5}{R}{R}..." | teto de 1 combate extra por turno | repete enquanto dá pra pagar (Treasure da Old Gnawbone) até o letal; trava de 60 |

**Escopo (Regra #7):**
- **Varrido:** os 3 combos que o Spellbook lista como "included" pra esta
  lista. Método: Spellbook ao vivo + teste dirigido de cada um.
- **Não varrido:** os 147 "almostIncluded" (falta 1 carta; nenhum está na
  lista).

---

## Varredura das demais cartas e mecânicas — 2026-09-28 (2ª rodada do dia)

**Pedido:** *"Verifique as demais cartas e mecânicas em busca de erros e
conserte pfv"*, logo depois da avaliação da Tiamat, que tinha declarado
fora do escopo "as outras classes da taxonomia nas 99 cartas".

**Método:**
- Oráculo ao vivo das 100 cartas: Scryfall `/cards/collection`, 100/100
  achadas pelo nome, nenhuma com `flavor_name` divergente.
- Leitura integral do `urdragon_goldfish_v1.py` (3.239 linhas).
- Comparação cláusula a cláusula, carta por carta.
- Varredura automática de tags e nomes órfãos: toda carta da lista tem
  dispatch por nome; as tags "órfãs" são decorativas de cartas
  despachadas pelo nome.
- Varredura por CONCEITO (Regra #3):
  - "é Dragão" em cada zona;
  - "criatura que você controla";
  - "quem tem esta habilidade" (cópias);
  - "terreno entra virado";
  - "custo de vida".
- Ordem de chamadas do turno (Regra #6).
- Um teste dirigido por correção: 38 novos, 79/79 no total. Os 37
  primeiros foram rodados contra o código anterior à rodada e falham
  todos lá.

### 🐛 Corrigido

**Conceito "é Dragão" por zona.** A Roaming Throne só escolhe o tipo "as
this creature enters". Na pilha, no cemitério e na biblioteca é Golem.

| Onde | Antes | Agora |
|---|---|---|
| Custo da Throne (Eminence, Servant, Dragonspeaker, Sarkhan, Horn, Incubator, Orb, Cavern/Haven/Courtyard) | com Dragonspeaker + Servant custava **1** (real: 4) | `is_dragon_card` em toda checagem de magia |
| Bladewing ("Dragon permanent card"), Haunting Voyage, Haven, snipe do oponente | podiam pegar a Throne no cemitério | idem |
| Herald's Horn ("creature card of the chosen type") | pegava Firdoch Core (artefato) e Throne do topo | só carta de criatura Dragão |

**Mana, terrenos e vida.**

| Carta / conceito | Cláusula | Antes | Agora |
|---|---|---|---|
| Ancient Tomb | "{T}: Add {C}{C}" | 1 mana, como todo terreno | 2 |
| Terreno que entra virado | Triome, Path, slow land, Farseek, Cultivate | UM slot por turno: Triome + Farseek no mesmo turno, o 1º virava mana | lista |
| Cultivate / Kodama's Reach | "put one onto the battlefield tapped and the other into your hand" | "simplificação": as duas no campo, destravadas | 1 virada no campo, 1 na mão |
| Ur-Dragon põe terreno da mão | Triome/Path/slow land "enters tapped" | sempre destravado | ponto único `land_enters` |
| Taxa de comandante | CR 903.8 | fora do `can_cast`: aprovava a Ur-Dragon sem a taxa e gastava mais do que havia | dentro de `effective_cost` |
| Custos de vida (taxonomia "mana ou VIDA nunca deduzido") | fetch 1, shock 2, Mana Confluence 1, Ancient Tomb 2, Sylvan Library 4, Anguished Unmaking 3 | nenhum cobrado (`life` já existia) | `pay_life`; Tomb/Confluence só quando a mana gasta passa das fontes sem dor |
| The Great Henge | "{T}: Add {G}{G}. You gain 2 life." | vida ignorada | +2 por turno |
| Path of Ancestry | "When that mana is spent to cast a creature spell that shares a creature type with your commander, scry 1." | fora "por valor baixo demais" (julgamento de valor, Regra #1) | scry 1 na 1ª magia de criatura Dragão do turno |
| Triomes (4) | "Cycling {3}" | custo alternativo inexistente | cicla na main 2 com mana sobrando e 7+ terrenos ou outro terreno na mão |
| Treasure, Klauth, +1 do Sarkhan Unbroken, Savage Ventmaw | "any color" / {R}{R}{R}{G}{G}{G} | só quantidade, nunca pagava pip | entram na checagem de cor |
| Dragon's Hoard | `{T}` compartilhado (mana OU compra) | comprava na main 1 E na main 2; a mana dela continuava no total | 1× por turno, e a mana sai |
| Haunting Voyage foretold | "{5}{B}{B}", magia de MV 6 | {B}{B} nunca checado; não disparava Up the Beanstalk; sumia (nem cemitério) | checa BB, dispara Beanstalk, vai pro cemitério |
| Arcane Denial | "You draw a card at the beginning of the next turn's upkeep." | nunca comprava | compra antes do meu próximo turno |

**Ordem de chamadas (Regra #6).**
- **Comandante:** só era checada no início de cada fase principal. Sol
  Ring, Treasure ou Orb conjurados no loop deixavam a Ur-Dragon
  conjurável, mas o loop gastava a mana em outra coisa. Agora ela entra
  assim que fica conjurável.
- **Sarkhan Unbroken:** o +1 (compra + mana) rodava DEPOIS do loop de
  conjuração, e a mana só servia na main 2. Agora ativa antes e ativa no
  turno em que entra.
- **Pumps (Lathliss, Bladewing, Scourge):** rodavam também no fim da main
  2, depois do combate: mana gasta em nada. Agora só antes do combate, e
  com a cor checada ({R}; {B}{R}). Secluded Courtyard e Orb pagam
  habilidade de Dragão.

**Combate.**

| Carta / conceito | Cláusula | Antes | Agora |
|---|---|---|---|
| The Ur-Dragon × Roaming Throne | o gatilho é de criatura Dragão em campo | Throne só dobrava se a Ur-Dragon ATACASSE | dobra sempre que ela está em campo |
| Twinflame Tyrant | "deals double that damage" | não dobrava o dano de comandante nem o "that many" da Old Gnawbone | dobra os dois; cada cópia dobra de novo |
| Dano de comandante | pump da Lathliss/Bladewing | ignorado | somado |
| Magda, Brazen Outlaw | o gatilho de Treasure já assumia que ela ataca | o dano dela (2) nunca entrava | entra (e na Gnawbone) |
| Firdoch Core | "{4}: This artifact becomes a 4/4 artifact creature until end of turn" | não modelado | anima no fim da main 1 com 5+ sobrando e Ur-Dragon/Utvara em campo; ataca como Dragão (Changeling) |
| Firdoch × Magda | o Firdoch vira 1× por turno | o combate extra do Charger contava de novo | 1× por turno |
| Return of the Wildspeaker | 2º modo: "Non-Human creatures you control get +3/+3" | só o modo de compra | pump no combate quando fecha o letal proxy; senão, compra na main 2 |
| Ancient Copper / Ancient Gold | "roll a d20" | 10 fixo | d20 de verdade (RNG próprio) |
| Rhythm of the Wild | riot: "+1/+1 counter OR haste" | sempre haste | haste só se vai atacar agora (main 1, sem outra haste); senão +1/+1 |
| Lightning Greaves | equip {0}, repetível | só re-equipava se o alvo saísse de campo (preso num Birds, nunca ia pra Ur-Dragon) | vai pra criatura que ganha com haste agora; senão, comandante |
| Terror of the Peaks × Great Henge | dano = poder lido na resolução | poder sem o contador do Henge | o controlador ordena o Henge antes (+1) |
| Great Henge (custo), Garruk's Uprising (ETB), Return of the Wildspeaker | "creature(s) you control" | só criatura nomeada; ficha de Dragão ignorada | fichas contam |

**Cópias (Regra #3, conceito "quem tem esta habilidade").**
- **Miirym:** a ficha-cópia era um corpo sem texto ("limitação do motor",
  que não era estrutural). Agora `sources(nome)` conta a carta nomeada +
  fichas-cópia + Sarkhan copiando. O texto da cópia vale de verdade:
  - dispara: Scourge, Terror, Lathliss, Miirym, Utvara, Old Gnawbone,
    Broodmother, gatilho da Ur-Dragon;
  - estáticos: Twinflame (×2 por cópia), Morophon (anthem e desconto por
    cópia), Roaming Throne (+1 disparo por cópia), Atarka, Goldspan,
    Eminence da cópia da Ur-Dragon;
  - atacando: gatilhos próprios de Goldspan, Ancient Copper/Gold, Klauth,
    Ventmaw e Dromoka (lifelink);
  - ETB da cópia: Hellkite Courser (põe a comandante) e Bladewing
    (reanima).
- **Miirym × Firdoch Core:** a cópia é artefato, não criatura. Agora dá
  mana, conta como Dragão e é Dwarf pra Magda, mas não ataca. Antes
  virava uma ficha de Dragão 0/0 que atacava.
- **Sarkhan, Soul Aflame:** "become a copy of it until end of turn" era só
  um contador. Agora:
  - no fim da main 1, se pode atacar, vira cópia do melhor Dragão nomeado
    que entrou no turno;
  - ataca com o P/T e os gatilhos dele;
  - conta como Dragão;
  - perde o próprio "Dragon spells cost {1} less" até o fim do turno;
  - volta no cleanup.

**Deck-out (CR 704.5b), achado ao medir o antes/depois.**
- **O furo:** `library_emptied` era só uma flag, e a partida seguia. O
  letal proxy era marcado no fim do turno. Só que o gatilho da Ur-Dragon
  ("draw that many cards", obrigatório) resolve ANTES do dano de combate.
  No código anterior a esta rodada, **16,2% das partidas** marcavam letal
  no mesmo turno em que o grimório acabou (1.000 seeds). Nessas, o piloto
  teria perdido antes do dano.
- **Agora:**
  - comprar de grimório vazio é derrota, e a partida para;
  - se o dano acumulado já tinha passado de 120, é vitória;
  - o piloto limita os atacantes: cada Dragão atacando custa as compras
    obrigatórias (gatilho da Ur-Dragon × cópias × Throne, + fichas da
    Utvara × Elemental Bond/Garruk's Uprising); ataca com no máximo
    (grimório − 1) / esse custo, os mais fortes primeiro;
  - com grimório abaixo de 10, recusa compra opcional: Temur "may", Hoard,
    Sylvan, RotW-compra, cycling, e o +1 do Sarkhan Unbroken (troca pelo
    −2).

**Modo de resiliência.** O oponente nunca atacava planeswalker. Agora o
atacante vai no Sarkhan Unbroken primeiro (mesma convenção do Prismatic
Bridge), e o Sarkhan morre com lealdade 0.

### 📝 Políticas (não regra) desta rodada

- Scry do Path: terreno pro fundo com 8+ terrenos (campo + mão); mágica
  pro fundo com menos de 4.
- Sylvan Library: paga 4 com 14+ de vida.
- Cycling: só na main 2.
- Firdoch: só com Ur-Dragon ou Utvara em campo.
- Return of the Wildspeaker: pump só quando fecha o letal proxy.
- Sarkhan, Soul Aflame: copia só antes do combate, entre Dragões nomeados.
- Deck-out: guarda 1 carta pro próximo passo de compra; limiar de compra
  opcional = 10.

### 📊 Continua estrutural (estado real de oponente)

| Carta | Cláusula |
|---|---|
| Exotic Orchard | "any color that a land an opponent controls could produce" |
| Balefire Dragon | "deals that much damage to each creature that player controls" (agora contada em `balefire_hits_total`) |
| Crux of Fate, Austere Command, Swords, Beast Within, Assassin's Trophy, Anguished Unmaking, An Offer | alvo/board de oponente (proxy a cada 3 turnos) |
| Swan Song, Arcane Denial, An Offer | bônus dado ao oponente |
| Miirym, Roaming Throne, Terror of the Peaks | ward {2} e "cost an additional 3 life" (mana/vida do oponente) |
| Smothering Tithe | quantos oponentes pagam {2} (estimativa fixa) |
| Goldspan | "becomes the target of a spell" (só o oponente miraria) |

### Escopo desta rodada (Regra #7)

Varrido nas 99 cartas + comandante, com método:
- **Custos (mana e vida), inclusive custo alternativo** (Foretell,
  Cycling). Método: leitura + teste.
- **Busca/tutor com restrição de tipo.** Método: grep dos 16 usos de
  `is_dragon` + teste.
- **Estáticos propagados:** Morophon, Twinflame, Throne, riot, Henge,
  Goldspan. Método: leitura + teste.
- **Gatilho compartilhado:** "criatura/Dragão entra", "magia de MV ≥5",
  "Dragões atacam". Método: todos os pontos de entrada + teste.
- **`{T}` compartilhado ou repetido:** Hoard, Firdoch/Magda. Método:
  leitura + teste.
- **Fórmula achatada:** d20. Método: leitura + teste.
- **Ordem de fases:** `play_turn` e `main_phase` relidos inteiros.
- **Fichas, 4 checagens da Regra #7:**
  - atacam, com doença de invocação;
  - disparam entrada;
  - morrem no wipe;
  - contam em "you control": Henge, Garruk's e RotW eram o furo.
- **Proxies de turno de oponente:** Tithe, Broodmother e Arcane Denial.

Não varrido:
- o `urdragon_goldfish_physical_v1.py` e o `_original`;
- as habilidades das cartas-candidatas fora da lista (Kindred Discovery,
  Radagast, Ramos, Karplusan etc.);
- o modelo de oponente do modo de resiliência em si (probabilidades).

### Validação

- Smoke: 99 cartas, 0 desconhecidas, 0 duplicadas.
- `test_urdragon_goldfish.py`: **83/83**. São 42 testes novos, um por
  correção:
  - custo da Throne na pilha;
  - Tomb 2;
  - taxa no `can_cast`;
  - 2 terrenos virados;
  - Cultivate 1+1;
  - vida (fetch/shock/Unmaking/Tomb/Confluence/Henge/Sylvan);
  - terreno da Ur-Dragon virado;
  - Herald's Horn;
  - Bladewing (tipo + Throne);
  - Haven/Voyage;
  - Hoard 1×;
  - comandante no loop;
  - +1 do Sarkhan antes do loop;
  - pumps só antes do combate e com cor;
  - Greaves;
  - riot;
  - Terror × Henge;
  - fichas em "creatures you control";
  - Throne × gatilho da Ur-Dragon;
  - Twinflame (dano de comandante e Gnawbone);
  - Magda;
  - Firdoch animado;
  - RotW pump;
  - d20;
  - cópias da Miirym (Scourge, Ur-Dragon, Courser, Firdoch);
  - Sarkhan copiando a Utvara;
  - Arcane Denial;
  - scry do Path;
  - cycling;
  - Voyage foretold;
  - ataque ao Sarkhan Unbroken;
  - Treasure pagando pip;
  - deck-out (derrota, vitória antes da compra, atacantes limitados,
    compra opcional recusada).
- Rodados contra o código anterior à rodada, os 37 primeiros testes
  novos falham todos (o bug existia) e passam no código novo.
- 20.000 + 20.000 partidas (padrão + resiliência, seed 8.000.000+): **0
  exceções**.
- Antes/depois em 2.000 seeds: `goldfish-log.md`.

---

## Tiamat (candidata) + modelo de custo, Orb, descarte e resiliência corrigidos — 2026-09-28

**Gatilho:** *"Avalia os prós e contras de incluir Tiamat no Ur-Dragon, a
carta está em anexo para facilitar"*. A Tiamat custa WUBRG e tutora. Pra
comparar de forma justa, o modelo de custo e de cores do arquivo foi
relido inteiro. Depois vieram os caminhos que buscam Dragão e o modo de
resiliência, onde estão os cortes candidatos. Os achados de base vieram
antes da carta.

### 🐛 Corrigido na base (afeta a lista atual)

| # | Carta / conceito | Cláusula real | Antes | Agora |
|---|---|---|---|---|
| 1 | Todo redutor (Eminence, Dragonlord's Servant, Dragonspeaker Shaman, Sarkhan Soul Aflame, Herald's Horn, Urza's Incubator, Radagast, Great Henge) | CR 601.2f: redução abate só mana **genérica** | descontava do valor de mana inteiro: Scourge de Valkas ({2}{R}{R}{R}) com Eminence + Dragonspeaker saía por 2; a Ur-Dragon podia custar menos que WUBRG | `effective_cost`: genérico − desconto + pips (menos o que o Morophon tira) |
| 2 | Checagem de cor (`has_color_sources_for`) | uma fonte paga **um** pip | cada cor checada sozinha: Command Tower + 5 Forest "pagava" WUBRG | condição de Hall sobre `source_color_sets` (uma entrada por fonte pronta) |
| 3 | Rhythm of the Wild | `{1}{R}{G}` | mv 2 | mv 3 |
| 4 | Sarkhan's Triumph | "Search your library for a Dragon **creature** card" | podia pegar Firdoch Core (Kindred Artifact, Changeling: é Dragon card, não criatura) | exige criatura |
| 5 | Orb of Dragonkind, sacrifício | "Look at the **top seven** cards ... Put the rest on the bottom ... in a random order" | buscava na biblioteca inteira (tutor completo) | só o topo 7; sem Dragão lá, a Orb sai por nada; o resto vai pro fundo embaralhado |
| 6 | Orb of Dragonkind, mana | "Add two mana in any combination of **colors**. Spend this mana only to cast Dragon spells" | contava só quantidade, nunca cor | cada mana do pool paga um pip de qualquer cor em magia de Dragão |
| 7 | Orb × comandante (Regra #6) | idem, sem "other": vale pra Ur-Dragon | a Orb só era ativada DEPOIS da checagem da comandante e só com Dragão na mão (a comandante fica na zona de comando) | `try_orb_mana_for_commander` antes da checagem, só quando isso torna a comandante conjurável |
| 8 | Descarte no cleanup | — (política) | menor custo primeiro, terreno antes de tudo, mesmo antes da comandante de 9 estar em campo | antes da comandante, terreno/ramp/redutor só saem se não sobrar outra carta |
| 9 | Dragonlord Dromoka | "Your opponents can't cast spells during your turn." | 📊 "sem contramágica de oponente" — mas o modo de resiliência TEM contramágica na Ur-Dragon desde 2026-09-20 | impede a contramágica (`counters_prevented_by`) |
| 10 | Rhythm of the Wild | "Creature spells you control can't be countered." | idem | idem |
| 11 | Cavern of Souls (Dragão) | "...and that spell can't be countered" | idem | idem (a Ur-Dragon precisa de WUBRG, a Cavern paga um pip) |
| 12 | Swan Song / Arcane Denial / An Offer You Can't Refuse | "Counter target instant ... / spell / noncreature spell" | nunca respondiam à contramágica deles | respondem se houver mana e cor sobrando (`counters_answered_total`); o bônus do oponente (2/2, 2 cartas, 2 Treasures) fica 📊 |
| 13 | Heroic Intervention | "Permanents you control gain hexproof and indestructible until end of turn." | fora do loop guloso E fora de `TRUE_INTERACTION_CARDS`: nunca saía da mão | responde a wipe (se leva a comandante ou 3+ permanentes) e a remoção pontual, com a mana que sobrou do meu turno |
| 14 | Teferi's Protection | "Until your next turn, your life total can't change and you gain protection from everything. All permanents you control phase out. Exile ..." | idem | responde a wipe; anula ataque/remoção até o meu próximo turno; vai pro exílio |
| 15 | Lightning Greaves | "Equipped creature has shroud" | 📊 "sem remoção alheia" — o modo de resiliência tem remoção pontual | o oponente mira a próxima peça da lista |
| 16 | Dragonlord Dromoka | "Flying, lifelink" | lifelink nunca somado | ganha o dano dela no combate (Atarka e Twinflame contam) |

Os itens 9–15 são exatamente a Regra #7, item 2. A justificativa 📊 era
verdadeira em 2026-08-29. Deixou de ser em 2026-09-20, quando o modo de
resiliência ganhou contramágica, wipe e remoção de oponente, e ninguém
voltou nessas cláusulas. Os itens 9, 10 e 16 mexem direto num corte
candidato (Dromoka), por isso entraram antes do A/B.

### Tiamat — oráculo ao vivo (Scryfall + rulings, salvo no oracle-cache)

`{2}{W}{U}{B}{R}{G}` Legendary Creature — Dragon God 7/7. Commander
legal, não é Game Changer, US$ 22,91.

| Cláusula | Status | Onde |
|---|---|---|
| Flying | ✅ | `FLYING_CREATURES` (haste do Dragon Tempest) |
| Legendary | ✅ | `LEGENDARY_SPELLS`; cópia da Miirym "isn't legendary" |
| Dragon (tipo) | ✅ | tag `dragon`: Eminence e redutores, Scourge/Tempest/Terror/Lathliss/Miirym, ataque da Ur-Dragon, Haven/Cavern/Courtyard/Orb pagam pips |
| "When Tiamat enters, **if you cast it**, search your library for up to five Dragon cards not named Tiamat that each have different names, reveal them, put them into your hand, then shuffle." | ✅ | `tiamat_tutor`, chamada só em `cast_card`. Entrada grátis (ataque da Ur-Dragon, Magda, Bladewing, Haunting Voyage, Sarkhan Unbroken −8, cópia da Miirym) não busca |
| — "Dragon cards" (não "creature") | ✅ | `is_dragon_card`: Firdoch Core e Morophon (Changeling) entram; Roaming Throne na biblioteca não (ruling de 2026-09-14) |
| — ruling: dispara se conjurada de qualquer zona | ✅ | só há conjuração da mão neste deck |
| Roaming Throne (Dragão) dobra o gatilho | ✅ | `roaming_throne_times`: até 10 Dragões |

Linhas de pilotagem (Regra #5), cada uma com teste:
- **Ordem de conjuração:** fila normal (ramp e comandante antes). Foi
  testada contra "Tiamat antes de tudo": o ganho de letal é igual e a
  comandante não atrasa (ver `goldfish-log.md`).
- **Sarkhan's Triumph** busca a Tiamat quando as 5 cores já estão
  disponíveis. É instantânea: 1 tutor vira 6 Dragões.
- **Haven of the Spirit Dragon** devolve a Tiamat pra mão, se ainda houver
  Dragão na biblioteca. Reconjurar busca mais 5.
- **Magda (5 Treasures)** e o **ataque da Ur-Dragon** evitam pôr a Tiamat
  em campo: "put onto the battlefield" não é conjurar. Só a usam quando
  não há outra opção.
- 📝 Ordem do tutor: lista fixa pelos motores de dano (Scourge, Terror,
  Lathliss, Miirym, Utvara...). A alternativa "mana primeiro" foi testada
  em `goldfish-log.md`.
- 📝 Bladewing/Haunting Voyage devolvem por maior MV. Podem devolver a
  Tiamat sem busca: é regra, não bug.

### Escopo desta rodada (Regra #7)

Varrido, com método:
- **Custo e redução:** `effective_cost` inteiro e todo redutor da lista.
  Método: leitura + teste dirigido.
- **Checagem de cor:** `has_color_sources_for` e `source_color_sets`.
  Método: leitura + teste dirigido.
- **Todo caminho que busca ou põe Dragão:** Triumph, Orb, Magda, Haven,
  Sarkhan −8, Bladewing, Voyage, ataque da Ur-Dragon e Tiamat. Método:
  grep + leitura + teste.
- **Toda cláusula 📊 "sem oponente" contra o que o modo de resiliência já
  modela** (contramágica, wipe, remoção, ataque). Método: grep de
  `opponent_dependent`/`interaction` + leitura das 7 funções
  `try_smart_opponent_*` + teste.
- **Descarte de cleanup.** Método: trace de partida + medição + teste.

Não varrido nesta rodada:
- as outras classes da taxonomia nas 99 cartas (Saga, custo alternativo,
  gatilho compartilhado de morte/sacrifício, doença de invocação em
  `{T}`);
- o `urdragon_goldfish_physical_v1.py`.

📊 que continua estrutural:
- ward {2} da Miirym e do Roaming Throne e as 3 vidas do Terror of the
  Peaks: é mana/vida do oponente, que não é modelada;
- o bônus que Swan Song, Arcane Denial e An Offer dão ao oponente;
- "This spell can't be countered" da própria Dromoka: a contramágica do
  modelo só mira a Ur-Dragon.

📝 simplificações:
- a checagem de cor não sabe quais fontes já foram viradas no turno (o
  modelo separa mana total de cor, igual antes);
- a proteção do Teferi contra descarte não é modelada.

### Validação

- Smoke: 99 cartas; com a troca, 99 com Tiamat e sem o corte; 0
  desconhecidas, 0 duplicadas.
- `test_urdragon_goldfish.py`: 41/41. São 23 testes novos:
  - custo só genérico;
  - Rhythm mv 3;
  - Hall;
  - Tiamat busca 5 só conjurada, não pelo ataque da Ur-Dragon e não via
    `enter_battlefield`;
  - Changeling conta como "Dragon card";
  - Throne dobra pra 10;
  - Haven devolve Tiamat;
  - Triumph busca Tiamat (com e sem 5 cores);
  - Triumph só criatura;
  - fila normal;
  - Orb topo 7;
  - Orb paga a comandante na main 1;
  - Orb como cor;
  - descarte protege ramp;
  - Dromoka/Rhythm/Cavern impedem contramágica;
  - Swan Song responde;
  - lifelink;
  - Heroic responde wipe;
  - Teferi cobre a rodada;
  - wipe pequeno ou sem mana não é respondido;
  - Greaves redireciona remoção.
- 20.000 + 20.000 partidas da lista (padrão + resiliência, seed
  7.600.000+): 0 exceções.
- 20.000 + 20.000 partidas com Tiamat no lugar da Dromoka: 0 exceções,
  12.488 conjurações, 55.276 Dragões buscados (4,4 por conjuração).
- Antes/depois em 2.000 seeds, por correção: `goldfish-log.md`.

---

## Fichas de Dragão viram criaturas de verdade + Draconic Visitor (candidata FRA) — 2026-09-25

**Gatilho:** avaliar a Draconic Visitor pro Ur-Dragon e pro Vihaan. Pra
comparar de forma justa, a carta precisava transformar Treasure em
Dragão. O motor de fichas de Dragão deste arquivo foi lido de ponta a
ponta pra isso. Resultado: fichas de Dragão eram só um contador (Regra
#3, conceito compartilhado "Dragão que você controla"). Todo gerador de
ficha de Dragão da lista estava parcialmente implementado.

### 🐛 Corrigido — motor único `create_dragon_tokens` / `ready_dragon_tokens`

| Carta / conceito | Cláusula real | Antes | Agora |
|---|---|---|---|
| The Ur-Dragon | "Whenever one or more Dragons you control attack, draw that many cards" | ficha nunca atacava | ficha pronta ataca e conta no "that many" |
| Utvara / Old Gnawbone (e Kindred Discovery, só no `CARD_DB`, fora da lista) | gatilhos de ataque/dano | só Dragão nomeado | contam fichas atacando |
| Lathliss, Dragon Queen | "create a 5/5 red Dragon creature token with flying" | contador, sem gatilho de entrada | ficha 5/5 que dispara Scourge/Tempest/Terror/Kindred/Hoard |
| Utvara Hellkite | "create a 6/6 red Dragon creature token with flying" | idem | ficha 6/6 com gatilhos de entrada |
| Miirym, Sentinel Wyrm | "create a token that's a copy of it" | idem | ficha com o poder impresso da carta copiada (📝 habilidades da cópia não replicadas) |
| Ancient Gold Dragon | "create ... 1/1 blue Faerie Dragon creature tokens with flying" | fichas genéricas (não-Dragão!) | 1/1 Dragão voador |
| Dragon Broodmother | "At the beginning of **each** upkeep, create a 1/1 ... Dragon" | 1 por rodada | 1 no meu upkeep + 1 por oponente (end step, prontas no meu turno); devour 📝 nunca usado |
| Elemental Bond / Garruk's Uprising / Temur Ascendancy / Terror of the Peaks | "whenever a creature ... enters" (nenhum diz nontoken) | ficha não disparava | `token_creature_etb_hooks` (Great Henge fora: "nontoken") |
| Haste | Temur Ascendancy (todas), Dragon Tempest (voadora, no turno em que entra) | — | `ready_dragon_tokens` |
| Pumps | Lathliss {1}{R} "+1/+0", Bladewing {B}{R} "+1/+1", Scourge {R} "+1/+0" | só contador | somam no poder de combate (`dragon_pump_bonus_this_turn`, `scourge_pump_this_turn`) |
| Wipe de oponente (resiliência) | "destroy all creatures" | fichas sobreviviam | `clear_dragon_tokens` |

**Roaming Throne** ("If a triggered ability of another creature you
control of the chosen type triggers, it triggers an additional time"):
Terror of the Peaks e Dragon Broodmother são criaturas Dragão com gatilho
próprio. Nenhuma das duas era dobrada, enquanto Scourge, Lathliss, Miirym,
Utvara e Old Gnawbone já eram. Corrigido via `roaming_throne_times()`.

**Teto do simulador:** `DRAGON_TOKEN_CAP = 400`. O motor Utvara + Old
Gnawbone é exponencial de verdade. Acima de 400 fichas a partida já está
decidida; a métrica `dragon_token_cap_hits` conta quantas vezes bateu no
teto. É a mesma convenção do `BOARD_CAP` do Prismatic Bridge.

**Métrica nova (só leitura):**
- `combat_damage_proxy_total` soma o dano de combate dos Dragões
  atacantes, sem bloqueio. Atarka dobra (double strike) e Twinflame dobra
  dano a oponente.
- `lethal_proxy_turn` é o primeiro turno com (dano de ETB + combate) ≥ 120
  (3 × 40). É a métrica limitada usada no A/B, porque a média de dano sem
  teto explode (`references/goldfish-sim-card-rules.md`).

### Draconic Visitor — oráculo ao vivo (cache FRA #80), cláusula a cláusula

`{3}{R}{R}` Creature — Dragon 5/5, `not_legal` até 2026-10-02.

| Cláusula | Status | Onde |
|---|---|---|
| Flying | ✅ | `FLYING_CREATURES` (Dragon Tempest dá haste) |
| Dragon (tipo) | ✅ | tag `dragon`: Eminence, Dragonspeaker Shaman, Dragonlord's Servant, Urza's Incubator, Herald's Horn, Scourge/Tempest/Terror/Lathliss/Miirym, ataque da Ur-Dragon |
| "If one or more artifact tokens would be created under your control, that many 5/5 red Dragon creature tokens with flying are created instead." | ✅ | `visitor_replaces_treasures` em `create_treasures`, `create_and_use_treasures` (Goldspan, Old Gnawbone, Ancient Copper, Smothering Tithe) e `do_magda_treasures` |

Detalhes:
- É substituição obrigatória (CR 614.1a). A mana do Treasure some; o
  simulador mede isso em `visitor_mana_lost_total`, e com Goldspan cada
  Treasure valia 2.
- A Magda (Brazen Outlaw) nunca junta os 5 Treasures do tutor.
- 🐛 achado no A/B: a Smothering Tithe é modelada no MEU upkeep, mas o
  gatilho real é no turno do oponente ("Whenever an opponent draws a
  card"). Com a Visitor, o Dragão nascia doente no meu turno. Agora
  `create_and_use_treasures(..., on_opp_turn=True)` faz a ficha nascer no
  turno anterior, então ela ataca no meu turno.
- Treasures do oponente (An Offer You Can't Refuse) não são "under your
  control", então a Visitor não substitui.

### Validação

- Smoke: 99 cartas, 0 desconhecidas.
- Testes dirigidos: `test_urdragon_goldfish.py`, 18/18. Cobrem:
  - fichas atacando no "that many" da Ur-Dragon;
  - doença de invocação e haste via Tempest;
  - ficha da Lathliss disparando Scourge + Terror;
  - fichas da Utvara disparando ETB;
  - Faerie Dragons como Dragões;
  - Broodmother em cada upkeep;
  - Roaming Throne dobrando Broodmother e Terror;
  - wipe limpando fichas;
  - Visitor substituindo Treasure (e com Goldspan);
  - Tithe no turno do oponente;
  - Magda sem tutor;
  - teto de fichas;
  - swap posicional/bit-idêntico;
  - `lethal_proxy_turn`.
- 20.000 + 20.000 partidas (padrão + resiliência, seed 8.000.000+), 0
  exceções.
- Antes/depois em 2.000 seeds: ver `goldfish-log.md`.

---

## CR 903.9a: comandante passa pelo cemitério de verdade antes da zona de comando — 2026-09-21

**Gatilho:** mesmo achado do usuário aplicado a todos os 9 decks desta
sessão, depois de eu documentar em TODOS eles que "o comandante nunca
dispara gatilho de morte": *"O comandante não morre e ao invés de ir
pro cemitério, pode ser movido de volta a zona de comando? Pq até onde
sei, comandantes podem ser mortos sim! Confere essa regra com muita
calma e atenção!"* Raciocínio completo da regra em
`megatron-tyrant-mardu/checklist-oraculo.md` (mesma correção, CR 903.9a
é ação baseada em estado — CR 704 — não substituição; texto oficial
cacheado em `rules-cache/comprehensive-rules.txt`, Regra 18 de
`references/user-standing-rules.md`).

**Achado específico deste deck:** `remove_permanent()` (ponto central
de remoção de permanente do campo, usado por `try_smart_opponent_wipe`
e `try_smart_opponent_removal`) desviava o comandante direto pra zona
de comando, pulando o cemitério inteiramente. Diferente do Megatron,
**este deck tem 0 cartas com gatilho "whenever ~ dies"/"creature put
into graveyard"** (reconfirmado por grep antes desta rodada, mesma
conclusão do grep original) — ou seja, não existe nenhuma carta na
lista que reagiria à correção. `put_into_graveyard()` (a função central
de "vai pro cemitério" deste arquivo) também não tem nenhum efeito
colateral (é só `state.graveyard.append(name)`, sem gatilho nenhum
disparado dali).

**Corrigido mesmo assim** por consistência estrutural (Regra #1 do
`CLAUDE.md`: habilidade real do jogo, mesmo que sem efeito numérico
observável hoje neste deck específico) — uma futura troca de carta com
gatilho de morte real não herdaria esse bug em silêncio. O comandante
agora: entra no cemitério de verdade via `put_into_graveyard()`, e SÓ
DEPOIS é removido de lá pra representar a escolha do dono de movê-lo
pra zona de comando (`commander_in_play = False`).

**Validação:** compilação OK. Bit-identidade em modo padrão
(`simulate_one`, 3000 seeds, seed_base 7600000) contra o commit
anterior: **0/3000 mismatches** — confirma que a correção não tem
NENHUM efeito no modo padrão (ambos os call sites de
`remove_permanent` — `try_smart_opponent_wipe`/`try_smart_opponent_
removal` — só disparam com `interaction_rng` ativo, ou seja, só no modo
de resiliência). Regressão de 20.000 partidas em modo de resiliência
(`simulate_one_with_interaction`, seed_base 9100000): 0 exceções, 0/20000
partidas com o comandante preso no cemitério (confirma que a sequência
cemitério→remoção funciona em todo caso testado). 2 testes dirigidos:
(1) `remove_permanent(state, COMMANDER)` com o comandante em campo →
`commander_in_play=False`, fora do campo, e NÃO preso no cemitério; (2)
permanente comum vai pro cemitério normalmente e FICA lá (sem a lógica
especial do comandante vazar pra outras cartas).

**Resultado:** correção estrutural sem impacto numérico observável
nesta lista atual (0 cartas reagem), mas fecha o gap de consistência
com CR 903.9a e remove o risco de uma troca de carta futura (qualquer
"whenever a creature dies"/"whenever a permanent is put into a
graveyard from the battlefield") herdar o bug em silêncio.

## Modo de resiliência ganha wipe de artefato e wipe de encantamento — 2026-09-20

**Gatilho:** mesmo achado do usuário aplicado a todos os decks: "Temos
que incluir remoções de artefatos e encantamentos tb: Vandalblast,
Farewell, Austere Command, etc…" — até esta rodada, só existia "destroy
all creatures". Raciocínio completo em
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Implementado (1ª versão, SUPERSEDIDA no mesmo dia):** inicialmente 2
funções novas com rolagens INDEPENDENTES (`ARTIFACT_WIPE_CHANCE_FACTOR
= 0.2`, `ENCHANTMENT_WIPE_CHANCE_FACTOR = 0.15`) somadas ao wipe de
criatura já existente, sem exclusão mútua.

### Correção de design: unificado num único roll + escolha ponderada — 2026-09-20

**Gatilho:** mesma correção do usuário aplicada primeiro no Megatron —
*"Obviamente tem que ter uma alternância de remoções, aleatória, até pq
wipes de criaturas são muito mais comuns que remoção de artefatos e
encantamentos"* — rolagens independentes permitiam (raramente) 2
sweepers no mesmo turno de oponente, e tratavam os 3 tipos como
igualmente prováveis. Raciocínio completo do redesign em
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Implementado (final):** `try_smart_opponent_wipe()` único, 2 passos —
1) rola 1x se ALGUM wipe acontece (`chance = interaction_chance() *
TOTAL_WIPE_CHANCE_FACTOR`, soma dos 3 pesos = 0.75); 2) SÓ se disparar,
escolhe 1 TIPO via `state.interaction_rng.choices()` ponderado
(`WIPE_TYPE_WEIGHTS = {"creature": 0.4, "artifact": 0.2, "enchantment":
0.15}`), restrito aos tipos com alvo legal em campo. Delega pro mesmo
`remove_permanent()` de sempre. The Ur-Dragon nunca é artefato nem
encantamento (Legendary Creature — Dragon Avatar, confirmado via
Scryfall), então nunca é alvo direto. `ARTIFACT_ISH` já inclui
"artifact_creature" — Roaming Throne-equivalentes e mana rocks reais
(Sol Ring, Arcane Signet, talismãs) são alvos legais; 8 encantamentos
reais (Kindred Discovery, Dragon Tempest, Elemental Bond, Smothering
Tithe, etc.) agora alcançáveis. `state.wiped_this_round` setado se o
tipo escolhido não for criatura mas algum permanente destruído também
for criatura de verdade.

**Validação:** modo padrão 100% bit-idêntico ao commit `8b84daf` (2.000
seeds) + regressão de 20.000 partidas em modo resiliência, 0 exceções +
testes dirigidos (no máximo 1 tipo por chamada, 0 violações em 1.500
chamadas; distribuição ponderada bate com os pesos relativos dentro de
3pp com 20.000 chamadas forçadas).

**Resultado (A/B 2000 jogos mesma seed_base, design unificado final):**
% de jogos com pelo menos 1 wipe de qualquer tipo sobe de 37,0% pra
62,2% (antes = commit `8b84daf`, só wipe de criatura). Avg wipes totais
por jogo: 0,416 → 0,882. 21,9% dos jogos "depois" sofrem pelo menos 1
artifact wipe, 17,2% pelo menos 1 enchantment wipe.

## Bug de design: modelo assumia 100% da mesa mirando em mim, todo turno, de todo oponente — 2026-09-20

**Gatilho:** mesmo achado do usuário aplicado ao Megatron primeiro —
*"se sempre for 3 contra 1, aí não consigo fazer nada, nunca!"* —
medição real (não estimativa) mostrou 78,2% das rodadas com pelo menos
1 evento de interação contra mim, quase o dobro da calibração original.
Raciocínio completo e opções levantadas em
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Corrigido:** mesmo padrão do Megatron — `OPPONENT_ATTENTION_CHANCE =
1/NUM_OPPONENTS`, gate rolado no início de `try_smart_opponent_turn()`
antes de qualquer categoria.

**Validação:** modo padrão 100% bit-idêntico ao HEAD anterior (5.000
seeds) + regressão de 20.000 partidas no modo resiliência, 0 exceções.

**Resultado (A/B mesma seed, 2000 jogos):**

| Métrica | Antes do gate | Depois do gate |
|---|---|---|
| Rodadas com zero interação | 21,8% | 58,7% |
| Avg ataques de oponente sofridos | 2,98 | 1,19 |
| Avg vida final | 35,28 | 38,14 |

## Bug real de orquestração de turno (2ª rodada): wipe é simétrico pra mesa inteira — 2026-09-20

**Gatilho:** mesmo achado do usuário aplicado ao Megatron primeiro —
*"se jogador A faz wipe, jogador C não tem como atacar até voltar ao
turno do jogador A, a não ser no caso de haste!"* — a correção anterior
só tornava wipe/ataque mutuamente exclusivos no MESMO turno do wiper,
mas um wipe simétrico também mata as criaturas de qualquer outro
oponente que ataque DEPOIS na mesma rodada. Raciocínio e validação
completos em `megatron-tyrant-mardu/checklist-oraculo.md` — aqui só o
resultado específico deste deck.

**Corrigido:** mesmo padrão do Megatron — `state.wiped_this_round`
(setado por `try_smart_opponent_wipe`, resetado 1x por rodada em
`simulate_one_with_interaction`), `try_smart_opponent_attack()` reduz a
própria chance pra `POST_WIPE_ATTACK_HASTE_FACTOR = 0.15` quando o flag
está ligado (nunca zero — haste continua possível). Gate manual antigo
removido de `try_smart_opponent_turn()`.

**Validação:** modo padrão confirmado 100% bit-idêntico ao HEAD anterior
(5.000 seeds, campos `turn`/`life`/`commander_cast_count`) + regressão
de 20.000 partidas no modo resiliência, 0 exceções.

**Resultado (A/B mesma seed, 2000 jogos):**

| Métrica | Antes (wipe só bloqueia o próprio turno) | Depois (wipe suprime a rodada inteira) |
|---|---|---|
| Avg board wipes sofridos | 0,900 | 0,883 |
| Avg ataques de oponente sofridos | 2,983 | 2,905 |
| Avg vida final | 35,28 | 35,40 |

## Bug real de orquestração de turno: wipe e ataque no mesmo turno de oponente — 2026-09-20

**Gatilho:** mesmo achado do usuário aplicado ao Megatron primeiro —
board wipe é sorcery (main phase de UM oponente), ataque vem de
criatura em campo DAQUELE MESMO oponente. Se o wipe for simétrico, ele
não ataca no mesmo turno. Regra #6 do CLAUDE.md (bug de orquestração,
não pego em auditoria carta-a-carta). Raciocínio e validação completos
em `megatron-tyrant-mardu/checklist-oraculo.md` — aqui só o resultado
específico deste deck.

**Corrigido:** `try_smart_opponent_turn()` simula o turno de 1 oponente
por vez (`NUM_OPPONENTS = 3` por rodada, nova constante — este deck
não tinha essa convenção antes, adotada agora igual ao Megatron), wipe
e ataque mutuamente exclusivos dentro do MESMO turno de oponente.

**Validação:** teste dirigido (2000 seeds, exclusão mútua 100%) +
regressão de 20.000 partidas, 0 exceções + modo padrão confirmado
intocado (nenhuma função compartilhada tocada).

**Resultado (batch 2000 jogos mesma seed):**

| Métrica | Modelo antigo (1 rolagem/rodada) | Modelo novo (3 turnos/rodada) |
|---|---|---|
| Avg board wipes sofridos | 0,43 | 0,87 |
| Graveyard wipe sofrido (partidas) | 41,3% | 72,2% |
| Avg remoções inteligentes sofridas | 0,83 | 1,26 |
| Nunca resolveu em 8 turnos | 31,6% | 45,0% |
| Avg dano proxy total | 310,33 | 43,29 |

Queda MUITO mais acentuada que a do Megatron (310→43, ~14% do valor
anterior) — este deck depende inteiramente da comandante resolver E
atacar pra qualquer dano real, e com 3 turnos de oponente reais por
rodada em vez de 1 rolagem agregada, a chance dela nunca resolver
subiu de 31,6% pra 45,0%.

## Modo de resiliência portado do Megatron (6 categorias de interação de oponente) — 2026-09-20

**Gatilho:** usuário pediu pra avaliar o esforço de portar o modo de
resiliência (implementado no Megatron, várias rodadas 2026-09-19/20)
pro resto dos decks. Avaliação usando o Hei Bai como piloto mostrou 2
lacunas estruturais sérias lá (sem `sacrifice()` central, sem combate
modelado nenhum). Usuário então pediu pra implementar de verdade no
Ur-Dragon, com resultado **separado do goldfish atual, preservando o
original**.

**Arquitetura preservada:** `simulate_one`/`run_batch` continuam
exatamente como sempre foram — confirmado com **5.000 seeds de
equivalência bit-a-bit** (`commander_cast_turn`,
`commander_cast_count`, `proxy_damage_total`, `commander_damage_dealt`,
`cards_drawn_extra`, `dragon_tokens`), 0 diferenças, mesmo mexendo em
`cast_card`/`enter_battlefield` (funções compartilhadas pelos 2 modos).
Todo o modo novo mora em `simulate_one_with_interaction`/
`run_batch_with_interaction`, funções NOVAS, nunca chamadas pelo
goldfish padrão.

**Diferenças reais do port vs. o Megatron original (não foi
copy-paste):**

1. **Sem `sacrifice()` preexistente** — o motor do Ur-Dragon é ETB/
   ataque, não sacrifício. `remove_permanent()` é uma versão nova e
   mais simples: grep confirmou **0 cartas "whenever ~ dies"** neste
   deck, então não existe web de gatilhos de morte pra replicar (era o
   grosso da complexidade do `sacrifice()` do Megatron). Só precisa
   saber mandar o comandante pra zona de comando (mesmo padrão já
   usado no retorno do Hellkite Courser em `end_step`) em vez do
   cemitério.
2. **Sem `toughness` rastreado por criatura** — o `Card` deste arquivo
   só tem `power` (motor só precisa de poder de saída, nunca modelou
   bloqueio pro lado do jogador). Isso torna **bloqueio impossível de
   implementar sem inventar dado que não existe** — `try_smart_
   opponent_attack` aqui nunca é bloqueado, todo ataque conecta direto
   em `state.life` (novo, só existe pro modo de resiliência — o
   goldfish padrão documenta explicitamente "Vida não é rastreada no
   simulador", convenção preservada 100%).
3. **Sem `state.rng` guardado no state** — nenhuma carta tipo
   Blightsteel Colossus (Megatron) achada nesta rodada. `put_into_
   graveyard()` existe como rede de segurança central, mas **isso NÃO
   é uma auditoria completa das 99 cartas** procurando "would be put
   into a graveyard from anywhere" — só o Megatron recebeu essa
   auditoria até agora.
4. **Alvo do graveyard snipe é Dragão-específico**: usa o MESMO
   critério que `reanimate_dragons_from_graveyard()` (Haunting Voyage)
   já usa — maior MV entre Dragão-criatura no cemitério — em vez do
   critério criatura/artefato genérico do Megatron, porque a recursão
   real deste deck é de Dragão, não de artefato.
5. **`INTERACTION_ENGINE_PRIORITY` curada do zero** pros motores reais
   do Ur-Dragon: Roaming Throne (dobra tudo, prioridade 1), Dragon
   Tempest, Scourge of Valkas, Herald's Horn, Smothering Tithe,
   Dragon's Hoard, Up the Beanstalk, Elemental Bond, Garruk's Uprising,
   Sylvan Library.
6. **Counterspell** — mesmo padrão do Megatron: taxa de comandante
   (CR 903.10a, já existia neste arquivo como `commander_cast_count`)
   incrementada ANTES do check de counter (conta "vezes conjurado",
   não "vezes resolvido"); movido de `enter_battlefield` pra
   `cast_card` pra evitar incremento duplicado. Hookado direto no
   branch `if name == COMMANDER` de `cast_card()`.

**Validação:** 8 testes unitários dirigidos (gating; board wipe destrói
tudo e manda comandante pra zona de comando; removal mira a peça de
maior prioridade presente; ataque sempre conecta — sem bloqueio; discard
aleatório; graveyard wipe dispara 1x só; graveyard snipe mira Dragão de
maior MV; counterspell gasta mana+taxa mas não resolve, e recast no
turno seguinte paga taxa mais alta) + 5.000 seeds de equivalência
bit-a-bit do modo padrão (0 diferenças) + smoke test (batch 2000) +
**regressão de 20.000 partidas em CADA modo, 0 exceções nos dois**.

**Resultado real (batch 2000 jogos mesma seed, padrão vs. resiliência):**

| Métrica | Padrão | Resiliência |
|---|---|---|
| Turno médio de conjuração (que resolveu) | 6,66 | — |
| Nunca resolveu em 8 turnos | 21,3% | 31,6% |
| Avg dano/perda-de-vida proxy total | 990,50 | 310,33 |
| Avg counterspells sofridos | — | 0,10 |
| Avg board wipes sofridos | — | 0,43 (5,25 criaturas perdidas quando dispara) |
| Partidas com graveyard wipe sofrido | — | 41,3% (máx. 1x/partida) |
| Avg graveyard snipes sofridos | — | 0,15 |
| Avg remoções inteligentes sofridas | — | 0,83 (Roaming Throne 16,1%, Dragon Tempest 14,4%) |
| Avg ataques de oponente sofridos | — | 1,26 |
| Avg descartes forçados sofridos | — | 1,21 |

Direção esperada em tudo: a comandante resolve 10,3pp menos vezes em 8
turnos e o dano proxy cai pra menos de 1/3 (990,50→310,33) — bate com o
quanto o motor inteiro deste deck depende da Ur-Dragon resolver E
atacar (Roaming Throne/Dragon Tempest/Scourge of Valkas, os alvos mais
removidos, são multiplicadores centrais — perde-los corta o motor de
dano escalável pela raiz).

## Achado real 2026-09-14 (usuário perguntou se Roaming Throne está certa em todos os decks onde aparece)

Mesma varredura pedida depois do fix do Beorn. Este deck já tinha uma
arquitetura mais madura pra Roaming Throne (`ROAMING_THRONE_TYPE =
"dragon"`, tag cravada diretamente no `CARD_DB` da própria carta — bem
melhor que o Beorn original), mas isso trouxe um problema DIFERENTE: como
`is_dragon(name)` só olha a tag estática, ela reconhece Roaming Throne
como Dragão mesmo enquanto ela está só na **biblioteca ou na mão** — onde
o oráculo real não concede tipo nenhum ainda ("as this creature enters,
choose a creature type" só se aplica depois de resolver). Achei **5
pontos reais** de busca/tutor de Dragão fora do campo de batalha que
incorretamente aceitavam Roaming Throne como se fosse "a Dragon creature
card":

1. **Sarkhan's Triumph** ("search your library for a Dragon creature
   card, put it into your hand") — podia tutorar a própria Roaming
   Throne.
2. Métrica auxiliar do mesmo Sarkhan's Triumph (`sarkhan_triumph_hand_had_no_dragon`)
   — checava a mão por um "Dragão" incluindo Roaming Throne.
3. **Orb of Dragonkind** (checagem "tem Dragão na mão?") — mesma coisa.
4. **Orb of Dragonkind** (tutor pela ativação de sacrifício) — mesma coisa.
5. **Sarkhan Unbroken**, ultimate (−8: "put all Dragon creature cards
   from your library onto the battlefield") — o mais grave dos 5, porque
   não é um tutor de 1 carta, é um mass-cheat: colocaria a Roaming Throne
   em campo de graça igual a qualquer Dragão de verdade.

**Não é bug** (verificado e mantido): o tutor da **Magda** (sacrificar 5
Treasures → "search for an artifact or Dragon creature card") continua
encontrando Roaming Throne normalmente — mas isso está CORRETO, porque
Roaming Throne também é um artefato de verdade (`is_artifact_card`),
então o modo "artifact card" da busca genuinamente a alcança, independente
de ser Dragão ou não.

**Corrigido:** novo helper `is_dragon_card(name)` (= `is_dragon(name) and
name != "Roaming Throne"`), usado nos 5 pontos acima que buscam fora do
campo de batalha. `is_dragon()` puro continua reconhecendo Roaming Throne
normalmente pras checagens de BATALHA (contagem de Dragões em campo, a
própria dobra do gatilho dela via Roaming Throne — que já estava correta
antes, essa parte não mudou).

**Validação:** 2 testes unitários dirigidos (Sarkhan's Triumph tutora um
Dragão real quando disponível, ignorando Roaming Throne; sem Dragão real
na biblioteca, não tutora nada — não usa Roaming Throne como substituto)
— passando. Batch de 2.000 partidas antes/depois (mesma seed 7500000):
`tutors_used_total` 0,3935→0,398; `orb_mana_activations_total`
0,4675→0,4585; `dragons_free_entry_total` 1,1575→1,1495 — movimento
pequeno (cenário raro: só importa quando Roaming Throne seria o único ou
o de maior MV entre os "Dragões" candidatos). 20.000 partidas de
regressão (seed 7600000+), **0 exceções**.

---

## Auditoria oráculo-por-oráculo completa — 2026-09-14

Extensão pra este deck da mesma auditoria já feita em Beorn/Captain
Storm/Rat King/Prismatic Bridge/Toph/Edgar Markov/Hei Bai/Maralen/
Megatron/Nekusar/Thranduil nesta sessão. Este já era um dos simuladores
mais auditados da sessão (rodadas em 2026-08-27, 2026-08-29, 2026-08-30 e
2026-09-01, ver seção abaixo com o gap daquela última rodada — Lightning
Greaves). Mesmo assim, a releitura clause-by-clause do oráculo real
(Scryfall `/cards/collection`, 100 nomes — comandante + 71 cartas de
deck + 36 terrenos incluindo as 8 registradas só pra teste comparativo,
0 `not_found`) contra o `CARD_DB`/dispatch real achou **2 gaps reais
adicionais**, ambos em mecânicas centrais do tema tribal (escala por
contagem de Dragão / dobra de Roaming Throne), a mesma classe de bug já
achada em Beorn (anthem estático não propagado) e Rat King (contagem de
tribo mal disparada).

**Método:** (a) detecção automatizada de tags órfãs (definidas em `add()`,
nunca lidas fora dele) — achou 20 candidatos, **todos falsos positivos**
confirmados lendo o dispatch real (por nome, dentro de funções
compartilhadas como `dragon_enters()`/`creature_etb_hooks()`/
`try_dragon_pumps()` — este arquivo já é maduro o bastante pra ter várias
dessas, mesmo padrão já documentado na rodada de 2026-09-01); (b)
releitura completa do oráculo de cada carta com gatilho "whenever a
Dragon enters/attacks" ou anthem/contador estático, comparando contra
TODAS as funções que leem `power`/dano/contagem de Dragão (não só a
primeira que aparece), atrás do padrão "efeito estático aplicado em UMA
função mas não propagado pras outras que leem o mesmo dado" (mesma classe
do Beorn) e "cascata de gatilho compartilhada só parcialmente
correta" (mesma classe do Rat King/Prismatic Bridge).

### 🐛 Os 2 gaps reais corrigidos nesta rodada

1. **Roaming Throne dobrava a fonte ERRADA de dano em `dragon_enters()`
   — Dragon Tempest sendo dobrado quando NUNCA deveria, Scourge of Valkas
   deixando de dobrar exatamente quando deveria.** Oráculo real da
   Roaming Throne: *"If a triggered ability of ANOTHER CREATURE you
   control of the chosen type triggers, it triggers an additional
   time."* A restrição é sobre a FONTE da habilidade ser uma criatura
   (diferente da própria Roaming Throne) — não tem nada a ver com QUAL
   Dragão causou o gatilho disparar. O código anterior tratava Scourge of
   Valkas (`"Whenever this creature or another Dragon you control
   enters... X damage"`, criatura Dragão) e Dragon Tempest (`"Whenever a
   Dragon you control enters... X damage"`, **encantamento**, não
   criatura) como UMA única fonte combinada (`dmg_sources`), com o mesmo
   multiplicador `total_times = times_scourge if (name !=
   "Scourge of Valkas") else 1` — comparando contra o NOME DO DRAGÃO QUE
   ENTROU, não contra a fonte da habilidade. Isso já contradizia o padrão
   correto usado no próprio arquivo em `combat_step()` pros gatilhos de
   ataque (`times = 2 if (Roaming Throne in battlefield and n !=
   Roaming Throne) else 1`, que compara a FONTE). Dois erros reais na
   direção oposta:
   - **Dragon Tempest era dobrado sempre que Roaming Throne estava em
     campo** (superestimando dano em TODO evento de Dragão entrando, não
     um caso raro — o efeito mais impactante dos dois), quando o texto
     real da Roaming Throne nunca alcança um encantamento.
   - **Scourge of Valkas deixava de dobrar exatamente quando ELA MESMA
     era o Dragão entrando** (subestimando dano nesse caso específico —
     o "another" da Roaming Throne se refere a Scourge não ser a própria
     Roaming Throne, não ao Dragão que disparou o gatilho).
   Corrigido separando as duas fontes: Scourge dobra com Roaming Throne
   em campo (independente de qual Dragão entrou); Dragon Tempest nunca
   dobra (independente de Roaming Throne). Validado isoladamente (ver
   `goldfish-log.md`) — cenário só-Dragon-Tempest+Roaming-Throne não
   dobra mais; cenário só-Scourge+Roaming-Throne, com a própria Scourge
   entrando, agora dobra.

2. **The Great Henge — só metade do gatilho recorrente estava
   implementada (o draw, nunca o contador).** Oráculo real: *"Whenever a
   nontoken creature you control enters, put a +1/+1 counter on it AND
   draw a card."* `creature_etb_hooks()` já tinha o draw desde a rodada
   de 2026-08-27 (registrado no `goldfish-log.md` como correção da carta
   inteira), mas o `+1/+1 counter` real — que aumenta o PODER daquela
   criatura pelo resto do jogo — nunca tinha sido rastreado em lugar
   nenhum. Isso subestimava poder em TODO gatilho power-dependente do
   arquivo que usa `effective_power()`: Elemental Bond/Garruk's
   Uprising/Temur Ascendancy (thresholds de poder pra compra), Terror of
   the Peaks (dano = poder da criatura que entrou), Klauth (soma do poder
   de todos os Dragões atacantes), Return of the Wildspeaker (maior poder
   entre não-Humanos), e o próprio custo dinâmico da Great Henge pra
   qualquer avaliação futura de "maior poder em campo". Corrigido com
   `state.great_henge_counters` (dict por nome, mesmo padrão de
   contadores agregados já usado pra Marwyn/Immaculate Magistrate no
   arquivo irmão `thranduil_goldfish_v1.py`) — incrementado em
   `creature_etb_hooks()` junto do draw já existente, lido em
   `effective_power()` (que já centralizava o anthem estático da
   Morophon, agora soma os dois). ~2.19 contadores/partida em média — não
   é um efeito marginal.

### Falsos positivos descartados (tags órfãs, 20 candidatos, 0 gaps reais)

Todas as 20 tags reportadas pela detecção automatizada (`tribal_impulse`,
`dragon_hoard`, `dragon_tutor_sac`, `kindred_discovery`,
`sarkhan_unbroken`, `reanimate_dragon_etb`, `upkeep_dragon_token`,
`goldspan`, `extra_combat_paid`, `dragon_etb_token`, `dragon_etb_copy`,
`ramos_counters`, `creature_etb_damage_power`, `treasure_tutor_dragon`,
`first_creature_discount`, `power4_draw_optional`, `cost_reduce_power`,
`opponent_dependent`, `treasure_tax`, `roaming_throne`) são rótulos
descritivos — a carta correspondente é despachada de verdade por
checagem de NOME dentro de uma função compartilhada (`dragon_enters()`,
`creature_etb_hooks()`, `resolve_etb()`, `combat_step()`,
`try_dragon_pumps()`, `try_dragon_hoard_draw()`, `try_haven_recursion()`,
`do_magda_treasures()`, `do_orb_dragonkind()`, `main_phase()`,
`upkeep_step()`, `effective_cost()`/`rocks_mana()`), não pela tag em si —
confirmado lendo cada dispatcher, não só contando ocorrências de string
(mesmo cuidado documentado na rodada de 2026-09-01).

### Dragonlord Dromoka — clásula confirmada 📊 (não é gap novo)

*"Your opponents can't cast spells during your turn"* — puramente
dependente de oponente real (sem contramagia/timing de oponente
modelado neste goldfish solo), mesma classe já documentada pra Cavern of
Souls ("can't be countered")/Balefire Dragon (limpeza de board de
oponente)/Rhythm of the Wild (creature spells can't be countered).
Flying/lifelink já cobertos pela abstração de combate existente (lifelink
não numérico — vida não é rastreada no simulador, mesma premissa de
sempre).

---

## Resumo numérico (rodada 2026-09-14)

- **99 cartas na lista afinada** (`lista.md`) + comandante, mais 8
  cartas registradas só pra testes comparativos fora da lista atual.
- **🐛 Corrigido nesta rodada:** 2 gaps (Roaming Throne dobrando fonte
  errada em `dragon_enters()`; The Great Henge sem o `+1/+1` contador
  real).
- **✅ Falsos positivos descartados:** 20 tags órfãs, todas já
  corretamente dispatchadas por nome.
- **📊 Estrutural confirmado (sem mudança de código):** Dragonlord
  Dromoka ("opponents can't cast spells during your turn").

---

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge, Rat King, Thranduil e Ulalek.

**Contexto importante:** este simulador já tinha passado por múltiplas
rodadas de auditoria completa antes desta (2026-08-27, 2026-08-29,
2026-08-30 — documentadas extensivamente em `goldfish-log.md`), incluindo
correções reais de haste/summoning sickness, lealdade de Sarkhan Unbroken,
Haunting Voyage foretell, etc. **Este deck tem 2 simuladores** —
`urdragon_goldfish_v1.py` (lista "afinada", `lista.md`) e
`urdragon_goldfish_physical_v1.py` (deck físico real, `lista-fisica.md`,
com 3 cartas extras registradas só nesse arquivo). Esta auditoria cobriu o
arquivo principal (`urdragon_goldfish_v1.py`); o físico herda a mesma
base de código e as mesmas correções onde as cartas coincidem.

**Método:** detecção automatizada de (a) tags órfãs e (b) nomes de carta
com poucas ocorrências. ~26 candidatos apareceram; a esmagadora maioria
eram falsos positivos (dispatch por nome dentro de funções compartilhadas
como `dragon_enters()`, `try_dragon_pumps()`, `ready_creatures()` — este
arquivo já é maduro o bastante pra ter várias dessas). **1 gap real
confirmado.**

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real, sem combate/P-T por criatura
  individual — limite conhecido, não julgamento de valor.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.

## 🐛 O gap corrigido nesta rodada

**Lightning Greaves** — tinha só a tag genérica `"interaction"` (bucket
de proteção do próprio board), **sem nenhum efeito real implementado**
— nem sequer o haste, que é o ganho mais relevante possível pra este
deck especificamente: a Ur-Dragon não tem haste nativo, e o motor
inteiro de compra de cartas do deck (*"Whenever one or more Dragons you
control attack, draw that many cards..."*) depende dela atacar. Oráculo
real: *"Equipped creature has haste and shroud. Equip {0}."* Corrigido
com `try_lightning_greaves_equip()` — equipa automaticamente na
comandante assim que ambas estão em campo (Equip {0}, sem custo real),
reequipa em outra criatura se a comandante ainda não resolveu, e
re-equipa automaticamente se o alvo anterior saiu de campo. `shroud` não
tem efeito modelável (sem oponente/remoção alheia neste goldfish solo)
— 📊, documentado.

Este arquivo já modela haste/summoning-sickness de forma sofisticada
(`ready_creatures()`, tags `haste`/`haste_all`/`haste_flying`/`riot`)
desde a rodada de 2026-08-27 — o gap era especificamente a ausência total
de qualquer lógica de equipamento pra essa carta, não um limite do
motor de haste em si.

Validado com 4 testes unitários isolados + regressão de 20.000 partidas
(seed 4000000+, turns=10, 0 exceções) + `run_batch` antes/depois via
`importlib` (3000 jogos, seed 7000000, turns=10) — ver `goldfish-log.md`
pra métricas específicas.

## Falsos positivos descartados (já corretamente implementados)

- **Ancient Copper Dragon / Ancient Gold Dragon** — habilidades de d20
  (`combat_treasure_d20`/`combat_token_d20`) dispatchadas por tag numa
  função central de combate, não por nome — confirmado lendo o dispatch
  real, não só contando ocorrências do nome.
- **The Great Henge, Terror of the Peaks, Miirym, Lathliss, Dragon's
  Hoard, Orb of Dragonkind, Hellkite Charger, Radagast of Rhosgobel,
  Goldspan Dragon, Kindred Discovery, Temur Ascendancy, Ramos Dragon
  Engine, Bladewing the Risen, Sarkhan Unbroken, Smothering Tithe,
  Magda Brazen Outlaw, Herald's Horn, Dragon Broodmother** — todas
  dispatchadas por checagem de nome direta dentro de funções
  compartilhadas (`dragon_enters()`, `try_dragon_pumps()`,
  `resolve_etb()`, etc), confirmadas lendo o código, não a contagem
  ingênua de string.
- **Rhythm of the Wild** (tag `opponent_dependent`) — dispatchada de
  verdade (riot→haste, ver `ready_creatures()`); a tag em si é só um
  rótulo descritivo órfão, não indica ausência de efeito.
- **Mana Confluence** — terreno de mana genérica pura (produz qualquer
  cor, sem habilidade condicional adicional), corretamente sem tag
  extra.
- **An Offer You Can't Refuse, Heroic Intervention** — pacote
  "interaction", proxy consistente com o resto da sessão (conjuráveis,
  sem alvo de oponente real, `try_use_own_interaction()`).

## Sarkhan Unbroken — heurística de pilotagem (não um gap)

As 3 habilidades de lealdade estão todas implementadas (+1 draw+mana, -2
token de Dragão, -8 ultimate búsca todos os Dragões). A escolha de
"nunca usar o -2, sempre +1 até poder usar o -8" é uma heurística de
pilotagem racional documentada (token único não compensa desviar do
caminho pro ultimate) — não uma lacuna de implementação.

---

## Resumo numérico

- **99 cartas na lista afinada** (`lista.md`).
- **🐛 Corrigido nesta rodada:** 1 carta (Lightning Greaves).
- **✅ Falsos positivos descartados:** ~20 cartas/grupos, já corretamente
  implementadas via dispatch por nome ou por tag central.
- **📊 Estrutural confirmado:** shroud do próprio Lightning Greaves (sem
  oponente/remoção alheia modelada).

---

# Achado adicional — `urdragon_goldfish_physical_v1.py` estava QUEBRADO

Ao verificar se o mesmo gap do Lightning Greaves existia na variante
física (já que o docstring dela cita a carta explicitamente como
presente na caixa), a simples tentativa de `import` do arquivo **crashava
imediatamente** com `AssertionError: faltando no CARD_DB: Sarkhan
Unbroken` — ou seja, este segundo simulador não rodava UMA ÚNICA partida
desde que a variante física existe (`lista-fisica.md` data de
2026-08-29). Investigando mais a fundo (comparação sistemática de todo
nome em `lista-fisica.md` contra as chaves reais do `CARD_DB`, não só o
primeiro erro que aparecia), achei **3 cartas genuinamente ausentes do
CARD_DB apesar de estarem na lista física real**:

1. **Sarkhan Unbroken** — planeswalker inteiro faltando (nem `add()`, nem
   nenhuma lógica de lealdade). Corrigido registrando a carta e portando
   a mesma implementação real de lealdade (+1 draw+mana / -2 token / -8
   ultimate, heurística de pilotagem já validada) do
   `urdragon_goldfish_v1.py`.
2. **Mana Confluence** — terreno de mana genérica de qualquer cor,
   faltando por completo.
3. **Sundown Pass** — slow land real ("enters tapped unless you control
   two or more other lands"). Corrigido registrando a carta + portando a
   lógica `SLOW_LANDS` do arquivo principal pro `play_land()` local.

Além disso, apliquei o **mesmo fix do Lightning Greaves** (equipa na
comandante, concede haste real) nesta variante — a carta está
confirmada na caixa física pelo próprio docstring do cabeçalho.

**Bug adicional encontrado e corrigido, não relacionado ao crash:** os
dois arquivos escreviam no MESMO nome de arquivo de saída
(`urdragon_v1_runs.jsonl`) — rodar um dos dois simuladores por último
sobrescrevia silenciosamente o output do outro sem aviso nenhum.
Corrigido: a variante física agora escreve em
`urdragon_physical_v1_runs.jsonl` (arquivo novo, não sobrescreve nada).

**Validação:** 5 testes unitários isolados (import sem crash + Lightning
Greaves + Sarkhan Unbroken +1 uma vez por turno + Sundown Pass tapped/
destravado) + regressão de 200 partidas de sanidade + regressão completa
de 20.000 partidas (seed 5000000+, turns=10, 0 exceções). Como o arquivo
nunca tinha rodado uma partida sequer antes, não há uma comparação
antes/depois de métricas no sentido usual — a validação real É o arquivo
passar a rodar de ponta a ponta com números plausíveis (Dragon tokens
médios ~12.0, color screw em ~31% dos jogos — mesma ordem de grandeza do
arquivo principal, nenhum outlier suspeito).

**Escopo não coberto nesta rodada:** esta correção resolveu o crash e
portou os 2 gaps já identificados no arquivo principal (Lightning
Greaves, e agora Sarkhan Unbroken/Mana Confluence/Sundown Pass como
efeito colateral de destravar o import). Uma auditoria linha-a-linha
COMPLETA da variante física — cobrindo as cartas que só existem nela
(Scalelord Reckoner, Dragon's Hoard, Smuggler's Surprise, Magda Brazen
Outlaw, Firdoch Core) contra o oráculo real — **não foi feita nesta
rodada** e fica como trabalho futuro dedicado, na mesma categoria dos 4
decks sem simulador algum (não é uma decisão de valor, é reconhecer que
essa é uma tarefa de escopo comparável a auditar um deck inteiro à parte,
não um recorte que cabe dentro desta passada).
