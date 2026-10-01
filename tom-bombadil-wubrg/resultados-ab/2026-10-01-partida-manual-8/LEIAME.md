# Tom Bombadil — partida manual #8 (2026-10-01): dados brutos e script (rodada em andamento)

Arquivo da Regra #8 (`CLAUDE.md`). **Status: aguardando as respostas do usuário** às dúvidas levantadas na análise; a seção
"Partida manual #8" de `tom-bombadil-wubrg/goldfish-log.md` só é escrita depois delas.

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do Archidekt playtester que o usuário colou na conversa (8 elementos = 8 turnos), extraído por script do
  registro da conversa (sem redigitar) e conferido `==` com o texto extraído. A foto da mão inicial (7 cartas, "Keep this", Interaction simulator ligado)
  mostra: Narci, O'aka, Forest, Jugan Defends the Temple, Sol Ring, Flooded Strand, Estrid's Invocation; a 8ª carta do T1 (Resourceful Defense) é a compra do turno.
- Oráculo: `scryfall-cache/oracle-cache.json` (ao vivo). Adicionados nesta rodada: Ugin, Eye of the Storms e as fichas Human Monk e Astartes Warrior (versão com vigilance, a que a Birth of the Imperium cria).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | log bruto da partida #8 | usado |
| `analisa_partida.py` | mesmo script das partidas #6/#7 (trace por turno, terrenos, fetch, saber por objeto-Saga, fontes viradas, compras por turno) | usado |
| `resumos/trace.md` | saída do script | usado |
| `descomprimir.sh` | descomprime `dados/*.xz` | — |

Reproduz: `bash descomprimir.sh; python3 analisa_partida.py dados/partida.json.xz > /tmp/trace8.md` (= `resumos/trace.md`).
Simulador (`tom_goldfish_v1.py`): não alterado.
