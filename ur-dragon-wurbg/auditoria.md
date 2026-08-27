# Auditoria — The Ur-Dragon (5 cores — WUBRG)

Fontes usadas nesta auditoria: Scryfall REST API (`cards/collection`, `cards/search?q=is:gamechanger`, campos `legalities.commander`, `color_identity`, `oracle_text`, `type_line`, `cmc`), consultada em 2026-08-20. Definições de Bracket: `references/commander-rules.md#brackets` do skill mtg-commander (fonte primária: anúncios oficiais da Wizards).
Data da auditoria: 2026-08-20

---

## 1. Validação formal

| Check | Resultado | Fonte |
|---|---|---|
| Total de cartas | 100 (99 + comandante) | contagem das linhas coladas |
| Singleton | Sem duplicatas | `uniq -d` sobre os nomes |
| Identidade de cor (5 cores) | Sem violação | `color_identity` |
| Cartas banidas em Commander | Nenhuma | `legalities.commander` |

**Comandante:** The Ur-Dragon — `{4}{W}{U}{B}{R}{G}` — Legendary Creature Dragon Avatar.

---

## 2. Terrenos e curva

- Terrenos: **36** (`type_line`).
- CMC médio, não-terrenos, sem comandante: **3.9** (`cmc`).

> **Atualização (2026-08-27) — auditoria de pips real:** contagem
> carta a carta dos pips coloridos de todo o deck (79→96 pips
> corrigidos conforme recontagem) mostrou vermelho em **42,7% de toda a
> demanda de pips** do deck, mas só **19,8% das fontes de mana** (gap de
> +23,0pp — o maior desequilíbrio já medido em qualquer deck desta
> biblioteca). Verde também sub-representado (+5,5pp), branco moderado
> (+7,0 a +8,6pp), preto e azul sobre-representados (-10,4pp e -11,2pp).
> Confirmado de forma independente pelo Commander Template (ferramenta
> externa, "ADD 8 RED SOURCES") e por uma métrica nova no simulador
> (`color_screw_turns`): **38-41% das partidas têm pelo menos 1 turno
> com mana total suficiente mas a cor errada**, começando em média já
> no turno ~3,7-3,9. Duas trocas aplicadas por causa disso — ver
> `goldfish-log.md` Teste #2/Correção #5: Watery Grave → Karplusan
> Forest (R/G) e Island → Battlefield Forge (R/W), ambas testadas em
> pares de seed antes de aplicar, efeito real mas parcial (não fecha o
> gap de +23pp sozinho).

> **Atualização (2026-08-27) — recontagem pós-trocas + fixação
> restrita a tipo de criatura:** com as 2 trocas de terreno aplicadas, o
> gap de vermelho caiu pra **+20,0pp** (25 fontes/22,7% vs. 42,7% de
> demanda). Usuário apontou um segundo erro conceitual: Cavern of Souls,
> Secluded Courtyard e Haven of the Spirit Dragon produzem mana de
> qualquer cor pra criatura do tipo escolhido/fixo (Dragão nesse deck),
> e eu tinha as 3 tratadas como incolores no simulador. Corrigido —
> contam agora como fonte real de qualquer cor especificamente pra
> conjurar Dragões (21 criaturas, 49% de todos os pips do deck, 70,7%
> da demanda de vermelho). Fontes de vermelho pra conjurar um Dragão
> especificamente: **28**, não 25 — 3 a mais do que a fixação "geral" do
> deck sugere. Impacto real medido (mesma seed, só o fix): nunca
> conjurada -2,5pp, color screw -3,3pp, dano proxy médio +18%. Ver
> `goldfish-log.md` Correção #10 e Regra 6 de
> `references/user-standing-rules.md` (adendo). O gap de +20pp segue
> real pro caso geral (removal, ramp, artifacts não-Dragão continuam sem
> se beneficiar dessas 3 terras) — só não é tão ruim quanto parecia
> especificamente pra conjurar as próprias ameaças do deck.

