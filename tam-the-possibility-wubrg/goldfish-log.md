# Tam, the Possibility (WUBRG) — goldfish log

> **Decisão 2026-10-21: as cores dos terrenos dos oponentes são ALEATÓRIAS** (pedido do usuário; convenção já era essa, nenhuma linha de base muda; uma mão que depende da Orchard/Fellwar para uma cor específica a tem em 40,9% das partidas no T2 e 58,5% no T3): [`resultados-ab/2026-10-21-cores-terrenos-oponentes/`](resultados-ab/2026-10-21-cores-terrenos-oponentes/LEIAME.md).

> **Atualização 2026-10-21 (§6): goldfish manual #2 do usuário + Saheeli −2 como cópia de artefato de mana** (o usuário jogou no T6 o Servo copiando o Fellwar Stone para pagar o Teferi; o simulador só copiava P/T de criatura; implementado e validado: bit-idêntico com a chave desligada em 20.000 × 2 modos, a cópia dispara em 2,9% / 2,0% das partidas e a linha de base muda ≤ 0,1 ponto): [`resultados-ab/2026-10-20-goldfish-manual-2/`](resultados-ab/2026-10-20-goldfish-manual-2/LEIAME.md) e [`resultados-ab/2026-10-21-saheeli-copia-de-artefato/`](resultados-ab/2026-10-21-saheeli-copia-de-artefato/LEIAME.md). **Goldfish manual #4** (2026-10-21; Nissa, Teferi TA, Ajani, Garruk e Gauntlet; nenhuma regra mudou; erros de regra do relato: Teferi `+1` ×3 e `−1` ×2, Ajani `−2` com 7 compras (a regra dá 8); a Elspeth foi anulada pela Vex): [`resultados-ab/2026-10-21-goldfish-manual-4/`](resultados-ab/2026-10-21-goldfish-manual-4/LEIAME.md). **Goldfish manual #3** (2026-10-21; nenhuma regra mudou; a diferença para o simulador é a convenção de cor da Exotic Orchard: com os terrenos de oponente produzindo as 5 cores a partir do T2 o simulador reproduz a mediana do usuário, 1 / 3 / 4 planeswalkers em T5 / T6 / T7): [`resultados-ab/2026-10-21-goldfish-manual-3/`](resultados-ab/2026-10-21-goldfish-manual-3/LEIAME.md).

