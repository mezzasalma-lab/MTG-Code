# Tom Bombadil: goldfish manual #13 (2026-11-11)

**Status: bruto arquivado, análise preliminar feita, dúvidas enviadas ao usuário; NADA compilado ainda** (regra permanente: perguntar e esperar a resposta antes de compilar). O `LEIAME` final, o ledger de compras e de fichas, os testes, o `goldfish-log.md`/`checklist-oraculo.md` e a verificação de reprodução vêm depois das respostas.

## Como os dados foram obtidos
- O usuário colou (na mesma mensagem das respostas do Mothman #3) *"Goldfish manual do Tom Bombadão. Mão inicial na foto. Segue o log:"* e o JSON do playtester do Archidekt (7 blocos de turno, 102 registros).
- `orquestracao/extrair_json_da_conversa.py` lê o registro da sessão, acha a mensagem com "Tom Bombad", "Wooded Foothills" e "Satsuki, the Living Lore", extrai o JSON com `json.JSONDecoder().raw_decode` e grava `partida.json` e a mensagem original; o `.json` solto foi conferido contra o `.xz` e apagado.
- **Foto da mão inicial** (`dados/mao_inicial_foto.webp`; "Keep this", **Mulligan (0)**, simulador de interação **On**): Satsuki the Living Lore, Historian's Boon, Godless Shrine, The First Iroan Games, Command Tower, Wooded Foothills, The Cruelty of Gix. É exatamente a ordem das 7 primeiras compras do T1; a 8ª (Serra's Sanctum) é a compra do turno. Sem mulligan.
- Oráculos: todos os nomes do log estão no `scryfall-cache/oracle-cache.json`, exceto a **Song of the Dryads** (carta do oponente simulado: *"Enchant permanent. Enchanted permanent is a colorless Forest land."*, vista só no log; o marcador `Forest` no Tom é o jeito do usuário de marcá-la).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz`, `dados/mensagem_usuario_original.txt.xz`, `dados/mao_inicial_foto.webp` | log bruto, mensagem e foto | bruto |
| `analisa_partida.py` → `resumos/trace.md` | trace e verificações automáticas (cópia da #12) | gerado |
| `orquestracao/estado_por_turno.py`, `orquestracao/sequencia_bruta.py` → `resumos/estado_por_turno.txt`, `resumos/sequencia_bruta.txt` | estado ao fim de cada turno; os 102 registros em ordem | apoio (o log não registra ficha que some) |

## Leitura preliminar (SEM compilar; minha leitura do log + oráculo)
O script marcou **0 violações provadas** e 2 "anomalias" de marcador que as fontes explicam (Satsuki dá +1 de saber na Iroan Games no T5; o Goldberry move o marcador da There and Back Again no T7). Compras por turno: 8, 1, 1, 1, 3, 1, 1 (as 3 do T5 = compra natural + as 2 do capítulo III da Iroan Games, com o Soldier 4/4). Mana: T5 fecha em 9 de 10 (Tom com WUBRG: Sanctum W, Temple Garden G, Godless Shrine B, Command Tower U, Ziatora R; depois o Bloom Tender dá 5 cores).
Pontos que vão virar dúvida (sem eles o jogo não fecha pelo oráculo): (1) T5, a Historian's Boon vendo a **There and Back Again** entrar (encantamento não-ficha) deveria dar um 2º Soldier e o log só tem o da própria Boon; (2) T7, o **capítulo III da There and Back Again** disparou (Smaug) com a Boon em campo e não há Angel 4/4; (3) o marcador de saber da There and Back Again no T6/T7; (4) a Song of the Dryads no Tom (T5) e o capítulo I da Yojimbo (T6); (5) T7 sem nenhuma conjuração.

## O que NÃO foi feito (Regra #7)
Rulings ao vivo desta partida, ledger, testes dirigidos, `SHA256SUMS`, `verificar_reproducao.sh` e a documentação no `goldfish-log.md`: **pendentes** até as respostas.
