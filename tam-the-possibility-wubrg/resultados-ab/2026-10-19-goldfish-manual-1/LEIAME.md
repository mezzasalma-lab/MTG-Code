# Goldfish manual #1 do Tam (jogado pelo usuário no playtester do Archidekt) — 2026-10-19

Arquivado conforme a Regra #8 da CLAUDE.md. **O que é:** o log que o usuário colou na conversa (*"Fiz um goldfish manual do deck da Tam como está"*), a lista `lista.md` sem nenhuma troca, 10 turnos, com o playtester do Archidekt (que simula interações de oponente). Prometi não mexer no log até as respostas; elas chegaram em 2026-10-19 e estão abaixo, literais.

## Respostas do usuário às 5 perguntas (literais)

1. *"Sim, no commander sempre há compra no 1o turno (mais de 2 jogadores)"*
2. *"O playtester do Archidekt tem simulador de interações, então ele simula ataques, counters e outras interações. Golem me atacou e Aetherize só afeta criaturas atacando, eu não ataquei nesse simulador."*
3. *"Foi uma redução de -12 para jogar um turno extra"* (a ficha de Jace foi de 13 para 1: o `[−12]` do Ichormoon Gauntlet)
4. *"Vronos 152 foi erro. Os contadores Indestructible, Vigilance e Can't be blocked no arcane signet foram do Ultimate do Vronos. Os proliferate não foram da Tam, mas sim do (0) Proliferate que o Ichormoon dá a todos os meus PW! Com o Oath of Teferi posso usar ele até 2x por turno meu!"*
5. *"As 8 cartas iniciais sâo as 7 iniciais mais a primeira compra no turno 0"*
   Antes (na mensagem original): *"Todas as instâncias de undo foram erros meus"*.

**Efeito no simulador:** a resposta 1/5 tornou o `tam_goldfish_v1.py` compra no T1 (chave `FIRST_TURN_SKIPS_DRAW = False`; commit "Tam: compra no 1o turno"); antes ele pulava (eu tinha herdado o `if turn == 1 and on_play` do Mothman). A resposta 4 confirma que a Tam **não ativou** neste jogo (morreu no T8 e voltou no T9 com doença de invocação) e que os proliferates vieram do Gauntlet `0` com o Oath of Teferi (2× por planeswalker por turno): é a mecânica de `testes/t_manual1.py`.

## Arquivos

| arquivo | o que é | status |
|---|---|---|
| `dados/mensagem_usuario_original.txt` | a mensagem inteira como chegou (texto + JSON + a frase final) | bruto, intocado |
| `dados/goldfish_manual_1_bruto.json` | só o JSON do log: 10 blocos (um por turno), cada evento = movimento de carta/contador no playtester | bruto, intocado |
| `dados/fichas_do_oponente_scryfall.json` | Scryfall: **Golem** e **Doombot** do log são FICHAS 3/3 de artefato (não cartas; o cache do repositório não guarda fichas), as outras 4 cartas de oponente (Nature's Claim, Assassin's Trophy, Witness Protection, Aetherize) já estão no `oracle-cache.json` | bruto |
| `orquestracao/linha_do_tempo.py` → `resumos/linha_do_tempo.md` | resumo por turno, **só do bruto** (compras, terreno, magias, buscas, saídas, cartas do oponente, última lealdade do bloco) | usado |
| `orquestracao/replay_manual_1.py`, `replay_stats.py` → `resumos/replay_padrao_300.txt`, `replay_resiliencia_300.txt` | o simulador jogando as MESMAS 18 cartas na MESMA ordem (resto do baralho em 300 ordens) | usado |
| `testes/t_manual1.py` (na pasta do deck) | 9 testes que reproduzem as jogadas dele | 9/9 passam |

