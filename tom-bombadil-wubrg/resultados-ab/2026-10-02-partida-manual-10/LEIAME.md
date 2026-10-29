# Tom Bombadil — partida manual #10 (2026-10-02): dados brutos, script e ledger de compras 

Arquivo da Regra #8 (`CLAUDE.md`). **Status: concluída com as respostas do usuário** (2026-10-02). A análise em prosa está na seção "Partida manual #10" de `tom-bombadil-wubrg/goldfish-log.md`.

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do Archidekt playtester que o usuário colou na conversa (13 elementos = 13 turnos), extraído por script do registro da conversa
  (sem redigitar) e conferido `==` com o texto extraído. Foto da mão inicial (após **1 mulligan grátis**, simulador de interação **On**): Enchantress's Presence, Summon: Primal Odin,
  Leyline Binding, Utopia Sprawl, Femeref Enchantress, Hallowed Fountain, Misty Rainforest; a 8ª carta do T1 (Starfield of Nyx) é a compra do turno.
- Oráculo: `scryfall-cache/oracle-cache.json` (ao vivo). Adicionados nesta rodada: Blind Obedience, Deafening Silence, Reject Imperfection, Steel Hellkite, Witness Protection e as fichas Knight (2/2 branco) e Human Soldier (1/1 branco).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | log bruto da partida #10 | usado |
| `analisa_partida.py` | mesmo script das partidas #6–#9 | usado |
| `resumos/trace.md` | saída do script | usado |
| `resumos/rulings_scryfall.json` | rulings ao vivo (Scryfall) de 14 cartas | usado (não conferido por `cmp`: depende da API) |
| `ledger_compras.py` | conta ESPERADA × LOG das compras por turno (motores de compra de encantamento); os eventos por turno foram lidos à mão do trace (suposições no cabeçalho do script) | usado |
| `resumos/ledger_compras.md` | saída do ledger | usado |
| `descomprimir.sh` | descomprime `dados/*.xz` | — |

Reproduz: `bash descomprimir.sh; python3 analisa_partida.py dados/partida.json.xz > /tmp/trace10.md` (= `resumos/trace.md`) e `python3 ledger_compras.py > /tmp/ledger.md` (= `resumos/ledger_compras.md`).
Simulador (`tom_goldfish_v1.py`): não alterado.

## Confirmações do usuário (2026-10-02)
Terrenos: Ketria Triome no T2 e Savai Triome no T12 (repetições = desfazer). Compras: esqueceu quase todas as do Femeref e algumas das demais (ledger −13). Kami War: o loop (Hex Parasite 1→0 no upkeep + passo natural) exilou a Deafening Silence;
o saber 2 do T12 foi erro. Knights 1→2 (T13), Iroan II com 2 marcadores, marcadores do Champion esquecidos, Fable descartada (o "campo" foi erro), 3 descartes onde eram 2 e Resourceful Defense em 3 registros: erros.
Tom morto no T6 (o usuário diz Casualties of War; o log só tem o Casualties no T11 e o Torment no T6). Os eventos por turno do ledger são leitura minha do trace (suposições no cabeçalho de `ledger_compras.py`).
O script e o `resumos/trace.md` não foram alterados: o trace lista "violação" de terrenos nos T2, T4, T10 e T12 e a anomalia de saber da Kami War no T12, que o relato do usuário explica (desfazer/erro de registro).

## O que as verificações NÃO provam
Custo e cor de mana em T11–T13, ordem da pilha, escolhas de alvo e efeitos do oponente além do que o log mostra.

## Correção posterior (2026-10-03)
O usuário confirmou (na partida #11) que achava que os marcadores de saber também aumentam no upkeep. Nesta partida isso aparece nas Sagas devolvidas pela Starfield: Bath Song (T10), Summon: Knights (T11 e T12) e Primal Odin (T13) terminam o turno com 1 marcador; pela regra 714.3b ganhariam o 2º no mesmo turno (a In the Darkness Bind Them do T13 está certa, com 2). O trace e o script não mudaram.
