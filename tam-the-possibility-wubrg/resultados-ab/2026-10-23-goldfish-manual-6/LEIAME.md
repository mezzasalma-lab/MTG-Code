# Goldfish manual #6 do Tam (jogado pelo usuário no playtester do Archidekt) — 2026-10-23, compilado em 2026-10-28

Arquivado conforme a Regra #8 da CLAUDE.md. **O que é:** o log que o usuário colou na conversa (*"Mais um Goldfish manuel. Mão inicial em anexo."*), a `lista.md` sem nenhuma troca, **11 blocos (T1 a T11)** e a **foto da mão inicial**. O usuário numera os turnos a partir de 0; aqui "T1" é o 1º bloco.

> **STATUS DESTA PASTA:** fechada em 2026-10-28. Verificação de reprodutibilidade: `bash orquestracao/verificar_reproducao.sh` → **12/12 saídas byte a byte iguais** (`resumos/verificacao_reproducao.txt`): linha do tempo, eventos, deltas de lealdade e planeswalkers por turno (só do bruto), os 3 replays, os 3 replays em 300 ordens e a contagem dos 239 testes do simulador. **Os replays e os testes dependem do simulador vivo** (`tam_goldfish_v1.py`, que esta rodada **não alterou**): se ele mudar, mudam. **Não conferido por `cmp`:** `dados/duvidas_enviadas_2026-10-23.txt` (recuperado do transcript à mão) e o texto interpretado deste LEIAME.

## O que o usuário escreveu (literal)

> *"Mais um Goldfish manuel. Mão inicial em anexo."* (2026-10-23) e, depois das 9 dúvidas, em 2026-10-28: *"Sobre a Tam: 1) Não me lembro 2) Sim 3) Lurker 4) deve ter sido por ativaçao de PW com custo 0 pelo Ichormoon, ou pelo Flux Channeler, não me lembro com exatidão 5) Foi counterspell de simulador de interaçao 6) Não me lembro 7) Confere, só não usei o botão de passar turno para não ter interaçao, mas já vi que errei nisso 8) Na maior parte das vezes bloqueei com criaturas que não morreram pelo dano sofrido, nas demais eu descontei a vida 9) Syphon mind descartou Mind Sculptor / Prismari matou pelo 2 de dano, não considerei os outros modos / Denial counterou a Kiora / fichas que simulam ataques do oponente"* (texto byte a byte em `dados/respostas_usuario_2026-10-28.txt`; as 9 perguntas, recuperadas do transcript, em `dados/duvidas_enviadas_2026-10-23.txt`).

A instrução permanente dele (*"me pergunte qq dúvida antes de começar a compilar qq coisa"*) foi seguida: perguntei em 2026-10-23, só arquivei o bruto e esperei; **compilei em 2026-10-28 depois das respostas**.

## As 9 dúvidas e as respostas

