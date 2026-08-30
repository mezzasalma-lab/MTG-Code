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

### Correção #4 — redução de custo baseada em poder (Ghalta, Great Henge, Goreclaw, Radagast, Emerald Medallion, Defiler of Vigor)

**Gatilho (usuário):** escolha explícita entre as opções de continuação — priorizar a maior peça arquitetural que faltava, já sinalizada como limitação conhecida no Jogo 6 ("a taxa de 42,8%/48,4% provavelmente subestima a taxa real, porque o simulador trata Ghalta e Great Henge como CMC cheio").

**Implementado:**
- `total_power_in_play(state)` — soma exata (não é aproximação: poder total não depende de qual criatura tem qual contador, só da soma) usada pelo Ghalta ("custa {X} menos, onde X é o poder total das suas criaturas").
- `greatest_power_in_play(state)` — usado pelo Great Henge ("custa {X} menos, onde X é o maior poder"). Esse **é** uma premissa explícita: como o sim só rastreia `counters_on_board` como total agregado (não por criatura), assume que todos os contadores foram parar na sua maior criatura — é o que um jogador ótimo faria em qualquer gatilho "target creature you control" (a maioria dos geradores de contador do deck), e é a estimativa mais otimista/realista disponível sem reescrever o motor pra rastrear contadores por criatura.
- `effective_cost(state, card)` centraliza todos os redutores: Ghalta, Great Henge, Goreclaw ("creature spells com poder 4+ custam {2} menos"), Emerald Medallion ("green spells custam {1} menos"), Defiler of Vigor ("pode pagar 2 vida: green permanent spells custam {G} menos" — sim não rastreia vida, então assume que sempre paga), Radagast ("a primeira creature spell no turno custa {2} menos" — nova flag `radagast_discount_available`, resetada a cada turno, consumida no primeiro creature spell pago). Toda redução respeita o piso dos pips coloridos (CR 601.2f: redução genérica nunca reduz abaixo do custo colorido).

**Correção pós-review (o usuário pegou):** minha descrição inicial do Radagast citou só a metade do desconto. O texto real é "costs {2} less to cast **and can be cast as though it had flash**" — a metade flash não tinha sido mencionada nem implementada. Ela continua sem efeito modelável (esse motor só conjura na main phase do próprio turno, não simula turno do oponente/janela de instant-speed — mesma ressalva já documentada pro "untap" do Little Bear), mas agora está documentada explicitamente no código-fonte em vez de simplesmente omitida do relato.
- `can_cast()` e `cast_spell()` agora usam `effective_cost()` em vez do `mv` cru — inclusive nos dois pontos de cast do comandante.

**Achado lateral, corrigido na mesma rodada:** ao montar as tabelas de poder pra isso, notei que `g_pips` (pips de `{G}` no custo, usado pra checar "fontes verdes suficientes") estava errado pra ~40 cartas — os blocos de definição (`draw_defs`, `removal_defs`, `protection_defs`, `bear_defs`, `counters_defs`, `finisher_defs`) davam `g_pips=1` pra **todo mundo do grupo**, sem olhar o custo real. Isso deixava cartas incolores (Chronicle of Victory `{6}`, Genji Glove `{5}`, Roaming Throne `{4}`, Solemn Simulacrum `{4}`, etc.) exigindo 1 fonte verde à toa, e cartas `{G}{G}`/`{G}{G}{G}`/`{G}{G}{G}{G}` (Craterhoof `{G}{G}{G}`, Great Henge `{G}{G}`, Unnatural Growth `{G}{G}{G}{G}`, Tribute to the World Tree `{G}{G}{G}`, Archdruid's Charm `{G}{G}{G}`, Ayula's Influence `{G}{G}{G}`, etc.) exigindo só 1 quando precisam de 2-4. `ramp_defs` tinha uma fórmula própria que também errava o Radagast (conflava "produz mana verde" com "custa mana verde" — Radagast não produz, mas custa `{2}{G}{G}`). Corrigido com uma tabela `REAL_G_PIPS` com os pips reais de cada carta (Scryfall), aplicada sobre o `CARD_DB` depois de todos os `add()`.

**Resultado (n=2000, seed_base=6000000, antes → depois):**

