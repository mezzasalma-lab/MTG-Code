# 2026-10-21 — Tam: cores dos terrenos dos oponentes (Exotic Orchard, Fellwar Stone)

Pergunta aberta desde o goldfish #3 (*"quais cores os terrenos dos seus 3 oponentes reais costumam produzir?"*). **Decisão do usuário (2026-10-21), literal: *"Decida os terrenos dos oponentes de forma aleatória"*.**

## Conclusão

**Convenção mantida, sem mudança de código** (então nenhuma linha de base muda): as cores dos terrenos dos 3 oponentes são **aleatórias, sorteadas por semente**: `make_opp` sorteia uma **identidade de 2 cores** por oponente (`rng.sample(COLORS5, 2)`) e cada terreno que ele joga produz **uma cor sorteada** dessa identidade (`opponent_turn`: 80% de chance de jogar terreno por turno até o 8º turno dele, 35% depois). A Exotic Orchard e o Fellwar Stone produzem as cores que **algum terreno de oponente em campo** produz (oráculo: *"a land an opponent controls could produce"*): no turno 1 do jogador nenhum oponente jogou terreno e eles não produzem nada.

**O que isso significa em números** (`cores_disponiveis.md`, N = 10.000 sementes, modo padrão; início do turno do jogador):

| início do turno | oponentes com ≥ 1 terreno | cores diferentes (média) | P(uma cor específica, ex. {G}) | P(as 5 cores) |
|---|---|---|---|---|
| T2 | 2,41 | 2,04 | **40,9%** | 0,0% |
| T3 | 2,88 | 2,94 | 58,5% | 1,9% |
| T4 | 2,98 | 3,38 | 67,1% | 5,7% |
| T5 | 3,00 | 3,62 | 72,1% | 9,9% |

Uma mão que depende da Orchard ou do Fellwar para uma cor específica **no T2 só tem essa cor em ~41% das partidas** (e ~59% no T3). No playtester do Archidekt a Orchard do usuário tocou {G} no T2 (goldfish #3): lá a cor é livre. **O custo da convenção aleatória nesse caso:** no goldfish #3 os planeswalkers em T5 / T6 / T7 passam de **1 / 3 / 4** (terrenos de oponente com as 5 cores a partir do T2, `resultados-ab/2026-10-21-goldfish-manual-3/`) para **0 / 1 / 3** (aleatório). No goldfish #4 a convenção não pesou (a mão não depende da Orchard).

## Escopo (Regra #7)

**Verificado:** a leitura do código (`make_opp`, `opponent_turn`, `opp_land_colors`) e a tabela acima, por execução (`python3 cores_disponiveis.py 10000`; semente 1.000.000+i; sai idêntica ao arquivo `cores_disponiveis.md`).
**Não verificado / limites:** (1) a identidade de **2 cores** por oponente é uma escolha de modelagem (decks de Commander reais têm de 1 a 5 cores; um oponente de 1 cor ou de 4 mudaria a probabilidade de uma cor específica); (2) o modo de resiliência usa a mesma convenção; (3) os terrenos dos oponentes não incluem terrenos de qualquer cor (Command Tower, City of Brass, Exotic Orchard deles), que dariam as 5 cores; (4) nenhuma linha de base foi refeita (não houve mudança de código).
