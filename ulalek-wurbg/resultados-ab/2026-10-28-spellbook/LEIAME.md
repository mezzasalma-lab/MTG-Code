# Commander Spellbook — `ulalek-wurbg` (2026-10-28)

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).

## Resultado

- Comandante(s): Ulalek, Fused Atrocity; cartas lidas de `lista.md`: 100; nomes não reconhecidos pelo Spellbook: **0**.
- Combos achados: **5** (de 2 cartas: 0); "quase": 58; tag do Spellbook: **R**; Game Changers: Ancient Tomb, Rhystic Study, The One Ring.
- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **True**; de corte (com Mind Stone o combo some) = **True**.

### Combos
  - `5642-5657-5705` (3 cartas, tag E Exhibition): Echoes of Eternity + Glaring Fleshraker + Ulalek, Fused Atrocity → Infinite creature LTB; Infinite creature ETB; Infinite creature sacrifice triggers; Infinite death triggers
  - `5637-5642-5657--34` (3 cartas, tag E Exhibition): Echoes of Eternity + Kozilek's Unsealing + Ulalek, Fused Atrocity → Infinite colorless mana; Infinite copies of abilities you control on the stack; Infinite copies of a specific creature; Infinite creature tokens
  - `5642-5657-5664` (3 cartas, tag S Spicy): Echoes of Eternity + Ulalek, Fused Atrocity + Writhing Chrysalis → Infinite copies of abilities you control on the stack; Infinite creature tokens; Infinite death triggers; Infinite creature ETB
  - `5657-5664-7116` (3 cartas, tag O Oddball): Eldritch Immunity + Ulalek, Fused Atrocity + Writhing Chrysalis → Infinite creature LTB; Infinite creature ETB; Infinite creature sacrifice triggers; Infinite death triggers
  - `5334-5657-5705` (3 cartas, tag E Exhibition): Glaring Fleshraker + Roaming Throne + Ulalek, Fused Atrocity → Infinite creature LTB; Infinite creature ETB; Infinite creature sacrifice triggers; Infinite death triggers

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/spellbook_raw_ulalek-wurbg_2026-10-28.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |
| `dados/spellbook_ulalek-wurbg_2026-10-28.json` | JSON derivado das respostas (combos, "quase", `estimate-bracket`, controles) |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |

Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).

## Não feito (Regra #7)

Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.
