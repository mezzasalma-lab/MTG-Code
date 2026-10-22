# Goldfish manual #5 do Tam (jogado pelo usuário no playtester do Archidekt) — 2026-10-21/22

Arquivado conforme a Regra #8 da CLAUDE.md. **O que é:** o log que o usuário colou na conversa (*"Mais um Goldfish:"*), a `lista.md` sem nenhuma troca, **11 blocos (T1 a T11)**, sem foto. O usuário numera os turnos a partir de 0; aqui "T1" é o 1º bloco.

## O que o usuário escreveu (literal)

> *"Nesse esqueci muitos gatilhos da Ichormoon, mas depois do 3o emblema no campo fica impossível perder proliferando e jogando turnos extras!"*

## Dúvidas NÃO respondidas (o usuário mandou *"Termine tudo que falta!"* em vez de responder)

No #1 ele pediu *"me pergunte qq dúvida antes de começar a compilar qq coisa"*. Eu ia perguntar; ele respondeu **"Termine tudo que falta!"**, então **compilei sem as respostas** e deixei cada ambiguidade marcada abaixo com a premissa usada. Se alguma premissa estiver errada, é só dizer: nenhuma conclusão depende dela.

| # | o que o log mostra | premissa que usei | onde pesa |
|---|---|---|---|
| 1 | T1: 7 cartas na abertura, **2 devolvidas à biblioteca** (The Chain Veil, Narset Transcendent), compra do T1 (Way of the Paradox) | mulligan até **5 cartas**; as 2 foram para o **fundo**; o log não diz quantos mulligans foram (2, ou 3 contando o 1º grátis) | o replay começa com a mão de 5 |
| 2 | T4: com Promenade, Thicket, Watery Grave e Bloom Tender sobravam **7 mana** (teste `Manual #5 T4`): Pyromancer (2) + Paradox (3) + **Way of the Necromancer** ({1}{B}), e a Necromancer ficou na mão | foi **escolha** dele (ou esquecimento); não é limite de regra | só descrição |
| 3 | T7: Tam conjurada com imposto 1 e **de volta à zona de comando** na hora (imposto 2); a carta de oponente **Ertai's Scorn** (`Counter target spell`) aparece no bloco anterior (T6), o mesmo padrão da Vex do #4 (aparece no bloco antes da magia anulada) | a Tam foi **anulada** pela Ertai's Scorn | o Garruk (5) ficou sem o desconto da Tam e só entrou no T8 |
| 4 | T7: Vronos 4→5→4→3→4 (líquido 0); City of Brass e Promenade viradas e desviradas | cliques **desfeitos**, nenhuma ativação | só descrição |
| 5 | T10: Jace 5→**1**→10; T11: Jace 13→1 (−12)→**10** | o `1` é um passo do contador da interface (adicionar contador); o valor final (10) é o que vale | só descrição |
| 6 | T10: Teferi, Temporal Archmage 5→4→3 (`−1` duas vezes) | o mesmo erro do #4 (esperava `−2`; o Teferi TA só tem `−1`): uma ativação por turno, o certo é 4 | erro de regra do relato |
| 7 | T9: o Damning Verdict do oponente ("destroy all creatures with no counters") matou o Kitten e 2 Beasts (3 criaturas); a Way of the Necromancer deu **+1** em cada planeswalker | pela regra seriam **+3** (uma por criatura morta); ele esqueceu 2 | erro de regra do relato |
| 8 | T10 e T11: os `0: Proliferate` do Gauntlet não aparecem no log (custo 0); o comentário dele diz que **esqueceu muitos gatilhos do Ichormoon** | não sei quais proliferates e quais contadores de gatilho (a cada magia não-criatura) ele deixou de fazer | só descrição |

## Arquivos

