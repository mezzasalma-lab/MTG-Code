# Goldfish manual #2 do Tam (jogado pelo usuário no playtester do Archidekt) — 2026-10-20

Arquivado conforme a Regra #8 da CLAUDE.md. **O que é:** o log que o usuário colou na conversa (*"Mais um goldfish manual, mão inicial na foto em anexo"*) com a foto da mão inicial, a `lista.md` sem nenhuma troca, 8 turnos, com o playtester do Archidekt (simulador de interações ligado: a foto mostra *"Interaction simulator (On)"*). Mesma rotina do #1: listei as dúvidas antes de interpretar; as respostas estão abaixo, literais.

## Respostas do usuário (literais)

Às 5 dúvidas (mensagem de 2026-10-20 e a seguinte):
- **T8 (parou?):** *"Parei de propósito mesmo"* (sem dizer o plano).
- **1) Saheeli em T4 e T5:** *"A Saheeli entrou só no T5; o T4 foi undo"*
- **2) Jace e Tam no T4:** *"Tam atacou, Jace ativou para compra e subiu por prliferate"*
- **3) Wanderer e Servo no T7:** *"Então proliferei errado, esqueci o servo"*
- **4) Ataques do oponente:** *"Planeswalker na maioria das vezes"*

**Como li cada resposta (leitura minha, marcada como tal):**
1. O bloco T4 do log tem a Saheeli em campo (`hand→battlefield`, lealdade 5), mas o mana do T4 só fecha para a Way (3 toques: Town, Triome, Fellwar). No T5 fecha exato para Saheeli (2) + Aminatou (3) = 5 toques. **Corrigido: Saheeli entra no T5.**
2. A Tam ficou virada no T4 = **atacou** (não ativou; ela precisa de {W}{U}{B}{R}{G} e o mana do T4 já tinha sido gasto na Way). O Jace usou o −3 (5 → 2, comprou a Aminatou). **Não há fonte de proliferate em campo no T4** (Tam atacou, Whale e Flux Channeler não estavam em campo): os cliques de lealdade 3, 4, 3, 4, 5, 4, 3 entre o −3 e o fim do bloco **não correspondem a nenhuma habilidade possível**, e o log fecha o T4 com Jace 2 (= 5 − 3), que é o único valor consistente com as regras. **Tratei o Jace como 2 no fim do T4.** O T5 tem o mesmo padrão (2 → 1 → 2); o T6 começa em 2 (o proliferate da Whale o leva a 3), então também tratei como 2.
3. **Corrigido:** a Eternal Wanderer **não** recebe o contador do proliferate da Whale (o gatilho da 2ª magia resolve ANTES de ela entrar): fica em **5**, não 6; e faltou o Servo da Saheeli na conjuração dela (**2 Servos no T7**, não 1).
4. Os `Zombie` (T4) e `Carnivore` (T6) são fichas de oponente (o Carnivore é uma ficha Beast no Scryfall); o `Murderous Rider // Swift End` do T7 matou o Teferi (7 de lealdade). O log **não tem vida nem dano**, então não dá para dizer quanto dano os planeswalkers tomaram.

## Arquivos

| arquivo | o que é | status |
|---|---|---|
| `dados/mensagem_usuario_original.txt` | a mensagem inteira como chegou (texto + JSON), extraída do transcript da sessão, sem retocar | bruto, intocado |
| `dados/goldfish_manual_2_bruto.json` | só o JSON do log: 8 blocos (um por turno), cada evento = movimento de carta/contador/virada no playtester | bruto, intocado |
| `dados/mao_inicial_foto.webp` | a foto da mão inicial anexada pelo usuário (Boseiju, Verdant Catacombs, City of Brass, Chandra Legacy of Fire, Way of the Deathbringer, Fellwar Stone, Saheeli Sublime Artificer; *Keep this* / *Mulligan (0)*) | bruto |
| `orquestracao/linha_do_tempo.py` → `resumos/linha_do_tempo.md` | resumo por turno, **só do bruto** (compras, terreno, magias, buscas, saídas, cartas de oponente, última lealdade do bloco) | usado |
| `orquestracao/replay_manual_2.py`, `replay_stats2.py` → `resumos/replay_padrao_300.txt`, `replay_resiliencia_300.txt`, `replay_semente_{1,2,3}.txt` | o simulador jogando as MESMAS 20 cartas na MESMA ordem (resto do baralho em 300 ordens) | usado |
| `testes/t_manual2.py` (na pasta do deck) | 16 testes: as jogadas dele, já com as correções, mais a nova copia de artefato de mana da Saheeli | 16/16 passam (162/162 no total) |

