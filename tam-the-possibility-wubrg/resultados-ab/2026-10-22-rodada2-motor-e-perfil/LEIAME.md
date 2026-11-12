# 2026-10-22 — Tam, rodada 2: turnos extras empilhados, ordem de pagamento, combo da mão, tetos e o perfil `playtester`

Origem: o goldfish manual #5 do usuário (11 blocos, 2026-10-21) e o pedido **"Termine tudo que falta!"**. O #5 revelou **duas lacunas de motor** que nenhuma auditoria carta-a-carta pegaria (o erro não mora na carta: mora na contagem de turnos extras e na ordem em que o simulador escolhe de onde tirar o mana) e deixou três pendências do `goldfish-log.md` §5 (tetos de 80 ativações / 60 magias por turno; combo Orrery + Tezzeret + Chain Veil só fechando com o pagamento já em campo; resiliência não calibrada pra mesa do usuário). Cada correção ficou atrás de uma chave; `False` nas quatro chaves de motor = o simulador do commit `b7c0e19` (rodada 1), **bit a bit**.

## Conclusão (medido, N = 10.000 pareado, sementes 3.000.000+i)

1. **As quatro correções de motor quase não mexem no resultado, nos dois modos. A linha de base muda em décimos de ponto, dentro do ruído, exceto os turnos extras.** `depois` × `antes` no modo padrão: mesa limpa até T8 / T9 / T10 **+0,21 ± 0,25 / +0,38 ± 0,29 / +0,16 ± 0,24 pontos**; na resiliência **+0,00 ± 0,07 / +0,11 ± 0,15 / +0,03 ± 0,22**. Só 77,2% (padrão) e 83,4% (resiliência) das partidas dão o mesmo resultado inteiro: elas mudam de caminho, mas o desfecho médio não se mexe.
2. **Turnos extras empilhados (`EXTRA_TURNS_STACK`) é o único efeito mensurável: +0,0465 ± 0,0048 turno extra jogado por partida (0,434 → 0,480) no padrão; +0,009 ± 0,002 na resiliência.** É a regra real da Ichormoon Gauntlet (cada `−12` é um turno extra) e a linha que o usuário jogou no #5 (T11 com 4 turnos extras seguidos). O efeito no resultado é nulo (mesa limpa até T10 −0,03 ± 0,03 pontos): turno extra só é jogado quando a partida já está ganha na maior parte das vezes.
3. **Ordem de pagamento (`VIVID_LAST` + `SIBLING_FIRST`)** muda 19,4% das partidas no padrão (80,6% idênticas) e traz **+0,010 ± 0,005 planeswalker no fim de T6 (3,140 → 3,150) e +0,014 ± 0,009 mana no T6**, mesa limpa até T10 +0,18 ± 0,24 pontos (dentro do ruído). Mecanismo: o Bloom Tender / Faeburrow Elder rende 1 mana por **cor** entre os permanentes; pagar com terrenos/rochas **antes** de virá-lo deixa a cor nova da magia (Pyromancer, R) entrar na conta dele, e a 2ª unidade do filtro (Fire-Lit Thicket, Sol Ring) deixa de desperdiçar um terreno. É a linha do T4 do #5 (Pyromancer + Necromancer com Bloom Tender) que o simulador não fechava.
4. **Combo da mão (`COMBO_CAST_PAYOFF_FROM_HAND`):** o combo Orrery + Tezzeret + Chain Veil montado agora conjura All Will Be One / Sanctum Lurker **da mão** (mana infinito paga) e fecha: **`m_combo_wins` 0,0082 → 0,0097 (+0,0015 ± 0,0008)**, 99,8% das partidas idênticas, pagamento conjurado da mão em 19 de 10.000 partidas no padrão (9 na resiliência). O combo monta em 2,87% das partidas (padrão) e 1,03% (resiliência); **antes** fechava em 0,82% e agora em 0,98%: o valor da peça era um piso, como a Regra #4 (adendo, item 3) previa.
5. **Os tetos de 80 ativações de lealdade / 60 magias por turno NÃO são o gargalo:** o de ativações aperta em **38 de 10.000 partidas (0,38%) no padrão e 14 (0,14%) na resiliência; o de magias em 0**. Com os tetos subidos para 400 / 300 (`tetos_altos`), 99,6% das partidas são idênticas às de 80 / 60; as 0,4% que mudam têm +0,06 ativação de planeswalker por partida e **mesa limpa até T10 −0,07 ± 0,05 pontos** (`resumos/comparacoes_entre_variantes.txt`; o sinal é de um ruído de 0,4% das partidas, não de efeito de modelo). Os tetos ficam em 80 / 60.
6. **Perfil `playtester` (`OPP_PLAYTESTER` + `OPP_CARD_MIX`, calibrado nos 5 logs; ver `../2026-10-22-calibracao-playtester/`):** no **padrão não muda nada de relevante** (mesa limpa até T10 +0,35 ± 0,31 pontos contra `depois`; só o número de magias do oponente muda); **na resiliência é a diferença entre dois mundos: mesa limpa até T8 / T9 / T10 0,41% / 1,77% / 4,99% → 5,79% / 19,43% / 40,16%** (`perfil` − `depois`: +5,4 / +17,7 / **+35,2 ± 1,0 pontos**), primeiro oponente fora até T8 6,8% → 34,2% (+27,4 ± 1,0), planeswalkers no fim de T6 1,64 → 2,55, e eu **nunca** morro (`died_any` 12,9% → 0,0%). A resiliência de sempre (arquétipos do Prismatic Bridge) é uma mesa hostil; o `playtester` é "o que o bot do Archidekt faz". **Não é "a mesa real dele"** (3 humanos).

