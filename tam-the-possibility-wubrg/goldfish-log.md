# Tam, the Possibility (WUBRG) — goldfish log

> **Atualização 2026-10-21 (§6): goldfish manual #2 do usuário + Saheeli −2 como cópia de artefato de mana** (o usuário jogou no T6 o Servo copiando o Fellwar Stone para pagar o Teferi; o simulador só copiava P/T de criatura; implementado e validado: bit-idêntico com a chave desligada em 20.000 × 2 modos, a cópia dispara em 2,9% / 2,0% das partidas e a linha de base muda ≤ 0,1 ponto): [`resultados-ab/2026-10-20-goldfish-manual-2/`](resultados-ab/2026-10-20-goldfish-manual-2/LEIAME.md) e [`resultados-ab/2026-10-21-saheeli-copia-de-artefato/`](resultados-ab/2026-10-21-saheeli-copia-de-artefato/LEIAME.md). **Goldfish manual #3** recebido (2026-10-21), aguardando respostas do usuário: [`resultados-ab/2026-10-21-goldfish-manual-3/`](resultados-ab/2026-10-21-goldfish-manual-3/).

> **Arquivo dos dados (Regra #8):** [`resultados-ab/2026-10-19-simulador-baseline/`](resultados-ab/2026-10-19-simulador-baseline/LEIAME.md) (brutos `.json.xz`, regressão, conservação, bit-identidade, determinismo, como reproduzir cada tabela) e [`resultados-ab/2026-10-19-goldfish-manual-1/`](resultados-ab/2026-10-19-goldfish-manual-1/LEIAME.md) (o goldfish manual do usuário, compilado). Auditoria de oráculo: [`checklist-oraculo.md`](checklist-oraculo.md). Simulador: `tam_goldfish_v1.py`; testes: `python3 testes/rodar_testes.py` (146).

## 1. Linha de base (2026-10-19): a `lista.md` COMO ESTÁ, nenhuma troca aplicada

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

1. **Nenhuma troca foi aplicada.** O pacote de 6 trocas da avaliação do Moxfield continua só proposta; medir o efeito dele no simulador exige implementar as cartas candidatas (Swords to Plowshares, Oath of Ajani, Doubling Season, Commodore Guff, Karn's Bastion, Mutational Advantage), e só faço isso se você pedir.
2. **Política para discutir:** (a) a ultimate que mata o planeswalker (Vronos `-7` com 7) é decisão do simulador; no seu goldfish você esperou a Vronos chegar a 12. (b) a Tam ativa pouco no simulador (1,18 por partida), e no seu goldfish ela nem ativou (os proliferates vieram do Gauntlet `0`). Qual é a sua regra de jogo para cada uma?
3. **Compra no T1 nos outros decks: RESOLVIDO em 2026-10-20.** Varredura por execução nos 20 simuladores (`varredura-2026-10-05/scripts/audit_compra_t1.py`): só o Mothman pulava; corrigido (`../wise-mothman-sultai/resultados-ab/2026-10-20-compra-no-t1/`); hoje 20 de 20 compram.
4. Os erros factuais da Yavimaya (fetch achando "qualquer terreno") em `auditoria.md`, `avaliacao-moxfield.md` e no registro estão corrigidos (errata no `LEIAME.md` do registro).

## 6. Goldfish manual #2 (2026-10-20) e a Saheeli (2026-10-21)

Pasta do jogo: `resultados-ab/2026-10-20-goldfish-manual-2/` (`LEIAME.md`: log bruto, foto da mão, linha do tempo, **respostas literais**, 16 testes, replay). 8 turnos, mão com Chandra, Way of the Deathbringer, Fellwar Stone, Saheeli e Boseiju; Tam no T3. As respostas do usuário corrigiram o log: a Saheeli entrou só no T5 (o T4 foi undo); no T7 a Eternal Wanderer **não** podia receber o proliferate da Whale (entra depois do gatilho) e faltou o Servo dela; parou no T8 de propósito. 13 das 14 jogadas testáveis **já eram reproduzidas** pelas regras do simulador (mana, custos com a Tam, ordem do gatilho da Whale e do Flux, Chandra `+1`, Aminatou `−1`, Wrenn, Jace, Swift End em planeswalker).
**Achado (Regra #1/#5):** o `−2` da Saheeli só cobria metade do oráculo (cópia de P/T de criatura). O usuário jogou a outra metade no T6 (o Servo vira cópia do Fellwar Stone e paga o Teferi). Implementado em `resultados-ab/2026-10-21-saheeli-copia-de-artefato/` com a chave `SAHEELI_COPY_MANA_ARTIFACT`: cópia de Sol Ring (2 de mana), Arcane Signet e Fellwar Stone (1) num Servo/Food desvirado, só se uma carta valiosa da mão passa a caber (ensaio a seco); **Orrery e Chain Veil não** (lendários); Staff of Compleation e cópia de habilidades de criatura não cobertos. **Medido** (N = 10.000 pareado): 97,06% / 97,98% das partidas idênticas; cópia de mana em 2,94% / 2,02%; ativações da Saheeli +0,017 / +0,019 por partida; mana no T6 +0,002; mesa limpa até T10 +0,10 ± 0,10 (padrão). **A linha de base do §1 vale dentro de ±0,1 ponto.** Validação: 171/171 testes; bit-identidade 20.000 / 20.000 por modo; regressão 20.000 × 2 com 0 exceções; determinismo 0 divergências; a 1ª bit-identidade (inválida só porque todo `Permanent` ganhou o atributo `copy_of`) ficou arquivada e marcada.
**Diferenças de política** entre o usuário e o simulador (não são lacunas de regra; nenhuma foi alterada): (a) a **Tam nunca ataca** no simulador (`NON_ATTACKERS`: o `{T}` de proliferate vale mais); o usuário atacou com ela no T4, quando não tinha mana WUBRG; (b) o **Aminatou `−1` nunca pisca uma rocha de mana virada** (`blink_value` = 0); o usuário piscou o Fellwar no T7 para pagar a Wrenn.
**Não comparado:** vida e dano de oponente (o log não tem); qual mana pagou o quê; os cliques de lealdade do Jace no T4/T5 (lidos como ruído de undo).
