# The Wise Mothman — log do goldfish (simulador `mothman_goldfish_v1.py`)

> **Atualização 2026-10-07 (§10):** a guarda do payoff antes do terreno que o §8 arquivou (aritmética) era cega a cor e superestimou o efeito (Ruin Crab +21% → **+13%**; mesa limpa até T8 +0,9 → **+0,6 ponto**). O padrão agora é o ensaio a seco, igual aos outros 5 simuladores: [`resultados-ab/2026-10-07-guarda-ensaio-a-seco/LEIAME.md`](resultados-ab/2026-10-07-guarda-ensaio-a-seco/LEIAME.md). Os lotes do §8 ficam como estavam (guarda aritmética, **superados em magnitude**).

> **Atualização 2026-10-07 (§11): Riverchurn Monument** (inclusão + 5 cortes; simulador com as duas ativadas; método `SWAP_IN_PLACE`): [`resultados-ab/2026-10-07-riverchurn-monument/`](resultados-ab/2026-10-07-riverchurn-monument/LEIAME.md).

> **Dados brutos, scripts e como refazer cada tabela:** `resultados-ab/2026-10-05-ab-pacote-kozilek-master/` (pacote, Master, Kozilek, controles) · `resultados-ab/2026-10-05-ab-kozilek-self-deck/` (Kozilek × estilo de jogo) · `resultados-ab/2026-10-05-simulador-v1-validacao/` (testes, varreduras, determinismo, regressão) · `resultados-ab/2026-10-06-tergrid-e-ferramenta-mill/` (ferramenta de mill nos oponentes + Tergrid) · `resultados-ab/2026-10-06-partida-manual-1/` (partida manual #1: log, ledger, ensaio) · `resultados-ab/2026-10-06-landfall-payoff-primeiro/` (correção da ordem terreno × payoff de landfall) · `resultados-ab/2026-10-06-partida-manual-2/` (partida manual #2).
> Auditoria cláusula-a-cláusula: `checklist-oraculo.md`. Simulador no commit `91b1a3d` (código congelado durante as baterias).
> **Atenção (2026-10-06):** os números dos §1–§6 foram gerados com a ordem antiga (terreno antes do Ruin Crab/Icetill), que é `LANDFALL_PAYOFF_FIRST = False` e bit-idêntica a `91b1a3d`. O padrão do simulador agora é `True` (§8): a linha de base muda pouco (mesa limpa até T8 de 50,7% para 51,6%; deck-out sem diferença).
> **Premissas e o que NÃO se mede:** mesa de 4 com **3 oponentes passivos** (sem tabuleiro, todo atacante conecta; mill/vida/rad/biblioteca deles são reais; `OPP_TARGET_PROB` 0,7 para efeitos que precisam de alvo); a IA do jogador é uma heurística declarada (checklist §5), **evidência de apoio, não a fonte da verdade** (Regra #5 de `CLAUDE.md`). Todos os números abaixo são paridos por semente, com IC95%; "*" = a diferença excede o IC.

## 1. Linha de base (lista atual, N = 10.000, sementes 3.000.000+i, 12 turnos)

| | modo padrão | modo resiliência |
|---|---|---|
| Mothman conjurado até T4 / T5 / nunca em 12 turnos | 61,2% / 74,5% / 1,7% | 56,2% / 68,6% / 2,5% |
| **mesa inteira (3 oponentes) eliminada até T7 / T8 / T9 / T10** | 14,8% / **50,7%** / 75,5% / **85,0%** | 6,0% / **23,5%** / 43,1% / **58,1%** |
| 1º oponente eliminado até T6 / T8 | 38,8% / 84,8% | 23,3% / 65,8% |
| como os oponentes saem (média de 3 por partida) | vida 2,50 · comandante (21) 0,26 · biblioteca vazia 0,10 | vida 2,12 · comandante 0,36 · biblioteca 0,07 |
| **eu perdo por deck-out** (`self_lost`) | **3,29%** | **1,53%** |
| gatilhos do Mothman por partida (meu mill / mill de oponente) | 27,6 (7,9 / 20,0) | 24,0 (6,8 / 17,5) |
| contadores +1/+1 postos (todas as fontes) / maior poder | 111 / 29 | 78 / 24 |
| cartas milladas: eu / oponentes | 16,8 / 84,2 | 16,0 / 69,4 |
| partidas com o combo Ascension + (Mindcrank ou Master) | 2,18% | 1,60% |
| partidas em que o Kozilek **embaralha** o cemitério / em que é **conjurado** | **27,4%** / 4,0% | 26,5% / 3,7% |

Leitura (raciocinada, de números medidos): o deck mata a mesa **passiva** por perda de vida (rad + Mindcrank/Konrad/Palantír + combate), não por dano de comandante nem por deck-out de oponente; o combo da Ascension aparece em ~2% das partidas, a mesma ordem da conta hipergeométrica (1,6–3,5%) de `candidatas-pos-eoe.md`.

## 2. Kozilek: ele evita a morte por self-mill?

**Sim, mas por ser milado ou descartado, não por ser conjurado** (só 4% das partidas chegam a conjurá-lo; ele embaralha em 27%). Taxa de deck-out (`self_lost`), N = 10.000 pareado:

| estilo de jogo | com Kozilek (lista atual) | Kozilek **sem** o embaralhar | Kozilek **cortado** (← Forest) | o embaralhar vale |
|---|---|---|---|---|
| **cuidadoso** (guarda de biblioteca ligada), padrão | 3,29% | 5,73% (+2,44 ± 0,36 *) | 5,97% (+2,68 ± 0,57 *) | **~2,4 pontos** |
| cuidadoso, resiliência | 1,53% | 2,95% (+1,42 ± 0,28 *) | 3,30% (+1,77 ± 0,42 *) | ~1,4 pontos |
| **descuidado** (guarda desligada), padrão | 8,14% (+4,85 ± 0,44 *) | 10,91% (+7,62 ± 0,55 *) | 11,64% (+8,35 ± 0,70 *) | ~2,8 pontos |
| descuidado, resiliência | 3,85% (+2,32 ± 0,31 *) | 5,51% (+3,98 ± 0,41 *) | 6,69% (+5,16 ± 0,54 *) | ~1,7 pontos |

- **O seguro tira cerca de 40% das derrotas por deck-out de quem joga cuidadoso** (3,29% contra 5,73%) e tem o efeito colateral esperado: sem ele a mesa é limpa até T10 em 2,2 pontos a menos (−2,15 ± 0,36 *).
- **A disciplina de biblioteca vale mais que o Kozilek:** jogar descuidado custa +4,85 pontos de deck-out, o dobro do que o Kozilek devolve. Os dois somam: cuidadoso + Kozilek é o melhor dos quatro cantos.
- Cortar o Kozilek (← Forest) deixa a mesa **mais rápida até T8 (+2,1 ± 1,3 *)** (uma terra no lugar de um 10-mana) e **mais lenta até T10 (−1,2 ± 1,0 *)**, com deck-out +2,7 pontos: o Kozilek é o seguro, não o motor de velocidade.
- Sensibilidade (N = 2.000, ver `ab-kozilek-self-deck/resumos/compacto_2000.txt`): `reserva_0` (a IA deixa a biblioteca chegar a 0) +1,4 ± 0,6 pontos de deck-out; `reserva_16` −0,75 ± 0,51 (guarda mais folgada: sem custo de velocidade medido, +0,6 ± 0,5 em T10); o Palantír (oponente sempre recusa) e o limite de biblioteca do Mesmeric Orb **não mexem** nada mensurável (diferença de deck-out +0,0 ± 0,14 pontos com o limite removido: ele quase nunca chega a valer).
- **Não verificado:** um jogador humano pode jogar melhor ou pior que a heurística do simulador; o ganho do seguro depende de quanta auto-mill o jogador aceita. O que é robusto aqui é a ORDEM (disciplina > Kozilek > nada) e o piso de ~2 pontos de deck-out.

## 3. Pacote de 5 trocas (`candidatas-pos-eoe.md` §0) e Master of Lake-town

N = 10.000 pareado, diferença sobre a lista atual, **pontos percentuais** de partidas com a mesa limpa até T8 (e T10):

| variante | padrão T8 | padrão T10 | resiliência T8 | resiliência T10 | deck-out (padrão) |
|---|---|---|---|---|---|
| **pacote de 5 trocas** | **+4,6 ± 1,4 *** | +2,3 ± 0,9 * | +2,1 ± 1,1 * | +0,9 ± 1,3 | −0,7 ± 0,5 * |
| S1 Evolution Sage ← Selkie | +2,4 ± 1,4 * | +0,7 ± 1,0 | +1,3 ± 1,1 * | +0,2 ± 1,3 | −0,4 ± 0,5 |
| S2 Karn's Bastion ← Swarmyard | +0,7 ± 1,2 | +0,4 ± 0,9 | −0,1 ± 1,0 | +0,6 ± 1,2 | −0,1 ± 0,5 |
| S3 Bruvac ← Soul-Guide Lantern | +1,3 ± 1,2 * | +0,9 ± 0,9 * | +0,5 ± 1,0 | +0,8 ± 1,2 | −0,7 ± 0,4 * |
| S4 Garruk's Uprising ← An Offer | +1,3 ± 1,4 | +0,2 ± 1,0 | +0,7 ± 1,1 | +0,7 ± 1,3 | +0,4 ± 0,5 |
| S5 Opulent Palace ← Bojuka Bog | +2,0 ± 1,4 * | +1,2 ± 1,0 * | +1,6 ± 1,1 * | +1,4 ± 1,3 * | −0,3 ± 0,5 |
| **Master ← Negate** | **+3,6 ± 1,3 *** | +1,0 ± 0,9 * | +2,2 ± 1,1 * | +0,9 ± 1,2 | −0,1 ± 0,5 |
| Master ← Strip Mine | +2,2 ± 1,2 * | +1,0 ± 0,9 * | +1,2 ± 1,0 * | +1,0 ± 1,2 | −0,5 ± 0,5 * |
| Master ← Yavimaya Hollow | +1,8 ± 0,7 * | +0,5 ± 0,6 | +1,3 ± 0,6 * | +0,7 ± 0,8 | −0,4 ± 0,4 * |
| **pacote de 5 + Master ← Negate** | **+6,9 ± 1,4 *** | **+2,6 ± 0,9 *** | **+3,6 ± 1,2 *** | **+2,4 ± 1,3 *** | −0,8 ± 0,5 * |

- **Combo Ascension:** com o Master em campo a fração de partidas em que o combo (Ascension + perda de vida → mill) fecha sobe de 2,2% para **3,4% a 4,2%** (medido), dependendo do corte.
- As diferenças das trocas individuais **não se somam** (soma das 5 = +7,7; o pacote = +4,6): há redundância entre elas (proliferate e mill dobrado competem pelo mesmo gargalo: a perda de vida do oponente).
- **Limite do medidor (importante):** o corte de controle `Hardened Scales ← Forest` MOVEU `counters_placed_total` em −7,5 ± 3,1 (a métrica de contadores funciona), mas **não** mexeu na velocidade de limpeza (T8 +0,3 ± 1,4): neste simulador a mesa passiva cai por vida, não por tamanho das criaturas. **Portanto este A/B não consegue valorizar cartas cuja função é crescer contadores** (Terrasymbiosis, Corpsejack, Mutational Advantage…); para elas o medidor adequado é o próprio nº de contadores / poder do Mothman, e a velocidade seria um piso. A lista Tier 2 de `candidatas-pos-eoe.md` **não foi simulada** (só o pacote de 5 e o Master).
- **Master: o corte menos custoso, medido, é Negate** (maior ganho de velocidade). Mas o simulador não mede o valor de interação contra um oponente real além do proxy; Negate protege o motor contra remoção/wipe de não-criatura (modo resiliência: o ganho do Master ← Negate continua positivo, +2,2 ± 1,1 em T8), e a escolha final fica com o usuário (**nada foi cortado nem adicionado na lista dele**).

## 4. Controles e verificações (ver as pastas de validação)

Controle positivo do medidor de deck-out: guarda desligada → `self_lost` +4,85 ± 0,44 (subiu, como devia). Controle de corte de peça: Scales ← Forest → contadores −7,5 (desceu). 134 testes dirigidos; 20.000 partidas × 12 configurações sem exceção; determinismo 0 divergências em 3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos; varreduras de entrada de terreno (27 terrenos × oráculo), fetch real, landfall (7.299 entradas = 7.299 chamadas). Achados reais da construção e do A/B (erros de combate quando a mesa morre entre dois pontos do mesmo passo) estão em `checklist-oraculo.md` e nos `LEIAME.md` das pastas.

## 5. O que NÃO foi feito (Regra #7)

Cartas Tier 2 (Terrasymbiosis, Corpsejack, Loading Zone, Mutational Advantage, Contentious Plan, Tekuthal, Lo and Li, Oko, Grist, Trystan, Rancor, Biosynthic Burst, Drix, Thrummingbird, Vraska) **não** implementadas; oponentes reais/politicas de mesa; Commander Spellbook **não** foi rodado de novo (nenhuma carta foi trocada na lista); o corte do Master não foi decidido pelo usuário.

## 6. Ferramenta de mill nos oponentes (2026-10-06)

`python3 ferramentas/mill_oponentes.py -n 5000 [--modo resiliencia] -v base -v pacote5 -v "meu:Negate=>The Master of Lake-town"` (uso completo no cabeçalho do arquivo). Mostra por turno, por fonte e "o que o mill rende", e com 2+ variantes a diferença pareada com IC95%. Dados brutos, tabelas e verificação: `resultados-ab/2026-10-06-tergrid-e-ferramenta-mill/` (6 de 6 saídas idênticas no `cmp`).
**Medido (N = 5.000, mesma semente; padrão, com a resiliência entre parênteses; combina com o §1, N = 10.000):**

- **83,9 cartas milladas dos oponentes por partida (68,7)**, 50,7 não-terreno (42,1). Só **30%** da biblioteca de cada oponente está milada em T12 (25%); o mill concentra-se em T6–T8 (14,4 / 19,8 / 16,9 cartas por rodada nos 3 oponentes, padrão).
- **Fontes (cartas/partida, padrão):** Mindcrank 18,8 · rad 13,1 · Altar of the Brood 11,9 · Psychic Corrosion 11,9 · Ruin Crab 9,3 · Mesmeric Orb 4,1 · Undead Alchemist 4,1 · combo Ascension 3,0 · Ashiok 2,6 · Deepmuck 1,5 · Zellix 1,1 · Memory Erosion 1,0 · Altar of Dementia 0,9 · Konrad 0,6 · Didn't Say Please 0,2. Na resiliência o rad passa a primeiro (16,0) e o Mindcrank cai para 13,0.
- **O mill é motor de contadores e de rad, não a forma de matar:** 0,10 oponente por partida sai por biblioteca vazia (0,06); pelo menos 1 oponente decka em **6,2%** das partidas (4,1%). Os 2,9 oponentes eliminados saem por perda de vida (2,50) e comandante (0,26). Mesa limpa até T8: 51,4% (24,1%) · T10: 85,3% (58,6%).
- **Pareado (padrão, diferença sobre a lista atual; * = excede o IC):** pacote de 5 trocas: cartas milladas −1,0 ± 2,7 (sem efeito), rad +1,5 cartas (proliferate), mesa limpa T8 +4,3 ± 1,9 pontos *; **pacote + Master ← Negate: +14,7 ± 2,8 cartas** (o Master sozinho responde por +13,8) *; Bruvac sozinho +2,3 ± 2,2 (Mindcrank +1,0); sem o embaralhar do Kozilek −0,6 ± 0,5 (0,7%, efeito colateral: o Kozilek não é fonte de mill do oponente). Resiliência, pacote + Master: +13,5 ± 2,4 cartas *.
- **Achados da ferramenta (corrigidos antes de arquivar, não afetam os brutos):** a ordem de desempate de uma linha dependia de `PYTHONHASHSEED`; e a soma por fonte não fechava com o total (80,9 contra 83,9) porque o loop do combo Ascension + Mindcrank mila a biblioteca inteira fora de `mill_event`. Agora há a linha `ascension_loop` e uma asserção de que a soma das fontes é o total.
- **Não verificado / limites:** oponentes passivos (sem tabuleiro, sem escolha, sem interação com o mill: um oponente real com Bruvac na mesa ou fetchland muda os números); a ferramenta mede mill de oponente, não o auto-mill (`self_lost`, §2).

**Tergrid (candidata):** não implementada no motor. Oráculo + rulings + enumeração por script + Spellbook + tetos medidos em `candidatas-pos-eoe.md` §12: o mill **não** dispara a Tergrid (só sacrifício/descarte do oponente); a lista tem 1 fonte de sacrifício (Kozilek, ataca em 2% das partidas) e 0 de descarte.

## 7. Partida manual #1 (2026-10-06, 9 turnos, Archidekt playtester)

Dados, scripts e como refazer: `resultados-ab/2026-10-06-partida-manual-1/LEIAME.md` (**aguardando respostas do usuário**; nada foi tratado como erro do usuário ainda). O usuário avisou que o log **não contém o mill de oponente** (Memory Erosion por magia; Ruin Crab quando entram terrenos, até 2 vezes por turno com o Icetill).
- **Legal:** mana viável em T2-T9 (por script), retraces da Six pagos (Icetill, Ruin Crab, Hardened Scales), Wave Goodbye devolveu só as criaturas sem contador, Evacuation devolveu as outras 5.
- **O log prova:** (1) a substituição do **Kami of Whispered Hopes nunca foi aplicada** (7 colocações com ele em campo, todas +1 onde a regra manda +2); (2) 3 gatilhos do Mothman por mill meu **sem contador** (T4 X = 2; T7 Siege; T8 Palantír); (3) **≥ 1 mill meu a menos** em T6 e em T8; (4) **jogadas de terreno do Icetill não usadas**: T6 1 de 2, T7 0 de 2, T8 1 de 2, T9 0 de 2, com o Ruin Crab em campo (6 gatilhos do Crab perdidos); (5) a Six não atacou em T5-T7.
- **Reconstruído:** 4 eventos de mill de oponente (Erosion T6 e T7; Crab T7 e T8) = 22 cartas, ~13,8 não-terrenos; contadores esperados pelas regras 45,3 contra 7 no log (23,3 dependem do mill de oponente).
- **Ensaio no simulador (apoio, Regra #5):** o mesmo campo no início do T7 rende em média 7,0 terrenos entrando, 7,0 gatilhos do Crab e 64 cartas milladas de oponente (manual: 1 terreno e 1 gatilho).
- **Gap do simulador achado (a corrigir, atrás de chave):** o simulador joga o terreno **antes** de conjurar o Ruin Crab/Icetill (100% das sementes em 4 cenários dirigidos), enquanto o jogador real conjura o payoff e só depois joga o terreno (foi o T8 do usuário). Ver o commit seguinte.
- **Não verificado:** vida, rad, ordem da pilha, quais cartas o oponente milou, o que veio depois do ataque do T9.

## 8. Correção do simulador: o terreno entrava ANTES do Ruin Crab / Icetill (2026-10-06)

> **Superado em magnitude (2026-10-07, §10):** os números desta seção usam a guarda aritmética do comandante; com o ensaio a seco (padrão atual) o efeito é menor.

Achado no ensaio da partida manual #1 (§7): o usuário conjurou Ruin Crab, Mothman e Icetill e só então jogou o terreno; o simulador chamava `play_land_phase` antes de `cast_loop`, então o payoff de landfall nunca estava em campo quando o terreno do turno entrava (100% das sementes em 4 cenários dirigidos). Pasta: `resultados-ab/2026-10-06-landfall-payoff-primeiro/` (LEIAME completo).
- **Correção:** chave `LANDFALL_PAYOFF_FIRST` (padrão `True`) + `cast_landfall_payoffs_first`: com um terreno por jogar, conjura Ruin Crab / Icetill Explorer / Evolution Sage **antes** se o mana de agora já o paga; o comandante tem prioridade; o retrace da Six só antecipa se sobra outro terreno na mão.
- **Validação:** 139/139 testes dirigidos (5 novos); bit-identidade 20.000 × 2 modos (chave desligada == `91b1a3d` em 40.000 de 40.000; ligada: 28.717 sem disparo e idênticas, 11.283 com disparo, 0 divergências); regressão 20.000 × 4 configurações × 2 modos, 0 exceções; determinismo 3 `PYTHONHASHSEED` × 1.500 × 2 modos, 0 divergências; varreduras da Regra #10 OK (7.329 entradas de terreno = 7.329 chamadas de landfall).
- **Medido (N = 10.000 pareado, ligada − desligada, padrão; resiliência entre parênteses):** o payoff entra antes do terreno em 0,37 (0,29) vezes por partida; gatilhos do Ruin Crab **+0,32 ± 0,03** (+0,22 ± 0,03), +21%; cartas milladas dos oponentes +1,6 ± 0,4 (+0,8 ± 0,4), +1,9%; mesa limpa até T8 **+0,9 ± 0,4** pontos (+0,8 ± 0,3), até T10 sem diferença; **deck-out sem efeito** (+0,02 ± 0,29; +0,02 ± 0,19 pontos). Com o pacote de 5 trocas (traz a Evolution Sage, também payoff de landfall) o ganho em T8 é maior: +1,5 ponto.
- **Nova linha de base (padrão; resiliência):** mesa limpa até T7 / T8 / T10 = 15,3% / **51,6%** / 84,9% (6,3% / 24,3% / 58,2%); cartas milladas dos oponentes 85,8 (70,2). As comparações pareadas dos §2-§3 não mudam de direção.
- **A classe nos outros simuladores** (`varredura-2026-10-05/scripts/audit_landfall_ordem.py`): 1 candidato claro, o **Toph**; Beorn, Maralen, Thranduil e Prismatic Bridge o script não lia (leitura à mão). **Corrigidos em 2026-10-07** (`<deck>/resultados-ab/2026-10-07-landfall-payoff-primeiro/`): os 5 tinham o mesmo erro; `audit_landfall_ordem.py` agora dá 0 candidatos nos 19 simuladores.
- **Não verificado:** o humano pode preferir outra ordem (guardar o terreno por informação); só 3 payoffs foram incluídos (o Altar of the Brood também dispara com terreno).

## 9. Partida manual #2 (2026-10-06, 7 turnos, Archidekt playtester)

Dados, scripts e como refazer: `resultados-ab/2026-10-06-partida-manual-2/LEIAME.md` (**respostas do usuário recebidas em 2026-10-07**, no fim desta seção). O log termina no meio do gatilho de combate do T7 (o usuário se perdeu contando os marcadores do Ouroboroid).
- **O log prova:** (1) **T3 e T4 não fecham de mana com o texto real da Gyre Sage** (1 G por *contador*): Mothman 4 com 3 fontes; Henge 5 (`{7}{G}{G}` menos o maior poder, 4) com 4 fontes; fecham se a Gyre Sage der 1 G por *ponto de poder*; (2) T4 sem jogada de terreno com a Takenuma na mão; (3) a compra do Henge para a Broodscale (T4) não aparece; (4) as substituições do **Kami e do Winding Constrictor foram aplicadas pela metade** (T5: Constrictor 1 em vez de 2, Kami 2 em vez de 3; T6: Ouroboroid entrando 2 em vez de 3, gatilho do Mothman +2 em vez de +3, combate +6 por criatura em vez de +7, ficha Eldrazi Spawn sem contador) e, no T7, as duas valeram (+13 = 11 + 2, certo); (5) a Gyre Sage ganhou +2 no T5 que o meu ledger não explicava (**retirado como achado** depois da resposta 5: a fonte foi o mill do rad com o Mothman); (6) com o Constrictor em campo cada ETB/ataque do Mothman dá **2** rad counters: mills do T6 e do T7 ≥ 1 abaixo do exigido.
- **O erro se compõe:** o Ouroboroid vai de c para **2c + 3** contadores a cada combate. Pelas regras, com as mesmas escolhas de alvo, o fim do T6 seria Mothman 13 / Ouroboroid 15 (log: 10 / 10) e o gatilho do T7 X = 16, +18 por criatura (log: X = 11, +13).
- **O simulador acerta** as 5 cláusulas que o log errou (Gyre Sage por contador, Henge 5, Kami + Constrictor = +3, rad +1 com Constrictor, Ouroboroid com ficha e as duas substituições): `resumos/confere_simulador.txt`.
- **Não verificado:** vida, rad, ordem da pilha e o que veio depois do último registro (T7 interrompido).
- **Respostas do usuário (2026-10-07), literais resumidas:** (1) leu a Gyre Sage como 1 mana por ponto de **poder** (erro de leitura; o simulador estava certo); (2) esqueceu a compra do Henge no T4; (3) "baixei o Constrictor primeiro e o Kami depois, então…" (**frase cortada na mensagem**; a ordem coincide com a que o ledger já assumia, Kami 0 / Constrictor 1 no Constrictor e 1/1 no Kami, então isso explica a ausência do Kami na conta do Constrictor, **mas não o +1 do próprio Constrictor sobre si mesmo**, que segue sem explicação); (4) esqueceu as fichas Eldrazi Spawn; (5) os +2 da Gyre Sage vieram "do mill do rad counter e Mothman"; (6) pegou **1** rad e não 2 (esqueceu o +1 do Constrictor); (7) parou antes de somar os contadores do Ouroboroid no T7 porque "já tinha errado tudo mesmo".
  - **Correção minha (Regra #7):** eu havia marcado a Gyre Sage +2 como "sem fonte pelas regras". Faltou considerar que o Mothman dá rad a **cada** jogador ("each player gets a rad counter"): o mill do rad **dos oponentes**, nos turnos deles, também dispara o Mothman e o log não o registra. É a explicação compatível com a resposta 5, mas de quem foi o mill **não consta** (inferência). O replay do fim do T6 pelas regras passa a usar esse +2: Gyre Sage **12** (era 10); os demais números não mudam.

## 10. Guarda do payoff antes do terreno: aritmética × ensaio a seco (2026-10-07)

Pasta: `resultados-ab/2026-10-07-guarda-ensaio-a-seco/` (`LEIAME.md` completo; tabelas em `resumos/resumo_guarda.md`).
- **Achado:** ao corrigir os outros 5 simuladores, a fórmula `custo do comandante <= mana de agora + 1` falhou no Beorn (comandante atrasado em 38 de 2.000 partidas). No Mothman ela falha por **cor**: Ruin Crab `{U}` + comandante `{1}{B}{G}{U}` = 5 = mana de agora + 1, mas o Crab gasta o único Island e o comandante não é conjurado (cena dirigida nos testes).
- **Correção:** chave `LANDFALL_GUARD_DRYRUN` (padrão **True**): ensaio a seco do resto da fase nas duas ordens, o payoff só passa se nenhuma jogada não-terreno da ordem antiga se perder. `False` = a guarda aritmética arquivada.
- **Medido (N = 10.000 pareado, padrão; guarda aritmética → ensaio a seco):** payoff antes do terreno 0,37 → **0,21** por partida; gatilhos do Ruin Crab **+0,32 → +0,20** (+21% → +13%); Icetill replays +0,17 → +0,02; contadores do Mothman +0,94 → +0,69; mesa limpa até T8 **+0,9 → +0,6 ponto** (resiliência +0,8 → +0,5); deck-out sem efeito nas duas. **Pacote de 5 trocas + Master** (N = 2.000, pacote − guarda): mesa limpa até T8 **+6,6 (aritmética) × +5,6 (ensaio)** pontos no padrão, +4,1 × +4,0 na resiliência: a conclusão do pacote não muda.
- **Nova linha de base** (padrão; resiliência), mesa limpa até T8: 50,7% (ordem antiga) → **51,3%** (ensaio a seco; era 51,6% com a guarda aritmética).
- **Validação:** testes dirigidos 141/141; bit-identidade com `LANDFALL_PAYOFF_FIRST` desligada == `91b1a3d` 20.000 × 2 modos com o código final; regressão 20.000 × 2 modos da variante `ensaio` (0 exceções); determinismo 3 `PYTHONHASHSEED` × 1.500 × 2 modos; a pasta `2026-10-06-landfall-payoff-primeiro` continua reproduzindo byte a byte (configs e `bitident.py` fixam `LANDFALL_GUARD_DRYRUN = false`).
- **Não verificado:** o critério do ensaio a seco é conservador (no Mothman recusa cerca de metade dos payoffs que a guarda aritmética deixava passar, parte por efeito colateral benigno do landfall): o número do ensaio é um limite **inferior** do payoff-primeiro e o da guarda aritmética, **superior**.

## 11. Riverchurn Monument: inclusão e 5 cortes (2026-10-07)

Pasta: `resultados-ab/2026-10-07-riverchurn-monument/` (`LEIAME.md` completo: como foi gerado, mapa arquivo → status, comandos, verificação). Pergunta do usuário: avaliar a inclusão e elencar 5 trocas, do menos para o mais importante ao gameplan.
- **Carta (oráculo ao vivo, rulings 2025-02-07):** `{1}{U}` artefato; `{1},{T}`: qualquer número de jogadores-alvo milam 2; **Exhaust** `{2}{U}{U},{T}`: milam tantas cartas quanto o próprio cemitério (uma vez por objeto). Implementada com as duas cláusulas, o artefato (Altar of the Brood, Mesmeric Orb, Construct da Urza's Saga) e as rulings; chaves `RIVERCHURN_*`; testes dirigidos 157/157 (16 novos).
- **Spellbook** (nomes reconhecidos 91/91, controles positivo e de corte passaram): o Monument **não cria combo novo**; 8 combos de 2 peças "quase" (Traumatize, Maddening Cacophony, Jidoor, Singularity Rupture, Cut Your Losses, Terisian Mindbreaker, Fleet Swallower, Kitsune's Technique), **nenhuma na lista**: nada muda no Bracket. Os únicos cortes que derrubam combo são as 5 peças dos 2 combos da lista (fora das candidatas).
- **Medido (Monument ← Negate, N = 10.000 pareado, no lugar):** mesa limpa até T8 **+1,03 ± 0,28 ponto** (padrão: 51,4% → 52,4%), **+0,36 ± 0,24** (resiliência: 24,0% → 24,4%); cartas milladas dos oponentes +1,9 por partida (de 85,4); eu perco por deck-out −0,12 ± 0,19 (sem efeito). **Todo o ganho vem das ativadas** (só o corpo: +0,02 ± 0,21). A carta entra em campo em 18,7% das partidas (12 turnos), entra até T4 em 5,4%; nas partidas em que entra, tap 1,73× e Exhaust 0,17× por partida; **entrando até T4: +10,5 ± 3,3 pontos de mesa limpa até T8** (`resumos/condicional.txt`).
- **Políticas (sensibilidade, plataforma ← Negate):** o limiar do Exhaust quase não importa (só letal +0,97, 12 cartas +1,01, 48 +0,98); **incluir a mim como alvo** (quando a biblioteca deixa) +1,31 ± 0,33; **pagar o tap ANTES das conjurações piora o T8** (+0,64) apesar de milar mais (+3,5 cartas): o `{1}` compete com o desenvolvimento; a janela do fim do turno do oponente (mana que sobrou/segurada pras contramágicas) fica igual ao padrão (+1,03) e dá +0,2 carta milada. A política padrão (só com mana sobrando) é a melhor em velocidade.
- **Sinergia medida, rara:** Exhaust com a Bloodchief Ascension armada (3 marcadores; cada carta milada tira 2 de vida) acontece em 0,2% das partidas; é uma linha real, não um motor.
- **Antissinergia (por script):** 4 cartas da lista exilam cemitério (Bojuka Bog, Soul-Guide Lantern, Agatha's Soul Cauldron, Ashiok), e o Exhaust lê o tamanho do cemitério dos oponentes.
- **Sobre o pacote de 5 trocas + Master ← Negate (pendente):** o Monument continua positivo por cima dele (Bruvac dobra o mill dele): ← Muldrotha +0,87 ± 0,35, ← Arcane Denial +0,79 ± 0,29, ← Fallout +0,66 ± 0,24, ← Wave Goodbye +0,63 ± 0,25, ← Toxic Deluge +0,53 ± 0,23, ← V.A.T.S. +0,30 ± 0,26 pontos de T8 (padrão). **Conflito de cortes:** Offer (Garruk's Uprising), Negate (Master), Lantern, Bog, Selkie e Swarmyard já estão reservados por esse pacote.
- **5 cortes, do menos importante para o mais importante ao gameplan** (pelo papel real; o simulador só confirma que o Monument não perde para nenhum deles além do ruído): **1. An Offer You Can't Refuse** (3ª "counter noncreature" com Negate e Fierce Guardianship; dá 2 Treasures a um oponente em mesa de 4) · **2. Negate** (mesma função) · **3. Muldrotha** (6 de mana, recursão redundante com Six, Icetill, Evolution Witness e Agadeem; o plano é milar oponente, não se reciclar) · **4. Toxic Deluge** (3º varredor, simétrico e pago com vida; Wave Goodbye é unilateral pelos contadores e Fallout dá rad) · **5. Arcane Denial** (dá até 2 cartas ao oponente em mesa de 4; empata com o Monument na resiliência, +0,03 ± 0,26, mas é uma das duas contras de criatura). A ordem **entre 3, 4 e 5 não é separável estatisticamente** (ICs sobrepostos); é por papel.
- **O que o simulador acha barato mas NÃO é corte (Regra #5, o simulador não modela o oponente real):** Generous Patron (o Mothman mira até X criaturas de **qualquer** jogador e o Patron compra ao pôr contador em criatura que não é sua), Agatha's Soul Cauldron (exila criatura do cemitério que o Monument enche e dá contador + as habilidades dela), Tear Asunder e V.A.T.S. (as 2 remoções pontuais, a lacuna estrutural do §7 da auditoria), Didn't Say Please (contra qualquer mágica + mill 3: motor E1), Zellix (ΔT8 +0,05 ± 0,34: troca lateral, é o outro mill repetível), Bojuka Bog e Lantern (hate de cemitério que um deck de mill precisa porque entrega cemitério ao oponente).
- **Não verificado:** criaturas e tabuleiro de oponente; decks de oponente que usam o cemitério; a prioridade de conjuração do Monument (fixa em 57, sem sensibilidade); a ordem humana real das ativações além das 4 políticas; o pacote aplicado junto (só o Monument por cima); a pergunta aberta do Zellix (gatilho por jogador × por evento no mill simultâneo de 3 oponentes; sem ruling achada, o simulador conta 1 por evento).
- **Validação:** testes 157/157; bit-identidade 80.000/80.000 (`SWAPS=()` == `cd5d453`) e 32.444/32.444 (Monument fora de campo, `ACTIVATE` ligado × desligado), 0 divergências; regressão 20.000 × 2 modos × 3 variantes, 0 exceções; determinismo 3 `PYTHONHASHSEED` × 1.500 × 2 modos × 2 conjuntos de chaves, 0 divergências.
- **Método novo (`SWAP_IN_PLACE`, padrão `False`):** a carta que entra ocupa o lugar da que sai antes do embaralhamento: 79% das partidas ficam idênticas à base (com `remove+append`: 0%) e o IC95% cai cerca de 5×. A triagem de 84 cortes com `remove+append` (N = 2.000) ficou **SUPERADA** (arquivada, marcada).

#### Cortes: `Monument ← X` (N = 10.000 pareado, no lugar; diferença em PONTOS percentuais de partidas; `*` = excede o IC95%)

| # | corte (X) | mesa limpa T8 padrão | T8 resiliência | T10 padrão | T10 resiliência | contadores +1/+1 (padrão) | eu perco por deck-out (padrão) |
|---|---|---|---|---|---|---|---|
| 1 | An Offer You Can't Refuse | +1.00 ± 0.30 * | +0.42 ± 0.25 * | +0.13 ± 0.25 | -0.24 ± 0.34 | +0.86 ± 0.45 * | +0.08 ± 0.19 |
| 2 | Didn't Say Please | +0.98 ± 0.29 * | +0.44 ± 0.23 * | +0.46 ± 0.24 * | +0.75 ± 0.32 * | +0.71 ± 0.43 * | -0.03 ± 0.18 |
| 3 | Negate | +1.03 ± 0.28 * | +0.36 ± 0.24 * | +0.29 ± 0.24 * | +0.13 ± 0.32 | +0.73 ± 0.44 * | -0.12 ± 0.19 |
| 4 | Muldrotha, the Gravetide | +0.65 ± 0.36 * | +0.44 ± 0.30 * | -0.12 ± 0.30 | +0.20 ± 0.37 | +0.15 ± 0.57 | +0.34 ± 0.28 * |
| 5 | Tear Asunder | +0.52 ± 0.27 * | +0.28 ± 0.24 * | +0.00 ± 0.21 | +0.27 ± 0.30 | +0.23 ± 0.39 | +0.01 ± 0.17 |
| 6 | Generous Patron | +0.39 ± 0.31 * | +0.41 ± 0.26 * | -0.23 ± 0.26 | +0.19 ± 0.34 | +1.43 ± 0.49 * | +0.22 ± 0.21 * |
| 7 | Agatha's Soul Cauldron | +0.48 ± 0.28 * | +0.30 ± 0.24 * | +0.55 ± 0.25 * | +0.47 ± 0.32 * | +0.06 ± 0.46 | -0.25 ± 0.19 * |
| 8 | Nuclear Fallout | +0.60 ± 0.26 * | +0.18 ± 0.23 | +0.04 ± 0.21 | +0.18 ± 0.29 | +0.46 ± 0.40 * | -0.15 ± 0.17 |
| 9 | Toxic Deluge | +0.55 ± 0.25 * | +0.22 ± 0.24 | +0.30 ± 0.20 * | +0.24 ± 0.30 | +0.36 ± 0.35 * | -0.07 ± 0.15 |
| 10 | Arcane Denial | +0.61 ± 0.27 * | +0.03 ± 0.26 | +0.04 ± 0.24 | +0.07 ± 0.31 | -0.11 ± 0.45 | -0.05 ± 0.20 |
| 11 | Wave Goodbye | +0.43 ± 0.26 * | +0.19 ± 0.23 | +0.14 ± 0.19 | +0.24 ± 0.31 | +0.04 ± 0.38 | -0.06 ± 0.15 |
| 12 | Hedge Shredder | +0.38 ± 0.30 * | +0.21 ± 0.24 | -0.05 ± 0.23 | -0.19 ± 0.32 | +0.05 ± 0.41 | -0.12 ± 0.20 |
| 13 | Heroic Intervention | +0.43 ± 0.26 * | +0.13 ± 0.22 | +0.07 ± 0.20 | -0.26 ± 0.30 | +0.04 ± 0.37 | +0.01 ± 0.17 |
| 14 | Zellix, Sanity Flayer | +0.05 ± 0.34 | +0.36 ± 0.28 * | -0.25 ± 0.28 | +0.96 ± 0.39 * | -2.06 ± 0.54 * | +0.06 ± 0.23 |
| 15 | V.A.T.S. | +0.24 ± 0.26 | +0.09 ± 0.22 | +0.26 ± 0.21 * | +0.30 ± 0.31 | -0.10 ± 0.37 | -0.12 ± 0.16 |
| 16 | Bojuka Bog | +0.11 ± 0.44 | +0.20 ± 0.35 | -0.12 ± 0.37 | -0.19 ± 0.45 | -0.36 ± 0.60 | -0.38 ± 0.24 * |
| 17 | Yavimaya Hollow | +0.11 ± 0.43 | +0.14 ± 0.34 | -0.14 ± 0.36 | +0.08 ± 0.43 | -0.57 ± 0.59 | -0.07 ± 0.26 |
| 18 | Evolution Witness | +0.21 ± 0.30 | +0.02 ± 0.26 | +0.06 ± 0.24 | -0.20 ± 0.35 | +0.12 ± 0.47 | -0.12 ± 0.19 |
| 19 | Cold-Eyed Selkie | +0.13 ± 0.26 | -0.04 ± 0.23 | -0.09 ± 0.22 | -0.21 ± 0.31 | -0.76 ± 0.40 * | -0.14 ± 0.17 |
| 20 | Soul-Guide Lantern | +0.12 ± 0.31 | -0.08 ± 0.27 | -0.24 ± 0.25 | -0.03 ± 0.35 | -0.45 ± 0.47 | -0.05 ± 0.19 |

#### Sensibilidades do próprio Monument (plataforma `Monument ← Negate`)

| variante | T8 padrão | T8 resiliência | T10 padrão | cartas milladas dos oponentes (padrão) | tap/partida | Exhaust/partida |
|---|---|---|---|---|---|---|
| padrão (Negate) | +1.03 ± 0.28 * | +0.36 ± 0.24 * | +0.29 ± 0.24 * | +1.94 ± 0.39 * | 0.324 | 0.031 |
| sens_sem_ativar | +0.02 ± 0.21 | -0.20 ± 0.21 | +0.05 ± 0.22 | -0.14 ± 0.32 | 0.000 | 0.000 |
| sens_exhaust_so_letal | +0.97 ± 0.28 * | +0.33 ± 0.24 * | +0.29 ± 0.24 * | +1.23 ± 0.37 * | 0.350 | 0.006 |
| sens_exhaust_12 | +1.01 ± 0.29 * | +0.38 ± 0.24 * | +0.27 ± 0.24 * | +2.04 ± 0.39 * | 0.308 | 0.047 |
| sens_exhaust_48 | +0.98 ± 0.28 * | +0.32 ± 0.24 * | +0.29 ± 0.24 * | +1.45 ± 0.38 * | 0.345 | 0.011 |
| sens_eu_tambem | +1.31 ± 0.33 * | +0.48 ± 0.26 * | +0.30 ± 0.26 * | +1.78 ± 0.42 * | 0.324 | 0.028 |
| sens_tap_primeiro | +0.64 ± 0.29 * | +0.24 ± 0.24 | +0.36 ± 0.25 * | +3.47 ± 0.43 * | 0.419 | 0.089 |
| sens_fim_do_oponente | +1.03 ± 0.28 * | +0.38 ± 0.24 * | +0.30 ± 0.24 * | +2.13 ± 0.40 * | 0.359 | 0.032 |
| sens_otimista | +0.40 ± 0.30 * | +0.11 ± 0.25 | +0.35 ± 0.25 * | +3.49 ± 0.43 * | 0.408 | 0.125 |

#### Monument sobre o pacote de 5 trocas + Master ← Negate (pendente; base = o pacote; N = 10.000)

| corte (Monument entra) | T8 padrão | T8 resiliência | T10 padrão | cartas milladas dos oponentes (padrão) |
|---|---|---|---|---|
| Muldrotha, the Gravetide | +0.87 ± 0.35 * | +0.40 ± 0.30 * | +0.11 ± 0.29 | +2.52 ± 0.50 * |
| Toxic Deluge | +0.53 ± 0.23 * | +0.48 ± 0.24 * | +0.20 ± 0.19 * | +1.43 ± 0.36 * |
| Arcane Denial | +0.79 ± 0.29 * | +0.25 ± 0.27 | +0.04 ± 0.23 | +1.82 ± 0.44 * |
| Wave Goodbye | +0.63 ± 0.25 * | +0.31 ± 0.24 * | +0.15 ± 0.18 | +1.15 ± 0.38 * |
| Nuclear Fallout | +0.66 ± 0.24 * | +0.28 ± 0.23 * | +0.01 ± 0.18 | +1.69 ± 0.40 * |
| V.A.T.S. | +0.30 ± 0.26 * | +0.16 ± 0.22 | +0.19 ± 0.20 | +1.43 ± 0.38 * |