Reproduzir: `python3 orquestracao/linha_do_tempo.py`; `python3 orquestracao/replay_stats.py 300 padrao` (e `resiliencia`); `python3 testes/rodar_testes.py` na pasta do deck. Código: commit do `tam_goldfish_v1.py` ao fim da rodada (ver `resultados-ab/2026-10-19-simulador-baseline/LEIAME.md`).

## O jogo do usuário (da `resumos/linha_do_tempo.md`)

Mão inicial de 8: Windswept Heath, Onakke Oathkeeper, Leyline Immersion, Baxter Building, Wooded Bastion, Ichormoon Gauntlet, Way of the Pyromancer, Plaza of Heroes. Compras seguintes, na ordem: City of Brass, Spire Garden, Vronos, Bloom Tender, Liliana's Talent, Way of the Paradox (+ Overgrown Tomb pelo `-3` da ficha de Jace), Tezzeret, Oath of Teferi, Sanctum Lurker.

| fim do turno | planeswalkers | o que aconteceu (do log) |
|---|---|---|
| T1 | 0 | Heath → Indatha Triome (virado) |
| T2 | 0 | Wooded Bastion; Onakke Oathkeeper |
| T3 | Jace 3 | Spire Garden; Way of the Pyromancer (a ficha de Jace aparece com 1, 2 e 3 no log; leitura minha: empower 2 + um `+1` concedido pela Pyromancer) |
| T4 | Jace 4 | Plaza of Heroes; **Tam** (T4); Pyromancer `+1` de novo; oponente: Nature's Claim |
| T5 | Jace 3 | Baxter Building; Bloom Tender, Ichormoon Gauntlet; Pyromancer sai do campo (Nature's Claim); Bloom Tender morre (Assassin's Trophy) |
| T6 | Vronos 7, Jace 5 | City of Brass; **Vronos** (primeiro planeswalker de carta); oponente: Golem |
| T7 | Vronos 8, Jace 8 | Way of the Paradox (empower 5) e Liliana's Talent; Overgrown Tomb como 2ª terra do turno |
| T8 | Tezzeret 4, Vronos 10, Jace 11 | Tezzeret (`-X` com X=1 busca **Sol Ring**); Leyline Immersion; oponente: Witness Protection e Doombot; **a Tam morre** (Immersion junto) e volta com imposto 1 |
| T9 | Tezzeret 7, Vronos 5, Jace 1 | Oath of Teferi (exila o Tezzeret: volta no end step); Tezzeret `-X` com X=2 busca **Arcane Signet**; Jace 13 → 1 (`-12`: **turno extra**); **Vronos `-7` (12 → 5)** no Arcane Signet; Tam recastada (imposto 1); oponente: Aetherize |
| T10 (turno extra) | Tezzeret 13, Vronos 11, Jace 7 | Sanctum Lurker; muitos `0: Proliferate` do Gauntlet (2× por PW com o Oath) |

O log **não tem vida de oponente**: não há "vitória" nem dano registrado, então não dá para comparar mesa limpa; só desenvolvimento de mesa.

## Cada cláusula operacional do relato é uma afirmação testável (Regra #6)

| o que o usuário fez | teste em `testes/t_manual1.py` | resultado |
|---|---|---|
| Pyromancer `+1` na ficha de Jace (2 → 3 → 4) | `Way of the Pyromancer da' +1 {R} tambem a ficha de Jace` | ✅ |
| Jace 13 → 1 com o `-12` do Gauntlet e turno extra | `Jace com 13 usa o -12 do Ichormoon Gauntlet` | ✅ |
| Gauntlet `0` 2× por PW com o Oath of Teferi (não 3×) | `com Oath of Teferi o '0: Proliferate' ... 2x por planeswalker` | ✅ |
| Tezzeret `-X` X=1 → Sol Ring, X=2 → Arcane Signet | `Tezzeret -X com X=1 busca Sol Ring e com X=2 busca Arcane Signet` | ✅ |
| Oath exila o Tezzeret que já ativou; volta no end step como objeto novo (lealdade 4) | `Oath of Teferi exila o Tezzeret...` | ✅ |
| Vronos `-7` (12 → 5) no Arcane Signet: 9/9, indestrutível, vigilância, não bloqueável | `Vronos -7 em Arcane Signet` | ✅ |
| Tam morre com a Immersion, volta à zona de comando, imposto | `a Tam morre (a Leyline Immersion vai junto)...` | ✅ |
| Paradox + Jace `-3` → 2ª terra (Overgrown Tomb) | `Way of the Paradox + Jace -3 (compra)...` | ✅ |
| Onakke Oathkeeper com Bastion + Triome no T2 | `a ordem do turno do usuario ... e' legal` | ✅ |

