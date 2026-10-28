# Commander Spellbook — `vihaan-goldwaker-mardu` (2026-10-28)

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).

## Resultado

- Comandante(s): Vihaan, Goldwaker; cartas lidas de `lista.md`: 100; nomes não reconhecidos pelo Spellbook: **0**.
- Combos achados: **4** (de 2 cartas: 0); "quase": 98; tag do Spellbook: **P**; Game Changers: Smothering Tithe, Teferi's Protection.
- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **True**; de corte (com Mind Stone o combo some) = **True**.

### Combos
  - `1308-4682-7890` (3 cartas, tag P Powerful): Anointed Procession + Gleaming Splendor + Smothering Tithe → Infinite card draw for any number of players; Infinite draw triggers for any number of players; Near-infinite Treasure tokens; Near-infinite colored mana
  - `865-2034-2429` (3 cartas, tag E Exhibition): Ashnod's Altar + Mahadi, Emporium Master + Revel in Riches → Win the game at the beginning of your next upkeep
  - `3809-4682-7890` (3 cartas, tag P Powerful): Gleaming Splendor + Goldspan Dragon + Smothering Tithe → Infinite card draw for any number of players; Infinite draw triggers for any number of players; Near-infinite Treasure tokens; Near-infinite colored mana
  - `4682-5184-7890` (3 cartas, tag P Powerful): Gleaming Splendor + Smothering Tithe + Xorn → Infinite card draw for any number of players; Infinite draw triggers for any number of players; Near-infinite Treasure tokens; Near-infinite colored mana

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/spellbook_raw_vihaan-goldwaker-mardu_2026-10-28.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |
| `dados/spellbook_vihaan-goldwaker-mardu_2026-10-28.json` | JSON derivado das respostas (combos, "quase", `estimate-bracket`, controles) |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |

Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).

## Não feito (Regra #7)

Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.
