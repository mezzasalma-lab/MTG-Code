# Checklist cláusula-a-cláusula — Esika // The Prismatic Bridge

## Rodada Reality Fracture: Tam, Loyal Tutor, Entrust the Spark — 2026-09-25

**Gatilho:** o usuário confirmou as 3 candidatas de FRA que eu tinha
apontado pro deck ("Tam, the Possibility, Loyal Tutor e Entrust the Spark
foram as que pensei mesmo"). Regra 10 aplicada: oráculo ao vivo, curva,
motores do deck e simulador rodado com vários cortes e um controle.

**Fontes:**
- oráculo ao vivo pelo Scryfall (`/cards/named?exact=`, 2026-09-25), salvo no
  `oracle-cache.json`. As 3 cartas ainda não têm rulings publicadas.
- CR atualizadas para a versão efetiva de 2026-09-25 (`rules-cache/`).
- rulings da The Chain Veil, da Oath of Teferi e da Urza Assembles the Titans.

### As 3 candidatas: cláusula a cláusula (entram só via `swap`, a lista não muda)

| Carta | Cláusula (oráculo ao vivo) | Implementação |
|---|---|---|
| Tam, the Possibility ({1}{G}{U}, Legendary Creature — Gorgon Wizard 2/4) | "Planeswalker spells you cast cost {1} less to cast." | `spell_cost`: abate só genérico (tabela `GENERIC_MANA`). Aminatou ({W}{U}{B}) e Nicol Bolas ({U}{B}{B}{B}{R}) não caem; cada cópia reduz de novo. |
| | "{W}{U}{B}{R}{G}, {T}: Proliferate X times, where X is the number of planeswalker types among planeswalkers you control." | `try_tam_proliferate`. X = tipos distintos (`PW_TYPES`, CR 205.3j): 4 Teferis contam 1, The Eternal Wanderer não tem tipo. Tem {T}, então sofre doença de invocação (CR 302.6). Duas janelas: (a) main, antes da passada de lealdade, só se deixa um ultimate pagável no turno; (b) end step do último oponente, com a mana que sobrou do meu turno. Cada proliferate passa pelo mesmo `proliferate_loyalty` (Doubling Season/Vorinclex/Innkeeper, All Will Be One, veneno, +1/+1, lore da Urza). |
| | (Regra #4: The Peregrine Dynamo) "Copy target activated ... ability ... from another legendary source that's not a commander" | A Tam é lendária e não é comandante. A Dynamo copia a ativação na janela de fim de rodada ({1}): X proliferates de novo sem os 5 de mana. No main a Dynamo fica guardada pro ultimate. |
| | 2/4 no combate | Não ataca (perderia o {T}); bloqueia normalmente (`CREATURE_STATS`). A Bridge pode acertá-la (é criatura). |
| Loyal Tutor ({W}, Instant) | "Search your library for a planeswalker card, reveal it, then shuffle and put that card on top." | `try_loyal_tutor`. Com a Bridge em campo, o PW escolhido vai pro topo e o gatilho de upkeep dela o põe em campo de graça. Mesmo ranking da Arena Rector: maior MV, depois maior lealdade; nunca um nome que já controlo. Janelas: end step do último oponente (mana que sobrou) ou em resposta ao gatilho da Bridge no upkeep (CR 113.7a: remover a Bridge depois do gatilho na pilha não o anula). Sem a Bridge, vira "compre o PW certo", só a partir do T8 (`LOYAL_TUTOR_DRAW_MIN_TURN`, política medida: ver goldfish-log). Dispara Inexorable Tide/Flux Channeler/Ichormoon (`on_spell_cast`). |
| Entrust the Spark ({3}{G}{U}, Sorcery) | "You may sacrifice a planeswalker. If you do, search your library for a planeswalker card, put it onto the battlefield, then shuffle." | `_entrust_choice` + `resolve_entrust_the_spark`. Sem PW em campo fica na mão (não faz nada). Sacrifica o PW de menor lealdade, que quase sempre já ativou no turno, e busca o melhor PW direto pro campo. O buscado ativa no mesmo main phase (CR 606.3). O sacrifício é morte: o gatilho do Carth the Lion resolve DEPOIS da busca (`defer_triggers`). |

### 🐛 Bugs de motor achados nesta rodada (afetam a lista atual, não só as candidatas)

1. **PW que entra no main phase só ativava no turno seguinte (Regra #6, orquestração).**
   - A única passada de lealdade (`activate_planeswalkers`) rodava ANTES do loop de conjuração.
   - Afetava todo PW conjurado da mão, capítulo II da Urza no meio do main, ficha da Tamiyo CS −X que entra durante a passada.
   - CR 606.3: "A player may activate a loyalty ability of a permanent they control any time they have priority and the stack is empty during a main phase of their turn, but only if no player has previously activated a loyalty ability of that permanent that turn". Não há doença de invocação pra lealdade.
   - Ruling da Chain Veil: vale também "planeswalkers that come under your control later in the turn".
   - Novo `activate_unactivated_planeswalkers`, chamado depois de cada conjuração e no fim do main.
   - Na rodada anterior, o fix 8 ("PW conjurado ganha lealdade") deu a lealdade, mas não a ativação.
2. **Desconto de custo usava `mv - len(colors)` como genérico.**
   - O Tamiyo's Notebook deixava Nicol Bolas ({U}{B}{B}{B}{R}) em 3 e Counterspell/Damn/Mana Drain em 1.
   - Nova tabela `GENERIC_MANA`, tirada do `mana_cost` real do cache (CR 601.2f: redução só abate genérico).
3. **Proliferate e Deepglow Skate não punham lore na Urza Assembles the Titans (Regra #3).**
   - CR 701.34a ("any number of permanents ... that have a counter") e 714.2b (capítulo dispara ao cruzar N).
   - É escolha do jogador: `try_urza_extra_lore` só inclui a saga se o capítulo vale agora.
     - II: com PW de MV≤6 na mão.
     - III: só antes da passada de lealdade do meu turno; senão o "this turn" se perde e a saga é sacrificada.

### 📝 Aproximações documentadas (não são 📊 de oponente)

- Cópias da Tam (ficha do Oko −5) seguem a doença de invocação da carta original. O motor rastreia criatura nomeada por nome.
- O custo {W}{U}{B}{R}{G} usa o modelo de cor agregado do arquivo: 1 fonte por cor, sem casamento fonte↔símbolo. É a mesma convenção de toda conjuração deste simulador.

## Rodada dedicada: auditoria completa das 100 cartas + todos os gaps — 2026-09-24

**Gatilho:** "Sim, faz a rodada dedicada fechando os gaps restantes" (depois da
rodada do modelo de combate, que listou 14 gaps). Método da Regra #1 inteiro:
oráculo AO VIVO das 100 cartas (Scryfall `/cards/collection`, 0 não
encontradas), rulings de toda carta com interação duvidosa, leitura do `.py`
inteiro, comparação cláusula por cláusula, e checagem de ordem de fases
(Regra #6). O saldo foi bem maior que os 14 gaps da lista: a auditoria achou
**bugs de motor** que afetavam o deck inteiro.

### 🐛 Bugs de motor (os maiores, afetavam todas as partidas)

1. **Terreno na mão era "conjurado" como mágica de custo 0.** O loop de
   conjuração não excluía terrenos: todo terreno da mão ia pro campo todo
   turno, além do land drop. Medido no commit anterior: até o T4, 2,65 land
   drops mas 5,0 terrenos em campo. Inflava toda a mana do deck e
   adiantava a Bridge em ~1 turno (T4,2 → T5,2 real).
2. **Planeswalker conjurado da mão entrava sem lealdade** (só os postos pela
   Bridge/Urza/Ugin/Tamiyo tinham). 57% dos PWs em campo no fim da partida
   nunca tinham ativado nada.
3. **Doubling Season dobrava o custo [+N] de lealdade.** Ruling oficial: "if
   you activate an ability whose cost has you put loyalty counters on a
   planeswalker, the number you put on isn't doubled ... cost, not effect".
   Vorinclex e Innkeeper nível 3 ("If YOU would put") dobram — ruling do
   Carth confirma. Novo `cost_counter_multiplier` (vale pra custo e pra
   marcador em jogador/veneno).
4. **Carth the Lion cobrava {1} de MANA por ativação.** O oráculo é
   "cost an additional **[+1]**" — é +1 de LEALDADE (rulings: [+1]→[+2],
   [0]→[+1], [−6]→[−5]; 2 Carths = [+2]). Era um bônus tratado como imposto.
5. **Delighted Halfling nunca gerava mana colorida** (o filtro "cor ∈
   produces={C}" vinha antes do filtro "só pra lendária").
6. **Bloom Tender contava "cores" de terreno** (o `CARD_DB` guarda
   identidade de cor nos terrenos; terreno é incolor). Novo `permanent_colors`.
7. **Mulligan embaralhava as cartas postas no fundo** (CR 103.5: vão pro
   fundo, sem embaralhar).
8. **Gatilhos de "sempre que conjurar" não disparavam na conjuração da
   própria Bridge** (nem da Sterling Grove, nem das remoções do modelo de
   combate). Novo ponto único `on_spell_cast`.
9. **Ordem de turno extra (Regra #6):** no modo resiliência os 3 oponentes
   jogavam ANTES do turno extra e de novo depois dele. "Take an extra turn
   after this one" vem logo depois do nosso turno.
10. **Regra de lenda** não existia pra segundos exemplares (fichas-cópia).

### Cláusula por cláusula — o que mudou nesta rodada

| Carta | Cláusula (oráculo ao vivo) | Antes → agora |
|---|---|---|
| Aminatou | +1 compra e devolve 1 ao topo; −1 blink; −6 troca permanentes | +1 era vazio → implementado (com a Bridge em campo, põe PW caro no TOPO pra Bridge colocar de graça — Regra #4); −1 implementado (blink de Deepglow/PW/Carth/Oath de Nissa); −6 📊 (permanentes não-criatura de oponente não modelados; entregaria todos os nossos PWs) |
| Kaya | 0: compre 2 | nunca escolhido → política usa quando ela está segura e a mão curta |
| Narset | −2: olha 4, pega não-criatura não-terreno | comprava o topo → seleção real |
| Nicol Bolas | "has all loyalty abilities of all other planeswalkers" | deferido → empresta ultimates/+ dos outros (ruling: 1 ativação por turno, custo sai do Bolas); −8 1x (📊 quem perde depende de lendária do oponente) |
| Oko | +1 compra 2, descarta 1 (crime) ou 2; −5 ficha-cópia de cada outro não-terreno | +1 vazio, −5 inexistente → implementados; crime rastreado (toda ação nossa que mira oponente); fichas-cópia com o nome da carta, regra de lenda, Doubling Season ×2 |
| Tamiyo, Compleated Sage | −7 Tamiyo's Notebook (custo −{2}, {T}: compre) | só contava → implementado; cópia de encantamento do cemitério agora dispara ETB (bug achado pelo teste) |
| Tamiyo, Field Researcher | −7 emblema: conjurar da mão sem pagar | só as 3 compras → emblema implementado |
| Teferi, Hero | +1 desvira 2 terrenos no end step | nunca → mana pra flash/resposta; −8 emblema acumula (2 = 2 exílios por compra) |
| Teferi, Temporal Archmage | +1 olha 2 pega 1; −1 desvira 4; −10 lealdade no turno dos oponentes | +1 comprava o topo; −1 e emblema inexistentes → implementados (emblema: 1 ativação por PW em cada turno de oponente; não re-ulta, a permissão não acumula) |
| Teferi, Time Raveler | estático: oponente só conjura em velocidade de feitiço | → oponente não contramagica a Bridge (resiliência); +1 📝 (sem janela de instantâneo no nosso lado) |
| Teferi, Who Slows the Sunset | +1 desvira terreno/artefato/criatura; −2 olha 3; −7 emblema desvira tudo no untap do oponente | só vida / compra do topo → mana extra, seleção real, mana de pé no turno dos oponentes; compra do emblema conta só oponente vivo e acumula por emblema |
| Elspeth | −7 emblema | acumula (+2/+2 por emblema) |
| Vraska | 0 "lose 1 life"; −9 veneno | vida nunca saía; −9 nunca usado → veneno real, proliferate em jogador envenenado, Vorinclex dobra, eliminação com 10 |
| Ugin | −10 põe terrenos em campo | landfall (Evolution Sage) agora dispara |
| Ichormoon Gauntlet | PWs ganham [0] proliferate e [−12] turno extra; +1 marcador ao conjurar não-criatura | 100% ausente → implementado |
| The Peregrine Dynamo | copia habilidade ativada/disparada de fonte lendária | 📝 "exceção arquitetural" → implementado (copia a melhor ativação de PW, a Chain Veil, ou o proliferate de end step da Atraxa; cópia não paga custo — ruling) |
| Oath of Nissa | ETB olha 3; PW com mana de qualquer cor | 100% ausente → implementado |
| Oath of Teferi | ETB exila outro permanente, volta no end step | ausente → implementado (volta antes do proliferate da Atraxa) |
| Paradox Haze | cópias | 2 Hazes = 2 upkeeps extras (ruling) |
| Nesting Grounds | {1},{T}: mover marcador | ausente → move 1 lealdade pra um PW alcançar o ultimate no turno (CR 122.5: mover = pôr → Doubling Season dobra, All Will Be One dispara) |
| Sterling Grove | {1}, sacrifique: tutor de encantamento pro topo | ausente → só sem a Bridge em campo (com ela, o upkeep revela o topo e manda o encantamento pro fundo — anti-sinergia real) e em resposta a remoção mirando a Grove |
| Plaza of Heroes | cor p/ lendária; cor de lendária em campo; {3},{T}, exile: protege criatura lendária | só {C} → as 3 implementadas (a Bridge é lendária de 5 cores) |
| Interplanar Beacon | +1 vida ao conjurar PW; mana de 2 cores só p/ PW | ausentes → implementadas |
| Shocklands (10) | paga 2 vida ou entra virada | de graça → política: paga só se a mana muda o turno |
| City of Brass / Mana Confluence | 1 de dano/vida por uso | ausente → aproximação (viradas por último) |
| The World Tree | entra virada | ausente → implementado |
| Blasphemous Act | −{1} por criatura em campo | ausente no loop genérico → `spell_cost` |
| Innkeeper's Talent | nível 1 fora do modelo de combate; nível 2 ward {1} | nível 1 só no combate → todo modo; ward implementado (suposição: oponente paga a partir do T4) |
| Counterspell / Mana Drain / Swan Song / Dovin's Veto | contramágica | 📊 → no modo resiliência ficam na mão e contramagicam remoção/wipe/contramágica do oponente (Swan Song dá o Bird 2/2 voador; Mana Drain dá a mana no próximo main) |
| Mutational Advantage / Ripples of Potential | hexproof/indestrutível/previne dano; phasing | só o proliferate → respostas protetoras (remoção e combate letal a PW) |
| Veil of Summer | "spells you control can't be countered" | 📊 → protege a conjuração da Bridge |
| Delighted Halfling | "that spell can't be countered" | → Bridge paga com ela não é contramagicada |
| Kaya | hexproof | → oponente não a escolhe como alvo |
| Urza | cópia pela Tamiyo CS | começa saga nova |

### 📊 / 📝 que continuam (com a cláusula citada)

- **Exotic Orchard** — "any color that a land an opponent controls could
  produce": terrenos do oponente não modelados; assume as 5 cores numa mesa de 3.
- **Esika, God of the Tree** (frente do MDFC) — conjurar a Esika significa não
  ter a Bridge; o plano do deck é sempre a Bridge (política, não omissão).
- **Aminatou −6**, **Bolas +1 (oponente exila)**, **Narset/Ashiok estáticos**,
  **Vorinclex (oponente põe metade)**, **Kaya 0 (oponentes fazem scry)**,
  **Rhystic Study**, **Veil (compra se oponente conjurou azul/preta)**,
  **Swords/Path (efeito no oponente)** — dependem de estado de oponente não
  modelado.
- **The World Tree** (busca de Gods) — não há God no grimório (Esika está na
  zona de comando).
- 📝 Teferi, Time Raveler +1 (feitiço com flash): o simulador não tem janela
  de instantâneo do nosso lado além das respostas.
- 📝 Segunda Urza simultânea (cópia do Oko −5) e cópia de Innkeeper (nível 1)
  não têm estado próprio; cópia de Bloom Tender usa a doença da original.
- 📝 Teto do simulador de 400 permanentes: Oko −5 com Doubling Season copia a
  própria Doubling Season e o tabuleiro cresce ×4, ×8... (real). Acima disso a
  partida já está decidida; bate em ~4% das partidas.

### Validação

- Reestruturação dos PWs em tabela de habilidades: **md5 idêntico** ao antes
  (padrão e resiliência) antes de qualquer correção.
- Cada correção medida isoladamente (2.000 partidas, mesmas seeds) — tabela no
  `goldfish-log.md`.
- `test_prismatic_bridge_goldfish.py`: **85/85** (33 testes novos, um por
  correção; o da ordem de turno extra roda o loop inteiro — Regra #6).
- Regressão: 20.000 partidas modo padrão + 20.000 mesa mista + 5.000 em cada
  perfil (go-wide/voltron/low/sem combate) + 5.000 com cada carta de
  pillowfort: **0 exceções**. Travamento achado e resolvido no caminho:
  crescimento explosivo real (Oko −5 copiando Doubling Season) → teto de 400
  permanentes no simulador.

## Modelo de combate (oponente ataca planeswalkers) + 9 correções pré-existentes — 2026-09-24

**Gatilho:** pergunta do usuário — *"Conseguimos implementar no goldfish um
simulador de ataque aos PW? [...] Vale incluir Silent Arbiter e Dueling [Grounds]?"*
— aprovado com 3 perfis de mesa + perfil **misto** ("um pouco de cada,
simulando diferentes decks de forma aleatória", que é a mesa real dele).

**Nota sobre "não fabricar tabuleiro do oponente" (CLAUDE.md):** o modelo
cria criaturas de oponente abstratas (P/R/voar/atropelar) como MODELO DE
AMEAÇA, mesma categoria do modo de resiliência já aprovado (remoção/wipe
de oponente simulados) — foi exatamente o que o usuário pediu. Só existe
no modo de resiliência (`simulate_one_with_interaction(attack_profile=...)`);
o modo padrão continua sem oponente nenhum (confirmado bit-a-bit abaixo).

### O modelo (suposições documentadas, não dados reais)

- Arquétipos por oponente: `go_wide` (1–3 criaturas 1/1–2/2 por turno a
  partir do T2, até 15; 15% voam, 10% ímpeto), `voltron` (comandante 3/3
  com atropelar a partir do T3, +1..3/+1..3 por turno até 20; volta 1 turno
  depois de removido com metade do bônus; 35% voa; até 2 apoios 2/2) e
  `low` (30%/turno de uma 3/3 ou 4/4 a partir do T3, até 3). `mixed` sorteia
  o arquétipo de cada oponente por partida.
- O campo cresce todo turno do oponente; ele só ataca a mim/meus PWs no
  turno em que passa no gate de atenção já existente (1/3).
- Alvo: atacantes, do maior pro menor, vão pro PW de maior lealdade até
  somar o suficiente pra matá-lo; depois o próximo; o resto na minha vida.
- Imposto (Sphere/Ghostly Prison): o oponente usa até metade da mana dele
  (turno, máx. 10). Ghostly Prison: atacante de vida não pago é
  redirecionado pro PW (ruling oficial: "a creature that can't attack you
  can still attack a planeswalker you control").
- Bloqueio: prefere matar-e-sobreviver, depois parede, depois chump com
  ficha/dork se o PW morreria ou o atacante tem poder ≥2, troca com
  "motor" só se o PW morreria. Voar/atropelar/toque mortífero/golpe
  duplo/vínculo com a vida modelados. Criatura que atacou no meu turno
  fica virada até o meu untap (não bloqueia).
- Nossas remoções/wipes agora têm efeito real nos 2 lados e ficam na mão
  até existir ameaça (instantâneas usadas na velocidade de feitiço, no meu
  turno — simplificação).
- O motor não encerra a partida com vida ≤ 0 — a métrica `died_turn` marca.

### Cláusula-a-cláusula (cartas que o modelo toca)

| Carta | Cláusula (oráculo Scryfall ao vivo) | Status |
|---|---|---|
| Silent Arbiter / Dueling Grounds | "No more than one creature can attack/block each combat." | ✅ (só no A/B, fora da lista) |
| Sphere of Safety | imposto {X} por atacante em você OU nos seus PWs, X = seus encantamentos | ✅ (A/B) |
| Ghostly Prison | imposto {2} só pra atacar VOCÊ (PW não é protegido — ruling) | ✅ (A/B) |
| The Eternal Wanderer | "No more than one creature can attack The Eternal Wanderer each combat." | 🐛→✅ novo |
| The Eternal Wanderer | +1 exila criatura até o end step do dono; −4 cada jogador fica com 1 | ✅ com alvo real |
| Nicol Bolas, Dragon-God | −3 destrói criatura | ✅ ; −8 📊 (depende de o oponente controlar lendária — só o comandante voltron é rastreado; segue como contagem) |
| Kaya, Intangible Slayer | −3 exila + ficha 1/1 voadora (cópia) pra nós ; +2 "you gain 3 life" | ✅ ; vida do +2 🐛 agora real |
| Vraska, Betrayal's Sting | −2 criatura vira Treasure | ✅ (comandante: 2 turnos até voltar) |
| Teferi, Hero of Dominaria | −3 3ª do topo ; −8 emblema "sempre que comprar, exile permanente de oponente" | ✅ (emblema: só no modelo de combate) |
| Teferi, Time Raveler | −3 devolve criatura | ✅ (ficha some; comandante recasta com doença) |
| Tamiyo, Compleated Sage | +1 vira e congela 1 | ✅ |
| Tamiyo, Field Researcher | +1 compra quando as 2 marcadas causam dano de combate (até meu próximo turno) ; −2 congela 2 | ✅ (+1: ataque proxy + bloqueio) |
| Elspeth, Sun's Champion | −3 destrói poder ≥4 (dos 2 lados) ; −7 emblema +2/+2 e voar | ✅ |
| Liliana, Dreadhorde General | estático "criatura sua morre → compre" ; −4 cada um sacrifica 2 ; −9 cada oponente fica com 1 de cada tipo | ✅ |
| Ugin, the Spirit Dragon | +2 3 de dano ; −X exila coloridos MV ≤ X (dos 2 lados) ; −10 ganha 7 de vida | ✅ ; vida do −10 🐛 agora real |
| Oko, the Ringleader | início de combate: vira cópia de criatura sua (não lendária, sem marcadores — CR 707.2) | ✅ novo |
| Innkeeper's Talent | nível 1: +1/+1 no início de combate (dobra com dobradores) | ✅ novo |
| Arena Rector | "When this creature dies... search for a planeswalker, put it onto the battlefield" | ✅ (antes 📊: nada matava criatura nossa — agora combate/wipes/remoção matam) |
| Atraxa, Praetors' Voice | voar/vigilância/toque mortífero/vínculo ✅ ; "At the beginning of your end step, proliferate" | 🐛 nunca existia → ✅ |
| Deepglow Skate / Carth the Lion | ETB | 🐛 só disparava conjurando da mão → ✅ em todo ponto de entrada (`creature_enters`) |
| Remoções/wipes (Swords, Path, Damn, Anguished Unmaking, Void Rend, Toxic Deluge, Supreme Verdict, Blasphemous Act, Farewell) | efeito real, custo real ({B}{B}/overload {2}{W}{W}, "pay X life", "−{1} por criatura", 13 de dano, "lose 3 life") | ✅ no modelo de combate |
| The Peregrine Dynamo | "Legendary **Artifact** Creature" | 🐛 wipe de artefato nunca a alcançava (Regra #3) → ✅ |

### 🐛 Bugs pré-existentes achados e corrigidos (valem no modo padrão também)

1. **Sphinx of the Second Sun implementado com um texto que a carta não
   tem.** O código dava "if you cast it, take an extra turn" + sacrifício
   no upkeep (auditoria de 09-13/14 escrita de memória — exatamente o que a
   Regra #1 proíbe). Oráculo real: "At the beginning of each of your
   postcombat main phases, there is an additional beginning phase after
   this phase." Rulings oficiais conferidas: untap real, gatilhos de upkeep
   disparam (a Bridge de novo!), compra no draw step, efeitos "until your
   next turn" não expiram, depois vai pro end phase (sem main phase).
   Paradox Haze não dobra esse upkeep ("first upkeep each turn"). Novo:
   `sphinx_additional_beginning_phase`, chamado no main pós-combate de
   `play_turn` (Regra #6: ordem real das fases conferida).
2. **Criatura entrando fora do "conjurar da mão"** (Bridge, ult do Ugin,
   cópia da Tamiyo CS): sem doença de invocação (dork gerava mana no
   mesmo turno) e sem ETB de Deepglow Skate/Carth the Lion. Novo ponto
   único `creature_enters`.
3. **Atraxa**: proliferate de end step nunca implementado.
4. **Doubling Season**: só a metade de marcador existia; "creates twice
   that many tokens" nunca. E cópias (Tamiyo CS copiando Doubling
   Season/Vorinclex do cemitério) não empilhavam.
5. **Damn**: cor registrada como {B,W}; a cor da carta é só preta ({B}{B};
   o {W} é do overload/identidade de cor).
6. **Oath of Teferi + capítulo III da Urza somavam** (+2 ativações). Os 2
   dizem "twice rather than only once" — não empilham (ruling oficial da
   Oath). Só a Chain Veil soma.
7. **Urza Assembles the Titans**: marcador de lore não era dobrado por
   Doubling Season/Vorinclex/Innkeeper nível 3; agora dobra, com Read ahead
   real (CR 702.155a: no turno em que entra só dispara o capítulo com
   número EXATO de marcadores).
8. **All Will Be One**: carta na lista com ZERO código. Agora dispara em
   todo ponto em que colocamos marcadores (lealdade, PW entrando — ruling
   oficial 2023-02-04 —, +1/+1, lore). Modelo de combate: mata a maior
   criatura de oponente que o dano mata; senão, dano no oponente (proxy).
9. **Vida real**: ganhos de vida dos PWs (Kaya +2, Teferi Sunset +1, Ugin
   −10) só alimentavam contador; e o gatilho de end step da The Chain Veil
   ("if you didn't activate a loyalty ability... lose 2 life") não existia.

### Gaps restantes confirmados (NÃO feitos nesta rodada — ficam pra uma rodada dedicada)

Listados aqui pra não sumirem (Regra #1 — nenhum é julgamento de valor,
é escopo desta rodada): Oath of Nissa (ETB + mana de qualquer cor pra PW),
Oath of Teferi (ETB blink), Ichormoon Gauntlet (2 cláusulas), Nicol Bolas
(estático), Oko −5 e +1, Vraska −9, Aminatou −1/−6, Teferi Temporal
Archmage −1, Teferi Hero +1 (untap 2 terrenos no end step), Tamiyo CS −7
(Notebook), Nesting Grounds (mover marcador), Sterling Grove (tutor),
Innkeeper's Talent nível 2 (ward {1}), Kaya 0 (política nunca escolhe).

### Validação

- Modelo de combate sozinho: modo padrão **bit-idêntico** (md5 de 300
  seeds × 10 turnos = `78111885dbba34ca35dc78d829e8053c`, igual ao antes).
- As 9 correções: antes/depois medidos uma a uma (2.000 partidas, mesmas
  seeds, padrão + resiliência) — tabela em `goldfish-log.md`.
- `test_prismatic_bridge_goldfish.py`: **52/52** testes dirigidos (cada
  cláusula acima dispara de verdade; Sphinx/Atraxa/Chain Veil testados
  rodando `play_turn` inteiro — Regra #6).
- Regressão: 20.000 partidas modo padrão + 20.000 mesa mista + 5.000 em
  cada perfil (go_wide/voltron/low/sem combate) + 5.000 com cada carta de
  pillowfort: **0 exceções**.

## CR 903.9a: comandante passa pelo cemitério de verdade antes da zona de comando — 2026-09-21

**Gatilho:** mesmo achado do usuário aplicado a todos os 9 decks desta
sessão, depois de eu documentar em TODOS eles que "o comandante nunca
dispara gatilho de morte": *"O comandante não morre e ao invés de ir
pro cemitério, pode ser movido de volta a zona de comando? Pq até onde
sei, comandantes podem ser mortos sim! Confere essa regra com muita
calma e atenção!"* Raciocínio completo da regra em
`megatron-tyrant-mardu/checklist-oraculo.md` (CR 903.9a é ação baseada
em estado — CR 704 — não substituição; texto oficial cacheado em
`rules-cache/comprehensive-rules.txt`, Regra 18 de
`references/user-standing-rules.md`).

**Achado específico deste deck: 2 call sites reais, não só 1.** Este
deck tem DOIS sistemas de remoção de comandante — `remove_permanent`
(novo chokepoint do modo de resiliência, porte dos outros 6 decks) E
`resolve_removal_round` (sistema ANTIGO, específico deste deck, mira
só Bridge/protetores, sempre ativo desde o turno 1 e rodando em modo
PADRÃO também, não só resiliência — `simulate_one` chama `play_turn`
sem `skip_legacy_removal`). Os dois desviavam o comandante direto pra
zona de comando sem passar pelo cemitério. Corrigidos os 2.

**Comandante é Enchantment, não Creature** (The Prismatic Bridge,
confirmado Scryfall) — checado se isso muda o critério: este deck tem
**0 cartas "creature dies"/"planeswalker dies" que reagiriam a um
ENCANTAMENTO morrendo** (Carth the Lion, o único gatilho de morte real
do deck, reage só a "a creature or a planeswalker you control dies" —
Bridge nunca é nenhum dos 2). Correção puramente estrutural, sem
impacto numérico, nos 2 call sites.

**Validação:** compilação OK. Bit-identidade em modo padrão
(replicando o path completo de `simulate_one`, 3000 seeds cada, COM e
SEM Greater Auramancy — já que `resolve_removal_round` roda em ambas
as variantes) contra o commit anterior: **0/3000 mismatches em cada
variante**. Regressão de 20.000 partidas em modo padrão (exercitando o
sistema legado) + 20.000 em modo de resiliência: 0 exceções nos 2, 0
comandantes presos no cemitério. 3 testes dirigidos: (1)
`remove_permanent` no comandante — não fica presa no cemitério; (2)
`resolve_removal_round` (sistema legado) no comandante — mesma
checagem; (3) permanente comum continua indo pro cemitério
normalmente.

## `try_smart_opponent_removal` nunca respeitava shroud de Sterling Grove/Greater Auramancy — 2026-09-21

**Gatilho:** usuário perguntou diretamente, revisando os números de A/B
da rodada anterior: *"Vc levou em conta que existe menos remoção de
encantamento do que de criatura, na Prismatic Bridge? E que a Greater
Auramancy e outro encantamento protegem todos os encantamentos no
deck..."*

**Oráculo real confirmado via Scryfall** — Greater Auramancy ({1}{W},
Shadowmoor 2008) e Sterling Grove ({G}{W}, Modern Horizons 2 2021): as
duas têm a MESMA cláusula, *"Other enchantments you control have
shroud"* (shroud de verdade, não hexproof — protege só contra efeitos
que usam a palavra "target"). Checado contra as 4 wipes reais desta
própria lista (Toxic Deluge/Blasphemous Act/Supreme Verdict/Farewell) —
nenhuma usa "target" ("all creatures", "destroy all creatures", "exile
all X"), então shroud nunca bloqueia um wipe de verdade — o número de
enchantment wipe do A/B anterior (0,48/jogo) está correto, shroud
genuinamente não se aplica a essa categoria.

**Mas achei um bug real na categoria de remoção ALVO** (`try_smart_
opponent_removal`, diferente da categoria de wipe): shroud DEVERIA
bloquear essa categoria (remoção pontual sempre usa "target" de
verdade), mas a função nunca checava `protectors_in_play()`. 2 dos 8
itens de `NONPLANESWALKER_ENGINE_PRIORITY` são encantamentos reais
(Doubling Season, Innkeeper's Talent) — ficavam vulneráveis a remoção
direta mesmo com Sterling Grove em campo, quando deveriam estar
protegidos até o protetor sair primeiro.

**Achado de arquitetura**: o sistema LEGADO (`resolve_removal_round`,
desligado desde que o modo de resiliência substituiu ele) já modelava
isso certo — redirecionava a remoção pro protetor primeiro via
`protectors_in_play()`. Essa checagem nunca foi portada pra
`try_smart_opponent_removal` quando o modo de resiliência assumiu a
categoria — mesmo padrão da Regra #3 do CLAUDE.md (conceito
compartilhado certo numa função, nunca propagado pra função nova que
substituiu ela).

**Corrigido:** se o alvo determinado (lealdade de planeswalker ou
fallback `NONPLANESWALKER_ENGINE_PRIORITY`) for um Encantamento de
verdade (`C(target).type == "Enchantment"`) E houver protetor em campo,
redireciona pro protetor (`protectors_in_play()`, mesma função já
existente). Planeswalkers nunca são encantamento nesta lista (sem
híbrido, confirmado) — o ramo de lealdade nunca precisa de
redirecionamento, shroud de Sterling Grove/Greater Auramancy não
alcança planeswalker nenhum.

**Validação:** modo padrão 100% bit-idêntico ao HEAD anterior (2.000
seeds — mudança é 100% dentro do modo de resiliência, nunca tocado em
modo padrão) + regressão de 20.000 partidas em modo resiliência, 0
exceções + 3 testes dirigidos (Doubling Season nunca removido com
Sterling Grove em campo, 0/1000; Doubling Season removível normalmente
sem protetor, 1000/1000; planeswalker nunca redirecionado mesmo com
protetor em campo, 1000/1000).

**Resultado (A/B 2000 jogos mesma seed_base):** efeito real mas
pequeno, como esperado de uma carta única precisando estar em campo no
exato momento do roll — Sterling Grove passa a ser removido em 0,3%
dos jogos (0,0% antes, nunca era alvo desta categoria antes do fix).
Doubling Season/Innkeeper's Talent removidos praticamente na mesma taxa
(2,5%/4,0-4,2%) porque a maioria dos jogos onde eles são removidos não
tinha Sterling Grove em campo simultaneamente — a correção só muda o
comportamento na janela estreita onde as duas condições coincidem, mas
está certa pela regra real independente do tamanho do efeito medido.

## Modo de resiliência ganha wipe de artefato e wipe de encantamento — 2026-09-20

**Gatilho:** "Temos que incluir remoções de artefatos e encantamentos
tb: Vandalblast, Farewell, Austere Command, etc…" — raciocínio completo
(e a correção de design que se seguiu no mesmo dia) em
`megatron-tyrant-mardu/checklist-oraculo.md`.

**Implementado direto no design FINAL** (este deck recebeu a extensão
DEPOIS da correção de design, então nunca passou pela versão com
rolagens independentes): `try_smart_opponent_wipe(state, log)` único —
1 rolagem "algum wipe acontece" seguida de escolha ponderada de 1 TIPO
só (`WIPE_TYPE_WEIGHTS = {"creature": 0.4, "artifact": 0.2,
"enchantment": 0.15}`), restrita aos tipos com alvo legal em campo
(`C(n).type == "Creature"/"Artifact"/"Enchantment"`).

**Achado real específico deste deck — o ÚNICO dos 7 onde o wipe alcança
o comandante:** The Prismatic Bridge É Enchantment de verdade
(confirmado via Scryfall), então um wipe de ENCANTAMENTO escolhido pela
rolagem ponderada a atinge — o único dos 3 tipos que faz isso neste
deck (wipe de criatura e de artefato nunca a alcançam). `remove_
permanent()` já trata isso corretamente (CR 903.9 — vai pra zona de
comando, nunca cemitério de verdade) sem precisar de exceção extra
dentro da função de wipe. The Chain Veil (já em `NONPLANESWALKER_
ENGINE_PRIORITY`, o maior multiplicador de ativação do deck) é um
artefato real, alvo legal de wipe de artefato.

**Teste dirigido específico:** confirmado que quando a rolagem escolhe
"enchantment" e a Bridge está em campo, ela é removida do battlefield,
`bridge_in_play` vira `False`, e ela NUNCA aparece em `state.graveyard`
(1.241/1.241 disparos corretamente roteados pra zona de comando em
3.000 chamadas simuladas).

**Validação:** modo padrão 100% bit-idêntico ao commit `d66e569` (2.000
seeds) + regressão de 20.000 partidas em modo resiliência, 0 exceções +
testes dirigidos (no máximo 1 tipo por chamada; distribuição ponderada
correta; roteamento CR 903.9 da Bridge via wipe de encantamento).

**Resultado (A/B 2000 jogos mesma seed_base):** % de jogos com pelo
menos 1 wipe de qualquer tipo sobe de 38,7% pra 64,5% (antes = commit
`d66e569`, só wipe de criatura). Avg wipes totais por jogo: 0,465 →
0,982. 16,4% dos jogos "depois" sofrem pelo menos 1 artifact wipe,
27,9% pelo menos 1 enchantment wipe (inclui os casos onde a própria
Bridge é a vítima).

## Porte completo do modo de resiliência (interação de oponente) — 2026-09-20

**Gatilho:** usuário pediu direto, mesmo protocolo já aplicado a
Megatron/Ur-Dragon/Hei Bai/Markov/Ulalek/Toph: *"Repita o processo todo
com o deck da Prismatic Bridge."*

**Diferença estrutural real vs. os outros 6 decks, resolvida ANTES de
implementar:** este arquivo já tinha um sistema de remoção de oponente
próprio (`resolve_removal_round`), construído sob medida em rodada
anterior pra responder "vale incluir Greater Auramancy?" — 12%/oponente/
turno, sempre ativo desde o turno 1, sem gates, mira só Bridge/
protetores. Simplesmente empilhar o modo de resiliência padrão por cima
duplicaria a pressão de remoção (o mesmo problema de "3 contra 1" já
corrigido no Megatron). Perguntei ao usuário antes de implementar; opção
escolhida: **o modo de resiliência SUBSTITUI o sistema antigo dentro
dele mesmo, sem tocar no modo padrão.** `play_turn()` ganhou um parâmetro
`skip_legacy_removal: bool = False` (default preserva 100% o
comportamento de todo call site existente); `simulate_one_with_
interaction()` passa `True`, desligando `resolve_removal_round` só
dentro do modo de resiliência. `resolve_removal_round` continua
intocado no modo padrão, respondendo à pergunta original do Greater
Auramancy sem nenhuma mudança.

**2 bugs reais de Carth the Lion encontrados e corrigidos, sem relação
com o modo de resiliência** — achados só por auditar como
`remove_permanent` deveria interagir com `state.loyalty` (Regra #3 do
CLAUDE.md: conceito compartilhado, não carta isolada). Oráculo real
(Scryfall): *"Whenever Carth enters or a planeswalker you control dies,
look at the top seven cards of your library. You may reveal a
planeswalker card from among them and put it into your hand. Put the
rest on the bottom of your library in a random order."*
1. **"Put the rest on the bottom" estava recolocando no TOPO**
   (`state.library = top7 + rest`) — o oposto do oráculo real. Corrigido
   pra `rest + shuffled_top7`. Isso muda a ordem da biblioteca em TODO
   ETB da Carth, não só quando acha um planeswalker — e por consequência
   o restante do jogo inteiro (mesma seed) diverge depois desse ponto,
   já que consome a mesma `state.rng` compartilhada por tudo mais.
2. **A metade "morte de planeswalker" nunca disparava.** O comentário
   original (2026-09-01) dizia "nada remove nossos planeswalkers uma vez
   em campo" — isso já era FALSO em modo padrão: `add_loyalty()` mata um
   planeswalker de verdade quando a lealdade cai a 0 ou menos (ex.:
   ultimate que zera a própria lealdade). Medido: **1.861 mortes de
   planeswalker em 3.000 partidas de modo padrão** — não um evento raro,
   um evento comum que nunca disparava o gatilho de card advantage da
   Carth. Corrigido: extraído `_planeswalker_dies()` de dentro de
   `add_loyalty()` (mesma cascata real de "um planeswalker seu morre",
   reusada tanto pra lealdade chegando a 0 quanto pra remoção/wipe de
   oponente — a regra real não distingue a causa).

**Consequência real de validação:** como os 2 fixes mudam o consumo de
`state.rng` no meio de partidas reais, comparação bit-a-bit contra o
checkpoint anterior diverge amplamente (~19% das seeds em 5.000, a
maioria delas SEM nenhuma métrica relacionada à Carth mudando —
confirmado por teste dirigido que isso vem do reordenamento de
biblioteca no ETB, não de um bug novo). Isso é o comportamento CORRETO
e esperado de uma correção real de RNG-stream compartilhado (mesmo
padrão já visto no fix do Blightsteel Colossus no Megatron) — validação
trocada de bit-idêntico pra comparação agregada A/B, exatamente como
naquele caso.

**Achado real adicional, documentado mas NÃO corrigido nesta rodada**
(📊, mesma classe do token do Ugin no Ulalek): Arena Rector — *"When
this creature dies, you may exile it. If you do, search your library
for a planeswalker card, put it onto the battlefield, then shuffle."*
Diferente do bug real da Carth (já alcançável em modo padrão, 1.861/
3.000 jogos), morte de CRIATURA nomeada nunca foi possível neste arquivo
antes desta rodada — só fica relevante especificamente quando o NOVO
wipe/remoção alcança a própria Arena Rector, não um pré-requisito
estrutural do port (diferente dos 2 fixes da Carth, que já custavam
valor real em modo padrão hoje).

**Implementado (7 categorias, design final direto):** ataque sem
bloqueio, remoção "inteligente" (mira o planeswalker de MAIOR lealdade
em campo — motor dinâmico real deste deck, qualquer um dos 17 pode
estar em campo a qualquer momento — com fallback pra
`NONPLANESWALKER_ENGINE_PRIORITY` curada: Doubling Season, The Chain
Veil, Vorinclex, Innkeeper's Talent, Deepglow Skate, Carth the Lion,
Evolution Sage, Flux Channeler), discard aleatório, board wipe (só
`type == "Creature"` de verdade — a Bridge é Enchantment, nunca
alcançada por um wipe de criatura), graveyard hate (mass exile + exílio
único, alvo = maior MV entre criatura OU planeswalker no cemitério,
mesmo critério real que `Tamiyo, Compleated Sage -X` já usa pra
recursão), e counterspell mirando só o cast da Bridge (normal ou
flash). `remove_permanent()` (novo): comandante vai pra zona de comando
(CR 903.9, mesma convenção que `resolve_removal_round` já usava);
planeswalker delega pra `_planeswalker_dies` (loyalty dict + Carth
sincronizados); token deixa de existir sem cemitério; carta nomeada vai
pro cemitério de verdade.

**Achado real de calibração, DIFERENTE dos outros 6 decks — a Bridge
sobrevive MAIS sob o modo de resiliência novo que sob o sistema antigo:**
o sistema antigo (`resolve_removal_round`) foi construído
especificamente pra ameaçar a Bridge (essa era a pergunta de pesquisa
original do arquivo). O novo sistema padronizado, seguindo a MESMA
convenção já estabelecida nos outros 6 decks, exclui o comandante de
`NONPLANESWALKER_ENGINE_PRIORITY`/board wipe (ela já tem categoria
dedicada de counterspell, e remoção não a mata de verdade mesmo via CR
903.9) — resultado real medido: Bridge removida em média 1,24x sob o
sistema antigo vs. **0,00x** sob o novo (nunca removida diretamente,
só contra-atacada no cast); Bridge em campo no fim da partida 72,0%
(antigo) vs. **90,8%** (novo). Isso é uma consequência ESPERADA e
CORRETA da decisão de design escolhida pelo usuário (substituir, não
empilhar, mantendo a mesma convenção dos outros decks) — mas muda
substancialmente o que os números do modo de resiliência deste deck
respondem, comparado à pergunta original do Greater Auramancy (que
continua sendo respondida pelo modo padrão intocado). Registrado aqui
explicitamente pra não virar uma surpresa silenciosa.

**Validação:**
- Regressão de 20.000 partidas em modo padrão (pós-fix da Carth) E em
  modo resiliência, 0 exceções nos dois.
- Testes dirigidos: comandante removido vai pra zona de comando (nunca
  cemitério) e fica recastável (taxa já existia, confirmada); remoção
  de planeswalker sincroniza `state.loyalty` e dispara Carth
  corretamente; token não vai pro cemitério; carta nomeada vai;
  `skip_legacy_removal=True` desliga o sistema antigo por completo
  dentro do modo de resiliência, `False` (default) mantém o sistema
  antigo rodando normalmente no modo padrão; taxa de ataque pós-wipe
  cai pra ~13,5% da taxa base (~ fator 0,15 esperado); reordenamento de
  biblioteca da Carth confirmado batendo com o oráculo real ("rest" vai
  pro fundo, não pro topo).
- `run_batch_with_interaction` (2000 jogos, 10 turnos): avg ataques
  sofridos 2,04, avg remoções inteligentes 1,80 (miram planeswalkers,
  não a Bridge), avg board wipes 0,77 (56,1% das partidas), avg
  counterspells 0,06, avg vida final 36,82, Bridge recastada após
  remoção em apenas 4,5% das partidas (baixo porque ela quase nunca é
  removida sob o novo sistema, ver achado de calibração acima).

## Auditoria oráculo-por-oráculo completa — 2026-09-13/14

Extensão pra este deck da mesma auditoria já feita no Megatron/Azula/
Beorn/Captain Storm/Edgar Markov/Hei Bai/Maralen/Kutzil/Nekusar/Ms.
Bumbleflower/Rat King. Oráculo real via Scryfall pras 65 cartas + 29
terrenos + comandante (MDFC modal, layout `modal_dfc` confirmado —
Esika, God of the Tree {1}{G}{G} / The Prismatic Bridge {W}{U}{B}{R}{G}),
comparado cláusula-por-cláusula contra o código já existente (que já
tinha passado por 3 rodadas anteriores — 2026-08-21, 08-28, 09-01 — e é
um dos arquivos mais maduros e documentados do repositório).

**Achado principal — 3 fontes reais de "ativar lealdade mais de 1x por
turno" nunca implementadas, num deck com 17 planeswalkers:**

1. **Oath of Teferi** — "You may activate the loyalty abilities of
   planeswalkers you control **twice each turn** rather than only
   once." Estático, sempre ligado enquanto em campo — a carta inteira
   tinha `tags=set()` (nem fantasma, tag nenhuma).
2. **The Chain Veil** — "{4}, {T}: For each planeswalker you control,
   you may activate one of its loyalty abilities **once this turn** as
   though none of its loyalty abilities have been activated this
   turn." Habilidade ativada real, paga — também `tags=set()`.
3. **Urza Assembles the Titans** — Saga (Read ahead) 100% ausente:
   capítulo I (revela o topo, planeswalker vai pra mão — scry 4 não
   modelado, sem infra de scry neste arquivo), capítulo II (planeswalker
   MV≤6 da mão pra campo de graça), capítulo III (dobra ativação de
   lealdade só naquele turno, depois sacrifica).

Com 17 planeswalkers na lista, esses 3 multiplicadores de ativação são
provavelmente o maior bloco de valor real do deck fora da própria Bridge
— nenhum estava implementado. Corrigido com uma função central
`extra_pw_activation_sources()` (as 3 fontes são aditivas, não mutuamente
exclusivas — Oath of Teferi permite 2x, Chain Veil/Urza cap. III cada
um concede "mais uma" em cima disso), consumida por
`activate_planeswalkers()` (que já ativava 1x por planeswalker por
turno, CR 606.3 — agora ativa `1 + extras` vezes, respeitando a taxa do
Carth the Lion em CADA ativação individual, inclusive as extras).

**Achado secundário — 11 cartas de interação nunca contavam pra métrica,
ao contrário de todos os outros decks da sessão:** Counterspell, Mana
Drain, Path to Exile, Swords to Plowshares, Anguished Unmaking, Damn,
Void Rend, Toxic Deluge, Blasphemous Act, Supreme Verdict e Farewell
tinham as tags reais (`removal`/`counterspell`/`wipe`) desde a
construção original, mas essas tags nunca eram lidas em lugar nenhum —
as cartas eram conjuradas pelo loop genérico (corretamente sem efeito
de bordo real, Regra 1: sem oponente/spell real pra mirar, e nenhum
wipe destrói o próprio board sem motivo), mas nem sequer contavam como
"interação conjurada" na métrica agregada, inconsistente com a
convenção das 5 métricas básicas usada em todos os outros decks
auditados nesta sessão. Corrigido com `interaction_spells_cast_total`.

**Validação:** smoke test (105 nomes no `CARD_DB`, 99 cartas na
decklist, 0 desconhecidas) + 2.000 partidas antes/depois (mesma seed
3000000) + 20.000 partidas de regressão (seed 7000000), 0 exceções em
ambas. Testes unitários dirigidos confirmaram cada correção: Oath of
Teferi e The Chain Veil dobram as ativações reais de um planeswalker no
mesmo turno; Urza dispara os 3 capítulos corretamente (tutora
planeswalker no I, coloca em campo de graça no II, marca a flag de
dobra no III e se sacrifica); Swords to Plowshares agora conta pra
`interaction_spells_cast_total` ao ser conjurada. Métricas de 2.000
partidas subiram como esperado: ativações de planeswalker por partida
7.01→8.65, ultimates usados 1.18→1.48, draws via planeswalker
3.87→4.66 — nenhuma mudança de categoria no comportamento típico do
deck, só o motor de superfriends ficando mais completo.

---

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado ao
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron e Nekusar.

**Aviso importante sobre este deck especificamente:** diferente dos
outros, este simulador foi construído **deliberadamente com escopo
restrito** (docstring original: *"Este é um simulador FOCADO, não um
goldfish completo de curva geral... Escopo deliberadamente restrito ao
que a pergunta do usuário pede: turno em que a Bridge resolve, taxa de
acerto da Bridge em criatura/planeswalker, e sobrevivência da
Bridge/protetores sob remoção do oponente"*). Não modela casting geral de
toda a lista com a mesma profundidade dos outros 6 decks — mas modela
com precisão real tudo que compõe o motor central (Bridge + 17
planeswalkers com lealdade rastreada). Nesta rodada, apliquei o mesmo
padrão "compile TUDO" às lacunas que **estavam documentadas como
deferidas**, não ao escopo original do simulador em si.

## 🐛 Achados corrigidos nesta rodada

O docstring antigo tinha 2 notas de "deferido": uma citando "14 cartas
tageadas draw sem gatilho" (na verdade só 2 não-planeswalker, ambas
genuinamente 📊 — ver abaixo) e outra citando 6 fontes de proliferate
fora de escopo "por volume". Investigando cada uma individualmente
contra o oráculo real (não a alegação do comentário antigo):

1. **Sphinx of the Second Sun** — "if you cast it, take an extra turn"
   nunca implementado (nem a fila de turnos extras existia no arquivo).
   Corrigido: `extra_turns_pending`/`sphinx_sacrifice_pending`, mesma
   convenção já usada nos simuladores do Maralen/Megatron desta sessão.
   Verificado que a condição "if you cast it" **não** é satisfeita
   quando a Bridge põe a carta em campo (ela não conjura, só coloca) —
   isso é regra real, não uma lacuna.
2. **Carth the Lion** — ETB "look at top 7, reveal planeswalker, put in
   hand" 100% ausente (eu tinha memorizado errado o texto dela antes de
   verificar — não é a habilidade que eu assumi inicialmente). Corrigido:
   `do_carth_etb()`. Estático real "planeswalker loyalty abilities cost
   {1} more" também implementado (`activate_planeswalkers()`, taxa real
   nas nossas próprias ativações).
3. **Flux Channeler / Inexorable Tide** — "whenever you cast a
   noncreature/any spell, proliferate" 100% ausentes apesar de reusarem
   uma função (`proliferate_loyalty()`) já testada pro Evolution
   Sage/Vraska. Corrigidos, disparam independentemente se ambos em campo.
4. **Mutational Advantage / Ripples of Potential** — proliferate no
   próprio efeito ao serem conjuradas, 100% ausente. Corrigido.

Validado com 6+ testes unitários isolados + regressão de 20.000 partidas
(0 erros, alternando `with_greater_auramancy`) + `run_batch` confirmando
ativação real (Sphinx extra turn 4,7% dos jogos, Carth tutor 11,2%).

## Reclassificações (não bugs, verificação corrigiu minha própria memória)

- **Arena Rector**: eu lembrava errado como ETB "exile + recast lendário
  do cemitério" — o texto real é um **gatilho de MORTE** ("When this
  creature dies..."). Como nada remove nossas próprias
  criaturas/planeswalkers neste modelo (`resolve_removal_round()` só
  atinge Sterling Grove/Greater Auramancy/a própria Bridge), esse
  gatilho nunca teria janela real — 📊 estrutural confirmado, não gap.
- **The Peregrine Dynamo**: "{1},{T}: copy target activated/triggered
  ability from another legendary source" — exceção arquitetural real
  (escolher QUAL dentre N fontes legendárias copiar), mesma classe do
  Strionic Resonator/Weaver of Harmony noutros decks — 📝.
- **Rhystic Study / Veil of Summer**: ambas opponent-dependent de
  verdade ("whenever an opponent casts a spell" / "if an opponent has
  cast a blue or black spell this turn") — 📊, mesma convenção
  consistente em todo o resto da sessão. A nota antiga do docstring
  ("14 cartas") estava contando os 12 planeswalkers com tag "draw" que
  JÁ tinham sido corrigidos na rodada de lealdade (2026-08-28) — a nota
  ficou desatualizada, não os gaps continuavam reais.

## Deferido, confirmado genuinamente fora de escopo (não implementado)

- **Nicol Bolas, Dragon-God** — estático "has all loyalty abilities of
  all other planeswalkers" exigiria uma segunda camada de escolha por PW
  em cima da lógica já hardcoded de `resolve_planeswalker()`.
- **Ichormoon Gauntlet** — concede uma habilidade de lealdade NOVA
  ("[0]: Proliferate", "[−12]: extra turn") a cada um dos 17
  planeswalkers — mesma classe de reestruturação do Nicol Bolas, escopo
  desproporcional ao resto desta rodada.

---

## Resumo numérico

- **~65 cartas não-terreno** (escopo do simulador — foco no motor
  Bridge/planeswalker, não curva geral completa).
- **🐛 Corrigido nesta rodada:** 5 cartas (Sphinx of the Second Sun,
  Carth the Lion, Flux Channeler, Inexorable Tide, Mutational
  Advantage/Ripples of Potential).
- **📊/📝 Confirmado estrutural (2 reclassificações de memória errada,
  não bugs):** Arena Rector, The Peregrine Dynamo.
- **Deferido, genuinamente desproporcional:** Nicol Bolas, Ichormoon
  Gauntlet (ambos exigiriam reestruturar a arquitetura hardcoded de
  planeswalker deste arquivo especificamente, não um julgamento de
  valor sobre a carta em si).
