# Goldfish Log — Edgar Markov

## Simulação #1 — gerada por Claude (RNG real, não é partida sua)

**Método:** embaralhei a lista de 100 cartas de `lista.md` com `random.shuffle` do Python (sem seed fixa, entropia do sistema) em 2026-08-20. On the play, sem compra no T1.

**Mão inicial:** Takenuma Abandoned Mire, Smothering Tithe, Godless Shrine, Arcane Signet, Roaming Throne, Swamp, Swords to Plowshares

**T1:** Joga Takenuma, Abandoned Mire.

**T2:** Compra: Sevinne's Reclamation. Joga Godless Shrine. Conjura Swords to Plowshares (`{W}`) — sem alvo real num goldfish solo (não há criatura de oponente), incluído aqui só como jogada de curva hipotética.

**T3:** Compra: Unholy Annex // Ritual Chamber. Joga Swamp. Conjura Arcane Signet (`{2}`).

**T4:** Compra: Skullclamp. Sem terreno na mão. Conjura Skullclamp (`{1}`).

**T5:** Compra: Phyrexian Altar. Sem terreno na mão (3 terrenos + Arcane Signet = 4 fontes de mana no total).
**Correção em relação a uma primeira passada automática:** meu script inicial tentou conjurar Sevinne's Reclamation aqui, mas isso está errado — Sevinne's Reclamation exige um alvo no cemitério com custo de mana 3 ou menos, e nenhuma criatura morreu ainda nessa simulação, então **não há alvo legal e a mágica não pode ser conjurada**. Corrigindo: com 4 mana disponível, a jogada real é conjurar **Roaming Throne** (`{4}`), escolhendo o tipo Vampire ao entrar (sinergiza com o Eminence do próprio Edgar Markov e com os outros gatilhos de Vampiro da lista).

**T6:** Compra: Edgar Markov. Sem terreno na mão. Mana disponível: 3 terrenos + Arcane Signet = 4. Edgar Markov custa `{3}{R}{W}{B}` = 6 total — **não castável ainda**, faltam 2 fontes de mana. Com os 4 mana disponíveis, a jogada real é conjurar **Smothering Tithe** (`{3}{W}`), usando Godless Shrine/Arcane Signet pro W.

**Board final (fim do T6):** Takenuma Abandoned Mire, Godless Shrine, Swamp, Arcane Signet | Skullclamp, Roaming Throne (tipo Vampire), Smothering Tithe.
**Mão remanescente:** Sevinne's Reclamation (ainda sem alvo), Unholy Annex // Ritual Chamber, Phyrexian Altar, Edgar Markov (o próprio comandante preso na mão por falta de mana).
**Observação honesta:** essa mão específica ficou land-light (só 3 terrenos em 6 turnos) e nunca chegou a resolver o próprio comandante em campo — ele ficou parado na mão do T6 em diante por faltar 2 fontes de mana. Não simulei além do T6.

---

## Simulação #2 — goldfish Python completo (`edgar_markov_goldfish_v1.py`) — 2026-08-21

**Script construído do zero**, CARD_DB gerado via Scryfall `cards/collection` (99 cartas), tags derivadas de `oracle_text` real. Passo 0 (regra de Roaming Throne, `references/goldfish-sim-card-rules.md`): varredura mecânica encontrou **16 vampiros com gatilho próprio** (de 20 + o próprio Edgar) — todos implementados como mecânica real (Eminence, contador de ataque do Edgar, Sanctum Seeker, Champion of Dusk, Welcoming Vampire, Clavileño, Vito Fanatic de Aclazotz em 3 estágios, e o pacote de morte Blood Artist/Cruel Celebrant/Cordial Vampire/Vindictive Vampire/Vein Ripper via um loop de sacrifício limitado a 2 por turno).

**Simplificações documentadas no docstring do script:** sem combate real contra o oponente (assume Edgar sempre ataca livre depois do summoning sickness); drain/lifegain rastreados como contadores agregados, não life totals reais; Ashnod's Altar/Phyrexian Altar não contam pro `total_mana()` automático (exigem sacrifício, só geram mana quando o loop de sacrifício os usa de fato).

**n=2000, 8 turnos:**

```
Avg mulligans: 0,58
Turno médio de conjuração do Edgar Markov: 5,90 | mediana: 6
Nunca conjurado em 8 turnos: 17,1%
Avg tokens de Vampiro via Eminence: 2,46
Avg turnos em que Edgar atacou: 1,74
Avg contadores +1/+1 distribuídos: 5,90
Avg drain_total (proxy): 0,65 | Avg lifegain_total (proxy): 0,77
Avg criaturas sacrificadas: 1,09 | Avg gatilhos de morte: 0,58
Avg compras via Champion of Dusk: 0,22 | via Welcoming Vampire: 0,25
Avg drains via Sanctum Seeker: 0,16
Avg Demons via Vito Fanatic (3o estágio): 0,00
Avg gatilhos de Clavileño (sem efeito extra modelado): 0,21
```

**Combo Exquisite Blood + Vito, Thorn of the Dusk Rose — resposta à pergunta em aberto da auditoria original ("não simulei o deck pra saber em que turno esse combo tipicamente monta"):**

```
Partidas em que o combo montou E ligou (até T8): 0,1% (2 de 2000)
Turno médio em que liga, quando acontece: 7,67 | mediana: 8
```

**Leitura:** dentro de uma janela normal de 8 turnos, o combo montar e efetivamente ligar é **raríssimo** (0,1%) — exige que as duas peças específicas (Exquisite Blood + Vito, Thorn of the Dusk Rose, cada uma ~1% de densidade em 99 cartas) sejam compradas e conjuradas na mesma partida, o que é uma coincidência dupla rara mesmo com o volume de tutores do deck (Vampiric Tutor, Diabolic Intent, Demonic Tutor via Emeritus of Woe — o simulador atual não modela ativação de tutor pra buscar peça específica, é uma extensão futura). Isso não muda a classificação de Bracket 4 (o critério oficial é sobre a PRESENÇA estrutural do combo com habilitadores redundantes, não sobre a frequência real de montagem em partidas de goldfish) — mas é um dado real que faltava.

**Roaming Throne:** em campo em 10,2% dos jogos, dobrando em média 0,30 gatilhos de Vampiro por partida — número baixo porque a maioria dos 16 gatilhos de vampiro tem densidade individual baixa (cada vampiro é só 1 carta de 99), a mesma dinâmica de baixa coincidência já vista nos outros decks desse usuário.

---

### Política "caçar o combo" — comprova a classificação de Bracket com dado real — 2026-08-21