Reproduzir: `python3 orquestracao/linha_do_tempo.py`; `python3 orquestracao/replay_stats2.py 300 padrao` (e `resiliencia`); `python3 testes/rodar_testes.py` na pasta do deck. O código do simulador usado nos replays é o do commit que fecha a rodada da Saheeli (`../2026-10-21-saheeli-copia-de-artefato/LEIAME.md`).

## O jogo do usuário (da `resumos/linha_do_tempo.md`, com as correções acima)

Mão inicial de 8 (7 da foto + compra do T1): Boseiju, Verdant Catacombs, City of Brass, Chandra Legacy of Fire, Way of the Deathbringer, Fellwar Stone, Saheeli, Starting Town. Compras seguintes, na ordem: Dreamtide Whale, Wooded Foothills, Plaza of Heroes, (Jace −3) Aminatou, The Eternal Wanderer, (Aminatou +1) Teferi, Windswept Heath (Teferi +1), Watery Grave, Wrenn and Realmbreaker (Teferi +1), Yavimaya (Jace −3), Temple Garden, Overwrite the Multiverse (Aminatou +1).

| fim do turno | planeswalkers (corrigido) | o que aconteceu |
|---|---|---|
| T1 | 0 | Verdant Catacombs → Zagoth Triome (virado) |
| T2 | 0 | Starting Town (desvirada: 2º turno); Fellwar Stone |
| T3 | 0 | City of Brass; **Tam** com Triome + Town + Fellwar |
| T4 | Jace 2 | Plaza of Heroes; Way of the Deathbringer (cria o Jace com 5); Jace −3 (compra a Aminatou); **Tam atacou**; oponente: ficha Zombie |
| T5 | Jace 2, Saheeli 5, Aminatou 4 | Boseiju; Saheeli (2) e Aminatou (3) com a Tam; Servo; Aminatou +1: compra Teferi e devolve a Wanderer ao topo |
| T6 | Jace 3, Saheeli 4, Aminatou 5, Teferi 5 | Wooded Foothills → Spara's HQ; Whale (3); **Saheeli −2: Servo vira cópia do Fellwar e paga o Teferi (4)**; Teferi como 2ª magia: o proliferate da Whale não pega o Teferi (4), pega Saheeli, Aminatou, Jace e o contador de tempo da Whale; Teferi +1 (5, compra Windswept Heath); oponente: ficha Carnivore |
| T7 | Chandra 5, Wanderer **5** (log: 6), Aminatou 5, Saheeli 5, Wrenn 5, Jace 1; Teferi morreu | Watery Grave (entrou desvirada: pagou 2 de vida); Chandra, Servo, Chandra +1 ({R}×5); Wanderer (paga pelo mana da Chandra); Whale 2ª magia: proliferate; Teferi +1 (7); Wanderer 0: Samurai; **Aminatou −1 pisca o Fellwar virado** (volta desvirado: paga a Wrenn); Wrenn +1 (Boseiju vira 3/3); Jace −3 (compra Yavimaya); oponente: Swift End mata o Teferi |
| T8 (parou de propósito) | Aminatou 6 | Yavimaya; Aminatou +1 (compra Overwrite the Multiverse, devolve Windswept Heath ao topo) |

O log **não tem vida de oponente**: não há "vitória" nem dano registrado, então não dá para comparar mesa limpa; só desenvolvimento de mesa.

## Cada cláusula operacional do relato é uma afirmação testável (Regra #6)

