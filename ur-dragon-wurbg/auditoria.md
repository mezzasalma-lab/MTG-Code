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
- **Combo de 2 peças:** não identifiquei via varredura de texto. Não é prova de ausência — só não achei com os padrões que busquei (untap livre, copy livre, "infinite"-adjacentes).

---

## 5. Classificação de Bracket

**Bracket 3 (Upgraded), no teto de Game Changers (3 de 3).**

Base: 3 Game Changers, sem negação de terras em massa, sem turno extra, sem combo de 2 peças identificado na varredura de texto que fiz. Hellkite Charger dá combate adicional pago (não turno extra), o que não é um dos três critérios de exclusão listados no texto oficial que tenho registrado.

---

## Links

- EDHREC: https://edhrec.com/commanders/the-ur-dragon
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
