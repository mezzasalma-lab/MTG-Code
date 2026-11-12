# Thranduil: lista física, atualização de 2026-10-23

Pedido do usuário: *"O deck do Thranduil faltam as seguintes cartas:"* Beast Whisperer; Devoted Druid; Maralen, Fae Ascendant; Buried Alive; Deadly Rollick; Awaken the Honored Dead.
- `scryfall_faltantes.json`: resposta crua do Scryfall (`/cards/named?exact=`, 2026-10-23) para as 6 cartas: nome, custo, tipo, oráculo, preço (`usd`, `usd_foil`, `eur`), legalidade em Commander, `flavor_name` (nenhuma tem; Regra #2).
- `confere.py` → `confere.txt`: recalcula a lista física (`lista.md` menos as 6) e compara com o bloco "Lista física atual" de `../../lista-fisica.md`; deve imprimir `OK` (94 de 100).
- **Escopo (Regra #7):** isto registra o que está em mãos (palavra do usuário); não audita as cláusulas dessas 6 cartas no simulador (elas aparecem nele, mas não foram reconferidas contra o oráculo agora) e não avalia trocas (nenhuma foi pedida). Preços são os do Scryfall, não cotação de loja.