| # | o que o log mostra | o que eu supus | resposta do usuário | situação agora |
|---|---|---|---|---|
| 1 | T4: o Oko entra da mão (L4) com 3 terrenos virados; o Way of the Paradox já pagou os 3. O T5 começa com o Oko `mão → campo` de novo. A Fracture do oponente (T4) | clique desfeito do Oko; a Fracture acertou o Jace token | *"Não me lembro"* | **não confirmada pelo usuário, mas sustentada por três coisas independentes:** (a) pelas regras o Oko ({G}{U} depois da Tam) não cabe depois do Way ({2}{G}) com 3 terrenos (teste `M6 T4`); (b) 8 cartas no fim do T4 → o descarte da Promise of Loyalty do log só acontece se o Oko estava na mão (teste da aritmética da mão); (c) o T5 repete o `hand → battlefield` do mesmo id. **Fracture: por eliminação, o Jace token:** só podia mirar artefato, encantamento ou planeswalker; o Way of the Paradox seguiu funcionando no T10 (2º terreno por ativação), o Oko estava na mão, e no T8 o Lurker criou uma ficha de Jace NOVA (se a 1ª existisse, o `empower` poria contadores nela). Premissa, não fato |
| 2 | T4: Jace L5 → 2 → 3 → 4 → 5 → 2, uma compra (Way of the Mind Sculptor) | o 1º `−3` foi desfeito com 3 cliques de `+1`; houve um único `−3` | *"Sim"* | ✅ confirmada (teste `M6 T4 Jace -3`) |
| 3 | T8: o Lurker deu `empower Jace 1` e o token novo fechou em L2, sem proliferate | o `+2` do Lurker, um clique a mais ou outra coisa | *"Lurker"* | **respondida, mas a aritmética não fecha:** `empower Jace 1` dá L1 (teste `M6 T8`) e o `[+2]` concedido pelo Lurker daria L3; o log tem L1 → L2. O +1 que falta fica **sem explicação pelo oráculo**; não muda nada adiante (a ficha fecha o T8 em L2 e o T9 soma 1 de proliferate) |
| 4 | T9: a Tam gira e há UMA onda de `+1` nos 4 planeswalkers | 1 proliferate ou 4 | *"deve ter sido por ativaçao de PW com custo 0 pelo Ichormoon, ou pelo Flux Channeler, não me lembro com exatidão"* | **a resposta não explica o T9:** o Ichormoon Gauntlet só entra no T10 (evento 37) e o Flux Channeler no T11 (evento 71). A resposta combina com as 4 ondas do **T11**. **Pela regra, a Tam do T9 proliferaria X = 4 vezes** (Oko, Domri, Wrenn, Jace = 4 tipos): +4 em cada um (teste `M6 T9`: 14 / 11 / 11 / 6); o log tem +1 (11 / 8 / 8 / 3). **Divergência do relato (12 contadores de lealdade a menos no T9), origem desconhecida**; o simulador faz X = 4 |
| 5 | T11: a Kiora entra e vai ao cemitério sem evento do oponente; depois é conjurada de novo do cemiterio pelo emblema da Wrenn | por escolha ou morta por algo | *"Foi counterspell de simulador de interaçao"* | ✅ explicada: o contra-feitiço do simulador de interação do playtester (a foto mostra *"Interaction simulator (On)"*); a **Forceful Denial** do T10 (resposta 9) era o contra-feitiço. Teste `M6 T11 Kiora` (anulada → cemitério → conjurada do cemitério pelo emblema, 3 de mana de novo) |
| 6 | T11: o Dack Fayden `biblioteca → mão` depois do combate | qual efeito o comprou | *"Não me lembro"* | **sem fonte no log.** Descartei: o Jace `−3` + o gatilho do WotMS compraram a Staff of Compleation e o Flux Channeler; o `−3` do Dihada (revela 4, pega as lendárias) só poderia ser, mas o Dihada entra DEPOIS do Dack no log; a Staff (`{T}`, 4 de vida: compra) nunca foi conjurada. **Aberta** |
| 7 | T11: 4 ondas de proliferate e Oko 15 → 3 | Wrenn, Tezzeret e Domri usaram o `[0]` do Gauntlet nas ondas 1 a 3, o Oko o `−12`, o Jace o `−3`, o Dihada o `[0]` na onda 4 | *"Confere, só não usei o botão de passar turno para não ter interação, mas já vi que errei nisso"* | ✅ confirmada. **O turno extra do Oko (`−12` do Gauntlet) NÃO foi jogado:** ele não apertou o botão de passar turno para o simulador de interação não agir, e reconhece que errou. A partida do usuário termina no T11 por isso (testes `M6 T11 Gauntlet`, `Dihada`) |
| 8 | o log não registra combate (Steam Vents animado no T6, Food/Elk virado no T11) | quais criaturas atacaram e se houve dano | *"Na maior parte das vezes bloqueei com criaturas que não morreram pelo dano sofrido, nas demais eu descontei a vida"* | ✅ respondida (qualitativa): o combate foi contra **atacantes simulados** (resposta 9); a vida dele está fora do log. Não testável pelo simulador (estado de oponente) |
| 9 | T7 Syphon Mind, T8 Prismari Command, T10 Forceful Denial; Cat, Spirit, Rukh, Wurm e Spider (T5–T9) | descarte do WotMS; o Lurker morto; contra-feitiço; fichas ou criaturas | *"Syphon mind descartou Mind Sculptor; Prismari matou pelo 2 de dano, não considerei os outros modos; Denial counterou a Kiora; fichas que simulam ataques do oponente"* | ✅ respondida. Syphon Mind: o WotMS vai ao cemitério (evento 18 do T7). Prismari: o Lurker é 3/2 (cache), o 2 de dano o mata; **os outros modos (comprar/descartar 2, Treasure, destruir artefato) não foram aplicados por ele**. Denial: contrariou a Kiora (resposta 5). Cat, Spirit, Rukh, Wurm e Spider são **fichas que simulam ataques do oponente**, não cartas |

