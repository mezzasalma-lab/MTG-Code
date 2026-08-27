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