| o que o usuário fez | teste em `testes/t_manual2.py` | resultado |
|---|---|---|
| T3: Tam ({1}{G}{U}) com Triome + Town + Fellwar | `a Tam ... sai com Zagoth Triome + Starting Town + Fellwar Stone` | ✅ |
| T4: Way sem Jace cria a ficha com 5; Jace −3 (5 → 2) compra; Tam pode atacar | `Way of the Deathbringer sem ficha de Jace ...` | ✅ (regra); **política**: a Tam nunca ataca no simulador (`NON_ATTACKERS`) |
| T5: Saheeli custa 2 e Aminatou 3 com a Tam; as duas com 5 toques; Servo na Aminatou | `com a Tam, Saheeli custa 2 e Aminatou 3 ...` | ✅ |
| T5: Aminatou +1 compra e devolve ao topo | `Aminatou +1 (3 -> 4) compra 1 e devolve 1 ...` | ✅ (a escolha da carta é da IA) |
| T6: Wooded Foothills busca Spara's HQ (Forest, entra virado) | `Wooded Foothills (Mountain ou Forest) busca ...` | ✅ |
| T6: 2ª magia (Teferi) dispara a Whale; Teferi não é proliferado; Teferi +1 | `Whale (1a magia) + Teferi (2a) ...` | ✅ |
| **T6: Saheeli −2: Servo vira cópia do Fellwar e rende mana** | `Whale (3) + Teferi (4) = 7 de mana ...`, `Saheeli -2 em copia de artefato de MANA ...` | 🐛 **não existia** (o −2 só copiava P/T de criatura); **corrigido** nesta rodada, ver abaixo |
| T7: Chandra +1 ({R}×5) paga o genérico da Wanderer | `Chandra +1 com 5 planeswalkers ...` | ✅ |
| T7 (corrigido): Wanderer não é proliferada; Servo em cada magia não-criatura | `Chandra e Wanderer (2a magia ...)` | ✅ |
| T7: Wanderer 0 → Samurai | `Eternal Wanderer 0: Samurai ...` | ✅ |
| T7: o piscar da Aminatou −1 num Fellwar virado devolve mana | `o piscar da Aminatou -1 num Fellwar Stone VIRADO ...` | ✅ (regra); **política**: `best_blink_target` nunca escolhe uma rocha de mana virada (valor 0) |
| T7: Wrenn +1 anima um terreno 3/3 | `Wrenn and Realmbreaker (4) +1 ...` | ✅ |
| T7: Jace −3 compra; remoção do oponente mata um planeswalker (modo de resiliência) | `Jace -3 (4 -> 1) compra a Yavimaya; ...` | ✅ |
| T8: Yavimaya | `Yavimaya, Cradle of Growth: cada terreno e' tambem Forest ...` | ✅ |

**Achado desta rodada (Regra #1/#5): a cláusula "target artifact you control becomes a copy of another target artifact or creature" da Saheeli só estava modelada pela metade** (cópia de P/T de criatura; o próprio `checklist-oraculo.md` ("NÃO varrido neste arquivo") declarava "não varrido: cópia de habilidades"). O usuário jogou exatamente a outra metade no T6. Corrigido com a chave `SAHEELI_COPY_MANA_ARTIFACT` e arquivado em [`../2026-10-21-saheeli-copia-de-artefato/`](../2026-10-21-saheeli-copia-de-artefato/LEIAME.md) (bit-identidade com a chave desligada, regressão, A/B pareado, determinismo).

## O simulador jogando as mesmas cartas (não é validação: a IA joga diferente do usuário)

Mesma mão e mesmas 12 compras, resto do baralho em 300 ordens, a IA do simulador decide (`resumos/replay_*_300.txt`; simulador **com** a cópia de mana da Saheeli):

| | usuário (corrigido) | simulador, modo padrão (mediana) | simulador, resiliência (mediana) |
|---|---|---|---|
| Tam em campo | T3 | T3 | T3 |
| planeswalkers no fim do T4 / T5 / T6 / T7 / T8 | 1 / 3 / 4 / 6 / 6 | 2 / 4 / 6 / 7 / 9 | 1 / 2 / 2,5 / 3 / 3 |
| 1ª ultimate | nenhuma | T8 (126/300 partidas) | T8 (49/300) |
| partidas com cópia de mana da Saheeli | 1 (T6) | 141/300 | 41/300 |

**Leitura (limites):** no modo padrão o simulador desenvolve mais planeswalkers do que o usuário com as mesmas cartas (a IA conjura e ativa tudo o que paga, e a mesa dele foi limitada por 1 jogo humano com o playtester interagindo); na resiliência fica abaixo (remoção, wipes, descarte, anulação e ataque a planeswalker modelados de outro jeito). Como no #1, isto **não** diz qual está certo: são 1 jogo humano e 300 ordens do resto do baralho. As diferenças de política que apareceram: a **Tam nunca ataca** no simulador (o usuário atacou no T4, quando não tinha mana WUBRG para ativar); o **Aminatou −1 não pisca rocha de mana virada** (o usuário piscou o Fellwar para pagar a Wrenn); e o **Chandra** foi a jogada do T4 do simulador (o usuário jogou a Way).

## Escopo (Regra #7)

**Comparado:** a linha do tempo inteira contra as regras do simulador (16 testes, 13 do relato e 3 da correção), e o desenvolvimento de mesa com as mesmas cartas.
**Não comparado / não resolvido:** vida e dano de oponente (o log não tem); qual mana pagou o quê em cada ativação (o log só mostra terrenos virados); os cliques de lealdade do Jace no T4 e no T5 (li como ruído de undo: o estado final de cada turno é o único consistente com as regras); o upkeep da Whale no T8 (não aparece no log; o usuário parou de propósito, sem dizer o plano); os turnos de oponente do playtester (só aparecem os nomes das cartas); a escolha de alvo dos ataques do oponente (*"Planeswalker na maioria das vezes"*, sem número). O replay usa 300 ordens do resto do baralho, não as cartas que o usuário de fato comprou depois da 12ª compra.
