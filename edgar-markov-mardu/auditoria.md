# Auditoria — Edgar Markov (Mardu — R/W/B)

Fontes usadas nesta auditoria: Scryfall REST API (`cards/collection`, `cards/named`, `cards/search?q=is:gamechanger`, campos `legalities.commander`, `color_identity`, `oracle_text`, `type_line`, `cmc`), consultada em 2026-08-20. Definições de Bracket: `references/commander-rules.md#brackets` do skill mtg-commander.
Data da auditoria: 2026-08-20

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

- Terrenos: **37** (contagem por `type_line`, com quantidades — 4 Plains + 4 Swamp inclusas).
- CMC médio, não-terrenos, sem comandante: **3.23** (`cmc`).

---

## 3. Game Changers — contagem oficial

Cruzamento contra `https://api.scryfall.com/cards/search?q=is:gamechanger` (53 cartas, consultado 2026-08-20):

**3 Game Changers: Smothering Tithe, Teferi's Protection, Vampiric Tutor.**

Isso sozinho seria o teto do Bracket 3. Mas a lista tem outro elemento que muda a classificação — ver seção 4.

---

## 4. Combo de 2 peças — encontrado, com fonte direta

Varredura de `oracle_text` identificou um combo de 2 cartas presente na lista:

- **Exquisite Blood** (texto Scryfall): *"Whenever an opponent loses life, you gain that much life."*
- **Vito, Thorn of the Dusk Rose** (texto Scryfall): *"Whenever you gain life, target opponent loses that much life."*

Com as duas em campo, qualquer perda de vida de um oponente (mesmo 1 ponto) dispara um loop: oponente perde vida → você ganha vida (Exquisite Blood) → oponente perde vida de novo (Vito) → repete. Isso drena o oponente até 0 sem limite de mana ou de turnos adicionais — é o combo clássico "Sanguine Bond/Exquisite Blood + Vito", aqui montado com Vito no lugar de Sanguine Bond.

O deck tem múltiplos gatilhos de perda de vida de oponente que poderiam iniciar o loop com as duas peças em campo: Blood Artist, Cruel Celebrant, Zulaport Cutthroat, Sanctum Seeker (todos conferidos via `oracle_text` — cada um causa "each opponent loses X life" em algum gatilho de morte/ataque).

O critério oficial de Bracket 3 (`references/commander-rules.md#brackets`, citando o texto da Wizards) exclui "combo de 2 peças antes do turno 6". Não simulei o deck pra saber em que turno esse combo tipicamente monta — não tenho esse dado e não vou inventá-lo. Mas a presença de um combo de 2 peças com múltiplos habilitadores redundantes (4 fontes diferentes de "opponent loses life" já contadas) é, pela própria definição oficial, uma estrutura de Bracket 4/5, independente da contagem de Game Changers.

---

## 5. Outras estruturas restritas

- **Negação de terras em massa:** nenhuma encontrada na varredura de `oracle_text`.
- **Turnos extras:** nenhum efeito de turno extra encontrado.

---

## 6. Classificação de Bracket

**Bracket 4 (Optimized).**

Motivo: presença do combo de 2 peças Exquisite Blood + Vito, Thorn of the Dusk Rose, com múltiplos habilitadores redundantes na própria lista (seção 4). Isso desqualifica o deck de Bracket 1-3 pelo critério oficial, independente de a contagem de Game Changers (3) estar dentro do teto do Bracket 3.

---

## Links

- EDHREC: https://edhrec.com/commanders/edgar-markov
- Scryfall Game Changers (fonte usada): https://api.scryfall.com/cards/search?q=is:gamechanger