| arquivo | o que é | status |
|---|---|---|
| `dados/mensagem_usuario_original.txt` | a mensagem inteira como chegou (texto + JSON + a nota final), extraída do transcript da sessão, sem retocar | bruto, intocado |
| `dados/goldfish_manual_5_bruto.json` | só o JSON do log: 11 blocos (11, 5, 8, 14, 14, 20, 28, 29, 34, 59, 128 eventos), cada evento = movimento de carta/contador/virada no playtester | bruto, intocado |
| `orquestracao/linha_do_tempo.py` → `resumos/linha_do_tempo.md`; `orquestracao/eventos_compactos.py` → `resumos/eventos_compactos.txt`; `orquestracao/deltas_lealdade.py` → `resumos/deltas_lealdade.txt` | resumos por turno e por evento e a sequência de mudanças de lealdade, **só do bruto** | usado |
| `orquestracao/replay_manual_5.py` → `resumos/replay_semente_{1,2,3}.txt` (+ `../2026-10-22-calibracao-playtester/orquestracao/replay_perfil.py`, que faz o replay em 300 ordens) | o simulador jogando as MESMAS cartas na MESMA ordem | usado |
| `testes/t_manual5.py` (na pasta do deck) | os testes das jogadas dele pelas regras | ver abaixo |

O oráculo de **Ertai's Scorn, Goblin Wizard e Eldrazi Angel** (cartas/fichas de oponente do T5, T6 e T10) entrou em `scryfall-cache/oracle-cache.json` (Regra 15); Loran of the Third Path, Damning Verdict, Promise of Loyalty já estavam.

## O jogo do usuário (da `resumos/linha_do_tempo.md` e dos `deltas_lealdade`)

Abertura: mão de 5 (Way of the Pyromancer, Bloom Tender, Fire-Lit Thicket, Ripples of Potential, Bountiful Promenade) + Way of the Paradox na compra do T1. **Só 7 terrenos jogados no jogo todo** (Fire-Lit Thicket, Promenade, Watery Grave, Ketria Triome, City of Brass, Overflowing Basin, Mossfire Valley; a Plaza of Heroes foi comprada e não jogada): o desenvolvimento veio do Bloom Tender, dos planeswalkers (Jace `+1`, Domri `+1`) e da cor dos permanentes.

