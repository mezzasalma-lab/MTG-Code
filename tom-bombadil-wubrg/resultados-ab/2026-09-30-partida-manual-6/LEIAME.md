# Tom Bombadil — partida manual #6 (2026-09-30): dados brutos, script e verificações

Arquivo da Regra #8 (`CLAUDE.md`). A análise em prosa está em
`tom-bombadil-wubrg/goldfish-log.md`, seção "Partida manual #6 (2026-09-30)".

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do Archidekt playtester que o usuário colou na conversa (13 elementos = 13 turnos; cada
  registro = estado de um objeto quando ele mudou; zona `opponentsCards` = interação que o usuário põe contra si).
  O original só existia no texto da sessão; foi extraído do registro da conversa por script (sem redigitar).
- Oráculo: `scryfall-cache/oracle-cache.json` (ao vivo). Nesta rodada foram adicionados Wan Shi Tong, Librarian; Jin-Gitaxias,
  Core Augur; e as fichas Snail, Goblin Shaman, Wraith, Treasure e o emblema The Ring.

## Mapa arquivo → o que é → status
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | log bruto da partida #6 | usado |
| `analisa_partida.py` | trace por turno + verificações automáticas (mesmo script da #7; 1ª versão só checava terrenos/fetch/saber/Tom, a versão final acrescentou chave por id de objeto, cópias-ficha, fontes viradas × magias e a separação "violação provada" × "anomalia sem fonte") | usado |
| `resumos/trace.md` | saída do script (regerada com a versão final) | usado |
| `descomprimir.sh` | descomprime `dados/*.xz` | — |
| `SHA256SUMS` | hashes | `sha256sum -c SHA256SUMS` |

Código do simulador: **não foi alterado**.

## Comando que reproduz a tabela
```
bash descomprimir.sh
python3 analisa_partida.py dados/partida.json.xz > /tmp/trace6.md      # = resumos/trace.md
```

## Reprodutibilidade
- `cmp` do trace refeito a partir de `dados/partida.json.xz` contra `resumos/trace.md`: **idêntico byte a byte**.
- Resultado automático: 0 violações provadas; 3 anomalias sem fonte, todas na mesma Saga (In the Darkness Bind Them, T12).

## O que as verificações automáticas NÃO provam
Custo/cor de mana, ordem da pilha, escolhas e compras por habilidade foram conferidos à mão no `goldfish-log.md`; o log do
playtester não registra o que o jogador não executou, e mistura desfazer/refazer (ex.: Fable com duas entradas idênticas no T6).