Nenhuma jogada do relato exigiu mudar regra do simulador além da **compra do T1**.

## O simulador jogando as mesmas cartas (não é validação: a IA joga diferente do usuário)

Mesma mão e mesmas 10 compras, resto do baralho em 300 ordens, a IA do simulador decide (`resumos/replay_*_300.txt`):

| | usuário | simulador, modo padrão (mediana) | simulador, resiliência (mediana) |
|---|---|---|---|
| Tam em campo | T4 | T3 | T3 |
| planeswalkers no fim do T6 / T8 / T10 | 2 / 3 / 3 | 1 / 2 / 4 | 1 / 1 / 1 |
| 1ª ultimate | T9 (Vronos) | T6 (300/300 partidas) | T8 (148/300) |

**Leitura (limites):** o simulador desenvolve a mesa mais rápido que o usuário com as mesmas cartas no modo padrão (IA que conjura o que dá a cada turno, sem oponente real), e mais devagar na resiliência (remoção, wipes, descarte, anulação de magia e ataque a planeswalker). O usuário jogou com o playtester do Archidekt, que também interage (Nature's Claim, Assassin's Trophy, Witness Protection...): a resiliência é a referência mais próxima, e lá a mediana de planeswalkers fica em 1. Isto **não** diz qual está certo: são 1 jogo humano e 300 ordens do resto do baralho, com interação de oponente modelada de formas diferentes. A diferença mais clara de política (conferida em 60 ordens do replay: 60/60): o simulador usa a Vronos `-7` assim que ela chega a 7 de lealdade, **ela morre** (0 de lealdade) e fica um 9/9 não bloqueável; o usuário esperou a Vronos chegar a 12 e ficou com ela viva (5). É a política "toda ultimate é usada assim que paga" do simulador, não uma regra: vale discutir se a Vronos deveria esperar o proliferate.

## Achado lateral (Regra #10, escopo declarado)

A resposta 1 expôs uma inconsistência no repositório: o comentário *"Achado real 2026-09-18: 'skip the draw step' no 1o turno só existe na regra 1x1 (CR 103.8a). Commander é sempre multiplayer"* está em Maralen, Kutzil, Hei Bai, Megatron, Nekusar, Rat King, Ulalek, Ur-Dragon e Vihaan, mas o **Mothman** ainda tem `if state.turn == 1 and state.on_play: return` no `draw_step` e eu confirmei por execução que ele não compra no T1 (`draws_by_source` vazio após 1 turno; mão de 5 depois de jogar terra e uma magia). **Não verificado:** Azula, Beorn, Captain Storm, Edgar, Prismatic Bridge, Thranduil, Tom, Toph, Bumbleflower. Nada foi alterado fora do Tam; ver a proposta no relatório final.

## Escopo (Regra #7)

**Comparado:** a linha do tempo inteira contra as regras do simulador (9 testes), e o desenvolvimento de mesa com as mesmas cartas. **Não comparado:** vida e dano de oponente (o log não tem); decisões de mana por ativação (o log só mostra terrenos virados, não qual mana pagou o quê); os turnos de oponente do playtester (só aparecem os nomes das cartas deles); a interpretação de qual carta o Nature's Claim destruiu (o log mostra a Pyromancer saindo para o exílio no T5, não o motivo).
