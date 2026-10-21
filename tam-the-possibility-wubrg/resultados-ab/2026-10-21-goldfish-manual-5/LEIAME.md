# Goldfish manual #5 do Tam (jogado pelo usuário no playtester do Archidekt) — 2026-10-21

**Status: RECEBIDO, interpretação NÃO feita.** Conforme o pedido do usuário no manual #1 ("me pergunte qq dúvida antes de começar a compilar qq coisa"), as dúvidas vão ao usuário antes de qualquer leitura das jogadas.

Arquivado até aqui (só bruto e resumos mecânicos, sem interpretar):

| arquivo | o que é |
|---|---|
| `dados/mensagem_usuario_original.txt` | a mensagem inteira como chegou (extraída do transcript da sessão, sem retocar), incluindo o comentário final: *"Nesse esqueci muitos gatilhos da Ichormoon, mas depois do 3o emblema no campo fica impossível perder proliferando e jogando turnos extras!"* |
| `dados/goldfish_manual_5_bruto.json` | só o JSON do log: 11 blocos (T1 a T11; 11, 5, 8, 14, 14, 20, 28, 29, 34, 59, 128 eventos). Sem foto da mão inicial. |
| `orquestracao/linha_do_tempo.py` → `resumos/linha_do_tempo.md` | resumo por turno, só do bruto |
| `orquestracao/eventos_compactos.py` → `resumos/eventos_compactos.txt` | um evento por linha, só do bruto |

Observações mecânicas do bruto (ainda não interpretadas): T1 tem 7 compras, 2 cartas de volta à biblioteca (The Chain Veil, Narset Transcendent) e 1 compra; T11 tem 128 eventos (pode conter turnos extras); o Jace (ficha) tem um único id no jogo todo.
