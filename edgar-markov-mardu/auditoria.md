# Auditoria — Edgar Markov (Mardu — R/W/B)

Fontes usadas nesta auditoria: Scryfall REST API (`cards/collection`, `cards/named`, `cards/search?q=is:gamechanger`, campos `legalities.commander`, `color_identity`, `oracle_text`, `type_line`, `cmc`, `produced_mana`), consultada em 2026-08-20/21. EDHREC (`json.edhrec.com/pages/commanders/edgar-markov.json`, campos `synergy`/`num_decks`/`potential_decks`). Definições de Bracket: `references/commander-rules.md#brackets` do skill mtg-commander.
Data da auditoria: 2026-08-20. Ramp/draw/remoção/sinergia tribal (seções 3-8) completados em 2026-08-21 — a versão original não tinha dado de EDHREC nem varredura mecânica de `oracle_text` além da checagem de combo.

---

## 1. Validação formal

| Check | Resultado | Fonte |
|---|---|---|
| Total de cartas | 100 (99 + comandante) | contagem das linhas coladas |
| Singleton | Sem duplicatas | `uniq -d` sobre os nomes |
| Identidade de cor (Mardu) | Sem violação | `color_identity` |
| Cartas banidas em Commander | Nenhuma | `legalities.commander` |
| MDFCs não resolvidas no primeiro lote | 8, todas resolvidas individualmente via `cards/named?fuzzy` | Ojer Taq, Stensian Sanguinist, Funeral Room, Legion's Landing, Unholy Annex, Fell the Profane, Agadeem's Awakening, Westvale Abbey |

**Comandante:** Edgar Markov — `{3}{R}{W}{B}` — Legendary Creature Vampire Knight.

---

## 2. Terrenos e curva

