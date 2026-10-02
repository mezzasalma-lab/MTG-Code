# Tom Bombadil — partida manual #10 (2026-10-02): dados brutos, script e ledger de compras (rodada em andamento)

Arquivo da Regra #8 (`CLAUDE.md`). **Status: aguardando as respostas do usuário** às dúvidas levantadas na análise; a seção
"Partida manual #10" de `tom-bombadil-wubrg/goldfish-log.md` só é escrita depois delas.

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
| `ledger_compras.py` | conta ESPERADA × LOG das compras por turno (motores de compra de encantamento); os eventos por turno foram lidos à mão do trace (suposições no cabeçalho do script) | usado |
| `resumos/ledger_compras.md` | saída do ledger | usado |
| `descomprimir.sh` | descomprime `dados/*.xz` | — |

Reproduz: `bash descomprimir.sh; python3 analisa_partida.py dados/partida.json.xz > /tmp/trace10.md` (= `resumos/trace.md`) e `python3 ledger_compras.py > /tmp/ledger.md` (= `resumos/ledger_compras.md`).
Simulador (`tom_goldfish_v1.py`): não alterado.
