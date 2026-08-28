# Goldfish Compilado — Beorn the Fierce

Compilação de todos os goldfish rodados na sessão. Cada jogo foi registrado turno a turno a partir dos logs reais (imagens de opening hand + JSON de jogadas), com as correções apontadas ao longo do processo já aplicadas.

---

## Simulação estatística v1 — escrita e rodada por Claude (não é dado seu)

**Atribuição:** ao contrário dos jogos acima (suas partidas reais) e do script do Ulalek (seu script, seu Colab), esta simulação foi **escrita e executada por mim**, a seu pedido, pra ter o mesmo formato do seu simulador do Ulalek. Script completo salvo em `beorn_goldfish_v1.py` nesta pasta — reproduzível, não é caixa-preta.

**Metodologia:**
- Tags de cada carta derivadas do `oracle_text` real (Scryfall), buscado nas auditorias anteriores desta sessão — não inventadas.
- Modelo de mana simplificado por o deck ser mono-verde: contagem total de fontes de mana + contagem separada de "fontes verdes", já que **4 terrenos do deck** (War Room, Scavenger Grounds, Nykthos, Reliquary Tower) só produzem incolor a menos que Yavimaya, Cradle of Growth esteja em campo (ela transforma todo terreno em Floresta). Cartas com custo `{G}{G}` ou mais exigem essa contagem de fontes verdes, não só mana total.
- Gatilho do Beorn modelado meio a meio: a cada combate (se o comandante estiver em campo), converte a criatura de maior CMC no campo que ainda não é "Bear" em Bear; se isso deixar 3+ Bears sob controle, dispara o "compre 2".
- 500 jogos, 8 turnos, on the play — mesmos parâmetros do seu script do Ulalek, pra ficar comparável.

**Resultado (500 jogos, 8 turnos, on the play):**

```
=== Beorn the Fierce — Goldfish Summary v1 (simulado por Claude) ===
Games: 500 | Turns: 8 | On play: True

Avg mulligans: 0.48
Avg commander cast turn: 4.31
Commander cast by turn 4: 57.6%
Commander cast by turn 5: 81.6%

Avg spells cast: 12.52
Avg extra draws (gatilhos): 8.33
Avg Bear count final: 5.49
Avg Beorn 'draw 2' triggers (3+ Bears): 2.93
Avg Beorn combat triggers (converteu em Bear): 4.17
Avg ramp pieces em campo: 2.60
Avg remocao conjurada: 1.01
Avg finishers resolvidos: 0.47
Avg turno do 1o finisher relevante: 6.02
% de jogos com finisher ate T8: 37.0%
Avg cartas descartadas por limite de mao: 0.28
Avg battlefield final: 17.13
Avg mao final: 3.94
Avg terrenos jogados: 6.29
```

**Leitura, com ressalvas:**
- Comandante resolve consistente (T4.31 médio), parecido com o que os goldfish reais já mostraram (T4-7 nos seus jogos manuais).
- O gatilho "3+ Bears → compre 2" dispara quase 3x por partida em média — bate com o padrão que seus goldfish manuais já indicavam (motor de Urso funcionando desde cedo).
- **Limitação clara:** essa simulação não modela combate contra oponentes nem interação alheia — só desenvolvimento de board. "Finishers resolvidos" mede se a carta foi conjurada, não se ela matou alguém.

### Re-execução com n=1000 e n=2000 (a pedido do usuário) — checagem de estabilidade

Mesmo script, mesmos parâmetros (8 turnos, on the play), só variando o tamanho da amostra:

| Métrica | n=500 | n=1000 | n=2000 |
|---|---|---|---|
| Avg commander cast turn | 4.31 | 4.30 | 4.25 |
| Commander cast by T4 | 57.6% | 60.1% | 61.8% |
| Commander cast by T5 | 81.6% | 82.2% | 82.8% |
| Avg Bear count final | 5.49 | 5.61 | 5.70 |
| Avg Beorn 'draw 2' triggers | 2.93 | 3.00 | 3.06 |
| Avg finishers resolvidos | 0.47 | 0.51 | 0.53 |
| **% partidas com finisher até T8** | **37.0%** | **41.0%** | **42.8%** |
| Avg battlefield final | 17.13 | 17.46 | 17.57 |

A maioria das métricas fica estável dentro de 1-2 pontos percentuais conforme a amostra cresce — sinal de que n=500 já não estava muito ruidoso pra elas. A exceção é a taxa de finisher até T8, que subiu de 37,0% pra 42,8% entre n=500 e n=2000 — uma diferença de quase 6 pontos, maior do que eu esperava só por ruído amostral (erro-padrão estimado em n=2000 é de ±~1,5 ponto percentual pra uma proporção binária nesse patamar). Ou seja, o n=500 original provavelmente **subestimou** a taxa real de finisher — o número mais confiável dos três é o de n=2000: **42,8%** das partidas resolvem Craterhoof/Unnatural Growth/Ghalta/Genji Glove até o turno 8.

Isso ainda fica abaixo da impressão dos seus 5 goldfish manuais (Craterhoof resolveu no Jogo 5, 1 de 5 = 20%... mas nem todos os 5 jogos foram até o fim decidindo isso, então essa comparação direta não é robusta — 5 amostras manuais não têm poder estatístico pra confirmar ou refutar 42,8%). Não dá pra cruzar os dois valores como se fossem comparáveis.

### Correção — Managorger Hydra nunca crescia na simulação (bug real, apontado por você após o Jogo 6)