> **Atualização (2026-08-27) — correção de metodologia (Regra 8):**
> usuário apontou que somar todos os pips do deck inteiro como "demanda"
> superestima a pressão real — não considera que a maioria dos Dragões
> em campo nunca teve pip pago (token, reanimação, tutor, habilidade da
> própria Ur-Dragon), nem que o que É conjurado está espalhado ao longo
> de vários turnos. Medido de verdade: de ~7,85 Dragões em campo no fim
> de uma partida de 8 turnos, só **44,6% (3,50) foram realmente
> conjurados pagando mana** — 48,2% eram tokens (Lathliss/Miirym/
> Broodmother/Utvara), 7,2% entraram de graça (Bladewing/Haunting
> Voyage/Magda/permanente grátis da Ur-Dragon). Isso dá **0,44 Dragões
> conjurados por turno em média** — nunca "3 Dragões de pip vermelho no
> mesmo turno" como cenário típico. A tabela de pips agregados acima
> segue útil como triagem inicial de desequilíbrio de cor, mas a métrica
> correta de necessidade real é `color_screw_turns`/
> `first_color_screw_turn` (turno-a-turno, simulado de verdade): 34,5%
> dos jogos têm pelo menos 1 turno real de screw, turno médio do
> primeiro ~3,5. Ver `goldfish-log.md` Correção #11 e Regra 8 de
> `references/user-standing-rules.md`. No caminho, 3 bugs reais achados
> e corrigidos (Haunting Voyage nunca implementada; Utvara Hellkite e
> Old Gnawbone com gatilho auto-referente errado — ambos reagem a
> QUALQUER Dragão/criatura, não só a si mesmos) — dano proxy médio subiu
> 59% (57,03→90,79) só com esses fixes, sem trocar carta nenhuma.

> **Atualização (2026-08-27) — revisão completa do deck e do
> simulador:** usuário pediu revisão de tudo que estivesse "de fora ou
> errado". Auditadas as 47 tags únicas usadas no CARD_DB (68 cartas) e
> as 63 cartas não-terrestres contra o oráculo real completo. Achados e
> corrigidos: Klauth (usava só o próprio poder, não o poder total dos
> atacantes), Ramos (contador flat em vez de por-cor), Twinflame Tyrant
> (dobrador global de dano nunca implementado — afeta diretamente o
> `proxy_damage_total`), Atarka (double strike nunca implementado), The
> Great Henge (habilidade de mana {T}: Add GG nunca registrada), Garruk's
> Uprising (faltava a compra única de ETB), Up the Beanstalk e Sylvan
> Library (100% decorativas, nunca implementadas), Rhythm of the Wild
> (riot/haste nunca implementado), e um crash real (Haunting Voyage ×
> Bladewing the Risen reanimando o mesmo alvo — achado nos 30k jogos de
> robustez). 6 itens documentados como deferidos com razão explícita
> (Hellkite Charger extra combat, Sarkhan cópia, Return of the
> Wildspeaker non-Human, Haven of the Spirit Dragon reanimação, pumps
> ativados de Bladewing/Scourge). **Impacto acumulado, mesma
> seed_base=7600000:** dano proxy médio 90,79→**436,51** (+381%),
> Dragões em campo 8,08→**11,82**, nunca conjurada 48,1%→**41,4%**. O
> motor real do deck é substancialmente mais forte do que qualquer
> número reportado nesta sessão até aqui — efeito bola de neve de
> multiplicadores (Twinflame Tyrant, Atarka) empilhando sobre motores de
> mana/Treasure já corrigidos, não inflação artificial. Ver
> `goldfish-log.md` Correção #12 pra lista completa e detalhes de cada
> item.

