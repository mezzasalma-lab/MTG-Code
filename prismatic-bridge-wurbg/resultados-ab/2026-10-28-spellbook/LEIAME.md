# Commander Spellbook — `prismatic-bridge-wurbg` (2026-10-28)

Pedido do usuário (2026-10-28): *"Quero todos os Spellbooks sim, e salvos no repositório"*. Resumo de todos os decks: [`../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`](../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md).

## Resultado

- Comandante(s): Esika, God of the Tree // The Prismatic Bridge; cartas lidas de `lista.md`: 100; nomes não reconhecidos pelo Spellbook: **0**.
- Combos achados: **12** (de 2 cartas: 5); "quase": 92; tag do Spellbook: **R**; Game Changers: Farewell, Narset, Parter of Veils, Rhystic Study.
- Controles: positivo (Basalt Monolith + Rings of Brighthearth apareceu) = **True**; de corte (com Mind Stone o combo some) = **True**.

### Combos
  - `1529-5902` (2 cartas, tag S Spicy): Innkeeper's Talent + Vraska, Betrayal's Sting → Target opponent loses the game
  - `787-1124` (2 cartas, tag S Spicy): Teferi, Temporal Archmage + The Chain Veil → Infinite card draw; Infinite colored mana; Infinite colorless mana; Infinite planeswalker activations
  - `1124-2696` (2 cartas, tag S Spicy): Teferi, Who Slows the Sunset + The Chain Veil → Infinite activations of most planeswalkers; Infinite lifegain; Infinite lifegain triggers; Infinite mana permanents you control can produce
  - `2341-2696` (2 cartas, tag S Spicy): Teferi, Who Slows the Sunset + The Peregrine Dynamo → Infinite untap of permanents you control; Infinite lifegain; Infinite lifegain triggers; Infinite mana permanents you control can produce
  - `1529-1887` (2 cartas, tag S Spicy): Vorinclex, Monstrous Raider + Vraska, Betrayal's Sting → Target opponent loses the game
  - `193-1180-2369` (3 cartas, tag R Ruthless): Aminatou, the Fateshifter + Nicol Bolas, Dragon-God + Oath of Teferi → Exile all of your opponents' permanents and hands; Infinite card draw; Infinite creature ETB; Infinite creature LTB
  - `193-1124-1180` (3 cartas, tag R Ruthless): Aminatou, the Fateshifter + Nicol Bolas, Dragon-God + The Chain Veil → Exile all permanents opponents control; Infinite planeswalker activations; Infinite card draw; Infinite draw triggers
  - `787-1124-4450` (3 cartas, tag E Exhibition): Carth the Lion + Teferi, Temporal Archmage + The Chain Veil → Infinite card draw; Infinite colored mana; Infinite colorless mana; Infinite mana permanents you control can produce
  - `193-1543-1940-4772` (4 cartas, tag R Ruthless): Aminatou, the Fateshifter + Doubling Season + Ichormoon Gauntlet + Liliana, Dreadhorde General → Infinite turns; Lock
  - `193-1543-2984-4772` (4 cartas, tag R Ruthless): Aminatou, the Fateshifter + Doubling Season + Ichormoon Gauntlet + Ugin, the Spirit Dragon → Infinite turns; Lock
  - `193-1543-1887-1940` (4 cartas, tag R Ruthless): Aminatou, the Fateshifter + Ichormoon Gauntlet + Liliana, Dreadhorde General + Vorinclex, Monstrous Raider → Infinite turns; Lock
  - `193-1543-1887-2984` (4 cartas, tag R Ruthless): Aminatou, the Fateshifter + Ichormoon Gauntlet + Ugin, the Spirit Dragon + Vorinclex, Monstrous Raider → Infinite turns; Lock

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/spellbook_raw_prismatic-bridge-wurbg_2026-10-28.json.xz` | respostas CRUAS da API (`find-my-combos` por opção de comandante e para os 2 controles; `estimate-bracket`), com a entrada enviada |
| `dados/spellbook_prismatic-bridge-wurbg_2026-10-28.json` | JSON derivado das respostas (combos, "quase", `estimate-bracket`, controles) |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` nesta pasta |

Código: `spellbook-todos-os-decks-2026-10-28/orquestracao/csb_todos.py` (consulta) e `gera_resumo.py` (este LEIAME).

## Não feito (Regra #7)

Não conferi se o simulador deste deck executa os combos acima, não calculei a probabilidade por turno e não verifiquei o texto oficial atual de Brackets (a tag é do Spellbook, não o Bracket oficial). Detalhes em `../../../spellbook-todos-os-decks-2026-10-28/RESUMO.md`.