O script original tinha a Managorger Hydra só como corpo estático (1/1 com trample) — a tag `counters_engine` foi atribuída na definição da carta mas **nunca estava conectada a nenhuma lógica real**, então ela nunca ganhava contadores em nenhum dos jogos simulados, apesar do texto real ser *"Whenever a player casts a spell, put a +1/+1 counter on this creature"* (qualquer jogador, não só você).

Corrigido em `beorn_goldfish_v1.py` com duas partes:
1. **Rigoroso, sem suposição:** +1 contador a cada spell que VOCÊ conjura enquanto ela está em campo (usando o `spells_cast` que o script já rastreava).
2. **Premissa explícita, pedida por você — não é dado real:** +2 contadores por turno representando uma média conservadora/baixa de spells de oponentes numa mesa de Commander, e um tempo de vida médio de 4 dos seus turnos antes de cair pra remoção pontual (sorteado por jogo com `randint(1,7)`, média=4, já que ela é um alvo grande e óbvio na mesa).

**Re-execução com n=2000, mesmos parâmetros, só essa correção:**

| Métrica | Antes (bug) | Depois (corrigido) |
|---|---|---|
| Avg Bear count final | 5.70 | 5.69 (~igual, esperado — bug não afetava contagem de Ursos, só o tamanho da Managorger) |
| Avg battlefield final | 17.57 | 17.44 (~igual) |
| Managorger Hydra conjurada | (não rastreado) | 20,2% dos jogos (é 1 carta em 99, compra é aleatória) |
| Avg contadores +1/+1 finais da Managorger (quando conjurada) | 0 (sempre) | **8,77** |
| Removida pela remoção assumida (~4 turnos vivos) | — | 56,4% dos jogos em que foi conjurada, turno médio de morte: 5,86 |

**Validação cruzada com dado real:** no Jogo 6 (goldfish manual, log JSON), a Managorger Hydra terminou o T8 com **8 contadores** — bate quase exatamente com a média simulada de 8,77 mesmo sem premissa nenhuma calibrada nesse sentido (o número de 2 spells/turno de oponente foi sua estimativa dada de forma independente). Não é prova de que a premissa está certa (n=1 no Jogo 6, e lá também é fundamentalmente um goldfish solo — spells de oponentes reais nunca foram testados), mas é um sinal de consistência.

As demais métricas do resto do deck (turno do comandante, ramp, taxa de finisher) não mudaram de forma relevante, porque não dependiam do tamanho da Managorger.

### Segunda correção — regra de compra do turno 1 (multiplayer, apontada por você)

O parâmetro `on_play` do script pulava a compra do turno 1 de quem começa — isso é a regra correta **só em jogos de 2 jogadores**. Pela Comprehensive Rules oficiais da Wizards (CR 103.8a), essa regra não existe em multiplayer: em Commander (3+ jogadores), **todo mundo compra no seu turno 1**, incluindo quem começa. Removido o parâmetro `on_play` inteiro do script (não fazia mais sentido manter, já que sempre compra agora) e o T1 sempre puxa uma carta.

**Re-execução com n=2000, as duas correções juntas (Managorger + compra do T1):**

| Métrica | v1 original (com os 2 bugs) | Corrigido |
|---|---|---|
| Avg commander cast turn | 4.25 | **4.03** |
| Commander cast by T4 | 61.8% | **69.5%** |
| Commander cast by T5 | 82.8% | **88.8%** |
| Avg spells cast | 12.52 | 14.37 |
| Avg Bear count final | 5.70 | 6.22 |
| Avg Beorn 'draw 2' triggers | 3.06 | 3.41 |
| Avg ramp pieces em campo | 2.60 | 3.09 |
| Avg finishers resolvidos | 0.53 | 0.62 |
| **% partidas com finisher até T8** | **42,8%** | **48,4%** |
| Avg battlefield final | 17,57 | 19,10 |
| Avg mão final | 3,94 | 4,24 |
| Managorger Hydra — contadores finais (quando conjurada) | 0 (bug) | 9,31 |

A compra extra no T1 (1 carta a mais em ~toda partida, já que é praticamente garantida) empurrou todas as métricas de consistência pra cima de forma consistente — comandante mais rápido, mais ramp em jogo, mais finisher resolvido. A taxa de finisher até T8 subiu de 42,8% pra **48,4%** — quase metade das partidas agora, o número mais confiável que tenho até aqui pra essa métrica, já com as duas correções aplicadas.

### Terceira e quarta correção — Germination Practicum (Paradigm nunca implementada) e Genji Glove (custo de equip ignorado)

Você perguntou se o Paradigm da Germination Practicum tinha sido implementado, e se a Genji Glove tinha sido avaliada como finisher considerando os {5} de cast **+ {3} de equip separado** (confirmado via Scryfall: `{3}{G}{G}` pra conjurar, texto *"Put two +1/+1 counters on each creature you control. Paradigm..."*; Genji Glove é `{5}` pra conjurar, `Equip {3}`, e o combate extra só dispara quando a criatura equipada ataca). As duas eram bugs reais:

- **Germination Practicum:** só existia como tag `counters_engine` sem lógica nenhuma — cast dela não fazia nada além de contar como "spell conjurado" genérico. O Paradigm (recast de graça do exílio a cada primeiro main phase seu, a partir do turno seguinte) não existia.
- **Genji Glove:** o script marcava ela como finisher **resolvido no momento do cast** (5 mana), ignorando completamente o Equip {3} separado e o requisito de a criatura equipada realmente atacar pra disparar o combate extra.

