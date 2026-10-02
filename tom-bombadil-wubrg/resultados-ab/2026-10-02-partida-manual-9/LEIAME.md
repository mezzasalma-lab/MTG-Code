# Tom Bombadil — partida manual #9 (2026-10-02): dados brutos e script 

Arquivo da Regra #8 (`CLAUDE.md`). **Status: concluída com as respostas do usuário** (2026-10-02). A análise em prosa está na seção "Partida manual #9" de `tom-bombadil-wubrg/goldfish-log.md`.

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
| `resumos/rulings_scryfall.json` | rulings ao vivo (Scryfall) de 10 cartas | usado (não conferido por `cmp`: depende da API) |
| `descomprimir.sh` | descomprime `dados/*.xz` | — |

Reproduz: `bash descomprimir.sh; python3 analisa_partida.py dados/partida.json.xz > /tmp/trace9.md` (= `resumos/trace.md`).
Simulador (`tom_goldfish_v1.py`): não alterado.

## Confirmações do usuário (2026-10-02)
Indatha Triome no T7 = erro (achou que tirar o marcador do Binding disparava o capítulo II de novo); Battle at the Helvault = contrada pela Amazing Acrobatics (por isso vai ao cemitério); Anel esquecido (ITDBT I e II);
parou depois da Replenish sem resolver capítulos; Construct com 2 marcadores só para representar o 2/2; simulador de interação ligado depois da foto da mão. Respostas de 2026-10-02 (2ª rodada): T6 = 2 terrenos por erro (Urza's Saga + Jetmir's Garden; devia ser só o Garden; a Saga voltou à mão e foi jogada no T7);
Shapeshifter era uma ficha genérica 3/2 (não a carta real), atacou e o Tom 4/4 bloqueou; Rankle só descarte; Archfiend não faz nada ao entrar. Nenhum resíduo.
O script e o `resumos/trace.md` não foram alterados: a "violação" de 2 terrenos no T6 que ele lista foi confirmada como erro e nenhuma anomalia de saber (a busca da Indatha no T7 aparece como terreno buscado, sem anomalia de saber).

## O que o script NÃO prova
Custo e cor de mana, ordem da pilha, escolhas, efeitos das interações do oponente e compras por habilidade foram conferidos à mão no `goldfish-log.md`.
