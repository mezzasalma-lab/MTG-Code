# Checklist cláusula-a-cláusula — Vihaan, Goldwaker

## Preferências do usuário: exílio sempre primeiro e Dictate com Treasures animados (correção do simulador) — 2026-10-04

Origem: respostas do usuário (T7 erro dele; *"Prefiro sempre jogar o spell exilado para criar mais tesouros"*; *"O dictate é mais vantagem, eu sacrifico tesouros animados e todos os oponentes sacrificam criaturas"*). Código: `vihaan_goldfish_v1.py` (antes = commit `ba594c8`). Tudo que sustenta a conclusão está em `resultados-ab/2026-10-04-exilio-sempre-e-dictate/`. Oráculo e rulings: os já lidos ao vivo (`.../2026-10-03-partida-manual-1/dados/oraculo_rulings_ao_vivo.json`).

| Cláusula do oráculo | Ruling | Antes (`ba594c8`) | Depois |
|---|---|---|---|
| **Prosper**, Pact Boon: *whenever you play a card from exile, create a Treasure* | qualquer carta jogada do exílio (2021-07-23) | ✅ só as que expiram neste turno iam antes da mão | ✅ **toda** carta do exílio antes da mão (preferência do usuário); mais cartas ⇒ mais Pact Boon |
| **Inspired Tinkering**: *exile the top three cards… until the end of your next turn, you may play those cards* | "play" (terreno vale); dois turnos | 🐛 ficavam esperando depois da mão no turno em que eram exiladas | ✅ jogadas assim que aparecem (inclusive no meio do main) |
| **Dictate of Erebos**: *whenever a creature you control dies, each opponent sacrifices a creature of their choice* | um gatilho por criatura; o oponente escolhe (2014-04-26) | 📊 só contava o uso; o farm exigia Mahadi/Plunderer | ✅ o Dictate em campo aciona o farm (custo: 1 Treasure por morte sem reposição); 📊 o oponente nunca sacrifica nada: `dictate_triggers_total` × 3 oponentes = proxy |
| **Treasure**: *{T}, Sacrifice this token: Add one mana of any color* | habilidade de mana, ativável sem nada pra gastar | ✅ (rodada anterior) | ✅ |

**Regra #6 (ordem de eventos):** o Dictate é pago com terrenos/rocks antes (`spend_mana` só gasta Treasure no que falta) e os animados morrem depois, com ele em campo; o farm roda depois da 2ª `main_phase`.
**Regra #5:** o simulador não dá valor aos sacrifícios dos oponentes (📊), então a métrica de vitória não mostra a vantagem do Dictate; a análise prioriza a linha real do usuário e reporta o custo em Treasures (−0,084 ±0,015 no estoque, só pelo Dictate).
**Validação:** smoke; 16/16 testes dirigidos; bit-identidade com as 2 chaves desligadas (20.000+20.000 partidas); regressão 140.000 partidas, 0 exceções; A/B pareado N=2.000/10.000 nos dois modos.
**Classes da taxonomia da Regra #1 varridas (e só elas):** política de jogada contra a linha real do usuário (exílio primeiro), habilidade ativada que nunca era usada como saída (Treasure), gatilho compartilhado (morte de criatura → Dictate). **Não varridas:** as demais classes e cartas do `.py`.

## Prosper (exílio) e Mahadi (mortes de Treasure animado) — correção do simulador — oráculo, rulings e cláusulas — 2026-10-03

Origem: respostas do usuário à análise da partida manual #1 (§3b do `goldfish-log.md`). Código: `vihaan_goldfish_v1.py` (antes = commit `7cd3f55`). Tudo que sustenta a conclusão está em `resultados-ab/2026-10-03-exilio-primeiro-e-mahadi/` (LEIAME com o mapa arquivo → comando). Oráculo e rulings: os já lidos ao vivo (`.../2026-10-03-partida-manual-1/dados/oraculo_rulings_ao_vivo.json`).

| Cláusula do oráculo | Ruling | Antes (`7cd3f55`) | Depois |
|---|---|---|---|
| **Prosper**, Mystic Arcanum: *exile the top card… until the end of your next turn, you may play that card* | a carta segue custos e timing normais (2021-07-23) | ✅ terreno jogado (97,8% dos que tiveram vez); 🐛 **mágica: 63% expiravam** (a mão ia primeiro; o usuário sempre jogou o exílio antes: T5, T6, T7) | ✅ a que expira neste turno é conjurada antes da mão (97,2% conjuradas) |
| **Prosper**, Pact Boon: *whenever you play a card from exile, create a Treasure* | qualquer carta jogada do exílio, terreno inclusive | ✅ por carta jogada | ✅ mais cartas jogadas ⇒ mais Treasures (0,34 → 0,56 chamadas por jogo) |
| **Treasure**: *{T}, Sacrifice this token: Add one mana of any color* | habilidade de mana: pode ser ativada sem nada pra gastar (ruling 2017-09-29 da Storm: *"You can activate the mana ability of a Treasure even if you have nothing to spend that mana on"*) | 🐛 só havia saída de sacrifício com Ashnod's Altar / Krark-Clan Ironworks | ✅ o próprio Treasure é a saída |
| **Vihaan**: *Treasures you control become 3/3 Construct Assassin artifact creatures… until end of turn* | Treasures mantêm as habilidades enquanto são criaturas (2024-04-12); CR 611.2c | ✅ criatura até o fim do turno (rodada do Treasure animado) | ✅ sacrificá-los como criatura é morte de criatura |
| **Mahadi**: *at the beginning of your end step, create a Treasure for each creature that died this turn* | só mortes do meu turno | ✅ conta `deaths_this_turn`; 🐛 só havia mortes dos animados com Altar/KCI | ✅ + o farm com Mahadi/Plunderer (a linha do T8) |
| **Pitiless Plunderer**: *whenever another creature you control dies, create a Treasure* | dispara para cada outra criatura que morre junto (2018-01-19) | ✅ | ✅ também no farm |
| **Zulaport / Sephiroth / Marionette Master / Mirkwood Bats / Agent of the Iron Throne** | gatilhos de morte/sacrifício | ✅ | ✅ também nas mortes do farm (testado: Sephiroth vira na 4ª) |
| **Dictate of Erebos**: *whenever a creature you control dies, each opponent sacrifices a creature of their choice* | um gatilho por criatura que morre; o oponente escolhe (2014-04-26) | 📊 sem nem contagem | 📊 `dictate_triggers_total` conta o uso (proxy); o oponente nunca sacrifica nada (estado de oponente) |

**Regra #3 (conceito compartilhado "saída de sacrifício de Treasure"):** `aggressive_treasure_destruction` só reconhecia Altar e KCI como saídas; o Treasure sacrificado por mana (`spend_mana`) já usava o roteamento do animado. Conferido por grep: `state.treasures -=` só em `sacrifice_treasures`.
**Regra #6 (ordem de fases):** o farm roda **depois** da 2ª `main_phase` (a mana foi gasta, os animados que pagaram magias já saíram) e **antes** do `end_step` (o Mahadi conta `deaths_this_turn` ali); a expiração do exílio é checada no **início** de cada `main_phase`.
**Regra #7 (ficha, 4 checagens):** o Treasure animado ataca? sim, e é criatura até o fim do turno; dispara "dies"? sim (`on_permanent_sacrificed`); morre no wipe? sim; conta em "you control X"? sim. O Treasure criado depois do início do combate **não** é criatura (CR 611.2c): o farm só leva `treasures_animated_alive`.

**Validação:** smoke (99 cartas, 0 desconhecidas/duplicadas, 35 terrenos); 17 testes dirigidos 17/17; bit-identidade com as 2 chaves desligadas, 20.000+20.000 partidas; regressão 140.000 partidas, 0 exceções, 0 violações; A/B pareado N=2.000 e N=10.000 nos dois modos (win ≤T8 padrão +2,40 ±0,42pp; resiliência +0,63 ±0,25pp; estoque de Treasures no fim +0,49 ±0,16 no padrão).
**Classes da taxonomia da Regra #1 varridas (e só elas):** habilidade ativada que nunca era usada como saída (Treasure como sacrifício), gatilho compartilhado (mortes de criatura), ordem de fases/eventos, escolha de política contra a linha real do usuário (Regra #5: exílio primeiro).
**Não varridas:** as demais classes e as outras cartas do `.py`. **Aberto:** farm sem Mahadi/Plunderer (decisão de valor), Dictate 📊, Lotho/Tax em 2ª mágica de oponente 📊.

## Conjurar/jogar de fora da mão (correção do simulador) — oráculo, rulings e cláusulas — 2026-10-03

Origem: análise da partida manual #1 (seção abaixo) + invariante de validação. Código: `vihaan_goldfish_v1.py` (antes = commit `c04840d`). Tudo que sustenta a conclusão está em `resultados-ab/2026-10-03-fora-da-mao/` (LEIAME com o mapa arquivo → comando). Oráculo e rulings lidos **ao vivo** antes de escrever o código (Regra #3; resposta bruta em `.../dados/oraculo_rulings_ao_vivo.json`, 70 rulings de 29 cartas).

| Cláusula do oráculo | Ruling | Antes (`c04840d`) | Depois |
|---|---|---|---|
| **Prosper**: *you may play that card* (Mystic Arcanum) | terreno é "play" | 🐛 terreno exilado nunca jogado (`play_from_impulse` filtrava terreno) | ✅ `play_impulse_land`: é a jogada de terreno, antes do da mão; untapped primeiro |
| **Prosper**, Pact Boon: *whenever you play a card from exile* | qualquer carta jogada do exílio, **terreno inclusive** (2021-07-23) | ✅ só magia não-terreno | ✅ terreno, magia e a conjurada pelo Cascade |
| **Inspired Tinkering**: *you may play those cards* / **Professional Face-Breaker**: *you may play that card this turn* | "play" → terreno vale | 🐛 idem | ✅ `lands_ok=True` |
| **Grenzo** / **Laughing Jasper Flint**: *you may cast* | "cast" → terreno **não** vale | ✅ (por acidente) | ✅ de propósito (`lands_ok=False`) |
| **Mágica do exílio** (instantânea/feitiço jogada de lá) | segue custo e timing; resolve e vai ao cemitério | 🐛 virava **permanente parado**, efeito nunca resolvia | ✅ `cast_card(from_zone="exile")` |
| **Lotho**: *whenever a player casts their second spell each turn, you lose 1 life and create a Treasure* | conjuradas **antes** do Lotho contam (2023-06-16); gatilho de **cast** | 🐛 `spells_cast_this_turn` só subia em `cast_card`; 🐛 testava "em campo" **depois** de a magia entrar (disparava contra si) | ✅ flashback e Cascade contam; foto do Lotho no cast; 📊 2ª mágica de **oponente** (estado de oponente) |
| **Life Insurance**, extort: *whenever you cast a spell* | qualquer magia conjurada | 🐛 só da mão | ✅ também flashback, exílio e Cascade |
| **Rain of Riches**: *first spell each turn that mana from a Treasure was spent to cast has cascade* | — | ✅ só da mão | ✅ também flashback |
| **Captain Lannery Storm**: *whenever you sacrifice a Treasure, +1/+0 until end of turn* | qualquer sacrifício; os pagos para **conjurar** a Storm não contam (2017-09-29) | 🐛 não existia | ✅ `_storm_pump` no poder (proxy) e no "that many" do **Reaver Cleaver** quando ela é o portador |
| **Sevinne's Reclamation**: *return target permanent card MV ≤3 … if cast from a graveyard, may copy* | permanent card = artefato, batalha, criatura, encantamento, **terreno**, planeswalker (2024-06-07); a cópia não é "cast" | 🐛 filtro `ctype != "land"`: devolvia instantânea/feitiço, **inclusive ela mesma**; terreno nunca | ✅ `_sevinne_return_one` (cast e flashback); terreno devolvido entra tapped se a regra manda, sem gastar jogada de terreno |

