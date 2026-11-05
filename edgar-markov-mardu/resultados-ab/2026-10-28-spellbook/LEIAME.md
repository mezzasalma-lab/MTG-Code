# Commander Spellbook — `edgar-markov-mardu` (2026-10-28)

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).

## Resultado

- Comandante(s): Edgar Markov; cartas lidas de `lista.md`: 100; nomes não reconhecidos pelo Spellbook: **0**.
- Combos achados: **4** (de 2 cartas: 4); "quase": 183; tag do Spellbook: **S**; Game Changers: Smothering Tithe, Teferi's Protection, Vampiric Tutor.
- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **True**; de corte (com Mind Stone o combo some) = **True**.

### Combos
  - `5755-6191` (2 cartas, tag S Spicy): Bloodthirsty Conqueror + Enduring Tenacity → Infinite lifegain triggers; Infinite lifeloss; Infinite lifegain
  - `314-6191` (2 cartas, tag S Spicy): Bloodthirsty Conqueror + Vito, Thorn of the Dusk Rose → Infinite lifegain triggers; Infinite lifeloss; Infinite lifegain
  - `3966-5755` (2 cartas, tag S Spicy): Enduring Tenacity + Exquisite Blood → Infinite lifegain triggers; Infinite lifeloss; Infinite lifegain
  - `314-3966` (2 cartas, tag S Spicy): Exquisite Blood + Vito, Thorn of the Dusk Rose → Infinite lifegain triggers; Infinite lifeloss; Infinite lifegain

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/spellbook_raw_edgar-markov-mardu_2026-10-28.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |
| `dados/spellbook_edgar-markov-mardu_2026-10-28.json` | JSON derivado das respostas (combos, "quase", `estimate-bracket`, controles) |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |

Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).

## Não feito (Regra #7)

Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.