**Pedido do usuário:** implementar uma política que prioriza os 2 tutores reais e baratos (Vampiric Tutor `{B}`, Diabolic Intent `{1}{B}`) especificamente pra buscar a peça que falta do combo Exquisite Blood + Vito, Thorn of the Dusk Rose, e conjurar as peças assim que disponíveis — pra medir se o combo consegue ligar antes do turno 6 (o corte oficial de Bracket) quando o jogador está mirando nisso de propósito, não só por sorte.

**Implementação:** novo flag `COMBO_HUNTING_POLICY` (default `False`) + função `combo_hunt()`, chamada no topo do `main_phase`. Diabolic Intent busca a peça faltante direto pra mão (exige sacrificar uma criatura em campo); Vampiric Tutor busca pro topo da biblioteca (pega na próxima compra normal). Novo campo rastreado: `both_combo_pieces_turn` (turno em que as 2 peças já estão em campo, antes de precisar de um gatilho pra "ligar" o loop).

**n=2000, 8 turnos, comparando as duas políticas:**

| Métrica | Genérica (default) | Caçando o combo |
|---|---|---|
| 2 peças em campo até T4 | 0,0% | 0,3% |
| 2 peças em campo até T5 | 0,1% | 1,6% |
| **2 peças em campo até T6** | **0,1%** | **2,6%** |
| 2 peças em campo até T8 | 0,7% | 4,6% |
| Turno médio (quando acontece) | 7,38 | **6,20** |
| **Combo ligado (gatilho de vida disparou) até T6** | **0,0%** | **0,0%** |
| Combo ligado, total em 8 turnos | 0,1% | 0,6% |

**Verificação de correção:** rastreei uma partida individual (seed 6000261) onde as peças alinharam rápido — Vampiric Tutor no T1 buscou Exquisite Blood, Vito Thorn veio de compra natural no T3, Exquisite Blood entrou em campo no T5 assim que teve mana (`{4}{B}`). Confirma que a lógica está certa; é só raro de acontecer, não um bug.

**Leitura:** mesmo com o jogador ativamente perseguindo o combo com os 2 tutores reais, a chance dele estar **ligado** antes do turno 6 é **0,0%** em 2000 partidas. O cálculo manual de "melhor caso turno 5" feito antes de rodar essa simulação era otimista demais — assumia mana certa toda hora e nenhuma outra prioridade competindo, cenário que não reflete a realidade de um deck de 99 cartas singleton. Isso muda a classificação de Bracket de volta pra 3 (ver `auditoria.md` seção 12, 2ª correção) — o critério oficial é "antes do turno 6", e mesmo perseguido de propósito o combo não entrega isso de forma confiável.

---

## Correção #1 — revisão completa carta-a-carta (usuário: "faça a carta por carta do Markov")

