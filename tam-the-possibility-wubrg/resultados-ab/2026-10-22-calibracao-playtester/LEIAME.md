# 2026-10-22 — Calibração do oponente: o perfil `playtester` (resiliência com as taxas dos 5 goldfish do usuário)

Origem: a pendência "a resiliência é a mesma do Prismatic Bridge, não calibrada pro Tam; a calibração com a mesa real do usuário está pendente" (`goldfish-log.md` §1/§5) e o pedido **"Termine tudo que falta!"**. O que o usuário joga nos goldfish é o **playtester do Archidekt**: os oponentes são um bot que põe cartas em `opponentsCards` de vez em quando. Os 5 logs (#1 a #5, 46 turnos) são a única medida que tenho de "a mesa dele".

## Conclusão (medido)

1. **O bot do playtester é muito mais quieto que a resiliência de sempre.** Nos 5 logs, de T4 em diante (nenhum evento em T1–T3): **24 cartas de oponente em 31 turnos do usuário = 0,77 por turno para a mesa inteira** (IC95% 0,50–1,15). A resiliência de sempre põe **~8,5 criaturas de oponente em campo no T5–T10** (o playtester põe 1 a 2) e **9,1 interações por partida** contra 3,8 observadas (IC95% 2,0–6,4).
2. **O perfil `playtester` fecha essa conta.** Interações não-criatura por partida (T3–T12 no simulador): **3,82 (3,71–3,93)** contra **3,77 observados**; cada categoria dentro do IC95% observado (remoção 0,95, anulação 0,94, efeito em massa 1,07, descarte 0,86). Criaturas de oponente em campo (soma dos 3): 0,89 / 1,12 / 1,07 em T5 / T8 / T10 contra 1,0 / 2,1 / 2,4 cartas de criatura vistas nos logs (o simulador tira criaturas do campo com os meus planeswalkers; o observado é acumulado sem mortes).
3. **Com o perfil, a resiliência reproduz a trajetória de planeswalkers do usuário; sem ele, fica abaixo.** Replay das mãos e compras dos goldfish #3, #4 e #5 em 300 ordens do resto do baralho (tabela abaixo): no #4 e no #5 a mediana do simulador com o perfil **acompanha ou fica um pouco acima** do usuário (P(simulador ≥ usuário) de 52% a 96%); com a resiliência de sempre fica **abaixo** (P de 15% a 68%, e em 10 dos 12 turnos comparados abaixo de 45%). No #3 (mão com 4 terrenos e cor de terreno de oponente decidindo) os dois modos ficam abaixo (perfil: 0/0/1 contra 1/3/4); o gargalo ali é de cor, não de oponente.
4. **O que isso NÃO diz:** que a mesa real dele (3 humanos) joga como o bot do playtester. É a mesa dos *goldfish dele*. O modo de resiliência de sempre continua sendo a referência para uma mesa hostil; o `playtester` é a referência para "o que o playtester faz".

## As taxas observadas (`resumos/taxas_observadas.md`, só dos brutos)

Categoria de cada carta pelo oráculo (minha; o jogador não classificou): criatura/ficha (11: Golem, Doombot, Zombie, Carnivore, Warrior, Metallic Sliver, Graveborn, Spider, Goblin Wizard, Eldrazi Angel, Junji), remoção pontual (5: Nature's Claim, Assassin's Trophy, Disenchant, Swift End, Loran), anulação (2: Vex, Ertai's Scorn), efeito em massa (5: Split Up, Cleansing Nova, Damning Verdict, Promise of Loyalty, Aetherize), aura (1: Witness Protection).

| categoria | eventos | por turno do usuário | por partida de 9 turnos (T4–T12) |
|---|---|---|---|
| criatura | 11 | 0,355 | 3,19 (1,59–5,71) |
| remoção pontual | 5 | 0,161 | 1,45 (0,47–3,39) |
| anulação | 2 | 0,065 | 0,58 (0,07–2,10) |
| efeito em massa | 5 | 0,161 | 1,45 (0,47–3,39) |
| aura | 1 | 0,032 | 0,29 (0,01–1,62) |
| **total** | **24** | **0,774** | **6,97 (4,46–10,37)** |

Leitura: o descarte do Junji (T6 do #4) é uma **inferência** (os 2 descartes logo depois do Junji; ver o LEIAME do #4), por isso o descarte observado (0,29) tem IC sem informação e não serve de alvo.

## O perfil (`OPP_PLAYTESTER = True`, `OPP_CARD_MIX = True`, constantes `OPP_PLAYTESTER_*` no simulador)

| o quê | resiliência de sempre | perfil `playtester` | de onde vem |
|---|---|---|---|
| criatura de oponente | arquétipos (go wide: 1–3 fichas por turno desde o 2º turno dele; voltron; low) | **1 criatura com prob. 0,118** por turno de cada oponente, a partir do 3º turno dele, no máximo 4, tamanho {1:30%, 2:35%, 3:15%, 4:12%, 5:8%} | 11 criaturas / (31 turnos × 3 oponentes) |
| magias por turno dele (0 / 1 / 2) | 10% / 55% / 35% | 74% / 24% / 2% (média 0,28) | 24 cartas / 90 turnos de oponente |
| gate de atenção (liga remoção, wipe, ataque, descarte) | 1/3 dos turnos | **0,143** | ajuste: interações não-criatura somam ~3,8 por partida |
| fator da anulação | 0,5 | **0,125** | a anulação não passa pelo gate; ajuste: ~0,95 por partida |
| efeito em massa | sempre "destrói todas as minhas criaturas" | 4 variantes sorteadas: **Cleansing Nova** (todas), **Split Up** (só viradas OU só desviradas, o modo que mata mais), **Damning Verdict** (só as sem contador), **Promise of Loyalty** (fico com a melhor, que ganha Vow) | as 4 cartas de efeito em massa vistas |
| anulação | seca | metade **Vex**: eu compro 1 carta | Vex e Ertai's Scorn: 1 de 2 |

## Ajuste (`resumos/ajuste_perfil_{default,playtester}.txt`, N = 2.000 cada, resiliência, 12 turnos)

| por partida | observado (IC95%) | resiliência de sempre | perfil `playtester` |
|---|---|---|---|
| remoção pontual | 1,45 (0,47–3,39) | 2,22 | **0,95** |
| anulação | 0,58 (0,07–2,10) | 2,42 (**fora**) | **0,94** |
| efeito em massa | 1,45 (0,47–3,39) | 2,53 | **1,07** |
| descarte | 0,29 (0,00–1,60; inferido) | 1,96 (**fora**) | **0,86** |
| **total não-criatura** | **3,77 (2,00–6,42)** | **9,12 (fora)** | **3,82** |
| criaturas de oponente em campo, T5 / T8 / T10 | 1,0 / 2,1 / 2,4 (acumulado) | 7,8 / 9,0 / 8,4 | 0,89 / 1,12 / 1,07 |

**O que é ajuste e o que é validação:** o perfil foi **ajustado** nas taxas dos 5 logs (que incluem o #3, o #4 e o #5). A tabela do replay mede se ele aproxima o **resultado** (planeswalkers), uma grandeza que não entrou no ajuste, mas **não é validação independente** (mesmos 3 jogos).

## Replay: planeswalkers no fim de cada turno (mediana de 300 ordens; entre parênteses P(simulador ≥ usuário))

| jogo | | usuário | padrão | resiliência de sempre | resiliência `playtester` |
|---|---|---|---|---|---|
| #3 (T5 / T6 / T7) | | 1 / 3 / 4 | 0 / 1 / 3 | 0 / 0 / 1 (12% / 3% / 8%) | 0 / 0 / 1 (30% / 6% / 23%) |
| #4 (T4 a T9) | | 0 / 1 / 1 / 3 / 3 / 4 | 1 / 1 / 2 / 4 / 4 / 4 | 1 / 0 / 1 / 1 / 2 / 2 (— / 44% / 68% / 21% / 32% / 18%) | 1 / 1 / 2 / 3 / 4 / 4 (— / 81% / 96% / 65% / 82% / 61%) |
| #5 (T4 a T10) | | 1 / 2 / 2 / 2 / 4 / 5 / 7 | 1 / 2 / 4 / 7 / 11 / 13 / 16 | 1 / 1 / 1 / 1 / 2 / 3 / 3 (62% / 19% / 24% / 36% / 24% / 21% / 15%) | 1 / 2 / 2 / 4 / 4 / 8 / 10 (93% / 67% / 66% / 80% / 52% / 86% / 80%) |

(Os replays do modo `padrão` com e sem o perfil dão as mesmas medianas nos 3 jogos: no modo padrão o oponente não tem tabuleiro, então o perfil só mexe no número de magias dele.)

## Arquivos

| arquivo | o que é | status |
|---|---|---|
| `orquestracao/taxas_observadas.py` → `resumos/taxas_observadas.md` | as taxas, só dos 5 brutos (`goldfish_manual_N_bruto.json` das pastas dos jogos) | usado |
| `orquestracao/ajuste_perfil.py` → `resumos/ajuste_perfil_{default,playtester}.txt` | as mesmas grandezas medidas no simulador, com e sem o perfil | usado |
| `orquestracao/replay_perfil.py` → `resumos/replay_jogo{3,4,5}_{padrao,resiliencia_default,resiliencia_playtester,padrao_playtester}.txt` | os replays dos 3 jogos | usado |
| `orquestracao/roda_calibracao.sh`, `verificar_reproducao.sh` | lançador e a verificação por `cmp` | usado |
| `resumos/verificacao_reproducao.txt` | o resultado da verificação | usado |

## Como refazer

```
cd orquestracao
python3 taxas_observadas.py | cmp - ../resumos/taxas_observadas.md
bash roda_calibracao.sh                       # ajuste (N=2.000 x 2) e os 12 replays (N=300); ~15 min; usa o simulador VIVO (tam_goldfish_v1.py da pasta do deck)
bash verificar_reproducao.sh                  # refaz tudo numa pasta temporária e compara com `cmp`
sha256sum -c ../SHA256SUMS
```

## Escopo (Regra #7)

**Medido:** as taxas de 24 cartas de oponente em 46 turnos (5 logs do mesmo jogador, mesmo baralho, mesmo playtester); o perfil contra essas taxas e contra o resultado dos 3 replays que têm mão e compras completas.
**Não medido / limites:** (1) N pequeno: o IC95% da taxa total vai de 0,50 a 1,15 por turno, e o perfil usa a estimativa central; (2) o bot pode variar com o número de turnos, com o que o usuário joga ou com o tamanho da mesa dele (não testei); (3) a categoria de cada carta é minha, pelo oráculo; (4) o ataque dos oponentes a planeswalkers quase não aparece nos logs (nenhuma perda de lealdade por ataque que eu consiga ver), e no perfil ele sobra só quando passa o gate de atenção; (5) **o perfil não foi testado como substituto dos 3 humanos da mesa real**; (6) o tamanho das criaturas é o meu chute (a ficha Golem, Doombot etc. vem do Scryfall sem P/T no log); (7) não calibrei a escolha do alvo da remoção (3 das 5 remoções do playtester miram artefato/encantamento, e a resiliência de sempre mira planeswalker em 60%): com 5 eventos isso não se ajusta.