**Regra #3 (conceitos compartilhados):** "carta que entra/é conjurada de fora da mão" (5 caminhos: `cast_card`, `play_from_impulse`, `try_sevinne_flashback`, `do_cascade`, `try_face_breaker_impulse`/`pull_impulse`) e "permanent card" (2 pontos da Sevinne's). Grep conferido: `state.treasures -=` só em `sacrifice_treasures` (um ponto para o contador da Storm); `spells_cast_this_turn` só em `cast_card` antes da correção.
**Regra #6 (ordem de eventos):** o Lotho precisa estar em campo no CAST; o Pact Boon dispara no cast (antes de resolver: Blood Money destrói o Prosper depois de o Treasure ser criado); o terreno do exílio entra em `play_land` (antes de `main_phase`) para a mana valer no turno.
**Regra #7:** os Treasures criados por Pact Boon/Lotho/Storm/Cleaver não atacam no turno em que nascem (só os que existiam no início do combate viram criatura, CR 611.2c): o roteamento do Treasure animado, já corrigido, não muda.
**Erro de processo, registrado:** a 1ª versão do A/B tinha colunas lidas de contadores que o código antigo não tem (0 no ANTES, enganoso); foi apagada e refeita com medidas comparáveis antes de qualquer conclusão.

**Validação:** smoke (99 cartas, 0 desconhecidas/duplicadas, 35 terrenos); 37 testes dirigidos 37/37 (cenários T5–T8 da partida manual incluídos); bit-identidade com as 5 chaves desligadas, 20.000+20.000 partidas; regressão 180.000 partidas, 0 exceções, 0 violações (≤1 terreno por turno, 0 mágicas paradas no campo); A/B pareado N=2.000 e N=10.000 nos dois modos, todas as métricas diretas no sentido esperado (win ≤T8 padrão +1,29 ±0,30pp, resiliência +0,47 ±0,20pp).
**Classes da taxonomia da Regra #1 varridas (e só elas):** gatilho compartilhado ligado em só alguns pontos (cast de fora da mão), conceito compartilhado ("spell cast", "permanent card"), custo alternativo real (flashback, cast do exílio), fórmula dinâmica (Storm + Cleaver), busca sem restrição de tipo real (Sevinne's), ordem de fases/eventos (Lotho no cast).
**Não varridas:** as demais classes e as outras cartas do `.py`. **Aberto:** política "carta do exílio por último" (1,5 cartas/jogo expiram), 2ª mágica de oponente (Lotho/Tax) 📊, heurística "maior MV" da Sevinne's.

## Partida manual #1 — cláusulas das cartas que a partida exercita: log × oráculo × simulador — 2026-10-03

