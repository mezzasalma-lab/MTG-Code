# Commander Spellbook — `maralen-sultai` (2026-10-28)

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).

## Resultado

- Comandante(s): Maralen, Fae Ascendant; cartas lidas de `lista.md`: 100; nomes não reconhecidos pelo Spellbook: **0**.
- Combos achados: **9** (de 2 cartas: 9); "quase": 95; tag do Spellbook: **S**; Game Changers: Cyclonic Rift, Rhystic Study, Seedborn Muse.
- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **True**; de corte (com Mind Stone o combo some) = **True**.

### Combos
  - `2645-5168` (2 cartas, tag S Spicy): Bloom Tender + Staff of Domination → Infinite lifegain triggers; Infinite lifegain; Infinite card draw; Infinite untap of creatures you control
  - `1526-2645` (2 cartas, tag S Spicy): Circle of Dreams Druid + Staff of Domination → Infinite card draw; Infinite draw triggers; Infinite lifegain; Infinite lifegain triggers
  - `1526-2816` (2 cartas, tag S Spicy): Circle of Dreams Druid + Umbral Mantle → Infinite green mana; Infinitely large creature until end of turn; Infinite untap of creatures you control; Infinite mana creatures you control can produce
  - `2645-3151` (2 cartas, tag S Spicy): Elvish Archdruid + Staff of Domination → Infinite card draw; Infinite draw triggers; Infinite lifegain; Infinite lifegain triggers
  - `2816-3151` (2 cartas, tag S Spicy): Elvish Archdruid + Umbral Mantle → Infinite green mana; Infinitely large creature until end of turn; Infinite untap of creatures you control; Infinite mana creatures you control can produce
  - `2436-2645` (2 cartas, tag S Spicy): Marwyn, the Nurturer + Staff of Domination → Infinite card draw; Infinite draw triggers; Infinite lifegain; Infinite lifegain triggers
  - `2436-2816` (2 cartas, tag S Spicy): Marwyn, the Nurturer + Umbral Mantle → Infinite green mana; Infinitely large creature until end of turn; Infinite untap of creatures you control; Infinite mana creatures you control can produce
  - `1376-2645` (2 cartas, tag S Spicy): Priest of Titania + Staff of Domination → Infinite card draw; Infinite draw triggers; Infinite lifegain; Infinite lifegain triggers
  - `1376-2816` (2 cartas, tag S Spicy): Priest of Titania + Umbral Mantle → Infinite green mana; Infinitely large creature until end of turn; Infinite untap of creatures you control; Infinite mana creatures you control can produce

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/spellbook_raw_maralen-sultai_2026-10-28.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |
| `dados/spellbook_maralen-sultai_2026-10-28.json` | JSON derivado das respostas (combos, "quase", `estimate-bracket`, controles) |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |

Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).

## Não feito (Regra #7)

Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.