**Correções aplicadas:**
- Germination Practicum agora aplica +2/+2 (2 contadores) a cada criatura em campo no cast, e repete isso automaticamente a cada main phase seu a partir do turno seguinte (Paradigm). Como o motor não rastreia poder por criatura individualmente (limitação estrutural que já tínhamos identificado no Jogo 6, sobre Ghalta/Great Henge não terem redução de custo modelada), reporto o total acumulado de contadores como métrica agregada (`counters_on_board`), não como buff aplicado a criaturas específicas.
- A recast via Paradigm também conta como um spell de verdade sendo conjurado (é uma cópia sendo lançada), então agora também alimenta o crescimento da Managorger Hydra quando as duas estão em jogo juntas — sinergia real que passou a existir no modelo.
- Genji Glove só entra como finisher resolvido quando **equipada** (checagem separada de {3} de mana, no mesmo turno do cast se sobrar mana suficiente pro teto do modelo, senão automaticamente no turno seguinte) **e** existe criatura em campo pra atacar com ela.

**Re-execução com n=2000, as quatro correções juntas:**

| Métrica | Com só Managorger+T1 corrigidos | Com as 4 correções |
|---|---|---|
| % partidas com finisher até T8 | 48,4% | **48,0%** (quase igual — Genji Glove equipa em 97,9% dos jogos em que é conjurada, só que mais tarde) |
| Avg turno do 1º finisher relevante | 5,78 | 5,97 |
| Germination Practicum conjurada | (não rastreado) | 21,1% dos jogos |
| Avg contadores totais no board (via Germination Practicum) | 0 (bug) | **7,08** |
| Genji Glove conjurada | (não rastreado) | 19,4% dos jogos |
| Genji Glove efetivamente equipada | (assumido 100% no cast) | **97,9%**, turno médio 6,01 |

A taxa geral de finisher até T8 quase não mudou (48,0% vs 48,4%), mas a composição ficou mais honesta: antes a Genji Glove "resolvia" instantaneamente ao ser conjurada (T5 em média); agora ela precisa do Equip {3} e efetivamente entrega o combate extra por volta do T6 — um turno mais tarde, e corretamente condicionado a ter uma criatura pra atacar.

### Confirmação — segunda rodada de n=2000 com seed independente

Rodei outra vez com `seed_base=350000` em vez de `91000` (senão seria uma repetição idêntica dos mesmos jogos, não uma confirmação real — adicionei o parâmetro `seed_base` em `run_batch` pra isso):

| Métrica | Rodada 1 (seed 91000) | Rodada 2 (seed 350000, confirmação) |
|---|---|---|
| Avg commander cast turn | 4,03 | 4,03 |
| Commander cast by T4 | 69,5% | 69,5% |
| Commander cast by T5 | 88,8% | 88,5% |
| Avg Bear count final | 6,22 | 6,26 |
| % partidas com finisher até T8 | 48,0% | 46,0% |
| Managorger — avg contadores finais | 9,47 | 9,72 |
| Germination Practicum — avg contadores no board | 7,08 | 7,25 |
| Genji Glove — taxa de equip / turno médio | 97,9% / T6,01 | 97,1% / T5,96 |

Tudo dentro de 1-2 pontos percentuais entre as duas rodadas — a maior diferença é a taxa de finisher até T8 (48,0% vs 46,0%, ~2 pontos), compatível com o erro-padrão estimado de ±1,5pp que já tínhamos calculado antes pra essa métrica nesse tamanho de amostra. As correções (Managorger, compra do T1, Germination Practicum, Genji Glove) produzem resultados estáveis e reprodutíveis, não são artefato de uma sequência de sorteio específica.

---

## Jogo 1

**Mulligan:** 1 (mão inicial de 7 mulliganada; mão final mantida)

**Mão inicial mulliganada:** Unnatural Growth, Ayula's Influence, Chronicle of Victory, Ghalta Primal Hunger, Garruk's Uprising + 2 Forest

**Mão mantida (7 cartas):** Eternal Witness, Selvala Heart of the Wilds, Managorger Hydra, Little Bear + 3 Forest

**Turno a turno:**
- T1: Forest
- T2: compra Haywire Mite; Forest (2º land); joga Haywire Mite
- T3: compra Forest; Forest (3º land); joga Managorger Hydra
- T4: compra Chameleon Colossus; Forest (4º land); joga Selvala, Heart of the Wilds; Managorger Hydra sobe pra 4 contadores +1/+1
- T5: compra Forest; Forest (5º land); **Beorn the Fierce entra da command zone** — gatilho mira o Managorger Hydra, que vira Urso (contador de trample); Managorger ataca; compra Solemn Simulacrum; joga Chameleon Colossus; Managorger sobe pra 6 contadores +1/+1 (spells de oponentes contando também, por decisão do jogador durante a simulação)

**Board final (fim do T5):**
- Terrenos: 5 Forest
- Criaturas: Haywire Mite; Managorger Hydra (6 contadores +1/+1, Urso, trample — efetivamente 9/9 com o +2/+2 da Beorn); Selvala, Heart of the Wilds; Chameleon Colossus; Beorn the Fierce
- Mão: Solemn Simulacrum

**Destaque:** primeira confirmação do motor "criatura cresce sozinha → vira Urso → cresce ainda mais" funcionando desde o turno 5.

---

## Jogo 2

**Mulligan:** 0 (mão mantida)

**Mão inicial (7 cartas):** Patchwork Banner, Firdoch Core, Ohran Frostfang, Germination Practicum, Cultivate, War Room + 1 Forest

