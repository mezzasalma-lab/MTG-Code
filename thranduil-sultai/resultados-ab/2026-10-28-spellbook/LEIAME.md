# Commander Spellbook — `thranduil-sultai` (2026-10-28)

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).

## Resultado

- Comandante(s): Thranduil, the Elvenking; cartas lidas de `lista.md`: 100; nomes não reconhecidos pelo Spellbook: **0**.
- Combos achados: **4** (de 2 cartas: 1); "quase": 98; tag do Spellbook: **R**; Game Changers: Rhystic Study.
- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **True**; de corte (com Mind Stone o combo some) = **True**.

### Combos
  - `4762-6189` (2 cartas, tag P Powerful): Devoted Druid + Tyvar, the Pummeler → Infinite green mana; Infinitely large creatures you control until end of turn
  - `2207-4613-4762` (3 cartas, tag E Exhibition): Agatha's Soul Cauldron + Devoted Druid + Immaculate Magistrate → Infinite green mana; Infinite mana creatures you control can produce; Infinite untap of creatures you control; Infinite +1/+1 counters on creatures you control
  - `3990-4613-4762` (3 cartas, tag E Exhibition): Agatha's Soul Cauldron + Devoted Druid + Incubation Druid → Infinite colored mana
  - `2207-4762-7821` (3 cartas, tag S Spicy): Devoted Druid + Immaculate Magistrate + Thranduil, the Elvenking → Infinite +1/+1 counters on creatures you control; Infinite green mana

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/spellbook_raw_thranduil-sultai_2026-10-28.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |
| `dados/spellbook_thranduil-sultai_2026-10-28.json` | JSON derivado das respostas (combos, "quase", `estimate-bracket`, controles) |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |

Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).

## Não feito (Regra #7)

Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.
