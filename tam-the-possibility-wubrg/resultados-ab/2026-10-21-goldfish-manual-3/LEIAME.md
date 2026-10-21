# Goldfish manual #3 do Tam (jogado pelo usuário no playtester do Archidekt) — 2026-10-21

Arquivado conforme a Regra #8 da CLAUDE.md. **O que é:** o log que o usuário colou na conversa (*"Mais um Goldfish manual"*), a `lista.md` sem nenhuma troca, 7 blocos (T1 a T7), com o playtester do Archidekt (simulador de interações de oponente). **Sem foto desta vez:** a mão inicial vem das 8 primeiras compras do bloco 1. Mesma rotina dos #1 e #2: listei as dúvidas antes de interpretar; as respostas estão abaixo, literais.

## Respostas do usuário (literais)

1. **T5, Garruk (Beast 4/4):** *"T5 eu esqueci da compra com o Garruk"*
2. **T7 incompleto:** *"Parei o goldfish nesse momento"* (o bloco T7 termina quando o Dellian entra)
3. **Mão inicial:** *"está certo"* (7 primeiras cartas do bloco 1 + compra do T1 = Birds of Paradise, sem mulligan)
4. **Warrior (oponente, T4):** *"Warrior era 1/1 eu bloqueei com o Tam"* (a Tam é 2/4: mata a ficha e sobrevive)

**Como li cada resposta:** (1) o Garruk comprou 0 cartas no T5 no log; pelo oráculo ele compra quando entra criatura com poder ≥ 4, então o jogo real teria 1 carta a mais na mão no T5 (desconhecida). (2) No T7 não há nenhuma ativação de lealdade nem os 2 proliferates do Flux Channeler nas conjurações do Orrery e do Dellian **porque ele parou ali**, não por esquecimento; por regra, essas conjurações dariam 2 proliferates. (4) Bloqueio de oponente não é modelado no goldfish solo (estrutural: estado de oponente).

## Arquivos

| arquivo | o que é | status |
|---|---|---|
| `dados/mensagem_usuario_original.txt` | a mensagem inteira como chegou (texto + JSON), extraída do transcript da sessão, sem retocar | bruto, intocado |
| `dados/goldfish_manual_3_bruto.json` | só o JSON do log: 7 blocos, cada evento = movimento de carta/contador/virada no playtester | bruto, intocado |
| `dados/fichas_scryfall.json` | Scryfall: fichas Cadet (Ajani Unrelenting), Beast 4/4 (Garruk −3) e as dezenas de fichas "Warrior" (a do oponente era 1/1, resposta 4) | bruto |
| `orquestracao/linha_do_tempo.py` → `resumos/linha_do_tempo.md` | resumo por turno, **só do bruto** | usado |
| `orquestracao/replay_manual_3.py`, `replay_stats3.py` → `resumos/replay_{padrao,resiliencia}_300.txt`, `replay_{padrao,resiliencia}_300_cores_livres.txt`, `replay_semente_{1,2,3}.txt` | o simulador jogando as MESMAS 14 cartas na MESMA ordem (resto do baralho em 300 ordens); `cores_livres` = terrenos de oponente produzem as 5 cores a partir do T2 | usado |
| `testes/t_manual3.py` (na pasta do deck) | 9 testes das jogadas dele pelas regras | 9/9 passam (171/171 no total) |

**Reprodutibilidade (verificada com `cmp`, 8 de 8 idênticos):** `linha_do_tempo.md` refeita só do bruto; `replay_{padrao,resiliencia}_300.txt`, `replay_{padrao,resiliencia}_300_cores_livres.txt` e `replay_semente_{1,2,3}.txt` refeitos pelo simulador vivo. Integridade: `sha256sum -c SHA256SUMS`.

O oráculo do **Metallic Sliver** (carta de oponente no T5: `Artifact Creature — Sliver` 1/1, sem texto) entrou em `scryfall-cache/oracle-cache.json` (Regra 15).

## O jogo do usuário (da `resumos/linha_do_tempo.md`)

Mão inicial de 8: Flux Channeler, Ajani Unrelenting, Garruk Curse Breaker, Hallowed Fountain, Faeburrow Elder, Exotic Orchard, Chromatic Orrery, Birds of Paradise. Compras: The Chain Veil, Aminatou, Ripples of Potential, City of Brass, Professor Dellian Fel, Undergrowth Stadium (Aminatou +1), The Chain Veil de novo (devolvida ao topo). **Só 4 terrenos no jogo todo** (Fountain, Orchard, City, Stadium): o desenvolvimento veio de Birds, Elder e Orchard.

| fim do turno | planeswalkers | o que aconteceu |
|---|---|---|
| T1 | 0 | Hallowed Fountain virada (sem pagar 2 de vida) |
| T2 | 0 | Exotic Orchard; Birds ({G}) com o mana da Orchard |
| T3 | 0 | Faeburrow Elder (3) com Birds + Orchard + Fountain; sem terreno na mão |
| T4 | 0 | **Tam** ({1}{G}{U}) com Elder (G+W) + Fountain (U); ficha Warrior 1/1 do oponente, bloqueada pela Tam |
| T5 | Garruk 2 | City of Brass; Garruk (5 − 1 = 4) com Birds + Elder (3); Garruk −3 (5 → 2): Beast 4/4 trample (**esqueceu a compra do Garruk**); Flux Channeler com os 3 terrenos; oponente: Metallic Sliver |
| T6 | Ajani 7, Garruk 6, Aminatou 4 | Ajani (6 − 1 = 5) com Birds + City + Elder; proliferate do Flux (Garruk 2 → 3; o Ajani não: ainda na pilha); gasta o mana de Fountain + Orchard, **Garruk +2 desvira Orchard e City** (3 → 5); City de novo; Aminatou (3, a Tam não reduz cor); proliferate (Garruk 6, Ajani 6); Aminatou +1 (compra Undergrowth Stadium, devolve a Chain Veil); Stadium entra desvirado (3 oponentes); Ajani +1 (7); **3 Cadets** (3 ativações); oponente: Disenchant |
| T7 (parou aqui) | + Dellian 5 | Elder com 5 cores = 5 mana + Stadium + Orchard = Orrery (7); o Orrery (5 incolores) paga o Dellian (3) |