**A pergunta final** (*"O 'Interaction simulator (On)' da foto é a mesma configuração do #5?"*) **não foi respondida** de forma literal.

## Arquivos

| arquivo | o que é | status |
|---|---|---|
| `dados/mensagem_usuario_original.txt` | a mensagem inteira como chegou (texto + JSON), sem retocar | bruto, intocado |
| `dados/goldfish_manual_6_bruto.json` | só o JSON do log: 11 blocos (9, 3, 7, 20, 14, 20, 19, 28, 27, 39, 85 eventos), cada evento = movimento de carta/contador/virada no playtester | bruto, intocado |
| `dados/mao_inicial.webp` | a foto da mão inicial: Promise of Loyalty, Steam Vents, Hallowed Fountain, Way of the Paradox, Oko, Dihada, Domri; "Keep this" / "Mulligan (0)"; "Interaction simulator (On)" | bruto, intocado |
| `dados/duvidas_enviadas_2026-10-23.txt` | as 9 perguntas, recuperadas do transcript da sessão em 2026-10-28 (o texto não tinha ficado no repositório) | recuperado |
| `dados/respostas_usuario_2026-10-28.txt` | as respostas do usuário, literais | bruto, intocado |
| `orquestracao/linha_do_tempo.py` → `resumos/linha_do_tempo.txt`; `eventos_compactos.py` → `resumos/eventos_compactos.txt`; `deltas_lealdade.py` → `resumos/deltas_lealdade.txt` | resumos por turno e por evento, **só do bruto, sem interpretar** (o `deltas_lealdade` agrupa por NOME: no T8 mostra "Jace 2 → 1 (−1)" misturando a ficha antiga com a nova; não é uma ativação) | usado |
| `orquestracao/pws_por_turno.py` → `resumos/pws_por_turno.txt` (+ `_premissa_fracture`) | planeswalkers em campo no fim de cada turno, **só do bruto**, por intervalo de presença do id; trata o clique desfeito do Oko (re-entrada do mesmo id) e a ficha de Jace do T4 (premissa da Fracture, declarada) | usado |
| `orquestracao/replay_manual_6.py` → `resumos/replay_semente_{1,2,3}.txt`; `replay_escala_6.py` → `resumos/replay_escala_300_*.txt` | o simulador jogando as MESMAS cartas na MESMA ordem (mão de 7, 1 + todas as compras `library → hand` do log), 3 partidas inteiras e 300 ordens do resto do baralho nos 3 oponentes | usado |
| `testes/t_manual6.py` (na pasta do deck) | os testes das jogadas dele pelas regras | ver abaixo |
| `orquestracao/verificar_reproducao.sh` → `resumos/verificacao_reproducao.txt` | refaz os resumos e compara com `cmp` | verificação |

O oráculo da **Forceful Denial** (carta do oponente no T10) entrou em `scryfall-cache/oracle-cache.json` (Regra 15; faltava). As outras 33 cartas do log já estavam no cache; as 8 fichas/emblema do log (Cat, Food, Jace, Rukh, Spider, Spirit, Wurm, emblema da Wrenn) não são cartas.

## O jogo do usuário