### Tabela da linha de base nova (variante `depois`, N = 10.000; IC95% de proporção ≈ ±1 ponto no meio da distribuição)

| | padrão | resiliência | resiliência + `playtester` |
|---|---|---|---|
| mesa limpa até T8 / T9 / T10 / T12 | 15,4% / 43,1% / 68,7% / 90,3% | 0,4% / 1,8% / 5,0% / 17,8% | 5,8% / 19,4% / 40,2% / 73,8% |
| 1º oponente fora até T6 / T8 | 4,5% / 64,5% | 0,2% / 6,8% | 1,7% / 34,2% |
| Tam conjurada até T4 | 95,5% | 95,2% | 95,4% |
| planeswalkers no fim de T6 / T8 | 3,15 / 5,39 | 1,64 / 2,24 | 2,55 / 4,13 |
| mana disponível no T6 | 7,14 | 6,22 | 6,78 |
| ativações da Tam por partida | 1,086 | 0,583 | 1,098 |
| eu morri (vida ≤ 0) até T12 | 0% (oponente passivo) | 12,9% | 0,0% |

(Fontes: `resumos/resumo_descritivo_depois_10000.txt` e `resumo_descritivo_perfil_playtester_10000.txt`; o padrão com o perfil ligado é praticamente a coluna do padrão: mesa limpa até T10 69,0%.)

## O que mudou no código (`tam_goldfish_v1.py`, 100 linhas de diferença)