**Turno a turno:**
- T1: Forest
- T2: compra Springleaf Parade; Forest (2º land)
- T3: compra Ohran Frostfang (jogado depois); joga Emerald Medallion
- T4: compra Nykthos, Shrine to Nyx; Nykthos jogado (4º land); joga Radagast of Rhosgobel
- T5: **Beorn the Fierce entra da command zone** — gatilho mira o Radagast (já reduzido pela própria habilidade dele), que vira Urso com trample; compra Lotus Cobra; joga Lotus Cobra
- T6: compra Firdoch Core; joga Firdoch Core e Little Bear; Beorn ataca (ganha +1/+1); segundo combate mira o Lotus Cobra, que também vira Urso com trample; compra Defiler of Vigor, Haywire Mite, Lightning Greaves; joga Haywire Mite
- T7: joga Defiler of Vigor; compra Tireless Provisioner e Patchwork Banner

**Board final (fim do T7):**
- Terrenos: 2 Forest, Nykthos Shrine to Nyx, War Room
- Mana extra: Firdoch Core
- Criaturas: Beorn the Fierce (+1/+1); Radagast of Rhosgobel (Urso, 2 contadores +1/+1, trample); Lotus Cobra (Urso, 2 contadores +1/+1, trample); Little Bear; Haywire Mite; Defiler of Vigor

**Correção aplicada durante o jogo:** o Ohran Frostfang foi inicialmente descrito errado (como equipamento gerador de Cobra); corrigido para o oracle real — criatura Snake 2/6, dá deathtouch a atacantes e compra carta por dano de combate a jogador.

---

## Jogo 3

**Mulligan:** 1

**Mão inicial mulliganada:** Solemn Simulacrum, Germination Practicum, Tireless Tracker, Ezuri's Predation, Lumra Bellow of the Woods, Bala Ged Recovery, Ayula Queen Among Bears

**Mão mantida (7 cartas):** Craterhoof Behemoth, Maskwood Nexus, Tireless Provisioner, Garruk's Uprising, Beorn's Hospitality + 2 Forest

**Turno a turno:**
- T1-T2: Forest, Forest
- T3: Shamanic Revelation comprada; Forest (3º land); joga Beorn's Hospitality
- T4: Forest (4º land); joga Tireless Provisioner
- T5: Forest (5º land); joga Garruk's Uprising; landfall gera Treasure via Tireless Provisioner e +1/+1 counter via Beorn's Hospitality (a Hospitality bota contador em criatura, não faz Treasure — ver correção abaixo); compra Tribute to the World Tree
- T6: Forest (6º land); joga Tribute to the World Tree e Toski, Bearer of Secrets; **Beorn the Fierce entra da command zone** — converte o Toski em Urso com trample
- T7: joga Archdruid's Charm (comprado), Lightning Greaves, Maskwood Nexus, Allosaurus Shepherd (protegendo magias verdes); Chameleon Colossus e mais um Toski entram
- T8: joga Ayula Queen Among Bears, Herd Heirloom, Sol Ring, Forgotten Ancient

**Board final (fim do T8):**
- Terrenos: ~9 Forest
- Mana extra: Sol Ring, Herd Heirloom, Treasure
- Criaturas: Toski Bearer of Secrets (Urso, 4 contadores +1/+1, trample); Ayula Queen Among Bears (2 contadores +1/+1); Allosaurus Shepherd (2 contadores +1/+1, trample); Chameleon Colossus; Forgotten Ancient; Tireless Provisioner; Maskwood Nexus

**Correção aplicada:** os contadores do Tireless Provisioner vieram do Landfall do Beorn's Hospitality, não da Tribute to the World Tree (que só afetou criaturas que entraram depois dela, turno 6+).

---

## Jogo 4 (recomeço do Jogo com Radagast — pediu pra refazer do zero por erro de jogo)

**Mulligan:** 0

**Mão inicial (7 cartas):** Song of the Dryads, Tribute to the World Tree, Little Bear, Gigantic Big Bear + 3 Forest

**Turno a turno:**
- T1-T3: Forest, Forest, Forest; joga Tribute to the World Tree no T3
- T4: joga Nykthos, Shrine to Nyx (4º land)
- T5: Forest (5º land); **Beorn the Fierce entra da command zone**
- T6: Forest (6º land); joga Emerald Medallion e Germination Practicum (resolve, depois exilado via Paradigm); Beorn ganha 2 contadores +1/+1
- T7: joga Gigantic Big Bear — gatilho de combate da Beorn mira ele, vira Urso com trample
- T8: joga Little Bear, Roaming Throne (escolhendo Bear) e Tireless Provisioner — este último vira Urso com trample no 2º combate do turno
- T9: novo land via landfall do Tireless Provisioner, gera Treasure

**Board final (fim do T9):**
- Terrenos: ~6 Forest, Nykthos Shrine to Nyx
- Mana extra: Emerald Medallion, Treasure
- Criaturas: Beorn the Fierce (2 contadores +1/+1); Gigantic Big Bear (Urso, trample); Tireless Provisioner (Urso, trample); Little Bear
- Outros: Roaming Throne (tipo Bear escolhido)
- Mão: Beast Whisperer, Ezuri's Predation, Heroic Intervention, Ambush Viper

**Observação:** um bloco de 5 cópias extras de Emerald Medallion apareceu por erro de clique no simulador — ignorado no registro final.

---

## Jogo 5 (primeiro goldfish em que o Craterhoof Behemoth resolveu)

**Mulligan:** 0

**Mão inicial (7 cartas):** Lotus Cobra, Toski Bearer of Secrets, Emerald Medallion, Bala Ged Recovery, Allosaurus Shepherd, Craterhoof Behemoth + 1 Forest

