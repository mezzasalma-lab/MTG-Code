# Tom Bombadil — partida manual #8 (2026-10-01): dados brutos e script 

Arquivo da Regra #8 (`CLAUDE.md`). **Status: concluída com as respostas do usuário** (2026-10-01). A análise em prosa está na seção "Partida manual #8" de `tom-bombadil-wubrg/goldfish-log.md`.

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
| `resumos/rulings_scryfall.json` | rulings ao vivo (Scryfall) de 10 cartas | usado (não conferido por `cmp`: depende da API) |
| `descomprimir.sh` | descomprime `dados/*.xz` | — |

Reproduz: `bash descomprimir.sh; python3 analisa_partida.py dados/partida.json.xz > /tmp/trace8.md` (= `resumos/trace.md`).
Simulador (`tom_goldfish_v1.py`): não alterado.

## Confirmações do usuário (2026-10-01)
Jugan no T4 (O'aka antes do passo natural; o log mostra Lore 3 antes e um ajuste +4/+4 não explicado), Satsuki só na Fenrir (violação do "each Saga you control"), marcador da Birth esquecido (Resourceful Defense),
Human Citizen = 3 fichas 1/1 atacando pelo simulador de interação, Estrid no upkeep, encerramento antecipado no T8. Resíduo: 1 compra do T7 e o marcador natural da cópia da Estrid no T8.
O script e o `resumos/trace.md` não foram alterados (listam 2 "anomalias de saber" na Jugan e na Fenrir que o relato do usuário explica: remoção prévia pelo O'aka e Satsuki só na Fenrir).

## O que o script NÃO prova
Custo e cor de mana, ordem da pilha, escolhas (alvos de capítulo II), movimento de marcadores por Resourceful Defense e compras por habilidade foram conferidos à mão no `goldfish-log.md`.