- Terrenos: **39** — contagem por `type_line` contendo "Land" em QUALQUER face, incluindo os 5 MDFCs com verso terreno que estão listados fora da seção "Terrenos" do `lista.md` (Ojer Taq, Deepest Foundation // **Temple of Civilization**; Legion's Landing // **Adanto, the First Fort**; Fell the Profane // **Fell Mire**; Agadeem's Awakening // **Agadeem, the Undercrypt**; Westvale Abbey // Ormendahl, Profane Prince — este já estava na seção Terrenos). A contagem original desta auditoria (37) não tinha capturado os 4 MDFCs fora da seção Terrenos.
- CMC médio, não-terrenos, sem comandante: **3.23** (`cmc`).

**Fontes de mana por cor (campo `produced_mana`, todos os 39 terrenos possíveis):**

| Cor | Fontes |
|---|---|
| B (preto) | **23** |
| W (branco) | 18 |
| R (vermelho) | **14** |

Preto é claramente a cor primária (quase o dobro das fontes de vermelho) — coerente com o tema de vampiros/aristocratas, que é majoritariamente preto. Vermelho é a cor mais fraca das 3, mas 14 fontes num deck de 3 cores ainda é uma base razoável (não no nível crítico do problema de azul que o Thranduil tinha). Cabal Coffers (escala com Swamps) e Urborg, Tomb of Yawgmoth (torna todo terreno um Swamp também) reforçam ainda mais o preto especificamente.

---

## 3. Ramp — 6 peças

Cruzamento mecânico de `oracle_text` (regex por `{T}: Add`/custo de sacrifício + Add, não de memória) contra as 99 cartas do mainboard:

Arcane Signet, Sol Ring, Smothering Tithe (ramp condicional — dinheiro pra terrenos quando oponentes conjuram), **Ashnod's Altar** e **Phyrexian Altar** (`Sacrifice a creature: Add...` — ramp real, mas paga com corpo, não mana; sinergiza direto com o plano de sacrifício/aristocratas do deck, ver seção 6), **Pitiless Plunderer** (`Whenever a creature you control dies, create a Treasure token` — ramp condicional a criaturas morrendo, mesmo padrão dos altares).

**6 peças é baixo pro recomendado (10-12)**, mas o perfil é atípico de propósito: a maioria não é ramp "puro" de mana, é ramp acoplado ao motor de sacrifício (altares/Pitiless Plunderer convertem corpos — que esse deck já produz em excesso via Eminence do próprio Edgar Markov — em mana ou Treasures). Terrenos como **Cabal Coffers** (escala com Swamps) e **Urza's Saga** (busca artefato de baixo custo, incluindo Arcane Signet/Sol Ring/Skullclamp) reforçam isso fora da contagem estrita de "ramp".

---

## 4. Card draw — 11 fontes

Champion of Dusk, Clavileño First of the Blessed, Welcoming Vampire, Skullclamp, Black Market Connections, Caretaker's Talent, Plumb the Forbidden, e os terrenos utilitários Fountainport/Minas Tirith/Savai Triome (cycling)/Voldaren Estate.

Boa contagem, mas quase toda condicional a vampiros morrendo/atacando ou a criar tokens primeiro (Skullclamp precisa equipar uma criatura de poder 1 pra ser draw eficiente; Champion of Dusk conta vampiros em campo). Sem uma fonte grande incondicional tipo Rhystic Study — o motor de draw depende do resto do plano (tokens/vampiros) já estar funcionando.

---

## 5. Remoção e interação — corrigido após verificação manual do oracle_text

Varredura mecânica inicial cometeu 3 falsos positivos de "wipe" (Clever Concealment, Plumb the Forbidden, Bloodline Bidding) — nenhum dos três destrói/exila em massa. Corrigido manualmente após ler o `oracle_text` de cada um:

| Tipo | Cartas | Qtde |
|---|---|---|
| Remoção pontual | Anguished Unmaking, Get Lost, Path to Exile, Swords to Plowshares, Rite of Oblivion (exile + flashback), Vindicate, Goblin Bombardment (dano repetível via sacrifício) | 7 |
| Wipe/board control | The Meathook Massacre, Elspeth Storm Slayer (`-3`, remove 1 ameaça) | 2 |
| Proteção (não é remoção, mas é interação defensiva) | **Clever Concealment** (`phase out` de permanentes próprios — protege, não remove), **Teferi's Protection** (Game Changer, proteção total) | 2 |

**Total real: 9 efeitos de remoção/wipe** — dentro da faixa recomendada. Clever Concealment e Bloodline Bidding (recursão em massa, não wipe — ver seção 6) foram reclassificados corretamente.

---

## 6. Pacote de aristocratas/drain — o motor central, e o combo já identificado

Varredura de `oracle_text` (termos "opponent loses life"/"you gain life equal to"/gatilhos de morte) encontra **10 cartas** de drenagem de vida, coeso e validado por dado real do EDHREC (`synergy` score — positivo = joga mais nesse comandante especificamente):

| Carta | Inclusão em decks de Edgar Markov | Synergy score |
|---|---|---|
| Blood Artist | 82,4% | **+0,643** |
| Welcoming Vampire | 72,6% | **+0,599** |
| Sanctum Seeker | 67,9% | **+0,589** |
| Vito, Thorn of the Dusk Rose | 64,7% | **+0,549** |
| Cruel Celebrant | 62,9% | **+0,499** |
| Exquisite Blood | 51,3% | **+0,434** |

Todos com synergy score alto e positivo — confirma que o pacote não é goodstuff solto, é o padrão real de decks desse comandante. **O combo de 2 peças já identificado nesta auditoria (Exquisite Blood + Vito, Thorn of the Dusk Rose, seção 10) tem aqui pelo menos 4 habilitadores redundantes reais** (Blood Artist, Cruel Celebrant, Zulaport Cutthroat, Sanctum Seeker — qualquer "opponent loses life" liga o loop com as duas peças em campo).

Reforço adicional: **Ashnod's Altar/Phyrexian Altar** (seção 3) convertem o excesso de tokens de Vampiro (gerados pela Eminence do próprio Edgar Markov, seção 7) em mana ou Treasures, e cada sacrifício aciona os gatilhos de drain acima — o ramp, a geração de token e o drain não são planos separados, é um motor único.

---

## 7. Sinergia tribal (Vampiro) — Eminence do próprio comandante

**Edgar Markov** (oracle text, Scryfall): *"Eminence — Whenever you cast another Vampire spell, if Edgar is in the command zone or on the battlefield, create a 1/1 black Vampire creature token. First strike, haste. Whenever Edgar attacks, put a +1/+1 counter on each Vampire you control."*

Ponto crítico: **Eminence funciona com Edgar ainda na zona de comando** — não precisa resolver o comandante em campo pra o motor de tokens começar, só precisa conjurar vampiros. **19 criaturas do tipo Vampiro** na lista (contagem via `type_line`) alimentam isso: Bartolomé del Presidio, Blood Artist, Bloodletter of Aclazotz, Bloodthirsty Conqueror, Champion of Dusk, Charismatic Conqueror, Clavileño First of the Blessed, Cordial Vampire, Cruel Celebrant, Elenda the Dusk Rose, Indulgent Aristocrat, Nullpriest of Oblivion, Sanctum Seeker, Vein Ripper, Vindictive Vampire, Viscera Seer, Vito Fanatic of Aclazotz, Vito Thorn of the Dusk Rose, Welcoming Vampire.

**Roaming Throne** (já documentado como regra permanente em `references/goldfish-sim-card-rules.md`) escolhendo Vampiro dobraria os gatilhos "Whenever you cast another Vampire spell" da Eminence — se esse deck ganhar um simulador Python, aplicar a mesma implementação real já usada no Thranduil/Beorn, não só uma tag.

---

## 8. Win conditions

Sem 1 finisher único — o plano é: (1) o combo de drain infinito já identificado (seção 10) quando as 2 peças + qualquer habilitador se encontram; (2) atrito incremental via os 10 gatilhos de drain mesmo sem o combo montado (cada Vampiro que morre/ataca já dreno um pouco); (3) board wide de tokens de Vampiro crescendo com contadores via ataques do próprio Edgar Markov. **Skullclamp** e **The Meathook Massacre** dão outra camada — Skullclamp converte o excesso de tokens 1/1 em cartas, Meathook Massacre é wipe assimétrico que ainda dreno vida por criatura morta.

---

## 9. Game Changers — contagem oficial

Cruzamento contra `https://api.scryfall.com/cards/search?q=is:gamechanger` (53 cartas, consultado 2026-08-20):

**3 Game Changers: Smothering Tithe, Teferi's Protection, Vampiric Tutor.**

Re-verificado ao vivo em 2026-08-21 (o mesmo cruzamento, reconfirmado após uma dúvida do usuário sobre o total): continuam sendo exatamente essas 3. **Emeritus of Woe // Demonic Tutor NÃO conta** — mesmo o verso se chamando "Demonic Tutor" (que está na lista oficial de Game Changers), o objeto de carta MDFC completo (`"Emeritus of Woe // Demonic Tutor"`) não é o mesmo nome que `is:gamechanger` cataloga; confirmado diretamente via Scryfall que essa string não aparece na lista. Isso já estava certo na contagem original — nunca foi somado como 4º Game Changer nesta auditoria.

Isso está dentro do teto do Bracket 3 (até 3 permitidas). Ver seção 10 pra análise do combo de 2 peças — apesar de existir e ter habilitadores redundantes, o dado simulado (seção 10, e a política de "caçar o combo" testada à parte) mostra que ele não desqualifica o deck do critério oficial ("antes do turno 6"). Ver seção 12 pra classificação final.

---

## 10. Combo de 2 peças — encontrado, com fonte direta

Varredura de `oracle_text` identificou um combo de 2 cartas presente na lista:

- **Exquisite Blood** (texto Scryfall): *"Whenever an opponent loses life, you gain that much life."*
- **Vito, Thorn of the Dusk Rose** (texto Scryfall): *"Whenever you gain life, target opponent loses that much life."*

Com as duas em campo, qualquer perda de vida de um oponente (mesmo 1 ponto) dispara um loop: oponente perde vida → você ganha vida (Exquisite Blood) → oponente perde vida de novo (Vito) → repete. Isso drena o oponente até 0 sem limite de mana ou de turnos adicionais — é o combo clássico "Sanguine Bond/Exquisite Blood + Vito", aqui montado com Vito no lugar de Sanguine Bond.

O deck tem múltiplos gatilhos de perda de vida de oponente que poderiam iniciar o loop com as duas peças em campo: Blood Artist, Cruel Celebrant, Zulaport Cutthroat, Sanctum Seeker (todos conferidos via `oracle_text` — cada um causa "each opponent loses X life" em algum gatilho de morte/ataque).

O critério oficial de Bracket 3 (`references/commander-rules.md#brackets`, citando o texto da Wizards) exclui especificamente "combo de 2 peças **antes do turno 6**" — não a presença do combo por si só. Isso importa porque muda a conclusão desta seção (ver histórico completo na seção 12).

**Dado real, simulado (2026-08-21, `edgar_markov_goldfish_v1.py`, n=2000, 8 turnos):**

| Política | Combo ligado até T6 | Combo ligado, total em 8 turnos | Turno médio quando liga |
|---|---|---|---|
| Genérica (joga o que sai na mão) | 0,0% | 0,1% | 7,67 |
| Caçando o combo de propósito (prioriza os 2 tutores reais) | **0,0%** | 0,6% | — |

**Mesmo com o jogador priorizando ativamente os 2 tutores reais e baratos (Vampiric Tutor, Diabolic Intent) especificamente pra montar o combo, ele nunca liga antes do turno 6 em 2000 partidas simuladas.** Isso responde à pergunta que ficou em aberto na versão original desta seção ("não simulei pra saber em que turno monta") e é o dado decisivo que reverteu a classificação de Bracket 4 pra 3 (seção 12) — o combo existe e tem habilitadores redundantes, mas não desqualifica o deck pelo critério oficial de timing.

---

## 11. Outras estruturas restritas

- **Negação de terras em massa:** nenhuma encontrada na varredura de `oracle_text`.
- **Turnos extras:** nenhum efeito de turno extra encontrado.

---

## 12. Classificação de Bracket — 2ª correção, 2026-08-21 (dado simulado > estimativa teórica)

**Bracket 3 (Upgraded)**, revertendo a classificação anterior. Histórico completo das duas correções abaixo, porque cada uma foi real e vale registrar o raciocínio.

**1ª correção (mesma sessão, mais cedo):** a versão original classificou Bracket 4 pela simples presença do combo Exquisite Blood + Vito, Thorn of the Dusk Rose, ignorando que o critério oficial (`references/commander-rules.md#brackets`) é especificamente **"combo de 2 peças ANTES DO TURNO 6"**, não presença isolada. Corrigido pra Bracket 4 de novo, mas com justificativa diferente: o deck tem 2 tutores reais e baratos (Vampiric Tutor `{B}`, Diabolic Intent `{1}{B}`) que poderiam, em teoria, montar o combo já no turno 5 num cálculo manual de "melhor caso" (tutor T2 → draw T3 → Vito T3 → criatura+Diabolic Intent T4 → Exquisite Blood T5).

**2ª correção (esta seção, com simulação real):** implementei uma política de "caçar o combo" no goldfish (`edgar_markov_goldfish_v1.py`, flag `COMBO_HUNTING_POLICY`) — o jogador prioriza os 2 tutores especificamente pra achar a peça que falta, e prioriza conjurar as peças do combo assim que estão na mão, acima de qualquer outra jogada. Rodado n=2000, comparando contra a política genérica:

| Métrica | Genérica | Caçando o combo |
|---|---|---|
| 2 peças em campo até T6 | 0,1% | 2,6% |
| Combo **ligado** (gatilho de vida disparou) até T6 | 0,0% | **0,0%** |
| Combo ligado, total em 8 turnos | 0,1% | 0,6% |

**Mesmo com o jogador mirando o combo de propósito com os 2 tutores reais, a chance dele estar ligado antes do turno 6 é 0,0% em 2000 partidas.** O cálculo de "melhor caso turno 5" da 1ª correção era otimista demais — ele assumia mana certa toda hora, draws perfeitos e nenhuma outra prioridade competindo, um cenário que praticamente nunca ocorre de fato num deck de 99 cartas singleton. Verifiquei uma partida real onde as peças alinharam rápido (turno 5, log conferido manualmente) pra confirmar que a lógica de caça ao combo está certa — é só raro de acontecer, não um bug de modelagem.

**Conclusão final:** pelo critério oficial estrito ("antes do turno 6"), este deck não deveria ser excluído de Bracket 1-3 por esse combo especificamente — ele existe, tem habilitadores redundantes, e pode ser perseguido com tutores, mas na prática simulada não entrega uma vitória early game de forma confiável nem mesmo quando ativamente perseguido. Com 3 Game Changers (dentro do teto), sem mass land denial, sem turnos extras encadeados, e agora sem o combo cedo como estrutura desqualificante real — **Bracket 3** é a classificação correta pelo critério oficial. **Ressalva:** o deck ainda é um Bracket 3 forte/no teto, com qualidade de carta e um combo real (só lento) que o deixam mais perto do 4 em "sensação de poder" do que um Bracket 3 típico — mas a classificação formal segue os critérios estruturais, não a sensação.

---

## Links

- EDHREC: https://edhrec.com/commanders/edgar-markov
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