> **Atualização 2026-10-22 (§1 NOVO, §9, §10): o simulador mudou depois de 5 goldfish do usuário e a linha de base do modo padrão foi refeita.** Tam atacando (+3,7 pontos de mesa limpa até T10 no padrão, ~0 na resiliência), piscar de mana virado, Saheeli copiando criatura de mana / Staff, turnos extras empilhados, ordem de pagamento do mana "vivid", combo Orrery+Tezzeret+Chain Veil fechando com o pagamento na mão, e o perfil `playtester` da resiliência (calibrado nas taxas dos 5 logs). **O §1 antigo (2026-10-19) deixou de valer no modo padrão** e foi mantido como §1b. Pastas: [`resultados-ab/2026-10-22-politicas-tam/`](resultados-ab/2026-10-22-politicas-tam/LEIAME.md) (rodada 1), [`resultados-ab/2026-10-22-rodada2-motor-e-perfil/`](resultados-ab/2026-10-22-rodada2-motor-e-perfil/LEIAME.md) (rodada 2 e linha de base nova), [`resultados-ab/2026-10-22-calibracao-playtester/`](resultados-ab/2026-10-22-calibracao-playtester/LEIAME.md) (perfil) e [`resultados-ab/2026-10-21-goldfish-manual-5/`](resultados-ab/2026-10-21-goldfish-manual-5/LEIAME.md) (goldfish #5).

> **Arquivo dos dados (Regra #8):** [`resultados-ab/2026-10-19-simulador-baseline/`](resultados-ab/2026-10-19-simulador-baseline/LEIAME.md) (brutos `.json.xz`, regressão, conservação, bit-identidade, determinismo, como reproduzir cada tabela) e [`resultados-ab/2026-10-19-goldfish-manual-1/`](resultados-ab/2026-10-19-goldfish-manual-1/LEIAME.md) (o goldfish manual do usuário, compilado). Auditoria de oráculo: [`checklist-oraculo.md`](checklist-oraculo.md). Simulador: `tam_goldfish_v1.py`; testes: `python3 testes/rodar_testes.py` (146).

## 1. Linha de base ATUAL (2026-10-22): a `lista.md` COMO ESTÁ, nenhuma troca aplicada, simulador da rodada 2

Mesmo pedido e mesma configuração do §1b (12 turnos, mesa de 4, 3 oponentes de 40 de vida, N = 10.000 por modo, sementes 3.000.000+i, compra no T1; IC95%), mas com o simulador de hoje (`tam_goldfish_v1.py` == `resultados-ab/2026-10-22-rodada2-motor-e-perfil/codigo/tam_goldfish_v1_DEPOIS_rodada2.py`). Tabelas só dos brutos: `resumos/resumo_descritivo_depois_10000.txt` e `resumo_descritivo_perfil_playtester_10000.txt` da pasta da rodada 2. A coluna nova é a **resiliência com o perfil `playtester`**: o oponente do Archidekt que o usuário enfrenta nos goldfish (1 criatura de vez em quando, ~0,28 magia por turno dele, efeito em massa em 4 variantes, anulação que deixa comprar); **não é a mesa de 3 humanos dele**.

| métrica | modo padrão (oponente passivo, todo atacante conecta) | resiliência de sempre (arquétipos do Prismatic Bridge) | resiliência com perfil `playtester` |
|---|---|---|---|
| mesa limpa até T8 / T9 / T10 / T12 | 15,4% ± 0,7 / 43,1% / **68,7% ± 0,9** / 90,3% ± 0,6 | 0,4% / 1,8% / **5,0% ± 0,4** / 17,8% ± 0,7 | 5,8% ± 0,5 / 19,4% / **40,2% ± 1,0** / 73,8% ± 0,9 |
| turno da mesa limpa (entre as que limparam) | mediana **T10** (Q1–Q3: T9–T10) | mediana T11 (T10–T12) | mediana T10 (T9–T11) |
| 1º oponente fora até T6 / T8 | 4,5% / 64,5% | 0,2% / 6,8% | 1,7% / 34,2% |
| Tam conjurada até T3 / T4 / T6 | 81,0% / 95,5% / 98,8% | 81,0% / 95,2% / 98,5% | 81,0% / 95,4% / 98,8% |
| 1º planeswalker (de carta) até T3 / T4 | 7,4% / 56,8% | 6,6% / 45,8% | 7,2% / 52,9% |
| planeswalkers em campo (média) no fim de T4 / T6 / T8 / T10 | 0,94 / 3,15 / 5,39 / 6,45 | 0,72 / 1,64 / 2,24 / 2,81 | 0,86 / 2,55 / 4,13 / 5,38 |
| mana disponível no início de T4 / T6 / T8 (média) | 3,99 / 7,14 / 11,43 | 3,91 / 6,22 / 8,18 | 3,96 / 6,78 / 10,14 |
| entradas de planeswalker de carta por partida / planeswalkers que morrem | 9,9 / 1,2 | 6,6 / 2,8 | 9,9 / 1,7 |
| ultimates usadas por partida; 1ª ultimate até T8 | 5,0; 71,8% | 1,9; 16,6% | 4,8; 55,9% |
| ativações da Tam por partida; 1ª ativação até T6 / T8 | **1,09**; 4,4% / 29,3% | 0,58; 1,3% / 8,2% | 1,10; 3,3% / 22,1% |
| proliferates por partida (total / Gauntlet `0` / Tam / Flux Channeler / Vraska) | 19,4 / 8,4 / 6,1 / 2,7 / 1,2 | 7,0 / 1,9 / 2,4 / 1,0 / 0,7 | 17,4 / 7,0 / 5,7 / 2,5 / 1,2 |
| combo Orrery + Tezzeret + Chain Veil: montado / **fecha** (agora com o pagamento na mão) | 2,9% / 1,0% | 1,0% / 0,2% | 2,9% / 0,8% |
| eu cheguei a vida ≤ 0 até T12 (a partida continua, convenção do repositório) | — | **12,9%** (até T8: 4,1%) | 0,0% |
| remoções / wipes / anulações / descartes do oponente por partida | — | 2,2 / 1,2 / 2,3 / 1,9 | 0,9 / 0,5 / 0,9 / 0,8 |
| deck-out (comprar com a biblioteca vazia) | 0,9% | 0,4% | 1,3% |

**O que mudou em relação ao §1b (todo o resto do §1b sobre política continua valendo, salvo o que está dito aqui):**
- **Modo padrão: +3,5 pontos de mesa limpa até T10 (64,7% → 68,7%)**, quase tudo da **Tam atacando** (rodada 1: ela ataca em 99,7% das partidas, ~5 ataques por partida, e a Tamiyo compra +0,11 carta por partida; custo: 0,09 ativação a menos da Tam). A 2ª rodada (turnos extras, pagamento, combo da mão) soma décimos de ponto, dentro do ruído, exceto os turnos extras jogados (0,434 → 0,482 por partida).
- **Resiliência de sempre: praticamente igual** (mesa limpa até T10 4,8% → 5,0%): com criatura de oponente em campo a Tam fica em casa de bloqueadora.
- **A política (c) do §1b mudou:** o combo Orrery + Tezzeret + Chain Veil **conjura o pagamento da mão** (All Will Be One, Sanctum Lurker) e fecha; fechava em 0,82% e agora em 0,98% (padrão); a (b) também mudou na parte de ataque: a Tam deixa de ficar parada quando não ativa.
- **Perfil `playtester`:** a mesa do playtester é **muito mais quieta** do que a resiliência de sempre (24 cartas de oponente em 31 turnos do usuário contra ~9 interações + ~8,5 criaturas por partida na de sempre), e por isso a mesa limpa até T10 vai de 5,0% para 40,2%. O modo de sempre continua sendo a referência para uma mesa hostil; o `playtester` é a referência para "o que o bot do Archidekt faz".

**Limites (Regra #7):** (1) nenhuma das três colunas é a taxa de vitória; (2) o perfil foi **ajustado** nas taxas dos mesmos 5 logs em que é comparado (a tabela de replay do #3, #4 e #5 não é validação independente); (3) o IC95% da taxa de eventos de oponente dos logs é largo (0,50–1,15 por turno); (4) uma só família de sementes por lote.

## 1b. Linha de base de 2026-10-19 (**SUPERADA no modo padrão**; mantida como registro)

> O simulador do §1b é o commit `e265cb5`. No modo padrão a Tam não atacava; hoje ataca (§1). A coluna de resiliência continua válida como referência da resiliência de sempre (4,8% → 5,0% hoje). Os números abaixo não foram refeitos.

### (tabela de 2026-10-19)


Pedido: *"crie o simulador do deck e primeiro rode as simulações para ver como o deck assim roda!"*. 12 turnos, mesa de 4 (3 oponentes, 40 de vida), N = 10.000 por modo (sementes 3.000.000+i; o lote de 2.000 com sementes 1.000.000+i está em `resumos/`). Intervalos = IC95%. **Compra no T1** (Commander multijogador, confirmado pelo usuário).

| métrica | modo padrão (oponente passivo, todo atacante conecta) | modo de resiliência (remoção, wipe, descarte, anulação, ataque a planeswalker) |
|---|---|---|
| mesa limpa até T8 / T9 / T10 / T12 | 13,1% ± 0,7 / 38,7% / **64,7% ± 0,9** / 89,1% ± 0,6 | 0,4% / 1,7% / **4,8% ± 0,4** / 17,0% ± 0,7 |
| turno da mesa limpa (entre as que limparam) | mediana **T10** (Q1–Q3: T9–T11) | mediana T11 (T10–T12) |
| 1º oponente fora até T6 / T8 | 2,4% / 54,3% | 0,2% / 6,5% |
| Tam conjurada até T3 / T4 / T6 | 81,0% / 95,5% / 98,8% | 81,0% / 95,2% / 98,5% |
| 1º planeswalker (de carta) até T3 / T4 | 7,0% / 56,6% | 6,2% / 45,6% |
| planeswalkers em campo (média) no fim de T4 / T6 / T8 / T10 | 0,93 / 3,13 / 5,41 / 6,58 | 0,71 / 1,63 / 2,23 / 2,79 |
| mana disponível no início de T4 / T6 / T8 (média) | 3,99 / 7,11 / 11,37 | 3,91 / 6,22 / 8,18 |
| entradas de planeswalker de carta por partida (inclui reentrada por blink) / planeswalkers que morrem | 10,1 / 1,2 | 6,5 / 2,8 |
| ultimates usadas por partida; 1ª ultimate até T8 | 5,3; 71,3% | 1,8; 16,4% |
| ativações da Tam por partida; 1ª ativação até T6 / T8 | **1,18**; 4,7% / 30,4% | 0,57; 1,2% / 7,8% |
| proliferates por partida (total / Gauntlet `0` / Tam / Flux Channeler / Vraska) | 20,6 / 9,1 / 6,5 / 2,7 / 1,3 | 6,9 / 1,9 / 2,3 / 1,0 / 0,7 |
| combo Orrery + Tezzeret + Chain Veil: montado / fecha com pagamento em campo | 3,1% / 0,9% | 1,1% / 0,2% |
| eu cheguei a vida ≤ 0 até T12 (a partida continua, convenção do repositório) | — (sem dano ao jogador) | **12,9%** (até T8: 4,2%) |
| remoções / wipes / anulações de magia / descartes do oponente por partida | — | 2,2 / 1,2 / 2,3 / 1,9 |
| deck-out (comprar com a biblioteca vazia) | 1,1% | 0,4% |

**Como ler (limites, Regra #7):**
- O modo padrão é o teto (oponente sem tabuleiro, nenhum planeswalker é atacado); a resiliência é a referência mais próxima de uma mesa real, e ali o deck limpa a mesa até T12 em 17%, não em 89%. A distância entre os dois é o que as 4 mesas reais vão decidir; **nenhum dos dois é a "taxa de vitória"** do deck (não há combate de oponente real, nem política de alvo humana).
- A resiliência é a mesma do Prismatic Bridge, não calibrada pro Tam: o Tam tem poucas criaturas, então os ataques do oponente caem nos planeswalkers e em mim (2,8 planeswalkers mortos por partida). A calibração com a mesa real do usuário está pendente.
- **Política do jogador (premissas do simulador, não regras):** (a) toda ultimate é usada assim que paga, e o planeswalker morre se a ultimate custa a lealdade toda (a Vronos `-7` com 7 morre; o usuário esperou a Vronos chegar a 12 no goldfish dele); (b) a Tam só ativa com mana WUBRG sobrando depois de conjurar tudo e ativar os planeswalkers, e só com X ≥ 2, ≥ 2 permanentes com contador e X × alvos ≥ 6: por isso 1,18 ativações por partida; (c) o combo Orrery + Tezzeret + Chain Veil só encerra a partida com **pagamento em campo** (All Will Be One ou Sanctum Lurker); montado sem pagamento fica registrado, e o simulador não simula o laço infinito (teto de 80 ativações e 60 magias por turno, que apertou em 0,39% das partidas do modo padrão e 0,07% da resiliência); como o jogador real teria vitória em quase todo combo montado (ex.: lealdade infinita → Vraska `-9` e proliferate), os 3,1% "montado" são piso.
- Metas por oponente: no modo padrão as habilidades que miram o tabuleiro dele (Teferi `-3`, Vraska `-2`, Dellian `-3`...) valem como métrica proxy `interaction_plays` (existe alvo com 70% de chance a partir do T3).

## 2. O que a construção do simulador achou (nenhum desses é número de baseline: foram corrigidos antes)

Detalhe e testes em [`checklist-oraculo.md`](checklist-oraculo.md). Os que mais mexeriam no resultado: (1) **mana fantasma**: com o Chromatic Orrery em campo o mana flutuante `{C}` nunca era descontado do pool (o contador `A` ia a −119), e a Wrenn era reconjurada do cemitério em laço infinito; achado por partidas que não terminavam, corrigido e travado por exceção se o pool ficar negativo; (2) o mana flutuante só esvaziava no upkeep, não no fim de cada fase (CR 500.4); (3) o turno do oponente rodava o ataque ANTES da rolagem do gate de atenção (ordem de fases, Regra #6): só essa correção levou as derrotas minhas de 49% para 16% em 300 partidas de teste (12,9% no código final); (4) Kasmina `-8` deixava a magia no exílio E no cemitério (a invariante "carta acima do baralho" disparava em 25% das partidas do modo padrão e 10% da resiliência); (5) a regra da compra no T1; (6) 8 correções vindas das rulings (Liliana's Talent, Tamiyo em criatura de oponente, Oko, Saheeli, Peacemaker, Vronos, Tezzeret, Aminatou).

## 3. Validação do código final

Regressão **20.000 × 2 modos: 0 exceções, 0 carta acima do baralho, 0 campo negativo**; conservação de cartas (cada carta aparece exatamente o que a lista tem em mão + biblioteca + cemitério + exílio + campo) **20.000 × 2: 0 a mais, 0 a menos**; determinismo e bit-identidade: ver `resultados-ab/2026-10-19-simulador-baseline/LEIAME.md`; 146 testes dirigidos (terrenos, mana, custos, 25 planeswalkers, 8 Ways, permanentes, motor, rulings, as 9 jogadas do goldfish manual).

## 4. O goldfish manual do usuário vs. o simulador (mesmas cartas, ordem do log)

Resumo (detalhe em `resultados-ab/2026-10-19-goldfish-manual-1/LEIAME.md`): as 9 jogadas do relato (Pyromancer `+1` na ficha de Jace, Jace `-12` com turno extra, Gauntlet `0` 2× por planeswalker com o Oath, Tezzeret `-X` buscando Sol Ring e Arcane Signet, Oath exilando o Tezzeret, Vronos `-7` no Arcane Signet, Tam morta e recastada com imposto, Paradox + Jace `-3` para a 2ª terra) **reproduzem no simulador**. Com a mesma mão e as mesmas 10 compras, a IA do simulador põe a Tam no T3 (usuário: T4) e, no modo padrão, 4 planeswalkers no T10 (usuário: 3); na resiliência, 1. São 1 jogo humano contra 300 ordens do resto do baralho: não valida nem refuta o simulador.

## 5. Pendências e perguntas

> **Atualização 2026-10-22: o estado das pendências está no §10.** Os itens abaixo são o registro de 2026-10-19/20; o item 2(b) e a política (c) do §1b mudaram (Tam ataca; combo fecha com pagamento da mão).

1. **Nenhuma troca foi aplicada.** O pacote de 6 trocas da avaliação do Moxfield continua só proposta; medir o efeito dele no simulador exige implementar as cartas candidatas (Swords to Plowshares, Oath of Ajani, Doubling Season, Commodore Guff, Karn's Bastion, Mutational Advantage), e só faço isso se você pedir.
2. **Política para discutir:** (a) a ultimate que mata o planeswalker (Vronos `-7` com 7) é decisão do simulador; no seu goldfish você esperou a Vronos chegar a 12. (b) a Tam ativa pouco no simulador (1,18 por partida), e no seu goldfish ela nem ativou (os proliferates vieram do Gauntlet `0`). Qual é a sua regra de jogo para cada uma?
3. **Compra no T1 nos outros decks: RESOLVIDO em 2026-10-20.** Varredura por execução nos 20 simuladores (`varredura-2026-10-05/scripts/audit_compra_t1.py`): só o Mothman pulava; corrigido (`../wise-mothman-sultai/resultados-ab/2026-10-20-compra-no-t1/`); hoje 20 de 20 compram.
4. Os erros factuais da Yavimaya (fetch achando "qualquer terreno") em `auditoria.md`, `avaliacao-moxfield.md` e no registro estão corrigidos (errata no `LEIAME.md` do registro).

## 6. Goldfish manual #2 (2026-10-20) e a Saheeli (2026-10-21)

Pasta do jogo: `resultados-ab/2026-10-20-goldfish-manual-2/` (`LEIAME.md`: log bruto, foto da mão, linha do tempo, **respostas literais**, 16 testes, replay). 8 turnos, mão com Chandra, Way of the Deathbringer, Fellwar Stone, Saheeli e Boseiju; Tam no T3. As respostas do usuário corrigiram o log: a Saheeli entrou só no T5 (o T4 foi undo); no T7 a Eternal Wanderer **não** podia receber o proliferate da Whale (entra depois do gatilho) e faltou o Servo dela; parou no T8 de propósito. 13 das 14 jogadas testáveis **já eram reproduzidas** pelas regras do simulador (mana, custos com a Tam, ordem do gatilho da Whale e do Flux, Chandra `+1`, Aminatou `−1`, Wrenn, Jace, Swift End em planeswalker).
**Achado (Regra #1/#5):** o `−2` da Saheeli só cobria metade do oráculo (cópia de P/T de criatura). O usuário jogou a outra metade no T6 (o Servo vira cópia do Fellwar Stone e paga o Teferi). Implementado em `resultados-ab/2026-10-21-saheeli-copia-de-artefato/` com a chave `SAHEELI_COPY_MANA_ARTIFACT`: cópia de Sol Ring (2 de mana), Arcane Signet e Fellwar Stone (1) num Servo/Food desvirado, só se uma carta valiosa da mão passa a caber (ensaio a seco); **Orrery e Chain Veil não** (lendários); Staff of Compleation e cópia de habilidades de criatura não cobertos. **Medido** (N = 10.000 pareado): 97,06% / 97,98% das partidas idênticas; cópia de mana em 2,94% / 2,02%; ativações da Saheeli +0,017 / +0,019 por partida; mana no T6 +0,002; mesa limpa até T10 +0,10 ± 0,10 (padrão). **A linha de base do §1 vale dentro de ±0,1 ponto.** Validação: 171/171 testes; bit-identidade 20.000 / 20.000 por modo; regressão 20.000 × 2 com 0 exceções; determinismo 0 divergências; a 1ª bit-identidade (inválida só porque todo `Permanent` ganhou o atributo `copy_of`) ficou arquivada e marcada.
**Diferenças de política** entre o usuário e o simulador (não são lacunas de regra; nenhuma foi alterada): (a) a **Tam nunca ataca** no simulador (`NON_ATTACKERS`: o `{T}` de proliferate vale mais); o usuário atacou com ela no T4, quando não tinha mana WUBRG; (b) o **Aminatou `−1` nunca pisca uma rocha de mana virada** (`blink_value` = 0); o usuário piscou o Fellwar no T7 para pagar a Wrenn.
**Não comparado:** vida e dano de oponente (o log não tem); qual mana pagou o quê; os cliques de lealdade do Jace no T4/T5 (lidos como ruído de undo).

## 7. Goldfish manual #3 (2026-10-21)

Pasta: `resultados-ab/2026-10-21-goldfish-manual-3/` (`LEIAME.md`: log bruto, linha do tempo, **respostas literais**, 9 testes, replay com e sem a convenção de cor). 7 turnos (parou no T7 de propósito), mão com Flux Channeler, Ajani Unrelenting, Garruk Curse Breaker, Elder, Exotic Orchard, Orrery e Birds; **só 4 terrenos no jogo todo**; Tam no T4 (a ficha Warrior 1/1 do oponente foi bloqueada por ela); Garruk no T5 (o usuário **esqueceu a compra** do Garruk com o Beast 4/4), Ajani e Aminatou no T6 com o truque de gastar o mana antes do Garruk `+2` desvirar 2 terrenos, Orrery + Dellian no T7.
**Os 9 testes das jogadas passam sem mudar o simulador** (Elder com 2, 3 e 5 mana pelas cores dos permanentes; proliferate do Flux resolvendo antes de o Ajani e a Aminatou entrarem; Garruk `+2`; Cadet por ativação de lealdade; Orrery pagando o Dellian; Stadium desvirado com 3 oponentes; o Garruk compra com o Beast).
**Replay (300 ordens do resto do baralho, mesmas 14 cartas):** com a convenção do simulador, planeswalkers no fim de T5 / T6 / T7 (mediana) **0 / 1 / 3** (padrão) e 0 / 0 / 1 (resiliência) contra **1 / 3 / 4** do usuário. A causa é uma convenção, não regra: a **Exotic Orchard** (e o Fellwar) só produzem cores de terreno de OPONENTE (oráculo), e o simulador sorteia a identidade de cada oponente; no playtester a Orchard do usuário tocou {G} no T2. Com os terrenos dos oponentes produzindo as 5 cores **a partir do T2**, o padrão dá **1 / 3 / 4** (idêntico ao usuário) e a resiliência 0 / 0 / 2.
**Decidido pelo usuário em 2026-10-21: *"Decida os terrenos dos oponentes de forma aleatória"*.** Convenção mantida (sem mudança de código): cada oponente recebe uma identidade de 2 cores sorteada por semente e cada terreno dele produz uma delas. A Orchard/Fellwar só produz a cor se algum terreno de oponente a produz: P({G}) no início do T2 / T3 / T4 / T5 = **40,9% / 58,5% / 67,1% / 72,1%** (`resultados-ab/2026-10-21-cores-terrenos-oponentes/LEIAME.md`).
**Não comparado:** vida e dano de oponente; bloqueio da Tam (estado de oponente); qual mana pagou o quê; o que o usuário faria depois do T7.

## 8. Goldfish manual #4 (2026-10-21)

Pasta: `resultados-ab/2026-10-21-goldfish-manual-4/` (`LEIAME.md`: log bruto, foto da mão, linha do tempo, **respostas literais**, 11 testes, replay). 10 blocos (T1 a T10; o T10 é o **turno extra** do `−12` da Nissa dado pelo Ichormoon Gauntlet; o usuário numera os turnos a partir de 0). Mão com Ajani, Teferi TA, Nissa e Gauntlet; Tam no T3, Nissa no T5 (5 terrenos + 2 de vida num `{G/P}`), Elspeth **anulada pela Vex** no T6 (e a carta da Vex), Teferi e Garruk Veiled Butcher no T7 (o Split Up do oponente matou a Tam), Tam com imposto 1 no T8, Garruk Curse Breaker no T9, **Nissa `−12`**, e no turno extra: Ajani `−2`, proliferates do Gauntlet, Teferi `−10` (emblema).
**Os 11 testes das jogadas passam sem mudar o simulador** (182/182 no total). **Erros de regra do relato (do usuário, não do simulador):** o Teferi `+1` foi jogado errado nos T8 a T10 (olhar 2, 1 na mão, 1 no fundo; ele comprou 1 e devolveu 1: 3 cartas a menos); o Teferi `−1` duas vezes no T7 (só uma ativação por turno; o Teferi TA não tem `−2`); o Ajani `−2` comprou 7 em vez de 8 (o gatilho do próprio Ajani cria o Cadet antes de o `−2` resolver); a Garruk Curse Breaker foi colocada duas vezes (undo).
**Replay (300 ordens, mesmas 18 cartas, T1 a T9, planeswalkers no fim de T4 / T5 / T6 / T7 / T8 / T9, mediana):** usuário 0 / 1 / 1 / 3 / 3 / 4; simulador padrão **1 / 1 / 2 / 4 / 4 / 4**; resiliência 1 / 0 / 1 / 1 / 2 / 2. A convenção de cor de terreno de oponente (Orchard) **não pesa nesta mão** (a variante com 5 cores dá os mesmos números).
**Diferenças de política (nenhuma alterada):** o simulador paga 4 de vida nos dois `{G/P}` da Nissa já no T4 (o usuário pagou 2 no T5); escolhe o alvo do contador do Gauntlet pelo valor do `+1` (o usuário pôs na Nissa). **Não modelado (estado de oponente):** a carta que a Vex deixa comprar; Split Up distingue viradas × desviradas (o simulador destrói todas).
**Não comparado:** vida e dano de oponente; qual mana pagou o quê. **O Twilight Mire e o Ketria Triome descartados no T6** são lidos (releitura de 2026-10-22, inferência não confirmada) como o descarte do **Junji, the Midnight Sky** (*"When Junji dies... each opponent discards two cards and loses 2 life"*; 2 cartas, logo depois do Junji no log; mão de 5, então não é o limite de 7).

## 9. Goldfish manual #5 (2026-10-21/22)

Log do playtester do Archidekt: 11 blocos (T1–T11), `lista.md` sem troca, sem foto. Pasta: [`resultados-ab/2026-10-21-goldfish-manual-5/`](resultados-ab/2026-10-21-goldfish-manual-5/LEIAME.md). O usuário comentou: *"Nesse esqueci muitos gatilhos da Ichormoon, mas depois do 3o emblema no campo fica impossível perder proliferando e jogando turnos extras!"*.

- **O jogo:** mão de 5 depois de mulligan, só 7 terrenos jogados no jogo todo (o desenvolvimento veio do Bloom Tender e dos planeswalkers), Tam no T3, **anulada no T7 pela Ertai's Scorn** (imposto 2), 2 planeswalkers no T6, 4 no T8, 5 no T9, 7 no T10, **4 turnos extras no T11** pelos `−12` do Gauntlet e 3 emblemas (Teferi, Hero; Teferi, Temporal Archmage; Tamiyo); lealdades até 16 (Vronos).
- **Oito dúvidas NÃO respondidas** (o usuário mandou *"Termine tudo que falta!"*); cada uma ficou marcada no LEIAME com a premissa usada (mulligan até 5 com 2 cartas no fundo; Necromancer deixada na mão no T4 por escolha; Tam anulada pela Ertai's Scorn; cliques desfeitos; passo do contador da interface; Teferi TA `−1` ×2 por engano; Necromancer +1 em vez de +3; `0: Proliferate` do Gauntlet não registrado).
- **Erros de regra do relato** (não do simulador): Teferi, Temporal Archmage `−1` ×2 no T10 (só uma ativação por turno); Necromancer com +1 por planeswalker quando 3 criaturas morreram (a regra dá +3).
- **15 testes dirigidos** (`testes/t_manual5.py`): 13 passaram de primeira; **2 revelaram lacunas reais do simulador**, não do usuário: (1) **turnos extras eram booleano** (dois `−12` no mesmo turno rendiam 1 turno extra); (2) **ordem de pagamento** (o Bloom Tender era tocado com 2 cores antes da Pyromancer, e o Watery Grave era desperdiçado em vez da 2ª unidade do filtro). Ambas corrigidas na rodada 2 (`EXTRA_TURNS_STACK`, `VIVID_LAST`, `SIBLING_FIRST`).
- **Replay** (mesma mão, mesmas compras, 300 ordens do resto do baralho; planeswalkers no fim de T10): usuário 7; padrão 16; resiliência de sempre 3; **resiliência com `playtester` 10** (P(simulador ≥ usuário) de 52% a 93% nos turnos T4–T10). Não é validação: o perfil foi ajustado nos mesmos logs.
- **O que o log não tem:** vida e dano de oponente; a ordem exata das ~130 ações do T11; quais proliferates e gatilhos do Gauntlet ele fez.

## 10. Estado das pendências em 2026-10-22 (substitui o §5 onde diferir)

**Resolvido nesta rodada** (cada item com a pasta que o fecha):
1. **Tam atacando** e a política de ataque → rodada 1 (`TAM_ATTACKS`).
2. **Aminatou `−1` e Displacer Kitten em permanente de mana virado** → rodada 1 (`BLINK_UNTAP_MANA`); rara no baralho todo (0,74% / 0,26% das partidas).
3. **Saheeli copiando criatura de mana, Flux Channeler, Displacer Kitten e o Staff of Compleation** → rodada 1 (`SAHEELI_COPY_CREATURES`).
4. **Turnos extras empilhados, ordem de pagamento, combo com o pagamento na mão** → rodada 2.
5. **Tetos de 80 ativações / 60 magias por turno:** medidos; apertam em 0,38% / 0% das partidas (padrão) e 0,14% / 0% (resiliência); subir para 400 / 300 muda 0,4% das partidas e a mesa limpa até T10 em −0,07 ± 0,05 pontos. Ficam em 80 / 60.
6. **Resiliência calibrada com os logs do usuário** → perfil `playtester` (`resultados-ab/2026-10-22-calibracao-playtester/`).
7. **Os 2 descartes do T6 do #4, sem explicação:** explicados como o gatilho de morte do **Junji** ("each opponent discards two cards"), por **inferência** (os 2 descartes aparecem logo depois do Junji; ver §8 e o LEIAME do #4).
8. **Regra #10 adaptada ao Tam:** `varredura-2026-10-05/scripts/audit_tam_terrenos.py` (36 terrenos: entrada virada/desvirada contra o oráculo, alvo do fetch contra os subtipos do oráculo, terreno ≠ magia, landfall): 0 falhas.

**Segue aberto** (declarado, nenhum medido como importante):
1. **Nenhuma troca de carta aplicada** (o pacote de 6 trocas do Moxfield é só proposta; item 1 do §5).
2. **Dorks de mana (Birds, Bloom Tender, Hierarchs) e a Kiora não atacam** por decisão de política (o `{T}` de mana vale mais); a Tam não tem lógica de "ficar em casa" além de: na resiliência, só ataca se nenhum oponente tem criatura com poder.
3. **Piscar da Chain Veil virada** e de criatura de mana (Kitten pisca só não-terreno e a criatura volta com doença de invocação) não entram; **cópias da Saheeli de Whale, Peacemaker, Kiora, Oathkeeper e Lurker**: a política nunca as escolhe.
4. **Perfil `playtester`:** ajustado e comparado nos mesmos 5 logs; **não é a mesa de 3 humanos do usuário**; o alvo da remoção do oponente não foi calibrado (3 das 5 remoções observadas miram artefato/encantamento; a resiliência de sempre mira planeswalker em 60%); a categoria de cada carta de oponente é minha (pelo oráculo).
5. **As 8 dúvidas do #5** (§9) seguem sem resposta do usuário.
6. **Ordem de pagamento:** só a classe "mana vivid" e "unidade irmã de fonte já tocada" foi tratada; outras fontes cujo valor depende da ordem (filtros que dependem de cor já no pool, terrenos de 2 cores tocados antes de um "any color" mais barato) não foram varridas.
