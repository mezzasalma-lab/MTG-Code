# Commander Spellbook — `ur-dragon-wurbg` (2026-10-28)

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).

## Resultado

- Comandante(s): The Ur-Dragon; cartas lidas de `lista.md`: 100; nomes não reconhecidos pelo Spellbook: **0**.
- Combos achados: **3** (de 2 cartas: 2); "quase": 148; tag do Spellbook: **S**; Game Changers: Ancient Tomb, Smothering Tithe, Teferi's Protection.
- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **True**; de corte (com Mind Stone o combo some) = **True**.

### Combos
  - `2855-5982` (2 cartas, tag S Spicy): Ancient Gold Dragon + Dragon Tempest → Near-infinite damage
  - `1800-3398` (2 cartas, tag O Oddball): Hellkite Charger + Old Gnawbone → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite artifact tokens
  - `380-1110-3362` (3 cartas, tag O Oddball): Bladewing the Risen + Miirym, Sentinel Wyrm + Terror of the Peaks → Infinite creature LTB; Infinite creature ETB; Infinite death triggers; Infinite damage

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/spellbook_raw_ur-dragon-wurbg_2026-10-28.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |
| `dados/spellbook_ur-dragon-wurbg_2026-10-28.json` | JSON derivado das respostas (combos, "quase", `estimate-bracket`, controles) |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |

Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).

## Não feito (Regra #7)

Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.
