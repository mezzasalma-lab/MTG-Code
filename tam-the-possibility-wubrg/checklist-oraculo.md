# Tam, the Possibility (WUBRG) — checklist de oráculo do simulador `tam_goldfish_v1.py`

Construído em 2026-10-19 a pedido direto (*"crie o simulador do deck e primeiro rode as simulações para ver como o deck assim roda!"*). A lista simulada é a `lista.md` **como está** (99 cartas + Tam na zona de comando); nenhuma troca foi aplicada.

## Método (CLAUDE.md Regras #1, #3, #7) e o que cada passo cobre

1. **Oráculo e rulings ao vivo, não de memória.** Texto de cada carta: `tam_cartas.json` (recorte de `scryfall-cache/oracle-cache.json`; custo, tipos, P/T e lealdade vêm só dele). Rulings: `resultados-ab/2026-10-19-simulador-baseline/dados/rulings_deck.json` (campo `rulings_uri` do Scryfall; 427 linhas lidas por inteiro, conferidas na seção "Rulings" abaixo).
2. **Arquivo `.py` lido inteiro** (5.300 linhas) e comparado cláusula a cláusula com o oráculo: ✅ já certo, 🐛 corrigido nesta rodada, 📊 estrutural (cláusula citada).
3. **Teste dirigido por cláusula:** `testes/` (`python3 testes/rodar_testes.py`): 146 testes, cada um monta um `GameState` determinístico e confirma que a cláusula dispara de verdade (efeito, custo, limite de ativação, fase). Cada correção abaixo tem teste. Só o achado 5 (Ajani, Cadet em dobro) foi **pego pelo teste** (falhou antes de eu corrigir); nos demais o teste foi escrito junto da correção, sem rodar contra a versão antiga, então prova que o comportamento certo existe agora, não que o errado existia.
4. **Varreduras de classe sistêmica (Regra #10):** ver "Escopo" no fim.

## Achados desta rodada (todos corrigidos antes de qualquer número de baseline)

| # | achado | classe da taxonomia | correção | teste |
|---|---|---|---|---|
| 1 | Dihada +2 só dava indestrutível: faltavam **vigilância** e **lifelink**, e o alvo era o 1º legendário da lista | cláusula extra ignorada | `dihada_target` + vigilância (não vira o atacante) + lifelink vira vida no combate | `Dihada +2` |
| 2 | Emblema da Tamiyo (−7) "cast spells from your hand without paying mana costs": só guardava o emblema | habilidade nunca lida | `cast_cost_option(zone)`: da MÃO custa 0; Tam (zona de comando), Wrenn (cemitério) e Chandra (exílio) pagam | `Emblema da Tamiyo` |
| 3 | Staff of Compleation: faltava `{5}: Untap` | cláusula extra ignorada | `act_staff` desvira com mana ociosa e repete proliferate/compra | `Staff of Compleation` |
| 4 | Eternal Wanderer −4: **eu** escolho a criatura que fica de cada jogador, o código deixava a MELHOR do oponente | leitura de cláusula | fica a mais fraca dos oponentes | `Eternal Wanderer 0/-4` |
| 5 | Ajani Unrelenting: o Cadet criado pela +1 recebia o bônus **duas vezes** (no gatilho e na resolução) | contagem em dois pontos | só a resolução da +1 aplica (ruling 2026-08-21) | `Ajani` (pego pelo teste) |
| 6 | Domri +1: o `riot` nunca era consumido | habilidade nunca lida | mana da Domri é rastreado (`riot_pool`); criatura paga com ele ganha +1/+1 (dispara All Will Be One) ou haste (mana-dork e criatura de poder ≥ 5) | `Domri riot` |
| 7 | Garruk VB: faltava o estático "if a creature an opponent controls would die, exile it instead", e o +2 (−4/−1) era modelado como "congelar" | cláusula extra / fórmula achatada | oponente exilado não vai pro cemitério dele (afeta o −8 da Liliana's Talent); −4/−1 de verdade (restaura no meu upkeep; resistência 1 morre) | `Garruk VB +2/-2` |
| 8 | Garruk VB −2: eu só sacrificava se tivesse ficha, mas "**each player** sacrifices" me obriga | leitura de cláusula | sacrifico a criatura de menor valor (ficha primeiro); a IA só escolhe se isso não custa a Tam | `Garruk VB -2` |
| 9 | Ajani −3 podia matar a **Tam** (2/4 leva 4 de dano) de graça | efeito colateral no conceito "criatura minha" | a IA conta a Tam entre as perdas | `Ajani -3 nao e' escolhido...` |
| 10 | Rebound da Narset (−2): armava com qualquer magia, mas o oráculo diz "**from your hand**" | cláusula | `state.cast_zone`: só da mão consome | `Narset -2 ... da mao` |
| 11 | Leyline Immersion: **ward {2}** nunca cobrado contra a remoção do oponente | cláusula extra | oponente precisa de ≥ 4 terrenos (premissa `WARD_MIN_LANDS`) | `Leyline Immersion` |
| 12 | Vronos −7: o Construct não tinha **vigilância** | cláusula | `ctr["vigilance"]` | `Vronos` |
| 13 | Tamiyo +1: criatura marcada que **bloqueia** e dá dano de combate não comprava (o efeito dura até o meu próximo turno) | timing de fase | compra no combate do oponente | `Tamiyo +1` |
| 14 | **Ordem do turno do oponente (Regra #6):** o ataque dele rodava ANTES da rolagem do gate de atenção (usava a rolagem do oponente anterior); o wipe de criatura não limpava os outros oponentes; Dihada/Plaza não protegiam do wipe | orquestração de turno | `try_smart_opponent_turn`: gate → wipe → combate → wipe de cemitério → remoção → descarte (igual ao Prismatic Bridge); wipe simétrico; Dihada e Plaza | `Ordem das fases`, `Eternal Wanderer limite de ataque` |
| 15 | Turno extra do Ichormoon Gauntlet não contava no orçamento de turnos | convenção do repositório | conta (como no Prismatic) | `Gauntlet -12 ... turno extra` |
| 16 | `lose_life` encerrava a partida com vida ≤ 0: truncava toda métrica de mesa (derrota minha em 50% das partidas de resiliência, número **sem** significado) | convenção do repositório | só marca `died_turn`; a partida continua (Prismatic/Mothman) | `Vida <= 0 so' MARCA` |
| 17 | **Rulings** (seção abaixo): Liliana's Talent matava atacante **bloqueado**; Tamiyo não mirava criatura de oponente; Oko deixava o Elk como artefato; Saheeli copiava P/T com contadores; Peacemaker só via a remoção como crime; Vronos −7 excluía artefato-criatura; Tezzeret −5 excluía artefato-criatura e Aminatou −6 nem tinha efeito | leitura de ruling | corrigidos | `t_rulings.py` |
| 18 | **Mana fantasma:** com o Chromatic Orrery (ou Oath of Nissa pra planeswalker) em campo, pagar com mana FLUTUANTE descontava a chave `A` em vez da chave real: o `{C}` nunca saía do pool e `A` ia a −119 | mecânica de motor (custo nunca deduzido) | a unidade de pool carrega a chave de origem (`KS.key`); `pay_mana` levanta erro se o pool ficar negativo | `Mana flutuante com o Chromatic Orrery...`, `Invariante: o pool nunca fica negativo` (confirmado: o código antigo dá `{'C': 5, 'A': -3}`) |
| 19 | O mana flutuante só esvaziava no upkeep (sobrava do main 1 pro main 2 e pro turno dos oponentes) | orquestração de turno (Regra #6) | `empty_pool` no fim de cada main, no combate e no end step (CR 500.4) | `O mana flutuante some no fim de cada fase` |
| 20 | Kasmina `-8` deixava a magia no exílio E no cemitério (a invariante "carta acima do baralho" disparou em 25% das partidas padrão); o `-8` ignorava anulação de magia | conservação de cartas | sai do exílio ao ser conjurada; `counterspell_check` | `Conservacao de cartas...`, `conservacao.py` 20.000 × 2 |
| 21 | Impulso da Chandra (`0`) não jogado sumia do jogo, e magia de permanente do impulso podia sair no end step | zona / timing | sobra vai pro exílio; só conjura no main | `Conservacao de cartas...` |
| 22 | **Laços infinitos reais** do deck (Orrery + Tezzeret + Chain Veil; Wrenn + Gauntlet) travavam a simulação (partidas de minutos, lealdade 1.543) | motor sem teto | tetos declarados: 80 ativações de lealdade e 60 magias por turno, contados em `m_turn_cap_*` (apertaram em 0,39% das partidas padrão e 0,07% da resiliência) | `orquestracao/scan_slow.py` (4.000 sementes × 2 modos sem partida > 8 s, medido numa versão anterior às últimas correções; a regressão final de 20.000 × 2 terminou em ~10 min sem partida travada) |
| 23 | Métricas por turno (T8/T10) contavam partida já encerrada (mesa limpa) como 0: `pws_T10` (2,26) saía abaixo de `pws_T8` (4,67) | viés de métrica | `finalize` carrega adiante o último valor registrado | conferido: `pws_T10` 6,58 > `pws_T8` 5,41 |
| 24 | Compra no 1º turno | convenção | `FIRST_TURN_SKIPS_DRAW = False` | `Commander multijogador: NINGUEM pula a compra do 1o turno` |
| 25 | **Saheeli −2 só copiava P/T de criatura**: a metade "target artifact becomes a copy of another target **artifact** or creature" não existia (goldfish manual #2, T6: o Servo copia o Fellwar Stone e paga o Teferi) | implementação parcial (Regra #1/#5) | `SAHEELI_COPY_MANA_ARTIFACT`: cópia de Sol Ring / Arcane Signet / Fellwar Stone (não lendários) num Servo/Food desvirado, só se uma carta da mão passa a caber (ensaio a seco) | `t_manual2.py` (3 testes); bit-identidade 20.000 × 2 |
| 26 | **A Tam nunca atacava** (`NON_ATTACKERS`): o usuário ataca com ela quando não ativa (goldfish #2) e a Tamiyo `+1` precisa de uma criatura marcada que conecte | diferença de política que é linha de jogo real (Regra #5), não convenção | `TAM_ATTACKS`: ataca se `tam_activation_check` = 0 (sem `{W}{U}{B}{R}{G}`, X < 2 ou poucos alvos); na resiliência só se nenhum oponente tem criatura com poder; fica virada (CR 508.1) | `TAM_ATTACKS` (6 testes) |
| 27 | `best_blink_target` **nunca piscava permanente de mana virado** (Aminatou `−1` e Displacer Kitten), mas o usuário o fez (goldfish #2, T7) | linha de jogo real ausente | `BLINK_UNTAP_MANA`: ensaio a seco `blink_unlock_options` (só pisca se uma carta valiosa da mão passa a caber); terreno entra pelo ponto de entrada de terreno (choque paga 2 de vida); criatura volta com doença de invocação (excluída); Kitten só mira "nonland permanent" | `BLINK_UNTAP_MANA` (5 testes) |
| 28 | Saheeli `−2` **não copiava habilidades de CRIATURA** (Birds, Bloom Tender, Faeburrow Elder, Hierarchs) nem usava o Flux Channeler / Displacer Kitten copiados (gatilho duplicado) nem o Staff of Compleation | implementação parcial (cláusula "or creature") | `SAHEELI_COPY_CREATURES`: `saheeli_mana_choices`, `saheeli_trigger_wanted`, `saheeli_staff_wanted`; gatilhos leem `perms_eff`/`count_eff`; lendárias (Tam, Kiora) nunca; Servo copiando criatura tem doença de invocação | `SAHEELI_COPY_CREATURES` (5 testes) |
| 29 | **Turnos extras eram um booleano**: duas ativações do `−12` da Ichormoon Gauntlet no mesmo turno rendiam 1 turno extra (goldfish #5, T11: 4 turnos extras, 2 deles no mesmo turno) | contador acumulado lido como flag (Regra #1, taxonomia) | `EXTRA_TURNS_STACK`: `extra_turns_queued` é um contador consumido por `play_rounds` | `EXTRA_TURNS_STACK` |
| 30 | **Ordem de pagamento do mana (classe nova, não é carta):** o Bloom Tender / Faeburrow Elder (1 mana por COR entre meus permanentes) era tocado antes de a magia trazer a cor nova, e o genérico tocava outra fonte em vez da 2ª unidade de uma fonte já tocada (filtro Fire-Lit Thicket, Sol Ring) | mecânica de motor (Regra #10: o erro mora no motor, não na carta) | `VIVID_LAST` (adia o vivid se a magia traz cor nova e as outras fontes pagam) + `SIBLING_FIRST` (genérico sai primeiro do pool e da unidade irmã) | `VIVID_LAST`, `SIBLING_FIRST` |
| 31 | O combo Orrery + Tezzeret + Chain Veil só fechava com o pagamento **já em campo**; com All Will Be One / Sanctum Lurker **na mão**, só registrava a montagem (piso do valor da peça no A/B, Regra #4 adendo 3) | implementação parcial / orquestração | `COMBO_CAST_PAYOFF_FROM_HAND`: conjura o pagamento da mão com o mana infinito | `COMBO_CAST_PAYOFF_FROM_HAND` |
| 32 | (**não é erro de oráculo; é calibração**) a resiliência era a do Prismatic Bridge, 8,5 criaturas de oponente em campo no T5–T10 e 9,1 interações por partida, contra 1–2 criaturas e 3,8 interações nos 5 logs do usuário | convenção não calibrada (Regra #5) | `OPP_PLAYTESTER` + `OPP_CARD_MIX` (+ `aplica_perfil("playtester")`), desligados por padrão | `OPP_PLAYTESTER`, `OPP_CARD_MIX`; `resultados-ab/2026-10-22-calibracao-playtester/` |

## Legenda por carta

✅ implementado e testado · 🐛 corrigido nesta rodada (número acima) · 📊 estrutural (a cláusula está citada; o motivo é estado de OPONENTE real que o goldfish não modela; vira **métrica proxy** `interaction_plays`/`proxy_*` quando `OPP_TARGET_PROB` diz que existe alvo, ou efeito real no modo de resiliência).

## Terrenos (36)

| carta | cláusulas do oráculo | status |
|---|---|---|
| Baxter Building | `{T}: {C}`; `{4},{T}`: 4 mana de qualquer cor; `{4},{T}`: comprar 1 se controlo criatura de resistência ≥ 4 | ✅ conversor (fixa cor, 0 líquido), compra só com Tam 2/4, Whale 7/5, Fera 4/4, Kiora 2/4, Onakke 0/4 etc. (`toughness()`) |
| Boseiju, Who Endures | `{T}: {G}`; canal `{1}{G}` (−1 por criatura lendária) | ✅ canal com ≥ 7 terrenos; alvo "artifact, enchantment, or nonbasic land an opponent controls" = 📊 proxy |
| Bountiful Promenade, Rejuvenating Springs, Spire Garden, Undergrowth Stadium | entra virado a menos que haja 2+ oponentes (conta os de AGORA, ruling 2018/2020) | ✅ `alive_opps` |
| Breeding Pool, Hallowed Fountain, Overgrown Tomb, Steam Vents, Stomping Ground, Temple Garden, Watery Grave | choque: 2 de vida ou entra virado (se um efeito põe virado, ainda pode pagar mas continua virado) | ✅ paga com vida ≥ 10; testado nos 7 |
| City of Brass | 1 de dano ao ficar virada; `{T}`: qualquer cor | ✅ dano pago no `pay_mana` |
| Command Tower, Arcane Signet | qualquer cor da identidade (WUBRG = todas) | ✅ |
| Exotic Orchard, Fellwar Stone | qualquer cor que um terreno de OPONENTE possa produzir (nunca incolor, ruling) | ✅ `Opp.land_colors` |
| Fire-Lit Thicket, Flooded Grove, Twilight Mire, Wooded Bastion | `{T}: {C}`; `{X/Y},{T}`: dois mana nas duas cores | ✅ conversor (usa 1 mana de entrada da cor, entrega 2) |
| Great Hall of the Citadel | `{T}: {C}`; `{1},{T}`: 2 mana de qualquer cor **só pra magia lendária** | ✅ restrição por `Ctx.legendary` (todo planeswalker e Way é lendário) |
| Indatha, Jetmir's, Ketria, Spara's, Zagoth (triomes) | entra virado; ciclo `{3}` | ✅ + `act_cycle_triome` |
| Misty Rainforest, Verdant Catacombs, Windswept Heath, Wooded Foothills | `{T}`, 1 de vida, sacrifica: busca por SUBTIPO, entra desvirado, embaralha | ✅ (alvos 12/10/10/10 conferidos); a Yavimaya **não** faz carta da biblioteca virar Forest (ruling 2021-06-18) |
| Mossfire Valley, Overflowing Basin | `{1},{T}`: `{R}{G}` / `{G}{U}` | ✅ |
| Plaza of Heroes | `{T}: {C}`; qualquer cor só pra lendária; cor entre meus lendários; `{3},{T}`, exila: hexproof+indestrutível pra lendária | ✅ as 4 cláusulas (a 4ª protege a Tam de remoção/wipe no modo de resiliência) |
| Starting Town | entra virado a partir do 4º turno; `{T}`, 1 de vida: qualquer cor | ✅ |
| The World Tree | entra virado; `{G}`; com 6+ terrenos qualquer cor; `{W}{W}{U}{U}{B}{B}{R}{R}{G}{G}`... busca "any number of God cards" | ✅ as 3 primeiras; a 4ª: 📊 **0 cartas God na lista** ("Search your library for any number of God cards": nada a buscar) |
| Yavimaya, Cradle of Growth | todo terreno é Forest | ✅ todo terreno em campo toca `{G}`, conta pro Nissa −7 |

## Ramp e mana (16)

| carta | status |
|---|---|
| Sol Ring `{C}{C}`; Birds (voo, qualquer cor); Noble Hierarch (GWU, exalted); Ignoble Hierarch (BRG, exalted); Bloom Tender (vivid: 1 mana por cor entre permanentes, só W U B R G); Faeburrow Elder (vigilância, +1/+1 por cor, mesmo mana) | ✅ (doença de invocação bloqueia o `{T}`; exalted só atacando sozinho) |
| Chromatic Orrery `{C}x5`, gasta como qualquer cor, `{5},{T}`: compra 1 por cor | ✅ |
| Leyline Immersion (enchant legendary creature; ward {2}; `{T}`: 5 mana de qualquer cor, só pra magia) | ✅ 🐛11; hospedeiros: Tam, Kiora, Boo |
| Way of the Paradox / Pyromancer | ✅ |
| Chandra, Legacy of Fire | ✅ end step X dano; +1; 0 (impulso jogável) |
| Domri, Chaos Bringer | ✅ 🐛6 |
| Garruk Wildspeaker | ✅ |
| Wrenn and Realmbreaker | ✅ estático (terrenos qualquer cor), +1, −2 (mill 3, 1 permanente), −7 (emblema: terreno e permanente do cemitério) |

## Compra, remoção, proliferate, fichas, proteção, blink, tutores

Cada uma das cartas abaixo tem ao menos um teste por cláusula em `testes/` (arquivo e nome do teste batem com o nome da carta):

Dack Fayden (+1 ✅; −2 📊 "Gain control of target artifact"; −6 📊 emblema: **nenhuma magia da lista mira permanente de oponente**, as Auras miram o meu), Dihada (🐛1; −11 efeito real no modo de resiliência, proxy no padrão), Garruk Curse Breaker (estático + 3 habilidades ✅), Minsc & Boo (ETB/upkeep Boo, +1, −2 com compra ✅), Narset Transcendent (🐛10; −9 ✅ efeito medido: oponente sem magia não-criatura), Oath of Nissa ✅, Professor Dellian Fel ✅, Tamiyo (🐛2 🐛13), Teferi Hero (emblema: exila alvo de oponente a cada compra, real na resiliência) ✅, Teferi Temporal Archmage (emblema: 1 ativação por PW por turno de oponente) ✅, Way of the Mind Sculptor ✅, All Will Be One ✅ (um gatilho por EVENTO), Blasphemous Act ✅, Garruk Veiled Butcher (🐛7 🐛8; −3: 70% de eu comprar = 📊 mão de oponente não modelada), Nissa Ascended Animist ✅ (X fixo na resolução; Compleated), Oko ✅ (🐛17), Overwrite the Multiverse ✅, Promise of Loyalty ✅ (aproximação: o oponente mantém 1 criatura neutralizada), The Eternal Wanderer (🐛4; estático "no more than one creature can attack" ✅), Way of the Warlord ✅, Dreamtide Whale ✅, Flux Channeler ✅, Ichormoon Gauntlet ✅ (🐛15), Patrolling Peacemaker ✅ (🐛17), Staff of Compleation ✅ (🐛3), Teferi's Talent / Liliana's Talent ✅ (🐛17), The Chain Veil ✅, Vraska ✅, Way of the Necromancer ✅, Ajani Unrelenting (🐛5, 🐛9), Elspeth Sun's Champion ✅, Kasmina ✅, Kiora of Salt and Sand ✅, Saheeli ✅ (🐛17), Way of the Deathbringer / Healer / Wildspeaker ✅, Onakke Oathkeeper ✅, Ripples of Potential ✅, Sanctum Lurker ✅, Vronos (🐛12, 🐛17), Aminatou (🐛17; +1/−1 ✅; −6 efeito real só na resiliência, ver abaixo), Displacer Kitten ✅, Oath of Teferi ✅, Entrust the Spark ✅, Tezzeret the Seeker (🐛17), **Tam** ✅ (desconto só no genérico, imposto +2 por conjuração, `{W}{U}{B}{R}{G},{T}` X vezes onde X = tipos distintos: Jace token é Jace, The Eternal Wanderer não tem tipo).

**Aminatou −6** (não é "estrutural": é política, e está implementado): no modo padrão os oponentes não têm permanentes simulados, então trocar só entrega o meu campo; no modo de resiliência o efeito é real (o oponente recebe meus permanentes não-terreno menos a Aminatou; eu recebo as criaturas dele como fichas do mesmo P/T) e a IA só escolhe quando o tabuleiro dele vale ≥ 2,5× o meu + 16.

## Rulings do Scryfall conferidas (427 linhas lidas)

| carta | ruling | código |
|---|---|---|
| Tam | X só é determinado uma vez; proliferate várias vezes; custo total = custo + aumentos − reduções | ✅ `act_tam_proliferate`, `effective_cost` |
| Yavimaya | cartas na biblioteca não são Forest | ✅ `fetch_targets`; errata em `auditoria.md`, `avaliacao-moxfield.md` e `resultados-ab/2026-10-19-registro/LEIAME.md` |
| Domri | riot é substituição; sem contador possível → haste; haste vale pra sempre | ✅ 🐛6 |
| Garruk W | +3/+3 só nas criaturas de quando resolve | ✅ |
| Nissa | X fixo na resolução; bônus do −7 só nas criaturas de quando resolve; Compleated | ✅ |
| Oko | Elk perde os outros tipos (deixa de ser artefato) | ✅ 🐛17 |
| Tamiyo | pode mirar criatura de oponente (eu compro); gatilho vale se ela sair | ✅ 🐛17 |
| Teferi H | os 2 terrenos são escolhidos só no end step | ✅ |
| Teferi TA | emblema: 1 ativação por PW por turno de oponente (+ Chain Veil) | ✅ (Veil + emblema: ver "não varrido") |
| Way of the Mind Sculptor | compro antes da habilidade resolver | ✅ |
| Flux Channeler / Saheeli | gatilho resolve antes da magia, mesmo anulada | ✅ (`on_cast` antes de `counterspell_check`) |
| Saheeli | copia valores impressos | ✅ 🐛17 |
| Ajani | o token entra antes da habilidade resolver e recebe o bônus da +1 | ✅ 🐛5 |
| Kasmina | outros PWs ganham as habilidades; −8 busca cor do PW que ativou | ✅ |
| Liliana's Talent | qualquer dano de criatura no encantado destrói a criatura | ✅ combate (🐛17); dano não-combate de criatura: 📊 não modelado |
| Chain Veil | vale pra PWs que entram depois; cada resolução soma uma ativação | ✅ |
| Sanctum Lurker | PW com 0 fica; pode ativar `[0]` e `[+N]` | ✅ |
| Vronos | fase fora/dentro; −7 em artefato já criatura; ataca no mesmo turno se já estava em campo | ✅ 🐛17 |
| Tezzeret | afeta todos os artefatos, sobrescreve P/T anterior | ✅ 🐛17 |
| Eternal Wanderer | sem tipo; retorna no end step; ficha some; −4 não mira | ✅ 🐛4 |
| Peacemaker | crime = mirar oponente/permanente/magia/cemitério | ✅ 🐛17 |
| Ripples | fase dentro no untap, sem gatilho de entrada | ✅ |
| Vraska | veneno até 9; Compleated | ✅ |
| Empower Jace (todas as Ways) | não cria 2ª ficha de Jace | ✅ |

## Conceitos compartilhados (Regra #3), enumerados por script

`pw_types()` (X da Tam): 25 planeswalkers, **21 tipos distintos** (teste `Tipos de planeswalker da lista`), Jace token = Jace, Eternal Wanderer = 0. `is_legendary()` (Great Hall, Plaza, Dihada, Boseiju, Immersion): Tam, Kiora, Boo, os 25 PWs, 8 Ways, Chain Veil, Orrery. `colors_among()` (Bloom Tender, Faeburrow Elder, Orrery): só W U B R G; fichas coloridas contam; terreno é incolor. `is_artifact()` (Vronos, Tezzeret, Saheeli): Peacemaker e Servo são artefato-criatura; Elk de Oko não. `noncreature spell` (Flux, Gauntlet, Saheeli, Kitten): Peacemaker é criatura. Resistência ≥ 4 (Baxter): `toughness()` (Tam, Kiora, Whale, Onakke, tokens 4/4 e 8/8).

## Premissas e convenções declaradas (não são ausência de checagem)

- **Cores dos terrenos de oponente (decidido pelo usuário em 2026-10-21: *"Decida os terrenos dos oponentes de forma aleatória"*):** aleatórias por semente (identidade de 2 cores por oponente; cada terreno produz uma delas); a Exotic Orchard e o Fellwar Stone só produzem cores de terreno de oponente em campo (P({G}) no início do T2 = 40,9%, T3 = 58,5%). Medição e limites: `resultados-ab/2026-10-21-cores-terrenos-oponentes/LEIAME.md`.

Mesa de 4 (3 oponentes, 40 de vida); no modo padrão os oponentes são passivos e **todo atacante conecta**; **compra no T1** (Commander multijogador: ninguém pula a compra do 1º turno; o simulador pulava por eu ter herdado o `on_play` do Mothman, e o usuário corrigiu em 2026-10-19; chave `FIRST_TURN_SKIPS_DRAW = False`); `OPP_TARGET_PROB = 0.7` a partir do T3; crime por magia de oponente `OPP_CRIME_PROB_PER_NONCREATURE_SPELL = 0.25` (padrão); resiliência = o modelo do Prismatic Bridge (arquétipos go-wide / voltron / low, gate de atenção 1/3, remoção/wipe/descarte/anulação de magia/wipe de cemitério), com `WARD_MIN_LANDS = 4` e a remoção mirando a Tam em 15% das vezes.

## Escopo (Regra #7): o que foi e o que NÃO foi varrido

**Varrido, com método:** leitura integral do `.py`; cláusula a cláusula das 100 cartas contra o oráculo; as 427 linhas de rulings; 146 testes dirigidos (terrenos, mana, custos, 25 PWs, Ways, permanentes, motor, rulings, as 9 jogadas do goldfish manual); smoke (99 cartas, 0 desconhecidas, 0 duplicadas, 0 exceções em 200 × 2 modos); varredura AST de iteração de `set` (4 candidatos no Tam, todos sem ordem relevante: `len`, contagem comutativa e `any`); determinismo entre `PYTHONHASHSEED` e regressão (números nos arquivos de `resultados-ab/2026-10-19-simulador-baseline/`).

**NÃO varrido neste arquivo:** interação do emblema do Teferi TA com a Chain Veil (ativações extras no turno do oponente); dano de criatura que não é de combate na Liliana's Talent; Oath of Teferi / Eternal Wanderer em Aura (nenhuma carta da lista é Aura exilável além das Talents e da Immersion, que caem do PW/criatura); cópia de habilidades de CRIATURA pela Saheeli (a cópia de criatura só pega P/T; a de artefato de mana está coberta desde 2026-10-21, achado 25); "whenever you cast" fora da mão está coberto só pelos testes da Tamiyo/Narset/Chandra; combinações de condições de entrada de terreno; estado de oponente real (convenção do repositório).

## Rodada 2026-10-21: goldfish manual #2 (Saheeli −2 como cópia de artefato de mana)

Pasta: `resultados-ab/2026-10-21-saheeli-copia-de-artefato/`. **Cláusula:** *"−2: Target artifact you control becomes a copy of another target artifact or creature you control until end of turn, except it's an artifact in addition to its other types."* Antes: só a metade "creature" (P/T). **Agora:** a metade "artifact" para os artefatos de mana não lendários (Sol Ring, Arcane Signet, Fellwar Stone; Orrery e Chain Veil são `Legendary Artifact`: a cópia violaria a regra da lenda).
**Rulings** (8, `resultados-ab/2026-10-19-simulador-baseline/dados/rulings_deck.json`), conferidas contra o código **depois** de escrevê-lo (não antes: falha de processo da Regra #3, sem contradição achada): gatilho da Saheeli resolve antes da magia ✅ (já existia); copia valores IMPRESSOS + efeitos de cópia, sem contadores ✅; é artefato além dos tipos copiados ✅; copiar quem copia outra coisa vira o original ✅ (só copio cartas em campo); efeito já aplicado continua ✅ (n/a); **doença de invocação só se o alvo virar criatura no turno em que entra ✅** (a cópia de artefato de mana não é criatura, então o Servo recém-criado já paga); Equipment (2 rulings) n/a (a lista não tem Equipment).
**Não coberto:** cópia de habilidades de criatura (Birds, Bloom Tender, Flux Channeler, Displacer Kitten); Staff of Compleation; alvo que não seja Servo/Food; a política (usar a cópia só quando uma carta valiosa da mão passa a caber).
**Testes:** 182/182 (146 anteriores; `t_manual2.py` 16; `t_manual3.py` 9; `t_manual4.py` 11). **Diferenças de política com o goldfish do usuário (não alteradas):** a Tam nunca ataca (`NON_ATTACKERS`); `best_blink_target` nunca pisca rocha de mana virada.

**Status (2026-10-21, goldfish manual #4):** 11 testes novos (`t_manual4.py`), nenhum achado de regra no simulador. Cláusulas re-conferidas contra o oráculo do Scryfall no processo: Nissa Ascended Animist (compleated: cada `{G/P}` pago com vida tira 2 de lealdade), Teferi, Temporal Archmage (`+1` olha 2: 1 na mão, 1 no fundo; `−1` desvira 4; `−10` emblema), Ajani Unrelenting (o gatilho de Cadet resolve antes do `−2`), Garruk, Veiled Butcher, Ichormoon Gauntlet (`0: Proliferate`, `−12` turno extra, gatilho de contador adicional), Split Up (carta de oponente), Vex (carta de oponente; gravada no cache, Regra 15).

## Rodadas 2026-10-22: Tam atacando, piscar de mana virado, Saheeli (criatura/Staff), rodada 2 de motor e perfil `playtester`

Pastas: `resultados-ab/2026-10-22-politicas-tam/` (rodada 1), `resultados-ab/2026-10-22-rodada2-motor-e-perfil/` (rodada 2), `resultados-ab/2026-10-22-calibracao-playtester/`, `resultados-ab/2026-10-21-goldfish-manual-5/`. **Achados 26 a 32** (tabela acima). Origem: goldfish manuais #2, #3 e #5 do usuário e o pedido "Termine tudo que falta!".

**Rulings lidas (Scryfall, 2026-10-22, `resultados-ab/2026-10-22-rodada2-motor-e-perfil/dados/scryfall_rulings_2026-10-22.json`)**, conferidas contra o código **depois** de escrevê-lo (falha de processo da Regra #3 declarada, sem contradição achada):
- **Ichormoon Gauntlet** (1 ruling, 2023-02-04): *"Only one loyalty ability of each planeswalker may be activated per turn, no matter how many it has gained."* ✅ já limitado por `activated_loyalty_this_turn`; os 4 turnos extras do #5 T11 vêm de planeswalkers diferentes ativando o `−12`, 2 deles no mesmo turno. Não há ruling de empilhamento: vem do texto do oráculo.
- **Bloom Tender** (5 rulings, 2025-11-17): terreno é incolor; não produz incolor; confere-se cada uma das 5 cores e o mesmo permanente conta para várias; no máximo 1 de cada cor ✅ (`colors_among()` já fazia).
- **Faeburrow Elder** (2 rulings, 2019-10-04): no máximo +5/+5 e 5 mana; sendo verde e branca rende no mínimo {G}{W} ✅.
- **Vex**: sem rulings (oráculo no cache).

**Testes:** 220 passam, 0 falham (182 anteriores + 17 de `t_politicas.py` rodada 1 + 15 de `t_manual5.py` + 6 da rodada 2). **Smoke:** 99 cartas, 0 desconhecidas, 0 duplicadas, 0 exceções em 200 × 2 modos × 2 versões. **Regressão 20.000 × 2 modos** (`depois` e chaves desligadas): 0 exceções, 0 carta acima do baralho, 0 campo negativo. **Bit-identidade** com as chaves desligadas contra o snapshot anterior: 20.000 / 20.000 por modo, nas duas rodadas. **Determinismo** (3 `PYTHONHASHSEED` × 1.500 sementes × 2 modos): ver `resumos/determinismo.txt` das pastas das rodadas 1 e 2.

**Varridos nesta rodada, com método:** (a) o conceito "terreno" do Tam por script (`varredura-2026-10-05/scripts/audit_tam_terrenos.py`: 36 terrenos, entrada virada/desvirada contra o oráculo, alvo do fetch contra os subtipos do oráculo, terreno ≠ magia, regex de landfall: 0 falhas); (b) cada afirmação operacional dos goldfish #2, #3 e #5 por teste dirigido; (c) os tetos por turno em 20.000 partidas; (d) o perfil `playtester` contra as taxas dos 5 logs.
**NÃO varrido nesta rodada:** (1) outras ordens de pagamento além de "vivid" e "unidade irmã"; (2) política de ataque de dorks de mana e da Kiora (decisão de política, não de oráculo); (3) piscar da Chain Veil virada e de criatura de mana; (4) cópias da Saheeli de Whale, Peacemaker, Kiora, Oathkeeper e Lurker (a política nunca escolhe); (5) escolha de alvo da remoção do oponente no perfil `playtester` (não calibrada); (6) a mesa de 3 humanos do usuário (o perfil é o bot do Archidekt).

## Rodada 2026-10-28: goldfish manual #6 (compilado com as respostas do usuário)

Pasta: `resultados-ab/2026-10-23-goldfish-manual-6/`. **Oráculos conferidos no cache (ao vivo no Scryfall, Regra #1) antes dos testes:** Way of the Paradox (*"Whenever you activate a loyalty ability, you gain 1 life. You may play an additional land this turn."*, empower 5), Way of the Mind Sculptor (compra se tirou 2+), Sanctum Lurker (3/2; empower 1; `[+2]` para todo planeswalker), Wrenn and Realmbreaker (`−7`: emblema do cemitério), Tezzeret the Seeker (`−X`), Ichormoon Gauntlet, Dihada, Kiora of Salt and Sand, Dack Fayden, Flux Channeler, Staff of Compleation, Plaza of Heroes (`{T}: any color, spend only to cast a legendary spell`), Fracture, Prismari Command, Syphon Mind e **Forceful Denial** (faltava no cache; adicionada). **Achados:** nenhum de regra no simulador (19 testes, 239/239). **Diferenças de política (não alteradas):** `Tezzeret −X` prefere o Sol Ring (`TEZZ_PRIORITY` 55) ao Gauntlet (50), o usuário buscou o Gauntlet (**candidata a ajuste**, a decidir com A/B); no T4 o simulador conjura o Oko e não o Way of the Paradox. **Divergências do relato com as regras (o simulador está certo):** Oko do T4 sem mana; Tam do T9 com 1 proliferate em vez de X = 4. **Não varrido:** os outros modos do Prismari Command do oponente; o combate (estado de oponente).
