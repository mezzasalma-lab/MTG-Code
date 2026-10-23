# Goldfish manual #6 do Tam (2026-10-23) — PARCIAL: dados brutos arquivados, análise aguardando as respostas do usuário

**Status:** só o bruto e as saídas mecânicas (sem interpretação) estão aqui. A análise (linha do tempo
interpretada, afirmações → testes, replay no simulador, `goldfish-log.md` §11) **não foi feita**: a
instrução permanente do usuário é *"me pergunte qq dúvida antes de começar a compilar qq coisa"*, e as
dúvidas foram enviadas na conversa de 2026-10-23. Este LEIAME é reescrito quando as respostas chegarem.

## Arquivos

| arquivo | o que é |
|---|---|
| `dados/mensagem_usuario_original.txt` | a mensagem do usuário, byte a byte: "Mais um Goldfish manuel. Mão inicial em anexo." + o JSON do log (11 blocos) |
| `dados/goldfish_manual_6_bruto.json` | o JSON do log extraído da mensagem (11 blocos = T1..T11; eventos por bloco: 9, 3, 7, 20, 14, 20, 19, 28, 27, 39, 85) |
| `dados/mao_inicial.webp` | a foto da mão inicial: Promise of Loyalty, Steam Vents, Hallowed Fountain, Way of the Paradox, Oko, Dihada, Domri; botões "Keep this" / "Mulligan (0)"; "Interaction simulator (On)" |
| `orquestracao/eventos_compactos.py` → `resumos/eventos_compactos.txt` | um evento por linha, só do bruto, sem interpretar |
| `orquestracao/deltas_lealdade.py` → `resumos/deltas_lealdade.txt` | variação de lealdade/contadores por evento, só do bruto |
| `orquestracao/linha_do_tempo.py` → `resumos/linha_do_tempo.txt` | tabela por turno (compras, terreno, conjurou, buscou, saiu do campo, oponente, lealdade) |

Reproduzir: `python3 -I orquestracao/<script>.py > resumos/<script>.txt` (cada script lê só `dados/goldfish_manual_6_bruto.json`).

## O que NÃO foi feito (Regra #7)

Tudo da análise: respostas do usuário, testes dirigidos (`testes/t_manual6.py`), replay no simulador
(padrão / resiliência / playtester), conferência do oráculo de cartas novas no cache (Regra 15), `cmp` de
reprodução, `SHA256SUMS` final. A linha do tempo mecânica **não distingue** clique desfeito de jogada real
(o log não registra desfazer, nem combate, nem alvo das magias do oponente).