| fim do bloco | planeswalkers | o que aconteceu |
|---|---|---|
| T1 | 0 | Fire-Lit Thicket |
| T2 | 0 | Promenade (desvirada: 3 oponentes); Bloom Tender |
| T3 | 0 | Watery Grave (2 de vida); **Tam** |
| T4 | 1 (Jace) | **Pyromancer** (Jace 2) + Jace `+1` ({R}, 3) + **Way of the Paradox** (Jace 8); Necromancer na mão |
| T5 | 2 | Jace `−3` (compra o Ketria Triome); **Vronos** (4 com a Tam) `+1`; oponente: Goblin Wizard |
| T6 | 2 | **Way of the Necromancer** (Jace +2); Vronos `−2`; Jace `−3` (compra o Teferi, Hero); oponente: **Ertai's Scorn** e **Promise of Loyalty** (a Tam é sacrificada: zona de comando; o Bloom Tender fica com o contador Vow) |
| T7 | 2 | City of Brass; **Tam anulada** (Ertai's Scorn), imposto 2; Jace `−3` (compra o Garruk) |
| T8 | 4 | **Garruk** (5) `−3`: Beast 4/4 e o Garruk compra a Domri; **Domri** (4 mana; o Bloom Tender foi tocado); oponente: Loran destrói a Way of the Paradox |
| T9 | 5 | **Displacer Kitten**; **Teferi, Hero** com o gatilho do Kitten: pisca o Garruk (5) e o `−3` de novo (2º Beast); Teferi `+1` compra o Teferi TA; oponente: **Damning Verdict** (o Kitten sai do campo no log; os Beasts morrem pelo oráculo, o log não registra a saída de ficha) |
| T10 | 7 | **Ichormoon Gauntlet**; **Teferi TA** (`−1` ×2, erro), Tamiyo, Teferi `+1` (compra a Deathbringer), **Way of the Deathbringer** (Jace +5), Jace `−3` (compra a Elspeth); 2 proliferates (1 de `0: Proliferate`, 1 da **Ripples of Potential**); Garruk `−3`, Tamiyo `−2`; oponente: Eldrazi Angel |
| T11 | 11 | **4 turnos extras** pelo `−12` do Gauntlet (Jace, Domri, Vronos e Jace de novo; 2 no mesmo turno): Sanctum Lurker, Mossfire Valley, Kasmina, Tam (imposto 2), Sol Ring, Arcane Signet, Elspeth, Eternal Wanderer, Aminatou; **3 emblemas**: Teferi, Hero `−8` (9→1), Teferi TA `−10` (11→1), Tamiyo `−7` (11→4, compra 3: Sol Ring, Plaza, Signet); **7 proliferates** (contados pelo contador Vow do Bloom Tender, que ele incluiu em todos: V3→V10; a Vronos sobe 10→16 em 7 passos); lealdades até 16 (Vronos) |

O log **não tem vida de oponente**: não há "vitória" nem dano registrado; só desenvolvimento de mesa.

## Cada cláusula operacional do relato é uma afirmação testável (Regra #6)

| o que o usuário fez | teste em `testes/t_manual5.py` | resultado |
|---|---|---|
| T2: Promenade desvirada (3 oponentes); Promenade + Thicket (filtro) pagam o Bloom Tender | `Manual #5 T2` | ✅ |
| T3: Tam com Promenade + Thicket + Watery Grave (2 de vida) | `Manual #5 T3` | ✅ |
| T4: Pyromancer (Jace 2), Jace `+1` ({R}), Bloom Tender com 3 cores, Paradox (Jace 8) | `Manual #5 T4: Pyromancer ...` | ✅ |
| T4: sobrava mana para a Necromancer (Watery Grave + 1 flutuante) e ela ficou na mão | `Manual #5 T4 (DUVIDA)` | ✅ **só depois da rodada 2** (`SIBLING_FIRST`): o simulador antigo pagava a Pyromancer tocando o Bloom Tender com 2 cores e deixava 1 mana flutuando; a ordem de pagamento era a lacuna |
| T5: Jace `−3` compra; Vronos (4 com a Tam) com Bloom Tender + Grave | `Manual #5 T5` | ✅ |
| T6: Necromancer (Jace +2), Vronos `−2`, Jace `−3`; Teferi, Hero não cabia (sem `{W}`) | `Manual #5 T6: Way of the Necromancer ...` | ✅ |
| T6 (oponente): Promise of Loyalty sacrifica a Tam (zona de comando) e o Bloom Tender fica com Vow | `Manual #5 T6 (opp)` | ✅ (o efeito do oponente é imposto na mão do teste; o simulador modela a variante Promise do wipe só no perfil `playtester`) |
| T7/T11: imposto do comandante = {2} por conjuração anterior | `Manual #5 T7/T11` | ✅ |
| T8: Garruk (5), `−3`: Beast 4/4, o Garruk compra (a Domri); Domri só com o Bloom Tender | `Manual #5 T8` | ✅ |
| T9: Kitten + Teferi, Hero: pisca o Garruk (5, objeto novo), `−3` de novo, compra | `Manual #5 T9: Displacer Kitten ...` | ✅ |
| T9 (oponente): Damning Verdict poupa o Bloom Tender (Vow); Necromancer dá +1 por criatura morta em cada planeswalker | `Manual #5 T9 (opp)` | ✅ pela regra (3 mortes = +3; o log tem +1) |
| T10: Teferi TA `−1` desvira 4; uma ativação por turno | `Manual #5 T10: Teferi, Temporal Archmage ...` | ✅ (o log tem 2 cliques: erro do relato) |
| T10: Gauntlet: um gatilho por magia não-criatura (3 de 3) e `0: Proliferate` em cada planeswalker | `Manual #5 T10: Ichormoon Gauntlet ...` | ✅ |
| T11: 3 emblemas (Teferi, Hero `−8`; Teferi TA `−10`; Tamiyo `−7` com 3 compras e magia grátis) | `Manual #5 T11: emblemas` | ✅ |
| T11: 4 turnos extras pelos `−12` (2 no mesmo turno) | `Manual #5 T11: cada -12 ...` | ✅ **só depois da rodada 2** (`EXTRA_TURNS_STACK`): o simulador antigo guardava um booleano e dava 1 turno extra por turno |

**Duas lacunas reais do simulador vieram deste log** (Regra #1/#5, nenhuma é do usuário): a ordem em que o Bloom Tender e o filtro são tocados (`SIBLING_FIRST`, `VIVID_LAST`) e o empilhamento dos turnos extras do `−12` (`EXTRA_TURNS_STACK`); ver `../2026-10-22-rodada2-motor-e-perfil/LEIAME.md`.

## O simulador jogando as mesmas cartas (não é validação: a IA joga diferente do usuário)

Mão de 5 (a do log depois do mulligan) e as compras na ordem do log (as que ficaram com ele, inclusive as de habilidade), resto do baralho em 300 ordens (`orquestracao/replay_manual_5.py`; o replay em escala e a comparação com os modos de oponente estão em `../2026-10-22-calibracao-playtester/` (`replay_perfil.py`, `resumos/replay_jogo5_*`); `resumos/replay_semente_{1,2,3}.txt` mostram 3 partidas inteiras do modo padrão). Planeswalkers em campo no fim de cada turno (mediana de 300; entre parênteses P(simulador ≥ usuário)):

| turno | T4 | T5 | T6 | T7 | T8 | T9 | T10 |
|---|---|---|---|---|---|---|---|
| **usuário** | 1 | 2 | 2 | 2 | 4 | 5 | 7 |
| simulador, modo padrão (oponente passivo) | 1 | 2 | 4 | 7 | 11 | 13 | 16 |
| simulador, resiliência de sempre | 1 (62%) | 1 (19%) | 1 (24%) | 1 (36%) | 2 (24%) | 3 (21%) | 3 (15%) |
| **simulador, resiliência com o perfil `playtester`** | 1 (93%) | 2 (67%) | 2 (66%) | 4 (80%) | 4 (52%) | 8 (86%) | 10 (80%) |
| Tam em campo (mediana) | usuário T3 | | | | | | simulador T3 (todos os modos) |

**Leitura (limites):** (1) o **modo padrão** corre muito além do usuário (16 contra 7 no T10): a IA do simulador joga todas as cartas que o mana paga e usa as compras de habilidade na hora; o usuário jogou com 7 terrenos, **teve a Tam anulada no T7**, deixou a Necromancer na mão no T4 e, pelas palavras dele, esqueceu muitos gatilhos do Ichormoon. (2) A **resiliência de sempre** fica abaixo do usuário (mediana 3 contra 7 no T10): é uma mesa mais hostil do que a do playtester dele (ver a calibração). (3) Com o **perfil `playtester`** a trajetória do simulador **acompanha a do usuário nos T4–T8** (medianas 1/2/2/4/4 contra 1/2/2/2/4) e fica **acima** nos T9–T10 (8 e 10 contra 5 e 7): coerente com o que ele disse (esqueceu gatilhos) e com os erros de regra do relato (Teferi TA `−1` ×2, Necromancer +1 em vez de +3). (4) **Isto não valida o simulador**: é 1 jogo humano contra 300 ordens do resto do baralho, e o perfil foi ajustado nas taxas de oponente dos 5 logs, inclusive este.

## Escopo (Regra #7)

**Comparado:** a linha do tempo inteira (T1–T10) contra as regras do simulador (os testes de `t_manual5.py`), as 8 dúvidas acima como premissas, e o desenvolvimento de mesa com as mesmas cartas.
**Não comparado / não resolvido:** vida e dano de oponente (o log não tem); a ordem exata das ~130 ações do bloco T11 (4 turnos num bloco só: os turnos extras foram reconstruídos pelas ativações de `−12` e pelo untap); quais proliferates e gatilhos do Gauntlet ele fez (os `0` não aparecem); o que mais ele faria depois do T11 (o log termina no Aminatou, que ele jogou no 4º turno extra).