**Turno a turno:**
- T1: Forest; joga Allosaurus Shepherd
- T2: Bala Ged Recovery jogado como terreno (lado Sanctuary); compra Springleaf Parade
- T3: joga Emerald Medallion; compra Ohran Frostfang
- T4: joga Lotus Cobra; compra Dancing from Dark to Dawn
- T5: novo Forest; joga Toski, Bearer of Secrets
- T6: joga Birds of Paradise
- T7: **Beorn the Fierce entra da command zone** — converte o Toski em Urso com trample
- T8: compra Natural Order; joga Springleaf Parade com X=4, criando 4 tokens Shapeshifter (changeling); joga Dancing from Dark to Dawn e Scavenger Grounds (gera um token Bear via Landfall do Dancing)
- T9 (turno final): joga **Last March of the Ents** — com a maior toughness do board, compra várias cartas e coloca **Ohran Frostfang e Craterhoof Behemoth** direto no campo, de graça

**Board final:**
- Terrenos: vários Forest, Bala Ged Sanctuary, Scavenger Grounds
- Criaturas: Toski (Urso, trample); Birds of Paradise; 4x tokens Shapeshifter (changeling = Urso); token Bear (Dancing from Dark to Dawn); Ohran Frostfang; **Craterhoof Behemoth**

**Análise pós-jogo (cálculo de combate manual):**
Com o Craterhoof resolvendo (X = 11 criaturas em campo), o board teórico pós-buff seria:
- Beorn the Fierce: 17/17 trample
- Craterhoof Behemoth: 16/16 trample (tem haste própria)
- Toski, Bearer of Secrets: 14/14 trample
- Token Bear (Dancing): 15/15 trample
- Birds of Paradise: 11/12 trample
- Lotus Cobra: 12/12 trample
- Ohran Frostfang: 13/17 trample (mas SEM haste — não pode atacar no turno que entra)
- 4x Shapeshifter: 14/14 cada (mas tapados pra pagar mana do Last March — não atacam)

Atacantes disponíveis: Beorn, Craterhoof, Toski, token Bear, Birds of Paradise, Lotus Cobra = **85 de poder total**, suficiente pra matar 2 de 3 oponentes num pod de 40 de vida cada, mas não os 3 simultaneamente (cada atacante só ataca um jogador por vez).

**Discussão estratégica:** avaliou-se se valeria a pena segurar o Craterhoof na mão (não usar o Last March pra colocá-lo em jogo) e conjurá-lo no turno seguinte pra disparar o Dancing from Dark to Dawn (+8 contadores via valor de mana 8). Conclusão: não vale a pena — matar 2 oponentes garantidos agora é melhor do que arriscar um board parado por um turno inteiro contra board wipe/remoção, por um ganho marginal de contadores que não muda o resultado do jogo.

---

## Padrões confirmados nos 5 jogos