| chave (padrão) | o quê | de onde veio |
|---|---|---|
| `EXTRA_TURNS_STACK` (`True`) | `extra_turns_queued` é um **contador**: cada ativação do `−12` da Ichormoon Gauntlet soma 1 turno extra; `play_rounds` consome a fila. Antes era booleano: duas ativações no mesmo turno rendiam 1. | #5, T11: Jace, Domri, Vronos, Jace = 4 turnos extras seguidos |
| `VIVID_LAST` (`True`) | Em `pay_mana`, ao pagar uma magia que **acrescenta uma cor nova**, adia o Bloom Tender / Faeburrow Elder (`state._vivid_defer`) se as fontes que não são "vivid" bastam. Sem cor nova, paga como antes. (A 1ª versão, uma penalidade global em `_match`, quebrava os testes do goldfish #3 T4 e T10 e foi refeita.) | #5, T4: Pyromancer com 2 terrenos, depois o Bloom Tender rende 3, não 2 |
| `SIBLING_FIRST` (`True`) | O genérico sai primeiro de **pool flutuante e da unidade que sobra de uma fonte já tocada** (2ª unidade do filtro Fire-Lit Thicket, Sol Ring, Bloom Tender) antes de tocar outra fonte. | #5, T4: o Watery Grave era tocado por nada |
| `COMBO_CAST_PAYOFF_FROM_HAND` (`True`) | `try_infinite_combo`: com Orrery + Tezzeret + Chain Veil montados, conjura o pagamento (All Will Be One, Sanctum Lurker) que está **na mão**; sem pagamento na mão só registra a montagem. Métrica `m_combo_payoff_cast_from_hand`. | pendência do `goldfish-log.md` §5 |
| `OPP_PLAYTESTER` (`False`) + constantes `OPP_PLAYTESTER_*` | Perfil do oponente do playtester do Archidekt: criatura de oponente com prob. 0,118 por turno dele (3º turno em diante, no máx. 4), magias {0: 74%, 1: 24%, 2: 2%}, gate de atenção 0,143, fator de anulação 0,125. | `../2026-10-22-calibracao-playtester/` |
| `OPP_CARD_MIX` (`False`) | Efeito em massa em 4 variantes sorteadas (Cleansing Nova, Split Up, Damning Verdict, Promise of Loyalty) e anulação que deixa comprar (Vex, 50%). | idem |
| `aplica_perfil("playtester")` | Liga `OPP_PLAYTESTER` + `OPP_CARD_MIX` de uma vez. | idem |

O perfil usa **só chaves e constantes** (o harness `driver.py` não passa dicionário com chave inteira; `OPP_PLAYTESTER_SPELLS_PROB` é constante do módulo).

## Oráculo e rulings lidos ao vivo — `dados/scryfall_rulings_2026-10-22.json`

**Falha de processo, declarada:** a Regra #3 manda ler as rulings **antes** de escrever o código. Nesta rodada eu escrevi e validei o código primeiro e só li as rulings no fechamento (2026-10-22, resposta crua arquivada). Conferi o código contra cada uma delas depois; nenhuma contradiz:

- **Ichormoon Gauntlet** ("Planeswalkers you control have '[0]: Proliferate' and '[−12]: Take an extra turn after this one.'"): **uma** ruling (2023-02-04): *"Only one loyalty ability of each planeswalker may be activated per turn, no matter how many it has gained."* O simulador já limita a 1 ativação de lealdade por planeswalker por turno (`activated_loyalty_this_turn`); o #5 T11 tem 4 turnos extras pelos `−12` de Jace, Domri, Vronos e Jace de novo, **2 deles no mesmo turno** — por essa ruling, dois `−12` no mesmo turno só podem vir de planeswalkers diferentes, e o simulador antigo (booleano) dava 1 turno extra nesse caso. Cada `−12` resolvido é um turno extra; como todos são meus, a ordem entre eles não muda o resultado. Não há ruling de empilhamento no Scryfall para esta carta: o empilhamento sai do texto do oráculo (cada habilidade manda "take an extra turn"), não de uma ruling.
- **Bloom Tender** (Vivid): 5 rulings (2025-11-17): terreno é incolor (não conta como cor); **não produz incolor**; para cada uma das 5 cores confere-se se controlo um permanente daquela cor, e **o mesmo permanente conta para várias cores**; no máximo 1 mana de cada cor ({W}{U}{B}{R}{G}). É o que `colors_among()` já fazia (só W U B R G, ficha colorida conta, terreno incolor).
- **Faeburrow Elder**: 2 rulings (2019-10-04): no máximo +5/+5 e no máximo 5 mana; sendo verde e branca, rende no mínimo {G}{W}. Idem.
- **Vex** ("Counter target spell. That spell's controller may draw a card."): sem rulings. O "may draw" é o que o `OPP_CARD_MIX` modela (eu sempre compro quando posso).

Consequência de timing que a política usa e que **não** vem de ruling, e sim da ordem de uma conjuração: a magia que estou pagando ainda está na pilha quando o mana é gerado, então a cor dela **não** conta para o Bloom Tender nesse pagamento; só depois que ela resolve e vira permanente. Por isso `VIVID_LAST` adia o Bloom Tender *se* as outras fontes pagam: o Bloom Tender desvirado rende a cor nova na próxima magia do turno.

## Validação

| o quê | resultado | arquivo |
|---|---|---|
| testes dirigidos (182 anteriores + 17 da rodada 1 + 15 do #5 + 6 da rodada 2) | **220 passam, 0 falham** (na rodada 1 eram 212 com 2 falhas de propósito: as lacunas do #5 que esta rodada corrige) | `../../testes/` |
| smoke (99 cartas, 0 desconhecidas, 0 duplicadas, 200 partidas × 2 modos × 2 versões) | 0 exceções | `resumos/smoke.txt` |
| **bit-identidade:** vivo com as 4 chaves de motor = `False` == snapshot `b7c0e19` (sementes 5.000.000+i, impressão digital do resultado inteiro; campos novos ignorados) | **20.000 / 20.000 por modo, 0 diferenças** | `resumos/bitident_20000.txt` |
| A/B pareado `antes` × `depois` + 5 variantes (`so_turnos_extras`, `so_pagamento`, `so_combo_mao`, `tetos_altos`, `perfil_playtester`), N = 2.000 e 10.000 × 2 modos | tabelas acima; mesmas direções em N = 2.000 | `resumos/ab_*.txt` |
| descritivas da linha de base e do perfil, extras (tetos, combo, turnos extras) e comparações `tetos_altos` / `perfil_playtester` × `depois`, só dos brutos | usado | `resumos/resumo_descritivo_*`, `resumo_extra_*`, `comparacoes_entre_variantes.txt` |
| regressão 20.000 × 2 modos, `depois` e `chave_desligada` | **0 exceções, 0 carta acima do baralho, 0 campo negativo** nas 4 configurações; `Traceback` no `log_driver.txt`: 0 | `resumos/regressao_20000.txt` |
| determinismo: 3 `PYTHONHASHSEED` (11, 22, 33) × 1.500 sementes × 2 modos, campo a campo no estado final, **chaves de motor ligadas** e **com o perfil `playtester` ligado** (as duas baterias) | **0 sementes divergentes** nas 4 combinações; controle positivo: com as `FLAGS` do perfil o resultado de 40 sementes muda, então a 2ª bateria não é vácua | `resumos/determinismo.txt` |
| reprodutibilidade (tabelas refeitas só dos brutos `.json.xz`, `cmp`) | **10 de 10 saídas byte a byte iguais** (4 tabelas do A/B, 4 descritivas/extras, comparações entre variantes, índice). **`--tudo` (re-simulação de tudo, ~2 h) NÃO foi rodado nesta rodada** | `resumos/verificacao_reproducao.txt` |

## Mapa arquivo → o que é → status

| arquivo | o que é | status |
|---|---|---|
| `codigo/tam_goldfish_v1_ANTES_b7c0e19.py` (+ `tam_cartas.json`) | o simulador da rodada 1 (variante `antes`) | usado |
| `codigo/tam_goldfish_v1_DEPOIS_rodada2.py` | o simulador desta rodada (idêntico ao do repositório no commit da rodada; o `config.json` aponta para ele para a pasta ser verificável mesmo se o arquivo vivo mudar) | usado |
| `dados/scryfall_rulings_2026-10-22.json` | oráculo + rulings crus (Scryfall) de Ichormoon Gauntlet, Bloom Tender, Faeburrow Elder e Vex, lidos em 2026-10-22 | usado |
| `dados/raw_ab_2000[_resiliencia].json.xz`, `raw_ab_10000[_resiliencia].json.xz` | bruto por partida (colunas-v1), 7 variantes: `antes`, `depois`, `so_turnos_extras`, `so_pagamento`, `so_combo_mao`, `tetos_altos`, `perfil_playtester` | usado |
| `resumos/ab_*.txt` | A/B pareado de cada variante contra `antes` | usado |
| `resumos/resumo_descritivo_{depois,perfil_playtester}_10000.txt` | a linha de base (cada campo: média, IC95%, proporção) | usado (alimenta o `goldfish-log.md` §1) |
| `resumos/resumo_extra_{depois,perfil_playtester}_10000.txt` | tetos, combo, turnos extras, quartis | usado |
| `resumos/comparacoes_entre_variantes.txt` | `tetos_altos` e `perfil_playtester` pareados contra `depois` | usado |
| `resumos/{smoke,bitident_20000,regressao_20000,determinismo,indice_dados,verificacao_reproducao}.*`, `cadeia_horarios.txt`, `log_driver.txt` | validação e índice | usado |
| `orquestracao/` | `driver.py`, `abgen.py`, `config.json`, `cadeia.sh`, `resumo_variante.py`, `resumo_extra_variante.py`, `comparacoes.py`, `verificar_reproducao.sh` | usado |

## Como refazer

```
bash descomprimir.sh                                                          # .json.xz -> dados_json/ (fora do git)
cd orquestracao
python3 resumo_variante.py depois 10000 | cmp - ../resumos/resumo_descritivo_depois_10000.txt
python3 resumo_extra_variante.py depois 10000 | cmp - ../resumos/resumo_extra_depois_10000.txt
python3 comparacoes.py | cmp - ../resumos/comparacoes_entre_variantes.txt
bash verificar_reproducao.sh                                                  # tabelas do A/B, descritivas, extras, comparações e índice: cmp byte a byte (~4 min)
bash verificar_reproducao.sh --tudo                                           # re-simula smoke, bit-identidade, regressão e os 4 lotes do A/B (~2 h; não mude o `config.json`)
sha256sum -c ../SHA256SUMS                                                    # integridade
```

## Escopo (Regra #7)

**Varrido:** (a) as 4 correções de motor contra o #5, cada uma com teste dirigido (6 novos), bit-identidade com chave desligada e A/B pareado; (b) os tetos, medidos em 20.000 partidas; (c) a fração de partidas em que o combo monta e fecha; (d) o perfil contra as taxas dos 5 logs (pasta da calibração).
**Não varrido / limites:** (1) **uma só classe de ordem de pagamento foi tratada** (mana "vivid" e unidade irmã): não varri outras fontes cujo valor depende da ordem (ex.: Chromatic Orrery, filtros que dependem de cor já em pool, terrenos de 2 cores tocados antes de um "any color" que seria mais barato); (2) `OPP_PLAYTESTER` / `OPP_CARD_MIX` ficam **desligados por padrão**: o §1 do `goldfish-log.md` publica as duas linhas (padrão e resiliência de sempre) e a do perfil lado a lado, e nenhuma dessas três é "a mesa do usuário"; (3) o IC95% dos pontos percentuais acima é de 10.000 partidas pareadas; **uma só família de sementes**; (4) o número de turnos extras "tomados" é por partida, não por turno: partidas com ≥ 2 `−12` no mesmo turno não são identificáveis no bruto (o `m_extra_turns_taken` conta ativações, o `m_extra_turns_played` conta turnos jogados).