| Métrica | Antes (Correção #3) | Depois (Correção #4) |
|---|---|---|
| Avg spells cast | 10.76 | 11.53 |
| Avg extra draws (gatilhos) | 8.53 | 9.56 |
| Avg finishers resolvidos | 0.07 | 0.23 |
| **% de jogos com finisher até T8** | **6.8%** | **21.6%** |
| Avg turno do 1º finisher relevante | 7.00 | 6.71 |
| Avg battlefield final | 16.79 | 17.59 |

Confirma a hipótese do seu Jogo 6: a taxa de finisher estava mesmo subestimada por tratar Ghalta/Great Henge/Craterhoof (via Goreclaw/Radagast) como CMC cheio. Com redução de custo real, mais que triplicou (6.8% → 21.6%) — o efeito mais forte de qualquer correção nesta sessão depois do bug de mana do turno.

**Ainda não modelado (documentado, não é bug):** Ghalta/Great Henge não têm floor extra além dos pips coloridos — na prática eles quase sempre viram apenas `{G}{G}` de custo assim que o board tem poder suficiente, o que é o comportamento real da carta. Springleaf Parade (spell `{X}{G}{G}`) continua sem tratamento de X — fica pra uma rodada futura se quiser.

**Robustez:** sweep de 20.000 jogos, 0 erros, 0 timeouts.

---

### Correção #5 — "TODOS os gatilhos do deck", auditoria final carta por carta

**Gatilho (usuário):** *"Quero TODOS os gatilhos do deck contabilizadoa na simulação. Corrija isso e rode a simulação 5k vezes, me dê os números e explique o seu significado individual."*

Reli o arquivo inteiro (1186 linhas na época) e comparei, carta por carta, os 69 nomes únicos do decklist contra o `oracle_text` real de cada uma (via `scryfall-cache/oracle-cache.json`, nunca por memória). Confirmei primeiro que nenhuma carta do decklist está ausente do `CARD_DB` (69 únicas, 71 entradas incluindo comandante + Bear Token — sem fallback genérico escondido). Depois, gatilho por gatilho, achei 12 gaps reais 100% ausentes ou mecanicamente errados:

1. **The Great Henge** — sua PRÓPRIA habilidade de mana (`{T}: Add {G}{G}. You gain 2 life.`) nunca tinha sido implementada — só o gatilho de ETB (+1/+1 counter e compra) existia. A carta ficava em campo sem nunca produzir a mana que ela deveria.
2. **Defiler of Vigor** — só a metade de redução de custo existia. A metade que dá valor de verdade, *"Whenever you cast a green permanent spell, put a +1/+1 counter on each creature you control"*, estava 100% ausente.
3. **Eternal Witness** — ETB *"return target card from your graveyard to your hand"* 100% ausente (a carta só existia como corpo 2/1).
4. **Sakura-Tribe Elder** — erro mecânico, não só ausência: o código tratava ela como se tivesse ETB igual ao Cultivate, buscando a land E deixando o corpo 1/1 em campo pra sempre. O texto real é uma habilidade de **sacrifício** (*"Sacrifice this creature: Search your library for a basic land card..."*), não ETB — na Magic de verdade você escolhe entre manter o corpo OU sacrificar pela land, nunca os dois. Corrigido pra sacrificar de verdade no turno em que é conjurada (papel de rampa no decklist, tag `ramp`).
5. **Natural Order** — 100% ausente (sacrifica uma criatura verde, busca uma criatura verde da biblioteca direto pro campo). Implementado com gate em `can_cast()` (só é castável se existir uma criatura verde em campo pra sacrificar) e prioridade de busca pros finishers (Craterhoof Behemoth > Ghalta > Gigantic Big Bear).
6. **Lumra, Bellow of the Woods** — ETB *"mill four cards, then return all land cards from your graveyard to the battlefield tapped"* 100% ausente.
7. **Titania's Command** — "Choose two" dos 4 modos reais, 100% ausente. Modelado escolhendo sempre "buscar 2 terrenos" + "criar 2 Bears" (os 2 modos que não dependem de estado do oponente — o modo de exilar cemitério exigiria inventar o cemitério de um oponente).
8. **Archdruid's Charm** — a carta estava marcada com a tag `"removal"` e contando pro `removal_cast`, mas dos 3 modos reais ("Choose one"), 2 deles (contador+fight numa criatura do oponente; exilar artefato/encantamento do oponente) exigem um alvo que o oponente controla — proibido pela regra permanente de nunca inventar estado do oponente. Só o modo de tutor (criatura ou land) é legítimo nesse motor, então a carta NUNCA executa remoção de verdade aqui — a tag `"removal"` estava contando algo que nunca acontecia. Corrigido: tag trocada pra só `"tutor_modal"`, e o modo de tutor implementado de verdade (busca land se fontes verdes < 4, senão busca criatura verde pra mão).
9. **Springleaf Parade** — ETB (X tokens Shapeshifter changeling, X=1 pela mesma convenção de mv fixo já usada nesse arquivo pra outras cartas de custo `{X}`) E o estático (*"Creature tokens you control have '{T}: Add one mana of any color'"* — vale pra Bear Token também, não só pro próprio token dela) estavam 100% ausentes.
10. **Ohran Frostfang / Toski, Bearer of Secrets** — *"Whenever a creature you control deals combat damage to a player, draw a card"* 100% ausente porque não existia NENHUM modelo de combate/ataque genérico nesse arquivo (só o gatilho específico da Beorn). Construído um modelo mínimo: toda criatura apta a atacar (sem doença de invocação) é assumida atacando desimpedida a cada combate — mesma convenção já usada em outros decks da sessão pra esse tipo de gatilho, documentada como premissa (esse motor solo-goldfish não modela bloqueadores do oponente).
11. **Bug lateral encontrado ao construir o modelo de combate:** o próprio gatilho de ataque da Beorn (*"Whenever Beorn attacks..."*) disparava mesmo no turno em que ela era conjurada — ilegal (CR 302.6, doença de invocação também vale pra atacar, não só pra habilidades de `{T}`). Corrigido junto, gatilho agora gated por `can_attack()`.
12. **War Room / Nykthos, Shrine to Nyx** — as duas habilidades ativadas dos terrenos (War Room: `{3},{T}`, paga vida = cores na identidade do comandante, compra 1 — mono-verde = 1 vida; Nykthos: `{2},{T}`, adiciona mana = devoção à cor escolhida) estavam 100% ausentes, apesar dos terrenos já estarem em campo contando mana genérica. Implementadas com um limiar de rentabilidade pro Nykthos (só ativa com devoção ≥ 4, já que perde a mana base do terreno + paga {2} adicional).

**Deliberadamente NÃO implementado nesta rodada (documentado, não omitido):**
- **Bala Ged Recovery** (lado Sorcery, "return card from graveyard to hand") e a Aventura "Till and Tend" da **Beorn, Reluctant Host** (extra land drop) — o motor só modela UM modo de cast por carta; ambas já têm o modo real e completo do lado escolhido (land / criatura) totalmente implementado. Modelar os dois modos exigiria lógica de decisão dupla por carta MDFC/Aventura, desproporcional ao ganho pra 2 cartas — mantido como simplificação de escopo, não como gatilho ausente.
- **Chameleon Colossus** (pump `{1}{G}: +X/+X`) e **Ezuri's Predation** (exige criaturas do oponente) — exigem estado do oponente que esse motor não modela; consistente com a regra permanente de nunca inventar esse estado.
- **Scavenger Grounds** (sacrificar um Deserto pra exilar cemitérios) e **Boseiju, Who Endures** (Channel, alvo é permanente do oponente) — mesma razão, valor baixo/dependente de oponente.
- **Obscuring Haze** (`free_with_commander`) — o fog em si não tem alvo numérico nesse motor sem combate contra oponentes modelado; a isenção de custo condicional foi deixada de fora por ser baixo valor mesmo se implementada.

**Resultado (n=2000, seed_base=6000000, mesmos parâmetros da Correção #4, antes → depois):**

| Métrica | Antes (Correção #4) | Depois (Correção #5) |
|---|---|---|
| Avg spells cast | 11.53 | 12.15 |
| Avg extra draws (gatilhos) | 9.56 | **14.39** |
| Avg Bear count final | 6.41 | 6.58 |
| Beorn "draw 2" triggers (3+ Bears) | 3.16 | **2.73** |
| Beorn combat triggers | 4.25 | **3.50** |
| Avg finishers resolvidos | 0.23 | 0.37 |
| **% de jogos com finisher até T8** | **21.6%** | **32.9%** |
| Avg turno do 1º finisher relevante | 6.71 | 6.59 |
| Avg contadores +1/+1 totais no board | 8.60 | 10.88 |
| Avg cartas descartadas por limite de mão | 0.93 | **3.54** |
| Avg battlefield final | 17.59 | 19.19 |
| Avg mão final | 6.09 | 7.88 |

Os dois números que caem (gatilhos de combate/compra-2 da Beorn) são a correção do bug lateral (#11) — antes disparavam ilegalmente no turno do próprio cast da Beorn, agora só disparam quando ela pode atacar de verdade. Todo o resto sobe, e a taxa de finisher até T8 sobe de forma grande (21,6% → 32,9%) — a maior parte vem do Natural Order (cheat direto de Craterhoof/Ghalta pro campo, 14,5% dos jogos) e do Great Henge finalmente produzindo a própria mana (acelera tudo que vem depois). O salto de cartas descartadas por limite de mão (0,93 → 3,54) é consequência direta do motor de combate novo do Ohran Frostfang/Toski — com a premissa de "toda criatura apta ataca desimpedida", o total de compras extras quase dobrou (9,56 → 14,39), e a mão frequentemente estoura o limite de 7.

**Robustez:** sweep de 20.000 jogos (seeds 500000–519999, timeout de 2s/jogo) — 0 erros, 0 timeouts.

**Rodada oficial solicitada (n=5000, seed_base=91000 padrão do script):**

```
=== Beorn the Fierce — Goldfish Summary v1 (simulado por Claude) ===
Games: 5000 | Turns: 8 | Multiplayer (compra sempre no T1, CR 103.8a)

Avg mulligans: 0.43
Avg commander cast turn: 4.23
Commander cast by turn 4: 66.6%
Commander cast by turn 5: 88.5%

Avg spells cast: 12.13
Avg extra draws (gatilhos): 14.37
Avg Bear count final: 6.60
Avg Beorn 'draw 2' triggers (3+ Bears): 2.67
Avg Beorn combat triggers (converteu em Bear): 3.42
Avg ramp pieces em campo: 3.20
Avg remocao conjurada: 0.68
Avg finishers resolvidos: 0.37
Avg turno do 1o finisher relevante: 6.62
% de jogos com finisher ate T8: 31.8%
Avg cartas descartadas por limite de mao: 3.45
Avg battlefield final: 19.29

Managorger Hydra conjurada em 20.5% dos jogos
  Avg contadores +1/+1 finais: 7.90
  Removida por remocao (premissa de ~4 turnos vivos) em 39.9% dos jogos, turno medio: 6.62

Germination Practicum conjurada em 7.7% dos jogos
Avg contadores +1/+1 totais no board (soma de todas as fontes): 11.20

Natural Order conjurada em 14.8% dos jogos
Lumra: terrenos devolvidos do cemiterio em 4.9% dos jogos, media de 1.72 por jogo em que resolveu
Titania's Command conjurada em 16.4% dos jogos
Archdruid's Charm: modos escolhidos {'land': 92, 'creature': 919}
Eternal Witness devolveu carta do cemiterio em 13.3% dos jogos
Springleaf Parade conjurada em 20.0% dos jogos

Ohran Frostfang/Toski (dano de combate -> compra) ativo em 37.3% dos jogos, avg compras: 5.14
War Room ativada em 9.5% dos jogos, avg compras: 0.14
Nykthos (devocao >= 4) ativada em 11.0% dos jogos, avg ativacoes: 0.20

Genji Glove conjurada em 4.5% dos jogos, equipada em 50.2% dos jogos em que conjurada, turno medio 7.35
Avg mao final: 7.89 | Avg terrenos jogados: 6.48

Roaming Throne em campo em 14.0% dos jogos, avg gatilhos dobrados: 2.22
```

**Explicação individual de cada número (pedido explícito do usuário):**

- **Avg mulligans (0.43):** média de vezes que a mão inicial de 7 foi jogada de volta e comprada de novo (regra London, máx. 2 mulligans nesse modelo). Quanto mais baixo, melhor a consistência de mãos iniciais jogáveis.
- **Avg commander cast turn (4.23) / Commander cast by turn 4-5 (66.6%/88.5%):** em que turno médio a Beorn sai da zona de comando, e em quantos % dos jogos ela já está em campo até o turno 4 ou 5. É a métrica mais importante de "o deck liga a tempo".
- **Avg spells cast (12.13):** total de spells conjuradas em 8 turnos (inclui a própria Beorn, ramp, removal, etc.) — mede o quanto o motor de mana permite desenvolver o board.
- **Avg extra draws (14.37):** cartas compradas ALÉM da compra normal de turno — soma de TODOS os motores de compra do deck (Beast Whisperer, Garruk's Uprising, Tribute to the World Tree, Great Henge, Selvala, Chronicle of Victory, clues da Tireless Tracker, Return of the Wildspeaker/Shamanic Revelation, Last March of the Ents, War Room, e agora também Ohran Frostfang/Toski). É o número que mais mudou nesta rodada (9.56→14.39 no comparativo pareado) por causa do motor de dano de combate novo.
- **Avg Bear count final (6.60):** quantos Ursos (de qualquer origem — criatura real, token, changeling) estão em campo/já contados ao fim do turno 8. Alimenta diretamente o gatilho "3+ Ursos" da própria Beorn.
- **Avg Beorn 'draw 2' triggers (2.67):** quantas vezes por partida o gatilho "se 3+ Ursos sob seu controle, compre 2" disparou de verdade no combate.
- **Avg Beorn combat triggers (3.42):** quantas vezes por partida o gatilho de ataque da Beorn converteu outra criatura em Urso (agora corretamente só quando ela pode atacar).
- **Avg ramp pieces em campo (3.20):** quantidade de peças com a tag `ramp` (dorks, rocks, fetches de land) que chegaram a ser conjuradas.
- **Avg remocao conjurada (0.68):** spells de remoção de verdade conjurados (Beast Within, Song of the Dryads, Ezuri's Predation, Haywire Mite — não inclui mais Archdruid's Charm, que nunca remove nada de verdade nesse motor, ver gap #8).
- **Avg finishers resolvidos (0.37) / % com finisher até T8 (31.8%):** quantos "fechadores de jogo" (Craterhoof, Ghalta, Unnatural Growth, Genji Glove equipada, e agora também qualquer finisher trazido pelo Natural Order) foram resolvidos, e em quantos % dos 5000 jogos isso aconteceu até o turno 8. É a métrica-resumo mais importante pra saber se o deck "fecha o jogo" a tempo.
- **Avg turno do 1º finisher relevante (6.62):** em que turno médio, nos jogos em que aconteceu, o primeiro finisher resolveu.
- **Avg contadores +1/+1 no board (11.20):** soma agregada de TODOS os contadores +1/+1 distribuídos por qualquer fonte (Ayula, Tribute to the World Tree, Great Henge, Necklace of Girion, Dancing from Dark to Dawn, Little Bear, Forgotten Ancient, Germination Practicum, Beorn's Hospitality, Defiler of Vigor) — não é por criatura individual, é o total da mesa.
- **Avg cartas descartadas por limite de mão (3.45):** quantas cartas foram descartadas ao fim do turno por estourar o limite de 7 (a menos que Reliquary Tower/Thought Vessel estejam em campo). Alto porque o motor de compra ficou muito mais forte nesta rodada.
- **Avg battlefield final (19.29):** total de permanentes (terrenos + criaturas + outros) em campo ao fim do turno 8.
- **Managorger Hydra (20.5% conjurada, 7.90 contadores finais em média):** com que frequência ela é comprada/conjurada em 99 cartas, e quantos contadores +1/+1 acumula (seus spells reais + premissa de 2 spells/turno de oponentes) até morrer pra remoção assumida (~4 turnos de vida útil).
- **Germination Practicum (7.7% conjurada):** frequência de cast; o Paradigm dela (recast de graça a cada turno) já está incluído no total de contadores acima.
- **Natural Order (14.8% conjurada):** em quantos % dos 5000 jogos a carta foi conjurada — precisa de mana + uma criatura verde em campo pra sacrificar, então não é sempre castável mesmo quando comprada. As criaturas buscadas mostram a prioridade real (Craterhoof na esmagadora maioria, ver rodada de 5k acima).
- **Lumra (4.9% dos jogos, 1.72 terrenos devolvidos em média):** com que frequência a ETB dela chegou a devolver pelo menos 1 terreno do cemitério ao mil 4 (nem sempre encontra um terreno entre as 4 cartas milhadas).
- **Titania's Command (16.4% conjurada):** frequência de cast, sempre nos modos "buscar 2 terrenos + criar 2 Bears".
- **Archdruid's Charm (modos {'land': 92, 'creature': 919} em 5000 jogos):** de quantas vezes ela foi conjurada, quantas escolheram cada modo — a maioria escolhe buscar criatura (já tem 4+ fontes verdes na maioria dos casos em que é castável).
- **Eternal Witness (13.3% dos jogos devolveu carta):** com que frequência a ETB dela teve pelo menos uma carta no cemitério pra reaver.
- **Springleaf Parade (20.0% conjurada):** frequência de cast; sempre cria exatamente 1 token (X=1, premissa de custo mínimo já documentada no código).
- **Ohran Frostfang/Toski — dano de combate (37.3% dos jogos ativo, avg 5.14 compras):** em quantos % dos jogos pelo menos uma das duas está em campo gerando compra por dano de combate, e a média de cartas compradas por ESSA fonte especificamente (incluída também no "extra draws" geral acima). Número alto porque a premissa é "toda criatura apta ataca desimpedida" — sem bloqueadores de oponente modelados.
- **War Room (9.5% dos jogos ativada, avg 0.14 compras):** baixo porque compete por mana com o resto da mão praticamente todo turno (custa {3}+{T}, e essa mana quase sempre tem uso melhor).
- **Nykthos (11.0% dos jogos ativada, avg 0.20 ativações):** só ativa quando compensa (devoção ≥ 4), por isso a frequência baixa — na maior parte dos jogos o board não tem permanentes verdes suficientes pra valer a pena trocar a mana base do terreno por essa ativação.
- **Genji Glove (4.5% conjurada, 50.2% equipada quando conjurada, turno médio 7.35):** frequência de cast e, dado que foi conjurada, em quantos % o Equip {3} separado também foi pago a tempo dentro dos 8 turnos.
- **Roaming Throne (14.0% em campo, 2.22 gatilhos dobrados em média):** frequência em campo e quantas vezes por partida ela duplicou o gatilho de combate/compra da própria Beorn (tipo escolhido: Bear).

---

### Correção #6 — recursão vira 5ª métrica básica obrigatória (regra reforçada)

**Gatilho (usuário):** *"Vc precisa acrescentar a variável recursão e
interação à lista de variáveis para avaliar, medir e registrar em todos os
decks tb!"* — Beorn foi concluído (Correção #5) antes da regra das 5
métricas básicas obrigatórias (ramp/draw/interaction/recursion/finisher-
lethality) existir, então nunca teve o bloco resumido — só métricas
espalhadas pelo relatório.

**Adicionado:** bloco `--- Métricas básicas (checklist obrigatória) ---` no
final do `run_batch()`, agregando as 5 categorias a partir de métricas já
existentes (RAMP = `ramp_pieces_in_play`, DRAW = `extra_draws`, INTERACTION
= `removal_cast`, FINISHER/LETHALITY = `finishers_resolved`/turno médio) e
um novo agregado RECURSION = Eternal Witness (retorno pra mão) + Lumra
(terrenos do cemitério pro campo).

**Resultado:** puramente aditivo — confirmado com n=2000, seed_base=6000000:
`extra_draws`/`removal_cast`/finisher-até-T8 idênticos aos já reportados na
Correção #5 (14,39 / 0,69 / 32,9%). RECURSION novo: avg 0,21/partida
(n=200 de teste).

`lista.md` não mudou.

---

### Correção #7 — Bala Ged Recovery: MDFC verdadeiro, lado Sorcery nunca conjurado

**Gatilho (usuário):** depois do achado de Ojer Taq/Legion's Landing no
Edgar Markov (jogadas ilegalmente como land, layout "transform"), o usuário
pediu pra conferir todas as cartas modais/multi-face dos decks trabalhados
e registrar a regra de verificar o `layout` real (Scryfall) antes de
assumir qual face é jogável.

**Conferido:** Beorn tem 2 cartas multi-face — `Beorn, Reluctant Host //
Till and Tend` (layout `adventure`, confirmado) e `Bala Ged Recovery //
Bala Ged Sanctuary` (layout `modal_dfc`, confirmado). Ao contrário do Edgar
Markov, nenhuma das duas era um caso de ação ilegal: Adventure sempre
permite conjurar a criatura direto da mão (o modo "Till and Tend" primeiro
é só uma opção mais barata, não obrigatória), e MDFC verdadeiro permite
escolher livremente qual face jogar. Jogar Bala Ged Recovery sempre como o
lado Land (Sanctuary) é uma escolha **legítima**, não uma lacuna de regras.

**Mas era uma lacuna de valor real:** a frente (`{2}{G}`, *"Return target
card from your graveyard to your hand"*) nunca era sequer considerada — um
efeito de recursão real ficava permanentemente desligado. Implementado
(`try_bala_ged_recovery`, chamada antes do land-drop): só abre mão do land
se o cemitério tiver uma carta de MV≥3 pra recuperar (senão o land continua
sendo melhor).

**Resultado (n=2000, seed_base=6000000, antes → depois):**

| Métrica | Antes | Depois |
|---|---|---|
| RECURSION | 0,21 (Eternal Witness + Lumra) | 0,31 |
| Avg terrenos jogados | 6,54 | 6,50 |
| % finisher até T8 | 32,9% | 32,4% |

Trade-off pequeno e esperado — às vezes vale mais recuperar uma carta boa
do cemitério do que jogar mais um terreno, e isso custa uma fração de
consistência de mana/finisher.

**`Beorn, Reluctant Host // Till and Tend`:** mantido como está (sempre
conjurada como a criatura 5-mana direto) — decisão de escopo legítima já
documentada anteriormente, não uma ação ilegal (Adventure não obriga o modo
barato primeiro).

**Robustez:** sweep de 20.000 jogos (seeds 3000000–3019999, timeout
2s/jogo) — 0 erros, 0 timeouts.

`lista.md` não mudou.

---

### Correção #8 — verificação de planeswalkers (regra nova pós-Prismatic Bridge)

**Gatilho (usuário):** depois do Prismatic Bridge revelar que nenhum
simulador do repositório modelava lealdade/ativações de planeswalker, o
usuário registrou a regra permanente (categoria 12,
`goldfish-sim-card-rules.md`) — *"Adicione essa regra para tudo, sempre
também!"*

**Conferido:** `grep -in "Planeswalker" beorn_goldfish_v1.py` não encontra
nenhuma ocorrência. Beorn não tem nenhum planeswalker na lista — categoria
12 é **N/A por decklist**. Nenhuma mudança de código necessária.

---

### Rodada oficial final pós-checklist de mecânica — 2026-08-29

**Contexto:** fechamento da auditoria de mecânica (Correções #1-#8 acima:
gatilhos ausentes, doença de invocação, Bala Ged Recovery, planeswalkers).
Nenhuma delas tinha sido consolidada num batch oficial único com TODAS as
correções juntas — rodado agora pra ter o número de referência atual do
deck.

**n=5000, seed_base=91000 (padrão do script, mesma convenção da "Rodada
oficial solicitada" anterior):**

```
Avg mulligans: 0,43
Avg commander cast turn: 4,25 | por T4: 66,0% | por T5: 88,2%
Avg spells cast: 12,11 | Avg extra draws: 14,18
Avg Bear count final: 6,56 | Avg battlefield final: 19,20
Avg ramp em campo: 3,21 | Avg remoção conjurada: 0,69
Avg finishers resolvidos: 0,36 | 31,1% dos jogos com finisher até T8

--- Métricas básicas (checklist obrigatória) ---
RAMP: 3,21 | DRAW: 14,18 | INTERACTION: 0,69 | RECURSION: 0,31
FINISHER/LETHALITY: 0,36 resolvidos, 31,1% até T8, turno médio 6,62
```

**Leitura:** números estáveis frente à última rodada comparável
(Correção #7, n=2000/seed_base=6000000: commander T4,23, finisher 32,9%→
32,4%) — a soma de todas as correções de mecânica não moveu o
comportamento agregado do deck de forma relevante, só corrigiu a
contabilidade interna (gatilhos que antes eram fantasmas agora são reais).
Fica como o número de referência oficial atual, sem mudança em `lista.md`.

**Robustez:** herdada dos sweeps de 20.000 jogos já rodados em cada
correção anterior (0 erros, 0 timeouts) — nenhuma mudança de código nesta
rodada, só reconsolidação de métricas.

---

### Leva de 200 jogos — análise de melhoria (goldfish instrumentado, n=200, seed_base=8800000) — 2026-08-29

**Contexto:** pedido do usuário — rodar uma leva de 200 jogos (amostra
intermediária, maior que uma partida anedótica mas menor que o batch
oficial de 5000) e minerar os dados pra achar pontos reais de melhoria,
não só confirmar as médias já conhecidas.

**Números (dentro do ruído esperado frente ao batch oficial de 5000):**

```
Avg commander cast turn: 4,22 | por T4/T5: 68,0%/85,0%
Avg battlefield final: 19,32 | Avg Bear count final: 6,45
Avg finishers resolvidos: 0,28 | 25,5% dos jogos com finisher até T8
RAMP 3,35 | DRAW 14,61 | INTERACTION 0,65 | RECURSION 0,32
```

**Diagnóstico (minerado direto do `.jsonl`, não só do agregado impresso):**

- **Comandante quase nunca é o gargalo:** só 3,5% dos jogos nunca conjuram
  Beorn (96,5% de sucesso) — mono-verde não tem problema de fixação de mana,
  como esperado.
- **A engine de Urso funciona:** só 8,0% dos jogos terminam com menos de 3
  Ursos em campo (a condição mínima do próprio gatilho "compre 2" da Beorn)
  — o motor tribal entrega o que promete.
- **O gargalo real é fechar o jogo:** **74,5% dos jogos terminam SEM
  nenhum finisher resolvido** (Craterhoof, Ghalta, Unnatural Growth, Genji
  Glove equipada, ou o que o Natural Order buscar) até o turno 8, mesmo com
  board médio de 19,3 permanentes. Não é falta de mana nem de corpo em
  campo — é falta de UMA carta específica entre um punhado pequeno de
  finishers reais na mão.
- **Natural Order é o único tutor de finisher da lista, e raramente é
  conjurado:** só 10,0% dos 200 jogos (vs. 14,5-14,8% no agregado maior —
  dentro do ruído, mas consistentemente baixo). Ele resolve o problema
  quando chega à mão, mas nada na lista ajuda a ENCONTRAR o próprio Natural
  Order (ou os finishers diretamente) — o deck depende de topdeck puro pra
  esse pedaço do plano.

**O que podemos melhorar (recomendação, não aplicada — decisão do
usuário):** adicionar 1-2 tutores de criatura baratos e reais (ex.:
Eladamri's Call, Worldly Tutor, Chord of Calling — este último se
beneficia diretamente do board largo de Ursos via convoke) pra buscar
Craterhoof/Ghalta direto na mão sem depender só do Natural Order. Isso
ataca o gargalo medido (74,5% sem finisher) na raiz — mais consistência de
achar o fechador, não mais um fechador novo (a lista já tem finishers bons
o bastante, só faltam com pouca frequência real na mão dentro de 8
turnos).

**Robustez:** herdada dos sweeps de 20.000 já rodados nesta sessão — nenhum
código mudou nesta rodada, só mineração de dados de uma amostra nova.

---

### Auditoria completa de oráculo — TODAS as 70 cartas (comandante + 69), Scryfall em lote — 2026-08-30

**Gatilho (usuário):** *"Eu já cansei de pedir para vc compilar TODAS as
habilidades de TODAS as cartas, qual a dificuldade?"* — mesma auditoria
sistemática aplicada ao Thranduil, agora no Beorn. `POST
https://api.scryfall.com/cards/collection` (69 cartas + 1 fetch avulso pro
MDFC Bala Ged Recovery), oráculo completo comparado linha a linha contra
`CARD_DB` e a lógica do simulador.

**6 achados reais, todos corrigidos:**

1. **BUG GRAVE — o próprio anthem da Beorn nunca foi lido em lugar
   nenhum do código.** "Other Bears you control get +2/+2" estava
   registrado só como uma nota decorativa (`notes={"anthem_bear": True}`)
   no cadastro do comandante — nunca consultada. Isso importa de verdade:
   vários gatilhos do deck checam `power >= X` (Garruk's Uprising draw em
   power≥4, Tribute to the World Tree draw vs. contador em power≥3), e um
   Bear Token base 2/2 vira 4/4 com o anthem em campo — cruzava limiares
   de poder que ficavam fora de alcance no cálculo antigo. Corrigido em
   `on_creature_enters()`.
2. **Chameleon Colossus — ativação inteira faltando.** Só changeling e
   proteção contra preto estavam modeladas; "{2}{G}{G}: This creature gets
   +X/+X until end of turn, where X is its power" nunca foi implementada.
   Implementado como ativação repetível (`try_chameleon_colossus_pump`).
3. **Beorn's Hospitality — metade animate faltando.** Só o landfall (+1/+1
   counter) estava modelado; "{5}{G}{G}: This enchantment becomes a Bear
   creature... power/toughness equal to lands you control (doesn't end)"
   nunca foi implementado — um corpo real que escala com terrenos, ficava
   invisível. Implementado como ativação única (`try_beorns_hospitality_animate`).
4. **Nenhum terreno tinha mecanismo de "enters tapped" modelado (Regra
   12).** Achado: Bala Ged Sanctuary (lado terreno do MDFC Bala Ged
   Recovery) tem "This land enters tapped" incondicional no oráculo,
   nunca rastreado — mono-verde com 31 Forests torna o impacto pequeno,
   mas real. Implementado `tapped_lands_this_turn` (mesmo mecanismo já
   usado no Thranduil/Ur-Dragon).
5. **Boseiju, Who Endures (Channel) e Firdoch Core (virar criatura 4/4)**
   — auditados e confirmados como decisão de escopo correta (opponent-
   dependent e sem combate individual modelado, respectivamente), mas
   **sem nenhuma nota explicando isso no código** — agora documentados
   (Regra 13: nunca ausência silenciosa).

**Robustez:** 20.000 seeds (91000–111000), timeout padrão — 0 erros.

**Batch oficial, n=5000, seed_base=91000 (antes de toda esta auditoria →
depois):**

| Métrica | Antes | Depois |
|---|---|---|
| Avg finishers resolvidos | 0,36 | **0,44** (+22%) |
| % jogos com finisher até T8 | 31,1% | **36,0%** |
| DRAW (extra draws) | 14,18 | 14,86 |
| Avg battlefield final | 19,20 | 19,39 |
| Chameleon Colossus ativado | — | 4,8% dos jogos |
| Beorn's Hospitality animada | — | 4,0% dos jogos |

**Leitura:** o anthem faltando era o achado mais grave — afetava
diretamente os gatilhos de "power >= X" que várias cartas do deck
dependem, então o ganho em DRAW/finisher reflete o próprio motor de
carta do deck ficando mais preciso, não uma carta nova. `lista.md` não
muda — 100% correção de simulador.

**Pendência explícita pro usuário:** Ur-Dragon ainda falta a mesma
varredura completa — próximo da fila.

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