> **Atualização (2026-08-27) — 3 achados reais adicionais (usuário
> insistiu, com razão):** (1) nenhum terreno jamais entrava tapped no
> simulador — corrigido pros 4 Triomes, que têm "enters tapped"
> incondicional (os 8 choques continuam sempre destravados, premissa de
> "sempre paga vida" agora documentada); Cavern of Souls/Secluded
> Courtyard/Haven of the Spirit Dragon (as terras "tribais" de verdade)
> foram reverificadas e confirmadas corretas. (2) Haunting Voyage: modo
> foretold ("return ALL", não só até 2) implementado de verdade — tinha
> sido descartado por escopo na Correção #11, correção justa do usuário
> de que isso é esquecer a carta, não simplificar. (3) Crux of Fate não
> é simétrico (escolhe Dragão vs. não-Dragão, favorável pro deck) — e
> investigando isso achei que as 10 cartas 'interaction' (remoção/
> proteção) tinham o mesmo bug: a IA gulosa conjurava sem alvo real,
> desperdiçando mana. Corrigido excluindo 'interaction'/'wipe' do
> auto-cast. Impacto líquido combinado: nunca conjurada 41,4%→**39,8%**,
> color screw 33,1%→**35,1%** (Triomes tapped são custo real), dano
> proxy 436,51→396,75. Ver `goldfish-log.md` Correção #13.

---

## 3. Game Changers — contagem oficial

Cruzamento contra `https://api.scryfall.com/cards/search?q=is:gamechanger` (53 cartas, consultado 2026-08-20):

**3 Game Changers: Ancient Tomb, Smothering Tithe, Teferi's Protection.**

Teto exato do Bracket 3.

---

## 4. Estruturas restritas pelo sistema de Brackets

Varredura de `oracle_text` das 100 cartas.

- **Negação de terras em massa:** nenhuma encontrada.
- **Turnos extras:** nenhum efeito de turno extra encontrado no texto de nenhuma carta.
- **Combate adicional:** encontrado em **Hellkite Charger** — texto (Scryfall): *"Whenever this creature attacks, you may pay {5}{R}{R}. If you do, untap all attacking creatures and after this phase, there is an additional combat phase."* Isso é combate adicional, não turno extra — o critério oficial que separa Bracket 2/3 de Bracket 4 fala especificamente de "turnos extras encadeados", não de fases de combate adicionais. Não reclassifico o deck por causa disso, só registro que existe.
- **Combo de 2 peças:** não identifiquei via varredura de texto na auditoria original. Não era prova de ausência — e de fato existiam.

> **Atualização (2026-08-27) — Commander Spellbook:** consultei a API
> real (`backend.commanderspellbook.com/find-my-combos`) com a lista
> completa. Achou **3 combinações reais já montadas com cartas desta
> lista**: Old Gnawbone + Hellkite Charger (infinito de verdade — fases
> de combate/Treasure/dano infinitos), Miirym + Bladewing the Risen +
> Terror of the Peaks (infinito de verdade — ETB/dano infinitos), e
> Dragon Tempest + Ancient Gold Dragon (dano quase-infinito). **Mas
> calculei a probabilidade hipergeométrica real de montar cada uma até
> um turno de referência (Regra 7 de `user-standing-rules.md`,
> estabelecida por causa deste caso) — sem tutor que busque as peças
> especificamente, a chance de ter as 2 cartas do combo mais provável
> na mão até o turno 8 é só 1,9%, e 0,23% pro de 3 cartas.** Não é um
> combo turno 3-4, é um evento de cauda que não muda a classificação de
> Bracket na prática (ver critério oficial: precisa ser rápido E
> provável, não só existir). Registrado aqui como curiosidade de fim de
> jogo pro grupo saber, não como wincon planejado.

---

## 5. Classificação de Bracket

**Bracket 3 (Upgraded), no teto de Game Changers (3 de 3).**

Base: 3 Game Changers, sem negação de terras em massa, sem turno extra, sem combo de 2 peças identificado na varredura de texto que fiz. Hellkite Charger dá combate adicional pago (não turno extra), o que não é um dos três critérios de exclusão listados no texto oficial que tenho registrado.

---

## Links

- EDHREC: https://edhrec.com/commanders/the-ur-dragon
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
