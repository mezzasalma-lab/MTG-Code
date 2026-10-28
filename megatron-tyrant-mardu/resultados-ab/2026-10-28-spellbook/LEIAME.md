# Commander Spellbook — `megatron-tyrant-mardu` (2026-10-28)

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).

## Resultado

- Comandante(s): Megatron, Tyrant; cartas lidas de `lista.md`: 100; nomes não reconhecidos pelo Spellbook: **0**.
- Combos achados: **2** (de 2 cartas: 1); "quase": 27; tag do Spellbook: **R**; Game Changers: nenhum.
- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **True**; de corte (com Mind Stone o combo some) = **True**.

### Combos
  - `1571-2560` (2 cartas, tag R Ruthless): Blightsteel Colossus + Chandra's Ignition → Each opponent loses the game
  - `3169-5291-6250` (3 cartas, tag E Exhibition): Cursed Mirror + Daretti, Rocketeer Engineer + Genesis Chamber → Infinite artifact ETB; Infinite artifact LTB; Infinite artifact sacrifice triggers; Infinite creature LTB

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/spellbook_raw_megatron-tyrant-mardu_2026-10-28.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |
| `dados/spellbook_megatron-tyrant-mardu_2026-10-28.json` | JSON derivado das respostas (combos, "quase", `estimate-bracket`, controles) |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |

Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).

## Não feito (Regra #7)

Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.
