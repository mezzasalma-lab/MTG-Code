# Auditoria — Esika, God of the Tree // The Prismatic Bridge (5 cores — WUBRG)

Fontes usadas nesta auditoria: Scryfall REST API (`cards/collection`, `cards/named`, `cards/search?q=is:gamechanger`, campos `legalities.commander`, `color_identity`, `oracle_text`, `type_line`, `cmc`), consultada em 2026-08-20. Definições de Bracket: anúncios oficiais da Wizards ("Introducing Commander Brackets Beta", atualização de outubro/2025) já registrados em `references/commander-rules.md` do skill mtg-commander.
Data da auditoria: 2026-08-20

---

## 1. Validação formal

| Check | Resultado | Fonte |
|---|---|---|
| Total de cartas | 100 (99 + comandante) | contagem das linhas coladas pelo usuário |
| Singleton | Sem duplicatas | `uniq -d` sobre os nomes |
| Identidade de cor (5 cores) | Sem violação | `color_identity` de cada carta vs. do comandante |
| Cartas banidas em Commander | Nenhuma | `legalities.commander` |

**Comandante:** Esika, God of the Tree // The Prismatic Bridge — MDFC. Frente: Legendary Creature — God (custo não informado no Scryfall pro lado frente desse card, comum em cards de dupla face com custo só na segunda face). Verso: Legendary Enchantment.

---

## 2. Terrenos e curva

- Terrenos: **37** (contagem por `type_line` contendo "Land" e não contendo "Creature").
- CMC médio, não-terrenos, sem comandante: **3.66** (campo `cmc` do Scryfall).

Não tenho dado de EDHREC ou de goldfish pra esse deck ainda — não vou estimar "se isso é bom ou ruim pro plano" sem essa referência.

---

## 3. Game Changers — contagem oficial

Cruzamento carta a carta contra a lista de 53 Game Changers obtida via `https://api.scryfall.com/cards/search?q=is:gamechanger` em 2026-08-20:

**3 Game Changers: Farewell, Narset Parter of Veils, Rhystic Study.**

Isso é exatamente o teto do Bracket 3 (até 3 Game Changers, por `references/commander-rules.md#brackets`).

---

## 4. Estruturas restritas pelo sistema de Brackets

Varredura de `oracle_text` de todas as 100 cartas procurando por combo de 2 peças, negação de terras em massa, e turnos extras.

- **Negação de terras em massa:** não encontrado nenhum efeito do tipo "destroy all lands"/"sacrifice all lands" no texto de nenhuma carta.
- **Turnos extras:** encontrado em **Ichormoon Gauntlet** — texto (Scryfall): *"Planeswalkers you control have '[0]: Proliferate' and '[−12]: Take an extra turn after this one.'"* — habilidade de turno extra condicionada a um planeswalker equipado chegar a -12 de lealdade. Não é um efeito "livre"/repetível de turno extra por si só, mas é uma fonte real de turno extra presente na lista. Com o pacote de proliferate do deck (Inexorable Tide, Deepglow Skate, Evolution Sage — todos conferidos por `oracle_text`), a lealdade pode subir mais rápido que o normal.
- **Combo de 2 peças:** não identifiquei nenhum via varredura de texto (procurei por padrões de untap/copy livre e "infinite"-adjacentes nas 100 cartas). Isso não é uma prova formal de ausência de combo — só que não achei um usando os padrões de busca que apliquei.

---

## 5. Classificação de Bracket

**Bracket 3 (Upgraded), no teto de Game Changers (3 de 3).**

Base: 3 Game Changers (item 3), sem negação de terras em massa, sem combo de 2 peças identificado. O Ichormoon Gauntlet dá acesso a turno extra, mas não da forma "encadiada" que o texto oficial da Wizards usa como critério de exclusão de Bracket 3 (fonte: `references/commander-rules.md#brackets`, que reproduz o texto oficial "turnos extras... não encadeado" pra Bracket 3) — é uma ultimate de planeswalker específico, não um motor repetível independente.

Não tenho base suficiente pra afirmar mais que isso sem simular o deck ou ver decklists de referência — não vou especular sobre "quão forte" ele joga além do que os critérios formais permitem concluir.

---

## Links

- EDHREC: https://edhrec.com/commanders/esika-god-of-the-tree
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