Pedido: *"Analise esse Goldfish do Vihaan: Assumi algumas mortes em combate para gerar tesouros com o Mahadi, e um oponente fez 2 spells com Lotho e Tax em campo, gerando 2 tesouros fora do meu turno."* Tudo que sustenta a conclusão está em
`resultados-ab/2026-10-03-partida-manual-1/` (LEIAME com o mapa arquivo → comando). Oráculo e **rulings** (70, de 29 cartas) lidos **ao vivo** no Scryfall (2026-10-03) antes da análise (Regra #3); resposta bruta em `.../dados/oraculo_rulings_ao_vivo.json`. Todas as cartas do log estão em `scryfall-cache/oracle-cache.json`.

| Carta / cláusula do oráculo | Ruling relevante | Log | Simulador (`c04840d`) |
|---|---|---|---|
| **Prosper**, Mystic Arcanum: *at the beginning of your end step, exile the top card… until the end of your next turn, you may play that card* | Precisa seguir custos e timing normais | ✅ T4 Mire, T5 Sevinne's, T6 Lotho, T7 Blood Money | ✅ `end_step` com `deadline_turns=1`; 🐛 **terreno nunca jogado** |
| **Prosper**, Pact Boon: *whenever you play a card from exile, create a Treasure* | dispara com **qualquer** carta jogada do exílio (2021-07-23), terreno inclusive | ✅ T5 (Mire), T6 (Sevinne's), T7 (Lotho: sem linha "criada" ao lado) | ✅ só magia não-terreno; 🐛 terreno e mágica |
| **Lotho**: *whenever a player casts their second spell each turn, you lose 1 life and create a Treasure* | mágicas conjuradas **antes** do Lotho contam (2023-06-16) | ⚠️ T7 (Tax = 2ª), T8 (Dictate = 2ª) sem linha "criada" dedicada | ✅ só a minha 2ª mágica **da mão**; 🐛 não conta exílio/flashback/Cascade; 🐛 dispara em si mesmo se for a 2ª mágica; 📊 2ª mágica de **oponente** (estado de oponente) |
| **Monologue Tax**: *whenever an opponent casts their second spell each turn, you create a Treasure* | uma vez por turno **por oponente**; não importa se a Tax estava em campo na 1ª mágica (2021-04-16) | ⚠️ "2 Treasures fora do meu turno" (Lotho + Tax) informados pelo usuário | 📊 `opponent_dependent` (mágica de oponente); nunca fabricado |
| **Mahadi**: *at the beginning of your end step, create a Treasure for each creature that died this turn* | só mortes **do meu turno** | ✅ T6 volta do cemitério; Zulaport morreu no turno do oponente | ✅ `deaths_this_turn` no end step (inclui Treasure animado sacrificado); 📊 mortes assumidas em combate não existem (sem bloqueio) |
| **Captain Lannery Storm**: *haste* / *whenever attacks, create a Treasure* | — | ✅ T5, T6 | ✅ |
| **Storm**: *whenever you sacrifice a Treasure, +1/+0 until end of turn* | qualquer sacrifício (2017-09-29); os pagos para **conjurar** a Storm não contam | ⚠️ T6: Treasure F--PiJszG some com a Storm em campo | 🐛 **não existe** |
| **The Reaver Cleaver**: *+1/+1, trample, whenever deals combat damage to a player, create that many Treasures* / Equip {3} | — | ⚠️ equip não registrado; sobras de mana de 3 em T6 e T7 batem com ele | ✅ equip pago, "that many" = poder + 1 (dinâmico); 🐛 sem o +1/+0 da Storm |
| **Sevinne's Reclamation**: *return target permanent card MV ≤3 from your graveyard; if cast from a graveyard, may copy and choose a new target* / Flashback {4}{W} | permanent card inclui **terreno** (2024-06-07); a cópia não é "cast" e não copia de novo (2019-08-23); flashback exila sempre | ✅ T6 do exílio (Mahadi), T8 flashback (Zulaport); ⚠️ cópia não usada | ✅ flashback com original + cópia (`try_sevinne_flashback`); 🐛 do exílio vira permanente sem efeito; alvo exclui terreno (heurística) |
| **Eldest Reborn** (oponente): I sacrifice / II discard / III reanimate | cada capítulo no turno do dono, depois do draw (2018-04-27) | ✅ I: o usuário confirmou que sacrificou o **Zulaport**; ⚠️ II: **esqueceu** o descarte (resposta do usuário); III sem registro | 📊 carta de oponente |
| **Desolate Mire**: *{1},{T}: add {W}{B}* / **Rakdos Signet**: *{1},{T}: add {B}{R}* | +1 líquido cada | ✅ usados nas contas de mana | ✅ |
| **Dragonskull Summit**: *enters tapped unless you control a Swamp or a Mountain* | checa os que já estão em campo | ✅ T1 tapped (sem Mountain em campo) | ✅ (`land_enters_tapped`) |

**Regra #3 (conceito compartilhado "jogar/conjurar de FORA da mão"):** o simulador tem 5 caminhos que movem carta de fora da mão para o jogo, e cada um tratava um subconjunto das consequências de "cast"/"play": `cast_card` (completo), `play_from_impulse` (só mana + entrar + Pact Boon, mágica vira permanente), `try_sevinne_flashback` (mana + efeito, sem contar a mágica), `do_cascade` (entra + resolve, sem contar), `try_face_breaker_impulse`/`pull_impulse` (terreno descartado). Consequências compartilhadas que faltavam: contador de "second spell" (Lotho), extort (Life Insurance), Pact Boon, resolução de instantânea/feitiço, jogada de terreno.
**Regra #6 (ordem de fases/eventos):** o Lotho precisa estar em campo **no momento da conjuração**, não depois de a mágica entrar; o teste ficava depois de `enter_battlefield`.
**Regra #7 (ficha/token, 4 checagens):** só os Treasures que existem quando a habilidade resolve viram criatura (CR 611.2c) — conferido **por id** (`atacantes_vs_criacao.txt`): nenhum Treasure virado foi criado depois do primeiro toque de Treasure do turno; as mortes assumidas em combate são do usuário, não do simulador.

**Validação:** 7/7 saídas refeitas e iguais byte a byte (`resumos/verificacao_reproducao.txt`); mana fecha exato em T2, T3, T4, T8 (script `ledger_mana.py`); 4 testes diretos das lacunas do simulador.
**Classes da taxonomia da Regra #1 varridas (e só elas):** gatilho compartilhado ligado em só alguns pontos (cast de fora da mão), conceito compartilhado ("spell cast"), custo alternativo (flashback, cast do exílio), fórmula dinâmica achatada (Storm + Cleaver), ordem de fases (Lotho no cast).
**Não varridas:** as demais classes e as outras cartas do `.py`; as respostas do usuário sobre a atribuição dos Treasures de T6/T7/T8 (perguntas no `goldfish-log.md`).

## Sephiroth, Fabled SOLDIER // One-Winged Angel (correção do simulador) — oráculo, rulings e cláusulas — 2026-10-03

Pedido: *"Quero sim, corrija os itens 2 e 3."* (lacunas do Sephiroth levantadas ao responder se o simulador flipava com 4 mortes no turno). Código: `vihaan_goldfish_v1.py` (antes = commit `ba74496`). Tudo que sustenta a conclusão está em
`resultados-ab/2026-10-03-sephiroth/` (LEIAME com o mapa arquivo → comando). Oráculo e rulings lidos **ao vivo** no Scryfall (2026-10-03) antes de escrever o código e relidos antes de fechar a rodada (Regra #3); resposta bruta em `.../dados/oraculo_e_rulings.json`.

**Rulings (10, 2025-06-06) relevantes:** (i) *If Sephiroth, Fabled SOLDIER and one or more other creatures die at the same time, its last ability will trigger for each of those other creatures. (It won't transform, though.)* (ii) *If this card somehow enters the battlefield with its back face up, it didn't transform, so you won't get an emblem.* As demais 8 tratam de faces de carta dupla, cor, valor de mana e fichas-cópia e não mudam a leitura.

| Cláusula do oráculo | Status | Onde / como |
|---|---|---|
| Frente: "Whenever Sephiroth enters or attacks, you may sacrifice another creature. If you do, draw a card." | ✅ já existia · **não relida nesta rodada** | `try_sephiroth_sac_draw` (fora do escopo da correção) |
| Frente: "Whenever another creature dies, target opponent loses 1 life and you gain 1 life" | ✅ + 🐛 corrigido (simultaneidade) | `_sephiroth_death_triggers`: em lote (`begin_mass_death`) dispara para **cada outra** criatura que morre junto, em qualquer ordem de remoção, fichas incluídas; a morte do próprio Sephiroth **não** dispara a frente ("another") |
| Frente: "If this is the fourth time this ability has resolved this turn, transform Sephiroth" | ✅ + 🐛 corrigido (contador) | conta resoluções da frente, vira na 4ª; **não vira** se ele morre no mesmo lote (ruling i); o contador zera em cada turno de oponente (`try_smart_opponent_turn`) e na reentrada (objeto novo em `enter_battlefield`). As resoluções 5ª, 6ª… que já estavam na pilha continuam resolvendo, sem virar de novo |
| Verso: "Super Nova — … you get an emblem with 'Whenever a creature dies, …'" | 🐛 corrigido (acumula) | `super_nova_emblems` conta emblemas; cada virada dá 1 novo; emblema é objeto independente (continua mesmo sem Sephiroth em campo) |
| Emblema: "Whenever a **creature** dies" (sem "another") | ✅ | a morte do próprio Sephiroth dispara o emblema (W5/W8 nos testes) |
| Emblema + Sephiroth de frente em campo | 🐛 corrigido | 2 gatilhos por morte (o do emblema e o da frente); a 4ª resolução da frente vira de novo e dá um 2º emblema. Um emblema que nasce no meio do lote **não** dispara para as mortes do lote (já aconteceram) |
| Verso: "Flying" | 📊 | sem bloqueio nem remoção por voo no goldfish (evasão não muda nada aqui) |
| Verso: "Whenever Sephiroth attacks, you may sacrifice any number of other creatures. If you do, draw that many cards." | ✅ já existia · **não relida nesta rodada** | `try_sephiroth_sac_draw` |
| "another creature dies" de criatura de **oponente** | 📊 estrutural | a cláusula não restringe o controlador, mas o simulador não modela criaturas de oponente (estado real de oponente, Regra #1) |

**Regra #3 (conceito compartilhado "criatura morre"):** todas as vias que tiram criatura do campo, conferidas por grep em `vihaan_goldfish_v1.py` (`battlefield.remove`, `constructs -=`, `other_tokens -=`, zeramentos de contador nos wipes): `sacrifice_named_creature` e `remove_permanent` (nomeadas), `sacrifice_constructs`, `sacrifice_other_tokens`, `sacrifice_treasures` (animados), `_destroy_dragons`, os blocos de wipe de `try_smart_opponent_wipe` e Blood Money/Blasphemous Act — todas chamam `on_creature_dies` via `on_permanent_sacrificed`/`on_permanent_destroyed`. A única outra remoção direta do campo é o Cascade tirando a **mágica** resolvida (não é criatura). Os wipes (3 pontos) agora abrem e fecham o lote.
**Regra #6 (ordem de fases):** o contador zerava só no meu turno; `try_smart_opponent_turn` agora o zera no início de cada turno de oponente. A virada é medida no momento em que a 4ª resolução ocorre, não no end step, então não depende da ordem de `play_turn`.

**Erro meu na própria correção (pego por teste dirigido antes da medição):** a 1ª versão do lote disparava a frente também na morte do próprio Sephiroth (5 gatilhos num wipe com 4 outras criaturas). Corrigido com `dying=` nas duas vias de permanente nomeado. Conferido nos testes W1, W2, W3, W7, W8 e W9.

**Validação:** smoke (99 cartas, 0 desconhecidas/duplicadas, 35 terrenos); 28 testes dirigidos 28/28; bit-identidade com as 3 chaves desligadas, 20.000+20.000 partidas; regressão 140.000 partidas, 0 exceções, 0 violações dos invariantes novos; A/B pareado N=2.000 e N=10.000 (padrão e resiliência): virada do Sephiroth no modo resiliência **2,31% → ~0,61%** (−1,70 ±0,25pp), das quais 72% das viradas antigas (167/231) eram wipes em que ele morria junto (instrumentado no código antigo); drain e vitória até o T8 sem mudança mensurável. Reprodutibilidade: 11 de 11 saídas refeitas e iguais byte a byte (`resumos/verificacao_reproducao.txt`).
**Achados laterais (não corrigidos):** wipes próprios (Blood Money, Blasphemous Act) usam o caminho de **sacrifício** ("destroy" não é sacrifício: Mayhem Devil dispara a mais, comandante excluído); Sephiroth poderia sacrificar Treasures animados (política); Xorn e Pitiless Plunderer em lote por evento (pré-existente); 7 outros decks sorteiam o fundo no mulligan.
**Classes da taxonomia da Regra #1 varridas (e só elas):** gatilho compartilhado ligado em só alguns pontos (morte de criatura nos wipes e sacrifícios), conceito compartilhado "criatura que morre" (grep de todas as vias), ordem de fases / fronteira de turno (Regra #6), fórmula dinâmica (número de emblemas × número de gatilhos).
**Não varridas:** as demais classes e as outras cartas do `.py` (não foi auditoria carta a carta); as habilidades de entrada/ataque do Sephiroth não foram relidas.

## Treasure animado, mulligan e terreno tapped (correção do simulador) — oráculo, rulings e cláusulas — 2026-10-03

Pedido: *"Quero sim, corrija todos os erros do simulador!"* (resposta à oferta de corrigir o roteamento do Treasure animado). Código: `vihaan_goldfish_v1.py` (antes = commit `6e623d3`). Tudo que sustenta a conclusão está em
`resultados-ab/2026-10-03-treasure-animado-e-mulligan/` (LEIAME com o mapa arquivo → comando). Oráculo e rulings lidos **ao vivo** no Scryfall (2026-10-03) **antes** de escrever o código (Regra #3); resposta bruta em `.../dados/oraculo_e_rulings.json`.

**Oráculo (Vihaan, Goldwaker, Outlaws of Thunder Junction Commander):** *Other outlaws you control have vigilance and haste. At the beginning of combat on your turn, you may have Treasures you control become 3/3 Construct Assassin artifact creatures in addition to their other types until end of turn.*
**Rulings (5, 2024-04-12):** os Treasures animados mantêm as habilidades; Assassin é outlaw; um Treasure que já é criatura tem o P/T sobrescrito pelo efeito. **CR 611.2c** (`rules-cache/comprehensive-rules.txt`, linha 2915): o conjunto de objetos afetado é fixado quando o efeito contínuo começa.
**Cartas de contexto lidas:** Zulaport Cutthroat (1 ruling), Pitiless Plunderer (1), Mahadi, Emporium Master (0), Ashnod's Altar (0), Krark-Clan Ironworks (0), Sephiroth (10).

| Cláusula do oráculo | Status | Onde / como |
|---|---|---|
| Vihaan: "Other outlaws you control have vigilance and haste" | ✅ | haste propagado a `ready_creatures`; vigilância 📊 (sem bloqueio modelado), e é por ela que o Treasure animado que ataca continua desvirado para mana na 2ª main |
| Vihaan: "At the beginning of combat… Treasures you control become 3/3 Construct Assassin artifact creatures… until end of turn" (animação) | ✅ | `combat_step`: `treasures_animated_this_combat` e `treasures_animated_alive` = Treasures no início do combate |
| "… until end of turn" | 🐛 corrigido | os animados continuam criaturas na 2ª main phase; `end_step` zera `treasures_animated_alive` (antes só o Altar os via como criatura, e só no combate) |
| CR 611.2c: só os Treasures que existiam na resolução | 🐛 corrigido | `sacrifice_treasures` só roteia como criatura até `treasures_animated_alive`; o Treasure criado depois (Olivia, Face-Breaker, Pitiless Plunderer, Reaver Cleaver…) não é criatura. O código antigo sacrificava **todos** os Treasures ao Altar |
| Ruling: "Treasures keep any abilities they previously had while they're creatures" | ✅ | o animado continua podendo ser sacrificado por mana (`spend_mana`) e por qualquer outlet |
| Ashnod's Altar: "Sacrifice a creature: Add {C}{C}" | 🐛 corrigido | só aceita animados vivos |
| Krark-Clan Ironworks: "Sacrifice an artifact: Add {C}{C}" | 🐛 corrigido | aceita todos; o animado sacrificado a ele também é criatura (antes: "não é criatura fora do combate") |
| Zulaport / Pitiless Plunderer / Sephiroth / Agent of the Iron Throne / Mahadi: "creature dies / is sacrificed" | 🐛 corrigido por conceito compartilhado | disparam em **todo** sacrifício de Treasure animado (`on_permanent_sacrificed(is_creature=True)`), não só no do Altar |

**Regra #3 (conceito compartilhado "Treasure animado é criatura"):** os 9 pontos de `sacrifice_treasures` no `.py` (conferido por grep): `spend_mana` (mana de Treasure), `try_face_breaker_impulse`, `Deadly Dispute` (`resolve_instant_sorcery`), `Lich-Knights' Conquest`, Magda ("Sacrifice three Treasures"), Jan Jansen, `aggressive_treasure_destruction` (Altar e KCI). Todos passam agora pelo mesmo roteamento padrão (`as_creature=None`); só os dois explícitos antigos ficam sob a chave desligada.
**Regra #6 (ordem de fases):** `play_turn` = `… draw → play_land → main_phase → check_visitor_combo → combat_step (animação no início; destruição pós-combate) → main_phase (2ª: mana de Treasure animado) → … → end_step (Mahadi; zera os animados)`. A animação precede os dois pontos em que o sacrifício importa; Mahadi conta as mortes **antes** de o end step zerar. Teste em `play_turn` completo.

**Mulligan e terreno (Vihaan):** (1) o London Mulligan sorteava as cartas do fundo; agora `choose_bottom` (terreno só com mais de 4, depois a não-terreno de maior custo, protegendo `GOOD_KEEP`). (2) `play_land` jogava `lands_in_hand[0]`; agora `choose_land_to_play` (tapped em T1/T2 salvo se custar uma jogada de desenvolvimento) com a regra de "entra tapped" numa função só (`land_enters_tapped`: tag `etb_tapped`, checkland, fastland; shockland paga a vida).

**Validação:** smoke (99 cartas, 0 desconhecidas/duplicadas, 35 terrenos); bit-identidade com as 3 chaves desligadas, 20.000+20.000 partidas; regressão 160.000 partidas, 0 exceções; 42 testes dirigidos 42/42; A/B pareado N=2.000 (padrão e resiliência) e N=10.000 com as métricas novas se movendo no sentido esperado (animados sacrificados como criatura 0,56 → 1,53 por partida; mortes de criatura +1,05; mana T2/T3 do tapped +0,05/+0,08). Números no `goldfish-log.md`.

**Achados laterais (não corrigidos):** Sephiroth poderia sacrificar Treasures animados (política); Xorn e Pitiless Plunderer em lote por evento (pré-existente); 7 outros decks sorteiam as cartas do fundo no mulligan.
**Classes da taxonomia da Regra #1 varridas (e só elas):** gatilho compartilhado ligado em só alguns pontos (morte de criatura por sacrifício de Treasure), estático lido em uma função mas não propagado (Treasure animado = criatura), conceito compartilhado "criatura que morre", ordem de fases (Regra #6), custo/escolha do piloto (mulligan, terreno).
**Não varridas:** as demais classes e as outras cartas do `.py` (esta rodada não foi uma auditoria carta a carta).

## Kingpin, Wilson Fisk (candidata, implementada só no harness) — oráculo, rulings e cláusulas — 2026-10-03

A carta **não está na lista**; foi acrescentada em tempo de execução por `resultados-ab/2026-10-03-kingpin/orquestracao/kp_harness.py`
(monkeypatch; `vihaan_goldfish_v1.py` não foi alterado). Oráculo lido ao vivo no Scryfall (2026-10-03; Marvel Super Heroes Commander #661; a foto enviada confere com o oráculo) e
salvo em `scryfall-cache/oracle-cache.json`; resposta bruta e rulings em `resultados-ab/2026-10-03-kingpin/dados/rulings_Kingpin_Wilson_Fisk.json` (rulings de contexto em `rulings_contexto_vihaan_xorn_manufactor_procession.json`).

**Oráculo:** {3}{B}, Legendary Creature — Human Villain, 3/6. *Menace. Whenever you sacrifice Kingpin or another creature, create two Treasure tokens. This ability triggers only once each turn.*
**Rulings do Kingpin: nenhum (0).** **Rulings de contexto lidas antes de escrever o código:** Vihaan, Goldwaker (5; 2024-04-12): os Treasures animados "keep any abilities they previously had while they're creatures" e "outlaw" é Assassin/Mercenary/Pirate/Rogue/Warlock;
Xorn (1): várias Xorn somam; Academy Manufactor (4): cada criação vira 1 de cada (Clue, Food, Treasure); Anointed Procession (6): dobra a quantidade de cada tipo, e várias Processions multiplicam; Dictate of Erebos (5); Goldspan Dragon (3); Mirkwood Bats e Ashnod's Altar (0); Sephiroth (10).

| Cláusula do oráculo | Status | Como entra no harness |
|---|---|---|
| Legendary Creature 3/6, {3}{B} | ✅ | `add(KINGPIN, 4, "creature", {"kingpin"})`; poder 3 em `CREATURE_POWER` (métrica de combate) |
| tipos Human Villain (não é outlaw) | ✅ | sem tag `outlaw`: o Vihaan não lhe dá haste nem vigilância; entra e só ataca no turno seguinte |
| Menace | 📊 estrutural | sem bloqueio no goldfish (convenção do arquivo) |
| "Whenever you sacrifice Kingpin or another creature" | ✅ | gatilho em `on_permanent_sacrificed(..., is_creature=True)`, o ponto central de todo sacrifício do simulador (Constructs, fichas, criatura nomeada, Treasure animado via Altar); para "Kingpin" sacrificado, `_kp_self` deixa o gatilho enxergar a própria saída. Destruição/wipe (`on_permanent_destroyed`) **não** dispara, como no oráculo |
| "create two Treasure tokens" | ✅ | `create_treasures(state, 2)`: Xorn (+1), Anointed Procession (×2) e Academy Manufactor (Clue+Food+Treasure) valem como para qualquer criação, na ordem que maximiza (Xorn → Procession → Manufactor) |
| "This ability triggers only once each turn." | ✅ | flag `kp_triggered_this_turn`, zerada no início de `play_turn` |
| ruling do Vihaan: Treasure animado conserva habilidades = é criatura | ✅ nas políticas `anim`/`delib` | sacrificar um Treasure ANIMADO (após o início do combate, até o fim do turno) por qualquer via conta como criatura sacrificada para o Kingpin (mana no 2º main, Krark-Clan Ironworks, Magda); o simulador original passa `as_creature=False` e só o Altar passa `True`: lacuna do `.py` (abaixo), que aqui só o Kingpin enxerga |
| linha deliberada (não é cláusula) | ✅ política `delib` | no começo do `end_step`, sem disparo no turno e com Treasure animado sobrando, sacrifica UM por nada para disparar o Kingpin (−1 Treasure, +2/+3/+4/+6) |

**Regra #3 (conceitos compartilhados que a carta lê):** (a) **"sacrificar"** = `on_permanent_sacrificed` (o Mayhem Devil já lê o mesmo ponto: "Whenever you sacrifice a permanent"); a destruição passa por `on_permanent_destroyed`, que o Mayhem Devil e o Kingpin ignoram de propósito (conferido por leitura das duas funções); (b) **"criar Treasure"** = `create_treasures`, que já aplica Xorn/Procession/Academy e dispara `on_tokens_created` (Mirkwood Bats, Kambal, Caretaker's Talent), então cada disparo do Kingpin aciona esses pagadores de graça; (c) **"Treasure animado é criatura"** só existe em `treasures_animated_this_combat` (setado no início de `combat_step`, zerado em `play_turn`); a leitura de quantos animados restam (`_animated_left`) é do harness.
**Regra #6 (ordem de fases, `play_turn`):** `upkeep (Smaug, Revel, Laughing Jasper Flint) → compra → play_land → main_phase → combat_step (animação no início) → main_phase (2º main: aqui o Treasure animado já é criatura) → Magda (crime) → end_step`. O disparo `delib` roda no começo do end step (depois dos dois mains), então os 2 Treasures criados **não** são gastáveis naquele turno (valem a partir do seguinte) e a conta de Revel in Riches é feita no upkeep seguinte (o simulador a marca no end step e encerra a partida).

**Achado lateral do simulador (não corrigido nesta rodada, Regra #1; classe "gatilho compartilhado ligado só em ALGUNS pontos"):** o Treasure animado sacrificado é tratado como não-criatura em dois caminhos, para TODOS os gatilhos de criatura: `spend_mana` (mana do 2º main) e o ramo do Krark-Clan Ironworks de `aggressive_treasure_destruction` (só o Ashnod's Altar passa `as_creature=True`), apesar de o oráculo do Vihaan manter o Treasure criatura até o fim do turno. Zulaport Cutthroat, Nadier's Nightblade, Pitiless Plunderer, Sephiroth, Dictate of Erebos e Mahadi (end step, `deaths_this_turn`) subestimam esses eventos.

**Classes da taxonomia da Regra #1 varridas para esta carta (e só ela):** gatilho compartilhado (sacrifício, criação de Treasure), conceito compartilhado (criatura × Treasure animado), fórmula com multiplicadores (Xorn/Procession/Academy), ordem de fases, tipo (outlaw ou não), limite 1×/turno.
**Não varridas:** auditoria carta-a-carta do `.py` (a carta não está na lista), Menace/bloqueio (📊), oponente real.

## Inevitable Defeat (candidata, implementada só no harness) — oráculo, ruling e cláusulas — 2026-10-03

A carta **não está na lista**; foi acrescentada em tempo de execução por `resultados-ab/2026-10-03-inevitable-defeat/orquestracao/vih_harness.py`
(monkeypatch; `vihaan_goldfish_v1.py` não foi alterado). Oráculo lido ao vivo no Scryfall (2026-10-03) e salvo em `scryfall-cache/oracle-cache.json`;
resposta bruta e rulings em `resultados-ab/2026-10-03-inevitable-defeat/dados/rulings_Inevitable_Defeat.json`.

**Oráculo:** {1}{R}{W}{B}, Instant. *This spell can't be countered. Exile target nonland permanent. Its controller loses 3 life and you gain 3 life.*
**Rulings (1):** 2025-04-04 — se o alvo for ilegal quando a magia tenta resolver, ela não resolve e nenhum efeito acontece: ninguém ganha nem perde vida.

| Cláusula do oráculo | Status | Como entra no harness |
|---|---|---|
| "This spell can't be countered." | 📊 estrutural | o goldfish não tem contramágica de oponente |
| "Exile target nonland permanent." | 📊 estrutural | exílio de permanente de OPONENTE (não modelado). Conta como remoção (tag `removal` ⇒ `removal_cast_total`) |
| (efeito colateral do alvo) | ✅ | o alvo é permanente de oponente, então **comete crime** ("Targeting opponents, anything they control... is a crime", reminder text da Magda): `commits_crime_this_turn = True`, que o simulador lê no fim do turno para a Magda |
| "Its controller loses 3 life" | ✅ | `drain(state, 3, each_opp=False)` (alvo único: 3 de vida de mesa) |
| "and you gain 3 life." | ✅ | `gain_life(state, 3)`, que soma em `life_gained_this_turn` (lido pela Witch of the Moors no end step) |
| ruling 2025-04-04 (alvo ilegal ⇒ nada acontece) | 📊 estrutural | o goldfish assume alvo sempre legal |
| custo {1}{R}{W}{B} | ✅ com ressalva | o simulador só conta mana total; a restrição R+W+B é uma porta de cor do harness (`VIH_COLOR=sim|best`: 3 fontes distintas, Treasure e Arcane Signet como fonte de qualquer cor) |

**Regra #3 (conceitos compartilhados que a carta lê):** (a) "cometeu crime neste turno" — escrito por todas as remoções com alvo (linha ~1185 do `.py`) e lido só no fim do turno
pela Magda (linha ~2020); a Defeat escreve o mesmo flag; (b) "ganhou vida neste turno" — `gain_life` soma em `life_gained_this_turn`, zerado em `play_turn` e lido pela Witch no end step;
(c) "dano de mesa" (`drain`) — alimenta `table_damage_total`, que compõe `win_turn`. Nenhum conceito de tipo (artefato, token, criatura) é tocado: a carta não entra em campo.
**Regra #6 (ordem de fases):** o flag de crime é lido depois dos main phases (comentário do `.py`, bug corrigido em 2026-08-22), então a Defeat conjurada em qualquer main do meu turno conta. A Defeat no **turno do oponente** não é modelada (o simulador só conjura no meu turno): para a Magda isso seria um 2º Treasure possível, então o proxy é piso.

**Classes da taxonomia da Regra #1 varridas para esta carta (e só ela):** gatilho compartilhado (crime, ganho de vida), custo (cor), tipo (não é artefato/token/criatura), custo alternativo (nenhum no oráculo), fórmula dinâmica (nenhuma: 3 fixo no oráculo).
**Não varridas:** auditoria carta-a-carta do `.py` (não era o pedido), oponente real (📊).

## Draconic Visitor (candidata FRA) + 2 gaps reais achados no caminho — 2026-09-25

**Gatilho:** *"A carta Draconic Visitor, avalie ela como possível inclusao
tanto no Ur-Dragon, quanto no Vihan, e me diga aonde ela seria melhor e
pq, ou se não vale incluir em nenhum dos 2!"* A carta entra no simulador
só como candidata (via `swap`, troca posicional). `lista.md` não muda.

### Draconic Visitor — oráculo ao vivo (cache FRA #80), cláusula a cláusula

`{3}{R}{R}` Creature — Dragon 5/5. Legalidade: `not_legal` até o
lançamento de FRA (2026-10-02).

| Cláusula | Status | Onde |
|---|---|---|
| Flying | ✅ | poder 5 em `CREATURE_POWER`, conta no combate |
| "If one or more artifact tokens would be created under your control, that many 5/5 red Dragon creature tokens with flying are created instead." | ✅ | `create_treasures` e `create_constructs` → `_create_visitor_dragons` |

Detalhes da substituição (regras reais, não heurística):
- É efeito de substituição obrigatório (CR 614.1a, "instead"). Com a
  Visitor em campo nenhum Treasure, Clue, Food, Construct ou Servo chega a
  existir.
- O controlador escolhe a ordem das substituições (CR 616.1). A ordem que
  maximiza Dragões é: Xorn (+1) → Anointed Procession (×2) → Academy
  Manufactor (Clue + Food + Treasure = 3 fichas de artefato por Treasure) →
  Visitor. Exemplo: o Treasure do upkeep do Smaug com as 4 em campo vira
  (1+1)×2×3 = 12 Dragões 5/5.
- As fichas são criatura, não artefato. Disparam Kambal (2ª habilidade),
  Mirkwood Bats e Caretaker's Talent na criação. Morrem em "destroy all
  creatures": `_destroy_dragons` cobre Blood Money, Blasphemous Act e o
  wipe de oponente do modo de resiliência. Não têm haste: não são outlaws,
  então o Vihaan não dá haste a elas. Atacam do turno seguinte em diante.
- O combo Visitor + Pitiless Plunderer + Ashnod's Altar fica fora do
  Commander Spellbook. Foi derivado das regras: sacrifica um Dragão no
  Altar ({C}{C}), o Plunderer cria um Treasure, a Visitor troca por um
  Dragão, e repete. Isso dá mana incolor, mortes, fichas criadas e
  sacrifícios infinitos. Fecha o jogo com qualquer um dos pagadores da
  lista: Zulaport Cutthroat, Mirkwood Bats, Nadier's Nightblade, Kambal,
  Sephiroth (transforma na 4ª resolução, depois o emblema drena sem
  limite), Mayhem Devil, ou Agent of the Iron Throne com o Vihaan em campo.
  O Agent é Encantamento (Background), então não serve de primeira
  criatura do loop. Implementado em `check_visitor_combo`, chamada depois
  de cada fase principal e no end step.

📝 O que a Visitor desliga no deck (checado no oráculo de cada carta):
- a 2ª habilidade do próprio Vihaan (animar Treasures);
- a vitória alternativa da Revel in Riches;
- o dano do Smaug ("number of Treasures you control");
- o Treasure de 2 manas do Goldspan;
- o Scorpion Dragon da Magda, the Hoardmaster;
- o roubo do Kellogg;
- os contadores da Olivia;
- o −X/−X do Grim Hireling;
- o impulso do Professional Face-Breaker;
- o pump do Captain Lannery Storm;
- a cascata da Rain of Riches;
- o combustível de KCI e Jan Jansen;
- o dreno da Marionette Master;
- o anthem da Sentinel Sarah Lyons ("an artifact entered").

A Visitor pode ser sacrificada (Altar, Phyrexian Tower, Deadly Dispute,
Sephiroth) pra religar o modo Treasure. 📝 O simulador nunca faz isso.

### 🐛 Kambal, Profiteering Mayor — limite de 1x/turno aplicado à habilidade errada

Oráculo: 1ª habilidade "Whenever one or more tokens your opponents
control enter ... This ability triggers only once each turn."; 2ª
habilidade "Whenever one or more tokens you control enter, each opponent
loses 1 life and you gain 1 life." O código limitava a 2ª a 1x/turno. O
"only once each turn" pertence à 1ª. Corrigido em `on_tokens_created`:
agora drena a cada evento de criação.

### 🐛 The Reaver Cleaver — "that many" achatado pra 1 fixo

Oráculo: "Equipped creature gets +1/+1 and has trample and 'Whenever this
creature deals combat damage to a player or planeswalker, create that
many Treasure tokens.' Equip {3}". O código criava 1 Treasure sempre que
*qualquer* criatura atacava. Isso é a categoria "fórmula dinâmica
achatada" da Regra #1: o arquivo agora rastreia poder impresso
(`CREATURE_POWER`, novo nesta rodada), então dá pra calcular o valor
exato. Corrigido:
- equipa a criatura não-comandante de maior poder. O Vihaan nunca ataca
  neste simulador (`ready_creatures` o exclui);
- dispara só quando o portador ataca;
- cria poder + 1 Treasures (o próprio +1/+1), +2 com Sentinel Sarah Lyons
  ativa;
- se o portador sai de campo, o Equipamento fica solto (CR 301.5c) e
  reequipar custa {3} de novo.

### Métrica nova (só leitura, não muda nenhuma decisão)

- `combat_damage_proxy_total` soma o dano de combate sem bloqueio (mesma
  premissa "ataca livre" do resto do arquivo). Usa poder impresso,
  Treasure animado 3/3, Construct 1/1, ficha genérica 2 (📝 média), e
  Dragão 5/5. Bônus reais aplicados:
  - Caretaker's Talent nível 3 (+2/+2 em ficha de criatura);
  - Sentinel Sarah Lyons (+2/+2 se um artefato entrou no turno);
  - Shared Animosity nos grupos homogêneos Construct e Dragão.
- `drain(..., each_opp=True)` marca "each opponent loses N" (Zulaport,
  Mirkwood Bats, Nadier's, Kambal, Agent, extort). `table_damage_total`
  soma N × 3 nesses casos e N em "target"/"any target" (Mayhem Devil,
  Sephiroth, Marionette, Smaug, Sarah Lyons). `drain_damage_total` segue
  a convenção antiga.
- `win_turn` é o primeiro turno que cumpre uma destas condições:
  - (dano de mesa + combate) ≥ 120;
  - Revel in Riches no upkeep com 10+ Treasures;
  - combo da Visitor com pagador.

### Validação

- Smoke: 99 cartas, 0 desconhecidas/duplicadas.
- Testes dirigidos: `test_vihaan_goldfish.py`, 22/22. Cobrem Kambal,
  substituição e ordem Xorn/Anointed/Manufactor, Constructs, Dragões
  atacando/doentes, wipe matando Dragões, combo com e sem pagador, Agent
  exigindo o comandante, Revel no upkeep, peso "each opponent", Reaver
  Cleaver "that many", exigência de portador atacando e reequip pago, e
  swap posicional/bit-idêntico.
- 20.000 + 20.000 partidas (padrão + resiliência, seed 6.100.000+), 0
  exceções (rodado depois do fix da Cleaver).
- Antes/depois em 2.000 seeds: ver `goldfish-log.md`.

---

## Porte completo do modo de resiliência (interação de oponente) + CR 903.9a nativa desde o início — 2026-09-21

**Gatilho:** *"Ainda bem que vimos isso antes de implementar o Vihaan,
que tb tem muito sacrifício de artefatos!"* — comentário do usuário
logo após concluir a auditoria de CR 903.9a nos outros 9 decks desta
sessão (Megatron/Ur-Dragon/Hei Bai/Edgar Markov/Ulalek/Toph/Prismatic
Bridge/Maralen/Rat King Verminister), seguido de *"Vamos fazer o Vihaan
agora."* Este deck nunca tinha nenhuma extensão de resiliência antes
(criado em 2026-08-22, auditado clausula-a-clausula pela última vez em
2026-09-14, mas sem `interaction_rng`/`remove_permanent` nenhum) — porte
completo do zero, **primeiro deck desta sessão a nascer com a correção
de CR 903.9a nativa desde a 1ª linha**, em vez de implementada errado e
corrigida depois via retrofit (os outros 9 decks foram todos retrofit).

**Design incorporado direto do padrão final já validado nos outros 9
decks:** 7 categorias padronizadas (removal/attack/discard/wipe/
graveyard-wipe/graveyard-snipe/counterspell), wipe unificado (1 rolagem
"algum wipe acontece" + escolha ponderada de 1 TIPO só —
creature/artifact/enchantment — em vez de 3 rolagens independentes),
gate de atenção por oponente (`OPPONENT_ATTENTION_CHANCE`), supressão
de ataque pós-wipe simétrico (`state.wiped_this_round`).

**CR 903.9a aplicada desde o início em `remove_permanent`:** comandante
vai pro cemitério DE VERDADE primeiro (CR 700.4, "dies" — ação baseada
em estado, CR 704, não substituição — ver
`rules-cache/comprehensive-rules.txt` linhas 6888-6896, Regra 18 de
`references/user-standing-rules.md`), disparando `on_creature_dies`
normalmente (Zulaport Cutthroat/Pitiless Plunderer/Agent of the Iron
Throne/Sephiroth/Life Insurance — nenhum deles é ele mesmo; Vihaan
NUNCA é artefato, só creature+outlaw, `on_artifact_dies` nunca dispara
pra ele), só DEPOIS é removido de lá pra representar a escolha do dono
de movê-lo pra zona de comando. **Mayhem Devil fica de fora** (via
`on_permanent_destroyed`, uma cópia de `on_permanent_sacrificed` SEM a
linha do Mayhem Devil) — oráculo real é "whenever YOU SACRIFICE", e
destruição/wipe de oponente nunca é sacrifício feito por mim.

**Achado real ADICIONAL durante a validação (2 bugs pré-existentes do
próprio motor do deck, não de oponente — achados só porque a regressão
de 20.000 partidas rodou de verdade pela 1ª vez neste espaço de
seeds):** `sacrifice_named_creature` (chokepoint central de sacrifício
VOLUNTÁRIO já existente no arquivo desde 2026-08-22) **nunca tratava o
caso do comandante** — se ela fosse escolhida como sacrifício, ficava
presa no cemitério pra sempre, `commander_in_play` travado em `True`.
O fallback do **Deadly Dispute** (`resolve_instant_sorcery`, custo
adicional mandatório "sacrifice an artifact or creature") escolhia
`candidates[0]` sem NENHUMA preferência contra o comandante — se
Treasures/Constructs/tokens genéricos estivessem todos zerados,
`candidates[0]` podia literalmente ser Vihaan mesmo com outro
artefato/criatura real disponível, dependendo só da ordem de
`state.battlefield`. **319/20.000 seeds (1,6%) tinham o comandante
preso no cemitério** antes desta correção. Corrigidos os 2: (1)
`sacrifice_named_creature` agora trata o comandante igual `remove_
permanent` (cemitério de verdade → zona de comando), MAS mantém Mayhem
Devil disparando aqui — diferente de `remove_permanent`, isto É um
sacrifício de verdade feito por mim; (2) Deadly Dispute agora prefere
qualquer outro artefato/criatura real antes de considerar o comandante,
só a sacrifica quando ela é genuinamente a ÚNICA opção legal (o custo é
mandatório, sem alternativa de não pagar).

**Validação:** compilação OK. Bit-identidade em modo padrão (20.000
seeds, seed_base 6000000) contra o commit anterior, comparando só as
chaves PRÉ-EXISTENTES (campos novos do modo de resiliência excluídos
da comparação, já que trivialmente começam no default em modo padrão):
**0/20000 mismatches** — antes do fix do Deadly Dispute. Depois do fix
do Deadly Dispute (mudança de comportamento real e intencional, não
regressão): **657/20000 mismatches (3,3%)**, divergência esperada e
legítima (mesma categoria "RNG ripple" do Blightsteel Colossus/
Megatron/Toph — agora que o comandante é corretamente deprioritizado
como fodder, jogos que antes a sacrificavam por acidente seguem um
caminho diferente). Validado por comparação A/B agregada (10.000
seeds) em vez de bit-identidade:
`treasures_created_total`/`creature_deaths_total`/
`drain_damage_total`/`cards_drawn_extra`/`combat_attacks_total` todos
dentro de margem pequena e coerente (ex. 9,2643→9,1674), e "comandante
nunca conjurado" **idêntico** nos dois lados (0,79%/0,79% — confirma
que o fix só afeta QUEM é sacrificado depois dela já estar em campo,
nunca se/quando ela é conjurada). Regressão de 20.000 partidas em modo
padrão + 20.000 em modo de resiliência (rodada de novo após o fix dos
2 bugs pré-existentes): 0 exceções nos 2, **0 comandantes presos no
cemitério nos 2** (era 319/20000 em resiliência antes do fix). 7 testes
dirigidos: (1) `remove_permanent` — Zulaport dispara, comandante não
presa; (2) Mayhem Devil NÃO dispara por destruição de oponente; (3)
`sacrifice_named_creature` — Mayhem Devil DISPARA (sacrifício real),
comandante não presa; (4) contra-ataque intercepta o cast, mana já
gasta, ela nunca entra em campo; (5) Deadly Dispute prefere Sol Ring ao
comandante quando ambos disponíveis; (6) Deadly Dispute sacrifica o
comandante só quando é a única opção, sem ficar presa; (7)
`try_smart_opponent_wipe` inclui o comandante nos alvos, ela não fica
presa no cemitério.

**Resultado:** primeiro deck desta sessão a nascer com CR 903.9a nativa
desde o início — mas a validação rigorosa (20k regressão, não só bit-
identidade rasa) ainda achou 2 bugs REAIS pré-existentes no motor
próprio do deck (não relacionados a oponente), confirmando o valor de
sempre rodar a regressão completa mesmo quando a lógica nova "parece"
certa por construção.

## Auditoria oráculo-por-oráculo completa — 2026-09-14

Última das 16 decks desta campanha (mesmo tratamento já aplicado a
Edgar Markov, Hei Bai, Kutzil, Maralen, Ms. Bumbleflower, Nekusar,
Prismatic Bridge, Rat King, Thranduil, Toph, Azula, Beorn, Captain Storm,
Ur-Dragon e Ulalek). A rodada de 2026-09-01 (ver seção abaixo) já tinha
corrigido 3 gaps reais e concluído "arquitetura já madura, poucos gaps
restantes" — releitura completa desta rodada, clause-by-clause contra o
oráculo real (Scryfall `/cards/collection` em 2 lotes de 45/46, todas as
91 cartas encontradas de primeira, sem fallback `fuzzy` necessário —
inclusive o MDFC Brightclimb//Grimclimb e o `transform` do Sephiroth),
achou **16 gaps reais adicionais**, a maioria numa classe de bug que a
detecção automatizada de "tag órfã" das rodadas anteriores não conseguia
enxergar: **tag aplicada ao subconjunto ERRADO de cartas** (não uma tag
nunca lida — a tag "outlaw" É lida em vários lugares — mas aplicada
faltando em 7 cartas e sobrando em 2), e **habilidades 100% ausentes sem
nenhuma tag própria pra detecção automatizada encontrar** (Magda's
Scorpion Dragon só tinha um comentário mencionando o nome, nunca uma
implementação real).

### 🐛 Os 16 gaps reais corrigidos nesta rodada

**Grupo 1 — tags `outlaw`/`haste` erradas (afeta Back in Town, Olivia,
Laughing Jasper Flint, e o novo item 3 abaixo):**

1. **Tag `outlaw` faltando em 7 cartas com type real Assassin/Mercenary/
   Pirate/Rogue/Warlock** (verificado via `type_line` do Scryfall, não
   assumido): Captain Lannery Storm (*Human Pirate*), Grim Hireling
   (*Tiefling Rogue*), Lotho, Corrupt Shirriff (*Halfling Rogue*), Mari,
   the Killing Quill (*Vampire Assassin*), Pitiless Plunderer (*Human
   Pirate*), Witch of the Moors (*Human Warlock*), Zulaport Cutthroat
   (*Human Rogue Ally*). `OUTLAW_TYPES` já existia no arquivo mas nunca
   era usado pra checar tipo real — a tag era aplicada manualmente carta
   a carta, e essas 7 ficaram de fora.
2. **Tag `outlaw` sobrando em 2 cartas SEM type outlaw real**: Jan
   Jansen, Chaos Crafter (*Gnome Artificer* — Artificer não é outlaw
   type) e Magda, the Hoardmaster (*Dwarf Berserker* — Berserker não é
   outlaw type).
   Corrigido em `CARD_DB`. Afeta 4 pontos reais de leitura: `Back in
   Town` (alvo em pilha "outlaw creature cards"), o gatilho da Olivia,
   Opulent Outlaw ("um ou mais outlaws causam dano"), o X do Laughing
   Jasper Flint ("número de outlaws que você controla") e o novo item 3.
3. **Vihaan, Goldwaker — 2ª habilidade estática (a "menor" das duas,
   nunca lida) 100% ausente.** Oráculo real: *"Other outlaws you control
   have vigilance and haste."* Só a 1ª habilidade (animar Treasures em
   combate) estava implementada. Vigilance é 📊 (sem bloqueio modelado,
   não muda nada). Haste NUNCA era propagado pra `ready_creatures` —
   toda criatura outlaw sem a keyword impressa (Grenzo, Laughing Jasper
   Flint, Lotho, Mari, Olivia, Orochi Soul-Reaver, Pitiless Plunderer,
   Prosper, Witch of the Moors, Zulaport, Aya) ficava presa com doença de
   invocação no turno em que entrava, mesmo com Vihaan em campo
   concedendo haste de verdade — perdendo o gatilho de ataque daquele
   turno inteiro. Corrigido em `combat_step()`:
   `"haste" in CARD_DB[n].tags or (state.commander_in_play and is_outlaw(n))`.
4. **Tags `haste` faltando em 3 cartas com "Haste" real no oráculo**
   (Scryfall): Goldspan Dragon (*"Flying, haste"*), Jan Jansen, Chaos
   Crafter (*"Haste"*), Sentinel Sarah Lyons (*"Haste"*). Sem a tag,
   `ready_creatures` as tratava como tendo doença de invocação no turno
   em que entravam — Goldspan Dragon nunca disparava seu próprio
   "attacks: create Treasure" no turno de entrada; Sentinel Sarah Lyons
   nunca disparava seu Battalion (já implementado desde 2026-09-01) no
   turno de entrada.

**Grupo 2 — timing errado (mesma classe de bug documentada desde a
criação do arquivo pro Mahadi, replicada aqui em 2 cartas novas):**

5. **Laughing Jasper Flint — gatilho inteiro na fase ERRADA, 0% de valor
   gerado desde sempre.** Oráculo real: *"At the beginning of your
   upkeep, exile the top X cards of target opponent's library... Until
   end of turn, you may cast spells from among those cards..."* — estava
   implementado dentro de `end_step()` (fase que só roda DEPOIS das 2
   main phases do turno). Como `play_from_impulse()` só é chamado de
   dentro de `main_phase()`, as cartas exiladas no end_step nunca tinham
   janela nenhuma pra serem jogadas — a habilidade inteira produzia zero
   valor, só acumulava lixo em `impulse_pool`. Corrigido: movida pra
   `play_turn()`, na mesma posição de upkeep real já usada pelo Smaug the
   Magnificent (logo após o reset de flags do turno). `deadline_turns=0`
   continua correto nessa posição nova (a fase de upkeep é o INÍCIO do
   turno, então "until end of turn" cobre as 2 main phases inteiras
   deste mesmo turno).
6. **Urabrask's Forge — token criado DEPOIS do snapshot de atacantes do
   combate, nunca contava como atacante no próprio combate em que
   nascia, apesar de ter haste real impressa.** Oráculo real: *"At the
   beginning of combat on your turn, put an oil counter..., then create
   an X/1 red Phyrexian Horror creature token with trample and HASTE...
   Sacrifice that token at the beginning of the next end step."* O
   código antigo criava o token no FINAL de `combat_step()`, depois de
   `ready_other`/`total_attackers` já calculados — o token literalmente
   não podia contribuir pra nenhum gatilho de "criatura ataca" deste
   mesmo combate (Aya/Grenzo/Face-Breaker/Orochi/Olivia), e era
   sacrificado no `end_step()` sem nunca ter feito nada. Corrigido: movida
   pro TOPO de `combat_step()` (mesma posição de "beginning of combat" já
   usada pra animação de Treasures do Vihaan), com novo parâmetro
   `haste=True` em `create_other_tokens()` (não marca como
   summoning-sick). Bônus real da mesma correção: `state.forge_oil`
   nunca era lido em lugar nenhum além do próprio incremento — o X/1 real
   continua 📊 (P/T por criatura não é rastreado neste arquivo, mesma
   limitação estrutural de sempre), mas o token agora ao menos CONTA como
   1 atacante genérico pros gatilhos de combate, que é o mínimo que a
   contagem baseada em presença (não P/T) deste simulador consegue
   refletir. Também corrigido: se Anointed Procession dobra a criação
   (2 tokens em vez de 1), o `end_step()` antigo só sacrificava 1 sempre
   — novo campo `state.forge_tokens_this_turn` sacrifica a quantidade
   exata criada.

**Grupo 3 — gatilho "one or more" (lote) confundido com gatilho "a
creature"/"a historic creature" (por instância — 2 cartas onde o oráculo
NÃO usa a fórmula em lote que suas cartas-irmãs no mesmo deck usam):**

7. **Aya of Alexandria — achatado pra "1 token fixo se pelo menos 1
   criatura histórica atacar" em vez de 1 por criatura histórica.**
   Oráculo real: *"Whenever A HISTORIC creature you control deals combat
   damage to a player, create a...token"* — SEM "one or more" (ao
   contrário de Olivia/Professional Face-Breaker/Grim Hireling/Orochi
   Soul-Reaver, todas com "one or more...", corretamente já modeladas
   como 1 gatilho em lote). `any(is_historic(n) for n in
   ready_creatures)` virou `sum(...)` + Constructs + Treasures animados
   pelo Vihaan (ambos artefatos, ambos históricos).
8. **Grenzo, Havoc Raiser — mesma classe de bug.** Oráculo real:
   *"Whenever A creature you control deals combat damage to a
   player..."* — singular, sem "one or more". `pull_impulse(state, 1,
   ...)` virou `pull_impulse(state, total_attackers, ...)` (a contagem
   real já calculada no topo de `combat_step()`).

**Grupo 4 — habilidades reais 100% ausentes:**

9. **Magda, the Hoardmaster — 2ª habilidade real inteira ausente, só
   citada num comentário enganoso.** Oráculo real: *"Sacrifice three
   Treasures: Create a 4/4 red Scorpion Dragon creature token with flying
   and haste. Activate only as a sorcery."* — a linha 307 do arquivo
   (`other_tokens: int ... # criaturas token genericas (changeling,
   manifest, Scorpion Dragon...)`) sugeria que já estava coberta pelo
   contador genérico, mas nenhum código em lugar nenhum de fato
   sacrificava Treasures e criava o token. Só a 1ª habilidade ("whenever
   you commit a crime") estava implementada. Corrigido com um loop em
   `main_phase()` (sem {T} no custo real — repetível livremente enquanto
   sobrar Treasure, ao contrário de Jan Jansen que tem {T} e é capado a
   1x/turno corretamente).
10. **Professional Face-Breaker — 2ª habilidade real inteira ausente**
    (tag `impulse_treasure_sac` nunca lida). Oráculo real: *"Sacrifice a
    Treasure: Exile the top card of your library. You may play that card
    this turn."* Corrigido com `try_face_breaker_impulse()`, heurística
    conservadora de 1x/turno (mesmo padrão do Jan Jansen) pra não brigar
    demais pelo combustível de Treasure que Vihaan anima em combate.
11. **Agent of the Iron Throne — metade real da habilidade concedida
    ausente.** Oráculo real (Background): *"Commander creatures you own
    have 'Whenever an ARTIFACT OR CREATURE you control is put into a
    graveyard from the battlefield, each opponent loses 1 life.'"* — só
    a metade artefato (`on_artifact_dies`) estava coberta; a metade
    CRIATURA (provavelmente a mais comum das duas neste deck aristocrata
    cheio de sac outlets) nunca disparava. Corrigido em
    `on_creature_dies()`. Também corrigido, pra bater com "commander
    creatures you own": a habilidade só existe enquanto Vihaan
    (`state.commander_in_play`) estiver de fato em campo — faltava esse
    gate em AMBAS as metades (impacto prático baixo, já que Vihaan é
    sempre a 1ª coisa que `main_phase()` tenta conjurar, mas corrige o
    texto pro caso raro de mana nunca ter dado pro comandante).
12. **Extort (Life Insurance) — habilidade real 100% ausente**, tag
    presente no `CARD_DB` (`extort`), nunca lida. Oráculo real: *"Extort
    (Whenever you cast a spell, you may pay {W/B}. If you do, each
    opponent loses 1 life and you gain that much life.)"* Mesma
    convenção já usada em TODO drain/vida deste arquivo (Zulaport/Mayhem
    Devil/Nadier's Nightblade/etc): é um drain disparado pela SUA PRÓPRIA
    ação (conjurar uma mágica), não por um evento do oponente que
    precisaria ser simulado — modelável de verdade via `drain()`+
    `gain_life()`, diferente de efeitos genuinamente `opponent_dependent`
    que exigem um alvo/evento do oponente pra sequer acontecer. Corrigido
    em `cast_card()`, com snapshot do estado ANTES do próprio ETB (a
    própria Life Insurance não "paga extort" na sua própria conjuração —
    a habilidade só existe uma vez em campo). Não expandido pro caminho
    de `do_cascade()` (cascade via Rain of Riches não incrementa
    `spells_cast_this_turn`/não passa por `cast_card()` — limitação
    pré-existente, não introduzida nem agravada por esta correção,
    documentada como fora de escopo desta rodada por afetar também o
    Lotho e não ser o foco do achado).
13. **Sevinne's Reclamation — custo alternativo Flashback {4}{W}
    inteiramente ausente** (categoria (k) da campanha). Só o cast normal
    da mão estava implementado. Oráculo real completo: *"Return target
    permanent card with mana value 3 or less from your graveyard to the
    battlefield. If this spell was cast from a graveyard, you may copy
    this spell and may choose a new target for the copy. Flashback
    {4}{W}."* — uma ativação via flashback resolve DUAS vezes (original +
    cópia). Corrigido com `try_sevinne_flashback()`, mesma heurística de
    alvo (maior MV≤3, não-terreno) do cast normal; exila depois (não
    volta pro cemitério).
14. **The Reaver Cleaver — custo real Equip {3} nunca pago.** O bônus de
    combate (*"Whenever this creature deals combat damage..., create
    that many Treasure tokens"*, já modelado como proxy de +1 Treasure/
    combate — "that many" exigiria P/T por criatura, que este arquivo não
    rastreia, mesma limitação 📊 de sempre) disparava de graça em
    qualquer ataque, sem nunca ter sido equipado em ninguém. Corrigido
    com `try_equip_reaver_cleaver()` — paga Equip {3} uma vez (fica
    equipado o resto da partida — este simulador nunca reequipa),
    condicionado a ter pelo menos 1 criatura real em campo; o gatilho de
    combate agora exige `state.reaver_cleaver_equipped`.

**Grupo 5 — custo/escala real substituída por valor fixo/arbitrário:**

15. **Back in Town — MV real errado no `CARD_DB` (6 em vez de 3) + custo
    X nunca pago + cap arbitrário de X≤2.** Oráculo real (Scryfall):
    `{X}{2}{B}`, cmc=3 (X conta 0 pra CMC, regra padrão) — o custo fixo
    real é `{2}{B}`=3, não 6. `CARD_DB.mv` corrigido pra 3. O código
    antigo pagava só o (errado) custo fixo de 6 e nunca cobrava X mana
    nenhuma, capando arbitrariamente `X = min(2, remaining_mana)`.
    Corrigido: `X = min(outlaws reais no cemitério, mana que sobrou
    depois do custo fixo real)`, com `spend_mana(state, x)` de verdade —
    sem cap artificial.
16. **Lich-Knights' Conquest — fodder incompleto.** Oráculo real:
    *"Sacrifice any number of ARTIFACTS, ENCHANTMENTS, and/or TOKENS."*
    O código só contava Constructs+Food+Clue como fodder, ignorando
    Treasures e `other_tokens` — AMBOS são tokens de verdade (Treasure
    também é artefato), e Treasures são de longe o maior reservatório do
    deck inteiro (motor central, `TREASURE_MAXIMIZE_POLICY`). Corrigido:
    `fodder = treasures + constructs + other_tokens + foods + clues`,
    sacrificando na mesma ordem de prioridade já usada em Deadly Dispute
    (Treasure > Construct > other_tokens > Food/Clue), reusando
    `on_permanent_sacrificed()` pra Food/Clue (que não tinham função de
    sacrifício própria antes) — hub central continua sendo o único ponto
    de disparo de gatilhos de morte, nenhuma lógica duplicada.

### Verificações que confirmaram implementação correta (não eram gaps)

- **Requisition Raid (Spree)** — modelado como remoção genérica de custo
  base sem escolher modo, mesma convenção já usada pra Council's
  Judgment/outros removals multi-modo neste arquivo; o modo 3 ("+1/+1 em
  cada criatura que um jogador alvo controla", que PODERIA mirar o
  próprio jogador) exigiria P/T por criatura pra ter efeito numérico —
  estrutural, não um gap.
- **Exotic Orchard** — cor por fonte nunca é rastreada em NENHUM terreno
  deste arquivo (convenção já documentada pro Brightclimb Pathway); tratar
  como terreno genérico de 1 mana é consistente com o resto, não uma
  exceção.
- **Jan Jansen — as 2 habilidades de {T}** já estavam corretamente
  mapeadas (Treasure sacrificado = artefato NÃO-criatura → 2 Constructs;
  Construct sacrificado = artefato-criatura → 2 Treasures) e corretamente
  capadas a 1 ativação/turno (as 2 habilidades compartilham o mesmo {T}).
  Só faltavam as tags `haste`/`outlaw` corrigidas (grupo 1).
- **Sephiroth, Fabled SOLDIER // One-Winged Angel** — releitura completa
  do oráculo (front+back via Scryfall `card_faces`) confirmou que a
  implementação de 2026-08-31 já bate 100% clause-by-clause (emblem Super
  Nova independente da carta, sem cap de 4x/turno pós-transform, escala
  de sacrifício "any number" no ataque pós-transform).
- **Blasphemous Act / Blood Money** — excluem o próprio Vihaan do wipe
  (convenção implícita já consistente entre as duas cartas — sacrificar o
  próprio comandante junto com o resto do board num wipe autoinfligido
  não é uma jogada racional que nenhum piloto faria).

### Gaps considerados e deliberadamente NÃO alterados

- **Extort × `do_cascade()`** — cascade (Rain of Riches) não passa por
  `cast_card()`, então spells conjuradas via cascade não disparam Extort
  nem incrementam `spells_cast_this_turn` (afeta também o gatilho "2ª
  mágica do turno" do Lotho). Pré-existente, não introduzido nem agravado
  por esta rodada; documentado aqui pra rodadas futuras, fora de escopo
  desta (cascade só dispara em ≤1 mágica/turno, via `cascade_used_this_
  turn`, impacto baixo).
- **Food/Clue tokens sem habilidade própria ativável** (`{2}, Sac: gain 3
  life` / `{2}, Sac: draw a card`, texto de lembrete padrão desses tipos
  de token) — únicos criados via Academy Manufactor, nunca tinham
  nenhuma função de sacrifício antes desta rodada; agora só são
  sacrificáveis como fodder do Lich-Knights' Conquest (item 16). Dar a
  eles um sink genérico próprio (vida/draw) seria expandir escopo além
  de cartas realmente listadas na lista — mantido fora, mesmo padrão de
  "não inventar mecânica nova não pedida por uma carta real" já usado
  noutras rodadas desta campanha.

### Validação

- **Smoke test:** `CARD_DB` 94 entradas, `BASE_LIBRARY` 99 cartas (100%
  batendo com `lista.md`), 0 cartas desconhecidas, 0 duplicatas,
  comandante presente.
- **38 testes unitários isolados** (script dedicado), cobrindo cada uma
  das 16 correções individualmente — todos passando (outlaw/haste tags,
  anthem de haste do Vihaan propagado, timing do Laughing Jasper Flint e
  do Urabrask's Forge incl. duplicação via Anointed Procession, deadline
  off-by-one do Prosper/Inspired Tinkering, escala por-atacante da
  Aya/Grenzo, Magda/Face-Breaker/Extort/Sevinne flashback gerando valor,
  gate do Agent of the Iron Throne, MV+X real do Back in Town, fodder
  completo do Lich-Knights' Conquest, gate de Equip do Reaver Cleaver).
- **Antes/depois via `git stash`/`git stash pop`** (2.000 jogos, mesma
  seed 7500000, turns=8):

| Métrica | Antes | Depois |
|---|---|---|
| Avg Treasures em campo no fim | 2,60 | 2,06 |
| Avg Treasures sacrificados (total) | 4,83 | 5,37 |
| Avg outros tokens criados | 0,83 | 1,61 |
| Avg mortes de artefato | 5,05 | 5,57 |
| Avg drain/dano agregado (proxy) | 3,34 | 3,93 |
| Avg vida ganha | 1,09 | 1,33 |
| Avg combates com ≥1 atacante | 4,04 | 4,31 |
| Sephiroth transformado — % jogos | 0,6% | 0,7% |
| RECURSION avg/jogo | 0,13 | 0,14 |
| FINISHER Revel in Riches — % jogos | 0,1% | 0,2% |
| Avg Scorpion Dragons da Magda (novo) | — | 0,09 |
| Avg impulsos Face-Breaker (novo) | — | 0,37 |
| Avg Extort pago (novo) | — | 0,17 |
| Avg flashbacks Sevinne's (novo) | — | 0,01 |

  Todas as métricas se moveram na direção esperada (mais atacantes
  hasty/outlaw contando combates, mais sinks reais de Treasure/token
  drenando o pool mais rápido — daí Treasures em campo no fim caindo
  mesmo com mais sinks ativos —, mais drain/vida via Extort+Agent of the
  Iron Throne+escala real da Aya/Grenzo), nenhuma métrica explodiu, e as
  4 métricas novas confirmam que cada habilidade recém-implementada
  realmente dispara em jogos reais.
- **Regressão de 20.000 partidas** (seed 9500000+, turns=10): **0
  exceções**.

---

Pedido direto do usuário (2026-09-01): *"AGORA FAZ O QUE SEMPRE Te MANDei
FAZER: COmpila a porra de TODAS AS CARTAS DOS DECKS UMA A UMA... cada
carta tem que ser lida linha a linha"* — mesmo tratamento já aplicado a
Toph, Beorn, Edgar Markov, Hei Bai, Maralen, Megatron, Nekusar, Prismatic
Bridge, Rat King, Thranduil, Ulalek e Ur-Dragon.

**Contexto importante:** este simulador já foi construído do zero
(2026-08-22) especificamente pra corrigir 5 problemas reais de um script
anterior de terceiros (mana nunca gasta de verdade, um combo fictício,
combate contra oponentes fictícios, sorteios de probabilidade em vez de
texto real, timing errado do Mahadi) — já nasceu com um padrão de rigor
alto. Mesmo assim, a releitura linha-a-linha desta rodada achou **3 gaps
reais**.

**Método:** detecção automatizada de 37 tags órfãs + nomes de carta com
poucas ocorrências. A esmagadora maioria eram falsos positivos — este
arquivo tem uma arquitetura de aristocratas MUITO centralizada
(`on_permanent_sacrificed()` → `on_creature_dies()`/`on_artifact_dies()`/
`on_token_leaves()`, chamada por toda via real de sacrifício), então
cartas com efeitos de morte/sacrifício raramente precisam de dispatch
próprio — aparecem "órfãs" na varredura textual mas estão corretamente
cobertas pelo hub central.

**Legenda:**
- ✅ **Implementado** — efeito real no código, local citado.
- 📊 **N/A estrutural** — sem oponente real, sem combate/P-T por criatura
  individual — limite conhecido, não julgamento de valor.
- 🐛 **Corrigido nesta rodada (2026-09-01)**.

## 🐛 Os 3 gaps corrigidos nesta rodada

1. **High Market** (tag `sac_outlet_life`) — *"{T}, Sacrifice a creature:
   You gain 1 life."* 100% ausente — nem sequer citada fora do próprio
   `add()`.
2. **Phyrexian Tower** (tag `sac_outlet_bb`) — *"{T}, Sacrifice a
   creature: Add {B}{B}."* Mesma situação.
   Ambas corrigidas com `try_sac_land_outlets()`, chamada no início do
   `end_step()` (depois do combate, quando tokens do turno já atacaram e
   Constructs/other_tokens sobrando não têm mais uso pendente). Só
   sacrifica tokens descartáveis, nunca uma criatura nomeada real — dar
   um corpo de verdade por 1 vida ou 1 mana extra é claramente mau
   negócio, nenhum piloto racional faria isso. Reusa
   `sacrifice_constructs()`/`sacrifice_other_tokens()`, que já disparam
   TODOS os gatilhos reais de morte centralizados
   (`on_permanent_sacrificed()`) — Zulaport Cutthroat, Pitiless
   Plunderer, Mahadi (via `deaths_this_turn`), Sephiroth, Mayhem Devil —
   sem duplicar nenhuma lógica. Síntese bônus real: como isso roda ANTES
   do check da Witch of the Moors no mesmo `end_step()`, a vida ganha via
   High Market agora também satisfaz a condição "if you gained life this
   turn" dela em turnos que, de outra forma, não teriam ganho de vida.
3. **Sentinel Sarah Lyons** (tag `anthem_artifact`) — oráculo real tem 2
   habilidades: *"As long as an artifact entered the battlefield under
   your control this turn, creatures you control get +2/+2"* (estático
   numérico — 📊 genuíno, este arquivo não rastreia P/T por criatura em
   NENHUM outro lugar, consistente) e *"Battalion — Whenever Sentinel
   Sarah Lyons and at least two other creatures attack, she deals damage
   equal to the number of artifacts you control to target player"* (gatilho
   real e quantificável, mesma convenção de proxy de dano já usada pro
   Smaug the Magnificent — nunca implementado). Corrigido em
   `combat_step()`, com novo helper `artifacts_in_play()` (soma
   permanentes artifact/artifact_creature nomeados + Treasures +
   Constructs).

Validado com 9 testes unitários isolados + regressão de 20.000 partidas
(seed 8000000+, turns=10, 0 exceções) + `run_batch` antes/depois via
`importlib` (3000 jogos, seed 9000000, turns=10): drain/dano proxy
9.91→11.74, vida ganha 2.78→3.32, mana bônus via sac outlets 5.71→6.10.

## Achado verificado, não um gap (decisão de design já documentada)

O próprio docstring do cabeçalho já documentava, de forma transparente
(não uma omissão disfarçada), que **Grenzo, Havoc Raiser** e **Laughing
Jasper Flint** têm habilidades reais que exilam da biblioteca do
OPONENTE, mas usam a PRÓPRIA biblioteca como fonte substituta aproximada
(diferente da convenção "sem efeito numérico" usada pra Mari/Smothering
Tithe/Monologue Tax/Revel in Riches/Kellogg, todas no mesmo bloco de
"simplificações documentadas"). Essa inconsistência interna já estava
sinalizada no próprio texto do arquivo — não é uma descoberta desta
rodada, e como é uma decisão de design deliberada (não uma omissão
silenciosa) já revisada anteriormente, **não foi alterada** aqui pra
evitar uma regressão de comportamento não solicitada nesta passada.

## Demais cartas — confirmadas ✅ implementadas via dispatch centralizado

Verificação sistemática de todas as ~35 tags/nomes suspeitos restantes
confirmou dispatch real: `checkland_br/rw/wb` (genérico via
`CHECKLAND_TYPES`), `creature_death_drain`/`artifact_death_drain`/
`token_leave_drain`/`token_etb_drain`/`token_create_or_sac_drain`
(centralizados em `on_creature_dies()`/`on_artifact_dies()`/
`on_token_leaves()`), `death_drain_transform` (Sephiroth, lógica extensa
de emblem/transformação), `fabricate3`/`recursion_repeat`/`recursion_sac`/
`recursion_x`/`historic_combat_token`/`combat_impulse`/`upkeep_impulse`/
`impulse_end_step`/`lifegain_recursion`/`sac_damage`/`treasure_attack_damage`/
`forge_token`/`token_draw`/`alt_win` — todas com dispatch por nome
confirmado por leitura direta do código, não por contagem ingênua de
string. `gy_hate` (Bojuka Bog) e as 5 tags já auto-rotuladas `_unused`
(Kellogg, Dictate of Erebos, Boros Charm, Teferi's Protection, Grim
Hireling) confirmadas 📊 genuinamente estruturais via oráculo real
buscado no Scryfall (todas opponent-dependent ou combat-dependent sem
modelo).

---

## Resumo numérico

- **~95 cartas na lista** (`lista.md`).
- **🐛 Corrigido nesta rodada:** 3 cartas (High Market, Phyrexian Tower,
  Sentinel Sarah Lyons).
- **✅ Falsos positivos descartados:** ~34 tags/cartas, confirmadas
  corretamente implementadas via dispatch centralizado.
- **📊 Estrutural confirmado (verificado via Scryfall, não assumido):**
  Kellogg (roubo de criatura), Dictate of Erebos (edict), Boros Charm/
  Teferi's Protection (proteção sem ameaça real), Grim Hireling (-X/-X
  sem alvo), Bojuka Bog (graveyard hate sem oponente), anthem estático da
  Sentinel Sarah Lyons.
