# The Wise Mothman: partida manual #3 (2026-11-11)

**Status: bruto arquivado, análise preliminar feita, dúvidas enviadas ao usuário; NADA compilado ainda** (regra permanente: perguntar e esperar a resposta antes de compilar). O `LEIAME` final, o ledger de contadores, os testes dirigidos, a conferência com o simulador, o `goldfish-log.md`/`checklist-oraculo.md` e a verificação de reprodução vêm depois das respostas.

## Como os dados foram obtidos
- O usuário colou o log JSON do playtester do Archidekt (6 blocos de turno, 84 registros) com *"Mais um goldfish DO Wise Mothman: Mão inicial na foto. Segue o log:"* e a foto da mão inicial.
- `orquestracao/extrair_json_da_conversa.py` lê o registro da sessão, acha a última mensagem com "Wise Mothman", "Altar of the Brood" e "Zagoth Triome", extrai o JSON com `json.JSONDecoder().raw_decode` e grava `partida.json` e a mensagem original. O `.json` solto foi conferido contra o `.xz` e apagado.
- **Foto da mão inicial** (`dados/mao_inicial_foto.webp`; "Keep this", **Mulligan (0)**, simulador de interação **On**): Breeding Pool, Forest, Plaza of Heroes, Forest, An Offer You Can't Refuse, Tropical Island, Forest. É **exatamente a ordem** das 7 primeiras entradas library→mão do T1; a 8ª (Altar of the Brood) é a compra do turno. Sem mulligan.
- Oráculos: `scryfall-cache/oracle-cache.json` (as 17 cartas reais do log estão no cache e na `lista.md`; a **Dark Deal** é carta do oponente simulado, não da lista).

## Arquivos
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | log bruto | usado |
| `dados/mensagem_usuario_original.txt.xz` | a mensagem do usuário, textual | bruto |
| `dados/mao_inicial_foto.webp` | foto da mão inicial | bruto |
| `analisa_partida.py` → `resumos/trace.md` | trace turno a turno (cópia do script da #2) | usado |
| `orquestracao/estado_por_turno.py`, `orquestracao/sequencia_bruta.py` | estado ao fim de cada turno; sequência crua com marcadores e virada | apoio (o log NÃO registra ficha que some nem mill de oponente) |
| `orquestracao/checagens_preliminares.py` → `resumos/checagens_preliminares.txt` | cor do Mothman no T4, Dark Deal, cartas devolvidas no T6, jogadas de terreno, mills próprios, contadores | usado |

## Leitura preliminar (SEM compilar; minha leitura do log + oráculo, não prova de intenção)
O que o log e o oráculo provam sozinhos (`resumos/checagens_preliminares.txt`):
1. **T4: The Wise Mothman custa {1}{B}{G}{U} e os 4 terrenos virados (Forest, Breeding Pool, Forest, Tropical Island) só dão G e U**: sem {B}. A Plaza of Heroes (qualquer cor para magia lendária) estava na mão e foi descartada pela Dark Deal.
2. **T4: Dark Deal** ("discards all the cards in their hand, then draws that many cards minus one"): 6 descartadas, **4 compradas, esperado 5**.
3. **T6: a Evolution Witness devolve "target permanent card"** e o log leva à mão **Didn't Say Please e An Offer You Can't Refuse, que são Instants**; a **Rejuvenating Springs** (terreno) sai do cemitério direto para o **campo**, sem carta da lista que o permita (e seria o 2º terreno do turno).
4. **T6: nenhum mill próprio** (o Mothman deu 1 rad no T4 e outro no ataque do T5; o rad do T5 foi cumprido com a Gyre Sage).
5. T5 e T6: contadores no Mothman (8 no T5, depois de 7 cliques após a Six), Six (4) e Evolution Witness (5) sem fonte visível no log (mill de oponente não aparece; limite declarado nas #1 e #2).

## O que NÃO foi feito (Regra #7)
Rulings ao vivo desta partida, ledger de contadores, conferência com o simulador, testes dirigidos, `SHA256SUMS`, `verificar_reproducao.sh` e a documentação no `goldfish-log.md`/`checklist-oraculo.md`: **pendentes** até as respostas.
