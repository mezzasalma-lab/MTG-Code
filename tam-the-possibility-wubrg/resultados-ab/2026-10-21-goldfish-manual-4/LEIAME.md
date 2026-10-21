# Goldfish manual #4 do Tam (jogado pelo usuário no playtester do Archidekt) — 2026-10-21

Arquivado conforme a Regra #8 da CLAUDE.md. **O que é:** o log que o usuário colou na conversa (*"Mais goldfish manual. Mão inicial na foto"*), com a foto da mão, a `lista.md` sem nenhuma troca, 10 blocos (T1 a T10; o T10 é um **turno extra**), com o playtester do Archidekt (simulador de interações de oponente). Mesma rotina dos #1 a #3: listei as dúvidas antes de interpretar; as respostas estão abaixo, literais.

## O que o usuário escreveu (literal)

Junto do log: *"Ignorei a interação entre o turno 8 e o 9 pq usei 12 de lealdade da Nissa para ter mais um turno com a habilidade da Ichormoon. TB usei muitos (0) Proliferate da Ichor!"*

Às dúvidas:
- **0) Numeração:** *"Sim, turno 0 é o primeiro."* (o "turno 8 e 9" dele são os meus **T9 e T10**; o T10 é o turno extra do `−12` da Nissa no T9, sem turno de oponente no meio)
- **1) Elspeth (T6):** primeiro *"Elspeth foi erro, desfiz"*; depois, corrigindo: ***"A Elspeth foi countered pela Vex e comprei uma carta!"***
- **2) Teferi (T7):** *"Teferi era para ser −2, eu cliquei duas vezes no −1 para chegar lá!"*
- **3) Teferi `+1`:** *"Teferi +1 não é compra uma carta e coloca uma carta no fundo da biblioteca?"*; depois: ***"Fiz o Teferi errado no +1 então, eu não olhei as 2 do topo!"***
- **4) Garruk Curse Breaker (T9):** *"Eu cliquei antes de virar os terrenos, por isso desfiz e fiz de novo."*

**Como li cada resposta (leitura minha, marcada como tal):**
- **Turnos do log:** T1..T10 do log = turnos 0..9 do usuário. O T10 é o turno extra; a Cleansing Nova que aparece no fim do T9 não aconteceu antes dele e foi ignorada pelo usuário.
- **Elspeth (T6):** foi **anulada** pela **Vex** (`Instant {2}{U}`, Scryfall: *"Counter target spell. That spell's controller may draw a card."*); a carta que a Vex deixa comprar é a **Garruk, Veiled Butcher**. O `hand→battlefield` e o `battlefield→graveyard` do log são a forma de o playtester representar "anulada". O Twilight Mire e o Ketria Triome indo ao cemitério no fim do T6 ficam **sem explicação** (o usuário não os comentou).
- **Teferi, Temporal Archmage tem `+1`, `−1` e `−10`: não existe `−2`.** Duas ativações no mesmo turno só com Chain Veil ou Oath (nenhum em campo). **Tratei o T7 como um `−1` só (lealdade 4)**; o log passou o Teferi a 3, **1 abaixo do que a regra dá** daí em diante.
- **Teferi `+1` (T8, T9, T10) foi jogado errado:** o oráculo é *"Look at the top two cards of your library. Put one of them into your hand and the other on the bottom of your library"* (+1 carta na mão por ativação); no jogo dele entrou uma carta e voltou outra ao fundo (Mossfire Valley no T8, Staff of Compleation no T9, sem evento no T10), e a mão não cresceu. O jogo real teria **3 cartas a mais** na mão em T10. Não corrigi o log (as cartas a mais são desconhecidas).
- **Ajani `−2` (T10):** o log mostra 7 compras com 7 criaturas, mas o gatilho do próprio Ajani ("whenever you activate a loyalty ability, create a Cadet") resolve **antes** do `−2`, então a regra dá **8 compras**; o usuário criou os Cadets em lote depois. O simulador faz as 8.
- **Garruk Curse Breaker (T9):** `hand→battlefield` duas vezes = undo; conta uma vez (4 de mana).

## Arquivos

| arquivo | o que é | status |
|---|---|---|
| `dados/mensagem_usuario_original.txt` | a mensagem inteira como chegou (texto + JSON + a nota final), extraída do transcript da sessão, sem retocar | bruto, intocado |
| `dados/goldfish_manual_4_bruto.json` | só o JSON do log: 10 blocos, cada evento = movimento de carta/contador/virada no playtester | bruto, intocado |
| `dados/mao_inicial_foto.png` | a foto da mão inicial anexada pelo usuário (Ajani Unrelenting, Teferi Temporal Archmage, Nissa Ascended Animist, Indatha Triome, Ichormoon Gauntlet, Starting Town, Ketria Triome) | bruto |
| `dados/fichas_scryfall.json` | Scryfall: fichas Graveborn (3/1), Spider, Phyrexian Horror (`*/*`: X = lealdade da Nissa), Cadet, Beast 4/4; e a carta **Vex** (também gravada em `scryfall-cache/oracle-cache.json`, Regra 15) | bruto |
| `orquestracao/linha_do_tempo.py` → `resumos/linha_do_tempo.md`; `resumos/eventos_compactos.txt` | resumo por turno, **só do bruto** | usado |
| `orquestracao/replay_manual_4.py`, `replay_stats4.py` → `resumos/replay_{padrao,resiliencia}_300.txt`, `…_300_cores_livres.txt`, `replay_semente_{1,2,3}.txt` | o simulador jogando as MESMAS 18 cartas na MESMA ordem (resto do baralho em 300 ordens) | usado |
| `testes/t_manual4.py` (na pasta do deck) | 11 testes das jogadas dele pelas regras, já com as correções | 11/11 passam (182/182 no total) |