1. A Beorn chega em jogo de forma consistente entre os turnos 4-7.
2. O gatilho de conversão em Urso sempre encontrou um alvo relevante no primeiro combate disponível.
3. Peças "fabricadoras de Urso" alternativas (Beorn's Hospitality, Tribute to the World Tree, Roaming Throne, Maskwood Nexus, Springleaf Parade) apareceram em jogos diferentes e sempre geraram valor, independente do timing da Beorn.
4. O Craterhoof Behemoth, quando resolveu (Jogo 5), confirmou ser um fechador de jogo real — 85+ de poder disponível em um único turno.
5. Nenhum dos 5 jogos testou ativamente a remoção do deck (Beast Within, Song of the Dryads, Ezuri's Predation) sendo usada contra ameaças reais, nem o combo Genji Glove (fase de combate extra).

---

## Jogo 6

**Correções feitas pelo usuário após a primeira versão deste registro (todas verificadas e aplicadas):**
1. Germination Practicum foi conjurado no T5, **depois** do Allosaurus Shepherd (não antes/incerto como eu tinha escrito).
2. Firdoch Core **conta como Urso desde que entra em campo**, mesmo sem ser ativado como criatura — Changeling ("This card is every creature type") dá o subtipo Bear ao permanente independentemente de ele ser criatura ou não; eu tinha avaliado errado que só contaria se fosse animado. Confirmado também que a própria Beorn the Fierce é `type_line: Legendary Creature — Bear Shapeshifter Warrior` — ela mesma é um Urso.
3. Eu errei ao chamar o T1 de "estar na compra, não na estrela": pela regra oficial (Comprehensive Rules 103.8a), a compra do turno 1 só é pulada em jogos **de 2 jogadores** — em Commander multiplayer (3+ jogadores), ninguém pula a primeira compra, nem quem começa. Comprar uma 8ª carta no T1 é o comportamento padrão de mesa, não um sinal de estar "na compra". Isso também expõe uma falha real no `beorn_goldfish_v1.py`: o parâmetro `on_play` do script modela a regra de 2 jogadores (pula a 1ª compra de quem começa), o que não corresponde a como Commander realmente funciona — o script deveria sempre dar a compra do T1, independente de quem começa.

**Mão inicial (7 cartas, ver imagem anexada):** Eternal Witness, Germination Practicum, Managorger Hydra, Lotus Cobra + 3 Forest

**Turno a turno (ações confirmadas):**
- T1: compra Scavenger Grounds (compra normal de mesa multiplayer, turno 1 de quem começa); Forest (1º land)
- T2: compra Firdoch Core; Forest (2º land); joga Lotus Cobra
- T3: compra Forest; Forest (3º land, aciona landfall da Lotus Cobra); joga Firdoch Core — **já é Urso desde que entra (Changeling)**
- T4: compra Bala Ged Recovery // Bala Ged Sanctuary; Forest (4º land, landfall); **Beorn the Fierce entra da command zone** (T4 — bate exatamente com a média de T4,25 dos 2000 goldfishes simulados); no combate, gatilho da Beorn mira a Lotus Cobra, que vira Urso — **e com Firdoch Core + Lotus Cobra + a própria Beorn, já são 3 Ursos no primeiro combate possível, disparando "compre 2" já no T4**
- T5: compra Springleaf Parade; Forest (5º land); joga Managorger Hydra (2º gatilho de combate da Beorn mira nela, também vira Urso); compra Song of the Dryads e Allosaurus Shepherd; joga Allosaurus Shepherd, depois **Germination Practicum** (dá +2/+2 a cada criatura em campo — Beorn chega a 2 contadores por isso), e Song of the Dryads
- T6: compra Forest; Forest (6º land); joga Dancing from Dark to Dawn
- T7: compra Forest; Forest (7º land, cria token Bear 2/2 via landfall do Dancing); joga Solemn Simulacrum (busca +1 land); landfall do Solemn cria outro token Bear; compra Ambush Viper e Forest
- T8: compra Ghalta, Primal Hunger; joga Ghalta (custo reduzido pelo poder total do board — bem mais barato que o CMC 12 cheio); compra The Great Henge; joga Great Henge (custo reduzido pelo maior poder entre suas criaturas) e Springleaf Parade com X=6, criando **6 tokens Shapeshifter** (cada um vira mana dork de qualquer cor)

**Board ao fim do T8 (citado direto do JSON, sem reconstrução):**
- Beorn the Fierce: 18 contadores +1/+1 → base 6/6 + 18 = **24/24** trample
- Managorger Hydra: 8 contadores +1/+1, Urso (+2/+2 do anthem) → **~11/11** trample
- Lotus Cobra: 10 contadores +1/+1, Urso (+2/+2 do anthem) → **~14/13** trample
- Ghalta, Primal Hunger: já com contador de trample e Urso, 2 contadores +1/+1 → base 12/12 + 2 + 2 (anthem) = **~16/16**
- 6 tokens Shapeshifter (Springleaf Parade): 2 contadores +1/+1 cada → **3/3** cada, todos taps por mana de qualquer cor
- 2-3 tokens Bear (Dancing from Dark to Dawn, landfall): 2/2 base, alguns já com contadores
- The Great Henge e Firdoch Core em campo — Firdoch nunca foi ativado como criatura nesse jogo, mas **contou como Urso o tempo todo mesmo assim** (Changeling dá o subtipo Bear independente de ser criatura ou não), contribuindo pro "3+ Ursos" da Beorn desde que entrou em campo no T3

**Achado mais importante — limitação real do meu simulador Python (`beorn_goldfish_v1.py`):** o script que rodei nos 2000 goldfishes trata custo de mana como fixo (CMC cheio) pra todas as cartas, incluindo Ghalta, Primal Hunger e The Great Henge. Nesse jogo real, as duas resolveram no turno 8 pagando muito menos que o CMC nominal (12 e 9), porque ambas reduzem custo com base no poder do board — exatamente o cenário que o motor de contadores (Germination Practicum + Dancing from Dark to Dawn + conversão em Urso da Beorn) cria. Isso significa que a taxa de 42,8% de "finisher até T8" que os 2000 goldfishes simulados indicaram provavelmente **subestima** a taxa real nas partidas em que esse motor de contadores liga cedo (turno 5-6, como aconteceu aqui) — o simulador não modela esse desconto de custo, então penaliza artificialmente Ghalta e Great Henge como se fossem sempre CMC cheio.

---

### Implementado — duplicação de gatilhos do Roaming Throne (tipo Bear)

Mesma regra permanente aplicada no Thranduil (pedido do usuário: implementar de verdade em qualquer deck com essa carta, documentado em `references/goldfish-sim-card-rules.md`). Roaming Throne estava só com a tag `"double_trigger"`, sem lógica nenhuma.

**Premissa:** tipo escolhido sempre "Bear" — a própria Beorn é `Legendary Creature — Bear Shapeshifter Warrior`, então o próprio gatilho de combate dela (converte criatura em Urso, depois checa 3+ Ursos → compra 2) dispara **uma segunda vez completa** quando o Roaming Throne está em campo: converte outra criatura, recheca a contagem de Ursos de novo (podendo disparar o "compre 2" duas vezes no mesmo combate).

**Resultado (n=2000):**

```
Roaming Throne em campo em 21,4% dos jogos (tipo escolhido: Bear)
Avg gatilhos de combate da Beorn dobrados por partida: 3,44
```

---

### Correção #1 — mana gasta no turno nunca era rastreada (bug fundamental)

**Gatilho (usuário):** "VAMOS REVISAR O BEORN do mesmo modo, carta por carta e o simulador todo"

Antes de auditar carta por carta, encontrei um bug estrutural que invalidava qualquer contagem de gatilhos por spell: `can_cast()` comparava o custo de cada carta contra `total_mana(state)` — o total de fontes de mana em campo — mas **nada subtraía a mana já gasta em cast anteriores no mesmo turno**. Testei ao vivo: com 6 fontes de mana em campo e Tireless Tracker (3) + Beast Whisperer (4) + Little Bear (3) na mão (10 de custo total), o `main_phase()` conjurava **as três**, usando 6 de mana real pra pagar 10.

Isso inflava artificialmente `spells_cast` (e por tabela: contadores da Managorger Hydra, gatilhos da Roaming Throne, Genji Glove equipando cedo demais, etc.) e acelerava todo o desenvolvimento de board a cada jogo simulado, todo jogo.

**Correção:**
- Novo campo `mana_spent_this_turn` em `GameState`, resetado no início de cada `play_turn()`.
- Novo helper `remaining_mana(state) = total_mana(state) - mana_spent_this_turn`.
- `can_cast()` agora compara contra `remaining_mana()`, não `total_mana()`.
- `cast_spell()` incrementa `mana_spent_this_turn` pelo `mv` real da carta conjurada; os dois pontos de cast do comandante em `main_phase()` (antes do loop e dentro dele) fazem o mesmo.
- Genji Glove: a lógica de equipar (Equip {3}, custo separado do cast {5}) usava um teto arbitrário (`total_mana >= 8` no turno do cast, `>= 3` depois) pra compensar a falta de rastreamento — trocada por `remaining_mana(state) >= 3` (que agora funciona corretamente tanto no turno do cast quanto depois), debitando os 3 do Equip do mesmo jeito.

**Resultado (n=2000, seed_base=6000000, antes → depois):**

| Métrica | Antes (bug) | Depois (corrigido) |
|---|---|---|
| Avg spells cast | 15.65 | 10.42 |
| Avg extra draws (gatilhos) | 11.93 | 7.17 |
| Avg Bear count final | 7.16 | 5.68 |
| Beorn "draw 2" triggers (3+ Bears) | 4.28 | 3.07 |
| Beorn combat triggers | 5.53 | 4.50 |
| Avg finishers resolvidos | 0.64 | 0.09 |
| **% de jogos com finisher até T8** | **49.6%** | **8.3%** |
| Avg battlefield final | 19.79 | 15.73 |
| Managorger conjurada | 23.8% | 18.9% |
| Managorger avg contadores finais | 10.25 | 7.63 |
| Germination Practicum conjurada | 23.7% | 8.0% |
| Genji Glove conjurada | 18.4% | 3.7% |
| Genji Glove equipada (dado que conjurada) | 99.2% | 58.1% |
| Roaming Throne em campo | 23.9% | 14.4% |

O impacto é enorme — a taxa de "finisher até T8" caiu de quase metade dos jogos pra menos de 1 em 10. Todo número reportado em qualquer entrada anterior deste log (incluindo os 42,8%/48,4% mencionados no Jogo 6, que já vinham de UMA rodada de 2000 jogos deste mesmo simulador com bug) estava inflado por esse bug — o simulador estava efetivamente jogando com mana infinita dentro de cada turno.

**Robustez:** sweep de 20.000 jogos (seeds 6000000–6019999, timeout de 2s/jogo) rodado após a correção — 0 erros, 0 timeouts.

---

### Correção #2 — doença de invocação pros mana dorks

Consequência direta da Correção #1: com mana real rastreada, ficou óbvio que os mana dorks criatura (Birds of Paradise, Llanowar Elves, Lotus Cobra, Selvala, Heart of the Wilds) estavam contribuindo pra `total_mana()`/`green_sources()` **no próprio turno em que eram conjurados**, o que é ilegal — criatura sem haste não pode usar habilidade de `{T}` no turno em que entra (CR 302.6). Isso não afeta terrenos nem artefatos de mana (Sol Ring, Necklace of Girion, Patchwork Banner, Firdoch Core) — só permanentes do tipo Creature.

**Correção:** novo campo `dork_entered_turn: Dict[str,int]` em `GameState`, populado em `cast_spell()` quando uma criatura com a tag `ramp` entra em campo. `total_mana()`/`green_sources()` agora pulam qualquer dork cujo turno de entrada seja igual ao turno atual.

**Resultado (n=2000, seed_base=6000000):**

| Métrica | Antes (Correção #1) | Depois (Correção #2) |
|---|---|---|
| Avg spells cast | 10.42 | 10.22 |
| % de jogos com finisher até T8 | 8.3% | 7.2% |
| Avg battlefield final | 15.73 | 15.57 |
| Managorger conjurada | 18.9% | 18.6% |

Impacto pequeno e no sentido esperado (menos mana disponível cedo = leve desaceleração). **Robustez:** sweep de 20.000 jogos, 0 erros, 0 timeouts.

---

### Correção #3 — auditoria carta por carta: gatilhos 100% ausentes (ETB, cast, landfall)

**Gatilho (usuário):** "VAMOS REVISAR O BEORN do mesmo modo, carta por carta e o simulador todo"

Comparei o `oracle_text` real de todas as 70 cartas (via Scryfall) contra o código carta por carta. Achado mais grave: **não existia nenhum despacho de landfall** — apesar de 6 cartas do deck dependerem dele (Lotus Cobra, Tireless Tracker, Tireless Provisioner, Beorn's Hospitality, Dancing from Dark to Dawn, Necklace of Girion), nada disparava quando um terreno entrava em campo. Junto com isso, vários gatilhos de "criatura entra"/"conjura um spell" também estavam totalmente ausentes.

**Implementado nesta rodada:**
- Infraestrutura nova: `on_creature_enters()`, `on_spell_cast_effects()`, `on_land_enters()` — despachantes centralizados chamados em todo lugar que uma criatura/spell/terreno entra em campo (land drop normal, terrenos buscados por rampa, criaturas coladas via cheat-into-play), substituindo os poucos `if card == "X"` soltos que existiam.
- **Ayula, Queen Among Bears** (0% → implementada): outro Bear entrando põe 2 contadores +1/+1 num Bear (IA sempre escolhe o modo de contador, não o modo de luta, que não é simulável nesse motor).
- **Ayula's Influence** (0% → implementada): ativação repetível "descarta uma land: cria um Bear 2/2", condicionada a sobrarem 2+ lands na mão.
- **Maskwood Nexus** (0% → implementada): agora concede o tipo Bear pra TODAS as suas criaturas globalmente (`is_bear()` centralizado, novo helper), e a ativação `{3},{T}: cria Shapeshifter 2/2 changeling` roda com mana sobrando.
- **Beast Whisperer**: "conjura criatura → compra" agora dispara de verdade (antes só tinha a tag, sem lógica).
- **Necklace of Girion**: "conjura spell verde" e "Forest entra" (via landfall, considerando Yavimaya) agora dão o contador de verdade.
- **Dancing from Dark to Dawn**: as DUAS metades agora funcionam — contador X (mv do spell) em criatura conjurada, e token Bear 2/2 via landfall (antes só a tag existia, zero lógica).
- **Garruk's Uprising**: ETB próprio (compra se já controla poder 4+) e o gatilho recorrente (criatura poder 4+ entra → compra) implementados via `BASE_POWER`.
- **Tribute to the World Tree**: criatura entra → compra se poder≥3, senão 2 contadores.
- **The Great Henge**: removido o proxy antigo e **errado** ("compra 1 no próprio cast se bear_count>0", que não é o texto real da carta) — agora é o gatilho de verdade: cada criatura NÃO-token que entra dá 1 contador +1/+1 + compra 1.
- **Selvala, Heart of the Wilds**: "compra se poder maior que qualquer outra criatura" aproximado via `max_power_seen` rastreado ao longo do jogo.
- **Forgotten Ancient**: contador em cada spell seu conjurado + heurística de +2/turno pros spells de oponentes (mesmo padrão já usado pra Managorger Hydra).
- **Little Bear**: metade modelável do ETB implementada (+1/+1 counter se já existe outro Bear em campo); a metade "untap" não tem efeito simulável nesse motor (documentado).
- **Chronicle of Victory**: "conjura spell do tipo escolhido → compra" implementado (tipo escolhido: Bear, mesma convenção da Roaming Throne).
- **Last March of the Ents**: era um proxy fixo de "compra 6" hardcoded — agora usa a maior toughness real em campo (`BASE_TOUGHNESS`, tabela nova) E implementa a segunda metade da carta, que estava 100% ausente: colocar criaturas da mão em campo de graça.
- **Tireless Tracker**: landfall agora gera Clue de verdade (`state.clues`), craqueado com mana sobrando (`try_crack_clues`) por {2}: compra 1 + contador na Tracker.
- **Bug de fetch**: Cultivate/Three Visits/Sakura-Tribe Elder/Solemn Simulacrum buscavam **qualquer terreno da biblioteca** (incluindo os 6 não-básicos nomeados) — o texto real busca land básica/Forest, e nesse decklist só "Forest" se qualifica. Corrigido, e agora o terreno buscado também dispara landfall (antes não disparava).
- **Correção de log**: Jogo 3 dizia que o Treasure veio do Beorn's Hospitality (landfall) — a Hospitality bota +1/+1 counter, não faz Treasure; era o Tireless Provisioner (também em campo) que gerou o Treasure. Texto corrigido acima.

**Resultado (n=2000, seed_base=6000000, antes → depois):**

| Métrica | Antes (Correção #2) | Depois (Correção #3) |
|---|---|---|
| Avg spells cast | 10.22 | 10.76 |
| Avg extra draws (gatilhos) | 6.99 | 8.53 |
| Avg Bear count final | 5.63 | 6.16 |
| Avg battlefield final | 15.57 | 16.79 |
| Avg terrenos jogados | 6.39 | 6.51 |
| Germination Practicum — contadores totais no board | 1.26 | 6.94 |
| % de jogos com finisher até T8 | 7.2% | 6.8% |

Impacto moderado e no sentido esperado: mais compra (draw engines reais agora funcionando), mais Bears (Ayula's Influence + Dancing from Dark to Dawn landfall + Maskwood), mais contadores no board (Last March colocando criaturas extras em campo pra Germination Practicum's Paradigm buffar). Taxa de finisher ficou estável (~7%), já que os gatilhos implementados nesta rodada são majoritariamente motores de compra/contadores, não finalizadores diretos.

**Não implementado nesta rodada (decisão consciente, mesma convenção de sempre documentar em vez de fingir que não existe):** redução de custo baseada em poder (Ghalta, The Great Henge, Goreclaw, Defiler of Vigor, Radagast, Emerald Medallion) — já é uma limitação conhecida documentada no Jogo 6 deste log. Exigiria rastrear poder por criatura individualmente (esse motor só tem um agregado `counters_on_board`, não por criatura), uma mudança arquitetural maior que fica pra uma próxima rodada se você quiser que eu ataque isso.

**Robustez:** sweep de 20.000 jogos, 0 erros, 0 timeouts.

---

<!-- Para novas partidas avulsas, use o formato abaixo -->

## Partida #N — AAAA-MM-DD

- **Formato do teste:** goldfish / playtest com amigos / mesa competitiva
- **Mão inicial (mulligan até):**
- **Turno da primeira jogada relevante:**
- **Turno do primeiro ataque/combo:**
- **Curva de mana observada:**
- **Bombas/peças-chave puxadas:**
- **Removals sofridos/enviados:**
- **Resultado:** vitória / derrota / sem resolução
- **Turno de fim de jogo:**
- **O que funcionou bem:**
- **O que travou o deck:**
- **Ajustes a considerar:**
