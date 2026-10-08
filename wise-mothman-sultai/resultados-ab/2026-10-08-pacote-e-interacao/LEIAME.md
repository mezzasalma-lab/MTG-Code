# 2026-10-08 — pacote Horrigan + Branching Evolution, qual interação cortar, remoções (Drown in the Loch, Atomize...)

Pedido do usuário (2026-10-08): *"Ainda não fizemos nenhuma mudança no deck, o que vc me sugere? Abrir mão de interação por Remoção?"*

**STATUS: EM ANDAMENTO.** O worker reiniciou uma vez (2026-10-08 ~00:40 UTC) e derrubou o 1º lote; o driver desta pasta foi tornado retomável por variante (`dados/raw_pacote_10000[_resiliencia]_parcial.json.xz`). Quando `dados/pacote.done` e `dados/gy.done` existirem, as tabelas saem de `orquestracao/rank_pacote.py` e esta página é completada (SHA256SUMS, cmp, tabela → comando).

## O que já está nesta pasta e sustenta a resposta dada ao usuário
| arquivo | o que é | status |
|---|---|---|
| `dados/spellbook_pacote.json`, `resumos/log_spellbook_pacote.txt` | Commander Spellbook: 99 nomes reconhecidos (0 não reconhecidos); base = 2 combos (Ascension + Mindcrank; Altar of Dementia + Great Henge [+ Glen Elendra]) e 134 "quase"; pacote exato (−Offer −Negate +Horrigan +Branching) = 0 combos novos, 0 perdidos; base + cada remoção candidata (Drown in the Loch, Assassin's Trophy, Putrefy, Beast Within, Deadly Rollick, Atomize, Casualties of War) = 0 combos novos; controle positivo (Thassa + Consultation) OK; controle de corte (cortar Mindcrank some Ascension + Mindcrank) OK. "Quase" novo com o pacote: Branching Evolution + Walking Ballista + (Vigor ou Rite of Passage); nenhuma das duas está na lista. | usado |
| `dados/rulings_remocoes.json` | oráculo e rulings ao vivo (Scryfall) de Drown in the Loch, Atomize, Deadly Rollick, Assassin's Trophy | usado |
| `orquestracao/csb_pacote.py` (+ `csb_stefano.py`) | gera o Spellbook acima: `python3 csb_pacote.py ../../../lista.md ../dados/spellbook_pacote.json` | usado |
| `orquestracao/gera_config.py`, `config_pacote.json`, `lanca_tudo.sh`, `lanca_gy.sh`, `gy_opp.py`, `rank_pacote.py`, `driver_mm.py`, `abgen.py` | A/B pareado de 9 variantes (N = 10.000, 2 modos) e tamanho do cemitério dos oponentes por turno | em execução |
| `codigo/mothman_goldfish_v1_estado_2026-10-08.py` | simulador congelado (== o vivo de 2026-10-07, `cmp` igual ao `codigo/mothman_goldfish_v1_C2.py` da pasta `candidatas-stefano-2`) | usado |
| `resumos/smoke_pacote.txt` | smoke das 9 variantes: 99 cartas, 0 desconhecidas, 0 duplicadas, 0 exceções em 200 partidas × 2 modos | usado |

Dados do modo resiliência citados na resposta (média por partida, base, N = 10.000, sementes 3.000.000+i): peças do meu motor removidas por remoção pontual do oponente 0,838; wipes do oponente que pegaram 0,654; contramágicas conjuradas 0,689 (em 50,8% das partidas); proteções usadas 0,182 (16,6%); comandante anulado 0,123. Vêm de `../2026-10-07-candidatas-stefano-2/dados/raw_final_10000_resiliencia.json.xz` (variante `base`); modelo do oponente: 7 categorias, 1/3 de atenção por turno, proxy declarado (não é jogo real).