**Reprodutibilidade (verificada com `cmp`, 8 de 8 idênticos):** `linha_do_tempo.md` refeita só do bruto; `replay_{padrao,resiliencia}_300.txt`, `replay_{padrao,resiliencia}_300_cores_livres.txt` e `replay_semente_{1,2,3}.txt` refeitos pelo simulador vivo. Integridade: `sha256sum -c SHA256SUMS`.

## O jogo do usuário (da `resumos/linha_do_tempo.md`, com as correções)

Mão inicial de 8 (7 da foto + compra do T1 = Flooded Grove): Ajani Unrelenting, Teferi TA, Nissa, Indatha Triome, Ichormoon Gauntlet, Starting Town, Ketria Triome, Flooded Grove. **Linha:** Tam no T3, Gauntlet no T4, Nissa no T5, Teferi no T7, Garruk Veiled Butcher no T7, Garruk Curse Breaker no T9, **Nissa `−12` no T9 (turno extra)** e, no turno extra, Ajani `−2` e Teferi `−10`.

| fim do turno (log) | planeswalkers | o que aconteceu |
|---|---|---|
| T1 | 0 | Indatha Triome virada |
| T2 | 0 | Starting Town (2º turno: desvirada) |
| T3 | 0 | Overflowing Basin (filtro `{1},{T}: {G}{U}`); **Tam** com Triome + Town + Basin |
| T4 | 0 | Exotic Orchard; Ichormoon Gauntlet ({2}{U}) |
| T5 | Nissa 6 | Yavimaya; **Nissa** ({3}{G}{G}{G/P}{G/P} − 1) com 5 terrenos + 2 de vida num `{G/P}` (entra com 5); `+1` (6): Horror 6/6; oponente: Graveborn, Vex |
| T6 | Nissa 7 | Flooded Grove; **Elspeth anulada pela Vex**, a Vex deixa comprar a Garruk Veiled Butcher; Nissa `+1` (7): Horror 7/7; oponente: Junji |
| T7 | Nissa 10, Teferi, Garruk VB | **Teferi TA** (5): o Gauntlet põe +1 na Nissa (8); Teferi `−1` desvira 4 terrenos (log: 3, erro); **Garruk Veiled Butcher** (4) com os terrenos desvirados, `0: Proliferate` do Gauntlet; Nissa `+1` (10): Horror 10/10; **Split Up** do oponente mata a Tam e a Horror 10/10 (desviradas) e poupa as que atacaram |
| T8 | Nissa 12, Garruk VB 7, Teferi 7 | Wooded Bastion; **Tam com imposto 1** (5) + Onakke (2) = os 7 terrenos; `+1` e proliferate; Horror 11/11; oponente: Spider |
| T9 | Garruk CB, Nissa 2, Garruk VB 8, Teferi 9 | **Garruk Curse Breaker** (4), Gauntlet +1 na Nissa (13), `−3`: Beast 4/4 e o Garruk compra (Bloom Tender); Bloom Tender; proliferate (Nissa 14); **Nissa `−12` (Gauntlet): 14 → 2, turno extra**; oponente (ignorado): Cleansing Nova |
| T10 (extra) | Ajani, Garruk CB, Garruk VB 10, Teferi 2, Nissa 4, Dack 4 | Arcane Signet; **Ajani** (5): `−2` com a mão vazia compra 1 por criatura; 2 ondas de proliferate do Gauntlet; Dack Fayden; **Teferi `−10` (12 → 2): emblema**; 6 Cadets; o oponente não age (turno extra) |

O log **não tem vida de oponente**: não há "vitória" nem dano registrado, então não dá para comparar mesa limpa; só desenvolvimento de mesa.

## Cada cláusula operacional do relato é uma afirmação testável (Regra #6)

