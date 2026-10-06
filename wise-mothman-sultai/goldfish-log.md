# The Wise Mothman — log do goldfish (simulador `mothman_goldfish_v1.py`)

> **Dados brutos, scripts e como refazer cada tabela:** `resultados-ab/2026-10-05-ab-pacote-kozilek-master/` (pacote, Master, Kozilek, controles) · `resultados-ab/2026-10-05-ab-kozilek-self-deck/` (Kozilek × estilo de jogo) · `resultados-ab/2026-10-05-simulador-v1-validacao/` (testes, varreduras, determinismo, regressão).
> Auditoria cláusula-a-cláusula: `checklist-oraculo.md`. Simulador no commit `91b1a3d` (código congelado durante as baterias).
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
