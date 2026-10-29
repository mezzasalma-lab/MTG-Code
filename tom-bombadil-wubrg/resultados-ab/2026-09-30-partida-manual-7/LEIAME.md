# Tom Bombadil — partida manual #7 (2026-09-30): dados brutos, scripts e verificações

Arquivo da Regra #8 (`CLAUDE.md`). A análise em prosa está em
`tom-bombadil-wubrg/goldfish-log.md`, seção "Partida manual #7 (2026-09-30)".

## Como os dados foram obtidos
- `dados/partida.json.xz`: o JSON do Archidekt playtester que o usuário colou na conversa (8 elementos = 8 turnos;
  cada registro = estado de um objeto quando ele mudou; zona `opponentsCards` = interação que o usuário põe contra si).
  O original só existia no texto da sessão; foi extraído por script do registro da conversa (entrada de fila do usuário,
  `json.JSONDecoder.raw_decode`, sem redigitar) e conferido `==` com o texto extraído (8 turnos, 9/6/8/11/10/20/20/47 registros).
- Oráculo: `scryfall-cache/oracle-cache.json` (buscado ao vivo; Golgari Charm e Torment of Hailfire foram adicionados nesta rodada).
  Rulings ao vivo de 15 cartas em `resumos/rulings_scryfall.json` (Golgari Charm não tem ruling).

## Mapa arquivo → o que é → status
| arquivo | o que é | status |
|---|---|---|
| `dados/partida.json.xz` | log bruto da partida #7 | usado |
| `analisa_partida.py` | trace por turno + verificações automáticas (terrenos por turno, fetch, marcadores de saber por objeto-Saga, cópias-ficha de Saga, gatilho do Tom ≤ 1/turno, fontes viradas × magias, compras library→mão por turno). Capítulo final das Sagas e fetchlands vêm do oráculo no cache | usado; mesma versão usada na #6 |
| `resumos/trace.md` | saída do script | usado |
| `resumos/rulings_scryfall.json` | rulings ao vivo (Scryfall) | usado |
| `resumos/varredura_lista.txt` | varredura por script das 100 cartas de `lista.md`: terreno extra, cópia, "could produce", lore/proliferate (regex sobre o oráculo) | usado |
| `orchard_sens.py` | sensibilidade pareada da convenção do Exotic Orchard no simulador (sem alterar o simulador: troca a carta em `CARD_DB` em memória) | usado |
| `dados/orchard_sens_{0..3}.json.xz` | saída bruta das 4 partes (N=3000 pares, sementes 1_000_000+i, 10 turnos, modo padrão) | usado |
| `resumos/orchard_sens_sum.md` | tabela do resumo | usado (tabela do goldfish-log) |
| `resumos/controle_base_vs_tom_v1_runs.txt` | controle: variante `base` = `tom_v1_runs.jsonl` (turno do Tom idêntico em 3000/3000; `mana_by_turn` idêntico em 3000/3000) | usado |
| `orquestracao/lancar_orchard_sens.sh` | lançador das 4 partes | usado |
| `descomprimir.sh` | descomprime `dados/*.xz` | — |
| `SHA256SUMS` | hashes | `sha256sum -c SHA256SUMS` |

Código do simulador (`tom-bombadil-wubrg/tom_goldfish_v1.py`): **não foi alterado** nesta rodada.

## Comandos que reproduzem cada tabela
```
bash descomprimir.sh
python3 analisa_partida.py dados/partida.json.xz > /tmp/trace7.md          # = resumos/trace.md
python3 orchard_sens.py sum dados/orchard_sens > /tmp/orch.md              # = resumos/orchard_sens_sum.md
```

## Reprodutibilidade (feita antes de declarar arquivado)
- `cmp` do trace refeito a partir de `dados/partida.json.xz` contra `resumos/trace.md`: **idêntico byte a byte**.
- `cmp` do resumo do Orchard refeito a partir dos `.json.xz` contra `resumos/orchard_sens_sum.md`: **idêntico byte a byte**.
- NÃO conferidos: `resumos/rulings_scryfall.json` e `resumos/varredura_lista.txt` (dependem da API ao vivo e do cache; gerados uma vez).
- As simulações em si (`orchard_sens.py run`) não foram re-executadas para comparar com os `.json`; a garantia é o controle
  `base` = `tom_v1_runs.jsonl` (3000/3000 iguais).

## Confirmações do usuário (2026-09-30 e 2026-10-01, depois do arquivamento)
Todas as anomalias da partida #7 foram respondidas: as 6 cópias-ficha de The Bath Song (T8), a Bath Song indo 2× ao cemitério (foi 1×), a morte da Barbara Wright no T6 (Golgari Charm não a mata:
1/3 com −1/−1), o Farseek arrastado para o campo em vez de descartado, o 2º terreno do T8 (esqueceu a City of Brass) e o Exotic Orchard do T5 (suposição dele de que gerava a cor que faltava) foram
erros ou suposições dele. Setessan Champion: o usuário disse que só ganha marcador e que quem compra é a Sythis; o oráculo ao vivo diz que o Champion **também compra** (contador + compra), então as
7 compras que faltam (6 do Champion, 1 da Sythis) são leitura errada da carta + esquecimento (conta por turno no `goldfish-log.md`). A nova tabela "library→mão no log" do `resumos/trace.md` é o lado
"log" dessa conta. Nenhum resíduo.

## O que as verificações automáticas NÃO provam
Custo e cor de mana, ordem da pilha, escolhas (alvos, descartes, capítulo de read ahead) e compras/descartes por habilidade só
foram conferidos à mão no `goldfish-log.md`; o log do playtester não registra gatilhos que o jogador não executou, então
"ausente no log" não distingue esquecimento de jogada diferente.
