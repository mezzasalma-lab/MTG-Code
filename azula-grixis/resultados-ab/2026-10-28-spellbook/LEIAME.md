# Commander Spellbook — `azula-grixis` (2026-10-28)

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).

## Resultado

- Comandante(s): Fire Lord Azula; cartas lidas de `lista.md`: 100; nomes não reconhecidos pelo Spellbook: **0**.
- Combos achados: **4** (de 2 cartas: 1); "quase": 73; tag do Spellbook: **R**; Game Changers: nenhum.
- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **True**; de corte (com Mind Stone o combo some) = **True**.

### Combos
  - `11-3368` (2 cartas, tag E Exhibition): Narset's Reversal + Reiterate → Infinite magecraft triggers
  - `11-2196-7089` (3 cartas, tag S Spicy): Fire Lord Azula + Frantic Search + Narset's Reversal → Infinite self-discard triggers; Infinite draw triggers; Infinite looting; Near-infinite storm count
  - `11-5195-7089` (3 cartas, tag S Spicy): Fire Lord Azula + Narset's Reversal + Storm-Kiln Artist → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite artifact tokens
  - `3368-4036-5195` (3 cartas, tag E Exhibition): Reiterate + Seething Song + Storm-Kiln Artist → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite artifact tokens

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/spellbook_raw_azula-grixis_2026-10-28.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |
| `dados/spellbook_azula-grixis_2026-10-28.json` | JSON derivado das respostas (combos, "quase", `estimate-bracket`, controles) |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |

Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).

## Não feito (Regra #7)

Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.
