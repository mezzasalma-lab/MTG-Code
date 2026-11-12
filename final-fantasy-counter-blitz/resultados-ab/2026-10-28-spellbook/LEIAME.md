# Commander Spellbook — `final-fantasy-counter-blitz` (2026-10-28)

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).

## Resultado

- Comandante(s): Tidus, Yuna's Guardian / Yuna, Grand Summoner; cartas lidas de `lista.md`: 100; nomes não reconhecidos pelo Spellbook: **0**.
- Combos achados: **1/1** (de 2 cartas: 0); "quase": 65/65; tag do Spellbook: **P/P**; Game Changers: Farewell.
- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **True**; de corte (com Mind Stone o combo some) = **True**.

### Combos (Tidus, Yuna's Guardian)
  - `2265-3693-6593` (3 cartas, tag S Spicy): Gatta and Luzzu + Hardened Scales + Walking Ballista → Infinite damage; Infinite +1/+1 counters on a creature

### Combos (Yuna, Grand Summoner)
  - `2265-3693-6593` (3 cartas, tag S Spicy): Gatta and Luzzu + Hardened Scales + Walking Ballista → Infinite damage; Infinite +1/+1 counters on a creature

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/spellbook_raw_final-fantasy-counter-blitz_2026-10-28.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |
| `dados/spellbook_final-fantasy-counter-blitz_2026-10-28.json` | JSON derivado das respostas (combos, "quase", `estimate-bracket`, controles) |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |

Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).

## Não feito (Regra #7)

Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.
