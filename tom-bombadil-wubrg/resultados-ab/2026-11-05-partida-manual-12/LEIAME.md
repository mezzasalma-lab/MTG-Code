# Tom Bombadil: goldfish manual #12 (2026-11-05)

**Status: bruto arquivado; dúvidas enviadas ao usuário; NADA compilado ainda** (pedido dele: *"ME PERGUNTE AS DUVIDAS"*, e a regra permanente de perguntar antes de compilar). Este arquivo é só o ponto de partida: o `LEIAME` final, o ledger, os testes, o `goldfish-log.md` e a verificação de reprodução vêm depois das respostas.

## Como os dados foram obtidos

- O usuário colou na conversa o log JSON do playtester do Archidekt (10 blocos de turno, 221 eventos; um evento = foto do estado de um objeto quando ele mudou) com o texto *"MAIS UM GOLDFISH MANUAL DO TOM BOMBADIL"*.
- `orquestracao/extrair_json_da_conversa.py` lê a transcrição da sessão, acha a última mensagem do usuário com essa frase, extrai o JSON com `json.JSONDecoder().raw_decode` e grava a mensagem original e o JSON.
- Uso: `python3 -I orquestracao/extrair_json_da_conversa.py <transcript.jsonl> <pasta_saida>`.
- Sem foto da mão inicial até agora (pergunta enviada).

## Arquivos

| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | o JSON do log, sem alteração (conferido byte a byte contra o JSON extraído antes de apagá-lo) | bruto |
| `dados/mensagem_usuario_original.txt.xz` | a mensagem inteira do usuário, textual | bruto |
| `analisa_partida.py` | cópia do script da #11 (terrenos por turno, fetch, marcadores por objeto, 1 gatilho do Tom por turno). **Ainda não adaptado**: não distingue o MESMO objeto jogado 2× (desfazer) de dois terrenos, nem fetch ainda não acionada no fim do jogo | a corrigir na compilação |
| `ledger_compras.py` | cópia da #11; os eventos esperados estão fixos para aquele jogo, **tem de ser reescrito** para a #12 | a reescrever |
| `orquestracao/estado_por_turno.py`, `orquestracao/sequencia_bruta.py` | estado ao fim de cada turno e sequência crua de eventos (agora apontam para `dados/partida.json.xz` desta pasta) | usados |
| `orquestracao/baixar_rulings.py` | cópia da #11 (lista de cartas fixa; ainda não rodado para a #12) | a adaptar |
| `resumos/trace.md` | saída de `python3 -I analisa_partida.py dados/partida.json.xz` | gerado, lido |

## Leitura preliminar (SEM compilar; minha leitura do log, não prova)

- O script marcou 2 "violações" que não se sustentam: (1) **Plains ×2 no T7** é o MESMO objeto (`ym_I-HoDOr6`) com `hand→battlefield` duas vezes, o padrão de desfazer já confirmado pelo usuário nas #9–#11; (2) **Verdant Catacombs** entrou no T10 e não foi acionada: é uma fetch parada no fim do log, não um erro.
- Compras: as contagens por turno (8, 1, 1, 2, 2, 3, 1, 1, 2, 4) batem com minha leitura (compra natural + Enchantress's Presence por magia de encantamento + Song of Eärendil cap. I), mas **o T1 = 8 só fecha com a foto/mulligan**.
- Mana T1–T7 e T9–T10 fecha por terreno virado + bônus da Fertile Ground; **T8 não fecha com certeza** (imposto do Tom, dúvida 1).

## Dúvidas enviadas ao usuário (aguardando respostas)

1. T8: imposto do Tom (`commandTax = 0` no recast; nas #10 e #11 o contador foi ajustado).
2. T8: contador de saber da ITDBT 4→3 movido para um Human Soldier com Nesting Grounds, antes do Tom voltar.
3. T9: Resurgent Belief (contador removido na fase principal, não no upkeep) e Kiora/Kraken ×2.
4. T10: Sagas sem marcador novo, mas com os efeitos do cap. II aplicados.
5. T7: Iroan Games (3º marcador depois da Soul Shatter; Human Soldier criado no T7; ficha virada).
6. T6: Jugan indo ao cemitério na hora, sem o Monk do cap. I.
7. T8/T9: Fertile Ground × Austere Command.
8. Simulador de interação (Fold into Aether no T5; quantas por rodada; Walker e Plant Warrior).
9. Fim do log: Verdant Catacombs, cartas que ficaram na mão, o jogo acabou no T10?
10. Foto da mão inicial, mulligan e configuração do simulador.

## O que NÃO foi feito (Regra #7)

Rulings ao vivo desta partida não baixadas (oráculos lidos do cache do repositório; Fold into Aether, Walker e Plant Warrior consultados ao vivo no Scryfall: um contra-feitiço e duas fichas do oponente simulado); testes dirigidos, ledger, comparação com o simulador, `goldfish-log.md`, `SHA256SUMS` e verificação de reprodução: **pendentes**.
