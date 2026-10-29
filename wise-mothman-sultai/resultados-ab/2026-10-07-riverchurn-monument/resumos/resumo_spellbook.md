# Commander Spellbook: Riverchurn Monument no Mothman (2026-10-07)

- Nomes verificados em `GET /cards/?q=`: **91**; NAO reconhecidos: **nenhum** (incluindo `Riverchurn Monument`, `The Wise Mothman` e as duas cartas do controle positivo).
- Combos INCLUIDOS na lista atual (99 + comandante):
  - **Bloodchief Ascension + Mindcrank** — Infinite mill, Near-infinite lifegain (bracketTag `S`)
  - **Altar of Dementia + The Great Henge** — Infinite self-mill, Infinite creature ETB (bracketTag `E`)
  - 'quase incluidos' na base: 134
- **Com o Monument (sem cortar nada):** combos novos incluidos = **0**; `quase` com o Monument = **8** (cada um precisa de UMA carta que NAO esta na lista):
  - Monument + **Maddening Cacophony** → Infinite mill (tag `E`, popularidade 24648)
  - Monument + **Jidoor, Aristocratic Capital // Overture** → Infinite mill for target opponent (tag `E`, popularidade 17821)
  - Monument + **Traumatize** → Infinite mill for target opponent (tag `E`, popularidade 12561)
  - Monument + **Singularity Rupture** → Infinite mill (tag `E`, popularidade 12526)
  - Monument + **Cut Your Losses** → Infinite mill for up to two target players (tag `E`, popularidade 12165)
  - Monument + **Terisian Mindbreaker** → Infinite mill for target opponent (tag `S`, popularidade 9719)
  - Monument + **Fleet Swallower** → Infinite mill for target opponent (tag `S`, popularidade 7413)
  - Monument + **Kitsune's Technique** → Infinite mill for target opponent (tag `E`, popularidade 5214)

## Corte por corte (`Monument <- X`): o que SOME e o que APARECE

- 87 cortes consultados (toda carta nao-basica da lista, menos o comandante). Cortes que **derrubam um combo incluido**: 5
  - cortar **Altar of Dementia** derruba: Altar of Dementia + The Great Henge
  - cortar **Bloodchief Ascension** derruba: Bloodchief Ascension + Mindcrank
  - cortar **Glen Elendra Archmage** derruba: Altar of Dementia + The Great Henge
  - cortar **Mindcrank** derruba: Bloodchief Ascension + Mindcrank
  - cortar **The Great Henge** derruba: Altar of Dementia + The Great Henge
- Cortes que **adicionam** combo incluido: **0** (nenhum).

## Controles (a API ignora, sem erro, nome nao reconhecido: resultado vazio sem controle e' vacuo)

- **Controle positivo** (Negate+Swiftfoot Boots → Thassa's Oracle+Demonic Consultation): combo apareceu = **True**.
- **Controle de corte** (Mindcrank → Evolution Sage): a base tem Ascension+Mindcrank = **True**; sumiu ao cortar = **True**.
