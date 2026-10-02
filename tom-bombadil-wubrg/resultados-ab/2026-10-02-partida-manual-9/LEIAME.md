# Tom Bombadil — partida manual #9 (2026-10-02): dados brutos e script (rodada em andamento)

Arquivo da Regra #8 (`CLAUDE.md`). **Status: aguardando as respostas do usuário** às dúvidas levantadas na análise; a seção
"Partida manual #9" de `tom-bombadil-wubrg/goldfish-log.md` só é escrita depois delas.

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do Archidekt playtester que o usuário colou na conversa (8 elementos = 8 turnos), extraído por script do registro da conversa
  (sem redigitar) e conferido `==` com o texto extraído. A foto da mão inicial (7 cartas, "Keep this", **Interaction simulator (Off)** na tela) mostra: Power Conduit,
  Overgrown Tomb, Birth of the Imperium, Battle at the Helvault, Binding the Old Gods, Command Tower, Serra's Sanctum; a 8ª carta do T1 (City of Brass) é a compra do turno.
  O usuário informou que implementou "até três interações por rodada" (o log tem 4 cartas de oponente em `opponentsCards`: Shapeshifter, Rankle, Amazing Acrobatics, Archfiend of Ifnir).
- Oráculo: `scryfall-cache/oracle-cache.json` (ao vivo). Adicionados nesta rodada: Amazing Acrobatics, Rankle, Master of Pranks, Shapeshifter e a ficha Construct.

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | log bruto da partida #9 | usado |
| `analisa_partida.py` | mesmo script das partidas #6–#8 | usado |
| `resumos/trace.md` | saída do script | usado |
| `descomprimir.sh` | descomprime `dados/*.xz` | — |

Reproduz: `bash descomprimir.sh; python3 analisa_partida.py dados/partida.json.xz > /tmp/trace9.md` (= `resumos/trace.md`).
Simulador (`tom_goldfish_v1.py`): não alterado.