O log **não tem vida de oponente**: não há "vitória" nem dano registrado; só desenvolvimento de mesa.

## Cada cláusula operacional do relato é uma afirmação testável (Regra #6)

| o que o usuário fez | teste em `testes/t_manual3.py` | resultado |
|---|---|---|
| T2/T3: Birds só com a Orchard; Elder com Birds + Orchard + Fountain | `Birds ({G}) so' com a Exotic Orchard ...` | ✅ (com cor de oponente livre; ver convenção abaixo) |
| T4: Elder = 1 mana por cor entre os permanentes; Tam com Elder + Fountain | `Faeburrow Elder vira 1 mana por COR ...` | ✅ |
| T5: Garruk com Birds + Elder; −3 cria o Beast 4/4 e o Garruk COMPRA; Flux Channeler | `Garruk ({3}{G}{G} - 1 = 4) ...` | ✅ (o simulador compra; o usuário esqueceu) |
| T6: Ajani com 3 fontes; proliferate resolve antes de o Ajani entrar; Garruk +2; Cadet por ativação | `Ajani ({4}{R}{R} - 1 = 5) ...` | ✅ |
| T6: Aminatou como 2ª magia (Flux), Aminatou +1, Ajani +1, 3 Cadets | `Aminatou ({W}{U}{B}, a Tam nao reduz cor) ...` | ✅ |
| T6: Undergrowth Stadium desvirado com 3 oponentes | `Undergrowth Stadium entra DESVIRADO ...` | ✅ |
| T7: Elder com 5 cores = 5 mana: Elder + Stadium + Orchard = Orrery | `Faeburrow Elder com 5 cores ...` | ✅ |
| T7: Orrery recém-jogado vira e paga o Dellian (mana de qualquer cor) | `o Orrery recem-jogado vira {C}x5 ...` | ✅ |
| T7 (regra, não está no log): 2 magias não-criatura = 2 proliferates do Flux | `Orrery e Dellian sao 2 magias nao-criatura ...` | ✅ |

**Nenhuma jogada do relato exigiu mudar regra do simulador.** (A correção da Saheeli desta sessão veio do goldfish #2, não deste.)

## O simulador jogando as mesmas cartas (não é validação: a IA joga diferente do usuário)

Mesma mão e mesmas 6 compras, resto do baralho em 300 ordens, a IA do simulador decide (`resumos/replay_*_300*.txt`):

| planeswalkers no fim de T5 / T6 / T7 | usuário | simulador (convenção dele), padrão | simulador (convenção dele), resiliência | **simulador, cores livres a partir do T2**, padrão | **cores livres**, resiliência |
|---|---|---|---|---|---|
| mediana | **1 / 3 / 4** | 0 / 1 / 3 | 0 / 0 / 1 | **1 / 3 / 4** | 0 / 0 / 2 |
| Tam em campo | T4 | T4 | T4 | T3 | T3 |

**Leitura (limites):** a diferença do simulador para o jogo do usuário vem quase toda de **uma convenção**: a **Exotic Orchard** (e o Fellwar Stone) só produzem cores que um terreno de OPONENTE produz (oráculo), e o simulador sorteia a identidade de cor de cada um dos 3 oponentes (na semente 1 só produziam {B}, então a Orchard não pagava o {G} do Birds no T2). No playtester do Archidekt a Orchard do usuário tocou {G} no T2. Com os terrenos dos oponentes produzindo as 5 cores **a partir do T2** (os oponentes ainda não têm terreno no T1 dele), o simulador no modo padrão reproduz a mediana do usuário (**1 / 3 / 4**). Isso **não** diz qual convenção é a da mesa real do usuário (depende dos terrenos dos 3 oponentes). Na resiliência (remoção, wipe, descarte, anulação, ataque a planeswalker) o simulador fica abaixo (0 / 0 / 2); isto é o modelo de interação, não a Orchard. A 1ª ultimate acontece em 228 de 300 ordens (padrão, cores livres) no T7; o usuário não chegou a nenhuma (parou no T7).

## Escopo (Regra #7)

**Comparado:** a linha do tempo inteira contra as regras do simulador (9 testes), e o desenvolvimento de mesa com as mesmas cartas, com e sem a convenção de cor de terreno de oponente.
**Não comparado / não resolvido:** vida e dano de oponente (o log não tem); o bloqueio da Tam (não modelado: estado de oponente); qual mana pagou o quê em cada ativação (o log só mostra terrenos virados); a carta que o Garruk teria comprado no T5; o que aconteceria depois do T7 (o usuário parou); a ficha Warrior só aparece pela resposta dele (Scryfall tem dezenas). O replay usa 300 ordens do resto do baralho, não as cartas que o usuário de fato compraria depois.