Usuário: *"Repita a auditoria minuciosa com o Edgar Markov"*, seguido de *"Agora faça a carta por carta do Markov"* — o mesmo rigor já aplicado no Ur-Dragon e no Hei Bai, nunca tinha sido feito neste deck (a Simulação #2 e a política de caçar o combo, acima, cobriam o motor central de vampiro/aristocratas, mas nunca uma varredura carta-a-carta contra o oráculo real das 99 cartas).

Conferido `oracle_text` real (Scryfall, `/tmp/scryfall_cache/edgar_markov_full.json`) de toda a lista contra `edgar_markov_goldfish_v1.py`. Achado: bem mais bugs que qualquer rodada do Hei Bai — várias cartas tinham tag mas ZERO implementação de verdade (`has_tag()` só é checado em 2 lugares no código inteiro: `is_vampire`/`ramp` — todo o resto das tags como `drain_aristocrats`/`token_maker`/`draw` eram decorativas, sem nenhum dispatch real por trás).

### Corrigido (achados reais novos)

1. **Funeral Room // Awakening Hall e Unholy Annex // Ritual Chamber tinham `mv` errado.** O código somava o custo dos 2 lados do Room (`2+1+6+2=11` e `2+1+3+2=8`) em vez de usar o custo real de conjurar CADA porta separadamente (Rooms não funcionam assim — você conjura uma porta de cada vez, pelo custo dela). `mv=11`/`mv=8` deixava essas 2 cartas praticamente incastáveis num goldfish de 8 turnos, travando o drain barato e recorrente que ambas oferecem por só `{2}{B}` (mv 3). Corrigido pra `mv=3` nas duas (porta primária/mais barata), e implementado o efeito real de cada uma (ver #7).
2. **Purphoros, God of the Forge — 100% ausente.** "Whenever another creature you control enters, deals 2 damage to each opponent" nunca era checado em lugar nenhum, apesar de ser um motor de dano central pra um deck que cria token toda hora (Eminence). Implementado via novo dispatch `on_creature_enters()`, chamado em toda entrada de criatura (conjurada ou token).
3. **Warleader's Call — 100% ausente.** "Whenever a creature you control enters, deals 1 damage to each opponent" — mesmo padrão do Purphoros, mesmo dispatch novo.
4. **Skullclamp — 100% ausente.** "Equipped creature dies: draw two cards" — o motor clássico de token-pra-carta deste arquétipo nunca tinha nenhum efeito. Modelado equipando o primeiro sacrifício de cada turno (custo real de {1} pra reequipar, já que o Equipment sobrevive à morte da criatura anterior).
5. **Ophiomancer — 100% ausente.** "At the beginning of each upkeep, if you control no Snakes, create a 1/1 black Snake token with deathtouch" — a única criatura do deck com gatilho de upkeep de verdade, nunca implementada. Novo `do_upkeep()`, chamado no início de cada turno.
6. **Pitiless Plunderer tinha mecânica ERRADA.** Tageado `ramp` e contribuindo +1 mana genérico automático em `total_mana()` todo turno — mas ele não tem habilidade de mana própria nenhuma; o real é "whenever another creature you control dies, create a Treasure token", condicional a morte de verdade. Corrigido: removida a tag `ramp` errada, implementado o Treasure real dentro do `sac_loop` (só gera valor quando algo morre).
7. **Zulaport Cutthroat — 100% ausente do pacote de drain**, apesar de tageado `drain_aristocrats` e citado na própria `auditoria.md` (seção 6) como "habilitador redundante" do combo. Texto idêntico ao Blood Artist ("this or another creature you control dies, opponent loses 1, you gain 1") — nunca estava no set `DEATH_PAYOFFS` de verdade. Corrigido, junto com **Bastion of Remembrance** (drain 1/1 + token ETB de Human Soldier, também ausente) e **Funeral Room**/**Unholy Annex** (agora castáveis, com seus efeitos reais: drain do Funeral Room, e o gatilho de end step do Unholy Annex — compra 1 carta, e se controlar um Demon, drena 2/ganha 2).
8. **The Meathook Massacre estava com a fórmula errada.** Reusava a mesma fórmula "drain 1, gain 1" dos outros payoffs, mas o oráculo real é assimétrico: "whenever a creature you control dies, EACH OPPONENT LOSES 1 life" (sem ganho de vida nessa cláusula — o "you gain 1" dela só dispara quando morre criatura DO OPONENTE, que não existe neste goldfish solo). Corrigido pra `(drain=1, gain=0)`.
9. **Vito, Thorn of the Dusk Rose — a peça de combo mais famosa da lista tinha ZERO implementação da PRÓPRIA habilidade.** "Whenever you gain life, target opponent loses that much life" só era usado como string-match pra decidir se o combo com Exquisite Blood estava montado — nunca gerava valor real por conta própria (mesmo sem Exquisite Blood em campo, cada vida ganha por QUALQUER fonte deveria drenar o oponente). Corrigido via novos helpers centralizados `gain_life()`/`lose_life_opponent()`, usados por todo o motor (Blood Artist, Cruel Celebrant, Sanctum Seeker, Vito Fanatic, etc.) em vez da lógica duplicada e inconsistente que existia antes.
10. **Bloodthirsty Conqueror nunca era checado como habilitador ALTERNATIVO do combo infinito.** "Whenever an opponent loses life, you gain that much life" forma o MESMO loop com Vito Thorn que Exquisite Blood forma — só o segundo era detectado. Corrigido: `_check_combo()` agora testa os 2 habilitadores.
11. **Anointed Procession e Mondrak, Glory Dominus — dobradores de token 100% ausentes**, apesar de tageados `token_maker`. "If one or more tokens would be created, twice that many instead" — mecânica DIFERENTE do Roaming Throne (que dobra o GATILHO, não a contagem de token) — empilham multiplicativamente entre si (2 dobradores = 4x). Novo `token_multiplier()`, aplicado em toda criação de token modelada (Eminence, Ophiomancer, Bastion of Remembrance, Pitiless Plunderer, 3º estágio do Vito Fanatic).
12. **`_times()` (dobra do Roaming Throne) não checava se a fonte do gatilho era mesmo uma criatura Vampiro.** Por coincidência todos os gatilhos já implementados antes eram Vampiros de verdade, então nunca deu bug visível — mas os gatilhos novos desta rodada (Purphoros, Warleader's Call, Ophiomancer, Skullclamp, Pitiless Plunderer, Zulaport Cutthroat, Meathook Massacre, Bastion of Remembrance, Funeral Room, Unholy Annex) têm fontes que não são criaturas Vampiro — Roaming Throne (que só dobra "outra criatura... do tipo escolhido") nunca deveria dobrar esses. `_times()` ganhou um parâmetro `is_vampire_source`, passado `False` explicitamente nos novos.
13. **Mana de Ashnod's Altar/Phyrexian Altar (e agora Treasure do Pitiless Plunderer) nunca era realmente gastável.** O `sac_loop()` roda DEPOIS do `main_phase()` — ou seja, a mana bônus gerada por sacrificar tokens só ficava disponível depois que o turno já tinha acabado de conjurar tudo que dava, sendo descartada no reset (`mana_spent_this_turn = 0`) do turno seguinte sem nunca virar spell nenhum. Corrigido extraindo o loop genérico de conjuração pra `cast_available_spells()`, chamado de novo depois do `sac_loop()`.
14. **Welcoming Vampire tinha a condição de gatilho ERRADA.** "Whenever one or more OTHER creatures you control with power 2 or less enter" — o código antigo checava se um Vampiro tinha sido CONJURADO (condição da Eminence, gatilho diferente), perdendo criaturas não-Vampiro de poder baixo (ex. Ophiomancer, 2/2) e só acertando por coincidência quando a Eminence também disparava. Corrigido dentro do novo `on_creature_enters()`, checando poder real via novo dicionário `CREATURE_POWER`.
15. **Bug de robustez pego durante o teste desta rodada** (só na política `COMBO_HUNTING_POLICY=True`, não no batch oficial default): o custo adicional do Diabolic Intent dentro de `combo_hunt()` podia sacrificar a PRÓPRIA Vito, Thorn of the Dusk Rose (única peça-criatura do combo) buscando a outra peça — autodestrutivo, e causava crash mais tarde quando o `combo_hunt` rodava de novo achando Vito Thorn "faltando" (foi pro cemitério, não tá mais na biblioteca pra buscar). Corrigido excluindo `COMBO_PIECES` dos candidatos a sacrifício.

Testado: 300 jogos smoke test (0 erros, política default), 25.000 jogos de robustez com timeout de 2s/jogo (0 erros, 0 timeouts, política default) + 15.000 jogos (0 erros, política `COMBO_HUNTING_POLICY=True`, depois do fix #15).

### Deferido (achado, documentado, não implementado)

- MDFCs land-primary (**Ojer Taq, Deepest Foundation // Temple of Civilization**, **Legion's Landing // Adanto, the First Fort**, **Agadeem's Awakening // Agadeem, the Undercrypt**): só o verso Land é jogado — o lado spell (Ojer Taq triplica token de criatura; Legion's Landing cria um Vampiro; Agadeem's Awakening reanima em massa) nunca é conjurado. Modelar escolha dinâmica entre face land/spell exigiria uma reforma arquitetural maior — perda real de valor, documentada em vez de silenciosa.
- Cordial Vampire (+1/+1 counters) e o gatilho de morte da própria Elenda (X tokens = poder dela): sem payoff numérico modelável — nenhuma criatura NOMEADA morre neste simulador (só tokens, decisão já documentada desde a Simulação #2), então Elenda nunca teria chance real de morrer. O passivo dela ("+1/+1 quando outra criatura morre") agora É rastreado (`elenda_counters`, por transparência de dado, sem payoff numérico adicional).
- Loyalty abilities (Elspeth Storm Slayer, Sorin), nível 2/3 do Caretaker's Talent, modo escolhido do Black Market Connections, ativada do Mondrak, escolha de tipo do Cavern of Souls: nenhuma engine de "1 ativada por turno"/"escolha modal" existe neste simulador — mesma classe de simplificação já usada nos outros decks desta sessão.
- Fetch lands: modeladas como duais estáticas de 2 cores, sem sacrifício/busca real — sem efeito na contagem de mana (1 fetch = 1 land = 1 mana), decisão consistente com o resto do simulador (nenhum land search existe aqui).

**Impacto real** (`n=2000`, política default, `seed_base=6000000`):

| métrica | antes | depois |
|---|---|---|
| Nunca conjurado em 8 turnos | 17,1% | **16,1%** |
| Avg tokens de Vampiro via Eminence | 2,46 | 2,68 |
| Avg drain_total | 0,65 | **2,20 (3,4x)** |
| Avg lifegain_total | 0,77 | **1,36** |
| Avg criaturas sacrificadas | 1,09 | 1,39 |
| Avg gatilhos de morte (death payoffs) | 0,58 | **1,28 (2,2x)** |
| Combo ligado (Exquisite Blood/Bloodthirsty Conqueror + Vito Thorn) | 0,1% | **0,6% (6x)** |
| Avg dano via Purphoros (novo) | — | 0,33 |
| Avg dano via Warleader's Call (novo) | — | 0,42 |
| Avg Snakes via Ophiomancer (novo) | — | 0,21 |
| Avg compras via Skullclamp (novo) | — | 0,21 |
| Avg Treasures via Pitiless Plunderer (novo) | — | 0,04 |
| Avg compras via Unholy Annex end step (novo) | — | 0,52 |

Salto real, não inflação — a maior parte vem de mecânicas que estavam **completamente ausentes** (Purphoros, Warleader's Call, Skullclamp, Ophiomancer, Zulaport Cutthroat, Vito Thorn), o mesmo padrão que já apareceu no Ur-Dragon e no Hei Bai: este deck estava sendo medido, desde a Simulação #2, como um motor de valor mais fraco do que a lista realmente é. Isso também reforça a leitura de poder da `auditoria.md` (seção 6, "10 cartas de drenagem de vida") — na prática são pelo menos 12 (some Purphoros e Warleader's Call, que drenam via ETB de criatura, não morte) e o combo tem 2 habilitadores redundantes reais em vez de 1 (Exquisite Blood E Bloodthirsty Conqueror, não só o primeiro).

`lista.md` não mudou — puro fix de simulador, carta por carta.

---

## Correção #2 — motor de tutores estava incompleto (usuário perguntou direto)

Usuário: *"Vc contabilizou a eminence do Edgar Markov, certo? Toda vez que Vito (ou qq outro vampiro) entra por cast ele gera um vampiro 1/1 com lifelink que tb pode ser sacrificado para o Diabolic Intent, ou usado pelo Skullclamp, etc… Além disso o Emeritus of Woe tem o Demonic Tutor Prepared, mais um tutor! Vc contabilizou isso tudo?"*

### Verificado com teste real (já estava correto, sem bug)

- **A Eminence em si.** `eminence_trigger()` cria o token corretamente sempre que um Vampiro é conjurado (Edgar em campo ou zona de comando). Correção de detalhe: o token da Eminence do **próprio Edgar Markov** é "1/1 black Vampire creature token" — **sem lifelink** (oráculo real, conferido de novo no Scryfall). Lifelink é do token do **Legion's Landing** ("1/1 white Vampire creature token with lifelink") — cartas diferentes. Não muda nenhuma métrica (este simulador não modela combate/vida própria real), só uma correção de precisão.
- **Os tokens da Eminence já alimentavam o Skullclamp.** `state.tokens` é a MESMA lista usada pelo `sac_loop()` (que já processa Ashnod's Altar/Phyrexian Altar/Viscera Seer/Goblin Bombardment) e pelo `Skullclamp` (implementado na Correção #1) — o primeiro sacrifício de cada turno já é o mesmo evento que dispara o draw 2 do Skullclamp. Já estava certo.

### Corrigido (achados reais novos — o usuário estava certo em desconfiar)

1. **Diabolic Intent nunca considerava sacrificar um token da Eminence.** O custo adicional dele ("sacrifice a creature") só olhava pra `state.battlefield` (criaturas nomeadas) — nunca pra `state.tokens` (o excedente de Vampiros 1/1 que É literalmente pra isso que servem). Um jogador de verdade sempre sacrifica o token de graça antes de perder uma carta real. Corrigido com `_pay_diabolic_intent_cost()`, compartilhado entre a política default e o `combo_hunt()`.
2. **Vampiric Tutor e Diabolic Intent só tinham busca de verdade DENTRO do `combo_hunt()`**, que só roda com `COMBO_HUNTING_POLICY=True` — **não é o padrão** (`False`). Isso significa que no batch oficial reportado ao usuário até agora (`n=2000`, política default), os 2 tutores reais do deck eram conjurados às cegas, gastando carta e mana, **sem nenhum efeito de busca**. Corrigido: nova função `_tutor_target()` (prioriza fechar o combo se só falta 1 peça, senão pega o maior mana value disponível na biblioteca — mesma convenção "pega o melhor" usada nos outros decks desta sessão), usada tanto pela política default quanto pelo `combo_hunt()`.
3. **Emeritus of Woe // Demonic Tutor — 100% ausente**, exatamente como o usuário apontou. "This creature enters prepared" dá 1 cópia de graça do Demonic Tutor (busca real) na hora que ele resolve — sem pagar `{1}{B}` de novo. E "at the beginning of your end step, if two or more creatures died this turn, this creature becomes prepared" o deixa preparado de novo toda vez que 2+ criaturas morrem no turno — bem alcançável neste deck (o `sac_loop` já sacrifica até 2 tokens por turno sozinho). Implementado: tutor de graça no ETB (`apply_etb`), flag `emeritus_prepared` setada em `do_end_step()`, consumida no início do próximo `main_phase()` (velocidade real de sorcery).
4. **Bug de robustez pego durante o teste desta correção:** com o fix #1 (Diabolic Intent agora podendo ser conjurado na política default, não só dentro do `combo_hunt`), faltava excluir "Diabolic Intent" do loop genérico de conjuração quando não há NENHUM fodder disponível (nem token, nem criatura nomeada) — a magica exige sacrifício como custo adicional obrigatório, sem isso não pode ser conjurada de verdade. Corrigido no filtro de `castables` de `cast_available_spells()`.

Testado: 300 jogos smoke test (0 erros, as 2 políticas), 25.000 jogos de robustez política default + 15.000 política `COMBO_HUNTING_POLICY=True` (0 erros/timeouts nas 2).

**Impacto real** (`n=2000`, política default, `seed_base=6000000`, comparado com o estado pós-Correção #1):

| métrica | antes (Correção #1) | depois |
|---|---|---|
| Avg tutores usados no total (novo) | 0,00 | **0,40** |
| Avg tutores via Emeritus of Woe (novo) | 0,00 | 0,11 |
| Avg criaturas sacrificadas | 1,39 | 1,34 |
| Avg gatilhos de morte | 1,28 | 1,24 |
| Avg drain_total | 2,20 | 2,16 |
| Combo ligado | 0,6% | 0,7% |

Impacto líquido pequeno nos agregados de drain/morte (ruído esperado — os tutores agora buscam cartas diferentes das que sairiam por compra normal, mudando a curva de jogo sem necessariamente aumentar volume de gatilhos), mas o achado em si é real e relevante: **3 tutores reais do deck (Vampiric Tutor, Diabolic Intent, Demonic Tutor via Emeritus of Woe) foram de zero efeito pra ~0,4 buscas por partida.** Isso é consistência de simulador, não inflação de número — o deck sempre teve esses tutores, só não estavam sendo modelados.

`lista.md` não mudou.

---

## Correção #3 — Firdoch Core (não está na lista) + Emeritus of Woe cobrando mana errado (usuário corrigiu direto)

Usuário: *"E mais uma vez, Firdoch core trigga a eminence do Markov tb!"* — depois, ao pedir confirmação do nome exato: *"Achei que tinha colocado o artefato Firdoch Core neste deck tb, é o mesmo que está no Ur-Dragon"* + *"O tutor do Eminence of Woe não é gratuito, ele custa 2cmc para cast."*

### Verificado — Firdoch Core NÃO é bug de simulador, é ausência real na lista

Conferido `oracle_text` real (Scryfall): **Firdoch Core** é `Kindred Artifact — Shapeshifter`, `{3}`, *"Changeling (This card is every creature type.) {T}: Add one mana of any color. {4}: This artifact becomes a 4/4 artifact creature until end of turn."* Changeling faz ele contar como "Vampire spell" ao ser conjurado (dispararia a Eminence de verdade, igual o usuário lembrava), e ele já está confirmado e implementado no simulador do Ur-Dragon (`ur-dragon-wurbg/goldfish-log.md`, Correção #3, 2026-08-23).

**Mas ele não está em `edgar-markov-mardu/lista.md`** — a lista atual das 99 cartas + comandante não inclui o Firdoch Core. Isso não é um bug de simulador pra corrigir (o simulador está certo em não contar uma carta que não está na lista) — é uma decisão de deckbuilding em aberto: o usuário lembrava de ter colocado, mas a lista real não tem. Fica pendente de confirmação do usuário se quer adicionar (e o que cortar, já que Commander é sempre 100 cartas exatas) — não alterei `lista.md` sem essa decisão.

### Corrigido (achado real novo — usuário corrigiu direto)

**Emeritus of Woe // Demonic Tutor — o tutor via "prepared" estava sendo tratado como grátis, mas não é.** Reconferido o oráculo: *"This creature enters prepared. (While it's prepared, you may cast a copy of its spell. Doing so unprepares it.)"* — o texto de lembrete **não diz "without paying its mana cost"** (diferente de mecânicas que são free-cast de verdade, como o kicker do Aang's Journey no Hei Bai) — "prepared" só dá a PERMISSÃO de conjurar a cópia (mesmo sem a carta física na mão), o custo real do Demonic Tutor (`{1}{B}` = 2 mana) ainda é pago. A implementação da Correção #2 (rodada anterior) tratava como grátis — bug real, corrigido: `try_emeritus_prepared_tutor()` agora só dispara com `remaining_mana(state) >= 2`, gastando os 2 mana de verdade, chamado em 2 janelas por turno (fim do main_phase inicial + depois da mana extra do sac_loop, mesmo padrão já usado pro resto do motor) pra não deixar a "preparação" perdida se não sobrar mana na primeira janela.

Testado: 300 jogos smoke test (0 erros, as 2 políticas), 25.000 jogos de robustez política default + 15.000 política `COMBO_HUNTING_POLICY=True` (0 erros/timeouts nas 2).

**Impacto real** (`n=2000`, política default, `seed_base=6000000`, comparado com o estado pós-Correção #2):

| métrica | antes (Correção #2) | depois |
|---|---|---|
| Avg tutores via Emeritus of Woe | 0,11 | **0,05 (quase metade)** |
| Avg tutores usados no total | 0,40 | 0,34 |
| Avg drain_total | 2,16 | 2,14 |
| Combo ligado | 0,7% | 0,5% |

Queda pequena e proporcional — exatamente o esperado de exigir 2 mana de verdade em vez de disparar sempre de graça. Nenhuma outra métrica teve mudança fora do ruído normal de "tutor busca carta diferente, muda ligeiramente a curva do resto do jogo".

`lista.md` não mudou (a questão do Firdoch Core segue em aberto, aguardando decisão do usuário).

---

## Correção #4 — Stensian Sanguinist // Exsanguinate também tinha "prepared" ausente (usuário perguntou direto)

Usuário: *"Vc contou o Exsanguinate preparado do Sanguine Stensian como mana sink e um finalizador potencial?"*

Não — 100% ausente, mesma classe de bug do Emeritus of Woe (Correção #2), só que com gatilho diferente. Conferido o oráculo real: **Stensian Sanguinist** — *"Whenever you attack, target attacking creature gains deathtouch until end of turn. Whenever that creature deals combat damage to a player this combat, this creature becomes prepared."* Verso **Exsanguinate** (`{X}{B}{B}`, Sorcery) — *"Each opponent loses X life. You gain life equal to the life lost this way."* A tag `drain_aristocrats` que ele tinha era decorativa E errada (o gatilho real não é "criatura morre", é combate) — removida.

### Implementado

- `combat_step()`: como este simulador não modela bloqueadores (a premissa inteira do combate aqui já é "Edgar ataca livre, sem oposição"), qualquer ataque conecta — então a condição "dealt combat damage to a player" é praticamente garantida sempre que há combate. Stensian não precisa nem atacar ela mesma, só estar em campo. Fica `stensian_prepared = True`.
- `try_stensian_prepared_exsanguinate()`: mesma lição já aprendida no Emeritus of Woe — "prepared" não é free-cast, ainda paga o custo real (`{B}{B}` fixo). `X` = toda a mana sobrando menos esse `{B}{B}` (mana sink de verdade — sem custo de oportunidade em gastar mana que sobraria sem uso mesmo). Só conjura se `X > 0`. Como o "torna-se preparado" acontece DENTRO do combate (depois das 2 janelas de conjuração do turno), a cópia só pode ser conjurada a velocidade de sorcery no turno SEGUINTE — mesma limitação de 1 turno de atraso do Emeritus of Woe, pela mesma razão (este simulador não modela uma 2ª main phase pós-combate). Chamado nas 2 mesmas janelas (fim do main_phase inicial + depois da mana extra do sac_loop).
- O drain/gain do Exsanguinate passa pelos helpers centralizados `lose_life_opponent()`/`gain_life()` — herda de graça a checagem do combo Exquisite Blood/Bloodthirsty Conqueror + Vito Thorn (um X grande de Exsanguinate É um jeito real de ligar o combo se as peças já estiverem em campo).

Testado: 300 jogos smoke test (0 erros, as 2 políticas), 25.000 jogos de robustez política default + 15.000 política `COMBO_HUNTING_POLICY=True` (0 erros/timeouts nas 2).

**Impacto real** (`n=2000`, política default, `seed_base=6000000`, comparado com o estado pós-Correção #3):

| métrica | antes (Correção #3) | depois |
|---|---|---|
| Avg Exsanguinate conjurados (novo) | 0,00 | **0,07** |
| Avg X total do Exsanguinate (novo) | 0,00 | 0,26 |
| Avg drain_total | 2,14 | **2,42** |
| Avg lifegain_total | 1,31 | **1,58** |
| Combo ligado | 0,5% | 0,7% |

Salto real e proporcional ao esperado — Exsanguinate é raro de disparar (precisa de Stensian em campo, sobreviver até o combate, e ter mana sobrando no turno seguinte, numa janela de só 8 turnos simulados), mas quando dispara move `drain_total`/`lifegain_total` de forma visível porque `X` pode ser grande (mana sink de verdade).

`lista.md` não mudou.

---

## Correção #5 — Stensian preparado podia ser usado na 2ª main phase do MESMO turno, não só no seguinte (usuário corrigiu de novo)

Usuário: *"Os spells preparados que são preparados no combate podem ser cast na second main phase, não precisam esperar um turno."*

Achado real — a Correção #4 (rodada anterior, mesmo dia) implementou o custo real do Exsanguinate mas errou o timing: assumiu que "prepared" só liberava a cópia no turno **seguinte**, por analogia direta com o Emeritus of Woe (que de fato só fica preparado no fim do end step, depois da 2ª main phase — aí sim só dá pra usar no turno de novo). Mas um turno de Magic real é `main phase 1 → combate → main phase 2 → end step`, tudo no mesmo turno — Stensian Sanguinist fica prepared **durante** o combate, e ainda sobra uma main phase inteira **no mesmo turno** pra conjurar a cópia a velocidade de sorcery.

### Corrigido

`try_stensian_prepared_exsanguinate()` agora é chamado logo depois do `combat_step()` em `play_turn()` (a 2ª main phase de verdade), além das 2 janelas que já existiam antes do combate (que continuam válidas como fallback pro turno seguinte — "prepared" não expira no fim do turno, o texto de lembrete não diz isso).

Testado: 300 jogos smoke test (0 erros, as 2 políticas), 25.000 jogos de robustez política default + 15.000 política `COMBO_HUNTING_POLICY=True` (0 erros/timeouts nas 2).

**Impacto real** (`n=2000`, política default, `seed_base=6000000`, comparado com o estado pós-Correção #4):

| métrica | antes (Correção #4) | depois |
|---|---|---|
| Avg Exsanguinate conjurados | 0,07 | **0,12** |
| Avg X total do Exsanguinate | 0,26 | 0,37 |
| Avg drain_total | 2,42 | 2,54 |
| Avg lifegain_total | 1,58 | 1,70 |

Alta real e proporcional — a janela extra na mesma turno captura valor que se perderia de vez numa simulação de só 8 turnos (mana que sobrava logo depois do combate mas já tinha sido gasta de novo até o início do turno seguinte, ou o próprio jogo acabando antes de chegar lá).

`lista.md` não mudou.

---

## Verificação — a linha de finalizador "sacrifica pro Altar → dreno dos payoffs → Exsanguinate grande" está de verdade encadeada (usuário pediu confirmação)

Usuário: *"O grande lance é a multiplicação: Se eu sacrificar tokens para altar gerando mana, com zulaport/blood artist/etc no campo, eu causo dano nos sacs, gero mana, faço um exsanguinate de 10+ e ganho o mesmo em vida! No momento certo pode eliminar um oponente!"*

Confirmado com teste ao vivo (não só releitura de código) — board de teste: Ashnod's Altar + Zulaport Cutthroat + Blood Artist + Stensian Sanguinist (já preparado) + 8 terrenos + 2 tokens de Vampiro disponíveis:

```
sac_loop() sacrifica os 2 tokens no Ashnod's Altar:
  +4 mana efetiva (Altar) | drain +4, gain +4 (Zulaport Cutthroat + Blood Artist, cada um 2x — 1 por sacrifício)
try_stensian_prepared_exsanguinate() usa os 12 mana restantes:
  X = 10 | drain +10, gain +10

Total do turno: drain_total 0 → 14, lifegain_total 0 → 14
```

A cadeia está corretamente encadeada de ponta a ponta: sacrificar no Altar gera mana (`sac_loop`, `mana_spent_this_turn -= 2` por uso) **e** dispara os payoffs de morte (`_apply_death_payoffs`, uma vez por sacrifício) simultaneamente — e essa mana extra fica disponível pro Exsanguinate no MESMO turno (via a janela de 2ª main phase da Correção #5). Com um board maior (mais payoffs em campo, mais tokens sacrificados, mais mana disponível) o `X` escala junto.

**Limite honesto do simulador:** não existe life total de oponente real rastreado aqui (só os contadores agregados `drain_total`/`lifegain_total`), então "eliminar um oponente" não é algo que o simulador valida literalmente — mas o pico no `X` do Exsanguinate (visível em `exsanguinate_x_total` no batch oficial) reflete bem o potencial de dano dessa linha quando as peças se encontram.

`lista.md` não mudou.

---

## Correção #6 — auditoria do resto do deck (usuário: "Audite o resto do deck")

Depois de 5 rodadas focadas em cartas específicas (o motor de aristocratas/Eminence, os tutores, os 2 "prepared"), o usuário pediu pra varrer o que sobrou. Conferido `oracle_text` real de toda carta ainda não tocada diretamente por uma pergunta pontual.

### Corrigido (achados reais novos)

1. **Removal/proteção nunca era excluída do loop genérico de conjuração** — a MESMA classe de bug já corrigida no Hei Bai/Ur-Dragon (sessão inteira), mas que nunca chegou a ser aplicada aqui apesar de 5 rodadas de correção. Anguished Unmaking, Get Lost, Path to Exile, Swords to Plowshares, Vindicate, Rite of Oblivion (removal sem alvo real), Call the Coppercoats (sempre X=0, conta criaturas de oponente que não existem aqui), Clever Concealment e Teferi's Protection (proteção pura) eram conjuradas às cegas, gastando carta e mana de graça. Novo `EXCLUDE_BLIND_CAST`.
2. **Plumb the Forbidden, Sevinne's Reclamation e Bloodline Bidding — 100% ausentes**, conjuradas às cegas sem nenhum efeito. Implementadas: Plumb the Forbidden sacrifica todos os tokens disponíveis (cada um dispara os death payoffs) e copia o draw por sacrifício; Sevinne's Reclamation busca o melhor permanente MV≤3 no cemitério; Bloodline Bidding reanima todos os Vampiros do cemitério. Baixo volume (poucas criaturas nomeadas morrem neste simulador), mas real quando acontece — 1 e 5 ocorrências em 2000 jogos, respectivamente, conferido com soma bruta pra confirmar que não é zero-por-bug.
3. **Bloodletter of Aclazotz — 100% ausente.** "If an opponent would lose life during YOUR TURN, they lose twice that much life instead." Este simulador só simula os PRÓPRIOS turnos — ou seja, essa condição é sempre verdadeira aqui, um multiplicador universal sobre TODO drain do motor (Zulaport, Blood Artist, Purphoros, Warleader's Call, Sanctum Seeker, Exsanguinate, tudo). Implementado como replacement effect dentro de `lose_life_opponent()`.
4. **Elspeth, Storm Slayer — dobrador de token nunca foi incluído.** Mesmo texto estático do Anointed Procession/Mondrak ("if one or more tokens would be created, twice that many instead"), só citada num comentário antigo, nunca de verdade adicionada em `TOKEN_DOUBLER_SOURCES`.
5. **Smothering Tithe tinha a MESMA classe de bug do Pitiless Plunderer** (Correção #1): tag `ramp` inventada dando +1 mana automático todo turno. O único gatilho real dela ("whenever an opponent draws a card") exige o OPONENTE comprar carta — nunca acontece neste simulador que só avança os próprios turnos (mesma limitação arquitetural do Seedborn Muse no Hei Bai). Tag e `produces` removidos.
6. **Bartolomé del Presidio e Phyrexian Tower são sac outlets reais nunca incluídos em `SAC_OUTLETS`.** Bartolomé ("Sacrifice another creature or artifact: put a +1/+1 counter") é de graça, igual Viscera Seer. Phyrexian Tower ("{T}, Sacrifice a creature: Add {B}{B}") é um terreno normal — usar essa habilidade EM VEZ do `{T}: Add C` normal dá ganho líquido de +1 (não +2, já que é o mesmo tap).
7. **Indulgent Aristocrat** ("{2}, Sacrifice a creature: put a +1/+1 counter on each Vampire") é um outlet de sacrifício real, só que PAGO — agora considerado no `sac_loop` quando não há outlet de graça em campo, gastando os 2 mana de verdade.
8. **Urza's Saga — 100% ausente**, tratada só como terreno incolor fixo. Implementado o capítulo III (2 turnos depois de jogada): busca um artefato de custo `{0}` ou `{1}` (Sol Ring/Skullclamp) e se sacrifica, exatamente como o oráculo real. Capítulo II (Construct token, exige uma ativação `{2}`+tap por turno) fica deferido — mesma classe de simplificação de "ativada por turno" já usada no resto do motor.
9. **Nenhum terreno tinha rastreio de "tapado" neste simulador** (diferente do Hei Bai). Savai Triome (sempre tapado) e Blackcleave Cliffs/Haunted Ridge (condicional à quantidade de OUTROS terrenos já em campo) contribuíam mana no mesmo turno em que entravam, sem restrição nenhuma. Novo `tapped_lands_this_turn`, subtraído de `total_mana()`.

### Deferido (achado, documentado, não implementado)

- Charismatic Conqueror: gatilho exige permanente de OPONENTE entrando destapado — nunca teria janela real aqui (mesma classe do Seedborn Muse/Smothering Tithe). Corpo vanilla é o resultado correto.
- Nullpriest of Oblivion (kicker, reanima da graveyard se kicked): baixo valor esperado, mesma razão do Sevinne's Reclamation/Agadeem's Awakening — pool de reanimação quase sempre vazio.
- Voldaren Estate / Fountainport (Blood/Fish/Treasure tokens): ativadas caras (mana adicional além do tap), mesma classe de simplificação do Mondrak/Westvale Abbey.

Testado: 300 jogos smoke test (0 erros, as 2 políticas), 25.000 jogos de robustez política default + 15.000 política `COMBO_HUNTING_POLICY=True` (0 erros/timeouts nas 2).

**Impacto real** (`n=2000`, política default, `seed_base=6000000`, comparado com o estado pós-Correção #5):

| métrica | antes (Correção #5) | depois |
|---|---|---|
| Avg drain_total | 2,54 | **4,10 (1,6x)** |
| Avg lifegain_total | 1,70 | **2,71** |
| Avg criaturas sacrificadas | 1,33 | **2,24** |
| Avg gatilhos de morte | 1,23 | **2,13** |
| Avg tutores via Urza's Saga (novo) | 0,00 | 0,14 |
| Avg compras via Plumb the Forbidden (novo) | 0,00 | 0,22 |
| Combo ligado | 0,7% | **1,5%** |
| Nunca conjurado em 8 turnos | 17,1% | 16,3% |

Salto real e bem maior que qualquer rodada anterior deste deck (fora a Correção #1) — o combinado de excluir removal do auto-cast (liberando espaço pra spells reais) + Bloodletter of Aclazotz dobrando tudo + 2 sac outlets novos + Urza's Saga se acumula de forma multiplicativa, não aditiva.

`lista.md` não mudou.

---

## Correção #7 — tokens viviam fora do battlefield (achado arquitetural) + terrenos/Class/modal reconferidos (usuário: "terrenos, geradores de tesouro e tokens, etc?")

Usuário: *"Todas as cartas auditadas e contabilizadas de forma correta no simulador? terrenos, geradores de tesouro e tokens, etc?"*

Reconferindo tokens especificamente, achei um bug arquitetural maior que qualquer achado pontual das rodadas anteriores.

### Achado central: tokens nunca entravam em `state.battlefield`

Todo token deste deck (Vampire Token da Eminence, Snake Token do Ophiomancer, Human Soldier Token do Bastion of Remembrance, Vampire Demon Token do Vito Fanatic) só era adicionado a `state.tokens` — um pool separado, usado só como munição de sacrifício pelo `sac_loop`. Nunca ia pra `state.battlefield`, a lista que `is_vampire()`/`is_creature()`/toda contagem de "quantos Vampiros você controla" de fato lê. Confirmado ao vivo:

```python
state.battlefield = ['Edgar Markov']
state.tokens = ['Vampire Token', 'Vampire Token', 'Vampire Token']
sum(1 for c in state.battlefield if is_vampire(c))  # => 1, deveria ser 4
```

Isso significava que **Champion of Dusk** ("draw X cards where X = Vampires you control") e o gatilho de ataque do **Sanctum Seeker** ("whenever A Vampire you control attacks") nunca contavam os tokens da própria Eminence — o motor mais central do deck estava invisível pra si mesmo. Corrigido: todo token agora entra em `state.battlefield` também (novas entradas em `CARD_DB` — sem isso, `is_vampire()`/`is_creature()` dariam `KeyError`, os nomes não existiam na base). Todo ponto que faz `state.tokens.pop()` agora também remove a MESMA instância de `state.battlefield`. Verificado com invariante ao vivo: 3000 jogos × 8 turnos, 0 divergências entre as duas listas.

De quebra, isso destampou outro bug: **Sanctum Seeker disparava só 1x por combate** (flat), quando o oráculo real é "whenever A Vampire you control attacks" — um gatilho POR vampiro atacante, igual o próprio contador de ataque do Edgar (que já escalava com `vamps_in_play`, mas via a contagem incompleta). Corrigido pra escalar com `vamps_in_play` também — maior salto desta rodada (0,17 → 0,97, quase 6x).

### Outros achados reais (terrenos, Class, modal)

1. **Cabal Coffers tinha mana de graça inventada.** O oráculo real não tem NENHUM `{T}: Add` — a única habilidade é `{2}, {T}: Add B for each Swamp you control`. O código antigo dava +1 (terreno normal) MAIS o bônus de Swamps, sem nunca pagar o `{2}`. Corrigido com `try_cabal_coffers()`, custo real, só ativa se `swamps > 2` (compensa o custo).
2. **`swamp_count()` comparava substring do NOME** (`"Swamp" in c`) — perdia Blood Crypt e Godless Shrine, que têm o TIPO Swamp de verdade mas não têm "Swamp" no nome. Corrigido com `SWAMP_TYPED_LANDS`.
3. **Minas Tirith** ("enters tapped unless you control a legendary creature") nunca checava isso — agora integrado ao `tapped_lands_this_turn` já existente, com um novo `LEGENDARY_CREATURE_NAMES`.
4. **Caretaker's Talent — a habilidade BASE do Class** ("whenever one or more tokens enter, draw a card, once per turn") estava lumped errado como "modal deferido" junto com os níveis 2/3 desde a Correção #1 — mas essa parte NÃO depende de nível nenhum, é ativa desde que a carta resolve. Implementada (níveis 2/3 continuam deferidos).
5. **Black Market Connections — 100% ausente**, mesmo erro de "modal deferido". Como este simulador não rastreia vida própria real, um jogador greedy escolhe os 3 modos toda vez (Treasure + compra + token Shapeshifter 3/2 changeling) sem custo de verdade neste modelo. Implementado.

Testado: 300+ jogos smoke test (0 erros, as 2 políticas), 25.000 jogos de robustez política default + 15.000 política `COMBO_HUNTING_POLICY=True` (0 erros/timeouts nas 2) + invariante de consistência tokens/battlefield em 3000 jogos completos (0 divergências).

**Impacto real** (`n=2000`, política default, `seed_base=6000000`, comparado com o estado pós-Correção #6):

| métrica | antes (Correção #6) | depois |
|---|---|---|
| Avg drains via Sanctum Seeker | 0,17 | **0,97 (5,7x)** |
| Avg contadores +1/+1 (ataque do Edgar) | 6,27 | **8,75** |
| Avg drain_total | 4,10 | **5,23** |
| Avg lifegain_total | 2,71 | **3,54** |
| Avg compras via Champion of Dusk | 0,28 | 0,37 |
| Avg compras via Caretaker's Talent (novo) | 0,00 | 0,19 |
| Avg Treasures via Black Market Connections (novo) | 0,00 | 0,44 |
| Avg compras via Black Market Connections (novo) | 0,00 | 0,40 |
| Avg tokens via Black Market Connections (novo) | 0,00 | 0,44 |

Salto real e concentrado no achado central (Sanctum Seeker escalando de verdade) — o resto das correções desta rodada (Cabal Coffers, Minas Tirith, Caretaker's Talent, Black Market Connections) soma valor real mas menor, cada um limitado pela raridade de 1 carta em 99.

`lista.md` não mudou.

---

## Correção #8 — Treasure virou token de verdade + Black Market Connections mais conservador (usuário pediu direto)

Usuário: *"Coloca Black Market connections por default gerando 1 tesouro por 1 vida, para disparar Caretaker's Talent e outros gatilhos de token/artefato."*

### Achado: Treasure nunca era um token de verdade

Tanto o Treasure do **Pitiless Plunderer** quanto o do **Black Market Connections** eram implementados como um bônus de mana abstrato (`mana_spent_this_turn -= t`) — nunca uma entrada real em `state.battlefield`. Isso significava que o Treasure nunca disparava o **Caretaker's Talent** (implementado na Correção #7 — "whenever one or more tokens you control enter") nem qualquer outro gatilho futuro de token/artefato, mesmo sendo literalmente um token.

Corrigido com `create_treasure_and_crack()`: o Treasure agora entra de verdade em `state.battlefield` (dispara `on_token_enters`, novo — extraído de `on_creature_enters` pra também cobrir tokens não-criatura), e só depois é "rachado" pela própria habilidade dele (`T, Sacrifice: Add one mana of any color`) na mesma passada — um jogador greedy sempre cracka na hora. Compartilhado pelas 2 fontes de Treasure do deck (Pitiless Plunderer, Black Market Connections). Verificado com invariante ao vivo (2000 jogos): nenhum Treasure Token nunca fica "esquecido" em campo entre turnos.

### Black Market Connections — modo padrão mais conservador

Junto com o pedido, reconsiderei a Correção #7: por padrão, escolher os 3 modos toda vez (Treasure + compra + token Shapeshifter) só porque vida não é rastreada aqui era otimista demais — perder 6 vida por turno de forma automática não é um piloto realista, mesmo sem um número exato de vida neste modelo. Corrigido pra só o modo pedido (Sell Contraband, 1 Treasure) por padrão; Buy Information e Hire a Mercenary ficam deferidos.

Testado: 500 jogos smoke test (0 erros, as 2 políticas), 25.000 jogos de robustez política default + 15.000 política `COMBO_HUNTING_POLICY=True` (0 erros/timeouts) + invariante de token/battlefield e "nenhum Treasure sobra em campo" em 2000 jogos completos (0 divergências).

**Impacto real** (`n=2000`, política default, `seed_base=6000000`, comparado com o estado pós-Correção #7 — queda esperada, Black Market Connections ficou mais conservador):

| métrica | antes (Correção #7) | depois |
|---|---|---|
| Avg drain_total | 5,23 | 4,86 |
| Avg contadores +1/+1 (ataque do Edgar) | 8,75 | 7,57 |
| Avg compras via Black Market Connections (removido) | 0,40 | — |
| Avg tokens via Black Market Connections (removido) | 0,44 | — |
| Avg Treasures via Black Market Connections | 0,44 | 0,44 (mantido, agora token real) |
| Avg compras via Caretaker's Talent | 0,19 | 0,18 (mantido — agora também é alimentado pelos Treasures) |

`lista.md` não mudou.

---

<!-- Para novas partidas (reais ou novas simulações), use o formato abaixo -->

## Partida #N — AAAA-MM-DD

- **Formato do teste:** goldfish / playtest com amigos / mesa competitiva
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:** vitória / derrota / sem resolução
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**