| o que o usuário fez | teste em `testes/t_manual4.py` | resultado |
|---|---|---|
| T3/T4: Tam e Gauntlet com Triome + Town + Basin (filtro) | `Tam ... e Ichormoon Gauntlet ... Overflowing Basin` | ✅ |
| T5: Nissa com 5 terrenos + 2 de vida (entra com 5), `+1`, Horror X/X com X = lealdade | `Nissa (... - 1 = 6) com 5 terrenos ...` | ✅ |
| T6: a Elspeth anulada pelo oponente vai ao cemitério | `a Elspeth ... e' ANULADA por um oponente (Vex) ...` | ✅ (modo de resiliência; **a carta que a Vex deixa comprar não é modelada**: estado de oponente) |
| T7: Teferi com o gatilho do Gauntlet na Nissa; Teferi `−1` desvira 4; sem 2º `−1` | `Teferi TA ... o gatilho do Gauntlet ...` | ✅ |
| T7: Garruk Veiled Butcher com `0: Proliferate` do Gauntlet; Nissa `+1`, Horror 10/10 | `Garruk Veiled Butcher ... 0: Proliferate` | ✅ |
| T8: Tam com imposto 1 (5) + Onakke (2) com 7 terrenos, exato | `Tam do imposto 1 ... e Onakke Oathkeeper ... 7 terrenos` | ✅ |
| T9: Garruk Curse Breaker, Gauntlet, `−3` Beast 4/4, compra, proliferate | `Garruk Curse Breaker ... Gauntlet poe +1 num planeswalker ...` | ✅ (o simulador escolhe o alvo do contador do Gauntlet pelo valor do `+1`; o usuário pôs na Nissa: **política**) |
| T9: Nissa `−12` (Gauntlet) dá o turno extra | `Nissa -12 (Gauntlet, 14 -> 2) ...` | ✅ |
| T10: Ajani `−2` com a mão vazia: 1 compra por criatura, incluindo o Cadet do próprio Ajani | `Ajani ... o gatilho do proprio Ajani cria 1 Cadet ANTES ...` | ✅ (o usuário comprou 7; a regra dá 8) |
| T10: Teferi `+1` olha 2, 1 na mão, 1 no fundo; `−10` emblema | `Teferi TA -10 (12 -> 2) ...` | ✅ (o usuário jogou o `+1` errado) |
| T7: Split Up do oponente mata a Tam | `Split Up do oponente ...` | ✅ (o simulador destrói **todas** as criaturas: não distingue viradas × desviradas: proxy) |

**Nenhuma jogada do relato exigiu mudar regra do simulador.** Os desvios de regra do relato são do usuário (Teferi `+1` ×3, Teferi `−1` ×2, Ajani `−2` com 7 compras, a compra do Garruk não aplicada), e estão listados acima.

## O simulador jogando as mesmas cartas (não é validação: a IA joga diferente do usuário)

Mesma mão e mesmas 10 compras (as que **ficaram** com o usuário), resto do baralho em 300 ordens, a IA do simulador decide, T1 a T9 (`resumos/replay_*_300*.txt`):

| planeswalkers no fim de T4 / T5 / T6 / T7 / T8 / T9 (mediana) | |
|---|---|
| usuário | 0 / 1 / 1 / 3 / 3 / 4 |
| simulador, modo padrão | 1 / 1 / 2 / 4 / 4 / 4 |
| simulador, resiliência | 1 / 0 / 1 / 1 / 2 / 2 |
| Tam em campo | usuário T3; simulador T3 (os dois modos) |

**Leitura (limites):** nesta mão a IA do simulador no modo padrão se aproxima do jogo dele (a diferença é 1 planeswalker a mais em T4, T6, T7 e T8: o simulador conjura a Nissa já no T4 pagando 4 de vida nos dois `{G/P}` (entra com 3) e, no modo padrão, não perde a Elspeth para uma anulação). **A convenção das cores de terreno de oponente não pesa nesta mão** (a variante `cores_livres` dá exatamente os mesmos números: a mão não depende da Exotic Orchard). Na resiliência (remoção, wipe, descarte, anulação, ataque a planeswalker) o simulador fica abaixo, como nos outros goldfish; isso é o modelo de interação, não regra. A "1ª ultimate" do simulador (300 de 300 no modo padrão, mediana T8) é quase sempre o `−7` da Nissa; o usuário nunca usou o `−7`: usou o `−12` do Gauntlet (turno extra).

## Escopo (Regra #7)

**Comparado:** a linha do tempo inteira contra as regras do simulador (11 testes), e o desenvolvimento de mesa com as mesmas cartas.
**Não comparado / não resolvido:** vida e dano de oponente (o log não tem); o efeito real do Split Up (escolha viradas × desviradas: o simulador destrói todas), do Cleansing Nova e do Spider; as cartas que o usuário teria comprado se tivesse jogado o Teferi `+1` certo (3) e a 8ª do Ajani; o Twilight Mire e o Ketria Triome descartados no T6 (sem explicação); qual mana pagou o quê em cada ativação (o log só mostra terrenos virados; por exemplo o Teferi do T7 aparece com 4 terrenos virados para um custo de 5); a ordem exata dos 6 Cadets do T10 contra as ativações (o log os cria em lote). O replay usa 300 ordens do resto do baralho, não as cartas que o usuário de fato compraria depois da 10ª compra.