Abertura: 7 cartas (Promise of Loyalty, Steam Vents, Hallowed Fountain, Way of the Paradox, Oko, Dihada, Domri), sem mulligan, + a compra do T1 (Liliana's Talent). Planeswalkers em campo no fim de cada turno (`resumos/pws_por_turno.txt`): **T4 1, T5 2, T6 3, T7 4, T8 4, T9 4, T10 5, T11 6** (sem a premissa da Fracture; com ela, T4 0, T5 1, T6 2, T7 3).

| bloco | o que aconteceu |
|---|---|
| T1–T2 | Hallowed Fountain e Steam Vents entram virados (sem pagar 2 de vida) |
| T3 | Plaza of Heroes; **Tam** (`{1}{G}{U}`: a Plaza paga o `{G}` porque a Tam é lendária) |
| T4 | **Way of the Paradox** (Jace token com 5); Jace `−3` (compra o WotMS; o 1º `−3` foi desfeito); o clique do Oko foi desfeito; descarta a Promise of Loyalty; oponente: Fracture (Jace token, por eliminação) |
| T5 | Mossfire Valley; **Oko** `+2` (L6, Food) |
| T6 | Overflowing Basin; **Wrenn** `+1` (anima o Steam Vents); Oko `+1` (L7); oponente: Rukh |
| T7 | Wooded Foothills → Indatha Triome; **Domri** `+1` (L6); Oko `+2` (L9); Wrenn `+1`; oponente: Syphon Mind (descarta o WotMS) |
| T8 | Fellwar Stone; **Sanctum Lurker** (ficha de Jace nova, L2); Oko L10, Domri L7, Wrenn L7; oponente: Prismari Command (mata o Lurker) |
| T9 | Undergrowth Stadium; **Tam** (1 onda de `+1`, X = 4 pela regra); **Wrenn `−7`** (L8 → 1): emblema; Oko `+2` (L13), Domri `+1`, Jace `−1` (Surveil: Stomping Ground ao cemitério) |
| T10 | Stomping Ground **do cemitério** e City of Brass (2º terreno pelo Way of the Paradox); **WotMS do cemitério** pelo emblema (Jace +5 → L7); Jace `−3` (compra Vronos e City of Brass); **Tezzeret** `−3` (Ichormoon Gauntlet); oponente: Forceful Denial |
| T11 | **Kiora anulada** pela Denial e recast do cemitério; Wooded Foothills ×2 do cemitério (Jetmir's Garden, Zagoth Triome); **4 ondas de proliferate** pelo `[0]` do Gauntlet; **Oko `−12` (turno extra não jogado)**; Jace `−3` (Staff of Compleation e Flux Channeler); Flux Channeler, **Dihada**; planeswalkers: Wrenn 5, Tezzeret 5, Jace 5, Domri 14, Oko 6, Dihada 6 |

O log **não tem vida de oponente nem a vida dele**; não há vitória registrada.

## Cada cláusula operacional do relato é uma afirmação testável (Regra #6)

`testes/t_manual6.py`: **19 testes, todos passam; os 239 do simulador do Tam passam** (`resumos/testes_tam_todos.txt`). **Nenhum teste achou lacuna de regra no simulador.** Três testes documentam diferenças que NÃO são do simulador:

| o que o usuário fez | teste | resultado |
|---|---|---|
| T3: Tam com Plaza ({G}, lendária) + Steam Vents + Fountain; sem {G} não conjura | `M6 T3` | ✅ |
| T4: Way of the Paradox com a Plaza; empower 5 cria o Jace com 5; o Oko não cabe depois | `M6 T4` | ✅ (**divergência do relato:** o Oko do log não foi pago) |
| T4: 8 cartas no fim do turno descartam 1; com o Oko conjurado seriam 7 | `M6 T4 aritmética` | ✅ |
| T4: Jace `−3` compra 1 (L5 → 2), Paradox: +1 de vida e 2º terreno | `M6 T4 Jace -3` | ✅ |
| T5: Oko com Plaza + Mossfire (filtro) + Vents; `+2`: L6 e Food | `M6 T5` | ✅ |
| T6: Wrenn com o filtro do Basin; `+1` anima o Steam Vents (3/3); Oko `+1` faz da Food um Elk | `M6 T6` | ✅ |
| T7: Wooded Foothills: 1 de vida, busca o Indatha Triome (Forest), entra virado | `M6 T7` | ✅ |
| T8: Lurker: empower 1 → L1; `[+2]` concedido a todo planeswalker | `M6 T8` | ✅ (**o L2 do log não sai das regras**, resposta 3) |
| T8: Lurker é 3/2 (o 2 de dano do Prismari o mata) | `M6 T8 Prismari` | ✅ |
| T9: Tam proliferaria X = 4 vezes (+4 em cada um) | `M6 T9` | ✅ (**divergência do relato:** o log tem +1) |
| T9: Wrenn `−7` (L8 → 1) cria o emblema; Jace `−1` faz Surveil | `M6 T9 Wrenn` | ✅ |
| T10: terreno e WotMS do cemitério pelo emblema; empower 5 (L2 → 7) | `M6 T10 emblema` | ✅ |
| T10: Jace `−3` com WotMS compra 2 (Vronos e City of Brass); Paradox: 2º terreno | `M6 T10 Jace` | ✅ |
| T10: Tezzeret `−X` com X = 3 busca o Ichormoon Gauntlet | `M6 T10 Tezzeret` | ✅ |
| T10: com Sol Ring e Gauntlet na biblioteca o simulador busca o **Sol Ring** (`TEZZ_PRIORITY` 55 > 50); o usuário buscou o Gauntlet | `M6 T10 (política)` | ✅ **diferença de política, não de regra; não alterei** (o log não diz se o Sol Ring estava na biblioteca; com 4 planeswalkers e a Tam o Gauntlet vale mais, e esta é uma candidata a ajuste do simulador) |
| T11: Kiora anulada pelo contra-feitiço e recast do cemitério pelo emblema | `M6 T11 Kiora` | ✅ |
| T11: Gauntlet `[0]` ×3 = 3 proliferates; Oko `−12` enfileira o turno extra | `M6 T11 Gauntlet` | ✅ |
| T11: Dihada entra com 5 e recebe o `[0]` (L6) | `M6 T11 Dihada` | ✅ |
| T11: o Dack não tem fonte de compra no log (a Staff nunca foi conjurada; o Dihada entra depois) | `M6 (dúvida 6)` | ✅ (documenta, não resolve) |

## Replay no simulador (mesma mão e mesmas compras; resto do baralho em 300 ordens)

`resumos/replay_escala_300_*.txt`. Planeswalkers no fim do T10 (mediana): **padrão 13**, **resiliência de sempre 2**, **resiliência com o perfil `playtester` 8**, contra **5** do usuário (log). P(simulador ≥ usuário) no T10: 100% / 17% / 79%. A **Tam sai no T3 em 300 de 300** ordens nos 3 modos, como a do usuário. **Não é validação:** o perfil `playtester` foi ajustado nos logs #1–#5, não neste; o simulador joga outras linhas (no T4 ele conjura o Oko e não o Way of the Paradox); o usuário não jogou o turno extra e teve o clique do Oko desfeito.

## Escopo (Regra #7): o que esta compilação NÃO fez

- **Não resolvi:** a dúvida 1 (só sustentei: o usuário não lembra), o +1 do Jace no T8 (3), por que o T9 teve 1 onda (4: a resposta dele não explica o T9) e o que comprou o Dack (6). Nenhuma delas muda um teste.
- **Não comparei:** vida e dano (o log não tem), qual mana pagou o quê, o combate (estado de oponente), os outros modos do Prismari Command (ele não os aplicou).
- **Não alterei o simulador.** A diferença do Tezzeret (`TEZZ_PRIORITY`) e as linhas de jogo do T4 (o simulador conjura o Oko e não o Way) ficam como diferenças de política.
- **O replay não é validação** (perfil ajustado em outros logs; N = 300 ordens do resto, mesma mão e compras); a premissa da Fracture só altera a contagem de planeswalkers do T4 ao T7.
- **Provas de uma execução só:** nenhuma além dos `cmp` abaixo.
