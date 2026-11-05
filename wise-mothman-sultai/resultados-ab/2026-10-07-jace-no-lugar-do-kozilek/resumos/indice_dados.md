| arquivo | conteúdo |
|---|---|
| `final.done` | sinal de fim do lançador |
| `jace_scryfall.json` | resposta bruta de API (Scryfall / Commander Spellbook); chaves: card, rulings, search_prints |
| `raw_final_1_10000.json.xz` | bruto por partida: 6 variantes (`base`, `kozilek_por_jace`, `kozilek_por_jace_so_motor`, `kozilek_por_jace_remocao_20`, `kozilek_por_jace_remocao_50`, `kozilek_por_forest`) × N=10000; 245 campos numéricos (todos os do estado final, incl. `jace_*`) |
| `raw_final_1_10000_resiliencia.json.xz` | bruto por partida: 6 variantes (`base`, `kozilek_por_jace`, `kozilek_por_jace_so_motor`, `kozilek_por_jace_remocao_20`, `kozilek_por_jace_remocao_50`, `kozilek_por_forest`) × N=10000; 245 campos numéricos (todos os do estado final, incl. `jace_*`) |
| `raw_final_2_10000.json.xz` | bruto por partida: 7 variantes (`base`, `offer_por_jace`, `negate_por_jace`, `selkie_por_jace`, `deluge_por_jace`, `arcane_denial_por_jace`, `negate_por_jace_remocao_33`) × N=10000; 245 campos numéricos (todos os do estado final, incl. `jace_*`) |
| `raw_final_2_10000_resiliencia.json.xz` | bruto por partida: 7 variantes (`base`, `offer_por_jace`, `negate_por_jace`, `selkie_por_jace`, `deluge_por_jace`, `arcane_denial_por_jace`, `negate_por_jace_remocao_33`) × N=10000; 245 campos numéricos (todos os do estado final, incl. `jace_*`) |
| `spellbook_jace.json` | resposta bruta de API (Scryfall / Commander Spellbook); chaves: reconhece, nao_reconhecidos, base, monument_por_corte, monument_sem_cortar, controle_positivo, controle_corte |
| `validacao.done` | sinal de fim do lançador |
